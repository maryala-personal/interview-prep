# Design an Object Storage System (S3)

> **Companies**: Amazon, Google, Microsoft, Dropbox, Snowflake | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Erasure coding vs replication trade-offs, consistent hashing for data placement, metadata vs data plane separation, multi-tenancy at exabyte scale, how you handle partial failures during writes

---

## The First 5 Minutes — Scoping & Technical Clarifications

These are the questions that signal you understand distributed storage, not just "what features does S3 have":

1. **What's the durability target?** S3 promises 11 nines (99.999999999%). That drives the entire replication/coding strategy. Are we targeting that or something lower?
2. **Object size distribution?** Small objects (<1 MB) dominate by count but large objects (>100 MB) dominate by bytes. Do we optimize for one or both? This changes the write path completely.
3. **Read/write ratio and access pattern?** Most object stores are write-once-read-many. Are we dealing with hot/warm/cold tiering?
4. **Consistency model?** S3 went from eventual to strong read-after-write consistency in Dec 2020. Are we designing for strong consistency?
5. **Multi-tenancy requirements?** How many tenants, per-tenant QPS limits, namespace isolation?
6. **Single vs multi-region?** Cross-region replication or single-region with AZ redundancy?
7. **Maximum object size?** S3 supports 5 TB with multipart upload. What's our limit?
8. **Versioning and lifecycle?** Do we need object versioning, TTL-based expiry, storage class transitions?

### Working Assumptions

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Total storage | 100 PB | Starting scale, growing ~30%/year |
| Object count | 10 billion | Avg object size ~10 KB median, but long tail |
| Write QPS | 50,000 | ~4.3B writes/day |
| Read QPS | 500,000 | 10:1 read:write ratio |
| Durability target | 99.999999999% (11 nines) | Industry standard |
| Availability target | 99.99% (4 nines) | ~52 min downtime/year |
| p99 read latency | <100 ms (first byte) | For hot tier objects |
| Metadata size per object | ~1 KB | Key, size, checksum, ACL, custom metadata |
| Metadata total | 10 TB | 10B objects x 1 KB |

**Bandwidth math**: 500K reads/sec x 100 KB avg read size = 50 GB/s read throughput. At 10 Gbps per storage node, that's minimum 40 nodes just for read bandwidth — before replication overhead.

---

## High-Level Design

```
                           ┌─────────────────┐
                           │   API Gateway    │
                           │  (REST/HTTP)     │
                           └────────┬─────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              ┌─────▼──────┐ ┌─────▼──────┐ ┌──────▼─────┐
              │ Auth/IAM   │ │  Metadata  │ │  Data      │
              │ Service    │ │  Service   │ │  Routing   │
              └────────────┘ └─────┬──────┘ └──────┬─────┘
                                   │               │
                            ┌──────▼──────┐  ┌─────▼──────────┐
                            │  Metadata   │  │  Placement     │
                            │  Store      │  │  Service       │
                            │ (sharded DB)│  │ (consistent    │
                            └─────────────┘  │  hashing)      │
                                             └─────┬──────────┘
                                                   │
                    ┌──────────────┬────────────────┼────────────────┐
                    │              │                │                │
              ┌─────▼────┐  ┌─────▼────┐    ┌──────▼───┐    ┌──────▼───┐
              │ Storage  │  │ Storage  │    │ Storage  │    │ Storage  │
              │ Node 1   │  │ Node 2   │    │ Node 3   │    │ Node N   │
              │(data +   │  │(data +   │    │(data +   │    │(data +   │
              │ erasure)  │  │ erasure) │    │ erasure) │    │ erasure) │
              └──────────┘  └──────────┘    └──────────┘    └──────────┘
```

**Why this architecture?** Separating the metadata plane from the data plane is the foundational decision. Metadata operations (list, head, ACL checks) are small and frequent; data operations are large and throughput-bound. Coupling them means metadata latency degrades under heavy data transfer. S3 made this split, and it's why they could add strong consistency to metadata without re-architecting the data path.

---

## Core Concepts Deep Dive

### Concept 1: Erasure Coding vs Replication

**What it is**: Erasure coding splits data into k data chunks and generates m parity chunks (Reed-Solomon coding). Any k of the k+m chunks can reconstruct the original data. Compare to 3x replication which stores 3 full copies.

**How it applies**: For 11 nines durability with 3x replication, you need 3x storage overhead. With RS(10,4) erasure coding, you get the same durability with only 1.4x overhead. At 100 PB scale, that's 160 PB difference — millions of dollars in hardware.

**The math**: For RS(10,4), any 10 of 14 chunks recover data. Probability of losing more than 4 chunks simultaneously (assuming independent 1% annual disk failure rate): C(14,5) x (0.01)^5 x (0.99)^9 ~ 2 x 10^-9 per object per year. With scrubbing and repair, effective durability exceeds 11 nines.

**Common misconception**: "Just use 3x replication, it's simpler." At small scale, yes. But erasure coding isn't just about storage savings — it also provides better read throughput because you can read from any k of k+m nodes in parallel, hedging against slow nodes.

### Concept 2: Consistent Hashing for Data Placement

**What it is**: Maps objects to storage nodes using a hash ring with virtual nodes. Each physical node owns multiple positions on the ring. When a node joins/leaves, only 1/N of keys need to move (where N is total nodes).

**How it applies**: The placement service determines which storage nodes hold chunks for a given object. Virtual nodes ensure even distribution — a 100-node cluster might use 15,000 virtual nodes (150 per physical), so each physical node owns ~150 positions.

**The math**: With random placement and N nodes, standard deviation of load is O(sqrt(K/N)) where K is total objects. With virtual nodes (V per physical node), it improves to O(sqrt(K/(NV))). Typically V=100-200 gives <5% load imbalance.

**Common misconception**: Candidates think consistent hashing alone handles rebalancing. In practice, you need a placement policy layer on top — considering rack awareness (don't put two chunks in the same rack), disk utilization, and node capacity heterogeneity.

### Concept 3: Metadata Store Design — The Hard Part

**What it is**: Every object operation hits metadata first. The metadata store must handle 550K QPS (reads + writes combined), support prefix listing, and provide strong consistency for read-after-write semantics.

**How it applies**: S3 initially used a coordination-free design with eventual consistency. In 2020, they switched to a strongly consistent metadata layer. The trick: they built a per-prefix serialization layer that doesn't require global consensus for every write.

**The math**: 10 billion objects x 1 KB metadata = 10 TB metadata. Partitioned by bucket + key prefix across ~100 metadata shards, each shard holds ~100 GB — easily fits in memory for fast reads. At 550K QPS across 100 shards = 5,500 QPS per shard, well within single-node DB capacity.

**Common misconception**: "Use a single DynamoDB/Cassandra cluster for metadata." This misses that LIST operations require range scans over key prefixes. You need a store that supports both point lookups (GET object metadata) and range scans (LIST prefix) efficiently — a B-tree based store or partitioned SQL database outperforms a hash-partitioned KV store here.

### Concept 4: Multipart Upload Protocol

**What it is**: For large objects (>100 MB), the client splits the file into parts, uploads each independently (possibly in parallel), then issues a complete request that assembles them server-side.

**How it applies**: Each part is stored as an independent object with its own erasure coding. The complete operation is a metadata-only operation that creates a manifest pointing to parts. This means a 5 TB upload doesn't need 5 TB of contiguous storage — parts can be spread across the cluster.

**The math**: With 100 MB parts and 10 Gbps client bandwidth, a 5 TB upload takes ~400 seconds (6.7 min) with 10 parallel streams. Without multipart (single stream), it would take ~4000 seconds (67 min) and a single network hiccup means restarting the entire upload.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Write Path & Durability

**Interviewer**: "Walk me through what happens when a client uploads a 500 MB object end-to-end."

**You**: The client calls `PUT /bucket/key` with the object body. The API gateway authenticates via IAM, then contacts the metadata service to check bucket existence and ACLs. Since 500 MB exceeds the single-PUT threshold (typically 100 MB), the client library actually initiates a multipart upload: `POST /bucket/key?uploads` returns an upload ID. The client splits into 5 x 100 MB parts and uploads each with `PUT /bucket/key?partNumber=N&uploadId=X`. For each part, the data routing layer asks the placement service for target nodes using consistent hashing on `(bucket, key, part_number)`. The data is erasure coded into 10 data + 4 parity chunks, streamed to 14 storage nodes. Each node acknowledges after fsyncing to disk. The routing layer waits for at least 10+1 acks before returning success to the client (we need at least k+1 to guarantee durability even if one ack was false). After all parts succeed, the client calls `POST /bucket/key?uploadId=X` with the part manifest. The metadata service atomically creates the object record pointing to all parts.

**Interviewer**: "What if a storage node fails mid-write? Say chunk 7 of 14 never gets acknowledged."

**You**: The write path has a timeout — say 30 seconds. If chunk 7's node doesn't ack, we have two options depending on our erasure coding parameters. With RS(10,4), we can tolerate 4 missing chunks. So we proceed with 13/14 successful writes — still above the k=10 threshold. We mark the object as "degraded" in metadata and enqueue a background repair task that will re-encode the missing chunk and place it on a healthy node. If more than 4 nodes fail simultaneously during a single write, we return 503 to the client and they retry. The key insight: we never ack a write to the client until we have enough chunks to guarantee reconstruction.

**Interviewer**: "How does the background repair process work? What prevents it from falling behind?"

**You**: Each storage node runs a scrubber daemon that periodically (every ~2 weeks for cold data, daily for hot) reads each chunk, verifies its checksum, and reports health to a repair coordinator. The coordinator maintains a priority queue: recently degraded objects repair first, cold data on a slower schedule. For repair, the coordinator reads k healthy chunks from available nodes, reconstructs the missing chunk via Reed-Solomon decoding, and writes it to a new healthy node. The math on keeping up: with 1% annual disk failure rate and 100 PB across 10,000 disks (10 TB each), we expect 100 disk failures per year, or about 2 per week. Each failed disk holds ~10 TB, and with 10 Gbps network per node, repair takes ~8,000 seconds (~2.2 hours) per disk. So we're repairing one disk's worth of data while the next failure is statistically ~3.5 days away — plenty of margin.

**Interviewer**: "What about the durability math during the repair window? That's when you're most vulnerable."

**You**: Exactly — the "repair window" is the critical period. During repair of a failed node, objects that had chunks on that node are at k+m-1 redundancy instead of k+m. For RS(10,4), we go from tolerating 4 failures to 3. The probability of a second simultaneous failure during a 2.2-hour repair window is (99 remaining disks x 0.01/365/24 x 2.2) ~ 0.00025, or about 0.025%. The probability of losing data (4 additional failures during repair) is astronomically small: ~10^-15. This is how we achieve 11 nines. The key engineering decision: prioritize repair of objects with the fewest remaining healthy chunks. An object missing 2 chunks repairs before an object missing 1.

### Deep Dive Path 2: Consistent Metadata & Strong Read-After-Write

**Interviewer**: "How do you provide strong read-after-write consistency? If I PUT an object and immediately GET it, I should always see the new version."

**You**: The metadata service is the linearization point. Every PUT must commit to the metadata store before returning 200 to the client. Every GET reads from the metadata store to find chunk locations. If metadata is a single leader (or uses consensus per partition), and the PUT's commit happens-before the GET's read in real time, the GET will see the new version. The tricky part is LIST operations — S3 had to ensure that a newly PUT object appears in subsequent LIST results, which means LIST must read from the leader (or a follower that's caught up to the PUT's log position).

**Interviewer**: "But with a sharded metadata store, how do you handle cross-shard consistency for LIST that spans multiple shards?"

**You**: Great question — this is what made S3's consistency upgrade so hard. LIST results are sorted lexicographically by key, and a single LIST call might span multiple metadata shards. The approach: each shard maintains a monotonically increasing logical timestamp. When a PUT commits on shard A at timestamp T_A, the LIST coordinator reads from all relevant shards and waits until each shard has advanced past any in-flight writes it knows about. In practice, S3 built a witness/sequencer service that serializes PUTs per key prefix and ensures LIST operations read a consistent snapshot. They described this in their 2021 paper: the metadata uses a per-key-prefix chain of log entries, and LIST walks the chain.

**Interviewer**: "What about conditional writes — like only write if the object doesn't exist?"

**You**: S3 added conditional writes (If-None-Match) in 2024. The implementation uses the per-key serialization in the metadata store: the PUT acquires a lock (or uses optimistic concurrency with version check) on the key, reads current state, checks the condition, and commits or rejects atomically. At the metadata shard level, this is a compare-and-swap operation. The important design choice is lock granularity — per-key locking is fine because keys are independent. You'd never want per-bucket locking since a hot bucket could see millions of concurrent PUTs.

**Interviewer**: "How would you handle the thundering herd problem on a popular object?"

**You**: For reads, a caching layer in front of storage nodes handles this. The first request fetches from storage, populates a CDN or local cache, and subsequent requests serve from cache. For metadata, popular objects can overwhelm a single metadata shard. The solution is read replicas — metadata writes go to the leader, but reads can go to followers with a "read your own writes" guarantee (the client includes the write timestamp and the follower ensures it's caught up). If a single key gets extreme read traffic (say a viral image), the metadata for that key can be replicated to a dedicated cache tier.

### Deep Dive Path 3: Multi-Tenancy & Throttling at Scale

**Interviewer**: "You have 10,000 tenants sharing this system. How do you prevent one tenant from impacting others?"

**You**: Multi-tenancy isolation has three layers: (1) Request admission control — each tenant has a per-second request budget enforced at the API gateway using token bucket rate limiting. (2) Bandwidth throttling — each tenant gets a bandwidth allocation enforced at the data routing layer. (3) Metadata isolation — tenants' metadata is partitioned by bucket ID, so a tenant doing heavy LIST operations only loads their own shards. The API gateway maintains per-tenant counters in a distributed rate limiter (similar to the rate limiter design) using sliding window counters in Redis. If a tenant exceeds their budget, we return 429 (SlowDown) with a Retry-After header.

**Interviewer**: "What about noisy neighbor at the storage node level? Rate limiting at the gateway doesn't prevent hot partitions."

**You**: Right — gateway rate limiting prevents abuse but doesn't prevent hot spots. At the storage node level, we use fair queuing: each node maintains per-tenant request queues with weighted fair scheduling. A node serving chunks for 50 tenants gives each tenant a proportional share of IOPS and bandwidth. If tenant A is doing 10x more reads than tenant B, but both have equal quotas, tenant A's excess requests queue up while tenant B's get immediate service. Additionally, the placement service actively monitors per-node utilization and can migrate hot objects' chunks to less loaded nodes. The nuclear option for extremely hot objects is to promote them to a dedicated cache tier — essentially a CDN within the storage system.

**Interviewer**: "How do you handle the billing and metering for this? You need exact byte counts."

**You**: Metering is a streaming aggregation problem. Every API gateway emits a usage event (tenant, operation, bytes, timestamp) to a Kafka topic. A Flink job aggregates by tenant per minute into a metering database. For billing accuracy, we need exactly-once semantics — Kafka + Flink with idempotent writes to the metering DB achieves this. We cross-validate by comparing gateway-side metrics with storage-node-side metrics. The metering DB is partitioned by tenant ID and optimized for time-range queries (for monthly billing). Storage usage (GB-hours) is calculated from periodic snapshots of the metadata store — a nightly job walks all metadata shards and sums per-tenant storage.

---

## How Real Companies Built This

- **Amazon S3**: The original. Separates metadata (index) from data plane. Uses erasure coding for durability. Added strong consistency in Dec 2020 via a new metadata caching layer. [AWS re:Invent 2021 — S3 Strong Consistency](https://www.youtube.com/watch?v=MEgWAENFpPc)
- **MinIO**: Open-source S3-compatible. Uses Reed-Solomon erasure coding with configurable parity. Written in Go. [MinIO Erasure Coding Docs](https://min.io/docs/minio/linux/operations/concepts/erasure-coding.html)
- **Facebook f4**: Warm blob storage that replaced Haystack for older photos. Uses Reed-Solomon (10,4) coding. Reduced replication factor from 3.6x to 1.4x, saving petabytes. [Facebook f4 Paper — OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/muralidhar)
- **Azure Blob Storage**: Uses Local Reconstruction Codes (LRC) for erasure coding — a variant of Reed-Solomon that allows local repair from fewer chunks for single failures. [Azure Storage — USENIX ATC 2012](https://www.usenix.org/conference/atc12/technical-sessions/presentation/huang)
- **Ceph RADOS**: Open-source distributed storage using CRUSH algorithm (a variant of consistent hashing with hierarchical failure domains). [Ceph CRUSH Paper — SC 2006](https://ceph.io/assets/pdfs/weil-crush-sc06.pdf)

---

## The Complete Reference Design

### API Design

```
PUT    /v1/{bucket}/{key}              # Upload object
PUT    /v1/{bucket}/{key}?partNumber=N&uploadId=X  # Upload part
POST   /v1/{bucket}/{key}?uploads      # Initiate multipart upload
POST   /v1/{bucket}/{key}?uploadId=X   # Complete multipart upload
GET    /v1/{bucket}/{key}              # Download object
GET    /v1/{bucket}/{key}?versions     # List object versions
HEAD   /v1/{bucket}/{key}              # Get object metadata
DELETE /v1/{bucket}/{key}              # Delete object
GET    /v1/{bucket}?prefix=P&marker=M&max-keys=1000  # List objects

# Headers:
# Authorization: AWS4-HMAC-SHA256 Credential=...
# Content-MD5: base64-encoded MD5 for integrity
# If-None-Match: * (conditional write)
# x-amz-storage-class: STANDARD | INFREQUENT | GLACIER

# Response (PUT):  200 OK
# ETag: "d41d8cd98f00b204e9800998ecf8427e"
# x-amz-version-id: v1_abc123
```

### Database Schema (Metadata Store)

```sql
-- Partitioned by bucket_id hash across ~100 shards
CREATE TABLE object_metadata (
    bucket_id     BIGINT NOT NULL,
    object_key    VARCHAR(1024) NOT NULL,
    version_id    BIGINT NOT NULL DEFAULT 0,
    size_bytes    BIGINT NOT NULL,
    etag          CHAR(32) NOT NULL,
    content_type  VARCHAR(256),
    storage_class SMALLINT DEFAULT 0,        -- 0=standard, 1=IA, 2=glacier
    is_deleted    BOOLEAN DEFAULT FALSE,     -- versioned delete markers
    created_at    TIMESTAMP NOT NULL,
    acl_json      JSONB,
    user_metadata JSONB,                     -- custom x-amz-meta-* headers
    chunk_manifest JSONB NOT NULL,           -- [{chunk_id, node_id, offset}]
    PRIMARY KEY (bucket_id, object_key, version_id)
) PARTITION BY HASH (bucket_id);

CREATE INDEX idx_list ON object_metadata (bucket_id, object_key);
CREATE INDEX idx_lifecycle ON object_metadata (storage_class, created_at)
    WHERE is_deleted = FALSE;

CREATE TABLE multipart_uploads (
    upload_id    UUID PRIMARY KEY,
    bucket_id    BIGINT NOT NULL,
    object_key   VARCHAR(1024) NOT NULL,
    initiated_at TIMESTAMP NOT NULL,
    status       SMALLINT DEFAULT 0  -- 0=in_progress, 1=completed, 2=aborted
);

CREATE TABLE upload_parts (
    upload_id    UUID NOT NULL REFERENCES multipart_uploads(upload_id),
    part_number  INT NOT NULL,
    size_bytes   BIGINT NOT NULL,
    etag         CHAR(32) NOT NULL,
    chunk_manifest JSONB NOT NULL,
    PRIMARY KEY (upload_id, part_number)
);
```

### Key Algorithms — Placement with Consistent Hashing

```python
import hashlib
from bisect import bisect_right
from typing import List, Tuple

class PlacementService:
    def __init__(self, virtual_nodes_per_physical: int = 150):
        self.ring: List[Tuple[int, str]] = []
        self.vnodes = virtual_nodes_per_physical
        self.node_rack: dict[str, str] = {}

    def add_node(self, node_id: str, rack_id: str):
        self.node_rack[node_id] = rack_id
        for i in range(self.vnodes):
            h = self._hash(f"{node_id}:{i}")
            self.ring.append((h, node_id))
        self.ring.sort()

    def get_placement(self, object_key: str, num_chunks: int = 14) -> List[str]:
        """Return num_chunks distinct nodes across distinct racks."""
        h = self._hash(object_key)
        idx = bisect_right(self.ring, (h,)) % len(self.ring)
        selected_nodes, selected_racks = [], set()
        visited = 0
        while len(selected_nodes) < num_chunks and visited < len(self.ring):
            _, node_id = self.ring[(idx + visited) % len(self.ring)]
            rack = self.node_rack[node_id]
            if node_id not in selected_nodes:
                rack_count = sum(1 for n in selected_nodes
                                 if self.node_rack[n] == rack)
                if rack_count < (num_chunks // 3 + 1):
                    selected_nodes.append(node_id)
                    selected_racks.add(rack)
            visited += 1
        return selected_nodes

    def _hash(self, key: str) -> int:
        return int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2**32)
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Storage nodes | 100 PB x 1.4 (erasure) / 10 TB per node | 14,000 disks (~1,400 nodes) |
| Metadata DB | 10B objects x 1 KB = 10 TB | 100 shards x 100 GB, 3 replicas = 30 TB |
| Network (read) | 500K QPS x 100 KB avg = 50 GB/s | 400 x 10 Gbps links |
| Network (write) | 50K QPS x 100 KB x 1.4 = 7 GB/s | 56 x 10 Gbps links |
| API gateways | 550K total QPS / 50K per gateway | 11 gateways (20 with headroom) |
| Repair bandwidth | 2 disk failures/week x 10 TB / 2.2 hrs | ~10 Gbps dedicated repair bandwidth |

---

## Senior vs Staff vs Principal

| Aspect | Senior (E5/L5) | Staff (E6/L6) | Principal (L66+) |
|--------|----------------|----------------|-------------------|
| **Architecture** | Clean metadata/data separation, correct erasure coding choice | Designs placement algorithm with rack/AZ awareness, explains repair math | Designs the consistency protocol for metadata, reasons about durability during correlated failures |
| **Scale** | Handles capacity math correctly | Designs multi-tier storage (hot/warm/cold) with automatic lifecycle | Designs cross-region replication with conflict resolution, reasons about CAP implications |
| **Trade-offs** | Knows erasure coding saves storage vs replication | Quantifies repair window risk, explains when replication beats EC (small objects, latency-sensitive) | Designs adaptive coding schemes — different EC parameters based on object age and access pattern |
| **Operations** | Mentions monitoring and alerting | Designs repair scheduler, explains node drain for maintenance | Designs capacity planning system, multi-tenant resource isolation, SLA enforcement |

---

## Red Flags & Common Mistakes

1. **"Just use 3x replication"** — Shows no understanding of storage economics at scale. 3x vs 1.4x at 100 PB = $2M+/year difference.
2. **Ignoring the metadata problem** — Spending 40 minutes on data placement and 0 on metadata. Metadata is the bottleneck and the consistency challenge.
3. **No durability math** — If you can't calculate the probability of data loss under your design, you can't defend your durability claims.
4. **Treating all objects the same** — A 1 KB object and a 5 TB object have fundamentally different write paths. Not discussing multipart upload is a miss.
5. **No failure handling in the write path** — "Write to 14 nodes and return success." What if 3 of them fail? When do you ack to the client?
6. **Conflating availability and durability** — Durability means data isn't lost. Availability means you can access it now. An object can be durable but temporarily unavailable.
7. **No mention of checksums** — Data integrity (bit rot detection) via per-chunk checksums and periodic scrubbing is fundamental to any storage system.
