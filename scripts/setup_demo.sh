#!/usr/bin/env bash
set -euo pipefail
trap 'echo "An unexpected error occurred. See logs above."; exit 1' ERR

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker-compose.yml"
DEMO_SPECS_DIR="$REPO_ROOT/demo_specs"
ZIP_OUT="$REPO_ROOT/demo_specs.zip"
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

# Helper: check command exists
check_cmd() {
  command -v "$1" >/dev/null 2>&1 || { log "Required command '$1' not found. Please install it and re-run."; exit 2; }
}

log "Starting Infrastructure as Spec Demo Setup"

# Validate prerequisites
log "Validating prerequisites..."
# Check for Podman first, then Docker
if command -v podman >/dev/null 2>&1; then
  CONTAINER_CMD="podman"
  log "Using Podman for container management"
elif command -v docker >/dev/null 2>&1; then
  CONTAINER_CMD="docker"
  log "Using Docker for container management"
else
  error "Neither Podman nor Docker found. Please install one of them."
fi

check_cmd curl

# Check Podman Compose or Docker Compose
if command -v podman-compose >/dev/null 2>&1; then
  COMPOSE_CMD="podman-compose"
  log "Using Podman Compose"
elif $CONTAINER_CMD compose version >/dev/null 2>&1; then
  COMPOSE_CMD="$CONTAINER_CMD compose"
  log "Using Docker Compose (modern)"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
  log "Using Docker Compose (legacy)"
else
  log "No container compose tool found. Installing podman-compose..."
  if command -v pip3 >/dev/null 2>&1; then
    pip3 install podman-compose
    if [ $? -eq 0 ]; then
      COMPOSE_CMD="podman-compose"
      log "✅ Podman Compose installed successfully"
    else
      error "Failed to install podman-compose. Please install it manually."
    fi
  else
    error "pip3 not found. Please install Python3 and pip3, then re-run."
  fi
fi

log "Using Compose: $COMPOSE_CMD"

# Start demo containers
log "Starting demo containers..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d

# Wait for services to be reachable with timeout
wait_for_service() {
  local url="$1"
  local service_name="$2"
  local timeout=300
  local interval=5

  log "Waiting for $service_name at $url..."
  local count=0
  while [ $count -lt $timeout ]; do
    if curl -sSf "$url" >/dev/null 2>&1; then
      log "$service_name is ready!"
      return 0
    fi
    sleep $interval
    count=$((count + interval))
  done

  error "Timeout waiting for $service_name at $url"
}

# Wait for all services
wait_for_service "http://localhost:3000" "Open WebUI"
wait_for_service "http://localhost:8080/v1/meta" "Weaviate"

# Wait for LM Studio to be ready
log "Waiting for LM Studio to be ready..."
timeout=60
count=0
while [ $count -lt $timeout ]; do
  if curl -s http://localhost:1234/v1/models >/dev/null 2>&1; then
    log "✅ LM Studio is ready!"
    break
  fi
  sleep 2
  count=$((count + 2))
done

if [ $count -ge $timeout ]; then
  log "⚠️  LM Studio not ready within timeout. Please ensure it's running with models loaded."
fi

# Check if LM Studio is running and start it if needed
log "Checking LM Studio status..."
if ! curl -s http://localhost:1234/v1/models >/dev/null 2>&1; then
  log "LM Studio not running. Attempting to start it..."

  # Try to start LM Studio (macOS specific)
  if command -v open >/dev/null 2>&1; then
    open -a "LM Studio" || log "Warning: Could not start LM Studio automatically. Please start it manually."
    sleep 10  # Give it time to start

    # Check again
    if curl -s http://localhost:1234/v1/models >/dev/null 2>&1; then
      log "✅ LM Studio started successfully"
    else
      log "⚠️  LM Studio may not be fully ready yet. Please ensure it's running with models loaded."
    fi
  else
    log "⚠️  Cannot automatically start LM Studio. Please start it manually."
  fi
else
  log "✅ LM Studio is already running"
fi

log "Note: Ensure these models are loaded in LM Studio:"
log "  - For embeddings: 'nomic-embed-text' (recommended)"
log "  - For chat: Any lightweight model like 'llama-3.1-8b' or 'mistral-7b'"
log "  - LM Studio should be running on localhost:1234 (default)"

# Optional: Setup Kubernetes namespace and secrets if kubectl available
if command -v kubectl >/dev/null 2>&1; then
  log "kubectl found. Setting up Kubernetes resources..."
  if kubectl version --short >/dev/null 2>&1; then
    log "Creating 'production' namespace (if missing)..."
    kubectl apply -f - <<EOF || log "Warning: Failed to create namespace"
apiVersion: v1
kind: Namespace
metadata:
  name: production
EOF

    # Create auth-secrets if missing
    if ! kubectl get secret auth-secrets -n production >/dev/null 2>&1; then
      log "Creating placeholder auth-secrets JWT_SECRET_KEY..."
      # Generate a random key
      if command -v openssl >/dev/null 2>&1; then
        SECRET_VAL="$(openssl rand -base64 32)"
      else
        SECRET_VAL="$(python3 -c 'import secrets,base64;print(base64.b64encode(secrets.token_bytes(24)).decode())' 2>/dev/null || echo 'fallback-secret-key')"
      fi
      kubectl create secret generic auth-secrets --from-literal=JWT_SECRET_KEY="$SECRET_VAL" -n production || log "Warning: Failed to create secret"
      log "Secret 'auth-secrets' created in 'production' namespace."
    else
      log "Secret 'auth-secrets' already exists in 'production'."
    fi
  else
    log "kubectl cannot access any cluster. Skipping k8s setup."
  fi
else
  log "kubectl not installed. Skipping k8s setup."
fi

# Create demo_specs.zip for distribution
if [ -d "$DEMO_SPECS_DIR" ]; then
  log "Creating $ZIP_OUT for distribution..."
  rm -f "$ZIP_OUT"
  if command -v zip >/dev/null 2>&1; then
    (cd "$REPO_ROOT" && zip -r "$(basename "$ZIP_OUT")" "$(basename "$DEMO_SPECS_DIR")" >/dev/null)
  else
    # Fallback to tar.gz if zip not available
    tar -czf "${ZIP_OUT%.zip}.tar.gz" -C "$REPO_ROOT" "$(basename "$DEMO_SPECS_DIR")"
    log "zip not found, created ${ZIP_OUT%.zip}.tar.gz instead."
  fi
  log "Demo specs archive ready."
else
  log "Warning: demo_specs directory not found at $DEMO_SPECS_DIR"
fi

# Clean up temporary files
log "Cleaning up temporary files..."
find "$REPO_ROOT" -name "*.DS_Store" -delete 2>/dev/null || true
find "$REPO_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$REPO_ROOT" -name "*.pyc" -delete 2>/dev/null || true

# Run validation
log "Running validation checks..."
if [ -f "$REPO_ROOT/scripts/validate.sh" ]; then
  if "$REPO_ROOT/scripts/validate.sh"; then
    log "Validation passed!"
  else
    log "Warning: Some validations failed. Check logs for details."
  fi
else
  log "Warning: Validation script not found."
fi

# Create embeddings automatically
log "Creating embeddings for demo specs..."
if command -v python3 >/dev/null 2>&1; then
  if [ -f "$REPO_ROOT/demo_specs/scripts/create_weaviate_embeddings.py" ]; then
    cd "$REPO_ROOT/demo_specs/scripts"
    if python3 create_weaviate_embeddings.py; then
      log "✅ Embeddings created successfully!"
    else
      log "⚠️  Embedding creation failed. You can run it manually later."
    fi
  else
    log "⚠️  Embedding script not found."
  fi
else
  log "⚠️  Python3 not found. Skipping automatic embedding creation."
fi

log "Setup complete!"
cat << 'EOF'

🎉 Infrastructure as Spec Demo Environment Ready!

Next steps:
1. Open Open WebUI at: http://localhost:3000
2. The demo specs have been automatically embedded and are ready for querying!

3. Try these example queries:
   - "Which APIs require authentication?"
   - "Why is payment-service returning 405 errors?"
   - "Show me network policy violations"
   - "What are the payment service configurations?"

Demo scenarios available in: demo_specs/scenarios/
Automation scripts in: demo_specs/scripts/

For troubleshooting:
- Check container logs: $COMPOSE_CMD logs
- View setup logs: logs/setup.log
- Stop demo: $COMPOSE_CMD down
- Re-run embeddings: cd demo_specs/scripts && python3 create_weaviate_embeddings.py

Happy exploring! 🚀

EOF

exit 0
