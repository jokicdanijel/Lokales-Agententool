#!/usr/bin/env bash
set -euo pipefail

# opena6 Browser Agent — Route Registration & Health Check
# Registers agent with opena1 (coordinator) and validates opena2 connectivity

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="${PROJECT_ROOT}/5.opena6_browser"
PORT="${OPENA6_PORT:-12349}"
OPENA1_URL="${OPENA1_URL:-http://127.0.0.1:12344}"
OPENA2_URL="${OPENA2_URL:-http://127.0.0.1:12345}"

echo "=========================================="
echo "opena6 Browser Agent — Registration Script"
echo "=========================================="

# ============================================================================
# PREFLIGHT CHECKS
# ============================================================================

echo ""
echo "1️⃣  Preflight Checks..."

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check if venv exists
if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
    echo "❌ Virtual environment not found at ${PROJECT_ROOT}/.venv"
    echo "   Run: python3 -m venv ${PROJECT_ROOT}/.venv"
    exit 1
fi

# Activate venv
source "${PROJECT_ROOT}/.venv/bin/activate"
echo "✅ Virtual environment activated"

# Check dependencies
echo "Checking dependencies..."
python3 -c "import fastapi; import uvicorn; import playwright" 2>/dev/null || {
    echo "❌ Dependencies missing. Installing..."
    pip install -q -r "${SERVICE_DIR}/requirements.txt"
}
echo "✅ All dependencies available"

# ============================================================================
# HEALTH CHECKS
# ============================================================================

echo ""
echo "2️⃣  Health Checks..."

# Check opena1 (coordinator)
echo "Checking opena1 health..."
if curl -s "${OPENA1_URL}/health" | jq -e '.status=="ok"' > /dev/null 2>&1; then
    echo "✅ opena1 is healthy"
else
    echo "⚠️  opena1 not responding (will retry at startup)"
fi

# Check opena2 (archivator)
echo "Checking opena2 health..."
if curl -s "${OPENA2_URL}/health" | jq -e '.status=="ok"' > /dev/null 2>&1; then
    echo "✅ opena2 is healthy"
else
    echo "⚠️  opena2 not responding (will retry at startup)"
fi

# ============================================================================
# AGENT STARTUP (if not already running)
# ============================================================================

echo ""
echo "3️⃣  Starting opena6 Agent..."

if curl -s "http://127.0.0.1:${PORT}/health" 2>/dev/null | jq -e '.status=="ok"' > /dev/null 2>&1; then
    echo "✅ opena6 already running on port ${PORT}"
else
    echo "Starting opena6 on port ${PORT}..."
    
    cd "${SERVICE_DIR}"
    export OPENA6_PORT="${PORT}"
    
    # Start in background
    nohup python3 -m app.main > "${PROJECT_ROOT}/logs/opena6.nohup.log" 2>&1 &
    AGENT_PID=$!
    echo "Started with PID ${AGENT_PID}"
    
    # Wait for startup (30s timeout)
    for i in {1..30}; do
        if curl -s "http://127.0.0.1:${PORT}/health" 2>/dev/null | jq -e '.status=="ok"' > /dev/null 2>&1; then
            echo "✅ opena6 started successfully"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "❌ opena6 failed to start (timeout after 30s)"
            exit 1
        fi
        sleep 1
    done
fi

# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

echo ""
echo "4️⃣  Registering Route with opena1..."

ROUTE_PAYLOAD=$(cat <<EOF
{
  "agent_id": "opena6",
  "endpoint": "http://127.0.0.1:${PORT}",
  "component": "browser",
  "status": "healthy"
}
EOF
)

RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "${ROUTE_PAYLOAD}" \
  "${OPENA1_URL}/route/update" || echo "{}")

if echo "${RESPONSE}" | jq -e '.agent_id=="opena6"' > /dev/null 2>&1; then
    echo "✅ Route registered with opena1"
    echo "   Agent ID: opena6"
    echo "   Endpoint: http://127.0.0.1:${PORT}"
else
    echo "⚠️  Route registration returned: ${RESPONSE}"
fi

# ============================================================================
# VERIFICATION
# ============================================================================

echo ""
echo "5️⃣  Verification..."

# Test opena6 health
HEALTH=$(curl -s "http://127.0.0.1:${PORT}/health" | jq .)
echo "opena6 Health:"
echo "${HEALTH}" | jq .

# Get metrics
echo ""
echo "opena6 Metrics:"
curl -s "http://127.0.0.1:${PORT}/metrics" | head -10

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
echo "=========================================="
echo "✅ opena6 Registration Complete"
echo "=========================================="
echo ""
echo "Service Details:"
echo "  Service: opena6 (Browser Automation)"
echo "  Port: ${PORT}"
echo "  Health: http://127.0.0.1:${PORT}/health"
echo "  API Docs: http://127.0.0.1:${PORT}/docs"
echo "  Logs: ${PROJECT_ROOT}/logs/opena6.nohup.log"
echo ""
echo "Next Steps:"
echo "  1. View API docs: curl http://127.0.0.1:${PORT}/docs"
echo "  2. Test playbook: curl -X POST http://127.0.0.1:${PORT}/api/test-playbook"
echo "  3. Run integration tests: pytest tests/test_browser_service.py"
echo ""
