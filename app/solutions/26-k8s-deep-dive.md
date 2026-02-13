# Design a Container Orchestration System (Kubernetes Deep Dive)

> **Companies**: Google (GKE team), Microsoft (AKS), Amazon (EKS), every company with platform engineering
> **Level**: Staff / Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you reason about declarative state management, control loop semantics, eventual consistency in a reconciliation-based system, and the trade-offs of a level-triggered architecture at scale?
> **Your EKS advantage**: You build the thing. You know why the API server watch cache exists, why etcd compaction matters, and what happens when a control loop falls behind. You can talk about real production numbers, not textbook theory.

---

## The First 5 Minutes — Technical Scoping

- "Are we designing a managed orchestration system like EKS/GKE, or self-managed? That fundamentally changes who owns the control plane lifecycle — upgrades, HA, etcd backup/restore."
- "What cluster scale? 100 nodes with 5K pods, or 5,000 nodes with 150K pods? At 5K nodes the bottlenecks shift from scheduler throughput to API server memory pressure and etcd write amplification."
- "What workload mix? Long-running services, batch jobs, or GPU training workloads? This changes scheduling policy and preemption design."
- "Do we need multi-tenancy? Namespace-level soft isolation, or hard isolation with virtual clusters? Determines our admission control and RBAC strategy."
- "What's our API server QPS target? In production EKS, a 1000-node cluster generates roughly 2,000-3,000 QPS against the API server, and a large chunk of that is list/watch traffic from controllers."
- "What's the upgrade SLA? Zero-downtime control plane upgrades? That forces HA API server design with rolling update semantics."
- "Do workloads need hard scheduling guarantees — bin packing for cost, or spread for availability? This shapes the scheduler plugin architecture."
- "Are we supporting custom resource definitions and custom controllers? That's where most real platform complexity lives."

### Working Assumptions
| Parameter | Value |
|-----------|-------|
| Cluster size | 1,000 nodes, scaling to 5,000 |
| Pod count | 50,000 active pods |
| API server QPS | ~2,500 sustained, ~8,000 burst |
| etcd | 3-node quorum, ~8 GB database size |
| etcd write throughput | ~10,000 writes/sec sustained |
| etcd p99 read latency | <5ms at steady state |
| Scheduler throughput | ~100 pods/sec for standard scheduling |
| Control plane HA | 3 API servers, leader-elected controller-manager and scheduler |
| Node heartbeat interval | 10s (Lease-based) |
| Watch connections | ~5,000 concurrent (controllers + kubelets + operators) |

---

## High-Level Architecture

```
                            ┌─────────────────────────────────────┐
                            │         Control Plane (HA)          │
  kubectl / SDK             │                                     │
       │                    │  ┌───────────┐   ┌───────────────┐  │
       │  HTTPS/gRPC        │  │ API Server │──▶│     etcd      │  │
       ├───────────────────▶│  │  (x3 HA)  │◀──│  (3-node Raft)│  │
       │                    │  └─────┬──┬──┘   └───────────────┘  │
       │                    │        │  │                          │
       │                    │   ┌────┘  └────┐                    │
       │                    │   ▼            ▼                    │
       │                    │ ┌──────────┐ ┌───────────┐          │
       │                    │ │Controller │ │ Scheduler │          │
       │                    │ │ Manager   │ │(leader-   │          │
       │                    │ │(leader-   │ │ elected)  │          │
       │                    │ │ elected)  │ └───────────┘          │
       │                    │ └──────────┘                        │
       │                    └─────────────────────────────────────┘
       │
       │                    ┌─────────────────────────────────────┐
       │                    │           Data Plane (per Node)     │
       │                    │                                     │
       │                    │  ┌─────────┐  ┌─────────────────┐   │
       │                    │  │ kubelet  │──│ Container Runtime│  │
       │                    │  │         │  │ (containerd/CRI) │   │
       │                    │  └────┬────┘  └─────────────────┘   │
       │                    │       │                              │
       │                    │  ┌────┴────┐  ┌──────────┐          │
       │                    │  │kube-proxy│  │ CNI Plugin│          │
       │                    │  │/ cilium  │  │(VPC-CNI) │          │
       │                    │  └─────────┘  └──────────┘          │
       │                    │                                     │
       │                    │  ┌──────────┐  ┌──────────┐         │
       │                    │  │CSI Driver │  │ Node     │         │
       │                    │  │          │  │ Problem  │         │
       │                    │  │          │  │ Detector │         │
       │                    │  └──────────┘  └──────────┘         │
       │                    └─────────────────────────────────────┘
```

**Why this architecture**: Kubernetes is fundamentally a *declarative state management system*. The user writes desired state (Deployment spec), the system continuously reconciles actual state toward desired state. This is level-triggered, not edge-triggered — if a controller misses an event, it will still converge because it always compares full desired vs. actual state on every reconciliation. This makes the system self-healing by design, at the cost of increased read load on the API server.

---

## Core Concepts Deep Dive

### Concept 1: The Reconciliation Loop Pattern

This is the beating heart of Kubernetes. Every controller — Deployment, ReplicaSet, StatefulSet, your custom operators — follows the same pattern.

**The actual mechanics** (not the textbook version):

1. **SharedIndexInformer**: Each controller creates informers for the resources it cares about. The informer establishes a watch connection to the API server and maintains a local cache (the *store*). On startup, it does a full LIST, then switches to WATCH for incremental updates.

2. **DeltaFIFO queue**: Watch events (ADDED, MODIFIED, DELETED) flow into a DeltaFIFO queue inside the informer. This is a FIFO queue where each entry is keyed by object namespace/name and contains deltas (changes).

3. **Indexer/Cache**: The reflector pops deltas off the DeltaFIFO and applies them to the thread-safe store (cache). This gives controllers O(1) reads without hitting the API server.

4. **Event handlers to Work queue**: The informer calls registered event handlers (AddFunc, UpdateFunc, DeleteFunc). These handlers typically just enqueue the object key (`namespace/name`) into a rate-limited work queue — they do NOT do real work.

5. **Worker goroutines to Reconcile**: Worker goroutines pull keys off the work queue and call the reconciliation function. The reconciler reads desired state from the cache, compares to actual state, and takes corrective action.

**Why level-triggered beats edge-triggered**: If a watch connection drops and reconnects, the informer does a re-list. The reconciler doesn't care — it just compares desired vs. actual. Edge-triggered systems (react to events) can miss events and drift. Level-triggered systems (react to state differences) self-correct.

```go
// The canonical controller-runtime reconcile pattern
func (r *DeploymentReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var deployment appsv1.Deployment
    if err := r.Get(ctx, req.NamespacedName, &deployment); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Compare desired state (deployment.Spec) vs actual state (ReplicaSets, Pods)
    existingRS, err := r.getReplicaSetsForDeployment(ctx, &deployment)
    if err != nil {
        return ctrl.Result{}, err
    }

    // Reconcile: create/update/delete ReplicaSets to match desired state
    if needsRollout(&deployment, existingRS) {
        return r.rollout(ctx, &deployment, existingRS)
    }

    return ctrl.Result{}, nil
}
```

### Concept 2: etcd — The Source of Truth

etcd is a distributed key-value store using Raft consensus. In Kubernetes, it is the single source of truth for all cluster state.

**Raft internals that matter for K8s**:
- **Leader election**: One etcd node is leader, handles all writes. Followers replicate. Leader sends heartbeats; if followers don't hear from leader, they start an election. In a 3-node cluster, you need 2 nodes for quorum.
- **Log replication**: Leader appends write to its log, replicates to followers. Once a majority acknowledges, the write is committed. This means a 3-node etcd cluster tolerates 1 node failure for writes.
- **MVCC (Multi-Version Concurrency Control)**: etcd stores every revision of every key. The API server uses this for watch semantics — "give me all changes since revision X." This is how watches work efficiently.
- **Compaction**: Old revisions accumulate. etcd must compact (garbage collect old revisions) periodically. If compaction falls behind, the database grows unbounded. EKS runs auto-compaction every 5 minutes. If your watch tries to resume from a revision that has been compacted, you get a `410 Gone` and must re-list.

**Why etcd is the bottleneck at scale**:
- Every object write (Pod creation, status update, node heartbeat) goes through etcd
- At 5K nodes with 10s heartbeat intervals, that is 500 Lease updates/sec just for node heartbeats
- Pod status updates during deployments create write storms
- The API server watch cache helps with reads, but writes always hit etcd

**What EKS does**: EKS runs etcd on dedicated instances with provisioned IOPS (io2 EBS volumes), auto-compaction, periodic snapshots to S3, and automatic defragmentation during maintenance windows.

### Concept 3: The API Server — Gateway to Everything

The API server is a stateless HTTP/gRPC server that serves as the hub for all cluster communication. Nothing talks to etcd directly except the API server.

**Request processing pipeline**:
1. **Authentication**: x509 client certs, bearer tokens, OIDC, webhook token review. EKS uses IAM authentication via `aws-iam-authenticator` (maps IAM roles/users to K8s identities).
2. **Authorization**: RBAC (Role-Based Access Control), ABAC, webhook. RBAC checks if the authenticated identity has permission for the requested verb on the requested resource.
3. **Admission Control**: Mutating webhooks, then object schema validation, then validating webhooks. This is where policies like "inject sidecar" (Istio) or "enforce resource limits" (OPA/Gatekeeper) run.
4. **etcd storage**: Object is serialized (protobuf for built-in types, JSON for CRDs) and written to etcd.
5. **Watch notification**: The watch cache picks up the etcd event and fans it out to all watchers.

**The watch cache** is critical for scale. Without it, every controller's watch would be a separate etcd watch. The API server maintains a single watch per resource type against etcd, caches recent events, and multiplexes to all client watchers. At 5K nodes, you might have 10,000+ watch connections — each one against etcd would destroy it.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "What happens when you run kubectl apply?"

**Interviewer**: "Walk me through exactly what happens from the moment you hit enter on `kubectl apply -f deployment.yaml`."

**You**: "Starting client-side: kubectl reads the kubeconfig file, which specifies the cluster endpoint, auth method, and CA cert. For EKS, the kubeconfig has an `exec` block that calls `aws eks get-token`, which generates a presigned STS URL as a bearer token. kubectl resolves the API server DNS, establishes TLS, and sends an HTTP PUT or PATCH to `/apis/apps/v1/namespaces/default/deployments/my-app`.

Server-side, the request hits the API server handler chain. First, authentication — the token authenticator extracts the bearer token, calls the token review webhook (aws-iam-authenticator), which validates the STS presigned URL and returns the mapped Kubernetes identity.

Next, RBAC authorization checks: does this identity have the `update` or `patch` verb on `deployments` in this namespace? If RBAC denies it, we get a 403.

Then admission control — mutating admission webhooks fire first. For example, a webhook might inject default resource requests/limits. Then the object passes schema validation. Then validating webhooks fire — OPA/Gatekeeper might enforce 'all deployments must have resource limits.'

Finally, the API server writes to etcd. For `apply`, it uses server-side apply with field management — it tracks which fields each applier owns to enable safe concurrent updates. The object gets a new resourceVersion (etcd revision). The response goes back to kubectl with the updated object."

**Interviewer**: "Now the Deployment exists. How does a running Pod actually materialize?"

**You**: "The Deployment controller in kube-controller-manager is watching Deployments via a SharedIndexInformer. It picks up the new Deployment, computes the desired ReplicaSet spec (using the pod template hash), and creates a ReplicaSet object via the API server.

The ReplicaSet controller, also in kube-controller-manager, is watching ReplicaSets. It picks up the new ReplicaSet, sees that desired replicas is 3 but actual pods is 0, and creates 3 Pod objects. These Pods have `spec.nodeName` unset — they are *unscheduled*.

The scheduler is watching for Pods with empty `spec.nodeName`. It picks up each Pod and runs the scheduling cycle:
1. **Filtering**: Run filter plugins — does the node have enough CPU/memory? Does it match nodeSelector? Do taints/tolerations allow it? Are PV topology constraints satisfied?
2. **Scoring**: Run scoring plugins on passing nodes — least requested resources, node affinity scores, pod topology spread, inter-pod affinity.
3. **Binding**: The scheduler does an optimistic `Bind` — it updates the Pod's `spec.nodeName` via the API server. This is async — the scheduler does not wait for the Pod to actually start.

The kubelet on the target node is watching for Pods assigned to its node. It picks up the Pod, calls the CRI (Container Runtime Interface) — typically containerd — to pull images and start containers. The CNI plugin (like VPC-CNI on EKS) allocates an IP address from the VPC subnet. The Pod gets a network namespace with that IP. The kubelet updates Pod status back to the API server."

**Interviewer**: "What if the node dies after the Pod starts?"

**You**: "The node controller in kube-controller-manager monitors node health via Lease objects. Each kubelet renews its Lease every 10 seconds. The node controller checks leases with a default tolerance of 40 seconds. After 40 seconds without a lease renewal, the node controller marks the node condition as `Unknown`.

After `pod-eviction-timeout` (the taint-based eviction flow uses `--default-not-ready-toleration-seconds=300`), the node controller adds a `NoExecute` taint: `node.kubernetes.io/unreachable:NoExecute`. Pods without a matching toleration get evicted — the Pod objects are deleted.

The ReplicaSet controller then sees that it has fewer Pods than desired replicas and creates new Pod objects. The scheduler binds them to healthy nodes. The entire self-healing loop runs without any central coordinator — each controller independently reconciles its part of the state."

**Interviewer**: "What are the problems with this eviction approach at scale?"

**You**: "Several. First, the 5-minute default eviction timeout is slow for stateless workloads. Many teams override `tolerationSeconds` on their Pods to 30 seconds. Second, if you have a network partition that makes 100 nodes appear unreachable simultaneously, the node controller rate-limits evictions to avoid cascading failure (`--node-eviction-rate=0.1`, meaning 1 node per 10 seconds). In a large zone failure, evictions can take a long time.

Third, the Lease-based heartbeat does not detect all failure modes — a node might have kubelet running but the container runtime hung. Node Problem Detector catches some of these cases but is not comprehensive. At EKS, we supplement this with EC2-level health checks — if the underlying EC2 instance fails its system status check, we can proactively terminate the instance and let the node auto-scaler replace it, which is faster than waiting for the K8s Pod eviction timeout."

### Deep Dive Path 2: "Design the scheduling algorithm"

**Interviewer**: "Scheduling throughput is a bottleneck. How would you redesign the scheduler?"

**You**: "The default scheduler does serial scheduling — one Pod at a time through the filter/score cycle. At 100 pods/sec that is fine for most clusters, but for batch workloads spinning up thousands of Pods, it becomes a bottleneck.

The Scheduler Framework (KEP-624) made the scheduler extensible via plugins at defined extension points: PreFilter, Filter, PostFilter, PreScore, Score, Reserve, Permit, PreBind, Bind, PostBind. This lets you swap scheduling logic without forking the scheduler.

For throughput, you can enable scheduling parallelism by evaluating nodes in parallel during the filter/score phase. The scheduler already limits the percentage of nodes scored (default 50% for clusters with more than 100 nodes, controlled by `percentageOfNodesToScore`).

For batch scheduling, you want *gang scheduling* — schedule all N pods of a job together or none. The community has Coscheduling (scheduler plugin) and Volcano for this. The key challenge is avoiding deadlock — if Job A needs 10 GPUs and Job B needs 10 GPUs, and only 16 are available, you need priority-based preemption.

For multi-scheduler architectures, you can run domain-specific schedulers alongside the default. Each Pod specifies its scheduler via `spec.schedulerName`. The risk is resource conflicts — two schedulers might assign Pods to the same node, overcommitting it. Kubernetes handles this via kubelet admission rejecting Pods that exceed node capacity, but that creates churn."

### Deep Dive Path 3: "How would you handle control plane upgrades?"

**Interviewer**: "Walk me through zero-downtime Kubernetes control plane upgrades."

**You**: "In EKS, the control plane is fully managed so we handle this for customers. The approach is:

1. **API servers** are stateless and sit behind a load balancer. You can run old and new versions simultaneously as long as they support the same storage versions. Deploy new API server instances, health-check them, then drain old ones. The NLB handles connection draining.

2. **etcd** upgrades are trickier because of Raft. We do rolling upgrades: take one member out, upgrade it, rejoin. With a 3-node cluster, quorum is maintained throughout. The key constraint is etcd only supports one minor version skew between members during upgrade.

3. **Controller manager and scheduler** are leader-elected. The upgrade process: start new version, stop old version, new version acquires the Lease. During the switch there is a brief period with no active controller, but since the system is level-triggered, it catches up immediately.

4. **Version skew policy** is critical: API server must be >= controller-manager/scheduler version, and kubelet can be up to 3 minor versions behind the API server (as of 1.28+). This allows control plane first, then gradual node upgrades.

The hard part is CRD schema changes. If a custom controller uses a CRD that changes schema across versions, you need the conversion webhook running to translate between versions during the upgrade window."

---

## How the Industry Built This

- **EKS**: Runs a managed control plane per customer (dedicated etcd, API servers) in a separate AWS-managed VPC. Uses ENI cross-account attachment to connect the customer data plane to the managed control plane. The EKS control plane runs across 3 AZs. Reference: [EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/).
- **GKE**: Pioneered managed K8s. GKE Autopilot fully manages the data plane too — you just submit Pods. Under the hood, GKE runs K8s control planes on Borg. Uses Dataplane V2 (based on Cilium eBPF) for networking.
- **AKS**: Runs shared control planes for small clusters, dedicated for large ones. Uses Azure CNI for networking. Virtual nodes (ACI) for burst capacity.
- **Open source KEPs**: KEP-624 (Scheduling Framework), KEP-1040 (Priority and Fairness for API server), KEP-2876 (CRD Validation with CEL), KEP-3488 (CEL for Admission Control), KEP-3157 (API server tracing with OpenTelemetry).

---

## The Complete Reference Design

### Key Resource Definitions

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app.kubernetes.io/name: web-app
    app.kubernetes.io/version: "1.2.3"
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero-downtime deployments
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: web-app
      containers:
      - name: web-app
        image: 123456789.dkr.ecr.us-west-2.amazonaws.com/web-app:1.2.3
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            memory: 512Mi  # No CPU limits — best practice
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 20
```

### Controller Pattern (Go)

```go
func (r *WebAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    var app myv1.WebApp
    if err := r.Get(ctx, req.NamespacedName, &app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Reconcile the Deployment
    deploy := &appsv1.Deployment{ObjectMeta: metav1.ObjectMeta{
        Name: app.Name, Namespace: app.Namespace,
    }}
    result, err := ctrl.CreateOrUpdate(ctx, r.Client, deploy, func() error {
        deploy.Spec.Replicas = app.Spec.Replicas
        deploy.Spec.Template.Spec.Containers[0].Image = app.Spec.Image
        return ctrl.SetControllerReference(&app, deploy, r.Scheme)
    })
    if err != nil {
        return ctrl.Result{}, err
    }
    log.Info("Deployment reconciled", "result", result)

    // Update status
    app.Status.AvailableReplicas = deploy.Status.AvailableReplicas
    if err := r.Status().Update(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}
```

### Performance Characteristics
| Component | Metric | Value at 1K nodes | Value at 5K nodes |
|-----------|--------|-------------------|-------------------|
| API Server | QPS | ~2,500 | ~12,000 |
| API Server | Watch connections | ~3,000 | ~15,000 |
| API Server | Memory | ~4 GB | ~20 GB |
| etcd | Write latency p99 | ~8ms | ~30ms |
| etcd | DB size | ~2 GB | ~8 GB |
| Scheduler | Throughput | ~100 pods/sec | ~50 pods/sec |
| Scheduler | p99 latency | ~20ms | ~100ms |
| Node heartbeat | Lease updates/sec | 100 | 500 |

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| etcd disk IOPS | 10K writes/sec * 3 (Raft replication) | ~30K IOPS (io2 EBS) |
| API server CPU | ~1 core per 500 QPS | 5-24 cores |
| API server memory | ~4 MB per watch + object cache | 4-20 GB |
| etcd memory | ~2x DB size for working set | 4-16 GB |
| Network (control plane) | watch fan-out * avg event size | ~100 Mbps per API server |

---

## Senior vs Staff vs Principal

| Level | What they demonstrate | Example |
|-------|----------------------|---------|
| Senior | Understands K8s architecture, can design controllers, handles one deep dive | Explains reconciliation loop correctly, knows API server request lifecycle |
| Staff | Understands cross-component interactions, performance implications, proposes improvements | Explains why API Priority and Fairness matters for protecting system-critical watches, knows etcd scaling limits, can design custom schedulers |
| Principal | Challenges the K8s model itself, reasons about fleet management, drives platform strategy | Discusses when K8s adds unnecessary complexity, proposes simplified abstractions like Autopilot, reasons about multi-cluster federation trade-offs |

---

## Red Flags and Common Mistakes

- **Treating K8s as a black box**: Saying "the scheduler picks a node" without explaining filter/score plugins, percentageOfNodesToScore, or the scheduling framework extension points.
- **Not understanding eventual consistency**: Thinking K8s operations are synchronous. Everything is asynchronous and eventually consistent — `kubectl apply` returns before any Pod exists.
- **Ignoring etcd as the bottleneck**: Designing without considering etcd write amplification, compaction, or the fact that every status update is an etcd write.
- **Missing the watch cache**: Not knowing that the API server caches watch events and multiplexes them. Without this, the system cannot scale.
- **Adding CPU limits**: Many candidates add CPU limits, but CPU throttling (CFS bandwidth control) causes latency spikes. Best practice is CPU requests (for scheduling) without CPU limits. Memory limits are essential to prevent OOM kills of other Pods.
- **Confusing level-triggered vs edge-triggered**: This is the most fundamental K8s concept. If you cannot explain why level-triggered reconciliation is more resilient than event-driven, you do not deeply understand K8s.
