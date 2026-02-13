# Design a Distributed Task Scheduler

> **Companies**: Uber, Meta, Google, Amazon, Airbnb, LinkedIn, Stripe | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a system that reliably executes tasks at the right time, at most once or at least once, even when nodes fail? This probes your understanding of distributed coordination, exactly-once semantics (or lack thereof), priority scheduling, dead letter handling, and the fundamental trade-off between scheduling latency and system reliability. If you've worked on Kubernetes, this is directly analogous to kube-scheduler — the interviewer wants to see that connection.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**Questions that show the interviewer you know what you're doing:**

- "What types of tasks? One-time (send email at 3pm), recurring (run report every hour), or event-triggered (process upload when complete)?"
- "What's the scheduling precision needed? Second-level, minute-level, or best-effort?"
- "What's the delivery guarantee? At-most-once (acceptable to miss some), at-least-once (duplicates OK), or exactly-once (critical — like financial transactions)?"
- "How many tasks per day? Thousands or billions?"
- "What's the acceptable delay between scheduled time and execution? Seconds or minutes?"
- "Do tasks have priorities? Can a high-priority task preempt a running low-priority task?"
- "What's the execution duration range? Milliseconds (send an API call) or hours (ML training job)?"
- "Do tasks have dependencies? DAG-style execution (task B runs after task A completes)?"

### Working Assumptions
| Parameter | Value | Derivation |
|-----------|-------|------------|
| Total scheduled tasks | 100M active tasks at any time | Mix of one-time and recurring |
| New tasks created/day | 10M | Mostly recurring schedule expansions |
| Task executions/day | 500M | 100M active x average 5 executions/day |
| Task executions/sec (peak) | ~20K | 500M / 86,400 x 3 (peak factor) |
| Scheduling precision | 1 second | Must fire within 1 second of scheduled time |
| Delivery guarantee | At-least-once | Idempotent task handlers expected |
| Task payload size | 1KB average | Serialized job parameters |
| Execution duration | 100ms to 30 minutes | Mix of quick API calls and longer jobs |
| Priority levels | 3 (high, normal, low) | High = financial, Normal = notifications, Low = analytics |

---

## High-Level Design (Brief — 5 minutes)

```
+------------------+
| Task API         |     Create, cancel, query tasks
| (CRUD)           |
+--------+---------+
         |
         v
+------------------+     +-------------------+
| Task Store       |     | Timer Service     |     Wakes up tasks at
| (MySQL/Postgres  |<--->| (per-partition    |     scheduled time
|  partitioned by  |     |  tick every 1s)   |
|  task_id)        |     +--------+----------+
+------------------+              |
                                  | enqueue ready tasks
                                  v
                       +-------------------+
                       | Task Queue        |     Priority queue for
                       | (Kafka / SQS /    |     ready-to-run tasks
                       |  Redis Sorted Set)|
                       +--------+----------+
                                |
              +-----------------+-----------------+
              |                 |                 |
              v                 v                 v
       +-----------+     +-----------+     +-----------+
       | Worker 1  |     | Worker 2  |     | Worker N  |
       | (executes |     |           |     |           |
       |  tasks)   |     |           |     |           |
       +-----------+     +-----------+     +-----------+
              |
              v
       +-------------------+
       | Dead Letter Queue |     Failed tasks after max retries
       +-------------------+

       +-------------------+
       | Scheduler Leader  |     Single leader via Raft/lease
       | Election          |     Prevents duplicate scheduling
       +-------------------+
```

**Why this architecture?**: This mirrors how kube-scheduler works in Kubernetes — a control loop watches for unscheduled pods (tasks), selects a node (worker), and binds them. The key insight is separating task storage (durable, queryable) from task queuing (fast, ordered by priority/time). The timer service is the "scheduling loop" that moves tasks from stored to queued when their time arrives.

---

## Core Concepts Deep Dive

### Concept 1: Time-Based Partitioning — The Timing Wheel

**What it is**: A timing wheel is a circular buffer of time slots. Each slot represents a time interval (e.g., 1 second). Tasks are placed in the slot corresponding to their scheduled time. A pointer advances one slot per tick. When the pointer reaches a slot, all tasks in that slot are dequeued for execution. This is O(1) for insert and O(1) amortized for expiration.

**How it applies here**: The timer service uses a hierarchical timing wheel. Level 1: 3,600 slots (1 second each, covering 1 hour). Level 2: 24 slots (1 hour each, covering 1 day). Level 3: 365 slots (1 day each, covering 1 year). When a task is scheduled 3 days from now, it goes into Level 3. As time progresses, it cascades down to Level 2, then Level 1, and finally fires.

**The math/mechanics**: With 100M active tasks, most are in upper levels. Level 1 (current hour): ~6M tasks (500M/day / 24 * peak factor). Level 2 (today): ~20M tasks. Level 3 (future): ~74M tasks. Level 1 memory: 6M tasks x 1KB = 6GB — fits in memory. Kafka's delayed message delivery uses a similar approach internally.

**Connection to Kubernetes**: kube-scheduler's scheduling queue has three sub-queues: activeQ (ready to schedule now — like our Level 1), backoffQ (failed, waiting for retry — like our retry mechanism), and unschedulableQ (can't schedule yet due to constraints — like our Level 2/3). The control loop pops from activeQ, tries to schedule, and moves to backoffQ on failure.

**Common misconception**: Candidates propose a database query `SELECT * FROM tasks WHERE scheduled_time <= NOW()` running every second. This works at small scale but at 100M tasks, this query is expensive even with an index. The timing wheel avoids the query entirely — tasks self-select when their slot is reached.

### Concept 2: At-Least-Once Delivery & Idempotency

**What it is**: In a distributed system, guaranteeing that a task executes exactly once is extremely hard (requires distributed transactions). At-least-once is achievable: if a worker crashes mid-execution, the task is re-delivered to another worker. The task may execute more than once, so handlers must be idempotent.

**How it applies here**: When a worker picks up a task from the queue, the task remains in the queue with a visibility timeout (SQS model) or the consumer offset isn't committed (Kafka model). If the worker completes successfully, it acknowledges the task (deletes from queue or commits offset). If the worker crashes, the visibility timeout expires and the task becomes visible again for another worker.

**The math/mechanics**: Visibility timeout should be > expected execution time + buffer. For a task that runs for 5 minutes, set timeout to 10 minutes. If the worker is still running but slow, it must send heartbeats to extend the timeout — otherwise a second worker picks up the same task. This is the same pattern as Kubernetes lease renewals — a node must renew its lease to prove it's alive.

**Common misconception**: Candidates claim "exactly-once" delivery is easy. It's not. Even with Kafka's transactional consumers, you get exactly-once within the Kafka boundary — but the side effect (sending an email, charging a credit card) may still duplicate if the worker crashes after the side effect but before committing. True exactly-once requires the side effect to be part of the same transaction as the acknowledgment (e.g., writing results to a Kafka topic in the same transaction).

### Concept 3: Priority Scheduling & Starvation Prevention

**What it is**: Tasks have different priorities. A billing task should execute before a marketing email. But pure priority queuing leads to starvation — low-priority tasks never execute during high-traffic periods.

**How it applies here**: Separate queues per priority level. Workers poll high-priority first, then normal, then low. To prevent starvation, use weighted fair queuing: for every 10 high-priority tasks, pull 3 normal and 1 low. Alternatively, age-based priority boosting: a low-priority task that's been waiting more than 5 minutes gets promoted to normal priority.

**Connection to Kubernetes**: kube-scheduler uses priority classes (PriorityClass resource). High-priority pods can preempt lower-priority ones. But preemption is a last resort — the scheduler first tries to find nodes with available capacity. Our task scheduler follows the same principle: prioritize but avoid preemption unless absolutely necessary (preemption wastes the work already done on the preempted task).

**Common misconception**: Candidates use a single priority queue (min-heap by `(priority, scheduled_time)`). This works for small scale but doesn't allow independent scaling of priority levels. With separate queues, you can have 10 workers dedicated to high-priority and 90 for normal — adjustable at runtime.

### Concept 4: Failure Handling — Retries, Backoff & Dead Letters

**What it is**: Tasks fail. The scheduler must retry with exponential backoff, cap retries, and eventually move permanently failed tasks to a dead-letter queue (DLQ) for human investigation.

**How it applies here**: Retry policy: attempt 1 immediately, attempt 2 after 1 minute, attempt 3 after 5 minutes, attempt 4 after 30 minutes, attempt 5 after 2 hours. After 5 failures, move to DLQ. The retry schedule uses the timing wheel — a failed task is re-inserted at the appropriate future slot.

**The math/mechanics**: With 500M executions/day and 2% failure rate = 10M failures/day. 95% succeed on retry 1 = 9.5M re-executions. 4% on retry 2 = 400K. 1% go to DLQ = 100K/day. DLQ processing is manual (on-call investigates) or automated (replay after underlying issue is fixed).

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: The Scheduling Loop — How Tasks Fire at the Right Time

**Interviewer**: "Walk me through exactly what happens when a task is scheduled for 3:00:05 PM. How does it actually fire at that time?"

**You**: "When the task is created via API, it's written to the task store (MySQL, partitioned by task_id) with `scheduled_time = 2026-02-12T15:00:05Z` and `status = SCHEDULED`. It's also inserted into the timing wheel. Since 3:00:05 PM is, say, 2 hours away, it goes into the Level 2 wheel (hourly slots) at slot 15 (3 PM hour).

The timer service runs a tick every second. At 2:00 PM, the Level 2 pointer reaches the 3 PM slot. All tasks in this slot are cascaded down to Level 1 (second-level slots). Our task lands in Level 1 slot 5 (second 5 of the 3:00 PM minute).

At 3:00:05 PM, the Level 1 pointer reaches slot 5. The timer service dequeues our task, changes its status to QUEUED in the task store, and publishes it to the task queue (Kafka topic partitioned by priority). A worker consumes the message, executes the task, and acknowledges completion. Total time from scheduled to execution: ideally < 1 second (one tick)."

**Interviewer**: "The timer service is a single process? What if it crashes?"

**You**: "The timer service runs as an active-passive pair with leader election (via etcd lease or ZooKeeper — same mechanism as Kubernetes controller-manager leader election). The leader runs the tick loop. The standby monitors the leader's lease. If the lease expires (leader crashed), the standby acquires the lease and becomes the new leader.

On failover, the new leader must recover the timing wheel state. It does this by querying the task store: `SELECT * FROM tasks WHERE status = 'SCHEDULED' AND scheduled_time BETWEEN NOW() AND NOW() + 1 HOUR`. This rebuilds the Level 1 wheel. Level 2 and 3 are rebuilt lazily (tasks cascade down as time progresses). Failover time: lease timeout (~10 seconds) + wheel rebuild (~5 seconds for 6M tasks) = ~15 seconds. Tasks scheduled during this window fire up to 15 seconds late."

**Interviewer**: "15 seconds of delay is a lot. How do you reduce it?"

**You**: "Two improvements. First, reduce the lease timeout to 3 seconds (with frequent heartbeats every 1 second) — this is what etcd uses for Kubernetes leases. Second, instead of active-passive, use active-active with partitioned ownership. Partition the task space by task_id hash into, say, 16 partitions. Each partition has its own timer service instance with its own timing wheel. With 16 partitions, a single instance failure only affects 1/16 of tasks, and failover for that partition takes 3-5 seconds. This is similar to how Kubernetes shards controller responsibilities across multiple controller-manager instances."

**Interviewer**: "How do you prevent duplicate firing? If the leader crashes right after dequeuing a task but before updating the task store?"

**You**: "The task store is the source of truth. The timer service uses a compare-and-swap (CAS) operation: `UPDATE tasks SET status = 'QUEUED' WHERE task_id = X AND status = 'SCHEDULED'`. If the old leader already dequeued and updated, the new leader's CAS fails (status is already QUEUED), and it skips the task. If the old leader dequeued but crashed before updating, the CAS succeeds — the task is re-dequeued. This means the task might be published to Kafka twice, but Kafka consumer deduplication (based on task_id as the idempotency key) or the worker's idempotent execution handles it."

### Deep Dive Path 2: Worker Execution & Failure Handling

**Interviewer**: "A worker picks up a task and starts executing. What guarantees do we have?"

**You**: "The worker consumes a message from Kafka. The message contains the task_id and payload. The worker: (1) updates task status to RUNNING in the task store, (2) executes the task handler (calls an API, runs a computation, etc.), (3) on success, updates status to COMPLETED and commits the Kafka offset, (4) on failure, updates status to FAILED with error details.

If the worker crashes during execution (between steps 1 and 3), the Kafka consumer group rebalance detects the dead consumer and reassigns the partition. The uncommitted message is re-delivered to another worker. That worker sees the task status is RUNNING — it must decide: is the previous execution still running (worker is just slow) or did it crash? It checks the task's last heartbeat timestamp. If no heartbeat for > visibility timeout, assume crashed and re-execute."

**Interviewer**: "The task is 'charge customer's credit card.' Duplicate execution is catastrophic. How do you handle this?"

**You**: "For non-idempotent operations like charging a credit card, we need an idempotency key at the executor level. The task record includes a unique `execution_id` (UUID generated when the task is created). The payment service uses this as an idempotency key: `POST /v1/charges { idempotency_key: execution_id, amount: ..., card: ... }`. If the charge was already processed (first worker succeeded but crashed before acking), the payment service returns the previous result without re-charging. This pushes the exactly-once guarantee to the downstream service, which is the correct pattern — Stripe, for example, supports idempotency keys natively.

The task scheduler provides at-least-once delivery; the task handler provides idempotency. Together, they achieve effectively-once execution."

**Interviewer**: "A task keeps failing. Walk me through the retry and DLQ flow."

**You**: "The retry policy is configurable per task. Default: exponential backoff with jitter. Attempt 1: immediate. Attempt 2: 60s +/- 15s jitter. Attempt 3: 300s +/- 60s. Attempt 4: 1800s. Attempt 5: 7200s. Max 5 attempts.

On each failure, the worker updates the task store: `status = RETRY, attempt_count += 1, next_retry_at = NOW() + backoff`. The task is re-inserted into the timing wheel at `next_retry_at`. The jitter prevents thundering herd on correlated failures (e.g., a downstream service is down and 1000 tasks all retry at the same second).

After 5 failures, `status = DEAD_LETTER`. The task is published to a DLQ topic in Kafka. An alerting system notifies the task owner. The DLQ has a separate UI where operators can inspect failed tasks, fix the underlying issue, and replay them. Replay is just re-publishing the task to the main queue with reset attempt count."

### Deep Dive Path 3: Recurring Tasks & Cron Scheduling

**Interviewer**: "How do you handle recurring tasks? Run this every 5 minutes."

**You**: "Recurring tasks are defined with a cron expression: `*/5 * * * *` (every 5 minutes). The task store has a `schedule` field alongside `scheduled_time`. The scheduling loop: when a recurring task executes successfully, the scheduler computes the next execution time from the cron expression and creates a new task instance with that time. Each execution is a separate row in the task store with a unique execution_id but the same recurring_task_id.

For efficiency, I don't pre-create all future instances. I create only the next instance on each completion (or on each successful scheduling). This is lazy expansion — similar to how a Kubernetes CronJob controller creates Jobs on schedule rather than pre-creating them."

**Interviewer**: "What if the scheduler is down for 30 minutes and misses 6 executions of a 5-minute cron?"

**You**: "Configurable catch-up policy. Option 1: `skip_missed` — compute the next future execution time and schedule that. The 6 missed executions are gone. This is right for 'send daily report' — sending 6 reports at once is wrong. Option 2: `catch_up` — schedule all missed executions immediately. Right for 'process pending invoices every 5 minutes' — you need to process the backlog. Option 3: `catch_up_once` — schedule one catch-up execution to handle the entire missed window. This is the default for Kubernetes CronJobs (`startingDeadlineSeconds` controls this behavior).

Implementation: on recovery, the scheduler queries `SELECT * FROM recurring_tasks WHERE next_scheduled_time < NOW()`. For each, it applies the catch-up policy. With 100K recurring tasks, this query returns ~600 missed tasks for a 30-minute outage — trivially processed."

**Interviewer**: "How does this compare to kube-scheduler architecturally?"

**You**: "Very similar at the core. kube-scheduler is a specialized task scheduler where the 'task' is a Pod and the 'worker' is a Node. kube-scheduler's control loop: (1) watch for unscheduled Pods (new tasks), (2) filter nodes that can run the Pod (worker capacity/constraints), (3) score remaining nodes (priority/bin-packing), (4) bind Pod to best node (assign task to worker).

Our general scheduler differs in that: (1) we have time-based triggering (kube-scheduler triggers immediately), (2) we have recurring tasks (kube CronJob controller handles this separately), (3) we have priority queuing (kube uses PriorityClass for preemption). But the architectural pattern — a control loop watching a task store and dispatching to workers — is identical. The lesson from Kubernetes: keep the scheduler stateless and derive all state from the task store (etcd for K8s, MySQL/Postgres for us). This simplifies failover enormously."

---

## How Real Companies Built This

- **Uber (Cherami / Cadence / Temporal)**: Built Cadence (now open-sourced as Temporal) for reliable task scheduling and workflow orchestration. Temporal uses a persistence layer (Cassandra/MySQL) for task state, a matching service for task-to-worker assignment, and history service for replay. Key insight: workflows as code — instead of configuring retries/timeouts, you write them in Go/Java. Blog: https://www.uber.com/blog/cadence-architecture/

- **Google (Borg / Cloud Tasks)**: Borg is the original container orchestrator (predecessor to Kubernetes). Google Cloud Tasks provides a managed task queue with scheduled delivery. Uses a Paxos-based coordinator for exactly-once delivery within the queue boundary. The Omega paper (https://research.google/pubs/pub41684/) describes the shared-state scheduling approach that influenced Kubernetes.

- **Meta (Async Task Framework)**: Uses a combination of MySQL-backed task store + Kafka queues for execution. Processes billions of tasks daily (notification delivery, feed ranking, data pipeline triggers). Key optimization: tasks are batched by type — instead of 1M individual "send push notification" tasks, batch them into "send push notification to [1M user IDs]".

- **Airbnb (Chronos / custom)**: Originally used Chronos (Mesos-based cron scheduler), migrated to a custom solution with MySQL + SQS. Key learning: Chronos's dependency on ZooKeeper was an operational burden. Their custom solution uses simpler leader election via database row locking.

- **Key lesson**: Every large company ends up building a custom task scheduler because the requirements (billions of tasks, exactly-once-ish delivery, complex retry policies, task DAGs) exceed what off-the-shelf solutions provide. Temporal is the closest to a general-purpose solution.

---

## The Complete Reference Design

### API Design
```
# Create a one-time task
POST /v1/tasks
Request: {
  "task_type": "send_email",
  "scheduled_time": "2026-02-12T15:00:05Z",
  "priority": "normal",
  "payload": {
    "to": "user@example.com",
    "template": "welcome"
  },
  "retry_policy": {
    "max_attempts": 5,
    "backoff": "exponential",
    "initial_delay_seconds": 60
  },
  "idempotency_key": "welcome-email-user-123"
}
Response 201: {
  "task_id": "task-abc123",
  "status": "SCHEDULED",
  "scheduled_time": "2026-02-12T15:00:05Z"
}

# Create a recurring task
POST /v1/tasks/recurring
Request: {
  "task_type": "generate_report",
  "schedule": "0 */6 * * *",    # every 6 hours
  "priority": "low",
  "payload": { "report_type": "daily_summary" },
  "catch_up_policy": "skip_missed",
  "timezone": "America/Los_Angeles"
}
Response 201: {
  "recurring_task_id": "rt-xyz789",
  "next_execution": "2026-02-12T18:00:00Z"
}

# Get task status
GET /v1/tasks/task-abc123
Response 200: {
  "task_id": "task-abc123",
  "status": "COMPLETED",
  "scheduled_time": "2026-02-12T15:00:05Z",
  "started_at": "2026-02-12T15:00:05.234Z",
  "completed_at": "2026-02-12T15:00:05.891Z",
  "attempt_count": 1,
  "worker_id": "worker-17"
}

# Cancel a task
DELETE /v1/tasks/task-abc123
Response 200: { "status": "CANCELLED" }
```

### Database Schema
```sql
CREATE TABLE tasks (
    task_id           VARCHAR(36) PRIMARY KEY,
    recurring_task_id VARCHAR(36),              -- NULL for one-time tasks
    task_type         VARCHAR(100) NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED',
                      -- SCHEDULED, QUEUED, RUNNING, COMPLETED, FAILED, RETRY,
                      -- DEAD_LETTER, CANCELLED
    priority          SMALLINT NOT NULL DEFAULT 1,  -- 0=high, 1=normal, 2=low
    scheduled_time    TIMESTAMP NOT NULL,
    started_at        TIMESTAMP,
    completed_at      TIMESTAMP,
    payload           JSONB NOT NULL,
    idempotency_key   VARCHAR(200),
    attempt_count     SMALLINT DEFAULT 0,
    max_attempts      SMALLINT DEFAULT 5,
    next_retry_at     TIMESTAMP,
    worker_id         VARCHAR(50),
    last_heartbeat    TIMESTAMP,
    error_message     TEXT,
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW(),
    partition_key     INTEGER GENERATED ALWAYS AS (
        abs(hashtext(task_id)) % 16
    ) STORED  -- for sharding
);

CREATE INDEX idx_tasks_scheduled ON tasks(scheduled_time, status)
    WHERE status IN ('SCHEDULED', 'RETRY');
CREATE INDEX idx_tasks_status ON tasks(status, priority);
CREATE INDEX idx_tasks_recurring ON tasks(recurring_task_id);
CREATE UNIQUE INDEX idx_tasks_idempotency ON tasks(idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE TABLE recurring_tasks (
    recurring_task_id VARCHAR(36) PRIMARY KEY,
    task_type         VARCHAR(100) NOT NULL,
    schedule          VARCHAR(100) NOT NULL,     -- cron expression
    timezone          VARCHAR(50) DEFAULT 'UTC',
    priority          SMALLINT DEFAULT 1,
    payload           JSONB NOT NULL,
    catch_up_policy   VARCHAR(20) DEFAULT 'skip_missed',
    is_active         BOOLEAN DEFAULT TRUE,
    last_executed_at  TIMESTAMP,
    next_scheduled_at TIMESTAMP,
    created_at        TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recurring_next ON recurring_tasks(next_scheduled_at)
    WHERE is_active = TRUE;
```

### Key Algorithms
```python
import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, List, Callable

@dataclass
class Task:
    task_id: str
    task_type: str
    scheduled_time: float       # unix timestamp
    priority: int               # 0=high, 1=normal, 2=low
    payload: dict
    attempt_count: int = 0
    max_attempts: int = 5

# --- Hierarchical Timing Wheel ---
class TimingWheel:
    """
    Hierarchical timing wheel for O(1) task scheduling.
    Inspired by Kafka's implementation (kafka.utils.timer).
    """
    def __init__(self, tick_ms=1000, wheel_size=3600):
        self.tick_ms = tick_ms
        self.wheel_size = wheel_size
        self.slots = [[] for _ in range(wheel_size)]
        self.current_slot = 0
        self.current_time = int(time.time())
        self.overflow_wheel = None  # next level for far-future tasks

    def add(self, task: Task):
        delay_seconds = int(task.scheduled_time - self.current_time)
        if delay_seconds < 0:
            delay_seconds = 0  # fire immediately
        if delay_seconds < self.wheel_size:
            slot = (self.current_slot + delay_seconds) % self.wheel_size
            self.slots[slot].append(task)
        else:
            # Overflow to next level
            if self.overflow_wheel is None:
                self.overflow_wheel = TimingWheel(
                    tick_ms=self.tick_ms * self.wheel_size,
                    wheel_size=self.wheel_size
                )
            self.overflow_wheel.add(task)

    def advance(self) -> List[Task]:
        """Advance one tick, return tasks ready to fire."""
        self.current_slot = (self.current_slot + 1) % self.wheel_size
        self.current_time += 1
        ready = self.slots[self.current_slot]
        self.slots[self.current_slot] = []
        # Cascade from overflow wheel
        if self.overflow_wheel and self.current_slot == 0:
            cascaded = self.overflow_wheel.advance()
            for task in cascaded:
                self.add(task)  # re-insert at appropriate slot
        return ready


# --- Worker Pool with Priority Queuing ---
class WorkerPool:
    """
    Processes tasks with priority-based weighted fair queuing.
    Similar to kube-scheduler's activeQ processing.
    """
    def __init__(self, num_workers=10, weights=(10, 3, 1)):
        self.queues = {0: [], 1: [], 2: []}  # priority -> task list
        self.weights = weights  # high, normal, low
        self.lock = threading.Lock()

    def enqueue(self, task: Task):
        with self.lock:
            self.queues[task.priority].append(task)

    def dequeue(self) -> Optional[Task]:
        """Weighted fair dequeue to prevent starvation."""
        with self.lock:
            for priority, weight in enumerate(self.weights):
                for _ in range(weight):
                    if self.queues[priority]:
                        return self.queues[priority].pop(0)
        return None


# --- Retry with Exponential Backoff ---
def compute_next_retry(attempt_count: int, base_delay: int = 60) -> float:
    """Exponential backoff with jitter."""
    import random
    delay = base_delay * (2 ** (attempt_count - 1))
    delay = min(delay, 7200)  # cap at 2 hours
    jitter = random.uniform(0.75, 1.25)
    return time.time() + delay * jitter


# --- Scheduling Loop (analogous to kube-scheduler's Run()) ---
class SchedulerLoop:
    """
    Main scheduling loop. Analogous to kube-scheduler:
    - Watch for new tasks (unscheduled pods)
    - Move ready tasks to execution queue (bind pod to node)
    - Handle retries (backoff queue)
    """
    def __init__(self, timing_wheel: TimingWheel,
                 worker_pool: WorkerPool,
                 task_store):  # database client
        self.wheel = timing_wheel
        self.pool = worker_pool
        self.store = task_store
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            # 1. Advance timing wheel (tick)
            ready_tasks = self.wheel.advance()

            # 2. Enqueue ready tasks to worker pool
            for task in ready_tasks:
                # CAS: only enqueue if still SCHEDULED
                if self.store.cas_status(task.task_id,
                                         expected='SCHEDULED',
                                         new='QUEUED'):
                    self.pool.enqueue(task)

            # 3. Sleep until next tick
            time.sleep(1)

    def stop(self):
        self.running = False
```

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Task store (database) | 100M active tasks x 2KB each | 200GB (fits in single Postgres, shard for throughput) |
| Timing wheel memory | Level 1: 6M tasks x 1KB | 6GB RAM per scheduler instance |
| Task queue (Kafka) | 20K tasks/sec peak x 1KB | 20MB/s throughput |
| Workers | 20K tasks/sec / 100 tasks/sec/worker | 200 workers (for 100ms avg tasks) |
| Scheduler instances | 16 partitions | 16 instances (active-active) |
| Dead letter queue | 100K tasks/day x 2KB | Negligible |
| Database write QPS | 20K task updates/sec (status changes) | Sharded MySQL/Postgres |
| Database read QPS | 20K reads/sec (task lookups) + scheduler queries | Read replicas |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Designs task queue with workers, handles basic retries, understands at-least-once | Builds a simple scheduled task system with SQS + Lambda, handles retries with exponential backoff |
| Staff | Designs timing wheel for efficient scheduling, handles leader election for scheduler, reasons about exactly-once semantics, draws Kubernetes parallels | Implements hierarchical timing wheel, designs CAS-based deduplication, explains the at-least-once + idempotency = effectively-once pattern, partitions scheduler for availability |
| Principal | Designs the system as a platform (multi-tenant task scheduling), reasons about task DAGs and workflow orchestration, considers priority inversion and starvation, thinks about observability (task SLOs, latency histograms) | Proposes Temporal-like workflow engine, designs SLO monitoring for task latency, considers multi-tenant isolation (noisy neighbor prevention), designs the task scheduler as an internal platform with self-service API |

---

## Red Flags & Common Mistakes
- **Polling the database every second for due tasks**: `SELECT WHERE scheduled_time <= NOW()` on 100M rows is expensive. Use a timing wheel or sorted data structure (Redis sorted set, delay queue).
- **No leader election for the scheduler**: Without coordination, multiple scheduler instances will fire the same task multiple times. You need either leader election or partitioned ownership.
- **Claiming "exactly-once" is easy**: It requires distributed transactions or idempotency at the handler level. Don't hand-wave this — explain the pattern clearly.
- **No failure handling story**: What happens when tasks fail? Retries, backoff, dead-letter queues are essential. An interviewer will always ask.
- **Ignoring priority starvation**: Pure priority queuing means low-priority tasks may never run during peak load. Weighted fair queuing or aging is needed.
- **Forgetting about recurring task catch-up**: If the scheduler was down for an hour, what happens to missed cron executions? This must be configurable.
- **Not mentioning observability**: Task scheduling latency (how late was the task vs. scheduled time), execution duration, failure rates by type — these metrics are critical for operating the system.
