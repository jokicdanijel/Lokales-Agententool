#!/bin/bash
echo "✅ QUICK HEALTH CHECK - All 12 Ports"
echo "════════════════════════════════════════════════════════"

TOKEN="MEIN_SUPER_TOKEN_123"
HEALTHY=0

for port in 12344 12345 12346 12347 12348 12349 12353 12354 12355 12356 12357 12358; do
    if curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:$port/health" 2>/dev/null | jq -e '.status == "healthy"' > /dev/null 2>&1; then
        echo "✅ Port $port: HEALTHY"
        ((HEALTHY++))
    else
        echo "⏳ Port $port: checking..."
    fi
done

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ Status: $HEALTHY/12 services healthy"
echo "════════════════════════════════════════════════════════"
