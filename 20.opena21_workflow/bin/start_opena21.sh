#!/bin/bash
#
# opena21 Workflow Engine Start Script
# PORTIER 3.0 kompatibel
#
set -euo pipefail

# Verzeichnisse
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/.opena21.pid"
NOHUP_LOG="$LOG_DIR/opena21.nohup.log"

# Konfiguration
SERVICE_NAME="opena21"
PORT=12364
PYTHON_CMD="python3"

# Hilfsfunktionen
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$NOHUP_LOG"
}

error() {
    echo "[ERROR] $*" >&2
    exit 1
}

# Logs-Verzeichnis erstellen
mkdir -p "$LOG_DIR"

# Check ob bereits läuft
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        log "⚠️ $SERVICE_NAME bereits aktiv (PID: $PID)"
        exit 0
    else
        log "🧹 Verwaiste PID-Datei entfernt"
        rm -f "$PID_FILE"
    fi
fi

# Environment prüfen
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log "⚠️ .env Datei fehlt - erstelle Template"
    cat > "$PROJECT_DIR/.env" << EOF
# opena21 Workflow Engine Configuration
OPENA21_PORT=12364
BEARER_TOKEN=\${BEARER_TOKEN}
SERVICE_NAME=opena21
PROGRAM_TARGET=workflowp
VERSION=2.0

# PORTIER Integration
PORTIER_URL=http://127.0.0.1:12344
OPENA2_URL=http://127.0.0.1:12345
KORDP_URL=http://127.0.0.1:12346

# Workflow Engine
WORKFLOW_DEFAULT_TIMEOUT=300
WORKFLOW_MAX_RETRIES=3
WORKFLOW_STEP_TIMEOUT=30
STORAGE_BACKEND=memory

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/opena21.nohup.log
EOF
fi

# Dependencies prüfen
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    log "📦 Dependencies installieren..."
    cd "$PROJECT_DIR"
    "$PYTHON_CMD" -m pip install --break-system-packages -r requirements.txt --quiet --disable-pip-version-check || \
    "$PYTHON_CMD" -m pip install -r requirements.txt --quiet --disable-pip-version-check
fi

# Port prüfen
if command -v netstat >/dev/null 2>&1; then
    if netstat -tuln | grep -q ":$PORT "; then
        error "❌ Port $PORT bereits belegt"
    fi
elif command -v ss >/dev/null 2>&1; then
    if ss -tuln | grep -q ":$PORT "; then
        error "❌ Port $PORT bereits belegt"
    fi
fi

# Service starten
log "🚀 Starte $SERVICE_NAME auf Port $PORT..."
cd "$PROJECT_DIR"

# nohup mit Logging
nohup "$PYTHON_CMD" main.py > "$NOHUP_LOG" 2>&1 &
PID=$!

# PID speichern
echo "$PID" > "$PID_FILE"

# Kurz warten und prüfen
sleep 2
if kill -0 "$PID" 2>/dev/null; then
    log "✅ $SERVICE_NAME gestartet (PID: $PID)"
    
    # Health-Check
    sleep 3
    if command -v curl >/dev/null 2>&1; then
        if curl -s "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
            log "🟢 Health-Check erfolgreich"
        else
            log "🔴 Health-Check fehlgeschlagen"
        fi
    fi
else
    rm -f "$PID_FILE"
    error "❌ Start fehlgeschlagen"
fi

log "📋 Logs: tail -f $NOHUP_LOG"
log "🌐 Health: curl http://127.0.0.1:$PORT/health"
log "📚 API Docs: http://127.0.0.1:$PORT/docs"

exit 0