#!/usr/bin/env bash
set -euo pipefail

# START AGENTS 8-10 (Phase 3)
# Telephone, Call-Tracking, Unlock

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/1.portier_openai/venv313"

if [ ! -d "$VENV" ]; then
    echo "❌ venv313 not found at $VENV"
    exit 1
fi

source "$VENV/bin/activate"

# Stop existing processes
echo "🛑 Stopping any existing agents..."
pkill -f "main_opena8_telephone.py" || true
pkill -f "main_opena9_call_tracking.py" || true
pkill -f "main_opena10_unlock.py" || true
sleep 1

# Start Agent 8: Telephone
echo "🚀 Starting Agent 8 (Telephone) on port 12356..."
nohup python "$ROOT/19.dashboard_agent/main_opena8_telephone.py" > "$ROOT/logs/opena8.nohup.log" 2>&1 &
sleep 2

# Start Agent 9: Call-Tracking
echo "🚀 Starting Agent 9 (Call-Tracking) on port 12357..."
nohup python "$ROOT/19.dashboard_agent/main_opena9_call_tracking.py" > "$ROOT/logs/opena9.nohup.log" 2>&1 &
sleep 2

# Start Agent 10: Unlock
echo "🚀 Starting Agent 10 (Unlock) on port 12358..."
nohup python "$ROOT/19.dashboard_agent/main_opena10_unlock.py" > "$ROOT/logs/opena10.nohup.log" 2>&1 &
sleep 2

# Health checks
echo "✅ Checking health..."
TOKEN=$(cat "$ROOT/.env" 2>/dev/null || echo "MEIN_SUPER_TOKEN_123")

mkdir -p "$ROOT/logs"

for port in 12356 12357 12358; do
    if curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:$port/health" | jq . > /dev/null 2>&1; then
        echo "✅ Port $port: HEALTHY"
    else
        echo "⚠️ Port $port: Not responding yet (starting...)"
    fi
done

# Register agents with opena19
echo "📝 Registering with Dashboard..."
DASHBOARD="http://127.0.0.1:12349"

for agent_id in "opena8_telephone" "opena9_call_tracking" "opena10_unlock"; do
    port=$((12356 + $(echo "$agent_id" | grep -o "[0-9]*" | tail -1 | sed 's/^0*//')))
    
    curl -s -X POST "$DASHBOARD/api/agent/register" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"agent_id\": \"$agent_id\", \"endpoint\": \"http://127.0.0.1:$port\"}" | jq .
    
    echo "✅ Registered: $agent_id"
done

echo "✅ Phase 3 startup complete!"
echo "📊 Agents running on ports 12356-12358"
