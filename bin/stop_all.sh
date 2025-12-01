#!/usr/bin/env bash
# bin/stop_all.sh — Stop all ELION services
# Usage: bash bin/stop_all.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIDS_DIR="$ROOT/.runtime/pids"

if [ ! -d "$PIDS_DIR" ]; then
    echo "⚠️  No PID directory found. Services may not be running."
    exit 0
fi

echo "🛑 Stopping ELION services..."
echo ""

STOPPED=0
FAILED=0

for pid_file in "$PIDS_DIR"/*.pid; do
    [ -f "$pid_file" ] || continue
    
    service_name="$(basename "$pid_file" .pid)"
    pid="$(cat "$pid_file")"
    
    if ps -p "$pid" > /dev/null 2>&1; then
        kill "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
        
        # Wait for process to stop
        for i in {1..10}; do
            if ! ps -p "$pid" > /dev/null 2>&1; then
                echo "  ✅ $service_name (PID $pid) stopped"
                rm -f "$pid_file"
                ((STOPPED++))
                break
            fi
            sleep 0.5
        done
        
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "  ❌ $service_name (PID $pid) failed to stop"
            ((FAILED++))
        fi
    else
        echo "  ⚠️  $service_name: Process not found (cleaning PID file)"
        rm -f "$pid_file"
    fi
done

echo ""
echo "📊 Summary: $STOPPED services stopped"

if [ "$FAILED" -gt 0 ]; then
    echo "   ⚠️  $FAILED services failed to stop"
fi

echo ""
echo "✅ Shutdown complete!"
