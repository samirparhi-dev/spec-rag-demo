#!/usr/bin/env bash
set -euo pipefail
trap 'echo "An unexpected error occurred. See logs above."; exit 1' ERR

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker-compose.demo.yml"
DEMO_SPECS_DIR="$REPO_ROOT/demo_specs"
ZIP_OUT="$REPO_ROOT/demo_specs.zip"

# Helper: check command exists
check_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Required command '$1' not found. Please install it and re-run."; exit 2; }
}

echo "Validating prerequisites..."
check_cmd docker
check_cmd docker-compose || check_cmd docker-compose-plugin || echo "docker-compose not found; using 'docker compose' if available."

# Create a minimal docker-compose for the demo (idempotent)
cat > "$COMPOSE_FILE" <<'EOF'
version: '3.8'
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - ENABLE_RAG=true
      - ENABLE_MCP=true
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    restart: unless-stopped
EOF

echo "Starting demo containers with docker compose..."
# Try modern docker compose first, fallback to docker-compose
if docker compose version >/dev/null 2>&1; then
  docker compose -f "$COMPOSE_FILE" up -d
else
  docker-compose -f "$COMPOSE_FILE" up -d
fi

# Wait for services to be reachable
wait_for_http() {
  local url="$1" local retries=20 local delay=3
  for i in $(seq 1 $retries); do
    if curl -sSf "$url" >/dev/null 2>&1; then
      echo "Service $url reachable."
      return 0
    fi
    echo "Waiting for $url ... ($i/$retries)"
    sleep $delay
  done
  echo "Timeout waiting for $url"
  return 1
}

echo "Waiting for Open WebUI (http://localhost:3000)..."
wait_for_http "http://localhost:3000" || echo "Open WebUI may not be ready yet. Check docker logs."

echo "Waiting for Ollama (http://localhost:11434)..."
wait_for_http "http://localhost:11434" || echo "Ollama may not be ready yet."

echo "Waiting for Qdrant (http://localhost:6333)..."
wait_for_http "http://localhost:6333" || echo "Qdrant may not be ready yet."

# Optionally create k8s namespace and secret (if kubectl connected)
if command -v kubectl >/dev/null 2>&1; then
  echo "kubectl found. Verifying cluster access..."
  if kubectl version --short >/dev/null 2>&1; then
    echo "Creating 'production' namespace (if missing)..."
    kubectl apply -f - <<EOF || true
apiVersion: v1
kind: Namespace
metadata:
  name: production
EOF
    # Create auth-secrets if missing
    if ! kubectl get secret auth-secrets -n production >/dev/null 2>&1; then
      echo "Creating placeholder auth-secrets JWT_SECRET_KEY (random)..."
      # generate a random key
      if command -v openssl >/dev/null 2>&1; then
        SECRET_VAL="$(openssl rand -base64 32)"
      else
        SECRET_VAL="$(python3 -c 'import secrets,base64;print(base64.b64encode(secrets.token_bytes(24)).decode())')"
      fi
      kubectl create secret generic auth-secrets --from-literal=JWT_SECRET_KEY="$SECRET_VAL" -n production || true
      echo "Secret 'auth-secrets' created in 'production' namespace."
    else
      echo "Secret 'auth-secrets' already exists in 'production'."
    fi
  else
    echo "kubectl cannot access any cluster. Skipping k8s secret creation."
  fi
else
  echo "kubectl not installed. Skipping k8s secret creation."
fi

# Create demo_specs.zip for distribution (idempotent)
if [ -d "$DEMO_SPECS_DIR" ]; then
  echo "Creating $ZIP_OUT ..."
  rm -f "$ZIP_OUT"
  if command -v zip >/dev/null 2>&1; then
    (cd "$REPO_ROOT" && zip -r "$(basename "$ZIP_OUT")" "$(basename "$DEMO_SPECS_DIR")" >/dev/null)
  else
    # fallback to tar.gz if zip not available
    tar -czf "${ZIP_OUT%.zip}.tar.gz" -C "$REPO_ROOT" "$(basename "$DEMO_SPECS_DIR")"
    echo "zip not found, created ${ZIP_OUT%.zip}.tar.gz instead."
  fi
  echo "Artifact ready."
else
  echo "demo_specs directory not found at $DEMO_SPECS_DIR"
fi

# Prune obvious unwanted files (safe list)
echo "Pruning common unwanted files (if present)..."
PRUNE_LIST=("*.DS_Store" "node_modules" "__pycache__" ".pytest_cache")
for p in "${PRUNE_LIST[@]}"; do
  find "$REPO_ROOT" -name "$p" -exec rm -rf {} + 2>/dev/null || true
done

echo "Setup complete. Next steps:"
echo " - Open http://localhost:3000 and upload demo_specs/ into Documents"
echo " - Use the notebook waviate/weaviate_chunking_demo.ipynb to test ingestion into Weaviate"
echo " - Review demo_specs/README.md for artifact descriptions"
exit 0
