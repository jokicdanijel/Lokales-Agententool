#!/bin/bash
# Stop Portier 2.0 Stack
# LOCATION: /home/danijel-jd/.../1.opena1&2_portier/bin/stop_stack.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$PROJECT_DIR/logs"

echo "🛑 Stopping Portier 2.0 Stack..."

# Stop opena2
if [ -f "$LOGS_DIR/opena2.pid" ]; then
    PID=$(cat "$LOGS_DIR/opena2.pid")
    if kill -0 $PID 2>/dev/null; then
        echo "▶️  Stopping opena2 (PID: $PID)..."
        kill $PID
        rm "$LOGS_DIR/opena2.pid"
        echo "✅ opena2 stopped"
    else
        echo "⚠️  opena2 not running (stale PID file)"
        rm "$LOGS_DIR/opena2.pid"
    fi
else
    echo "⚠️  opena2 PID file not found"
fi

# Stop opena1
if [ -f "$LOGS_DIR/opena1.pid" ]; then
    PID=$(cat "$LOGS_DIR/opena1.pid")
    if kill -0 $PID 2>/dev/null; then
        echo "▶️  Stopping opena1 (PID: $PID)..."
        kill $PID
        rm "$LOGS_DIR/opena1.pid"
        echo "✅ opena1 stopped"
    else
        echo "⚠️  opena1 not running (stale PID file)"
        rm "$LOGS_DIR/opena1.pid"
    fi
else
    echo "⚠️  opena1 PID file not found"
fi

# Stop kordp
if [ -f "$LOGS_DIR/kordp.pid" ]; then
    PID=$(cat "$LOGS_DIR/kordp.pid")
    if kill -0 $PID 2>/dev/null; then
        echo "▶️  Stopping kordp (PID: $PID)..."
        kill $PID
        rm "$LOGS_DIR/kordp.pid"
        echo "✅ kordp stopped"
    else
        echo "⚠️  kordp not running (stale PID file)"
        rm "$LOGS_DIR/kordp.pid"
    fi
else
    echo "⚠️  kordp PID file not found"
fi

echo ""
echo "🟢 Portier 2.0 Stack stopped"
