#!/usr/bin/env bash
# Health Check – Verify Port-Policy Standardization
# Checks all 4 core services for compliant health endpoints

set -u

SERVICES=(
  "opena1:12344"
  "kordp:12346"
  "archivp:12348"
  "opena2:12348"
)

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Health Check – Port-Policy Standardization              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

PASSED=0
FAILED=0

for service_def in "${SERVICES[@]}"; do
  SERVICE_NAME="${service_def%%:*}"
  PORT="${service_def##*:}"

  echo "Testing: $SERVICE_NAME (port $PORT)..."

  RESPONSE=$(curl -s -m 2 "http://127.0.0.1:$PORT/health" 2>/dev/null || echo "")

  if [ -z "$RESPONSE" ]; then
    echo "  ❌ NOT RESPONDING (service not running or port unreachable)"
    FAILED=$((FAILED + 1))
    echo ""
    continue
  fi

  # Extract port_policy
  WINDOW=$(echo "$RESPONSE" | jq -r '.port_policy.window?' 2>/dev/null || echo "")
  FORBIDDEN=$(echo "$RESPONSE" | jq -r '.port_policy.forbidden?' 2>/dev/null || echo "")

  if [ "$WINDOW" == "[12344,12399]" ] || [ "$WINDOW" == "[ 12344, 12399 ]" ]; then
    echo "  ✅ port_policy.window: $WINDOW"
    PASSED=$((PASSED + 1))
  else
    echo "  ⚠️  port_policy.window: $WINDOW (expected [12344,12399])"
    FAILED=$((FAILED + 1))
  fi

  if echo "$FORBIDDEN" | grep -q "8080"; then
    echo "  ✅ port_policy.forbidden: $FORBIDDEN"
  else
    echo "  ⚠️  port_policy.forbidden: $FORBIDDEN (expected [8080])"
  fi

  echo "  Raw response: $RESPONSE" | head -1
  echo ""
done

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                      SUMMARY                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo "Passed: $PASSED/4"
echo "Failed: $FAILED/4"

if [ $FAILED -eq 0 ]; then
  echo "Status: ✅ All services compliant"
  exit 0
else
  echo "Status: ⚠️  Some services not responding (start them with bin/ops.sh start <service>)"
  exit 1
fi
