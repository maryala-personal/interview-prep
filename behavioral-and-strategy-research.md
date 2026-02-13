# Senior/Staff Software Engineer Interview Preparation Guide

## For: AWS EKS Dataplane/Controlplane Engineer (Python & Go)

**Compiled: February 2025 | Applicable through 2026 hiring cycles**

> This guide is tailored for a candidate with deep Kubernetes infrastructure experience
> (EKS control plane and data plane), proficiency in Python and Go, and targeting
> Senior (E5/L5/L63) through Staff (E6/L6/L65) roles at top-tier companies.

---

# Table of Contents

1. [Behavioral Interview Deep Dive](#1-behavioral-interview-deep-dive)
2. [Team Matching Strategies](#2-team-matching-strategies)
3. [Interview Process by Company](#3-interview-process-by-company)
4. [Preparation Timeline (4-8 Week Plan)](#4-preparation-timeline)
5. [Streamlit App Ideas for Interview Prep Tracking](#5-streamlit-app-ideas-for-interview-prep-tracking)

---

# 1. Behavioral Interview Deep Dive

## 1.1 Frameworks for Structuring Answers

### STAR Framework (Situation, Task, Action, Result)

The gold standard. Every behavioral answer should follow this structure:

- **Situation**: Set the scene in 2-3 sentences. Provide enough context that the interviewer understands the stakes, the team, and the constraints. For your background: "I was working on the EKS data plane team, responsible for the networking layer that handles pod-to-pod communication across 50,000+ clusters..."
- **Task**: What was your specific responsibility? At senior/staff level, this must show *ownership* and *scope*. Not "I was asked to..." but "I identified the need to..." or "I took ownership of..."
- **Action**: The longest section (60-70% of your answer). Detail YOUR specific contributions. Use "I" not "we." Describe technical decisions, trade-offs, how you influenced others, and how you navigated obstacles.
- **Result**: Quantify impact. Revenue saved, latency reduced, incidents prevented, teams unblocked, adoption numbers. Always include what you *learned* and what you would do differently.

**For Staff-level answers**: Extend STAR to include **I** (Impact beyond your team) and **L** (Lessons/Leadership). Staff engineers are evaluated on cross-organizational impact.

### CARL Framework (Context, Action, Result, Learning)

Simpler variant. Useful for shorter behavioral questions or follow-ups. Emphasizes the learning component that staff-level candidates must demonstrate.

### SBI Framework (Situation, Behavior, Impact)

Best for conflict resolution and feedback-related questions. Focuses on observable behaviors and their concrete impact.

### The "Pyramid" Approach for Staff-Level

Start with the outcome/impact (the "so what"), then drill into details. This mirrors how staff engineers communicate: leading with business impact, then technical depth on demand. Interviewers for E6/L6+ roles specifically look for this communication pattern.

---

## 1.2 Behavioral Questions by Category

### A. Leadership and Influence (Without Authority)

This is the #1 differentiator between Senior and Staff. Staff engineers lead through influence, not management authority.

**Common questions:**

1. "Tell me about a time you drove a technical initiative across multiple teams."
2. "Describe a situation where you had to convince senior leadership to change direction on a technical decision."
3. "Tell me about a time you mentored someone and it significantly impacted the team."
4. "How have you influenced engineering culture or practices beyond your immediate team?"
5. "Describe a time you had to lead a project where you had no formal authority over the contributors."
6. "Tell me about a time you identified a problem nobody else saw and drove the solution."

**How to answer with EKS experience:**

- Leading the design of a new controller or operator that required buy-in from multiple teams (API team, networking team, node team)
- Proposing and driving an RFC/design doc for a cross-cutting concern (e.g., observability, upgrade strategy, API deprecation)
- Establishing on-call practices, runbook standards, or incident response procedures adopted beyond your team
- Driving a Golang library or shared tooling adoption across the org

**Meta-specific (E5/E6):** Meta evaluates "Leadership & Drive" as a core signal. They want examples of proactive problem identification and mobilizing others. Think about times you created a roadmap, set technical direction, or unblocked multiple teams.

**Uber-specific:** Uber values "ownership mindset" heavily. They want to see that you treat the business problem as your own. Think about times your technical decisions directly impacted rider/driver experience or infrastructure cost.

**Microsoft-specific:** Microsoft looks for "Growth Mindset" and "Customer Obsession." Frame answers in terms of customer impact (internal or external) and what you learned.

---

### B. Conflict Resolution and Difficult Conversations

7. "Tell me about a time you had a significant disagreement with a colleague about a technical approach."
8. "Describe a situation where you received critical feedback. How did you handle it?"
9. "Tell me about a time you had to deliver difficult feedback to a peer or report."
10. "Describe a conflict between two team members that you helped resolve."
11. "Tell me about a time when you disagreed with your manager's decision. What did you do?"
12. "How have you handled a situation where a senior engineer on your team was underperforming?"

**Frameworks for conflict answers:**

- Always show you *sought to understand* the other perspective first
- Demonstrate that you separated the technical merits from the personal dynamics
- Show how you found common ground or created a structured decision-making process (e.g., writing a comparison doc, running a prototype/benchmark, defining evaluation criteria)
- End with the outcome AND the relationship impact (positive)

**EKS-specific conflict examples to prepare:**

- Disagreement about whether to use a CRD-based approach vs. a webhook-based approach for a feature
- Conflict between "move fast" (ship the feature) vs. "do it right" (address tech debt first) on the control plane
- Disagreement with a partner team (e.g., VPC networking team) about API contract ownership
- Push-back from customers (internal or external) on a breaking change or deprecation

---

### C. Technical Decision-Making Under Ambiguity

13. "Tell me about a time you had to make a critical technical decision with incomplete information."
14. "Describe a situation where you had multiple viable technical approaches. How did you decide?"
15. "Tell me about a time when a technical bet you made didn't work out. What happened?"
16. "Describe the most architecturally complex system you've designed. What trade-offs did you make?"
17. "How do you decide when to build vs. buy vs. adopt open-source?"
18. "Tell me about a time you had to simplify a complex system."

**Staff-level differentiators for these questions:**

- Show you considered the 2nd and 3rd order effects of your decision
- Demonstrate awareness of organizational and business constraints, not just technical ones
- Discuss how you communicated the decision and its trade-offs to stakeholders
- Show that you created a framework or criteria that others could reuse

**EKS-specific examples:**

- Deciding between extending an existing Kubernetes controller vs. writing a new one
- Choosing a concurrency model in Go for a high-throughput data plane component
- Deciding how to handle backward compatibility when evolving a Kubernetes API
- Making a build-vs-upstream decision (fork upstream K8s code vs. contribute back vs. build custom)

---

### D. Cross-Team Collaboration

19. "Tell me about a project that required coordinating across 3+ teams."
20. "How do you handle dependencies on teams that have different priorities?"
21. "Describe a time you had to align multiple stakeholders with competing interests."
22. "Tell me about a time you improved a cross-team process."

**EKS examples:**

- Coordinating between control plane, data plane, networking, and security teams for a major K8s version upgrade
- Working with the AWS IAM team on IRSA (IAM Roles for Service Accounts) integration
- Partnering with internal customers (SageMaker, Lambda, etc.) who run on EKS

---

### E. Mentoring and Growing Others

23. "Tell me about how you've grown the technical skills of your team."
24. "Describe your approach to code review. How do you balance speed with teaching?"
25. "Tell me about a time you helped someone get promoted."
26. "How do you onboard new engineers to a complex system?"

**EKS examples:**

- Onboarding new engineers to the Kubernetes codebase (notoriously complex)
- Creating design review processes, writing culture, or architecture decision records (ADRs)
- Running tech talks or internal training on Kubernetes internals

---

### F. Handling Ambiguity and Driving Clarity

27. "Tell me about a time you were given a vague problem and had to define the solution space."
28. "How do you prioritize when everything seems urgent?"
29. "Describe a time when requirements changed significantly mid-project."
30. "Tell me about a time you had to say no to a stakeholder."

---

## 1.3 Meta-Specific Behavioral Signals (Evaluated in "Behavioral" Round)

Meta's behavioral interview for E5/E6 explicitly evaluates four signals:

| Signal | What They Look For | Senior (E5) | Staff (E6) |
|--------|-------------------|-------------|------------|
| **Resolution/Drive** | Proactive problem-solving, bias for action, persistence | Solves problems in your team's domain | Identifies and solves problems across the org |
| **Collaboration** | Working effectively with others, including through conflict | Works well within your team and adjacent teams | Drives alignment across orgs with competing priorities |
| **Communication** | Clarity of thought, conciseness, ability to adjust to audience | Communicates clearly to technical peers | Communicates effectively to executives and non-technical stakeholders |
| **Growth/Coachability** | Learning from mistakes, seeking feedback, growing others | Shows personal growth and helps teammates grow | Creates systems and culture that grow many engineers |

---

## 1.4 Preparing Your Story Bank

Build a bank of **8-12 stories** from your EKS experience that can be adapted to multiple questions. Each story should cover:

| Story # | Project/Situation | Categories It Covers | Impact Metrics |
|---------|-------------------|---------------------|----------------|
| 1 | Major control plane feature | Technical decision, Cross-team, Ambiguity | |
| 2 | Production incident | Leadership, Conflict, Communication | |
| 3 | Tech debt initiative | Drive, Influence, Technical decision | |
| 4 | Mentoring/onboarding | Growth, Collaboration, Communication | |
| 5 | Cross-team dependency | Collaboration, Conflict, Stakeholder management | |
| 6 | Performance optimization | Technical decision, Data-driven, Impact | |
| 7 | Process improvement | Leadership, Culture, Influence | |
| 8 | Failed project/mistake | Growth, Learning, Resilience | |

**Fill this table in with your actual experiences. Have 2-3 backup stories.**

---

# 2. Team Matching Strategies

## 2.1 Your Competitive Advantages

With EKS Dataplane/Controlplane experience in Python and Go, you have a rare skill set:

- **Deep Kubernetes internals**: API server, etcd, controllers, scheduler, kubelet, CNI, CSI, CRI
- **Cloud provider integration**: How K8s integrates with cloud-native networking, storage, IAM
- **Go**: The lingua franca of cloud-native infrastructure
- **Python**: Widely used for tooling, automation, ML infrastructure
- **Distributed systems at scale**: EKS serves hundreds of thousands of clusters
- **AWS operational experience**: Understanding of control plane as a managed service

---

## 2.2 Meta (Facebook/Meta Platforms)

### Target Teams

#### 1. Production Engineering (PE) -- Infrastructure

**What they do:** Meta's PE teams own the reliability, scalability, and efficiency of Meta's entire infrastructure. This is Meta's equivalent of SRE but with more software engineering emphasis.

**Specific sub-teams:**
- **Container Orchestration / Twine**: Meta's internal container orchestration system (not Kubernetes, but analogous). Your EKS experience translates directly -- scheduling, resource management, container lifecycle, service discovery.
- **Compute Platform**: Manages the fleet of machines, capacity planning, bin-packing, machine lifecycle. Deeply relevant if you've worked on EKS node management or Karpenter-style autoscaling.
- **Network Infrastructure PE**: Owns the software-defined networking layer. If you've worked on EKS VPC CNI plugin or pod networking, this maps directly.
- **Resource Management / Efficiency**: Optimizing compute utilization across the fleet. Translates from your experience with EKS resource management, pod scheduling, and bin-packing.

**Why they'd want you:** Meta has been investing heavily in efficiency (Project Aria, etc.) and someone who understands container orchestration at the control plane level is extremely valuable.

#### 2. Infrastructure -- Platforms

- **Service Mesh / RPC Framework (ServiceRouter, Thrift)**: If you've worked on EKS service mesh integrations (Envoy, App Mesh), this is a natural fit.
- **Kubernetes/Cloud Migration Teams**: Meta has been evaluating/adopting Kubernetes for certain workloads. Your deep K8s expertise is directly applicable.
- **Storage Infrastructure**: If you've touched CSI drivers or persistent storage on EKS.

#### 3. AI Infrastructure

- **Training Infrastructure**: Teams building the platform for training large models (PyTorch clusters, GPU scheduling). Your container orchestration + Python experience is directly relevant.
- **Inference Infrastructure**: Deploying and serving models at scale. Container orchestration is central to this.
- **MLOps / ML Platform**: Building the tooling and platforms that ML engineers use. Python + orchestration experience is ideal.

**Leveling context:** PE roles at Meta are on the same ladder as SWE (E3-E8). E5 is Senior, E6 is Staff. PE tends to value operational experience and incident response more heavily.

#### How to position yourself for Meta:
- Emphasize **scale** (number of clusters, API calls/sec, nodes managed)
- Emphasize **reliability** (SLAs, incident response, blast radius reduction)
- Emphasize **efficiency** (cost reduction, utilization improvements)
- Prepare to discuss Meta's unique constraints: massive scale, custom hardware, internal tooling

---

## 2.3 Uber

### Target Teams

#### 1. Compute Platform

**What they do:** Owns the container orchestration and compute abstraction layer for all of Uber's services.

**Specific sub-teams:**
- **Container Platform (formerly Peloton)**: Uber built Peloton (open-source resource manager) and has since evolved their compute platform. They now use a mix of Kubernetes and custom orchestration. Your EKS control plane experience maps perfectly.
- **Kubernetes Platform**: Uber's migration to Kubernetes has been a multi-year initiative. They run large K8s clusters and need engineers who understand K8s internals at the deepest level.
- **Serverless / Function Platform**: Building Uber's internal serverless compute. Container lifecycle management is central.

#### 2. Infrastructure Platform

- **Networking Infrastructure**: Service mesh (Uber uses a custom sidecar-based mesh), load balancing, DNS, traffic management. If you've worked on EKS networking (CNI, service mesh, load balancer controllers), this is a strong match.
- **Storage Platform**: Distributed storage systems (SchemalessDB, Docstore, etc.). Relevant if you've worked on EKS storage integration.
- **Observability Platform**: Metrics, logging, tracing at massive scale. If you've built or operated monitoring for EKS clusters, this transfers well.

#### 3. Developer Platform

- **CI/CD Platform**: Build and deployment infrastructure. Your experience with K8s deployment controllers and rollout strategies is relevant.
- **Developer Experience**: Tooling and abstractions that make Uber's engineers productive. Python tooling experience is valuable here.

#### 4. AI/ML Platform

- **Michelangelo**: Uber's ML platform for training and serving models. Container orchestration + Python = perfect fit.
- **GPU Compute**: Managing GPU clusters for ML workloads. K8s GPU scheduling and device plugins are directly relevant.

**Leveling context:** Uber uses L3-L7 leveling. L5a is Senior I, L5b is Senior II, L6 is Staff. For EKS experience, L5b-L6 is the target range depending on years of experience and scope.

#### How to position yourself for Uber:
- Emphasize **migration experience** (K8s migrations, version upgrades at scale)
- Emphasize **multi-tenancy** (how you handle noisy neighbors, resource isolation)
- Emphasize **developer experience** (how you make K8s accessible to app developers)
- Prepare to discuss Uber's constraints: real-time systems, global scale, cost sensitivity

---

## 2.4 Microsoft

### Target Teams

#### 1. Azure Kubernetes Service (AKS)  -- THE Top Match

**What they do:** Microsoft's managed Kubernetes service, directly competing with EKS. This is the most natural team match.

**Specific sub-teams:**
- **AKS Control Plane**: API server management, etcd operations, controller management. You literally do the same thing for EKS. This is a 1:1 match.
- **AKS Data Plane / Node**: Kubelet, node provisioning (AKS Node Provisioner / Karpenter equivalent), OS image management. Direct match if you work on EKS data plane.
- **AKS Networking**: Azure CNI, Network Policy, Service Mesh (Istio-based add-on). Maps to EKS VPC CNI plugin work.
- **AKS Security**: Workload identity, pod security, network policy, Azure Policy integration.
- **AKS Add-ons and Extensions**: KEDA, Dapr, GitOps (Flux), monitoring add-ons.

**Why this is the top match:** You would bring direct competitor expertise. Microsoft would highly value your knowledge of how EKS solves the same problems. Be prepared to discuss what AKS does better/worse than EKS (do your homework on AKS features).

#### 2. Azure Infrastructure

- **Azure Compute (VMSS, Spot, etc.)**: The layer below AKS. How VMs are provisioned and managed. Relevant if you've worked on EKS node group management.
- **Azure Networking (Virtual Networks, Load Balancer)**: The cloud networking layer that K8s sits on top of.
- **Azure Resource Manager (ARM)**: The control plane for all Azure resources. If you've worked on EKS CloudFormation integrations or AWS service integration.

#### 3. Azure AI Infrastructure

- **Azure AI Compute**: GPU/TPU cluster management for Azure OpenAI and other AI services. K8s is the foundation. This is a rapidly growing area.
- **Azure Machine Learning**: The ML platform. Uses K8s heavily for training and inference workloads.

#### 4. Microsoft Developer Division (DevDiv)

- **GitHub Actions Infrastructure**: CI/CD at scale, uses K8s for runner management.
- **Azure DevOps**: Build/release pipelines infrastructure.
- **VS Code Remote / Codespaces**: Container-based development environments. K8s orchestration is central.

**Leveling context:** Microsoft levels: 59-67+ for engineering. L63 is Senior, L65 is Principal (equivalent to Staff). L64 is sometimes used as Senior II. For your background, L63-L65 is the target.

#### How to position yourself for Microsoft:
- Emphasize **managed service experience** (you know what it takes to run K8s as a service)
- Emphasize **scale and reliability** (EKS scale numbers, SLA management)
- Emphasize **customer empathy** (understanding K8s user pain points)
- Be ready to compare/contrast EKS vs AKS architectural decisions
- Microsoft heavily values **inclusive/growth mindset culture** -- prepare examples

---

## 2.5 AI Companies -- Infrastructure and Platform Teams

### OpenAI

**Relevant teams:**
- **Infrastructure / Compute Platform**: Manages the GPU clusters and compute fabric that trains and serves GPT models. Kubernetes is foundational to their infrastructure. They run massive K8s clusters with custom schedulers.
- **Platform Engineering**: Internal developer platform, CI/CD, deployment infrastructure. Go + Python + K8s = perfect fit.
- **API Platform / Serving Infrastructure**: The infrastructure behind the ChatGPT and API products. Container orchestration, autoscaling, traffic management at enormous scale.
- **Reliability Engineering**: Ensuring uptime for the API. On-call, incident response, SLO management. Your EKS operational experience is directly relevant.
- **Research Infrastructure**: Building the tools and systems that researchers use. Jupyter infrastructure, experiment tracking, resource management.

**What they work on specifically:** Custom Kubernetes operators for GPU workload management, multi-cluster scheduling, large-scale model checkpointing and loading, inference optimization infrastructure, developer tooling in Python.

**Why they'd want you:** OpenAI's compute infrastructure is Kubernetes-heavy and they need people who understand K8s internals (not just YAML-level usage). Go is their primary infrastructure language.

### Anthropic

**Relevant teams:**
- **Infrastructure / Platform**: Building and operating the compute platform that trains Claude models. K8s-based orchestration for GPU workloads, custom scheduling, resource management.
- **Reliability / Production Engineering**: Keeping the API reliable at scale. Similar to SRE but with more software engineering focus.
- **Developer Tools / Internal Platform**: Tooling and automation for research and engineering teams. Python-heavy.
- **Serving Infrastructure**: The system that serves Claude (the model you're reading right now). Autoscaling, traffic management, model loading/unloading, multi-region deployment.
- **Training Infrastructure**: Large-scale distributed training systems. GPU cluster management, job scheduling, checkpoint management.

**What they work on specifically:** Kubernetes cluster management at scale, custom controllers for ML workloads, GPU-aware scheduling, efficient model serving infrastructure, internal developer platform.

**Why they'd want you:** Anthropic is growing rapidly and needs infrastructure engineers who can operate at scale. K8s + Go + Python + managed service experience is an ideal combination.

### Google DeepMind

**Relevant teams:**
- **DeepMind Infrastructure**: Building the custom infrastructure for AI research. Uses GKE (Google's K8s service) and internal Google infrastructure (Borg). Your K8s experience translates, though Google uses Borg internally.
- **Research Platform**: The platform that researchers use to run experiments. Job scheduling, resource management, notebook infrastructure.
- **ML Infrastructure**: Training frameworks, distributed training infrastructure, model serving.

**Note:** Google/DeepMind primarily uses internal tools (Borg, Colossus, etc.) rather than open-source K8s internally. However, GKE (their external K8s service) team values EKS experience. The DeepMind infra teams increasingly use GKE-based workflows.

**Google Cloud -- GKE Team (separate from DeepMind but worth mentioning):**
- **GKE Control Plane**: Direct competitor to EKS. Same dynamic as AKS -- your competitor expertise is highly valued.
- **GKE Autopilot**: Serverless K8s (similar to Fargate). Control plane abstraction.
- **GKE Networking**: Network policy, service mesh (Anthos Service Mesh).

### Other AI Companies to Consider

#### Databricks
- **Compute Platform**: K8s-based compute for Spark and ML workloads. Go + K8s is a perfect fit.
- **Infrastructure**: Cloud infrastructure management across AWS, Azure, GCP.

#### Scale AI
- **Infrastructure / Platform**: Managing the compute platform for data labeling and AI evaluation.

#### Nvidia
- **DGX Cloud Infrastructure**: K8s-based GPU cloud infrastructure.
- **GPU Operator Team**: Kubernetes operators for GPU management.

#### CoreWeave
- **Kubernetes Infrastructure**: Their entire cloud is built on Kubernetes. They are one of the largest Kubernetes deployments in the world. Your expertise would be directly applicable to their core product.

#### Anyscale (Ray)
- **Ray on Kubernetes**: Building KubeRay and K8s integrations for Ray. Go + K8s = perfect match.

---

## 2.6 Team Matching Strategy Summary

| Priority | Company | Team | Match Score | Notes |
|----------|---------|------|-------------|-------|
| 1 | Microsoft | AKS Control Plane / Data Plane | 10/10 | Direct competitor experience. Strongest match. |
| 2 | OpenAI | Infrastructure / Compute Platform | 9/10 | K8s + Go + scale. High-growth. |
| 3 | Anthropic | Infrastructure / Platform | 9/10 | K8s + Go + Python. High-growth. |
| 4 | Meta | Production Engineering -- Compute/Containers | 8/10 | Not K8s but container orchestration. Translates well. |
| 5 | Uber | Compute Platform / K8s Platform | 9/10 | Active K8s migration. Direct K8s expertise valued. |
| 6 | CoreWeave | Kubernetes Infrastructure | 10/10 | K8s-native cloud. Perfect technical match. |
| 7 | Google Cloud | GKE Team | 10/10 | Direct competitor. |
| 8 | Databricks | Compute Platform | 8/10 | K8s + Go. Strong match. |

---

# 3. Interview Process by Company

## 3.1 Meta

### Process Overview

| Stage | Details |
|-------|---------|
| **Recruiter Screen** | 30 min. Discuss experience, level expectations, team interests. |
| **Technical Phone Screen** | 45 min. 1-2 coding problems (LeetCode medium). Python or Go is fine. |
| **Onsite (Virtual Loop)** | 4-5 interviews in one day (sometimes split across 2 days). |

### Onsite Breakdown

| Round | Duration | Content | Level Impact |
|-------|----------|---------|------------|
| **Coding 1** | 45 min | 2 algorithmic problems. Medium to Hard. | Same for E5/E6 |
| **Coding 2** | 45 min | 2 algorithmic problems. Medium to Hard. | Same for E5/E6 |
| **System Design** | 45 min | Design a large-scale system. | E5: Design the system. E6: Design + deep dive into trade-offs, capacity planning, failure modes. |
| **Behavioral** | 45 min | 4-6 behavioral questions. Meta-specific signals. | E5: Team-level examples. E6: Org-level examples with clear cross-team impact. |
| **System Design 2 (E6 only)** | 45 min | Second system design OR "architecture" round. Deeper, more open-ended. | E6 only. Demonstrates ability to drive complex technical direction. |

### Leveling: E5 vs E6

| Dimension | E5 (Senior) | E6 (Staff) |
|-----------|-------------|------------|
| **Scope** | Owns a feature or component | Owns a system or technical area |
| **Influence** | Within team, adjacent teams | Across org (50+ engineers) |
| **Ambiguity** | Given a well-defined problem space | Defines the problem space |
| **Coding bar** | Strong Medium, some Hard | Same, but expected to be cleaner/faster |
| **System design bar** | Can design a complete system | Can design a system AND articulate why, influence the team/org |
| **Behavioral bar** | Team-level leadership | Org-level leadership, strategy influence |
| **YoE typical** | 5-10 years | 8-15+ years |

### Timeline
- Recruiter to onsite: 2-4 weeks
- Onsite to decision: 1-2 weeks
- Team matching: 1-4 weeks after passing (Meta does centralized hiring -- you pass the loop, then match to teams)
- Total: 4-10 weeks

### Meta Team Matching Process
Meta uses a **centralized hiring model**. You interview generically (not for a specific team), receive an offer with a level, and THEN match with teams. This means:
- You can talk to multiple teams after passing
- Teams pitch YOU (you have leverage)
- Ask your recruiter to connect you with infrastructure/PE teams specifically
- You can negotiate team placement as part of your offer

---

## 3.2 Uber

### Process Overview

| Stage | Details |
|-------|---------|
| **Recruiter Screen** | 30 min. Background, level expectations, team interests. |
| **Technical Phone Screen** | 60 min. 1-2 coding problems + short system design discussion. |
| **Onsite (Virtual Loop)** | 4-5 interviews over 1-2 days. |

### Onsite Breakdown

| Round | Duration | Content | Level Impact |
|-------|----------|---------|------------|
| **Coding (DSA)** | 45-60 min | 1-2 problems. LeetCode Medium-Hard. | Same for L5/L6 |
| **System Design** | 45-60 min | Design a distributed system. Often domain-relevant (ride matching, pricing, etc.). | L5: Solid design. L6: Design + extended discussion of evolution, organizational impact. |
| **Domain-Specific / Deep Dive** | 45-60 min | For infra roles: deep dive into your domain expertise. Expect K8s, distributed systems, networking questions. | More important at L6. They want to see you're a domain expert. |
| **Behavioral / Culture Fit** | 45-60 min | Uber's cultural values: ownership, customer obsession, bold bets, integrity. | L5: Team-level. L6: Org-level. |
| **Hiring Manager / Bar Raiser** | 45-60 min | Mixed: technical depth + behavioral. The "bar raiser" is an experienced interviewer from outside the hiring team. | Calibration round. Especially important for leveling decisions. |

### Leveling: L5 vs L6

| Dimension | L5b (Senior II) | L6 (Staff) |
|-----------|-----------------|------------|
| **Scope** | Leads large features or small systems | Owns large systems or technical domains |
| **Influence** | Team + adjacent teams | Multiple teams, org-level |
| **Coding bar** | Consistent Medium-Hard | Same, with emphasis on production-quality code |
| **System design bar** | Solid end-to-end design | Design + evolution + org-wide technical strategy |
| **YoE typical** | 5-8 years | 8-14+ years |

### Timeline
- Recruiter to onsite: 2-4 weeks
- Onsite to decision: 1-2 weeks
- Uber does **team-matched hiring** -- you interview with a specific team
- Total: 3-7 weeks

### Uber Team Matching Process
Uber uses a **team-matched hiring model**. You interview for a specific team from the start. This means:
- Research the team before interviewing
- Your system design questions may be domain-relevant
- Build rapport with the hiring manager early
- If one team doesn't work out, your recruiter can redirect you to another team (sometimes without re-interviewing)

---

## 3.3 Microsoft

### Process Overview

| Stage | Details |
|-------|---------|
| **Recruiter Screen** | 30 min. Background, level discussion, team matching. |
| **Technical Phone Screen** | 45-60 min. 1-2 coding problems. Often easier than Meta/Uber. |
| **Onsite (Virtual Loop)** | 4-5 interviews in one day. |

### Onsite Breakdown

| Round | Duration | Content | Level Impact |
|-------|----------|---------|------------|
| **Coding 1** | 45-60 min | 1-2 problems. LeetCode Easy-Medium (sometimes Medium-Hard for senior+). | Same for L63/L65 |
| **Coding 2** | 45-60 min | 1-2 problems. May focus on practical coding (debugging, code review style). | Same for L63/L65 |
| **System Design** | 60 min | Design a large-scale system. Microsoft interviewers often go deep on Azure services. | L63: Design the system. L65: Design + strategy + cross-team architecture. |
| **Behavioral** | 45-60 min | Microsoft values + competencies. Integrated into every round (each interviewer assesses behavior). | L65 has a much higher bar for leadership examples. |
| **"As Appropriate" (AA) Interview** | 45-60 min | With a senior leader (typically a Partner or Director). More strategic/behavioral. Final calibration on level. | THE most important round for leveling. This person has "hire/no-hire" authority. |

### Leveling: L63 vs L64 vs L65

| Dimension | L63 (Senior) | L64 (Senior, higher band) | L65 (Principal/Staff) |
|-----------|--------------|--------------------------|----------------------|
| **Scope** | Component/feature ownership | System ownership | Multi-system / domain ownership |
| **Influence** | Team | Team + adjacent | Org (100+ engineers) |
| **Coding bar** | Solid Medium | Solid Medium-Hard | Medium-Hard + production quality |
| **System design bar** | Complete design | Design + deep trade-offs | Design + organizational strategy |
| **YoE typical** | 5-8 years | 7-10 years | 10-18+ years |

### Timeline
- Recruiter to onsite: 1-3 weeks
- Onsite to decision: 3-7 days (Microsoft is often faster than others)
- Microsoft does **team-matched hiring** for most roles
- Total: 2-5 weeks

### Microsoft Team Matching Process
Microsoft uses **team-matched hiring**. You apply to a specific team/role. However:
- If you don't pass for one team, the recruiter may refer you to another team
- For AKS specifically, ask to talk to the AKS engineering manager early
- Microsoft has an internal transfer culture -- joining a related team and transferring to AKS later is viable
- The "AA" interviewer may be from a different team to provide calibration

---

## 3.4 AI Companies (OpenAI, Anthropic)

### OpenAI

| Stage | Details |
|-------|---------|
| **Recruiter Screen** | 30 min |
| **Technical Screen** | 60 min. Coding + system design. May include infra-specific questions. |
| **Onsite** | 4-6 rounds over 1-2 days |
| **Rounds** | Coding (1-2), System Design (1-2), Behavioral (1), Technical Deep Dive / Domain (1) |
| **Timeline** | 3-8 weeks total. Can move fast if they're eager. |
| **Leveling** | Uses internal levels. Roughly maps to: L4 = Senior, L5 = Staff. Compensation is highly equity-heavy. |

**OpenAI-specific notes:**
- System design questions often involve ML infrastructure: "Design a training pipeline" or "Design inference serving infrastructure"
- They value hands-on engineers who can operate their own systems
- Culture fit is important: they want people who are mission-driven (AI safety + capability)
- Coding bar is high, similar to Meta

### Anthropic

| Stage | Details |
|-------|---------|
| **Recruiter Screen** | 30 min |
| **Technical Screen** | 60 min. Often a practical coding exercise or take-home (they've experimented with both). |
| **Onsite** | 4-5 rounds |
| **Rounds** | Coding (1-2), System Design (1), Behavioral / Values (1), Technical Discussion / Domain (1) |
| **Timeline** | 3-6 weeks total. |
| **Leveling** | Internal leveling system. Infrastructure roles have Senior and Staff+ levels. |

**Anthropic-specific notes:**
- Strong emphasis on safety-consciousness and thoughtfulness
- Technical deep dive will probe your understanding of infrastructure failure modes and their implications
- They care about "careful engineering" -- reliability, correctness, security
- Python and Go are both used extensively in their infrastructure
- Smaller company, so the interview experience can be more personalized/variable

---

## 3.5 Company Comparison Summary

| Factor | Meta | Uber | Microsoft | OpenAI | Anthropic |
|--------|------|------|-----------|--------|-----------|
| **Coding Difficulty** | High (LC Med-Hard) | High (LC Med-Hard) | Medium (LC Easy-Med+) | High | Medium-High |
| **System Design Weight** | Very High | Very High | High | Very High | High |
| **Behavioral Weight** | High (dedicated round) | High (dedicated + bar raiser) | High (integrated) | Medium-High | Medium-High |
| **Domain Expertise Value** | Medium | High | Very High (for AKS) | High | High |
| **Team Matching** | After passing (centralized) | Before interview | Before interview | Before/during | Before/during |
| **Speed of Process** | Medium (4-10 wk) | Medium (3-7 wk) | Fast (2-5 wk) | Variable (3-8 wk) | Fast (3-6 wk) |
| **Negotiation Leverage** | High (compete offers) | Medium-High | Medium | High (hot market) | High (hot market) |

---

# 4. Preparation Timeline

## 4.1 Assessment: Where Are You Starting?

Before starting, honestly assess your current level:

| Skill | Rusty (Need 6+ weeks) | Moderate (Need 3-4 weeks) | Strong (Need 1-2 weeks of polish) |
|-------|----------------------|--------------------------|----------------------------------|
| **Coding (DSA)** | Can't solve LC Mediums consistently | Solve Mediums in 25-35 min, struggle with Hards | Solve Mediums in 15-25 min, can attempt Hards |
| **System Design** | Haven't designed systems outside your domain | Can design systems you've worked on, struggle with new domains | Can design novel systems with clear trade-off analysis |
| **Behavioral** | Haven't prepared stories, ramble in answers | Have some stories but not well-structured | Have a story bank, deliver in STAR format under 3 min |
| **Domain Knowledge** | Only know your specific area of K8s | Broad K8s knowledge, some gaps | Deep and broad K8s + cloud infrastructure knowledge |

---

## 4.2 The 8-Week Plan (Comprehensive)

### Phase 1: Foundation (Weeks 1-2) -- "Build the Base"

**Daily time commitment: 3-4 hours**

#### Week 1: Assessment and Coding Restart

| Day | Morning (1.5 hr) | Evening (1.5 hr) | Notes |
|-----|-------------------|-------------------|-------|
| Mon | Solve 3 LC Easy (arrays, strings, hash maps) | Review Big-O, common patterns (two pointer, sliding window) | Warm up. Don't time yourself yet. |
| Tue | Solve 3 LC Easy-Medium (linked lists, stacks, queues) | Review binary search, sorting algorithms | |
| Wed | Solve 2 LC Medium (trees, BFS/DFS) | Study: Binary trees, tree traversal patterns | |
| Thu | Solve 2 LC Medium (graphs, DFS/BFS) | Study: Graph representations, topological sort | |
| Fri | Solve 2 LC Medium (dynamic programming intro) | Study: DP patterns (1D DP, knapsack basics) | DP is the hardest category. Start early. |
| Sat | Mock interview: solve 2 problems in 45 min | Write first 3 behavioral stories (STAR format) | Time yourself. Simulate interview pressure. |
| Sun | Review all problems from the week. Identify weak patterns. | Read: "Designing Data-Intensive Applications" Ch. 1-2 | Spaced repetition of solutions. |

**Week 1 targets: 15-18 problems solved. 3 behavioral stories drafted.**

#### Week 2: Pattern Recognition and System Design Basics

| Day | Morning (1.5 hr) | Evening (1.5-2 hr) | Notes |
|-----|-------------------|---------------------|-------|
| Mon | 2 LC Medium (sliding window, two pointer) | System Design study: Scalability basics, load balancing | |
| Tue | 2 LC Medium (binary search variations) | System Design study: Database choices, caching | |
| Wed | 2 LC Medium (heap/priority queue, intervals) | System Design study: Message queues, async processing | |
| Thu | 2 LC Medium (backtracking, recursion) | System Design: Practice designing URL shortener or rate limiter | |
| Fri | 2 LC Medium (DP: 2D, string DP) | System Design study: Consistent hashing, CAP theorem | |
| Sat | Mock: 2 coding problems (45 min) | Write 3 more behavioral stories | |
| Sun | Review week's problems | DDIA Ch. 3-5 | |

**Week 2 targets: 12-14 problems solved. 6 behavioral stories drafted. System design fundamentals reviewed.**

---

### Phase 2: Intensification (Weeks 3-5) -- "Build Depth"

**Daily time commitment: 3-5 hours**

#### Week 3: Coding Depth + System Design Practice

| Day | Coding (1.5-2 hr) | System Design / Behavioral (1.5-2 hr) |
|-----|--------------------|-----------------------------------------|
| Mon | 2 LC Medium-Hard (graphs: Dijkstra, union-find) | Design: Distributed key-value store |
| Tue | 2 LC Medium (trie, string algorithms) | Design: Chat system (WhatsApp-like) |
| Wed | 2 LC Medium-Hard (DP: LCS, edit distance) | Behavioral: Practice 3 stories with a friend/timer |
| Thu | 2 LC Hard (from blind75/neetcode list) | Design: Notification system |
| Fri | 2 LC Medium (math, bit manipulation) | Design: Content delivery network |
| Sat | **Mock interview (full)**: 1 coding + 1 system design | Review + revise behavioral stories |
| Sun | Review weak areas from mock | DDIA Ch. 6-9 |

#### Week 4: Company-Specific Prep + Advanced System Design

| Day | Coding (1.5 hr) | System Design / Behavioral (2 hr) |
|-----|------------------|------------------------------------|
| Mon | 2 problems from Meta tagged list on LC | Design: Container orchestration system (K8s-like) -- use your domain expertise |
| Tue | 2 problems from Uber tagged list on LC | Design: Global load balancer / traffic management |
| Wed | 2 problems from Microsoft tagged list on LC | Design: Distributed logging and monitoring system |
| Thu | 2 problems (focus on weakest pattern) | Behavioral: Practice with mock interviewer (friend, paid service, or Pramp) |
| Fri | 2 problems (focus on 2nd weakest pattern) | Design: ML training platform (for AI company interviews) |
| Sat | **Mock interview** with friend or service | Design: API rate limiter at scale |
| Sun | Review + categorize all solved problems | Refine all 8-10 behavioral stories |

#### Week 5: Advanced Problems + Mock Interviews

| Day | Coding (1.5 hr) | Other (2 hr) |
|-----|------------------|--------------|
| Mon | 1 LC Hard + review solution approaches | System Design: Design a managed Kubernetes service (meta -- you know this) |
| Tue | 2 LC Medium-Hard (contest-style: timed 30 min each) | Behavioral mock interview (45 min) |
| Wed | 1 LC Hard + 1 Medium (mix of patterns) | System Design: Design Uber's ride matching |
| Thu | 2 problems from weak categories | **Full mock interview**: coding + SD + behavioral |
| Fri | Contest-style: 3 Mediums in 60 min | Research target companies/teams. Prepare questions to ask. |
| Sat | **Full mock interview** | Review and revise everything |
| Sun | Light review. Rest. | Light review. Rest. |

---

### Phase 3: Polish and Perform (Weeks 6-8) -- "Sharpen the Blade"

**Daily time commitment: 2-4 hours**

#### Week 6: Simulation and Refinement

| Focus | Activity |
|-------|----------|
| Coding | 1-2 problems/day. Focus on speed and communication. Practice talking through your approach out loud. |
| System Design | 2 full practice sessions this week. Each should be 45 min, simulating the real interview. Record yourself if possible. |
| Behavioral | Run through all 8-12 stories. Ensure each is under 3 min. Have a friend score you on STAR clarity. |
| Company Research | Deep dive on each target company's recent engineering blog posts, tech talks, and product launches. |

#### Week 7: Interview Week (if scheduling allows)

- Schedule interviews strategically:
  - **First**: Company you care LEAST about (warm-up)
  - **Middle**: Second-choice company
  - **Last**: Top-choice company (you'll be sharpest)
- Space interviews 2-3 days apart if possible
- Day before each interview: light review only. No new problems. Rest well.

#### Week 8: Remaining Interviews + Negotiation Prep

- Continue interviewing
- Start preparing for negotiation:
  - Research compensation ranges on levels.fyi
  - Understand equity structures (RSU vesting schedules differ by company)
  - Plan your negotiation strategy: compete offers against each other

---

## 4.3 The 4-Week Accelerated Plan

If you only have 4 weeks, compress as follows:

| Week | Coding | System Design | Behavioral |
|------|--------|---------------|------------|
| 1 | 3 problems/day, focus on top patterns (arrays, strings, trees, graphs, DP basics) | Study fundamentals (1 hr/day) | Draft 6 stories |
| 2 | 2-3 problems/day, company-tagged problems | Practice 1 design/day (30-45 min each) | Polish stories, 1 mock |
| 3 | 2 problems/day + 2 mock coding interviews | 2 mock design interviews | 1 behavioral mock |
| 4 | 1 problem/day (maintenance). Focus on weak areas. | Light review before each interview | Light review before each interview |

---

## 4.4 Daily Structure (Recommended)

### Option A: Morning Person (3-4 hours before work)

```
5:30 AM - 6:00 AM: Coffee + review yesterday's problems (spaced repetition)
6:00 AM - 7:30 AM: Solve 2 new coding problems
7:30 AM - 8:30 AM: System design study or behavioral prep (alternate days)
8:30 AM - 9:00 AM: Log progress in tracking app, plan tomorrow
```

### Option B: Evening Person (3-4 hours after work)

```
7:00 PM - 7:30 PM: Review morning flashcards (spaced repetition)
7:30 PM - 9:00 PM: Solve 2 new coding problems
9:00 PM - 10:00 PM: System design study or behavioral prep (alternate days)
10:00 PM - 10:15 PM: Log progress, plan tomorrow
```

### Option C: Split Day (shorter but more sustainable)

```
Morning (1.5 hr): 1-2 coding problems
Lunch (30 min): Review flashcards or read 1 system design concept
Evening (1.5 hr): System design practice OR behavioral prep
```

---

## 4.5 Problems Per Day by Phase

| Phase | Problems/Day | Types | Time per Problem |
|-------|-------------|-------|------------------|
| Week 1-2 | 2-3 | Easy to Medium | 30-40 min (with learning) |
| Week 3-5 | 2-3 | Medium to Hard | 25-35 min (building speed) |
| Week 6-8 | 1-2 | Medium-Hard (maintenance) | 20-30 min (interview speed) |

**Total problems over 8 weeks: ~120-150 unique problems**

**Recommended problem lists:**
- **Blind 75** (75 problems): Essential patterns. Do all of these.
- **Neetcode 150** (150 problems): Extended list. Do as many as time allows.
- **Company-tagged problems** on LeetCode Premium: Do 10-20 per target company.
- **Sean Prashad's LeetCode Patterns**: Organized by pattern, excellent for systematic practice.

---

## 4.6 When to Focus on What

| Time Left | Coding : System Design : Behavioral |
|-----------|--------------------------------------|
| 8 weeks out | 60% : 25% : 15% |
| 6 weeks out | 50% : 30% : 20% |
| 4 weeks out | 40% : 35% : 25% |
| 2 weeks out | 30% : 35% : 35% |
| 1 week out | 20% : 30% : 50% |
| Day before | 0% : 10% : 90% (review stories, rest) |

**Rationale:** Coding takes the longest to build but plateaus. System design benefits from accumulation. Behavioral is the easiest to improve quickly but needs freshness. Behavioral answers degrade if over-rehearsed too early.

---

# 5. Streamlit App Ideas for Interview Prep Tracking

## 5.1 Core Features

### Feature 1: Problem Tracker with Spaced Repetition

**What it does:** Track every coding problem you solve, categorize by pattern, and schedule reviews using spaced repetition (SM-2 algorithm or simpler Leitner system).

**UI Design:**

```
+--------------------------------------------------+
|  PROBLEM TRACKER                    [+ Add Problem]|
+--------------------------------------------------+
| Filter: [All Patterns v] [All Difficulty v] [Due] |
+--------------------------------------------------+
| Problem       | Pattern      | Diff | Last  | Next |
|               |              |      | Seen  | Due  |
+--------------------------------------------------+
| Two Sum       | Hash Map     | Easy | 2d ago| Today|
| LRU Cache     | Design+Hash  | Med  | 5d ago| Today|
| Merge K Lists | Heap         | Hard | 1d ago| +3d  |
+--------------------------------------------------+
| [Review Due Problems (3)]                          |
+--------------------------------------------------+
```

**Implementation notes:**
- Use `st.dataframe()` with editable columns or `st.data_editor()`
- Store data in a local SQLite database or JSON file
- Spaced repetition: track `ease_factor`, `interval`, `next_review_date` per problem
- Color-code rows: red = overdue, yellow = due today, green = not due yet

### Feature 2: Progress Dashboard

**What it does:** Visual overview of your preparation progress across all three areas.

**UI Design:**

```
+--------------------------------------------------+
|  PREP DASHBOARD           Week 3 of 8             |
+--------------------------------------------------+
| CODING          SYSTEM DESIGN     BEHAVIORAL      |
| [====60%===]    [===45%====]     [==35%===]       |
| 72/120 probs    9/20 designs     7/12 stories     |
+--------------------------------------------------+
| THIS WEEK                                          |
| Mon: [x]2 probs [x]1 SD  [ ]behavioral           |
| Tue: [x]2 probs [ ]       [x]story practice       |
| Wed: [ ]        [ ]       [ ]                      |
+--------------------------------------------------+
| PATTERN COVERAGE                                   |
| Arrays/Strings  [========90%]  18/20              |
| Trees/Graphs    [=====60%]     12/20              |
| DP              [===35%]       7/20               |
| ...                                                |
+--------------------------------------------------+
```

**Implementation notes:**
- Use `st.progress()`, `st.metric()`, and `st.columns()` for layout
- Weekly calendar view with `st.checkbox()` for daily tasks
- Pattern coverage as horizontal bar chart using `st.bar_chart()` or Plotly

### Feature 3: Behavioral Story Bank

**What it does:** Structured storage and practice for behavioral stories.

**UI Design:**

```
+--------------------------------------------------+
|  STORY BANK                        [+ Add Story]  |
+--------------------------------------------------+
| Story: "EKS Control Plane Migration"               |
| Tags: [leadership] [cross-team] [technical-decision]|
+--------------------------------------------------+
| Situation:                                         |
| [Text area with your situation...]                 |
|                                                    |
| Task:                                              |
| [Text area...]                                     |
|                                                    |
| Action:                                            |
| [Text area...]                                     |
|                                                    |
| Result:                                            |
| [Text area with metrics...]                        |
+--------------------------------------------------+
| Covers questions: Q1, Q7, Q13, Q19                |
| Last practiced: 2 days ago                         |
| Confidence: [===========85%]                       |
| [Practice Now] [Edit]                              |
+--------------------------------------------------+
```

**Implementation notes:**
- Each story has: title, STAR components, tags, mapped questions, confidence rating, last practiced date
- "Practice Now" button shows the story title and a timer (3 min), then reveals your notes after
- Map stories to the question categories from Section 1
- Highlight coverage gaps: "You have no story covering 'mentoring'"

### Feature 4: System Design Notebook

**What it does:** Structured notes for system design topics with key concepts, common designs, and practice log.

```
+--------------------------------------------------+
|  SYSTEM DESIGN NOTEBOOK                            |
+--------------------------------------------------+
| Topics:                                            |
| [x] URL Shortener        Practiced: 2x            |
| [x] Chat System          Practiced: 1x            |
| [ ] Rate Limiter          Practiced: 0x            |
| [ ] K8s-like Orchestrator Practiced: 0x            |
+--------------------------------------------------+
| Selected: Chat System                              |
|                                                    |
| Key Components:                                    |
| - WebSocket servers for real-time                  |
| - Message queue (Kafka) for async delivery         |
| - ...                                              |
|                                                    |
| Trade-offs to discuss:                             |
| - Push vs Pull for message delivery                |
| - SQL vs NoSQL for message storage                 |
| - ...                                              |
|                                                    |
| My Notes:                                          |
| [Rich text editor area]                            |
+--------------------------------------------------+
```

### Feature 5: Interview Calendar and Company Tracker

```
+--------------------------------------------------+
|  INTERVIEW TRACKER                                 |
+--------------------------------------------------+
| Company    | Stage       | Date    | Status       |
+--------------------------------------------------+
| Meta       | Onsite      | Mar 15  | Scheduled    |
| Uber       | Phone Screen| Mar 8   | Completed    |
| Microsoft  | Recruiter   | Mar 3   | Completed    |
| OpenAI     | Applied     | Feb 28  | Waiting      |
+--------------------------------------------------+
| UPCOMING:                                          |
| Mar 8 - Uber Phone Screen                         |
|   Prep: Review Uber-tagged LC problems             |
|   Focus: Coding + brief SD discussion              |
+--------------------------------------------------+
```

---

## 5.2 Technical Implementation Recommendations

### Data Storage

```python
# Use SQLite for simplicity and portability
import sqlite3
import json
from datetime import datetime, timedelta

# Tables:
# - problems (id, title, url, pattern, difficulty, notes, ease_factor,
#             interval, next_review, times_reviewed, last_reviewed)
# - stories (id, title, situation, task, action, result, tags,
#            mapped_questions, confidence, last_practiced)
# - designs (id, topic, components, tradeoffs, notes, times_practiced)
# - interviews (id, company, team, stage, date, status, notes)
# - daily_log (id, date, coding_count, sd_minutes, behavioral_minutes, notes)
```

### App Structure

```
interview-prep/
    app.py                  # Main Streamlit app (entry point)
    pages/
        1_Problem_Tracker.py
        2_Story_Bank.py
        3_System_Design.py
        4_Dashboard.py
        5_Interview_Calendar.py
    db/
        database.py         # SQLite helper functions
        init_db.py          # Schema initialization
    data/
        prep.db             # SQLite database (auto-created)
        problems_seed.json  # Optional: seed data with Blind75 problems
    utils/
        spaced_rep.py       # Spaced repetition algorithm
        charts.py           # Chart generation helpers
```

### Key Streamlit Patterns

```python
# Sidebar navigation (Streamlit handles this automatically with pages/)
# In app.py:
import streamlit as st

st.set_page_config(page_title="Interview Prep Tracker", layout="wide")
st.title("Interview Prep HQ")

# Session state for persistence within a session
if 'current_story' not in st.session_state:
    st.session_state.current_story = None

# Data editor for problem tracking (Streamlit 1.23+)
edited_df = st.data_editor(
    problems_df,
    column_config={
        "difficulty": st.column_config.SelectboxColumn(
            options=["Easy", "Medium", "Hard"]
        ),
        "pattern": st.column_config.SelectboxColumn(
            options=["Array", "HashMap", "Tree", "Graph", "DP", ...]
        ),
        "next_review": st.column_config.DateColumn(),
    },
    num_rows="dynamic",  # Allow adding rows
)

# Progress metrics
col1, col2, col3 = st.columns(3)
col1.metric("Problems Solved", "72/120", "+5 this week")
col2.metric("Designs Practiced", "9/20", "+2 this week")
col3.metric("Stories Ready", "7/12", "+1 this week")

# Timer for practice
if st.button("Start 3-min Practice Timer"):
    with st.empty():
        for remaining in range(180, 0, -1):
            mins, secs = divmod(remaining, 60)
            st.markdown(f"## {mins:02d}:{secs:02d}")
            time.sleep(1)
        st.markdown("## Time's up!")
```

### Spaced Repetition Algorithm (SM-2 Simplified)

```python
def update_review_schedule(problem, quality: int):
    """
    quality: 0-5 (0=blackout, 5=perfect recall)
    Returns updated ease_factor, interval, next_review_date
    """
    if quality < 3:
        # Reset: problem needs re-learning
        problem.interval = 1
        problem.repetitions = 0
    else:
        if problem.repetitions == 0:
            problem.interval = 1
        elif problem.repetitions == 1:
            problem.interval = 3
        else:
            problem.interval = int(problem.interval * problem.ease_factor)
        problem.repetitions += 1

    # Update ease factor
    problem.ease_factor = max(1.3,
        problem.ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    )
    problem.next_review = datetime.now() + timedelta(days=problem.interval)
    return problem
```

---

## 5.3 Simple but Effective UI Patterns

1. **Traffic Light Status**: Use colored circles (red/yellow/green) for at-a-glance status on everything -- problem confidence, story readiness, interview stage.

2. **Daily Streak Counter**: Show a GitHub-style contribution graph for prep consistency. `st.markdown()` with custom HTML/CSS or use `streamlit-calendar`.

3. **Today's Focus**: A single top-level card that says: "Today: Solve 2 DP problems, review 3 spaced-rep problems, practice 'EKS Migration' story." Auto-generated from your schedule and spaced repetition queue.

4. **Quick Add**: Floating action button or persistent sidebar form to quickly log a solved problem without navigating away from your current page.

5. **Weekly Report**: Auto-generated summary every Sunday: problems solved, patterns covered, mock interview scores, areas to focus on next week.

---

# Appendix A: Key Resources

## Coding
- **LeetCode Premium** ($35/month): Company-tagged problems, frequency data
- **Neetcode.io**: Free video explanations organized by pattern
- **Blind 75 list**: The essential 75 problems -- do all of them
- **AlgoExpert** (optional): Good video explanations, curated list

## System Design
- **"Designing Data-Intensive Applications" by Martin Kleppmann**: The bible. Read at minimum Ch. 1-9.
- **"System Design Interview" by Alex Xu (Vol 1 & 2)**: Practical, interview-focused
- **ByteByteGo** (Alex Xu's blog/newsletter): Excellent diagrams and explanations
- **Donnemartin's system-design-primer** (GitHub): Free, comprehensive
- **Jordan Has No Life** (YouTube): Excellent system design walkthrough videos

## Behavioral
- **"The Staff Engineer's Path" by Tanya Reilly**: Essential reading for Staff-level behavioral prep
- **"An Elegant Puzzle" by Will Larson**: Engineering leadership perspective
- **StaffEng.com**: Collection of Staff+ engineer stories and advice
- **Exponent** (tryexponent.com): Mock behavioral interview practice with AI

## Kubernetes / Infrastructure (to refresh domain knowledge)
- **"Kubernetes in Action" by Marko Luksa (2nd ed)**: Deep dive reference
- **Kubernetes source code** (k8s.io): You should be able to discuss controller patterns, API machinery, scheduler framework
- **AWS EKS Best Practices Guide** (GitHub): Review to ensure your knowledge is current
- **CNCF Landscape**: Know the major projects and where they fit

## Mock Interviews
- **Pramp**: Free peer mock interviews
- **Interviewing.io**: Mock interviews with engineers from top companies ($$$)
- **Exponent**: AI-powered mock interviews
- **Peer practice**: Find a friend also interviewing. Trade mock interviews weekly.

---

# Appendix B: EKS Experience Translation Guide

Use this table to translate your EKS experience into language each company will understand:

| Your EKS Experience | Meta Translation | Uber Translation | Microsoft Translation | AI Company Translation |
|---------------------|-----------------|-------------------|----------------------|----------------------|
| EKS Control Plane (API server, etcd, controllers) | "Managed distributed control plane at scale serving 100K+ clusters" | "Kubernetes control plane expertise for multi-tenant orchestration" | "Deep managed K8s control plane experience, directly applicable to AKS" | "Control plane for large-scale compute orchestration" |
| EKS Data Plane (kubelet, node management, networking) | "Node fleet management and container runtime at massive scale" | "Container lifecycle and compute abstraction layer" | "Node provisioning and management for managed K8s" | "Compute node management for GPU/CPU workloads" |
| VPC CNI / Networking | "Software-defined networking for container orchestration" | "Container networking and service mesh infrastructure" | "Cloud-integrated container networking (Azure CNI equivalent)" | "Network infrastructure for distributed training/serving" |
| Go development | "Go -- primary language for infrastructure services" | "Go -- infrastructure and platform development" | "Go -- cloud infrastructure and K8s controller development" | "Go -- infrastructure services and operators" |
| Python development | "Python -- tooling, automation, data analysis" | "Python -- platform tooling and ML infrastructure" | "Python -- automation, testing, ML integration" | "Python -- ML platform tooling, research infrastructure" |
| On-call / incident response | "Production engineering for always-on managed service" | "Operational excellence for real-time systems" | "Live site incident management for cloud service" | "Reliability engineering for AI serving infrastructure" |
| K8s version upgrades at scale | "Zero-downtime platform migrations across 100K+ clusters" | "Large-scale platform upgrades without customer impact" | "Managed K8s upgrade orchestration" | "Infrastructure platform upgrades for ML workloads" |

---

# Appendix C: Questions to Ask Interviewers

Prepare 3-5 thoughtful questions for each interview. These signal your seniority:

### For Any Company
1. "What does the on-call rotation look like for this team? What's a recent interesting incident?"
2. "How does the team make technical decisions? Is there a design review or RFC process?"
3. "What's the biggest technical challenge the team is facing in the next 6-12 months?"
4. "How is individual impact measured for senior/staff engineers on this team?"
5. "What does the path from Senior to Staff (or Staff to Principal) look like here?"

### For Meta Specifically
6. "How does this team interact with the container orchestration (Twine) team?"
7. "Is there adoption of Kubernetes for any workloads at Meta, or is it all internal systems?"
8. "How does the PE promotion process work, and how does it differ from SWE?"

### For Uber Specifically
9. "Where is Uber in the Kubernetes migration journey? What are the biggest remaining challenges?"
10. "How does compute platform interact with the ML platform teams?"

### For Microsoft / AKS Specifically
11. "How does AKS differentiate from EKS and GKE in the next year? What's the competitive strategy?"
12. "How much of the AKS control plane is upstream K8s vs. custom Microsoft code?"
13. "How does the AKS team collaborate with the Azure Compute (VMSS) team?"

### For AI Companies
14. "What does the GPU cluster management stack look like? How much is Kubernetes vs. custom?"
15. "How do you handle the tension between researcher velocity and infrastructure reliability?"
16. "What's the ratio of build-internally vs. use open-source for infrastructure components?"

---

*Last updated: February 2025. Interview processes evolve; verify specifics with your recruiter.*
*Good luck. You have a rare and valuable skill set. Prepare thoroughly and negotiate confidently.*
