# Design a Load Balancer

> **Companies**: Amazon (ELB), Google (Cloud LB), Cloudflare, Meta, Netflix, Uber | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: L4 vs L7 trade-offs, consistent hashing for session affinity, health checking under partial failures, how to handle millions of connections without state explosion, DSR (Direct Server Return) and why it matters

---

## The First 5 Minutes — Scoping & Technical Clarifications

1. **L4 (TCP/UDP) or L7 (HTTP/gRPC)?** This is the single most important question. L4 is stateless per-packet forwarding; L7 requires connection termination and protocol parsing. Totally different architectures.
2. **Scale targets?** Connections per second (CPS), concurrent connections, throughput (Gbps). A million CPS is very different from a million concurrent connections.
3. **Global or regional?** DNS-based global load balancing (like Route53) vs regional (like an ALB in one AZ). Global adds latency-based routing and failover.
4. **Health checking model?** Active (LB probes backends) vs passive (LB monitors response codes). What's the detection latency SLA — seconds or minutes?
5. **Session affinity requirements?** Stateless round-robin or sticky sessions (same client always goes to same backend)? Sticky sessions add complexity and reduce load distribution.
6. **TLS termination?** At the LB (offload crypto from backends) or pass-through to backends? TLS termination at LB requires managing certificates and has CPU cost.
7. **Multi-tenancy?** Shared LB infrastructure across customers (like AWS ALB) or dedicated instances?
8. **Failure domain?** What happens when the LB itself fails? HA pair, anycast, or distributed architecture?

### Working Assumptions

| Parameter | Value | Derivation |
|-----------|-------|------------|
| New connections/sec | 1,000,000 CPS | High-traffic web service |
| Concurrent connections | 10,000,000 | Avg connection duration 10 sec |
| Throughput | 100 Gbps | Mix of API calls and media |
| Backend servers | 1,000 | Across multiple AZs |
| Health check interval | 5 sec | Active TCP/HTTP checks |
| Failover detection | <10 sec | Time to remove unhealthy backend |
| p99 added latency | <1 ms (L4), <5 ms (L7) | LB processing overhead |
| TLS handshakes/sec | 500,000 | 50% of connections are new TLS |

**Bandwidth math**: 100 Gbps through a single server is impossible — a 100G NIC maxes at ~12.5 GB/s. We need distributed architecture: 10 LB nodes with 10G each, or use DSR so return traffic bypasses the LB entirely (asymmetric traffic — responses are 10-100x larger than requests).

---

## High-Level Design

```
         Clients (Internet)
              │
         ┌────▼────┐
         │  DNS /   │  ← Global: latency-based routing, geo
         │  Anycast │     Regional: returns LB VIP
         └────┬────┘
              │
    ┌─────────▼──────────┐
    │   Edge / L4 Tier   │  ← Stateless packet forwarding
    │  (ECMP + DSR)      │     Consistent hashing for affinity
    │  [LB Node 1..N]    │     Handles millions CPS
    └─────────┬──────────┘
              │
    ┌─────────▼──────────┐
    │   L7 Tier          │  ← HTTP parsing, TLS termination
    │  (Envoy/HAProxy)   │     Content-based routing
    │  [Proxy 1..M]      │     Rate limiting, auth
    └─────────┬──────────┘
              │
    ┌─────────▼──────────┐
    │   Backend Servers   │
    │  [Server 1..1000]   │
    └─────────────────────┘
```

**Why this architecture?** Two-tier LB (L4 + L7) separates concerns. The L4 tier handles raw throughput and connection distribution — it's extremely fast because it operates on packets without understanding HTTP. The L7 tier handles application-aware routing, TLS, and observability. This is exactly how AWS ELB works: NLB is L4, ALB is L7, and you can chain NLB -> ALB for both packet efficiency and L7 features.

---

## Core Concepts Deep Dive

### Concept 1: L4 Load Balancing — Packet-Level Forwarding

**What it is**: The LB receives TCP SYN, makes a backend selection, and rewrites packet headers to forward traffic. Three modes: (1) NAT — rewrite destination IP to backend, source IP to LB (LB sees all traffic both ways). (2) DSR (Direct Server Return) — rewrite destination MAC to backend, backend responds directly to client (LB only sees inbound traffic). (3) Tunneling (IP-in-IP) — encapsulate original packet in a new IP packet to the backend.

**How it applies**: DSR is critical for throughput. In a typical web request, the response is 10-100x larger than the request (think: 500-byte request, 50 KB HTML response). With NAT, the LB must handle 101x the traffic. With DSR, the LB only handles 1x — responses go directly from backend to client. This is how Maglev (Google) and Katran (Meta) work.

**The math**: 100 Gbps of response traffic with NAT requires LB to handle 100 Gbps. With DSR, if requests are 1/50th of responses, the LB handles only 2 Gbps. That's a 50x reduction in LB throughput requirements.

**Common misconception**: "DSR means the backend needs to know the client IP." Not exactly — with DSR, the backend receives packets with the VIP as the destination IP (via MAC rewriting or tunneling). The backend must be configured to accept traffic for the VIP on a loopback interface, and it responds directly to the client's IP. The client never knows the backend's real IP.

### Concept 2: Consistent Hashing for Connection Affinity

**What it is**: Map each connection (identified by client IP + port, or some header) to a backend using a hash ring. When backends are added/removed, only 1/N of connections remap. This provides "sticky" routing without per-connection state on the LB.

**How it applies**: Without consistent hashing, adding a backend remaps ~all connections (modulo N changes). With consistent hashing + virtual nodes, adding 1 backend to 100 remaps only ~1% of connections. For long-lived WebSocket connections, this prevents mass disconnection during scaling events.

**The math**: Google's Maglev uses a custom consistent hashing table (not ring-based) that guarantees minimal disruption AND equal load distribution. Each backend is assigned positions in a fixed-size lookup table (65,537 entries). When a backend is removed, only its entries are reassigned. Lookup is O(1) — just hash the 5-tuple and index into the table.

**Common misconception**: "Consistent hashing gives perfect load distribution." It doesn't — some backends get more virtual nodes in popular hash ranges. Maglev-style tables address this by ensuring exactly equal slot allocation across backends.

### Concept 3: Health Checking — The Subtlety of "Is This Backend Healthy?"

**What it is**: Active health checks (LB probes backend periodically) vs passive (LB monitors real traffic responses). Both have failure modes.

**How it applies**: Active: LB sends GET /health every 5 seconds. After 3 consecutive failures (15 seconds), mark backend unhealthy. Problem: the health endpoint might succeed while the application path is broken (database connection pool exhausted). Passive: LB monitors real 5xx responses. After 5 errors in 10 seconds, mark unhealthy. Problem: low-traffic backends might take minutes to accumulate enough errors. Best practice: combine both. Active for basic liveness, passive for application health.

**The math**: With 1,000 backends and 5-second health check intervals, the LB sends 200 health checks/sec (plus response processing). Trivial for the LB, but if health checks go over the network, each check adds ~1ms of network time. Total: 200ms of health check work per second across all backends.

**Common misconception**: "A backend is either healthy or unhealthy." Reality: backends can be partially degraded — serving some requests slowly, returning errors for specific endpoints, or running out of memory gradually. Sophisticated LBs use "outlier detection" (Envoy's term): track per-backend p99 latency and error rate, temporarily remove backends that are statistically worse than peers, even if active health checks pass.

### Concept 4: Connection Draining and Graceful Removal

**What it is**: When a backend is being decommissioned (deploy, scale-down), stop sending new connections but let existing connections finish. Without draining, existing requests get RST (connection reset).

**How it applies**: The LB marks the backend as "draining" — it's removed from the active pool for new connections but existing connections continue until they complete or a timeout expires (typically 30-300 seconds). For HTTP/2, this is especially important because a single TCP connection carries many multiplexed streams.

**The math**: With 10M concurrent connections across 1,000 backends, each backend has ~10K connections. If average request takes 200ms, draining takes 200ms for most connections. But long-polling/WebSocket connections might last hours. A 5-minute drain timeout catches 99.9% of connections. The remaining 0.1% get RST — acceptable for most applications.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: L4 Data Path and Scaling

**Interviewer**: "A packet arrives at your load balancer from a client. Walk me through exactly what happens at L4."

**You**: The client's TCP SYN arrives at the LB's VIP (Virtual IP), let's say `203.0.113.10:443`. The network delivers it to one of our LB nodes via ECMP (Equal-Cost Multi-Path) — the router hashes the 5-tuple (src IP, src port, dst IP, dst port, protocol) and picks an LB node. The LB node receives the SYN, hashes the 5-tuple against our consistent hash table to select a backend, say `10.0.1.50`. In DSR mode, the LB rewrites the destination MAC address to the backend's MAC (or encapsulates via IP-in-IP if cross-subnet) and forwards. The SYN reaches the backend, which has the VIP configured on its loopback interface, so it accepts the connection. The backend's SYN-ACK goes directly to the client — it bypasses the LB entirely because the source IP is the VIP (which the backend is configured to use). All subsequent data packets from the client follow the same ECMP + consistent hash path to the same LB node, which forwards to the same backend.

**Interviewer**: "What happens if that LB node fails? ECMP will rehash and send packets to a different LB node that doesn't know about the existing connection."

**You**: This is the key problem with stateless L4 LBs. When an LB node fails, ECMP redistributes its traffic to remaining nodes. These nodes have no connection state — they'll hash the 5-tuple and likely pick a different backend, breaking existing connections. Three solutions: (1) **Connection tracking via shared state**: All LB nodes share a connection table (but this adds latency and complexity). (2) **Consistent hashing guarantee**: If all LB nodes use the same consistent hash table, they'll independently map the same 5-tuple to the same backend — even if the handling LB node changes. This is Maglev's approach. (3) **Connection state replication**: Primary/backup pairs where the backup receives all connection state. Google's Maglev solution is elegant: since the hash table is deterministic and identical on all nodes, any node can handle any packet and get the same result.

**Interviewer**: "But what if a backend fails? The consistent hash maps to a dead backend."

**You**: When health checks detect a backend failure, we update the consistent hash table on all LB nodes (propagated via a configuration push or gossip). The failed backend's hash slots are redistributed to remaining backends. For new connections, they immediately go to healthy backends. For existing connections that were going to the dead backend — those are already broken at the TCP level (the backend sent RST or timed out). The client will reconnect and the new connection will hash to a healthy backend. The vulnerability window is between when the backend dies and when health checks detect it (5-15 seconds with typical settings). During this window, packets go to a dead backend and get dropped. This is why passive health checking (monitoring real traffic for failures) complements active checks — it can detect failures in seconds rather than waiting for the next health check interval.

**Interviewer**: "How do you handle connection table overflow at 10M concurrent connections?"

**You**: With DSR, the LB doesn't need to track connections at all — it's stateless packet forwarding. Each packet is independently hashed and forwarded. The only state is the consistent hash table (fixed size, ~256 KB for 65K entries) and the backend health map. Memory usage is O(backends), not O(connections). This is why DSR is essential at scale. If we're doing NAT (which requires connection tracking for return traffic), the connection table at 10M entries with ~100 bytes per entry = 1 GB — fits in memory but requires careful management of timeouts and cleanup. Linux conntrack can handle this but becomes CPU-bound at ~2M entries/sec of new connections.

### Deep Dive Path 2: L7 Load Balancing and Advanced Routing

**Interviewer**: "When would you choose L7 over L4? What's the actual cost?"

**You**: L7 when you need: content-based routing (route /api/* to backend pool A, /static/* to CDN), header inspection (A/B testing based on cookies), TLS termination (centralized cert management), request-level load balancing (HTTP/2 multiplexes many requests on one connection — L4 can only balance at connection level, so one connection = one backend, even if it carries 100 concurrent requests). The cost: L7 requires TCP termination — the LB maintains two TCP connections (client-to-LB and LB-to-backend), copies data between them at the application layer. This is ~10x more CPU than L4 packet forwarding. A single Envoy proxy can handle ~50K requests/sec at L7 vs ~1M packets/sec at L4 on similar hardware.

**Interviewer**: "Walk me through how an L7 LB handles HTTP/2 connection coalescing and per-request load balancing."

**You**: The client opens a single HTTP/2 connection to the LB. The LB terminates TLS, parses HTTP/2 frames. Each HTTP/2 stream (request) is independently routed to potentially different backends. The LB maintains a pool of HTTP/2 connections to each backend. When a new request arrives, the LB picks a backend (round-robin, least-connections, or consistent hash on a header), selects a backend connection from the pool, and sends the request on a new stream. This is fundamentally different from L4: at L4, all streams on a connection go to the same backend because L4 only sees the TCP connection, not individual HTTP/2 streams. This is why Kubernetes switched from iptables-based service routing to considering L7 approaches for gRPC services — gRPC uses HTTP/2, and L4 load balancing creates severe hotspots when clients maintain long-lived gRPC connections.

**Interviewer**: "How do you handle WebSocket upgrades and long-lived connections at L7?"

**You**: WebSocket starts as an HTTP/1.1 Upgrade request. The L7 LB sees the Upgrade header, selects a backend, forwards the upgrade request, and if the backend responds with 101 Switching Protocols, the LB switches to tunnel mode — it stops parsing HTTP and just forwards raw TCP frames bidirectionally. The challenge: each WebSocket connection consumes a backend connection from the LB's pool. With 1M concurrent WebSockets, the LB maintains 1M client connections + 1M backend connections = 2M file descriptors. At ~1 KB memory per connection, that's 2 GB just for connection state. The LB needs to be sized for concurrent connections, not just requests/sec. This is why separate LBs for WebSocket traffic are common — the resource profile is completely different from request/response HTTP.

**Interviewer**: "How would you implement rate limiting at the L7 LB?"

**You**: Two approaches: (1) Local rate limiting — each LB node maintains per-client token buckets. Simple, fast (no network calls), but inaccurate in a distributed LB: if 10 LB nodes each allow 100 req/s for a client, the effective limit is 1,000 req/s. (2) Global rate limiting — LB nodes call a central rate limit service (Redis-backed) before forwarding. Accurate, but adds 1-2ms latency per request. The practical solution: local rate limiting with a safety margin (set local limit to 1/N of global limit, where N is LB nodes) for fast rejections, plus asynchronous reporting to a global counter for accuracy. If the global counter shows a client is over limit, push a block rule to all LB nodes. This is how Envoy's rate limit filter works — local fast-path, global slow-path.

### Deep Dive Path 3: Global Load Balancing and Anycast

**Interviewer**: "How would you extend this to global load balancing across regions?"

**You**: Two levels: DNS-based and anycast. DNS-based: Route53/Cloud DNS returns different LB VIPs based on the client's location (latency-based routing). The client resolves `api.example.com` and gets the nearest region's VIP. Problem: DNS TTL means failover takes minutes, and DNS doesn't know if the target region is healthy. Anycast: advertise the same VIP from all regions via BGP. The internet's routing protocols naturally send clients to the nearest region. Failover is automatic — if a region withdraws the BGP route, traffic shifts to the next nearest region in seconds. Problem: anycast is unreliable for TCP — a BGP route change mid-connection sends packets to a different region (connection breaks). Solution: use anycast for the initial connection, then redirect/pin to a specific regional IP. Google's GCLB does this: anycast for the frontend, GRE tunnel to the backend region.

**Interviewer**: "How does AWS Global Accelerator work differently?"

**You**: Global Accelerator gives you two anycast IPs. Client connects to the nearest AWS edge location via anycast. The edge terminates the TCP connection and forwards traffic to the target region over AWS's private backbone (not the public internet). This provides two benefits: (1) the TCP connection is between the client and the nearby edge, so mid-connection BGP changes don't break it, and (2) inter-region traffic uses AWS's backbone which has lower latency and less packet loss than the public internet. Failover: if the target region is unhealthy, the edge redirects to a backup region. Detection time is 10-30 seconds (health check interval). The architecture is essentially anycast + TCP termination at the edge + private backbone tunneling.

**Interviewer**: "What about geo-partitioning requirements where data must stay in a specific region?"

**You**: Global LB with geo-fencing. DNS or anycast routes clients to their legal region, and the LB enforces that EU clients always hit EU backends, even if US backends have lower latency. Implementation: the L7 LB inspects the client's GeoIP (from source IP database), adds an `X-Client-Region` header, and routes to the appropriate backend pool. For failover, if the EU region is down, we have two choices: (1) fail closed — return 503 (data sovereignty requirement met, availability sacrificed), or (2) fail open — route to another region with degraded service (show cached data, no writes). The choice depends on regulatory requirements. GDPR typically requires option 1 for write operations.

---

## How Real Companies Built This

- **Google Maglev**: Software-defined L4 LB using consistent hashing. Each Maglev machine handles 10M+ packets/sec. Uses ECMP + identical hash tables for stateless failover. [Maglev Paper — NSDI 2016](https://research.google/pubs/pub44824/)
- **Meta Katran**: Open-source XDP/BPF-based L4 LB. Processes packets in kernel space without context switches. Handles 10M+ packets/sec per machine. [Katran GitHub](https://github.com/facebookincubator/katran)
- **Netflix Zuul**: L7 gateway handling edge routing, A/B testing, canary deployments. Written in Java with Netty. [Netflix Tech Blog — Zuul 2](https://netflixtechblog.com/zuul-2-the-netflix-journey-to-asynchronous-non-blocking-systems-45947377fb5c)
- **Cloudflare Unimog**: Global L4 LB using anycast + XDP. Handles DDoS at the edge without centralized state. [Cloudflare Blog — Unimog](https://blog.cloudflare.com/unimog-cloudflares-edge-load-balancer/)
- **Envoy Proxy**: L7 proxy used by Istio, AWS App Mesh, and others. xDS API for dynamic configuration. [Envoy Architecture](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/arch_overview)
- **AWS ELB Architecture**: NLB (L4, 100M+ flows) → ALB (L7, HTTP routing) → target groups. [AWS re:Invent — ELB Deep Dive](https://www.youtube.com/watch?v=VIgAT7vjol8)

---

## The Complete Reference Design

### API Design

```
# LB Management API
POST   /v1/load-balancers
{
  "name": "api-lb",
  "type": "L7",                    # L4 | L7
  "listeners": [
    {"port": 443, "protocol": "HTTPS", "certificate_arn": "..."}
  ],
  "default_target_group": "tg-api-servers"
}

POST   /v1/target-groups
{
  "name": "tg-api-servers",
  "protocol": "HTTP",
  "port": 8080,
  "health_check": {
    "path": "/health",
    "interval_sec": 5,
    "healthy_threshold": 2,
    "unhealthy_threshold": 3,
    "timeout_sec": 3
  },
  "algorithm": "LEAST_CONNECTIONS",  # ROUND_ROBIN | LEAST_CONNECTIONS | CONSISTENT_HASH
  "stickiness": {
    "enabled": true,
    "type": "COOKIE",
    "ttl_sec": 3600
  }
}

POST   /v1/target-groups/{id}/targets
{ "ip": "10.0.1.50", "port": 8080, "weight": 100 }

# Routing rules (L7)
POST   /v1/load-balancers/{id}/rules
{
  "priority": 10,
  "conditions": [{"field": "path", "values": ["/api/*"]}],
  "actions": [{"type": "forward", "target_group": "tg-api-servers"}]
}
```

### Database Schema

```sql
CREATE TABLE load_balancers (
    id           UUID PRIMARY KEY,
    name         VARCHAR(256) NOT NULL,
    type         VARCHAR(4) NOT NULL,  -- L4 | L7
    vip          INET NOT NULL,
    state        VARCHAR(16) DEFAULT 'provisioning',
    created_at   TIMESTAMP NOT NULL,
    region       VARCHAR(32) NOT NULL
);

CREATE TABLE target_groups (
    id              UUID PRIMARY KEY,
    name            VARCHAR(256) NOT NULL,
    protocol        VARCHAR(8) NOT NULL,
    port            INT NOT NULL,
    algorithm       VARCHAR(32) DEFAULT 'ROUND_ROBIN',
    health_path     VARCHAR(256),
    health_interval INT DEFAULT 5,
    drain_timeout   INT DEFAULT 300
);

CREATE TABLE targets (
    target_group_id UUID NOT NULL REFERENCES target_groups(id),
    ip              INET NOT NULL,
    port            INT NOT NULL,
    weight          INT DEFAULT 100,
    health_status   VARCHAR(16) DEFAULT 'unknown',
    last_health_check TIMESTAMP,
    PRIMARY KEY (target_group_id, ip, port)
);

CREATE TABLE routing_rules (
    lb_id           UUID NOT NULL REFERENCES load_balancers(id),
    priority        INT NOT NULL,
    condition_json  JSONB NOT NULL,
    target_group_id UUID NOT NULL REFERENCES target_groups(id),
    PRIMARY KEY (lb_id, priority)
);
```

### Key Algorithms — Maglev Consistent Hashing

```python
class MaglevHashTable:
    """Google Maglev-style consistent hash table.
    Guarantees minimal disruption + equal distribution."""

    TABLE_SIZE = 65537  # prime number

    def __init__(self, backends: list[str]):
        self.backends = backends
        self.table = self._build_table()

    def _build_table(self) -> list[int]:
        n = len(self.backends)
        # Each backend gets a permutation of table positions
        permutations = []
        for backend in self.backends:
            offset = hash(backend + "_offset") % self.TABLE_SIZE
            skip = hash(backend + "_skip") % (self.TABLE_SIZE - 1) + 1
            perm = [(offset + j * skip) % self.TABLE_SIZE
                    for j in range(self.TABLE_SIZE)]
            permutations.append(perm)

        table = [-1] * self.TABLE_SIZE
        next_idx = [0] * n  # next position in each backend's permutation
        filled = 0

        while filled < self.TABLE_SIZE:
            for i in range(n):
                # Find next empty slot for backend i
                while table[permutations[i][next_idx[i]]] != -1:
                    next_idx[i] += 1
                table[permutations[i][next_idx[i]]] = i
                filled += 1
                if filled >= self.TABLE_SIZE:
                    break
        return table

    def lookup(self, key: str) -> str:
        idx = hash(key) % self.TABLE_SIZE
        return self.backends[self.table[idx]]
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| L4 LB nodes | 100 Gbps / 10 Gbps per node (DSR) | 10 nodes (2 Gbps actual with DSR) |
| L7 proxy nodes | 1M req/s / 50K per Envoy | 20 Envoy instances |
| TLS handshakes | 500K/s / 20K per core (RSA-2048) | 25 CPU cores for TLS |
| Connection memory (L7) | 10M conns x 2 (client+backend) x 1 KB | 20 GB total across proxies |
| Health check bandwidth | 1000 backends x 200 B/check / 5s | 40 KB/s (negligible) |
| Config store | Backend list, rules, certs | <1 GB, replicated 3x |

---

## Senior vs Staff vs Principal

| Aspect | Senior (E5/L5) | Staff (E6/L6) | Principal (L66+) |
|--------|----------------|----------------|-------------------|
| **Architecture** | Clean L4/L7 separation, understands NAT vs DSR | Designs consistent hashing for connection affinity, explains ECMP | Designs global anycast + TCP termination at edge, cross-region failover |
| **Scale** | Correct capacity math for connections and throughput | Explains XDP/BPF for kernel-bypass packet processing, DPDK | Designs multi-tier LB fabric for 100M+ concurrent connections |
| **Health checking** | Active health checks with threshold | Outlier detection (p99 latency, error rate), partial degradation handling | Designs cascading health systems, global health aggregation, blast radius control |
| **Operations** | Rolling backend deploys with drain | Connection draining across L4+L7, zero-downtime LB upgrades | Designs LB-as-a-service platform with per-tenant isolation and SLA guarantees |

---

## Red Flags & Common Mistakes

1. **Not distinguishing L4 from L7** — These are fundamentally different systems. Conflating them shows shallow understanding.
2. **Ignoring DSR** — At high throughput, NAT-mode LB becomes the bottleneck. Not mentioning DSR for L4 is a miss.
3. **"Use round-robin"** — Round-robin with no health checking, no connection awareness, no affinity. This is a 5-minute answer, not a system design.
4. **No failure story for the LB itself** — The LB is a single point of failure. How does it survive failures? ECMP + consistent hashing or active/passive failover?
5. **Ignoring the connection draining problem** — Rolling deploys without drain break in-flight requests. This is a production-critical issue.
6. **Not understanding ECMP rehashing** — When an LB node fails, ECMP redistributes ALL flows, not just the failed node's. This breaks connections unless you use consistent hashing.
7. **"Just put it behind DNS"** — DNS has TTL caching (minutes to hours). It's not a substitute for packet-level load balancing.
