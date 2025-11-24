#!/bin/bash
# start_browser_agent.sh - Start 5.opena6_browser Agent
# PORTIER 3.0 - Browser Automation Agent Launcher

set -e

# Configuration
AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_NAME="5.opena6_browser"
PORT=12350
CONFIG_PATH="$AGENT_DIR/config.json"
MAIN_PY="$AGENT_DIR/main.py"
LOG_DIR="$AGENT_DIR/logs"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p "$LOG_DIR"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🌐 5.opena6_browser - Agent Launcher${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if config exists
if [ ! -f "$CONFIG_PATH" ]; then
    echo -e "${RED}❌ Config not found: $CONFIG_PATH${NC}"
    exit 1
fi

# Check if main.py exists
if [ ! -f "$MAIN_PY" ]; then
    echo -e "${RED}❌ main.py not found: $MAIN_PY${NC}"
    exit 1
fi

# Kill existing process if running
pkill -f "opena6.*main.py" 2>/dev/null || true
sleep 1

# Start agent
echo -e "${BLUE}📌 Starting agent...${NC}"
python3 "$MAIN_PY" "$CONFIG_PATH" "$PORT" > "$LOG_DIR/opena6.log" 2>&1 &

AGENT_PID=$!

# Wait for agent to start
sleep 2

# Check if process is running
if ! kill -0 $AGENT_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start agent${NC}"
    cat "$LOG_DIR/opena6.log"
    exit 1
fi

echo -e "${GREEN}✅ Agent started successfully${NC}"
echo -e "${GREEN}   PID: $AGENT_PID${NC}"
echo -e "${GREEN}   Port: $PORT${NC}"
echo -e "${GREEN}   Logs: $LOG_DIR/opena6.log${NC}"

# Display startup info
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "🚀 ${GREEN}PORTIER 3.0 - Option-2-Flow${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📡 Health Check:    curl http://0.0.0.0:$PORT/health"
echo "📊 Status Endpoint: curl http://0.0.0.0:$PORT/status"
echo "🔧 Execute Command: curl -X POST http://0.0.0.0:$PORT/execute \\"
echo "                      -H 'Authorization: Bearer sk_opena6_browser_v3_production' \\"
echo "                      -H 'Content-Type: application/json' \\"
echo "                      -d '{\"action\":\"open\",\"url\":\"https://example.com\"}'"
echo ""
echo "📚 Documentation: see CMD_SCHEMA.md"
echo "🔍 View logs:     tail -f $LOG_DIR/opena6.log"
echo ""

# Keep in foreground
wait $AGENT_PID
