# Design a Data Plane

> **Companies**: Amazon (EKS data plane), Google (GKE), Microsoft (AKS), Cloudflare, Datadog, any company running workloads on K8s
> **Level**: Staff / Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design the node-level infrastructure that actually runs containers — the kubelet, container runtime, CNI networking, and CSI storage? Can you reason about Linux kernel primitives (cgroups, namespaces, eBPF), network data paths, and node lifecycle management?
> **Your EKS advantage**: You work on the EKS data plane. You know the VPC-CNI plugin internals, how kubelet manages pod lifecycle, the AMI build process, and real-world node failure modes. You can talk about warm IP pools, custom networking, and prefix delegation from experience.

---

## The First 5 Minutes — Technical Scoping

- "Are we designing for a managed node group (like EKS managed node groups) or self-managed nodes? That determines who owns AMI lifecycle, kubelet configuration, and node health monitoring."
- "What's our networking model? Overlay (VXLAN/Geneve) or native routed (VPC-CNI/Azure CNI)? This fundamentally changes the data path — overlay adds encap/decap overhead, native routed has VPC IP allocation limits."
- "What container runtime? containerd is the standard now since dockershim removal in 1.24. But some workloads need Kata Containers or gVisor for hard isolation. Are we supporting multiple runtimes per node?"
- "What's the pod density target per node? The default is 110 pods/node but VPC-CNI limits this to the number of ENI secondary IPs — for m5.xlarge that's 58 pods max. Prefix delegation raises this to 110+."
- "Do we need GPU/accelerator support? NVIDIA device plugin, time-slicing, MIG partitioning — this changes the device plugin architecture and scheduling constraints."
- "What storage requirements? EBS (block), EFS (NFS), FSx (high-perf)? Each has different CSI driver characteristics and failure modes."
- "How fast must nodes join the cluster? For autoscaling, the time from EC2 launch to pod-ready determines your scaling responsiveness. In EKS, we target ~60 seconds with cached AMIs."

### Working Assumptions
| Parameter | Value |
|-----------|-------|
| Nodes | 1,000 worker nodes (m5.2xlarge, 8 vCPU, 32 GB) |
| Pods per node | 58 (VPC-CNI default) or 110+ (prefix delegation) |
| Container runtime | containerd 1.7+ via CRI |
| CNI | VPC-CNI (native routed) or Cilium (eBPF) |
| Node boot to pod-ready | <90 seconds |
| kubelet PLEG interval | 1 second |
| Node heartbeat | 10s via Lease objects |
| Image pull time | <10s for cached, <60s for cold pull (1 GB image) |
| CSI | EBS CSI driver for block storage |

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Worker Node                            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │                   kubelet                         │    │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────────┐  │    │
│  │  │ Pod      │  │ PLEG     │  │ Volume Manager │  │    │
│  │  │ Lifecycle│  │ (Pod     │  │ (attach/mount  │  │    │
│  │  │ Manager  │  │  Lifecycle│  │  CSI volumes)  │  │    │
│  │  │         │  │  Event   │  │                │  │    │
│  │  │         │  │  Gen)    │  │                │  │    │
│  │  └────┬────┘  └──────────┘  └────────────────┘  │    │
│  │       │                                          │    │
│  │  ┌────┴─────────────────────────────────────┐    │    │
│  │  │          CRI (gRPC interface)            │    │    │
│  │  └────┬─────────────────────────────────────┘    │    │
│  └───────┼──────────────────────────────────────────┘    │
│          │                                               │
│  ┌───────┴──────────────────────────────────────────┐    │
│  │              containerd                           │    │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────┐  │    │
│  │  │ Image    │  │ Snapshotter│  │ Runtime      │  │    │
│  │  │ Service  │  │ (overlayfs)│  │ (runc/kata)  │  │    │
│  │  └──────────┘  └───────────┘  └──────────────┘  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │              Networking Stack                     │    │
│  │  ┌───────────┐  ┌───────────┐  ┌──────────────┐  │    │
│  │  │ CNI Plugin│  │ kube-proxy│  │ CoreDNS      │  │    │
│  │  │ (VPC-CNI/ │  │ /Cilium   │  │ (cluster DNS)│  │    │
│  │  │  Cilium)  │  │ eBPF      │  │              │  │    │
│  │  └───────────┘  └───────────┘  └──────────────┘  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │              Storage Stack                        │    │
│  │  ┌───────────┐  ┌───────────────────────────┐    │    │
│  │  │ CSI Driver│  │ Device Plugins            │    │    │
│  │  │ (EBS/EFS) │  │ (GPU/FPGA/custom)         │    │    │
│  │  └───────────┘  └───────────────────────────┘    │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Linux Kernel                                    │    │
│  │  cgroups v2 │ namespaces │ eBPF │ netfilter     │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**Why this architecture**: The data plane is a layered system where each layer provides a well-defined interface. The kubelet is the node agent that manages Pod lifecycle. It talks to the container runtime via CRI (Container Runtime Interface), to the network via CNI (Container Network Interface), and to storage via CSI (Container Storage Interface). These interfaces allow swapping implementations without changing the kubelet — you can run containerd or CRI-O, VPC-CNI or Cilium, EBS or Ceph, all through the same interfaces.

---

## Core Concepts Deep Dive

### Concept 1: kubelet Pod Lifecycle Management

The kubelet is the most complex node-level component. It watches the API server for Pods assigned to its node and ensures containers match the declared spec.

**Pod startup sequence** (the actual steps, not the simplified version):

1. **kubelet receives Pod spec** via watch from API server (filtered to `spec.nodeName == thisNode`).
2. **Admission**: kubelet runs its own admission checks — does the node have enough resources? Are required volumes available? Are the container images allowed by the NodeRestriction admission plugin?
3. **Volume setup**: The Volume Manager attaches volumes (CSI `ControllerPublishVolume`), waits for attachment, then mounts (CSI `NodeStageVolume` + `NodePublishVolume`). For EBS, this means calling the EC2 API to attach the volume to the instance, then running `mount` on the block device.
4. **Image pull**: containerd pulls container images. Image pull secrets are resolved from the Pod spec. For ECR, this uses the `ecr-credential-provider` kubelet plugin.
5. **Sandbox creation**: containerd creates the Pod sandbox — a pause container that holds the network namespace. The CNI plugin is called to set up networking for this sandbox.
6. **Init containers**: Run in order, each must complete before the next starts.
7. **App containers**: Started in parallel (with startup/liveness/readiness probes configured).
8. **Probe management**: kubelet runs probes according to their schedule. A failed readiness probe removes the Pod from Service endpoints. A failed liveness probe triggers container restart.

**PLEG (Pod Lifecycle Event Generator)**: The kubelet polls containerd every 1 second to detect container state changes. This is the "generic PLEG" — it relists all containers and diffs. When a container exits unexpectedly, PLEG detects it and the kubelet initiates restart (based on `restartPolicy`). PLEG latency > 3 minutes causes the node to report `NotReady`. This is a common production issue — usually caused by slow container runtime operations (hung image pulls, stuck volume mounts).

```go
// Simplified kubelet sync loop
func (kl *Kubelet) syncLoop(updates <-chan kubetypes.PodUpdate) {
    syncTicker := time.NewTicker(time.Second)
    for {
        select {
        case update := <-updates:
            kl.handlePodUpdates(update.Pods)
        case <-syncTicker.C:
            kl.handlePodSyncs(kl.getPodsToSync())
        case <-kl.pleg.Watch():
            kl.handlePodLifecycleEvents()
        case <-housekeepingTicker.C:
            kl.handleHousekeeping()
        }
    }
}
```

### Concept 2: Container Networking (CNI Deep Dive)

The CNI specification is simple: a binary that takes a container namespace and returns an IP configuration. But the implementations are complex.

**VPC-CNI (EKS default)**:
- Each node gets multiple ENIs (Elastic Network Interfaces). Each ENI has a primary IP and multiple secondary IPs.
- When a Pod needs an IP, the CNI assigns a secondary IP from a warm pool. The Pod's network namespace gets a `veth` pair: one end in the Pod, other end on the host, with the secondary IP assigned.
- **The IP warm pool problem**: The VPC-CNI daemon (`ipamd`) pre-allocates IPs to reduce Pod startup latency. It maintains `WARM_IP_TARGET` (default: 1 ENI worth of IPs) ready to assign. If the warm pool is empty and a new ENI must be attached, Pod startup is delayed by ~5-10 seconds.
- **Prefix delegation**: Instead of assigning individual secondary IPs to ENIs, assign /28 prefixes (16 IPs per prefix). This dramatically increases pod density — from 58 pods on m5.xlarge to 110+.
- **Custom networking**: By default, Pods get IPs from the node's subnet. With custom networking, Pods can get IPs from a different subnet (useful for separating node and pod CIDR ranges or using dedicated pod subnets with larger CIDR blocks).

**Cilium (eBPF-based)**:
- Replaces kube-proxy entirely. Service load balancing happens in eBPF at the kernel level, bypassing iptables.
- Uses eBPF programs attached to TC (traffic control) hooks for packet processing.
- Supports transparent encryption (WireGuard or IPsec), network policies with L7 visibility, and Hubble for observability.
- On EKS, Cilium can run in "chaining" mode (using VPC-CNI for IP allocation, Cilium for policy and load balancing) or "ENI" mode (Cilium manages ENIs directly).

**Network data path for a Pod-to-Pod packet**:
```
Pod A (10.0.1.5) → veth → host routing table → [iptables/eBPF] →
  if same node: → veth → Pod B (10.0.1.8)
  if different node (VPC-CNI): → ENI → VPC routing → target node ENI → veth → Pod B
  if different node (overlay): → VXLAN encap → UDP → target node → VXLAN decap → veth → Pod B
```

### Concept 3: Container Runtime and Linux Primitives

**containerd architecture**:
containerd is a container runtime daemon that manages the complete container lifecycle. The kubelet communicates with it via CRI (gRPC).

Key components:
- **Image service**: Pulls and stores OCI images. Uses overlayfs as the default snapshotter — each layer is a separate directory, and the container filesystem is a union mount of all layers.
- **Runtime service**: Creates and manages container processes. Uses `runc` (the OCI runtime reference implementation) by default. `runc` sets up Linux namespaces, cgroups, and seccomp profiles, then executes the container entrypoint.
- **Shim**: Each container has a shim process (`containerd-shim-runc-v2`) that acts as the parent of the container process. This allows containerd to restart without affecting running containers.

**Linux primitives for container isolation**:
- **Namespaces**: PID (process isolation), Network (network stack), Mount (filesystem), UTS (hostname), IPC (inter-process communication), User (UID mapping). Each Pod gets its own network and IPC namespace. Each container gets its own PID and mount namespace.
- **cgroups v2**: Resource limits and accounting. CPU limits use the CFS (Completely Fair Scheduler) bandwidth controller — a container with `limits.cpu: 2` gets 200ms of CPU time per 100ms period. Memory limits use the memory controller — exceeding the limit triggers OOM kill.
- **seccomp**: System call filtering. The default seccomp profile blocks ~50 dangerous syscalls (e.g., `mount`, `reboot`, `kexec_load`).
- **AppArmor/SELinux**: Mandatory Access Control. Restricts file access, network operations, and capability usage beyond what namespaces provide.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Walk me through Pod networking"

**Interviewer**: "A Pod on Node A sends an HTTP request to a Service backed by Pods on Node B. Walk me through every hop."

**You**: "Starting from the application's perspective: the app resolves the Service DNS name (e.g., `my-service.default.svc.cluster.local`) via CoreDNS. CoreDNS returns the Service ClusterIP (say, 10.100.50.10).

The app sends a TCP SYN to 10.100.50.10:80. The packet leaves the Pod's network namespace via the veth pair to the host network namespace.

**With kube-proxy (iptables mode)**: On the host, the packet hits iptables rules installed by kube-proxy. The KUBE-SERVICES chain matches the ClusterIP and jumps to KUBE-SVC-xxx, which uses a random probability chain to select a backend Pod IP (say, 10.0.2.15 on Node B). The packet is DNAT'd — destination changes from 10.100.50.10 to 10.0.2.15. SNAT may be applied depending on the source.

**With kube-proxy (eBPF/Cilium)**: The packet is intercepted by a BPF program on the TC egress hook of the veth. The BPF program looks up the Service in a BPF map, selects a backend, and rewrites the destination IP. No iptables involved — this is significantly faster at scale (iptables rules grow linearly with Services * Endpoints; eBPF lookups are O(1) hash map lookups).

After DNAT, the packet has destination 10.0.2.15 (Pod on Node B). With VPC-CNI, this IP is a real VPC IP. The host routing table sends the packet out the ENI. VPC routing delivers it to Node B's ENI (because the VPC route table knows which ENI has which IPs). On Node B, the packet arrives at the ENI, enters the host network namespace, and is routed via the veth pair into the target Pod's network namespace.

With overlay networking (VXLAN), the host would encapsulate the packet in a UDP/VXLAN header with the outer destination being Node B's node IP. Node B's VXLAN interface decapsulates and delivers to the Pod."

**Interviewer**: "What happens when a Pod is terminating but a client still sends traffic to it?"

**You**: "This is a classic race condition. When a Pod starts terminating, two things happen in parallel:
1. The kubelet sends SIGTERM to the container and starts the `terminationGracePeriodSeconds` countdown.
2. The Endpoints controller removes the Pod from the Endpoints object, and kube-proxy updates iptables to stop sending new traffic.

The race: the Pod might stop accepting connections (SIGTERM handler) before kube-proxy has updated its rules on all nodes. New connections will be sent to a Pod that is already shutting down.

The solution is a `preStop` lifecycle hook that sleeps for a few seconds before the app shuts down:
```yaml
lifecycle:
  preStop:
    exec:
      command: ['sleep', '15']
```
This gives kube-proxy time to propagate the endpoint removal across all nodes before the app starts rejecting connections. The sleep duration should be longer than the worst-case endpoint propagation time (typically 5-10 seconds in a large cluster)."

### Deep Dive Path 2: "Design the node bootstrap process"

**Interviewer**: "How do you get a bare EC2 instance to a fully functional K8s node as fast as possible?"

**You**: "The EKS-optimized AMI is the key. It ships with containerd, kubelet, VPC-CNI, and system dependencies pre-installed. The bootstrap process on boot:

1. **cloud-init / user-data**: The launch template includes a bootstrap script that configures the kubelet with cluster-specific parameters: API server endpoint, cluster CA certificate, DNS cluster IP.

2. **kubelet starts**: It uses the TLS bootstrap protocol — generates a CSR (Certificate Signing Request), sends it to the API server signed with the bootstrap token. The csrapprover controller in the controller-manager auto-approves it (for managed node groups, the IAM role mapping validates the node identity).

3. **Node registration**: kubelet registers the Node object with the API server. The node starts in `NotReady` state.

4. **CNI setup**: The VPC-CNI daemon starts, attaches an ENI, allocates a warm pool of IPs. This takes 5-10 seconds.

5. **System pods start**: kube-proxy (or Cilium), CoreDNS stubs, node problem detector, CSI node plugins start as DaemonSets.

6. **Node Ready**: Once the CNI reports ready and system pods are running, the node transitions to `Ready`. The scheduler can now assign Pods.

To minimize time-to-ready:
- Use cached AMIs with pre-pulled common images.
- Enable prefix delegation to reduce ENI allocation calls.
- Set `--max-pods` appropriately to avoid unnecessary ENI operations.
- Use warm pools (EC2 feature) to have pre-initialized instances ready to go.
- The total time: ~45-90 seconds from EC2 launch to first Pod scheduled."

### Deep Dive Path 3: "How do you handle node failures gracefully?"

**Interviewer**: "A node's disk fills up. What happens?"

**You**: "The kubelet has built-in eviction thresholds. When the node filesystem (nodefs) exceeds the eviction threshold (default: available < 15% for soft eviction, < 10% for hard eviction), the kubelet starts evicting Pods.

The eviction order:
1. Pods using more ephemeral storage than their request
2. BestEffort Pods (no resource requests)
3. Burstable Pods (partial resource requests)
4. Guaranteed Pods (requests == limits) are evicted last

The kubelet also watches for `imagefs` pressure (container image storage). When imagefs is pressured, it garbage-collects unused images — oldest unused first.

The kubelet sets the node condition `DiskPressure: True`, which triggers a taint `node.kubernetes.io/disk-pressure:NoSchedule`. The scheduler will not place new Pods on this node.

The operational response at EKS scale: we monitor `kubelet_evictions` and `node_filesystem_avail` metrics. Persistent disk pressure indicates the node type is undersized for the workload. The fix is usually: increase instance storage, add instance store volumes for ephemeral storage, or set appropriate `ephemeralStorage` requests so the scheduler accounts for disk usage."

---

## How the Industry Built This

- **EKS**: Custom-built VPC-CNI that allocates real VPC IPs to Pods. EKS-optimized Amazon Linux AMI with pre-installed K8s binaries. Managed node groups with automatic AMI updates and rolling replacement. [EKS networking best practices](https://aws.github.io/aws-eks-best-practices/networking/).
- **GKE**: Dataplane V2 (Cilium-based eBPF networking). COS (Container-Optimized OS) as the node OS. GKE Autopilot fully manages nodes.
- **AKS**: Azure CNI with overlay mode (avoids IP exhaustion). Mariner Linux as the node OS. Virtual Kubelet for burst to ACI.
- **Key KEPs**: KEP-2400 (Node-level resource management), KEP-3063 (Dynamic Resource Allocation for GPUs), KEP-4033 (Device Plugin Manager overhaul), KEP-2254 (cgroup v2 support).

References:
- https://kubernetes.io/docs/concepts/architecture/nodes/
- https://github.com/containernetworking/cni/blob/main/SPEC.md
- https://github.com/aws/amazon-vpc-cni-k8s
- https://docs.cilium.io/en/stable/
- https://github.com/kubernetes/enhancements/tree/master/keps/sig-node

---

## The Complete Reference Design

### Node Configuration

```yaml
# kubelet configuration for production
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
containerRuntimeEndpoint: unix:///run/containerd/containerd.sock
maxPods: 110
podPidsLimit: 4096
evictionHard:
  memory.available: "100Mi"
  nodefs.available: "10%"
  imagefs.available: "15%"
evictionSoft:
  memory.available: "200Mi"
  nodefs.available: "15%"
evictionSoftGracePeriod:
  memory.available: "1m30s"
  nodefs.available: "1m30s"
kubeReserved:
  cpu: "200m"
  memory: "1Gi"
  ephemeral-storage: "1Gi"
systemReserved:
  cpu: "200m"
  memory: "500Mi"
imageGCHighThresholdPercent: 85
imageGCLowThresholdPercent: 80
```

### VPC-CNI Configuration

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: aws-node
  namespace: kube-system
spec:
  template:
    spec:
      containers:
      - name: aws-node
        env:
        - name: ENABLE_PREFIX_DELEGATION
          value: "true"         # Enable /28 prefix delegation
        - name: WARM_PREFIX_TARGET
          value: "1"            # Keep 1 warm prefix (16 IPs)
        - name: MINIMUM_IP_TARGET
          value: "3"            # Minimum warm IPs
        - name: ENABLE_POD_ENI
          value: "true"         # Enable security groups for pods
        - name: AWS_VPC_K8S_CNI_CUSTOM_NETWORK_CFG
          value: "true"         # Custom networking (pod subnet != node subnet)
```

### Performance Characteristics
| Component | Metric | Value |
|-----------|--------|-------|
| Pod startup (warm IP) | Time to running | ~2-5s |
| Pod startup (cold ENI attach) | Time to running | ~10-20s |
| Image pull (cached) | Time | <1s |
| Image pull (1 GB, cold) | Time | ~30-60s |
| VPC-CNI IP allocation | Latency | ~100ms (warm pool) |
| kube-proxy iptables | Rule count at 5K services | ~50K rules |
| Cilium eBPF | Service lookup | O(1), ~100ns |
| kubelet PLEG | Relist interval | 1s |
| Node heartbeat (Lease) | Interval | 10s |

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Pod IPs per node | ENI count * IPs per ENI (or prefix delegation) | 58-110+ per node |
| Node kubelet memory | ~50 MB base + ~1 MB per pod | 100-200 MB |
| containerd memory | ~50 MB base + image cache | 200-500 MB |
| System reserved CPU | kubelet + containerd + kube-proxy + CNI | 400m-1000m |
| System reserved memory | kubelet + containerd + OS | 1.5-3 GB |

---

## Senior vs Staff vs Principal

| Level | What they demonstrate | Example |
|-------|----------------------|---------|
| Senior | Understands kubelet, CRI, CNI basics, can explain pod networking | Draws the veth pair diagram, explains how kube-proxy works |
| Staff | Understands the full data path, can compare iptables vs eBPF, knows CNI implementation differences | Explains VPC-CNI warm pool mechanics, designs for pod density limits, understands PLEG failure modes |
| Principal | Designs the node platform (AMI pipeline, bootstrap, health monitoring), reasons about eBPF vs iptables for fleet-wide decisions | Proposes custom node OS, designs graceful node draining with zero-downtime guarantees, architects GPU sharing across pods |

---

## Red Flags and Common Mistakes

- **Not understanding the veth pair model**: Every Pod has a virtual ethernet pair connecting its namespace to the host. If you cannot explain this, you do not understand Pod networking.
- **Ignoring IP address exhaustion**: With VPC-CNI, each Pod consumes a VPC IP. A /24 subnet gives 254 IPs — that is fewer than 5 nodes worth of Pods. This is a real operational issue at EKS scale.
- **Confusing overlay vs native networking**: Overlay (VXLAN) adds encapsulation overhead but is more flexible. Native (VPC-CNI) has no overhead but ties you to the cloud provider's IP management.
- **Not knowing about PLEG**: PLEG latency is one of the most common causes of node NotReady. If kubelet cannot relist containers within the threshold, the node appears unhealthy. Causes: slow container runtime, too many containers per node, disk I/O pressure.
- **Skipping system reserved resources**: If you do not reserve CPU and memory for kubelet, kube-proxy, and the container runtime, user Pods can starve system components and make the node unresponsive. This is the `kubeReserved` and `systemReserved` kubelet configuration.
