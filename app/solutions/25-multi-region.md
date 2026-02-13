# Design a Multi-Region Deployment System

> **Companies**: Amazon, Google, Meta, Netflix, Uber, Stripe, Cloudflare | **Level**: Staff/Principal (rarely Senior — this is a platform architecture question) | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: CAP theorem applied to real architectures, cross-region data replication trade-offs, failover mechanics and blast radius control, how to reason about latency budgets across regions, understanding of DNS-based routing, Global Accelerator, and regional isolation

---

## The First 5 Minutes — Scoping & Technical Clarifications

1. **Active-active or active-passive?** Active-active: all regions serve traffic simultaneously (harder, better UX). Active-passive: one primary region, others are standby (simpler, wastes standby resources).
2. **Data consistency model?** Strong consistency across regions (high latency) vs eventual consistency (data divergence risk)? This is THE fundamental trade-off.
3. **What data needs replication?** User data (must be replicated), session data (can be regional), cache data (can be rebuilt). Classifying data by replication needs is critical.
4. **Failover RTO/RPO?** RTO (Recovery Time Objective): how fast must we failover? RPO (Recovery Point Objective): how much data loss is acceptable? RTO=5 min + RPO=0 is very different from RTO=1 hour + RPO=1 hour.
5. **Which regions?** US-East, US-West, EU, APAC? Each additional region multiplies complexity.
6. **Regulatory constraints?** GDPR (EU data must stay in EU), data residency laws. This constrains where data can be replicated.
7. **Services or infrastructure?** Are we designing the platform that enables services to go multi-region, or designing a specific service to be multi-region?
8. **Current architecture?** Single-region monolith migrating to multi-region, or greenfield multi-region design?

### Working Assumptions

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Regions | 3 (US-East, US-West, EU-West) | Global user base |
| Total QPS | 1,000,000 | Split ~40/30/30 across regions |
| Inter-region latency | US-East <-> US-West: 70ms, US <-> EU: 90ms | Real AWS numbers |
| Failover RTO | <5 minutes | Customer SLA commitment |
| Failover RPO | <10 seconds | Async replication lag |
| Data size per region | 50 TB (primary database) | Active dataset in PostgreSQL/DynamoDB |
| Replication bandwidth | 500 MB/s cross-region | Sustained, for async replication |
| Services | 50 microservices | Varying criticality tiers |

**Latency math**: A synchronous cross-region write (US-East -> EU for strong consistency) adds 2 x 90ms = 180ms (round-trip) to every write. At p50=5ms for a local write, this is a 36x latency increase. This is why most multi-region systems use async replication with eventual consistency.

---

## High-Level Design

```
                    ┌─────────────────────────┐
                    │   Global Traffic Manager │
                    │   (Route53 / Global      │
                    │    Accelerator)           │
                    │                          │
                    │   Latency-based routing  │
                    │   Health check failover  │
                    └────────┬────────┬────────┘
                             │        │
              ┌──────────────┘        └──────────────┐
              │                                      │
   ┌──────────▼──────────┐            ┌──────────────▼──────────┐
   │   REGION: US-EAST    │            │   REGION: EU-WEST       │
   │   (primary for US    │◄──────────►│   (primary for EU       │
   │    users' data)      │  async     │    users' data)         │
   │                      │  repl.     │                         │
   │ ┌──────────────────┐ │            │ ┌──────────────────────┐│
   │ │ API Gateway      │ │            │ │ API Gateway          ││
   │ │ (regional ALB)   │ │            │ │ (regional ALB)       ││
   │ └────────┬─────────┘ │            │ └────────┬─────────────┘│
   │          │            │            │          │              │
   │ ┌────────▼─────────┐ │            │ ┌────────▼─────────────┐│
   │ │ Service Mesh     │ │            │ │ Service Mesh         ││
   │ │ (50 services)    │ │            │ │ (50 services)        ││
   │ └────────┬─────────┘ │            │ └────────┬─────────────┘│
   │          │            │            │          │              │
   │ ┌────────▼─────────┐ │            │ ┌────────▼─────────────┐│
   │ │ Data Layer       │ │            │ │ Data Layer           ││
   │ │ - RDS (primary)  │──async──────►│ │ - RDS (replica)      ││
   │ │ - DynamoDB Global│◄─────────────│ │ - DynamoDB Global    ││
   │ │ - Redis (local)  │ │            │ │ - Redis (local)      ││
   │ │ - Kafka (MirrorM)│◄─────────────│ │ - Kafka (MirrorMaker)││
   │ └──────────────────┘ │            │ └──────────────────────┘│
   └──────────────────────┘            └─────────────────────────┘
```

**Why this architecture?** Regional isolation with async replication. Each region is a fully functional deployment that can serve all traffic independently (active-active). Data is partitioned by user home region: US users' primary data lives in US-East, EU users' in EU-West. Each region has a read replica of the other regions' data. Writes go to the user's home region; reads can be served from the local region's replica. This gives: (1) low-latency reads everywhere (local replica), (2) low-latency writes to home region (no cross-region round-trip), (3) eventual consistency for cross-region reads (replication lag ~1-10 seconds), (4) clean failover (promote replica to primary).

---

## Core Concepts Deep Dive

### Concept 1: Data Replication Strategies — The CAP Trade-off in Practice

**What it is**: Three replication models: (1) **Synchronous**: Write to all regions before acking client. Strong consistency, high latency. (2) **Asynchronous**: Write to local region, ack client, replicate in background. Low latency, eventual consistency, possible data loss on failover. (3) **Semi-synchronous**: Write to local region + at least one remote region before acking. Middle ground.

**How it applies**: Most production systems use async for most data, with sync or semi-sync for critical data. Example at Stripe: payment transactions use synchronous cross-region replication (can't lose a payment), but session data and caches use async (losing a session is annoying but not catastrophic). The classification:

| Data Type | Replication | Consistency | Example |
|-----------|-------------|-------------|---------|
| Financial transactions | Synchronous | Strong | Payment records |
| User account data | Semi-synchronous | Strong within home region | Profile, settings |
| Session data | None (regional only) | Local only | Login sessions |
| Cache | None (rebuilt) | Eventual | Redis, CDN |
| Analytics events | Async | Eventual | Click streams |

**The math**: Synchronous replication across US-East <-> EU: +180ms per write. At 100K writes/sec, that's 100K x 180ms = 18,000 seconds of write latency per second — 18K concurrent write transactions in flight at any time. This requires careful connection pool sizing and timeout management. Semi-synchronous (ack after local + 1 remote): +70ms (US-East to US-West) — much more tolerable.

**Common misconception**: "Use DynamoDB Global Tables, it handles everything." DynamoDB Global Tables provide async replication with last-writer-wins conflict resolution. For most data this is fine, but for financial data (balance updates) or counters, last-writer-wins causes data loss. You need application-level conflict resolution (CRDTs, version vectors) or a different replication strategy for those data types.

### Concept 2: Traffic Routing — DNS, Anycast, and Regional Failover

**What it is**: Global traffic routing determines which region handles each user's request. Three approaches: (1) DNS-based (Route53 latency-based routing), (2) Anycast (Global Accelerator), (3) Application-layer routing (L7 gateway inspects request and routes).

**How it applies**: DNS-based: Route53 returns the IP of the nearest region's ALB based on the client's DNS resolver location. Failover: Route53 health checks the ALB endpoint; if unhealthy, it removes the region from DNS responses. Propagation time: DNS TTL (60 seconds) + client cache = 1-5 minutes failover. Global Accelerator: Two anycast IPs, client connects to nearest AWS edge location. The edge routes to the target region over AWS backbone. Failover: 10-30 seconds (health check detection, no DNS propagation needed). The edge re-routes to the next healthy region.

For EKS specifically: each region has an EKS cluster with its own ALB Ingress Controller. Route53 weighted/latency-based routing distributes traffic across regional ALBs. The EKS Service Mesh (Istio or App Mesh) handles inter-service routing within each region. Cross-region service calls go through a regional gateway (not direct pod-to-pod) to maintain isolation.

**The math**: Route53 health checks: 10-second interval, 3 failures to mark unhealthy = 30 seconds detection. DNS TTL of 60 seconds means clients see the change within 60 seconds of the DNS update. Total failover: ~90 seconds best case, ~5 minutes worst case (cached DNS clients). Global Accelerator: 10-second health check interval, immediate re-routing = ~30 seconds total failover.

**Common misconception**: "Set DNS TTL to 0 for instant failover." Even with TTL=0, many clients (browsers, OS resolvers) cache DNS for 30-60 seconds regardless of TTL. And TTL=0 massively increases DNS query volume. The practical minimum TTL is 30-60 seconds.

### Concept 3: Blast Radius Control — Why Regions Must Be Isolated

**What it is**: A failure in one region must not cascade to other regions. This requires: no cross-region synchronous dependencies, independent deployment pipelines per region, separate resource quotas, and circuit breakers on cross-region calls.

**How it applies**: Anti-patterns that create cross-region coupling: (1) Shared centralized database that all regions write to — if the DB's region fails, all regions fail. (2) Cross-region synchronous service calls in the request path — if the remote region is slow, the local region's latency increases. (3) Shared global configuration service — a misconfiguration propagates globally instantly.

The design principle: each region must be able to operate in "island mode" — completely disconnected from other regions for hours. Reads serve from local replicas (stale but available). Writes to the local region's data succeed. Writes that require cross-region coordination queue locally and sync when connectivity returns.

**The math**: If one region has a 1% chance of a 10-minute outage per month, and regions are independent, the probability of a global outage (all 3 regions down) is (0.01)^3 = 10^-6 per month. If regions are coupled (shared database), the probability of global outage ≈ 0.01 per month. Independence gives 10,000x better global availability.

**Common misconception**: "Active-active means requests can hit any region." For writes, the request should go to the data's home region. If a US user's write goes to EU (because DNS mis-routed), it must cross-region to US-East where the user's primary data lives. Active-active for reads, home-region routing for writes.

### Concept 4: Database Replication Strategies for Multi-Region

**What it is**: Different database technologies offer different multi-region capabilities. The choice depends on consistency needs, operational complexity, and cost.

**How it applies**:
- **Amazon Aurora Global Database**: Async replication from primary region to up to 5 read-replica regions. Replication lag <1 second typically. Failover promotes a replica to primary (RPO <1 sec, RTO <1 min). Single-writer model — writes go to one region only.
- **DynamoDB Global Tables**: Active-active multi-region. Writes in any region, async replication to all others. Last-writer-wins conflict resolution. Good for data that doesn't have write conflicts (user profiles, preferences).
- **CockroachDB / Google Spanner**: Synchronous replication with distributed transactions (TrueTime / hybrid logical clocks). Strong consistency everywhere, but write latency includes cross-region round-trip. Best for financial systems where consistency is non-negotiable.
- **Kafka with MirrorMaker 2**: Event stream replication across regions. Each region has its own Kafka cluster. MirrorMaker 2 asynchronously replicates topics between clusters. Consumers in each region read from their local cluster.

**The math**: Aurora Global Database: ~100MB/s replication bandwidth for 10K writes/sec at 10KB per write. Cross-region bandwidth cost: ~$0.02/GB = ~$173K/year for continuous 100MB/s replication. Spanner: write latency = max(inter-region RTT) / 2 for Paxos quorum = ~45ms for US-East/US-West/EU (quorum at 2 of 3, closest two are US-East + US-West at 70ms RTT). This is much better than the 180ms for synchronous replication to all regions.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Failover Mechanics

**Interviewer**: "US-East goes down completely — AZ-level outage affecting all three AZs. Walk me through the failover."

**You**: The failover has five phases: (1) **Detection** (0-30 seconds): Route53 health checks fail for the US-East ALB. Three consecutive failures at 10-second intervals = 30 seconds. Global Accelerator detects faster: 10-15 seconds. (2) **Traffic rerouting** (30-90 seconds): Route53 removes US-East from DNS responses. Clients with cached DNS continue hitting US-East (TCP timeout, retry). New DNS lookups resolve to US-West. Global Accelerator immediately re-routes all new connections to US-West. (3) **Database promotion** (1-3 minutes): Aurora's global database promotes the US-West read replica to primary. This is a manual or automated action via RDS failover API. RPO: ~1 second of writes may be lost (async replication lag). (4) **Configuration update** (1-2 minutes): Services in US-West must know they're now the primary for US users' data. This is done via a regional configuration flag (e.g., SSM Parameter Store or a ConfigMap in EKS). Services read the flag and adjust their behavior — they start accepting writes for US users instead of proxying to US-East. (5) **Stabilization** (2-5 minutes): US-West absorbs the additional traffic. Auto Scaling Groups (ASGs) and EKS Horizontal Pod Autoscaler (HPA) scale up pods and nodes to handle the increased load. Pre-provisioned capacity (warm pool) reduces scaling time.

Total RTO: ~3-5 minutes from outage to full traffic serving in US-West.

**Interviewer**: "What about the RPO? You said ~1 second of data loss. What does that mean concretely?"

**You**: With Aurora Global Database, async replication lag is typically 100-500ms but can spike to seconds during high write volume. When US-East fails, any writes that were committed in US-East but not yet replicated to US-West are lost. Concretely: if we do 10K writes/sec and the replication lag was 1 second, we lose 10K write transactions. These could be user profile updates, order placements, payment records. For payments, this is unacceptable — which is why payment writes use a different pattern: the payment service writes to both US-East AND US-West synchronously (dual-write with idempotency keys). If US-East fails, the US-West copy serves as the source of truth. The extra write latency (+70ms to US-West) is acceptable for payment transactions.

**Interviewer**: "How do you handle the failback? US-East comes back up."

**You**: Failback is more complex than failover. Steps: (1) **Rebuild**: US-East's database is restored from backups + replayed WAL. It becomes a read replica of US-West (which is now the primary). (2) **Catch-up**: Aurora replicates all changes since the outage from US-West to US-East. For a 2-hour outage at 500MB/s write throughput, that's ~3.6TB of data to replicate — at 100MB/s cross-region, takes ~10 hours. During this time, US-West serves all traffic. (3) **Validate**: Run consistency checks between US-East and US-West. Confirm all data matches. (4) **Switch primary**: Promote US-East back to primary via a planned failover (Aurora supports this with minimal downtime). (5) **Route traffic**: Update Route53 to include US-East again. Gradual ramp: start with 10% of traffic, increase over an hour.

The key insight: failback is NOT urgent. The system works fine with US-West as primary. Take time to validate before switching back. Rushed failbacks cause more outages than the original failure.

### Deep Dive Path 2: Data Partitioning and Cross-Region Reads/Writes

**Interviewer**: "How do you decide which region owns which user's data?"

**You**: User data partitioning strategy: each user has a "home region" determined at registration time based on their geographic location (from IP geolocation or explicit country selection). The home region is stored in a global routing table — a lightweight, strongly-consistent lookup: `user_id -> home_region`. This table is replicated synchronously to all regions (it's tiny — 1B users x 16 bytes = 16 GB, fits in any database with room to spare).

Request flow: (1) Request arrives at the local region's API gateway. (2) Gateway extracts user_id from the auth token. (3) Gateway looks up user's home region from the routing table. (4) If local region == home region: process locally (fast path). (5) If local region != home region: for reads, serve from local read replica (eventual consistency, acceptable for most reads). For writes, proxy to the home region (adds cross-region latency but ensures consistency). The proxy is transparent to the service — the regional gateway handles it.

**Interviewer**: "What about data that involves multiple users in different home regions? Like a chat message from a US user to an EU user."

**You**: Cross-region data operations are the hardest case. Three approaches: (1) **Write to sender's home region, replicate to receiver's**: Chat message is stored in US-East (sender's home). Async replication copies it to EU-West. The EU user reads from their local replica — they might see the message 1-2 seconds after it was sent (replication lag). For chat, this is acceptable. (2) **Write to both regions synchronously**: For data where both parties need immediate consistency (e.g., a shared document edit), write to both regions in a distributed transaction. This adds 90ms latency but guarantees both see the same state. (3) **Event-based**: Write an event to the sender's regional Kafka. MirrorMaker replicates to the receiver's region. The receiver's service processes the event and writes to the local store. Decouples the write from cross-region latency.

**Interviewer**: "How does EKS handle cross-region service communication?"

**You**: In our EKS setup, each region has its own cluster. Cross-region service calls go through a dedicated gateway service — never direct pod-to-pod (which would require cross-region VPC peering or a service mesh spanning regions). The gateway pattern: Service A in US-East needs to call Service B in EU-West. Service A calls `cross-region-gateway.us-east` (an internal service in the US-East cluster). The gateway forwards the request to `cross-region-gateway.eu-west` over a private link (VPC peering or Transit Gateway). The EU-West gateway routes to Service B in the EU-West cluster. This adds ~2-3ms gateway overhead on top of the 90ms cross-region latency.

For EKS specifically: we use AWS App Mesh or Istio for service mesh within each region. Cross-region traffic is NOT handled by the mesh — it goes through explicit gateway hops. This prevents accidental cross-region calls (a service can't inadvertently call a pod in another region) and provides a single control point for cross-region traffic policies, rate limiting, and circuit breaking.

### Deep Dive Path 3: Deployment Strategy and Regional Independence

**Interviewer**: "How do you deploy code changes across multiple regions safely?"

**You**: Staged regional deployments with progressive rollout. Never deploy to all regions simultaneously — a bad deployment that takes down one region is recoverable; a bad deployment that takes down all regions is catastrophic.

Deployment pipeline: (1) **Dev/staging**: Deploy and test in a non-production environment. (2) **Canary region** (e.g., US-West, lower traffic): Deploy to one region. Monitor error rates, latency, business metrics for 30-60 minutes. (3) **Second region** (US-East): If canary is healthy, deploy to the highest-traffic region. Monitor for 1-2 hours. (4) **Remaining regions** (EU-West): Deploy to the rest. Each stage has automated rollback triggers: if error rate increases >0.1% or p99 latency increases >20%, automatically roll back that region.

In EKS: each region's cluster has its own ArgoCD instance (or Flux). A GitOps repo contains per-region deployment manifests. The CI pipeline updates the canary region's manifest first. After automated validation (health checks, integration tests, synthetic monitoring), it updates the next region's manifest. The pipeline is a directed graph, not a linear sequence — if the canary fails, the pipeline stops and alerts.

**Interviewer**: "What about database schema migrations? You can't deploy code that expects a new column to a region where the database doesn't have it yet."

**You**: Schema migrations must be backward-compatible and deployed ahead of the code that uses them. The pattern: (1) **Add migration** (expand): Add new column/table without removing anything. Deploy schema change to ALL regions first. Since it's additive, it doesn't break existing code. (2) **Deploy code**: Roll out new code that uses the new column across regions (staged). New code reads from the new column if present, falls back to old column. (3) **Backfill**: Migrate data from old column to new column in a background job. (4) **Remove old** (contract): After all code is on the new version and data is migrated, remove the old column. Deploy this schema change to all regions.

The key: never do a "big bang" schema change that requires code and schema to deploy simultaneously. The expand-contract pattern ensures any combination of old code + new schema or new code + old schema works correctly.

**Interviewer**: "How do you handle regional configuration differences? EU requires different data handling than US."

**You**: Regional configuration layers: (1) **Global config**: Shared across all regions (feature flags, API versions). Stored in a global config service (LaunchDarkly, AWS AppConfig) replicated to all regions. (2) **Regional config**: Region-specific settings (compliance flags, endpoint URLs, capacity limits). Stored per-region in local config stores (SSM Parameter Store, ConfigMaps). (3) **Regulatory overrides**: Per-region data handling rules (GDPR erasure, data residency). Enforced at the API gateway and data layer.

In EKS: Kustomize overlays per region. The base deployment is identical; regional overlays add/modify environment variables, ConfigMaps, and resource limits. Example: EU-West overlay adds `GDPR_ENABLED=true`, `DATA_RESIDENCY=eu-west-1`, and extra CPU for the data processing pods (GDPR compliance checks add overhead).

---

## How Real Companies Built This

- **Netflix**: Active-active across 3 AWS regions (US-East, US-West, EU). Custom traffic routing (Zuul), regional Cassandra clusters with async replication. [Netflix Multi-Region Strategy](https://netflixtechblog.com/active-active-for-multi-regional-resiliency-c47719f6685b)
- **Uber**: Active-active across multiple datacenters. Custom CRDT-based data replication for driver/rider state. Ringpop for consistent hashing across services. [Uber Multi-Region](https://www.uber.com/blog/disaster-recovery-failover/)
- **Stripe**: Active-active with synchronous replication for payment data. Custom routing layer determines data home region. [Stripe Engineering — Multi-Region](https://stripe.com/blog/fast-secure-and-scalable-an-inside-look-at-stripes-new-infrastructure)
- **AWS EKS Multi-Region**: EKS clusters per region with Route53 for routing. AWS recommends GitOps (Flux/ArgoCD) per region with progressive deployment. [EKS Multi-Cluster Best Practices](https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#multi-region)
- **Google Spanner**: Synchronous replication using TrueTime for linearizable cross-region transactions. The gold standard for strongly consistent multi-region databases. [Spanner Paper — OSDI 2012](https://research.google/pubs/pub39966/)
- **CockroachDB**: Open-source Spanner-like. Distributed SQL with synchronous replication. [CockroachDB Multi-Region](https://www.cockroachlabs.com/docs/stable/multiregion-overview.html)
- **Cloudflare**: Workers run at 300+ edge locations. Data stored at edge (Durable Objects) with automatic replication. [Cloudflare Global Architecture](https://blog.cloudflare.com/architecture-overview/)

---

## The Complete Reference Design

### API Design

```
# Regional routing configuration
PUT /v1/routing/users/{user_id}/home-region
{ "region": "us-east-1" }

# Health check endpoint (called by Route53/Global Accelerator)
GET /v1/health/region
# Response:
{
  "region": "us-east-1",
  "status": "healthy",
  "database": "primary",           # primary | replica | promoting
  "replication_lag_ms": 150,
  "services_healthy": 48,
  "services_total": 50,
  "capacity_utilization": 0.65     # 65% of max capacity
}

# Failover management API
POST /v1/failover/initiate
{
  "source_region": "us-east-1",
  "target_region": "us-west-2",
  "type": "planned",               # planned | emergency
  "services": ["all"]              # or specific service list
}

# Cross-region proxy (internal)
POST /v1/proxy/cross-region
{
  "target_region": "eu-west-1",
  "service": "user-service",
  "method": "POST",
  "path": "/v1/users/123/profile",
  "body": {...},
  "timeout_ms": 5000,
  "idempotency_key": "uuid-v4"
}
```

### Database Schema

```sql
-- Global routing table (replicated synchronously to all regions)
CREATE TABLE user_routing (
    user_id      BIGINT PRIMARY KEY,
    home_region  VARCHAR(16) NOT NULL,       -- us-east-1, eu-west-1, etc.
    created_at   TIMESTAMP NOT NULL,
    migrated_at  TIMESTAMP                   -- if user moved regions
);
-- Sharded by user_id, small enough to fit in any single DB
-- Replicated via DynamoDB Global Tables or Spanner

-- Regional service health (per region, not replicated)
CREATE TABLE region_health (
    region_id       VARCHAR(16) PRIMARY KEY,
    status          VARCHAR(16) NOT NULL,    -- healthy, degraded, failover
    primary_db      BOOLEAN NOT NULL,         -- is this region the DB primary?
    last_failover   TIMESTAMP,
    replication_lag INTERVAL,
    updated_at      TIMESTAMP NOT NULL
);

-- Deployment tracking (global, replicated)
CREATE TABLE deployments (
    id              UUID PRIMARY KEY,
    service_name    VARCHAR(128) NOT NULL,
    version         VARCHAR(64) NOT NULL,
    target_region   VARCHAR(16) NOT NULL,
    status          VARCHAR(16) NOT NULL,    -- pending, deploying, deployed, rolled_back
    started_at      TIMESTAMP NOT NULL,
    completed_at    TIMESTAMP,
    health_check    JSONB                    -- post-deploy health metrics
);
CREATE INDEX idx_deploy_svc ON deployments(service_name, target_region, started_at DESC);
```

### Key Algorithms — Regional Failover Controller

```python
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class RegionStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    FAILED = "failed"

@dataclass
class RegionHealth:
    region_id: str
    status: RegionStatus
    health_check_failures: int
    replication_lag_ms: float
    capacity_utilization: float
    last_updated: float

class FailoverController:
    FAILURE_THRESHOLD = 3        # consecutive failures before failover
    REPL_LAG_MAX_MS = 5000       # max acceptable replication lag
    CAPACITY_MAX = 0.85          # max capacity before warning

    def __init__(self, regions: list[str], primary_region: str):
        self.regions = regions
        self.primary = primary_region
        self.health: dict[str, RegionHealth] = {}
        self.failover_in_progress = False

    def update_health(self, region_id: str, healthy: bool, repl_lag_ms: float, capacity: float):
        current = self.health.get(region_id)
        failures = 0 if healthy else (current.health_check_failures + 1 if current else 1)

        status = RegionStatus.HEALTHY
        if not healthy and failures >= self.FAILURE_THRESHOLD:
            status = RegionStatus.FAILED
        elif not healthy:
            status = RegionStatus.FAILING
        elif repl_lag_ms > self.REPL_LAG_MAX_MS:
            status = RegionStatus.DEGRADED
        elif capacity > self.CAPACITY_MAX:
            status = RegionStatus.DEGRADED

        self.health[region_id] = RegionHealth(
            region_id=region_id, status=status,
            health_check_failures=failures,
            replication_lag_ms=repl_lag_ms,
            capacity_utilization=capacity,
            last_updated=time.time()
        )

        if status == RegionStatus.FAILED and region_id == self.primary:
            self._initiate_failover(region_id)

    def _initiate_failover(self, failed_region: str):
        if self.failover_in_progress:
            return
        self.failover_in_progress = True

        # Select best failover target
        target = self._select_failover_target(failed_region)
        if not target:
            raise Exception("No healthy region available for failover")

        # Execute failover steps
        self._update_dns(failed_region, target)          # Remove failed, weight target
        self._promote_database(target)                    # Aurora promote replica
        self._update_regional_config(target, is_primary=True)
        self._scale_up_target(target)                     # HPA/ASG scaling

        self.primary = target
        self.failover_in_progress = False

    def _select_failover_target(self, exclude: str) -> Optional[str]:
        candidates = [
            (rid, h) for rid, h in self.health.items()
            if rid != exclude and h.status in (RegionStatus.HEALTHY, RegionStatus.DEGRADED)
        ]
        if not candidates:
            return None
        # Prefer: healthy > degraded, then lowest replication lag
        candidates.sort(key=lambda x: (
            0 if x[1].status == RegionStatus.HEALTHY else 1,
            x[1].replication_lag_ms
        ))
        return candidates[0][0]
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Compute per region | 1M QPS / 3 regions = 333K QPS / 10K per pod = 33 pods | 33 pods x 50 services = 1650 pods per region |
| Failover headroom | Each region must handle 1.5x normal load | 50% over-provisioned (2475 pods per region) |
| Database per region | 50 TB primary + replicas | Aurora db.r6g.16xlarge (3 AZs) + Global DB |
| Cross-region bandwidth | 500 MB/s replication + 100 MB/s Kafka MM | 4.8 Gbps cross-region (dedicated) |
| Cross-region cost | 600 MB/s x $0.02/GB | ~$1M/year cross-region transfer |
| DNS/Global Accelerator | 1M QPS DNS resolution | Route53 or Global Accelerator ($0.025/GB) |
| Regional Redis | 1.5 TB per region (local cache) | 3 Redis clusters, 10 shards each |
| EKS clusters | 3 regions x 1 cluster | 3 EKS control planes + managed node groups |

---

## Senior vs Staff vs Principal

| Aspect | Senior (E5/L5) | Staff (E6/L6) | Principal (L66+) |
|--------|----------------|----------------|-------------------|
| **Architecture** | Understands active-active vs active-passive, DNS routing basics | Designs data partitioning by home region, async replication with conflict resolution | Designs adaptive routing (shift traffic based on cost/latency/capacity), handles data sovereignty requirements |
| **Failover** | Describes manual failover process | Automates failover with health checks, designs RPO/RTO trade-offs by data type | Designs chaos engineering for regional failure, automated failover testing, blast radius analysis |
| **Data** | Knows about cross-region replication | Designs hybrid replication strategy (sync for payments, async for everything else) | Reasons about CRDTs for conflict resolution, Spanner-style distributed transactions, TCO of consistency models |
| **Deployment** | Deploys to all regions simultaneously | Designs staged rollout with canary region, automated rollback | Designs the platform that enables 50 teams to safely do multi-region deployments independently |

---

## Red Flags & Common Mistakes

1. **"Just replicate everything synchronously"** — At 90ms cross-region RTT, this destroys write latency. The candidate doesn't understand the CAP trade-off.
2. **No data classification** — Treating all data the same. Session data doesn't need cross-region replication. Payment data needs synchronous replication. Conflating these is a red flag.
3. **Active-active without conflict resolution** — "Both regions accept writes to any user." What happens when both regions update the same user's profile? Without last-writer-wins, CRDTs, or home-region routing, you get data corruption.
4. **No blast radius control** — A deployment or failure in one region cascades to others. If you don't mention regional isolation, the interviewer worries about global outages.
5. **Ignoring the cost of cross-region traffic** — Cross-region data transfer is ~$0.02/GB. At 500 MB/s continuous, that's ~$1M/year. Not mentioning cost shows lack of production experience.
6. **Deploy everywhere at once** — No staged rollout, no canary region. A bad deployment takes down all 3 regions simultaneously.
7. **Ignoring DNS propagation time** — "Failover is instant with Route53." It's not. DNS TTL, client caching, and health check intervals mean failover takes 1-5 minutes minimum.
8. **No failback strategy** — Everyone designs failover. Few design failback. How do you safely return to the original region without causing a second outage?
