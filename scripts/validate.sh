#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="$REPO_ROOT/logs"

log() {
  echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGS_DIR/validate.log"
}

# Validate OpenAPI specs
validate_openapi() {
  log "Validating OpenAPI specs..."
  find "$REPO_ROOT/demo_specs/openapi" -type f \( -name "*.yaml" -o -name "*.json" \) -exec \
    openapi-validator {} \; >> "$LOGS_DIR/openapi_validation.log" 2>&1
}

# Validate K8s resources
validate_k8s() {
  log "Validating Kubernetes resources..."
  
  # Check manifests with kubeval
  find "$REPO_ROOT/k8s" -type f -name "*.yaml" -exec \
    kubeval --strict {} \; >> "$LOGS_DIR/k8s_validation.log" 2>&1
    
  # Validate policies
  if command -v cilium >/dev/null 2>&1; then
    find "$REPO_ROOT/k8s/policies" -type f -name "*cilium*.yaml" -exec \
      cilium policy validate {} \; >> "$LOGS_DIR/policy_validation.log" 2>&1
  fi
}

# Validate MCP configs
validate_mcp() {
  log "Validating MCP configurations..."
  for config in "$REPO_ROOT"/mcp/*.json; do
    if ! jq empty "$config" >/dev/null 2>&1; then
      log "Invalid JSON in: $config"
      return 1
    fi
  done
}

# Check demo data
validate_demo_data() {
  log "Validating demo data..."
  
  local required_files=(
    "demo_specs/openapi/payment_api.json"
    "demo_specs/kubernetes/deployment.yaml"
    "demo_specs/monitoring/prometheus.yml"
  )
  
  for file in "${required_files[@]}"; do
    if [[ ! -f "$REPO_ROOT/$file" ]]; then
      log "Missing required file: $file"
      return 1
    fi
  done
}

# Main validation
main() {
  log "Starting validation..."
  
  validate_openapi || log "OpenAPI validation failed"
  validate_k8s || log "K8s validation failed"
  validate_mcp || log "MCP validation failed"
  validate_demo_data || log "Demo data validation failed"
  
  log "Validation completed"
}

main "$@"
