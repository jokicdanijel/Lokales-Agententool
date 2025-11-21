#!/usr/bin/env bash
# Start all ELION agents with project .venv
# Usage: bash bin/start_all_agents.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${ROOT}/.venv/bin/python"
LOGS="${ROOT}/logs"

mkdir -p "$LOGS"

echo "🚀 Starting ALL ELION Agents..."
echo ""

# Agent definitions: name, port, script path
declare -a AGENTS=(
    "opena1:12344:1.opena1&2_portier/opena1_app.py"
    "opena2:12345:1.opena1&2_portier/opena2_app.py"
    "opena3:12347:2.opena3_openwebui/main_openwebui_bridge.py"
    "telegram:12348:src/pkg/main_opena4_telegram.py"
    "vscode:12350:src/pkg/main_opena4_vscode.py"
    "browser:12351:src/pkg/main_opena5_browser.py"
    "email:12352:src/pkg/main_opena6_email.py"
    "whatsapp:12353:src/pkg/main_opena7_whatsapp.py"
    "telephone:12354:src/pkg/main_opena8_telephone.py"
    "call_tracking:12355:src/pkg/main_opena9_call_tracking.py"
    "unlock:12356:src/pkg/main_opena10_unlock.py"
    "social_media:12357:src/pkg/main_opena11_social_media.py"
    "influencer:12358:src/pkg/main_opena12_influencer.py"
    "calendar:12359:src/pkg/main_opena13_calendar.py"
    "html:12360:src/pkg/main_opena14_html.py"
    "shop:12361:src/pkg/main_opena15_shop.py"
    "crm:12362:src/pkg/main_opena16_crm.py"
    "analytics:12363:src/pkg/main_opena17_analytics.py"
    "dashboard:12364:src/pkg/main_opena18_dashboard.py"
    "workflow:12365:src/pkg/main_opena19_workflow.py"
    "finance:12366:src/pkg/main_opena_finance.py"
)

STARTED=0
SKIPPED=0
FAILED=0

for agent_def in "${AGENTS[@]}"; do
    IFS=':' read -r name port script <<< "$agent_def"
    
    # Check if already running
    if lsof -i ":$port" > /dev/null 2>&1; then
        echo "  ⚠️  $name (port $port): Already running"
        ((SKIPPED++))
        continue
    fi
    
    # Check if script exists
    if [ ! -f "$ROOT/$script" ]; then
        echo "  ❌ $name: Script not found ($script)"
        ((FAILED++))
        continue
    fi
    
    # Start agent
    log_file="$LOGS/${name}.nohup.log"
    nohup "$VENV" "$ROOT/$script" > "$log_file" 2>&1 &
    PID=$!
    
    # Wait briefly to verify
    sleep 0.3
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "  ✅ $name (port $port) — PID $PID"
        ((STARTED++))
    else
        echo "  ❌ $name (port $port): Failed to start"
        ((FAILED++))
    fi
done

echo ""
echo "📊 Summary:"
echo "   ✅ Started: $STARTED"
echo "   ⚠️  Skipped (already running): $SKIPPED"
echo "   ❌ Failed: $FAILED"
echo ""

# Health check sample (first 5 services)
echo "🏥 Health Check (sample):"
sleep 2
for agent_def in "${AGENTS[@]:0:5}"; do
    IFS=':' read -r name port script <<< "$agent_def"
    if curl -s "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
        echo "  ✅ $name"
    else
        echo "  ❌ $name (not responding)"
    fi
done

echo ""
echo "✅ Agent startup complete!"
echo "   Logs: $LOGS/"
echo "   Check status: curl http://127.0.0.1:12344/health"
