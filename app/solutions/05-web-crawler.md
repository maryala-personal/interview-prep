# Design a Web Crawler

> **Companies**: Google, Microsoft (Bing), Amazon, Apple, Pinterest, LinkedIn | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a distributed system that handles extreme scale (billions of pages), reason about politeness policies and URL frontier management, and think through deduplication at web scale? This problem tests your understanding of distributed task scheduling, content hashing, and the practical challenges of dealing with the messy, adversarial real web.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**These are the questions that make the interviewer think "this person knows what they're doing."**

- "What's the crawl scope? The entire web (billions of pages) or a specific domain/set of domains?"
- "What's the target crawl rate? 1000 pages/sec or 100K pages/sec? This determines the level of distribution needed."
- "What content types are we crawling? HTML only, or also PDFs, images, JavaScript-rendered pages?"
- "What's the freshness requirement? Do we need to re-crawl pages and how often? Daily, weekly?"
- "Do we need to handle dynamic/JavaScript-rendered content? This requires headless browser rendering, which is 100x more expensive."
- "What's our politeness policy? Respect robots.txt, enforce per-domain rate limits, handle crawler traps?"
- "What's the storage strategy? Store raw HTML, extracted text, or just metadata/links?"
- "What's the deduplication strategy? Same content at different URLs (mirrors), URL normalization?"

### Working Assumptions

| Parameter | Value |
|-----------|-------|
| Pages to crawl | 5B pages (initial crawl) |
| Target crawl rate | 10K pages/sec |
| Avg page size | 100 KB (HTML) |
| URL frontier size | 10B URLs (discovered but not yet crawled) |
| Re-crawl frequency | Weekly for top 10M sites, monthly for rest |
| Storage per page | 100 KB HTML + 5 KB metadata |
| Politeness | 1 req/sec per domain, respect robots.txt |
| Total storage (initial) | ~500 TB |

**The math**:
- 5B pages at 10K pages/sec = 500,000 seconds = ~6 days for a full crawl
- 10K pages/sec x 100 KB = 1 GB/sec inbound bandwidth
- URL frontier: 10B URLs x 100 bytes avg = 1 TB — needs to be on disk, not RAM
- robots.txt cache: ~500M domains x 10 KB avg = 5 TB (cache hot ones in memory)

---

## High-Level Design (Keep it brief — 5 minutes max)

```
                    ┌───────────────────┐
                    │   URL Frontier    │ ← Priority queue of URLs to crawl, partitioned by domain
                    │   (RocksDB +      │
                    │    Redis queues)   │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │  Scheduler /      │ ← Enforces politeness (1 req/sec/domain), assigns work
                    │  Coordinator      │
                    └────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │  Worker    │ │  Worker   │ │  Worker   │  ← 500+ workers, each fetches ~20 pages/sec
        │  (fetcher) │ │  (fetcher)│ │  (fetcher)│
        └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │  Content   │ │  URL      │ │  Dedup    │
        │  Store     │ │  Extractor│ │  Service  │
        │  (S3/HDFS) │ │  (parser) │ │ (Bloom +  │
        │            │ │           │ │  SimHash) │
        └────────────┘ └───────┬───┘ └───────────┘
                               │
                        ┌──────▼──────┐
                        │  Back to    │
                        │  Frontier   │ ← Newly discovered URLs fed back to the frontier
                        └─────────────┘
```

**Why this architecture?** The URL frontier is the heart of the crawler — it's a distributed priority queue that determines what to crawl next, respecting politeness constraints. We separate fetching (I/O bound — waiting on network) from processing (CPU bound — parsing, extracting, deduplication) because they scale differently. The feedback loop (extracted URLs → frontier) is what makes this a continuous crawl, not a one-shot job.

---

## Core Concepts Deep Dive

### Concept 1: URL Frontier — The Prioritized Politeness Queue

**What it is**: The URL frontier is not a simple queue. It's a two-level structure: a priority queue (which URLs are most important) feeding into per-domain FIFO queues (enforcing politeness). This is the Mercator architecture pattern.

**How it applies here**:
- **Front queues (priority)**: URLs are bucketed by priority — e.g., high-priority for news sites that change hourly, low-priority for deep archive pages. Priority is based on PageRank, freshness requirements, and domain importance.
- **Back queues (politeness)**: One queue per domain (or per IP). A worker can only pull from a domain queue if enough time has passed since the last request to that domain (e.g., 1 second).
- **Queue router**: Maps URLs from front queues to the correct back queue based on the domain.

**The math/mechanics**:
- 10B URLs in the frontier. At 100 bytes per URL, that's 1 TB.
- Can't fit in RAM. Use RocksDB (LSM-tree on SSD) for the bulk frontier.
- Hot domains (top 1M) have their queues in Redis for fast access.
- Per-domain rate: 1 req/sec. With 500M unique domains, at any moment we can have at most 500M requests in flight (one per domain). In practice, at 10K pages/sec, we're actively crawling ~10K domains simultaneously.

**Common misconception**: Candidates propose a single priority queue (like Kafka). This ignores politeness — you'd need to skip messages for domains that were recently fetched, which turns your queue into a random-access data structure. The Mercator two-level design is the standard.

### Concept 2: Content Deduplication — Exact and Near-Duplicate

**What it is**: The web has massive duplication. The same article appears on mirrors, syndication sites, and slight URL variations. We need to avoid storing (and re-crawling) duplicate content.

**How it applies here**:
- **URL deduplication**: Before adding a URL to the frontier, check if we've already seen it. Use a Bloom filter for O(1) checks with ~1% false positive rate.
- **Content deduplication**: After fetching a page, hash the content (MD5 or SHA-256) and check against a content fingerprint store. Exact duplicates are caught.
- **Near-duplicate detection**: Pages that are 95% identical (same article, different ads/headers). Use SimHash — a locality-sensitive hash that maps similar documents to similar hash values. Two documents with Hamming distance < 3 in their 64-bit SimHash are near-duplicates.

**The math/mechanics**:
```
Bloom filter for 10B URLs:
- Desired false positive rate: 1%
- Bits needed: -n * ln(p) / (ln(2))^2 = -10B * ln(0.01) / 0.48 = ~96B bits = 12 GB
- Hash functions: k = (m/n) * ln(2) = (96B/10B) * 0.69 = ~7

SimHash for near-duplicate detection:
- Convert document to set of shingles (3-word sequences)
- Hash each shingle to 64-bit value
- Aggregate: for each bit position, sum (+1 if 1, -1 if 0)
- Final hash: 1 if sum > 0, 0 otherwise
- Compare: Hamming distance < 3 = near-duplicate
```

**Common misconception**: Candidates forget about near-duplicates. Exact hash deduplication catches mirrors but misses the far more common case: same article with different navigation bars, ads, or timestamps. SimHash or MinHash are essential for production crawlers.

### Concept 3: Politeness and robots.txt — Respecting the Web

**What it is**: A crawler must be a good citizen. This means: respecting robots.txt (which URLs are off-limits), enforcing per-domain request rate limits, and handling soft-404s, redirects, and crawler traps.

**How it applies here**:
- **robots.txt**: Before crawling any path on a domain, fetch and cache the domain's robots.txt. Parse it using the standard (RFC 9309). Cache with a 24-hour TTL.
- **Rate limiting**: At most 1 request per second per domain (configurable per domain). The back-queue structure in the frontier enforces this.
- **Crawler traps**: Dynamically generated URLs that create infinite loops (e.g., calendar pages: /calendar/2025/01, /calendar/2025/02, ..., /calendar/3025/12). Detection: limit crawl depth per domain (e.g., max 10 hops from the seed URL), limit URLs per domain (e.g., max 100K).

**Common misconception**: Candidates skip robots.txt entirely. In a real interview, mentioning it proactively shows you understand the practical and ethical aspects of web crawling. Not mentioning it is a minor red flag.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "URL Frontier and Scheduling"

**Interviewer**: "You mentioned a Mercator-style frontier. Walk me through what happens when a worker asks for the next URL to crawl."

**You**: "The worker sends a request to the scheduler: 'give me a URL.' The scheduler iterates through back queues that are eligible (enough time has passed since the last fetch for that domain). It picks the highest-priority eligible queue, dequeues the front URL, records the fetch timestamp for that domain, and assigns the URL to the worker. The worker fetches the page, processes it, and reports back. The scheduler is essentially a round-robin over eligible back queues, weighted by priority. To avoid the scheduler becoming a bottleneck, we partition: shard back queues by domain hash. Each scheduler shard manages a subset of domains. Workers are assigned to scheduler shards."

**Interviewer**: "How do you handle priority? A breaking news page should be crawled before a 5-year-old blog post."

**You**: "Priority is a composite score. Components: (1) Domain authority — PageRank or a simpler domain popularity metric based on inbound link count. (2) Freshness score — pages that change frequently (detected via last-modified headers or change rate from previous crawls) get higher priority. (3) Explicit boost — manually boosted domains (news sites, critical business partners). (4) Age — URLs that have been in the frontier longest get a priority bump to prevent starvation. The priority is recalculated periodically (every re-crawl cycle) and determines which front queue the URL goes into. I'd use 3-5 front queues (high, medium, low, re-crawl, backfill)."

**Interviewer**: "What happens when you discover 10 million new URLs from one site? Say you're crawling a forum with millions of threads."

**You**: "Per-domain URL budget. We cap the number of URLs in the frontier per domain — say, 100K. Once the budget is hit, new URLs from that domain are dropped (or stored in a low-priority overflow). This prevents a single site from dominating the frontier. The budget is proportional to the domain's importance: top 1000 sites get 1M URL budget, most sites get 10K. This also protects against crawler traps — a trap that generates infinite URLs hits the budget and stops. We also enforce max depth: if a URL is more than 10 link-hops from the seed, deprioritize it heavily."

**Interviewer**: "Your scheduler is a bottleneck. How do you scale it?"

**You**: "Partition by domain. If we have 500M domains, partition them into 1000 shards of 500K domains each. Each scheduler shard manages the back queues for its domains. Workers connect to a specific shard (or round-robin across shards). This gives us 1000x parallelism. Within each shard, the scheduler handles ~10 req/sec (10K total / 1000 shards). The shard assignment uses consistent hashing on domain name, so domains always go to the same shard. Each shard maintains its back queues and politeness state independently."

### Deep Dive Path 2: "Fetching and Processing at Scale"

**Interviewer**: "Walk me through a worker fetching a page. What are all the things that can go wrong?"

**You**: "The worker gets a URL from the scheduler. Step 1: DNS resolution. We maintain a local DNS cache (TTL-respecting) to avoid hammering DNS servers. DNS failures: retry once, then skip and re-queue with delay. Step 2: Check robots.txt (cached, refresh every 24h). If disallowed, skip. Step 3: HTTP GET with a 30-second timeout. Set User-Agent to identify our crawler. Follow redirects up to 5 hops. Handle HTTP 301/302 (update the URL), 403 (respect it, don't retry), 429 (back off, increase politeness delay for this domain), 500 (retry with exponential backoff up to 3 times). Step 4: Content-type check. If it's not text/html (or whatever we're targeting), skip. Step 5: Decode the charset (not everything is UTF-8). Step 6: Parse the HTML, extract text, extract links. Step 7: Content dedup check (SimHash). Step 8: Store content to S3/HDFS. Step 9: Feed extracted URLs back to the frontier."

**Interviewer**: "How do you handle JavaScript-rendered pages? Like a single-page React app?"

**You**: "Static HTML parsing won't get the content. We need a headless browser — Chromium via Puppeteer/Playwright. This is 100x more expensive: a headless browser takes ~500ms-2s per page instead of ~100ms for a static fetch, and uses 100MB+ RAM per instance. The approach: two-tier fetching. First, fetch with a lightweight HTTP client. If the page has minimal content (< 100 words of visible text) but lots of JavaScript, flag it for headless rendering. A separate pool of headless browser workers handles these pages. We'd render maybe 5-10% of pages this way. Google reportedly uses headless rendering for a significant fraction of their crawls. The key is to NOT render everything — it's too expensive."

**Interviewer**: "At 10K pages/sec, how many workers do you need and how do you manage them?"

**You**: "Each worker is I/O bound — waiting on network responses. With async I/O (Python asyncio, Go goroutines), a single worker process can handle ~50 concurrent fetches. At 200ms average response time, that's 50 / 0.2 = 250 pages/sec per worker. For 10K pages/sec: 10K / 250 = 40 worker processes. In practice, with variance and headless rendering, I'd run ~100 worker instances across 20 machines. Each machine: 5 worker processes, 8 cores (mostly idle — I/O bound), 32 GB RAM (for DNS cache, HTML parsing), and high network bandwidth. I'd deploy these on Kubernetes with horizontal pod autoscaling based on frontier queue depth."

### Deep Dive Path 3: "Deduplication and Storage"

**Interviewer**: "Your Bloom filter for URL dedup has a 1% false positive rate. That means 1% of new URLs are incorrectly flagged as already seen. Is that acceptable?"

**You**: "For most use cases, yes. 1% false positive means we miss 1% of unique pages — about 50M pages out of 5B. These pages will be discovered and crawled in the next crawl cycle. However, if we need lower false positives, we can: (1) increase Bloom filter size — 0.1% FP rate needs ~14.4 GB for 10B URLs. (2) Use a Counting Bloom Filter if we need deletions (URLs that are removed from the frontier). (3) Use a Cuckoo filter for better space efficiency at low FP rates. The false negative rate is 0% — we'll never crawl a URL we've already crawled, which is the more important guarantee."

**Interviewer**: "How do you handle URL normalization? `http://Example.com/path` and `https://example.com/path/` are the same page."

**You**: "URL normalization is a critical preprocessing step before the Bloom filter check. Rules: (1) Lowercase the scheme and host: `HTTP://Example.COM` → `http://example.com`. (2) Remove default ports: `:80` for HTTP, `:443` for HTTPS. (3) Remove trailing slashes: `/path/` → `/path`. (4) Sort query parameters: `?b=2&a=1` → `?a=1&b=2`. (5) Remove known tracking parameters: `utm_source`, `fbclid`, `ref`. (6) Decode unnecessary percent-encoding: `%41` → `A`. (7) Remove fragment identifiers: `#section`. (8) Normalize scheme: I'd canonicalize to HTTPS where we know the site supports it. After normalization, hash the canonical URL for the Bloom filter. Without normalization, we'd crawl the same page dozens of times under different URL forms."

**Interviewer**: "You're storing 500 TB of crawled HTML. How do you store and retrieve it efficiently?"

**You**: "Primary store: S3 (or HDFS on-prem). Each crawled page is stored as an object with key = `content_hash` (SHA-256 of the raw HTML). This gives us automatic dedup — two different URLs with identical content map to the same object. Metadata is stored separately in a database (DynamoDB or HBase): URL → content_hash, last_crawl_time, HTTP status, content_type, etc. For batch processing (building a search index), we use a columnar format: store all pages from a single domain in one file (WARC format, the web archive standard). This gives sequential read throughput for MapReduce jobs. For real-time access (fetching a single page), the S3 key lookup by content_hash is O(1). Compression: gzip each HTML page — typical 10x compression, so 500 TB becomes ~50 TB actual storage."

---

## How Real Companies Built This

- **Google**: The original Googlebot is described in the seminal paper "The Anatomy of a Large-Scale Hypertextual Web Search Engine" (Brin & Page, 1998). Modern Googlebot uses headless Chromium for rendering (announced 2019). They crawl hundreds of billions of pages. See also: "Web Crawling" chapter in "Introduction to Information Retrieval" (Stanford NLP Group, free online).
- **Common Crawl**: An open, non-profit web crawl used by researchers. They crawl ~3B pages/month and store everything in WARC format on AWS S3. Their architecture is publicly documented and is a great reference. See: https://commoncrawl.org/
- **Scrapy**: Open-source crawling framework in Python. While not web-scale, its architecture (downloader middleware, item pipelines, URL dedup) mirrors production crawlers. See: https://github.com/scrapy/scrapy
- **Mercator**: The original paper describing the frontier architecture — "Mercator: A Scalable, Extensible Web Crawler" (Heydon & Najork, 1999). This is the canonical reference for frontier design.
- **Key lesson**: DNS resolution is the hidden bottleneck. At 10K pages/sec, that's 10K DNS lookups/sec. Without a local DNS cache, your crawler will overwhelm public DNS resolvers and get rate-limited. Every production crawler runs its own caching DNS resolver.

---

## The Complete Reference Design

### API Design
```
# Internal APIs (no public-facing API for a crawler)

# Worker → Scheduler: Request work
POST /api/v1/scheduler/next-urls
Request: {
    "worker_id": "w-042",
    "batch_size": 50,
    "capabilities": ["html", "headless"]   // What this worker can handle
}
Response: {
    "urls": [
        {
            "url": "https://example.com/page",
            "priority": 0.85,
            "depth": 3,
            "domain": "example.com",
            "last_crawled": "2026-01-15T00:00:00Z"
        }
    ]
}

# Worker → Coordinator: Report results
POST /api/v1/crawler/results
Request: {
    "worker_id": "w-042",
    "results": [
        {
            "url": "https://example.com/page",
            "status": 200,
            "content_hash": "sha256:abc123...",
            "content_size": 45320,
            "extracted_urls": ["https://example.com/link1", "https://other.com/link2"],
            "simhash": "0xABCDEF1234567890",
            "fetch_time_ms": 230,
            "content_type": "text/html"
        }
    ]
}

# Monitoring API
GET /api/v1/crawler/stats
Response: {
    "pages_crawled_today": 864000000,
    "pages_per_second": 10234,
    "frontier_size": 9876543210,
    "active_workers": 98,
    "domains_being_crawled": 12456,
    "error_rate": 0.032
}
```

### Database Schema
```sql
-- Frontier: URL queue (RocksDB / LevelDB per shard)
-- Key: priority_bucket:domain:url_hash
-- Value: serialized URL entry
{
    "url": "https://example.com/page",
    "priority": 0.85,
    "depth": 3,
    "discovered_at": 1707696000,
    "source_url": "https://example.com/"
}

-- Metadata store (DynamoDB / HBase)
-- Crawl metadata per URL
CREATE TABLE crawl_metadata (
    url_hash        BINARY(32) PRIMARY KEY,   -- SHA-256 of normalized URL
    url             TEXT NOT NULL,
    domain          VARCHAR(255) NOT NULL,
    last_crawl_time TIMESTAMP,
    last_status     SMALLINT,
    content_hash    BINARY(32),               -- SHA-256 of content
    simhash         BIGINT,                   -- 64-bit SimHash
    content_size    INT,
    crawl_count     INT DEFAULT 0,
    change_rate     FLOAT,                    -- Estimated changes per day
    INDEX idx_domain (domain, last_crawl_time)
);

-- Domain metadata
CREATE TABLE domain_metadata (
    domain          VARCHAR(255) PRIMARY KEY,
    robots_txt      TEXT,
    robots_fetched  TIMESTAMP,
    crawl_delay     INT DEFAULT 1,            -- Seconds between requests
    url_budget      INT DEFAULT 10000,
    priority_class  VARCHAR(20),              -- 'high', 'medium', 'low'
    last_crawl_time TIMESTAMP
);

-- Redis: Politeness state
-- Key: domain:last_fetch:{domain_name}
-- Value: Unix timestamp of last fetch
-- TTL: 60 seconds
```

### Key Algorithms
```python
import hashlib
import mmh3
import math
from typing import List

class BloomFilter:
    """Space-efficient probabilistic URL dedup."""

    def __init__(self, expected_items: int = 10_000_000_000, fp_rate: float = 0.01):
        self.size = int(-expected_items * math.log(fp_rate) / (math.log(2) ** 2))
        self.num_hashes = int((self.size / expected_items) * math.log(2))
        self.bit_array = bytearray(self.size // 8 + 1)

    def add(self, url: str):
        for i in range(self.num_hashes):
            idx = mmh3.hash(url, seed=i) % self.size
            self.bit_array[idx // 8] |= (1 << (idx % 8))

    def might_contain(self, url: str) -> bool:
        for i in range(self.num_hashes):
            idx = mmh3.hash(url, seed=i) % self.size
            if not (self.bit_array[idx // 8] & (1 << (idx % 8))):
                return False
        return True

def normalize_url(url: str) -> str:
    """Canonicalize URL for dedup."""
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    host = parsed.hostname.lower() if parsed.hostname else ""
    port = parsed.port
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None
    netloc = host + (f":{port}" if port else "")

    path = parsed.path.rstrip("/") or "/"

    # Sort and filter query params
    tracking_params = {"utm_source", "utm_medium", "utm_campaign", "fbclid", "ref", "gclid"}
    params = parse_qs(parsed.query, keep_blank_values=True)
    filtered = {k: v for k, v in sorted(params.items()) if k not in tracking_params}
    query = urlencode(filtered, doseq=True)

    return urlunparse((scheme, netloc, path, "", query, ""))

def simhash(text: str, hash_bits: int = 64) -> int:
    """Compute SimHash for near-duplicate detection."""
    # Generate shingles (3-word sequences)
    words = text.lower().split()
    shingles = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]

    # Initialize bit counters
    v = [0] * hash_bits

    for shingle in shingles:
        h = int(hashlib.md5(shingle.encode()).hexdigest(), 16) & ((1 << hash_bits) - 1)
        for i in range(hash_bits):
            if h & (1 << i):
                v[i] += 1
            else:
                v[i] -= 1

    # Convert to fingerprint
    fingerprint = 0
    for i in range(hash_bits):
        if v[i] > 0:
            fingerprint |= (1 << i)
    return fingerprint

def hamming_distance(a: int, b: int) -> int:
    """Count differing bits between two SimHash values."""
    return bin(a ^ b).count("1")

def is_near_duplicate(hash1: int, hash2: int, threshold: int = 3) -> bool:
    return hamming_distance(hash1, hash2) <= threshold
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Content Storage (S3) | 5B pages x 100 KB x 0.1 (compression) | ~50 TB |
| Metadata DB | 5B rows x 200 bytes | ~1 TB |
| Bloom Filter (URL dedup) | 10B URLs, 1% FP rate | ~12 GB RAM |
| Frontier (RocksDB) | 10B URLs x 100 bytes | ~1 TB SSD |
| DNS Cache | 500M domains x 100 bytes | ~50 GB |
| Network (inbound) | 10K pages/sec x 100 KB | ~1 GB/sec |
| Workers | 10K pages/sec / 250 pages/sec/worker | ~40 processes (100 with headroom) |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Designs basic crawl loop, handles dedup with hashing, mentions robots.txt | Implements URL frontier as a queue, uses Bloom filter for dedup, respects robots.txt |
| Staff | Designs the Mercator frontier (priority + politeness), handles near-duplicate detection, considers JavaScript rendering | Proposes two-level frontier, implements SimHash, designs the headless rendering pipeline, discusses crawler traps |
| Principal | Thinks about crawl freshness and prioritization at web scale, considers legal/ethical implications, proposes incremental crawling | Designs adaptive crawl scheduling based on change frequency, discusses copyright implications of content storage, proposes differential crawling (only re-fetch changed content using ETags/If-Modified-Since), considers multi-region crawling for latency |

---

## Red Flags & Common Mistakes

- **Treating the frontier as a simple FIFO queue**: Without priority and politeness, you'll hammer popular sites and starve important pages. The Mercator design is the expected answer.
- **Forgetting about DNS**: At 10K pages/sec, DNS is a bottleneck. Not mentioning DNS caching shows you haven't thought about the network stack.
- **No deduplication strategy**: The web has massive duplication. A crawler without dedup will waste 30-40% of its resources on duplicate content.
- **Ignoring robots.txt**: This is both a technical and ethical requirement. Not mentioning it is a red flag.
- **Over-engineering with Kafka**: Candidates often propose Kafka for the URL frontier. Kafka is a commit log, not a priority queue. You can't efficiently skip or reorder messages. Use a purpose-built frontier (RocksDB + domain queues).
