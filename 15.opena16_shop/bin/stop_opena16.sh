#!/usr/bin/env bash
# =============================================================================
# opena16 - Shop Management Agent Stop Script
# Port: 12361
# Kürzel: shopp
# =============================================================================

set -euo pipefail

# Farbcodes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/logs/opena16.pid"

# Config
SERVICE_NAME="opena16"

# =============================================================================
# MAIN
# =============================================================================

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}[WARNING] PID-Datei nicht gefunden: $PID_FILE${NC}"
    echo -e "${YELLOW}[INFO] Service läuft möglicherweise nicht${NC}"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo -e "${YELLOW}[WARNING] Prozess mit PID $PID existiert nicht mehr${NC}"
    rm -f "$PID_FILE"
    exit 0
fi

echo -e "${YELLOW}[INFO] Stoppe $SERVICE_NAME (PID: $PID)...${NC}"

# Graceful shutdown (SIGTERM)
kill -TERM "$PID" 2>/dev/null || true

# Wait for termination
sleep 2

# Check if still running
if kill -0 "$PID" 2>/dev/null; then
    echo -e "${YELLOW}[WARNING] Prozess läuft noch, forciere Beendigung (SIGKILL)...${NC}"
    kill -KILL "$PID" 2>/dev/null || true
    sleep 1
fi

# Remove PID file
rm -f "$PID_FILE"

echo -e "${GREEN}[INFO] ✅ $SERVICE_NAME erfolgreich gestoppt${NC}"
