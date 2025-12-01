#!/bin/bash
# 📧 Email Agent 6.0 - Start Script (PORTIER PAS-6.0)

set -euo pipefail

AGENT_DIR="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/6.opena7_email"
AGENT_NAME="opena7_email"
PORT=12351
PID_FILE="$AGENT_DIR/pids/${AGENT_NAME}.pid"
LOG_FILE="$AGENT_DIR/logs/${AGENT_NAME}.nohup.log"
ENV_FILE="$AGENT_DIR/.env"

echo "🚀 Starting Email Agent 6.0 on port $PORT..."

# Create necessary directories
mkdir -p "$AGENT_DIR/pids" "$AGENT_DIR/logs"

# Check if already running
if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ Email Agent is already running (PID: $PID)"
        exit 1
    else
        echo "🧹 Removing stale PID file"
        rm -f "$PID_FILE"
    fi
fi

# Check port availability
if netstat -tuln | grep -q ":$PORT "; then
    echo "❌ Port $PORT is already in use"
    exit 1
fi

# Verify Python environment
cd "$AGENT_DIR"
if [[ ! -f "main_email_agent.py" ]]; then
    echo "❌ main_email_agent.py not found in $AGENT_DIR"
    exit 1
fi

# Check environment file
if [[ ! -f "$ENV_FILE" ]]; then
    echo "⚠️ No .env file found. Creating template..."
    cat > "$ENV_FILE" << 'EOF'
# Email Agent 6.0 Configuration
OPENAI_API_KEY=your_openai_api_key_here
BEARER_TOKEN=your_bearer_token_here

# Email Settings
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Agent Settings
AGENT_PORT=12351
DEBUG_MODE=false
LOG_LEVEL=INFO

# Performance
MAX_EMAILS_PER_REQUEST=50
AI_TIMEOUT=30
RATE_LIMIT=100
EOF
    echo "📝 Created .env template. Please configure it before starting the agent."
    exit 1
fi

echo "🔧 Checking Python dependencies..."
python3 -m pip install -q -r requirements.txt

echo "🌟 Starting Email Agent 6.0..."
nohup python3 -m uvicorn main_email_agent:app \
    --host 127.0.0.1 \
    --port "$PORT" \
    --log-level info \
    > "$LOG_FILE" 2>&1 &

# Get PID and save it
PID=$!
echo "$PID" > "$PID_FILE"

echo "✅ Email Agent 6.0 started successfully!"
echo "   PID: $PID"
echo "   Port: $PORT"
echo "   Log: $LOG_FILE"
echo "   Dashboard: http://127.0.0.1:$PORT/html/index.html"

# Wait a moment and check if it's actually running
sleep 2
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "❌ Agent failed to start. Check logs:"
    tail -20 "$LOG_FILE"
    exit 1
fi

echo "🎯 Email Agent 6.0 is ready for email automation!"