# Design a Control Plane

> **Companies**: Amazon (EKS), Google (GKE), Microsoft (AKS), any managed K8s provider, AI infra companies
> **Level**: Staff / Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a highly available, strongly consistent control plane that serves as the coordination layer for a distributed system? Can you reason about leader election, Raft consensus, admission control pipelines, and API server scalability?
> **Your EKS advantage**: You work on the EKS control plane. You know the cross-account ENI architecture, how etcd is managed at scale, how API server priority and fairness works in production, and the real failure modes of HA control planes.

---

## The First 5 Minutes — Technical Scoping

- "Is this a managed control plane (EKS-style, where the provider runs it) or self-managed? If managed, we need to design for multi-tenant control plane hosting and cross-account network isolation."
- "What's the target cluster scale? At 100 nodes the control plane is trivial. At 5,000 nodes, API server memory pressure from the watch cache becomes the primary bottleneck, and etcd write latency determines your Pod scheduling throughput."
- "What's our availability SLA? 99.95% (EKS SLA) means ~22 minutes downtime per month. 99.99% means ~4 minutes. That changes our HA topology and failover strategy."
- "Do we need to support custom resource definitions and aggregated API servers? CRDs change storage and conversion webhook requirements. Aggregated API servers change our routing architecture."
- "What's the upgrade model? In-place rolling updates or blue-green? K8s has strict version skew policies — API server must be the newest component."
- "What admission control requirements exist? Webhook latency directly impacts API request latency. A slow validating webhook can make the entire cluster feel broken."
- "Do we need audit logging? Every API request? That's significant I/O — at 5K QPS with full request/response bodies, audit logs can be 10+ GB/day."

### Working Assumptions
| Parameter | Value |
|-----------|-------|
| Target clusters | 1,000-5,000 nodes per cluster |
| API server QPS | ~3,000 sustained, ~10,000 burst |
| etcd cluster | 3 or 5 nodes, cross-AZ |
| etcd DB size limit | 8 GB (etcd default, configurable) |
| Watch connections | 5,000-15,000 concurrent |
| Availability SLA | 99.95% (managed), 99.9% (self-managed) |
| Upgrade window | Zero-downtime for API server, <30s for controller failover |
| Admission webhook timeout | 10s default, 2s recommended |
| Audit log volume | ~5 GB/day at Metadata level for 1K-node cluster |

---

## High-Level Architecture

```
  Client (kubectl, controllers, kubelets)
       │
       │  HTTPS (mTLS)
       ▼
  ┌──────────────┐
  │   L4 Load    │  NLB / internal LB
  │   Balancer   │  Health checks: /healthz, /readyz, /livez
  └──────┬───────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐┌────────┐┌────────┐
│API Srv ││API Srv ││API Srv │   Stateless, horizontally scaled
│  (v1)  ││  (v1)  ││  (v1)  │   Each serves all API groups
└───┬────┘└───┬────┘└───┬────┘
    │         │         │
    │    ┌────┴────┐    │        Watch cache per API server
    │    │ Shared  │    │        (in-memory ring buffer of events)
    │    │ etcd    │    │
    │    │ watches │    │
    │    └─────────┘    │
    │         │         │
    ▼         ▼         ▼
┌─────────────────────────────┐
│     etcd cluster (Raft)     │
│  ┌──────┐┌──────┐┌──────┐  │
│  │Node 1││Node 2││Node 3│  │  One leader, two followers
│  │(AZ-a)││(AZ-b)││(AZ-c)│  │  Quorum: 2 of 3
│  └──────┘└──────┘└──────┘  │
└─────────────────────────────┘

┌──────────────────────────────────┐
│  Leader-Elected Components       │
│  ┌───────────────┐ ┌──────────┐  │
│  │ kube-controller│ │  kube-   │  │  Only leader is active
│  │ -manager       │ │scheduler │  │  Lease-based election
│  │ (active/standby│ │(active/  │  │  Lease duration: 15s
│  │  x3)          │ │standby)  │  │  Renew interval: 10s
│  └───────────────┘ └──────────┘  │
└──────────────────────────────────┘
```

**Why this architecture**: The control plane separates concerns along consistency boundaries. The API server is stateless and horizontally scalable — any instance can serve any request. etcd provides strong consistency via Raft (linearizable reads and writes). The controller manager and scheduler are leader-elected because they must make serialized decisions (you don't want two schedulers binding the same Pod to different nodes). This separation means the read path scales independently from the write path, and the coordination path (controllers) doesn't bottleneck the data path (API serving).

---

## Core Concepts Deep Dive

### Concept 1: API Server Request Pipeline

The API server is the most complex component in the control plane. It is an HTTP server with a sophisticated handler chain.

**The full request pipeline**:

```
Request → TLS termination
  → Authentication (authn chain: x509 → bearer token → OIDC → webhook)
  → Authorization (authz chain: RBAC → webhook → node authorizer)
  → Mutating Admission (webhooks, in order)
  → Object Schema Validation
  → Validating Admission (webhooks, in parallel)
  → etcd Read/Write (via storage layer)
  → Response
```

**API Priority and Fairness (APF)** — KEP-1040: This is critical at scale. Without APF, a misbehaving controller can send thousands of LIST requests and starve the kubelet heartbeats. APF classifies requests into priority levels and uses fair queuing (shuffle sharding) within each level. System-critical traffic (node heartbeats, leader election) gets the highest priority. User requests get lower priority.

```yaml
apiVersion: flowcontrol.apiserver.k8s.io/v1beta3
kind: PriorityLevelConfiguration
metadata:
  name: system-critical
spec:
  type: Limited
  limited:
    nominalConcurrencyShares: 100
    lendablePercent: 0  # Never lend capacity to lower priorities
    limitResponse:
      type: Queue
      queuing:
        queues: 64
        handSize: 8
        queueLengthLimit: 50
---
apiVersion: flowcontrol.apiserver.k8s.io/v1beta3
kind: FlowSchema
metadata:
  name: protect-node-heartbeats
spec:
  priorityLevelConfiguration:
    name: system-critical
  matchingPrecedence: 100
  rules:
  - subjects:
    - kind: Group
      group:
        name: system:nodes
    resourceRules:
    - verbs: ["update"]
      apiGroups: ["coordination.k8s.io"]
      resources: ["leases"]
```

### Concept 2: Leader Election Mechanics

The controller manager and scheduler use Kubernetes Lease objects for leader election. This is not a distributed lock — it is a lease with a timeout.

**How it works**:
1. Each instance tries to create or update a Lease object in `kube-system` namespace.
2. The holder writes its identity and a `renewTime` timestamp.
3. The holder must renew before `leaseDurationSeconds` expires (default 15s, renew every 10s).
4. If the lease expires, another instance can acquire it by doing a conditional update (using `resourceVersion` for optimistic concurrency).

**What happens during failover**:
- Current leader process crashes or loses connectivity.
- Lease is NOT renewed. After 15 seconds, it expires.
- Standby instances attempt to acquire the lease. One succeeds.
- The new leader starts reconciling from current state (level-triggered, so it just reads desired vs. actual and catches up).
- During the 15-second gap, no controllers are running. Pods still run, but no new reconciliation happens. This is safe because the system is level-triggered — the new leader will reconcile everything.

**EKS implementation**: EKS runs 3 replicas of controller-manager and scheduler behind the managed control plane. The leader election happens against the same etcd cluster as the API server. The cross-AZ latency (typically 1-2ms within a region) is low enough that Lease renewal is reliable.

```go
// Leader election configuration in controller-manager
leaderElection: {
    leaderElect:        true,
    leaseDuration:      15 * time.Second,
    renewDeadline:      10 * time.Second,
    retryPeriod:        2 * time.Second,
    resourceLock:       "leases",
    resourceName:       "kube-controller-manager",
    resourceNamespace:  "kube-system",
}
```

### Concept 3: etcd Operations and Failure Modes

**Raft consensus in practice**:

etcd uses Raft for all state changes. The leader appends entries to its log, replicates to followers, and commits once a quorum (majority) acknowledges. For a 3-node cluster, quorum is 2. For 5 nodes, quorum is 3.

**Why 3 nodes, not 5**: In most K8s deployments, 3 etcd nodes is standard. 5 nodes gives you tolerance for 2 failures (vs 1), but adds write latency because the leader must wait for 3 acknowledgments instead of 2. For cross-AZ deployments where each AZ has 1 etcd node, 3 nodes in 3 AZs is the sweet spot — you survive a full AZ failure.

**etcd failure modes that affect K8s**:

1. **Slow disk**: etcd is extremely sensitive to disk latency. If `wal_fsync_duration_seconds` exceeds 10ms consistently, leader heartbeats fail and you get unnecessary leader elections. This causes API server request failures. EKS uses io2 EBS volumes with provisioned IOPS to prevent this.

2. **Database size limit**: etcd has a default 2 GB limit (configurable to 8 GB). If the DB hits this limit, etcd rejects all writes with `mvcc: database space exceeded`. The cluster is effectively frozen. You must compact and defragment to recover. This happens when compaction falls behind (too many revisions accumulate) or when someone stores large objects (secrets with huge certificates, configmaps with big files).

3. **Watch starvation**: If many clients establish watches and the event rate is high, the etcd server can spend all its CPU serializing and sending watch events, starving write requests. The API server watch cache mitigates this by maintaining one watch per resource type to etcd and multiplexing to clients.

4. **Split brain during network partition**: Raft prevents split brain by requiring quorum for writes. If a partition isolates the leader from the majority, the majority elects a new leader. The old leader's writes since the partition are rejected. Clients connected to the old leader get errors and must reconnect.

**Key etcd metrics to monitor**:
- `etcd_server_leader_changes_seen_total` — frequent leader changes indicate disk/network issues
- `etcd_disk_wal_fsync_duration_seconds` — p99 should be <10ms
- `etcd_mvcc_db_total_size_in_bytes` — track against the 8 GB limit
- `etcd_server_proposals_failed_total` — proposal failures indicate quorum loss

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Design the admission control pipeline"

**Interviewer**: "How would you design an extensible admission control system?"

**You**: "Admission control runs after authentication and authorization, before the object is persisted to etcd. There are two phases: mutating and validating.

Mutating admission runs first because it can modify the object. Webhooks are called in order (determined by webhook configuration). Each webhook receives the `AdmissionReview` object, can patch the object (JSON Patch), and return it. Common use cases: injecting sidecar containers (Istio), adding default resource limits, injecting node selectors for multi-tenancy.

After mutation, the API server validates the object against its OpenAPI schema. Then validating webhooks run — these can reject but not modify. They run in parallel for performance. Common use cases: OPA/Gatekeeper policy enforcement, image allowlisting, label requirements.

The key design decisions are:
1. **Failure policy**: `Fail` or `Ignore`. If a webhook is unreachable, do you reject all requests (safe but causes outages) or skip the webhook (available but bypasses policy)? In production, system-critical webhooks (like security policy) should `Fail`, while optional webhooks should `Ignore`.
2. **Timeout**: Default is 10s but should be 2-3s in practice. A slow webhook blocks every API request that matches its rules.
3. **Scope**: Match rules should be as narrow as possible. A webhook that matches all resources in all namespaces will be called for every API request, including the control plane's own operations. A misconfigured webhook can lock you out of the cluster — you cannot even delete the webhook because the deletion request also triggers it."

**Interviewer**: "How do you prevent a webhook from bricking the cluster?"

**You**: "Several approaches. First, exclude `kube-system` and control plane namespaces from webhook rules using `namespaceSelector`. Second, use `objectSelector` to only match specific labels. Third, the API server has a `--enable-admission-plugins` flag with built-in admission controllers that run before webhooks — these cannot be broken by external services.

For EKS, we run admission webhooks with `failurePolicy: Ignore` for non-critical webhooks and have circuit-breaking — if a webhook fails consistently, we temporarily stop calling it. The `matchPolicy: Equivalent` setting also helps by routing requests through webhooks even when the API version differs from the configured rule.

The nuclear option is disabling webhooks via the API server flag `--disable-admission-plugins`, but in a managed service you cannot do that. Instead, you use `kubectl delete validatingwebhookconfiguration <name>` — this bypasses the webhook itself because webhook configurations are exempted from their own webhooks by default (since K8s 1.25 with the `matchConditions` field via CEL expressions)."

### Deep Dive Path 2: "How would you handle API server scalability?"

**Interviewer**: "Your API server is getting 10K QPS. It is falling over. What do you do?"

**You**: "First, I need to understand the request mix. In a typical K8s cluster, the majority of API server load is not from kubectl users — it is from controllers and kubelets doing list/watch operations. A 5K-node cluster has 5,000 kubelets each watching Pods, Services, ConfigMaps, Secrets. Plus controllers watching their respective resources.

The primary scalability lever is the **watch cache**. The API server maintains an in-memory cache of recent events per resource type. When a client does a watch, it reads from this cache, not from etcd. The cache is a ring buffer (default 100 events per resource, configurable via `--watch-cache-sizes`). This means 5,000 kubelets watching Pods all read from the same in-memory cache, not 5,000 separate etcd watches.

Second, **API Priority and Fairness (APF)**. Without APF, a misbehaving controller doing aggressive LIST requests can consume all API server capacity, starving kubelet heartbeats. APF ensures system-critical requests (node heartbeats, leader election) are always served, even under load.

Third, **horizontal scaling**. API servers are stateless — you can run 3, 5, or more behind a load balancer. The constraint is etcd — more API servers means more watch connections to etcd and higher write amplification. In practice, 3-5 API servers handle most clusters up to 5K nodes.

Fourth, **request coalescing**. When many controllers list the same resource simultaneously (e.g., after a watch bookmark or reconnect), the API server can coalesce these into a single etcd read. This is especially important during control plane restart when all informers re-list simultaneously.

Fifth, **reduce object sizes**. Large Secrets and ConfigMaps (>1 MB) cause etcd and API server pressure. Use external-secrets-operator for large secrets. Use projected volumes instead of mounting entire configmaps."

### Deep Dive Path 3: "Design the managed control plane architecture"

**Interviewer**: "You are building EKS. How do you run thousands of customer control planes?"

**You**: "The key architectural decision is isolation vs efficiency. Each customer gets dedicated etcd and API server instances — you cannot share etcd across customers because it holds all cluster secrets and a compromised etcd means full cluster compromise.

The architecture is:
1. **Control plane hosting**: Each customer's control plane (API servers, controller-manager, scheduler, etcd) runs as pods in a management cluster (or on dedicated EC2 instances). EKS runs these in a separate AWS-managed VPC, not in the customer's account.

2. **Network isolation**: The customer's worker nodes need to reach the API server. EKS creates cross-account ENIs in the customer's VPC that tunnel traffic to the managed control plane. This provides network-level isolation — the customer cannot access other customers' control planes, and the managed control plane can reach the customer's VPC for webhook calls.

3. **Right-sizing**: Small clusters (10 nodes) do not need the same resources as large clusters (5K nodes). The hosting platform must dynamically size etcd storage, API server memory, and controller-manager CPU based on cluster size and actual utilization.

4. **Upgrade orchestration**: When a new K8s version is released, the platform must upgrade thousands of control planes. This is a rolling operation with canary deployments — upgrade 1%, monitor for errors, then gradually roll out. If a customer's control plane has custom webhooks that break with the new version, the upgrade must be rolled back for that customer.

5. **Monitoring and SLO enforcement**: Each control plane has health checks and SLIs — API server latency p99, etcd leader stability, controller reconciliation lag. If an SLI degrades, the platform automatically takes remediation actions (restart unhealthy pods, scale up resources, trigger etcd defragmentation)."

---

## How the Industry Built This

- **EKS**: Dedicated control plane per customer in AWS-managed VPC. Cross-account ENIs for data plane connectivity. Auto-scaling etcd with io2 EBS. Managed add-ons (CoreDNS, kube-proxy, VPC CNI) with automated upgrades. [EKS architecture docs](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html).
- **GKE**: Runs control planes on Borg (Google's internal orchestrator). Pioneered managed node pools and Autopilot (fully managed data plane). Uses a regional control plane (3 AZs) by default.
- **AKS**: Shares control plane infrastructure for cost efficiency on smaller clusters. Free control plane tier (shared), paid tier (dedicated with SLA). Uses Azure Resource Manager for provisioning.
- **k3s**: Lightweight control plane using SQLite instead of etcd for single-node deployments. Demonstrates that etcd is the heaviest dependency in the control plane.

References:
- https://kubernetes.io/docs/concepts/overview/components/
- https://github.com/kubernetes/enhancements/tree/master/keps/sig-api-machinery/1040-priority-and-fairness
- https://etcd.io/docs/v3.5/op-guide/performance/
- https://aws.github.io/aws-eks-best-practices/reliability/docs/controlplane/

---

## The Complete Reference Design

### API Server Configuration (Key Flags)

```yaml
# Key API server configuration for production
apiVersion: v1
kind: Pod
metadata:
  name: kube-apiserver
spec:
  containers:
  - name: kube-apiserver
    command:
    - kube-apiserver
    - --etcd-servers=https://etcd-0:2379,https://etcd-1:2379,https://etcd-2:2379
    - --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt
    - --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml
    - --audit-policy-file=/etc/kubernetes/audit/policy.yaml
    - --audit-log-path=/var/log/kubernetes/audit.log
    - --audit-log-maxage=30
    - --enable-admission-plugins=NodeRestriction,PodSecurity
    - --authorization-mode=Node,RBAC
    - --watch-cache-sizes=pods#1000,nodes#1000
    - --max-requests-inflight=800
    - --max-mutating-requests-inflight=400
    - --request-timeout=60s
```

### etcd Cluster Configuration

```yaml
# etcd configuration for production K8s
name: etcd-0
data-dir: /var/lib/etcd
listen-client-urls: https://0.0.0.0:2379
listen-peer-urls: https://0.0.0.0:2380
initial-cluster: etcd-0=https://etcd-0:2380,etcd-1=https://etcd-1:2380,etcd-2=https://etcd-2:2380
auto-compaction-mode: periodic
auto-compaction-retention: "5m"
quota-backend-bytes: 8589934592  # 8 GB
snapshot-count: 10000
heartbeat-interval: 500        # 500ms — tuned for cross-AZ
election-timeout: 5000         # 5s — must be > 10x heartbeat for cross-AZ
```

### Controller Manager Reconciler Pattern

```go
// Custom controller with leader election and proper error handling
func main() {
    mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
        Scheme:                  scheme,
        LeaderElection:          true,
        LeaderElectionID:        "my-controller-leader",
        LeaderElectionNamespace: "kube-system",
        LeaseDuration:           ptr(15 * time.Second),
        RenewDeadline:           ptr(10 * time.Second),
        RetryPeriod:             ptr(2 * time.Second),
        Controller: config.Controller{
            MaxConcurrentReconciles: 10,  // Parallel reconciliation
        },
    })
    // Register reconcilers, start manager...
}

func (r *Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. Fetch the object
    var obj myv1.MyResource
    if err := r.Get(ctx, req.NamespacedName, &obj); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 2. Check if being deleted (finalizer pattern)
    if !obj.DeletionTimestamp.IsZero() {
        return r.handleDeletion(ctx, &obj)
    }

    // 3. Add finalizer if not present
    if !controllerutil.ContainsFinalizer(&obj, finalizerName) {
        controllerutil.AddFinalizer(&obj, finalizerName)
        if err := r.Update(ctx, &obj); err != nil {
            return ctrl.Result{}, err
        }
    }

    // 4. Reconcile desired state
    result, err := r.reconcileDesiredState(ctx, &obj)
    if err != nil {
        // Set degraded condition
        meta.SetStatusCondition(&obj.Status.Conditions, metav1.Condition{
            Type:    "Ready",
            Status:  metav1.ConditionFalse,
            Reason:  "ReconciliationFailed",
            Message: err.Error(),
        })
        r.Status().Update(ctx, &obj)
        return ctrl.Result{RequeueAfter: 30 * time.Second}, err
    }

    // 5. Update status
    meta.SetStatusCondition(&obj.Status.Conditions, metav1.Condition{
        Type:   "Ready",
        Status: metav1.ConditionTrue,
        Reason: "ReconciliationSucceeded",
    })
    return result, r.Status().Update(ctx, &obj)
}
```

### Performance Characteristics
| Component | Metric | Value at 1K nodes | Value at 5K nodes |
|-----------|--------|-------------------|-------------------|
| API Server | p99 latency (non-list) | ~50ms | ~200ms |
| API Server | p99 latency (list) | ~500ms | ~2s |
| API Server | Memory (watch cache) | ~2 GB | ~10 GB |
| etcd | Raft proposal latency | ~5ms | ~15ms |
| etcd | Leader elections/hour | 0 (stable) | 0 (stable) |
| Controller Manager | Reconciliation queue depth | ~100 | ~1,000 |
| Controller Manager | Reconcile latency p99 | ~100ms | ~500ms |
| Scheduler | Scheduling latency p99 | ~20ms | ~100ms |

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| etcd disk | DB size + WAL + snapshots | 50 GB SSD with 30K+ IOPS |
| etcd memory | 2x DB size | 8-16 GB |
| API server instances | 1 per 2K QPS | 2-5 instances |
| API server memory | watch cache + working set | 4-20 GB per instance |
| Controller manager | CPU-bound during reconciliation bursts | 4-8 cores |

---

## Senior vs Staff vs Principal

| Level | What they demonstrate | Example |
|-------|----------------------|---------|
| Senior | Knows the components and their roles, can explain request flow | Explains API server -> etcd flow, knows RBAC basics |
| Staff | Designs for failure, understands APF, can reason about etcd scaling limits | Explains why watch cache matters, designs webhook failure policies, knows etcd compaction mechanics |
| Principal | Designs the managed control plane hosting platform, reasons about multi-cluster fleet management | Proposes cross-account isolation architecture, designs control plane right-sizing and auto-remediation, discusses when to shard clusters vs scale single clusters |

---

## Red Flags and Common Mistakes

- **Skipping admission control**: Many candidates design the data path but forget the admission pipeline. Admission control is where security policy, multi-tenancy enforcement, and operational guardrails live.
- **Not understanding etcd quorum math**: Saying "5-node etcd is always better than 3-node" without understanding the write latency trade-off (5-node requires 3 acks, 3-node requires 2 acks) and the fact that for cross-AZ deployments, 3 nodes in 3 AZs survives a full AZ failure.
- **Treating the API server as a database**: The API server is a gateway with a watch cache. The database is etcd. Understanding this separation is key to scaling the control plane.
- **Ignoring API Priority and Fairness**: Without APF, a thundering herd of controller reconnects after a control plane restart can starve critical traffic. This is the most common production incident pattern at scale.
- **Not considering webhook failure modes**: A webhook that is down with `failurePolicy: Fail` will reject all matching requests, potentially including the requests needed to fix the webhook itself (deadlock).
