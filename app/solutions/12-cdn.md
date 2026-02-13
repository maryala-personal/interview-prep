# Design a Content Delivery Network (CDN)

> **Companies**: Amazon (CloudFront), Cloudflare, Akamai, Meta, Netflix, Google | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you reason about caching at global scale, HTTP protocol mechanics, cache invalidation strategies, and the physics of network latency? This question probes your understanding of how the internet actually works — DNS, TCP/TLS, HTTP caching headers, edge computing, and the fundamental trade-off between consistency and latency when content is cached across hundreds of locations worldwide.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**Questions that show the interviewer you know what you're doing:**

- "What type of content? Static assets (images, JS, CSS), video streaming, or dynamic API responses? This changes the caching strategy entirely."
- "What's the cache hit ratio target? 95%+ for static, but what about dynamic content?"
- "What's the latency target? Sub-50ms for cache hits? What about cache misses (origin fetch)?"
- "How many PoPs (Points of Presence) are we designing for? 50 or 500?"
- "What's the invalidation SLA? When content changes at origin, how fast must all edges reflect the update — seconds, minutes?"
- "What's the total data volume? Terabytes or petabytes across all edges?"
- "Do we need to handle TLS termination at the edge? HTTP/2, HTTP/3 (QUIC)?"
- "What's the origin infrastructure? Single origin or multi-region origins?"

### Working Assumptions
| Parameter | Value | Derivation |
|-----------|-------|------------|
| Global requests | 10M requests/sec (peak) | Large CDN scale (Cloudflare handles ~40M rps) |
| Content types | 80% static (images, JS, CSS), 15% video, 5% dynamic | Typical web traffic mix |
| Total unique content | 500TB | Across all origins |
| PoPs (Points of Presence) | 200 globally | Major metro areas worldwide |
| Servers per PoP | 10-100 (varies by traffic) | Larger PoPs in high-traffic areas |
| Cache hit ratio target | 95% for static, 80% overall | Standard CDN target |
| p50 latency (cache hit) | < 20ms | Edge server is physically close to user |
| p50 latency (cache miss) | < 200ms | Origin fetch + edge caching |
| Invalidation SLA | < 30 seconds globally | When origin pushes purge |
| Bandwidth | 100+ Tbps aggregate | Across all PoPs |

---

## High-Level Design (Brief — 5 minutes)

```
User in Tokyo
    |
    v  (DNS resolves to nearest PoP)
+-----------+     +-------------------+
|  DNS /    |---->|  Edge PoP Tokyo   |
|  Anycast  |     |  +-------------+  |
+-----------+     |  | TLS Term    |  |
                  |  +------+------+  |
                  |         |         |
                  |  +------v------+  |
                  |  | Edge Cache  |  |     CACHE HIT -> respond directly
                  |  | (SSD+RAM)  |  |
                  |  +------+------+  |
                  |         |         |
                  +---------|─────────+
                            | CACHE MISS
                            v
                  +-------------------+
                  |  Shield / Mid-Tier|     Aggregates cache misses
                  |  Cache            |     to protect origin
                  +--------+----------+
                           |
                           v
                  +-------------------+
                  |  Origin Server    |     Customer's actual server
                  |  (S3, web app)    |
                  +-------------------+

Control Plane:
  - Configuration service (routing rules, cache policies)
  - Purge/Invalidation service (fan-out to all PoPs)
  - Health monitoring & traffic shifting
  - Analytics & logging pipeline
```

**Why this architecture?**: A CDN is fundamentally a distributed cache with geographic awareness. The two-tier cache (edge + shield) is critical — without the shield layer, a cache miss at any of 200 PoPs hits the origin independently, turning N cache misses into N origin requests for the same content. The shield collapses these into a single origin fetch.

---

## Core Concepts Deep Dive

### Concept 1: DNS-Based & Anycast Routing

**What it is**: How does the user's request reach the nearest PoP? Two approaches: (1) DNS-based routing — the CDN's authoritative DNS server returns the IP of the nearest PoP based on the resolver's IP (geo-IP lookup), or (2) Anycast — the same IP address is advertised via BGP from all PoPs, and BGP routing naturally sends the request to the nearest one.

**How it applies here**: Modern CDNs use Anycast for most traffic. Every PoP advertises the same IP prefix. The internet's BGP routing sends each packet to the closest PoP (by BGP hop count, which roughly correlates with latency). Anycast is simpler than DNS-based routing (no DNS TTL issues, no resolver IP inaccuracy) and handles failover naturally — if a PoP goes down, BGP withdraws the route and traffic shifts to the next nearest PoP in seconds.

**The math/mechanics**: DNS-based routing has a fundamental problem: DNS resolvers cache records for TTL duration (typically 60-300 seconds). During this window, users can be routed to a sub-optimal PoP. With 60s TTL, failover takes 60s. With Anycast, BGP convergence time is 5-30 seconds for failover. But Anycast only works for stateless protocols — TCP connections can break during BGP route changes.

**Common misconception**: Candidates describe DNS routing without mentioning Anycast. In reality, Cloudflare, AWS CloudFront, and most modern CDNs use Anycast. Also, candidates forget that DNS-based geo-routing uses the resolver's IP, not the user's — if a user in Tokyo uses a DNS resolver in California, they get routed to a California PoP.

### Concept 2: Cache Hierarchy — Edge, Shield, Origin

**What it is**: A single layer of edge caches has a problem: if 200 PoPs all have a cache miss for the same content simultaneously, the origin gets 200 requests. A shield (mid-tier) cache sits between edges and origin. All edge cache misses for a content region route to one shield, which deduplicates requests to origin.

**How it applies here**: Edge PoPs are grouped into regions. Each region has a shield PoP (a larger, higher-capacity PoP). Cache miss at edge in Tokyo goes to shield in Tokyo (larger cache, higher hit rate), and only if the shield misses does the request go to origin. This turns 200 potential origin requests into 1.

**The math/mechanics**: Without shield: origin receives `PoP_count * miss_rate * QPS_per_PoP`. With 200 PoPs, 5% miss rate, 50K QPS per PoP = 500K origin requests/sec. With shield (10 shield PoPs, 2% shield miss rate): origin receives `10 * 0.02 * aggregate_QPS_per_shield_region`. If each shield serves 20 PoPs at 1M QPS combined = 200K origin requests/sec — a 60% reduction. And that's conservative — request deduplication at the shield (coalescing concurrent misses for the same URL) can reduce it further.

**Common misconception**: Candidates draw a single cache layer. The two-tier hierarchy is standard in every production CDN. Also, the "thundering herd" problem — when a popular cached item expires and 200 PoPs simultaneously request it from origin. The shield handles this with request coalescing: the first miss triggers an origin fetch, and subsequent concurrent misses wait for that fetch to complete.

### Concept 3: Cache Invalidation & Consistency

**What it is**: When content changes at the origin, how do you ensure all edge caches serve the updated content? This is the hardest problem in CDN design. Options: TTL-based expiration, active purge, and cache tags.

**How it applies here**: TTL-based is the default — set `Cache-Control: max-age=3600` and edges serve stale content for up to an hour. For immediate invalidation, the origin sends a purge request to the CDN's control plane, which fans out to all PoPs via a pub/sub system. Cache tags allow purging by group — "purge all images for product-123" — instead of individual URLs.

**The math/mechanics**: Purge fan-out: control plane publishes to a message bus, each PoP subscribes and deletes matching cache entries. With 200 PoPs and <100ms per-PoP processing, global purge completes in <30 seconds (limited by the slowest PoP). For cache tags, each edge maintains a reverse index: tag -> [list of cached URLs with that tag]. Purge by tag = lookup tag, delete all matching entries.

**Common misconception**: Candidates say "set a low TTL" for cache invalidation. Low TTLs reduce hit rate — a 10-second TTL means every 10 seconds, the edge re-fetches from origin. The right answer is long TTL + active purge. Also, purging is not instant — there's a propagation window where some edges have old content and some have new. This is an eventual consistency model, and the application must be designed to tolerate it (e.g., versioned URLs: `style.v2.css`).

### Concept 4: TLS Termination & Protocol Optimization

**What it is**: The edge PoP terminates the user's TLS connection (HTTPS), so the TLS handshake happens with a nearby server (1 RTT) instead of the distant origin (potentially 100+ ms RTT). This eliminates the latency penalty of the TLS handshake, which is 1-2 RTTs (3-4 RTTs for TLS 1.2 without resumption).

**How it applies here**: Edge servers hold TLS certificates for all served domains. With TLS 1.3, the handshake is 1 RTT. If the user is 5ms from the edge, that's 5ms for the handshake. Without CDN, the handshake with a 150ms-away origin would be 300ms (2 RTTs for TLS 1.2). That's 295ms saved on every new connection. HTTP/2 multiplexing and HTTP/3 (QUIC) further reduce latency.

**Common misconception**: Candidates focus only on caching and forget that a CDN's biggest latency win is often TLS termination, not caching. Even for cache misses, the user's TCP+TLS connection terminates at the edge, and the edge maintains a persistent, pre-warmed connection to the shield/origin. This turns a cold connection (3-4 RTTs to origin) into a warm one (1 RTT to edge + pre-established connection to origin).

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Cache Hit/Miss Flow End-to-End

**Interviewer**: "Walk me through exactly what happens when a user requests an image that's NOT in the edge cache."

**You**: "The user's browser resolves `cdn.example.com` via DNS. The CDN's Anycast IP routes the request to the nearest PoP — let's say Tokyo. The edge server terminates TLS (1 RTT, ~5ms for nearby user). It parses the HTTP request, computes a cache key (typically the full URL + `Vary` headers), and looks up the key in its local cache — first the in-memory hot cache (LRU, ~32GB RAM), then the SSD-based warm cache (~4TB). Cache miss on both.

The edge forwards the request to the shield PoP (Tokyo regional shield). The connection between edge and shield is persistent and pre-warmed — no TLS handshake needed, ~2ms added. The shield also checks its cache — miss again (this is the first request for this image globally).

The shield sends a request to the origin (customer's S3 bucket or web server). The connection to origin is also persistent. Origin responds with the image + cache headers (`Cache-Control: public, max-age=86400`). The shield caches the response and forwards it to the requesting edge. The edge caches it and responds to the user.

Total latency: 5ms (user to edge) + 2ms (edge to shield) + 50ms (shield to origin, assuming same continent) + origin processing = ~60-80ms for the full miss path. Subsequent requests from ANY edge in the Tokyo shield region hit the shield cache — 7ms total."

**Interviewer**: "How does the cache key work? What if the same URL should serve different content to different users?"

**You**: "The cache key is based on the URL plus the `Vary` header from the origin's response. If the origin sends `Vary: Accept-Encoding`, the CDN caches separate versions for gzip, brotli, and uncompressed. If `Vary: Accept-Language`, separate versions per language. The CDN typically normalizes `Accept-Encoding` to a small set (gzip, br, identity) to avoid cache fragmentation. For user-specific content — authenticated responses — the origin should send `Cache-Control: private` or `no-store`, and the CDN should not cache it. If you need edge caching of personalized content, you use Edge Side Includes (ESI) or fragment caching — cache the template at the edge, fetch only the personalized fragment from origin."

**Interviewer**: "What about the thundering herd problem? A popular cached item expires."

**You**: "Request coalescing at the shield layer. When the first cache miss arrives, the shield places a lock on that cache key and sends one request to origin. All subsequent concurrent requests for the same key wait on that lock — they don't generate additional origin requests. When the origin responds, the shield caches it and responds to all waiting requests simultaneously. We also use `stale-while-revalidate` — the edge serves the stale cached content to users while asynchronously fetching the fresh version from origin. Users get a fast response (stale but usually fine), and the cache is updated in the background."

**Interviewer**: "What happens if the origin is down?"

**You**: "Three strategies. First, `stale-if-error`: if the origin returns a 5xx or times out, serve the stale cached version with a header indicating it's stale. Most users won't notice. Second, origin failover: if the primary origin is down, route to a secondary origin (configured by the customer). Third, custom error pages cached at the edge. The CDN should NEVER return a raw 502/503 to the end user — it should always have a fallback. We track origin health with active health checks (every 5-10 seconds) and passively via error rate monitoring."

### Deep Dive Path 2: Cache Invalidation at Scale

**Interviewer**: "A customer deploys new code and needs all their cached CSS/JS purged in under 30 seconds worldwide. How?"

**You**: "The customer calls our Purge API: `POST /purge {"urls": [...]}` or `POST /purge {"tags": ["release-v2"]}`. The control plane validates the request and publishes purge events to a global message bus — we use Kafka with cross-region replication. Each PoP has a local consumer that processes purge events. On receiving a purge, the PoP deletes matching entries from its local cache (both RAM and SSD tiers). With 200 PoPs and Kafka replication latency of ~500ms cross-region, plus local processing of ~100ms, we complete global purge in under 5 seconds for most PoPs, under 30 seconds for the last PoP."

**Interviewer**: "What about cache tags? How do you implement 'purge all images for product ID 123'?"

**You**: "Each cached response can have associated tags. When the origin responds with `X-Cache-Tag: product-123, images`, the edge stores a reverse mapping: `product-123 -> [url1, url2, ...]` and `images -> [url1, url3, ...]`. This is stored in a lightweight local database (RocksDB or similar) on each edge server. When a tag purge arrives, the edge looks up all URLs for that tag and deletes them from cache. The trade-off is storage overhead for the reverse index — but with efficient encoding, it's small relative to the cached content itself."

**Interviewer**: "The purge fan-out failed for 5 PoPs. What now?"

**You**: "First, retries — the Kafka consumer retries failed purges with exponential backoff. Second, each PoP maintains a local purge log with sequence numbers. If a PoP was down during a purge, when it comes back online it replays all missed purge events from Kafka (consumers track their offset). Third, as a safety net, we have a global purge audit service that periodically checks (via sampling) whether edge caches have stale content post-purge. If it detects stale content, it triggers a targeted re-purge. The system is designed to be eventually consistent — it's acceptable for a few PoPs to serve stale content for an extra minute, as long as convergence happens."

### Deep Dive Path 3: Performance Optimization & Protocol

**Interviewer**: "How much latency does the CDN actually save? Break it down."

**You**: "Let's compare a user in Tokyo accessing an origin in US-East. Without CDN: DNS lookup (50ms), TCP handshake (150ms RTT), TLS 1.3 handshake (150ms RTT), HTTP request+response (150ms RTT) = ~500ms minimum. With CDN, cache hit: DNS (5ms, cached), TCP handshake (5ms to nearby edge), TLS 1.3 (5ms), HTTP request+response from edge cache (5ms) = ~20ms. That's a 25x improvement. Even a cache miss is faster: the user connects to edge in 15ms, then the edge uses a pre-warmed persistent connection to origin — saving the TCP+TLS handshake entirely. Cache miss becomes ~15ms (user to edge) + 150ms (edge to origin, pre-warmed) = ~165ms vs 500ms."

**Interviewer**: "What about HTTP/3 and QUIC? How does that change things?"

**You**: "QUIC combines the TCP and TLS handshakes into a single round trip — 1 RTT for new connections, 0 RTT for resumed connections. With 0-RTT, the user sends the HTTP request in the very first packet. For a nearby edge, this means the request arrives in 5ms with zero handshake overhead. QUIC also eliminates TCP's head-of-line blocking — with HTTP/2 over TCP, a single dropped packet blocks all streams. With QUIC, each stream is independently flow-controlled. This matters most on lossy networks (mobile, WiFi). Cloudflare reported 12% improvement in page load time after deploying QUIC. Reference: https://blog.cloudflare.com/http3-the-past-present-and-future/"

**Interviewer**: "How do you decide what to cache and what not to cache?"

**You**: "Three layers of decisions. First, respect the origin's `Cache-Control` headers — `no-store` means never cache, `private` means don't cache on shared caches (CDN), `public, max-age=N` means cache for N seconds. Second, the CDN customer can override these with CDN-specific rules — 'cache all `.jpg` for 24 hours regardless of origin headers.' Third, the CDN itself has intelligent defaults — never cache responses with `Set-Cookie` headers, never cache POST requests, and always cache 301/308 redirects. The key principle: the CDN should be transparent by default (respect origin headers) but allow customers to override when they know better."

---

## How Real Companies Built This

- **Cloudflare**: Runs one of the largest Anycast networks with 300+ PoPs. Uses a tiered cache (Argo Tiered Caching) to reduce origin load. Key innovation: Workers (edge compute) allow running custom JavaScript at the edge — moving logic closer to users. Blog: https://blog.cloudflare.com/

- **Netflix Open Connect**: Built their own CDN with custom hardware (Open Connect Appliances) placed inside ISP networks. Each appliance is a FreeBSD server with 100-200TB of SSD storage, serving 90Gbps. By being INSIDE the ISP, latency is <1ms. Netflix serves 15%+ of internet bandwidth during peak hours. Blog: https://openconnect.netflix.com/

- **Akamai**: Pioneered the CDN industry. Key contribution: consistent hashing for cache routing (the original research paper). Also pioneered "edge includes" (ESI) for caching fragments of dynamic pages.

- **AWS CloudFront**: Uses a "Regional Edge Cache" (their shield layer) between 400+ edge locations and the origin. Integrates deeply with S3 and Lambda@Edge for edge compute.

- **Key lesson**: Modern CDNs are not just caches — they're edge compute platforms. The trend is moving more logic to the edge (Cloudflare Workers, Lambda@Edge, Deno Deploy) to reduce origin dependency entirely.

---

## The Complete Reference Design

### API Design
```
# Cache Purge API
POST /v1/purge
Headers: Authorization: Bearer <api-key>
Request: {
  "type": "url",                       # url | tag | prefix
  "values": ["https://example.com/img/hero.jpg"],
  "soft_purge": false                   # true = mark stale, false = delete
}
Response 202: {
  "purge_id": "purge-abc123",
  "estimated_completion_seconds": 5
}

# Cache Purge Status
GET /v1/purge/purge-abc123
Response 200: {
  "status": "completed",
  "pops_purged": 200,
  "pops_pending": 0,
  "duration_seconds": 3.2
}

# CDN Configuration
PUT /v1/zones/{zone_id}/rules
Request: {
  "rules": [
    {
      "match": {"path": "*.jpg", "method": "GET"},
      "cache": {"ttl": 86400, "browser_ttl": 3600},
      "headers": {"X-Cache-Tag": "images"}
    }
  ]
}
```

### Edge Server Cache Architecture
```
+----------------------------------------------------------+
|  Edge Server                                              |
|                                                           |
|  +------------------+                                     |
|  | Hot Cache (RAM)  |  LRU, 32GB, <1ms lookup             |
|  | ~50K objects     |                                     |
|  +--------+---------+                                     |
|           | miss                                          |
|  +--------v---------+                                     |
|  | Warm Cache (SSD) |  LRU, 4TB, <5ms lookup              |
|  | ~10M objects     |                                     |
|  +--------+---------+                                     |
|           | miss                                          |
|  +--------v---------+                                     |
|  | Shield Request   |  Persistent conn to shield          |
|  | (with coalesce)  |  Dedup concurrent misses            |
|  +------------------+                                     |
|                                                           |
|  +------------------+                                     |
|  | Purge Listener   |  Kafka consumer for purge events    |
|  +------------------+                                     |
|                                                           |
|  +------------------+                                     |
|  | Tag Index        |  tag -> [url1, url2, ...]           |
|  | (RocksDB)        |                                     |
|  +------------------+                                     |
+----------------------------------------------------------+
```

### Key Algorithms
```python
import hashlib
import time
import threading
from collections import OrderedDict

class LRUCache:
    """Thread-safe LRU cache for edge server."""
    def __init__(self, max_size_bytes):
        self.max_size = max_size_bytes
        self.current_size = 0
        self.cache = OrderedDict()  # key -> (value, size, expiry, tags)
        self.lock = threading.Lock()
        self.tag_index = {}         # tag -> set of keys

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            value, size, expiry, tags = self.cache[key]
            if expiry and time.time() > expiry:
                self._evict(key)
                return None
            self.cache.move_to_end(key)
            return value

    def put(self, key, value, ttl=None, tags=None):
        size = len(value)
        expiry = time.time() + ttl if ttl else None
        with self.lock:
            if key in self.cache:
                self._evict(key)
            while self.current_size + size > self.max_size and self.cache:
                self._evict_lru()
            self.cache[key] = (value, size, expiry, tags or [])
            self.current_size += size
            for tag in (tags or []):
                self.tag_index.setdefault(tag, set()).add(key)

    def purge_by_tag(self, tag):
        with self.lock:
            keys = self.tag_index.pop(tag, set())
            for key in keys:
                self._evict(key)
            return len(keys)

    def _evict(self, key):
        if key in self.cache:
            _, size, _, tags = self.cache.pop(key)
            self.current_size -= size
            for tag in tags:
                if tag in self.tag_index:
                    self.tag_index[tag].discard(key)

    def _evict_lru(self):
        key, _ = self.cache.popitem(last=False)
        self._evict(key)


class RequestCoalescer:
    """Deduplicates concurrent cache miss requests to shield/origin."""
    def __init__(self):
        self.in_flight = {}  # cache_key -> Event
        self.results = {}    # cache_key -> response
        self.lock = threading.Lock()

    def fetch_or_wait(self, cache_key, fetch_fn):
        with self.lock:
            if cache_key in self.in_flight:
                event = self.in_flight[cache_key]
            else:
                event = threading.Event()
                self.in_flight[cache_key] = event
                # First requester — do the actual fetch
                threading.Thread(
                    target=self._do_fetch,
                    args=(cache_key, fetch_fn, event)
                ).start()

        event.wait(timeout=30)
        return self.results.get(cache_key)

    def _do_fetch(self, cache_key, fetch_fn, event):
        try:
            result = fetch_fn()
            self.results[cache_key] = result
        finally:
            event.set()
            with self.lock:
                self.in_flight.pop(cache_key, None)
```

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Edge servers | 10M QPS / 50K QPS per server | ~200 edge servers minimum |
| RAM per edge | 32GB hot cache | 32GB per server |
| SSD per edge | 4TB warm cache | 4TB NVMe per server |
| Shield servers | 20 shield PoPs x 10 servers each | 200 shield servers |
| Bandwidth per PoP | 10M QPS x 100KB avg / 200 PoPs | ~50Gbps per PoP |
| Total bandwidth | 200 PoPs x 50Gbps | ~10Tbps aggregate |
| Purge propagation | 200 PoPs via Kafka | < 5 seconds p99 |
| Origin protection | 10M QPS x 5% miss x shield dedup | ~50K origin requests/sec |
| DNS/Anycast | 200 PoPs advertising same /24 prefix | Standard BGP setup |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Understands basic caching, can describe edge->origin flow, knows about TTL | Designs a single-tier edge cache with origin fallback, correctly uses Cache-Control headers |
| Staff | Designs two-tier cache hierarchy, explains thundering herd mitigation, reasons about cache invalidation at scale, understands Anycast vs DNS routing | Adds shield layer with request coalescing, designs purge fan-out system, explains TLS termination latency savings, discusses HTTP/2 and QUIC trade-offs |
| Principal | Thinks about the CDN as a platform (edge compute), designs for multi-tenant isolation, reasons about economics (bandwidth costs, peering agreements), considers failure blast radius | Proposes edge compute for dynamic content, discusses ISP peering strategy (Netflix-style), designs graceful degradation (stale-if-error), considers how to handle DDoS at the edge |

---

## Red Flags & Common Mistakes
- **No shield/mid-tier layer**: A single edge cache layer causes origin overload. The two-tier hierarchy is table stakes.
- **Ignoring TLS/protocol optimization**: Caching is only half the CDN story. TLS termination at the edge is often the biggest latency win.
- **"Just set a low TTL" for invalidation**: Low TTL destroys hit rate. Long TTL + active purge is the answer.
- **No thundering herd mitigation**: When a popular item expires, request coalescing is essential.
- **Forgetting about the Vary header**: The same URL may need different cached versions for different Accept-Encoding, Accept-Language, etc.
- **Not mentioning origin shielding/health**: What happens when origin is down? stale-if-error, failover, custom error pages.
- **Over-engineering for dynamic content**: If the interviewer says "static CDN," don't spend time on edge compute. Ask first.
