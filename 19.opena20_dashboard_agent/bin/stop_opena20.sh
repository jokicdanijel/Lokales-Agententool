#!/bin/bash
# Stop opena20 Dashboard Agent

cd "$(dirname "$0")/.." || exit 1

if [ -f logs/opena20.pid ]; then
    PID=$(cat logs/opena20.pid)
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f logs/opena20.pid
        echo "✅ opena20 stopped (PID: $PID)"
    else
        rm -f logs/opena20.pid
        echo "⚠️ opena20 was not running"
    fi
else
    echo "⚠️ No PID file found"
fi
