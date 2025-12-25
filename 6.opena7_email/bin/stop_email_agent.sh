#!/bin/bash
# 📧 Email Agent 6.0 - Stop Script (PORTIER PAS-6.0)

set -euo pipefail

AGENT_DIR="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/6.opena7_email"
AGENT_NAME="opena7_email"
PID_FILE="$AGENT_DIR/pids/${AGENT_NAME}.pid"

echo "🛑 Stopping Email Agent 6.0..."

if [[ ! -f "$PID_FILE" ]]; then
    echo "❌ No PID file found. Agent may not be running."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "❌ Process $PID not running. Removing stale PID file."
    rm -f "$PID_FILE"
    exit 1
fi

echo "🔄 Terminating process $PID..."
kill "$PID"

# Wait for graceful shutdown
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Email Agent stopped successfully"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "⚡ Force killing process $PID..."
    kill -9 "$PID"
    sleep 1
fi

rm -f "$PID_FILE"
echo "✅ Email Agent 6.0 stopped"
