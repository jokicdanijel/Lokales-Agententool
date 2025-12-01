#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# opena4 Stop Script (Telegram Agent)
# ══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verzeichnisse
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/opena4.pid"

# PID-Check
if [[ ! -f "$PID_FILE" ]]; then
    echo -e "${YELLOW}⚠️  opena4 läuft nicht (kein PID-File)${NC}"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Prozess $PID existiert nicht mehr${NC}"
    rm -f "$PID_FILE"
    exit 0
fi

# Graceful shutdown (SIGTERM)
echo -e "${YELLOW}🛑 Stoppe opena4 (PID: $PID)...${NC}"
kill -TERM "$PID"

# Warte max. 10 Sekunden
for i in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo -e "${GREEN}✅ opena4 gestoppt${NC}"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill
echo -e "${RED}⚠️  Prozess reagiert nicht, force kill...${NC}"
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"
echo -e "${GREEN}✅ opena4 gestoppt (force)${NC}"
