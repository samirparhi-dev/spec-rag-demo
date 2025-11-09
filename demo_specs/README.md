# Demo Specifications Directory

This directory contains all the infrastructure specifications that are processed and embedded into the vector database for the Infrastructure as Spec demo.

## Directory Structure

```
demo_specs/
├── openapi/            # API specifications
│   ├── auth_service.yaml
│   ├── payment_api.json
│   └── user_service.yaml
├── kubernetes/         # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── policies/           # Network and security policies
│   ├── payment-authz-policy.yaml
│   └── payment-service-netpol.yaml
├── logs/               # Sample logs and telemetry
│   ├── cilium_hubble_flows.jsonl
│   ├── istio_envoy_access.log
│   ├── k8sgpt_analysis.json
│   ├── kubernetes_events.json
│   └── payment-service.log
├── scenarios/          # Demo scenarios and prompts
│   ├── scenario-2.md
│   ├── scnario.md
│   ├── system-prompt.md
│   └── user_service.yaml
├── scripts/            # Automation and utility scripts
│   ├── create_weaviate_embeddings.py
│   ├── run_scheduled_prompts.py
│   ├── scheduled_prompts.yaml
│   └── weaviate_chunking_demo.ipynb
├── terraform/          # Infrastructure as Code examples
│   ├── main.tf
│   ├── providers.tf
│   └── variables.tf
├── gitlab-ci/          # CI/CD pipeline configurations
│   ├── .gitlab-ci.yml
│   └── gitlab-ci-schedule.yml
├── monitoring/         # Monitoring and alerting configs
│   └── prometheus.yml
└── README.md          # This file
```

## Content Categories

### OpenAPI Specifications
- **auth_service.yaml**: Authentication service API definition
- **payment_api.json**: Payment processing API specification
- **user_service.yaml**: User management service API

### Kubernetes Manifests
- **deployment.yaml**: Sample application deployment
- **service.yaml**: Service definitions and networking
- **ingress.yaml**: Ingress routing configuration

### Security Policies
- **payment-authz-policy.yaml**: Istio authorization policies
- **payment-service-netpol.yaml**: Cilium network policies

### Sample Logs & Telemetry
- **cilium_hubble_flows.jsonl**: Network flow observability data
- **istio_envoy_access.log**: Service mesh access logs
- **k8sgpt_analysis.json**: AI-powered Kubernetes diagnostics
- **kubernetes_events.json**: Cluster event logs
- **payment-service.log**: Application-specific logs

### Demo Scenarios
- **scenario-2.md**: Detailed payment service investigation scenario
- **scnario.md**: General demo scenarios
- **system-prompt.md**: AI assistant system prompts
- **user_service.yaml**: User service configuration

### Automation Scripts
- **create_weaviate_embeddings.py**: Main embedding creation script
- **run_scheduled_prompts.py**: Scheduled prompt execution
- **scheduled_prompts.yaml**: Prompt scheduling configuration
- **weaviate_chunking_demo.ipynb**: Jupyter notebook for chunking demos

### Infrastructure as Code
- **main.tf**: Terraform resource definitions
- **providers.tf**: Provider configurations
- **variables.tf**: Variable definitions

### CI/CD Pipelines
- **.gitlab-ci.yml**: Main CI/CD pipeline
- **gitlab-ci-schedule.yml**: Scheduled pipeline jobs

### Monitoring
- **prometheus.yml**: Prometheus scraping configuration

## Embedding Process

All files in this directory are automatically processed by the `create_weaviate_embeddings.py` script:

1. **File Discovery**: Recursively scans all relevant file types
2. **Content Extraction**: Parses JSON, YAML, Markdown, logs, and code files
3. **Text Chunking**: Splits content into 1000-character chunks with 200-character overlap
4. **Embedding Generation**: Uses LM Studio to create vector embeddings
5. **Vector Storage**: Stores embeddings in Weaviate with metadata

## File Types Processed

The embedding script processes these file extensions:
- `.json` - API specs, configurations
- `.yaml` / `.yml` - Kubernetes manifests, policies
- `.md` - Documentation and scenarios
- `.log` - Application and system logs
- `.py` - Python scripts and utilities
- `.tf` - Terraform configurations

## Adding New Specifications

To add new specifications to the knowledge base:

1. Place files in the appropriate subdirectory
2. Update this README if creating new categories
3. Re-run the embedding script:
   ```bash
   cd demo_specs/scripts
   python3 create_weaviate_embeddings.py
   ```

## Demo Scenarios

### Scenario 1: API Security Investigation
**Problem**: Payment service returns 405 Method Not Allowed errors
**Data Sources**:
- OpenAPI specs (`payment_api.json`)
- Network flows (`cilium_hubble_flows.jsonl`)
- Access logs (`istio_envoy_access.log`)
- Authorization policies (`payment-authz-policy.yaml`)

### Scenario 2: Pod Health Diagnostics
**Problem**: Payment service in CrashLoopBackOff state
**Data Sources**:
- Kubernetes events (`kubernetes_events.json`)
- Pod logs (`payment-service.log`)
- K8sGPT analysis (`k8sgpt_analysis.json`)
- Deployment specs (`deployment.yaml`)

### Scenario 3: Network Policy Validation
**Problem**: Unexpected traffic patterns in Cilium Hubble flows
**Data Sources**:
- Network policies (`payment-service-netpol.yaml`)
- Flow logs (`cilium_hubble_flows.jsonl`)
- Service definitions (`service.yaml`)

## Notes

- All sensitive information in demo files is sanitized
- File paths are preserved as metadata for traceability
- Chunking strategy ensures context preservation across splits
- Embeddings are generated using `text-embedding-nomic-embed-text-v1.5` model

## Related Files

- `../mcp-config/mcp.json` - MCP server configurations for live data
- `../scripts/setup_demo.sh` - Main setup script
- `../run-setup.md` - Complete setup guide
- `../README.md` - Main project documentation
