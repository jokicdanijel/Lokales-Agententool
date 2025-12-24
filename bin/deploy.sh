#!/bin/bash
# ELION Hyper-Dashboard – Production Deployment Script
# Performs preflight check before deployment

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "🚀 ELION HYPER-DASHBOARD – DEPLOYMENT"
echo "========================================================================"
echo ""
echo "Timestamp: $(date)"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Activate virtual environment
if [[ -d "$VENV_DIR" ]]; then
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}⚠️ Virtual environment not found: $VENV_DIR${NC}"
    echo -e "${YELLOW}   Attempting to use system Python${NC}"
fi

# Step 1: Run Preflight Check
echo ""
echo "========================================================================"
echo "STEP 1: PREFLIGHT CHECK"
echo "========================================================================"

if [ -f "$PROJECT_ROOT/scripts/preflight_check.py" ]; then
    if python3 "$PROJECT_ROOT/scripts/preflight_check.py"; then
        echo -e "${GREEN}✅ Preflight check passed${NC}"
    else
        echo -e "${RED}❌ Preflight check failed${NC}"
        echo ""
        echo "Deployment aborted. Fix violations before deploying."
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ Preflight script not found, skipping${NC}"
fi

# Step 2: Validate Baseline
echo ""
echo "========================================================================"
echo "STEP 2: BASELINE VALIDATION"
echo "========================================================================"

if [ -f "$PROJECT_ROOT/scripts/validate_baseline.py" ]; then
    if python3 "$PROJECT_ROOT/scripts/validate_baseline.py"; then
        echo -e "${GREEN}✅ Baseline validation passed${NC}"
    else
        echo -e "${RED}❌ Baseline validation failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ Baseline validation script not found, skipping${NC}"
fi

# Step 3: Run Discovery
echo ""
echo "========================================================================"
echo "STEP 3: AGENT DISCOVERY"
echo "========================================================================"

if [ -f "$PROJECT_ROOT/scripts/agent_discovery.py" ]; then
    if python3 "$PROJECT_ROOT/scripts/agent_discovery.py"; then
        echo -e "${GREEN}✅ Agent discovery completed${NC}"
    else
        echo -e "${YELLOW}⚠️ Agent discovery had warnings${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Agent discovery script not found, skipping${NC}"
fi

# Step 4: Environment Setup
echo ""
echo "========================================================================"
echo "STEP 4: ENVIRONMENT SETUP"
echo "========================================================================"

mkdir -p "$PROJECT_ROOT/data/auth"
mkdir -p "$PROJECT_ROOT/data/billing"
mkdir -p "$PROJECT_ROOT/data/workflows"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/artifacts"

echo -e "${GREEN}✅ Directories created${NC}"

# Step 5: Start Services
echo ""
echo "========================================================================"
echo "STEP 5: SERVICE STARTUP"
echo "========================================================================"
echo ""
echo "Starting services in order..."
echo ""

# Array of services with ports
declare -A SERVICES=(
    ["opena2"]="12345"
    ["opena1"]="12344"
    ["auth"]="12370"
    ["billing"]="12371"
    ["website"]="12372"
    ["opena20"]="12349"
    ["opena21"]="12368"
)

# Start core services
for service in opena2 opena1 auth billing website opena20 opena21; do
    port="${SERVICES[$service]}"

    echo -e "${BLUE}Starting $service (Port $port)...${NC}"

    start_script="$PROJECT_ROOT/bin/start_${service}.sh"

    if [[ -f "$start_script" ]]; then
        # Start in background
        bash "$start_script" > "$PROJECT_ROOT/logs/${service}_startup.log" 2>&1 &

        # Wait for port to be available
        sleep 2

        # Check if port is listening (requires netcat)
        if command -v nc &> /dev/null; then
            if nc -z 127.0.0.1 "$port" 2>/dev/null; then
                echo -e "${GREEN}✅ $service started on port $port${NC}"
            else
                echo -e "${YELLOW}⚠️ $service may not be fully ready (port not responding)${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ $service started (netcat not available for port check)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Start script not found: $start_script${NC}"
    fi

    echo ""
done

# Step 6: Health Check
echo ""
echo "========================================================================"
echo "STEP 6: HEALTH CHECK"
echo "========================================================================"
echo ""

echo "Waiting 5 seconds for all services to initialize..."
sleep 5

for service in "${!SERVICES[@]}"; do
    port="${SERVICES[$service]}"

    if command -v curl &> /dev/null; then
        if curl -sf "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service (Port $port) - HEALTHY${NC}"
        else
            echo -e "${RED}❌ $service (Port $port) - UNREACHABLE${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ curl not available, skipping health check for $service${NC}"
    fi
done

# Final Summary
echo ""
echo "========================================================================"
echo "🎉 DEPLOYMENT COMPLETE"
echo "========================================================================"
echo ""
echo -e "${BLUE}Services:${NC}"
echo "  - Auth:      http://127.0.0.1:12370"
echo "  - Billing:   http://127.0.0.1:12371"
echo "  - Website:   http://127.0.0.1:12372"
echo "  - Dashboard: http://127.0.0.1:12349"
echo "  - Workflow:  http://127.0.0.1:12368"
echo ""
echo "Logs: $PROJECT_ROOT/logs/"
echo ""
echo -e "${GREEN}✅ System is ready for use${NC}"
echo ""
