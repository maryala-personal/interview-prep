# Design a Distributed File System (GFS/HDFS)

> **Companies**: Google, Meta, Amazon, Microsoft, Snowflake, Databricks, Cloudera | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Single-master metadata design and its limits, chunk replication vs erasure coding, write semantics (append-only vs random write), how to handle master failure, understanding of the GFS/HDFS lineage and why those design choices were made

---

## The First 5 Minutes — Scoping & Technical Clarifications

1. **Workload pattern?** Large sequential reads/writes (analytics, log processing) or small random I/O (database-like)? GFS/HDFS were designed for the former — this drives the 64-128 MB chunk size.
2. **Write model?** Append-only (GFS, HDFS) or random overwrites? Append-only drastically simplifies consistency and concurrency.
3. **File size distribution?** GFS was designed for files in the GB-TB range. Small files (<1 MB) are an anti-pattern — each file consumes metadata regardless of size.
4. **Consistency model?** GFS had relaxed consistency (defined but not necessarily consistent for concurrent appends). HDFS has write-once-read-many with strong consistency. Which do we need?
5. **Throughput vs latency?** GFS optimized for throughput (MB/s) not latency (IOPS). Are we designing for MapReduce-style batch processing or interactive queries?
6. **Scale targets?** Number of files, total storage, concurrent readers/writers?
7. **Fault tolerance?** What happens when a chunkserver dies? When the master dies? Replication factor?
8. **POSIX compliance?** Full POSIX (hard — especially locking and random writes) or relaxed API (easier, GFS approach)?

### Working Assumptions

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Total storage | 10 PB | Large analytics cluster |
| File count | 100 million | Mix of large and medium files |
| Average file size | 100 MB | Long tail from 1 MB to 100 GB |
| Chunk size | 64 MB | GFS default, balances metadata overhead vs read granularity |
| Total chunks | 160 million | 10 PB / 64 MB |
| Replication factor | 3 | GFS/HDFS default |
| Metadata per chunk | ~100 bytes | chunk_id, file_id, version, locations (3 replicas) |
| Total metadata | ~16 GB | 160M chunks x 100 bytes |
| Read throughput target | 100 GB/s aggregate | 1000 concurrent MapReduce readers |
| Write throughput target | 10 GB/s aggregate | 100 concurrent writers |
| Chunkservers | 1,000 | 10 PB x 3 (replication) / 30 TB per server |

**Metadata math**: 16 GB of metadata fits in a single master's RAM — this is why GFS/HDFS use a single-master design. The master never touches data (chunks), only metadata. At 100M files and 160M chunks, the master handles ~100K metadata operations/sec (list, open, create). This is the scalability bottleneck.

---

## High-Level Design

```
                    ┌──────────────────────────────┐
                    │         MASTER NODE           │
                    │  (single leader, hot standby) │
                    │                               │
                    │  ┌─────────────────────────┐  │
                    │  │ Namespace (file tree)    │  │
                    │  │ - /user/data/file1.csv  │  │
                    │  │ - /logs/2024/01/app.log │  │
                    │  └─────────────────────────┘  │
                    │  ┌─────────────────────────┐  │
                    │  │ Chunk Table (in-memory)  │  │
                    │  │ chunk_id -> [CS1,CS2,CS3]│  │
                    │  └─────────────────────────┘  │
                    │  ┌─────────────────────────┐  │
                    │  │ Operation Log (on-disk)  │  │
                    │  │ WAL for namespace changes│  │
                    │  └─────────────────────────┘  │
                    └──────────────┬───────────────┘
                                   │
            Metadata ops           │          Heartbeats + chunk reports
         (open, create, delete)    │         (every 10 sec from each CS)
                                   │
    ┌──────────────┬───────────────┼───────────────┬──────────────┐
    │              │               │               │              │
┌───▼────┐   ┌────▼───┐    ┌──────▼───┐    ┌──────▼───┐   ┌─────▼────┐
│ Chunk  │   │ Chunk  │    │ Chunk    │    │ Chunk    │   │ Chunk    │
│Server 1│   │Server 2│    │Server 3  │    │Server 4  │   │Server N  │
│ 30 TB  │   │ 30 TB  │    │ 30 TB   │    │ 30 TB   │   │ 30 TB   │
│ [chunks│   │ [chunks│    │ [chunks  │    │ [chunks  │   │ [chunks  │
│  as    │   │  as    │    │  as      │    │  as      │   │  as      │
│  files]│   │  files]│    │  files]  │    │  files]  │   │  files]  │
└────────┘   └────────┘    └──────────┘    └──────────┘   └──────────┘
      ▲            ▲             ▲               ▲              ▲
      │            │             │               │              │
      └────────────┴─────────────┴───────────────┴──────────────┘
                     DATA flows directly between
                     client and chunkservers
                     (master is NOT in the data path)
```

**Why this architecture?** The single-master design is the core insight from the GFS paper. By keeping ALL metadata in one node's RAM, metadata operations are extremely fast (microseconds) and consistent (no distributed consensus needed for metadata). The master never handles data — clients read/write directly to chunkservers. This separation means the master handles 100K+ metadata ops/sec while chunkservers handle 100 GB/s of data throughput independently. The risk is single-point-of-failure, mitigated by WAL + standby replicas.

---

## Core Concepts Deep Dive

### Concept 1: The Single-Master Design — Radical Simplicity

**What it is**: One master node holds all metadata in RAM: the file namespace (directory tree), the mapping of files to chunks, and the mapping of chunks to chunkservers. The master persists namespace changes to a Write-Ahead Log (WAL) on disk and periodically checkpoints the full state.

**How it applies**: The master does NOT store chunk locations persistently. On startup, it polls all chunkservers ("what chunks do you have?"). Chunkservers report their chunk lists via heartbeats every 10 seconds. This design means chunk location is soft state — if a chunkserver joins or dies, the master learns via heartbeats, not database writes.

**The math**: 160M chunks x 100 bytes = 16 GB metadata in RAM. Modern servers have 256-512 GB RAM — plenty. The master handles ~100K metadata ops/sec (Google's production GFS numbers). WAL writes at 100K ops/sec x 100 bytes = 10 MB/s — trivially handled by an SSD.

**Common misconception**: "Single master is a bottleneck." For metadata-heavy workloads (small files, frequent opens), yes — the master is the scalability limit. But GFS was designed for large files with sequential access. A MapReduce job opens a file once, then reads chunks for hours. The metadata:data ratio is tiny. For workloads with millions of small files, HDFS added federation (multiple NameNodes, each owning a namespace partition).

### Concept 2: Chunk Replication — Write Pipeline

**What it is**: When a client writes to a chunk, the data flows through a replication pipeline. GFS uses a chain replication topology: client -> primary chunkserver -> secondary 1 -> secondary 2. The primary assigns a sequence number to the write (for ordering), and all replicas apply writes in the same order.

**How it applies**: The write flow: (1) Client asks master for chunk locations. Master returns primary + secondaries. (2) Client pushes data to all 3 chunkservers (pipelined — data flows client -> CS1 -> CS2 -> CS3 using TCP forwarding). (3) Client sends write request to the primary. (4) Primary assigns a serial number and forwards the write order to secondaries. (5) Secondaries apply the write and ack. (6) Primary acks to client after all replicas confirm.

**The math**: Write latency = data transfer time + serialization delay. For a 64 MB chunk at 100 MB/s network between chunkservers: transfer takes ~0.64 seconds. Pipelining means total pipeline time is ~0.64s (not 3 x 0.64s) because data is forwarded immediately. Throughput for a single file write: limited by the slowest link in the pipeline. For aggregate throughput across many files, writes are parallelized across different chunkserver groups.

**Common misconception**: "Client writes to all 3 replicas in parallel." GFS uses chain replication (serial forwarding), not parallel fan-out. Chain replication is better for network utilization: the client's upload bandwidth is used once (to the first chunkserver), and subsequent hops use inter-server bandwidth.

### Concept 3: Consistency Model — "Defined" vs "Consistent"

**What it is**: GFS distinguishes between "consistent" (all replicas have the same data) and "defined" (consistent AND all clients see what the write intended). For serial writes from a single client, the result is defined. For concurrent appends from multiple clients, the result is "defined but interspersed" — each append is atomic, but the order across clients is non-deterministic.

**How it applies**: The record append operation (GFS's main write primitive) works like this: the client says "append this data to the file." The primary picks the offset (not the client). If the append would cross a chunk boundary, the primary pads the current chunk and starts a new one. The append succeeds atomically — all replicas have the same data at the same offset. But if the primary or a secondary fails mid-append, different replicas might have different data. GFS handles this by having the client retry — duplicates are possible and the application must handle them (using checksums and sequence numbers in the record format).

**The math**: At Google's scale, GFS record append failures were ~1% of append operations. With retry, the effective failure rate was negligible, but the application had to tolerate occasional duplicate records and padding bytes in the file.

**Common misconception**: "GFS provides strong consistency." It doesn't — it provides a relaxed model that was sufficient for MapReduce (which has its own dedup and sort phases). HDFS took a different approach: write-once semantics with a single writer per file at a time, giving stronger consistency at the cost of no concurrent appends.

### Concept 4: Master Failure and Recovery

**What it is**: The master's WAL is replicated to shadow masters. On master failure, a shadow master takes over by loading the latest checkpoint + replaying the WAL. Chunk locations are rebuilt from chunkserver heartbeats.

**How it applies**: Recovery time: load checkpoint (seconds for a 16 GB snapshot from SSD) + replay WAL (depends on how many ops since last checkpoint, typically seconds) + collect chunk reports from all 1,000 chunkservers (first heartbeat within 10 seconds, but waiting for ALL servers takes longer — stagger over 30-60 seconds). Total failover time: ~1-2 minutes. During failover, clients cannot do metadata operations (open, create) but existing data reads/writes continue — clients already have chunk locations cached.

**The math**: HDFS improved this with Active/Standby NameNode. The Active writes edits to a shared journal (JournalNode quorum, 3-5 nodes using QJM). The Standby continuously applies these edits. Failover takes <30 seconds because the Standby's state is nearly current. HDFS also has ViewFS for namespace federation — multiple NameNodes each own a portion of the namespace.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Read Path End-to-End

**Interviewer**: "A MapReduce job wants to read a 1 TB file. Walk me through the read path from the client to the data."

**You**: The MapReduce framework splits the file into input splits, typically one per chunk (64 MB). For a 1 TB file, that's ~16,384 chunks. The framework spawns ~16,384 map tasks, each reading one chunk. Each map task's read flow: (1) Call master: `open("/data/input/file.csv")` — master returns file metadata including chunk list. (2) For each chunk, call master: `get_chunk_locations(chunk_id)` — master returns 3 chunkserver addresses. (3) Read data directly from the nearest chunkserver (rack-aware — prefer same-rack, then same-datacenter). The client reads the full 64 MB chunk in sequential I/O from the chunkserver's local disk. The chunkserver verifies checksums (per-64 KB block) during the read and returns data to the client.

MapReduce's scheduler tries to place map tasks on the same node or rack as the chunk (data locality). If the chunk's primary chunkserver is also running a MapReduce worker, the read is a local disk read (no network) — ~100 MB/s. If not, it's a network read — limited by the slower of disk I/O and network (~10 Gbps = 1.25 GB/s per link). Aggregate read throughput for the entire job: 1,000 chunkservers x 100 MB/s = 100 GB/s. The 1 TB file reads in ~10 seconds of wall-clock time.

**Interviewer**: "The master gets 16,384 `get_chunk_locations` calls in rapid succession. Is that a problem?"

**You**: Not for a single job, but at scale: if 100 MapReduce jobs start simultaneously, each reading a 1 TB file, the master sees 1.6M metadata requests in a burst. At 100K ops/sec capacity, this queues up for 16 seconds. GFS handled this with client-side caching: the client caches chunk locations with a TTL (e.g., 60 seconds). For sequential reads of a file, the client prefetches chunk locations in batches: "give me locations for chunks 0-99 of file X." One metadata call covers 100 chunks. The 16,384 chunks become ~164 metadata calls — trivial.

**Interviewer**: "What if a chunkserver is slow? The map task blocks waiting for data."

**You**: Speculative execution. MapReduce detects slow tasks (taking >1.5x the median task time) and launches a duplicate task reading the same chunk from a different replica. Whichever finishes first wins. At the file system level, the client can also do hedged reads: send the read request to two chunkservers simultaneously and use the first response. The cost is doubled read bandwidth for slow tasks, but since slow tasks are ~5% of total, the overhead is 5% more reads for much better tail latency. GFS clients did this for latency-sensitive workloads.

**Interviewer**: "How do checksums work? What about bit rot?"

**You**: Each 64 MB chunk is divided into 64 KB blocks. Each block has a 32-bit CRC checksum stored separately on the chunkserver. On every read, the chunkserver verifies the block's checksum before returning data. If the checksum fails, the chunkserver returns an error — the client retries from a different replica and reports the corruption to the master. The master then schedules re-replication: read from 2 healthy replicas and create a new third replica on a different chunkserver. The corrupted chunkserver is told to delete the bad chunk. For proactive detection, each chunkserver runs a background scrubber that reads and checksums all chunks every 2-4 weeks, reporting corruption to the master. This catches bit rot before a read request hits the bad block.

### Deep Dive Path 2: Write Path and Consistency

**Interviewer**: "Three different producers are concurrently appending to the same log file. How does GFS handle this?"

**You**: GFS's record append is the key operation. Each producer calls `record_append(file, data)`. The flow: (1) Producer asks master for the current last chunk of the file and its primary chunkserver. (2) Master grants a lease to the primary chunkserver (60-second lease, renewable). The lease ensures only one primary per chunk at a time. (3) All three producers push their data to all 3 chunkservers of the current last chunk (data flow is pipelined). (4) Each producer sends a write request to the primary. (5) The primary serializes the requests — assigns sequential offsets within the chunk. Say producer A gets offset 0, producer B gets offset 1000, producer C gets offset 2000 (assuming 1000-byte records). (6) Primary tells secondaries to apply writes in the same order. (7) After all replicas confirm, primary acks each producer with their assigned offset.

**Interviewer**: "What if the primary crashes after writing its local copy but before secondaries confirm?"

**You**: This is where GFS's relaxed consistency shows. If the primary crashes, the master detects the lease expiration (60 seconds) and grants a new lease to a different chunkserver. The new primary might have a different state than the old primary (it received data from producers but the write wasn't serialized). GFS handles this with chunk versioning: the master increments the chunk version when granting a new lease. Chunkservers with stale versions are told to delete their copies. The new primary starts with whatever state it had at the time of the failure. Some appends might be duplicated or lost — the application is expected to handle this via sequence numbers in the record format. This is explicitly a trade-off: GFS chose availability and throughput over strong consistency for concurrent appends.

**Interviewer**: "HDFS chose a different model. How does it compare?"

**You**: HDFS doesn't allow concurrent appends to the same file. A file is write-once: one writer opens the file, writes to it, closes it, and the file is immutable after close. HDFS 2.x added append, but only for a single writer at a time. The write pipeline is similar (client -> DN1 -> DN2 -> DN3), but the NameNode grants an exclusive write lease — no concurrent writers. This gives strong consistency: after the write completes and the file is closed, all readers see exactly what was written. No duplicates, no padding. The trade-off: HDFS can't handle the concurrent-log-append workload that GFS was designed for. For log ingestion, HDFS users typically write to per-producer files and merge later, or use a system like Kafka that handles concurrent appends with its own log structure.

**Interviewer**: "How would you modernize GFS for today's workloads?"

**You**: Several improvements over the original GFS design: (1) **Erasure coding instead of 3x replication** — saves 50%+ storage. HDFS 3.x added EC support (Reed-Solomon). (2) **Replace single master with distributed metadata** — Ceph uses a CRUSH-based distributed placement algorithm with no centralized metadata. GFS2 (Colossus) at Google replaced the single master with a distributed metadata service (BigTable-backed). (3) **Tiered storage** — hot data on SSD, warm on HDD, cold on object storage (S3). Automated lifecycle based on access patterns. (4) **Stronger consistency** — Modern workloads (interactive analytics, ML training) need stronger guarantees than GFS provided. Colossus reportedly uses Reed-Solomon coding and offers stronger consistency.

### Deep Dive Path 3: Master Scalability and Federation

**Interviewer**: "At 500 million files, the single master runs out of memory. How do you scale?"

**You**: Three approaches, each with different trade-offs: (1) **Vertical scaling** — A 1 TB RAM machine holds metadata for 5 billion files. Practical up to ~10 billion files. Simple but expensive and still a single point of failure during upgrades. (2) **Namespace federation** — HDFS Federation splits the namespace into independent volumes: `/user` is served by NameNode A, `/logs` by NameNode B. Each NameNode manages its own namespace independently. Cross-namespace operations (move file from /user to /logs) require coordination. This is HDFS's approach since 2.x. (3) **Distributed metadata** — Ceph's approach: no master at all. File locations are computed (not looked up) using a deterministic algorithm (CRUSH). Metadata is distributed across MDS (Metadata Server) nodes using dynamic subtree partitioning. Most scalable but most complex.

**Interviewer**: "Walk me through HDFS Federation in detail. How does the client know which NameNode to contact?"

**You**: HDFS uses a client-side routing layer called ViewFS. The configuration maps path prefixes to NameNodes:

```xml
<property>
  <name>fs.viewfs.mounttable.default.link./user</name>
  <value>hdfs://namenode-a:8020/user</value>
</property>
<property>
  <name>fs.viewfs.mounttable.default.link./logs</name>
  <value>hdfs://namenode-b:8020/logs</value>
</property>
```

The client resolves the path prefix, contacts the appropriate NameNode, and proceeds normally. DataNodes are shared — all NameNodes share the same pool of DataNodes. Each DataNode stores block pools for all NameNodes, identified by a namespace ID. The DataNode sends heartbeats to all NameNodes independently. The benefit: each NameNode scales independently. The downside: no cross-NameNode directory listing (you can't `ls /` and see files from both), and rebalancing data across NameNodes requires manual intervention.

**Interviewer**: "What about Ceph's approach with CRUSH? How does it eliminate the metadata lookup?"

**You**: CRUSH is a pseudo-random placement algorithm. Given an object name and a cluster map (list of storage nodes with their hierarchy — rack, host, disk), CRUSH deterministically computes which storage nodes hold the object. No lookup needed — any client with the cluster map can compute placement locally. The algorithm ensures even distribution, respects failure domains (don't put 2 replicas in the same rack), and minimizes data movement when nodes are added/removed (similar to consistent hashing but with hierarchical awareness). The client does: `placement = CRUSH(hash(object_name), cluster_map, replication_rule)`. This returns a list of OSDs (Object Storage Daemons) that hold the object. No metadata server is involved in data path — only the MDS handles namespace operations (directories, permissions).

---

## How Real Companies Built This

- **Google GFS**: The original paper. Single master, 64 MB chunks, relaxed consistency, record append primitive. [GFS Paper — SOSP 2003](https://research.google/pubs/pub51/)
- **Google Colossus**: GFS successor. Distributed metadata (BigTable-backed), erasure coding, smaller chunk size (1 MB), stronger consistency. [Colossus — Google I/O 2010](https://cloud.google.com/blog/products/storage-data-transfer/a-peek-behind-colossus-googles-file-system)
- **Apache HDFS**: Open-source GFS. Write-once semantics, NameNode HA with QJM, Federation for namespace scaling. [HDFS Architecture Guide](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
- **Ceph**: No single master. CRUSH algorithm for placement, MDS for namespace, RADOS for storage layer. [Ceph Paper — OSDI 2006](https://www.usenix.org/conference/osdi-06/ceph-scalable-high-performance-distributed-file-system)
- **Facebook HDFS (Warm Storage)**: Modified HDFS with erasure coding (Reed-Solomon 10+4) for warm data, reducing storage overhead from 3x to 1.4x. [Facebook Warm Storage — OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/muralidhar)

---

## The Complete Reference Design

### API Design

```
# File operations (client -> master)
POST   /v1/files/create    { "path": "/user/data/file.csv", "replication": 3 }
GET    /v1/files/open       { "path": "/user/data/file.csv" }
       # Returns: { "file_id": "...", "chunks": [{"chunk_id": "c1", "locations": ["CS1","CS2","CS3"]}] }
DELETE /v1/files/delete     { "path": "/user/data/file.csv" }
GET    /v1/files/list       { "path": "/user/data/", "recursive": false }

# Chunk operations (client -> master)
POST   /v1/chunks/alloc     { "file_id": "...", "chunk_index": 5 }
       # Returns: { "chunk_id": "c5", "primary": "CS2", "secondaries": ["CS1","CS3"], "lease_expires": "..." }

# Data operations (client -> chunkserver, master NOT involved)
PUT    /v1/data/{chunk_id}  # Write chunk data (64 MB max)
GET    /v1/data/{chunk_id}?offset=0&length=65536  # Read chunk data
POST   /v1/data/{chunk_id}/append  # Atomic record append

# Chunkserver -> master heartbeat
POST   /v1/heartbeat
{
  "chunkserver_id": "CS1",
  "chunks": ["c1", "c5", "c12"],
  "disk_usage": { "total_gb": 30000, "used_gb": 25000 },
  "load": 0.75
}
```

### Database Schema (Master In-Memory + WAL)

```sql
-- These tables represent the master's in-memory state
-- Persisted to WAL for namespace mutations, rebuilt from chunkserver heartbeats for chunk locations

CREATE TABLE namespace (
    inode_id      BIGINT PRIMARY KEY,
    parent_id     BIGINT REFERENCES namespace(inode_id),
    name          VARCHAR(256) NOT NULL,
    is_directory  BOOLEAN NOT NULL,
    file_size     BIGINT DEFAULT 0,
    replication   SMALLINT DEFAULT 3,
    block_size    INT DEFAULT 67108864,    -- 64 MB
    owner         VARCHAR(64),
    permissions   SMALLINT DEFAULT 755,
    created_at    TIMESTAMP NOT NULL,
    modified_at   TIMESTAMP NOT NULL,
    UNIQUE (parent_id, name)
);

CREATE TABLE chunk_metadata (
    chunk_id      BIGINT PRIMARY KEY,
    file_id       BIGINT NOT NULL REFERENCES namespace(inode_id),
    chunk_index   INT NOT NULL,             -- position within file
    version       INT NOT NULL DEFAULT 1,   -- incremented on lease grant
    size_bytes    INT NOT NULL DEFAULT 0,   -- actual data size
    checksum      BIGINT,                   -- aggregate checksum
    UNIQUE (file_id, chunk_index)
);

-- NOT persisted — rebuilt from heartbeats
CREATE TABLE chunk_locations (
    chunk_id         BIGINT NOT NULL,
    chunkserver_id   VARCHAR(64) NOT NULL,
    is_primary       BOOLEAN DEFAULT FALSE,
    lease_expires    TIMESTAMP,
    last_reported    TIMESTAMP NOT NULL,
    PRIMARY KEY (chunk_id, chunkserver_id)
);
```

### Key Algorithms — Chunk Placement with Rack Awareness

```python
import random
from collections import defaultdict

class ChunkPlacement:
    """Rack-aware chunk placement for replication."""

    def __init__(self):
        self.servers: dict[str, dict] = {}  # server_id -> {rack, capacity, used, load}
        self.rack_servers: dict[str, list[str]] = defaultdict(list)

    def add_server(self, server_id: str, rack: str, capacity_gb: int):
        self.servers[server_id] = {
            "rack": rack, "capacity": capacity_gb, "used": 0, "load": 0.0
        }
        self.rack_servers[rack].append(server_id)

    def select_replicas(self, replication: int = 3) -> list[str]:
        """Select chunkservers for a new chunk.
        Policy: first replica on a lightly loaded server,
        second on a different rack, third on same rack as second
        (for intra-rack bandwidth during pipeline replication)."""
        available = [
            (sid, info) for sid, info in self.servers.items()
            if info["used"] < info["capacity"] * 0.95  # <95% full
        ]
        if len(available) < replication:
            raise Exception("Insufficient capacity")

        # Sort by load (prefer less loaded)
        available.sort(key=lambda x: (x[1]["load"], x[1]["used"] / x[1]["capacity"]))
        selected = []
        selected_racks = set()

        # First replica: least loaded server
        first = available[0]
        selected.append(first[0])
        selected_racks.add(first[1]["rack"])

        # Second replica: different rack, least loaded
        for sid, info in available[1:]:
            if info["rack"] not in selected_racks:
                selected.append(sid)
                selected_racks.add(info["rack"])
                second_rack = info["rack"]
                break

        # Third replica: same rack as second (if possible), different server
        for sid, info in available[1:]:
            if sid not in selected and info["rack"] == second_rack:
                selected.append(sid)
                break

        # Fallback: any available server
        while len(selected) < replication:
            for sid, info in available:
                if sid not in selected:
                    selected.append(sid)
                    break

        return selected[:replication]
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Chunkservers | 10 PB x 3 replication / 30 TB per server | 1,000 servers |
| Master RAM | 160M chunks x 100B + 100M files x 200B = 36 GB | Single server, 64+ GB RAM |
| Master disk (WAL) | 100K ops/sec x 100B = 10 MB/s | SSD, 1 TB |
| Network per chunkserver | Sequential read at ~200 MB/s per disk x 12 disks | 2 x 25 Gbps NIC |
| Aggregate read BW | 1000 servers x 2 GB/s (conservative) | 2 TB/s potential |
| Heartbeat traffic | 1000 servers x 1 KB / 10 sec | 100 KB/s (negligible) |
| Chunk report (startup) | 1000 servers x 30K chunks/server x 50B | 1.5 GB over ~60 sec |

---

## Senior vs Staff vs Principal

| Aspect | Senior (E5/L5) | Staff (E6/L6) | Principal (L66+) |
|--------|----------------|----------------|-------------------|
| **Architecture** | Clean master/chunkserver separation, understands why data bypasses master | Designs write pipeline with primary/secondary chain replication, explains lease mechanism | Designs distributed metadata (Colossus-style), compares GFS/HDFS/Ceph trade-offs |
| **Consistency** | Understands replication provides durability | Explains GFS's relaxed consistency model and why it works for MapReduce | Designs stronger consistency models for modern workloads, explains linearizable reads |
| **Scale** | Correct metadata math showing single-master feasibility | Designs namespace federation (HDFS-style), explains CRUSH algorithm | Designs multi-datacenter replication, reasons about cross-DC consistency and bandwidth |
| **Failure handling** | Mentions master standby and chunk re-replication | Designs master failover with WAL + QJM, explains data loss window | Designs zero-RPO master HA, reasons about correlated failures (rack power, network partition) |

---

## Red Flags & Common Mistakes

1. **Putting data through the master** — The most fundamental mistake. The master handles ONLY metadata. Data flows directly between clients and chunkservers.
2. **"Use a database for metadata"** — Metadata must be in RAM for performance. A database lookup for every chunk read would add 1-5ms per metadata op, making it too slow for high-throughput sequential reads.
3. **No discussion of chunk size** — 64 MB is not arbitrary. Smaller chunks mean more metadata (more master RAM, more heartbeat traffic). Larger chunks waste space for small files and reduce parallelism.
4. **Ignoring the small file problem** — Each file consumes ~200 bytes of master metadata regardless of size. 1 billion 1-KB files use 200 GB of master RAM but only 1 TB of actual data. This is why HDFS has the "small file problem."
5. **No write pipeline** — "Client writes to all 3 replicas in parallel." GFS uses chain replication for a reason: it's more bandwidth-efficient and provides natural sequencing.
6. **Confusing GFS and POSIX** — GFS is NOT a POSIX filesystem. It has relaxed consistency, no random writes, and application-level record dedup.
7. **No checksum story** — Silent data corruption (bit rot) is real. Without per-block checksums and periodic scrubbing, the system silently serves corrupt data.
