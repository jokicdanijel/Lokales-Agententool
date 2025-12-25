#!/usr/bin/env bash
# bin/start_20_services.sh — Start 20 scalable services via nohup
# Usage: bash bin/start_20_services.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICES_DIR="$ROOT/src/services"
LOGS_DIR="$ROOT/logs"

# Service definitions (name, port)
declare -A SERVICES=(
    [portier]=12344
    [archivator]=12345
    [telegram]=12346
    [inference]=12348
    [browser]=12349
    [vscode]=12350
    [email]=12351
    [whatsapp]=12352
    [phone]=12353
    [calendar]=12354
    [social_media]=12355
    [shop]=12356
    [html_creator]=12357
    [homepage_creator]=12358
    [stocks_crypto]=12359
    [influencer]=12360
    [unlock_master]=12361
    [local_archiv]=12362
    [custom_1]=12363
    [custom_2]=12364
)

mkdir -p "$LOGS_DIR"

echo "🚀 Starting 20 ELION Services..."
echo ""

STARTED=0
FAILED=0

for service in "${!SERVICES[@]}"; do
    port=${SERVICES[$service]}
    service_path="$SERVICES_DIR/$service"

    if [ ! -f "$service_path/main.py" ]; then
        echo "  ❌ $service: main.py not found"
        ((FAILED++))
        continue
    fi

    log_file="$LOGS_DIR/${service}.nohup.log"

    # Check if already running
    if lsof -i ":$port" > /dev/null 2>&1; then
        echo "  ⚠️  $service (port $port): Already running"
        ((STARTED++))
        continue
    fi

    # Start service
    cd "$service_path"
    nohup python3 main.py > "$log_file" 2>&1 &
    PID=$!

    # Wait briefly to verify
    sleep 0.5

    if ps -p "$PID" > /dev/null 2>&1; then
        echo "  ✅ $service (port $port) — PID $PID"
        ((STARTED++))
    else
        echo "  ❌ $service (port $port): Failed to start"
        ((FAILED++))
    fi
done

echo ""
echo "📊 Summary: $STARTED/$((${#SERVICES[@]})) services started"

if [ "$FAILED" -gt 0 ]; then
    echo "   ⚠️  $FAILED services failed"
fi

echo ""
echo "📍 Service Health Check:"
for service in "${!SERVICES[@]}"; do
    port=${SERVICES[$service]}
    if curl -s "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
        echo "  ✅ $service"
    fi
done | head -10

echo ""
echo "✅ Production deployment complete!"
