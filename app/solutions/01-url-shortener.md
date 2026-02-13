# Design a URL Shortener

> **Companies**: Meta, Google, Amazon, Uber, Stripe | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you reason about hashing/encoding trade-offs, design a high-throughput read-heavy service with strong availability guarantees, and think through cache invalidation and data partitioning at scale? This is a "simple" problem that exposes whether you understand distributed systems fundamentals or just memorize architectures.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**These are the questions that make the interviewer think "this person knows what they're doing."**

- "What's our expected read-to-write ratio? URL shorteners are heavily read-biased — are we talking 100:1 or 1000:1?"
- "What QPS should I design for? Are we at Bitly scale (~100K reads/sec) or internal-tool scale (~1K reads/sec)?"
- "What's our latency SLA for redirects? For a redirect service, p99 under 10ms seems critical — is that right?"
- "Do shortened URLs expire? Is there a TTL, or are they permanent? This drastically changes storage planning."
- "Do we need analytics — click counts, referrer tracking, geo breakdowns? Or is this purely a redirect service?"
- "What's our URL length constraint? 7 chars gives us 3.5 trillion combinations with base62 — is that sufficient?"
- "Single region or multi-region? If multi-region, do we need globally unique short codes without coordination?"
- "Should we support custom aliases? That changes the collision-handling story significantly."

### Working Assumptions

| Parameter | Value |
|-----------|-------|
| DAU | 100M |
| Read QPS (redirects) | 100K/sec |
| Write QPS (new URLs) | 1K/sec |
| Read:Write Ratio | 100:1 |
| URL Size (avg) | 200 bytes long URL + 7 bytes short code |
| Storage (Year 1) | ~6 TB |
| p99 Latency (redirect) | < 10ms |
| Availability | 99.99% (52 min downtime/year) |

**The math**:
- 1K writes/sec x 86,400 sec/day = ~86M new URLs/day
- 86M x 365 = ~31B URLs/year
- Each record: 7 bytes (short code) + 200 bytes (long URL) + 50 bytes (metadata) = ~257 bytes
- 31B x 257 bytes = ~8 TB/year (call it 6 TB with compression)
- 100K reads/sec — with 80/20 rule (20% of URLs get 80% of traffic), a cache holding ~20M hot URLs covers most reads

---

## High-Level Design (Keep it brief — 5 minutes max)

```
                         ┌──────────────┐
                         │   DNS/CDN    │  ← Cache 301 redirects at edge for hot URLs
                         └──────┬───────┘
                                │
                         ┌──────┴───────┐
                         │ Load Balancer│  ← L7 LB, route /api/* to write svc, /{code} to read svc
                         └──────┬───────┘
                    ┌───────────┴───────────┐
              ┌─────┴─────┐           ┌─────┴─────┐
              │  Write    │           │  Read     │
              │  Service  │           │  Service  │
              └─────┬─────┘           └─────┬─────┘
                    │                       │
              ┌─────┴─────┐           ┌─────┴─────┐
              │  ID Gen   │           │  Redis    │  ← LRU cache, ~20M entries, ~5GB
              │  Service  │           │  Cache    │
              └─────┬─────┘           └─────┬─────┘
                    │                       │
                    └───────────┬───────────┘
                         ┌──────┴───────┐
                         │   Database   │  ← Sharded by short_code hash
                         │  (DynamoDB / │
                         │   Cassandra) │
                         └──────────────┘
```

**Why this architecture?** We separate read and write paths because the ratio is 100:1 — the read path is a simple cache-then-DB lookup optimized for latency, while the write path handles the harder problem of generating globally unique short codes without coordination. The cache absorbs the vast majority of read traffic since URL access follows a power-law distribution.

---

## Core Concepts Deep Dive

### Concept 1: Short Code Generation — Base62 Encoding vs. Hashing

**What it is**: We need to map a long URL to a unique 7-character string. There are two fundamental approaches: (1) generate a unique integer ID and encode it in base62, or (2) hash the long URL and take a prefix.

**How it applies here**: Base62 encoding of a 64-bit counter gives us codes like `aB3x9Kz`. With 7 characters, base62 gives us 62^7 = 3.5 trillion unique codes. That's 100+ years at 1K writes/sec.

**The math/mechanics**:
```
Base62 alphabet: [0-9a-zA-Z]
ID 1000000 → base62 → "4c92"  (padded to 7 chars: "0004c92")
```
- **Counter-based (Snowflake-style)**: Each node gets a range (e.g., node 1 gets IDs 1-1M, node 2 gets 1M-2M). No coordination needed within a range. When a range is exhausted, request a new one from ZooKeeper/etcd.
- **Hash-based (MD5/SHA-256 + truncation)**: Hash the long URL, take first 43 bits (7 base62 chars). Collision probability with 1B URLs: ~0.01% (birthday problem: n^2 / 2k where k = 62^7). Must handle collisions.

**Common misconception**: Many candidates say "just use MD5 and take 7 chars." But MD5 truncation has a real collision probability. With 1B URLs and 7 base62 chars, you'll see ~140 collisions. You need a collision resolution strategy (append counter, rehash, check-and-retry).

### Concept 2: Data Partitioning & Consistent Hashing

**What it is**: At 31B URLs/year, no single database node can hold all the data. We need to partition (shard) across nodes while keeping lookups O(1).

**How it applies here**: We shard by the short code itself (not by user or long URL) because every read request comes with the short code. Hash the short code to determine the partition.

**The math/mechanics**: With consistent hashing using virtual nodes:
- 10 physical DB nodes, 100 virtual nodes each = 1000 points on the hash ring
- Each node holds ~3.1B URLs (31B / 10)
- Adding a node only moves ~1/N of the data (not N-1/N like naive modulo)
- Use Murmur3 hash for uniform distribution with low collision rate

**Common misconception**: Candidates often propose sharding by the first character of the short code. This creates massive hotspots — popular codes aren't uniformly distributed across the alphabet. Always hash the full key.

### Concept 3: Caching Strategy — Cache-Aside with Write-Around

**What it is**: With 100K reads/sec and most traffic hitting a small subset of URLs, caching is essential. We use cache-aside (lazy loading) because not all URLs are read frequently.

**How it applies here**:
- **Read path**: Check Redis first → cache miss → read from DB → populate cache → return
- **Write path**: Write to DB only (write-around). Don't populate cache on write because most new URLs won't be read immediately.
- **Eviction**: LRU eviction. With 20M cached entries at ~250 bytes each = ~5GB — fits in a single Redis instance.
- **Cache hit ratio**: With power-law access patterns, expect 90-95% hit ratio, reducing DB load from 100K to 5-10K QPS.

**Common misconception**: Candidates propose write-through caching for a URL shortener. This wastes cache space — millions of URLs are created but accessed only a handful of times. Write-around with LRU naturally surfaces hot URLs.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Short Code Generation & Uniqueness"

**Interviewer**: "You mentioned a counter-based approach for generating short codes. How do you ensure uniqueness across multiple write service instances?"

**You**: "I'd use a range-based allocation scheme. A coordination service — say, ZooKeeper or etcd — maintains a global counter. Each write service instance requests a range of, say, 1 million IDs at a time. Instance A gets range [0, 1M), instance B gets [1M, 2M), and so on. Within its range, each instance increments a local in-memory counter with no coordination. When the range is exhausted, it fetches a new one. This gives us the throughput of uncoordinated writes with the uniqueness guarantee of a centralized counter."

**Interviewer**: "What happens if a write service crashes mid-range? You've allocated IDs 5M-6M but it only used 5M-5.2M before dying."

**You**: "We lose the unused portion of that range — IDs 5.2M through 6M are wasted. With a 7-character base62 code space of 3.5 trillion, losing a few million IDs is negligible. The trade-off is worth it: we get crash recovery simplicity (just allocate a new range to the replacement instance) without needing to persist per-instance counter state. If we really cared about ID waste, we could shrink the range to 10K, but that means more frequent coordination with ZooKeeper."

**Interviewer**: "Now, a customer wants custom aliases — say, `short.url/my-brand`. How does this change your design?"

**You**: "Custom aliases bypass the counter entirely — the user provides the short code. The critical issue is collision: what if `my-brand` already exists? We need a check-and-insert atomic operation. In DynamoDB, that's a conditional PutItem with `attribute_not_exists(short_code)`. In SQL, it's an INSERT with a unique constraint. The write path now forks: auto-generated codes use the counter (guaranteed unique, no DB check needed), custom aliases do a conditional write (one round-trip to DB). I'd also add validation — length limits, character whitelist, blocklist for offensive terms."

**Interviewer**: "What if you're running multi-region? How do you handle the counter allocation and custom alias conflicts?"

**You**: "For the counter, I'd assign non-overlapping mega-ranges per region. Region US gets [0, 1T), EU gets [1T, 2T), APAC gets [2T, 3T). Within each region, the local ZooKeeper allocates sub-ranges to instances. No cross-region coordination needed for auto-generated codes. For custom aliases, it's harder — two users in different regions could simultaneously claim `my-brand`. I'd designate one region as the 'source of truth' for custom aliases and do a synchronous cross-region check before confirming. Alternatively, use a conflict-free approach: append a region prefix to custom aliases internally but make it transparent to users via DNS routing."

### Deep Dive Path 2: "Read Path Performance & Caching"

**Interviewer**: "Walk me through what happens when a user clicks `short.url/aB3x9Kz`. Every network hop, every lookup."

**You**: "DNS resolves `short.url` to our CDN edge. The CDN checks its cache — if we've configured 301 (permanent) redirects with a cache header, hot URLs are served directly from the edge with ~5ms latency. On a CDN miss, the request hits our L7 load balancer, which routes `/{code}` paths to the read service fleet. The read service first checks the local in-process cache (an LRU map holding ~100K entries, ~25MB). On a miss, it checks Redis. On a Redis miss, it hashes `aB3x9Kz` to determine the DB partition, queries the DB, populates Redis, populates the local cache, and returns a 301 redirect. Worst-case path: CDN miss → LB → service → local cache miss → Redis miss → DB read → return. That's about 20-30ms."

**Interviewer**: "You said 301 redirect. Why not 302? What's the trade-off?"

**You**: "301 is 'moved permanently' — browsers cache it forever. This means the browser never hits our service again for that URL, which massively reduces our QPS. But it also means we lose analytics visibility (no click counting) and can't change the destination URL later. 302 is 'moved temporarily' — browsers hit us every time, giving us full analytics and mutability. The right answer depends on requirements. If analytics matter (and they usually do for a URL shortener business), use 302. If pure cost optimization matters, use 301. I'd default to 302 and cache at the CDN level with a short TTL (say 5 minutes) for a middle ground."

**Interviewer**: "Your Redis cluster goes down entirely. What happens to read latency?"

**You**: "Without Redis, all 100K reads/sec hit the DB directly. Our DB is provisioned for ~10K QPS (the expected cache-miss rate). So we're at 10x capacity. The options: (1) The local in-process cache absorbs some load — with 100K entries per instance and 50 read service instances, we can serve maybe 30-40% of requests from local caches. (2) DB auto-scaling kicks in, but that takes minutes. (3) We'd see degraded latency (200-500ms instead of 10ms) and potentially start shedding load via circuit breakers. The mitigation is Redis Sentinel or Redis Cluster with replicas — if the primary dies, a replica promotes in seconds. I'd also add a second cache tier (like Memcached) as a fallback, or use Redis Cluster with 3 replicas across AZs so a full outage is extremely unlikely."

**Interviewer**: "How do you handle cache invalidation when a URL is updated or deleted?"

**You**: "For deletes, the write service deletes from the DB and publishes an invalidation event to a Kafka topic. Each read service instance subscribes and removes the key from both Redis and local caches. There's a small window (seconds) where stale data could be served — that's acceptable for a URL shortener. For updates (changing the destination URL), same pattern. The key insight is that URL shorteners are almost append-only — updates and deletes are extremely rare (maybe 0.001% of operations), so optimizing the invalidation path for low latency isn't worth the complexity. A simple event-based invalidation with eventual consistency is fine."

### Deep Dive Path 3: "Scaling, Partitioning & Multi-Region"

**Interviewer**: "You said you'd shard by short code hash. Walk me through what happens when you need to add more DB nodes."

**You**: "With consistent hashing, adding a node N11 to our 10-node ring means N11 takes responsibility for a portion of the hash ring that was previously owned by its clockwise neighbor. Concretely, if each node owns ~10% of the ring, N11 will take ~9% of keys from one neighbor (1/11 of total). The migration process: (1) Add N11 to the hash ring configuration. (2) Background migration job copies affected keys from the old owner to N11. (3) During migration, the read service checks both old and new owner (double-read). (4) Once migration completes, update the ring to mark N11 as active, and the old owner can garbage-collect migrated keys. Using virtual nodes (100 per physical node) ensures the load is evenly distributed and rebalancing moves data from all existing nodes, not just one."

**Interviewer**: "What about multi-region? How do you handle a user creating a short URL in US-East and someone accessing it from EU-West?"

**You**: "Two approaches. First, async replication: writes go to the local region's DB, and we replicate to other regions asynchronously (DynamoDB Global Tables does this out of the box with ~1 second replication lag). A URL created in US-East is accessible in EU-West within 1-2 seconds. For a URL shortener, this latency is fine — the user who creates the URL usually shares it, and there's a natural delay before anyone clicks it. Second approach: all writes go to a single primary region, reads are local. This is simpler but adds write latency for non-primary regions. I'd go with DynamoDB Global Tables — it handles conflict resolution (last-writer-wins by default) and cross-region replication automatically."

**Interviewer**: "You mentioned DynamoDB Global Tables with last-writer-wins. What if two different regions create the same custom alias simultaneously?"

**You**: "That's a real conflict. Last-writer-wins would silently overwrite one mapping, which is unacceptable — you'd have one user's custom alias pointing to another user's URL. The fix: for custom aliases, route all writes through a single primary region (or use DynamoDB's conditional writes which only succeed in one region). Alternatively, prepend a region identifier to the internal key but keep the external short URL the same — route `short.url/my-brand` to the region that created it via DNS-based routing (GeoDNS). The cleanest solution is to make custom alias creation a strongly consistent operation through a single leader, while keeping auto-generated URLs eventually consistent across regions."

---

## How Real Companies Built This

- **Bitly**: Uses a combination of counter-based ID generation and base62 encoding. They partition by short code and use Redis heavily for caching. At peak they handle ~10B clicks/month across ~300M shortened URLs. See: Bitly's engineering blog on architecture scaling.
- **Google (goo.gl, now deprecated)**: Used a hierarchical ID generation scheme tied to Google's internal infrastructure (Spanner for strong consistency). The deprecation in favor of Firebase Dynamic Links shows how URL shorteners evolved into deep-linking platforms.
- **TinyURL**: One of the earliest, uses a simple auto-increment counter with MySQL. Works at their scale but wouldn't scale to Bitly's traffic without sharding.
- **Key lesson**: Every production URL shortener eventually needs analytics (click tracking, geo, referrer). Design the redirect path to emit events to a stream (Kafka) from day one, even if you don't build the analytics dashboard immediately.

---

## The Complete Reference Design

### API Design
```
POST /api/v1/urls
Request: {
    "long_url": "https://example.com/very/long/path?with=params",
    "custom_alias": "my-brand",        // optional
    "ttl_seconds": 86400               // optional, 0 = permanent
}
Response: {
    "short_url": "https://short.url/aB3x9Kz",
    "short_code": "aB3x9Kz",
    "long_url": "https://example.com/very/long/path?with=params",
    "expires_at": "2026-02-12T00:00:00Z",
    "created_at": "2025-02-12T00:00:00Z"
}
Headers: X-RateLimit-Remaining: 95, X-Request-ID: uuid-v4

GET /{short_code}
Response: 302 Found
Headers: Location: https://example.com/very/long/path?with=params
         Cache-Control: max-age=300

GET /api/v1/urls/{short_code}/stats
Response: {
    "short_code": "aB3x9Kz",
    "total_clicks": 150234,
    "clicks_24h": 1203,
    "top_countries": [{"US": 45.2}, {"UK": 12.1}],
    "top_referrers": [{"twitter.com": 30.5}]
}

DELETE /api/v1/urls/{short_code}
Response: 204 No Content
```

### Database Schema
```sql
-- DynamoDB table (or Cassandra equivalent)
-- Table: url_mappings
-- Partition key: short_code (String)
{
    "short_code": "aB3x9Kz",              -- Partition key
    "long_url": "https://example.com/...", -- Target URL
    "user_id": "u_123456",                 -- Creator
    "created_at": 1707696000,              -- Unix timestamp
    "expires_at": 1707782400,              -- TTL for auto-expiry (DynamoDB TTL)
    "click_count": 0                       -- Atomic counter
}

-- For SQL (PostgreSQL with partitioning):
CREATE TABLE url_mappings (
    short_code  VARCHAR(7) PRIMARY KEY,
    long_url    TEXT NOT NULL,
    user_id     BIGINT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMP,
    click_count BIGINT DEFAULT 0
) PARTITION BY HASH (short_code);

-- Create 16 hash partitions
CREATE TABLE url_mappings_p0 PARTITION OF url_mappings FOR VALUES WITH (MODULUS 16, REMAINDER 0);
CREATE TABLE url_mappings_p1 PARTITION OF url_mappings FOR VALUES WITH (MODULUS 16, REMAINDER 1);
-- ... through p15

CREATE INDEX idx_user_urls ON url_mappings (user_id, created_at DESC);
CREATE INDEX idx_expiry ON url_mappings (expires_at) WHERE expires_at IS NOT NULL;
```

### Key Algorithms
```python
import string

BASE62 = string.digits + string.ascii_lowercase + string.ascii_uppercase

def encode_base62(num: int) -> str:
    """Convert integer to base62 string."""
    if num == 0:
        return BASE62[0]
    result = []
    while num > 0:
        result.append(BASE62[num % 62])
        num //= 62
    return ''.join(reversed(result)).zfill(7)

def decode_base62(s: str) -> int:
    """Convert base62 string back to integer."""
    num = 0
    for char in s:
        num = num * 62 + BASE62.index(char)
    return num

class RangeAllocator:
    """Allocates ID ranges from ZooKeeper/etcd. Each instance
    gets a batch of IDs to assign locally without coordination."""

    def __init__(self, zk_client, range_size=1_000_000):
        self.zk = zk_client
        self.range_size = range_size
        self.current_id = 0
        self.max_id = 0

    def next_id(self) -> int:
        if self.current_id >= self.max_id:
            start = self._fetch_range()
            self.current_id = start
            self.max_id = start + self.range_size
        id_val = self.current_id
        self.current_id += 1
        return id_val

    def _fetch_range(self) -> int:
        # Atomic compare-and-swap on ZK node /url_counter
        # Returns the previous value, sets new value = old + range_size
        while True:
            data, stat = self.zk.get("/url_counter")
            current = int(data)
            new_val = current + self.range_size
            if self.zk.set("/url_counter", str(new_val).encode(), version=stat.version):
                return current

def shorten_url(long_url: str, allocator: RangeAllocator, custom_alias: str = None) -> str:
    if custom_alias:
        # Conditional write — fails if alias already exists
        success = db.put_item(
            Item={"short_code": custom_alias, "long_url": long_url},
            ConditionExpression="attribute_not_exists(short_code)"
        )
        if not success:
            raise ConflictError("Alias already taken")
        return custom_alias

    unique_id = allocator.next_id()
    short_code = encode_base62(unique_id)
    db.put_item(Item={"short_code": short_code, "long_url": long_url})
    return short_code
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Storage (DB) | 31B URLs/yr x 257 bytes | ~8 TB/year |
| Cache (Redis) | 20M hot entries x 250 bytes | ~5 GB |
| Network (reads) | 100K req/sec x 1 KB response | ~100 MB/sec |
| Network (writes) | 1K req/sec x 500 bytes | ~500 KB/sec |
| Compute (read) | 100K QPS / 2K QPS per instance | ~50 read instances |
| Compute (write) | 1K QPS / 500 QPS per instance | ~2 write instances |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Solid technical design, handles one deep dive well | Explains base62 encoding, designs cache-aside pattern, calculates storage needs correctly |
| Staff | Drives trade-off discussions, considers operational concerns, sees cross-system implications | Proposes 301 vs 302 trade-off proactively, designs analytics pipeline with Kafka, discusses cache failure cascading and circuit breakers |
| Principal | Challenges the problem framing, proposes novel approaches, thinks about 3-year evolution | Questions whether a URL shortener is the right abstraction (vs. deep links), proposes multi-region architecture with conflict resolution, discusses how analytics requirements will dominate the system cost at scale |

---

## Red Flags & Common Mistakes

- **Using MD5/SHA and ignoring collisions**: The birthday problem is real at scale. 1B URLs with 43-bit hash space gives ~140 collisions. Always have a collision resolution strategy or use counter-based generation.
- **Not separating read and write paths**: At 100:1 ratio, this is a classic CQRS candidate. Candidates who propose a single service handling both miss the scaling story.
- **Forgetting about analytics**: Every production URL shortener needs click tracking. Not mentioning it suggests you haven't thought about the business use case.
- **Over-engineering the write path**: At 1K writes/sec, a single MySQL instance handles this fine. Don't propose Kafka, event sourcing, and CQRS for the write path. Save complexity for the read path where the scale actually is.
- **Ignoring the 301 vs 302 decision**: This is a classic senior-level signal. It touches caching, analytics, and mutability — interviewers love when you bring it up unprompted.
