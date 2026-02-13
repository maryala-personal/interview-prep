# Design an Ad Click Aggregation System

> **Companies**: Meta, Google, Amazon, Twitter/X, TikTok, Snap, Pinterest | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Exactly-once counting at massive scale, late-arriving data handling, lambda vs kappa architecture trade-offs, real-time aggregation with correctness guarantees, reconciliation between real-time and batch pipelines

---

## The First 5 Minutes — Scoping & Technical Clarifications

1. **What aggregation granularity?** Per-ad per-minute? Per-campaign per-hour? This determines window sizes and storage requirements.
2. **Latency requirement?** How fast must aggregated counts be available? Real-time (<1 min) for bidding optimization vs near-real-time (<1 hour) for reporting dashboards?
3. **Exactly-once semantics?** Ad clicks are money. Over-counting charges advertisers too much (legal liability). Under-counting loses revenue. What's the tolerance?
4. **Click-through rate (CTR)?** What fraction of impressions become clicks? Typical is 0.5-2%. This determines click volume relative to impression volume.
5. **Fraud detection integration?** Do we filter invalid/bot clicks before aggregation or after? This affects the pipeline architecture.
6. **Late-arriving data?** Clicks can arrive out of order due to mobile offline, network delays. What's the maximum lateness we handle — minutes, hours, days?
7. **Query patterns?** Real-time dashboards (time-series), ad-hoc analytics (slice and dice by dimension), billing reconciliation (exact counts)?
8. **Multi-region?** Are clicks generated globally but aggregated centrally, or per-region?

### Working Assumptions

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Daily ad impressions | 100 billion | Large ad platform (Meta-scale) |
| Click-through rate | 1% | Industry average |
| Daily clicks | 1 billion | 100B x 1% |
| Click events/sec (peak) | 50,000 | 1B/day avg = ~11.5K/s, 4x peak factor |
| Event size | ~500 bytes | ad_id, user_id, timestamp, device, geo, campaign_id |
| Daily click data | ~500 GB | 1B x 500 bytes |
| Aggregation latency | <1 min for real-time, <1 hour for batch | Real-time feeds bidding; batch feeds billing |
| Unique ads | 10 million | Active campaigns |
| Aggregation dimensions | ad_id, campaign_id, geo, device_type, hour | 5 key dimensions |
| Late data window | 7 days | Mobile/offline clicks can arrive very late |

**Storage math**: Pre-aggregated click counts per ad per minute: 10M ads x 1440 min/day x 8 bytes (count) = ~115 GB/day. With 5 dimensions, cross-product is much larger but most cells are sparse — realistic storage is ~500 GB/day for all aggregation tables. Retained for 2 years = ~365 TB.

---

## High-Level Design

```
  Click Events (SDKs, pixels)
          │
    ┌─────▼──────────────────┐
    │  Ingestion Layer       │
    │  (Kafka — partitioned  │
    │   by ad_id)            │
    └─────┬──────────────────┘
          │
    ┌─────┼─────────────────────────────────┐
    │     │                                 │
    │  ┌──▼───────────────┐  ┌──────────────▼──────────┐
    │  │ Real-Time Path   │  │ Batch Path              │
    │  │ (Flink/Spark     │  │ (Spark on hourly        │
    │  │  Streaming)      │  │  Kafka snapshots)       │
    │  │                  │  │                          │
    │  │ - Dedup (bloom)  │  │ - Exact dedup (sort)    │
    │  │ - Window agg     │  │ - Full re-aggregate     │
    │  │ - Approx counts  │  │ - Exact counts          │
    │  └──────┬───────────┘  └──────────┬──────────────┘
    │         │                         │
    │  ┌──────▼───────────┐  ┌──────────▼──────────────┐
    │  │ Real-Time Store  │  │ Batch Store             │
    │  │ (Redis/Druid)    │  │ (ClickHouse/BigQuery)   │
    │  │ Latest counts    │  │ Source-of-truth counts  │
    │  └──────────────────┘  └─────────────────────────┘
    │                                                    │
    │         RECONCILIATION LAYER                       │
    │    (Batch corrects real-time periodically)         │
    └────────────────────────────────────────────────────┘
          │
    ┌─────▼──────────────────┐
    │  Query/API Layer       │
    │  - Dashboard (real-time│
    │    store for freshness)│
    │  - Billing (batch      │
    │    store for accuracy) │
    │  - Analytics (batch    │
    │    store for ad-hoc)   │
    └────────────────────────┘
```

**Why this architecture?** This is the Lambda Architecture: a real-time path for low-latency approximate results and a batch path for high-latency exact results, with reconciliation between them. The real-time path uses Bloom filters for dedup (fast but probabilistic) and tumbling windows for aggregation. The batch path does exact dedup (sort and deduplicate on event ID) and produces the billing source-of-truth. The alternative is Kappa Architecture (single streaming path with exactly-once guarantees) — simpler but harder to achieve true exactly-once at this scale.

---

## Core Concepts Deep Dive

### Concept 1: Exactly-Once Click Counting — The Hard Problem

**What it is**: A click event must be counted exactly once in the final aggregate, despite: (1) network retries (producer sends same click twice), (2) consumer failures (Flink crashes and replays from Kafka), (3) late-arriving duplicates (mobile SDK retries after hours).

**How it applies**: Three levels of dedup: (1) **Client-side**: Each click event gets a unique `click_id` (UUID v4) generated by the SDK. Retries send the same `click_id`. (2) **Ingestion-side**: Kafka dedup using `click_id` as the idempotent key — Kafka producers with `enable.idempotence=true` prevent duplicate writes to the same partition. (3) **Processing-side**: Flink uses checkpointing (Chandy-Lamport snapshots) to ensure exactly-once processing — if a Flink task fails, it restores from the last checkpoint and replays from the Kafka offset stored in that checkpoint. The combination guarantees that each `click_id` is counted exactly once in the output.

**The math**: At 50K clicks/sec, if 0.1% are duplicates (network retries), that's 50 duplicate clicks/sec. Without dedup, daily over-count would be 50 x 86,400 = 4.3M clicks — at $1 CPM, that's $4,300/day of false billing. At Meta's scale (billions of clicks/day), the error would be millions of dollars per month.

**Common misconception**: "Kafka guarantees exactly-once, so we're done." Kafka's exactly-once is within the Kafka system (producer → broker → consumer). End-to-end exactly-once requires the consumer's output to be idempotent — if Flink writes to Redis and crashes, on replay it must not double-count. This requires either idempotent writes (upsert with version) or transactional sinks (Flink's two-phase commit to supported sinks).

### Concept 2: Windowed Aggregation — Tumbling vs Sliding vs Session

**What it is**: Aggregating events within time windows. Tumbling windows: fixed-size, non-overlapping (every 1 minute). Sliding windows: fixed-size, overlapping (1-minute window sliding every 10 seconds). Session windows: variable-size, defined by activity gaps (new window after 30 seconds of no clicks for a user).

**How it applies**: For ad click aggregation, tumbling windows per minute are the standard. The aggregation key is (ad_id, window_start). When a click for ad_id=123 arrives at 10:05:32, it's assigned to window [10:05:00, 10:06:00). The window closes at 10:06:00 and emits the count. For campaign-level reporting, we aggregate over hourly windows. For billing, daily windows.

**The math**: With 10M unique ads and 1-minute windows, the in-memory state during a window is up to 10M counters x 8 bytes = 80 MB. With 5 aggregation dimensions (ad_id, campaign_id, geo, device, hour), the state is 5x but heavily sparse — most (ad_id, geo, device) combinations have zero clicks. Realistic in-memory state: ~500 MB-1 GB. Well within Flink's managed state capabilities.

**Common misconception**: "Just aggregate on event_time." What about late data? A click at 10:05:32 might arrive at 10:07:00 — after the [10:05, 10:06) window has closed. You need watermarks and allowed lateness. Flink's watermark says "I believe all data up to time T has arrived." If a late event arrives after the watermark, it goes to a side output for late data processing or triggers a window update.

### Concept 3: Lambda vs Kappa Architecture

**What it is**: Lambda has two paths (real-time + batch) with reconciliation. Kappa has a single streaming path that serves as both real-time and source-of-truth.

**How it applies**: Lambda's advantage: the batch path can do expensive operations (exact dedup with a full sort, fraud model re-evaluation, backfills) that are impractical in real-time. Kappa's advantage: one codebase, one pipeline, no reconciliation complexity. At Meta/Google scale, Lambda is preferred because: (1) billing accuracy requires batch re-computation as the source of truth, and (2) fraud detection models improve over time — yesterday's clicks need re-evaluation with today's model.

**The math**: Lambda's reconciliation overhead: running a nightly batch job over 1B clicks (500 GB) takes ~30 minutes on a 100-node Spark cluster. The batch results become the source of truth, and any discrepancies with the real-time counts are corrected. Kappa would need to reprocess the same data in-stream when correcting, which at 50K events/sec requires careful backpressure management.

**Common misconception**: "Lambda is outdated, use Kappa." LinkedIn's Jay Kreps (who coined "Kappa") intended it for cases where stream processing is sufficient. For ad billing — where money is at stake and retroactive corrections are needed — having an independent batch path that validates the streaming path is a feature, not a bug. Most large ad platforms use Lambda or a hybrid.

### Concept 4: Fraud Detection Integration

**What it is**: 20-30% of ad clicks are fraudulent (bots, click farms, accidental clicks). Invalid clicks must be filtered before billing but should still be counted for analytics (to show advertisers their traffic quality).

**How it applies**: Two-phase filtering: (1) Real-time: rule-based filters (too many clicks from same IP in 1 second, known bot user agents, click with no preceding impression). Removes ~80% of fraud. (2) Batch: ML model trained on labeled fraud data (click patterns, device fingerprints, session behavior). Catches remaining ~20% of fraud. The real-time filter runs in the streaming path before aggregation. The batch filter runs post-aggregation and adjusts counts retroactively.

**The math**: At 1B clicks/day, 25% fraudulent = 250M invalid clicks. Revenue impact of not filtering: at $0.50 CPC average, that's $125M/day in false charges. Even 1% slippage in fraud detection = $1.25M/day. This is why ad platforms have dedicated anti-fraud teams.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Exactly-Once End-to-End

**Interviewer**: "Walk me through how you guarantee a click is counted exactly once, from the client SDK to the billing report."

**You**: The flow has four stages, each with dedup guarantees. (1) **SDK**: generates a `click_id` (UUID v4) when the user taps. If the network request fails, the SDK retries with the same `click_id`. The server responds with the `click_id` to confirm receipt. (2) **Ingestion**: The click ingestion service writes to Kafka with `click_id` as the message key. Kafka producer has `enable.idempotence=true` — the broker deduplicates retries using the producer ID and sequence number. The click lands on a Kafka partition determined by hash(ad_id) — this ensures all clicks for the same ad go to the same partition, which is important for downstream aggregation. (3) **Stream processing**: Flink consumes from Kafka with exactly-once checkpointing. Flink's state backend stores the running count per (ad_id, window). On checkpoint, Flink atomically commits the Kafka offset and the state snapshot. If the Flink task crashes, it restores from the checkpoint — the Kafka offset rolls back, Flink replays the events, and the state is exactly as it was at checkpoint time. No double-counting. (4) **Sink**: Flink writes aggregated counts to the output store. For exactly-once sink, we use idempotent writes: `UPSERT INTO click_counts (ad_id, window, count) VALUES (...) ON CONFLICT (ad_id, window) DO UPDATE SET count = EXCLUDED.count`. Since the write is idempotent and the Flink state determines the correct count, replays produce the same output.

**Interviewer**: "What about late-arriving clicks? A mobile user clicks at 10:05 but the event arrives at 10:15 because they were offline."

**You**: Flink uses watermarks to handle event-time processing. The watermark says "all events up to time T-allowed_lateness have arrived." We set `allowed_lateness` to, say, 5 minutes. Events within the lateness window trigger a window update — the window [10:05, 10:06) fires at 10:06, but if a late event arrives at 10:10 (within 5-min lateness), Flink re-fires the window with the updated count. Events arriving after the lateness window (e.g., at 10:15) go to a side output. The batch path picks them up: the nightly batch job re-aggregates ALL clicks from the raw Kafka log (which retains 7 days of data), producing correct final counts that include all late arrivals. The batch counts overwrite the real-time counts for billing purposes.

**Interviewer**: "How do you handle the case where the same click_id arrives in two different Kafka partitions?"

**You**: This shouldn't happen if we partition by ad_id — same ad's clicks go to the same partition. But what if the same click gets ingested through two different ingestion paths (e.g., mobile SDK and server-side pixel fire)? The `click_id` would be different since they're generated independently. This is the hardest dedup case — we need entity-level dedup, not just event-level. Solution: in the real-time path, Flink maintains a Bloom filter per ad_id to catch likely duplicates (user_id + ad_id + timestamp within 5-second window). False positive rate of 0.1% is acceptable for real-time. In the batch path, we do exact dedup: sort all clicks by (user_id, ad_id, timestamp), and if two clicks for the same user/ad are within 5 seconds, keep only the first. This catches the cross-path duplicates that the Bloom filter might miss.

**Interviewer**: "Size that Bloom filter for me."

**You**: We need to track click_ids seen in the current window. At 50K clicks/sec and 1-minute windows, that's 3M entries per window. For a 0.1% false positive rate, the optimal Bloom filter size is -n*ln(p) / (ln(2))^2 = -3M * ln(0.001) / 0.48 = ~43 MB per window. With 10 hash functions. This fits easily in Flink's state. We rotate the filter every window (clear and start fresh). For cross-window dedup (same click arriving in different windows), we keep the previous window's filter too — total 86 MB. Negligible memory.

### Deep Dive Path 2: Aggregation Pipeline Design

**Interviewer**: "Design the aggregation pipeline. How do you handle multi-dimensional aggregation efficiently?"

**You**: We use a two-level aggregation pattern. Level 1: per-partition aggregation in Flink. Each Flink task processes one Kafka partition (keyed by ad_id) and computes per-ad-per-minute counts. This is embarrassingly parallel — no shuffling needed. Level 2: dimensional rollup. After level 1 produces (ad_id, minute, count), a second Flink job reads these pre-aggregated results and computes rollups: by campaign (sum ad counts for all ads in campaign), by geo, by device type, by hour. These rollups are written to different materialized views in the output store.

**Interviewer**: "Why not aggregate all dimensions in a single Flink job?"

**You**: Combinatorial explosion. With 5 dimensions and various rollup combinations (ad_id alone, ad_id+geo, campaign_id+device+geo, etc.), a single job would need to maintain state for all possible combinations simultaneously. That's 2^5 - 1 = 31 possible rollup combinations per event. Instead, level 1 stores the finest granularity (per-ad-per-minute), and level 2 jobs compute specific rollups on demand. Some popular rollups (campaign per hour, geo per day) are pre-materialized. Ad-hoc rollups (campaign+device+geo for last week) are computed at query time from the fine-grained data using OLAP queries on ClickHouse.

**Interviewer**: "Walk me through the ClickHouse schema for this."

**You**: ClickHouse uses a MergeTree engine optimized for time-series aggregation:

```sql
CREATE TABLE click_aggregates (
    ad_id        UInt64,
    campaign_id  UInt64,
    geo          LowCardinality(String),
    device_type  LowCardinality(String),
    window_start DateTime,
    click_count  UInt64,
    impression_count UInt64,
    spend_micros UInt64
) ENGINE = SummingMergeTree()
ORDER BY (campaign_id, ad_id, geo, device_type, window_start)
PARTITION BY toYYYYMM(window_start)
TTL window_start + INTERVAL 2 YEAR;
```

SummingMergeTree automatically merges rows with the same ORDER BY key by summing the numeric columns. This means we can INSERT duplicate aggregation windows and ClickHouse handles the merge. The ORDER BY is chosen for common query patterns: filter by campaign, then ad, then geo — this gives columnar locality for range scans. Partition by month enables efficient data lifecycle (drop old partitions). At 500 GB/day raw, ClickHouse's columnar compression achieves ~10:1, so stored data is ~50 GB/day = ~36 TB for 2 years.

**Interviewer**: "How do you handle the reconciliation between real-time and batch?"

**You**: The batch job runs every hour, processing the last 2 hours of raw Kafka data (overlapping to catch late arrivals). It computes exact counts per (ad_id, minute) and writes to a `batch_click_counts` table in ClickHouse. A reconciliation job compares `realtime_click_counts` with `batch_click_counts` for the same windows. If the delta exceeds a threshold (e.g., >0.5%), it triggers an alert for investigation. For billing, the batch table is always the source of truth — the billing system reads from the batch table only after the reconciliation job confirms convergence. Realtime counts are used for dashboards, ad optimization, and budget pacing — where approximate counts with <1 min latency are more valuable than exact counts with 1-hour latency.

### Deep Dive Path 3: Scaling and Fault Tolerance

**Interviewer**: "What happens when a Flink taskmanager dies mid-aggregation?"

**You**: Flink's exactly-once relies on periodic checkpointing (default: every 1 minute). When a taskmanager dies, the Flink JobManager detects the failure via heartbeat timeout (30 seconds). It restores the failed task on a new taskmanager from the last successful checkpoint: (1) the Kafka consumer offset rolls back to the checkpoint's offset, (2) the aggregation state (in-memory hash maps or RocksDB) is restored from the checkpoint stored in HDFS/S3, (3) processing resumes from the checkpoint offset. Events between the checkpoint and the failure are replayed — but since the state is restored to the checkpoint, the replay produces the same results (deterministic processing). The total recovery time is ~1-2 minutes (30s detection + 30s state restoration + replay). During recovery, no output is produced — downstream systems see a gap, filled when the recovered task catches up.

**Interviewer**: "At 50K events/sec, how many Flink tasks do you need and how do you handle backpressure?"

**You**: Flink parallelism typically matches Kafka partitions. With 50K events/sec and 1K events/sec per task (conservative, including state operations), we need 50 tasks. Kafka would have 50 partitions. In practice, each Flink task handles more — ~5-10K events/sec for aggregation workloads — so 10-20 tasks suffice. For backpressure: if a downstream operator (e.g., the ClickHouse sink) is slow, Flink's credit-based flow control propagates backpressure upstream. The source operator (Kafka consumer) slows down its poll rate. Kafka buffers the unconsumed events (with retention, not data loss). This is why Kafka retention must be longer than the maximum expected backpressure duration — typically 7 days. If backpressure persists, we scale up Flink parallelism by adding partitions and tasks.

**Interviewer**: "How do you scale ClickHouse for query traffic? Dashboards might query the same data repeatedly."

**You**: Three strategies: (1) **Pre-aggregated materialized views**: ClickHouse creates materialized views that pre-aggregate on write. A dashboard querying "clicks per campaign per hour" reads a pre-aggregated table, not scanning raw minute-level data. (2) **Query caching**: ClickHouse has built-in query cache with 1-minute TTL. Dashboard refreshes every 30 seconds; 50% of queries hit cache. (3) **Read replicas**: ClickHouse cluster with 3 replicas per shard. Read queries are distributed across replicas. With 10 shards and 3 replicas = 30 nodes, each handling ~3K QPS for dashboard queries. For heavy ad-hoc analytics, we offload to a separate ClickHouse cluster backed by the same S3 data (cold storage) — this prevents analytics queries from impacting real-time dashboard performance.

---

## How Real Companies Built This

- **Meta (Facebook Ads)**: Uses Scuba for real-time ad analytics (in-memory columnar store) and Hive/Spark for batch reconciliation. Custom streaming pipeline on internal Kafka. [Scuba Paper — VLDB 2014](http://www.vldb.org/pvldb/vol6/p1057-wiener.pdf)
- **Google Ads**: MillWheel for streaming, then superseded by Cloud Dataflow (Apache Beam model). Streaming + batch unified programming model. [MillWheel Paper — VLDB 2013](https://research.google/pubs/pub41378/)
- **Twitter (Ads)**: Summingbird — unified batch + streaming on Storm + Hadoop. [Summingbird Paper](https://dl.acm.org/doi/10.14778/2733004.2733016)
- **LinkedIn**: Unified streaming processing on Samza, backed by Brooklin for Kafka transport. [LinkedIn Unified Streaming](https://engineering.linkedin.com/blog/2020/unified-streaming-and-batch)
- **Uber**: Apache Flink for real-time aggregation, Apache Hudi for incremental batch processing. [Uber Engineering — Real-Time Analytics](https://www.uber.com/blog/real-time-exactly-once-ad-event-processing/)
- **Cloudflare**: Custom click aggregation using Workers + Durable Objects for edge-side counting. [Cloudflare Workers Analytics](https://blog.cloudflare.com/explaining-cloudflares-abr-analytics/)

---

## The Complete Reference Design

### API Design

```
# Click ingestion (high throughput, fire-and-forget)
POST /v1/clicks
{
  "click_id": "uuid-v4",
  "ad_id": 12345,
  "campaign_id": 678,
  "user_id": "hashed_uid",
  "timestamp": "2024-01-15T10:05:32.123Z",
  "device_type": "mobile_ios",
  "geo": "US-CA",
  "ip": "203.0.113.50",
  "referrer": "https://example.com/feed"
}
# Response: 202 Accepted { "click_id": "uuid-v4" }

# Aggregation queries (dashboard)
GET /v1/reports/clicks?campaign_id=678&granularity=minute&start=2024-01-15T10:00:00Z&end=2024-01-15T11:00:00Z
# Response:
{
  "campaign_id": 678,
  "data": [
    {"window": "2024-01-15T10:00:00Z", "clicks": 14523, "impressions": 1452300, "ctr": 0.01},
    {"window": "2024-01-15T10:01:00Z", "clicks": 15102, "impressions": 1510200, "ctr": 0.01}
  ],
  "source": "realtime",  // or "batch" for reconciled data
  "freshness": "2024-01-15T10:02:05Z"
}

# Billing reconciliation (exact counts)
GET /v1/billing/clicks?campaign_id=678&date=2024-01-15
# Always reads from batch source-of-truth
```

### Database Schema

```sql
-- Raw click events (Kafka -> HDFS/S3 for batch, ClickHouse for OLAP)
CREATE TABLE raw_clicks (
    click_id      UUID,
    ad_id         UInt64,
    campaign_id   UInt64,
    user_id       String,
    event_time    DateTime64(3),
    ingest_time   DateTime64(3),
    device_type   LowCardinality(String),
    geo           LowCardinality(String),
    is_valid      UInt8 DEFAULT 1,       -- 0 = filtered by fraud detection
    fraud_reason  LowCardinality(String) DEFAULT ''
) ENGINE = MergeTree()
ORDER BY (ad_id, event_time)
PARTITION BY toYYYYMMDD(event_time)
TTL event_time + INTERVAL 90 DAY;

-- Pre-aggregated: per-ad per-minute (real-time path writes here)
CREATE TABLE click_agg_realtime (
    ad_id         UInt64,
    campaign_id   UInt64,
    geo           LowCardinality(String),
    device_type   LowCardinality(String),
    window_start  DateTime,
    click_count   UInt64,
    valid_click_count UInt64,
    impression_count  UInt64,
    spend_micros  UInt64
) ENGINE = SummingMergeTree()
ORDER BY (campaign_id, ad_id, window_start, geo, device_type)
PARTITION BY toYYYYMM(window_start);

-- Batch reconciled (source of truth for billing)
CREATE TABLE click_agg_batch (
    -- same schema as click_agg_realtime
    -- populated by hourly Spark batch job
) ENGINE = ReplacingMergeTree(batch_version)
ORDER BY (campaign_id, ad_id, window_start, geo, device_type)
PARTITION BY toYYYYMM(window_start);
```

### Key Algorithms — Flink Windowed Aggregation with Exactly-Once

```python
# Flink-style windowed aggregation (conceptual Python)
from dataclasses import dataclass
from collections import defaultdict
import time

@dataclass
class ClickEvent:
    click_id: str
    ad_id: int
    campaign_id: int
    event_time: float  # epoch seconds
    geo: str
    device_type: str

class WindowedAggregator:
    """Tumbling window aggregation with late data handling."""

    def __init__(self, window_size_sec: int = 60, allowed_lateness_sec: int = 300):
        self.window_size = window_size_sec
        self.allowed_lateness = allowed_lateness_sec
        self.windows: dict[tuple, dict] = defaultdict(lambda: {"count": 0, "ads": set()})
        self.watermark = 0.0
        self.bloom_filters: dict[int, set] = defaultdict(set)  # window -> seen click_ids

    def process(self, event: ClickEvent) -> list[dict]:
        """Process one click event. Returns emitted window results."""
        # Assign to window
        window_start = int(event.event_time // self.window_size) * self.window_size
        window_key = (event.ad_id, window_start)

        # Dedup via click_id
        if event.click_id in self.bloom_filters[window_start]:
            return []  # duplicate, skip
        self.bloom_filters[window_start].add(event.click_id)

        # Check lateness
        if window_start + self.window_size + self.allowed_lateness < self.watermark:
            return [{"type": "late_data", "event": event}]  # too late, side output

        # Aggregate
        self.windows[window_key]["count"] += 1

        # Advance watermark (simplified: use max event_time - slack)
        self.watermark = max(self.watermark, event.event_time - 10)

        # Emit closed windows
        results = []
        for key, data in list(self.windows.items()):
            ad_id, ws = key
            if ws + self.window_size <= self.watermark:
                results.append({
                    "ad_id": ad_id,
                    "window_start": ws,
                    "click_count": data["count"]
                })
                del self.windows[key]
                # Keep bloom filter for allowed_lateness period
        return results
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Kafka | 50K events/sec x 500B = 25 MB/s, 50 partitions | 5 brokers, 3x replication, 7-day retention = 15 TB |
| Flink (real-time) | 50K events/sec / 5K per task = 10 tasks | 10 taskmanagers, 4 CPU 8 GB each |
| Flink (state) | 10M ads x 100B per window state | ~1 GB managed state (RocksDB) |
| Spark (batch) | 500 GB/day hourly = ~20 GB/batch | 50-node Spark cluster, 30 min/run |
| ClickHouse | 500 GB/day raw, 50 GB/day compressed | 30 nodes, 3 replicas x 10 shards |
| Redis (real-time cache) | 10M ads x 100B = 1 GB | 3-node Redis cluster |
| Total daily storage | Raw: 500 GB + Agg: 50 GB = 550 GB/day | ~200 TB/year |

---

## Senior vs Staff vs Principal

| Aspect | Senior (E5/L5) | Staff (E6/L6) | Principal (L66+) |
|--------|----------------|----------------|-------------------|
| **Pipeline** | Correct Kafka -> Flink -> store pipeline with windowing | Designs exactly-once end-to-end with checkpoint math, handles late data | Designs Lambda with reconciliation, reasons about consistency guarantees across paths |
| **Scale** | Correct QPS and storage math | Designs multi-level aggregation to avoid combinatorial explosion, OLAP schema | Designs multi-region aggregation with global consistency, cross-datacenter Kafka mirroring |
| **Correctness** | Knows dedup is needed, uses click_id | Designs Bloom filter sizing, explains Flink checkpointing semantics | Designs fraud detection integration, billing reconciliation with audit trail |
| **Trade-offs** | Lambda vs Kappa at a high level | Quantifies latency/accuracy trade-off, explains when Kappa is sufficient | Designs adaptive pipelines that switch between modes based on load, cost optimization |

---

## Red Flags & Common Mistakes

1. **"Just count clicks in a database"** — No streaming, no windowing, no dedup. This fails at any real scale.
2. **Ignoring exactly-once** — "We use Kafka so it's exactly-once." Kafka alone doesn't guarantee end-to-end exactly-once. You need idempotent sinks.
3. **No late data handling** — Assuming all events arrive in order. Mobile networks cause minutes to hours of delay.
4. **No fraud detection mention** — 20-30% of ad clicks are invalid. Not filtering them is a billion-dollar mistake.
5. **Single aggregation level** — Trying to pre-compute all dimension combinations. The combinatorial explosion makes this impossible.
6. **No reconciliation story** — Real-time counts and batch counts WILL diverge. Without reconciliation, you don't know which to trust.
7. **Ignoring the money** — Ad clicks are financial transactions. The system needs auditability, exactly-once billing, and fraud controls. Treating it as a generic counting problem misses the business context.
