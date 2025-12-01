#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# opena10 Start Script (Port 12355)
# ──────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$PROJECT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

PORT=12355
PID_FILE="logs/opena10.pid"
LOG_FILE="logs/opena10.nohup.log"

# ──────────────────────────────────────────────────────────────────────────────
# PID-CHECK (Konflikt vermeiden)
# ──────────────────────────────────────────────────────────────────────────────

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "❌ opena10 läuft bereits (PID $OLD_PID)"
        echo "   Stoppe zuerst mit: bash bin/stop_opena10.sh"
        exit 1
    else
        echo "⚠️  Stale PID-File entfernt (Prozess $OLD_PID nicht aktiv)"
        rm -f "$PID_FILE"
    fi
fi

# ──────────────────────────────────────────────────────────────────────────────
# PORT-CHECK
# ──────────────────────────────────────────────────────────────────────────────

if lsof -i :$PORT >/dev/null 2>&1; then
    BLOCKING_PID=$(lsof -ti :$PORT)
    echo "❌ Port $PORT bereits belegt (PID: $BLOCKING_PID)"
    echo "   Prüfe mit: lsof -i :$PORT"
    exit 1
fi

# ──────────────────────────────────────────────────────────────────────────────
# ENV LOADING
# ──────────────────────────────────────────────────────────────────────────────

if [ -f "$ROOT_DIR/.env" ]; then
    echo "✅ Lade .env aus Projekt-Root"
    set -a
    source "$ROOT_DIR/.env"
    set +a
elif [ -f "$PROJECT_DIR/.env" ]; then
    echo "✅ Lade lokale .env"
    set -a
    source "$PROJECT_DIR/.env"
    set +a
else
    echo "⚠️  Keine .env gefunden (verwende Defaults)"
fi

# BEARER_TOKEN validation
if [ -z "$BEARER_TOKEN" ]; then
    echo "⚠️  WARNING: BEARER_TOKEN nicht gesetzt"
    echo "   Security ist deaktiviert!"
fi

# ──────────────────────────────────────────────────────────────────────────────
# DEPENDENCIES
# ──────────────────────────────────────────────────────────────────────────────

echo "📦 Prüfe Dependencies..."

# Check if running in externally-managed environment
if python3 -c "import sys; sys.exit(0 if hasattr(sys, 'base_prefix') else 1)" 2>/dev/null; then
    # Try installing with --break-system-packages for externally-managed Python
    python3 -m pip install --break-system-packages -q fastapi uvicorn pydantic sqlalchemy 2>/dev/null || \
    python3 -m pip install --user -q fastapi uvicorn pydantic sqlalchemy 2>/dev/null || \
    echo "⚠️  Dependencies bereits installiert oder Installation übersprungen"
else
    python3 -m pip install -q fastapi uvicorn pydantic sqlalchemy 2>/dev/null || \
    echo "⚠️  Dependencies bereits installiert"
fi

# ──────────────────────────────────────────────────────────────────────────────
# DIRECTORIES
# ──────────────────────────────────────────────────────────────────────────────

mkdir -p logs data

# ──────────────────────────────────────────────────────────────────────────────
# START SERVICE
# ──────────────────────────────────────────────────────────────────────────────

echo "🚀 Starte opena10 auf Port $PORT..."

nohup python3 main_calltracking_agent.py > "$LOG_FILE" 2>&1 &
PID=$!

echo $PID > "$PID_FILE"

# Wait for startup
sleep 2

# Verify process is running
if ! kill -0 $PID 2>/dev/null; then
    echo "❌ opena10 Start fehlgeschlagen!"
    echo "   Logs: tail -20 $LOG_FILE"
    exit 1
fi

echo "✅ opena10 gestartet!"
echo "   PID: $PID"
echo "   Port: $PORT"
echo "   Health: http://127.0.0.1:$PORT/health"
echo ""
echo "📋 Log-Tail:"
tail -15 "$LOG_FILE"
