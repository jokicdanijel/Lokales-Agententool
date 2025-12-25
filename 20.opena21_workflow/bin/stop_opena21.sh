#!/bin/bash
#
# opena21 Workflow Engine Stop Script
# PORTIER 3.0 kompatibel
#
set -euo pipefail

# Verzeichnisse
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/.opena21.pid"
LOG_DIR="$PROJECT_DIR/logs"
NOHUP_LOG="$LOG_DIR/opena21.nohup.log"

# Konfiguration
SERVICE_NAME="opena21"
PORT=12364

# Hilfsfunktionen
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    if [ -f "$NOHUP_LOG" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$NOHUP_LOG"
    fi
}

# PID-Datei prüfen
if [ ! -f "$PID_FILE" ]; then
    log "⚠️ $SERVICE_NAME läuft nicht (keine PID-Datei)"
    exit 0
fi

PID=$(cat "$PID_FILE")

# Prozess prüfen
if ! kill -0 "$PID" 2>/dev/null; then
    log "⚠️ $SERVICE_NAME läuft nicht (PID $PID nicht gefunden)"
    rm -f "$PID_FILE"
    exit 0
fi

log "🛑 Stoppe $SERVICE_NAME (PID: $PID)..."

# Graceful Shutdown (SIGTERM)
kill -TERM "$PID"

# Warten auf Shutdown
for i in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        log "✅ $SERVICE_NAME erfolgreich gestoppt"
        rm -f "$PID_FILE"
        exit 0
    fi
    log "⏳ Warte auf Shutdown... ($i/10)"
    sleep 1
done

# Force Kill (SIGKILL)
log "⚠️ Graceful Shutdown fehlgeschlagen - Force Kill..."
if kill -0 "$PID" 2>/dev/null; then
    kill -KILL "$PID"
    sleep 1

    if ! kill -0 "$PID" 2>/dev/null; then
        log "✅ $SERVICE_NAME force-stopped"
        rm -f "$PID_FILE"
    else
        log "❌ Konnte $SERVICE_NAME nicht stoppen"
        exit 1
    fi
fi

# Port-Check
if command -v netstat >/dev/null 2>&1; then
    if netstat -tuln | grep -q ":$PORT "; then
        log "⚠️ Port $PORT noch belegt"
    else
        log "🟢 Port $PORT freigegeben"
    fi
elif command -v ss >/dev/null 2>&1; then
    if ss -tuln | grep -q ":$PORT "; then
        log "⚠️ Port $PORT noch belegt"
    else
        log "🟢 Port $PORT freigegeben"
    fi
fi

exit 0
