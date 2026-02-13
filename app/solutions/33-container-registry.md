# Design a Container Registry

> **Companies**: Amazon (ECR), Google (Artifact Registry), Docker (Hub), GitHub (GHCR), JFrog (Artifactory), any company with CI/CD pipelines
> **Level**: Staff / Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a content-addressable storage system that efficiently stores, distributes, and secures container images? Can you reason about OCI image specifications, layer deduplication, image pull performance at scale, and registry-to-K8s integration (image pull secrets, admission policies, image caching)?
> **Your EKS advantage**: You understand the image pull critical path — from kubelet image pull, to ECR credential provider, to containerd image store. You know how image pull latency affects Pod startup time and what strategies (caching, pre-pulling, lazy loading) reduce it at scale.

---

## The First 5 Minutes — Technical Scoping

- "Are we designing the registry service itself, or the K8s integration? The registry is essentially a content-addressable blob store with an HTTP API. The K8s integration — credential management, image pull optimization, vulnerability scanning, admission policies — is where the real complexity lives."
- "What scale? How many images, how many pulls per second? ECR handles millions of pulls/day per region. A 1000-node cluster doing a rolling deployment of a 1 GB image means 1000 concurrent pulls — that is 1 TB of bandwidth in minutes."
- "Multi-region? If workloads run in us-west-2 and us-east-1, do we need cross-region replication? Pulling a 1 GB image across regions adds ~10 seconds and significant data transfer costs."
- "Image scanning requirements? Scan on push (block vulnerable images), scan on pull (real-time vulnerability checks), or continuous scanning (detect new CVEs against existing images)?"
- "Immutable tags? In production, you never want `latest` or mutable tags — a re-push of the same tag can change what is deployed without any K8s resource change. Immutable tags or digest-based pulls are essential."
- "What image formats? OCI images, Helm charts (OCI-based), WASM modules? Modern registries store any OCI artifact, not just container images."
- "Private registry authentication model? Per-cluster credentials, per-namespace credentials, or node-level credentials (like EC2 instance role for ECR)?"

### Working Assumptions
| Parameter | Value |
|-----------|-------|
| Total images | 10,000 unique images, 100,000 tags |
| Image size (median) | 500 MB (multi-layer) |
| Layer deduplication ratio | ~60% shared layers (common base images) |
| Pull rate | ~5,000 pulls/hour steady, ~50,000/hour during deployments |
| Push rate | ~500 pushes/hour (CI/CD pipelines) |
| Regions | 3 (us-west-2, us-east-1, eu-west-1) |
| Vulnerability scanning | Scan on push, block critical CVEs |
| Authentication | ECR with IAM roles, IRSA for EKS |
| Retention | 90 days for non-production tags |

---

## High-Level Architecture

```
                    ┌────────────────────────────────────┐
                    │         Registry Service            │
                    │                                     │
  docker push /     │  ┌──────────┐  ┌───────────────┐  │
  crane push        │  │ API      │  │ Auth/AuthZ    │  │
  ──────────────▶  │  │ (OCI     │  │ (IAM/OIDC/    │  │
                    │  │  Distribution│ token-based)│  │
                    │  │  Spec)   │  │               │  │
                    │  └────┬─────┘  └───────────────┘  │
                    │       │                            │
                    │  ┌────┴────────────────────────┐   │
                    │  │  Manifest Store              │   │
                    │  │  (image manifests, tags,     │   │
                    │  │   multi-arch index)          │   │
                    │  └────┬────────────────────────┘   │
                    │       │                            │
                    │  ┌────┴────────────────────────┐   │
                    │  │  Blob Store                  │   │
                    │  │  (content-addressed layers)  │   │
                    │  │  Key: sha256 digest          │   │
                    │  │  Value: compressed layer     │   │
                    │  │  Backend: S3/GCS/Azure Blob  │   │
                    │  └────────────────────────────┘   │
                    │                                     │
                    │  ┌──────────────────────────────┐  │
                    │  │  Vulnerability Scanner        │  │
                    │  │  (Trivy/Grype/ECR scanning)  │  │
                    │  │  Scan on push, continuous     │  │
                    │  └──────────────────────────────┘  │
                    └────────────────────────────────────┘

                    ┌────────────────────────────────────┐
                    │       K8s Cluster Integration       │
                    │                                     │
                    │  ┌──────────────────────────────┐  │
                    │  │  kubelet                      │  │
                    │  │  └─ credential provider       │  │
                    │  │     (ecr-credential-provider) │  │
                    │  │  └─ containerd                │  │
                    │  │     └─ image pull (CRI)       │  │
                    │  │     └─ snapshotter (overlayfs)│  │
                    │  └──────────────────────────────┘  │
                    │                                     │
                    │  ┌──────────────────────────────┐  │
                    │  │  Admission Control             │  │
                    │  │  - Image policy webhook       │  │
                    │  │  - Sigstore/Cosign validation │  │
                    │  │  - Allowed registry list      │  │
                    │  └──────────────────────────────┘  │
                    └────────────────────────────────────┘
```

**Why this architecture**: A container registry is fundamentally a content-addressable storage system. Images are stored as layers (blobs) identified by SHA256 digests. Manifests describe how layers compose into an image. This content-addressable design enables layer deduplication — if 100 images share the same base layer (e.g., `ubuntu:22.04`), the layer is stored once. The OCI Distribution Specification defines the HTTP API for push/pull, making registries interoperable.

---

## Core Concepts Deep Dive

### Concept 1: OCI Image Format and Content-Addressable Storage

An OCI image consists of:

**1. Manifests**: JSON documents that describe the image. A manifest lists:
- Config blob (runtime configuration: env vars, entrypoint, labels)
- Ordered list of layer digests (the filesystem layers)
- Media type for each layer

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": "sha256:abc123...",
    "size": 7023
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:layer1hash...",
      "size": 32654
    },
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:layer2hash...",
      "size": 16724
    }
  ]
}
```

**2. Index (multi-arch)**: A manifest list pointing to platform-specific manifests (amd64, arm64). When kubelet pulls `my-image:v1`, the runtime requests the index, selects the manifest matching its architecture, then pulls the layers.

**3. Layers (blobs)**: Compressed tar archives of filesystem diffs. Each layer represents changes from the previous layer: added files, modified files, deleted files (whiteout entries). Stored in S3/GCS by their SHA256 digest. Deduplication is automatic — two images with the same base layer reference the same blob.

**Layer deduplication math**: If 100 images are built from `python:3.11` (500 MB base), the base layer is stored once. Without dedup: 100 * 500 MB = 50 GB. With dedup: 500 MB + 100 * (app layer, ~50 MB each) = 5.5 GB. That is a ~10x storage reduction.

### Concept 2: Image Pull Optimization

Image pull is often the biggest contributor to Pod startup latency, especially for cold pulls (image not cached on node).

**The pull sequence**:
1. kubelet receives Pod spec, asks containerd to ensure the image exists.
2. containerd checks its local image store. If the image (by digest or tag) is cached, skip pull.
3. If not cached, containerd resolves the tag to a digest by fetching the manifest from the registry.
4. containerd checks each layer — if the layer digest exists locally, skip it. Otherwise, download the layer.
5. containerd decompresses layers and applies them via the snapshotter (overlayfs).
6. Container is created with the union mount of all layers.

**Optimization strategies**:

**Pre-pulling**: DaemonSet that pulls commonly-used images to all nodes. Ensures the first Pod using that image does not pay the pull cost. Karpenter can specify AMIs with pre-cached images.

**Image streaming / lazy loading**: Instead of pulling the entire image before starting the container, start the container and load filesystem layers on demand. SOCI (Seekable OCI) on EKS does this — it creates a SOCI index that allows random access into compressed layers. The container starts in seconds even for multi-GB images, and layers are fetched in the background.

```yaml
# SOCI index annotation on the image manifest
# AWS ECR auto-generates SOCI indices for images > 250 MB
```

**Registry proximity**: Pull from the same region. Cross-region pulls add latency and data transfer cost. ECR cross-region replication ensures images are available in all regions where you run workloads.

**Layer caching on nodes**: containerd caches layers by digest. If a new image version changes only the top layer (app code), the base layers are already cached. This is why good Dockerfile layer ordering matters — put rarely-changing layers (OS packages, runtime) first, frequently-changing layers (app code) last.

### Concept 3: Image Security — Signing, Scanning, and Admission

**Image signing with Sigstore/Cosign**: Every image pushed to the registry should be signed. Cosign generates a signature using the image digest and a private key (or keyless signing via OIDC identity). The signature is stored as an OCI artifact alongside the image.

```bash
# Sign an image
cosign sign --key cosign.key 123456789.dkr.ecr.us-west-2.amazonaws.com/app:v1.2.3

# Verify a signature
cosign verify --key cosign.pub 123456789.dkr.ecr.us-west-2.amazonaws.com/app:v1.2.3
```

**Admission control for image verification**: A K8s admission webhook (like Kyverno or Connaisseur) can verify image signatures before allowing Pods to run:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
spec:
  validationFailureAction: Enforce
  rules:
  - name: verify-cosign-signature
    match:
      any:
      - resources:
          kinds:
          - Pod
    verifyImages:
    - imageReferences:
      - "123456789.dkr.ecr.us-west-2.amazonaws.com/*"
      attestors:
      - entries:
        - keys:
            publicKeys: |-
              -----BEGIN PUBLIC KEY-----
              ...
              -----END PUBLIC KEY-----
```

**Vulnerability scanning**: ECR's enhanced scanning uses Amazon Inspector to continuously scan images for CVEs. You can gate deployments on scan results:
- **Critical/High CVEs**: Block deployment via admission webhook
- **Medium CVEs**: Allow deployment but create a Jira ticket
- **Continuous scanning**: New CVEs are published daily. Images that were clean yesterday might have vulnerabilities today. Continuous scanning detects this and can trigger alerts or automated re-builds.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Walk me through image pull authentication on EKS"

**Interviewer**: "How does kubelet authenticate to ECR to pull private images?"

**You**: "There are several approaches, each with different trade-offs.

**1. Node-level IAM role (EC2 instance profile)**: The simplest approach. The node's IAM role includes `ecr:GetAuthorizationToken` and `ecr:BatchGetImage` permissions. The kubelet credential provider (ecr-credential-provider plugin) calls STS to get temporary ECR credentials. Every Pod on the node can pull from ECR — no per-namespace isolation.

**2. IRSA (IAM Roles for Service Accounts)**: More granular. Each K8s ServiceAccount is annotated with an IAM role ARN. The Pod's projected service account token is exchanged for AWS credentials via the OIDC provider. The kubelet (or a sidecar) uses these credentials to authenticate to ECR. This gives per-ServiceAccount access control — different teams can access different ECR repositories.

**3. imagePullSecrets**: Standard K8s mechanism. A Secret of type `kubernetes.io/dockerconfigjson` is created in the namespace, containing registry credentials. The Pod spec references it via `imagePullSecrets`. Drawback: ECR tokens expire every 12 hours, so you need a credentials refresh mechanism (like external-secrets-operator or a CronJob).

**The credential provider plugin flow** (modern approach, K8s 1.26+):
1. kubelet needs to pull an image from `123456789.dkr.ecr.us-west-2.amazonaws.com/app:v1`.
2. kubelet calls the ecr-credential-provider binary via the kubelet credential provider API.
3. The binary matches the image registry against its configuration, calls `ecr:GetAuthorizationToken`.
4. ECR returns a base64-encoded username:password (username is `AWS`, password is a 12-hour token).
5. kubelet passes these credentials to containerd, which includes them in the HTTP request to the registry.
6. Credentials are cached by the kubelet for the token's lifetime.

```yaml
# kubelet credential provider configuration
apiVersion: kubelet.config.k8s.io/v1
kind: CredentialProviderConfig
providers:
- name: ecr-credential-provider
  matchImages:
  - "*.dkr.ecr.*.amazonaws.com"
  - "*.dkr.ecr.*.amazonaws.com.cn"
  defaultCacheDuration: "12h"
  apiVersion: credentialprovider.kubelet.k8s.io/v1
```"

### Deep Dive Path 2: "Design for high-throughput image distribution"

**Interviewer**: "You are rolling out a new version to 5,000 nodes simultaneously. The 2 GB image needs to reach every node. How do you design for this?"

**You**: "This is a real challenge. 5,000 nodes x 2 GB = 10 TB of data transfer. Even with layer caching reducing this to maybe 500 MB of new layers per node, that is still 2.5 TB.

**Approach 1: Registry with CDN/caching**
ECR uses S3 as the blob store with CloudFront as a CDN. The first pull fetches from S3, subsequent pulls in the same region hit the CloudFront cache. But 5,000 concurrent pulls to a single S3 prefix can hit throughput limits (5,500 GET/sec per prefix). ECR partitions blobs across multiple S3 prefixes to handle this.

**Approach 2: P2P image distribution (Dragonfly/Spegel)**
Instead of every node pulling from the registry, nodes share layers peer-to-peer. The first node pulls from the registry, then other nodes can pull from that first node. Dragonfly (CNCF project) implements this — it runs a daemon on each node that acts as a local proxy/cache. When containerd pulls an image, it goes through the Dragonfly daemon, which checks peers first.

Spegel is a newer, simpler option — it is a K8s-native image sharing daemon that uses the OCI distribution spec. Each node advertises which layers it has. Other nodes discover peers via a hash ring and pull layers from the closest peer.

**Approach 3: Pre-bake images into AMIs**
For known images (base images, system services), build them into the node AMI. When a node launches, the image is already on disk. This is the fastest option but requires AMI rebuild pipelines and does not work for frequently-updated application images.

**Approach 4: Image streaming (SOCI)**
With SOCI indices, containerd starts the container without downloading the full image. Layers are loaded on demand via HTTP range requests. A 2 GB image with SOCI starts in ~5 seconds instead of ~60 seconds. The layers stream in the background while the application is already running.

For a 5,000-node deployment, I would use:
1. SOCI for fast startup (container starts in seconds).
2. Staggered rollout (`maxSurge: 25%`) to avoid 5,000 simultaneous pulls.
3. Regional ECR replication to pull from the local region.
4. Proper layer ordering in Dockerfiles to maximize cache hits (base layer changes rarely)."

### Deep Dive Path 3: "Design an image lifecycle and garbage collection policy"

**Interviewer**: "We have 50 TB of images in ECR. How do you manage lifecycle?"

**You**: "ECR lifecycle policies automate image cleanup based on rules:

```json
{
  \"rules\": [
    {
      \"rulePriority\": 1,
      \"description\": \"Keep last 10 production images\",
      \"selection\": {
        \"tagStatus\": \"tagged\",
        \"tagPrefixList\": [\"prod-\"],
        \"countType\": \"imageCountMoreThan\",
        \"countNumber\": 10
      },
      \"action\": { \"type\": \"expire\" }
    },
    {
      \"rulePriority\": 2,
      \"description\": \"Delete untagged images older than 7 days\",
      \"selection\": {
        \"tagStatus\": \"untagged\",
        \"countType\": \"sinceImagePushed\",
        \"countUnit\": \"days\",
        \"countNumber\": 7
      },
      \"action\": { \"type\": \"expire\" }
    },
    {
      \"rulePriority\": 3,
      \"description\": \"Delete dev images older than 30 days\",
      \"selection\": {
        \"tagStatus\": \"tagged\",
        \"tagPrefixList\": [\"dev-\", \"feature-\"],
        \"countType\": \"sinceImagePushed\",
        \"countUnit\": \"days\",
        \"countNumber\": 30
      },
      \"action\": { \"type\": \"expire\" }
    }
  ]
}
```

**Node-level garbage collection**: containerd also has GC. The kubelet triggers image GC when `imagefs` usage exceeds `imageGCHighThresholdPercent` (default 85%). It deletes unused images, oldest first, until usage drops below `imageGCLowThresholdPercent` (default 80%). A 'used' image is one referenced by any Pod on the node.

**The tag immutability problem**: If someone re-pushes `app:v1` with different content, running Pods still use the old image (kubelet has it cached), but new nodes pull the new (different) image. You get inconsistent deployments. Solutions:
1. ECR tag immutability (prevent tag overwrite).
2. Always reference by digest: `app@sha256:abc123...`.
3. Use a policy that tags with unique identifiers (git SHA, build number)."

---

## How the Industry Built This

- **ECR (AWS)**: Fully managed registry. S3 backend for blob storage. Cross-region/cross-account replication. Enhanced scanning via Amazon Inspector. SOCI support for lazy loading. IAM-based authentication. [ECR docs](https://docs.aws.amazon.com/ecr/).
- **Artifact Registry (Google)**: Successor to GCR. Supports OCI artifacts (images, Helm charts, language packages). Regional and multi-regional storage. Binary Authorization integration for admission control.
- **GHCR (GitHub)**: Integrated with GitHub Actions CI/CD. Free for public images. Uses GitHub identity for authentication.
- **Distribution (CNCF)**: The open-source registry implementation. Basis for Harbor, GitLab Container Registry, and others. Implements the OCI Distribution Spec. [github.com/distribution/distribution](https://github.com/distribution/distribution).
- **Harbor (CNCF)**: Enterprise registry with vulnerability scanning (Trivy), image signing (Cosign/Notary), replication, and RBAC. [goharbor.io](https://goharbor.io/).

References:
- https://github.com/opencontainers/distribution-spec
- https://github.com/opencontainers/image-spec
- https://docs.aws.amazon.com/AmazonECR/latest/userguide/
- https://github.com/sigstore/cosign
- https://github.com/awslabs/soci-snapshotter

---

## The Complete Reference Design

### ECR Repository Configuration

```yaml
# Terraform/CloudFormation for production ECR
resource "aws_ecr_repository" "app" {
  name                 = "my-app"
  image_tag_mutability = "IMMUTABLE"  # Prevent tag overwrite

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr.arn
  }
}

resource "aws_ecr_replication_configuration" "cross_region" {
  replication_configuration {
    rule {
      destination {
        region      = "us-east-1"
        registry_id = data.aws_caller_identity.current.account_id
      }
      destination {
        region      = "eu-west-1"
        registry_id = data.aws_caller_identity.current.account_id
      }
    }
  }
}
```

### Performance Characteristics
| Operation | Metric | Value |
|-----------|--------|-------|
| Image pull (cached, same region) | Latency | <1s |
| Image pull (1 GB, cold, same region) | Latency | 20-40s |
| Image pull (1 GB, SOCI) | Container start | ~3-5s |
| Image pull (cross-region) | Additional latency | +10-20s |
| Image push (500 MB) | Latency | 5-15s |
| Manifest resolution (tag to digest) | Latency | ~50-100ms |
| ECR auth token retrieval | Latency | ~200ms |
| Vulnerability scan (on push) | Latency | 30-120s |
| Layer upload (parallel) | Throughput | ~100 MB/s per layer |

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Storage (with dedup) | images * avg_unique_layers * avg_layer_size | 5-20 TB |
| Bandwidth (deployment) | nodes * new_layer_size / rollout_time | 10-100 Gbps |
| ECR pull rate limit | 1000 pulls/sec per account/region (can request increase) | Monitor throttling |
| Node disk for images | running_images * decompressed_size | 50-200 GB per node |

---

## Senior vs Staff vs Principal

| Level | What they demonstrate | Example |
|-------|----------------------|---------|
| Senior | Understands OCI image format, can set up ECR and imagePullSecrets | Explains layers and deduplication, configures registry authentication |
| Staff | Designs image distribution for scale, implements scanning and signing pipelines, optimizes pull performance | Proposes SOCI for large images, designs lifecycle policies, implements Cosign verification via admission webhook |
| Principal | Designs the organization-wide image supply chain, architects multi-region distribution, reasons about SBOM and compliance | Proposes P2P distribution for 10K-node clusters, designs image provenance chain (build → sign → scan → attest → deploy), architects cross-account registry sharing with least-privilege IAM |

---

## Red Flags and Common Mistakes

- **Using mutable tags in production**: `latest` or any mutable tag means the same tag can point to different images. This breaks reproducibility and can cause different nodes to run different image contents.
- **Not considering pull throughput during deployments**: A 1000-node rolling deployment pulling a 1 GB image generates ~1 TB of registry traffic. Without caching, CDN, or staggered rollouts, this can throttle the registry.
- **Storing secrets in images**: API keys, database passwords, or certificates baked into image layers are visible to anyone who can pull the image. Layers are not encrypted. Use K8s Secrets or external secret managers instead.
- **Ignoring image size**: Large images slow down deployments, increase storage costs, and widen the attack surface. Multi-stage Docker builds, distroless base images, and layer optimization should be standard practice.
- **No vulnerability scanning**: Running unscanned images in production means unknown CVEs are exposed. Scan on push and block critical CVEs via admission control.
- **Pulling by tag instead of digest**: Tags can change. Digests are immutable. For production deployments, always reference the image by its SHA256 digest to guarantee exactly-once image content.
