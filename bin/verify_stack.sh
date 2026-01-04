#!/usr/bin/env bash
# bin/verify_stack.sh — Verify ELION stack health
# Usage: bash bin/verify_stack.sh

set -euo pipefail

echo "🔍 Verifying ELION Hyper-Dashboard Stack..."
echo ""

# Core services health endpoints
SERVICES=(
    "opena1:12344:/health"
    "opena2:12345:/health"
    "kordp:12346:/health"
    "opena3:12347:/health"
    "telegram:12346:/health"
)

PASSED=0
FAILED=0

echo "📍 Health Checks:"
for service in "${SERVICES[@]}"; do
    IFS=':' read -r name port endpoint <<< "$service"

    url="http://127.0.0.1:${port}${endpoint}"

    if response=$(curl -s -f "$url" 2>&1); then
        echo "  ✅ $name ($port) — OK"
        ((PASSED++))
    else
        echo "  ❌ $name ($port) — FAILED"
        ((FAILED++))
    fi
done

echo ""
echo "📊 Health Check Results: $PASSED passed, $FAILED failed"

# Port checks
echo ""
echo "📍 Port Allocation:"
for port in 12344 12345 12346 12347; do
    if lsof -i ":$port" > /dev/null 2>&1; then
        echo "  ✅ Port $port — In use"
    else
        echo "  ⚠️  Port $port — Available (service not running)"
    fi
done

# Safepoint check
echo ""
echo "📍 Archivator (Safepoints):"
ARCHIVP_STORE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/archivp_store"
INDEX_FILE="$ARCHIVP_STORE/index.jsonl"

if [ -f "$INDEX_FILE" ]; then
    count=$(wc -l < "$INDEX_FILE")
    echo "  ✅ Index: $count safepoints"

    latest_dir=$(find "$ARCHIVP_STORE" -type d -name "[0-9][0-9]" | sort -r | head -1)
    if [ -n "$latest_dir" ]; then
        latest_count=$(find "$latest_dir" -name "SP*.json" 2>/dev/null | wc -l)
        echo "  ✅ Latest: $latest_count files in $(basename "$latest_dir")"
    fi
else
    echo "  ❌ Index not found: $INDEX_FILE"
    ((FAILED++))
fi

# ENV check
echo ""
echo "📍 Environment:"
if [ -f ".env" ]; then
    echo "  ✅ .env file present"

    if grep -q "OPENAI_API_KEY=" .env; then
        echo "  ✅ OPENAI_API_KEY configured"
    else
        echo "  ⚠️  OPENAI_API_KEY missing"
    fi
else
    echo "  ⚠️  .env file not found (optional)"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
    echo "✅ Stack verification PASSED!"
    exit 0
else
    echo "❌ Stack verification FAILED ($FAILED issues)"
    exit 1
fi
