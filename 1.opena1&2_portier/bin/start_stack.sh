#!/bin/bash
# Start Portier 2.0 Stack (opena2 + opena1 + kordp)
# LOCATION: /home/danijel-jd/.../1.opena1&2_portier/bin/start_stack.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$PROJECT_DIR/logs"
VENV_PYTHON="$PROJECT_DIR/venv313/bin/python3"

mkdir -p "$LOGS_DIR"

echo "🚀 Starting Portier 2.0 Stack..."

# Check if services are already running
if pgrep -f "opena2_app.py" > /dev/null; then
    echo "⚠️  opena2 already running"
else
    echo "▶️  Starting opena2 (Port 12345)..."
    cd "$PROJECT_DIR"
    nohup "$VENV_PYTHON" opena2_app.py > "$LOGS_DIR/opena2.log" 2>&1 &
    echo $! > "$LOGS_DIR/opena2.pid"
    sleep 2
    echo "✅ opena2 started (PID: $(cat $LOGS_DIR/opena2.pid))"
fi

if pgrep -f "main_production.py --port 12344" > /dev/null; then
    echo "⚠️  opena1 already running"
else
    echo "▶️  Starting opena1 (Port 12344)..."
    cd "$PROJECT_DIR"
    nohup "$VENV_PYTHON" main_production.py --port 12344 > "$LOGS_DIR/opena1.log" 2>&1 &
    echo $! > "$LOGS_DIR/opena1.pid"
    sleep 2
    echo "✅ opena1 started (PID: $(cat $LOGS_DIR/opena1.pid))"
fi

if pgrep -f "kordp.main_production --port 12346" > /dev/null; then
    echo "⚠️  kordp already running"
else
    echo "▶️  Starting kordp (Port 12346)..."
    cd "$PROJECT_DIR"
    nohup "$VENV_PYTHON" -m kordp.main_production --port 12346 > "$LOGS_DIR/kordp.log" 2>&1 &
    echo $! > "$LOGS_DIR/kordp.pid"
    sleep 2
    echo "✅ kordp started (PID: $(cat $LOGS_DIR/kordp.pid))"
fi

echo ""
echo "🟢 Portier 2.0 Stack running:"
echo "   opena2 (Archivator) → http://127.0.0.1:12345"
echo "   opena1 (Coordinator) → http://127.0.0.1:12344"
echo "   kordp (Gateway) → http://127.0.0.1:12346"
echo ""
echo "📊 Check status:"
echo "   curl -s http://127.0.0.1:12345/health | jq ."
echo "   curl -s http://127.0.0.1:12344/health | jq ."
echo "   curl -s http://127.0.0.1:12346/health | jq ."
echo ""
echo "📝 View logs:"
echo "   tail -f $LOGS_DIR/opena2.log"
echo "   tail -f $LOGS_DIR/opena1.log"
echo "   tail -f $LOGS_DIR/kordp.log"
echo ""
echo "🛑 Stop stack:"
echo "   $SCRIPT_DIR/stop_stack.sh"
