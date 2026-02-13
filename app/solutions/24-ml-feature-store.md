# Design an ML Feature Store / Training Pipeline

> **Companies**: Meta, Google, Uber, Airbnb, Netflix, LinkedIn, Stripe, DoorDash | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Understanding of training-serving skew and how to prevent it, online vs offline feature serving with different latency/throughput profiles, point-in-time correctness for training data, how feature computation pipelines scale, integration with Kubernetes-based ML infrastructure

---

## The First 5 Minutes — Scoping & Technical Clarifications

1. **Online vs offline serving?** Online: p99 <10ms feature lookup during inference. Offline: batch retrieval for training data generation. The architecture differs fundamentally.
2. **Feature freshness requirements?** Real-time features (updated per event, e.g., "clicks in last 5 minutes") vs batch features (updated hourly/daily, e.g., "user's average spend last 30 days").
3. **Point-in-time correctness?** Training data must use features as they were at prediction time, not current values. Without this, you get data leakage.
4. **Feature sharing and discovery?** How many teams produce features? How do consumers find and reuse features? This drives the registry/catalog design.
5. **Scale — features and entities?** How many unique features, how many entities (users, items), what's the feature vector size?
6. **Compute environment?** Where do feature transformations run — Spark, Flink, Ray, or Kubernetes-based (KubeFlow)?
7. **Model serving integration?** Are features fetched by the model server at inference time, or pre-computed and embedded in the request?
8. **Data sources?** Event streams (Kafka), data warehouse (BigQuery, Snowflake), transactional databases (PostgreSQL)?

### Working Assumptions

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Total features | 10,000 | Across 200 ML models |
| Unique entities | 1 billion (users) + 100 million (items) | E-commerce/social platform |
| Online serving QPS | 500,000 | 500K inference requests/sec needing features |
| Online p99 latency | <5 ms | Feature retrieval must be faster than model inference |
| Feature vector size | 500 features avg per model x 8 bytes = 4 KB | Typical dense feature set |
| Online store size | 1.1B entities x 4 KB = 4.4 TB | All entity features |
| Offline store size | 4.4 TB x 365 days historical | ~1.6 PB for point-in-time |
| Feature freshness | 1 min for real-time, 1 hour for batch | Different SLAs by feature type |
| Training data generation | 1 TB/day | Training set for daily model retraining |

**Throughput math**: 500K QPS x 4 KB per request = 2 GB/s read throughput from online store. Redis cluster with 10 shards, each handling 50K QPS at 200 MB/s — feasible.

---

## High-Level Design

```
    ┌───────────────────────────────────────────────────────────┐
    │                   FEATURE REGISTRY                        │
    │  (schema, owners, lineage, discovery, versioning)        │
    └──────────────────────┬────────────────────────────────────┘
                           │
    ┌──────────────────────┼────────────────────────────────────┐
    │                      │                                    │
    │   DATA SOURCES       │     FEATURE COMPUTATION            │
    │                      │                                    │
    │  ┌──────────┐  ┌─────▼──────┐  ┌──────────────────────┐  │
    │  │ Kafka    │─►│ Stream     │  │ Batch Engine         │  │
    │  │ (events) │  │ Engine     │  │ (Spark/KubeFlow)     │  │
    │  └──────────┘  │(Flink/     │  │ - Daily features     │  │
    │  ┌──────────┐  │ Spark SS)  │  │ - Historical backfill│  │
    │  │ Warehouse│  │ - Real-time│  └──────────┬───────────┘  │
    │  │ (BQ/SF)  │  │   features │             │              │
    │  └──────────┘  └─────┬──────┘             │              │
    │                      │                    │              │
    └──────────────────────┼────────────────────┼──────────────┘
                           │                    │
              ┌────────────┼────────────────────┼────────┐
              │            ▼                    ▼        │
              │  ┌──────────────┐    ┌──────────────┐   │
              │  │ Online Store │    │ Offline Store │   │
              │  │ (Redis/      │    │ (S3/Parquet  │   │
              │  │  DynamoDB)   │    │  + Hive/     │   │
              │  │ Low-latency  │    │  Delta Lake) │   │
              │  │ key-value    │    │ Historical   │   │
              │  └──────┬───────┘    └──────┬───────┘   │
              │         │                   │           │
              └─────────┼───────────────────┼───────────┘
                        │                   │
              ┌─────────▼───────┐  ┌────────▼─────────────┐
              │ Model Serving   │  │ Training Pipeline    │
              │ (online         │  │ (offline             │
              │  inference)     │  │  point-in-time join) │
              └─────────────────┘  └──────────────────────┘
```

**Why this architecture?** The dual-store pattern (online + offline) is the fundamental insight. Online serving needs sub-5ms key-value lookups — Redis or DynamoDB. Training needs historical features with point-in-time correctness — time-partitioned Parquet files on S3. The feature registry is the glue: it defines each feature once, and the system materializes it into both stores. This prevents training-serving skew: the same feature definition produces both the training data and the serving-time values.

---

## Core Concepts Deep Dive

### Concept 1: Training-Serving Skew — The Silent Model Killer

**What it is**: When features used during training differ from features used during inference. The model learns patterns on training features but gets different feature distributions at serving time. This silently degrades model accuracy.

**How it applies**: Common causes: (1) **Code skew**: Training features computed in Python/Spark, serving features computed in Java/C++. Subtle differences in NULL handling, string encoding, or numerical precision. (2) **Data skew**: Training uses features from the data warehouse (batch-updated daily), but serving computes features in real-time (up-to-the-second). The distributions differ. (3) **Time-travel violation**: Training data uses future information. For example, using "user's total purchases this month" computed at month-end for a training example from mid-month.

**The math**: Studies at Uber and Netflix show that training-serving skew accounts for 60%+ of production ML bugs. A 1% feature discrepancy can reduce model AUC by 0.5-2%, which at scale translates to millions in lost revenue.

**Common misconception**: "Just use the same code for training and serving." This helps with code skew but doesn't solve data/time skew. The feature store solves all three by: (1) defining features once in the registry, (2) materializing from a single transformation pipeline to both stores, (3) enforcing point-in-time correctness during training data generation.

### Concept 2: Point-in-Time Joins — Preventing Data Leakage

**What it is**: When generating training data, each training example has a timestamp (when the prediction would have been made). Features must be joined as-of that timestamp — using only information available at that point in time.

**How it applies**: Example: predicting "will user X click ad Y at time T?" Features needed: "user X's click count in the last 7 days" as of time T. If we use the current click count (or the click count at the end of day T), we're leaking future information into the training example. The point-in-time join retrieves the feature value that was valid at time T.

**The math**: For a training dataset with 1B examples and 500 features each, the point-in-time join must look up 500B feature values across time-partitioned storage. Naive implementation (one lookup per feature per example) is impossibly slow. Optimized approach: sort training examples by entity_id and timestamp, then scan the feature history table (also sorted by entity_id and timestamp) using a merge join. This is O(N + M) where N is training examples and M is feature history — much better than O(N * M) for nested loops.

**Common misconception**: "Just use the latest feature values for training." This creates a leakage problem AND a freshness problem. During training, you'd use today's feature values for historical events — the model learns patterns that don't exist in the real-time serving path.

### Concept 3: Online Store Architecture — Sub-5ms Feature Retrieval

**What it is**: The online store must serve feature vectors at 500K QPS with p99 <5ms. This requires: (1) all data in memory or NVMe, (2) efficient serialization, (3) batch get support (one request fetches all features for an entity).

**How it applies**: Redis cluster with hash-based sharding by entity_id. Each entity's feature vector is stored as a single Redis hash: `HGETALL user:12345` returns all features for user 12345 in one network round-trip. For multi-entity lookups (e.g., features for user AND item), the model server issues parallel requests. Feature vectors are serialized as Protocol Buffers for compact encoding and schema evolution.

**The math**: 1.1B entities x 4 KB = 4.4 TB. Redis uses ~2x memory overhead (hash table + string encoding), so 8.8 TB. With 10 shards, each shard holds 880 GB. r6g.16xlarge instances (512 GB RAM) can hold this with a shard split to 20 shards (440 GB each). At 500K QPS across 20 shards = 25K QPS per shard — well within Redis's ~100K QPS capacity.

**Common misconception**: "Use a database for online serving." Even with SSDs, a PostgreSQL lookup takes 1-5ms (B-tree traversal + disk I/O). At 500K QPS, that's unsustainable. Redis/Memcached with all data in RAM gives <1ms p99. DynamoDB is an alternative (3-5ms p99, no operational burden), but at 500K QPS the cost is significant (~$300K/year for on-demand, less with provisioned capacity).

### Concept 4: Feature Computation on Kubernetes — KubeFlow, Ray, and Feast

**What it is**: Feature computation pipelines run as batch jobs (Spark on K8s) or streaming jobs (Flink on K8s). KubeFlow Pipelines orchestrates the DAG. Ray provides distributed compute for Python-heavy feature engineering. Feast is the most popular open-source feature store.

**How it applies**: A typical feature computation pipeline on EKS: (1) KubeFlow Pipeline defines the DAG: read raw data from S3 -> compute features in Spark/Ray -> write to offline store (S3 Parquet) and online store (Redis). (2) Spark runs on Kubernetes using the Spark Operator — each feature computation is a SparkApplication CRD. (3) Ray Cluster on K8s handles Python feature transformations that don't need Spark's full MapReduce model (e.g., embedding computations, complex aggregations on single-entity data). (4) Feast manages the feature registry and orchestrates materialization from offline to online store.

**The math**: Daily feature computation: 1 TB of raw data -> 100 GB of computed features (10:1 compression from aggregation). Spark on K8s with 50 executors (4 CPU, 16 GB each) processes 1 TB in ~15 minutes. Materialization from S3 to Redis (100 GB to 20 Redis shards) at 500 MB/s per shard = ~10 seconds per shard.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Online Serving Under Latency Constraints

**Interviewer**: "A recommendation model needs 500 features for the user and 200 features for each of 100 candidate items. Walk me through how you serve this at p99 <10ms."

**You**: Total features needed: 500 (user) + 200 x 100 (items) = 20,500 features. At 8 bytes each, that's 164 KB per inference request. The request flow: (1) Model server receives inference request with user_id and 100 candidate item_ids. (2) Issue parallel Redis requests: one `HGETALL user:{user_id}` for user features, and one `HMGET item:{item_id} feat1 feat2 ... feat200` per item. With Redis pipelining, we batch all 101 requests into a single network round-trip per shard. If items are distributed across 20 shards, we make ~20 parallel network calls. (3) Each call takes ~1ms (network RTT) + ~0.1ms (Redis processing). Total: ~1.5ms for feature retrieval. (4) Model inference in TensorFlow/PyTorch: ~5ms. Total: <10ms.

**Interviewer**: "What if some features are real-time (computed from the last 5 minutes of events) and others are batch (computed daily)?"

**You**: Two-tier online store. Batch features are materialized to Redis by the nightly pipeline — they change once per day. Real-time features are computed by a Flink streaming job and written to a separate Redis instance (or a separate key space in the same cluster). The model server fetches from both and merges. The real-time features have higher write QPS (updating on every event) but lower read volume (only for features that need freshness). Example: "user's click count in last 5 minutes" — Flink maintains a sliding window counter per user, writing to Redis every second. At serving time, the model server reads this counter alongside the batch features.

The merge logic: the feature registry defines each feature's "source" (batch or streaming). The model server's feature retrieval SDK knows which store to query for each feature. If the streaming store is unavailable, we fall back to the batch value (stale but available — graceful degradation). This is configurable per feature: some features (e.g., user's account status) MUST be fresh and have no fallback.

**Interviewer**: "How do you handle feature freshness monitoring? How do you know if the streaming pipeline is lagging?"

**You**: Three monitoring layers: (1) **Pipeline lag**: Flink exposes the watermark lag metric — the difference between the current event time watermark and wall-clock time. If lag exceeds 1 minute, alert. (2) **Online store freshness**: Each feature write includes a `computed_at` timestamp. A monitoring job periodically reads features and checks `now() - computed_at`. If any feature is staler than its SLA (e.g., 5 minutes for real-time features), alert. (3) **Feature distribution drift**: Compare the distribution of features served online vs features in the latest training dataset. If the KL divergence exceeds a threshold, alert — this indicates either a pipeline bug or a genuine distribution shift that may require model retraining.

**Interviewer**: "What about cold-start entities? A new user has no features."

**You**: Default values defined per feature in the registry. When the online store returns no data for a user (cache miss), the SDK returns the default feature vector. Defaults can be: (1) Global mean (for numeric features), (2) Zero vector (for embeddings), (3) "unknown" category (for categorical features). The model is trained with these defaults for a fraction of examples (data augmentation with missing features) so it gracefully handles cold-start. Additionally, we compute "session features" in real-time from the user's current session — even a new user generates clickstream data within minutes, providing some signal.

### Deep Dive Path 2: Point-in-Time Training Data Generation

**Interviewer**: "Walk me through generating training data with point-in-time correctness for a click prediction model."

**You**: The training data generation pipeline takes: (1) A label table: `(user_id, item_id, timestamp, label)` — e.g., "user 123 saw item 456 at 10:05 AM and clicked/didn't click." (2) Feature tables: for each feature, a time-series of values per entity: `(entity_id, feature_name, value, valid_from, valid_to)`. The join: for each training example `(user_id, timestamp)`, retrieve the user's feature values where `valid_from <= timestamp < valid_to`. This is the "as-of" join.

Implementation in Spark:
```python
# Labels: (user_id, item_id, timestamp, label)
# User features: (user_id, feature_name, value, valid_from, valid_to)

labels_df = spark.read.parquet("s3://training/labels/")
user_features_df = spark.read.parquet("s3://features/user_features/")

# Point-in-time join
training_df = labels_df.join(
    user_features_df,
    on=(labels_df.user_id == user_features_df.user_id) &
       (user_features_df.valid_from <= labels_df.timestamp) &
       (labels_df.timestamp < user_features_df.valid_to),
    how="left"
)
```

The challenge: this range join is expensive. With 1B labels and 100B feature records, a naive join is O(N*M). Optimization: partition both tables by entity_id, sort by timestamp within each partition, and use a merge join. Spark's bucketed join with sort-merge does this efficiently.

**Interviewer**: "How do you handle features with different update frequencies? User profile updates daily, click features update per-minute."

**You**: The offline store has per-feature time-partitioning. Daily features (user profile, aggregate statistics) have one record per day: `valid_from = 2024-01-15T00:00:00, valid_to = 2024-01-16T00:00:00`. Real-time features (click counts, session metrics) have fine-grained records: one per minute or per event. During the point-in-time join, each feature is joined independently based on its own `valid_from/valid_to` range. Features with different granularities naturally compose — the join selects the correct version for each feature at the label's timestamp.

For storage efficiency: daily features = 1 record/entity/day. 1B users x 365 days x 500 features x 8 bytes = ~1.4 PB/year. Real-time features at 1-minute granularity = 1440 records/entity/day — 1000x more data. We don't store all real-time features at 1-minute granularity for 365 days. Instead: raw event data retained for 7 days (for recent training), then downsampled to hourly for 30 days, then daily for 365 days. This "tiered retention" keeps storage manageable: ~50 TB for real-time features at the yearly level.

**Interviewer**: "How does Feast handle this? What are its limitations?"

**You**: Feast defines features as "Feature Views" — a group of related features from the same data source with the same entity key and timestamp column. The offline store interface supports point-in-time joins via `get_historical_features()`, which takes a label DataFrame and returns features joined as-of each label's timestamp. Feast's implementation delegates to the offline store engine (Spark, BigQuery, Snowflake) for the actual join execution.

Limitations: (1) Feast's point-in-time join is entity-by-entity — it doesn't optimize cross-entity joins (e.g., features about the interaction between user and item). (2) Feast doesn't natively support real-time features computed by streaming pipelines — you need to push computed features to Feast's online store via a separate process. (3) Feast's feature registry is a simple file (YAML definitions in a Git repo) — it lacks a rich UI for feature discovery, lineage tracking, and impact analysis. Production-grade alternatives: Tecton (managed, handles streaming features natively), Feathr (LinkedIn's open-source, integrates with Spark and KubeFlow), or custom solutions.

### Deep Dive Path 3: Feature Pipeline Infrastructure on Kubernetes

**Interviewer**: "You're running feature pipelines on EKS. How do you orchestrate batch and streaming feature computation?"

**You**: Two orchestration layers: KubeFlow Pipelines for batch DAGs, and Flink on K8s for streaming. For batch: a KubeFlow Pipeline runs nightly — each step is a K8s pod. Step 1: SparkApplication CRD reads raw data from S3, computes aggregate features, writes Parquet to S3 (offline store). Step 2: A Python pod reads the Parquet, formats for Redis, and bulk-loads to the Redis cluster (online store materialization). Step 3: A validation pod compares feature distributions against previous day — flags anomalies. The pipeline is defined in Python using KubeFlow's SDK and versioned in Git.

For streaming: Flink runs as a FlinkDeployment CRD (via the Flink Kubernetes Operator). The Flink job reads from Kafka, computes windowed aggregations (sliding window counters, session aggregations), and writes to Redis. The Flink operator handles savepoints, upgrades, and auto-scaling (increasing parallelism based on Kafka consumer lag).

Resource management: feature pipelines are in a dedicated K8s namespace with ResourceQuotas. Batch Spark jobs use spot/preemptible instances (cost savings, tolerant of interruptions via Spark's RDD lineage). Flink streaming uses on-demand instances (can't tolerate interruptions). Node affinity ensures Spark executors land on spot nodes and Flink taskmanagers on on-demand nodes.

**Interviewer**: "How do you handle a feature pipeline that produces incorrect features? A bug in the Spark job wrote bad data to the online store."

**You**: Feature versioning + rollback. Every feature materialization writes to a versioned slot in the online store: `user:123:v5` (features computed by pipeline version 5). The model server reads from the current active version (configured via a feature flag). If version 5 has a bug: (1) Switch the active version pointer from v5 back to v4 — instant rollback, the model server immediately reads v4 features. (2) Fix the pipeline code. (3) Backfill: re-run the corrected pipeline, writing to v6. (4) Switch active version to v6 after validation.

For the offline store: Parquet files are immutable and partitioned by date + version. A bad batch writes to `s3://features/user_features/date=2024-01-15/version=5/`. Rollback: the training pipeline reads from `version=4` for that date. The bad version stays in S3 for debugging but is excluded from training data by the version pointer.

Monitoring: automated feature quality checks run after every pipeline execution. Checks include: (1) NaN/NULL rate per feature (<0.1% threshold), (2) distribution statistics (mean, variance, min, max) compared to rolling 7-day average, (3) feature coverage (% of entities with non-default values). Failures block materialization to the online store — the pipeline writes to a staging area, validation runs, and only on pass does it promote to production.

---

## How Real Companies Built This

- **Uber Michelangelo**: One of the first feature stores. Feature pipelines in Spark, online serving via Cassandra, offline in Hive. [Uber Michelangelo](https://www.uber.com/blog/michelangelo-machine-learning-platform/)
- **Airbnb Zipline**: Feature framework with point-in-time correctness built into the API. Backfill and online serving share feature definitions. [Airbnb Zipline](https://medium.com/airbnb-engineering/zipline-airbnbs-machine-learning-data-management-platform-78a5fa53ea64)
- **Feast**: Open-source feature store. Supports multiple backends (Redis, DynamoDB, BigQuery). Feature definitions in Python, CLI for materialization. [Feast Docs](https://docs.feast.dev/)
- **Tecton**: Managed feature platform built by ex-Uber Michelangelo team. Native streaming feature support, automatic backfill, built-in monitoring. [Tecton Architecture](https://www.tecton.ai/blog/what-is-a-feature-store/)
- **LinkedIn Feathr**: Open-source feature store with point-in-time join optimization using Spark. [Feathr GitHub](https://github.com/feathr-ai/feathr)
- **Google Vertex AI Feature Store**: Managed service. BigTable for online, BigQuery for offline. Integrated with Vertex Pipelines. [Vertex AI Feature Store](https://cloud.google.com/vertex-ai/docs/featurestore/overview)

---

## The Complete Reference Design

### API Design

```python
# Feature Registry API
POST /v1/feature-views
{
  "name": "user_click_features",
  "entities": ["user_id"],
  "features": [
    {"name": "click_count_7d", "dtype": "INT64", "description": "Total clicks in last 7 days"},
    {"name": "avg_session_duration", "dtype": "FLOAT64", "description": "Average session length in seconds"},
    {"name": "favorite_category", "dtype": "STRING", "description": "Most clicked category"}
  ],
  "source": {"type": "spark_batch", "schedule": "daily", "query": "SELECT ..."},
  "online_store": "redis",
  "offline_store": "s3_parquet",
  "ttl_days": 365
}

# Online feature retrieval (model server calls this)
POST /v1/features/online
{
  "feature_views": ["user_click_features", "user_profile_features"],
  "entities": [{"user_id": "123"}, {"user_id": "456"}]
}
# Response (p99 <5ms):
{
  "results": [
    {"user_id": "123", "click_count_7d": 42, "avg_session_duration": 320.5, ...},
    {"user_id": "456", "click_count_7d": 7, "avg_session_duration": 180.2, ...}
  ],
  "metadata": {"freshness": "2024-01-15T10:00:00Z", "version": 5}
}

# Offline training data generation
POST /v1/features/historical
{
  "feature_views": ["user_click_features", "item_features"],
  "entity_df_path": "s3://training/labels/2024-01-15/",  # (entity_id, timestamp, label)
  "output_path": "s3://training/datasets/2024-01-15/"
}
# Returns: path to Parquet file with point-in-time joined features
```

### Database Schema

```sql
-- Feature Registry (PostgreSQL)
CREATE TABLE feature_views (
    id           UUID PRIMARY KEY,
    name         VARCHAR(256) UNIQUE NOT NULL,
    description  TEXT,
    entity_type  VARCHAR(64) NOT NULL,         -- user, item, session
    owner_team   VARCHAR(128) NOT NULL,
    source_type  VARCHAR(32) NOT NULL,          -- spark_batch, flink_stream
    source_config JSONB NOT NULL,               -- query, schedule, topic
    online_store VARCHAR(32) DEFAULT 'redis',
    ttl_days     INT DEFAULT 365,
    version      INT NOT NULL DEFAULT 1,
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP NOT NULL
);

CREATE TABLE features (
    id              UUID PRIMARY KEY,
    feature_view_id UUID NOT NULL REFERENCES feature_views(id),
    name            VARCHAR(256) NOT NULL,
    dtype           VARCHAR(32) NOT NULL,       -- INT64, FLOAT64, STRING, EMBEDDING
    description     TEXT,
    default_value   TEXT,
    monitoring      JSONB,                      -- thresholds for quality checks
    UNIQUE (feature_view_id, name)
);

CREATE TABLE materialization_runs (
    id              UUID PRIMARY KEY,
    feature_view_id UUID NOT NULL REFERENCES feature_views(id),
    version         INT NOT NULL,
    status          VARCHAR(16) NOT NULL,       -- running, succeeded, failed
    records_written BIGINT,
    started_at      TIMESTAMP NOT NULL,
    completed_at    TIMESTAMP,
    quality_report  JSONB                       -- distribution stats, null rates
);

-- Online Store (Redis key layout)
-- Key: {entity_type}:{entity_id}:{feature_view_name}
-- Value: Protobuf-serialized feature vector + metadata
-- Example: user:123:user_click_features -> {click_count_7d: 42, ..., _version: 5, _ts: 1705312800}

-- Offline Store (S3 Parquet layout)
-- s3://features/{feature_view_name}/date={YYYY-MM-DD}/version={N}/part-*.parquet
-- Parquet columns: entity_id, event_timestamp, valid_from, valid_to, feature_1, feature_2, ...
```

### Key Algorithms — Point-in-Time Join

```python
import pandas as pd
from typing import List

def point_in_time_join(
    labels_df: pd.DataFrame,        # entity_id, timestamp, label
    feature_dfs: List[pd.DataFrame], # entity_id, valid_from, feature_*
    entity_key: str = "entity_id",
    timestamp_col: str = "timestamp",
) -> pd.DataFrame:
    """Efficient point-in-time join using sort-merge."""
    result = labels_df.sort_values([entity_key, timestamp_col])

    for feat_df in feature_dfs:
        feat_df = feat_df.sort_values([entity_key, "valid_from"])

        # As-of merge: for each label row, find the latest feature row
        # where valid_from <= label.timestamp
        result = pd.merge_asof(
            result.sort_values(timestamp_col),
            feat_df.rename(columns={"valid_from": timestamp_col}),
            on=timestamp_col,
            by=entity_key,
            direction="backward",  # latest feature <= label timestamp
            tolerance=pd.Timedelta("365 days"),
        )

    return result

# Spark version for production scale:
# from pyspark.sql import Window
# from pyspark.sql.functions import col, max as spark_max
#
# window = Window.partitionBy("entity_id").orderBy("valid_from").rangeBetween(
#     Window.unboundedPreceding, 0)
# features_with_latest = feature_df.withColumn(
#     "latest_value", spark_max("valid_from").over(window))
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Online store (Redis) | 4.4 TB x 2 (overhead) = 8.8 TB | 20 shards x 440 GB, r6g.16xlarge |
| Online QPS | 500K / 20 shards = 25K per shard | Well within Redis 100K QPS |
| Offline store (S3) | 1.6 PB historical + 50 TB/year growth | S3 Standard + Glacier tiering |
| Feature registry | 10K features, light traffic | Single PostgreSQL instance |
| Batch compute (Spark) | 1 TB input, 50 executors x 4 CPU | 200 CPU, 30 min/run on EKS |
| Stream compute (Flink) | 100K events/sec, 10 tasks | 10 taskmanagers, 4 CPU 8 GB |
| Training data gen | 1 TB labels x 10K features PIT join | 100-node Spark, 1 hour |

---

## Senior vs Staff vs Principal

| Aspect | Senior (E5/L5) | Staff (E6/L6) | Principal (L66+) |
|--------|----------------|----------------|-------------------|
| **Architecture** | Clean online/offline split, understands why both stores exist | Designs feature registry with versioning, lineage, and quality monitoring | Designs multi-team feature platform with self-service, governance, and cost attribution |
| **Correctness** | Knows point-in-time correctness matters | Implements PIT join in Spark, explains data leakage scenarios | Designs incremental PIT computation, handles schema evolution without recomputing history |
| **Scale** | Correct capacity math for Redis and S3 | Designs tiered storage for features (hot/warm/cold), caching for popular entities | Designs global feature serving across regions, optimizes for cost at PB scale |
| **Operations** | Mentions monitoring | Designs feature quality checks, freshness alerting, drift detection | Designs A/B testing infrastructure for features, impact analysis ("which models break if I change this feature?") |

---

## Red Flags & Common Mistakes

1. **No training-serving skew discussion** — This is THE central problem a feature store solves. If you don't mention it, you've missed the point.
2. **"Just compute features at inference time"** — For batch features (user's 30-day average), recomputing at inference time is prohibitively expensive. Pre-computation is essential.
3. **Using a relational database for online serving** — p99 <5ms at 500K QPS is not achievable with PostgreSQL/MySQL. You need an in-memory store.
4. **No point-in-time correctness** — Training with current feature values for historical events causes data leakage. This is the #1 cause of "model works in training but fails in production."
5. **Treating all features the same** — Real-time features (updated per-event) and batch features (updated daily) have fundamentally different computation and serving architectures.
6. **No feature versioning** — When a feature definition changes, you need to regenerate training data and retrain models. Without versioning, you can't roll back a bad feature change.
7. **Ignoring cold-start** — New entities have no features. Without default values and graceful degradation, the model server crashes or returns garbage predictions.
