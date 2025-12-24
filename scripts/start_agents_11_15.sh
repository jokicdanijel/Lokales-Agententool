#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Phase 4 Agents Starter (11-15)
# Social Media, Influencer, Calendar, HTML, Shop
# ============================================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/logs"

# Ensure log directory
mkdir -p "$LOG_DIR"

# Source venv
VENV="$ROOT/1.opena1&2_portier/venv313"
if [ ! -d "$VENV" ]; then
    echo "❌ venv313 not found at $VENV"
    exit 1
fi

source "$VENV/bin/activate"

# Token check
TOKEN_FILE="$ROOT/.env"
if [ ! -f "$TOKEN_FILE" ]; then
    echo "⚠️  Token file missing. Generating..."
    bash "$ROOT/bin/env_bootstrap.sh"
fi

echo "🚀 Starting Phase 4 Agents (11-15)..."
echo ""

# Define agents
declare -A AGENTS=(
    ["opena11"]="$ROOT/19.dashboard_agent/main_opena11_social_media.py|12359"
    ["opena12"]="$ROOT/19.dashboard_agent/main_opena12_influencer.py|12360"
    ["opena13"]="$ROOT/19.dashboard_agent/main_opena13_calendar.py|12361"
    ["opena14"]="$ROOT/19.dashboard_agent/main_opena14_html.py|12362"
    ["opena15"]="$ROOT/19.dashboard_agent/main_opena15_shop.py|12363"
)

# Start each agent
for agent in "${!AGENTS[@]}"; do
    IFS='|' read -r script port <<< "${AGENTS[$agent]}"

    if [ ! -f "$script" ]; then
        echo "❌ Script not found: $script"
        continue
    fi

    log_file="$LOG_DIR/${agent}.nohup.log"

    # Check if already running
    if lsof -Pi ":${port}" -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  $agent already running on port $port"
        continue
    fi

    echo "Starting $agent on port $port..."
    nohup python "$script" > "$log_file" 2>&1 &

    sleep 1

    # Verify
    if lsof -Pi ":${port}" -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ $agent started (PID: $(lsof -Pi ":${port}" -sTCP:LISTEN -t | head -1))"
    else
        echo "❌ $agent failed to start. Check $log_file"
    fi
done

echo ""
echo "✅ Phase 4 startup complete!"
echo ""
echo "Agent Status:"
echo "  opena11_SocialMedia  : http://127.0.0.1:12359/health"
echo "  opena12_Influencer   : http://127.0.0.1:12360/health"
echo "  opena13_Calendar     : http://127.0.0.1:12361/health"
echo "  opena14_HTML         : http://127.0.0.1:12362/health"
echo "  opena15_Shop         : http://127.0.0.1:12363/health"
echo ""
echo "View logs: tail -f $LOG_DIR/opena1*.log"
