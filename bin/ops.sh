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
  start             - Start all services (uses scripts/start_all.sh or delegates to Python)
  stop              - Stop all services
  health            - Check Dashboard /health endpoint (no token required)
  status            - Check Dashboard /api/status/all (requires token)
  agents:register   - Register agents with dashboard
  verify            - Run integration verification
  logs              - Show service logs
  help              - Show this help

Examples:
  bin/ops.sh start
  bin/ops.sh status
  bin/ops.sh agents:register
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
    
    # Check for OPENAI_API_KEY
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
      if grep -q "^OPENAI_API_KEY=" "$PROJECT_ROOT/.env"; then
        echo "✅ OPENAI_API_KEY found in .env"
      else
        echo "⚠️  OPENAI_API_KEY not found in .env"
        echo "    To set it, run: echo 'OPENAI_API_KEY=your_key_here' >> .env"
      fi
    else
      echo "⚠️  No .env file found. Creating from template..."
      if [[ -f "$PROJECT_ROOT/.env.example" ]]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        echo "📝 Created .env from .env.example. Please edit it to add your keys."
      fi
    fi
    
    # Delegate to start_all.sh if available, otherwise use Python services
    if [[ -x "$PROJECT_ROOT/scripts/start_all.sh" ]]; then
      exec "$PROJECT_ROOT/scripts/start_all.sh"
    elif [[ -x "$PROJECT_ROOT/bin/start_all_agents.sh" ]]; then
      exec "$PROJECT_ROOT/bin/start_all_agents.sh"
    else
      echo "ℹ️  No automated start script found. Starting core services manually..."
      echo "    Please start services individually or use:"
      echo "    - python3 src/services/portier/main.py"
      echo "    - python3 1.opena1&2_portier/main_opena2.py"
      echo "    - python3 src/services/telegram/main.py"
    fi
    ;;

  stop)
    echo "🛑 Stopping ELION Hyper-Dashboard services..."
    if [[ -x "$PROJECT_ROOT/scripts/stop_all.sh" ]]; then
      exec "$PROJECT_ROOT/scripts/stop_all.sh"
    else
      echo "Stopping known processes..."
      pkill -f "main_dashboard.py" 2>/dev/null || true
      pkill -f "main_opena1.py" 2>/dev/null || true
      pkill -f "main_opena2.py" 2>/dev/null || true
      pkill -f "main_kordp.py" 2>/dev/null || true
      echo "✅ Stopped"
    fi
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
