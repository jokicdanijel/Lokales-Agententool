#!/bin/bash
# Start/Stop Pool Services (Agent17-Agent20)
# Ports: 12366-12369

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SERVICES=("agent17" "agent18" "agent19" "agent20")
PORTS=(12366 12367 12368 12369)

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ────────────────────────────────────────────────────────────────────
# Functions
# ────────────────────────────────────────────────────────────────────

start_service() {
    local service=$1
    local port=$2
    local service_dir="$PROJECT_ROOT/src/services/pool/$service"
    
    if [ ! -d "$service_dir" ]; then
        echo -e "${RED}❌ Service directory not found: $service_dir${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Starting $service (Port $port)...${NC}"
    
    cd "$service_dir"
    bash run.sh
    
    cd "$PROJECT_ROOT"
}

stop_service() {
    local service=$1
    local pid_file="$PROJECT_ROOT/.runtime/${service}.pid"
    
    if [ ! -f "$pid_file" ]; then
        echo -e "${YELLOW}⚠️  $service not running (no PID file)${NC}"
        return 0
    fi
    
    local pid=$(cat "$pid_file")
    
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${YELLOW}Stopping $service (PID: $pid)...${NC}"
        kill "$pid"
        sleep 1
        
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${RED}Force killing $service...${NC}"
            kill -9 "$pid"
        fi
        
        rm -f "$pid_file"
        echo -e "${GREEN}✅ $service stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  $service not running (stale PID file)${NC}"
        rm -f "$pid_file"
    fi
}

status_service() {
    local service=$1
    local port=$2
    local pid_file="$PROJECT_ROOT/.runtime/${service}.pid"
    
    if [ ! -f "$pid_file" ]; then
        echo -e "${RED}❌ $service (Port $port): NOT RUNNING${NC}"
        return 1
    fi
    
    local pid=$(cat "$pid_file")
    
    if kill -0 "$pid" 2>/dev/null; then
        # Health check
        local health=$(curl -s http://127.0.0.1:$port/health 2>/dev/null || echo "UNREACHABLE")
        
        if [[ "$health" == *"healthy"* ]]; then
            echo -e "${GREEN}✅ $service (Port $port): HEALTHY (PID: $pid)${NC}"
        else
            echo -e "${YELLOW}⚠️  $service (Port $port): RUNNING but UNHEALTHY (PID: $pid)${NC}"
        fi
    else
        echo -e "${RED}❌ $service (Port $port): DEAD (stale PID)${NC}"
        rm -f "$pid_file"
        return 1
    fi
}

# ────────────────────────────────────────────────────────────────────
# Commands
# ────────────────────────────────────────────────────────────────────

cmd_start() {
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  Starting Pool Services (Agent17-20)${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    for i in "${!SERVICES[@]}"; do
        start_service "${SERVICES[$i]}" "${PORTS[$i]}"
    done
    
    echo ""
    echo -e "${GREEN}✅ All pool services started${NC}"
    echo -e "${YELLOW}Check status: bash bin/pool_services.sh status${NC}"
}

cmd_stop() {
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  Stopping Pool Services (Agent17-20)${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    for service in "${SERVICES[@]}"; do
        stop_service "$service"
    done
    
    echo ""
    echo -e "${GREEN}✅ All pool services stopped${NC}"
}

cmd_status() {
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  Pool Services Status (Agent17-20)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    for i in "${!SERVICES[@]}"; do
        status_service "${SERVICES[$i]}" "${PORTS[$i]}"
    done
}

cmd_restart() {
    cmd_stop
    sleep 2
    cmd_start
}

cmd_help() {
    echo "Pool Services Manager (Agent17-Agent20)"
    echo ""
    echo "Usage: bash bin/pool_services.sh {start|stop|status|restart|help}"
    echo ""
    echo "Commands:"
    echo "  start    - Start all pool services (Ports 12366-12369)"
    echo "  stop     - Stop all pool services"
    echo "  status   - Show status of all pool services"
    echo "  restart  - Restart all pool services"
    echo "  help     - Show this help"
    echo ""
    echo "Services:"
    for i in "${!SERVICES[@]}"; do
        echo "  - ${SERVICES[$i]} (Port ${PORTS[$i]})"
    done
}

# ────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────

case "${1:-help}" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    status)
        cmd_status
        ;;
    restart)
        cmd_restart
        ;;
    help|*)
        cmd_help
        ;;
esac
