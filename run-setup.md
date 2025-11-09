# Infrastructure as Spec Demo - Complete Setup Guide

## Overview

This guide provides the complete execution order for setting up the Infrastructure as Spec demo environment. The demo showcases how infrastructure specifications become queryable knowledge for AI-driven MLSecOps (Machine Learning Security Operations).

## Architecture Overview

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
│  │ Processing  │  │ (LM Studio) │  │ (Weaviate)  │                   │
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

MCP Servers Available:
• GitLab MCP: CI/CD pipeline context and issues
• Kubernetes MCP: Cluster state and pod information
• Prometheus MCP: Metrics and alerting data
• Fetch MCP: Web scraping for external documentation
```

## RAG Solution Logical Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                        USER QUERY PROCESSING                         │
└──────────────────────────────────────────────────────────────────────┘

1. User Query → Open WebUI (localhost:3000)
       ↓
2. Query Analysis → LM Studio (localhost:1234)
       ↓
3. Parallel Processing:
   ┌─────────────────────────────────┐  ┌─────────────────────────────┐
   │        RAG Retrieval           │  │      MCP Context            │
   │                                 │  │                             │
   │ Query → Semantic Search        │  │ Query → Live Systems        │
   │         ↓                      │  │         ↓                   │
   │ Weaviate Vector Search         │  │ GitLab/K8s/Prometheus APIs  │
   │ (Embedded Infra Specs)         │  │ (Real-time Data)            │
   │         ↓                      │  │         ↓                   │
   │ Relevant Chunks Retrieved      │  │ Current System State        │
   └─────────────────────────────────┘  └─────────────────────────────┘
                     ↓                           ↓
              ┌─────────────────────────────────────┐
              │         CONTEXT AGGREGATION         │
              │                                     │
              │ Combine:                            │
              │ • Embedded spec knowledge           │
              │ • Live system context               │
              │ • Historical patterns               │
              └─────────────────────────────────────┘
                              ↓
              ┌─────────────────────────────────────┐
              │         LLM GENERATION              │
              │                                     │
              │ LM Studio processes enriched        │
              │ context to provide intelligent      │
              │ analysis and recommendations        │
              └─────────────────────────────────────┘
                              ↓
              ┌─────────────────────────────────────┐
              │         RESPONSE DELIVERY           │
              │                                     │
              │ Formatted response with:            │
              │ • Root cause analysis               │
              │ • Remediation steps                 │
              │ • Preventive measures               │
              └─────────────────────────────────────┘
```

## Service Ports & URLs

| Service | External Port | Internal Port | URL | Purpose |
|---------|---------------|---------------|-----|---------|
| **Open WebUI** | 3000 | 8080 | http://localhost:3000 | Web interface for RAG queries |
| **Weaviate** | 8080 | 8080 + 50051 | http://localhost:8080 | Vector database for embeddings |
| **LM Studio** | 1234 | N/A | http://localhost:1234 | Local LLM API for embeddings/chat |
| **K8sGPT** | None | N/A | N/A | Kubernetes diagnostics (internal) |
| **MCP Servers** | N/A | N/A | Config: `mcp-config/mcp.json` | Model Context Protocol servers |

## Prerequisites

### Required Software
- **Container Runtime**: Podman (recommended) or Docker
- **LM Studio**: Local LLM application with MCP support
- **Python 3.11+**: For embedding scripts
- **kubectl**: Optional, for Kubernetes integration
- **Node.js/npm**: For MCP servers (if using external integrations)

### LM Studio Models
Download and load these models in LM Studio:
- **Embedding Model**: `text-embedding-nomic-embed-text-v1.5` (or `text-embedding-nomic-embed-text-v2-moe`)
- **Chat Model**: Any lightweight model like `llama-3.1-8b-instruct`, `mistral-7b-instruct-v0.2`, or `phi-3-mini-4k-instruct`

## Complete Execution Order

### Step 1: LM Studio Setup
```bash
# 1. Download and install LM Studio from https://lmstudio.ai/
# 2. Start LM Studio application
# 3. Load the embedding model: text-embedding-nomic-embed-text-v1.5
# 4. Load a chat model: llama-3.1-8b-instruct (or similar)
# 5. Start the local server (default port 1234)
```

**Verification:**
```bash
curl -s http://localhost:1234/v1/models
# Should return JSON with your loaded models
```

### Step 2: Run Complete Setup Script
```bash
cd /path/to/spec-rag-demo
./scripts/setup_demo.sh
```

**What the setup script does:**
1. ✅ Detects Podman/Docker and installs podman-compose if needed
2. ✅ Starts all containers (Open WebUI, Weaviate, K8sGPT)
3. ✅ Waits for services to be ready on ports 3000, 8080
4. ✅ Checks LM Studio connectivity on port 1234
5. ✅ Creates embeddings for all demo specifications using LM Studio
6. ✅ Sets up Kubernetes resources (if kubectl available)
7. ✅ Configures MCP servers for external integrations
8. ✅ Provides access URLs and next steps

### Step 3: Access the Demo
Once setup completes, access these URLs:

- **🎯 Open WebUI**: http://localhost:3000
  - Main interface for querying infrastructure specs
  - RAG-powered responses using embedded knowledge

- **🔍 Weaviate**: http://localhost:8080/v1/meta
  - Vector database health check
  - REST API for direct queries

- **🤖 LM Studio**: http://localhost:1234/v1/models
  - Local LLM API status
  - Model information and capabilities

## Demo Scenarios & Test Queries

### Example Queries to Try
Once everything is running, try these queries in Open WebUI:

1. **API Security**: "Which APIs require authentication?"
2. **Error Diagnosis**: "Why is payment-service returning 405 errors?"
3. **Network Analysis**: "Show me network policy violations"
4. **Configuration**: "What are the payment service configurations?"
5. **Kubernetes**: "Show me pod resource limits"
6. **Policies**: "Which services have authorization policies?"

### Demo Scenarios
The setup includes pre-configured scenarios in `demo_specs/scenarios/`:
- API Security Investigation
- Pod Health Diagnostics
- Network Policy Validation

## Manual Setup (Alternative)

If the automated script fails, follow these manual steps:

```bash
# 1. Start containers
podman-compose up -d

# 2. Wait for services
curl http://localhost:3000/health     # Open WebUI
curl http://localhost:8080/v1/meta    # Weaviate
curl http://localhost:1234/v1/models  # LM Studio

# 3. Create embeddings
cd demo_specs/scripts
python3 create_weaviate_embeddings.py

# 4. Access demo
open http://localhost:3000
```

## Troubleshooting

### Common Issues

**Containers not starting:**
```bash
# Check container status
podman-compose ps

# View logs
podman-compose logs

# Restart services
podman-compose restart
```

**LM Studio not responding:**
```bash
# Check if running
curl http://localhost:1234/v1/models

# Restart LM Studio and ensure server is started
```

**Embedding script fails:**
```bash
# Install dependencies
pip3 install requests weaviate-client

# Check Python version
python3 --version

# Run with verbose output
cd demo_specs/scripts
python3 create_weaviate_embeddings.py
```

**Port conflicts:**
```bash
# Check what's using ports
lsof -i :3000
lsof -i :8080
lsof -i :1234

# Stop conflicting services or change ports in docker-compose.yml
```

### Logs and Debugging
- **Setup logs**: `logs/setup.log`
- **Container logs**: `podman-compose logs` or `docker-compose logs`
- **Embedding logs**: Terminal output when running embedding script

## Stopping the Demo

```bash
# Stop all services
podman-compose down

# Remove volumes (WARNING: deletes data)
podman-compose down -v
```

## Next Steps

1. **Explore the specs**: Browse `demo_specs/` directory
2. **Customize queries**: Try different questions about your infrastructure
3. **Add new specs**: Place new files in `demo_specs/` subdirectories
4. **Re-embed**: Run embedding script after adding new specs
5. **Extend scenarios**: Add new demo scenarios in `demo_specs/scenarios/`

## Support

- **Documentation**: See `README.md` for detailed architecture
- **Logs**: Check `logs/` directory for troubleshooting
- **Demo specs**: Explore `demo_specs/` for sample data

---

**🎉 Happy exploring your Infrastructure as Spec demo!**

The system is now ready to demonstrate how specifications become intelligent, queryable knowledge for AI-driven infrastructure operations.