# Design a Cluster Scheduler

> **Companies**: Google (Borg/Omega/GKE), Microsoft (AKS), Amazon (EKS), ByteDance (Volcano), AI infra companies building GPU scheduling
> **Level**: Staff / Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a scheduler that efficiently assigns workloads to nodes while respecting constraints (resources, affinity, topology, preemption)? Can you reason about scheduling throughput vs quality trade-offs, gang scheduling, and the NP-hard nature of bin packing?
> **Your EKS advantage**: You understand the K8s Scheduling Framework extension points, how the default scheduler makes decisions, and the real-world performance characteristics at scale. You know why `percentageOfNodesToScore` exists, how preemption works, and the challenges of scheduling GPU workloads.

---

## The First 5 Minutes — Technical Scoping

- "What workload types? Web services (long-running, stable), batch jobs (short-lived, bursty), ML training (gang scheduling, GPU affinity), or a mix? Each has fundamentally different scheduling requirements."
- "What's the cluster scale? At 100 nodes, brute-force scoring works. At 5,000 nodes, you need to limit the scoring percentage to maintain throughput. At 50,000 nodes (Borg-scale), you need a fundamentally different architecture."
- "Do we need preemption? If high-priority Pods cannot schedule, should the scheduler evict lower-priority Pods? Preemption adds significant complexity — the scheduler must simulate the effect of evictions before committing."
- "Is this a single scheduler or multi-scheduler? K8s supports multiple schedulers (each Pod specifies `schedulerName`). But multiple schedulers can conflict — two schedulers might assign Pods to the same node, exceeding its capacity."
- "What scheduling quality do we need? Optimal bin packing (minimize cost) or fast placement (minimize scheduling latency)? These are in tension — optimal packing is NP-hard, fast placement uses heuristics."
- "Do we need gang scheduling? For distributed ML training, all pods in a training job must be scheduled together or not at all. If 7 of 8 GPUs are available, we should not schedule 7 and leave 1 pending — that wastes 7 GPUs."
- "Topology-aware scheduling? For GPU workloads, locality matters — GPUs on the same NVLink fabric have 10x the bandwidth of GPUs across PCIe. The scheduler needs to understand hardware topology."

### Working Assumptions
| Parameter | Value |
|-----------|-------|
| Cluster size | 1,000-5,000 nodes |
| Pods to schedule | ~100 pods/sec at peak (deployment rollouts) |
| Scheduling latency target | <100ms p99 for single-pod scheduling |
| Scheduler throughput | 100 pods/sec (standard), 50 pods/sec at 5K nodes |
| Node scoring percentage | 50% of nodes scored (default for >100 nodes) |
| Preemption | Enabled for Priority > 1000000 |
| Gang scheduling | Required for ML training jobs |
| Resource dimensions | CPU, memory, ephemeral-storage, nvidia.com/gpu |

---

## High-Level Architecture

```
                    ┌────────────────────────────────────┐
                    │        Scheduling Queue             │
                    │                                     │
                    │  ┌─────────────────────────────┐   │
                    │  │ ActiveQ (heap by priority)   │   │
                    │  │ - Unscheduled Pods sorted    │   │
                    │  │   by priority, then timestamp│   │
                    │  └──────────────┬──────────────┘   │
                    │                 │                   │
                    │  ┌──────────────┴──────────────┐   │
                    │  │ BackoffQ (exponential backoff)│  │
                    │  │ - Pods that failed scheduling │  │
                    │  │   (no node fits)              │  │
                    │  └──────────────┬──────────────┘   │
                    │                 │                   │
                    │  ┌──────────────┴──────────────┐   │
                    │  │ UnschedulableQ               │   │
                    │  │ - Pods waiting for cluster   │   │
                    │  │   state changes              │   │
                    │  └─────────────────────────────┘   │
                    └────────────────┬───────────────────┘
                                     │
                    ┌────────────────┴───────────────────┐
                    │       Scheduling Cycle              │
                    │                                     │
                    │  1. PreFilter plugins               │
                    │     (compute Pod requirements)      │
                    │              │                      │
                    │  2. Filter plugins                  │
                    │     (eliminate infeasible nodes)    │
                    │     - NodeResourcesFit              │
                    │     - NodeAffinity                  │
                    │     - TaintToleration               │
                    │     - TopologySpreadConstraint      │
                    │              │                      │
                    │  3. PostFilter plugins              │
                    │     (preemption if no node fits)    │
                    │              │                      │
                    │  4. PreScore plugins                │
                    │     (prepare scoring data)          │
                    │              │                      │
                    │  5. Score plugins                   │
                    │     (rank feasible nodes)           │
                    │     - NodeResourcesBalancedAlloc    │
                    │     - InterPodAffinity              │
                    │     - NodeAffinity                  │
                    │     - PodTopologySpread             │
                    │              │                      │
                    │  6. NormalizeScore                  │
                    │     (normalize to 0-100 range)      │
                    │              │                      │
                    │  7. Reserve plugins                 │
                    │     (optimistically claim resources)│
                    │              │                      │
                    │  8. Permit plugins                  │
                    │     (allow/deny/wait — gang sched.) │
                    │              │                      │
                    └────────────────┬───────────────────┘
                                     │
                    ┌────────────────┴───────────────────┐
                    │       Binding Cycle (async)         │
                    │                                     │
                    │  9. PreBind plugins                 │
                    │     (provision volumes, etc.)       │
                    │              │                      │
                    │  10. Bind plugin                    │
                    │      (write spec.nodeName to API    │
                    │       server)                       │
                    │              │                      │
                    │  11. PostBind plugins               │
                    │      (cleanup, metrics)             │
                    └────────────────────────────────────┘
```

**Why this architecture**: The K8s Scheduling Framework (KEP-624) was designed to make the scheduler extensible without forking. Each extension point has a well-defined interface. Plugins at different extension points collaborate to implement complex scheduling policies. The separation of scheduling cycle (synchronous, determines node) and binding cycle (asynchronous, writes to API server) allows the scheduler to start evaluating the next Pod while the current one is being bound.

---

## Core Concepts Deep Dive

### Concept 1: Filter and Score — The Two-Phase Decision

**Filtering (predicates)**: Eliminate nodes that cannot run the Pod. This is a hard constraint — either the node passes or it does not.

Key filter plugins:
- **NodeResourcesFit**: Does the node have enough CPU, memory, ephemeral-storage? Compares `allocatable - sum(existing pod requests)` against the new Pod's requests.
- **NodeAffinity**: Does the node match the Pod's `nodeAffinity` rules?
- **TaintToleration**: Does the Pod tolerate the node's taints?
- **PodTopologySpread**: Would scheduling on this node violate `topologySpreadConstraints`?
- **VolumeRestrictions**: Can the node's zone provide the required PVs?

**Scoring (priorities)**: Rank the feasible nodes. Each plugin returns a score of 0-100, weighted by its configured weight. The node with the highest total score wins.

Key score plugins:
- **NodeResourcesBalancedAllocation**: Prefer nodes where CPU and memory utilization are balanced. Avoids nodes that are 90% CPU but 10% memory.
- **NodeResourcesFit** (MostAllocated or LeastAllocated): MostAllocated for bin packing (cost optimization), LeastAllocated for spreading (availability).
- **InterPodAffinity**: Score based on pod affinity/anti-affinity preferences.
- **PodTopologySpread**: Score to achieve even distribution across topology domains (zones, nodes).

**percentageOfNodesToScore**: At 5,000 nodes, scoring all nodes for every Pod is too slow. The scheduler scores a percentage of nodes (default 50% for >100 nodes, configurable). It finds enough feasible nodes to score, scores them, and picks the best. This means scheduling decisions are not globally optimal — they are locally optimal across the scored subset.

```go
// The scoring loop (simplified from scheduler/framework/runtime/framework.go)
func (f *frameworkImpl) RunScorePlugins(ctx context.Context, state *framework.CycleState,
    pod *v1.Pod, nodes []*v1.Node) (framework.NodeScoreList, *framework.Status) {

    nodeScores := make(framework.NodeScoreList, len(nodes))
    for _, plugin := range f.scorePlugins {
        weight := f.pluginWeight(plugin.Name())
        for i, node := range nodes {
            score, status := plugin.Score(ctx, state, pod, node.Name)
            nodeScores[i].Score += score * int64(weight)
        }
    }
    return nodeScores, nil
}
```

### Concept 2: Preemption

When no node has enough resources for a high-priority Pod, the scheduler attempts preemption: evict lower-priority Pods to make room.

**The preemption algorithm** (PostFilter phase):
1. For each node, simulate evicting lower-priority Pods (sorted by priority, lowest first).
2. After each simulated eviction, re-run Filter plugins to check if the high-priority Pod now fits.
3. Among nodes where eviction works, pick the one with the least total evictions (minimize disruption).
4. Create a "nomination" — the scheduler does NOT evict Pods immediately. It sets `nominatedNodeName` on the preempting Pod and triggers eviction of victim Pods via the API server.
5. The kubelet handles the actual eviction (sends SIGTERM, waits gracePeriod, sends SIGKILL).
6. Once victims are gone, the scheduler binds the preempting Pod to the node.

**Why preemption is not immediate**: Evicted Pods need time to clean up (graceful shutdown). The scheduler cannot hold the scheduling thread waiting for this. Instead, it nominate and move on. The next scheduling cycle will see the freed resources and complete the binding.

**PriorityClasses**:
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical-workloads
value: 1000000
preemptionPolicy: PreemptLowerPriority
globalDefault: false
description: "For production services that must always run"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: batch-jobs
value: 100
preemptionPolicy: Never  # Batch jobs should not preempt anything
globalDefault: false
```

### Concept 3: Gang Scheduling and the Coscheduling Plugin

For distributed ML training, you need all workers scheduled together. If a training job needs 8 GPUs across 8 Pods, scheduling 7 and leaving 1 pending wastes 7 GPUs.

**The Coscheduling plugin** (part of scheduler-plugins SIG):
- Uses the **Permit** extension point. When a Pod in a PodGroup arrives, the permit plugin holds it in "waiting" state.
- Once all Pods in the PodGroup are in the waiting state (all have passed filter/score), the plugin releases all of them simultaneously.
- If not all Pods can be scheduled within a timeout, all are rejected and sent back to the queue.

```yaml
apiVersion: scheduling.sigs.k8s.io/v1alpha1
kind: PodGroup
metadata:
  name: training-job-1
spec:
  minMember: 8
  scheduleTimeoutSeconds: 300  # 5 min to schedule all 8 or fail
```

**Volcano scheduler**: An alternative for batch/HPC workloads. Volcano provides queue-based scheduling (fair-share queues, priority queues), gang scheduling, and resource reservation. It is a separate scheduler binary that runs alongside or instead of the default K8s scheduler.

**The challenge with gang scheduling**: Deadlock. If two jobs each need 8 GPUs and only 12 are available, neither can be fully satisfied. Without priority or fairness, both jobs wait forever. Volcano's queue system solves this with priority-based preemption at the job level.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Optimize scheduling throughput"

**Interviewer**: "Our scheduler is only doing 30 pods/sec. We need 200 pods/sec for batch workload bursts. How do you improve throughput?"

**You**: "Several approaches:

1. **Reduce percentageOfNodesToScore**: The default is calculated based on cluster size. For a 5K-node cluster, it scores ~50% of nodes. Reducing to 10-20% dramatically improves throughput at the cost of scheduling quality. For batch jobs that do not care about optimal placement, this is a good trade-off.

2. **Parallelize the binding cycle**: The scheduling cycle (filter/score) is serial — the scheduler processes one Pod at a time because the decision for Pod N depends on the assumed state after Pod N-1 is scheduled. But the binding cycle (writing to API server) is asynchronous and can be parallelized. The default scheduler already does this with a configurable binding goroutine count.

3. **Use scheduling profiles**: Run multiple scheduling profiles in one scheduler process. Different profiles can have different plugin configurations. Batch Pods use a lightweight profile (fewer scoring plugins), while service Pods use the full profile.

4. **Pod affinity optimization**: Pod affinity/anti-affinity is the most expensive scheduling feature. For each Pod, it must evaluate all existing Pods in the cluster. At 50K Pods, this is O(N) per scheduling decision. If your batch jobs do not need pod affinity, do not add it. The scheduler internally uses precomputed indices for pod affinity, but it is still the dominant cost.

5. **Scheduler queue optimization**: Group identical Pods (same requirements, same priority) and make a single scheduling decision for the group. The scheduler can then batch-bind all of them to the same or similar nodes. This is what 'scheduling gates' enable — you can gate a batch of Pods, compute their scheduling together, and release them.

6. **Run a separate batch scheduler**: Use a dedicated Volcano or custom scheduler for batch workloads with `spec.schedulerName: volcano`. This avoids contention with the default scheduler for service workloads."

### Deep Dive Path 2: "Design topology-aware GPU scheduling"

**Interviewer**: "We have nodes with 8 GPUs. How do you schedule ML training jobs that need 4 GPUs with NVLink affinity?"

**You**: "This requires topology-aware scheduling. The NVIDIA device plugin exposes GPUs to K8s as extended resources (`nvidia.com/gpu`). But K8s does not natively understand GPU topology — it treats GPUs as fungible.

**Topology Manager** (kubelet feature): The kubelet's Topology Manager ensures that CPU and device allocations are NUMA-aligned. When a Pod requests 4 GPUs, the Topology Manager can ensure all 4 are from the same NUMA node (which typically means the same NVLink switch group).

```yaml
# kubelet configuration
topologyManagerPolicy: best-effort  # or 'restricted' or 'single-numa-node'
topologyManagerScope: pod           # or 'container'
```

For the scheduler level, you need a custom scheduling plugin or use Dynamic Resource Allocation (DRA — KEP-3063):

```yaml
apiVersion: resource.k8s.io/v1alpha2
kind: ResourceClaimTemplate
metadata:
  name: gpu-claim
spec:
  spec:
    resourceClassName: gpu.nvidia.com
    parametersRef:
      apiGroup: gpu.nvidia.com
      kind: GpuClaimParameters
      name: nvlink-group-4
---
apiVersion: gpu.nvidia.com/v1alpha1
kind: GpuClaimParameters
metadata:
  name: nvlink-group-4
spec:
  count: 4
  sharing:
    strategy: None  # Exclusive access
  selector:
    nvlink: same-switch  # Must be on the same NVLink fabric
```

DRA is the future of device scheduling in K8s. It replaces the device plugin model with a more expressive resource claim model that supports topology constraints, partitioning (MIG), and time-sharing."

### Deep Dive Path 3: "How does the scheduler handle node affinity at scale?"

**Interviewer**: "We have complex node affinity rules across 1000 nodes. Performance is bad. Why?"

**You**: "Node affinity in the Filter phase is O(number of affinity terms * number of node labels), which is usually fast. The expensive part is inter-pod affinity — `podAffinity` and `podAntiAffinity`.

For inter-pod affinity, the scheduler must check existing Pods on candidate nodes. Specifically:
- For `podAffinity`: Is there a Pod matching the label selector on this node (or in the same topology domain)?
- For `podAntiAffinity`: Is there NO Pod matching the label selector on this node?

This requires iterating over all Pods in the cluster (or the topology domain) for each candidate node. The scheduler builds precomputed indices (existing pod affinity terms indexed by topology key and namespace), but at 50K Pods and 5K nodes, this is still the dominant scheduling cost.

**Optimization strategies**:
1. Replace pod anti-affinity with `topologySpreadConstraints`. Topology spread achieves the same goal (distribute Pods across zones/nodes) with better performance because it uses a precomputed counter instead of evaluating all Pods.
2. Use `requiredDuringSchedulingIgnoredDuringExecution` sparingly — prefer `preferredDuringSchedulingIgnoredDuringExecution`, which is a scoring optimization, not a filter.
3. Limit the namespace scope of pod affinity rules. Without `namespaceSelector`, the scheduler checks all namespaces by default (in older versions) — use `namespaces` to limit scope.
4. Use `matchLabelKeys` (K8s 1.29+) to automatically scope pod topology spread to the current revision, avoiding spreading across old ReplicaSets during rollouts."

---

## How the Industry Built This

- **Borg (Google)**: Google's internal cluster scheduler. Priority-based preemption, quota management, and alloc sets (gang scheduling). K8s scheduler is simplified from Borg. The Omega paper (2013) proposed shared-state, optimistic scheduling — multiple schedulers share cluster state and resolve conflicts.
- **Volcano**: CNCF project for batch/HPC scheduling on K8s. Queue management, gang scheduling, fair-share policies. Used by AI companies for GPU training workloads. [volcano.sh](https://volcano.sh/)
- **Scheduler Framework (KEP-624)**: Made the K8s scheduler extensible via plugins. Replaced the hard-coded predicate/priority system with pluggable extension points. [github.com/kubernetes/enhancements/tree/master/keps/sig-scheduling/624](https://github.com/kubernetes/enhancements/tree/master/keps/sig-scheduling/624).
- **Coscheduling plugin**: scheduler-plugins SIG implementation of gang scheduling using the Permit extension point.
- **Dynamic Resource Allocation (DRA, KEP-3063)**: The next generation of device scheduling. Replaces device plugins with a richer resource claim model.

References:
- https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/
- https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/
- https://github.com/kubernetes-sigs/scheduler-plugins
- https://volcano.sh/en/docs/
- Borg paper: https://research.google/pubs/pub43438/

---

## The Complete Reference Design

### Scheduler Configuration

```yaml
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
- schedulerName: default-scheduler
  plugins:
    score:
      enabled:
      - name: NodeResourcesFit
        weight: 1
      - name: PodTopologySpread
        weight: 2
      - name: InterPodAffinity
        weight: 1
      - name: NodeAffinity
        weight: 1
  pluginConfig:
  - name: NodeResourcesFit
    args:
      scoringStrategy:
        type: MostAllocated  # Bin packing for cost optimization
        resources:
        - name: cpu
          weight: 1
        - name: memory
          weight: 1
- schedulerName: batch-scheduler
  plugins:
    score:
      enabled:
      - name: NodeResourcesFit
        weight: 1
      disabled:
      - name: InterPodAffinity  # Disable expensive scoring for batch
      - name: PodTopologySpread
```

### Performance Characteristics
| Metric | Value at 1K nodes | Value at 5K nodes |
|--------|-------------------|-------------------|
| Scheduling throughput | ~100-150 pods/sec | ~50-80 pods/sec |
| Scheduling latency p50 | ~5ms | ~20ms |
| Scheduling latency p99 | ~20ms | ~100ms |
| Preemption evaluation | ~50ms | ~200ms |
| Binding cycle (async) | ~10ms | ~20ms |
| percentageOfNodesToScore | ~50% | ~20% |
| Filter phase cost | O(nodes * filter_plugins) | O(nodes * filter_plugins) |
| Inter-pod affinity cost | O(pods * nodes) | O(pods * nodes) |
| Memory (scheduler) | ~500 MB | ~2 GB |

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Scheduler CPU | 1 core per 50 pods/sec throughput | 2-4 cores |
| Scheduler memory | ~200 bytes per Pod cache entry + node cache | 500 MB - 2 GB |
| Scheduling queue depth | Burst pods / scheduling throughput | 100-1000 pending |
| Binding goroutines | 1-2x scheduling throughput | 100-200 concurrent binds |

---

## Senior vs Staff vs Principal

| Level | What they demonstrate | Example |
|-------|----------------------|---------|
| Senior | Understands filter/score, can configure node affinity and resource requests | Explains why a Pod is Pending (insufficient resources, taint mismatch), configures topology spread |
| Staff | Understands the Scheduling Framework, can design custom plugins, knows performance trade-offs | Implements a custom scoring plugin for cost optimization, explains percentageOfNodesToScore, designs preemption policies |
| Principal | Designs scheduling systems for heterogeneous hardware (GPUs, FPGAs), architects multi-scheduler strategies, reasons about Borg/Omega-style shared state | Proposes DRA for GPU topology-aware scheduling, designs gang scheduling with deadlock prevention, compares K8s scheduling with Borg and identifies where K8s model breaks down |

---

## Red Flags and Common Mistakes

- **Using pod anti-affinity when topology spread works**: Pod anti-affinity is O(pods * nodes) expensive. Topology spread constraints achieve the same goal (distribute across zones/nodes) with a precomputed counter. Always prefer topology spread unless you need exact label matching.
- **Not understanding percentageOfNodesToScore**: Many candidates think the scheduler evaluates all nodes. It does not — it samples. This means two identical Pods might land on different nodes because the scheduler scored different subsets. This is by design for throughput.
- **Ignoring the scheduling-binding pipeline**: The scheduling cycle is serial (one Pod at a time), but binding is async. If you design a scheduler that blocks on binding, throughput drops to ~10 pods/sec instead of 100.
- **Treating GPU scheduling like CPU scheduling**: GPUs are not fungible. Topology (NVLink, NVSwitch) matters enormously for training performance. A scheduler that ignores topology can place GPUs on different NUMA nodes with 10x worse interconnect bandwidth.
- **Not considering preemption cascades**: If a high-priority Pod preempts a medium-priority Pod, that medium-priority Pod becomes pending and might preempt a low-priority Pod. This cascade can be hard to reason about. Set preemption policies carefully.
