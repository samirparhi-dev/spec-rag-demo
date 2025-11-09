# Spec-driven MLSecOps Demo (Infra as Spec)

Purpose
- Demonstrate "Infrastructure as Spec": use OpenAPI, K8s manifests, Cilium/Istio policies, Hubble flows and logs as first-class spec inputs to an AI-driven MLSecOps demo.
- Show retrieval-augmented diagnostic workflows (RAG) with MCP servers, K8sGPT analysis, automatic recommendations and safe auto-heal examples.

High-level architecture
- Open WebUI (RAG frontend) ←→ LLM backend (Ollama/local)  
- Vector DB: Qdrant/Weaviate for embeddings  
- MCP Servers: GitLab, Kubernetes, Prometheus, Fetch → provide context to the assistant  
- Observability: Prometheus + Hubble (Cilium) + logs → fed into RAG + K8sGPT  
- Auto-heal: GitLab CI jobs + k8sgpt-driven remediation steps (opt-in/manual approval)

What's included
- demo_specs/: sample OpenAPI, K8s manifests, Cilium/Istio policy snippets and logs
- waviate/weaviate_chunking_demo.ipynb: example notebook for chunking/upload to Weaviate
- setup_demo.sh: idempotent script to prepare a local demo environment (Docker Compose + initial secrets + zip artifact)
- can you validate if this architecture is feasible.md: short validation summary

Quickstart (local demo)
1. Review demo_specs/ to understand the artifacts (openapi, k8s, policies, logs).
2. Make the script executable:
   chmod +x setup_demo.sh
3. Run setup (this will validate prerequisites, write a docker-compose.yml, start containers and create demo_specs.zip):
   ./setup_demo.sh
4. Open the Open WebUI UI at: http://localhost:3000 and upload demo_specs/ into Documents → configure embedding model nomic-embed-text or local embedder.
5. Run the Weaviate chunking notebook (if you prefer Weaviate) or use upload scripts to ingest artifacts.

Notes & safety
- No secrets are committed. The script will create a temporary JWT_SECRET_KEY in the cluster if kubectl is configured.
- The auto-heal jobs in CI are examples; in real environments require RBAC and human approval.
- See demo_specs/README.md for artifact details.

Support
- If Docker or kubectl are not present, the setup script will exit with guidance to install them.
