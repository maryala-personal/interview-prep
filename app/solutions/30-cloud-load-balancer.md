# Design a Cloud Load Balancer

> **Companies**: Amazon (ELB/EKS), Microsoft (Azure LB/AKS), Google (Cloud LB/GKE), Cloudflare, any company exposing K8s workloads externally
> **Level**: Staff / Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design the integration between Kubernetes Service abstractions and cloud provider load balancers? Can you reason about L4 vs L7 load balancing, health check propagation, connection draining, and the controller pattern that reconciles K8s resources to cloud infrastructure?
> **Your EKS advantage**: You understand the AWS Load Balancer Controller, how it reconciles Ingress/Service resources to ALB/NLB, the TargetGroupBinding CRD, and the real challenges of pod-readiness gates and IP-mode target groups. You know why NodePort mode has an extra hop and how IP-mode target groups solve it.

---

## The First 5 Minutes — Technical Scoping

- "Are we building the load balancer itself, or the K8s integration that provisions and configures cloud load balancers? In managed K8s, the interesting problem is the controller that translates K8s resources into cloud API calls."
- "L4 (NLB/TCP) or L7 (ALB/HTTP)? L4 is simpler but cannot do path-based routing or TLS termination. L7 adds latency but enables advanced routing, WAF integration, and TLS offloading."
- "What's the target group mode? Instance mode (traffic goes to NodePort, kube-proxy routes to Pod) or IP mode (traffic goes directly to Pod IPs)? IP mode eliminates the extra hop but requires the LB to track every Pod IP."
- "What's the scale? 10 Services with 50 Pods, or 500 Services with 50K Pods? At high scale, the controller's reconciliation loop must handle frequent endpoint churn without hammering the cloud API."
- "Do we need cross-cluster load balancing? Multiple EKS clusters behind one ALB? That changes the target group architecture."
- "What about internal vs external? Internal load balancers stay within the VPC. External ones get public IPs. Different security requirements."
- "TLS termination — at the LB, at the Pod, or both (re-encryption)? This affects certificate management and performance."

### Working Assumptions
| Parameter | Value |
|-----------|-------|
| Load balancer type | ALB (L7) for HTTP, NLB (L4) for TCP/gRPC |
| Target group mode | IP mode (direct to Pod) |
| Services with LB | 50 external-facing services |
| Total backend Pods | 5,000 |
| Endpoint churn rate | ~100 Pod IP changes/minute |
| Cloud API rate limit | AWS ELBv2 API: ~25 TPS per account/region |
| Health check interval | 10s (ALB), 30s (NLB) |
| Connection draining | 300s default |
| TLS termination | At the ALB (ACM certificates) |

---

## High-Level Architecture

```
                           Internet
                              │
                    ┌─────────┴─────────┐
                    │   Cloud LB (ALB)  │  L7: HTTP routing, TLS termination
                    │                    │  Path-based routing (/api → service-a,
                    │   ┌──────────┐    │               /web → service-b)
                    │   │ Listener │    │
                    │   │ (443/TLS)│    │
                    │   └────┬─────┘    │
                    │        │          │
                    │   ┌────┴───────┐  │
                    │   │  Rules     │  │  Routing rules from Ingress spec
                    │   │  (path,   │  │
                    │   │  host)    │  │
                    │   └────┬───────┘  │
                    │        │          │
                    │   ┌────┴───────┐  │
                    │   │Target Group│  │  Pod IPs (IP mode) or NodePorts
                    │   │ (TG)      │  │
                    │   └────┬───────┘  │
                    └────────┼──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
         │ Pod A    │   │ Pod B    │   │ Pod C    │
         │10.0.1.5  │   │10.0.2.8  │   │10.0.3.12 │
         │(Node 1)  │   │(Node 2)  │   │(Node 3)  │
         └─────────┘   └─────────┘   └─────────┘

┌────────────────────────────────────────────────────┐
│          K8s Cluster (Control Plane)                │
│                                                    │
│  ┌──────────────────────────────────────┐          │
│  │  AWS Load Balancer Controller         │          │
│  │  (watches Ingress/Service resources,  │          │
│  │   reconciles to ALB/NLB via AWS API)  │          │
│  │                                       │          │
│  │  Ingress → ALB + Listener + Rules +   │          │
│  │           Target Groups               │          │
│  │  Service (type: LoadBalancer) → NLB + │          │
│  │           Target Group                │          │
│  └───────────────┬──────────────────────┘          │
│                  │                                  │
│  ┌───────────────┴──────────────────────┐          │
│  │  TargetGroupBinding (CRD)             │          │
│  │  - Maps K8s Service to AWS TG         │          │
│  │  - Manages pod readiness gates        │          │
│  │  - Handles deregistration delay       │          │
│  └──────────────────────────────────────┘          │
└────────────────────────────────────────────────────┘
```

**Why this architecture**: The K8s-to-cloud-LB integration follows the standard controller pattern: watch K8s resources (Ingress, Service), reconcile to cloud resources (ALB, NLB, Target Groups). The key design decision is IP-mode target groups: the LB sends traffic directly to Pod IPs, eliminating the extra hop through kube-proxy that NodePort mode requires. This reduces latency, preserves source IP, and avoids the uneven load distribution that NodePort's random routing causes.

---

## Core Concepts Deep Dive

### Concept 1: The AWS Load Balancer Controller Reconciliation Loop

The AWS Load Balancer Controller is a K8s controller (runs as a Deployment) that watches Ingress and Service resources and reconciles them to AWS ELBv2 resources.

**Reconciliation for an Ingress resource**:
1. Ingress object created with annotation `kubernetes.io/ingress.class: alb`
2. Controller picks it up from its informer
3. Controller calls AWS API to create/update: ALB, Listeners, Rules, Target Groups
4. Controller creates `TargetGroupBinding` CRDs that link K8s Services to AWS Target Groups
5. Controller watches Endpoints/EndpointSlices for backend Pods
6. When Pod IPs change, controller calls `RegisterTargets` / `DeregisterTargets` on the Target Group

**The cloud API rate limit problem**: AWS ELBv2 APIs have rate limits (~25 TPS per account/region). If you have 500 Services with frequent Pod churn, the controller must batch and throttle API calls. The controller uses:
- **Batching**: Collect multiple target registration changes and apply them in one API call (RegisterTargets accepts up to 200 targets per call).
- **Throttling**: Exponential backoff on API throttling errors.
- **Delta-based updates**: Only call RegisterTargets/DeregisterTargets for changed Pods, not the full target list.

```go
// Simplified reconciliation loop for TargetGroupBinding
func (r *TargetGroupBindingReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var tgb elbv2api.TargetGroupBinding
    if err := r.Get(ctx, req.NamespacedName, &tgb); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Get current Pod IPs from EndpointSlices
    desiredTargets, err := r.getDesiredTargets(ctx, &tgb)
    if err != nil {
        return ctrl.Result{}, err
    }

    // Get current targets registered in AWS Target Group
    currentTargets, err := r.elbv2Client.DescribeTargetHealth(ctx, tgb.Spec.TargetGroupARN)
    if err != nil {
        return ctrl.Result{}, err
    }

    // Diff and apply
    toRegister, toDeregister := diffTargets(currentTargets, desiredTargets)
    if len(toRegister) > 0 {
        r.elbv2Client.RegisterTargets(ctx, tgb.Spec.TargetGroupARN, toRegister)
    }
    if len(toDeregister) > 0 {
        r.elbv2Client.DeregisterTargets(ctx, tgb.Spec.TargetGroupARN, toDeregister)
    }

    return ctrl.Result{}, nil
}
```

### Concept 2: Pod Readiness Gates and Zero-Downtime Deployments

The hardest problem in K8s load balancer integration is ensuring zero traffic loss during deployments and scale-down.

**The problem**: When a new Pod starts, it takes time for the LB to register the target and for health checks to pass (10-30 seconds for ALB). If K8s considers the Pod ready before the LB does, traffic might be routed to Pods that the LB has not registered yet.

**The solution: Pod Readiness Gates**: The AWS LB Controller adds a custom readiness condition to Pods:
```yaml
readinessGates:
- conditionType: target-health.elbv2.k8s.aws/my-target-group
```
The Pod is not considered `Ready` by K8s until both the container readiness probe passes AND the LB reports the target as healthy. This prevents the Deployment controller from proceeding with the rolling update until the new Pod is actually receiving traffic from the LB.

**Deregistration and connection draining**: When a Pod is terminating:
1. The Endpoints controller removes the Pod from Endpoints.
2. The LB Controller calls `DeregisterTargets` on the AWS Target Group.
3. The ALB starts connection draining — it stops sending new connections but allows existing connections to complete (default 300s).
4. Meanwhile, the Pod receives SIGTERM and starts shutting down.

The race condition: if the Pod shuts down before the ALB finishes draining connections, clients get 502 errors. The fix:
```yaml
lifecycle:
  preStop:
    exec:
      command: ['sleep', '15']
terminationGracePeriodSeconds: 60
```
The `preStop` sleep ensures the Pod stays alive long enough for the LB to deregister it and drain connections.

### Concept 3: L4 vs L7 Load Balancing Trade-offs

**NLB (Layer 4)**:
- Operates at the TCP/UDP layer. Does not inspect HTTP headers.
- Ultra-low latency: adds ~100-200 microseconds.
- Preserves source IP (client IP visible to the Pod).
- Supports static/Elastic IPs (important for firewall allowlisting).
- No path-based routing, no TLS termination (pass-through TLS).
- Best for: gRPC (HTTP/2 multiplexing), TCP protocols, latency-sensitive workloads.

**ALB (Layer 7)**:
- Operates at the HTTP layer. Inspects headers, paths, query strings.
- Higher latency: adds ~1-5ms.
- Does NOT preserve source IP by default (use `X-Forwarded-For` header).
- TLS termination with ACM certificates (free certificate management).
- Path/host-based routing, WAF integration, authentication (OIDC/Cognito).
- Best for: REST APIs, web applications, microservice routing.

**The gRPC problem with ALB**: gRPC uses HTTP/2, which multiplexes many requests over a single TCP connection. A round-robin L4 load balancer (NLB) will pin all requests from one client to one backend because they share one connection. The solution is L7 load balancing at the request level — but ALB's gRPC support has limitations. In practice, many teams use NLB with a client-side load balancing library (gRPC has built-in support) or a service mesh that does per-request load balancing at the sidecar.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Design for zero-downtime deployments"

**Interviewer**: "We are seeing 502 errors during deployments. How do you fix this?"

**You**: "502s during deployments are almost always caused by the timing gap between K8s Pod termination and LB target deregistration. Let me trace the problem.

During a rolling update, the Deployment controller terminates old Pods and creates new ones. When an old Pod is terminated:
1. K8s sets `deletionTimestamp` on the Pod.
2. The Endpoints controller removes the Pod from the Endpoints object.
3. kube-proxy (iptables/eBPF) removes the Pod from Service routing rules — this happens within seconds on the same cluster.
4. The AWS LB Controller sees the Endpoints change, calls DeregisterTargets — this takes 1-5 seconds to propagate.
5. The ALB stops sending NEW connections but existing connections continue (connection draining).
6. Meanwhile, the kubelet sends SIGTERM to the container.

The problem: if step 6 (app shutdown) completes before step 4 (LB deregistration), the ALB is still sending traffic to a Pod that is not listening anymore. Result: 502.

The fix has three parts:
1. **preStop sleep**: Delay SIGTERM delivery by 15-20 seconds so the LB has time to deregister.
2. **Pod readiness gates**: Ensure new Pods are registered and healthy in the LB before old Pods are terminated.
3. **terminationGracePeriodSeconds**: Set high enough to accommodate the preStop sleep + app shutdown time + connection draining.

```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
  - name: app
    lifecycle:
      preStop:
        exec:
          command: ['sleep', '15']
    readinessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
  readinessGates:
  - conditionType: target-health.elbv2.k8s.aws/my-tg-binding
```

With maxUnavailable=0 and maxSurge=1, the rolling update creates a new Pod, waits for it to be Ready (including LB health check via readiness gate), then terminates the old Pod (with preStop sleep for deregistration). Zero 502s."

### Deep Dive Path 2: "NodePort mode vs IP mode"

**Interviewer**: "Why does IP mode matter?"

**You**: "In NodePort mode, the LB sends traffic to any node's NodePort (e.g., port 30080). kube-proxy on that node uses iptables to randomly select a Pod — which might be on a different node. If the Pod is on a different node, there is an extra network hop, and the source IP is lost (SNAT'd to the node IP).

The problems:
1. **Extra hop**: If traffic hits Node A but the Pod is on Node B, traffic traverses the VPC network twice. That adds ~1ms latency.
2. **Uneven distribution**: The LB distributes evenly across nodes. But nodes have different numbers of Pods. A node with 1 Pod gets the same traffic as a node with 10 Pods. The single-Pod node is overloaded.
3. **Source IP loss**: kube-proxy SNAT is necessary to ensure return traffic goes back through the same node (so the LB sees the response). But the Pod sees the node's IP, not the client's IP.
4. **externalTrafficPolicy: Local**: Setting this on the Service avoids the extra hop — kube-proxy only routes to Pods on the same node. But now nodes without Pods in that Service will health-check fail and be removed from the LB. This means the LB must track which nodes have which Pods, and node auto-scaling changes the LB target list.

IP mode solves all of this. The LB sends traffic directly to the Pod IP. No extra hop, no SNAT (source IP preserved), perfectly even distribution across Pods. The trade-off: the LB Controller must track every Pod IP and register/deregister targets as Pods come and go. With VPC-CNI, Pod IPs are routable VPC IPs, so the LB can reach them directly."

### Deep Dive Path 3: "Design for high availability"

**Interviewer**: "How do you make the load balancer layer highly available?"

**You**: "At multiple levels:

**LB layer**: AWS ALB/NLB are managed services — AWS handles HA. ALBs run across AZs and auto-scale. NLBs have static IPs per AZ and handle millions of connections. You do not need to manage LB HA.

**Controller layer**: The AWS LB Controller runs as a K8s Deployment with 2+ replicas and leader election. If the leader pod fails, the standby acquires the lease and continues reconciliation. The controller is stateless — all state is in K8s resources and AWS resources. A restarting controller reads current state and reconciles.

**Target health**: The ALB health checks each Pod independently. If a Pod fails health checks, the ALB stops routing to it. This is independent of K8s readiness probes — the ALB has its own health check path and interval.

**Multi-AZ Pod distribution**: Use topology spread constraints to distribute Pods across AZs:
```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
```
If an AZ goes down, the ALB routes traffic to healthy targets in other AZs. Combined with the cluster autoscaler or Karpenter, new Pods are launched in the remaining AZs.

**Cross-cluster**: For multi-cluster HA, use Route53 weighted/failover routing across ALBs in different clusters. Or use AWS Global Accelerator for anycast-based routing to the nearest healthy ALB."

---

## How the Industry Built This

- **AWS**: ALB Ingress Controller (now AWS Load Balancer Controller). Supports both ALB (Ingress) and NLB (Service type: LoadBalancer). IP-mode target groups with VPC-CNI. TargetGroupBinding CRD for fine-grained control. [AWS LB Controller docs](https://kubernetes-sigs.github.io/aws-load-balancer-controller/).
- **GKE**: GKE uses NEG (Network Endpoint Groups) — Google's equivalent of IP-mode target groups. Built-in integration with Google Cloud Load Balancer. GKE Gateway controller for Gateway API.
- **AKS**: Application Gateway Ingress Controller (AGIC) for Azure Application Gateway. Azure Load Balancer for L4. Azure CNI provides Pod IPs routable within the VNet.
- **Gateway API**: The successor to Ingress. Provides a more expressive, role-oriented API for load balancer configuration. Separates GatewayClass (infra provider), Gateway (cluster operator), HTTPRoute (application developer). [gateway-api.sigs.k8s.io](https://gateway-api.sigs.k8s.io/).

References:
- https://kubernetes-sigs.github.io/aws-load-balancer-controller/
- https://gateway-api.sigs.k8s.io/
- https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer
- https://aws.github.io/aws-eks-best-practices/networking/loadbalancing/

---

## The Complete Reference Design

### Ingress with ALB

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip           # IP mode
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:...
    alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS13-1-2-2021-06
    alb.ingress.kubernetes.io/healthcheck-path: /healthz
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: "10"
    alb.ingress.kubernetes.io/target-group-attributes: deregistration_delay.timeout_seconds=30
    alb.ingress.kubernetes.io/wafv2-acl-arn: arn:aws:wafv2:...
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /api/v1
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

### Gateway API (Modern Approach)

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: app-gateway
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  gatewayClassName: aws-alb
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    tls:
      certificateRefs:
      - name: app-cert
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: api-route
spec:
  parentRefs:
  - name: app-gateway
  hostnames:
  - "api.example.com"
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api/v1
    backendRefs:
    - name: api-service
      port: 80
      weight: 90
    - name: api-service-canary
      port: 80
      weight: 10
```

### Performance Characteristics
| Component | Metric | Value |
|-----------|--------|-------|
| ALB | Added latency | ~1-5ms |
| NLB | Added latency | ~100-200us |
| ALB | Max new connections/sec | ~25,000 per AZ |
| NLB | Max new connections/sec | ~millions per AZ |
| Target registration | Propagation time | ~5-10s |
| Health check | ALB interval | 5-300s (default 15s) |
| Health check | NLB interval | 10s or 30s |
| Connection draining | Default timeout | 300s |
| LB Controller | Reconciliation latency | ~1-5s for target changes |
| LB Controller | AWS API calls per reconcile | 2-5 calls per Service |

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| ALBs | 1 per Ingress (or shared via IngressGroup) | 5-50 ALBs |
| Target Groups | 1 per Service per Ingress rule | 50-500 TGs |
| NLBs | 1 per Service type:LoadBalancer | 5-20 NLBs |
| Pod IPs per TG | Max 1000 targets per TG | Scale horizontally with multiple TGs |
| LB Controller | CPU during reconciliation | 200m-500m |

---

## Senior vs Staff vs Principal

| Level | What they demonstrate | Example |
|-------|----------------------|---------|
| Senior | Knows Service types and Ingress basics, can explain L4 vs L7 | Sets up an ALB Ingress with path routing |
| Staff | Understands IP mode vs NodePort trade-offs, designs for zero-downtime, knows pod readiness gates | Explains the 502-during-deployment problem and the three-part fix, designs target group lifecycle |
| Principal | Designs the LB Controller itself, reasons about cloud API rate limits, architects cross-cluster LB strategy | Proposes Gateway API migration path, designs multi-cluster active-active with Route53, architects LB controller for 1000+ clusters |

---

## Red Flags and Common Mistakes

- **Using NodePort mode without understanding the extra hop**: In NodePort mode, traffic hits a random node and gets rerouted via kube-proxy. This adds latency, loses source IP, and creates uneven load distribution.
- **Not configuring pod readiness gates**: Without readiness gates, K8s considers a Pod ready before the LB has registered it. During rolling updates, this causes traffic to hit Pods that are not yet receiving LB traffic — and more critically, causes old Pods to be terminated before new ones are truly ready.
- **Ignoring connection draining during termination**: If the app shuts down immediately on SIGTERM without a preStop sleep, the LB is still sending traffic to the terminating Pod. This is the number one cause of 502s during deployments.
- **One ALB per Ingress**: By default, each Ingress creates a separate ALB. At 50 Services, that is 50 ALBs — expensive and unnecessary. Use `alb.ingress.kubernetes.io/group.name` to share ALBs across Ingresses.
- **Not considering the gRPC load balancing problem**: gRPC over HTTP/2 multiplexes requests over a single TCP connection. L4 load balancers distribute connections, not requests. You need L7 load balancing or client-side load balancing for gRPC.
