# Design a Distributed Key-Value Store

> **Companies**: Amazon (DynamoDB), Meta, Google (Bigtable), Apple, Netflix, Uber | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: This is the foundational distributed systems question. It tests whether you truly understand the CAP theorem trade-offs (not just name-drop them), replication protocols (leader-based vs. leaderless), consistency models, partitioning strategies, and failure detection. The interviewer is looking for someone who can reason about the fundamental tensions in distributed storage — you can't have it all.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**Questions that show the interviewer you know what you're doing:**

- "What's our read/write ratio? Read-heavy (90/10) or write-heavy (50/50)? This determines our replication strategy."
- "What consistency model? Strong consistency (linearizable) or eventual? If eventual, what's the acceptable staleness window — seconds, minutes?"
- "What's our latency SLA? p50 < 5ms, p99 < 50ms? Or are we optimizing for throughput over latency?"
- "Expected data volume? GBs, TBs, PBs? This determines if we need partitioning from day one."
- "Key-value size? Small (< 1KB, like session data) or large (MBs, like blobs)? This changes the storage engine."
- "Do we need TTL support? Range queries? Or purely point lookups by key?"
- "Single datacenter or multi-region? What's our availability target — 99.9% or 99.99%?"
- "Failure tolerance — how many node failures should we survive without data loss?"

### Working Assumptions
| Parameter | Value | Derivation |
|-----------|-------|------------|
| Scale | 10TB total data, growing 1TB/month | Large but not Google-scale — fits a focused design |
| Operations | 500K reads/s, 100K writes/s | 5:1 read/write ratio, typical for KV stores |
| Key size | 64 bytes avg | UUIDs, user IDs, session keys |
| Value size | 1KB avg (max 1MB) | JSON objects, session data, feature flags |
| Latency SLA | p50 < 5ms, p99 < 20ms for reads; p50 < 10ms, p99 < 50ms for writes | Typical for online serving |
| Consistency | Tunable — strong by default, eventual for specific use cases | Best of both worlds per DynamoDB model |
| Replication factor | 3 replicas per key | Standard for durability |
| Availability target | 99.99% | 52 minutes downtime/year |
| Data model | Simple key-value, no range queries | Simplifies partitioning |

---

## High-Level Design (Brief — 5 minutes)

```
Client (SDK with retry + routing logic)
    |
    v
+-------------------+
|  Coordinator /    |     Stateless — routes to correct partition
|  Proxy Layer      |     (or client-side routing with gossip)
+--------+----------+
         |
    +----+----+----+----+
    |         |         |
    v         v         v
+-------+ +-------+ +-------+
|Node A | |Node B | |Node C |     Partition 1 (replicas)
|Leader | |Follow | |Follow |
+-------+ +-------+ +-------+

+-------+ +-------+ +-------+
|Node D | |Node E | |Node F |     Partition 2 (replicas)
|Leader | |Follow | |Follow |
+-------+ +-------+ +-------+

    ... (hundreds of partitions)

Gossip / Membership Protocol (Swim/Gossip)
    - Failure detection
    - Cluster membership
    - Partition map distribution
```

**Why this architecture?**: A distributed KV store must solve three fundamental problems: partitioning (spread data across nodes), replication (survive node failures), and consistency (what guarantees clients see). This design uses consistent hashing for partitioning, leader-based replication for strong consistency (with a leaderless option for availability), and a gossip protocol for cluster membership.

---

## Core Concepts Deep Dive

### Concept 1: Consistent Hashing with Virtual Nodes

**What it is**: Standard hash(key) % N breaks when N changes (nearly all keys remap). Consistent hashing maps both keys and nodes onto a hash ring. A key is assigned to the first node clockwise from its position on the ring. Adding/removing a node only moves ~1/N of the keys.

**How it applies here**: Each physical node gets 100-200 virtual nodes (vnodes) distributed across the ring. This ensures even data distribution even with heterogeneous hardware. For replication factor 3, a key is stored on the 3 consecutive distinct physical nodes clockwise on the ring.

**The math/mechanics**: With 100 physical nodes and 150 vnodes each = 15,000 points on the ring. Standard deviation of load per node drops from ~100% (with 1 point) to ~8% (with 150 points). When a node joins, each existing node transfers ~1/N of its data — for 100 nodes, each transfers ~1% of its keys.

**Common misconception**: Candidates describe consistent hashing without virtual nodes. Without vnodes, data distribution is highly uneven (some nodes get 2-3x more data). Also, candidates often forget to explain that the "preference list" (the N nodes responsible for a key) must skip duplicate physical nodes — if vnodes A1 and A2 are consecutive, both belong to physical node A, and the second replica must go to the next distinct node.

### Concept 2: Replication & Consistency — Quorum Protocol

**What it is**: With N replicas, a quorum read requires R responses and a quorum write requires W acknowledgments. If R + W > N, you get strong consistency because any read quorum overlaps with any write quorum. With N=3: R=2, W=2 gives strong consistency. R=1, W=1 gives eventual consistency with lower latency.

**How it applies here**: Tunable consistency per request. For strong consistency: W=2, R=2 (majority quorum). For eventual consistency: W=1, R=1 (fast path). The coordinator sends writes to all 3 replicas but waits for W acknowledgments before responding. Reads go to R replicas and return the value with the highest vector clock.

**The math/mechanics**: Write latency = max(fastest W of N replicas). For N=3, W=2: latency = 2nd fastest replica. If replicas have latencies [3ms, 5ms, 50ms] (one slow), write latency = 5ms, not 50ms. This tail-latency tolerance is a key advantage of quorum systems.

**Common misconception**: Candidates say "quorum means majority" — it doesn't. Quorum means R + W > N. You could do N=5, R=1, W=5 (fast reads, slow writes) or N=5, R=5, W=1 (fast writes, slow reads). The trade-off is between read and write latency. Also, R + W > N only gives linearizability if you implement read-repair or anti-entropy — raw quorum reads can return stale data during replica divergence.

### Concept 3: Conflict Resolution — Vector Clocks & CRDTs

**What it is**: In a leaderless system with eventual consistency, concurrent writes to the same key create conflicting versions. Vector clocks track causal ordering: each replica maintains a counter, and the vector clock is incremented on every write. If two vector clocks are not comparable (neither dominates), the writes are concurrent and require resolution.

**How it applies here**: Each value stored includes its vector clock: `{A: 3, B: 2, C: 1}`. On read, if the coordinator finds two versions with incomparable clocks, it can: (1) return both to the client for application-level resolution (Dynamo approach), (2) use last-writer-wins with wall clock timestamps (Cassandra approach — simpler but lossy), or (3) use CRDTs for mergeable data types (counters, sets).

**The math/mechanics**: Vector clock size = O(number of replicas that have written). With N=3, it's just 3 integers. But in Dynamo-style systems where any node can coordinate, the clock grows with the number of coordinator nodes — Amazon truncates after a threshold and accepts some false conflicts.

**Common misconception**: Candidates confuse vector clocks with Lamport timestamps. Lamport timestamps are a single integer and can determine "happens-before" but cannot detect concurrency. Vector clocks can detect concurrent writes (when neither clock dominates). Also, LWW (last-writer-wins) is not "eventually consistent" — it's "eventually losing data." Real systems use it because the simplicity trade-off is worth it for most workloads.

### Concept 4: Storage Engine — LSM Tree vs. B-Tree

**What it is**: The on-disk storage engine determines write throughput, read latency, and space amplification. LSM trees (Log-Structured Merge trees) buffer writes in memory (memtable), flush to sorted files on disk (SSTables), and periodically merge (compact) them. B-trees update in place with random I/O.

**How it applies here**: For a write-heavy KV store, LSM trees are the standard choice (used by LevelDB, RocksDB, Cassandra). Writes are O(1) amortized (append to memtable). Reads require checking the memtable + bloom filters on each SSTable level. For a read-heavy workload, B-trees (used by InnoDB, PostgreSQL) offer faster point reads but slower writes.

**The math/mechanics**: LSM write amplification = O(level_count * size_ratio). With 10x size ratio and 4 levels, each byte is written ~40 times total across compactions. Read amplification = O(level_count) in the worst case, but bloom filters reduce this to ~1 disk read for 99% of queries (1% false positive rate per level).

**Common misconception**: Candidates say "LSM trees are faster for writes" without discussing the write amplification cost of compaction. At high write throughput, compaction can fall behind, causing read latency to spike as more SSTables accumulate. This is the "write cliff" — a critical operational concern.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Consistency & Replication

**Interviewer**: "You said tunable consistency. Walk me through exactly what happens during a write with strong consistency."

**You**: "The client sends `PUT(key=user:123, value={...})` to the coordinator. The coordinator hashes the key to find the partition — say it maps to nodes A, B, C where A is the leader. The coordinator forwards the write to A. A appends to its write-ahead log (WAL), applies to memtable, then sends the write to B and C. With W=2, A waits for one follower acknowledgment. Once A has its own ack + 1 follower ack = 2, it responds success. The third replica receives the write asynchronously."

**Interviewer**: "What if node A (the leader) crashes mid-write? B got the write, C didn't."

**You**: "This is where the replication protocol matters. If we use Raft-style consensus, the write isn't committed until a majority (2 of 3) have it in their WALs. If A crashes after only B has the write, that's only 1 out of 3 — the write is not committed and the client gets an error (timeout or failure). When A recovers or a new leader is elected (B or C), the uncommitted entry is rolled back. If A and B both had it before A crashed, it IS committed (2 of 3), and the new leader (B) will replicate it to C. No data loss."

**Interviewer**: "Raft is expensive — every write goes through consensus. How do you make writes faster?"

**You**: "Several options. First, batch consensus — accumulate writes for 1-2ms and commit them as a batch in a single Raft round. This amortizes the cost of consensus across many writes. Raft throughput goes from ~10K to 100K+ ops/sec with batching. Second, for workloads that tolerate eventual consistency, bypass Raft entirely — write to the leader, which asynchronously replicates to followers. Third, use multi-Raft: each partition has its own independent Raft group. With 1000 partitions across 100 nodes, you have 1000 independent Raft groups running in parallel. TiKV and CockroachDB use this pattern."

**Interviewer**: "How does leader election work? What's the downtime during failover?"

**You**: "In Raft, each leader sends heartbeats every 150ms. If a follower doesn't receive a heartbeat for a randomized timeout (say 300-500ms), it starts an election. It increments its term, votes for itself, and requests votes from peers. A candidate wins with a majority. Typical failover time: 300-500ms election timeout + 1 round-trip for voting = ~500ms-1s total. During this window, writes to that partition fail — the coordinator retries or the client gets a temporary error. With 1000 partitions, a single node failure only affects the partitions where that node was leader (~10 partitions if 100 nodes)."

### Deep Dive Path 2: Partitioning & Rebalancing

**Interviewer**: "A node joins the cluster. Walk me through what happens to the data."

**You**: "When a new node joins, it gets assigned virtual nodes on the hash ring. The cluster coordinator (or gossip protocol) determines which key ranges transfer to the new node. For example, if the new node's vnode lands between existing nodes X and Y, it takes over the key range that was previously on Y. Y streams the relevant data to the new node in the background — this is a bulk transfer of SSTables, not individual key copies. During transfer, reads for those keys still go to Y (it's still authoritative). Once transfer is complete and verified, the routing table is atomically updated."

**Interviewer**: "How do you handle hot keys? One key getting 100x the traffic of others."

**You**: "Hot keys are a real problem — imagine a viral tweet's counter. Three approaches: First, client-side caching with short TTL (1-5s) for read-heavy hot keys — absorbs 90% of reads. Second, read replicas — replicate the hot partition to more nodes and load-balance reads across them. Third, key splitting — for write-heavy hot keys like counters, split `tweet:123:likes` into `tweet:123:likes:shard_0` through `tweet:123:likes:shard_9` and aggregate on read. This spreads writes across 10 partitions."

**Interviewer**: "You mentioned consistent hashing. Why not just hash(key) mod N with a fixed partition count — like Kafka does?"

**You**: "That's actually a great approach and simpler to implement. Pre-allocate a fixed number of partitions (say 10,000) at cluster creation. Assign partitions to nodes. When a node joins/leaves, reassign entire partitions — no key-level reshuffling. Kafka, Elasticsearch, and many systems use this. The trade-off: you must choose the partition count upfront, and it's hard to change later. Consistent hashing with vnodes is more flexible but operationally more complex. For a new system, I'd actually prefer the fixed partition count approach — it's simpler and the partition count can be generous (10K partitions for a cluster that'll grow to 1000 nodes)."

**Interviewer**: "What about data skew? What if 80% of writes go to 10% of keys?"

**You**: "Data skew is different from traffic skew. If certain key prefixes are hot (e.g., all keys starting with 'US:'), the hash function naturally distributes them evenly — hash('US:abc') and hash('US:xyz') are in completely different partitions. The problem is traffic skew on a single key, which I addressed with key splitting. For range-partitioned systems (like Bigtable), data skew IS a partitioning problem, and you need automatic partition splitting — when a partition exceeds a size threshold, split it in half and assign the halves to different nodes."

### Deep Dive Path 3: Failure Detection & Repair

**Interviewer**: "How do you detect that a node is down vs. just slow?"

**You**: "I'd use a SWIM-based gossip protocol. Each node periodically pings a random peer. If no response within a timeout (say 200ms), it asks K other nodes to probe the suspect (indirect probing). If all K fail, the node is marked as 'suspected.' After a configurable grace period (5-10s), it's marked 'dead.' The indirect probing step is critical — it prevents false positives from transient network issues between two specific nodes. SWIM gives O(log N) convergence time for failure detection across the cluster."

**Interviewer**: "A node was dead for 2 hours and comes back. How does it catch up?"

**You**: "Two mechanisms. First, Merkle tree anti-entropy: each replica maintains a Merkle tree (hash tree) over its key range. When the recovered node connects, it exchanges Merkle tree roots with its peers. If roots differ, they walk down the tree to find exactly which key ranges are out of sync and transfer only those ranges. This is O(log N) comparisons for N keys. Second, hinted handoff — while the node was down, writes destined for it were stored as 'hints' on other nodes. When it comes back, those hints are replayed. Hints handle the common case (short outage), Merkle trees handle the edge cases (long outage, bit rot)."

**Interviewer**: "What's the operational cost of Merkle trees? How often do you rebuild them?"

**You**: "Merkle trees are expensive to build from scratch — O(N) where N is the number of keys. You don't rebuild from scratch. You maintain them incrementally: when a key is written, update the leaf hash, then propagate up. This is O(log N) per write. The tree is persisted alongside the data. Cassandra rebuilds Merkle trees during repair operations (nodetool repair), which is famously slow on large datasets — hours for TBs of data. The lesson: run anti-entropy repair regularly (daily or weekly) so it's incremental and fast, not as a crisis response."

---

## How Real Companies Built This

- **Amazon DynamoDB**: The original Dynamo paper (2007, https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) defined the leaderless, quorum-based approach with vector clocks and consistent hashing. Modern DynamoDB moved to a leader-based model with Paxos for strong consistency while keeping the partitioning model. The key insight: they moved AWAY from leaderless because operational complexity of conflict resolution was too high.

- **Meta (RocksDB + ZippyDB)**: Meta's KV store ZippyDB uses RocksDB as the storage engine with Paxos for replication. They handle 10s of billions of QPS across their fleet. Key innovation: tunable consistency per-request and aggressive client-side caching. Blog: https://engineering.fb.com/2021/08/06/core-infra/zippydb/

- **Google (Bigtable / Spanner)**: Bigtable uses a sorted map model with range partitioning and GFS for storage. Spanner adds TrueTime for global strong consistency using GPS + atomic clocks. Key lesson: if you have accurate global clocks, you can achieve external consistency without the overhead of consensus on every read.

- **etcd (what you work with in K8s)**: etcd uses Raft for consensus with a single Raft group — limiting it to ~10K writes/sec. This is fine for Kubernetes metadata but wouldn't work for a general-purpose KV store. The lesson: consensus protocols limit throughput, which is why production KV stores use multi-Raft with thousands of independent groups.

---

## The Complete Reference Design

### API Design
```
PUT /v1/kv/{key}
Headers: X-Consistency: strong | eventual
Request: {
  "value": "base64-encoded-bytes",
  "ttl_seconds": 3600,       // optional
  "if_version": 42           // optional, for CAS (compare-and-swap)
}
Response 200: {
  "version": 43,
  "timestamp": "2026-02-12T...",
  "replicas_acked": 2
}

GET /v1/kv/{key}
Headers: X-Consistency: strong | eventual
Response 200: {
  "key": "user:123",
  "value": "base64-encoded-bytes",
  "version": 43,
  "timestamp": "2026-02-12T..."
}
Response 404: { "error": "key_not_found" }

DELETE /v1/kv/{key}
Response 200: { "deleted": true, "version": 44 }
```

### Database Schema (Storage Engine — LSM-based)
```
# On-disk format per partition:

WAL (Write-Ahead Log):
+----------+----------+---------+-------+-------+
| sequence | key_len  | key     | value | crc32 |
| (8 bytes)| (4 bytes)| (var)   | (var) | (4 B) |
+----------+----------+---------+-------+-------+

SSTable format:
+-------------------------------------------+
| Data Block 1 (sorted key-value pairs)     |
| Data Block 2                              |
| ...                                       |
| Index Block (key -> block offset)         |
| Bloom Filter (for key existence checks)   |
| Footer (offsets to index + bloom filter)  |
+-------------------------------------------+

Memtable: Skip list or red-black tree (in memory)
  - Sorted by key for efficient range scans and SSTable flush
  - Size threshold: 64MB before flush to disk
```

### Key Algorithms
```python
import hashlib
import bisect
from typing import Optional

class ConsistentHashRing:
    """Consistent hashing with virtual nodes."""
    def __init__(self, num_vnodes=150):
        self.num_vnodes = num_vnodes
        self.ring = []          # sorted list of (hash, physical_node)
        self.nodes = set()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str):
        self.nodes.add(node)
        for i in range(self.num_vnodes):
            vnode_key = f"{node}:vnode:{i}"
            h = self._hash(vnode_key)
            bisect.insort(self.ring, (h, node))

    def remove_node(self, node: str):
        self.nodes.discard(node)
        self.ring = [(h, n) for h, n in self.ring if n != node]

    def get_nodes(self, key: str, n: int = 3) -> list:
        """Return N distinct physical nodes responsible for this key."""
        if not self.ring:
            return []
        h = self._hash(key)
        idx = bisect.bisect_left(self.ring, (h,))
        result = []
        seen = set()
        for i in range(len(self.ring)):
            pos = (idx + i) % len(self.ring)
            _, node = self.ring[pos]
            if node not in seen:
                seen.add(node)
                result.append(node)
                if len(result) == n:
                    break
        return result


class QuorumCoordinator:
    """Handles quorum reads and writes."""
    def __init__(self, ring: ConsistentHashRing, n=3, default_w=2, default_r=2):
        self.ring = ring
        self.n = n
        self.default_w = default_w
        self.default_r = default_r

    def write(self, key: str, value: bytes, consistency: str = "strong"):
        w = self.default_w if consistency == "strong" else 1
        nodes = self.ring.get_nodes(key, self.n)
        acks = []
        for node in nodes:
            try:
                version = self._send_write(node, key, value)
                acks.append((node, version))
            except Exception:
                continue  # node unreachable — try others

        if len(acks) >= w:
            return {"status": "ok", "version": max(v for _, v in acks)}
        raise Exception(f"Write failed: only {len(acks)}/{w} acks")

    def read(self, key: str, consistency: str = "strong"):
        r = self.default_r if consistency == "strong" else 1
        nodes = self.ring.get_nodes(key, self.n)
        responses = []
        for node in nodes:
            try:
                val, version = self._send_read(node, key)
                responses.append((version, val, node))
            except Exception:
                continue

        if len(responses) < r:
            raise Exception(f"Read failed: only {len(responses)}/{r} responses")
        # Return highest version
        responses.sort(key=lambda x: -x[0])
        latest_version, latest_val, _ = responses[0]
        # Read repair: send latest to stale replicas
        for version, _, node in responses[1:]:
            if version < latest_version:
                self._send_write(node, key, latest_val)  # async
        return latest_val

    def _send_write(self, node, key, value):
        pass  # RPC to node

    def _send_read(self, node, key):
        pass  # RPC to node
```

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Storage per node | 10TB / 100 nodes x 3 replicas | ~300GB per node |
| Memory per node (memtable + cache) | 64MB memtable + 10GB block cache | ~11GB RAM per node |
| Network (write throughput) | 100K writes/s x 1KB x 3 replicas | ~300MB/s cluster-wide |
| Network (read throughput) | 500K reads/s x 1KB x 2 (quorum) | ~1GB/s cluster-wide |
| WAL disk throughput | 100K writes/s x 1KB per node | ~1MB/s per node (easily handled) |
| Compaction I/O | ~40x write amplification | ~40MB/s per node (background) |
| Cluster size | 10TB data x 3 replicas / 300GB per node | ~100 nodes |
| Partition count | 100 nodes x 100 partitions/node | 10,000 partitions |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Correct consistent hashing, basic replication, understands CAP trade-off | Designs hash ring with vnodes, implements W+R>N quorum, explains leader vs. leaderless |
| Staff | Reasons about consistency models deeply, designs conflict resolution, thinks about operational concerns (rebalancing, compaction) | Explains vector clocks vs. LWW trade-offs, designs Merkle tree anti-entropy, discusses write amplification in LSM trees, proposes multi-Raft for throughput |
| Principal | Challenges the problem framing, proposes adaptive consistency, thinks about failure modes at fleet level, discusses organizational trade-offs | Asks "who is the customer — is this an internal platform or external API?" Proposes per-key consistency tuning, designs for cascading failure prevention, discusses how to operate this at 1000-node scale with a team of 5 |

---

## Red Flags & Common Mistakes
- **Saying "we use consistent hashing" without explaining virtual nodes**: Shows surface-level knowledge. The interviewer will ask, and you need the vnode story.
- **Confusing CAP with a binary choice**: CAP is about what happens DURING a network partition. In normal operation, you can have both consistency and availability. The question is: when a partition occurs, do you choose C (reject writes) or A (allow stale reads)?
- **Ignoring the storage engine**: Many candidates draw boxes labeled "database" without discussing HOW data is stored on disk. LSM vs. B-tree is a fundamental choice with real trade-offs.
- **No failure detection story**: How do you know a node is down? "Health checks" is too vague. Describe the gossip protocol.
- **Over-engineering with Paxos/Raft when not needed**: If the interviewer says eventual consistency is fine, don't add consensus. Leader-less with quorum reads/writes is simpler and higher throughput.
- **Forgetting read repair and anti-entropy**: Quorum reads don't self-heal permanently. You need background repair mechanisms (Merkle trees, hinted handoff) or replicas drift over time.
