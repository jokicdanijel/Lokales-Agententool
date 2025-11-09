#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# agents_auto_register.sh – Self-Healing Auto-Discovery & Registration
# 
# Liest echte Servicenamen aus /health, registriert nur laufende Agenten,
# validiert JSON-Responses, und gibt sichere Übersicht.
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─ Configuration ──────────────────────────────────────────────────────────
DASHBOARD_URL="${DASHBOARD_URL:-http://127.0.0.1:12349}"

# Token-Auflösung: Priority order
if [ -z "${TOKEN:-}" ]; then
  # Try: DASHBOARD_ADMIN_TOKEN
  if [ -f ".env" ]; then
    TOKEN=$(grep "^DASHBOARD_ADMIN_TOKEN=" .env 2>/dev/null | cut -d= -f2 || true)
  fi
  
  # Fallback: erster Wert in .env
  if [ -z "$TOKEN" ] && [ -f ".env" ]; then
    TOKEN=$(head -1 .env | cut -d= -f2 || true)
  fi
  
  # Ultimate fallback
  if [ -z "$TOKEN" ]; then
    TOKEN="MEIN_SUPER_TOKEN_123"
  fi
fi

# ─ Known ports (only active ones for now) ──────────────────────────────
PORTS=(12345 12346 12347 12349 12350 12351 12352 12353)

# Erweitert werden können später: 12344, 12354–12367

# ─ State variables ─────────────────────────────────────────────────────────
REGISTERED_COUNT=0
FAILED_COUNT=0
SKIPPED_COUNT=0

# ────────────────────────────────────────────────────────────────────────────
# Helper: safe jq parse (no error on malformed JSON)
# ────────────────────────────────────────────────────────────────────────────
safe_jq() {
  local json="$1"
  local path="${2:-.}"
  echo "$json" | jq -r "$path // empty" 2>/dev/null || true
}

# ────────────────────────────────────────────────────────────────────────────
# Main Discovery Loop
# ────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Auto-Discovery & Registration – $(date +'%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Dashboard: ${DASHBOARD_URL}"
echo -e "Token:     ${TOKEN:0:20}... (length: ${#TOKEN})"
echo ""
echo -e "${YELLOW}Scanning ports: ${PORTS[*]}${NC}"
echo ""

# Collect endpoints
declare -A FOUND_ENDPOINTS

for PORT in "${PORTS[@]}"; do
  # Try /health with 2s timeout (was 1s, too aggressive)
  HEALTH_RESPONSE=$(curl -sS --max-time 2 "http://127.0.0.1:${PORT}/health" 2>/dev/null || true)
  
  # Empty response = not listening
  if [ -z "$HEALTH_RESPONSE" ]; then
    echo -e "${YELLOW}•${NC} Port ${PORT}: no response"
    ((SKIPPED_COUNT++))
    continue
  fi

  # Extract service name safely (handle JSON errors gracefully)
  SERVICE_NAME=$(echo "$HEALTH_RESPONSE" | jq -r '.service // empty' 2>/dev/null || true)
  
  if [ -z "$SERVICE_NAME" ]; then
    echo -e "${YELLOW}•${NC} Port ${PORT}: invalid or missing .service"
    ((SKIPPED_COUNT++))
    continue
  fi

  # Normalize agent_id: lowercase, replace spaces/slashes with _
  AGENT_ID=$(echo "$SERVICE_NAME" | tr '[:upper:]' '[:lower:]' | tr '[:space:]/' '_' | sed 's/_$//')
  
  # Store for batch registration
  FOUND_ENDPOINTS["$AGENT_ID"]="http://127.0.0.1:${PORT}"
  
  echo -e "${GREEN}✓${NC} Port ${PORT}: ${SERVICE_NAME} → agent_id='${AGENT_ID}'"
done

echo ""
echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}   Registration Phase${NC}"
echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
echo ""

# Register each endpoint
for AGENT_ID in "${!FOUND_ENDPOINTS[@]}"; do
  ENDPOINT="${FOUND_ENDPOINTS[$AGENT_ID]}"
  
  # POST /api/agent/register
  REGISTER_RESPONSE=$(curl -sS -X POST "${DASHBOARD_URL}/api/agent/register" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"agent_id\":\"${AGENT_ID}\",\"endpoint\":\"${ENDPOINT}\"}" 2>/dev/null || true)
  
  # Validate response
  REGISTERED_AGENT=$(safe_jq "$REGISTER_RESPONSE" '.agent // empty')
  
  if [ -n "$REGISTERED_AGENT" ]; then
    echo -e "${GREEN}✓${NC} Registered: ${AGENT_ID} → ${ENDPOINT}"
    ((REGISTERED_COUNT++))
  else
    echo -e "${RED}✗${NC} Failed: ${AGENT_ID} → ${ENDPOINT}"
    echo "  Response: ${REGISTER_RESPONSE:0:150}..."
    ((FAILED_COUNT++))
  fi
done

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Registry Snapshot${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Fetch and display registry
REGISTRY=$(curl -sS -H "Authorization: Bearer ${TOKEN}" \
  "${DASHBOARD_URL}/api/agent/list" 2>/dev/null || true)

AGENT_COUNT=$(safe_jq "$REGISTRY" '.agents | length // 0')
echo -e "Total agents in registry: ${GREEN}${AGENT_COUNT}${NC}"
echo ""

# Pretty-print agents
if [ "$AGENT_COUNT" -gt 0 ]; then
  echo "Agents:"
  safe_jq "$REGISTRY" '.agents | to_entries | .[] | "\(.value.agent_id) → \(.value.endpoint) (registered: \(.value.registered_at))"' | \
    sed 's/^/  /'
else
  echo -e "${YELLOW}(no agents found)${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Status Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Quick status check
STATUS=$(curl -sS -H "Authorization: Bearer ${TOKEN}" \
  "${DASHBOARD_URL}/api/status/all" 2>/dev/null || true)

UP_COUNT=$(safe_jq "$STATUS" '.agents | to_entries | map(select(.value.status == "up")) | length // 0')
DOWN_COUNT=$(safe_jq "$STATUS" '.agents | to_entries | map(select(.value.status == "down")) | length // 0')

echo -e "Agents Up:   ${GREEN}${UP_COUNT}${NC}"
echo -e "Agents Down: ${RED}${DOWN_COUNT}${NC}"
echo ""

# Summary stats
echo -e "${BLUE}Summary:${NC}"
echo -e "  Scanned ports:     ${#PORTS[@]}"
echo -e "  Found & listening: ${GREEN}$(( ${#FOUND_ENDPOINTS[@]} ))${NC}"
echo -e "  Registered:        ${GREEN}${REGISTERED_COUNT}${NC}"
echo -e "  Failed:            ${RED}${FAILED_COUNT}${NC}"
echo -e "  Skipped:           ${YELLOW}${SKIPPED_COUNT}${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

# Exit code based on results
if [ "$REGISTERED_COUNT" -eq 0 ]; then
  echo -e "${YELLOW}⚠ No agents were registered. Check ports and Dashboard.${NC}"
  exit 1
fi

if [ "$FAILED_COUNT" -gt 0 ]; then
  echo -e "${YELLOW}⚠ Some registrations failed, but ${REGISTERED_COUNT} succeeded.${NC}"
  exit 0
fi

echo -e "${GREEN}✓ Auto-Discovery & Registration complete.${NC}"
exit 0
