```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│              AI-DRIVEN MLSECOPS PLATFORM WITH AUTO-HEALING                          │
│                     (GitLab CI/CD + Cilium + Istio + K8sGPT)                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: SPEC & CODE REPOSITORY (GitLab)                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  OpenAPI     │  │  K8s YAML    │  │ Cilium CNP   │  │ Istio Policies│          │
│  │    Specs     │  │ Deployments  │  │   Policies   │  │  AuthZ Rules  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: GITLAB CI/CD PIPELINE (.gitlab-ci.yml)                                   │
│                                                                                     │
│  ① Build → ② SAST/DAST → ③ Container Scan → ④ Deploy → ⑤ Policy Validation       │
│                                                                                     │
│  Security Gates:                                                                   │
│  • Trivy scan (image vulnerabilities)                                              │
│  • Cilium policy dry-run (network)                                                 │
│  • Istio policy validation (mTLS)                                                  │
│  • K8sGPT pre-flight check                                                         │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: KUBERNETES CLUSTER (AKS/EKS with Cilium CNI)                            │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │  NETWORK LAYER: Cilium + Hubble                                            │  │
│  │  • eBPF-based CNI                                                           │  │
│  │  • L3/L4/L7 Network Policies                                                │  │
│  │  • Identity-based security                                                  │  │
│  │  • Hubble flow observability                                                │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │  SERVICE MESH LAYER: Istio                                                  │  │
│  │  • mTLS enforcement                                                          │  │
│  │  • L7 AuthZ policies                                                         │  │
│  │  • Traffic management                                                        │  │
│  │  • Distributed tracing                                                       │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │  APPLICATION PODS                                                            │  │
│  │  • user-service (needs auth)                                                 │  │
│  │  • payment-service (needs auth)                                              │  │
│  │  • frontend (public)                                                         │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: OBSERVABILITY & TELEMETRY                                                │
│                                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Hubble Relay     │  │ Prometheus       │  │ OpenTelemetry    │                │
│  │ (Network flows)  │  │ (Metrics)        │  │ (Traces/Logs)    │                │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘                │
│                                                                                     │
│  Flow Export → Elasticsearch/Loki → RAG Vector DB                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: AI-POWERED ANALYSIS & AUTO-HEALING                                       │
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────┐    │
│  │  K8sGPT OPERATOR (Kubernetes Diagnostics)                                  │    │
│  │  • Scans: Pods, Deployments, Services, NetworkPolicies                     │    │
│  │  • Analyzers: CrashLoopBackOff, ImagePullBackOff, Policy Drops             │    │
│  │  • Auto-fix: Restart pods, scale replicas, patch configs                   │    │
│  └───────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────┐    │
│  │  SPEC-DRIVEN RAG SYSTEM (from previous architecture)                       │    │
│  │  • Query: "Why is payment-service returning 405?"                          │    │
│  │  • Context: OpenAPI spec + Cilium logs + Hubble flows + K8s events        │    │
│  │  • Response: Root cause + remediation steps                                │    │
│  └───────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────┐    │
│  │  GUARDRAILS AI (MLSecOps Security Layer)                                   │    │
│  │  • Input validation: Sanitize user queries                                 │    │
│  │  • Output validation: Prevent sensitive data leaks                         │    │
│  │  • Prompt injection detection                                              │    │
│  │  • PII filtering (tokens, passwords, keys)                                 │    │
│  └───────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 6: PRIORITY ALERTING & SCHEDULED PROMPTS                                    │
│                                                                                     │
│  ┌────────────────────────────────────────────────────────────────────┐           │
│  │  CRITICAL ALERTS (Auto-triggered)                                  │           │
│  │  • CrashLoopBackOff in production namespace                        │           │
│  │  • Cilium policy DROP rate > 10%                                   │           │
│  │  • Istio mTLS failure rate > 5%                                    │           │
│  │  • 405 Method Not Allowed errors > threshold                       │           │
│  │  • Pod CPU/Memory throttling                                       │           │
│  │                                                                     │           │
│  │  Actions:                                                           │           │
│  │  1. K8sGPT analyzes issue                                          │           │
│  │  2. RAG system retrieves relevant specs                            │           │
│  │  3. Generate markdown report                                       │           │
│  │  4. Auto-apply fix OR notify for approval                          │           │
│  └────────────────────────────────────────────────────────────────────┘           │
│                                                                                     │
│  ┌────────────────────────────────────────────────────────────────────┐           │
│  │  SCHEDULED HEALTH CHECKS (Cron/GitLab Pipelines)                  │           │
│  │  • Daily: "Any new CVEs in running containers?"                    │           │
│  │  • Hourly: "Network policy violations in last hour?"               │           │
│  │  • Weekly: "Unused Istio AuthZ policies?"                          │           │
│  │  • On-deploy: "Validate all policies before merge"                │           │
│  └────────────────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 7: MCP SERVER INTEGRATIONS                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  GitLab MCP  │  │  K8s MCP     │  │ Prometheus   │  │  OTEL MCP    │          │
│  │  (CI/CD)     │  │  (Cluster)   │  │  MCP (Metrics)│  │ (Traces)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────────────────────────┘
```
