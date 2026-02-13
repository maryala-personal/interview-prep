# Design a Distributed Cache

> **Companies**: Meta, Google, Amazon, Microsoft, Netflix, Twitter/X, Uber | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a system that balances memory efficiency, cache hit ratio, and consistency? Can you reason about consistent hashing, eviction policies beyond simple LRU, handle the thundering herd problem, and design for partial failure (what happens when one cache node dies)? This is a problem where depth of understanding matters more than breadth — the interviewer will push until you reach the limits of your knowledge.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**These are the questions that make the interviewer think "this person knows what they're doing."**

- "What's the read-to-write ratio? Caches are read-dominant — 100:1? 1000:1? This affects the consistency model."
- "What's the expected data size? Are we caching small objects (1 KB user profiles) or large objects (10 MB rendered pages)?"
- "What's the total dataset size vs. cache capacity? If the cache can hold 10% of the dataset, the eviction policy matters a lot."
- "What's the latency SLA? p99 < 1ms (in-memory)? p99 < 5ms (Redis over network)?"
- "What consistency model? Write-through, write-behind, cache-aside? Or are we designing a standalone cache like Redis/Memcached?"
- "Do we need TTL-based expiration, LRU eviction, or both? What's the default TTL?"
- "What's the cache cluster size? 10 nodes or 1000 nodes? This affects the consistent hashing and rebalancing strategy."
- "Do we need replication within the cache for availability, or is it acceptable to have a cache miss on node failure?"

### Working Assumptions

| Parameter | Value |
|-----------|-------|
| Read QPS | 10M/sec (total across cluster) |
| Write QPS | 100K/sec |
| Read:Write ratio | 100:1 |
| Cache cluster size | 20 nodes |
| Memory per node | 64 GB |
| Total cache capacity | 1.28 TB |
| Average object size | 1 KB |
| Number of cached objects | ~1.28 billion |
| p99 read latency | < 1ms (local), < 5ms (remote) |
| p99 write latency | < 10ms |
| Availability | 99.99% |

**The math**:
- 20 nodes x 64 GB = 1.28 TB total cache capacity
- At 1 KB average object size: ~1.28 billion cached objects
- 10M reads/sec / 20 nodes = 500K reads/sec per node — well within Redis's capability (~1M ops/sec per node)
- Network: 10M reads/sec x 1 KB = 10 GB/sec total read bandwidth — ~500 MB/sec per node

---

## High-Level Design (Keep it brief — 5 minutes max)

```
┌──────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Client  │────→│  Cache Client    │────→│  Cache Cluster     │
│  Service │     │  Library         │     │                    │
└──────────┘     │  (consistent     │     │  ┌──────┐ ┌──────┐│
                 │   hash ring,     │     │  │Node 1│ │Node 2││
                 │   connection     │     │  │64 GB │ │64 GB ││
                 │   pooling,       │     │  └──────┘ └──────┘│
                 │   retry logic)   │     │  ┌──────┐ ┌──────┐│
                 └────────┬─────────┘     │  │Node 3│ │...   ││
                          │               │  │64 GB │ │      ││
                          │               │  └──────┘ └──────┘│
                 ┌────────▼─────────┐     └────────────────────┘
                 │  Config Service  │
                 │  (cluster        │  ← Tracks node membership, health, ring state
                 │   membership,    │
                 │   hash ring)     │
                 └──────────────────┘
```

**Why this architecture?** The intelligence lives in the client library, not the cluster. The client knows the hash ring, picks the right node for each key, and handles failover. This is the Memcached model — each node is independent and unaware of other nodes. Contrast with the Redis Cluster model where nodes coordinate. The client-side routing approach is simpler, more predictable, and avoids inter-node coordination overhead. The config service (ZooKeeper/etcd) tracks which nodes are alive and broadcasts ring changes to clients.

---

## Core Concepts Deep Dive

### Concept 1: Consistent Hashing with Virtual Nodes

**What it is**: When we have 20 cache nodes and a key, we need to deterministically route the key to a node. Naive modulo (`hash(key) % 20`) breaks horribly when nodes are added or removed — every key remaps. Consistent hashing puts nodes on a ring and assigns keys to the nearest clockwise node.

**How it applies here**:
- Each physical node maps to 150 virtual nodes on the ring (150 x 20 = 3000 ring positions).
- To find the node for a key: hash the key → find the next clockwise virtual node → map to physical node.
- Adding node 21: it takes over ~1/21 of the ring (~4.8%) from its clockwise neighbors. Only ~4.8% of keys are remapped.
- Without virtual nodes: nodes may own wildly uneven portions of the ring. With 150 virtual nodes, the standard deviation of load per node drops to ~3% — essentially uniform.

**The math/mechanics**:
```
Hash ring: [0, 2^32)
Node 1 virtual nodes: hash("node1-vn0"), hash("node1-vn1"), ..., hash("node1-vn149")
Key lookup: hash("user:12345") = 0xABCD1234
Find smallest virtual node position >= 0xABCD1234
Map virtual node to physical node → route request there
```
- Ring lookup: binary search on sorted list of virtual node positions → O(log N) where N = 3000 → ~12 comparisons.
- Alternative: jump consistent hash (Google, 2014) — no virtual nodes needed, O(1) lookup, perfectly uniform distribution, but only supports adding/removing from the tail.

**Common misconception**: Candidates know consistent hashing exists but can't explain why virtual nodes matter. Without them, the node-to-key mapping is highly non-uniform. With 20 nodes and no virtual nodes, the most loaded node could have 3x the keys of the least loaded.

### Concept 2: Cache Eviction Policies — Beyond Simple LRU

**What it is**: When the cache is full and a new item arrives, which item do we evict? LRU (Least Recently Used) is the default, but it has weaknesses.

**How it applies here**:
- **LRU**: Evict the item that hasn't been accessed the longest. Works well for temporal locality patterns. Weakness: a full table scan (touching every key once) pollutes the cache with items that won't be accessed again.
- **LFU (Least Frequently Used)**: Evict the least-accessed item. Better for frequency-based access patterns. Weakness: items that were popular in the past but no longer relevant stay cached forever.
- **W-TinyLFU (Caffeine's algorithm)**: A frequency sketch (Count-Min sketch) tracks access frequency. New items enter a "window" LRU. Items that prove their frequency earn promotion to the main LFU cache. This combines the benefits of LRU (recency) and LFU (frequency).
- **Redis's approximated LRU**: Redis doesn't maintain a true LRU linked list (too expensive). Instead, it samples 5 random keys and evicts the least recently used among the sample. Configurable via `maxmemory-samples`.

**The math/mechanics**:
```
W-TinyLFU:
- Count-Min sketch: 4 hash functions x 1M counters = 4MB
  → Tracks frequency of all keys, even evicted ones
- Window cache (1% of total): admits all new items
- Main cache (99%): admits only items with frequency > victim's frequency
- Hit ratio improvement: 5-10% over LRU on real workloads
```

**Common misconception**: Candidates say "LRU" and move on. Interviewers at the Staff+ level expect you to discuss when LRU is suboptimal (scan pollution, one-hit wonders) and what alternatives exist. Mentioning W-TinyLFU or segmented LRU shows deep understanding.

### Concept 3: The Thundering Herd Problem

**What it is**: When a popular cached item expires or a cache node crashes, hundreds of concurrent requests for the same key all miss the cache simultaneously. They all query the backend database, potentially overwhelming it.

**How it applies here**: Imagine a celebrity's profile is cached with a 5-minute TTL. When it expires, the next 100 requests all miss, all query the DB, all get the same result, and all try to write it to cache. The DB gets 100 identical queries in 50ms.

**Solutions**:
1. **Locking / request coalescing**: On a cache miss, the first request acquires a lock (Redis SETNX with TTL). Other requests for the same key wait (with timeout) for the lock holder to populate the cache. Only one DB query happens.
2. **Early expiration / probabilistic refresh**: Before the TTL expires, a random request refreshes the cache. The probability of refreshing increases as the TTL approaches. `should_refresh = random() < beta * exp(-delta * time_remaining)`. This spreads the refresh across time.
3. **Stale-while-revalidate**: Serve the stale cached value while asynchronously refreshing in the background. The user gets a slightly stale response instead of a latency spike.

**The math/mechanics**:
```python
# Probabilistic early refresh (XFetch algorithm)
import random, math

def should_early_refresh(ttl_remaining: float, delta: float = 1.0, beta: float = 1.0) -> bool:
    """Returns True if we should refresh the cache proactively."""
    if ttl_remaining <= 0:
        return True
    return random.random() < beta * math.exp(-delta * ttl_remaining)
```

**Common misconception**: Candidates solve this with "just add more DB replicas." That treats the symptom, not the cause. The thundering herd happens because N requests simultaneously bypass the cache. Request coalescing reduces N to 1, which is a fundamental solution regardless of DB capacity.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Consistent Hashing and Node Failure"

**Interviewer**: "Node 7 in your 20-node cluster crashes. Walk me through what happens."

**You**: "Node 7's 150 virtual nodes become inactive. The config service (ZooKeeper/etcd) detects the failure via health checks (missed heartbeats for 10 seconds) and broadcasts a ring update to all cache clients. The clients remove Node 7's virtual nodes from their local ring. Keys that were on Node 7 now map to the next clockwise node for each of Node 7's virtual node positions — distributed across many physical nodes. Because of virtual nodes, the load spreads roughly evenly: each surviving node takes on ~5.3% more keys (1/19 of Node 7's load). Those keys are now cache misses — they'll be populated on first access from the database."

**Interviewer**: "Those cache misses all hit at once. Node 7 had ~64 GB of data. That's potentially millions of cache misses in seconds."

**You**: "Yes, this is a localized thundering herd. The severity depends on the hit rate for those keys. In practice, most cached items are cold (80/20 rule) — maybe 20% of Node 7's keys are actively hot. That's ~12.8 GB / 1 KB per item = ~12.8M hot keys spread across 19 nodes = ~670K sudden cache misses per node. At 50K DB queries/sec per DB replica, this takes ~13 seconds to warm up. Mitigations: (1) Request coalescing — only one query per key reaches the DB. (2) Cache replicas — each key is stored on N nodes (e.g., N=2). If Node 7 dies, the replica on Node 8 still has the data. Cache misses drop to near zero, at the cost of 2x memory usage. (3) Gradual migration: the config service can remove Node 7 from the ring gradually (remove 10 virtual nodes at a time over 5 minutes), spreading the cache miss spike."

**Interviewer**: "You mentioned replicas. How do you keep the replica consistent with the primary?"

**You**: "The client writes to both the primary and the replica. Since the client knows the hash ring, it computes the primary node and the next N-1 clockwise nodes as replicas. On write: the client sends the write to both. If one fails, the write still succeeds (the healthy copy is authoritative). On read: the client reads from the primary. If the primary is down, it falls back to the replica. There's no synchronization between nodes — each node is independent. This means a write to the primary might not reach the replica (if the client crashes between the two writes). For a cache, this is acceptable — the worst case is a cache miss on failover, which triggers a DB read. We're not going for strong consistency here — caches are fundamentally best-effort."

**Interviewer**: "How do you add a new node to the cluster without disrupting traffic?"

**You**: "Step 1: Add the new node (Node 21) to the config service. Step 2: The config service broadcasts the updated ring to all clients, but clients don't immediately reroute traffic. Step 3: Node 21 runs a warm-up phase — it pre-populates its cache by scanning the keys it's now responsible for (based on its ring position) from the neighboring nodes or from the database. Step 4: After warm-up (cache fill reaches 80%), the config service marks Node 21 as 'active.' Clients update their rings to include Node 21. Traffic shifts gradually because virtual nodes ensure only ~1/21 of keys move. During the transition, some keys will miss on Node 21 and be populated from DB — this is a small, distributed load, not a spike."

### Deep Dive Path 2: "Cache Consistency and Invalidation"

**Interviewer**: "A user updates their profile. The database is updated, but the cache still has the old profile. How do you handle consistency?"

**You**: "Three strategies, with different trade-offs. (1) **Cache-aside (lazy invalidation)**: On write, delete the cache key. The next read misses the cache, queries DB, and populates the cache. This has a brief inconsistency window (between DB write and cache delete). (2) **Write-through**: On write, update both the DB and the cache atomically. No inconsistency window, but every write pays the cache-write latency. (3) **Write-behind**: On write, update the cache immediately and asynchronously write to the DB. Fastest writes, but data loss risk if the cache node crashes before the DB write. For most applications, cache-aside is the best default — it's simple, and the inconsistency window (milliseconds) is acceptable."

**Interviewer**: "With cache-aside, you said 'delete the cache key on write.' Why delete instead of update?"

**You**: "It's about preventing race conditions. Consider this sequence: (1) Thread A reads from DB and gets value V1. (2) Thread B writes V2 to DB. (3) Thread B deletes the cache key. (4) Thread A writes V1 to the cache (populating it from step 1). Now the cache has stale V1 while the DB has V2. If we had used 'update on write' (write-through), the same race can happen: (1) Thread B writes V2 to cache. (2) Thread A writes V1 to cache (from its earlier DB read). Deletion is safer because even if there's a race, the worst case is a cache miss, not stale data. The cache miss triggers a fresh DB read, which returns V2. With update-on-write, you can end up with a permanently stale entry."

**Interviewer**: "There's still a window where the cache is deleted but the DB hasn't been updated yet — or vice versa. How do you handle the 'delete from cache, then crash before DB write' scenario?"

**You**: "The correct order is: (1) Write to DB first. (2) Then delete from cache. If we crash between 1 and 2, the DB has the new value but the cache has the old value — this is a stale cache, which the TTL will eventually fix. If we crash between 2 and 1 (wrong order), the cache is deleted but the DB still has the old value — the next cache fill gets the old value, which is correct. So 'DB write first, cache delete second' is the safe order. For extra safety, use a delayed double-delete: (1) Delete from cache. (2) Write to DB. (3) Wait 500ms. (4) Delete from cache again. The second delete catches any stale read that happened between steps 1 and 2."

**Interviewer**: "How do you handle cache invalidation across multiple services? Service A updates the DB, but Service B also caches the same data."

**You**: "Publish an invalidation event. When Service A writes to the DB, it also publishes to a Kafka topic: `cache_invalidation:{entity_type}`. All services that cache this entity type subscribe to the topic and delete their local cache entries. This decouples the writer from the cache owners. The event contains the cache key (or entity ID + type), not the new value — each service fetches the new value from DB on its next cache miss. Latency of invalidation: Kafka end-to-end is ~10-50ms, so the stale window is short. For stricter consistency, use Redis pub/sub instead of Kafka (sub-millisecond)."

### Deep Dive Path 3: "Performance Optimization and Memory Efficiency"

**Interviewer**: "Your cache has a 90% hit ratio. How do you improve it to 95%?"

**You**: "Hit ratio depends on three factors: cache size, eviction policy, and access pattern. Options to improve: (1) **Increase cache size** — add more nodes or larger instances. If the working set is 2 TB and we have 1.28 TB cache, we're missing the 'tail' of the distribution. Going to 2 TB would capture nearly the entire working set. (2) **Improve eviction policy** — switch from LRU to W-TinyLFU. This identifies 'one-hit wonders' (items that are accessed once and never again) and doesn't waste cache space on them. On real workloads, this alone can improve hit ratio by 3-5%. (3) **Adjust TTLs** — if items are being evicted by TTL before they're accessed again, increase the TTL. Analyze the TTL vs. inter-access-time distribution. (4) **Prefetching** — for predictable access patterns, populate the cache before the request arrives. If user A loads their feed, prefetch the profiles of users in the feed."

**Interviewer**: "You're storing 1 KB objects. What about memory overhead per key? How much memory is actually used vs. useful data?"

**You**: "Redis stores each key-value pair with significant overhead: the key string, the value string, the dict entry (hash table slot), the redisObject wrapper, and the expire entry (if TTL is set). For a 1 KB value with a 50-byte key: useful data is ~1050 bytes, but Redis uses ~1200 bytes (14% overhead). For small values (100 bytes), the overhead can be 50-100% of the useful data. Optimization: (1) Use Redis hash packing — store multiple small values in a single Redis hash (up to `hash-max-ziplist-entries`). This uses the compact ziplist encoding and saves ~50% memory for small values. (2) Compress values with LZ4 or zstd in the client library before storing. 1 KB text compresses to ~300 bytes. (3) Use Redis's `MEMORY DOCTOR` and `MEMORY USAGE` commands to identify waste."

**Interviewer**: "Your cluster is running at 90% memory. What's your plan?"

**You**: "Immediate: Redis is configured with `maxmemory-policy allkeys-lru`, so it's already evicting least-recently-used keys when memory hits the limit. This is safe — no OOM crash. Short-term: identify the largest keys with `redis-cli --bigkeys` or SCAN with memory sampling. Often, a few oversized keys (10+ MB) are consuming disproportionate memory. Check for keys missing TTLs — they'll never be evicted except by LRU. Medium-term: add more nodes. With consistent hashing and virtual nodes, adding a node moves ~5% of keys to the new node, freeing 5% memory on each existing node. Long-term: review the caching strategy — are we caching data that shouldn't be cached (large blobs, rarely accessed items)? Implement a two-tier cache: small hot items in Redis, large/cold items in a cheaper store (Memcached, local disk cache)."

---

## How Real Companies Built This

- **Meta/Facebook (Memcached → TAO → Mcrouter)**: Started with Memcached, scaled to thousands of servers. Built Mcrouter (open-source) as a proxy layer that handles consistent hashing, replication, and failover. TAO is their specialized cache for social graph data with consistency guarantees. Key paper: "Scaling Memcache at Facebook" (NSDI 2013) — one of the most important caching papers. It describes the thundering herd solution (lease mechanism), cross-region caching, and cache invalidation at scale.
- **Netflix (EVCache)**: Built on top of Memcached with added replication, zone awareness, and auto-scaling. They cache everything — API responses, personalization data, streaming metadata. See: "EVCache: Distributed In-Memory Caching at Netflix" (Netflix Tech Blog).
- **Twitter**: Uses a combination of Redis (for structured data like sorted sets for timelines) and Memcached (for simple key-value caching). They open-sourced Twemproxy (nutcracker), a proxy for Redis/Memcached that handles sharding and connection pooling.
- **Redis Cluster (official)**: Redis's built-in clustering uses hash slots (16384 slots distributed across nodes) instead of consistent hashing. Each node owns a range of hash slots. Resharding is done by moving slots between nodes. See: https://redis.io/docs/reference/cluster-spec/
- **Key lesson**: Facebook's "lease" mechanism from their NSDI 2013 paper is the canonical solution to the thundering herd. When a cache miss occurs, the cache gives the client a "lease" (token). Only the client with the lease can populate the cache. Other clients for the same key wait for the lease holder. This prevents both thundering herds and stale data.

---

## The Complete Reference Design

### API Design
```
# Cache client library API (not HTTP — this is a client-side library)
class DistributedCache:
    def get(key: str) -> Optional[bytes]
    def set(key: str, value: bytes, ttl_seconds: int = 3600)
    def delete(key: str)
    def get_multi(keys: List[str]) -> Dict[str, bytes]  # Batch get (pipelined)
    def set_multi(entries: Dict[str, bytes], ttl_seconds: int = 3600)
    def incr(key: str, delta: int = 1) -> int            # Atomic increment
    def add(key: str, value: bytes, ttl_seconds: int = 3600) -> bool  # Set if not exists

# HTTP API (for cache-as-a-service)
GET /cache/{key}
Response: 200 OK with body, or 404 Not Found
Headers: X-Cache-Hit: true, X-Cache-TTL-Remaining: 2345

PUT /cache/{key}?ttl=3600
Request body: raw bytes
Response: 201 Created

DELETE /cache/{key}
Response: 204 No Content

# Admin API
GET /cache/stats
Response: {
    "total_keys": 1280000000,
    "memory_used_bytes": 1374389534720,
    "hit_rate": 0.923,
    "evictions_per_sec": 1250,
    "connections": 45000,
    "ops_per_sec": 10200000
}

GET /cache/ring
Response: {
    "nodes": [
        {"id": "node-1", "host": "cache-1:6379", "slots": 150, "keys": 64000000, "memory_gb": 61.2},
        {"id": "node-2", "host": "cache-2:6379", "slots": 150, "keys": 63500000, "memory_gb": 60.8}
    ],
    "total_virtual_nodes": 3000
}
```

### Database Schema
```
# Redis data model (per cache node)

# Key-Value storage
SET key value EX ttl_seconds
# Example: SET user:12345:profile "{\"name\":\"Alice\",...}" EX 3600

# Hash (for grouped data)
HSET user:12345 name "Alice" age 30 city "NYC"
HGET user:12345 name

# Connection Registry (config service — etcd/ZooKeeper)
/cache/cluster/nodes/node-1  → {"host": "cache-1", "port": 6379, "status": "active", "weight": 1}
/cache/cluster/nodes/node-2  → {"host": "cache-2", "port": 6379, "status": "active", "weight": 1}
/cache/cluster/ring_version  → 42  (incremented on any ring change)

# Monitoring (Prometheus metrics per node)
cache_hits_total{node="node-1"}
cache_misses_total{node="node-1"}
cache_evictions_total{node="node-1"}
cache_memory_bytes{node="node-1"}
cache_connections_current{node="node-1"}
cache_ops_per_second{node="node-1", op="get"}
cache_ops_per_second{node="node-1", op="set"}
cache_latency_seconds{node="node-1", op="get", quantile="0.99"}
```

### Key Algorithms
```python
import hashlib
import bisect
from typing import Optional, Dict, List
import time
import random
import math

class ConsistentHashRing:
    """Consistent hash ring with virtual nodes."""

    def __init__(self, nodes: List[str], virtual_nodes_per_node: int = 150):
        self.virtual_nodes_per_node = virtual_nodes_per_node
        self.ring: List[tuple[int, str]] = []  # (hash_position, physical_node)
        self.node_set: set = set()
        for node in nodes:
            self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def add_node(self, node: str):
        self.node_set.add(node)
        for i in range(self.virtual_nodes_per_node):
            h = self._hash(f"{node}-vn{i}")
            bisect.insort(self.ring, (h, node))

    def remove_node(self, node: str):
        self.node_set.discard(node)
        self.ring = [(h, n) for h, n in self.ring if n != node]

    def get_node(self, key: str) -> str:
        """Find the node responsible for a key."""
        if not self.ring:
            raise ValueError("Empty ring")
        h = self._hash(key)
        idx = bisect.bisect_left(self.ring, (h,))
        if idx >= len(self.ring):
            idx = 0  # Wrap around
        return self.ring[idx][1]

    def get_nodes(self, key: str, n: int = 2) -> List[str]:
        """Get N distinct physical nodes for a key (primary + replicas)."""
        if not self.ring:
            raise ValueError("Empty ring")
        h = self._hash(key)
        idx = bisect.bisect_left(self.ring, (h,))
        nodes = []
        seen = set()
        for i in range(len(self.ring)):
            pos = (idx + i) % len(self.ring)
            node = self.ring[pos][1]
            if node not in seen:
                seen.add(node)
                nodes.append(node)
                if len(nodes) >= n:
                    break
        return nodes


class CacheClient:
    """Distributed cache client with consistent hashing, coalescing, and failover."""

    def __init__(self, nodes: List[str], replicas: int = 2):
        self.ring = ConsistentHashRing(nodes)
        self.replicas = replicas
        self.in_flight: Dict[str, asyncio.Event] = {}  # For request coalescing

    async def get(self, key: str) -> Optional[bytes]:
        # Request coalescing: if another request for this key is in flight, wait for it
        if key in self.in_flight:
            await self.in_flight[key].wait()
            return await self._get_from_node(self.ring.get_node(key), key)

        self.in_flight[key] = asyncio.Event()
        try:
            nodes = self.ring.get_nodes(key, self.replicas)
            for node in nodes:
                try:
                    value = await self._get_from_node(node, key)
                    if value is not None:
                        return value
                except ConnectionError:
                    continue  # Try replica
            return None  # Cache miss
        finally:
            self.in_flight[key].set()
            del self.in_flight[key]

    async def set(self, key: str, value: bytes, ttl: int = 3600):
        nodes = self.ring.get_nodes(key, self.replicas)
        # Write to all replicas (best-effort for non-primary)
        for i, node in enumerate(nodes):
            try:
                await self._set_on_node(node, key, value, ttl)
            except ConnectionError:
                if i == 0:
                    raise  # Primary must succeed
                continue  # Replica failure is acceptable

    async def get_with_early_refresh(
        self, key: str, fetch_fn, ttl: int = 3600, beta: float = 1.0
    ) -> bytes:
        """Get with probabilistic early refresh to prevent thundering herd."""
        node = self.ring.get_node(key)
        value, remaining_ttl = await self._get_with_ttl(node, key)

        if value is None:
            # Cache miss — fetch, populate, return
            value = await fetch_fn()
            await self.set(key, value, ttl)
            return value

        # Probabilistic early refresh
        if remaining_ttl > 0:
            delta = ttl - remaining_ttl  # Time since last set
            if random.random() < beta * math.exp(-delta * remaining_ttl / ttl):
                # Refresh in background
                asyncio.create_task(self._background_refresh(key, fetch_fn, ttl))

        return value

    async def _background_refresh(self, key: str, fetch_fn, ttl: int):
        value = await fetch_fn()
        await self.set(key, value, ttl)
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Cache Memory | 20 nodes x 64 GB | 1.28 TB total |
| Read Throughput | 10M ops/sec / 20 nodes | 500K ops/sec per node |
| Write Throughput | 100K ops/sec / 20 nodes | 5K ops/sec per node |
| Network (read) | 10M ops/sec x 1 KB | 10 GB/sec total |
| Network (write) | 100K ops/sec x 1 KB x 2 replicas | 200 MB/sec total |
| Client Connections | 1000 app servers x 20 cache nodes | 20K connections per node |
| Memory Overhead | ~15% per-key overhead in Redis | ~192 GB effective overhead |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Implements consistent hashing, understands LRU eviction, designs cache-aside pattern | Explains hash ring with virtual nodes, handles basic get/set with TTL, understands cache miss behavior |
| Staff | Addresses thundering herd, cache consistency patterns, node failure recovery, and memory optimization | Implements request coalescing and early refresh, discusses cache-aside vs write-through trade-offs, designs replica-based failover, analyzes memory overhead |
| Principal | Designs cache as a platform, considers multi-region caching, proposes cache warming strategies, and cache observability | Proposes cross-region cache invalidation protocol, designs a cache analytics system (hit rate per key prefix, hotspot detection), discusses multi-tenant cache isolation, proposes cache-aware data access patterns that change application architecture |

---

## Red Flags & Common Mistakes

- **No consistent hashing**: Using modulo (`hash % N`) for node assignment means adding or removing a node invalidates the entire cache. This is the most basic distributed cache concept.
- **Ignoring the thundering herd**: When a popular key expires or a node crashes, the stampede to the backend can cause cascading failures. Not mentioning request coalescing or early refresh is a gap.
- **Treating cache as source of truth**: A cache is ephemeral. It can lose data at any time (eviction, crash, restart). Designs that rely on cache data being present are fundamentally broken.
- **No discussion of cache consistency**: The question "how do you keep the cache consistent with the database?" always comes up. Have the cache-aside pattern with "delete on write" ready, and understand why delete is safer than update.
- **Over-engineering with strong consistency**: A cache with strong consistency (every write immediately visible to all readers) is a distributed database, not a cache. Caches trade consistency for performance. Accept eventual consistency and design around it.
