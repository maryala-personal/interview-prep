# Design a Distributed Log System (Kafka)

> **Companies**: Confluent, LinkedIn, Uber, Meta, Amazon (Kinesis), Google (Pub/Sub), Stripe | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: This is the fundamental distributed systems building block question. A distributed log underpins event streaming, change data capture, message queuing, and event sourcing. The interviewer wants to see you reason about log-structured storage, replication for durability (ISR, leader election), consumer group coordination, exactly-once semantics, and the trade-off between throughput and latency. This question separates candidates who understand distributed systems primitives from those who just use them as black boxes.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**Questions that show the interviewer you know what you're doing:**

- "What's the throughput requirement? Millions of messages/second? What's the average message size?"
- "What ordering guarantees? Global ordering, per-partition ordering, or no ordering?"
- "What delivery semantics? At-most-once, at-least-once, or exactly-once?"
- "What's the acceptable end-to-end latency? Milliseconds (real-time) or seconds (batch-friendly)?"
- "How long do we retain messages? Hours, days, forever? Do consumers need to replay from arbitrary offsets?"
- "How many topics? Thousands or millions?"
- "Multi-datacenter replication? Active-active or active-passive?"
- "Consumer patterns — fan-out (pub/sub) or load-balanced (queue)? Both?"

### Working Assumptions
| Parameter | Value | Derivation |
|-----------|-------|------------|
| Message throughput | 2M messages/sec | Large-scale event streaming platform |
| Average message size | 1KB | Typical for event data (JSON/Avro/Protobuf) |
| Data throughput | 2GB/s write, 6GB/s read (3x fan-out) | 3 consumers per message on average |
| Topics | 10,000 | Microservices architecture with topic-per-entity |
| Partitions | 100,000 total | Average 10 partitions per topic |
| Replication factor | 3 | Standard for durability |
| Retention | 7 days default, configurable up to 30 days | Replay capability |
| End-to-end latency | p50 < 10ms, p99 < 100ms | Real-time event processing |
| Ordering guarantee | Per-partition | Standard Kafka model |
| Delivery semantics | At-least-once default, exactly-once available | Idempotent producers + transactional consumers |
| Consumer groups | 5,000 | Many teams consuming shared topics |

---

## High-Level Design (Brief — 5 minutes)

```
Producers
    |
    v (hash(key) -> partition)
+-------------------+
| Broker Cluster    |
| +---------+       |     Partition 0: [msg0, msg1, msg2, ...]
| |Broker 1 |       |     Partition 1: [msg0, msg1, msg2, ...]
| |(Leaders: |      |     Partition 2: [msg0, msg1, msg2, ...]
| | P0, P3)  |      |
| +---------+       |     Each partition:
| +---------+       |       - Leader: handles all reads/writes
| |Broker 2 |       |       - Followers: replicate from leader
| |(Leaders: |      |       - ISR (In-Sync Replicas): followers that
| | P1, P4)  |      |         are caught up
| +---------+       |
| +---------+       |
| |Broker 3 |       |
| |(Leaders: |      |
| | P2, P5)  |      |
| +---------+       |
+-------------------+
         ^
         |
+-------------------+     +-------------------+
| Controller        |     | ZooKeeper / KRaft |
| (leader election, |<--->| (metadata, leader |
|  partition mgmt)  |     |  election)        |
+-------------------+     +-------------------+
         |
         v
+-------------------+
| Consumer Groups   |
| Group A: C1->P0,  |     Each consumer in a group
|   C2->P1, C3->P2  |     owns exclusive partitions
| Group B: C1->P0,  |     (load-balanced consumption)
|   C2->P1,P2       |
+-------------------+
```

**Why this architecture?**: A distributed log is fundamentally a partitioned, replicated, append-only data structure. Partitioning provides parallelism (each partition is an independent ordered log). Replication provides durability (survive broker failures without data loss). The append-only nature provides high write throughput (sequential disk I/O) and offset-based consumption (consumers track their position with a simple integer). This is why Kafka achieves millions of messages/sec — the design plays to the strengths of disk and network I/O.

---

## Core Concepts Deep Dive

### Concept 1: The Log — Append-Only, Offset-Based

**What it is**: Each partition is an ordered, immutable sequence of messages. Each message gets a monotonically increasing offset (0, 1, 2, ...). Producers append to the end. Consumers read from any offset and advance sequentially. The log is segmented into files on disk (default 1GB segments) and old segments are deleted based on retention policy (time or size).

**How it applies here**: A partition's on-disk representation:
```
segment-00000000.log    (offsets 0-999999)
segment-00000000.index  (offset -> file position mapping)
segment-00000000.timeindex (timestamp -> offset mapping)
segment-01000000.log    (offsets 1000000-1999999)
...
```
Writes are sequential appends to the active segment — no random I/O. This is why Kafka's write throughput is close to the disk's sequential write speed (hundreds of MB/s per broker). The OS page cache handles read buffering — frequently accessed data is served from RAM, not disk.

**The math/mechanics**: Sequential write to disk: ~600MB/s on modern SSDs, ~200MB/s on spinning disks. Kafka writes at near this speed because it bypasses the database abstraction entirely — it IS the filesystem. Random writes (what a database does) are ~100x slower. This is the fundamental insight behind Kafka's performance.

**Common misconception**: Candidates think Kafka needs fast SSDs. Kafka actually performs well on spinning disks because its I/O pattern is purely sequential. SSDs help with random reads (consumers fetching old offsets) but sequential write throughput is comparable. LinkedIn ran Kafka on spinning disks for years.

### Concept 2: In-Sync Replicas (ISR) — The Replication Model

**What it is**: Each partition has one leader and N-1 followers. The leader handles all reads and writes. Followers replicate by fetching from the leader (pull-based). A follower is "in-sync" (in the ISR set) if it has replicated all messages within a configurable lag threshold (`replica.lag.time.max.ms`, default 30 seconds). If a follower falls behind, it's removed from ISR.

**How it applies here**: With replication factor 3 (1 leader + 2 followers), the ISR normally contains all 3 replicas. When a producer sends a message with `acks=all`, the leader waits for ALL replicas in the ISR to acknowledge before responding. If the ISR shrinks to just the leader (both followers are behind), `acks=all` only waits for the leader — this is dangerous because a leader crash now means data loss. `min.insync.replicas=2` prevents this: the broker rejects writes when ISR < 2, trading availability for durability.

**The math/mechanics**: Replication throughput: each follower fetches from the leader at near-network speed. With a 10Gbps network link between brokers, each follower can replicate at ~1.2GB/s. For a partition doing 50MB/s write throughput, replication is trivially handled. The bottleneck is the number of partitions per broker — each partition requires a fetch thread, and with 10,000 partitions per broker, the overhead of managing fetch connections becomes significant.

**Common misconception**: Candidates describe Kafka replication as synchronous Raft-style consensus. It's not. Kafka's ISR model is more flexible: it doesn't require a quorum for every write (unlike Raft). Instead, the ISR set dynamically adjusts — fast followers stay in, slow ones drop out. This allows higher throughput than Raft at the cost of potentially more nuanced failure modes. The KRaft protocol (Kafka's move away from ZooKeeper) uses Raft only for metadata consensus, not for data replication.

### Concept 3: Consumer Groups & Partition Assignment

**What it is**: A consumer group is a set of consumers that cooperatively consume a topic. Each partition is assigned to exactly one consumer in the group — this ensures each message is processed once within the group. If a consumer dies, its partitions are reassigned to surviving consumers (rebalance).

**How it applies here**: Topic T has 6 partitions. Consumer Group A has 3 consumers. Assignment: C1 gets P0,P1; C2 gets P2,P3; C3 gets P4,P5. If C3 dies, rebalance: C1 gets P0,P1,P4; C2 gets P2,P3,P5. If we add C4: C1->P0,P1; C2->P2,P3; C3->P4; C4->P5. Max parallelism = partition count (if consumers > partitions, extras are idle).

**The math/mechanics**: Rebalance protocol (Kafka's cooperative sticky assignor): (1) C3 dies, group coordinator detects via heartbeat timeout (10s default), (2) coordinator triggers rebalance by sending REBALANCE signal to remaining consumers, (3) consumers send JoinGroup with their subscription, (4) coordinator picks a leader consumer to compute assignment, (5) leader computes new assignment (sticky to minimize partition movement), (6) coordinator sends assignments to all consumers. During rebalance (typically 5-30 seconds), no messages are consumed from affected partitions — this is the "stop-the-world" problem.

**The fix**: Cooperative incremental rebalancing (Kafka 2.4+). Instead of revoking all partitions and reassigning, only the partitions that need to move are revoked. C1 and C2 keep their partitions; only C3's partitions (P4,P5) are reassigned. Consumption continues uninterrupted for C1 and C2. This reduces rebalance disruption from all-partitions-paused to only-moving-partitions-paused.

**Common misconception**: Candidates treat consumer groups as "just load balancing" and don't discuss the rebalance problem. In production, rebalance storms (frequent rebalances due to flaky consumers, slow heartbeats, or misconfigured session timeouts) are the #1 operational issue with Kafka consumers. Understanding the rebalance protocol is essential.

### Concept 4: Exactly-Once Semantics (EOS)

**What it is**: Kafka achieves exactly-once through two mechanisms: (1) idempotent producers — the broker deduplicates messages using a producer ID + sequence number, preventing duplicates from retries, and (2) transactional producers — a producer can atomically write to multiple partitions AND commit consumer offsets in a single transaction, enabling exactly-once stream processing (read-process-write patterns).

**How it applies here**: Without EOS: producer sends message, broker acks, ack is lost (network issue), producer retries, broker now has duplicate. With idempotent producer: broker tracks (producer_id, sequence_number) and rejects duplicates. With transactions: a stream processor reads from topic A, processes, and writes to topic B + commits its topic A offset — all atomically. If the processor crashes mid-way, the transaction is aborted and no partial results are visible.

**The math/mechanics**: Idempotent producer overhead: the broker maintains a map of (producer_id, partition) -> last_5_sequence_numbers. With 10K producers x 100K partitions = 1B entries x ~40 bytes = ~40GB. This is too much to store in memory for all producers. Kafka keeps only the last 5 sequences per producer per partition, and old entries are checkpointed to disk. Transactional overhead: 2-phase commit protocol adds ~2-5ms latency per transaction.

**Common misconception**: "Exactly-once" in Kafka means within the Kafka boundary (from producer to consumer within the same Kafka cluster). If your consumer writes to an external system (database, API), you're back to at-least-once unless the external system also supports idempotency. Kafka Streams' exactly-once works because both the input (topic A) and output (topic B + offsets) are within Kafka, so the transaction can span them.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Writing & Replication — End-to-End

**Interviewer**: "A producer sends a message to a topic with 6 partitions. Walk me through everything that happens until the message is durable."

**You**: "The producer has the topic's partition metadata cached (fetched from any broker on startup). It determines the target partition: if the message has a key, it computes `hash(key) % 6`. If no key, round-robin. Say it selects partition 3.

The producer checks its metadata cache for the leader of partition 3 — say it's broker 2. It sends a ProduceRequest to broker 2 containing the message (key, value, headers, timestamp). The producer batches messages — it accumulates messages for up to `linger.ms` (default 0, but typically set to 5-50ms) or until `batch.size` (default 16KB) is reached. Batching amortizes the network overhead.

Broker 2 receives the batch. It appends the messages to partition 3's active log segment (sequential write to the OS page cache — no fsync per message by default for throughput). It assigns offsets (monotonically increasing). If `acks=all`, broker 2 waits for all ISR members to replicate.

Followers (brokers 1 and 3 for this partition) continuously fetch from the leader. They send FetchRequests to broker 2 for partition 3, starting from their last replicated offset. Broker 2 responds with the new messages. Followers append to their local log segments and send acknowledgment back to the leader. Once all ISR members have replicated (or just the leader if `acks=1`), broker 2 advances the 'high watermark' (the offset up to which all ISR members have replicated) and sends the ProduceResponse to the producer with the assigned offset."

**Interviewer**: "What's the high watermark and why does it matter?"

**You**: "The high watermark (HW) is the offset up to which all ISR members have replicated. Consumers can only read up to the HW — not beyond. This prevents a consumer from reading a message that only exists on the leader. If the leader crashes before followers replicate, that message is lost, and the consumer would have read a phantom message.

Example: leader at offset 100, follower 1 at 98, follower 2 at 99. HW = min(100, 98, 99) = 98. Consumers can read up to offset 98. When follower 1 catches up to 99, HW advances to 99.

There's a subtle bug Kafka had before KIP-101: the follower's HW was updated one fetch cycle behind the leader's HW, which could cause data loss during leader failover under certain race conditions. KIP-101 introduced the 'leader epoch' to fix this — each new leader starts a new epoch, and followers truncate their logs to the end of the previous leader's epoch before fetching from the new leader."

**Interviewer**: "Leader of partition 3 (broker 2) crashes. What happens?"

**You**: "The controller (a special broker elected via KRaft/ZooKeeper) detects broker 2's failure via heartbeat timeout (~10 seconds). It selects a new leader for partition 3 from the ISR set. If ISR = {broker 1, broker 2, broker 3} and broker 2 dies, ISR becomes {broker 1, broker 3}. The controller picks broker 1 as the new leader (preferring the one with the highest log-end offset to minimize data loss).

The controller updates the metadata (new leader for partition 3 = broker 1) and sends LeaderAndIsrRequests to broker 1 (become leader) and broker 3 (follow broker 1 now). Producers and consumers refresh metadata (they detect the leader change when they get a NOT_LEADER_OR_FOLLOWER error on their next request to the dead broker) and redirect to broker 1.

Failover time: heartbeat timeout (~10s) + controller processing (~100ms) + metadata propagation (~100ms) = ~10-11 seconds. During this window, writes to partition 3 fail — producers retry with backoff. No data loss if the new leader was in ISR (it had all committed messages up to the high watermark)."

**Interviewer**: "What if the ISR shrinks to just the leader? The leader crashes — we lose data?"

**You**: "Yes, if ISR = {leader only} and the leader crashes, messages that were acknowledged (with `acks=all`, which means acks from all ISR = just the leader) but not replicated to followers are lost. This is why `min.insync.replicas=2` is critical for durable topics: the broker rejects writes when ISR < 2, returning NOT_ENOUGH_REPLICAS. This trades availability for durability — the partition is temporarily unavailable for writes but no committed data can be lost.

The configuration trinity for maximum durability: `replication.factor=3`, `min.insync.replicas=2`, `acks=all`. This means: 3 copies, at least 2 must be in sync, and the producer waits for all in-sync replicas to acknowledge. You can lose 1 broker without data loss and without unavailability."

### Deep Dive Path 2: Consumer Groups & Offset Management

**Interviewer**: "How do consumers track what they've consumed? What happens on failure?"

**You**: "Each consumer in a group tracks its position per partition as an offset (integer). Offsets are committed to a special internal topic `__consumer_offsets` (50 partitions, replicated). When a consumer processes a batch of messages, it periodically commits its offset: 'I've processed up to offset 500 on partition 3.'

Two commit modes: (1) auto-commit — the consumer client automatically commits every `auto.commit.interval.ms` (default 5 seconds). Simple but can cause duplicates (consumer crashes after processing but before auto-commit — messages are redelivered on rebalance) or data loss (auto-commit happens before processing completes — messages are lost on crash). (2) Manual commit — the consumer explicitly calls `commitSync()` or `commitAsync()` after processing. This gives precise control: commit after processing = at-least-once (duplicates on crash, no loss). Commit before processing = at-most-once (no duplicates, but possible loss)."

**Interviewer**: "A consumer is processing slowly and falls behind by millions of messages. What happens?"

**You**: "This is 'consumer lag.' The consumer continues consuming from its committed offset, which may be far behind the log head. Three concerns: (1) the data might be expired — if retention is 7 days and the consumer is 8 days behind, its offset points to deleted data. Kafka returns an OffsetOutOfRangeException, and the consumer resets to either the earliest available offset or the latest (configurable via `auto.offset.reset`). (2) The consumer reads from disk instead of page cache — data this old isn't in the OS cache, so reads hit disk. Throughput drops from GB/s (cache) to 100s of MB/s (disk). (3) The consumer creates I/O contention with the leader's replication traffic.

Mitigation: monitor consumer lag (`kafka.consumer:type=consumer-fetch-manager-metrics,client-id=...,records-lag-max`). Alert when lag exceeds a threshold. Scale up consumers (add more to the group, up to the partition count). If lag is permanent (consumer can't keep up), add partitions to the topic to increase parallelism — but this requires key-based consumers to handle partition reassignment (keys may map to different partitions)."

**Interviewer**: "How does the group coordinator handle a consumer that's alive but just processing slowly?"

**You**: "The group coordinator tracks liveness via heartbeats (`heartbeat.interval.ms=3s`, `session.timeout.ms=45s`). As long as the consumer sends heartbeats, it's considered alive regardless of processing speed. But there's a separate concern: `max.poll.interval.ms` (default 5 minutes). If the consumer doesn't call `poll()` within this interval (because it's stuck processing a large batch), the coordinator considers it 'stuck' and triggers a rebalance. The consumer loses its partition assignments and the stuck partitions are reassigned.

This is a common operational issue: a consumer processes a poison message (causes an exception or hangs), doesn't call `poll()` for 5 minutes, gets kicked from the group, the partition is reassigned to another consumer, which hits the same poison message — and you get a rebalance loop. The fix: implement a dead-letter queue per consumer — after N retries on a single message, skip it and publish to a DLQ topic. Also, set `max.poll.records` to limit batch size so processing always completes within `max.poll.interval.ms`."

### Deep Dive Path 3: Scaling & Performance at 2M Messages/Second

**Interviewer**: "2 million messages per second. How many brokers? How do you size the cluster?"

**You**: "At 1KB average message size, that's 2GB/s write throughput. With replication factor 3, total disk write = 2GB/s x 3 = 6GB/s cluster-wide. Each broker can sustain ~200MB/s write (sequential) on modern SSDs or spinning disks. So: 6GB/s / 200MB/s = 30 brokers minimum for write throughput.

Read throughput: 3 consumer groups reading all data = 6GB/s read. Each broker handles ~500MB/s read (from page cache for recent data). Read throughput is often easier to scale because hot data lives in the OS page cache.

Memory: Kafka relies heavily on the OS page cache. Rule of thumb: enough RAM to cache the active segment (last few hours) per partition. With 100K partitions / 30 brokers = 3,333 partitions per broker. Active segment per partition: ~100MB (at average write rate). Total page cache need: 333GB — which means 128-256GB RAM per broker is ideal.

Disk: 7 days retention at 2GB/s = 2 x 86,400 x 7 = 1.2PB total. With 3x replication = 3.6PB. 30 brokers = 120TB per broker. 12 drives of 10TB each per broker. JBOD (just a bunch of disks) — no RAID needed because Kafka's replication provides redundancy."

**Interviewer**: "How do you handle partition rebalancing when adding brokers?"

**You**: "Adding a broker to a Kafka cluster doesn't automatically rebalance partitions. Existing partitions stay on their current brokers. You need to explicitly reassign partitions using `kafka-reassign-partitions.sh` (or Cruise Control for automated rebalancing).

The reassignment process: (1) generate a reassignment plan (move partition 3 leader from broker 2 to new broker 31), (2) the controller tells broker 31 to start replicating partition 3 from the current leader, (3) broker 31 fetches all data for that partition (could be 10s of GB — this takes time), (4) once broker 31 is in-sync, the controller makes it the leader and removes the old assignment from broker 2, (5) broker 2 deletes its local data for that partition.

The key concern: during reassignment, the cluster has more replicas than normal (replication factor temporarily increases), consuming extra disk and network. At scale (100K partitions), rebalancing must be throttled to avoid saturating the network. Kafka's `--throttle` flag limits replication bandwidth during reassignment — typically 50-100MB/s per broker to leave headroom for production traffic."

**Interviewer**: "Kafka vs. Pulsar vs. Kinesis — how do they differ architecturally?"

**You**: "Three fundamentally different approaches. Kafka: partitions are tied to brokers (storage + compute coupled). Simple, fast, but rebalancing is painful and scaling requires data movement. Pulsar: separates storage (Apache BookKeeper) from serving (Pulsar brokers). Brokers are stateless — scaling is just adding brokers, no data movement. But the BookKeeper dependency adds operational complexity. Kinesis: fully managed, similar to Kafka conceptually but shards (partitions) are the unit of billing and scaling. Shard splitting/merging is seamless but more limited in throughput per shard.

For our design, the Kafka model is the right starting point. It's proven at massive scale (LinkedIn, Uber, Netflix). The Pulsar-style disaggregated storage is conceptually cleaner but adds a dependency (BookKeeper/S3). If I were building from scratch today, I'd consider Kafka's upcoming tiered storage (KIP-405) which gets the best of both: local storage for hot data, S3 for cold data, without a separate storage system."

---

## How Real Companies Built This

- **LinkedIn (Kafka's origin)**: Created Kafka in 2011 for activity stream processing. Processes 7+ trillion messages per day across 100K+ topics. Key innovation: the log as a fundamental data structure for both messaging and ETL. Jay Kreps' blog post "The Log" (https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) is essential reading.

- **Uber (Kafka at scale)**: Runs one of the largest Kafka deployments — multiple clusters handling petabytes per day. Key challenges: cross-datacenter replication (uReplicator), consumer lag monitoring, and dead letter queue management. They built custom tooling for cluster rebalancing and partition management. Blog: https://www.uber.com/blog/kafka/

- **Confluent (Kafka company)**: Developed Kafka Streams (stream processing library), ksqlDB (SQL on streams), Schema Registry (Avro/Protobuf schema management), and KRaft (removing ZooKeeper dependency). KRaft uses Raft consensus for metadata management, simplifying Kafka's architecture from 2 distributed systems (Kafka + ZooKeeper) to 1.

- **Amazon Kinesis**: AWS's managed streaming service. Differs from Kafka: shards (partitions) are the unit of billing ($0.015/shard-hour), throughput is limited per shard (1MB/s write, 2MB/s read), and retention is 7 days by default (365 max). Simpler to operate than Kafka but less flexible.

- **Key lesson**: The distributed log is the most important primitive in modern data infrastructure. Kafka won because it got the core abstraction right: a partitioned, replicated, append-only log with offset-based consumption. Everything else (exactly-once, transactions, streams, connectors) was built on top of this foundation.

---

## The Complete Reference Design

### API Design
```
# Produce messages
POST /v1/topics/{topic}/produce
Request: {
  "records": [
    {
      "key": "user-123",           # optional, for partitioning
      "value": "base64-encoded",
      "headers": {"event_type": "purchase"},
      "timestamp": 1739347200000   # optional, default = broker time
    }
  ],
  "acks": "all"                    # "0", "1", or "all"
}
Response 200: {
  "offsets": [
    {"partition": 3, "offset": 15000042, "timestamp": 1739347200000}
  ]
}

# Consume messages
GET /v1/topics/{topic}/consume?group_id=payment-processor&max_records=100
Response 200: {
  "records": [
    {
      "topic": "purchases",
      "partition": 3,
      "offset": 15000042,
      "key": "user-123",
      "value": "base64-encoded",
      "headers": {"event_type": "purchase"},
      "timestamp": 1739347200000
    }
  ]
}

# Commit offsets
POST /v1/topics/{topic}/commit
Request: {
  "group_id": "payment-processor",
  "offsets": [
    {"partition": 3, "offset": 15000043}
  ]
}
Response 200: { "committed": true }

# Topic management
POST /v1/topics
Request: {
  "name": "purchases",
  "partitions": 12,
  "replication_factor": 3,
  "config": {
    "retention.ms": 604800000,      # 7 days
    "min.insync.replicas": 2,
    "compression.type": "lz4",
    "max.message.bytes": 1048576    # 1MB
  }
}
```

### Storage Format (On-Disk)
```
# Partition directory structure:
/data/kafka-logs/purchases-3/    (topic "purchases", partition 3)
  |
  +-- 00000000000000000000.log       # Segment file (offsets 0-999999)
  +-- 00000000000000000000.index     # Offset -> file position
  +-- 00000000000000000000.timeindex # Timestamp -> offset
  +-- 00000000000001000000.log       # Next segment
  +-- 00000000000001000000.index
  +-- 00000000000001000000.timeindex
  +-- leader-epoch-checkpoint        # Leader epochs for truncation

# Log segment record format (Kafka's RecordBatch):
+--------------------------------------------------------------+
| Base Offset (8 bytes)                                        |
| Batch Length (4 bytes)                                        |
| Partition Leader Epoch (4 bytes)                              |
| Magic (1 byte) = 2                                           |
| CRC32 (4 bytes)                                              |
| Attributes (2 bytes: compression, timestamp type, txn, etc.) |
| Last Offset Delta (4 bytes)                                  |
| First Timestamp (8 bytes)                                    |
| Max Timestamp (8 bytes)                                      |
| Producer ID (8 bytes)  -- for idempotent/txn producers       |
| Producer Epoch (2 bytes)                                     |
| Base Sequence (4 bytes)                                      |
| Records Count (4 bytes)                                      |
+--------------------------------------------------------------+
| Record 0: [length, attributes, timestamp_delta,              |
|            offset_delta, key, value, headers]                |
| Record 1: ...                                                |
+--------------------------------------------------------------+

# Index file: maps offset -> physical position in .log file
# Sparse index: one entry per ~4KB of log data
# Binary search on index to find the starting position,
# then sequential scan in log file.
```

### Key Algorithms
```python
import hashlib
import time
import threading
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict

@dataclass
class Record:
    key: Optional[bytes]
    value: bytes
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: int = 0
    offset: int = -1  # assigned by broker

@dataclass
class RecordBatch:
    records: List[Record]
    producer_id: int = -1
    base_sequence: int = 0


# --- Partitioner (client-side) ---
class Partitioner:
    """Determines which partition a record goes to."""
    def partition(self, key: Optional[bytes], num_partitions: int) -> int:
        if key is None:
            # Round-robin for keyless messages (with sticky batching)
            return self._sticky_counter() % num_partitions
        # Murmur2 hash (Kafka's default partitioner)
        return self._murmur2(key) % num_partitions

    @staticmethod
    def _murmur2(data: bytes) -> int:
        """Kafka-compatible murmur2 hash (positive)."""
        length = len(data)
        seed = 0x9747b28c
        m = 0x5bd1e995
        h = seed ^ length
        for i in range(0, length - length % 4, 4):
            k = int.from_bytes(data[i:i+4], 'little')
            k = (k * m) & 0xFFFFFFFF
            k ^= k >> 24
            k = (k * m) & 0xFFFFFFFF
            h = (h * m) & 0xFFFFFFFF
            h ^= k
        remaining = length % 4
        if remaining >= 3:
            h ^= data[length - remaining + 2] << 16
        if remaining >= 2:
            h ^= data[length - remaining + 1] << 8
        if remaining >= 1:
            h ^= data[length - remaining]
            h = (h * m) & 0xFFFFFFFF
        h ^= h >> 13
        h = (h * m) & 0xFFFFFFFF
        h ^= h >> 15
        return h & 0x7FFFFFFF  # positive


# --- In-Sync Replica (ISR) Management ---
class ISRManager:
    """
    Tracks in-sync replicas for a partition.
    A follower is in-sync if it has replicated within
    replica.lag.time.max.ms of the leader.
    """
    def __init__(self, replicas: List[int], lag_threshold_ms: int = 30000):
        self.replicas = set(replicas)
        self.isr = set(replicas)
        self.lag_threshold_ms = lag_threshold_ms
        self.last_fetch_time = {r: time.time() * 1000 for r in replicas}
        self.leader_leo = 0  # Leader's log end offset

    def update_follower(self, replica_id: int, follower_leo: int):
        """Called when follower fetches from leader."""
        self.last_fetch_time[replica_id] = time.time() * 1000
        # If follower caught up to leader's LEO at time of fetch request
        if follower_leo >= self.leader_leo:
            self.isr.add(replica_id)

    def check_isr(self):
        """Remove followers that are too far behind."""
        now = time.time() * 1000
        for replica_id in list(self.isr):
            if replica_id == self._leader_id():
                continue
            if now - self.last_fetch_time.get(replica_id, 0) > self.lag_threshold_ms:
                self.isr.discard(replica_id)
                print(f"Replica {replica_id} removed from ISR (lag exceeded)")

    def can_accept_write(self, min_isr: int) -> bool:
        """Check if we have enough in-sync replicas."""
        return len(self.isr) >= min_isr

    def compute_high_watermark(self, replica_offsets: Dict[int, int]) -> int:
        """HW = min(LEO) across all ISR members."""
        isr_offsets = [replica_offsets[r] for r in self.isr
                       if r in replica_offsets]
        return min(isr_offsets) if isr_offsets else 0

    def _leader_id(self):
        return min(self.replicas)  # simplified


# --- Consumer Group Coordinator ---
class ConsumerGroupCoordinator:
    """
    Manages consumer group membership and partition assignment.
    Simplified version of Kafka's GroupCoordinator.
    """
    def __init__(self, topic_partitions: Dict[str, int]):
        self.topic_partitions = topic_partitions  # topic -> partition_count
        self.groups = {}  # group_id -> {consumer_id: subscription}
        self.assignments = {}  # group_id -> {consumer_id: [partitions]}

    def join_group(self, group_id: str, consumer_id: str,
                   subscribed_topics: List[str]):
        if group_id not in self.groups:
            self.groups[group_id] = {}
        self.groups[group_id][consumer_id] = subscribed_topics
        self._rebalance(group_id)

    def leave_group(self, group_id: str, consumer_id: str):
        if group_id in self.groups:
            self.groups[group_id].pop(consumer_id, None)
            self._rebalance(group_id)

    def _rebalance(self, group_id: str):
        """Range assignment strategy (simplified)."""
        members = self.groups.get(group_id, {})
        if not members:
            self.assignments[group_id] = {}
            return

        # Collect all partitions from subscribed topics
        all_partitions = []
        for consumer_id, topics in members.items():
            for topic in topics:
                count = self.topic_partitions.get(topic, 0)
                for p in range(count):
                    if (topic, p) not in all_partitions:
                        all_partitions.append((topic, p))

        # Distribute evenly (range assignment)
        consumer_ids = sorted(members.keys())
        assignment = {cid: [] for cid in consumer_ids}
        for i, partition in enumerate(sorted(all_partitions)):
            target = consumer_ids[i % len(consumer_ids)]
            assignment[target].append(partition)

        self.assignments[group_id] = assignment
        return assignment
```

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Brokers (write throughput) | 6GB/s total writes (3x replication) / 200MB/s per broker | 30 brokers |
| RAM per broker | Page cache for active segments: 3,333 partitions x 100MB | 128-256GB |
| Disk per broker | 7 days x 2GB/s / 30 brokers x 3 replication | 120TB per broker (12x10TB drives) |
| Network per broker | 200MB/s write + 200MB/s replication + 200MB/s reads | 10Gbps NIC minimum |
| Total cluster storage | 7 days x 2GB/s x 3 replication | 3.6PB |
| ZooKeeper/KRaft | 3-5 nodes (metadata only) | Lightweight (8GB RAM each) |
| Partitions per broker | 100K total / 30 brokers | ~3,333 per broker |
| Consumer groups | 5,000 groups x avg 10 consumers | 50K consumer connections |
| `__consumer_offsets` | 5,000 groups x 100K partitions x 16 bytes | ~8GB (50 partitions, replicated) |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Understands partitioned log, basic producer/consumer model, knows about replication | Designs a multi-broker log with partitions, describes produce/consume flow, mentions acks=all for durability |
| Staff | Deep understanding of ISR, high watermark, consumer group rebalancing, reasons about exactly-once semantics, sizes the cluster correctly | Explains the ISR shrink/expand mechanics, designs around min.insync.replicas, describes the cooperative rebalance protocol, implements idempotent producer deduplication, calculates disk/memory/network requirements |
| Principal | Reasons about multi-datacenter replication (active-active log), compares architectural approaches (Kafka vs Pulsar's disaggregated storage), thinks about schema evolution and data governance, considers the log as an organizational primitive (event-driven architecture) | Proposes MirrorMaker 2 for cross-DC replication with conflict resolution, discusses the trade-offs of Kafka's coupled storage vs Pulsar's BookKeeper, designs schema registry integration with backward/forward compatibility, thinks about how the log enables organizational decoupling between teams |

---

## Red Flags & Common Mistakes
- **Not understanding the difference between the log and a message queue**: A log retains messages for a time period and supports replay from any offset. A queue deletes messages after consumption. This fundamental difference enables event sourcing, CDC, and stream processing.
- **Ignoring ISR and high watermark**: Just saying "replicate to 3 brokers" without explaining how the system ensures consistency during failures is insufficient. ISR + HW is the core of Kafka's replication model.
- **Not addressing the rebalance problem**: Consumer group rebalancing is the #1 operational pain point. Candidates should mention cooperative rebalancing and the `max.poll.interval.ms` issue.
- **Claiming exactly-once is simple**: It's achievable within Kafka's boundary but requires idempotent producers + transactional consumers. External side effects still need idempotency at the application level.
- **Ignoring consumer lag**: How do you monitor it? What happens when a consumer falls behind? What's the operational response?
- **Proposing global ordering**: Global ordering across partitions is extremely expensive (single partition = no parallelism). Per-partition ordering with key-based routing is the correct answer for 99% of use cases.
- **Not mentioning compression**: Kafka supports message-level compression (gzip, snappy, lz4, zstd). LZ4 is the standard choice — 2x compression ratio with minimal CPU overhead. This halves network and disk usage.
