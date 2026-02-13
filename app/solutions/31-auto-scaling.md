# Design an Auto-Scaling System

> **Companies**: Amazon (EKS/Karpenter), Google (GKE Autopilot), Microsoft (AKS/KEDA), any company running K8s at scale with variable workloads
> **Level**: Staff / Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a multi-layer auto-scaling system that handles Pod-level scaling (HPA/VPA), node-level scaling (Cluster Autoscaler/Karpenter), and custom metric-based scaling (KEDA)? Can you reason about scaling feedback loops, oscillation, and the cold-start problem?
> **Your EKS advantage**: You know Karpenter intimately — its provisioner CRDs, the consolidation algorithm, how it bypasses the node group abstraction to call EC2 Fleet API directly. You understand the interaction between HPA and Cluster Autoscaler, and why scaling loops oscillate.

---

## The First 5 Minutes — Technical Scoping

- "What dimensions are we scaling? Horizontal Pod scaling (more replicas), vertical Pod scaling (bigger containers), or infrastructure scaling (more nodes)? Most production systems need all three, and they interact in complex ways."
- "What metrics drive scaling? CPU/memory (resource-based), request rate (throughput-based), queue depth (event-based), or custom business metrics? CPU-based scaling is the simplest but often the worst for bursty workloads."
- "What's the scaling latency budget? From 'load increase detected' to 'new Pod serving traffic' — is 30 seconds acceptable or do we need sub-second? This determines whether we can tolerate node provisioning delays."
- "What workload types? Long-running web services (scale on RPS), batch jobs (scale on queue depth), ML inference (scale on GPU utilization), or event-driven (scale to/from zero)?"
- "What's the cost sensitivity? Aggressive scale-down saves money but increases the risk of capacity starvation during load spikes. Conservative scale-down wastes money but provides buffer."
- "Karpenter or Cluster Autoscaler? Karpenter provisions nodes directly (no node groups), picks optimal instance types per pod requirement, and consolidates aggressively. Cluster Autoscaler works with node groups and has slower reaction time."

### Working Assumptions
| Parameter | Value |
|-----------|-------|
| Cluster size | 200-2000 nodes (elastic) |
| Pod count | 5,000-50,000 (elastic) |
| HPA evaluation period | 15s (default) |
| HPA scale-up stabilization | 0s (scale up immediately) |
| HPA scale-down stabilization | 300s (5 minutes, avoid flapping) |
| Node provisioning time | ~60s (Karpenter) vs ~120s (Cluster Autoscaler) |
| Node scale-down after idle | 30s (Karpenter) vs 10 min (Cluster Autoscaler default) |
| Cost target | <20% overprovisioning at steady state |

---

## High-Level Architecture

```
                    ┌─────────────────────────────────────┐
                    │         Metrics Pipeline            │
                    │                                     │
                    │  Prometheus ──▶ Metrics Server ──▶  │
                    │  Custom Metrics Adapter (Prometheus  │
                    │  adapter, KEDA, Datadog metrics)    │
                    └────────┬────────────────────────────┘
                             │
              ┌──────────────┼──────────────────┐
              │              │                  │
              ▼              ▼                  ▼
    ┌──────────────┐ ┌──────────────┐  ┌──────────────┐
    │     HPA      │ │     VPA      │  │    KEDA      │
    │ (Horizontal  │ │ (Vertical    │  │ (Event-driven│
    │  Pod         │ │  Pod         │  │  autoscaling)│
    │  Autoscaler) │ │  Autoscaler) │  │              │
    │              │ │              │  │  ScaledObject│
    │ Targets:     │ │ Targets:     │  │  → SQS depth │
    │ - CPU %      │ │ - CPU req    │  │  → Kafka lag │
    │ - Memory %   │ │ - Memory req │  │  → Custom    │
    │ - Custom     │ │              │  │              │
    └──────┬───────┘ └──────┬───────┘  └──────┬───────┘
           │                │                  │
           ▼                ▼                  ▼
    ┌─────────────────────────────────────────────────┐
    │              Pod Scaling Actions                  │
    │  scale Deployment.spec.replicas (HPA/KEDA)       │
    │  update Pod resource requests/limits (VPA)       │
    └────────────────────┬────────────────────────────┘
                         │
                         │ Pods may be Pending (insufficient
                         │ node capacity)
                         ▼
    ┌─────────────────────────────────────────────────┐
    │           Node Scaling Layer                     │
    │                                                  │
    │  ┌──────────────────┐  ┌──────────────────────┐ │
    │  │ Karpenter         │  │ Cluster Autoscaler   │ │
    │  │                   │  │                      │ │
    │  │ Watches Pending   │  │ Watches Pending Pods │ │
    │  │ Pods, calls EC2   │  │ scales ASG/node group│ │
    │  │ Fleet API directly│  │ (predefined instance │ │
    │  │ picks optimal     │  │  types)              │ │
    │  │ instance type     │  │                      │ │
    │  │                   │  │ Slower (~2-3 min)    │ │
    │  │ Faster (~60s)     │  │                      │ │
    │  └──────────────────┘  └──────────────────────┘ │
    └─────────────────────────────────────────────────┘
```

**Why this architecture**: Auto-scaling in K8s is a multi-layer system because pods and nodes scale independently. HPA/KEDA handle the "how many Pod replicas" question. The node scaler handles the "do we have enough infrastructure to run those Pods" question. These layers interact — HPA scales up pods, some become Pending because there is no capacity, the node scaler sees Pending pods and provisions nodes. This indirection is intentional: application teams set scaling policies (HPA), infrastructure teams set capacity policies (Karpenter NodePool). The separation of concerns is powerful but the interaction creates latency and potential feedback loops.

---

## Core Concepts Deep Dive

### Concept 1: HPA Algorithm and Oscillation

The Horizontal Pod Autoscaler follows a simple algorithm:

```
desiredReplicas = ceil(currentReplicas * (currentMetricValue / desiredMetricValue))
```

For example: 10 replicas at 80% CPU, target is 50% CPU:
`desiredReplicas = ceil(10 * (80/50)) = ceil(16) = 16`

**Why this oscillates**: The HPA evaluates every 15 seconds. After scaling up to 16 replicas, CPU drops to 30% (because the new pods share the load). Next evaluation: `ceil(16 * (30/50)) = ceil(9.6) = 10`. We scale back down. CPU goes back up. We scale up again. This oscillation is the most common HPA problem.

**Solutions**:
1. **Scale-down stabilization** (`behavior.scaleDown.stabilizationWindowSeconds`): Default 300s. The HPA records desired replicas every 15 seconds, and picks the highest value from the last 5 minutes. This prevents rapid scale-down.
2. **Scale-down rate limiting** (`behavior.scaleDown.policies`): Limit scale-down to X% or Y pods per period. For example, "scale down by at most 10% every 60 seconds."
3. **Scale-up rate limiting**: Less common but useful for preventing expensive scale spikes from a single metric blip.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # Target 60%, not 80% — leave headroom
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: 1000  # Scale when avg RPS per pod exceeds 1000
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
      - type: Percent
        value: 100           # Double capacity in one step
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 min cooldown
      policies:
      - type: Percent
        value: 10            # Max 10% reduction per minute
        periodSeconds: 60
```

### Concept 2: Karpenter vs Cluster Autoscaler

**Cluster Autoscaler**:
- Works with node groups (ASGs on AWS). Each node group has a fixed instance type and size range.
- When Pods are Pending, it simulates scheduling against each node group and picks the cheapest one that fits.
- Scale-down: scans for underutilized nodes (default <50% CPU requested), cordons, drains, and terminates.
- **Limitations**: Fixed instance types per group means you need many node groups to cover different workload shapes (CPU-heavy, memory-heavy, GPU). Scale-up latency is ~2-3 minutes (ASG launch time). Scale-down has a 10-minute default cooldown.

**Karpenter**:
- No node groups. Karpenter calls the EC2 Fleet API directly, requesting the optimal instance type from a set of allowed types.
- When Pods are Pending, Karpenter groups them by scheduling constraints (nodeSelector, affinity, topology), picks the cheapest instance type that satisfies all constraints, and launches it.
- **Consolidation**: Karpenter continuously evaluates whether nodes can be consolidated (replaced with fewer or cheaper nodes). If two m5.xlarge nodes are running at 25% utilization each, Karpenter can replace them with one m5.xlarge.
- **Disruption budgets**: Control how aggressively Karpenter consolidates. `spec.disruption.consolidationPolicy: WhenUnderutilized` enables automatic consolidation. `consolidateAfter: 30s` sets how quickly.
- Scale-up latency: ~60 seconds (direct EC2 launch, no ASG delay).

```yaml
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
      - key: kubernetes.io/arch
        operator: In
        values: ["amd64"]
      - key: karpenter.sh/capacity-type
        operator: In
        values: ["spot", "on-demand"]  # Prefer spot, fallback to on-demand
      - key: karpenter.k8s.aws/instance-category
        operator: In
        values: ["c", "m", "r"]        # Compute, general, memory-optimized
      - key: karpenter.k8s.aws/instance-generation
        operator: Gt
        values: ["4"]                   # 5th gen or newer
      nodeClassRef:
        name: default
  disruption:
    consolidationPolicy: WhenUnderutilized
    consolidateAfter: 30s
    expireAfter: 720h  # Replace nodes every 30 days for patching
  limits:
    cpu: "1000"        # Max 1000 vCPUs in this pool
    memory: 4000Gi
---
apiVersion: karpenter.k8s.aws/v1beta1
kind: EC2NodeClass
metadata:
  name: default
spec:
  amiFamily: AL2
  subnetSelectorTerms:
  - tags:
      karpenter.sh/discovery: my-cluster
  securityGroupSelectorTerms:
  - tags:
      karpenter.sh/discovery: my-cluster
  blockDeviceMappings:
  - deviceName: /dev/xvda
    ebs:
      volumeSize: 100Gi
      volumeType: gp3
      iops: 3000
      throughput: 125
```

### Concept 3: Event-Driven Autoscaling with KEDA

HPA works well for request-driven workloads but poorly for event-driven workloads (queue consumers, stream processors). KEDA fills this gap.

**How KEDA works**:
1. You define a `ScaledObject` that references a Deployment and a scaler (SQS queue depth, Kafka consumer lag, etc.).
2. KEDA polls the external metric source and computes desired replicas.
3. KEDA creates an HPA object behind the scenes with an external metric.
4. Critically: KEDA can scale to zero. Standard HPA has `minReplicas >= 1`. KEDA manages the 0-to-1 transition itself (by scaling the Deployment directly), then hands off to HPA for 1-to-N.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: queue-processor
spec:
  scaleTargetRef:
    name: queue-processor
  minReplicaCount: 0     # Scale to zero when queue is empty
  maxReplicaCount: 100
  cooldownPeriod: 300
  pollingInterval: 15
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.us-west-2.amazonaws.com/123456789/my-queue
      queueLength: "5"   # Target 5 messages per replica
      awsRegion: us-west-2
    authenticationRef:
      name: aws-credentials
```

**The scale-to-zero challenge**: When scaled to zero, there are no pods to process messages. When a new message arrives, KEDA must detect it, scale to 1, wait for the Pod to start (~5-30 seconds), and then the Pod starts processing. This cold-start latency is acceptable for queue consumers (messages wait in the queue) but not for synchronous request handling.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "The HPA-Karpenter interaction"

**Interviewer**: "Walk me through what happens when traffic spikes 10x."

**You**: "Let me trace through the full scaling cascade.

**T=0**: Traffic increases 10x. Pod CPU utilization jumps from 30% to 300% (effectively, requests are queuing).

**T=15s**: HPA evaluates. Current: 10 replicas at 300% CPU, target 60%. `desiredReplicas = ceil(10 * (300/60)) = 50`. HPA patches the Deployment to 50 replicas.

**T=16s**: The Deployment controller creates 40 new Pod objects. These Pods are `Pending` because the cluster does not have enough capacity for 40 new Pods.

**T=17s**: Karpenter detects 40 Pending Pods. It groups them by scheduling constraints, selects optimal instance types (maybe 5x m5.2xlarge to fit 8 Pods each), and calls the EC2 Fleet API.

**T=60-90s**: EC2 instances launch, bootstrap script runs, kubelet registers the nodes as `Ready`.

**T=90-120s**: The scheduler binds Pending Pods to the new nodes. kubelet pulls images (cached on AMI or pulled from ECR), starts containers. Pods become `Ready`.

**T=120-150s**: From traffic spike to all 50 Pods serving: ~2-2.5 minutes.

The bottleneck is node provisioning. To reduce this:
1. **Karpenter's launch template prewarming**: Use EC2 warm pools to have pre-initialized instances.
2. **Overprovisioning**: Run low-priority 'pause' Pods that consume cluster capacity. When real Pods need space, the pause Pods are preempted (evicted) instantly, and real Pods schedule onto the existing nodes with zero provisioning delay. Karpenter then replaces the lost capacity in the background.

```yaml
# Overprovisioning with pause pods
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: overprovisioning
value: -1  # Lowest priority — preempted first
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: overprovisioning
spec:
  replicas: 5  # 5 buffer pods worth of capacity
  template:
    spec:
      priorityClassName: overprovisioning
      containers:
      - name: pause
        image: registry.k8s.io/pause:3.9
        resources:
          requests:
            cpu: "2"
            memory: 4Gi
```

This trades cost (running empty Pods) for latency (instant scheduling during spikes)."

### Deep Dive Path 2: "VPA vs HPA — can you use both?"

**Interviewer**: "Can VPA and HPA coexist?"

**You**: "This is a common gotcha. VPA adjusts Pod resource requests. HPA adjusts replica count based on resource utilization (which is computed as actual usage / request). If VPA changes the request, HPA's utilization percentage changes, causing it to rescale. They can fight each other.

**The safe pattern**: Use VPA in recommendation mode (`updateMode: Off`) to get sizing recommendations, then apply them manually. Or use VPA for resource requests and HPA for custom metrics (not CPU/memory). Since HPA's custom metric is independent of resource requests, VPA changes do not affect it.

The emerging solution is **MultidimPodAutoscaler** (part of the Kubernetes autoscaling SIG) which combines horizontal and vertical scaling in a single controller. But it is not widely deployed yet.

In practice at EKS scale:
- Use HPA for all services with variable load (scale replicas on RPS or CPU).
- Use VPA in recommendation mode to right-size resource requests during initial deployment.
- Use Karpenter for node-level scaling with consolidation to reclaim unused capacity.
- Use KEDA for event-driven workloads that need scale-to-zero."

### Deep Dive Path 3: "Scaling GPU workloads"

**Interviewer**: "How do you autoscale ML inference workloads on GPUs?"

**You**: "GPU autoscaling is fundamentally different from CPU autoscaling because GPUs are not fractional by default and node provisioning is much slower (GPU instances are capacity-constrained in most regions).

**Pod-level scaling**: Use HPA with a custom metric — GPU utilization or inference queue depth. The NVIDIA DCGM exporter exposes `DCGM_FI_DEV_GPU_UTIL` as a Prometheus metric. Configure a Prometheus adapter to make this available as a K8s custom metric.

```yaml
metrics:
- type: Pods
  pods:
    metric:
      name: DCGM_FI_DEV_GPU_UTIL
    target:
      type: AverageValue
      averageValue: 70  # Scale when avg GPU utilization > 70%
```

**Node-level scaling**: Karpenter supports GPU instances:
```yaml
requirements:
- key: karpenter.k8s.aws/instance-category
  operator: In
  values: ["p", "g"]  # GPU instance families
- key: nvidia.com/gpu
  operator: Exists
```

The challenge: GPU instances take longer to launch (capacity constraints) and cost significantly more. You want to minimize idle GPU time. Karpenter consolidation helps — it can replace an underutilized p3.8xlarge (4 GPUs) with a p3.2xlarge (1 GPU) if only one GPU is in use.

**Time-slicing and MIG**: NVIDIA GPUs can be shared. Time-slicing lets multiple pods share one GPU (with scheduling overhead). MIG (Multi-Instance GPU) on A100/H100 physically partitions the GPU into isolated instances. The NVIDIA GPU Operator manages these configurations. This reduces the need for more GPU nodes by improving utilization per GPU."

---

## How the Industry Built This

- **Karpenter (AWS)**: Open-source node provisioner designed for K8s. Bypasses ASGs, calls EC2 Fleet API directly. Supports spot interruption handling, consolidation, drift detection. [karpenter.sh](https://karpenter.sh/)
- **GKE Autopilot**: Takes autoscaling to the extreme — Google manages both Pod and node scaling. You just submit Pods with resource requests and GKE handles everything. Uses per-Pod billing.
- **KEDA**: CNCF graduated project for event-driven autoscaling. 60+ scalers (SQS, Kafka, Prometheus, HTTP, etc.). [keda.sh](https://keda.sh/)
- **Cluster Autoscaler**: K8s SIG project. Mature but limited — works with node groups, slower than Karpenter, no consolidation. [cluster-autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler).
- **KEPs**: KEP-1610 (Container Resource based Autoscaling), KEP-2840 (In-place Pod vertical scaling — update resources without restart).

References:
- https://karpenter.sh/docs/
- https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- https://github.com/kubernetes/autoscaler
- https://keda.sh/docs/
- https://aws.github.io/aws-eks-best-practices/karpenter/

---

## The Complete Reference Design

### Full Autoscaling Stack

```yaml
# Layer 1: HPA for pod scaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 200
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
```

### Performance Characteristics
| Component | Metric | Value |
|-----------|--------|-------|
| HPA | Evaluation interval | 15s |
| HPA | Scale-up decision to new Pod | ~15-30s (existing capacity) |
| Karpenter | Pending Pod to node Ready | ~60-90s |
| Cluster Autoscaler | Pending Pod to node Ready | ~120-180s |
| Karpenter consolidation | Detection to node termination | ~30s + drain time |
| KEDA | Scale-to-zero to first Pod ready | ~30-60s |
| VPA | Recommendation latency | ~24 hours of data for stable recommendation |
| Overprovisioning | Scale-up with buffer | ~5-15s (instant scheduling) |

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Overprovision buffer | 10-20% of peak capacity | 5-10 buffer pods |
| Karpenter NodePool CPU limit | 1.5x average + headroom | depends on workload |
| HPA maxReplicas | 2-3x peak observed replicas | per-service |
| Spot instance ratio | 70-80% spot for fault-tolerant workloads | Karpenter handles interruption |

---

## Senior vs Staff vs Principal

| Level | What they demonstrate | Example |
|-------|----------------------|---------|
| Senior | Sets up HPA on CPU, understands basic node scaling | Configures HPA with CPU target, knows Cluster Autoscaler exists |
| Staff | Designs multi-layer scaling, prevents oscillation, compares Karpenter vs CA | Explains the overprovisioning pattern, designs HPA behavior policies, knows Karpenter consolidation mechanics |
| Principal | Designs the scaling strategy for the organization, handles GPU scaling, reasons about cost vs latency trade-offs | Proposes per-workload-class scaling policies, designs Karpenter NodePools for different cost/performance tiers, architects scale-to-zero for cost optimization |

---

## Red Flags and Common Mistakes

- **Setting HPA target to 80% CPU**: This leaves no headroom for bursts. By the time HPA reacts (15s evaluation + pod startup time), the existing pods are overwhelmed. Target 50-60% for request-driven services.
- **Ignoring the HPA-node scaling cascade latency**: HPA scales pods in 15s, but if there is no node capacity, Karpenter needs another 60s. Total latency from spike to relief is 75+ seconds. Overprovisioning eliminates the node provisioning delay.
- **Using VPA and HPA on the same CPU metric**: They will fight. VPA changes requests, changing utilization percentages, causing HPA to rescale.
- **Not setting Karpenter limits**: Without CPU/memory limits on the NodePool, a misconfigured HPA can scale to thousands of Pods, Karpenter provisions hundreds of nodes, and your AWS bill explodes.
- **Cluster Autoscaler with too many node groups**: Each node group adds latency to the CA decision loop. More than 20-30 node groups significantly slows CA. Karpenter avoids this entirely by not using node groups.
- **Not using topology-aware scaling**: Scaling all replicas into one AZ creates a single point of failure. Use topology spread constraints with HPA to ensure scaled replicas are distributed.
