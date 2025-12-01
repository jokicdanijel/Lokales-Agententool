#!/usr/bin/env bash
# bin/start_all.sh — Start all ELION services (opena1-opena21)
# Usage: bash bin/start_all.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="$ROOT/logs"
PIDS_DIR="$ROOT/.runtime/pids"

mkdir -p "$LOGS_DIR" "$PIDS_DIR"

echo "🚀 Starting ELION Hyper-Dashboard Services..."
echo ""

# Core services (mandatory)
CORE_SERVICES=(
    "1.opena1&2_portier/opena1_app.py:12344:opena1"
    "1.opena1&2_portier/opena2_app.py:12345:opena2"
    "src/services/portier/main.py:12346:kordp"
)

# Extended services (optional)
EXTENDED_SERVICES=(
    "2.opena3_openwebui/main_openwebui_bridge_v2.py:12347:opena3"
    "src/services/telegram/main.py:12348:telegram"
    "5.opena6_browser/main.py:12349:browser"
    "6.opena7_email/main.py:12351:email"
    "7.opena8_whatsapp/main.py:12352:whatsapp"
    "8.opena9_telephone/main.py:12353:telephone"
)

STARTED=0
FAILED=0

start_service() {
    local service_path="$1"
    local port="$2"
    local name="$3"
    
    local full_path="$ROOT/$service_path"
    local log_file="$LOGS_DIR/${name}.nohup.log"
    local pid_file="$PIDS_DIR/${name}.pid"
    
    # Check if file exists
    if [ ! -f "$full_path" ]; then
        echo "  ⚠️  $name: File not found ($service_path)"
        return 1
    fi
    
    # Check if already running
    if lsof -i ":$port" > /dev/null 2>&1; then
        echo "  ✅ $name (port $port): Already running"
        return 0
    fi
    
    # Start service
    local service_dir="$(dirname "$full_path")"
    cd "$service_dir"
    
    nohup python3 "$(basename "$full_path")" > "$log_file" 2>&1 &
    local pid=$!
    echo "$pid" > "$pid_file"
    
    # Wait briefly to verify
    sleep 1
    
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "  ✅ $name (port $port) — PID $pid"
        return 0
    else
        echo "  ❌ $name (port $port): Failed to start"
        rm -f "$pid_file"
        return 1
    fi
}

echo "📍 Core Services:"
for service in "${CORE_SERVICES[@]}"; do
    IFS=':' read -r path port name <<< "$service"
    if start_service "$path" "$port" "$name"; then
        ((STARTED++))
    else
        ((FAILED++))
    fi
done

echo ""
echo "📍 Extended Services:"
for service in "${EXTENDED_SERVICES[@]}"; do
    IFS=':' read -r path port name <<< "$service"
    if start_service "$path" "$port" "$name"; then
        ((STARTED++))
    else
        ((FAILED++))
    fi
done

echo ""
echo "📊 Summary: $STARTED services started"

if [ "$FAILED" -gt 0 ]; then
    echo "   ⚠️  $FAILED services failed or skipped"
fi

echo ""
echo "✅ Stack startup complete!"
echo ""
echo "Next steps:"
echo "  • Check status: bin/ops.sh status"
echo "  • View logs:    bin/ops.sh logs"
echo "  • Register:     bin/ops.sh agents:register"
