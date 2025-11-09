# Infrastructure as Spec Demo

## Overview

This repository demonstrates the evolution from **Infrastructure as Code** to **Infrastructure as Spec** using AI-driven MLSecOps (Machine Learning Security Operations). The demo showcases how specifications (OpenAPI, Kubernetes manifests, policies, logs) become first-class inputs to an intelligent system that provides automated diagnostics, remediation, and self-healing capabilities.

## Key Concepts

### Infrastructure as Spec
- **Traditional IaC**: Code defines infrastructure (Terraform, Helm, K8s YAML)
- **Infrastructure as Spec**: Specs drive infrastructure behavior and AI analysis
- **AI Enhancement**: Specs become queryable knowledge for RAG (Retrieval Augmented Generation) systems

### MLSecOps Platform
- **RAG System**: Open WebUI with vector search over infrastructure specs
- **MCP Servers**: Model Context Protocol for live data sources (GitLab, Kubernetes, Prometheus)
- **Auto-Healing**: GitLab CI/CD pipelines with K8sGPT-driven remediation
- **Observability**: Cilium Hubble flows, Istio metrics, and comprehensive logging

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE AS SPEC PLATFORM                   │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  SPEC-DRIVEN RAG SYSTEM                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ OpenAPI     │  │ Kubernetes  │  │ Cilium      │  │ Istio       │  │
│  │ Specs       │  │ Manifests   │  │ Policies    │  │ Policies    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
│                              ↓                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │
│  │ Chunking &  │  │ Embedding   │  │ Vector DB   │                   │
│  │ Processing  │  │ (LM Studio  │  │ (Weaviate)  │                   │
│  │             │  │  models)    │  │             │                   │
│  └─────────────┘  └─────────────┘  └─────────────┘                   │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  AI-POWERED ANALYSIS & AUTO-HEALING                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Open WebUI  │  │ MCP Servers │  │ K8sGPT      │  │ GitLab CI   │  │
│  │ (Frontend)  │  │ (Context)   │  │ (Analysis)  │  │ (Healing)   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  OBSERVABILITY & TELEMETRY                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Cilium      │  │ Istio       │  │ Prometheus  │  │ Logs        │  │
│  │ Hubble      │  │ Envoy       │  │ Metrics     │  │ (JSONL)     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

## Demo Scenarios

### 1. API Security Investigation
**Problem**: Payment service returns 405 Method Not Allowed errors
**Solution**: RAG system retrieves OpenAPI specs, Cilium logs, and Istio policies to identify root cause and suggest fixes

### 2. Pod Health Diagnostics
**Problem**: Payment service in CrashLoopBackOff
**Solution**: K8sGPT analyzes pod logs, events, and specs to diagnose missing JWT secret and auto-heal

### 3. Network Policy Validation
**Problem**: Unexpected traffic drops in Cilium Hubble flows
**Solution**: Cross-reference network policies with actual traffic patterns and recommend adjustments

## Repository Structure

```
spec-rag-demo/
├── demo_specs/              # Sample specs for ingestion
│   ├── openapi/            # API specifications
│   ├── kubernetes/         # K8s manifests
│   ├── policies/           # Cilium/Istio policies
│   ├── logs/               # Sample logs and telemetry
│   ├── scenarios/          # Demo scenarios and prompts
│   ├── scripts/            # Automation scripts
│   ├── terraform/          # Infrastructure as Code
│   ├── gitlab-ci/          # CI/CD pipelines
│   └── monitoring/         # Prometheus configs
├── designs/                # Architecture documentation
├── python-scripts/         # Guardrails and utilities
├── mcp-config/            # MCP server configurations
├── scripts/               # Setup and validation scripts
└── docker-compose.yml     # Demo environment
```

## Quick Start

### Prerequisites
- **Container Runtime**: Podman (recommended) or Docker
- **LM Studio**: Running locally on port 1234 with embedding and chat models loaded
- **kubectl** (optional, for K8s integration)
- **Python 3.11+** (for embedding scripts and utilities)

### Setup Demo Environment

```bash
# Clone repository
git clone https://github.com/yourusername/spec-rag-demo
cd spec-rag-demo

# 1. Start LM Studio locally
# - Download and install LM Studio from https://lmstudio.ai/
# - Load an embedding model (e.g., nomic-embed-text, text-embedding-ada-002)
# - Load a chat model (e.g., llama-3.1-8b, mistral-7b, phi-3)
# - Start the local server on port 1234

# 2. Run setup script (starts containers)
./scripts/setup_demo.sh

# Alternative: Use Podman Compose directly
podman-compose up -d
# or
docker-compose up -d
```

### Access the Demo

1. **Open WebUI**: http://localhost:3000
2. **Create Embeddings**: Run the embedding script to populate Weaviate
   ```bash
   cd demo_specs/scripts
   python create_weaviate_embeddings.py
   ```
3. **Configure Models in LM Studio**: Ensure your embedding and chat models are loaded and server is running on port 1234
4. **Try Queries**:
   - "Which APIs require authentication?"
   - "Why is payment-service returning 405 errors?"
   - "Show me network policy violations"

### Demo Scenarios

Run the included scenarios:

```bash
# Scenario 1: API Security
python demo_specs/scripts/run_scheduled_prompts.py --scenario api-security

# Scenario 2: Pod Diagnostics
python demo_specs/scripts/run_scheduled_prompts.py --scenario pod-health

# Scenario 3: Network Analysis
python demo_specs/scripts/run_scheduled_prompts.py --scenario network-policy
```

## Components

### RAG System (Open WebUI)
- **Frontend**: Web interface for queries and document management
- **Backend**: Local LLM (LM Studio) with vector search
- **Vector DB**: Weaviate for embeddings storage and semantic search
- **Embeddings**: LM Studio models (nomic-embed-text or similar) for semantic search
- **Chunking**: Intelligent text chunking with overlap for optimal retrieval

### MCP Servers
- **GitLab MCP**: CI/CD pipeline context and issues
- **Kubernetes MCP**: Cluster state and pod information
- **Prometheus MCP**: Metrics and alerting data
- **Fetch MCP**: Web scraping for external documentation

### Observability Stack
- **Cilium Hubble**: Network flow observability
- **Istio Envoy**: Service mesh metrics and logs
- **K8sGPT**: AI-powered Kubernetes diagnostics
- **Prometheus**: Metrics collection and alerting

### Auto-Healing
- **GitLab CI/CD**: Automated remediation pipelines
- **K8sGPT Integration**: Intelligent issue detection and fixes
- **Policy Validation**: Continuous compliance checking

## Development

### Adding New Specs
1. Place specifications in `demo_specs/` subdirectories
2. Update `demo_specs/README.md` with descriptions
3. Re-run embedding script to update Weaviate vector database:
   ```bash
   cd demo_specs/scripts
   python create_weaviate_embeddings.py
   ```

### Custom Scenarios
1. Add scenario files to `demo_specs/scenarios/`
2. Update `demo_specs/scripts/scheduled_prompts.yaml`
3. Test with Open WebUI

### Extending MCP Servers
1. Add configurations to `mcp-config/mcp.json`
2. Update Docker Compose services
3. Test integration with Open WebUI

## Security Considerations

- **Guardrails**: Input/output validation prevents prompt injection
- **PII Filtering**: Sensitive data redaction in responses
- **RBAC**: MCP servers respect Kubernetes permissions
- **Audit Logging**: All AI interactions are logged

## Troubleshooting

### Common Issues

**Open WebUI not accessible**
```bash
# Check container status
podman-compose ps
# or
docker-compose ps

# View logs
podman-compose logs open-webui
# or
docker-compose logs open-webui
```

**LM Studio not responding**
```bash
# Check if LM Studio is running on port 1234
curl -s http://localhost:1234/v1/models

# Ensure embedding model is loaded in LM Studio
# Recommended models: nomic-embed-text, text-embedding-ada-002, or any lightweight embedding model
```

**Weaviate connection failed**
```bash
# Check Weaviate health
curl -s http://localhost:8080/v1/meta

# View Weaviate logs
podman-compose logs qdrant
# or
docker-compose logs qdrant
```

**Embedding script fails**
```bash
# Install required Python packages
pip install weaviate-client requests

# Check LM Studio connectivity
python -c "import requests; print(requests.get('http://localhost:1234/v1/models').json())"

# Run embedding script with verbose output
cd demo_specs/scripts
python create_weaviate_embeddings.py
```

### Logs and Debugging
- Setup logs: `logs/setup.log`
- Validation logs: `logs/validate.log`
- Container logs: `podman-compose logs` or `docker-compose logs`
- Embedding script logs: Check terminal output when running `create_weaviate_embeddings.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add specs or scenarios to `demo_specs/`
4. Update documentation
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: See `designs/` directory for detailed architecture docs
