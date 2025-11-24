#!/bin/bash
# start_portier_stack.sh - Start PORTIER 3.0 Complete Stack
# Startet alle 20 Agenten (opena1-opena20) mit Health-Checks

set -e

# Configuration
WORKSPACE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui"
AGENT_DIR="$WORKSPACE/LocalAgent-Pro"
LOG_DIR="$WORKSPACE/logs"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Agent configuration
declare -A AGENTS=(
    [opena1]="12345:Coordinator"
    [opena2]="12346:Archivator"
    [opena3]="12347:Gateway"
    [opena4]="12348:ComputeAgent"
    [opena5]="12349:ComputeAgent"
    [opena6]="12350:BrowserAgent"
    [opena7]="12351:ComputeAgent"
    [opena8]="12352:ComputeAgent"
    [opena9]="12353:ComputeAgent"
    [opena10]="12354:ComputeAgent"
    [opena11]="12355:ComputeAgent"
    [opena12]="12356:ComputeAgent"
    [opena13]="12357:ComputeAgent"
    [opena14]="12358:ComputeAgent"
    [opena15]="12359:ComputeAgent"
    [opena16]="12360:ComputeAgent"
    [opena17]="12361:ComputeAgent"
    [opena18]="12362:ComputeAgent"
    [opena19]="12363:ComputeAgent"
    [opena20]="12364:Dashboard"
)

# Create logs directory
mkdir -p "$LOG_DIR"

# Banner
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 PORTIER 3.0 - Multi-Agent Stack Launcher${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📊 Starte ${#AGENTS[@]} Agenten..."
echo "📂 Workspace: $WORKSPACE"
echo "📝 Logs: $LOG_DIR"
echo ""

# Kill any existing agents
echo -e "${YELLOW}⏹️  Stopping any existing agents...${NC}"
pkill -9 -f "python3.*main.py" 2>/dev/null || true
sleep 2

# Array to track started PIDs
declare -a PIDS=()
declare -a NAMES=()

# Start each agent
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "🔧 Starting agents...\n"

for agent_name in "${!AGENTS[@]}"; do
    IFS=':' read -r port role <<< "${AGENTS[$agent_name]}"
    agent_path="$AGENT_DIR/$agent_name"

    if [ ! -d "$agent_path" ]; then
        echo -e "${RED}❌ $agent_name directory not found: $agent_path${NC}"
        continue
    fi

    if [ ! -f "$agent_path/main.py" ]; then
        echo -e "${RED}❌ $agent_name main.py not found${NC}"
        continue
    fi

    # Start agent
    cd "$agent_path"
    python3 main.py config.json $port > "$LOG_DIR/${agent_name}.log" 2>&1 &
    PID=$!

    PIDS+=($PID)
    NAMES+=("$agent_name:$port")

    echo -e "${GREEN}✓${NC} $agent_name (PID: $PID, Port: $port, Role: $role)"
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Wait for startup
sleep 3

# Health check
echo -e "\n🏥 Health Checks:\n"

health_ok=0
health_fail=0

for agent_info in "${NAMES[@]}"; do
    IFS=':' read -r agent_name port <<< "$agent_info"

    response=$(curl -s -o /dev/null -w "%{http_code}" "http://0.0.0.0:$port/health" 2>/dev/null || echo "000")

    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓${NC} $agent_name (Port $port): ONLINE"
        ((health_ok++))
    else
        echo -e "${RED}✗${NC} $agent_name (Port $port): OFFLINE (HTTP $response)"
        ((health_fail++))
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Summary
echo -e "\n📊 Status Summary:"
echo -e "   ${GREEN}✓ Online: $health_ok${NC}"
echo -e "   ${RED}✗ Offline: $health_fail${NC}"
echo -e "   Total: ${#NAMES[@]}"

echo ""
echo -e "${GREEN}✅ PORTIER 3.0 Stack is Running!${NC}"
echo ""

# Quick reference
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "🔗 Quick Reference:\n"
echo -e "📊 Dashboard:          http://0.0.0.0:8000"
echo -e "🎯 Coordinator:        http://0.0.0.0:12345/health"
echo -e "📝 Archivator:         http://0.0.0.0:12346/health"
echo -e "🌐 Gateway:            http://0.0.0.0:12347/health"
echo -e "🌐 Browser Agent:      http://0.0.0.0:12350/health"
echo ""
echo -e "📝 View Logs:"
echo -e "   tail -f $LOG_DIR/opena1.log      # Coordinator"
echo -e "   tail -f $LOG_DIR/opena2.log      # Archivator"
echo -e "   tail -f $LOG_DIR/opena6.log      # Browser Agent"
echo ""
echo -e "🔍 Test Command:"
echo -e "   curl http://0.0.0.0:12345/health | jq ."
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Keep running
echo ""
echo -e "⏳ Agents running in background. Press Ctrl+C to stop all."
echo ""

# Trap to stop all agents on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping PORTIER 3.0 Stack...${NC}"
    pkill -9 -f "python3.*main.py" 2>/dev/null || true
    echo -e "${GREEN}✅ All agents stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep process alive
while true; do
    sleep 1
done
