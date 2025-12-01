#!/bin/bash
# ====================================================
# 🔐 OPENA11 Unlock Master - Stop Script
# PORTIER PAS-6.0
# ====================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${PROJECT_DIR}/logs"
PID_FILE="${LOG_DIR}/opena11.pid"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🔐 Stopping OPENA11 Unlock Master${NC}"

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  No PID file found - agent may not be running${NC}"
    
    # Try to find and kill by port
    PID=$(lsof -ti:12357 2>/dev/null || true)
    if [ -n "$PID" ]; then
        echo -e "${YELLOW}Found process on port 12357 (PID: $PID)${NC}"
        kill -TERM "$PID" 2>/dev/null && echo -e "${GREEN}✅ Stopped${NC}" || echo -e "${RED}❌ Failed${NC}"
    fi
    exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
    echo -e "${YELLOW}Sending SIGTERM to PID $PID${NC}"
    kill -TERM "$PID"
    
    # Wait for graceful shutdown
    for i in {1..10}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            break
        fi
        sleep 0.5
    done
    
    # Force kill if still running
    if kill -0 "$PID" 2>/dev/null; then
        echo -e "${YELLOW}Force killing...${NC}"
        kill -9 "$PID" 2>/dev/null
    fi
    
    rm -f "$PID_FILE"
    echo -e "${GREEN}✅ OPENA11 Unlock Master stopped${NC}"
else
    echo -e "${YELLOW}Process $PID not running${NC}"
    rm -f "$PID_FILE"
fi