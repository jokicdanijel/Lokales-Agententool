#!/bin/bash
# ====================================================
# 📞 OPENA9 Telephone Agent - Start Script
# PORTIER PAS-6.0
# ====================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${PROJECT_DIR}/logs"
PID_FILE="${LOG_DIR}/opena9.pid"
LOG_FILE="${LOG_DIR}/opena9_telephone.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}📞 Starting OPENA9 Telephone Agent (PAS-6.0)${NC}"

# Create logs directory
mkdir -p "$LOG_DIR"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Agent already running (PID: $OLD_PID)${NC}"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# Load environment

# Set defaults
PORT=${OPENA9_PORT:-12355}
HOST=${OPENA9_HOST:-0.0.0.0}

# Change to project directory
cd "$PROJECT_DIR"

# Start the agent
echo -e "${GREEN}🚀 Starting on ${HOST}:${PORT}${NC}"

nohup python3 -m uvicorn main:app \
    --host "$HOST" \
    --port "$PORT" \
    --log-level info \
    > "$LOG_FILE" 2>&1 &

NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# Wait for startup
sleep 2

# Check if running
if kill -0 "$NEW_PID" 2>/dev/null; then
    echo -e "${GREEN}✅ OPENA9 Telephone Agent started successfully${NC}"
    echo -e "${GREEN}   PID: $NEW_PID${NC}"
    echo -e "${GREEN}   Port: $PORT${NC}"
    echo -e "${GREEN}   Logs: $LOG_FILE${NC}"
    echo -e "${GREEN}   Dashboard: http://127.0.0.1:${PORT}/html/index.html${NC}"
else
    echo -e "${RED}❌ Failed to start agent${NC}"
    tail -20 "$LOG_FILE"
    exit 1
fi
