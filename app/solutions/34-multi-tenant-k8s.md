# Design a Multi-Tenant Kubernetes Platform

> **Companies**: Any company running shared K8s infrastructure — Amazon (EKS), Google (GKE), Microsoft (AKS), Uber, Airbnb, Spotify, Stripe, platform engineering teams everywhere
> **Level**: Staff / Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a K8s platform that safely and efficiently serves multiple teams/tenants on shared infrastructure? Can you reason about isolation boundaries (namespace, network, compute), resource fairness (quotas, priority, preemption), security (RBAC, network policy, pod security), and the organizational trade-offs between shared clusters and cluster-per-team?
> **Your EKS advantage**: You understand the full isolation stack — IAM roles for service accounts (IRSA), namespace-level RBAC, VPC-CNI network policies, pod security standards, and the real-world challenges of noisy neighbors on shared clusters. You know when namespace isolation is sufficient and when you need cluster-per-tenant.

---

## The First 5 Minutes — Technical Scoping

- "What is our tenancy model? Namespace-per-team on a shared cluster, cluster-per-team, or a virtual cluster (vCluster) model? Each has fundamentally different isolation properties, cost characteristics, and operational complexity."
- "How many tenants? 10 teams on one cluster is manageable. 200 teams requires sophisticated automation — RBAC policies, quota management, and namespace provisioning at scale."
- "What isolation level do we need? Soft isolation (prevent accidental interference between teams) or hard isolation (prevent malicious tenants from accessing other tenants' data)? Hard isolation on shared infrastructure is very difficult without hypervisor-level separation."
- "What's the cost allocation model? Can we charge teams for their resource usage? That requires accurate metering of CPU, memory, GPU, storage, and network per namespace."
- "What self-service capabilities do teams need? Can they create their own CRDs, install operators, configure HPA, deploy admission webhooks? Each capability is a potential blast-radius expansion."
- "What compliance requirements? PCI DSS, SOC 2, HIPAA? These may mandate specific isolation controls (dedicated nodes, encryption, audit logging per tenant)."
- "How do tenants interact with the platform? kubectl directly, a GitOps tool (ArgoCD/Flux), an internal developer portal, or a higher-level abstraction that hides K8s entirely?"

### Working Assumptions
| Parameter | Value |
|-----------|-------|
| Tenants | 50 teams (engineering orgs) |
| Clusters | 3-5 shared clusters (production, staging) |
| Total nodes | 2,000 per cluster |
| Namespaces per tenant | 2-5 (per environment, per service group) |
| Isolation level | Soft isolation (prevent accidents, not malicious attack) |
| Resource fairness | Guaranteed quotas per team, burst allowed |
| Network isolation | Default deny between namespaces, explicit allow |
| Self-service | Teams deploy via GitOps (ArgoCD), no direct kubectl |
| Cost allocation | Per-namespace CPU/memory/storage metering |

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Platform Control Plane                       │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Tenant         │  │  GitOps        │  │  Platform    │  │
│  │  Provisioner    │  │  Controller    │  │  API         │  │
│  │  (namespace,    │  │  (ArgoCD)      │  │  (internal   │  │
│  │   RBAC, quotas, │  │                │  │   portal)    │  │
│  │   network       │  │  One AppProject│  │              │  │
│  │   policies)     │  │  per tenant    │  │              │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Policy Engine  │  │  Cost Metering │  │  Secret      │  │
│  │  (OPA/Gatekeeper│  │  (Kubecost/    │  │  Management  │  │
│  │   or Kyverno)   │  │   OpenCost)    │  │  (External   │  │
│  │                 │  │                │  │   Secrets    │  │
│  │  Enforce:       │  │  Per-namespace │  │   Operator)  │  │
│  │  - Resource     │  │  CPU/memory/   │  │              │  │
│  │    limits       │  │  storage usage │  │              │  │
│  │  - Image policy │  │                │  │              │  │
│  │  - Network      │  │                │  │              │  │
│  │    policy       │  │                │  │              │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Shared K8s Cluster                           │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Namespace: team-a-prod          ResourceQuota:     │    │
│  │  ┌──────────┐ ┌──────────┐       cpu: 100 cores    │    │
│  │  │ Service A │ │ Service B │       memory: 200Gi    │    │
│  │  │ (deploy)  │ │ (deploy)  │       pods: 500        │    │
│  │  └──────────┘ └──────────┘                          │    │
│  │  NetworkPolicy: deny-all + allow-within-namespace   │    │
│  │  RBAC: team-a-role (namespace-scoped)               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Namespace: team-b-prod          ResourceQuota:     │    │
│  │  ┌──────────┐ ┌──────────┐       cpu: 50 cores     │    │
│  │  │ Service C │ │ Service D │       memory: 100Gi    │    │
│  │  └──────────┘ └──────────┘                          │    │
│  │  NetworkPolicy: deny-all + allow-within-namespace   │    │
│  │  RBAC: team-b-role (namespace-scoped)               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Namespace: kube-system (platform-owned)             │    │
│  │  CoreDNS, kube-proxy, CNI, monitoring, ArgoCD       │    │
│  │  RBAC: platform-admin only                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Node Pools:                                                 │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐     │
│  │ General  │  │ GPU (team-c  │  │ High-memory       │     │
│  │ (shared) │  │  dedicated)  │  │ (shared)          │     │
│  └──────────┘  └──────────────┘  └───────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

**Why this architecture**: Multi-tenancy in K8s is built on layered isolation primitives. No single primitive provides complete isolation — you combine RBAC (API access control), ResourceQuota (resource limits), NetworkPolicy (network isolation), PodSecurity (runtime isolation), and admission policies (operational guardrails) to create a defense-in-depth strategy. The platform control plane automates tenant provisioning and policy enforcement, so individual teams do not need to understand the underlying isolation mechanisms.

---

## Core Concepts Deep Dive

### Concept 1: Namespace as the Tenancy Boundary

The namespace is the primary isolation unit in K8s. Most K8s resources are namespaced — Pods, Services, Deployments, ConfigMaps, Secrets, RBAC Roles. When properly configured, a tenant in namespace A cannot see or modify resources in namespace B.

**What namespaces isolate**:
- API access: RBAC Role/RoleBinding scoped to namespace. A team's ServiceAccount can only access resources in their namespace.
- Resource quotas: ResourceQuota limits total CPU, memory, storage, and object count per namespace.
- Network policies: NetworkPolicy controls pod-to-pod traffic at the namespace boundary.
- Service discovery: Services are namespace-scoped. `my-service` in namespace A and `my-service` in namespace B are different services.

**What namespaces do NOT isolate**:
- **Nodes**: Pods from different namespaces can run on the same node. A noisy neighbor can consume node CPU/memory and affect other Pods.
- **Cluster-scoped resources**: Nodes, PersistentVolumes, ClusterRoles, CRDs, namespaces themselves are cluster-scoped. A tenant with ClusterRole permissions can see all namespaces.
- **Kernel**: Pods share the host kernel. A container escape (kernel exploit) gives access to all containers on the node.
- **Network (without NetworkPolicy)**: By default, all Pods can communicate with all other Pods. NetworkPolicy must be explicitly configured.
- **DNS**: By default, Pods can resolve Services in any namespace (`my-service.other-namespace.svc.cluster.local`).

### Concept 2: Resource Fairness — Quotas, LimitRanges, and Priority

**ResourceQuota**: Caps total resource consumption per namespace.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: team-a-prod
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    pods: "500"
    services.loadbalancers: "5"
    persistentvolumeclaims: "50"
    requests.storage: 1Ti
    count/deployments.apps: "100"
```

**LimitRange**: Sets default and maximum resource requests/limits per container. Without LimitRange, a team could create a Pod requesting 1000 cores.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: team-a-prod
spec:
  limits:
  - type: Container
    default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    max:
      cpu: "8"
      memory: 16Gi
    min:
      cpu: 50m
      memory: 64Mi
  - type: PersistentVolumeClaim
    max:
      storage: 100Gi
```

**Priority and preemption across tenants**: When the cluster is fully utilized, which tenant's Pods get evicted? PriorityClasses define this:

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: team-a-production
value: 100000
preemptionPolicy: PreemptLowerPriority
description: "Production workloads for Team A"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: team-a-development
value: 1000
preemptionPolicy: Never
description: "Dev workloads for Team A — never preempt others"
```

**The fairness problem**: Quotas prevent one team from using all resources, but they do not guarantee a team CAN use their quota if the cluster is overcommitted. If Team A has a quota of 100 CPUs but the cluster only has 80 CPUs available (other teams are using the rest within their quotas), Team A's Pods are pending. The solution: ensure total quotas do not exceed cluster capacity, or use Karpenter to scale nodes to meet quota commitments.

### Concept 3: Network Isolation

By default, K8s has a flat network — every Pod can reach every other Pod. For multi-tenancy, this must be locked down.

**Default deny + explicit allow pattern**:

```yaml
# Default deny all ingress and egress for the namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: team-a-prod
spec:
  podSelector: {}  # Apply to all pods in namespace
  policyTypes:
  - Ingress
  - Egress
---
# Allow traffic within the namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: team-a-prod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: team-a-prod
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: team-a-prod
  - to:  # Allow DNS
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
---
# Allow ingress from the load balancer
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-from-lb
  namespace: team-a-prod
spec:
  podSelector:
    matchLabels:
      role: frontend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 10.0.0.0/8  # VPC CIDR (ALB IPs)
    ports:
    - protocol: TCP
      port: 8080
```

**Enforcement**: NetworkPolicy only works if the CNI plugin supports it. VPC-CNI supports K8s NetworkPolicy natively (since EKS 1.25+). Cilium provides enhanced network policies with L7 filtering (HTTP methods, paths) and DNS-based policies.

**Cross-namespace communication**: When Team A's service needs to call Team B's service, you need an explicit allow policy. This should go through a review process — the platform team controls which cross-namespace flows are permitted.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Shared cluster vs cluster-per-team"

**Interviewer**: "Should we give each team their own cluster or share?"

**You**: "This is the most important architectural decision. Let me lay out the trade-offs.

**Shared cluster (namespace-per-team)**:
- *Advantages*: Lower cost (shared control plane, shared system pods like CoreDNS, monitoring agents). Better resource utilization (teams can burst into shared capacity). Simpler networking (services call each other within the cluster). Fewer clusters to manage.
- *Disadvantages*: Noisy neighbor risk (one team's misbehaving workload can affect others). Complex RBAC/policy management. Blast radius is the entire cluster (a control plane issue affects everyone). CRD conflicts (two teams want different versions of the same CRD). Upgrade coordination (you cannot upgrade the cluster for one team without affecting others).

**Cluster-per-team**:
- *Advantages*: Strong isolation (each team has their own control plane, etcd, nodes). Independent upgrade schedules. No noisy neighbor issues. CRD freedom. Easier compliance (PCI team gets a dedicated cluster with specific controls).
- *Disadvantages*: Higher cost (control plane per cluster, duplicate system pods). Cross-cluster service communication requires service mesh or DNS federation. More clusters to manage (50 teams = 50 clusters = 50 upgrade cycles).

**Virtual clusters (vCluster)**:
- *Advantages*: Each tenant gets a virtual K8s API server (running as Pods inside the host cluster). Tenants see their own "cluster" with their own namespace structure, CRDs, and RBAC. But Pods actually run on the shared host cluster. Combines isolation of separate clusters with cost efficiency of shared infrastructure.
- *Disadvantages*: Additional complexity (syncer component translates virtual resources to host resources). Not all K8s features work seamlessly across the virtual/host boundary. Relatively newer technology.

**My recommendation for 50 teams**: A hybrid approach.
1. Shared clusters for standard workloads (80% of teams). Namespace-per-team with full isolation stack (RBAC + quotas + network policies + pod security).
2. Dedicated clusters for high-security or high-autonomy teams (payment processing, ML infrastructure).
3. vCluster for teams that need CRD control or admin-level access without the cost of a full cluster.

The EKS operational reality: each cluster costs ~$73/month for the control plane. 50 clusters = $3,650/month just for control planes. But more importantly, each cluster needs its own monitoring, logging, GitOps, and incident response. The operational cost of many clusters far exceeds the compute cost."

### Deep Dive Path 2: "Design the tenant provisioning system"

**Interviewer**: "How do you onboard a new team to the platform?"

**You**: "Tenant provisioning should be fully automated via a controller (operator pattern). A team requests a tenant via a CRD or an internal portal, and the provisioner creates everything needed.

```yaml
apiVersion: platform.company.com/v1
kind: Tenant
metadata:
  name: team-payments
spec:
  owner: payments-team@company.com
  environments:
  - name: prod
    cluster: prod-us-west-2
    resourceQuota:
      cpu: "100"
      memory: 200Gi
    networkPolicy: strict  # Default deny + explicit allow
    podSecurityStandard: restricted
  - name: staging
    cluster: staging-us-west-2
    resourceQuota:
      cpu: "50"
      memory: 100Gi
    networkPolicy: permissive
    podSecurityStandard: baseline
  costCenter: CC-1234
  oncall: payments-oncall@company.com
```

**What the provisioner creates for each environment**:
1. Namespace with labels (`team: payments`, `env: prod`, `cost-center: CC-1234`)
2. ResourceQuota matching the spec
3. LimitRange with sensible defaults
4. NetworkPolicy (default deny + intra-namespace allow + DNS allow)
5. RBAC: Role + RoleBinding granting the team's OIDC group access to the namespace
6. ServiceAccount with IRSA annotation for AWS access
7. ArgoCD AppProject restricting deployment to this namespace
8. External Secrets SecretStore for the team's secrets path in AWS Secrets Manager
9. Monitoring: namespace-scoped Prometheus rules, Grafana dashboards, PagerDuty integration

```go
func (r *TenantReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var tenant platformv1.Tenant
    if err := r.Get(ctx, req.NamespacedName, &tenant); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    for _, env := range tenant.Spec.Environments {
        ns := fmt.Sprintf("%s-%s", tenant.Name, env.Name)

        // Create namespace
        if err := r.ensureNamespace(ctx, ns, tenant); err != nil {
            return ctrl.Result{}, err
        }

        // Create ResourceQuota
        if err := r.ensureResourceQuota(ctx, ns, env.ResourceQuota); err != nil {
            return ctrl.Result{}, err
        }

        // Create NetworkPolicies
        if err := r.ensureNetworkPolicies(ctx, ns, env.NetworkPolicy); err != nil {
            return ctrl.Result{}, err
        }

        // Create RBAC
        if err := r.ensureRBAC(ctx, ns, tenant.Spec.Owner); err != nil {
            return ctrl.Result{}, err
        }

        // Create ArgoCD AppProject
        if err := r.ensureArgoProject(ctx, ns, tenant); err != nil {
            return ctrl.Result{}, err
        }
    }

    return ctrl.Result{}, nil
}
```

This controller watches Tenant CRDs and reconciles all the downstream resources. When a team is offboarded, deleting the Tenant CRD cascades deletion of everything (namespace deletion cleans up all namespaced resources)."

### Deep Dive Path 3: "How do you handle noisy neighbors?"

**Interviewer**: "Team A's batch job is consuming all the I/O bandwidth on shared nodes. Team B's latency-sensitive service is affected. How do you prevent this?"

**You**: "Noisy neighbors manifest at multiple layers:

**CPU**: Solved by resource requests (guaranteed via cgroup CPU shares) and limits (enforced via CFS bandwidth). But CPU limits cause throttling even when the node has idle CPU. Best practice: set CPU requests (for scheduling fairness) but not CPU limits (allow burst). Use PriorityClass to ensure latency-sensitive Pods are not preempted by batch Pods.

**Memory**: Solved by memory limits (hard cgroup limit, OOM kill on exceed). Unlike CPU, memory is not compressible — you cannot 'throttle' memory, you can only kill the process. Set memory limits equal to requests for guaranteed QoS class.

**Disk I/O**: This is the hardest noisy neighbor problem. K8s has limited support for I/O isolation. ephemeral-storage requests/limits control disk space but not I/O bandwidth. Solutions:
1. **io.max cgroup v2**: On cgroups v2, you can set I/O bandwidth limits per cgroup. The kubelet does not natively configure this, but you can use a custom init container or a device plugin.
2. **Dedicated node pools**: Put I/O-heavy batch workloads on separate node pools with dedicated EBS volumes. Use taints/tolerations to pin batch Pods to batch nodes.
3. **Local NVMe instance store**: Use instances with local NVMe (e.g., i3.xlarge, m5d.xlarge) for I/O-heavy workloads. The local disk has consistent performance (not shared with other instances like EBS).

**Network**: Network bandwidth is shared per node. One Pod can saturate the node's network. Solutions:
1. **Bandwidth plugin**: The K8s bandwidth plugin uses Linux tc (traffic control) to limit Pod bandwidth via annotations.
2. **ENA bandwidth per instance**: AWS ENAs have per-flow bandwidth limits. Larger instance types have higher bandwidth.
3. **Cilium bandwidth manager**: Uses eBPF to enforce per-Pod bandwidth limits with less overhead than tc.

**The general solution**: For truly isolated multi-tenancy, dedicate node pools per tenant (or per isolation class). Latency-sensitive production services get dedicated nodes with guaranteed performance. Batch jobs get shared nodes where noisy neighbor is acceptable. Taints, tolerations, and node affinity enforce this separation.

```yaml
# Node pool taints for tenant isolation
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: team-a-dedicated
spec:
  template:
    spec:
      taints:
      - key: dedicated
        value: team-a
        effect: NoSchedule
      requirements:
      - key: karpenter.sh/capacity-type
        operator: In
        values: ["on-demand"]  # No spot for production
  limits:
    cpu: "200"
```

Team A's Pods must have the matching toleration. No other team's Pods can schedule on these nodes."

---

## How the Industry Built This

- **EKS**: Namespace-level multi-tenancy with IRSA for per-tenant AWS access, VPC-CNI network policies, Pod Identity for simplified IAM integration. EKS Pod Identity (2023) simplifies the IRSA model. [EKS multi-tenancy best practices](https://aws.github.io/aws-eks-best-practices/security/docs/multitenancy/).
- **GKE**: GKE Enterprise includes Policy Controller (OPA-based), Config Sync (GitOps), and hierarchical namespaces (HNC). GKE Autopilot enforces pod security standards and resource limits by default.
- **AKS**: Azure Policy for K8s (OPA-based), AAD integration for RBAC, virtual nodes for burst. AKS has built-in workload identity.
- **Open source**: Capsule (multi-tenant operator), vCluster (virtual clusters), Loft (multi-tenancy platform), HNC (hierarchical namespace controller from K8s SIG), Kiosk (multi-tenancy extension).

References:
- https://kubernetes.io/docs/concepts/security/multi-tenancy/
- https://aws.github.io/aws-eks-best-practices/security/docs/multitenancy/
- https://github.com/loft-sh/vcluster
- https://github.com/projectcapsule/capsule
- https://github.com/kubernetes-sigs/hierarchical-namespaces
- KEP-2839 (Namespace labels for Pod Security Standards)

---

## The Complete Reference Design

### Tenant Provisioning CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: tenants.platform.company.com
spec:
  group: platform.company.com
  names:
    kind: Tenant
    plural: tenants
  scope: Cluster
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: ["owner", "environments"]
            properties:
              owner:
                type: string
              costCenter:
                type: string
              environments:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    cluster:
                      type: string
                    resourceQuota:
                      type: object
                      properties:
                        cpu:
                          type: string
                        memory:
                          type: string
```

### Policy Engine Configuration (Kyverno)

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resource-limits
spec:
  validationFailureAction: Enforce
  rules:
  - name: require-limits
    match:
      any:
      - resources:
          kinds:
          - Pod
    exclude:
      any:
      - resources:
          namespaces:
          - kube-system
          - karpenter
    validate:
      message: "All containers must have memory limits set."
      pattern:
        spec:
          containers:
          - resources:
              limits:
                memory: "?*"
---
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-image-registries
spec:
  validationFailureAction: Enforce
  rules:
  - name: allowed-registries
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Images must come from approved registries."
      pattern:
        spec:
          containers:
          - image: "123456789.dkr.ecr.*.amazonaws.com/*"
          initContainers:
          - image: "123456789.dkr.ecr.*.amazonaws.com/*"
---
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: enforce-pod-security
spec:
  validationFailureAction: Enforce
  rules:
  - name: restricted-security-context
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaceSelector:
            matchLabels:
              pod-security: restricted
    validate:
      message: "Containers must run as non-root with read-only root filesystem."
      pattern:
        spec:
          containers:
          - securityContext:
              runAsNonRoot: true
              readOnlyRootFilesystem: true
              allowPrivilegeEscalation: false
              capabilities:
                drop:
                - ALL
```

### RBAC Template per Tenant

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: tenant-developer
  namespace: team-a-prod
rules:
- apiGroups: ["", "apps", "batch"]
  resources: ["pods", "deployments", "statefulsets", "jobs", "cronjobs",
              "services", "configmaps", "secrets", "serviceaccounts"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
# Explicitly exclude dangerous permissions
# No access to: nodes, namespaces, clusterroles, CRDs, PVs
# No access to: pods/exec (prevent exec into other teams' pods)
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: team-a-developers
  namespace: team-a-prod
subjects:
- kind: Group
  name: team-a-developers  # OIDC group from identity provider
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: tenant-developer
  apiGroup: rbac.authorization.k8s.io
```

### Performance Characteristics
| Component | Metric | Value |
|-----------|--------|-------|
| Namespace provisioning | Time (controller) | ~5-10s |
| RBAC evaluation | Per-request overhead | ~1ms |
| NetworkPolicy enforcement | Per-packet overhead (eBPF) | ~100ns |
| NetworkPolicy enforcement | Per-packet overhead (iptables) | ~1-10us |
| ResourceQuota admission | Per-request overhead | ~2ms |
| OPA/Gatekeeper evaluation | Per-request overhead | ~5-20ms |
| Kyverno evaluation | Per-request overhead | ~5-15ms |
| Cost metering (Kubecost) | Collection interval | 1 minute |

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Namespaces per cluster | tenants * environments | 100-250 |
| RBAC objects | tenants * (Roles + RoleBindings + ServiceAccounts) | 500-1500 |
| NetworkPolicy rules | tenants * (default deny + allow rules) | 300-1000 |
| Admission webhook load | API QPS * matching rules | 1000-5000 evaluations/sec |
| Platform controller | Reconciles tenant CRDs | 200m CPU, 256 MB memory |

---

## Senior vs Staff vs Principal

| Level | What they demonstrate | Example |
|-------|----------------------|---------|
| Senior | Understands RBAC and namespaces, can configure resource quotas | Creates namespace with Role, RoleBinding, and ResourceQuota for a team |
| Staff | Designs the full isolation stack (RBAC + network policy + pod security + quotas), reasons about noisy neighbor mitigation | Implements default-deny network policies, designs tenant provisioning controller, compares shared vs dedicated clusters with cost analysis |
| Principal | Designs the organizational platform strategy, reasons about self-service vs guardrails trade-offs, architects for 100+ teams | Proposes vCluster for teams needing CRD control, designs cost allocation and chargeback systems, builds the internal developer platform abstraction that hides K8s complexity, decides when NOT to use K8s |

---

## Red Flags and Common Mistakes

- **Giving tenants cluster-admin**: Even for convenience during development. ClusterAdmin can see secrets in all namespaces, modify node objects, delete system pods. Always use namespace-scoped Roles.
- **No network policies**: Without NetworkPolicy, any Pod can call any other Pod in the cluster. A compromised Pod in one namespace can attack services in every other namespace. Default-deny is essential.
- **Shared CRDs without versioning**: If Team A installs CRD v1alpha1 and Team B needs v1beta1, they conflict at the cluster level. CRDs are cluster-scoped — this is a fundamental tension in shared clusters. The solution is vCluster or policy controls on CRD creation.
- **Resource quotas without LimitRanges**: Quotas limit total usage but not individual Pod size. Without LimitRange, a tenant can create one Pod requesting the entire quota, starving their other Pods. LimitRange sets default and maximum per-container limits.
- **Over-relying on namespace isolation for compliance**: Namespace isolation is soft isolation — it prevents accidents, not attacks. For PCI or HIPAA workloads, you likely need dedicated clusters, dedicated nodes (with taints), and potentially dedicated AWS accounts.
- **Not metering costs**: Without per-tenant cost visibility, platform teams cannot drive accountability. Teams with no cost visibility tend to over-provision. Kubecost or OpenCost should be deployed from day one.
- **Ignoring DNS cross-namespace resolution**: By default, Pods can resolve `service.other-namespace.svc.cluster.local`. This does not bypass NetworkPolicy (the connection will still be blocked), but it leaks information about what services exist in other namespaces. For strict multi-tenancy, consider DNS policies that restrict cross-namespace resolution.
