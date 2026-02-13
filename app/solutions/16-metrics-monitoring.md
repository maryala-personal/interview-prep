# Design a Metrics/Monitoring System (Datadog/Prometheus)

> **Companies**: Datadog, New Relic, Meta, Google, Amazon (CloudWatch), Uber, Netflix | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a system that ingests millions of time-series data points per second, stores them efficiently, and queries them at interactive speed? This probes your understanding of time-series databases, metric aggregation (pre-aggregation vs. query-time), push vs. pull collection models, and the fundamental trade-off between storage cost and query flexibility. If you've worked with Kubernetes metrics-server, Prometheus, or OpenTelemetry, draw on that experience heavily.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**Questions that show the interviewer you know what you're doing:**

- "What type of metrics? Counters (monotonically increasing), gauges (current value), histograms (distribution)? This affects storage and aggregation."
- "What's the ingestion rate? Millions of data points per second?"
- "What's the data retention policy? High-resolution for 7 days, downsampled for 1 year, aggregated for 5 years?"
- "What's the query latency SLA? Sub-second for recent data, seconds for historical?"
- "Push model (agents send to server) or pull model (server scrapes agents)? Or both?"
- "How many unique time series? Millions or billions? (Cardinality is the key cost driver.)"
- "Do we need alerting? What's the alerting latency — detect anomalies within seconds or minutes?"
- "Multi-tenant (SaaS like Datadog) or single-tenant (internal like Prometheus)?"

### Working Assumptions
| Parameter | Value | Derivation |
|-----------|-------|------------|
| Unique time series | 100M | 10K hosts x 200 metrics x 50 tag combinations |
| Data points ingested/sec | 10M | 100M series x 1 sample every 10 seconds (average) |
| Data point size | 16 bytes | 8-byte timestamp + 8-byte float64 value |
| Ingestion throughput | 160MB/s raw | 10M x 16 bytes |
| Raw retention | 15 days | Full 10-second resolution |
| Downsampled retention | 1 year at 1-minute resolution | 6x reduction |
| Aggregated retention | 5 years at 1-hour resolution | 360x reduction |
| Query latency (recent) | < 500ms for dashboard queries | Last 1 hour of data |
| Query latency (historical) | < 5 seconds | Last 30 days of data |
| Alerting latency | < 30 seconds | From metric emission to alert firing |
| Hosts/containers monitored | 100K | Large infrastructure |

### Reference Architecture: How Prometheus Works (Your K8s Experience)

Before designing, let's ground in what you already know. In Kubernetes:
- **metrics-server**: Scrapes kubelet's `/metrics/resource` endpoint every 15s, stores in memory (no persistence), serves `kubectl top` and HPA.
- **Prometheus**: Pull-based. Scrapes `/metrics` endpoints from pods (via ServiceMonitor CRDs). Stores in local TSDB. PromQL for queries. Not horizontally scalable by default.
- **Thanos/Cortex/Mimir**: Adds horizontal scaling to Prometheus — long-term storage in object storage (S3), query federation, global view across clusters.
- **OpenTelemetry (OTel)**: Vendor-neutral collection framework. OTel Collector receives metrics (push or pull), transforms, and exports to any backend (Prometheus, Datadog, CloudWatch).

Our design builds on these proven patterns.

---

## High-Level Design (Brief — 5 minutes)

```
Metric Sources (hosts, containers, applications)
    |
    v (push via OTel Collector / agents)
+-------------------+     +-------------------+
| Ingestion Gateway |---->| Kafka             |     Buffer & decouple
| (validates,       |     | (partitioned by   |     ingestion from
|  authenticates)   |     |  metric_name hash)|     storage
+-------------------+     +--------+----------+
                                   |
                    +--------------+--------------+
                    |              |              |
                    v              v              v
             +-----------+  +-----------+  +-----------+
             | Ingester 1|  | Ingester 2|  | Ingester N|
             | (in-memory|  |           |  |           |
             |  + WAL,   |  |           |  |           |
             |  writes to|  |           |  |           |
             |  TSDB)    |  |           |  |           |
             +-----------+  +-----------+  +-----------+
                    |              |              |
                    v              v              v
             +------------------------------------------+
             | Object Storage (S3)                      |
             | - Compressed TSDB blocks (2-hour chunks) |
             | - Downsampled blocks (1-min, 1-hour)     |
             +------------------------------------------+
                                   ^
                                   |
                    +-------------------+
                    | Query Engine      |     Reads from ingesters
                    | (PromQL / custom  |     (recent) + S3 (historical)
                    |  query language)  |
                    +-------------------+
                                   ^
                    +-------------------+
                    | Alerting Engine   |     Evaluates alert rules
                    | (periodic eval    |     every 15-30 seconds
                    |  of PromQL rules) |
                    +-------------------+
                                   |
                    +-------------------+
                    | Notification      |     PagerDuty, Slack, email
                    | Service           |
                    +-------------------+
```

**Why this architecture?**: This is essentially the Cortex/Mimir architecture (horizontally scalable Prometheus). The key insight: separate ingestion (write path) from querying (read path) so they scale independently. Ingesters buffer recent data in memory for fast queries; older data is flushed to cheap object storage (S3) in compressed blocks. This gives you both low-latency recent queries and cost-effective long-term storage.

---

## Core Concepts Deep Dive

### Concept 1: Time-Series Data Model & Storage

**What it is**: A time series is uniquely identified by a metric name + set of labels (tags): `http_request_duration_seconds{method="GET", endpoint="/api/users", status="200"}`. Each time series is a sequence of (timestamp, value) pairs. The data model is: `metric_name{label1="val1", label2="val2"} value timestamp`.

**How it applies here**: Storage is optimized for this pattern. Prometheus's TSDB stores time series in 2-hour blocks. Each block contains: (1) an index mapping label sets to series IDs, (2) compressed chunks of timestamp-value pairs per series. Chunks use gorilla compression (XOR encoding for timestamps, double-delta for values) achieving ~1.37 bytes per data point (vs. 16 raw bytes — 11.7x compression).

**The math/mechanics**: 100M time series x 1 sample every 10 seconds x 16 bytes raw = 160MB/s. With gorilla compression: 160MB/s / 11.7 = ~14MB/s stored. Over 15 days: 14MB/s x 86,400 x 15 = ~18TB. With downsampling (1-minute resolution for months): 18TB / 6 = 3TB for the next year. Total storage for 1+ year retention: ~20-25TB. Very manageable in S3 at ~$0.50/TB/month.

**Connection to K8s**: Prometheus in Kubernetes uses this exact TSDB format. When you configure a Prometheus PVC at 50GB, that covers about 3-5 days of full-resolution data for a medium cluster. That's why Thanos/Mimir exist — they offload to S3 for long-term.

**Common misconception**: Candidates propose using a general-purpose database (PostgreSQL, Cassandra) for time-series data. These are 10-100x less space-efficient and 10x slower for time-range queries. Purpose-built TSDB storage with columnar compression is essential at scale.

### Concept 2: Push vs. Pull Collection Model

**What it is**: Pull (Prometheus model): the monitoring server scrapes metric endpoints. Push (StatsD/Datadog model): agents on each host send metrics to a central collector. Hybrid (OpenTelemetry): agents can both scrape local targets and push to a remote collector.

**How it applies here**: Pull is great for long-lived services (Prometheus scrapes Kubernetes pods via service discovery). Push is necessary for: (1) short-lived jobs/serverless (they may die before being scraped), (2) massive scale (10M QPS ingest is hard to coordinate as pull), (3) environments where the monitoring server can't reach targets (firewalls, NAT).

For our design, we use push-based ingestion: agents/OTel Collectors on each host push metrics to the ingestion gateway. This scales better (no central coordinator scheduling scrapes), handles ephemeral workloads, and works across network boundaries.

**Connection to K8s**: In Kubernetes, Prometheus uses pull (scrape) because service discovery (via ServiceMonitor/PodMonitor CRDs) makes it easy to find targets. But even in K8s, the OTel Collector sidecar pattern is gaining traction — the collector scrapes the pod locally (pull) and pushes to a central backend (push). This hybrid model gives you the best of both.

**Common misconception**: Candidates declare "pull is better than push" (or vice versa) categorically. Neither is universally better. Pull has the advantage of "up" detection (if a scrape fails, you know the target is down). Push has the advantage of scalability and handling ephemeral workloads. Production systems support both.

### Concept 3: Cardinality — The Silent Killer

**What it is**: Cardinality is the number of unique time series. Each unique combination of metric name + label values creates a new series. `http_requests{method="GET", path="/api/users", user_id="12345"}` — if user_id has 10M distinct values, that single metric creates 10M time series. This is a "cardinality explosion."

**How it applies here**: High cardinality destroys: (1) memory (each active series needs ~3KB in the ingester's in-memory index), (2) storage (more series = more data), (3) query performance (querying across millions of series is slow). 100M series x 3KB = 300GB of index memory.

**The math/mechanics**: Safe cardinality per metric: < 10K. Dangerous: > 100K. Lethal: > 1M. A single high-cardinality label (user_id, request_id, trace_id) on a metric can create more series than the rest of the system combined. Mitigation: (1) validation at ingestion — reject metrics with labels that exceed cardinality limits, (2) relabeling (Prometheus relabel_configs) to drop or aggregate high-cardinality labels, (3) per-tenant cardinality limits in multi-tenant systems.

**Connection to K8s**: In Kubernetes, label explosion happens with pod-level metrics that include the pod name (which changes on every restart/deploy). Prometheus community best practice: use label `pod` for debugging but aggregate across pods for dashboards. kube-state-metrics is notorious for high cardinality — every Kubernetes object × every label on that object.

**Common misconception**: Candidates design the schema without discussing cardinality. In practice, cardinality management is the #1 operational challenge of monitoring systems. Datadog's pricing model is directly based on custom metrics count (a proxy for cardinality).

### Concept 4: Downsampling & Retention Tiers

**What it is**: Storing every 10-second sample forever is prohibitively expensive. Downsampling reduces resolution over time: raw (10s) for 15 days, 1-minute averages for 1 year, 1-hour averages for 5 years. Dashboards showing the last year don't need 10-second precision.

**How it applies here**: A background compaction process reads raw 2-hour blocks from S3, computes min/max/avg/sum/count for each 1-minute window, and writes a new downsampled block. Similarly, 1-minute blocks are further downsampled to 1-hour blocks. Queries automatically select the appropriate resolution based on the time range: querying last 1 hour uses raw data, last 30 days uses 1-minute, last year uses 1-hour.

**The math/mechanics**: Data reduction: 10-second raw: 6 samples/minute x 16 bytes = 96 bytes/min/series. 1-minute downsample: 5 aggregates x 8 bytes = 40 bytes/min/series but only 1 record per minute. Storage per series: raw 15 days = 6 x 86,400 x 15 x 16 = 124MB. 1-min for 1 year = 525,600 x 40 = 21MB. 1-hour for 5 years = 43,800 x 40 = 1.7MB. Total per series: ~147MB over 5 years. For 100M series: ~14.7PB. With compression (11.7x): ~1.25PB.

**Common misconception**: Candidates store everything at full resolution forever or delete old data. Downsampling is the standard approach — it preserves trends and anomaly visibility while reducing storage by orders of magnitude. Thanos does this automatically with its compactor component.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Ingestion Pipeline — Handling 10M Data Points/Second

**Interviewer**: "Walk me through how a metric from a container in Kubernetes ends up in your storage."

**You**: "The container exposes a `/metrics` endpoint in Prometheus exposition format. An OTel Collector sidecar (or DaemonSet agent) scrapes this endpoint every 15 seconds. The collector batches samples from all containers on the node — say 200 containers x 100 metrics = 20K samples per scrape. It serializes them in OTLP (OpenTelemetry Protocol — protobuf over gRPC) and pushes to our ingestion gateway.

The gateway validates the payload (schema, cardinality checks — reject if a label has > 10K distinct values), authenticates the tenant (API key), and rate-limits per tenant. Valid samples are published to Kafka, partitioned by hash(metric_name + sorted_labels). This ensures all samples for the same time series land on the same partition, which means the same ingester processes them — critical for efficient in-memory buffering.

An ingester consumes from Kafka partitions. It maintains an in-memory 'head block' — the last 2 hours of data as an in-memory TSDB. New samples are appended to the appropriate series in the head block AND written to a WAL (write-ahead log) on local SSD for durability. Every 2 hours, the head block is compacted into an immutable block, compressed (gorilla encoding), and uploaded to S3. The WAL is truncated."

**Interviewer**: "What if an ingester crashes? You have 2 hours of data in memory."

**You**: "The WAL provides durability. On crash, the ingester replays the WAL from the last S3 flush — recovers all data since the last 2-hour block upload. WAL replay for 2 hours of data at our throughput: 2h x 10M samples/s / 20 ingesters = 3.6B samples per ingester. At ~100 bytes per WAL record = 360GB. WAL replay at SSD read speed (~2GB/s) takes ~3 minutes. During this time, the ingester is unavailable for queries but Kafka messages queue up.

To reduce the blast radius, we also replicate ingested data: each sample is written to 3 ingesters (the Kafka consumer group is configured with 3x fan-out, or the ingestion gateway writes to 3 ingesters directly — this is the Cortex/Mimir replication model). If one ingester dies, the other 2 still serve queries. The failed ingester recovers from WAL and de-duplicates on the next S3 upload."

**Interviewer**: "10M samples/sec. How many ingesters do you need?"

**You**: "Each ingester handles active series in memory. With 100M series / 20 ingesters = 5M series per ingester. Memory: 5M x 3KB (index entry) + in-memory samples (2h x 5M / 10s x 16 bytes) = 15GB index + 57.6GB samples = ~73GB per ingester. With 128GB RAM instances, that's comfortable.

Throughput: 10M / 20 = 500K samples/sec per ingester. Each sample: hash lookup + append to chunk = ~1 microsecond. CPU: 500K x 1us = 0.5 core. The bottleneck is memory, not CPU. So 20 ingesters with 128GB RAM each handles our load with room for growth."

**Interviewer**: "How does Kafka help here vs. direct push to ingesters?"

**You**: "Kafka provides three things. First, decoupling — if ingesters are slow or restarting, data queues in Kafka instead of being dropped. At 160MB/s, Kafka can buffer hours of data if needed. Second, consistent routing — hash partitioning ensures the same series always goes to the same ingester, which prevents duplicate series and maintains memory efficiency. Third, replay — if we discover a bug in ingestion logic, we can replay from Kafka to reprocess. The trade-off is added latency (~5-50ms through Kafka) and operational complexity. For alerting where latency matters, we can have a parallel fast path that bypasses Kafka and pushes directly to the alerting engine."

### Deep Dive Path 2: Query Engine — Dashboard Queries at Interactive Speed

**Interviewer**: "A user opens a Grafana dashboard showing p99 latency across all API endpoints for the last hour. Walk me through the query."

**You**: "The dashboard panel generates a PromQL query: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service='api'}[5m])) by (le, endpoint))`.

The query engine parses this and plans execution. Step 1: identify the time range (last 1 hour at 15-second step). Step 2: determine which ingesters and storage blocks contain this data — last hour is in the ingesters' head blocks, not yet in S3. Step 3: fan out the inner selector `http_request_duration_seconds_bucket{service='api'}` to all ingesters in parallel. Each ingester scans its in-memory index for matching series (by label matchers), fetches the chunks for the time range, and returns raw samples.

Step 4: the query engine merges results from all ingesters, applies `rate()` (per-second increase), `sum() by (le, endpoint)` (aggregate buckets across instances), and `histogram_quantile(0.99)` (compute p99 from the histogram buckets). Step 5: return the result as a time series of p99 values, one per 15-second step, per endpoint."

**Interviewer**: "How fast is this? What if the query matches 10,000 time series?"

**You**: "For in-memory data (head block), the ingester's inverted index (label -> series IDs) makes the label matching step O(log N) per label value. Fetching 10K series x 1 hour at 10-second resolution = 10K x 360 points = 3.6M data points. At ~2 bytes per compressed point (gorilla encoding in memory), that's ~7MB of data. Transferring 7MB from 20 ingesters in parallel (350KB each) over gRPC takes ~5ms. The query engine's aggregation (rate, sum, quantile) on 3.6M points takes ~50ms. Total: ~100-200ms. Interactive speed.

For historical queries (last 30 days), the query engine reads from S3 instead. This is slower — S3 read latency is ~50-100ms per GET. But blocks are indexed, so we read only the relevant chunks. With a caching layer (Memcached for block metadata, local SSD for frequently accessed blocks), historical queries complete in 1-3 seconds for a 30-day range."

**Interviewer**: "What about queries that scan billions of data points? Like 'sum of all HTTP requests across all services for the last year?'"

**You**: "This is where downsampled data is critical. A 1-year query would scan 100M series x 525,600 minutes = 52.5 trillion data points at raw resolution — that's impossible in interactive time. Instead, the query engine automatically selects the 1-hour downsampled data: 100M series x 8,760 hours = 876B points. Still huge. The key optimization: pre-aggregation.

For queries that `sum()` across a high-cardinality dimension, we pre-compute the aggregation during ingestion. A 'recording rule' (Prometheus concept): `sum(http_requests_total) by (service)` is evaluated every minute and stored as a new, lower-cardinality metric. This reduces 100K series to 50 services — query time drops from minutes to milliseconds.

This is the fundamental trade-off: pre-aggregation reduces query latency but limits query flexibility (you can only aggregate in pre-defined dimensions). Raw data gives maximum flexibility but is expensive to query. Production systems use both: pre-aggregated metrics for dashboards, raw data for ad-hoc debugging."

### Deep Dive Path 3: Alerting Engine

**Interviewer**: "How does alerting work? Detect that p99 latency exceeds 500ms and notify the on-call."

**You**: "The alerting engine evaluates alert rules periodically (every 15-30 seconds). Each rule is a PromQL expression: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)) > 0.5`.

The engine: (1) evaluates the PromQL expression against the latest data (from ingesters, not S3 — alerting needs the freshest data), (2) compares the result to the threshold, (3) if the condition is true, starts a timer. (4) If the condition remains true for the `for` duration (e.g., 5 minutes — to avoid alerting on transient spikes), the alert transitions from 'pending' to 'firing'. (5) The firing alert is sent to the notification service (Alertmanager in Prometheus), which handles deduplication, grouping, routing (p99 latency -> team-api Slack channel + PagerDuty), and silencing.

End-to-end latency: metric emission (scrape every 15s) + Kafka propagation (~10ms) + ingester buffer (~0s, it's in memory) + alerting eval interval (15s) + for duration (5 min configurable) = ~5 minutes for a stable alert. The for duration is the dominant factor — it's intentionally high to prevent flapping."

**Interviewer**: "What about anomaly detection? Not just static thresholds."

**You**: "Beyond static thresholds, two approaches. First, dynamic thresholds based on historical patterns: compute a rolling 7-day average with standard deviation bands. Alert when the current value is > 3 sigma from the expected value. This catches 'traffic is 50% lower than normal on Tuesday at 3pm' without needing to set a specific number.

Second, rate-of-change detection: alert when `deriv(metric[1h])` exceeds a threshold — catches gradual degradation that hasn't hit an absolute threshold yet (e.g., memory leak growing 100MB/hour).

Both of these are implemented as PromQL-compatible functions in the query engine and evaluated by the same alerting loop. The challenge is false positives — anomaly detection at scale requires significant tuning per metric. This is where ML-based approaches (like Datadog's anomaly detection) add value, but they're complex to build and operate."

**Interviewer**: "How do you ensure the alerting engine itself is reliable? If monitoring is down, who monitors the monitoring?"

**You**: "Classic 'who watches the watchmen' problem. Three strategies. First, the alerting engine runs as a replicated, highly available service (3+ replicas). Each replica evaluates all alert rules independently. Alertmanager deduplicates duplicate alerts. Even if one replica fails, the other two still fire alerts.

Second, a 'dead man's switch' (also called 'watchdog'): a special alert that always fires. The notification service expects to receive this alert every minute. If it doesn't, something is wrong with the alerting pipeline. The notification service for the dead man's switch runs independently (separate infrastructure — different cloud region, different team's pager).

Third, synthetic monitoring: external probes that hit the monitoring system's own endpoints (health checks, test metric ingestion, test query execution). Run from a completely independent infrastructure. This is how Datadog monitors Datadog."

---

## How Real Companies Built This

- **Prometheus + Thanos/Mimir (CNCF ecosystem)**: Prometheus is the de facto standard for Kubernetes monitoring. Its TSDB is highly optimized for time-series workloads. Thanos and Grafana Mimir extend it with horizontal scaling and long-term storage in object storage. Mimir uses consistent hashing to distribute series across ingesters. Docs: https://prometheus.io/docs/ and https://grafana.com/docs/mimir/latest/

- **Datadog**: Multi-tenant SaaS monitoring at massive scale. Key innovations: per-customer cardinality management, OpenTelemetry-native ingestion, ML-based anomaly detection, and a custom query engine optimized for aggregation across billions of points. Blog: https://www.datadoghq.com/blog/engineering/

- **Meta (Gorilla / ODS)**: Built Gorilla, the TSDB that invented gorilla compression (XOR encoding for timestamps, double-delta for values). Paper: https://www.vldb.org/pvldb/vol8/p1816-teller.pdf. Achieved 12x compression vs. raw storage, enabling in-memory storage of 26 hours of data. ODS (Operational Data Store) is their production monitoring system serving all of Meta's infrastructure.

- **Netflix (Atlas)**: Custom time-series database designed for operational insights. Uses in-memory storage for recent data with pre-aggregation. Key design principle: queries should be pre-planned (recording rules), not ad-hoc, to bound query cost. Blog: https://netflixtechblog.com/

- **Key lesson**: The monitoring problem is 80% a storage/compression problem and 20% a query problem. Purpose-built TSDB storage (gorilla compression, columnar format, downsampling) is essential. Generic databases fail at this scale. OpenTelemetry is becoming the universal collection standard — design the ingestion pipeline to be OTel-native.

---

## The Complete Reference Design

### API Design
```
# Ingest metrics (OTLP-compatible)
POST /v1/metrics
Content-Type: application/x-protobuf  # or application/json
Request (JSON representation):
{
  "resource_metrics": [{
    "resource": {"attributes": {"host": "web-01", "k8s.pod": "api-abc"}},
    "scope_metrics": [{
      "metrics": [{
        "name": "http_request_duration_seconds",
        "histogram": {
          "data_points": [{
            "time_unix_nano": 1739347200000000000,
            "sum": 125.5,
            "count": 1000,
            "bucket_counts": [10, 50, 200, 500, 200, 40],
            "explicit_bounds": [0.01, 0.05, 0.1, 0.5, 1.0],
            "attributes": {"method": "GET", "endpoint": "/api/users"}
          }]
        }
      }]
    }]
  }]
}
Response 200: { "accepted": true }

# Query metrics (PromQL-compatible)
GET /v1/query_range?query=rate(http_requests_total{service="api"}[5m])&start=2026-02-12T09:00:00Z&end=2026-02-12T10:00:00Z&step=15s
Response 200: {
  "status": "success",
  "data": {
    "resultType": "matrix",
    "result": [
      {
        "metric": {"service": "api", "method": "GET"},
        "values": [[1739347200, "125.5"], [1739347215, "130.2"]]
      }
    ]
  }
}

# Create alert rule
POST /v1/alerts/rules
Request: {
  "name": "HighP99Latency",
  "expression": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)) > 0.5",
  "for": "5m",
  "labels": {"severity": "critical", "team": "api"},
  "annotations": {"summary": "P99 latency > 500ms for {{ $labels.service }}"}
}
```

### Storage Architecture
```
Time-Series Database Block Format (per 2-hour block):
+----------------------------------------------------------+
| Index                                                     |
|  - Postings: label_name=label_value -> [series_id, ...]  |
|  - Series: series_id -> {labels, chunk_refs}              |
+----------------------------------------------------------+
| Chunks                                                    |
|  - Series 1: [timestamp_delta, value_xor, ...]           |
|  - Series 2: [timestamp_delta, value_xor, ...]           |
|    (Gorilla-compressed: ~1.37 bytes per data point)       |
+----------------------------------------------------------+
| Tombstones (deleted series/time ranges)                   |
+----------------------------------------------------------+
| Meta.json (block ID, time range, series count, size)      |
+----------------------------------------------------------+

Block lifecycle:
  Head (in-memory, 0-2h) -> Persistent block (SSD) -> S3 upload
  -> Compaction (merge small blocks) -> Downsampling (1min, 1hr)
```

### Key Algorithms
```python
import struct
import math
from typing import List, Tuple

# --- Gorilla Compression (Facebook's time-series compression) ---
# Reference: "Gorilla: A Fast, Scalable, In-Memory Time Series Database"
# https://www.vldb.org/pvldb/vol8/p1816-teller.pdf

class GorillaEncoder:
    """
    Encodes (timestamp, float64_value) pairs with high compression.
    Timestamps: delta-of-delta encoding.
    Values: XOR encoding (consecutive values are often similar).
    Achieves ~1.37 bytes per data point vs. 16 bytes raw.
    """
    def __init__(self):
        self.bits = bytearray()
        self.bit_pos = 0
        self.prev_ts = 0
        self.prev_delta = 0
        self.prev_value_bits = 0
        self.first = True

    def encode_sample(self, timestamp: int, value: float):
        if self.first:
            # First sample: store raw
            self._write_bits(timestamp, 64)
            self._write_bits(struct.unpack('>Q', struct.pack('>d', value))[0], 64)
            self.prev_ts = timestamp
            self.prev_value_bits = struct.unpack('>Q', struct.pack('>d', value))[0]
            self.first = False
            return

        # Timestamp: delta-of-delta
        delta = timestamp - self.prev_ts
        dod = delta - self.prev_delta  # delta-of-delta
        if dod == 0:
            self._write_bit(0)              # 1 bit: '0'
        elif -63 <= dod <= 64:
            self._write_bits(0b10, 2)       # 2 bits: '10'
            self._write_bits(dod + 63, 7)   # 7 bits: value
        elif -255 <= dod <= 256:
            self._write_bits(0b110, 3)
            self._write_bits(dod + 255, 9)
        elif -2047 <= dod <= 2048:
            self._write_bits(0b1110, 4)
            self._write_bits(dod + 2047, 12)
        else:
            self._write_bits(0b1111, 4)
            self._write_bits(dod, 32)       # full 32 bits

        self.prev_delta = delta
        self.prev_ts = timestamp

        # Value: XOR with previous
        value_bits = struct.unpack('>Q', struct.pack('>d', value))[0]
        xor = self.prev_value_bits ^ value_bits
        if xor == 0:
            self._write_bit(0)              # identical: 1 bit
        else:
            self._write_bit(1)
            leading = self._count_leading_zeros(xor)
            trailing = self._count_trailing_zeros(xor)
            significant = 64 - leading - trailing
            self._write_bits(leading, 5)
            self._write_bits(significant, 6)
            self._write_bits(xor >> trailing, significant)

        self.prev_value_bits = value_bits

    def _write_bit(self, bit):
        if self.bit_pos % 8 == 0:
            self.bits.append(0)
        if bit:
            self.bits[-1] |= (1 << (7 - (self.bit_pos % 8)))
        self.bit_pos += 1

    def _write_bits(self, value, num_bits):
        for i in range(num_bits - 1, -1, -1):
            self._write_bit((value >> i) & 1)

    @staticmethod
    def _count_leading_zeros(value):
        if value == 0:
            return 64
        count = 0
        for i in range(63, -1, -1):
            if value & (1 << i):
                break
            count += 1
        return count

    @staticmethod
    def _count_trailing_zeros(value):
        if value == 0:
            return 64
        count = 0
        for i in range(64):
            if value & (1 << i):
                break
            count += 1
        return count


# --- Inverted Index for Label Matching ---
class InvertedIndex:
    """
    Maps label key-value pairs to series IDs.
    Used for fast label matching in queries.
    """
    def __init__(self):
        self.postings = {}  # (label_name, label_value) -> set(series_id)
        self.series = {}    # series_id -> {label_name: label_value}

    def add_series(self, series_id: int, labels: dict):
        self.series[series_id] = labels
        for k, v in labels.items():
            key = (k, v)
            if key not in self.postings:
                self.postings[key] = set()
            self.postings[key].add(series_id)

    def match(self, matchers: List[Tuple[str, str]]) -> set:
        """Find series matching all label matchers (AND semantics)."""
        result = None
        for label_name, label_value in matchers:
            series_ids = self.postings.get((label_name, label_value), set())
            if result is None:
                result = series_ids.copy()
            else:
                result &= series_ids  # intersection
        return result or set()


# --- Downsampling ---
def downsample_block(raw_samples: List[Tuple[int, float]],
                     resolution_seconds: int) -> List[dict]:
    """
    Downsample raw (timestamp, value) pairs to lower resolution.
    For each window, compute min, max, sum, count.
    """
    if not raw_samples:
        return []

    buckets = {}
    for ts, val in raw_samples:
        bucket_ts = (ts // resolution_seconds) * resolution_seconds
        if bucket_ts not in buckets:
            buckets[bucket_ts] = {
                "timestamp": bucket_ts,
                "min": val, "max": val,
                "sum": val, "count": 1
            }
        else:
            b = buckets[bucket_ts]
            b["min"] = min(b["min"], val)
            b["max"] = max(b["max"], val)
            b["sum"] += val
            b["count"] += 1

    return sorted(buckets.values(), key=lambda x: x["timestamp"])
```

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Ingesters | 100M series / 5M per ingester | 20 ingesters (128GB RAM each) |
| Ingester memory | 5M series x 3KB index + 2h samples | ~73GB per ingester |
| Kafka throughput | 10M samples/sec x 100 bytes | ~1GB/s (10-20 partitions) |
| S3 storage (15 days raw) | 14MB/s compressed x 86,400 x 15 | ~18TB |
| S3 storage (1 year downsampled) | ~3TB | At 1-min resolution |
| Query engine instances | 50K concurrent dashboard queries | 10-20 query nodes |
| Alerting engine | 10K alert rules x 15s eval interval | 3 replicas (HA) |
| Block cache (Memcached) | Hot blocks for query acceleration | 500GB across cluster |
| WAL disk per ingester | 2h at 14MB/s / 20 ingesters | ~50GB SSD per ingester |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Understands time-series model, designs basic ingest + store + query pipeline, mentions Prometheus | Describes push/pull collection, TSDB storage, basic alerting with thresholds |
| Staff | Designs for horizontal scale (Cortex/Mimir-style), explains gorilla compression, handles cardinality management, designs alerting with HA, draws K8s/Prometheus parallels | Separates ingester/querier/compactor, implements downsampling tiers, designs cardinality limits with per-tenant quotas, explains inverted index for label matching |
| Principal | Thinks about multi-tenant isolation (noisy neighbor), designs for cost optimization (storage tiers, pre-aggregation vs. raw), considers the monitoring system's own observability, reasons about OpenTelemetry convergence (metrics + traces + logs) | Proposes unified observability platform (metrics + traces + logs correlated), designs tenant-level cost attribution, considers how to migrate from Prometheus to a scalable backend without breaking existing dashboards/alerts |

---

## Red Flags & Common Mistakes
- **Using a general-purpose database for TSDB**: PostgreSQL or Cassandra at this ingestion rate and query pattern will be 10-100x slower and more expensive. Purpose-built TSDB storage is essential.
- **Ignoring cardinality**: Not discussing cardinality management is a major red flag. This is the #1 operational problem in production monitoring systems.
- **Pull-only or push-only without justification**: Both have trade-offs. A good answer discusses when to use each and ideally supports both.
- **No downsampling strategy**: Storing full-resolution data forever is not economically viable. Downsampling is table stakes.
- **Alert on raw metrics without for duration**: Alerting on every transient spike causes alert fatigue. The `for` duration and hysteresis are critical.
- **Forgetting about the alerting engine's own HA**: If the monitoring system goes down, who alerts on that? Dead man's switch is the expected answer.
- **Not mentioning OpenTelemetry**: OTel is the industry standard for metric collection. Mentioning it shows awareness of the current ecosystem.
