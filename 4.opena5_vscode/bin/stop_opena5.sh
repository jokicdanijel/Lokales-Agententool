#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# opena5 Stop Script (VS Code Agent)
# ══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/opena5.pid"

if [[ ! -f "$PID_FILE" ]]; then
    echo -e "${YELLOW}⚠️  opena5 läuft nicht${NC}"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Prozess existiert nicht mehr${NC}"
    rm -f "$PID_FILE"
    exit 0
fi

echo -e "${YELLOW}🛑 Stoppe opena5 (PID: $PID)...${NC}"
kill -TERM "$PID"

for i in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo -e "${GREEN}✅ opena5 gestoppt${NC}"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

echo -e "${RED}⚠️  Force kill...${NC}"
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"
echo -e "${GREEN}✅ opena5 gestoppt (force)${NC}"
