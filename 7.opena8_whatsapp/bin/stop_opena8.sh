#!/usr/bin/env bash
# Stop-Skript für opena8 (WhatsApp Agent)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"

AGENT_NAME="opena8"
PID_FILE="$AGENT_DIR/logs/${AGENT_NAME}.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  $AGENT_NAME läuft nicht (keine PID-Datei)"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo "⚠️  Prozess $PID existiert nicht mehr"
    rm -f "$PID_FILE"
    exit 0
fi

echo "🛑 Stoppe $AGENT_NAME (PID: $PID)..."

kill -TERM "$PID"

# Warte max. 10 Sekunden
for i in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "✅ $AGENT_NAME gestoppt"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill
echo "⚠️  Graceful shutdown timeout, force kill..."
kill -KILL "$PID" 2>/dev/null || true
rm -f "$PID_FILE"
echo "✅ $AGENT_NAME gestoppt (force)"
