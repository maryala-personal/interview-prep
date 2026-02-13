# Design a News Feed / Timeline

> **Companies**: Meta (very common), Twitter/X, LinkedIn, Google, TikTok, Pinterest | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you reason about fan-out strategies (push vs. pull vs. hybrid), design for extreme read-heavy workloads with personalization, and handle the tension between consistency and latency in a social graph? This problem is Meta's bread and butter — they want to see that you understand how content distribution works at planetary scale.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**These are the questions that make the interviewer think "this person knows what they're doing."**

- "What's the read-to-write ratio? Users read feeds far more than they post — are we at 100:1 or 1000:1?"
- "What's the follower distribution? A few users have millions of followers (celebrities), most have hundreds. This drives the fan-out strategy."
- "What's the latency SLA for feed loading? p99 < 200ms for the initial feed load?"
- "Are we ranking the feed or showing it chronologically? Ranking adds a real-time ML scoring layer."
- "What content types? Text-only, or images/videos too? This affects payload size and CDN strategy."
- "What's the freshness requirement? Can the feed be 30 seconds stale, or does it need near-real-time updates?"
- "Do we need to support 'seen' deduplication across devices?"
- "What's the expected engagement rate? This affects the write amplification from likes/comments updating feed items."

### Working Assumptions

| Parameter | Value |
|-----------|-------|
| DAU | 500M |
| Avg posts/day per active user | 2 |
| Avg followers per user | 200 (median), power-law distribution |
| Celebrity users (>1M followers) | ~50K |
| Feed read QPS | 500K/sec (each user refreshes ~10x/day) |
| Post write QPS | ~12K/sec (500M x 2 / 86400) |
| Feed items per load | 50 posts |
| p99 Feed load latency | < 300ms |
| Availability | 99.99% |

**The math**:
- 500M DAU x 2 posts/day = 1B posts/day = ~12K writes/sec
- 500M DAU x 10 reads/day = 5B reads/day = ~58K feed reads/sec (but bursty — peak is ~500K/sec)
- Average fan-out: 12K posts/sec x 200 followers = 2.4M fan-out writes/sec (if using push model)
- Celebrity fan-out: 1 celebrity post x 10M followers = 10M writes in a burst — this is the killer problem

---

## High-Level Design (Keep it brief — 5 minutes max)

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐
│  Client  │────→│ API Gateway  │────→│  Post Service    │ ← Accepts new posts, validates, stores
│          │     │              │     └────────┬─────────┘
│          │     │              │              │
│          │     │              │     ┌────────▼─────────┐
│          │     │              │     │  Fan-out Service  │ ← Push to follower feeds (non-celebrity)
│          │     │              │     └────────┬─────────┘
│          │     │              │              │
│          │     │              │     ┌────────▼─────────┐
│          │     │              │     │  Feed Cache       │ ← Pre-computed feed per user (Redis sorted set)
└──────────┘     │              │     │  (Redis Cluster)  │
                 │              │     └──────────────────┘
┌──────────┐     │              │
│  Client  │────→│              │────→┌─────────────────┐
│ (read)   │     │              │     │  Feed Service    │ ← Merges cached feed + celebrity posts on-read
└──────────┘     └──────────────┘     └────────┬────────┘
                                               │
                                      ┌────────▼────────┐
                                      │  Ranking Service │ ← ML model scores + re-ranks feed items
                                      └────────┬────────┘
                                               │
                                      ┌────────▼────────┐
                                      │  Posts DB        │ ← Source of truth: posts, user graph
                                      │  (Cassandra +    │
                                      │   Social Graph)  │
                                      └─────────────────┘
```

**Why this architecture?** The hybrid fan-out model is the key insight. For normal users (200 followers), we push posts to follower feeds at write time — this makes reads fast (just fetch from cache). For celebrities (10M+ followers), pushing is impractical (10M writes per post), so we pull their posts at read time and merge with the pre-computed feed. This is exactly what Twitter calls the "fan-out service" architecture.

---

## Core Concepts Deep Dive

### Concept 1: Fan-Out Strategies — Push, Pull, and Hybrid

**What it is**: When user A posts, how do A's 200 followers see it in their feed? Three approaches:

- **Push (fan-out on write)**: When A posts, immediately write the post ID to each follower's feed cache. Reads are O(1) — just fetch the pre-computed list.
- **Pull (fan-out on read)**: Store nothing. When B opens their feed, query all users B follows, fetch their recent posts, merge, and sort. Reads are O(N) where N = number of users followed.
- **Hybrid**: Push for normal users, pull for celebrities. Merge at read time.

**How it applies here**: Pure push breaks with celebrities. If a user with 10M followers posts, that's 10M writes to Redis. At 12K posts/sec globally, even if 0.1% are celebrities, that's 12 celebrity posts/sec x 10M = 120M writes/sec to the cache. That's unsustainable.

**The math/mechanics**: With hybrid:
- Non-celebrity posts (99.9% of traffic): fan-out to ~200 feeds each = 12K x 200 = 2.4M writes/sec to Redis — manageable
- Celebrity posts: stored once, pulled at read time. Each feed read merges cached feed (O(1) fetch) + N celebrity posts (where N = number of celebrities the user follows, typically < 50)
- Read-time merge: fetch 50 items from cache + fetch last 10 posts from each of 50 celebrities = 550 fetches, parallelized to ~10ms

**Common misconception**: Candidates say "use pull for everything." Pull-only means every feed load queries 200+ user timelines and merges them — at 500K reads/sec, that's 100M DB queries/sec. Caching helps but doesn't eliminate the fan-in cost. Push is essential for the common case.

### Concept 2: Feed Storage — Redis Sorted Sets

**What it is**: Each user has a pre-computed feed stored as a Redis sorted set, where the score is the post timestamp (or a ranking score) and the value is the post ID.

**How it applies here**:
```
ZADD user:12345:feed 1707696000 "post:abc123"
ZADD user:12345:feed 1707696060 "post:def456"
ZREVRANGE user:12345:feed 0 49  -- Get top 50 posts, newest first
```

**The math/mechanics**:
- Each user's feed holds ~500 post IDs (last few days)
- Post ID: 8 bytes, timestamp: 8 bytes, Redis overhead: ~64 bytes per entry
- Per user: 500 x 80 = 40 KB
- 500M users x 40 KB = 20 TB total — needs a Redis Cluster (~64 nodes with 512 GB each)
- But only DAU feeds need to be hot. 500M DAU x 40 KB = 20 TB still — we shard across the cluster

**Common misconception**: Candidates store the entire post content in the feed cache. Store only post IDs. Fetch full post content in a separate batch call to the post service. This reduces cache size by 10x and avoids update propagation when a post is edited.

### Concept 3: Social Graph and the "Small World" Problem

**What it is**: The social graph determines fan-out. It's stored separately from the feed and posts because graph queries (who follows whom) are fundamentally different from content queries.

**How it applies here**: We need two queries: (1) given a user, who are their followers? (push path), and (2) given a user, who do they follow? (pull path). These are inverse lookups on the same graph.

**The math/mechanics**:
- Adjacency list in a graph DB or simple key-value store
- `followers:userA` → set of user IDs who follow A (needed for fan-out)
- `following:userA` → set of user IDs A follows (needed for feed construction)
- Both stored in Redis as sets for O(1) membership checks
- Celebrity detection: flag users where `|followers| > threshold` (e.g., 500K)

**Common misconception**: Candidates forget that the social graph is the biggest data structure in the system. With 500M users x 200 avg connections, that's 100B edges. At 16 bytes per edge (two user IDs), that's 1.6 TB just for the graph — it needs its own storage tier.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Fan-Out Strategy and the Celebrity Problem"

**Interviewer**: "You said hybrid fan-out. Walk me through exactly what happens when Taylor Swift posts to her 100M followers."

**You**: "Taylor Swift is flagged as a celebrity (followers > 500K threshold). When she posts, the post goes to the Post Service, which writes it to Cassandra (the posts table). The fan-out service checks her follower count, sees she's a celebrity, and does NOT fan out to individual feeds. Instead, the post is added to a 'celebrity posts' cache — a per-celebrity sorted set in Redis. When any of her followers opens their feed, the Feed Service does two things in parallel: (1) fetches the pre-computed feed from the user's personal feed cache (the pushed items), and (2) fetches recent posts from all celebrities the user follows. It merges these two lists, ranks them, and returns top 50."

**Interviewer**: "What's the read latency impact? Now every feed read has to merge from multiple sources."

**You**: "Let's break it down. Step 1: Fetch user's pre-computed feed from Redis — one ZREVRANGE call, ~2ms. Step 2: Get list of celebrities the user follows — one SMEMBERS call on the 'following:celebrities' set, ~1ms. Say the user follows 30 celebrities. Step 3: Fetch last 10 posts from each celebrity's timeline — 30 parallel ZREVRANGE calls, ~3ms (pipelined). Step 4: Merge-sort the cached feed + celebrity posts — in-memory, < 1ms. Step 5: Pass to ranking service for scoring — ~10ms for an ML model inference. Total: ~17ms for the feed construction, well under our 300ms SLA. The celebrity pull adds about 5ms versus a pure push model."

**Interviewer**: "What if a celebrity unfollows or blocks someone? How do you ensure blocked users don't see their posts?"

**You**: "Block lists are checked at read time, not write time. When merging celebrity posts into a user's feed, we check if the celebrity has blocked this user (lookup in a block list cache — Redis set). If blocked, we skip that celebrity's posts. This is why pull-at-read-time is actually an advantage for celebrity content — we always have the latest relationship state. With push, we'd need to retroactively remove posts from millions of feeds, which is a nightmare. The block check adds one Redis SISMEMBER per celebrity — ~0.1ms each, negligible."

**Interviewer**: "How do you decide the celebrity threshold? What about users who go viral overnight — suddenly getting 10M followers from 1K?"

**You**: "The threshold isn't a hard line — it's a spectrum. I'd use a tiered system: under 10K followers, always push. Over 1M, always pull. Between 10K and 1M, it depends on posting frequency. A user who posts once a week with 500K followers — push is fine (500K writes once a week). A user who posts 20 times a day with 500K followers — that's 10M writes/day, switch to pull. For the viral scenario, we run a background job that monitors follower growth rate. When a user crosses the threshold, we stop fan-out for new posts immediately. Their existing pushed posts remain in follower feeds until they age out naturally. No retroactive cleanup needed."

### Deep Dive Path 2: "Feed Ranking and Real-Time Updates"

**Interviewer**: "You mentioned a ranking service. How does feed ranking work, and how do you keep it fast enough?"

**You**: "The ranking model takes the merged candidate set (say 200 posts) and scores each one based on features: relationship strength (how often the user interacts with the author), content type engagement (does this user like photos more than text?), recency, and global engagement signals (is this post trending?). The model is a lightweight neural net — not a transformer, something like a DeepFM or a wide-and-deep model that runs inference in ~5ms for 200 items. We pre-compute feature embeddings offline (user-author affinity scores, content embeddings) and store them in a feature store (Redis or a specialized system like Feast). At query time, we fetch features and run inference."

**Interviewer**: "What about new posts appearing in real-time? Like if I'm scrolling and a friend posts — does it just appear?"

**You**: "Two approaches. First, polling: the client polls every 30 seconds with a 'last seen timestamp.' The feed service returns only new items since that timestamp. This is simple but adds latency (up to 30 seconds) and wastes bandwidth for most polls that return nothing. Second, push via WebSocket or SSE: the fan-out service, when pushing to a user's feed cache, also publishes to a pub/sub channel. If the user has an active WebSocket connection, the notification is pushed immediately. The client shows a 'new posts' badge — the user taps it to refresh. I'd use WebSocket for active users and fall back to polling for background sessions. The key is to NOT insert new posts into the current view automatically — it's a terrible UX to have content shifting while reading."

**Interviewer**: "How do you handle the cold-start problem — a new user with no following, or a user who hasn't opened the app in 6 months?"

**You**: "For a new user with no following: the feed is empty, so we fall back to an 'Explore' feed — trending content, popular posts in their locale, content from suggested accounts. This is purely a pull-based operation: query the trending posts cache and the recommendation service. For a returning user after 6 months: their feed cache in Redis has likely been evicted (we TTL feed caches at 7 days inactive). On their first request, we rebuild their feed from scratch — pull posts from the last 48 hours from all accounts they follow, rank them, cache the result. This takes longer (~500ms-1s for the first load) but subsequent reads are fast. We can pre-warm feeds for users who show 're-engagement signals' (opening the app's landing page, receiving a push notification)."

### Deep Dive Path 3: "Storage, Consistency, and Failure Modes"

**Interviewer**: "Walk me through the write path. A user publishes a post — what happens step by step?"

**You**: "The client sends the post to the API gateway, which routes to the Post Service. Step 1: Validate content (spam check, content moderation — async pipeline, don't block the write). Step 2: Write the post to Cassandra (posts table, partition key = user_id, clustering key = timestamp DESC). This is the source of truth. Step 3: Publish a 'new post' event to Kafka. Step 4: Return 200 to the client — the post is committed. The fan-out service consumes from Kafka: it looks up the author's followers, checks if the author is a celebrity (if yes, just write to the celebrity timeline cache). For non-celebrities, it fans out — writing the post ID to each follower's feed sorted set in Redis. At 200 followers average, this takes ~2ms (pipelined Redis ZADD). Step 5: Async — content moderation pipeline processes the post. If flagged, remove from all feeds."

**Interviewer**: "What if the fan-out service crashes after writing to 100 of 200 follower feeds?"

**You**: "Kafka gives us at-least-once delivery. If the fan-out consumer crashes mid-processing, the message offset isn't committed, and another consumer picks it up. The problem is partial fan-out — those 100 followers already got the post. The retry will add it again to all 200 feeds. That means 100 followers get a duplicate. Solution: use the post ID as a deduplication key. Redis sorted sets inherently handle this — ZADD with the same member (post ID) and score just overwrites, no duplicate entry. So retrying the fan-out is idempotent. The 100 followers who missed the post get it on retry, the 100 who already have it just get a no-op ZADD."

**Interviewer**: "How much memory does your Redis cluster need, and what happens if a Redis node goes down?"

**You**: "Feed cache sizing: 500M users x 500 post IDs per feed x 80 bytes per entry = 20 TB. With Redis Cluster, we'd need ~40 nodes with 512 GB each (50% memory buffer for fragmentation and overhead). Each node holds ~12.5M user feeds. If a node goes down, its replica promotes (Redis Cluster uses async replication with automatic failover). We lose feeds that were written to the primary but not yet replicated — maybe the last 1-2 seconds of fan-out writes. Those users will have slightly stale feeds until they're rebuilt or new fan-outs arrive. For durability, the feed is a cache, not the source of truth. We can always rebuild any user's feed by querying Cassandra for posts from all users they follow. The rebuild is expensive (~200 Cassandra reads per user) but it's only needed for the ~12.5M users on the failed node."

**Interviewer**: "At 20 TB of Redis, that's expensive. How would you optimize cost?"

**You**: "Three optimizations. First, only cache active users' feeds. If a user hasn't opened the app in 7 days, evict their feed (LRU/TTL). That drops us from 500M to maybe 200M feeds — 8 TB. Second, store only post IDs (8 bytes) not full content. Third, compress the sorted set — instead of individual ZADD entries, batch the feed into a compact binary format and store as a single Redis string. This eliminates the per-entry overhead. Fourth, consider a tiered approach: hot feeds (last 24h active users) in Redis, warm feeds (1-7 days) in a cheaper store like Memcached or even SSDs. Most feed reads will hit the hot tier."

---

## How Real Companies Built This

- **Meta/Facebook**: Uses the hybrid fan-out model described here. Their system is called TAO (The Associations and Objects) for the social graph and Multifeed for the ranking. The ranking model runs on custom hardware (Facebook's Zion platform). See: "Serving a Billion Personalized News Feeds" (Meta Engineering blog, 2017), and "TAO: Facebook's Distributed Data Store for the Social Graph" (USENIX ATC 2013).
- **Twitter**: Originally used a pure push model (fan-out on write). When Justin Bieber tweeted, it literally caused 30M+ writes per tweet. They moved to a hybrid model in ~2012. See: "The Architecture Twitter Uses to Deal with 150M Active Users" (InfoQ, Raffi Krikorian's talk).
- **LinkedIn**: Uses a feed that's primarily pull-based with heavy caching, due to their different access pattern (users check LinkedIn much less frequently than Twitter/Facebook). See: LinkedIn Engineering blog on feed architecture.
- **Key lesson**: The fan-out strategy is the most impactful decision in this design. Getting it wrong means either write amplification (pure push) or read amplification (pure pull) at catastrophic scale. Every company at scale uses some form of hybrid.

---

## The Complete Reference Design

### API Design
```
POST /api/v1/feed/posts
Request: {
    "content": "Hello world!",
    "media_ids": ["img_abc123"],
    "visibility": "public"        // public, friends_only, private
}
Response: {
    "post_id": "p_7f3a2b",
    "author_id": "u_12345",
    "created_at": "2026-02-12T10:30:00Z",
    "status": "published"
}
Headers: X-Request-ID: uuid-v4

GET /api/v1/feed?cursor=<opaque_cursor>&limit=50
Response: {
    "items": [
        {
            "post_id": "p_7f3a2b",
            "author": {"id": "u_12345", "name": "Alice", "avatar_url": "..."},
            "content": "Hello world!",
            "media": [{"type": "image", "url": "..."}],
            "engagement": {"likes": 42, "comments": 7, "shares": 3},
            "created_at": "2026-02-12T10:30:00Z",
            "ranking_score": 0.95
        }
    ],
    "next_cursor": "eyJ0cyI6MTcwNzY5NjAwMH0=",
    "has_more": true
}

GET /api/v1/feed/updates?since=1707696000
Response: {
    "new_count": 3,
    "preview": "Alice, Bob, and 1 other posted"
}
```

### Database Schema
```sql
-- Cassandra: Posts table
CREATE TABLE posts (
    user_id     BIGINT,
    post_id     TIMEUUID,
    content     TEXT,
    media_urls  LIST<TEXT>,
    visibility  TEXT,
    created_at  TIMESTAMP,
    PRIMARY KEY (user_id, post_id)
) WITH CLUSTERING ORDER BY (post_id DESC)
  AND default_time_to_live = 7776000;  -- 90 days TTL

-- Cassandra: Social graph (followers)
CREATE TABLE followers (
    user_id      BIGINT,
    follower_id  BIGINT,
    followed_at  TIMESTAMP,
    PRIMARY KEY (user_id, follower_id)
);

-- Cassandra: Social graph (following)
CREATE TABLE following (
    user_id       BIGINT,
    followee_id   BIGINT,
    followed_at   TIMESTAMP,
    is_celebrity  BOOLEAN,
    PRIMARY KEY (user_id, followee_id)
);

-- Redis: Feed cache (sorted set per user)
-- Key: feed:{user_id}
-- Members: post_id (string)
-- Scores: timestamp or ranking score (float)
```

### Key Algorithms
```python
import asyncio
from typing import List, Tuple

CELEBRITY_THRESHOLD = 500_000

async def fan_out_post(post_id: str, author_id: str, timestamp: float):
    """Fan out a post to followers' feeds. Called by Kafka consumer."""
    follower_count = await redis.scard(f"followers:{author_id}")

    if follower_count > CELEBRITY_THRESHOLD:
        # Celebrity path: just add to celebrity timeline, no fan-out
        await redis.zadd(f"celebrity_timeline:{author_id}", {post_id: timestamp})
        await redis.zremrangebyrank(f"celebrity_timeline:{author_id}", 0, -501)
        return

    # Normal path: fan-out to all followers
    followers = await redis.smembers(f"followers:{author_id}")
    pipe = redis.pipeline()
    for follower_id in followers:
        pipe.zadd(f"feed:{follower_id}", {post_id: timestamp})
        pipe.zremrangebyrank(f"feed:{follower_id}", 0, -501)  # Keep last 500
    await pipe.execute()

async def get_feed(user_id: str, cursor: float, limit: int = 50) -> List[dict]:
    """Fetch a user's feed: merge cached feed + celebrity posts."""
    # Step 1: Fetch pre-computed feed (pushed items)
    cached_posts = await redis.zrevrangebyscore(
        f"feed:{user_id}", cursor, "-inf", start=0, num=limit * 2,
        withscores=True
    )

    # Step 2: Fetch celebrity posts this user should see
    celebrity_ids = await redis.smembers(f"following:celebrities:{user_id}")
    celebrity_tasks = [
        redis.zrevrangebyscore(
            f"celebrity_timeline:{celeb_id}", cursor, "-inf",
            start=0, num=10, withscores=True
        )
        for celeb_id in celebrity_ids
    ]
    celebrity_results = await asyncio.gather(*celebrity_tasks)

    # Step 3: Merge and sort by timestamp
    all_posts = list(cached_posts)
    for result in celebrity_results:
        all_posts.extend(result)
    all_posts.sort(key=lambda x: x[1], reverse=True)  # Sort by score/timestamp

    # Step 4: Rank (simplified — production uses ML model)
    ranked = await ranking_service.rank(user_id, all_posts[:limit * 2])
    return ranked[:limit]
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Feed Cache (Redis) | 200M active users x 500 posts x 80 bytes | ~8 TB (16 nodes x 512 GB) |
| Posts DB (Cassandra) | 1B posts/day x 1 KB avg x 90 days | ~90 TB |
| Social Graph | 500M users x 200 edges x 16 bytes | ~1.6 TB |
| Fan-out writes | 12K posts/sec x 200 followers | 2.4M Redis writes/sec |
| Feed reads | 500K/sec peak | ~32 Redis nodes (16K QPS each) |
| Network | 500K reads/sec x 50 KB response | ~25 GB/sec |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Understands push vs pull, designs the basic pipeline, handles feed caching | Explains fan-out on write, designs Redis sorted set feed cache, calculates storage correctly |
| Staff | Identifies the celebrity problem unprompted, proposes hybrid model, considers ranking implications | Designs tiered fan-out with celebrity threshold, proposes feed ranking architecture, discusses cache cost optimization |
| Principal | Questions the problem framing, considers content moderation pipeline, thinks about recommendation evolution | Discusses how ML ranking dominates feed quality, proposes exploration/exploitation trade-offs, designs the system for A/B testing different ranking models, considers regulation (content filtering, algorithmic transparency) |

---

## Red Flags & Common Mistakes

- **Pure push model without considering celebrities**: This is the #1 disqualifier. If you don't address the celebrity fan-out problem, the interviewer will assume you haven't thought about scale.
- **Storing full post content in the feed cache**: Store IDs only. Content lives in a separate post store. This is a 10x storage and update-propagation difference.
- **Ignoring feed ranking**: A chronological feed is a toy. Every production feed uses ML ranking. At least mention it, even if you don't design the ML pipeline.
- **Not discussing pagination/cursor strategy**: Offset-based pagination breaks with real-time feeds (new posts shift offsets). Use cursor-based pagination with timestamps.
- **Forgetting content moderation**: When a post is flagged/removed, you need to remove it from potentially millions of cached feeds. This is the reverse fan-out problem and it's expensive.
