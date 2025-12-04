#!/bin/bash
# Start opena20 Dashboard Agent
# Port: 12349

cd "$(dirname "$0")/.." || exit 1
source venv313/bin/activate 2>/dev/null || true

export OPENA20_PORT=12349
export BEARER_TOKEN="${BEARER_TOKEN:-c899b90d-faf8-485b-afa4-078357cf5313}"

mkdir -p logs data

echo "🚀 Starting opena20 Dashboard Agent on port 12349..."
nohup python3 main_dashboard.py > logs/opena20.nohup.log 2>&1 &
echo $! > logs/opena20.pid
echo "✅ opena20 started (PID: $(cat logs/opena20.pid))"
