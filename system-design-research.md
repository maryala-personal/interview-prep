# System Design Interview Preparation — Senior/Staff Engineer
## Tailored for: AWS EKS (Dataplane & Controlplane) | Kubernetes | Python & Go

> Comprehensive guide compiled for senior/staff-level system design interviews at
> Meta, Uber, Microsoft, and AI-focused companies. Leverages deep EKS/K8s expertise
> as a differentiator.

---

# Table of Contents

1. [Top 25 System Design Questions by Company](#1-top-25-system-design-questions-by-company)
2. [Infrastructure/Platform-Specific Designs (EKS-Aligned)](#2-infrastructureplatform-specific-designs-eks-aligned)
3. [Company-Specific Focus Areas](#3-company-specific-focus-areas)
4. [Staff-Level vs Senior-Level Expectations](#4-staff-level-vs-senior-level-expectations)
5. [Key Distributed Systems Concepts Deep Dive](#5-key-distributed-systems-concepts-deep-dive)
6. [Interview Frameworks & Execution Strategy](#6-interview-frameworks--execution-strategy)
7. [Recommended Study Plan & Resources](#7-recommended-study-plan--resources)

---

# 1. Top 25 System Design Questions by Company

## 1.1 The Core 25 Questions

| # | Question | Primary Companies | Frequency |
|---|----------|-------------------|-----------|
| 1 | Design a URL Shortener (TinyURL) | Meta, Microsoft, All | Very High (warm-up) |
| 2 | Design a News Feed / Timeline | Meta | Very High |
| 3 | Design a Chat/Messaging System (WhatsApp/Messenger) | Meta, Uber | Very High |
| 4 | Design a Rate Limiter | Meta, Uber, Microsoft | Very High |
| 5 | Design a Web Crawler | Microsoft, Meta | High |
| 6 | Design a Notification System | Meta, Uber | High |
| 7 | Design a Ride-Sharing Service (Uber/Lyft) | Uber | Very High |
| 8 | Design a Real-Time Location Tracking System | Uber | Very High |
| 9 | Design a Distributed Cache (Memcached/Redis) | Meta, Microsoft | High |
| 10 | Design a Search Autocomplete / Typeahead | Meta, Microsoft | High |
| 11 | Design a Distributed Key-Value Store | Meta, Microsoft, AI cos | High |
| 12 | Design a Content Delivery Network (CDN) | Meta, Microsoft | Medium-High |
| 13 | Design YouTube / Netflix (Video Streaming) | Meta, Microsoft | High |
| 14 | Design Google Maps / Proximity Service | Uber, Microsoft | High |
| 15 | Design a Distributed Task Scheduler | Uber, Meta, AI cos | High |
| 16 | Design a Metrics/Monitoring System (Datadog) | Uber, Meta, AI cos | High |
| 17 | Design a Distributed Log System (Kafka) | Uber, Meta | Medium-High |
| 18 | Design an Object Storage System (S3) | Microsoft, AI cos | Medium-High |
| 19 | Design a Container Orchestration System | Microsoft, AI cos | Medium (infra roles) |
| 20 | Design a Load Balancer | Microsoft, Uber | Medium-High |
| 21 | Design an Ad Click Aggregation System | Meta | High |
| 22 | Design a Hotel/Restaurant Reservation System | Uber, Microsoft | Medium |
| 23 | Design a Distributed File System (GFS/HDFS) | Meta, Microsoft | Medium |
| 24 | Design an ML Feature Store / Training Pipeline | AI companies | High (for AI roles) |
| 25 | Design a Multi-Region Deployment System | Meta, Microsoft, Uber | Medium-High |

---

## 1.2 Detailed Breakdown of Each Question

### Q1: Design a URL Shortener (TinyURL)
**Companies:** All (warm-up at Meta, Microsoft, screening at others)

**Key Components:**
- Encoding service: Base62 encoding, hash-based (MD5/SHA256 truncation), counter-based (Snowflake IDs)
- KV store for URL mappings (DynamoDB, Cassandra, or Redis + persistent store)
- Read-heavy: cache layer (Redis/Memcached) with LRU eviction
- 301 (permanent) vs 302 (temporary) redirects — trade-off: analytics vs cache
- Analytics pipeline for click tracking (async, Kafka -> aggregation)

**Scaling Considerations:**
- 100:1 read-to-write ratio; reads: ~100K QPS at scale
- Partitioning: hash-based on short URL key
- Cache hit ratio target: 80%+ (hot URLs follow Zipf distribution)
- Expiration/TTL management; periodic cleanup jobs

**Staff-Level Additions:**
- Custom domain support, abuse detection, rate limiting per tenant
- Multi-region with conflict-free replication (CRDTs or last-writer-wins)
- Discuss ID generation: Snowflake vs. centralized sequence vs. pre-generated ranges

---

### Q2: Design a News Feed / Timeline
**Companies:** Meta (signature question), sometimes Microsoft

**Key Components:**
- Fan-out on write vs. fan-out on read (hybrid approach for celebrities)
- Post service, Fan-out service, Feed service, Ranking service
- Social graph storage (adjacency list in DB, graph DB for complex queries)
- Feed cache per user (sorted set in Redis, score = timestamp)
- Ranking ML model (engagement prediction, content quality)

**Scaling Considerations:**
- Celebrity problem: users with millions of followers -> fan-out on read
- Hybrid: fan-out on write for normal users, on read for celebrities
- Feed generation latency SLA: < 200ms p99
- Feed pagination: cursor-based (not offset-based)

**Trade-offs:**
- Fan-out on write: high write amplification, but reads are fast (pre-materialized)
- Fan-out on read: low write cost, but reads require merging from multiple sources
- Cache invalidation complexity with hybrid approach

**Staff-Level Additions:**
- Content ranking pipeline (offline model training + online inference)
- A/B testing framework for feed ranking
- Multi-region consistency: eventual consistency is acceptable
- Discuss integrity/safety: content moderation pipeline before fan-out

---

### Q3: Design a Chat/Messaging System (WhatsApp/Messenger)
**Companies:** Meta (very common), Uber (for driver-rider chat)

**Key Components:**
- Connection management: WebSockets with long-lived connections
- Message service: generate message ID, persist, route
- Presence service: heartbeat-based online/offline status
- Group chat: fan-out to group members via message queue
- Message storage: per-conversation partition (Cassandra, HBase)
- Push notification service for offline users (APNs, FCM)
- End-to-end encryption: Signal Protocol (key exchange, ratcheting)

**Scaling Considerations:**
- Millions of concurrent WebSocket connections -> connection server fleet
- Connection server <-> message router mapping (consistent hashing or registry)
- Message ordering: per-conversation monotonic sequence numbers
- Storage: write-heavy, time-series-like access pattern (recent messages hot)

**Trade-offs:**
- WebSocket vs. long polling vs. SSE
- Message ordering: Lamport timestamps vs. server-assigned sequence numbers
- Sync protocol: last-seen sequence number per conversation
- Delivery guarantees: at-least-once with idempotent dedup on client

---

### Q4: Design a Rate Limiter
**Companies:** Meta, Uber, Microsoft (very frequently asked)

**Key Components:**
- Algorithms: Token bucket, leaky bucket, fixed window, sliding window log, sliding window counter
- Distributed rate limiting: Redis-based counters with Lua scripts for atomicity
- Rule engine: rate limit configuration per API, per user, per IP
- Response: HTTP 429 with Retry-After header, X-RateLimit-* headers

**Scaling Considerations:**
- Centralized vs. local rate limiting (trade-off: accuracy vs. latency)
- Race conditions in distributed counters -> Redis MULTI/EXEC or Lua scripts
- Sliding window counter: approximation using weighted current + previous window
- Global vs. per-node limits (e.g., 1000 global = 100 per node with 10 nodes)

**Algorithm Comparison:**
| Algorithm | Memory | Accuracy | Burst Handling |
|-----------|--------|----------|----------------|
| Token Bucket | Low | Good | Allows controlled bursts |
| Leaky Bucket | Low | Good | Smooths traffic (no bursts) |
| Fixed Window | Low | Poor (boundary) | Allows 2x burst at boundary |
| Sliding Window Log | High | Exact | No bursts |
| Sliding Window Counter | Low | Approximate | Minimal boundary issues |

**Staff-Level Additions:**
- Multi-tier rate limiting: edge (L7 LB) -> API gateway -> service-level
- Distributed rate limiting with eventual consistency (acceptable over-admit)
- Adaptive rate limiting based on system health (backpressure-driven)
- Rate limit as a platform service with self-service configuration

---

### Q5: Design a Web Crawler
**Companies:** Microsoft (Bing), Meta

**Key Components:**
- URL frontier: priority queue with politeness constraints (per-domain rate limit)
- DNS resolver with caching
- HTML downloader (respect robots.txt, handle redirects)
- Content parser: extract links, text, metadata
- URL deduplication: Bloom filter or hash set
- Content deduplication: SimHash / MinHash for near-duplicate detection
- URL storage: seen URLs, content store (S3/blob)

**Scaling Considerations:**
- Billions of pages -> distributed crawling across many workers
- Politeness: per-domain crawl delay, maintain separate queues per domain
- Consistent hashing to assign domains to crawler workers
- Trap detection: infinite URL spaces (calendars, query params)
- Freshness: re-crawl strategy based on page change frequency

---

### Q6: Design a Notification System
**Companies:** Meta, Uber

**Key Components:**
- Notification types: push (iOS/Android), SMS, email, in-app
- Event ingestion -> Kafka -> notification service
- Template engine, personalization, localization
- Provider adapters: APNs, FCM, Twilio, SendGrid
- User preference store: opt-in/opt-out per channel per notification type
- Deduplication and throttling (no spam)
- Delivery tracking: sent, delivered, opened, clicked

**Scaling Considerations:**
- Millions of notifications per minute during events (e.g., sports)
- Priority queues: critical (OTP) vs. marketing
- Retry with exponential backoff per provider
- Rate limiting per user to prevent notification fatigue

---

### Q7: Design a Ride-Sharing Service (Uber/Lyft)
**Companies:** Uber (signature), sometimes others

**Key Components:**
- Location service: driver location updates (every 3-5 seconds)
- Matching service: match riders to nearby drivers
- Geospatial index: geohash-based or QuadTree/S2 geometry cells
- Trip service: state machine (requested -> matched -> en-route -> in-progress -> completed)
- Pricing/surge engine: dynamic pricing based on supply/demand ratio per geo-cell
- ETA service: routing + ML-based travel time prediction
- Payment service: pre-auth, capture on completion, split payments

**Scaling Considerations:**
- Millions of active drivers updating location -> high write throughput
- Geospatial queries: "find 10 nearest drivers within 5km" in < 50ms
- Driver location: in-memory geospatial index (Redis GEO or custom S2-based)
- Matching optimization: Hungarian algorithm, greedy, or ML-based
- Multi-city/multi-region: shard by city/region

**Trade-offs:**
- Geohash vs. QuadTree vs. S2 cells for spatial indexing
- Push-based (server pushes ride to driver) vs. pull-based matching
- Consistency: double-booking prevention (optimistic locking on driver status)

---

### Q8: Design a Real-Time Location Tracking System
**Companies:** Uber, logistics companies

**Key Components:**
- High-frequency location ingestion (GPS, 1-5 sec intervals)
- Stream processing: Kafka -> Flink/Spark Streaming for real-time
- Geospatial storage: time-series DB (InfluxDB, TimescaleDB) or Cassandra
- Map tile rendering: vector tiles with live overlay
- WebSocket/SSE for real-time client updates
- Geofencing engine: detect enter/exit events for defined regions

**Scaling Considerations:**
- 1M active entities x 1 update/3 sec = 333K writes/sec
- TTL-based data eviction (keep last 24h hot, archive older)
- Geo-partitioned processing (reduce cross-region traffic)

---

### Q9: Design a Distributed Cache
**Companies:** Meta, Microsoft

**Key Components:**
- Cache eviction policies: LRU, LFU, ARC, random
- Consistent hashing with virtual nodes for data distribution
- Cache-aside, read-through, write-through, write-behind patterns
- Hot key mitigation: local cache + distributed cache (L1/L2)
- Serialization: Protobuf/MessagePack for efficiency

**Scaling Considerations:**
- Cache stampede: lock-based recompute, probabilistic early expiration
- Thundering herd: request coalescing (singleflight pattern in Go)
- Memory management: slab allocation (Memcached approach)
- Replication: primary-replica for read scaling, no replication for max memory

**Trade-offs:**
- Consistency vs. performance: cache invalidation is one of two hard problems
- TTL-based expiration vs. event-driven invalidation
- Embedded cache (in-process) vs. sidecar vs. remote cache

---

### Q10: Design Search Autocomplete / Typeahead
**Companies:** Meta, Microsoft

**Key Components:**
- Trie (prefix tree) with frequency counts at nodes
- Top-K suggestions: maintain min-heap of top-K at each node
- Data collection pipeline: search logs -> aggregation -> trie rebuild
- Multi-layer: browser cache (recent queries) -> CDN -> autocomplete service
- Personalization: blend global trending with user's search history

**Scaling Considerations:**
- Latency SLA: < 50ms (users type fast)
- Trie size: compressed trie, store in memory (fits for most use cases)
- Update strategy: offline rebuild every N hours, not real-time
- Sharding: by prefix range (a-f -> shard 1, g-m -> shard 2, etc.)

---

### Q11: Design a Distributed Key-Value Store
**Companies:** Meta, Microsoft, AI companies

**Key Components:**
- Partitioning: consistent hashing with virtual nodes
- Replication: quorum-based (W + R > N for strong consistency)
- Conflict resolution: vector clocks, last-writer-wins, or CRDTs
- Failure detection: gossip protocol (Phi Accrual failure detector)
- Anti-entropy: Merkle trees for replica synchronization
- Storage engine: LSM-tree (write-optimized) vs. B-tree (read-optimized)

**Scaling Considerations:**
- Tunable consistency: (N, W, R) parameters
- Compaction strategies: size-tiered vs. leveled (LSM-tree)
- Bloom filters to reduce unnecessary disk reads
- Cross-datacenter replication with async or semi-sync

**Reference Designs:** Dynamo (Amazon), Cassandra (Facebook), Riak

---

### Q12: Design a CDN
**Companies:** Meta, Microsoft

**Key Components:**
- Edge servers (PoPs) distributed globally
- Origin server + origin shield (reduce origin load)
- Cache hierarchy: L1 edge -> L2 regional -> origin
- Cache key: URL + Vary headers (Accept-Encoding, etc.)
- Invalidation: TTL-based + explicit purge API
- DNS-based routing: Anycast or GeoDNS to nearest PoP
- TLS termination at edge, HTTP/2 or HTTP/3 (QUIC)

**Scaling Considerations:**
- Cache hit ratio target: 95%+ for static content
- Long tail content: consistent hashing across edge cluster
- Video: adaptive bitrate streaming (HLS/DASH), chunked delivery
- DDoS protection at edge layer

---

### Q13: Design YouTube / Netflix (Video Streaming)
**Companies:** Meta, Microsoft

**Key Components:**
- Upload pipeline: chunked upload -> transcoding (FFmpeg) -> multiple resolutions/codecs
- Transcoding: DAG-based pipeline (split, transcode, merge, package)
- Storage: original in blob storage, transcoded in CDN-optimized storage
- Streaming: adaptive bitrate (ABR) with HLS/DASH
- Recommendation engine: collaborative filtering + content-based (ML)
- View counting: approximate real-time (Kafka -> aggregation)

**Scaling Considerations:**
- Transcoding is CPU-intensive: parallel workers, priority queues (popular content first)
- Storage: petabytes, tiered (hot/warm/cold)
- CDN: pre-populate popular content at edge
- Long tail: pull-through caching for less popular videos

---

### Q14: Design Google Maps / Proximity Service
**Companies:** Uber, Microsoft

**Key Components:**
- Map data: road network graph (nodes = intersections, edges = road segments)
- Routing: Dijkstra with A* or Contraction Hierarchies for pre-processing
- ETA prediction: historical data + ML (traffic patterns, time-of-day)
- Tile rendering: vector tiles at multiple zoom levels, pre-rendered + on-demand
- Proximity/nearby search: geohash-based index, QuadTree, or S2 cells
- Business data: separate service with geospatial index

**Scaling Considerations:**
- Map tiles: heavily cached, CDN-served
- Routing: pre-computed for common routes, real-time for less common
- Geospatial index partitioning: by geographic region

---

### Q15: Design a Distributed Task Scheduler
**Companies:** Uber, Meta, AI companies

**Key Components:**
- Task definition: one-time, recurring (cron), delayed
- Task queue: priority-based, partitioned by tenant or priority
- Scheduler: time-wheel or sorted set for due-time tracking
- Worker pool: pull-based (workers poll) or push-based (scheduler assigns)
- Exactly-once execution: distributed lock + idempotent tasks
- Dead letter queue for failed tasks, retry with backoff

**Scaling Considerations:**
- Millions of scheduled tasks: sharded time-wheel, DB-backed for persistence
- At-least-once delivery with idempotent handlers
- Worker scaling: auto-scale based on queue depth
- Multi-tenant: fair scheduling, resource quotas

**Staff-Level Additions (K8s parallel):**
- Draw parallels to kube-scheduler: predicate/priority functions, scheduler extenders
- Discuss gang scheduling for ML training jobs
- Preemption and priority-based eviction

---

### Q16: Design a Metrics/Monitoring System (Datadog/Prometheus)
**Companies:** Uber, Meta, AI companies

**Key Components:**
- Data model: metric name + labels/tags + timestamp + value
- Collection: pull-based (Prometheus) vs. push-based (StatsD/Datadog agent)
- Time-series database: columnar, compressed (gorilla encoding for timestamps/values)
- Query engine: PromQL-like, support aggregation, rate, percentiles
- Alerting: rules engine, threshold + anomaly-based, notification routing
- Dashboard service: Grafana-like visualization

**Scaling Considerations:**
- Cardinality explosion: limit label combinations
- Downsampling: 1s -> 1m -> 1h -> 1d for older data
- Write throughput: millions of data points per second -> LSM-tree + WAL
- Query: pre-aggregation for common queries, rollups

---

### Q17: Design a Distributed Log System (Kafka)
**Companies:** Uber, Meta

**Key Components:**
- Topic -> partitions -> segments on disk
- Append-only log with sequential writes (high throughput)
- Producer: partitioning strategy (key-based, round-robin)
- Consumer groups: each partition assigned to one consumer in group
- Replication: ISR (in-sync replicas), leader handles reads/writes
- Retention: time-based or size-based, compaction for changelogs

**Scaling Considerations:**
- Partition count = parallelism limit for consumers
- Rebalancing: cooperative sticky assignor to minimize disruption
- Exactly-once semantics: idempotent producers + transactional API
- Cross-datacenter: MirrorMaker 2, or active-active with conflict resolution

---

### Q18: Design an Object Storage System (S3)
**Companies:** Microsoft, AI companies

**Key Components:**
- Metadata service: object name -> storage location mapping
- Data service: chunked storage across data nodes, erasure coding (e.g., Reed-Solomon)
- Namespace: bucket + key hierarchy (flat namespace with prefix simulation)
- Consistency: strong read-after-write (S3 achieved this in 2020)
- Versioning: maintain version chain per object
- Lifecycle policies: transition between storage tiers (hot/warm/cold/archive)

**Scaling Considerations:**
- Metadata: partitioned by hash(bucket+key), replicated for durability
- Data placement: rack-aware, AZ-aware for fault tolerance
- Erasure coding vs. replication: storage efficiency (1.5x vs. 3x overhead)
- Multi-part upload for large objects (parallel upload of parts)

---

### Q19: Design a Container Orchestration System
**Companies:** Microsoft, AI companies (infra roles)

*See [Section 2.1](#21-design-a-container-orchestration-system) for full deep dive.*

---

### Q20: Design a Load Balancer
**Companies:** Microsoft, Uber

*See [Section 2.5](#25-design-a-cloud-load-balancer) for full deep dive.*

---

### Q21: Design an Ad Click Aggregation System
**Companies:** Meta (core business)

**Key Components:**
- Event ingestion: click events -> Kafka (partitioned by ad_id)
- Stream processing: Flink/Spark Streaming for real-time aggregation
- Aggregation granularity: per ad, per campaign, per advertiser, per time window
- Lambda/Kappa architecture: real-time stream + batch reconciliation
- Deduplication: click dedup using event_id in Redis/Bloom filter
- Query service: pre-aggregated materialized views for dashboard

**Scaling Considerations:**
- Billions of events/day: Kafka partitioning + parallel stream processing
- Exactly-once aggregation: Flink checkpointing + Kafka transactions
- Data reconciliation: batch job corrects real-time approximations
- Hot partition (viral ad): split processing with secondary aggregation

**Trade-offs:**
- Lambda (batch + stream) vs. Kappa (stream-only): complexity vs. correctness
- Approximate vs. exact counting at different latency tiers
- Pre-aggregation (fast queries, rigid schema) vs. raw events (flexible, slow queries)

---

### Q22: Design a Hotel/Restaurant Reservation System
**Companies:** Uber (UberEats), Microsoft

**Key Components:**
- Inventory service: available slots/rooms per time window
- Reservation service: create, modify, cancel with ACID guarantees
- Concurrency control: optimistic locking (version field) or pessimistic (SELECT FOR UPDATE)
- Overbooking strategy: allow N% overbooking based on cancellation rate
- Search: availability query with filters (date, location, price, rating)
- Payment: two-phase (reserve -> confirm) or saga pattern

**Scaling Considerations:**
- Hot inventory (popular restaurant Saturday night): serialization bottleneck
- Sharding by entity_id (restaurant/hotel); time-range queries are local
- Cache availability aggressively, invalidate on reservation change
- Idempotency keys for duplicate reservation prevention

---

### Q23: Design a Distributed File System (GFS/HDFS)
**Companies:** Meta, Microsoft

**Key Components:**
- Master/NameNode: metadata (file -> chunk list, chunk -> location)
- ChunkServers/DataNodes: store fixed-size chunks (64MB-256MB)
- Write: client -> master for chunk allocation -> pipeline to replicas
- Read: client -> master for chunk locations -> read from nearest replica
- Replication: typically 3x, rack-aware placement
- Master HA: hot standby with shared journal (ZooKeeper-based)

**Scaling Considerations:**
- Master memory: all metadata in memory (limits total file count)
- Large files preferred (small files = metadata bottleneck)
- Chunk size trade-off: large = fewer chunks, small = better parallelism
- Append-optimized: GFS assumes append-heavy workloads

---

### Q24: Design an ML Feature Store / Training Pipeline
**Companies:** AI companies, Uber (Michelangelo), Meta

*See [Section 3.4](#34-ai-companies-ml-infrastructure-focus) for full deep dive.*

---

### Q25: Design a Multi-Region Deployment System
**Companies:** Meta, Microsoft, Uber

**Key Components:**
- Deployment orchestrator: canary -> regional rollout -> global
- Traffic management: DNS-based (Route53) + L7 (Envoy, Istio)
- Data replication: sync (strong consistency, high latency) vs. async (eventual, low latency)
- Conflict resolution for multi-primary: CRDTs, last-writer-wins, application-level
- Health checking and automatic failover
- Configuration management: feature flags, regional overrides

**Scaling Considerations:**
- Network partition handling: CAP theorem in practice
- Data locality: serve reads from local region, write to primary or quorum
- Cross-region latency: 50-200ms (impacts consistency choices)
- Deployment blast radius: limit to one region at a time

---

# 2. Infrastructure/Platform-Specific Designs (EKS-Aligned)

> These leverage your deep EKS expertise. In interviews, demonstrating firsthand
> knowledge of building these systems is a massive differentiator.

## 2.1 Design a Container Orchestration System

### Requirements
- Schedule containers across a cluster of nodes
- Handle node failures, container restarts, resource management
- Support declarative desired-state management
- Service discovery, load balancing, secrets management

### Architecture (Modeled on Kubernetes)

```
                    +-------------------+
                    |    API Server      |  (RESTful, watches, admission control)
                    +-------------------+
                           |
              +------------+------------+
              |            |            |
     +--------+--+  +-----+-----+  +---+--------+
     | Scheduler  |  | Controller |  |   etcd     |
     |            |  |  Manager   |  | (3 or 5    |
     | (bin-pack,  |  | (reconcile |  |  node      |
     |  spread,   |  |  loops)    |  |  cluster)  |
     |  affinity) |  |            |  |            |
     +------------+  +------------+  +------------+
              |            |
     +--------+------------+---------+
     |        |            |         |
  +--+---+ +--+---+ +--+---+ +--+---+
  | Node | | Node | | Node | | Node |
  | Agent| | Agent| | Agent| | Agent|  (kubelet equivalent)
  |      | |      | |      | |      |
  | CRI  | | CRI  | | CRI  | | CRI  |  (containerd, CRI-O)
  +------+ +------+ +------+ +------+
```

### Key Components

**Control Plane:**
1. **API Server** (stateless, horizontally scalable)
   - RESTful API with OpenAPI spec
   - Authentication (x509, OIDC, webhook), Authorization (RBAC, ABAC)
   - Admission controllers: mutating + validating webhooks
   - Watch mechanism: long-poll/streaming for change notification
   - Resource versioning (optimistic concurrency via resourceVersion)

2. **etcd** (distributed KV store, source of truth)
   - Raft consensus for leader election and replication
   - 3 or 5 node cluster (tolerates 1 or 2 failures)
   - Watch API for change notifications -> API server watch cache
   - Compaction, defragmentation, snapshot/restore for operations
   - **Key insight from EKS:** etcd performance is the #1 bottleneck; separate etcd disks, tune heartbeat/election timeouts, use learner nodes for scale

3. **Scheduler**
   - Two-phase: filtering (predicates) -> scoring (priorities)
   - Predicates: resource fit, node affinity, taints/tolerations, pod anti-affinity
   - Priorities: least-requested, balanced resource, pod topology spread
   - Scheduling framework: plugins for extensibility (PreFilter, Filter, Score, Reserve, Bind)
   - **Advanced:** preemption (evict lower-priority pods), gang scheduling (all-or-nothing)

4. **Controller Manager**
   - Level-triggered reconciliation loops (not edge-triggered)
   - Each controller: observe (watch) -> diff (desired vs actual) -> act
   - Key controllers: ReplicaSet, Deployment (rolling update), StatefulSet, DaemonSet, Job/CronJob
   - Leader election among controller replicas (lease-based via etcd or K8s Lease objects)

**Data Plane (Node Components):**
1. **Node Agent (Kubelet)**
   - Pod lifecycle management: create, monitor, restart, kill
   - CRI (Container Runtime Interface): gRPC to containerd/CRI-O
   - CSI (Container Storage Interface): mount volumes
   - CNI (Container Network Interface): pod networking setup
   - Resource management: cgroups for CPU/memory limits, eviction manager
   - Health checks: liveness, readiness, startup probes

2. **Kube-proxy / iptables / eBPF**
   - Service -> Pod mapping via iptables rules, IPVS, or eBPF (Cilium)
   - ClusterIP, NodePort, LoadBalancer service types
   - Session affinity support

### Scaling Considerations
- **etcd:** Largest clusters push 10K-15K nodes; etcd list operations are expensive -> API server caching (watch cache), pagination, selectors
- **API server:** Horizontally scalable, use priority and fairness (APF) for request throttling
- **Scheduler:** Throughput: ~100 pods/sec with default plugins; optimize with scheduling profiles
- **Large cluster optimizations:** Informer-based caching, bookmark events, protobuf encoding

### Trade-offs (Staff-Level Discussion Points)
- **Declarative vs. imperative:** Declarative (desired state) enables self-healing but adds reconciliation latency
- **etcd vs. alternative stores:** etcd provides strong consistency + watch; alternatives (e.g., Kine with SQL) trade consistency model for operational simplicity
- **Single large cluster vs. multi-cluster federation:** Single = simpler management; multi = blast radius, multi-region, different trust boundaries
- **Pull-based (kubelet polls) vs. push-based (server pushes to agent):** K8s uses watch (push-like); pure push has delivery guarantee challenges

### Your EKS-Specific Edge
- Discuss how EKS manages the control plane as a service: multi-AZ etcd, managed API server scaling
- ENI-based pod networking (VPC CNI) vs. overlay networks: trade-off between IP management and simplicity
- EKS Fargate: serverless data plane, scheduling to managed nodes
- EKS control plane SLA: 99.95%, how it is achieved with cell-based architecture

---

## 2.2 Design a Control Plane

### What is a Control Plane?
The management layer that maintains the desired state of a distributed system and reconciles actual state to match.

### Architecture Pattern

```
+------------------+     +------------------+     +------------------+
|  External API    | --> |  State Store     | <-- |  Reconciliation  |
|  (CRUD + Watch)  |     |  (source of      |     |  Controllers     |
|                  |     |   truth)         |     |  (async loops)   |
+------------------+     +------------------+     +------------------+
        |                        ^                        |
        v                        |                        v
+------------------+     +------------------+     +------------------+
|  Admission       |     |  Leader          |     |  Data Plane      |
|  Control         |     |  Election        |     |  Agents          |
|  (validate,      |     |  (HA, single     |     |  (execute        |
|   mutate)        |     |   writer)        |     |   changes)       |
+------------------+     +------------------+     +------------------+
```

### Key Design Principles
1. **Desired State vs. Actual State:** Store desired state centrally; controllers reconcile
2. **Level-Triggered:** React to current state, not events (idempotent, self-healing)
3. **Watch-Based Notification:** Efficient change propagation without polling
4. **Leader Election for Singletons:** Only one controller instance active for write paths
5. **Idempotent Operations:** All control plane operations should be safely retried

### Components Deep Dive

**API Layer:**
- Versioned APIs (v1, v1beta1) for evolution without breaking clients
- Admission webhooks for policy enforcement (OPA/Gatekeeper, Kyverno)
- Rate limiting and priority-based request scheduling (APF in K8s)
- Audit logging for compliance

**State Store:**
- Strong consistency required (linearizable reads/writes)
- Watch capability for change notification
- Optimistic concurrency control (CAS operations)
- Options: etcd (K8s), ZooKeeper (Kafka), Consul, CockroachDB

**Reconciliation Engine:**
- Work queue with rate limiting and exponential backoff
- Shared informer caches to reduce API server load
- Controller sharding for horizontal scaling
- Status subresource for reporting actual state without triggering reconciliation

### Scaling Considerations
- API server: horizontal scaling with shared watch cache
- etcd: 3/5/7 nodes; sequential read/write model limits throughput
- Controller scalability: shard by namespace, by resource type, or by hash
- Multi-tenancy: namespace isolation, resource quotas, network policies

### Trade-offs
- **Strong consistency (etcd/Raft) vs. eventual consistency (Gossip):** Control planes usually need strong consistency for correctness
- **Single state store vs. federated:** Single = simpler; federated = partition tolerance across regions
- **Synchronous admission vs. async reconciliation:** Admission is synchronous (blocking on write); reconciliation is async (eventual convergence)

---

## 2.3 Design a Data Plane

### What is a Data Plane?
The layer that handles actual data processing, request routing, and workload execution based on control plane instructions.

### Architecture

```
Control Plane (pushes config)
        |
        v
+-------+--------+     +-----------------+     +-----------------+
| Data Plane Proxy| --> | Local Decision  | --> | Request/Packet  |
| (Envoy, eBPF,  |     | Engine (routing |     | Forwarding      |
|  iptables)      |     |  rules, LB)    |     |                 |
+-----------------+     +-----------------+     +-----------------+
        |
        v
+-----------------+
| Observability   |
| (metrics, logs, |
|  traces)        |
+-----------------+
```

### Key Components

**In Kubernetes Context:**
1. **kube-proxy (or replacement):**
   - Translates Service -> Endpoints mapping into forwarding rules
   - iptables mode: O(n) rules per service (doesn't scale well past 10K services)
   - IPVS mode: O(1) lookup, supports more LB algorithms
   - eBPF mode (Cilium): kernel-level forwarding, bypass iptables entirely

2. **CNI Plugin (Container Network Interface):**
   - Pod-to-pod networking setup
   - AWS VPC CNI: assigns real VPC IPs to pods (no overlay, native routing)
   - Calico: BGP-based routing or VXLAN overlay
   - Cilium: eBPF-based networking + security + observability
   - Trade-off: overlay (portable, more IPs) vs. native routing (performance, VPC integration)

3. **CRI (Container Runtime Interface):**
   - containerd: industry standard, used by EKS
   - CRI-O: K8s-specific, lighter
   - Runtime class: support multiple runtimes (runc, gVisor, Kata Containers)

4. **CSI (Container Storage Interface):**
   - Volume provisioning, attachment, mounting
   - EBS CSI driver, EFS CSI driver in EKS
   - Topology-aware provisioning (AZ-aware volume placement)

**In Service Mesh Context (Envoy-based):**
- Sidecar proxy or ambient mesh (waypoint proxy)
- xDS API: dynamic configuration from control plane (Istiod)
- L7 routing, traffic splitting, retries, circuit breaking
- mTLS between services (automatic cert rotation via SPIFFE/SPIRE)
- Observability: distributed tracing, access logs, metrics

### Data Plane Performance Considerations
- **Latency overhead:** Sidecar adds 1-3ms per hop; eBPF-based approaches < 0.5ms
- **Connection pooling:** Reuse upstream connections (HTTP/2 multiplexing)
- **Health checking:** Active (periodic probes) + passive (failure-based ejection)
- **Hot restart:** Envoy drains connections gracefully on config reload

### Your EKS-Specific Edge
- VPC CNI: pod IP = VPC IP -> security groups for pods, direct NLB -> pod routing
- Prefix delegation: assign /28 prefix per ENI for higher pod density
- Custom networking: pods in different subnets than nodes
- kube-proxy replacement with eBPF (Cilium on EKS)
- Pod networking performance tuning: jumbo frames, enhanced networking (ENA)

---

## 2.4 Design a Service Mesh

### Requirements
- Transparent service-to-service communication management
- Traffic management, security (mTLS), observability
- No application code changes

### Architecture (Istio-like)

```
+----------------------------------------------+
|                Control Plane                   |
|  +----------+  +----------+  +----------+    |
|  | Config   |  | Service  |  | Cert     |    |
|  | (traffic |  | Registry |  | Authority|    |
|  |  rules)  |  | (xDS)   |  | (mTLS)  |    |
|  +----------+  +----------+  +----------+    |
+----------------------------------------------+
         |  xDS (gRPC streaming)
         v
+----------------------------------------------+
|                Data Plane                      |
|  +------+  +------+  +------+  +------+      |
|  | Svc A|  | Svc B|  | Svc C|  | Svc D|      |
|  | +--+ |  | +--+ |  | +--+ |  | +--+ |      |
|  | |EP| |  | |EP| |  | |EP| |  | |EP| |      |
|  | +--+ |  | +--+ |  | +--+ |  | +--+ |      |
|  +------+  +------+  +------+  +------+      |
|  EP = Envoy Proxy (sidecar)                   |
+----------------------------------------------+
```

### Key Components

1. **Sidecar Proxy (Envoy)**
   - Intercepts all inbound/outbound traffic (iptables redirect)
   - L7 protocol parsing: HTTP/1.1, HTTP/2, gRPC, TCP
   - Load balancing: round-robin, least-connections, ring-hash, Maglev
   - Retries, timeouts, circuit breaking per-route
   - Distributed tracing: inject/propagate trace headers

2. **Control Plane (Istiod)**
   - Translates high-level config (VirtualService, DestinationRule) to Envoy xDS
   - Certificate Authority: issue short-lived SPIFFE certs for mTLS
   - Service discovery: aggregates K8s Services, external services
   - Config validation and status reporting

3. **Traffic Management**
   - Canary deployments: route 5% traffic to new version
   - A/B testing: route by headers (e.g., user-agent, cookie)
   - Traffic mirroring: shadow production traffic to test service
   - Fault injection: delay/abort for resilience testing

4. **Security**
   - mTLS: automatic, zero-config between mesh services
   - Authorization policies: L7 RBAC (allow service A -> service B on GET /api)
   - JWT validation at sidecar level

5. **Observability**
   - Metrics: request rate, latency (p50, p99), error rate (RED metrics)
   - Distributed tracing: Jaeger/Zipkin integration
   - Access logs: structured, per-request
   - Service graph: auto-generated topology map

### Trade-offs
- **Sidecar vs. Ambient Mesh (sidecarless):** Sidecar = per-pod overhead, fine-grained control; Ambient = shared waypoint proxies, lower resource overhead, but newer/less mature
- **Envoy vs. eBPF-based (Cilium Service Mesh):** Envoy = full L7 features; eBPF = lower latency for L3/L4, limited L7
- **Mesh vs. library-based (gRPC interceptors):** Mesh = language-agnostic, transparent; Library = lower latency, but code coupling
- **Central control plane vs. distributed:** Central = single point of config, easier to reason about; Distributed = more resilient

### Scaling Considerations
- Envoy memory: ~50MB per sidecar, matters at 10K+ pods
- xDS push frequency: batch config updates, use incremental xDS (delta)
- Certificate rotation: short-lived certs (24h) with background renewal
- At Uber scale: proprietary mesh, not Istio — performance is the driver

---

## 2.5 Design a Cloud Load Balancer

### Requirements
- Distribute traffic across backend instances
- Health checking, auto-scaling integration
- Support L4 (TCP/UDP) and L7 (HTTP/HTTPS) load balancing
- High availability, high throughput, low latency

### Architecture

```
Internet
    |
+---v---+
| DNS   | (Route53 / Azure Traffic Manager)
| (GSLB)|
+---+---+
    |
+---v----------------+
| L4 Load Balancer   | (NLB, Azure LB) - packet level
| (DSR / DNAT)       | (millions of connections, ~1ms added latency)
+---+----------------+
    |
+---v----------------+
| L7 Load Balancer   | (ALB, Azure App Gateway) - request level
| (HTTP routing,     |
|  TLS termination,  |
|  WAF integration)  |
+---+----------------+
    |
+---v---------+---v---------+---v---------+
| Backend     | Backend     | Backend     |
| Instance 1  | Instance 2  | Instance 3  |
+-------------+-------------+-------------+
```

### Key Components

**L4 Load Balancer:**
- Operates at TCP/UDP level (doesn't inspect HTTP)
- Techniques: DSR (Direct Server Return), DNAT, tunneling (IP-in-IP)
- Consistent hashing for sticky sessions (by 5-tuple)
- Maglev hashing (Google): minimal disruption on backend changes
- ECMP (Equal-Cost Multi-Path) for distributing across LB nodes
- VIP (Virtual IP) + BGP anycast for LB node redundancy

**L7 Load Balancer:**
- TLS termination (offload crypto from backends)
- HTTP routing: path-based, host-based, header-based
- Connection pooling to backends (HTTP/2 multiplexing)
- Request queuing and rate limiting
- WebSocket support (connection upgrade + long-lived forwarding)
- gRPC load balancing (per-RPC, not per-connection)

**Health Checking:**
- Active: periodic HTTP/TCP probes to backends
- Passive: track error rates, auto-eject unhealthy (outlier detection)
- Graceful drain: stop sending new connections, allow existing to complete

**Global Server Load Balancing (GSLB):**
- DNS-based: return different IPs based on client location (GeoDNS)
- Anycast: same IP advertised from multiple locations, BGP routes to nearest
- Health-aware: remove region from DNS if unhealthy
- Latency-based routing: Route53 latency records

### Scaling Considerations
- L4: millions of packets/sec per node (kernel bypass: DPDK, XDP/eBPF)
- L7: 100K-1M requests/sec per node depending on request size/TLS
- Horizontal scaling: add LB nodes behind ECMP/anycast
- Connection draining on LB scale-down

### AWS-Specific (EKS relevance)
- NLB -> K8s Service (type: LoadBalancer): direct pod targets with IP mode
- ALB Ingress Controller: K8s Ingress -> ALB rules, target group binding
- TargetGroupBinding CRD: decouple ALB targets from K8s service
- Gateway API: next-gen ingress, more expressive routing

### Trade-offs
- **L4 vs. L7:** L4 = higher throughput, less intelligence; L7 = richer routing, higher overhead
- **Proxy vs. DSR:** Proxy = can modify responses; DSR = lower latency (response bypasses LB)
- **Client-side LB vs. server-side LB:** Client-side (gRPC) = no proxy bottleneck; Server-side = simpler clients
- **Centralized LB vs. distributed (sidecar/mesh):** Centralized = single point of scaling; Distributed = higher aggregate capacity

---

## 2.6 Design an Auto-Scaling System

### Requirements
- Scale applications based on metrics (CPU, memory, custom metrics, queue depth)
- Scale infrastructure (nodes/VMs) to accommodate workloads
- Fast scale-up, graceful scale-down, avoid thrashing

### Architecture

```
+------------------+     +------------------+     +------------------+
| Metrics Pipeline |     | Scaling Policy   |     | Actuator         |
| (collect &       | --> | Engine           | --> | (execute scale   |
|  aggregate)      |     | (evaluate rules) |     |  actions)        |
+------------------+     +------------------+     +------------------+
        ^                        |
        |                        v
+------------------+     +------------------+
| Monitoring       |     | Cooldown &       |
| (Prometheus,     |     | Stabilization    |
|  CloudWatch)     |     | (prevent thrash) |
+------------------+     +------------------+
```

### Key Components

**Application-Level Auto-Scaling (HPA equivalent):**
- Metric sources: resource metrics (CPU/memory), custom metrics (queue depth, request latency), external metrics (SQS queue length)
- Scaling algorithm: `desiredReplicas = ceil(currentReplicas * (currentMetric / desiredMetric))`
- Stabilization window: prevent rapid scale-down after spike
- Behavior configuration: different scale-up and scale-down rates
- Multiple metrics: scale to satisfy all metric targets (take max desired replicas)

**Cluster-Level Auto-Scaling (Cluster Autoscaler / Karpenter):**
- Trigger: pending pods (can't be scheduled due to resource constraints)
- Node group selection: find cheapest node group that satisfies pod requirements
- Scale-down: identify underutilized nodes (< 50% utilization), drain pods, terminate
- Respect PodDisruptionBudgets during scale-down
- **Karpenter approach (EKS):** Direct pod-to-instance mapping, right-sizing, no node groups — provision exact instance type for pending pod(s)

**Predictive Auto-Scaling:**
- Use historical patterns to pre-scale before expected load
- ML model: time-series forecasting (daily/weekly patterns)
- Schedule-based: known events (Black Friday, product launches)

### Scaling Considerations
- **Scale-up latency:** Node provisioning (1-5 min) vs. pod scaling (seconds)
- **Bin-packing:** Karpenter consolidation — replace multiple underutilized nodes with fewer right-sized nodes
- **Spot/Preemptible instances:** Cost savings (60-90%) with interruption handling
- **Multi-AZ balancing:** Maintain even distribution for high availability

### Trade-offs
- **Reactive vs. predictive:** Reactive = simpler, but lags behind load; Predictive = proactive, but risk of over-provisioning
- **Horizontal vs. vertical:** Horizontal = more instances; Vertical = bigger instances (VPA in K8s) — horizontal preferred for stateless
- **Speed vs. stability:** Aggressive scaling = fast response but risk of thrashing; Conservative = stable but potential under-provisioning
- **Cost vs. performance:** Over-provision for safety (cost) vs. tight scaling (risk of latency spikes)

### Your EKS-Specific Edge
- Karpenter internals: provisioner -> node pool, machine -> node claim, consolidation algorithm
- EKS Managed Node Groups vs. self-managed vs. Fargate for different workload types
- Bottlerocket OS for faster node startup (< 30s boot time)
- Cluster Autoscaler vs. Karpenter: discuss the architectural differences and why Karpenter is superior for most use cases

---

## 2.7 Design a Cluster Scheduler

### Requirements
- Assign workloads to machines efficiently
- Respect resource constraints, affinity/anti-affinity, topology
- Optimize for utilization, fairness, and latency

### Architecture

```
+------------------+
| Scheduling Queue |  (pending workloads, priority-sorted)
+------------------+
         |
         v
+------------------+     +------------------+
| Filtering Phase  | --> | Scoring Phase    |
| (hard constraints|     | (soft preferences|
|  - resource fit  |     |  - spread        |
|  - taints        |     |  - affinity      |
|  - topology)     |     |  - utilization)  |
+------------------+     +------------------+
         |                        |
         v                        v
+------------------+     +------------------+
| Binding Phase    |     | Preemption       |
| (assign to node) |     | (evict lower     |
|                  |     |  priority pods)  |
+------------------+     +------------------+
```

### Key Design Decisions

**Scheduling Algorithms:**
1. **Single-scheduler (K8s default):** Simple, consistent, but throughput-limited (~100 pods/sec)
2. **Multi-scheduler (parallel):** Multiple schedulers, potential conflicts resolved by optimistic concurrency
3. **Two-level (Mesos):** Resource offers from agent -> framework scheduler decides
4. **Shared-state (Omega/Borg):** All schedulers see full cluster state, optimistic concurrency

**Gang Scheduling (for ML training):**
- All-or-nothing: either schedule all N pods of a job or none
- Critical for distributed training (all workers must start together)
- Implementations: Volcano, Coscheduling plugin in K8s scheduler framework
- Challenge: deadlock prevention (two gang jobs competing for same resources)

**Topology-Aware Scheduling:**
- NUMA-aware: pin pods to specific NUMA nodes for memory locality
- GPU topology: schedule related workloads on GPUs connected via NVLink
- Network topology: rack-aware, AZ-aware placement for latency and fault tolerance

**Bin-Packing vs. Spreading:**
- Bin-packing: maximize utilization, pack pods tightly -> fewer nodes needed -> cost savings
- Spreading: distribute pods across nodes/zones -> higher availability
- Production: usually hybrid — spread for HA, bin-pack for batch/preemptible

### Scaling Considerations
- Google Borg schedules across 10K+ nodes
- Scheduler throughput: batch scheduling decisions, evaluate only feasible nodes (percentageOfNodesToScore)
- Cache node information (snapshot-based scheduling in K8s)
- Separate scheduling queue from binding (async bind)

### Trade-offs
- **Centralized vs. distributed schedulers:** Centralized = global optimal; Distributed = higher throughput, local decisions
- **Preemption complexity:** Enables priority but adds significant complexity (cascading evictions)
- **Resource estimation:** Requests vs. actual usage — overcommit for utilization, risk eviction
- **Fairness vs. utilization:** Fair share per tenant vs. maximizing overall cluster utilization

---

## 2.8 Design a Container Registry

### Requirements
- Store and serve container images (OCI-compliant)
- Content-addressable storage, deduplication
- Access control, vulnerability scanning

### Architecture

```
+------------------+     +------------------+     +------------------+
| Registry API     |     | Metadata Store   |     | Blob Storage     |
| (Docker V2 API)  | --> | (repo, tags,     | --> | (S3, GCS)        |
| Push/Pull/Catalog|     |  manifests)      |     | Content-addressed|
+------------------+     +------------------+     +------------------+
        |                                                  |
        v                                                  v
+------------------+     +------------------+     +------------------+
| Auth Service     |     | Vulnerability    |     | CDN / Mirror     |
| (token-based,    |     | Scanner          |     | (geo-distributed |
|  RBAC)           |     | (Trivy, Grype)   |     |  pull)           |
+------------------+     +------------------+     +------------------+
```

### Key Components

**Image Storage Model:**
- Image = manifest (JSON) + config blob + layer blobs (tar.gz)
- Content-addressable: sha256 digest as blob key -> natural deduplication
- Layer sharing: base image layers shared across many images
- Manifest list: multi-architecture support (amd64, arm64)

**Push Flow:**
1. Client authenticates -> receives token
2. Check if blobs exist (HEAD request, content-addressed)
3. Upload missing blobs (chunked upload for large layers)
4. Upload manifest (references blobs by digest)
5. Tag manifest (tag is mutable pointer to digest)

**Pull Flow:**
1. Resolve tag to manifest digest
2. Download manifest
3. Download missing layers (check local cache first)
4. Verify digests

**Garbage Collection:**
- Mark-and-sweep: mark all blobs referenced by any manifest, delete unreferenced
- Must stop writes during GC or use reference counting
- Soft delete + grace period to handle race conditions

### Scaling Considerations
- Layer deduplication: common base images (alpine, ubuntu) -> massive storage savings
- Pull performance: geo-distributed mirrors, CDN for blob serving
- Registry proxy/pull-through cache: cache upstream images locally
- Parallel layer downloads: clients pull layers concurrently
- ECR (EKS): cross-region replication, lifecycle policies for image expiry

### Trade-offs
- **Centralized vs. distributed registry:** Centralized = simpler; Distributed = lower pull latency, higher availability
- **Push validation:** Scan on push (block vulnerable images) vs. scan async (faster push, allow vulnerable temporarily)
- **Tag mutability:** Mutable tags (latest can change) vs. immutable tags (content trust/Notary)
- **OCI artifacts:** Registry as generic artifact store (Helm charts, WASM, SBOM)

---

## 2.9 Design a Multi-Tenant Kubernetes Platform

### Requirements
- Multiple teams/applications share a K8s cluster
- Isolation: resource, network, security, blast radius
- Self-service: teams can deploy without platform team intervention
- Cost attribution, observability per tenant

### Architecture

```
+----------------------------------------------------------+
|                    Platform Control Plane                   |
|  +-------------+  +-------------+  +------------------+  |
|  | Tenant      |  | Policy      |  | Cost Attribution |  |
|  | Manager     |  | Engine      |  | Engine           |  |
|  | (onboard,   |  | (OPA/       |  | (resource usage  |  |
|  |  RBAC,      |  |  Kyverno)   |  |  per namespace)  |  |
|  |  quotas)    |  |             |  |                  |  |
|  +-------------+  +-------------+  +------------------+  |
+----------------------------------------------------------+
         |                    |                    |
+--------v--------------------v--------------------v-------+
|                    Shared K8s Cluster                      |
|  +-----------+  +-----------+  +-----------+              |
|  | Namespace |  | Namespace |  | Namespace |              |
|  | Team-A    |  | Team-B    |  | Team-C    |              |
|  | [quotas]  |  | [quotas]  |  | [quotas]  |              |
|  | [netpol]  |  | [netpol]  |  | [netpol]  |              |
|  | [rbac]    |  | [rbac]    |  | [rbac]    |              |
|  +-----------+  +-----------+  +-----------+              |
+----------------------------------------------------------+
```

### Isolation Dimensions

1. **Resource Isolation:**
   - ResourceQuotas per namespace (CPU, memory, pod count, PVC count)
   - LimitRanges: default requests/limits, min/max per container
   - Priority classes: platform-critical > production > development
   - Node pools: dedicated node groups for sensitive workloads

2. **Network Isolation:**
   - NetworkPolicies: default-deny ingress/egress per namespace
   - Whitelist specific cross-namespace traffic
   - DNS policies: restrict external DNS resolution
   - Service mesh: AuthorizationPolicy for L7 access control

3. **Security Isolation:**
   - RBAC: namespace-scoped roles, no cluster-admin for tenants
   - Pod Security Standards (PSS): restricted, baseline, privileged
   - Seccomp profiles, AppArmor/SELinux
   - Image policy: only pull from approved registries
   - Secret encryption at rest (KMS-backed in EKS)
   - IRSA (IAM Roles for Service Accounts) for AWS API access per tenant

4. **Blast Radius Isolation:**
   - Admission webhooks: validate resource specs, block risky configs
   - Rate limiting API server requests per namespace (APF)
   - Noisy neighbor protection: CPU throttling via CFS, memory eviction
   - Separate node pools for untrusted workloads (gVisor, Kata Containers)

5. **Observability Isolation:**
   - Per-tenant metrics (Prometheus with namespace labels, Thanos for multi-tenant)
   - Per-tenant logging (Fluentd/Fluent Bit routing by namespace)
   - Per-tenant tracing (Jaeger multi-tenant or separate collectors)
   - Cost reporting: resource usage * instance cost per namespace

### Self-Service Model
- GitOps (ArgoCD/Flux): tenants manage their own app deployments via Git
- Platform team manages: cluster infra, shared services, policies
- Tenant onboarding: automated namespace creation, RBAC, quotas via CRD/controller
- Internal Developer Platform: Backstage-based portal for self-service

### Scaling Considerations
- Hard multi-tenancy vs. soft: namespace-based (soft) vs. separate clusters (hard)
- vCluster / Cluster API for virtual cluster per tenant (stronger isolation)
- Control plane pressure: many namespaces -> large RBAC policies, slow API responses
- etcd size limit: 8GB default; too many resources across tenants can exhaust this

### Trade-offs
- **Shared cluster (multi-namespace) vs. cluster-per-tenant:**
  - Shared: cost-efficient (shared control plane, better bin-packing), complex isolation
  - Per-tenant: strong isolation, higher cost, operational overhead of many clusters
- **Virtual clusters (vCluster):** Middle ground — each tenant gets virtual API server, shares data plane
- **Policy enforcement:** Prevent vs. detect (shift-left in CI/CD vs. runtime admission)

---

# 3. Company-Specific Focus Areas

## 3.1 Meta (Infrastructure & Distributed Systems Focus)

### Interview Structure (E5/E6 — Senior/Staff)
- 2 system design rounds (45 min each)
- E5: design a system end-to-end, show you can handle scale
- E6: all of E5 plus influence, trade-off depth, multi-system thinking

### Common Questions
1. **Design News Feed** (signature question — very high frequency)
2. **Design Facebook Messenger / WhatsApp**
3. **Design Facebook Live (live streaming)**
4. **Design an Ad Click Aggregation Pipeline**
5. **Design a Distributed Cache (Memcache at Facebook scale)**
6. **Design a Rate Limiter**
7. **Design a Notification System**
8. **Design a Content Moderation System**
9. **Design a Social Graph Service**
10. **Design a Search System (Facebook Search)**

### What Meta Values
- **Scale thinking:** Everything at billions-of-users scale (2B+ DAU)
- **Concrete numbers:** Calculate QPS, storage, bandwidth requirements
- **Data modeling:** Schema decisions, partitioning strategies
- **Caching layers:** Multi-tier caching is core to Meta's architecture (Memcache, TAO)
- **Push vs. pull trade-offs** (fan-out analysis with concrete numbers)
- **Consistency trade-offs:** Meta uses eventual consistency extensively
- **Monitoring and alerting** as first-class design considerations

### Meta-Specific Systems to Know
- **TAO:** Social graph cache (objects + associations), leader/follower topology
- **Memcache at Facebook:** Lease-based invalidation, gutter servers, regional pools
- **Twine:** Container management system (their K8s equivalent)
- **Sharding:** Facebook uses MySQL with application-level sharding (not NoSQL)
- **XFaaS:** Serverless platform for microservices

### How to Leverage Your EKS Background at Meta
- Discuss Twine parallels when container orchestration comes up
- Show understanding of resource management at scale (scheduling, bin-packing)
- Control plane reliability patterns directly transfer
- etcd/consensus knowledge maps to ZooKeeper usage at Meta

---

## 3.2 Uber (Real-Time & Geo-Spatial Focus)

### Interview Structure
- 2 system design rounds
- Strong focus on real-time systems, geo-spatial, high availability

### Common Questions
1. **Design a Ride Matching System**
2. **Design Real-Time Location Tracking**
3. **Design Surge Pricing / Dynamic Pricing**
4. **Design a Food Delivery System (UberEats)**
5. **Design a Distributed Task Scheduler**
6. **Design a Geofencing Service**
7. **Design a Payment System**
8. **Design a Driver Onboarding System**
9. **Design a Metrics & Monitoring System**
10. **Design an Event-Driven Architecture**

### What Uber Values
- **Real-time systems:** Low-latency decision making (< 100ms for matching)
- **Geo-spatial expertise:** Geohash, S2 cells, H3 hexagonal grid system
- **High availability:** Multi-region, graceful degradation
- **Event-driven architecture:** Kafka-centric, event sourcing
- **Domain-driven design:** Clear bounded contexts, service boundaries
- **Data pipeline maturity:** Lambda architecture, stream processing (Flink)

### Uber-Specific Systems to Know
- **H3:** Uber's hexagonal hierarchical spatial index (open source)
- **Ringpop:** Consistent hashing library for service discovery
- **Peloton:** Uber's resource scheduler (similar to K8s scheduler + Mesos)
- **DOMA:** Domain-Oriented Microservice Architecture
- **Cadence/Temporal:** Workflow engine for durable execution (open-sourced by Uber)
- **Michelangelo:** ML platform (feature store, model serving, monitoring)
- **Schemaless:** Uber's append-only, sharded MySQL-based storage

### How to Leverage Your EKS Background at Uber
- Scheduler design directly maps to Peloton/Mesos concepts
- Multi-tenant platform design maps to Uber's shared infrastructure model
- Discuss container-native networking for low-latency service communication
- Auto-scaling for handling demand spikes (surge events)

---

## 3.3 Microsoft (Azure/Cloud Infrastructure Focus)

### Interview Structure
- 2 system design rounds (often one is a distributed systems deep dive)
- Cloud infrastructure roles: deep dive into specific Azure/cloud components

### Common Questions
1. **Design Azure Blob Storage / S3**
2. **Design a Distributed Key-Value Store (Cosmos DB)**
3. **Design a Cloud Load Balancer**
4. **Design Azure Functions (Serverless)**
5. **Design a CDN (Azure CDN / Akamai)**
6. **Design a Distributed Cache (Azure Redis Cache)**
7. **Design a Container Orchestration System (AKS)**
8. **Design a CI/CD Pipeline (Azure DevOps)**
9. **Design a Web Crawler (Bing)**
10. **Design a Search Autocomplete System**

### What Microsoft Values
- **Cloud-first thinking:** Everything as a managed service, multi-region
- **Reliability and SLA:** 99.99% availability, DR, RPO/RTO
- **Enterprise features:** Multi-tenancy, RBAC, compliance, audit logging
- **Distributed systems depth:** Consensus, replication, partition tolerance
- **Cost optimization:** Efficient resource utilization, tiered storage
- **Backward compatibility:** Versioned APIs, graceful deprecation

### Microsoft-Specific Systems to Know
- **Cosmos DB:** Multi-model, tunable consistency (5 levels: strong -> eventual)
- **Azure Service Fabric:** Stateful microservices, reliable collections
- **FASTER:** High-performance concurrent key-value store (research)
- **Azure Kubernetes Service (AKS):** Microsoft's managed K8s (competitor to EKS)
- **Tunder/Azure Resource Manager:** Cloud resource orchestration
- **Project Natick:** Underwater data centers (unique infrastructure thinking)

### How to Leverage Your EKS Background at Microsoft
- Direct competitor expertise (EKS vs. AKS) — show deep understanding of the problem space
- Discuss architectural differences: EKS ENI-based networking vs. AKS Azure CNI
- Control plane management: EKS cell-based architecture vs. AKS approach
- Show understanding of cloud provider abstractions (CPI, CSI, CNI)

---

## 3.4 AI Companies (ML Infrastructure Focus)

### Target Companies
OpenAI, Anthropic, Google DeepMind, Meta FAIR, NVIDIA, Databricks, Scale AI, Cohere, Mistral, xAI, Inflection, Hugging Face

### Common Questions
1. **Design an ML Training Pipeline (distributed training at scale)**
2. **Design a Model Serving / Inference System**
3. **Design a Feature Store**
4. **Design a GPU Cluster Scheduler**
5. **Design an ML Experiment Tracking System (MLflow/W&B)**
6. **Design a Data Labeling Platform**
7. **Design a Vector Database / Similarity Search System**
8. **Design a RAG (Retrieval-Augmented Generation) System**
9. **Design an LLM Serving System (with KV cache management)**
10. **Design a Model Registry and Deployment Pipeline**

### Deep Dive: Design an ML Training Pipeline

**Components:**
```
+------------------+     +------------------+     +------------------+
| Data Pipeline    |     | Training         |     | Model            |
| (ETL, feature    | --> | Orchestrator     | --> | Registry &       |
|  engineering,    |     | (distributed     |     | Evaluation       |
|  data loading)   |     |  training)       |     |                  |
+------------------+     +------------------+     +------------------+
        |                        |                        |
        v                        v                        v
+------------------+     +------------------+     +------------------+
| Feature Store    |     | GPU Cluster      |     | Experiment       |
| (online +        |     | Manager          |     | Tracker          |
|  offline)        |     | (scheduling,     |     | (metrics,        |
|                  |     |  checkpointing)  |     |  artifacts)      |
+------------------+     +------------------+     +------------------+
```

**Distributed Training Strategies:**
- **Data parallelism:** Replicate model on each GPU, split data batches, all-reduce gradients
- **Model parallelism:** Split model layers across GPUs (pipeline parallelism)
- **Tensor parallelism:** Split individual operations across GPUs (Megatron-LM style)
- **Expert parallelism:** MoE (Mixture of Experts) — route tokens to different experts on different GPUs
- **ZeRO (Zero Redundancy Optimizer):** Shard optimizer states, gradients, parameters across GPUs
- **3D parallelism:** Combine data + pipeline + tensor parallelism (used for GPT-scale models)

**Key Challenges:**
- GPU utilization: minimize idle time, overlap compute and communication
- Communication: all-reduce bandwidth (NVLink intra-node, InfiniBand inter-node)
- Checkpointing: periodic model state saves for fault recovery (expensive with large models)
- Elasticity: handle GPU failures, node preemption, dynamic scaling
- Data loading: not a bottleneck (prefetch, pipeline, distributed filesystem)

### Deep Dive: Design an LLM Inference Serving System

**Components:**
```
+------------------+     +------------------+     +------------------+
| Request Router   |     | Model Server     |     | KV Cache         |
| (load balancing, | --> | (GPU inference,  | --> | Manager          |
|  queuing,        |     |  batching)       |     | (memory pool,    |
|  rate limiting)  |     |                  |     |  paging)         |
+------------------+     +------------------+     +------------------+
        |                        |                        |
        v                        v                        v
+------------------+     +------------------+     +------------------+
| Token Streaming  |     | Model Sharding   |     | Autoscaling      |
| (SSE/WebSocket)  |     | (tensor parallel |     | (GPU-aware,      |
|                  |     |  across GPUs)    |     |  request-based)  |
+------------------+     +------------------+     +------------------+
```

**Key Optimizations:**
- **Continuous batching (vLLM):** Don't wait for all sequences in a batch to complete; dynamically add/remove sequences
- **PagedAttention (vLLM):** Manage KV cache like virtual memory pages -> reduce memory waste from fragmentation
- **Speculative decoding:** Use smaller model to draft tokens, verify with large model
- **Quantization:** FP16, INT8, INT4 -> reduce memory, increase throughput (at quality cost)
- **Flash Attention:** Fused kernel, tiled computation -> faster attention, less memory
- **Prefix caching:** Cache KV for common system prompts, share across requests
- **Disaggregated prefill and decode:** Separate compute for initial prefill vs. auto-regressive decode

**Scaling Considerations:**
- GPU memory is the bottleneck (not compute for many use cases)
- Model size determines minimum GPU count (70B params = ~140GB in FP16 = 2+ A100-80GB)
- Throughput vs. latency trade-off: larger batches = higher throughput but higher latency
- Time-to-first-token (TTFT) vs. tokens-per-second (TPS) SLAs
- Multi-model serving: share GPU cluster across models, bin-pack based on memory

### Deep Dive: Design a GPU Cluster Scheduler

**Requirements:**
- Schedule ML training and inference jobs across GPU clusters
- Handle GPU topology (NVLink, InfiniBand), multi-node jobs
- Fair sharing, priority, preemption, gang scheduling

**Key Components:**
- **Resource abstraction:** GPUs as first-class resources (type, memory, interconnect)
- **Topology-aware placement:** Schedule multi-GPU jobs on well-connected GPUs
  - Prefer same node (NVLink) > same rack (InfiniBand) > cross-rack
- **Gang scheduling:** All-or-nothing for distributed training jobs
- **Preemption:** Interrupt low-priority jobs for high-priority (save checkpoint first)
- **Queue management:** Per-team fair share queues, hierarchical quotas
- **Elastic training:** Allow jobs to run with variable number of GPUs

**K8s-Based GPU Scheduling:**
- NVIDIA device plugin: expose GPUs as extended resources
- GPU sharing: MIG (Multi-Instance GPU), time-slicing, MPS
- Topology Manager: NUMA-aligned GPU allocation
- Volcano scheduler: gang scheduling, job-level scheduling
- Kueue: K8s-native job queuing system (quotas, fair sharing, preemption)
- Run:ai / DynamicAI: commercial GPU orchestration on K8s

### How to Leverage Your EKS Background at AI Companies
- **Direct transfer:** K8s scheduler -> GPU scheduler, just with additional topology constraints
- **Karpenter-like provisioning for GPU nodes:** Right-size GPU instance types (p4d, p5, g5)
- **Multi-tenant GPU platform:** Same patterns as multi-tenant K8s but with GPU quotas
- **Control plane for ML:** Model deployment as a reconciliation loop (desired model state -> actual serving state)
- **Data plane for inference:** Load balancing for GPU-bound services, health checking for GPU failures

---

# 4. Staff-Level vs Senior-Level Expectations

## 4.1 The Core Differences

| Dimension | Senior (L5/E5) | Staff (L6/E6) |
|-----------|----------------|----------------|
| **Scope** | Design one system well | Design a system and its interactions with the ecosystem |
| **Depth** | Cover main components thoroughly | Deep dive into the hardest 2-3 components with novel insights |
| **Trade-offs** | Identify and discuss trade-offs | Quantify trade-offs and connect to business impact |
| **Ambiguity** | Handle well-defined requirements | Define the requirements yourself, handle ambiguity |
| **Scale** | Design for given scale | Discuss evolution: MVP -> growth -> scale architecture |
| **Failure modes** | Handle basic failures (node crash, network partition) | Discuss cascading failures, grey failures, partial outages |
| **Cross-cutting concerns** | Mention monitoring, security | Design monitoring/alerting/security as integral components |
| **Technical leadership** | Demonstrate personal expertise | Demonstrate ability to drive technical decisions for a team |
| **Communication** | Clear and structured | Clear, structured, and proactively addresses concerns |

## 4.2 How Staff Engineers Differentiate in System Design

### 1. Requirements Gathering (First 5 Minutes)
**Senior:** Asks basic clarifying questions (users, QPS, storage)

**Staff:**
- Asks about organizational context: "Who owns this system? One team or multiple?"
- Identifies tension in requirements: "Real-time and consistency are at tension here — which matters more?"
- Proposes phased approach: "Let me design for current scale but note where the architecture must change at 10x"
- Identifies non-functional requirements proactively: compliance, audit, multi-region, disaster recovery
- Asks about existing systems: "What exists today? Are we building from scratch or evolving?"

### 2. High-Level Design (10 Minutes)
**Senior:** Draws boxes and arrows, identifies major components

**Staff:**
- Starts with data flow and ownership boundaries
- Identifies the critical path and the areas of highest risk
- Discusses service boundaries using domain-driven design principles
- Proactively identifies what NOT to build: "We should use an existing queue here, not build our own"
- Mentions the team structure implications (Conway's Law)

### 3. Deep Dive (20 Minutes)
**Senior:** Explains how major components work, discusses basic scaling

**Staff:**
- Picks the most interesting/challenging component to deep dive
- Discusses multiple approaches with quantified trade-offs:
  - "Approach A gives us O(1) reads but O(n) writes. At our write rate of 10K/sec, this means..."
  - "Approach B uses 3x more storage but reduces p99 latency from 200ms to 20ms"
- Connects to real-world systems: "This is similar to how Cassandra handles X, but we need to modify because Y"
- Discusses failure modes in depth:
  - What happens during a network partition between these two services?
  - How do we handle a slow dependency without cascading failure?
  - What is the blast radius if this component fails?
- Proposes novel solutions where appropriate (not just textbook patterns)

### 4. Evolution and Operability (5 Minutes)
**Senior:** May mention monitoring if prompted

**Staff:**
- Discusses the system's evolution over time:
  - "Start with a monolith, extract this service when the team grows"
  - "At 100x scale, we'd need to shard this differently"
- Operational excellence:
  - SLOs: "We'd target p99 < 100ms, with error budget policy"
  - Deployment: canary, progressive rollout, automated rollback
  - Observability: RED metrics, distributed tracing, alerting strategy
  - Runbooks: "For on-call, the most common issue would be X, detected by Y, mitigated by Z"
- Cost analysis: "This design would cost approximately $X/month at scale, with these optimization opportunities"

## 4.3 Staff-Level Behavioral Signals

1. **Driving the conversation:** The candidate leads, not the interviewer. They set the agenda, timebox, and navigate.
2. **Comfort with ambiguity:** When requirements are vague, the candidate makes reasonable assumptions, states them, and proceeds.
3. **Opinionated but flexible:** Has a strong point of view backed by reasoning, but adjusts when given new information.
4. **Systems thinking:** Considers the broader ecosystem — how this system affects and is affected by other systems.
5. **Mentoring voice:** Explains decisions in a way that would teach a less senior engineer.
6. **Business awareness:** Connects technical decisions to business outcomes (cost, user impact, time-to-market).

## 4.4 Common Staff-Level Pitfalls to Avoid

1. **Over-designing:** Don't design for Google scale when the question is about a startup
2. **Name-dropping without depth:** Don't just say "use Kafka" — explain why and what alternatives you considered
3. **Ignoring the interviewer's hints:** They may be steering you toward the interesting part
4. **Spending too long on requirements:** 5 minutes max, then design with stated assumptions
5. **Not going deep enough:** Staff is about depth in the critical areas, not breadth across everything
6. **Forgetting operability:** Production systems need monitoring, deployment, and incident response

---

# 5. Key Distributed Systems Concepts Deep Dive

## 5.1 Consensus Algorithms

### Raft
**Used in:** etcd (K8s), Consul, CockroachDB, TiKV

**Core Concepts:**
- **Leader election:** Randomized election timeout, candidate requests votes, majority wins
- **Log replication:** Leader appends entries, replicates to followers, commits when majority ack
- **Safety:** At most one leader per term; committed entries are durable across leader changes
- **Membership changes:** Joint consensus for safe cluster reconfiguration

**Key Properties:**
- Strong leader: all writes go through leader
- Term numbers: monotonically increasing, detect stale leaders
- Log matching: if two logs have entry with same index and term, all preceding entries match
- Commit rule: entry committed when replicated to majority AND entry is from current term

**Performance Characteristics:**
- Write latency: 1 RTT (leader -> followers -> ack)
- Read latency: 0 RTT if read from leader with lease; 1 RTT for linearizable read (read index)
- Throughput limited by leader (single-writer)

**etcd-Specific:**
- Default heartbeat: 100ms, election timeout: 1000ms
- Recommended max cluster size: 5 (7 for larger deployments)
- Performance: ~10K writes/sec, ~100K reads/sec (with watch cache)
- Key bottleneck for large K8s clusters: list operations, watch connection count

### Paxos
**Used in:** Google Spanner (Multi-Paxos), Chubby

**Core Concepts:**
- **Proposer, Acceptor, Learner** roles
- **Two-phase:** Prepare (promise) -> Accept (accepted)
- Single-decree Paxos: agrees on one value
- Multi-Paxos: optimization for sequential decisions (stable leader skips prepare phase)

**Comparison with Raft:**
| Aspect | Raft | Paxos |
|--------|------|-------|
| Understandability | Designed for clarity | Notoriously hard to understand |
| Leader | Strong leader required | Flexible (leaderless Paxos exists) |
| Log | Sequential, gap-free | Can have gaps (requires filling) |
| Implementation | Many production implementations | Fewer correct implementations |
| Reconfiguration | Joint consensus | Complex, many variants |

### Practical Advice for Interviews
- Default to Raft when discussing consensus (easier to explain, widely used)
- Know when you need consensus: leader election, distributed locks, replicated state machine
- Know when you DON'T need consensus: eventual consistency is often sufficient (and faster)
- ZooKeeper uses ZAB (ZooKeeper Atomic Broadcast) — similar to Raft but predates it

---

## 5.2 CAP Theorem

### The Theorem
In a distributed system, during a network partition (P), you must choose between:
- **Consistency (C):** All nodes see the same data at the same time (linearizability)
- **Availability (A):** Every request receives a response (not necessarily the latest data)

### Practical Interpretation (PACELC)
- **PA/EL:** During partition -> Available; Else -> Low Latency (e.g., Cassandra, DynamoDB)
- **PC/EC:** During partition -> Consistent; Else -> Consistent (e.g., BigTable, HBase, etcd)
- **PA/EC:** During partition -> Available; Else -> Consistent (most RDBMS with async replication)

### Consistency Models Spectrum
```
Strongest                                                   Weakest
|---------------------------------------------------------------|
Linearizable > Sequential > Causal > Read-your-writes > Eventual
     (etcd)     (ZooKeeper)  (CRDTs)                    (Cassandra)
```

### When to Choose What
- **Strong consistency:** Financial transactions, inventory counts, coordination (etcd, Spanner)
- **Eventual consistency:** Social feeds, view counts, recommendations (Cassandra, DynamoDB)
- **Causal consistency:** Chat messages (order matters per conversation, not globally)
- **Tunable consistency:** Cassandra (ONE, QUORUM, ALL), DynamoDB (eventual, strong)
- **Cosmos DB 5 levels:** Strong, Bounded Staleness, Session, Consistent Prefix, Eventual

### Interview Application
- Always discuss the consistency model for your system design
- Most social/content systems: eventual consistency is fine
- Payment/booking systems: need strong consistency (at least for critical paths)
- The real choice is usually: "Which parts need strong consistency and which don't?"

---

## 5.3 Consistent Hashing

### Problem
- Regular hashing (key % N) causes massive remapping when N changes
- Adding/removing a server shuffles almost all keys

### Solution
- Hash both keys and servers onto a ring (0 to 2^32 - 1)
- A key maps to the first server clockwise on the ring
- Adding/removing a server only affects keys between it and its predecessor

### Virtual Nodes
- Each physical server gets multiple positions on the ring (100-200 virtual nodes)
- Solves: uneven distribution, heterogeneous servers (more vnodes for bigger servers)
- Used by: Cassandra, DynamoDB, Riak

### Bounded-Load Consistent Hashing
- Limit each server to at most (1 + epsilon) * average_load
- If target server is overloaded, route to next available server on ring
- Better load distribution at cost of some consistency on server changes

### Jump Consistent Hashing
- O(1) memory, O(ln n) time
- Only works for sequential server numbering (0 to n-1)
- Great for: partitioning across numbered shards
- Limitation: doesn't support arbitrary server addition/removal

### Maglev Hashing (Google)
- Consistent hashing optimized for load balancers
- Lookup table with minimal disruption on backend changes
- O(1) lookup time with small lookup table

---

## 5.4 Leader Election

### Approaches

**1. Raft/Paxos-based (via consensus)**
- Strongest guarantees, most overhead
- Used by: etcd, ZooKeeper, Consul
- Lease-based: leader holds a lease, must renew before expiry

**2. Database-based**
- Use a row with a lock column and TTL
- `UPDATE leaders SET owner = me, expires = now + 30s WHERE key = 'service-x' AND (expires < now OR owner = me)`
- Simple but depends on DB availability

**3. K8s Lease Objects**
- K8s controller-manager and scheduler use Lease objects for leader election
- Lease holder renews periodically; others watch for expiry
- Client-go has a leader election library

**4. Redlock (Redis)**
- Lock across N Redis instances (majority needed)
- Controversial: Martin Kleppmann's critique — clock skew can violate safety
- Acceptable for: distributed rate limiting, dedup (where occasional double-processing is OK)
- Not acceptable for: financial transactions, unique constraint enforcement

### Fencing Tokens
- Every leadership grant includes a monotonically increasing token
- Resources (DB, storage) reject operations with stale tokens
- Prevents: split-brain where old leader still thinks it is the leader

---

## 5.5 Distributed Locks

### Approaches

**1. ZooKeeper / etcd**
- Create ephemeral/sequential node; lowest sequence number holds lock
- Session-based: lock auto-released if holder dies (session expires)
- Watch predecessor for efficient waiting (no thundering herd)

**2. Redis (Redlock)**
- SET key value NX PX 30000 (set if not exists, with TTL)
- Redlock: acquire lock on majority of N Redis instances
- Simple, fast, but weaker guarantees (no fencing)

**3. Database**
- SELECT FOR UPDATE (pessimistic locking)
- Optimistic locking: version/etag check on update
- Advisory locks: PostgreSQL `pg_advisory_lock`

### Trade-offs
| Approach | Latency | Safety | Complexity |
|----------|---------|--------|------------|
| ZooKeeper/etcd | ~10ms | Strong (with fencing) | Medium |
| Redis (single) | ~1ms | Weak (no fencing, TTL) | Low |
| Redlock | ~5ms | Medium (clock concerns) | Medium |
| Database | ~5-20ms | Strong (ACID) | Low |

### When You Don't Need Distributed Locks
- Idempotent operations: just retry, no lock needed
- Last-writer-wins: use version vectors, no coordination
- CRDTs: conflict-free by design
- Partitioned workloads: each partition has a single writer (no contention)

---

## 5.6 Event Sourcing

### Concept
- Store the sequence of state-changing events, not the current state
- Current state is derived by replaying events from the beginning (or snapshot + events)
- Events are immutable, append-only

### Components
```
Command -> Command Handler -> Event Store (append-only log)
                                    |
                                    v
                              Projections (materialized views / read models)
```

### Benefits
- Complete audit trail (every change is recorded)
- Temporal queries: reconstruct state at any point in time
- Event replay: rebuild projections, backfill new read models
- Decoupling: consumers process events independently

### Challenges
- Event schema evolution: versioning events, upcasting
- Eventual consistency between write (event store) and read (projections)
- Event store growth: snapshots to avoid replaying from beginning
- Debugging: harder to understand current state (must trace events)

### When to Use
- Financial systems (audit trail, regulatory compliance)
- Collaborative editing (operational transformation or CRDTs + event log)
- Systems where "why did it change" matters as much as "what is the current state"
- NOT for: simple CRUD, high-volume low-value data (metrics, logs)

---

## 5.7 CQRS (Command Query Responsibility Segregation)

### Concept
- Separate the write model (commands) from the read model (queries)
- Write model: normalized, optimized for consistency
- Read model: denormalized, optimized for specific queries

### Architecture
```
+----------+     +------------+     +----------+
|  Write   | --> |  Event     | --> |  Read    |
|  Model   |     |  Bus       |     |  Model   |
|  (DB1)   |     |  (Kafka)   |     |  (DB2)   |
+----------+     +------------+     +----------+
     ^                                    |
     |                                    v
  Commands                             Queries
```

### Benefits
- Independent scaling of reads and writes
- Optimized data models for each access pattern
- Can use different databases for read and write (e.g., MySQL for writes, Elasticsearch for search)

### Trade-offs
- Eventual consistency between write and read models (stale reads possible)
- Increased complexity (two data models, sync mechanism)
- When NOT to use: simple domains with similar read/write patterns

### Relationship with Event Sourcing
- Often paired but independent concepts
- Event Sourcing -> events -> project into CQRS read models
- Can use CQRS without Event Sourcing (CDC from write DB to read DB)

---

## 5.8 Rate Limiting (Distributed)

### Algorithms (detailed in Q4 above)

### Distributed Implementation Patterns

**1. Redis + Lua Script (Token Bucket)**
```lua
-- Atomic token bucket in Redis
local tokens = redis.call('get', KEYS[1])
local last_refill = redis.call('get', KEYS[2])
local now = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local capacity = tonumber(ARGV[3])

-- Refill tokens
local elapsed = now - tonumber(last_refill or now)
tokens = math.min(capacity, tonumber(tokens or capacity) + elapsed * rate)

if tokens >= 1 then
    tokens = tokens - 1
    redis.call('set', KEYS[1], tokens)
    redis.call('set', KEYS[2], now)
    return 1  -- allowed
else
    return 0  -- rejected
end
```

**2. Local + Global Hybrid**
- Each server maintains a local counter
- Periodically sync with global counter (Redis/DB)
- Trade-off: accuracy vs. latency (local decisions are fast but approximate)

**3. Sliding Window Counter**
- Current window count + (previous window count * overlap percentage)
- Memory efficient (just two counters per window)
- 99.97% accuracy in practice (CloudFlare's approach)

### Multi-Tier Rate Limiting
1. **Edge (CDN/L7 LB):** IP-based rate limiting (DDoS protection)
2. **API Gateway:** Per-API-key rate limiting
3. **Service level:** Per-user, per-resource rate limiting
4. **Dependency level:** Client-side rate limiting to protect downstream services

---

## 5.9 Circuit Breakers

### States
```
+--------+     failures > threshold     +---------+
| CLOSED | --------------------------> |  OPEN   |
| (normal|                             | (reject |
|  flow) | <---------+                 |  all)   |
+--------+           |                 +---------+
                     |                      |
                     |    timeout expires    |
                     |                      v
                     |               +-----------+
                     +-------------- | HALF-OPEN |
                       success       | (allow    |
                                     |  limited) |
                                     +-----------+
```

### Configuration Parameters
- **Failure threshold:** Number or percentage of failures to trip (e.g., 50% of last 100 requests)
- **Timeout:** How long to stay open before testing (e.g., 30 seconds)
- **Half-open requests:** Number of trial requests in half-open state (e.g., 3)
- **Sliding window:** Time-based or count-based window for failure tracking

### Implementation Patterns
- **Per-host circuit breaker:** Track failures to each backend host independently (Envoy outlier detection)
- **Per-service circuit breaker:** Track aggregate failure rate to a service
- **Bulkhead + circuit breaker:** Separate thread pools per dependency + circuit breaker

### Libraries
- **Go:** sony/gobreaker, resilience-go
- **Python:** pybreaker, tenacity (retry with circuit breaker pattern)
- **Service mesh:** Envoy/Istio DestinationRule outlier detection (passive circuit breaking)

---

## 5.10 Backpressure

### The Problem
- When a producer generates data faster than a consumer can process it
- Without backpressure: memory exhaustion, OOM kills, cascading failures

### Strategies

**1. Drop (load shedding)**
- Drop oldest, drop newest, or random drop
- Used when: real-time data where stale data is useless (metrics, live video)
- K8s API server: priority and fairness (APF) drops lower-priority requests

**2. Buffer**
- Kafka-like queue absorbs temporary bursts
- Finite buffer with overflow policy (block producer or drop)
- Good for: bursty workloads with sufficient average capacity

**3. Slow down producer**
- TCP flow control (receiver window)
- gRPC flow control (HTTP/2 window)
- Reactive Streams: subscriber requests N items at a time

**4. Scale consumer**
- Auto-scaling based on queue depth / consumer lag
- K8s HPA with custom metrics (Kafka consumer lag -> scale consumers)
- Eventual convergence: if production rate consistently exceeds capacity, scaling alone won't help

**5. Adaptive load shedding**
- CoDel (Controlled Delay): drop from head of queue when queue latency exceeds threshold
- Client-side: exponential backoff with jitter
- Server-side: return 503 with Retry-After header, shed based on request priority

### Backpressure in K8s
- API server: APF (API Priority and Fairness) — queuing with priority levels
- etcd: rate limiting via --max-request-bytes, --quota-backend-bytes
- kubelet: eviction manager (memory pressure -> evict low-priority pods)
- Resource limits: CPU throttling (CFS bandwidth), memory OOM kills

---

## 5.11 Kubernetes Internals Deep Dive

### etcd
- **Raft consensus** for replication across 3/5 nodes
- **MVCC (Multi-Version Concurrency Control):** Each key has a revision history
- **Watch:** Clients subscribe to key/prefix changes (server push via gRPC streaming)
- **Compaction:** Remove old revisions to reclaim space (auto-compaction every 5 min in K8s)
- **Performance tuning:**
  - Dedicated SSD for etcd data directory
  - Separate etcd cluster from the main network
  - Adjust heartbeat-interval (100ms) and election-timeout (1000ms) for cross-AZ deployments
  - Monitor: etcd_disk_wal_fsync_duration_seconds, etcd_network_peer_round_trip_time_seconds

### API Server
- **RESTful API** with OpenAPI schema (auto-generated from Go types)
- **Request flow:** Authentication -> Authorization -> Admission (mutating -> validating) -> etcd
- **Watch cache:** In-memory cache of etcd state, serves watch requests without hitting etcd
- **API Priority and Fairness (APF):** Priority levels + flow schemas for request throttling
- **Aggregated API server:** Extend API server with custom API groups (e.g., metrics-server)
- **CRD (Custom Resource Definitions):** User-defined resources stored in etcd, reconciled by custom controllers
- **Encoding:** Internal types -> versioned types -> Protobuf/JSON for wire + storage

### Scheduler
- **Scheduling framework plugins:**
  - PreFilter / Filter (hard constraints): NodeResourcesFit, NodeAffinity, TaintToleration
  - PreScore / Score (soft preferences): NodeResourcesBalancedAllocation, InterPodAffinity, PodTopologySpread
  - Reserve / Permit / Bind: async binding, quota checks
- **Scheduling queue:** ActiveQ (ready to schedule), BackoffQ (retry), UnschedulableQ (waiting for cluster changes)
- **Preemption:** Find lower-priority pods to evict, simulate removal, check if pending pod fits
- **Throughput:** ~100 pods/sec default; adjustable via percentageOfNodesToScore (100 -> not all nodes evaluated)
- **Multi-scheduler:** Deploy custom scheduler alongside default; specify schedulerName in pod spec

### Kubelet
- **Pod lifecycle:**
  1. Watch API server for pods assigned to this node
  2. Create sandbox (pause container) via CRI
  3. Set up networking via CNI
  4. Mount volumes via CSI
  5. Start init containers (sequential), then main containers (parallel)
  6. Run probes: startup, liveness, readiness
  7. Report pod status back to API server
- **cAdvisor:** Embedded monitoring for container resource usage
- **Eviction manager:** Evict pods when node resources (memory, disk, PID) are under pressure
- **Node status:** Conditions (Ready, MemoryPressure, DiskPressure), capacity, allocatable
- **Static pods:** Managed by kubelet directly (no API server), used for control plane components

### CNI (Container Network Interface)
- **Spec:** Binary invoked by kubelet; ADD (create network), DEL (cleanup), CHECK (verify)
- **AWS VPC CNI:**
  - Assigns real VPC IPs to pods (secondary IPs on ENI)
  - Maximum pods = (ENIs per instance * IPs per ENI) - reserved
  - Prefix delegation: /28 prefix per ENI slot -> higher pod density
  - Security groups for pods: each pod can have its own SG
  - Custom networking: pods in different subnet than node
- **Calico:**
  - BGP routing: pods get routable IPs, no encapsulation overhead
  - VXLAN mode: overlay for environments that don't support BGP
  - NetworkPolicy enforcement via iptables/eBPF
- **Cilium:**
  - eBPF-based: bypass iptables entirely
  - L3/L4/L7 NetworkPolicy (HTTP-aware)
  - Service mesh features: mTLS, L7 load balancing without sidecar
  - Hubble: eBPF-powered observability

### CRI (Container Runtime Interface)
- **gRPC interface** between kubelet and container runtime
- **containerd:** Default in EKS, lightweight, OCI-compliant
- **CRI-O:** K8s-specific, minimal footprint
- **RuntimeClass:** Run different pods with different runtimes (runc for standard, gVisor/Kata for untrusted)
- **Image management:** Pull, verify, unpack, store images; lazy pulling (stargz, nydus) for faster startup

### CSI (Container Storage Interface)
- **Components:**
  - Controller (runs anywhere): CreateVolume, DeleteVolume, ControllerPublish (attach)
  - Node (runs on each node): NodeStage (format/mount to staging), NodePublish (bind mount to pod)
- **AWS EBS CSI:**
  - Dynamic provisioning: StorageClass -> PVC -> PV -> EBS volume
  - Topology-aware: provision in same AZ as node
  - Volume expansion, snapshots
- **AWS EFS CSI:**
  - Shared filesystem (NFS-based)
  - Access points for per-pod isolation
  - Cross-AZ access

---

# 6. Interview Frameworks & Execution Strategy

## 6.1 The RESHADED Framework

A structured approach for 45-minute system design interviews:

| Step | Time | Activity |
|------|------|----------|
| **R**equirements | 3-5 min | Functional requirements, non-functional requirements (scale, latency, consistency) |
| **E**stimation | 3-5 min | Back-of-envelope: QPS, storage, bandwidth |
| **S**torage schema | 3-5 min | Data model, database choices |
| **H**igh-level design | 5-8 min | Components, data flow, APIs |
| **A**PI design | 3-5 min | Key API endpoints, request/response formats |
| **D**etailed design | 12-15 min | Deep dive into 2-3 critical components |
| **E**valuation | 3-5 min | Trade-offs, failure modes, bottlenecks |
| **D**istinctive (Staff) | 5 min | Evolution, operational concerns, cost, alternatives |

## 6.2 Back-of-Envelope Estimation Cheat Sheet

### Latency Numbers (Approximate, 2024)
| Operation | Latency |
|-----------|---------|
| L1 cache reference | 0.5 ns |
| L2 cache reference | 7 ns |
| Mutex lock/unlock | 25 ns |
| Main memory reference | 100 ns |
| SSD random read | 16 us |
| Read 1 MB sequentially from SSD | 0.5 ms |
| Read 1 MB sequentially from memory | 0.25 ms |
| Disk seek (HDD) | 10 ms |
| Read 1 MB sequentially from HDD | 20 ms |
| Send packet CA -> Netherlands -> CA | 150 ms |
| Read 1 MB from network (1 Gbps) | 10 ms |

### Scale Numbers
| Metric | Approximate Value |
|--------|-------------------|
| Seconds per day | 86,400 (~100K) |
| Seconds per year | ~31.5 million (~32M) |
| 1 million requests per day | ~12 QPS |
| 100 million requests per day | ~1,200 QPS |
| 1 billion requests per day | ~12,000 QPS |
| 1 KB * 1 million = | 1 GB |
| 1 KB * 1 billion = | 1 TB |
| 1 MB * 1 million = | 1 TB |
| 1 MB * 1 billion = | 1 PB |

### Storage/Throughput Numbers
| Storage | Typical Throughput |
|---------|-------------------|
| MySQL (single node) | ~10K QPS (read), ~5K QPS (write) |
| Redis | ~100K QPS (single instance) |
| Cassandra (single node) | ~10K-50K QPS write |
| Kafka (single broker) | 100K-200K messages/sec |
| S3 | 3,500 PUT/sec, 5,500 GET/sec per prefix |

## 6.3 How to Discuss Trade-offs (Staff Level)

### The STAR-T Framework for Trade-offs
- **S**ituation: What constraint or requirement creates the trade-off?
- **T**rade-off: What are the options?
- **A**nalysis: Quantify the impact of each option
- **R**ecommendation: Which do you pick and why?
- **T**rigger: What would make you reconsider? (At what scale/requirement change does your choice become wrong?)

### Example (Chat System — Message Ordering):
- **Situation:** In a distributed chat system, messages arrive from multiple servers
- **Trade-off:** Server-assigned timestamps vs. Lamport clocks vs. client timestamps
- **Analysis:**
  - Server timestamps: simple, but clock skew across servers can reorder (up to ~1ms NTP drift)
  - Lamport clocks: causal ordering guaranteed, but total order is artificial for concurrent messages
  - Client timestamps: reflects user intent, but clients can lie or have wrong clocks
- **Recommendation:** Server-assigned per-conversation sequence numbers (monotonic, gap-free, authoritative)
- **Trigger:** If we go multi-region, a single sequence generator becomes a bottleneck. Then we'd move to per-region sequences with merge logic.

## 6.4 Common Mistakes in System Design Interviews

1. **Jumping to the solution** without clarifying requirements
2. **Not estimating scale** — your design for 1K users is different from 1B users
3. **Designing in silence** — always explain your thinking; the interview is about the thought process
4. **Only happy path** — what happens when things fail?
5. **Using buzzwords without understanding** — if you say "use Kafka," be prepared to explain WHY
6. **Single point of failure** — every component should be discussed for HA
7. **Ignoring data model** — the data model often drives the entire architecture
8. **Not discussing monitoring** — a system without observability is not production-ready
9. **Premature optimization** — start simple, then optimize identified bottlenecks
10. **Not managing time** — spending 20 minutes on requirements is a common trap

---

# 7. Recommended Study Plan & Resources

## 7.1 4-Week Study Plan (Intensive)

### Week 1: Foundations & Core Questions
- Day 1-2: Review distributed systems concepts (Section 5)
- Day 3-4: Practice URL Shortener, Rate Limiter, KV Store (warm-up problems)
- Day 5-6: Practice News Feed, Chat System (core Meta questions)
- Day 7: Review and refine approach

### Week 2: Company-Specific Focus
- Day 1-2: Meta questions (News Feed, Ad Aggregation, Cache, Notification)
- Day 3-4: Uber questions (Ride Matching, Location Tracking, Task Scheduler)
- Day 5-6: Microsoft questions (Object Storage, Load Balancer, KV Store)
- Day 7: AI company questions (Training Pipeline, Inference Serving, GPU Scheduler)

### Week 3: Infrastructure Deep Dives (Leverage Your EKS Expertise)
- Day 1-2: Container Orchestration, Control Plane design
- Day 3-4: Service Mesh, Load Balancer, Auto-scaling
- Day 5-6: Multi-tenant K8s Platform, Container Registry
- Day 7: Practice explaining K8s internals as a system design

### Week 4: Staff-Level Polish
- Day 1-2: Mock interviews with peers (focus on trade-offs and depth)
- Day 3-4: Practice driving the conversation, handling ambiguity
- Day 5-6: Review failure modes, operational concerns, cost analysis
- Day 7: Light review, rest before interviews

## 7.2 Key Resources

### Books
- "Designing Data-Intensive Applications" by Martin Kleppmann (foundational, must-read)
- "System Design Interview" Volumes 1 & 2 by Alex Xu (structured question walkthroughs)
- "Building Microservices" by Sam Newman (service boundaries, patterns)
- "Database Internals" by Alex Petrov (deep storage engine knowledge)
- "Understanding Distributed Systems" by Roberto Vitillo (concise distributed systems primer)

### Online Resources
- System Design Primer (GitHub - donnemartin/system-design-primer)
- DesignGurus.io (Grokking the System Design Interview — updated courses)
- ByteByteGo (Alex Xu's platform — visual system design explanations)
- MIT 6.824 Distributed Systems lectures (Raft paper, MapReduce, GFS, Spanner)
- Papers We Love: Dynamo, Spanner, Borg, Omega, Kafka, Raft, MapReduce, GFS papers

### Kubernetes-Specific
- "Kubernetes in Action" by Marko Luksa (comprehensive)
- Kubernetes source code (k8s.io/kubernetes — scheduler, controller-manager)
- Kubernetes Enhancement Proposals (KEPs) — understand design decisions
- EKS Best Practices Guide (aws.github.io/aws-eks-best-practices)
- Karpenter documentation and design docs

### Mock Interview Platforms
- Pramp (free peer mock interviews)
- Interviewing.io (paid, anonymous with industry engineers)
- Exponent (structured system design practice)
- IGotAnOffer (Meta-specific coaching)

## 7.3 Your Competitive Advantages (EKS Background)

1. **Control Plane Expertise:** You understand how to build reliable, highly available control planes — this applies to ANY system design
2. **Distributed Systems Intuition:** etcd, Raft, reconciliation loops, leader election — you use these daily
3. **Scale Thinking:** EKS manages thousands of clusters; you understand multi-tenant, multi-region systems
4. **Infrastructure-as-Code Mindset:** Declarative desired state, eventually consistent reconciliation
5. **Operational Maturity:** You know what it takes to run systems at 99.95%+ availability
6. **Go + Python:** Go for systems code (controllers, operators, high-performance services), Python for tooling, automation, ML pipelines

### How to Weave EKS Experience Into Answers

**When asked "Design X":**
1. Mention relevant K8s patterns: "This is similar to how the K8s scheduler handles bin-packing — we'd use a two-phase approach with filtering and scoring"
2. Reference real problems: "In EKS, we handle this by... which is analogous to this design"
3. Show depth: "One subtle issue with this approach is thundering herd on leader failover — we solved this in etcd by..."
4. Demonstrate leadership: "When we designed this for EKS, I advocated for approach X because..." (behavioral + technical)

---

# Appendix A: Quick Reference — Design Patterns for Distributed Systems

| Pattern | Use Case | Examples |
|---------|----------|---------|
| Sidecar | Add functionality to existing service without modification | Envoy proxy, log collectors |
| Ambassador | Proxy for outbound connections | Circuit breaker, retry logic |
| Scatter-Gather | Fan-out request, aggregate responses | Search across shards |
| Saga | Distributed transactions without 2PC | Order -> Payment -> Inventory |
| Outbox | Reliable event publishing with DB writes | Write to DB + outbox table, CDC to Kafka |
| Strangler Fig | Incremental migration from monolith to microservices | Route by path to old/new service |
| Bulkhead | Isolate failures to prevent cascading | Separate thread pools per dependency |
| Singleflight | Deduplicate concurrent identical requests | Cache miss thundering herd prevention |
| Circuit Breaker | Stop calling failing dependency | Hystrix, Envoy outlier detection |
| Retry + Backoff + Jitter | Handle transient failures | Exponential backoff with full jitter |
| Leader Election | Single writer, multiple readers | etcd Lease, ZooKeeper ephemeral nodes |
| Write-Ahead Log | Durability before commit | etcd WAL, Kafka segments |
| LSM Tree | Write-optimized storage | RocksDB, Cassandra, LevelDB |
| B-Tree | Read-optimized, range-query friendly storage | MySQL InnoDB, PostgreSQL |
| Bloom Filter | Probabilistic set membership (no false negatives) | Reduce unnecessary disk reads in LSM |
| Merkle Tree | Efficient data synchronization | Anti-entropy in Dynamo/Cassandra |
| Consistent Hashing | Distribute data with minimal reshuffling | Cassandra, DynamoDB, cache clusters |
| Vector Clock | Causal ordering + conflict detection | Dynamo, Riak |
| CRDT | Conflict-free replicated data types | Counters, sets, registers for multi-region |
| Gossip Protocol | Decentralized state dissemination | Membership, failure detection (Cassandra) |

---

# Appendix B: Go & Python Patterns for System Design Discussions

## Go Patterns (Infrastructure / K8s)

```go
// Singleflight — prevent thundering herd on cache miss
import "golang.org/x/sync/singleflight"
var g singleflight.Group
val, err, shared := g.Do(key, func() (interface{}, error) {
    return fetchFromDB(key)
})

// Context-based cancellation and timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
result, err := service.Call(ctx, request)

// Worker pool pattern
func workerPool(jobs <-chan Job, results chan<- Result, workers int) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    wg.Wait()
    close(results)
}

// Rate limiter using golang.org/x/time/rate (token bucket)
limiter := rate.NewLimiter(rate.Limit(100), 10) // 100/sec, burst 10
if err := limiter.Wait(ctx); err != nil {
    return err // context cancelled or deadline exceeded
}

// K8s controller pattern (simplified)
func (c *Controller) Run(ctx context.Context) {
    for {
        key, shutdown := c.queue.Get()
        if shutdown { return }
        if err := c.reconcile(ctx, key.(string)); err != nil {
            c.queue.AddRateLimited(key) // retry with backoff
        } else {
            c.queue.Forget(key)
        }
        c.queue.Done(key)
    }
}
```

## Python Patterns (ML / Tooling)

```python
# Async HTTP server with rate limiting (FastAPI)
from fastapi import FastAPI, HTTPException
from asyncio import Semaphore

app = FastAPI()
semaphore = Semaphore(100)  # max 100 concurrent requests

@app.post("/inference")
async def inference(request: InferenceRequest):
    async with semaphore:
        result = await model.predict(request.input)
        return {"result": result}

# Circuit breaker pattern
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=30):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = "CLOSED"
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError()
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise

# Distributed task with Celery (task scheduler pattern)
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379')

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_training_job(self, job_id):
    try:
        model = load_model(job_id)
        model.train()
        save_checkpoint(model, job_id)
    except TransientError as e:
        self.retry(exc=e)
```

---

# Appendix C: 30-Second Elevator Pitches for Each Design

Use these to quickly frame your answer at the start of each interview.

1. **URL Shortener:** "Write-once, read-many key-value mapping. The interesting parts are ID generation strategy, caching for hot URLs, and analytics pipeline."

2. **News Feed:** "The core challenge is fan-out strategy — write for normal users, read for celebrities, hybrid at scale. Ranking adds ML complexity."

3. **Chat System:** "Long-lived WebSocket connections, per-conversation ordering, presence tracking, and push notifications for offline users."

4. **Rate Limiter:** "Token bucket in Redis with Lua for atomicity. The interesting part is multi-tier rate limiting and the accuracy-latency trade-off in distributed settings."

5. **Ride Matching:** "Geospatial indexing (H3/S2 cells) for efficient proximity queries, real-time matching optimization, and dynamic pricing based on supply/demand per geo-cell."

6. **Container Orchestration:** "Declarative desired-state in etcd, reconciliation controllers, a pluggable scheduler with filter/score phases, and a node agent managing container lifecycle via CRI/CNI/CSI."

---

*Last updated: February 2026*
*Tailored for senior/staff engineer with AWS EKS Dataplane/Controlplane expertise*
