# Design a Container Orchestration System

> **Companies**: Amazon (EKS/ECS), Google (GKE), Microsoft (AKS), Docker, HashiCorp, Datadog | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Distributed consensus for cluster state, scheduling algorithms under constraints, how the control plane and data plane interact, failure detection and self-healing, understanding of the watch/reconciliation loop pattern that underpins Kubernetes

---

## The First 5 Minutes — Scoping & Technical Clarifications

These questions show you understand the distributed systems challenges, not just `kubectl apply`:

1. **Cluster scale?** Are we designing for 100 nodes or 15,000 nodes? This changes the state store choice, the scheduler design, and the API server architecture.
2. **Workload types?** Long-running services vs batch jobs vs DaemonSets vs CronJobs. Each has different scheduling, scaling, and lifecycle requirements.
3. **Scheduling latency SLA?** Time from pod submission to running on a node. Kubernetes targets <5 seconds for most pods — are we aiming for that?
4. **Consistency model for cluster state?** Strong consistency (Kubernetes uses etcd/Raft) vs eventual (Nomad-style). This is the foundational design choice.
5. **Multi-tenancy?** Single-tenant cluster vs multi-tenant with namespace isolation and resource quotas?
6. **Networking model?** Flat pod network (every pod gets a routable IP) vs NAT-based? This decides the CNI architecture.
7. **Storage requirements?** Stateless only, or do we support persistent volumes with dynamic provisioning?
8. **Upgrade strategy?** How do we update cluster components without downtime? Rolling updates of the control plane?

### Working Assumptions

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Cluster size | 5,000 nodes | Large production cluster |
| Pods per node | 110 (K8s default max) | ~550K total pods |
| API server QPS | 50,000 | Watches + CRUD from controllers, kubelet, users |
| etcd size | ~4 GB | All cluster objects serialized |
| Scheduling throughput | 100 pods/sec | Burst during deployments |
| Node heartbeat interval | 10 sec | kubelet -> API server |
| Pod eviction timeout | 5 min | After node deemed NotReady |
| p99 scheduling latency | <5 sec | From pending to scheduled |

**State math**: 550K pods x ~2 KB per pod spec = ~1.1 GB of pod state. Add services, endpoints, configmaps, secrets, CRDs: total etcd state ~4 GB. etcd recommends <8 GB — we're fine.

---

## High-Level Design

```
                    ┌─────────────────────────────────────────┐
                    │           CONTROL PLANE                  │
                    │                                          │
                    │  ┌──────────┐   ┌────────────────────┐  │
                    │  │ API      │   │ Controller Manager  │  │
                    │  │ Server   │◄─►│ (reconciliation     │  │
                    │  │ (REST +  │   │  loops)             │  │
                    │  │  Watch)  │   └────────────────────┘  │
                    │  └────┬─────┘   ┌────────────────────┐  │
                    │       │         │ Scheduler           │  │
                    │       │         │ (bin-packing +      │  │
                    │       │         │  affinity/anti-     │  │
                    │       │         │  affinity)          │  │
                    │  ┌────▼─────┐   └────────────────────┘  │
                    │  │ etcd     │                            │
                    │  │ (Raft    │                            │
                    │  │ consensus│                            │
                    │  │  3 or 5  │                            │
                    │  │  nodes)  │                            │
                    │  └──────────┘                            │
                    └───────────────────┬──────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────────┐
                    │                   │       DATA PLANE      │
                    │                   │                       │
          ┌─────────▼────────┐ ┌───────▼──────────┐  ┌────────▼───────┐
          │ Node 1           │ │ Node 2           │  │ Node N         │
          │ ┌──────────────┐ │ │ ┌──────────────┐ │  │ ┌────────────┐ │
          │ │ kubelet      │ │ │ │ kubelet      │ │  │ │ kubelet    │ │
          │ │ (watches API │ │ │ │              │ │  │ │            │ │
          │ │  server for  │ │ │ └──────────────┘ │  │ └────────────┘ │
          │ │  pod specs)  │ │ │ ┌──────────────┐ │  │ ┌────────────┐ │
          │ └──────────────┘ │ │ │ kube-proxy   │ │  │ │ kube-proxy │ │
          │ ┌──────────────┐ │ │ └──────────────┘ │  │ └────────────┘ │
          │ │ container    │ │ │ ┌──────────────┐ │  │ ┌────────────┐ │
          │ │ runtime (CRI)│ │ │ │ container    │ │  │ │ container  │ │
          │ └──────────────┘ │ │ │ runtime      │ │  │ │ runtime    │ │
          └──────────────────┘ │ └──────────────┘ │  │ └────────────┘ │
                               └──────────────────┘  └────────────────┘
```

**Why this architecture?** The declarative, level-triggered reconciliation model is the key insight. Instead of sending imperative commands ("start container X on node Y"), the system stores desired state (in etcd) and actual state (reported by kubelets). Controllers continuously reconcile the delta. This makes the system self-healing: if a controller crashes and restarts, it reads current state and catches up without needing a replay log. This is fundamentally different from imperative orchestration (like early Docker Swarm or Mesos frameworks).

---

## Core Concepts Deep Dive

### Concept 1: etcd and the Watch Protocol — The Source of Truth

**What it is**: etcd is a distributed key-value store using Raft consensus. Every cluster object (pod, service, deployment) is stored as a key-value pair in etcd. The API server is the only component that talks to etcd directly. All other components talk to the API server via REST + Watch.

**How it applies**: The Watch protocol is what makes Kubernetes reactive. When a controller starts, it lists all objects of its type, then opens a watch stream. etcd tracks a global revision number — each mutation increments it. A watch request says "give me all changes since revision X." If the controller loses connection, it reconnects with its last-seen revision and picks up where it left off. No polling needed.

**The math**: At 5,000 nodes with 110 pods each, kubelet heartbeats generate 5,000 node updates / 10 sec = 500 writes/sec to etcd. Add pod status updates, endpoint changes, leader elections: total ~2,000-5,000 writes/sec. etcd's throughput limit is ~10,000-20,000 writes/sec with SSDs, so we have headroom. But this is why clusters beyond 5,000 nodes need careful tuning.

**Common misconception**: "etcd is the bottleneck, replace it with a relational database." The issue isn't etcd's performance — it's the Watch semantics. etcd's MVCC with revision-based watches gives exactly-once ordered delivery of state changes. Replacing etcd requires replicating these semantics, which is non-trivial. K3s uses SQLite/PostgreSQL behind Kine, but Kine emulates etcd's Watch API.

### Concept 2: The Scheduler — Constraint Satisfaction Under Pressure

**What it is**: The scheduler watches for unscheduled pods (pods with no `nodeName` set), evaluates all candidate nodes against the pod's constraints, scores the candidates, and binds the pod to the best node. This is a two-phase process: filter (remove infeasible nodes) then score (rank remaining nodes).

**How it applies**: Filtering checks hard constraints: does the node have enough CPU/memory? Does it match the pod's nodeSelector? Does it satisfy affinity/anti-affinity rules? Scoring applies soft preferences: spread pods across zones (topology spread), prefer nodes with the image already cached, bin-pack to minimize fragmented resources.

**The math**: For 5,000 nodes, evaluating all nodes per pod is O(5000) per scheduling decision. At 100 pods/sec, that's 500K node evaluations/sec. Kubernetes optimizes this with "percentageOfNodesToScore" — once enough feasible nodes are found (default 50% of nodes or at least 100), scoring stops. This brings scheduling latency to ~5-20ms per pod. The scheduler also uses a scheduling queue with priority: system-critical pods schedule before best-effort.

**Common misconception**: "The scheduler is a simple bin-packing algorithm." It's actually a constraint satisfaction problem with soft and hard constraints, topology-aware spreading, pod affinity/anti-affinity (which requires knowing where other pods are running), and preemption logic (evict lower-priority pods to make room for higher-priority ones). The scheduler is the single most complex component in K8s.

### Concept 3: Controller Reconciliation — Level-Triggered vs Edge-Triggered

**What it is**: Controllers implement the reconciliation loop: observe current state, compare to desired state, take action to converge. Level-triggered means the controller doesn't care about the sequence of events that led to the current state — it only cares about the delta between desired and actual *right now*. Edge-triggered would mean reacting to each individual state change.

**How it applies**: A Deployment controller watches Deployment objects and ReplicaSets. When it sees a Deployment with `replicas: 5` but only 3 ReplicaSets pods running, it creates 2 more pod objects. It doesn't need to know *why* there are only 3 — maybe 2 crashed, maybe the user scaled down and then up. The controller just converges. The ReplicaSet controller then watches these pods and ensures the right count. This layering of controllers is the "controller of controllers" pattern.

**The math**: Each controller runs at a configurable resync period (default 10 hours in K8s). Between resyncs, it reacts to watch events. With 550K pods and a 10-hour resync, each controller processes ~55K objects/hour in background resync, plus real-time events. The work queue deduplicates events — if the same pod is updated 10 times in 1 second, the controller only processes it once.

**Common misconception**: "Controllers are event handlers." They're NOT. An event handler processes each event in order. A controller reconciles desired vs actual state regardless of what events occurred. If a controller misses an event (due to a restart), it doesn't matter — the next reconciliation loop catches the discrepancy. This is why K8s is self-healing.

### Concept 4: Networking — Pod-to-Pod, Service Discovery, and kube-proxy

**What it is**: Kubernetes networking has three layers: (1) Pod networking — every pod gets a unique IP via CNI plugin, all pods can reach all other pods without NAT. (2) Service networking — a virtual IP (ClusterIP) load-balanced across pod endpoints, implemented by kube-proxy using iptables/IPVS rules on every node. (3) Ingress — L7 routing from external traffic to services.

**How it applies**: When a pod calls a service (e.g., `http://payment-svc:8080`), DNS resolves `payment-svc` to the ClusterIP (e.g., 10.96.5.12). The packet hits iptables rules on the sending node, which DNAT the packet to a random healthy pod endpoint IP. With IPVS mode, kube-proxy programs IPVS load balancing rules instead of iptables chains, which scales better — O(1) for IPVS vs O(N) for iptables chain traversal per service.

**The math**: With 5,000 services and 100 endpoints each = 500K iptables rules. iptables performance degrades linearly — at 20K+ rules, rule insertion takes seconds. IPVS uses a hash table and handles millions of rules with O(1) lookup. This is why large clusters must use IPVS mode.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Pod Scheduling End-to-End

**Interviewer**: "Walk me through what happens from `kubectl apply -f deployment.yaml` to containers running on nodes."

**You**: The kubectl client serializes the Deployment YAML, sends a POST to the API server at `/apis/apps/v1/namespaces/default/deployments`. The API server authenticates (OIDC/certs), authorizes (RBAC), runs admission controllers (mutating webhooks inject sidecars, validating webhooks check policy), then persists to etcd. The Deployment controller, watching the Deployment resource via the API server, sees the new object. It creates a ReplicaSet object specifying the pod template and replica count. The ReplicaSet controller, watching ReplicaSets, creates N Pod objects with `nodeName` empty. The scheduler, watching for unscheduled pods, picks up each pod, runs the filter/score cycle, and writes `nodeName: node-42` to the pod spec via the API server. The kubelet on node-42, watching for pods assigned to it, sees the new pod, pulls the container image via CRI, creates the sandbox (network namespace, cgroup), starts the containers, and reports pod status back to the API server.

**Interviewer**: "What happens if the scheduler can't find a suitable node? All nodes are full."

**You**: The pod stays in Pending state in the scheduling queue. If the pod has a PriorityClass, the scheduler evaluates preemption: can we evict lower-priority pods to make room? It finds the cheapest set of victims (fewest evictions, lowest total priority) that would free enough resources. It sets a `nominatedNode` on the pending pod and sends delete requests for the victim pods with a graceful termination period (default 30 seconds). Once victims terminate, the scheduler retries and the pending pod gets scheduled. If preemption isn't possible (all pods are equal or higher priority), the pod stays Pending and the Cluster Autoscaler (if enabled) provisions a new node.

**Interviewer**: "How does the Cluster Autoscaler decide what type of node to add? In a heterogeneous cloud environment."

**You**: The Cluster Autoscaler maintains a list of node group templates (e.g., AWS ASGs with different instance types). For each pending pod, it simulates scheduling against each template: "would this pod fit on a m5.xlarge? An r5.2xlarge?" It selects the cheapest instance type that can run the pending pod AND any other pending pods in the queue (bin-packing across pending pods). It also considers balancing across AZs for HA. The scale-up decision takes ~30-60 seconds, then cloud provider latency to provision the node adds 1-3 minutes. Total time from pending pod to running: 2-5 minutes — which is why you want some buffer capacity for latency-sensitive workloads. In EKS, this is why Karpenter was built — it bypasses ASGs and calls EC2 directly with flexible instance selection, reducing provisioning time.

**Interviewer**: "Talk me through the failure mode where the scheduler makes a decision based on stale state. How does K8s handle scheduling races?"

**You**: This is the "optimistic concurrency" problem. The scheduler reads node state at time T, makes a decision, and binds at time T+delta. Between T and T+delta, another scheduler instance (if running multiple) might bind a different pod to the same node, or the node might lose capacity. K8s handles this in two ways: (1) The bind operation writes to etcd via the API server with a resource version check — if the pod was already bound, the write fails and the scheduler retries. (2) The kubelet performs admission checks locally before actually starting containers — if the node is overcommitted, the kubelet rejects the pod and it goes back to Pending. This is why K8s scheduling is eventually correct but not transactionally atomic — and it works fine because the reconciliation loop catches any discrepancies.

### Deep Dive Path 2: Failure Detection and Self-Healing

**Interviewer**: "A node stops responding. Walk me through how the system detects and recovers."

**You**: The kubelet sends heartbeats (NodeLease objects) to the API server every 10 seconds. The node lifecycle controller watches these leases. If no heartbeat is received for 40 seconds (default `node-monitor-grace-period`), the controller sets the node's condition to `NotReady`. After 5 minutes (`pod-eviction-timeout`), the node controller starts evicting pods from the dead node — it marks pods for deletion, and the ReplicaSet/Deployment controllers create replacement pods scheduled to healthy nodes. The 5-minute grace period prevents flapping during transient network partitions. For stateful workloads with persistent volumes, the system waits even longer — you don't want to force-detach a volume from a node that might still be running (risking data corruption from dual-writes).

**Interviewer**: "What if the control plane itself fails? What keeps running?"

**You**: This is critical to understand: the data plane survives control plane failure. If the API server goes down, existing pods continue running — kubelets have a local cache of their pod specs. kube-proxy rules are already programmed in iptables/IPVS. DNS caches are populated. The cluster continues serving traffic. What doesn't work: no new pods can be scheduled, no scaling, no deployments, no healing (dead pods won't be replaced). This is why the control plane runs as HA: 3-5 API server replicas behind a load balancer, 3-5 etcd nodes (Raft tolerates N/2-1 failures). In EKS, AWS manages the control plane across 3 AZs — customers never worry about etcd operations.

**Interviewer**: "How do you handle split brain? Two partitions of etcd both think they're the leader."

**You**: Raft consensus prevents split brain by design. A leader requires votes from a majority (N/2+1 nodes). With 5 etcd nodes split into partitions of 3 and 2, only the partition with 3 nodes can elect a leader — the partition with 2 nodes cannot form a quorum and becomes read-only (actually, it rejects both reads and writes in etcd's strict mode). The API servers connected to the minority partition will get errors and the load balancer health checks will route traffic to API servers connected to the majority partition. When the partition heals, the minority nodes sync from the leader's log. No conflicting writes are ever committed because they require majority acknowledgment.

**Interviewer**: "At 5,000 nodes, what if etcd becomes the bottleneck?"

**You**: Several strategies: (1) Separate etcd clusters for events vs everything else — events are high-volume, low-value data. K8s supports `--etcd-servers-overrides` to route event objects to a separate etcd cluster. (2) API server caching — the API server maintains an in-memory watch cache. Most read operations (GETs, LISTs) are served from cache without hitting etcd. Only writes and consistent reads hit etcd. (3) API Priority and Fairness (APF) — rate limit API requests by client type. System controllers get higher priority than user `kubectl` commands. (4) If truly at the limit, shard by namespace using virtual clusters (like vCluster) or federate across multiple clusters.

### Deep Dive Path 3: Networking Deep Dive — Service Mesh and DNS

**Interviewer**: "A Pod A calls Service B. Trace the packet from A to B including DNS resolution and load balancing."

**You**: Pod A's application calls `http://service-b.namespace.svc.cluster.local:8080`. The container's `/etc/resolv.conf` (injected by kubelet) has `nameserver 10.96.0.10` (CoreDNS ClusterIP) and `search namespace.svc.cluster.local svc.cluster.local cluster.local`. So it first tries `service-b.namespace.svc.cluster.local`. CoreDNS resolves this to the ClusterIP, say `10.96.5.20`. Pod A's TCP stack sends a SYN to `10.96.5.20:8080`. The packet hits iptables/IPVS rules on node A. With IPVS, the rule does DNAT: destination changes from `10.96.5.20` to a real pod IP, say `10.244.3.15` (random selection from healthy endpoints). The packet is routed via the CNI network — if using AWS VPC CNI, `10.244.3.15` is a real ENI secondary IP, so the packet routes through the VPC directly. If using overlay (Calico, Flannel), it's encapsulated (VXLAN or IP-in-IP) at node A and decapsulated at node B where pod B lives.

**Interviewer**: "What happens to in-flight connections when pod B is replaced during a rolling update?"

**You**: This is one of the most common production issues. When pod B is terminating: (1) The pod is removed from the endpoints list — kube-proxy updates iptables/IPVS rules on all nodes, but this propagation takes seconds. (2) The pod receives SIGTERM and starts graceful shutdown. (3) During the propagation window, new connections might still be routed to the terminating pod. The solution is the `preStop` hook: the pod runs a sleep (e.g., 5 seconds) in the preStop hook before the application receives SIGTERM. This gives kube-proxy time to update rules on all nodes. Additionally, the application should stop accepting new connections but finish processing in-flight requests (drain). The `terminationGracePeriodSeconds` (default 30s) defines how long K8s waits before sending SIGKILL.

**Interviewer**: "How does a service mesh like Istio change this picture?"

**You**: With Istio, a sidecar proxy (Envoy) is injected into every pod via a mutating admission webhook. Now the traffic flow changes: Pod A's application calls `service-b:8080`, but iptables rules inside the pod redirect outbound traffic to the local Envoy proxy (port 15001). Envoy resolves `service-b` via the Istio control plane (Istiod), which pushes endpoint lists and routing rules via xDS API. Envoy load-balances to pod B's Envoy sidecar, which forwards to pod B's application. The benefit: mTLS between all pods (zero-trust networking), traffic shifting (canary deployments at L7), circuit breaking, retries, and observability — all without application code changes. The cost: ~10ms p99 latency overhead per hop, ~50 MB memory per sidecar, and significant operational complexity. This is why ambient mesh (sidecar-less) is gaining traction.

---

## How Real Companies Built This

- **Google Borg/Omega**: Kubernetes' predecessors. Borg uses a single-leader centralized scheduler. Omega introduced shared-state optimistic scheduling. [Borg Paper — EuroSys 2015](https://research.google/pubs/pub43438/)
- **Kubernetes**: Open-source, CNCF project. etcd for state, level-triggered reconciliation, extensible via CRDs. [Kubernetes Design Docs](https://github.com/kubernetes/design-proposals-archive)
- **Amazon EKS**: Managed K8s. Control plane runs across 3 AZs, separate etcd per cluster. Uses ENI-based VPC networking. [EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/)
- **HashiCorp Nomad**: Alternative orchestrator using Raft for consensus but with a simpler scheduling model (no CRDs, no controllers). [Nomad Architecture](https://developer.hashicorp.com/nomad/docs/concepts/architecture)
- **Meta Twine**: Custom container orchestrator handling millions of containers. Uses a sharded scheduler for scale beyond what single-scheduler Kubernetes handles. [Twine — OSDI 2020](https://www.usenix.org/conference/osdi20/presentation/tang)

---

## The Complete Reference Design

### API Design

```
# Core resource APIs (declarative)
POST   /api/v1/namespaces/{ns}/pods                 # Create pod
GET    /api/v1/namespaces/{ns}/pods/{name}           # Get pod
GET    /api/v1/namespaces/{ns}/pods?watch=true&resourceVersion=X  # Watch
PUT    /api/v1/namespaces/{ns}/pods/{name}/status    # Update status (kubelet)
DELETE /api/v1/namespaces/{ns}/pods/{name}           # Delete pod
PATCH  /api/v1/namespaces/{ns}/pods/{name}           # Patch (strategic merge)

# Scheduling sub-resource
POST   /api/v1/namespaces/{ns}/pods/{name}/binding   # Bind pod to node

# Node lifecycle
PUT    /apis/coordination.k8s.io/v1/namespaces/kube-node-lease/leases/{node}
# ^ kubelet heartbeat via Lease object
```

### Database Schema (etcd Key Layout)

```
# etcd key structure (hierarchical)
/registry/pods/{namespace}/{name}          -> Pod JSON
/registry/services/{namespace}/{name}      -> Service JSON
/registry/deployments/{namespace}/{name}   -> Deployment JSON
/registry/nodes/{name}                     -> Node JSON
/registry/leases/kube-node-lease/{name}    -> Lease JSON (heartbeat)
/registry/events/{namespace}/{name}        -> Event JSON

# Each value includes:
# - metadata.resourceVersion (etcd revision for optimistic concurrency)
# - metadata.generation (spec change counter)
# - status (reported by controllers/kubelet)
```

### Key Algorithms — Scheduler Scoring

```go
// Simplified scheduler filter + score pipeline
func (s *Scheduler) Schedule(pod *v1.Pod, nodes []*v1.Node) (string, error) {
    // Phase 1: Filter — remove infeasible nodes
    feasible := make([]*v1.Node, 0)
    for _, node := range nodes {
        if s.nodeHasSufficientResources(node, pod) &&
           s.nodeMatchesAffinity(node, pod) &&
           s.nodeTolerateTaints(node, pod) &&
           s.nodeMatchesTopologyConstraints(node, pod) {
            feasible = append(feasible, node)
        }
    }
    if len(feasible) == 0 {
        return "", fmt.Errorf("no feasible nodes, attempting preemption")
    }

    // Phase 2: Score — rank feasible nodes (0-100 per plugin)
    scores := make(map[string]int)
    for _, node := range feasible {
        score := 0
        score += s.leastRequestedScore(node, pod) * 1   // weight=1
        score += s.balancedAllocationScore(node, pod) * 1
        score += s.imageLocalityScore(node, pod) * 1
        score += s.topologySpreadScore(node, pod) * 2    // weight=2
        scores[node.Name] = score
    }

    // Phase 3: Select highest score (random tie-break)
    best := selectHighestScore(scores)
    return best, nil
}

func (s *Scheduler) leastRequestedScore(node *v1.Node, pod *v1.Pod) int {
    // Prefer nodes with more available resources (spread workload)
    cpuFree := node.Status.Allocatable.Cpu - node.Status.Allocated.Cpu
    memFree := node.Status.Allocatable.Mem - node.Status.Allocated.Mem
    cpuScore := int(float64(cpuFree) / float64(node.Status.Allocatable.Cpu) * 100)
    memScore := int(float64(memFree) / float64(node.Status.Allocatable.Mem) * 100)
    return (cpuScore + memScore) / 2
}
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| etcd cluster | 3-5 nodes, NVMe SSDs, 4 CPU 16 GB each | 5 x m5.xlarge |
| API servers | 50K QPS / 20K per instance = 3 | 3 x c5.2xlarge (HA behind LB) |
| Scheduler | 100 pods/sec, single leader + standby | 2 x m5.large |
| Controller manager | Single leader + standby | 2 x m5.large |
| etcd storage | 4 GB state + WAL + snapshots | 100 GB NVMe per etcd node |
| Network | Pod CIDR: /16 = 65K IPs per node group | Multiple /16s for 550K pods |
| Watch bandwidth | 5K nodes x 10KB/sec avg = 50 MB/s | 400 Mbps to API servers |

---

## Senior vs Staff vs Principal

| Aspect | Senior (E5/L5) | Staff (E6/L6) | Principal (L66+) |
|--------|----------------|----------------|-------------------|
| **Architecture** | Clean control/data plane separation, explains reconciliation loop | Designs the scheduler with affinity/anti-affinity, explains etcd Watch semantics | Designs multi-cluster federation, reasons about scheduler sharding for 50K+ nodes |
| **Failure handling** | Knows pods restart on node failure | Explains split-brain prevention via Raft quorum, pod disruption budgets | Designs graceful control plane upgrades, etcd backup/restore, disaster recovery |
| **Networking** | Understands ClusterIP and kube-proxy basics | Explains iptables vs IPVS trade-offs at scale, CNI plugin architecture | Designs network policy enforcement, service mesh integration, multi-cluster networking |
| **Operations** | Can describe kubectl workflow | Designs admission webhooks for policy, RBAC model for multi-tenancy | Designs platform API abstractions, custom controllers for org-specific workflows |

---

## Red Flags & Common Mistakes

1. **Treating it as a monolith** — Not separating control plane from data plane. The whole point is that the data plane survives control plane failure.
2. **Ignoring etcd** — Spending 0 time on the state store. etcd's Raft consensus and Watch protocol are the foundation of everything.
3. **"The scheduler just picks a random node"** — Missing filter/score pipeline, resource constraints, affinity, topology spreading.
4. **No failure recovery story** — If you can't explain what happens when a node dies, you haven't designed an orchestrator — you've designed a deployment tool.
5. **Edge-triggered thinking** — Describing the system as event handlers instead of reconciliation loops. This is the most fundamental K8s design principle.
6. **Ignoring networking** — In a real interview, the interviewer will ask how pod-to-pod communication works. "It just works" isn't an answer.
7. **Not knowing the difference between control plane and data plane components** — Mixing up what runs where and why.
