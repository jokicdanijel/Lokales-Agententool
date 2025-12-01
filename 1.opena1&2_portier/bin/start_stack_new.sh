#!/bin/bash
# Portier 2.0 Stack Starter (opena2 + opena1 + kordp)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOGS_DIR"

# ---- VENV AUTOMATISCH FINDEN ----
if [ -d "$PROJECT_DIR/venv313" ]; then
    VENV_PYTHON="$PROJECT_DIR/venv313/bin/python3"
elif [ -d "$PROJECT_DIR/venv312" ]; then
    VENV_PYTHON="$PROJECT_DIR/venv312/bin/python3"
else
    echo "❌ Kein venv gefunden! Erwartet: $PROJECT_DIR/venv313"
    exit 1
fi

echo "🔧 Using Python: $VENV_PYTHON"
echo "🚀 Starting Portier 2.0 Stack..."

# ---- opena2 ----
if pgrep -f "opena2_app.py" >/dev/null; then
    echo "⚠️  opena2 already running"
else
    echo "▶️  Starting opena2 (Port 12345)..."
    cd "$PROJECT_DIR"
    nohup "$VENV_PYTHON" opena2_app.py > "$LOGS_DIR/opena2.log" 2>&1 &
    echo $! > "$LOGS_DIR/opena2.pid"
    sleep 2
    echo "✅ opena2 started (PID: $(cat $LOGS_DIR/opena2.pid 2>/dev/null || echo 'N/A'))"
fi

# ---- opena1 ----
if pgrep -f "main_production.py --port 12344" >/dev/null; then
    echo "⚠️  opena1 already running"
else
    echo "▶️  Starting opena1 (Port 12344)..."
    cd "$PROJECT_DIR"
    nohup "$VENV_PYTHON" main_production.py --port 12344 > "$LOGS_DIR/opena1.log" 2>&1 &
    echo $! > "$LOGS_DIR/opena1.pid"
    sleep 2
    echo "✅ opena1 started (PID: $(cat $LOGS_DIR/opena1.pid 2>/dev/null || echo 'N/A'))"
fi

# ---- kordp ----
if pgrep -f "kordp.main_production --port 12346" >/dev/null; then
    echo "⚠️  kordp already running"
else
    echo "▶️  Starting kordp (Port 12346)..."
    cd "$PROJECT_DIR"
    nohup "$VENV_PYTHON" -m kordp.main_production --port 12346 > "$LOGS_DIR/kordp.log" 2>&1 &
    echo $! > "$LOGS_DIR/kordp.pid"
    sleep 2
    echo "✅ kordp started (PID: $(cat $LOGS_DIR/kordp.pid 2>/dev/null || echo 'N/A'))"
fi

echo ""
echo "🟢 Portier 2.0 Stack running:"
echo "   opena2 → http://127.0.0.1:12345"
echo "   opena1 → http://127.0.0.1:12344"
echo "   kordp  → http://127.0.0.1:12346"
echo ""
echo "📊 Status:"
echo "   curl -s http://127.0.0.1:12345/health | jq ."
echo "   curl -s http://127.0.0.1:12344/health | jq ."
echo "   curl -s http://127.0.0.1:12346/health | jq ."
echo ""
echo "📝 Logs:"
echo "   tail -f $LOGS_DIR/opena2.log"
echo "   tail -f $LOGS_DIR/opena1.log"
echo "   tail -f $LOGS_DIR/kordp.log"
