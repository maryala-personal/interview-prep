# Design Search Autocomplete / Typeahead

> **Companies**: Google, Meta, Amazon, LinkedIn, Uber | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a system that serves suggestions in under 100ms at massive scale? This probes your understanding of trie data structures (or alternatives), prefix matching at scale, ranking algorithms, and how to keep suggestions fresh without sacrificing latency. The interviewer wants to see you reason about the tension between data freshness and serving speed.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**Questions that show the interviewer you know what you're doing:**

- "What's the expected QPS for autocomplete requests? Are we talking Google-scale (billions/day) or a mid-tier product?"
- "What's our p99 latency SLA? Autocomplete is useless above 100-200ms — are we targeting sub-50ms p99?"
- "How many unique search terms are we indexing? Millions or billions of distinct prefixes?"
- "Do we need personalized suggestions (user-specific) or just global popularity?"
- "How fresh do suggestions need to be? Can we tolerate minutes of staleness, or do trending queries need to appear in seconds?"
- "Multi-language support? CJK languages don't have space-delimited words — that changes the prefix strategy entirely."
- "Do we need to filter offensive/sensitive content in real-time?"
- "Single region or multi-region? Where are users concentrated?"

### Working Assumptions
| Parameter | Value | Derivation |
|-----------|-------|------------|
| DAU | 500M | Large search engine scale |
| Searches/user/day | 6 | Average engagement |
| Keystrokes per search triggering autocomplete | 8 | Average query ~4 words, ~2 keystrokes before selecting suggestion |
| Autocomplete QPS (average) | ~280K | 500M x 6 x 8 / 86,400 |
| Autocomplete QPS (peak) | ~840K | 3x average for peak hours |
| Unique queries | 5B total, 100M with meaningful frequency | Long tail — top 100M cover 99% of traffic |
| Suggestion latency SLA | p50 < 30ms, p99 < 100ms | Must feel instant to user |
| Top-K suggestions returned | 10 per prefix | Standard UX convention |
| Data freshness | Minutes for trending, hours for general | Trending queries need a fast path |
| Average query length | ~20 characters (~50 bytes with metadata) | Based on industry data |

---

## High-Level Design (Brief — 5 minutes)

```
User types "how t"
    |
    v
+---------------+     +------------------+     +-----------------------+
|  Client/App   |---->|  API Gateway /   |---->|  Autocomplete Service |
|  (debounce    |     |  Load Balancer   |     |  (stateless, reads    |
|   50-100ms)   |     |                  |     |   from local trie)    |
+---------------+     +------------------+     +-----------+-----------+
                                                           | read
                                                           v
                                                +-----------------------+
                                                |  In-Memory Trie       |
                                                |  (replicated to all   |
                                                |   serving nodes)      |
                                                +-----------+-----------+
                                                            | built from
                                                            v
+---------------+     +------------------+     +-----------------------+
|  Search Logs  |---->|  Aggregation     |---->|  Trie Builder         |
|  (Kafka)      |     |  Pipeline        |     |  (offline, periodic)  |
|               |     |  (Flink/Spark)   |     |                       |
+---------------+     +------------------+     +-----------------------+
                                                            |
                                                +-----------------------+
                                                |  Trending Service     |
                                                |  (near real-time      |
                                                |   frequency counts)   |
                                                +-----------------------+
```

**Why this architecture?**: The core insight is separating the **read path** (serving suggestions from in-memory tries on every node) from the **write path** (aggregating query frequencies offline and rebuilding tries periodically). This lets us serve at sub-50ms latency while still incorporating fresh data. The trending service is a fast path for breaking queries that can't wait for the next trie rebuild.

---

## Core Concepts Deep Dive

### Concept 1: Trie Data Structure & Prefix Matching

**What it is**: A trie (prefix tree) is a tree where each node represents a character. To find all completions for "how t", you traverse h->o->w-> ->t and then collect the top-K scored children. The critical optimization: at each trie node, we precompute and cache the top-10 suggestions reachable from that subtree.

**How it applies here**: With top-K caching at each node, every prefix lookup is O(L) where L = prefix length. No subtree traversal at query time.

**The math/mechanics**: For 100M unique queries averaging 20 characters:
- Naive trie: ~2B nodes (but with sharing, closer to 500M-1B)
- With top-K caching at each node: each node stores 10 pointers + scores = ~120 bytes/node
- Total memory: ~60-120GB — too large for a single machine
- **Solution**: Use a compressed radix tree (merge single-child chains), prune low-frequency queries, and partition by first 2 characters (26^2 = 676 partitions), each ~40-100MB

**Common misconception**: Candidates say "just use a trie" without addressing that a naive trie for billions of queries won't fit in memory. You need to prune (only keep queries above a frequency threshold), compress (merge single-child chains into a Patricia/radix tree), and partition.

### Concept 2: Ranking & Time-Decayed Scoring

**What it is**: Raw frequency alone produces stale suggestions. You need a scoring function that blends: query frequency, recency (time-decayed), and optionally user personalization.

**How it applies here**: `score = w1 * frequency + w2 * recency_decay(t) + w3 * user_affinity`. The recency decay uses exponential smoothing: `score_new = alpha * current_count + (1 - alpha) * score_old`. With alpha = 0.01 for hourly updates, a query needs sustained popularity to stay in top-K. A sudden spike (trending) is detected when `current_hour_count > 3x rolling_24h_average`.

**Common misconception**: Many candidates only consider raw frequency. Interviewers want to hear about recency bias (yesterday's viral query shouldn't dominate forever), personalization, and abuse prevention (someone can't spam-search to inject suggestions).

### Concept 3: Data Collection & Aggregation Pipeline

**What it is**: Every search generates a log event. You can't update the trie on every keystroke — you'd have billions of writes/day. Batch-aggregate instead.

**How it applies here**: Search logs flow into Kafka -> Flink aggregates counts per query per time window (1-hour tumbling windows) -> writes aggregated counts to a frequency store -> Trie Builder reads this store periodically (every 15-30 min) and produces a new trie snapshot -> snapshots distributed to serving nodes via S3.

**The math/mechanics**: 500M DAU x 6 searches = 3B search events/day. Flink reduces this to ~100M unique query-count pairs per hour. Trie builder processes 100M records in ~5 minutes on a 16-core machine.

**Common misconception**: Candidates try to update the trie in real-time per query. This is unnecessary (users don't need second-level freshness) and dangerous (write amplification destroys serving latency). Batch aggregation with a fast path only for trending is the answer.

### Concept 4: Atomic Trie Swap for Zero-Downtime Updates

**What it is**: Each serving node holds a trie in memory. When a new snapshot is ready, the node builds the new trie in background memory, then atomically swaps the pointer. Old trie is garbage collected.

**How it applies here**: Trie snapshots are serialized as flat files (~100-200MB per partition) in S3. Serving nodes poll for new snapshots, load into shadow memory, and swap. Zero downtime, zero serving impact.

**Common misconception**: Candidates propose distributed caches (Redis) for serving. A network hop per keystroke kills latency. In-memory local tries are the standard — the data is small enough and latency requirements strict enough.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Trie Design & Memory Optimization

**Interviewer**: "Walk me through the data structure. You said trie — how exactly are you storing 100M queries in memory?"

**You**: "I'd use a compressed radix tree where single-child chains are merged into one node. For 'interview', 'interesting', 'internal', the prefix 'inter' is a single node, not 5 separate ones. Each node stores: the compressed label (variable-length string), child pointers (hash map of next characters), and a precomputed top-10 list of `(query_string, score)` tuples. The top-10 list is the key optimization — every lookup is O(prefix_length) with no subtree traversal needed."

**Interviewer**: "How much memory does that actually take? Show me the math."

**You**: "100M unique queries, average 20 characters. A compressed radix tree typically has 1.5-2x nodes relative to unique strings — call it 150-200M nodes. Each node: 8 bytes label pointer + 8 bytes child map pointer + top-10 list at ~120 bytes (10 x 12 bytes for pointer + score) = ~136 bytes/node. So 200M x 136 = ~27GB. That's large but fits on modern machines with 64-128GB RAM. If we partition by first 2 characters into 676 shards, each shard is ~40MB. Easily fits with room for double-buffering during swaps."

**Interviewer**: "What if we have 5 billion unique queries, not 100 million?"

**You**: "Then the trie won't fit on a single machine even compressed. Two strategies: first, aggressively prune — only keep queries with frequency above a threshold (searched at least 10 times in the past month). That typically reduces 5B to under 500M given the Zipf distribution. Second, partition across machines using consistent hashing on the first N characters of the prefix. Each autocomplete request routes to one shard server. The downside is a network hop per request, but with co-located servers in the same AZ, that's ~0.5ms added latency."

**Interviewer**: "How does the top-K precomputation work when scores change?"

**You**: "During trie build, I do a bottom-up post-order traversal. Leaf nodes have their own score. Each internal node merges the top-10 lists of all children using a min-heap — take the top 10 across all children. This is O(N x K x log K) for the whole trie. When scores change at the next rebuild, the entire trie is rebuilt from scratch — simpler and more correct than incremental updates. Rebuild takes 5-10 minutes for 200M nodes, and we swap atomically."

**Interviewer**: "Why not use an inverted index like Elasticsearch?"

**You**: "For pure prefix matching with top-K, a trie with precomputed results is strictly faster — O(prefix_length) vs. O(prefix_length x log N) for an FST-based index. But Elasticsearch's completion suggester is the right answer at smaller scale (under 10M terms) because you get it for free. The custom trie only makes sense at hundreds of thousands of QPS with sub-50ms p99 requirements."

### Deep Dive Path 2: Freshness & Trending Queries

**Interviewer**: "A celebrity dies. Everyone starts searching their name. How fast does it appear in suggestions?"

**You**: "Two paths. The normal path — trie rebuild every 15-30 minutes — would take up to 30 minutes. Too slow for breaking events. So I'd add a trending layer: a separate in-memory data structure — a Count-Min Sketch or a simple hash map with sliding window counts — that tracks query frequencies in real-time via Kafka. When a query's current frequency exceeds 3x its rolling average, it's flagged as trending."

**Interviewer**: "How does the serving layer incorporate trending results?"

**You**: "At query time, the autocomplete service checks two sources: the static trie (bulk of suggestions) and the trending store (small — maybe 1000 trending queries globally). It merges results from both, with trending queries getting a score boost. The trending store is tiny, replicated to all servers via pub/sub with sub-second propagation. This gives seconds-level freshness for breaking queries without touching the trie rebuild pipeline."

**Interviewer**: "What about abuse? Someone scripts millions of searches for an offensive term to make it trend."

**You**: "Three layers. First, rate limiting per user/IP at the API gateway — no single user generates enough volume to move the needle. Second, the aggregation pipeline deduplicates by user — each user's query counts once per time window regardless of repetitions. Third, a blocklist filter in both the aggregation pipeline (don't count blocked terms) and at serving time (don't return blocked suggestions). The blocklist is maintained by a content moderation team and deployed as a config update."

**Interviewer**: "How would you handle this at startup scale vs. Google scale?"

**You**: "At startup scale (1M DAU), I wouldn't build any of this. I'd use Elasticsearch's completion suggester with an FST-based index. It handles prefix matching efficiently, scales to millions of terms, and the freshness issue doesn't matter at lower query volume. The custom trie architecture only makes sense when you're at hundreds of thousands of QPS and sub-50ms p99 is non-negotiable."

### Deep Dive Path 3: Multi-Region & Data Pipeline Resilience

**Interviewer**: "We're global — users in Tokyo, London, San Francisco. How does this work across regions?"

**You**: "Autocomplete is a great candidate for full regional independence. Each region has its own trie servers, its own aggregation pipeline, and its own trie builder. The source data (search logs) is region-local — Tokyo users generate Tokyo logs, which build Tokyo-specific tries. No cross-region consistency needed because suggestions should be locally relevant."

**Interviewer**: "But global trends? Something trending in the US should appear for Japanese users searching in English."

**You**: "Good call. I'd add a global aggregation layer that merges regional trending data. Each region publishes its trending queries to a global Kafka topic. A global aggregator produces a 'worldwide trending' list. Each region merges this global list into its local serving layer. Cross-region propagation latency is seconds via Kafka replication — acceptable for trending."

**Interviewer**: "What happens when the trie build fails? Or Kafka goes down?"

**You**: "Graceful degradation is key. If the trie build fails, serving nodes keep serving the previous snapshot — suggestions are stale but functional. I'd version every snapshot and keep the last 3 in S3 for rollback. If Kafka goes down, the aggregation pipeline stalls but serving is unaffected — it's decoupled. Trending detection degrades (no new trending queries), but the static trie still serves. The system should never return empty results. I'd also have a circuit breaker: if trie load time exceeds a threshold, abort and keep the old trie."

**Interviewer**: "How do you monitor the health of this pipeline?"

**You**: "Key metrics: trie age (time since last successful rebuild — alert if > 1 hour), Kafka consumer lag (alert if > 30 minutes), suggestion quality (sample queries and check if top suggestion is reasonable — A/B testing), and serving latency p99. I'd also track trie build duration and size over time — a sudden size change indicates a data quality issue in the pipeline."

---

## How Real Companies Built This

- **Google**: Uses precomputed suggestion tables (not a live trie) for the most common prefixes plus a real-time trending layer. The top 1M prefixes cover 99% of traffic and are served as flat lookup tables. For rare prefixes, they fall back to a more expensive search path. Reference: Google's original autocomplete patent; Zheng et al.'s work on efficient prefix matching.

- **LinkedIn**: Built a typeahead service using Lucene-based inverted index with prefix queries. For entity search (people, companies), an inverted index with prefix tokenization outperformed tries because they needed to match on multiple fields (name, title, company). Blog: https://engineering.linkedin.com/blog

- **Bing**: Uses a layered approach — L1 cache of top 10K prefixes (direct lookup), L2 compressed trie for medium-frequency, L3 disk-backed index for the long tail. Tiered serving optimizes for the Zipf distribution of query frequencies.

- **Key lesson**: Production autocomplete systems rarely use a single data structure. They combine precomputed tables for hot prefixes, tries for medium frequency, and fallback search for rare queries. The 80/20 rule applies heavily.

---

## The Complete Reference Design

### API Design
```
GET /v1/suggestions?prefix=how+t&limit=10&user_id=abc123
Headers: X-Region: us-west-2, X-Session-Id: xyz

Response 200:
{
  "suggestions": [
    {"text": "how to tie a tie", "score": 0.95, "type": "query"},
    {"text": "how to screenshot on mac", "score": 0.91, "type": "query"},
    {"text": "how to lose weight", "score": 0.88, "type": "query"}
  ],
  "trending": [
    {"text": "how to watch super bowl 2026", "score": 0.99, "type": "trending"}
  ],
  "request_id": "req-abc123",
  "latency_ms": 12
}
```

### Database Schema
```sql
-- Aggregated query frequencies (written by Flink, read by Trie Builder)
CREATE TABLE query_frequencies (
    query_hash    BIGINT,            -- murmur3 hash of normalized query
    query_text    VARCHAR(200),
    region        VARCHAR(20),
    time_bucket   TIMESTAMP,          -- hourly bucket
    raw_count     BIGINT,
    unique_users  BIGINT,
    decayed_score DOUBLE,
    PRIMARY KEY (query_hash, region, time_bucket)
) PARTITION BY RANGE (time_bucket);

CREATE INDEX idx_query_freq_score ON query_frequencies(region, decayed_score DESC);

-- Blocklist for content filtering
CREATE TABLE suggestion_blocklist (
    pattern    VARCHAR(200) PRIMARY KEY,
    reason     VARCHAR(100),
    added_at   TIMESTAMP,
    added_by   VARCHAR(50)
);
```

### Key Algorithms
```python
import heapq
import collections
import math

class TrieNode:
    __slots__ = ['children', 'top_suggestions', 'is_end', 'label']

    def __init__(self, label=''):
        self.label = label
        self.children = {}          # char -> TrieNode
        self.top_suggestions = []   # [(score, query_text)] max size K
        self.is_end = False


class AutocompleteTrie:
    def __init__(self, k=10):
        self.root = TrieNode()
        self.k = k

    def build_from_scored_queries(self, queries_with_scores):
        """Build trie from list of (query, score) tuples."""
        for query, score in queries_with_scores:
            self._insert(query, score)
        self._propagate_top_k(self.root)

    def _insert(self, query, score):
        node = self.root
        for ch in query:
            if ch not in node.children:
                node.children[ch] = TrieNode(ch)
            node = node.children[ch]
        node.is_end = True
        node.top_suggestions = [(score, query)]

    def _propagate_top_k(self, node):
        """Post-order traversal to bubble up top-K suggestions."""
        all_suggestions = list(node.top_suggestions)
        for child in node.children.values():
            self._propagate_top_k(child)
            all_suggestions.extend(child.top_suggestions)
        all_suggestions.sort(key=lambda x: -x[0])
        node.top_suggestions = all_suggestions[:self.k]

    def search(self, prefix):
        """Return top-K suggestions for prefix. O(len(prefix))."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        return node.top_suggestions


class TrendingDetector:
    """Detects trending queries using sliding window comparison."""
    def __init__(self, window_hours=24, spike_threshold=3.0):
        self.window_hours = window_hours
        self.spike_threshold = spike_threshold
        self.hourly_counts = {}  # query -> deque of (timestamp, count)

    def update(self, query, count, timestamp):
        if query not in self.hourly_counts:
            self.hourly_counts[query] = collections.deque(
                maxlen=self.window_hours
            )
        self.hourly_counts[query].append((timestamp, count))

    def is_trending(self, query, current_count):
        if query not in self.hourly_counts:
            return current_count > 1000  # absolute threshold for new queries
        history = self.hourly_counts[query]
        if len(history) < 2:
            return False
        avg = sum(c for _, c in history) / len(history)
        return avg > 0 and current_count / avg > self.spike_threshold
```

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Trie memory (per shard) | 200M nodes x 136 bytes / 676 shards | ~40MB per shard |
| Total trie memory (3 replicas) | 27GB x 3 replicas | ~81GB across fleet |
| Serving nodes | 840K peak QPS / 50K QPS per node | ~17 nodes (with 2x headroom: 34) |
| Kafka throughput | 3B events/day x 100 bytes | ~3.5MB/s sustained |
| Flink aggregation | 100M unique queries/hour | 4-8 task managers |
| Trie build time | 200M nodes, single threaded | ~5-10 minutes |
| Storage (query_frequencies) | 100M rows x 250 bytes x 720 hours | ~18TB (30 days) |
| Network (trie distribution) | 27GB snapshot to 34 nodes every 15 min | ~240Mbps |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Solid trie implementation, correct capacity math, handles basic scaling | Designs trie with top-K precomputation, calculates memory, adds caching layer |
| Staff | Separates read/write paths, designs data pipeline, handles freshness/trending, reasons about trade-offs between data structures | Adds the Kafka->Flink->TrieBuilder pipeline, trending detection with Count-Min Sketch, explains why tries beat inverted indexes here, discusses regional deployment |
| Principal | Questions assumptions, proposes tiered architecture, designs for graceful degradation, thinks about organizational boundaries | Proposes L1/L2/L3 serving tiers, designs trending as a separate service with independent SLA, plans for trie build failures (serve stale), considers A/B testing infrastructure for ranking |

---

## Red Flags & Common Mistakes
- **Using Redis/Memcached for serving**: Adding a network hop per keystroke is a latency killer. In-memory local data structures are the right answer for this problem.
- **Updating trie on every query**: Write amplification destroys serving performance. Batch aggregation is the way.
- **Ignoring the long tail**: The top 1M prefixes handle 99% of traffic. Don't over-engineer for rare prefixes.
- **No content filtering story**: Interviewers expect you to mention blocklists and abuse prevention unprompted.
- **Over-engineering personalization**: Unless the interviewer asks, keep it to global popularity + trending. Personalized suggestions are a separate system.
- **Forgetting client-side optimization**: Debouncing (wait 50-100ms between keystrokes before sending) and client-side caching (cache results for prefixes already fetched) reduce QPS by 50-70%.
- **No graceful degradation plan**: What if the trie build fails? Serve the previous snapshot. What if Kafka is down? Suggestions are stale but still work. The system should never return empty results.
