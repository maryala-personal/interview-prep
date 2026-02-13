# Design a Service Mesh

> **Companies**: Google (Istio/GKE), Microsoft (Open Service Mesh/AKS), Lyft (Envoy), any company with large microservice architectures
> **Level**: Staff / Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a transparent networking layer that provides observability, security, and traffic management for service-to-service communication? Can you reason about sidecar vs sidecarless architectures, xDS protocol, mTLS certificate rotation, and the performance overhead of proxying every packet?
> **Your EKS advantage**: You understand how service meshes interact with the K8s data plane — CNI chaining, iptables redirect rules, sidecar injection via mutating webhooks, and the operational cost of running a proxy per Pod. You know when a mesh adds value and when it is unnecessary overhead.

---

## The First 5 Minutes — Technical Scoping

- "What's the primary goal? Observability (distributed tracing, metrics), security (mTLS, authorization), or traffic management (canary releases, retries, circuit breaking)? Different goals lead to different architectures — you might not need a full mesh."
- "How many services and what's the call graph depth? 50 services with 3-hop depth is very different from 500 services with 10-hop depth. Deep call graphs amplify proxy latency."
- "What's the current networking model? If running Cilium with eBPF, we can get L4 network policies and observability without a sidecar mesh. Cilium Service Mesh provides L7 features via per-node proxies rather than per-pod sidecars."
- "What's the latency budget? Each sidecar hop adds ~1-3ms of p99 latency. For a 10-hop request chain, that is 20-60ms of added latency. Is that acceptable?"
- "What security requirements? Just encryption in transit (mTLS)? Or fine-grained authorization (service A can call service B method X but not method Y)? Full L7 authorization requires parsing application protocol in the proxy."
- "Multi-cluster? If services span multiple clusters, we need cross-cluster service discovery and trust domain federation."
- "What about non-K8s workloads? VMs, ECS tasks, Lambda functions? The mesh must handle heterogeneous endpoints."

### Working Assumptions
| Parameter | Value |
|-----------|-------|
| Services | 200 microservices |
| Pods | 10,000 across 500 nodes |
| Request rate | ~500K RPS across the mesh |
| p99 latency budget for proxy | <3ms per hop |
| mTLS cert rotation | Every 24 hours |
| Protocol | HTTP/2 and gRPC (majority), some TCP |
| Observability requirements | Distributed tracing, RED metrics, access logs |
| Authorization | Service-level (not method-level initially) |

---

## High-Level Architecture

```
                    ┌──────────────────────────┐
                    │      Control Plane        │
                    │                           │
                    │  ┌─────────┐ ┌────────┐  │
                    │  │  istiod  │ │  CA    │  │
                    │  │ (Pilot + │ │(cert   │  │
                    │  │ Galley + │ │ issuer)│  │
                    │  │ Citadel) │ │        │  │
                    │  └────┬────┘ └───┬────┘  │
                    │       │ xDS      │ mTLS  │
                    │       │ (gRPC)   │ certs │
                    └───────┼──────────┼───────┘
                            │          │
          ┌─────────────────┼──────────┼─────────────────┐
          │                 │          │                  │
    ┌─────┴─────┐    ┌─────┴─────┐    │           ┌─────┴─────┐
    │  Pod A     │    │  Pod B     │    │           │  Pod C     │
    │┌─────────┐│    │┌─────────┐│    │           │┌─────────┐│
    ││  App    ││    ││  App    ││    │           ││  App    ││
    ││Container││    ││Container││    │           ││Container││
    │└────┬────┘│    │└────┬────┘│    │           │└────┬────┘│
    │     │     │    │     │     │    │           │     │     │
    │┌────┴────┐│    │┌────┴────┐│    │           │┌────┴────┐│
    ││  Envoy  ││───▶││  Envoy  ││    │           ││  Envoy  ││
    ││ Sidecar ││    ││ Sidecar ││    │           ││ Sidecar ││
    ││(proxy)  ││    ││(proxy)  ││    │           ││(proxy)  ││
    │└─────────┘│    │└─────────┘│    │           │└─────────┘│
    └───────────┘    └───────────┘    │           └───────────┘
                                      │
                    ┌─────────────────┴──────────────────┐
                    │        Sidecarless Alternative      │
                    │  ┌──────────────────────────────┐  │
                    │  │  Per-Node Proxy (Cilium/      │  │
                    │  │  Ambient Mesh ztunnel)        │  │
                    │  │  L4: ztunnel (Rust, per-node) │  │
                    │  │  L7: waypoint proxy (Envoy,   │  │
                    │  │       per-service-account)    │  │
                    │  └──────────────────────────────┘  │
                    └────────────────────────────────────┘
```

**Why this architecture**: A service mesh separates networking concerns (mTLS, retries, observability) from application code. The sidecar model (Envoy proxy per Pod) provides per-workload isolation and fine-grained control. The control plane (istiod) computes routing configuration and pushes it to sidecars via the xDS protocol. The emerging sidecarless model (Istio Ambient, Cilium) reduces the resource overhead by moving L4 (mTLS, TCP metrics) to a per-node agent and L7 (HTTP routing, retries) to shared waypoint proxies.

---

## Core Concepts Deep Dive

### Concept 1: The xDS Protocol

xDS is the control plane to data plane API that Envoy uses. It is a set of discovery services that push configuration to proxies.

**Key xDS APIs**:
- **LDS (Listener Discovery Service)**: What ports/protocols to listen on
- **RDS (Route Discovery Service)**: HTTP routing rules (host/path matching, header-based routing)
- **CDS (Cluster Discovery Service)**: Upstream cluster definitions (load balancing policy, circuit breaker settings, health check config)
- **EDS (Endpoint Discovery Service)**: Actual IP:port pairs for each cluster (the real Pod IPs)
- **SDS (Secret Discovery Service)**: TLS certificates for mTLS

**How it works in practice**: istiod watches K8s Services, Endpoints, VirtualServices, DestinationRules, and PeerAuthentications. It compiles these into Envoy configuration and pushes via gRPC streaming to each sidecar. When a new Pod is added to a Service, the Endpoints update propagates through: API server -> istiod watch -> recompute EDS -> push to all connected sidecars.

**At scale**: With 10K Pods, istiod is pushing xDS updates to 10K Envoy sidecars. Each Service endpoint change triggers an EDS push to every sidecar that references that Service. This is a fan-out problem. istiod uses delta xDS (incremental updates) and debouncing (batch multiple changes into one push) to manage this.

```go
// istiod xDS push debouncing
const (
    debounceAfter  = 100 * time.Millisecond  // Wait for more changes
    debounceMax    = 10 * time.Second         // Max wait before pushing
)
```

### Concept 2: Sidecar Injection and Traffic Interception

**How the sidecar gets into the Pod**:
istiod runs a mutating admission webhook. When a Pod is created in a namespace with the `istio-injection: enabled` label, the webhook mutates the Pod spec to add:
1. An init container (`istio-init`) that sets up iptables rules to redirect all traffic through the sidecar
2. The Envoy sidecar container (`istio-proxy`)

**Traffic interception via iptables**:
```
# iptables rules installed by istio-init
# Redirect all outbound traffic to Envoy's outbound port (15001)
iptables -t nat -A OUTPUT -p tcp -j ISTIO_OUTPUT
iptables -t nat -A ISTIO_OUTPUT -o lo -d 127.0.0.1/32 -j RETURN  # skip loopback
iptables -t nat -A ISTIO_OUTPUT -j ISTIO_REDIRECT
iptables -t nat -A ISTIO_REDIRECT -p tcp -j REDIRECT --to-ports 15001

# Redirect all inbound traffic to Envoy's inbound port (15006)
iptables -t nat -A PREROUTING -p tcp -j ISTIO_INBOUND
iptables -t nat -A ISTIO_INBOUND -p tcp -j ISTIO_IN_REDIRECT
iptables -t nat -A ISTIO_IN_REDIRECT -p tcp -j REDIRECT --to-ports 15006
```

This is transparent to the application — it sends to the Service IP, but iptables redirects to Envoy on localhost, which then establishes the real connection to the target.

**Cilium alternative**: With Cilium Service Mesh, traffic interception uses eBPF instead of iptables. The eBPF program on the socket layer (sockops) redirects connections to the proxy, avoiding the iptables overhead entirely.

### Concept 3: mTLS Certificate Management

**The certificate lifecycle**:
1. When an Envoy sidecar starts, it requests a certificate from istiod via SDS (Secret Discovery Service).
2. istiod's built-in CA generates a short-lived cert (default 24 hours) with the Pod's SPIFFE identity: `spiffe://cluster.local/ns/<namespace>/sa/<service-account>`.
3. The cert is delivered via the SDS gRPC stream. No disk writes — the cert exists only in memory.
4. Envoy uses this cert for both client (outbound) and server (inbound) mTLS.
5. Before expiry, Envoy requests a new cert. The rotation is seamless — Envoy hot-swaps the cert without dropping connections.

**Trust domain federation**: For multi-cluster meshes, each cluster has its own CA but they share a root CA (or cross-sign). This allows Pods in Cluster A to verify certs from Pods in Cluster B. The SPIFFE IDs differentiate clusters: `spiffe://cluster-a/ns/default/sa/frontend`.

**EKS integration**: On EKS, you can use AWS Private CA (ACM PCA) as the root CA for Istio. This provides hardware-backed key storage and compliance certifications. istiod acts as an intermediate CA, signing workload certs under the ACM PCA root.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Sidecar vs Sidecarless — which and why?"

**Interviewer**: "Should we use the sidecar model or the newer sidecarless approach?"

**You**: "This is the most important architectural decision. Let me walk through the trade-offs.

**Sidecar model (Istio with Envoy sidecars)**:
- Each Pod gets its own Envoy proxy (~50-100 MB memory, ~50m CPU at idle, more under load).
- For 10K Pods, that is 500 GB - 1 TB of additional memory just for sidecars.
- Advantages: per-Pod L7 policy, per-Pod traffic management, failure isolation (a crashed sidecar only affects one Pod).
- Disadvantages: massive resource overhead, sidecar lifecycle coupling (if the sidecar crashes before the app, traffic is blackholed), upgrade complexity (must restart every Pod to update Envoy).

**Sidecarless model (Istio Ambient Mesh)**:
- L4 (mTLS, TCP metrics, L4 authorization): handled by `ztunnel`, a Rust-based per-node agent. One ztunnel per node instead of one Envoy per Pod.
- L7 (HTTP routing, retries, L7 authorization, tracing): handled by waypoint proxies — shared Envoy instances deployed per service account, only for services that need L7 features.
- Advantages: dramatically lower resource overhead (ztunnel uses ~50 MB per node, not per Pod), no sidecar lifecycle issues, independent upgrade path.
- Disadvantages: newer technology (Ambient went GA more recently), L4-only by default (need explicit opt-in to L7 via waypoints), per-node blast radius (if ztunnel crashes, all Pods on that node lose mesh networking).

**My recommendation**: For most workloads, start with Ambient Mesh for mTLS and L4 observability. Add waypoint proxies only for services that need L7 features (canary releases, request-level authorization). This gives you 80% of the mesh value at 20% of the resource cost."

**Interviewer**: "What about Cilium Service Mesh?"

**You**: "Cilium takes a different approach. Instead of a separate mesh control plane, it integrates mesh features directly into the CNI layer using eBPF.

L4 features (mTLS via WireGuard, network policies, TCP metrics) run in eBPF — zero additional proxies. L7 features (HTTP routing, Envoy-based) use a per-node Envoy proxy that Cilium manages.

The advantage is operational simplicity — if you already run Cilium as your CNI, adding mesh features is a configuration change, not a new infrastructure deployment. On EKS, this is compelling because Cilium can replace both kube-proxy and the sidecar mesh.

The trade-off: Cilium's mesh is tightly coupled to the CNI. If you need to support non-Cilium clusters or non-K8s workloads, Istio's cross-platform model is more flexible."

### Deep Dive Path 2: "Design canary deployments with a service mesh"

**Interviewer**: "How would you implement canary releases using the mesh?"

**You**: "The mesh gives us traffic splitting at the proxy layer, independent of K8s Deployments.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-service
spec:
  hosts:
  - my-service
  http:
  - route:
    - destination:
        host: my-service
        subset: stable
      weight: 95
    - destination:
        host: my-service
        subset: canary
      weight: 5
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: my-service
spec:
  host: my-service
  subsets:
  - name: stable
    labels:
      version: v1
  - name: canary
    labels:
      version: v2
```

This splits 5% of traffic to the canary. The proxy does the routing — it hashes the request and sends 1 in 20 to the canary subset.

The advanced version uses header-based routing for internal testing:
```yaml
http:
- match:
  - headers:
      x-canary:
        exact: "true"
  route:
  - destination:
      host: my-service
      subset: canary
- route:
  - destination:
      host: my-service
      subset: stable
```

**Progressive delivery with Flagger or Argo Rollouts**: These tools automate the canary process. Flagger watches canary metrics (success rate, latency p99), and if they meet the threshold, automatically increases the traffic weight. If metrics degrade, it rolls back by setting canary weight to 0.

The key insight: the mesh decouples traffic routing from deployment management. You can have two K8s Deployments (v1 and v2) both behind the same K8s Service, and the mesh controls the traffic split. Without a mesh, you would need to use the K8s Deployment `maxSurge`/`maxUnavailable` for basic rolling updates, but you cannot do weighted traffic splitting."

### Deep Dive Path 3: "Mesh observability — what do you actually get?"

**Interviewer**: "What observability does the mesh provide that you cannot get otherwise?"

**You**: "Three categories:

**1. Distributed tracing without code changes**: Envoy automatically generates trace spans for every request. It propagates trace headers (B3, W3C TraceContext) between sidecars. You get a full request trace across 10 services without any application instrumentation — the sidecars handle it. The catch: the application MUST propagate trace headers on outbound requests. The sidecar generates the span, but only the application can propagate the correlation ID to downstream calls.

**2. Golden signals (RED metrics) per service**: Every sidecar exposes Prometheus metrics:
- `istio_requests_total` — request count by source, destination, response code
- `istio_request_duration_milliseconds` — request latency histogram
- `istio_tcp_sent_bytes_total` / `istio_tcp_received_bytes_total`

This gives you a service-to-service traffic matrix without any application changes. You can build dashboards showing which services call which, error rates, and latency percentiles. Without a mesh, you need each service to instrument its HTTP client and server.

**3. Access logs with service identity**: Envoy logs every request with source and destination service identity (from mTLS certs). This replaces IP-based logs with identity-based logs — you see 'frontend called payment-service' instead of '10.0.1.5 called 10.0.2.15'. In an environment where Pod IPs are ephemeral, identity-based logs are far more useful for debugging.

**The overhead**: Envoy access logs at 500K RPS generate ~5 GB/hour of log data. Most deployments sample (1% of requests) or use tail-based sampling (log all errors, sample successful requests). Metrics are cheaper — Prometheus scrapes every 15-30 seconds and stores aggregated histograms."

---

## How the Industry Built This

- **Envoy (Lyft)**: The foundational data plane proxy. Written in C++, extensible via WASM filters. Envoy's xDS API became the standard for control plane to data plane communication. [envoyproxy.io](https://www.envoyproxy.io/)
- **Istio (Google/IBM)**: The most widely deployed service mesh. Consolidated control plane into istiod. Ambient Mesh (sidecarless) is the latest architecture. [istio.io](https://istio.io/)
- **Linkerd (Buoyant)**: Lightweight mesh using its own Rust-based proxy (linkerd2-proxy) instead of Envoy. Lower resource footprint than Istio. CNCF graduated project.
- **Cilium (Isovalent/Cisco)**: eBPF-based networking with integrated mesh features. Avoids iptables entirely. Service Mesh features run in-kernel for L4, per-node Envoy for L7.
- **AWS App Mesh**: AWS's managed service mesh using Envoy. Integrates with ECS, EKS, and EC2. Virtual nodes and virtual services provide the abstraction layer. Being replaced by VPC Lattice for many use cases.
- **VPC Lattice**: AWS's application networking service. Layer 7 load balancing, auth, and observability without sidecars. Works across VPCs, accounts, and compute types (EKS, ECS, Lambda, EC2).

References:
- https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/
- https://istio.io/latest/docs/ops/deployment/architecture/
- https://istio.io/latest/docs/ambient/overview/
- https://docs.cilium.io/en/stable/network/servicemesh/

---

## The Complete Reference Design

### Istio Installation (Production)

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  profile: default
  meshConfig:
    accessLogFile: /dev/stdout
    accessLogEncoding: JSON
    enableTracing: true
    defaultConfig:
      tracing:
        sampling: 1.0  # 1% sampling in production
      holdApplicationUntilProxyStarts: true  # Prevent app from starting before sidecar
    outboundTrafficPolicy:
      mode: REGISTRY_ONLY  # Only allow traffic to known services
  components:
    pilot:
      k8s:
        resources:
          requests:
            cpu: 500m
            memory: 2Gi
        hpaSpec:
          minReplicas: 2
          maxReplicas: 5
    ingressGateways:
    - name: istio-ingressgateway
      enabled: true
      k8s:
        serviceAnnotations:
          service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
```

### Authorization Policy

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: payment-service-policy
  namespace: payment
spec:
  selector:
    matchLabels:
      app: payment-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals:
        - "cluster.local/ns/frontend/sa/frontend-sa"
        - "cluster.local/ns/order/sa/order-sa"
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/charge"]
  - from:
    - source:
        principals:
        - "cluster.local/ns/monitoring/sa/prometheus"
    to:
    - operation:
        methods: ["GET"]
        paths: ["/metrics"]
```

### Performance Characteristics
| Component | Metric | Value |
|-----------|--------|-------|
| Envoy sidecar | Memory (idle) | 50-100 MB |
| Envoy sidecar | Memory (active, 1K RPS) | 100-200 MB |
| Envoy sidecar | CPU (1K RPS) | ~100m |
| Sidecar latency overhead | p50 | ~0.5ms |
| Sidecar latency overhead | p99 | ~2-5ms |
| ztunnel (per-node) | Memory | ~50 MB |
| ztunnel latency overhead | p99 | ~0.5ms (L4 only) |
| istiod | Memory (1K services) | ~1 GB |
| xDS push latency | Endpoint update to proxy | ~100-500ms |
| mTLS handshake | Additional latency (first request) | ~1-2ms |

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Sidecar memory (total) | pods * 100 MB | 10K pods = 1 TB |
| ztunnel memory (total) | nodes * 50 MB | 500 nodes = 25 GB |
| istiod instances | 1 per 2K sidecars | 2-5 replicas |
| CA cert issuance rate | pods * 1 cert/24hr | ~400 certs/hour |
| xDS push bandwidth | services * endpoints * push rate | ~10 Mbps per istiod |

---

## Senior vs Staff vs Principal

| Level | What they demonstrate | Example |
|-------|----------------------|---------|
| Senior | Understands sidecar model, can explain mTLS, knows basic traffic management | Draws the sidecar injection flow, explains how VirtualService works |
| Staff | Reasons about sidecar vs sidecarless trade-offs, understands xDS protocol, designs for scale | Compares Ambient Mesh vs sidecar resource costs, explains xDS push debouncing, designs progressive delivery |
| Principal | Questions whether a mesh is needed at all, proposes platform-level alternatives (VPC Lattice, eBPF-only), designs multi-cluster mesh federation | Argues for Cilium + WireGuard instead of full Istio for 80% of use cases, designs cross-cluster trust domain architecture |

---

## Red Flags and Common Mistakes

- **Adding a mesh without clear requirements**: A service mesh is a significant operational investment. If you just need mTLS, consider Cilium with WireGuard encryption. If you just need metrics, consider OpenTelemetry instrumentation. A full mesh should be justified by specific L7 routing or authorization needs.
- **Ignoring the resource cost**: Envoy sidecars add 50-200 MB per Pod. For a 10K-pod cluster, that is potentially 1 TB of memory just for proxies. Candidates who design a mesh without sizing the overhead are missing the operational reality.
- **Not understanding the iptables redirect**: The sidecar intercepts traffic via iptables NAT rules. If these rules are wrong, traffic bypasses the mesh entirely. If the sidecar starts after the app, early requests bypass mTLS. This is why `holdApplicationUntilProxyStarts` exists.
- **Assuming trace propagation is automatic**: The sidecar generates spans but the application must propagate trace headers. If the app does not forward `x-request-id` / `traceparent` headers, you get disconnected traces.
- **Overlooking sidecarless options**: Ambient Mesh and Cilium Service Mesh are production-ready alternatives that eliminate most of the sidecar overhead. Candidates who only know the sidecar model are behind the state of the art.
