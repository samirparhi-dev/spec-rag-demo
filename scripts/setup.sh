#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="$REPO_ROOT/logs"

# Create logs directory
mkdir -p "$LOGS_DIR"

log() {
  echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGS_DIR/setup.log"
}

error() {
  log "ERROR: $*"
  exit 1
}

# Check required tools
check_requirements() {
  local tools=(docker kubectl helm k9s cilium istioctl)
  
  for tool in "${tools[@]}"; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      error "Required tool not found: $tool"
    fi
  done
  
  log "All required tools found"
}

# Validate all YAML files
validate_yaml() {
  log "Validating YAML files..."
  
  find "$REPO_ROOT" -type f -name "*.yaml" -o -name "*.yml" | while read -r file; do
    if ! yamllint "$file" >> "$LOGS_DIR/yaml_validation.log" 2>&1; then
      error "YAML validation failed for: $file"
    fi
  done
  
  log "YAML validation complete"
}

# Setup directories
setup_dirs() {
  local dirs=(rag k8s mcp monitoring demo_specs scripts)
  
  for dir in "${dirs[@]}"; do
    mkdir -p "$REPO_ROOT/$dir"
  done
  
  # Move files to correct locations
  mv "$REPO_ROOT"/waviate/* "$REPO_ROOT/rag/weaviate/" 2>/dev/null || true
  
  log "Directory structure organized"
}

# Start required services
start_services() {
  log "Starting services..."
  
  docker-compose -f "$REPO_ROOT/docker-compose.yml" up -d
  
  # Wait for services
  local services=(open-webui qdrant ollama)
  for svc in "${services[@]}"; do
    timeout 300 bash -c "until curl -s http://localhost:${svc} >/dev/null; do sleep 5; done" || \
      error "Timeout waiting for $svc"
  done
  
  log "All services started"
}

# Main setup flow
main() {
  log "Starting setup..."
  
  check_requirements
  setup_dirs
  validate_yaml
  start_services
  
  # Run validation script
  if ! "$REPO_ROOT/scripts/validate.sh"; then
    error "Validation failed"
  fi
  
  log "Setup completed successfully"
  
  cat << EOF
Demo environment is ready!

1. Open WebUI: http://localhost:3000
2. Upload demo_specs/ into Documents
3. Try example queries from README.md

For troubleshooting, check logs in: $LOGS_DIR
EOF
}

main "$@"
