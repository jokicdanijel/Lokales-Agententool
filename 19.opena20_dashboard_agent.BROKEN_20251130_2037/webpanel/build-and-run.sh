#!/bin/bash
#
# OpenWebUI Agent V2 - Web Panel Docker Build & Run
# PORTIER 3.0 Enterprise Ready
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="opena3-webpanel"
CONTAINER_NAME="opena3-webpanel-container"
PORT=8088

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"; }
error() { echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"; }

cd "$SCRIPT_DIR"

log "🚀 Building OpenWebUI Agent V2 Web Panel..."

# Stop existing container
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    warn "Stopping existing container..."
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
    docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
fi

# Build image
log "📦 Building Docker image..."
docker build -t "$IMAGE_NAME" . || {
    error "Docker build failed!"
    exit 1
}

# Run container
log "▶️ Starting container on port $PORT..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$PORT:80" \
    --restart unless-stopped \
    "$IMAGE_NAME" || {
    error "Container start failed!"
    exit 1
}

# Wait for container to be ready
log "⏳ Waiting for web panel to be ready..."
for i in {1..10}; do
    if curl -s "http://localhost:$PORT" >/dev/null 2>&1; then
        log "✅ Web Panel ready!"
        log "🌐 Access: http://localhost:$PORT"
        log "🔗 API Target: Configure to http://127.0.0.1:12347"
        
        echo ""
        log "📋 Quick Test:"
        echo "  1. Open http://localhost:$PORT"
        echo "  2. Enter Bearer Token"
        echo "  3. Click 'Health Check'"
        echo "  4. Test Native Chat or CMD Dispatch"
        
        exit 0
    fi
    sleep 1
done

error "Web panel nicht innerhalb von 10 Sekunden bereit!"
error "Check container logs: docker logs $CONTAINER_NAME"
exit 1