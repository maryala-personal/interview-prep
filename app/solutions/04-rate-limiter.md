# Design a Rate Limiter

> **Companies**: Uber, Meta, Google, Amazon, Stripe, Cloudflare, Netflix | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you explain the algorithmic trade-offs between rate limiting strategies (token bucket, sliding window, leaky bucket), design a distributed rate limiter that works across multiple servers without a single bottleneck, and reason about the tension between accuracy and performance? This is a problem where the algorithms matter more than the architecture.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**These are the questions that make the interviewer think "this person knows what they're doing."**

- "Where in the stack is this rate limiter? API gateway level (per-client), service-to-service (per-upstream), or application-level (per-user-per-endpoint)?"
- "What's the rate limiting granularity? Per user? Per API key? Per IP? Per endpoint? Compound keys like user+endpoint?"
- "What's the acceptable false-positive rate? Is it okay to occasionally allow 105 requests when the limit is 100, or must it be exact?"
- "What's the latency budget? If the rate limiter adds > 1ms to every request, that might be unacceptable."
- "Should it be hard (strict drop at limit) or soft (allow bursts up to 2x for short periods)?"
- "Do we need to return rate limit headers (X-RateLimit-Remaining, X-RateLimit-Reset) to clients?"
- "What's the request volume? Are we rate-limiting 100K req/sec or 10M req/sec?"
- "Single datacenter or multi-region? Multi-region makes distributed counting significantly harder."

### Working Assumptions

| Parameter | Value |
|-----------|-------|
| Total request volume | 1M req/sec across all clients |
| Unique rate-limit keys (users) | 10M |
| Rate limit per user | 100 requests/minute |
| Latency budget for rate check | < 1ms p99 |
| Accuracy | Allow up to 5% overshoot (105 requests when limit is 100) |
| Rule types | Per-user, per-IP, per-user-per-endpoint |
| Availability | 99.99% (rate limiter failure = open, not closed) |

**The math**:
- 1M req/sec, each needs a rate limit check
- Each check: 1 Redis round-trip (~0.5ms local) or in-memory check (~0.01ms)
- Memory per key: ~100 bytes (counter + window metadata) x 10M keys = ~1 GB
- Redis can handle ~100K ops/sec per shard, so 1M req/sec needs ~10 Redis shards

---

## High-Level Design (Keep it brief — 5 minutes max)

```
┌──────────┐     ┌───────────────┐     ┌──────────────────┐
│  Client  │────→│ API Gateway / │────→│  Rate Limiter    │
│          │     │ Load Balancer │     │  Middleware       │
└──────────┘     └───────────────┘     └────────┬─────────┘
                                                │
                              ┌─────────────────┼─────────────────┐
                              │                 │                 │
                     ┌────────▼───┐    ┌────────▼───┐    ┌───────▼────┐
                     │ Local Rate │    │ Local Rate │    │ Local Rate │
                     │ Counter    │    │ Counter    │    │ Counter    │
                     │ (in-proc)  │    │ (in-proc)  │    │ (in-proc)  │
                     └────────┬───┘    └────────┬───┘    └────────┬───┘
                              │                 │                 │
                              └─────────────────┼─────────────────┘
                                                │ Async sync every 100ms
                                       ┌───────▼────────┐
                                       │  Redis Cluster  │ ← Global counter, sliding window state
                                       │  (10 shards)    │
                                       └───────┬────────┘
                                               │
                                       ┌───────▼────────┐
                                       │  Rules Config  │ ← Rate limit rules, stored in config service
                                       │  (etcd/consul) │
                                       └────────────────┘
```

**Why this architecture?** A centralized rate limiter (every request checks Redis) adds network latency to every request. Instead, we use a two-tier approach: a local in-process counter handles most checks with ~0.01ms latency, and it syncs with Redis asynchronously every 100ms for global accuracy. This gives us the speed of local counting with the correctness of centralized counting, accepting a small accuracy window (~5%).

---

## Core Concepts Deep Dive

### Concept 1: Rate Limiting Algorithms — The Big Four

**What it is**: There are four major algorithms, each with different trade-offs:

1. **Token Bucket**: A bucket holds up to N tokens. Each request consumes one token. Tokens are added at a fixed rate (e.g., 100/min). Allows bursts up to bucket size.
2. **Leaky Bucket**: Requests enter a FIFO queue. The queue drains at a fixed rate. Smooths out bursts — no traffic spikes pass through.
3. **Fixed Window Counter**: Count requests in fixed time windows (e.g., each minute). Simple but has the boundary problem.
4. **Sliding Window Log/Counter**: Tracks request timestamps in a sliding window. Most accurate but most memory-intensive.

**How it applies here**: Token bucket is the best default for API rate limiting because it allows natural bursts (a user sending 10 requests in 1 second is fine if they haven't used their budget) while enforcing a long-term average. Stripe, Cloudflare, and Kong all use token bucket variants.

**The math/mechanics**:
```
Token Bucket:
- bucket_size = 100 (max burst)
- refill_rate = 100 tokens / 60 seconds = 1.67 tokens/sec
- At time T, tokens = min(bucket_size, tokens + elapsed_time * refill_rate)
- Request allowed if tokens >= 1; then tokens -= 1

Fixed Window boundary problem:
- Window 1 (00:00-01:00): 99 requests at 00:59 → allowed
- Window 2 (01:00-02:00): 99 requests at 01:01 → allowed
- Result: 198 requests in a 2-second window, but limit is 100/min
```

**Common misconception**: Candidates default to fixed window counters because they're simple. But the boundary problem means a client can send 2x the limit in a short burst across window boundaries. Interviewers will ask about this — the sliding window counter fixes it with minimal extra complexity.

### Concept 2: Distributed Rate Limiting — Local + Global

**What it is**: With 50 API servers, a per-server rate limit of 100/min means the actual global limit is 5000/min (if requests are evenly distributed). We need a global counter, but checking Redis on every request adds latency.

**How it applies here**: The two-tier approach:
- **Local tier**: Each server maintains an in-memory token bucket per key. It makes rate limit decisions locally in ~10 microseconds.
- **Global tier**: Every 100ms, each server syncs its local counts with Redis. If the local counter says "50 tokens used" and Redis says "the global count is already 90," the local counter adjusts.
- **Accuracy trade-off**: In the 100ms between syncs, N servers could each allow requests independently, leading to a brief overshoot. With 50 servers and 100ms sync, worst case: 50 servers each allow 2 requests in 100ms = 100 extra requests = 100% overshoot for that 100ms window. In practice, with uneven distribution, overshoot is ~5-10%.

**The math/mechanics**:
```
Sync protocol (Lua script on Redis):
EVALSHA sync_script 1 "rate:user123" local_used server_id timestamp
-- Atomically: global_count += local_used; return global_count
-- If global_count > limit: return RATE_LIMITED
```

**Common misconception**: Candidates either go fully centralized (too slow) or fully local (no global enforcement). The hybrid approach is what production systems use. Stripe's rate limiter (described in their engineering blog) uses exactly this pattern.

### Concept 3: Sliding Window Counter — The Practical Algorithm

**What it is**: A hybrid of fixed window and sliding window log that gives high accuracy with low memory. Instead of storing every request timestamp (sliding window log), it keeps counters for the current and previous fixed windows and interpolates.

**How it applies here**:
```
Current window: 01:00-02:00, count = 30
Previous window: 00:00-01:00, count = 80
Current time: 01:15 (25% into current window)

Weighted count = previous_count * (1 - 0.25) + current_count
               = 80 * 0.75 + 30
               = 90

If limit is 100, this request is allowed (90 < 100).
```

**The math/mechanics**:
- Memory per key: 2 integers (current count, previous count) + 1 timestamp (window start) = 20 bytes
- Compare to sliding window log: storing 100 timestamps = 800 bytes per key
- Accuracy: within ~1% of a true sliding window. The interpolation slightly overestimates in some cases, which is conservative (blocks slightly early rather than late) — desirable for rate limiting.

**Common misconception**: Candidates spend 10 minutes on the sliding window log (storing individual timestamps). It's technically correct but wasteful. The sliding window counter achieves nearly the same accuracy with 40x less memory. This is what Cloudflare uses in production.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Algorithm Deep Dive — Token Bucket Implementation"

**Interviewer**: "Let's go deep on the token bucket. How do you implement it without a background thread adding tokens?"

**You**: "You don't need a background thread. Use lazy evaluation. Store two values per key: `tokens` (current token count) and `last_refill_time`. When a request arrives, calculate how many tokens should have been added since `last_refill_time`: `new_tokens = (now - last_refill_time) * refill_rate`. Update `tokens = min(bucket_size, tokens + new_tokens)` and `last_refill_time = now`. Then check if `tokens >= 1`. If yes, decrement and allow. If no, reject. This is O(1) time, O(1) space per key, and no background threads."

**Interviewer**: "Now make this atomic in Redis. Two requests arrive simultaneously for the same key."

**You**: "Use a Lua script on Redis. Lua scripts execute atomically — Redis is single-threaded, so no race conditions. The script: GET the key (a hash with tokens and last_refill_time fields), compute new tokens based on elapsed time, check if request is allowed, update the fields, SET with the new values. Because it's a single Lua script execution, it's atomic. The alternative is Redis WATCH/MULTI transactions, but those use optimistic locking and retry on conflict — Lua is simpler and faster."

**Interviewer**: "What about Redis latency? If Redis is across the network, you're adding 0.5ms per request."

**You**: "Three mitigations. First, the two-tier approach I described — check locally first, sync with Redis asynchronously. Most requests never touch Redis. Second, use Redis pipelining: batch multiple rate limit checks into a single round-trip. If the API server handles 10K req/sec and syncs every 100ms, that's 1000 rate limit checks per batch, sent as one pipeline. Third, Redis Cluster with local shards — put a Redis instance in each availability zone or even co-locate with the API servers. Network hop drops to < 0.1ms."

**Interviewer**: "Your Redis goes down. What happens?"

**You**: "Fail open. If Redis is unreachable, allow requests. The alternative — fail closed (block all requests) — means a Redis outage takes down your entire service, which is worse than temporarily allowing unlimited requests. The local rate limiters continue enforcing approximate limits based on per-server quotas. If you have 50 servers and a 100/min global limit, each server allows 2/min locally during the Redis outage. Not perfect, but keeps the system running. We also set up Redis Sentinel or Cluster for HA — a Redis outage should be extremely rare (seconds, not minutes)."

### Deep Dive Path 2: "Distributed Counting and Consistency"

**Interviewer**: "You mentioned 5% accuracy trade-off. Walk me through the worst case. When does the distributed counter fail?"

**You**: "Worst case: a client sends a burst of requests that get load-balanced across all 50 servers simultaneously. Each server's local counter is at zero (just synced). The limit is 100/min. Each of the 50 servers allows 2 requests before their local counters hit the per-server quota (100/50 = 2). That's 100 requests — correct. But if the requests arrive between syncs, each server allows up to the full local bucket before learning the global count. If local buckets are set to 10 (to allow small bursts), that's 50 x 10 = 500 requests before any server syncs with Redis. We mitigate by making the local bucket proportional: `local_bucket = max(1, global_limit / num_servers / 2)`. With 50 servers: `100 / 50 / 2 = 1`. Each server allows 1 request locally before syncing."

**Interviewer**: "How do you handle rate limiting across multiple regions?"

**You**: "Two approaches. First, per-region rate limits: if the global limit is 100/min, allocate 50/min to US, 30/min to EU, 20/min to APAC. Each region enforces its own limit independently — no cross-region coordination. Simple but inflexible if traffic shifts. Second, global rate limiting with async cross-region sync: each region maintains local counters and periodically (every 500ms) shares counts with other regions via a gossip protocol or a central aggregation service. The count is eventually consistent — a user can slightly exceed the limit during the sync window. For most use cases, per-region allocation is sufficient and much simpler."

**Interviewer**: "A customer complains they're being rate-limited but they've only sent 50 requests in the last minute. How do you debug this?"

**You**: "This is a real operational scenario. Common causes: (1) Clock drift — if the server's clock is ahead, the sliding window might include requests from the 'future.' Use NTP and monotonic clocks. (2) Shared rate limit key — maybe the customer has multiple API keys that map to the same rate limit key (e.g., all keys under one organization share a limit). (3) Stale local counter — if the local counter was initialized with a high count from a previous sync and hasn't decremented correctly. (4) Config mismatch — the rate limit rule was recently updated but hasn't propagated to all servers. I'd add detailed logging to each rate limit decision: key, algorithm, current count, limit, decision, server_id, sync_age. This makes debugging trivial."

### Deep Dive Path 3: "Advanced Patterns and Production Concerns"

**Interviewer**: "How would you implement different rate limit tiers? Free users get 10/min, paid users get 1000/min."

**You**: "The rate limit rule is stored in a config service (etcd or Consul). Each rule has: `key_pattern` (how to extract the key from the request — e.g., user_id from auth token), `limit`, `window`, and `algorithm`. Rules are loaded into memory on each API server at startup and refreshed every 30 seconds. When a request arrives, the middleware extracts the rate limit key, looks up the matching rule, and applies the algorithm. For tiered limits: the rule lookup includes the user's tier (fetched from the auth token or user profile cache). Free tier maps to rule `{limit: 10, window: 60s}`, paid maps to `{limit: 1000, window: 60s}`. The rate limit middleware doesn't care about tiers — it just applies whatever rule matches."

**Interviewer**: "What about rate limiting by multiple dimensions? Like 100/min per user AND 1000/min per IP AND 10000/min globally?"

**You**: "Apply multiple rate limiters in sequence. The request must pass ALL of them. Order matters for efficiency: check the most restrictive (user limit) first, then IP, then global. If the user limit rejects, we don't waste time checking IP and global. In Redis, this is three separate keys checked in one pipelined call: `pipeline.eval(token_bucket_lua, 'rate:user:123')`, `pipeline.eval(token_bucket_lua, 'rate:ip:1.2.3.4')`, `pipeline.eval(token_bucket_lua, 'rate:global')`. If any returns RATE_LIMITED, reject. The response headers show which limit was hit: `X-RateLimit-Limit: 100`, `X-RateLimit-Scope: user`."

**Interviewer**: "How do you handle rate limiting for WebSocket connections versus HTTP requests?"

**You**: "Different model. HTTP rate limiting counts requests. WebSocket rate limiting counts messages per second on an already-established connection. The rate limiter runs inside the WebSocket handler, not as API gateway middleware. For each WebSocket connection, we maintain a per-connection token bucket in memory (no Redis needed — it's local to the connection). If a client sends messages too fast, we either drop the messages or close the connection with an error code. For connection establishment, we rate-limit the initial HTTP upgrade request at the API gateway level like any other HTTP request."

---

## How Real Companies Built This

- **Stripe**: Uses a token bucket algorithm with a centralized Redis backend. They wrote an excellent blog post on their approach: "Scaling your API with rate limiters" (Stripe Engineering Blog, 2017). Key insight: they use "rate limit groups" so that related endpoints share a budget.
- **Cloudflare**: Uses a sliding window counter at their edge nodes. Each edge node makes rate limit decisions locally and syncs with a global state asynchronously. They process 25M+ req/sec globally. See: "How we built rate limiting capable of scaling to millions of domains" (Cloudflare Blog, 2017).
- **Google Cloud**: Uses a leaky bucket (token bucket variant) for API rate limiting. Their approach is documented in Google Cloud Architecture's "Rate Limiting Strategies and Techniques" guide.
- **Kong API Gateway**: Open-source API gateway with a Redis-backed rate limiter plugin. Uses the sliding window counter approach. Source code is a good reference: https://github.com/Kong/kong
- **Key lesson**: Every production rate limiter eventually needs "fail open" behavior. A rate limiter that fails closed and blocks all traffic is worse than no rate limiter at all. Rate limit state is ephemeral — if you lose it, the worst that happens is a few seconds of unlimited traffic.

---

## The Complete Reference Design

### API Design
```
# Rate limit headers (returned on every response)
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 73
X-RateLimit-Reset: 1707696060       # Unix timestamp when window resets
X-RateLimit-Policy: "100;w=60"      # IETF draft format: 100 per 60 seconds

# Rate limited response
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1707696060
Retry-After: 23                      # Seconds until client should retry
Content-Type: application/json
{
    "error": "rate_limit_exceeded",
    "message": "Rate limit of 100 requests per minute exceeded",
    "retry_after": 23
}

# Rate limit configuration API (internal)
PUT /api/v1/rate-limits/rules
Request: {
    "rules": [
        {
            "id": "user_default",
            "key_pattern": "user:{auth.user_id}",
            "algorithm": "token_bucket",
            "limit": 100,
            "window_seconds": 60,
            "burst_size": 20
        },
        {
            "id": "ip_global",
            "key_pattern": "ip:{request.remote_ip}",
            "algorithm": "sliding_window",
            "limit": 1000,
            "window_seconds": 60
        }
    ]
}
```

### Database Schema
```sql
-- Redis: Token Bucket state (per key)
-- Key: rate:{rule_id}:{key_value}  e.g., rate:user_default:user123
-- Type: Hash
{
    "tokens": "73.5",              -- Current token count (float for partial refills)
    "last_refill": "1707696000.123" -- Timestamp of last refill calculation
}
-- TTL: window_seconds * 2 (auto-cleanup of inactive keys)

-- Redis: Sliding Window Counter state
-- Key: rate:sw:{rule_id}:{key_value}
-- Type: Hash
{
    "current_count": "30",
    "current_window": "1707696000",   -- Window start timestamp
    "previous_count": "80"
}

-- Config store (etcd/Consul): Rate limit rules
-- Key: /rate-limits/rules/{rule_id}
-- Value: JSON rule definition (see API above)

-- PostgreSQL: Rate limit audit log (for debugging)
CREATE TABLE rate_limit_events (
    event_id     BIGSERIAL PRIMARY KEY,
    timestamp_ms BIGINT NOT NULL,
    key_value    VARCHAR(255) NOT NULL,
    rule_id      VARCHAR(100) NOT NULL,
    decision     VARCHAR(10) NOT NULL,   -- 'allow' or 'deny'
    current_count INT,
    limit_value   INT,
    server_id    VARCHAR(50),
    INDEX idx_key_time (key_value, timestamp_ms DESC)
) PARTITION BY RANGE (timestamp_ms);
```

### Key Algorithms
```python
import time
from dataclasses import dataclass

@dataclass
class TokenBucket:
    tokens: float
    last_refill: float
    bucket_size: int
    refill_rate: float  # tokens per second

def check_token_bucket(bucket: TokenBucket) -> bool:
    """Check and consume a token. Returns True if allowed."""
    now = time.monotonic()
    elapsed = now - bucket.last_refill

    # Lazy refill
    bucket.tokens = min(
        bucket.bucket_size,
        bucket.tokens + elapsed * bucket.refill_rate
    )
    bucket.last_refill = now

    if bucket.tokens >= 1.0:
        bucket.tokens -= 1.0
        return True
    return False

# Redis Lua script for atomic token bucket check
TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local bucket_size = tonumber(ARGV[2])
local refill_rate = tonumber(ARGV[3])

local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(data[1]) or bucket_size
local last_refill = tonumber(data[2]) or now

-- Lazy refill
local elapsed = now - last_refill
tokens = math.min(bucket_size, tokens + elapsed * refill_rate)

if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tostring(tokens), 'last_refill', tostring(now))
    redis.call('EXPIRE', key, math.ceil(bucket_size / refill_rate) * 2)
    return {1, math.floor(tokens)}  -- allowed, remaining
else
    redis.call('HMSET', key, 'tokens', tostring(tokens), 'last_refill', tostring(now))
    local retry_after = math.ceil((1 - tokens) / refill_rate)
    return {0, retry_after}  -- denied, retry_after seconds
end
"""

def sliding_window_counter(
    redis_client, key: str, limit: int, window_seconds: int
) -> tuple[bool, int]:
    """Sliding window counter check. Returns (allowed, remaining)."""
    now = time.time()
    current_window = int(now // window_seconds) * window_seconds
    window_position = (now - current_window) / window_seconds  # 0.0 to 1.0

    pipe = redis_client.pipeline()
    pipe.hgetall(f"rate:sw:{key}")
    result = pipe.execute()[0]

    prev_count = int(result.get("previous_count", 0))
    curr_count = int(result.get("current_count", 0))
    stored_window = int(result.get("current_window", 0))

    # Roll over window if needed
    if stored_window < current_window:
        prev_count = curr_count if stored_window == current_window - window_seconds else 0
        curr_count = 0

    # Weighted count
    weighted = prev_count * (1 - window_position) + curr_count
    remaining = max(0, limit - int(weighted) - 1)

    if weighted < limit:
        # Allow and increment
        pipe = redis_client.pipeline()
        pipe.hmset(f"rate:sw:{key}", {
            "current_count": curr_count + 1,
            "current_window": current_window,
            "previous_count": prev_count,
        })
        pipe.expire(f"rate:sw:{key}", window_seconds * 2)
        pipe.execute()
        return True, remaining
    else:
        return False, 0
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Redis Memory | 10M keys x 100 bytes per key | ~1 GB |
| Redis Throughput | 1M checks/sec (with pipelining) | 10 shards x 100K ops/sec |
| Local Memory | 100K hot keys x 50 bytes per server | ~5 MB per server |
| Network (Redis) | 1M req/sec x 200 bytes per req | ~200 MB/sec |
| Config Propagation | 30-sec refresh x 50 servers | Negligible |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Explains one algorithm well, implements it correctly, handles the Redis integration | Implements token bucket in Redis with Lua script, explains fixed window boundary problem |
| Staff | Compares algorithms with trade-offs, designs distributed rate limiting, considers failure modes | Proposes two-tier local+global approach, discusses accuracy-latency trade-off, designs fail-open behavior, handles multi-dimension rate limiting |
| Principal | Designs rate limiting as a platform service, considers organizational impact, proposes adaptive rate limiting | Designs a self-service rate limit configuration system, proposes adaptive rate limiting based on server load (shed 10% traffic when CPU > 80%), discusses rate limiting's role in overall API governance |

---

## Red Flags & Common Mistakes

- **Only knowing one algorithm**: If you can only explain token bucket and can't discuss trade-offs with sliding window or leaky bucket, you'll struggle when the interviewer asks "why not X?"
- **Ignoring the boundary problem with fixed windows**: This is a classic follow-up question. If you propose fixed window counters, the interviewer will ask about the boundary. Have the sliding window counter ready.
- **Centralized rate limiter without discussing latency**: Checking Redis on every request adds 0.5-1ms. At 1M req/sec, that's a significant latency tax. Not discussing the local+global hybrid shows you haven't thought about production performance.
- **Forgetting fail-open**: The rate limiter must not become a single point of failure. If Redis dies, allow traffic (fail open), not block traffic (fail closed).
- **Not mentioning response headers**: `X-RateLimit-Remaining` and `Retry-After` are basic API design. Not including them suggests you haven't built production APIs.
