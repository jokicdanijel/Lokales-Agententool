#!/usr/bin/env bash
# Start-Skript für opena9 (Telefonie Agent)
# Port: 12354

set -euo pipefail
# Robustes .env-Parsing (safe für Keys mit = Zeichen)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$AGENT_DIR")"

AGENT_NAME="opena9"
AGENT_PORT=12354
AGENT_SCRIPT="main_telephone_agent.py"

PID_FILE="$AGENT_DIR/logs/${AGENT_NAME}.pid"
LOG_FILE="$AGENT_DIR/logs/${AGENT_NAME}.nohup.log"

mkdir -p "$AGENT_DIR/logs"

# ============================================================================
# PID-CHECK
# ============================================================================

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "❌ $AGENT_NAME läuft bereits (PID: $OLD_PID)"
        echo "   Stoppe mit: bin/stop_${AGENT_NAME}.sh"
        exit 1
    else
        echo "🧹 Lösche verwaiste PID-Datei (Prozess $OLD_PID existiert nicht mehr)"
        rm -f "$PID_FILE"
    fi
fi

# ============================================================================
# PORT-CHECK
# ============================================================================

if lsof -i :$AGENT_PORT >/dev/null 2>&1; then
    echo "❌ Port $AGENT_PORT ist bereits belegt!"
    lsof -i :$AGENT_PORT
    exit 1
fi

# ============================================================================
# .ENV LADEN
# ============================================================================

# ============================================================================
# TOKEN-CHECK
# ============================================================================

if [ -z "${BEARER_TOKEN:-}" ]; then
    echo "❌ BEARER_TOKEN nicht gesetzt!"
    echo "   Generiere mit: bin/env_bootstrap.sh"
    exit 1
fi

# ============================================================================
# DEPENDENCIES
# ============================================================================

echo "📦 Prüfe Dependencies..."

# FastAPI, uvicorn, pydantic, requests
python3 -c "import fastapi, uvicorn, pydantic, requests" 2>/dev/null || {
    echo "⚠️  Dependencies fehlen, installiere..."
    pip3 install fastapi uvicorn pydantic requests
}

# ============================================================================
# START
# ============================================================================

echo "🚀 Starte $AGENT_NAME auf Port $AGENT_PORT..."

cd "$AGENT_DIR"

nohup python3 "$AGENT_SCRIPT" > "$LOG_FILE" 2>&1 &
NEW_PID=$!

echo "$NEW_PID" > "$PID_FILE"

sleep 2

if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "✅ $AGENT_NAME gestartet!"
    echo "   PID: $NEW_PID"
    echo "   Port: $AGENT_PORT"
    echo "   Health: http://127.0.0.1:$AGENT_PORT/health"
    echo ""
    echo "📋 Log-Tail:"
    tail -15 "$LOG_FILE" | grep -E "INFO|ERROR|WARNING" || tail -15 "$LOG_FILE"
else
    echo "❌ Start fehlgeschlagen!"
    echo "📋 Log:"
    cat "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
