#!/usr/bin/env bash
# start_opena7.sh – Start opena7 E-Mail Agent (Port 12352)
# PORTIER 3.0 Compliance

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$PROJECT_DIR")"

cd "$PROJECT_DIR"

# ============================================================================
# CONFIG
# ============================================================================

PORT=12352
PID_FILE="logs/opena7.pid"
LOG_FILE="logs/opena7.nohup.log"
SERVICE_NAME="opena7"

# ============================================================================
# PID-CHECK
# ============================================================================

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "❌ $SERVICE_NAME läuft bereits (PID: $OLD_PID)"
        echo "   Stoppe zuerst: bin/stop_opena7.sh"
        exit 1
    else
        echo "🧹 Lösche verwaiste PID-Datei (Prozess $OLD_PID existiert nicht mehr)"
        rm -f "$PID_FILE"
    fi
fi

# ============================================================================
# PORT-CHECK
# ============================================================================

if lsof -i :$PORT >/dev/null 2>&1; then
    echo "❌ Port $PORT bereits belegt!"
    lsof -i :$PORT
    exit 1
fi

# ============================================================================
# ENV LADEN
# ============================================================================

# ============================================================================
# BEARER_TOKEN VALIDIERUNG
# ============================================================================

if [ -z "${BEARER_TOKEN:-}" ]; then
    echo "❌ BEARER_TOKEN nicht gesetzt in .env"
    echo "   Generiere: bin/env_bootstrap.sh"
    exit 1
fi

# ============================================================================
# DEPENDENCIES
# ============================================================================

echo "📦 Prüfe Dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI nicht installiert, installiere Dependencies..."
    pip install -q fastapi uvicorn pydantic requests email-validator
fi

# ============================================================================
# LOGS VORBEREITEN
# ============================================================================

mkdir -p logs
touch "$LOG_FILE"

# ============================================================================
# SERVICE STARTEN
# ============================================================================

echo "🚀 Starte $SERVICE_NAME auf Port $PORT..."

# Setze ENV-Variablen für Service
export OPENA7_PORT=$PORT
export ARCHIVP_ROOT="${ARCHIVP_ROOT:-$ROOT_DIR/1.opena1&2_portier/archivp_store}"

nohup python3 main_email_agent.py > "$LOG_FILE" 2>&1 &
PID=$!

echo $PID > "$PID_FILE"

# ============================================================================
# HEALTH-CHECK
# ============================================================================

echo "⏳ Warte auf Service-Start..."
sleep 3

if kill -0 $PID 2>/dev/null; then
    echo ""
    echo "✅ $SERVICE_NAME gestartet!"
    echo "   PID: $PID"
    echo "   Port: $PORT"
    echo "   Health: http://127.0.0.1:$PORT/health"
    echo ""
    echo "📋 Log-Tail:"
    tail -10 "$LOG_FILE"
else
    echo "❌ Service-Start fehlgeschlagen!"
    echo ""
    echo "📋 Log:"
    tail -20 "$LOG_FILE"
    exit 1
fi
