#!/usr/bin/env bash
# stop_opena6.sh – Stop opena6 Browser Agent
# PORTIER 3.0 Compliance

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# ============================================================================
# CONFIG
# ============================================================================

PID_FILE="logs/opena6.pid"
SERVICE_NAME="opena6"

# ============================================================================
# PID-CHECK & STOP
# ============================================================================

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  $SERVICE_NAME läuft nicht (PID-Datei fehlt)"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo "⚠️  Prozess $PID existiert nicht mehr (verwaiste PID-Datei)"
    rm -f "$PID_FILE"
    exit 0
fi

echo "🛑 Stoppe $SERVICE_NAME (PID: $PID)..."

# Graceful Shutdown (SIGTERM)
kill -TERM "$PID" 2>/dev/null || true

# Warte auf Prozess-Ende (max. 10 Sekunden)
for i in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "✅ $SERVICE_NAME gestoppt!"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force Kill (SIGKILL)
echo "⚠️  Graceful Shutdown fehlgeschlagen, Force-Kill..."
kill -KILL "$PID" 2>/dev/null || true
rm -f "$PID_FILE"

echo "✅ $SERVICE_NAME gestoppt (Force-Kill)!"
