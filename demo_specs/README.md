# demo_specs — sample artifacts for the Spec-driven demo

Purpose
- Provide small, focused artifacts that represent the types of specs and logs used in the MLSecOps demo:
  - openapi/: API contracts used by RAG
  - kubernetes/: deployment/service/ingress manifests
  - terraform/: minimal example to show infra-as-code
  - gitlab-ci/: simple CI pipeline examples
  - monitoring/: sample Prometheus config

Notes
- Secrets are not committed. The deployment manifests reference a secret named `auth-secrets` and the setup script will create a placeholder secret if kubectl is configured.
- Use these files as inputs to Open WebUI / RAG ingestion and K8sGPT analysis.
