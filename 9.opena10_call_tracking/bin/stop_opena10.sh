#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# opena10 Stop Script
# ──────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

PID_FILE="logs/opena10.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  Kein PID-File gefunden (opena10 läuft nicht)"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo "⚠️  Prozess $PID nicht aktiv (Stale PID-File)"
    rm -f "$PID_FILE"
    exit 0
fi

echo "🛑 Stoppe opena10 (PID $PID)..."

kill -SIGTERM "$PID"

# Wait for graceful shutdown (max 10 seconds)
for i in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "✅ opena10 gestoppt"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo "⚠️  Graceful shutdown timeout, force kill..."
kill -SIGKILL "$PID" 2>/dev/null || true
rm -f "$PID_FILE"

echo "✅ opena10 gestoppt (force)"
