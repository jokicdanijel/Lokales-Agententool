#!/usr/bin/env bash
# ELION Hyper-Dashboard 2.0 - Dashboard Service Starter
# Port: 12349
# Service: opena20 (Dashboard Backend + Admin UI)

set -Eeuo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
VENV="$PROJECT_ROOT/1.opena1&2_portier/venv313/bin/activate"
DASHBOARD_MODULE="src.pkg.main_dashboard:app"
PORT=12349
SERVICE_NAME="dashboard"

LOGS_DIR="$PROJECT_ROOT/logs"
RUNTIME_DIR="$PROJECT_ROOT/.runtime/pids"
PID_FILE="$RUNTIME_DIR/${SERVICE_NAME}.pid"
LOG_FILE="$LOGS_DIR/${SERVICE_NAME}.nohup.log"

# ─────────────────────────────────────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────────────────────────────────────

cd "$PROJECT_ROOT"

# Verzeichnisse erstellen
mkdir -p "$LOGS_DIR" "$RUNTIME_DIR"

# Virtual Environment aktivieren
if [ ! -f "$VENV" ]; then
    echo "❌ ERROR: venv not found at $VENV"
    exit 1
fi

source "$VENV"

# ENV-Token sicherstellen
python3 -c "from src.pkg.security import _read_env_token; _read_env_token()" 2>/dev/null || true

# OpenAI API Key für opena20 exportieren (falls .env existiert)

fi

# ─────────────────────────────────────────────────────────────────────────────
# START SERVICE
# ─────────────────────────────────────────────────────────────────────────────

echo "🚀 Starting ELION Dashboard (Port $PORT)..."

# Port-Check
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  WARNING: Port $PORT already in use"
    EXISTING_PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
    echo "   Process PID: $EXISTING_PID"
    read -p "   Kill existing process? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill -9 "$EXISTING_PID" 2>/dev/null || true
        sleep 1
    else
        echo "❌ Aborted"
        exit 1
    fi
fi

# Starte uvicorn im Hintergrund
nohup python3 -m uvicorn "$DASHBOARD_MODULE" \
    --host 127.0.0.1 \
    --port "$PORT" \
    --no-access-log \
    --log-level warning \
    > "$LOG_FILE" 2>&1 &

DASHBOARD_PID=$!
echo $DASHBOARD_PID > "$PID_FILE"

# Warte auf Service
sleep 2

# Health-Check
if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    echo "✅ Dashboard started successfully"
    echo "   PID: $DASHBOARD_PID"
    echo "   Port: $PORT"
    echo "   Logs: $LOG_FILE"
    echo ""
    echo "🌐 Access:"
    echo "   Admin UI:  http://127.0.0.1:$PORT/admin"
    echo "   API Docs:  http://127.0.0.1:$PORT/docs"
    echo "   Health:    http://127.0.0.1:$PORT/health"
else
    echo "❌ ERROR: Dashboard failed to start (health check failed)"
    echo "   Check logs: tail -f $LOG_FILE"
    exit 1
fi
