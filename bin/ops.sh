#!/usr/bin/env bash
# ==============================================================================
# bin/ops.sh (ELION Hyper-Dashboard Stack Controller)
# Einheitliche CLI für alle Stack-Operationen
# ==============================================================================

set -euo pipefail

# Detect script directory and project root
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source common library if available
if [[ -f "$SCRIPT_DIR/../scripts/_lib.sh" ]]; then
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/../scripts/_lib.sh"
  load_env
else
  # Fallback: set basic defaults
  DASHBOARD_PORT="${DASHBOARD_PORT:-12349}"
  OPENA1_PORT="${OPENA1_PORT:-12344}"
  OPENA2_PORT="${OPENA2_PORT:-12345}"
  
  # Read token from .env if exists
  if [[ -f "$PROJECT_ROOT/.env" ]]; then
    # Look specifically for DASHBOARD_ADMIN_TOKEN
    TOK=$(grep "^DASHBOARD_ADMIN_TOKEN=" "$PROJECT_ROOT/.env" 2>/dev/null | cut -d= -f2 || echo "")
    
    # If not found, warn but continue
    if [[ -z "$TOK" ]]; then
      echo "⚠️  DASHBOARD_ADMIN_TOKEN not found in .env" >&2
    fi
  else
    TOK=""
  fi
fi

cd "$PROJECT_ROOT"

# Endpoints
DASH="http://127.0.0.1:$DASHBOARD_PORT"
OPENA1="http://127.0.0.1:$OPENA1_PORT"
OPENA2="http://127.0.0.1:$OPENA2_PORT"

# ==============================================================================
# Helper Functions
# ==============================================================================

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "❌ Required command not found: $1"; exit 1; }
}

need_token() {
  [[ -n "${TOK:-}" ]] || { echo "❌ No token found. Create/fill $PROJECT_ROOT/.env"; exit 1; }
}

usage() {
  cat <<'USAGE'
ELION Hyper-Dashboard OPS – Stack Controller

Commands:
  start             - Start all services (opena1, opena2, Dashboard)
  stop              - Stop all services (graceful shutdown via PID files)
  restart           - Stop and start all services
  health            - Quick health check (all core services)
  status            - Full system status (requires Bearer token)
  monitor           - Continuous health monitoring (Ctrl+C to stop)
  agents:register   - Register agents with dashboard
  verify            - Run integration verification + E2E test
  logs              - Show recent service logs (tail -100)
  logs:follow       - Follow logs in real-time
  e2e               - Run Option-2-Flow E2E test
  help              - Show this help

Examples:
  bin/ops.sh start
  bin/ops.sh monitor
  bin/ops.sh e2e
  bin/ops.sh logs:follow
USAGE
}

# ==============================================================================
# Command Handlers
# ==============================================================================

[[ $# -lt 1 ]] && { usage; exit 1; }

cmd="$1"; shift || true

case "$cmd" in
  start)
    echo "🚀 Starting ELION Hyper-Dashboard services..."
    
    # Load .env tokens
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
      echo "❌ .env nicht gefunden. Bitte zuerst bin/env_bootstrap.sh ausführen"
      exit 1
    fi
    
    # Export OpenAI Keys aus .env
    export OPENAI_API_KEY_OPENA1=$(grep '^OPENAI_API_KEY_OPENA1=' "$PROJECT_ROOT/.env" | cut -d= -f2 | tr -d '"')
    export OPENAI_API_KEY_OPENA2=$(grep '^OPENAI_API_KEY_OPENA2=' "$PROJECT_ROOT/.env" | cut -d= -f2 | tr -d '"')
    
    if [[ -z "$OPENAI_API_KEY_OPENA1" ]] || [[ -z "$OPENAI_API_KEY_OPENA2" ]]; then
      echo "⚠️  OpenAI Keys nicht vollständig in .env"
      echo "    Benötigt: OPENAI_API_KEY_OPENA1 und OPENAI_API_KEY_OPENA2"
    fi
    
    echo ""
    echo "=== Starting Core Services ==="
    
    # opena1 mit Key starten
    cd "$PROJECT_ROOT/1.opena1&2_portier"
    if [[ -x "bin/start_opena1_with_key.sh" ]]; then
      echo "🔹 opena1 (Port 12344)..."
      bin/start_opena1_with_key.sh
    else
      echo "⚠️  bin/start_opena1_with_key.sh nicht gefunden"
    fi
    
    # opena2 mit Key starten
    if [[ -x "bin/start_opena2_with_key.sh" ]]; then
      echo "🔹 opena2 (Port 12345)..."
      bin/start_opena2_with_key.sh
    else
      echo "⚠️  bin/start_opena2_with_key.sh nicht gefunden"
    fi
    
    # Dashboard starten (falls vorhanden)
    cd "$PROJECT_ROOT"
    if [[ -f "19.opena20_dashboard_agent/main_dashboard.py" ]]; then
      echo "🔹 Dashboard (Port 12349)..."
      cd 19.opena20_dashboard_agent
      mkdir -p ../logs
      nohup python3 main_dashboard.py > ../logs/dashboard.nohup.log 2>&1 &
      echo "✅ Dashboard gestartet (PID: $!)"
      cd "$PROJECT_ROOT"
    fi
    
    sleep 3
    
    echo ""
    echo "=== Health Check ==="
    curl -s http://127.0.0.1:12344/health 2>/dev/null | jq -c '{service, status, openai_key_present}' || echo "❌ opena1 nicht erreichbar"
    curl -s http://127.0.0.1:12345/health 2>/dev/null | jq -c '{service, status, entries, openai_key_present}' || echo "❌ opena2 nicht erreichbar"
    curl -s http://127.0.0.1:12349/health 2>/dev/null | jq -c '{service, status}' || echo "⚠️  Dashboard nicht erreichbar"
    
    echo ""
    echo "✅ Stack gestartet. Verwende 'bin/ops.sh status' für Details."
    ;;

  stop)
    echo "🛑 Stopping ELION Hyper-Dashboard services..."
    
    # Stop via PID files if available
    if [[ -f "$PROJECT_ROOT/logs/opena1.pid" ]]; then
      PID=$(cat "$PROJECT_ROOT/logs/opena1.pid")
      kill "$PID" 2>/dev/null && echo "✅ opena1 gestoppt (PID: $PID)" || echo "⚠️  opena1 PID $PID nicht gefunden"
      rm -f "$PROJECT_ROOT/logs/opena1.pid"
    fi
    
    if [[ -f "$PROJECT_ROOT/logs/opena2.pid" ]]; then
      PID=$(cat "$PROJECT_ROOT/logs/opena2.pid")
      kill "$PID" 2>/dev/null && echo "✅ opena2 gestoppt (PID: $PID)" || echo "⚠️  opena2 PID $PID nicht gefunden"
      rm -f "$PROJECT_ROOT/logs/opena2.pid"
    fi
    
    # Fallback: kill by process name
    echo "Stoppe bekannte Prozesse..."
    pkill -f "opena1_app.py" 2>/dev/null && echo "✅ opena1_app.py gestoppt" || true
    pkill -f "opena2_app.py" 2>/dev/null && echo "✅ opena2_app.py gestoppt" || true
    pkill -f "main_dashboard.py" 2>/dev/null && echo "✅ Dashboard gestoppt" || true
    
    echo "✅ Services gestoppt"
    ;;

  health)
    need_cmd curl
    echo "🏥 Checking Dashboard health..."
    curl -s "$DASH/health" | (command -v jq >/dev/null 2>&1 && jq . || cat)
    ;;

  status)
    need_cmd curl
    need_token
    echo "📊 Checking system status..."
    curl -s -H "Authorization: Bearer $TOK" "$DASH/api/status/all" | (command -v jq >/dev/null 2>&1 && jq . || cat)
    ;;

  agents:register)
    echo "📝 Registering agents..."
    if [[ -x "$PROJECT_ROOT/scripts/register_agents.py" ]]; then
      python3 "$PROJECT_ROOT/scripts/register_agents.py"
    elif [[ -x "$PROJECT_ROOT/scripts/agents_register.sh" ]]; then
      "$PROJECT_ROOT/scripts/agents_register.sh"
    else
      echo "⚠️  No registration script found. Using manual registration..."
      need_cmd curl
      need_token
      
      echo "Registering opena1..."
      curl -s -X POST "$DASH/api/agent/register" \
        -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
        -d '{"agent_id":"opena1","endpoint":"http://127.0.0.1:12344"}' | (command -v jq >/dev/null 2>&1 && jq . || cat)
      
      echo "Registering opena2..."
      curl -s -X POST "$DASH/api/agent/register" \
        -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
        -d '{"agent_id":"opena2","endpoint":"http://127.0.0.1:12345"}' | (command -v jq >/dev/null 2>&1 && jq . || cat)
      
      echo "✅ Agent registration complete"
    fi
    ;;

  verify)
    echo "🔍 Running integration verification..."
    if [[ -x "$PROJECT_ROOT/scripts/verify_stack.sh" ]]; then
      "$PROJECT_ROOT/scripts/verify_stack.sh"
    else
      echo "Running quick verification..."
      "$0" health
      echo ""
      "$0" status
    fi
    ;;

  logs)
    echo "📜 Showing recent logs..."
    tail -n 100 "$PROJECT_ROOT/logs"/*.log 2>/dev/null || echo "No logs found in logs/ directory"
    ;;

  logs:follow)
    echo "📜 Following logs (Ctrl+C to stop)..."
    tail -f "$PROJECT_ROOT/logs"/*.log 2>/dev/null || echo "No logs found in logs/ directory"
    ;;

  restart)
    echo "🔄 Restarting services..."
    "$0" stop
    sleep 2
    "$0" start
    ;;

  monitor)
    echo "🔍 Starting continuous health monitoring (Ctrl+C to stop)..."
    echo ""
    
    while true; do
      clear
      echo "=== ELION Health Monitor ($(date '+%Y-%m-%d %H:%M:%S')) ==="
      echo ""
      
      # opena1
      echo -n "🔹 opena1 (12344): "
      if HEALTH=$(curl -s -m 2 http://127.0.0.1:12344/health 2>/dev/null); then
        STATUS=$(echo "$HEALTH" | jq -r '.status' 2>/dev/null || echo "error")
        KEY=$(echo "$HEALTH" | jq -r '.openai_key_present' 2>/dev/null || echo "false")
        if [[ "$STATUS" == "ok" ]] && [[ "$KEY" == "true" ]]; then
          echo "✅ OK (Key present)"
        else
          echo "⚠️  Status: $STATUS, Key: $KEY"
        fi
      else
        echo "❌ UNREACHABLE"
      fi
      
      # opena2
      echo -n "🔹 opena2 (12345): "
      if HEALTH=$(curl -s -m 2 http://127.0.0.1:12345/health 2>/dev/null); then
        STATUS=$(echo "$HEALTH" | jq -r '.status' 2>/dev/null || echo "error")
        ENTRIES=$(echo "$HEALTH" | jq -r '.entries' 2>/dev/null || echo "0")
        KEY=$(echo "$HEALTH" | jq -r '.openai_key_present' 2>/dev/null || echo "false")
        if [[ "$STATUS" == "ok" ]]; then
          echo "✅ OK ($ENTRIES entries, Key: $KEY)"
        else
          echo "⚠️  Status: $STATUS"
        fi
      else
        echo "❌ UNREACHABLE"
      fi
      
      # Dashboard
      echo -n "🔹 Dashboard (12349): "
      if HEALTH=$(curl -s -m 2 http://127.0.0.1:12349/health 2>/dev/null); then
        STATUS=$(echo "$HEALTH" | jq -r '.status' 2>/dev/null || echo "error")
        if [[ "$STATUS" == "healthy" ]] || [[ "$STATUS" == "ok" ]]; then
          echo "✅ OK"
        else
          echo "⚠️  Status: $STATUS"
        fi
      else
        echo "❌ UNREACHABLE"
      fi
      
      echo ""
      echo "Next check in 5s... (Ctrl+C to stop)"
      sleep 5
    done
    ;;

  e2e)
    echo "🧪 Running E2E Option-2-Flow Test..."
    if [[ -x "$PROJECT_ROOT/tests/e2e_option2_flow.sh" ]]; then
      exec "$PROJECT_ROOT/tests/e2e_option2_flow.sh"
    else
      echo "❌ E2E Test script nicht gefunden: tests/e2e_option2_flow.sh"
      exit 1
    fi
    ;;

  help|-h|--help)
    usage
    ;;

  *)
    echo "❌ Unknown command: $cmd"
    echo ""
    usage
    exit 1
    ;;
esac
