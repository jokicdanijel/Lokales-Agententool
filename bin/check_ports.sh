#!/usr/bin/env bash
# bin/check_ports.sh — Check port allocation
# Usage: bash bin/check_ports.sh

set -euo pipefail

echo "🔍 ELION Port Allocation Check"
echo ""

# Backend ports (12344-12399)
echo "📍 Backend Services (Policy: 12344-12399):"
for port in {12344..12350}; do
    if lsof -i ":$port" > /dev/null 2>&1; then
        process=$(lsof -i ":$port" -t | head -1)
        name=$(ps -p "$process" -o comm= 2>/dev/null || echo "unknown")
        echo "  ✅ Port $port — In use ($name, PID $process)"
    else
        echo "  ⚪ Port $port — Available"
    fi
done

# OpenWebUI (8080 - UI only)
echo ""
echo "📍 OpenWebUI (UI-only port):"
if lsof -i ":8080" > /dev/null 2>&1; then
    process=$(lsof -i ":8080" -t | head -1)
    name=$(ps -p "$process" -o comm= 2>/dev/null || echo "unknown")
    echo "  ✅ Port 8080 — In use ($name, PID $process)"
else
    echo "  ⚪ Port 8080 — Available"
fi

echo ""
echo "✅ Port check complete"
