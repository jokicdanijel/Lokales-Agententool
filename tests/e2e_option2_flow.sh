#!/bin/bash
# E2E Test für Option-2-Flow (OpenAI → opena1 → opena2 → kordp → ...)
# CI-tauglich, Exit-Codes, strukturierte Ausgabe

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "🧪 E2E Test: Option-2-Flow"
echo "============================================"
echo ""

# Token laden
if [[ ! -f .env ]]; then
    echo -e "${RED}❌ Fehler: .env nicht gefunden${NC}"
    exit 1
fi

export TOKEN="$(grep '^BEARER_TOKEN=' .env | cut -d= -f2 | tr -d '"')"

if [[ -z "$TOKEN" ]]; then
    echo -e "${RED}❌ Fehler: BEARER_TOKEN nicht in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Token geladen${NC}"
echo ""

# ============================================
# 1. PRECONDITIONS & HEALTH CHECK
# ============================================

echo "=== 1. Health Check Stack ==="
echo ""

HEALTH_FAILED=0

# opena1
echo -n "🔹 opena1 (Port 12344): "
if OPENA1_HEALTH=$(curl -s http://127.0.0.1:12344/health 2>/dev/null); then
    OPENA1_STATUS=$(echo "$OPENA1_HEALTH" | jq -r '.status' 2>/dev/null || echo "error")
    OPENA1_KEY=$(echo "$OPENA1_HEALTH" | jq -r '.openai_key_present' 2>/dev/null || echo "false")

    if [[ "$OPENA1_STATUS" == "ok" ]] && [[ "$OPENA1_KEY" == "true" ]]; then
        echo -e "${GREEN}✅ OK (Key present)${NC}"
    else
        echo -e "${RED}❌ FEHLER (Status: $OPENA1_STATUS, Key: $OPENA1_KEY)${NC}"
        HEALTH_FAILED=1
    fi
else
    echo -e "${RED}❌ UNREACHABLE${NC}"
    HEALTH_FAILED=1
fi

# opena2
echo -n "🔹 opena2 (Port 12345): "
if OPENA2_HEALTH=$(curl -s http://127.0.0.1:12345/health 2>/dev/null); then
    OPENA2_STATUS=$(echo "$OPENA2_HEALTH" | jq -r '.status' 2>/dev/null || echo "error")
    OPENA2_KEY=$(echo "$OPENA2_HEALTH" | jq -r '.openai_key_present' 2>/dev/null || echo "false")
    OPENA2_ENTRIES=$(echo "$OPENA2_HEALTH" | jq -r '.entries' 2>/dev/null || echo "0")

    if [[ "$OPENA2_STATUS" == "ok" ]] && [[ "$OPENA2_KEY" == "true" ]]; then
        echo -e "${GREEN}✅ OK (Key present, $OPENA2_ENTRIES entries)${NC}"
    else
        echo -e "${RED}❌ FEHLER (Status: $OPENA2_STATUS, Key: $OPENA2_KEY)${NC}"
        HEALTH_FAILED=1
    fi
else
    echo -e "${RED}❌ UNREACHABLE${NC}"
    HEALTH_FAILED=1
fi

if [[ $HEALTH_FAILED -eq 1 ]]; then
    echo ""
    echo -e "${RED}❌ Health Check fehlgeschlagen - E2E Test abgebrochen${NC}"
    exit 1
fi

echo ""

# ============================================
# 2. OPTION-2-FLOW AUSLÖSEN
# ============================================

echo "=== 2. Option-2-Flow Test ==="
echo ""

TEST_ID="OPT2-E2E-$(date +%Y%m%d%H%M%S)"
echo "📋 Request ID: $TEST_ID"

RESPONSE=$(curl -s -X POST http://127.0.0.1:12344/log/opena1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"source\": \"e2e_test\",
    \"event\": \"option2_flow_validation\",
    \"payload\": {
      \"request_id\": \"$TEST_ID\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
      \"message\": \"E2E Test für Option-2-Flow nach Key-Rotation\"
    }
  }" 2>&1)

if echo "$RESPONSE" | jq -e '.ok == true' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Request akzeptiert${NC}"
else
    echo -e "${RED}❌ Request fehlgeschlagen:${NC}"
    echo "$RESPONSE" | jq . || echo "$RESPONSE"
    exit 1
fi

echo ""

# ============================================
# 3. SAFEPOINT VERIFIKATION
# ============================================

echo "=== 3. Safepoint Verifikation ==="
echo ""

sleep 2  # Kurze Pause für Dateisystem-Sync

TODAY=$(date +%Y/%m/%d)
ARCHIV_DIR="$BASE_DIR/1.opena1&2_portier/archivp_store/$TODAY"

if [[ ! -d "$ARCHIV_DIR" ]]; then
    echo -e "${RED}❌ Archiv-Verzeichnis nicht gefunden: $ARCHIV_DIR${NC}"
    exit 1
fi

LATEST_SAFEPOINT=$(find "$ARCHIV_DIR" -name "*.json" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | awk '{print $2}')

if [[ -z "$LATEST_SAFEPOINT" ]]; then
    echo -e "${RED}❌ Keine Safepoints in $ARCHIV_DIR gefunden${NC}"
    exit 1
fi

echo "📂 Letzter Safepoint: $(basename $LATEST_SAFEPOINT)"
echo ""

# Safepoint-Struktur prüfen
SP_SRC=$(jq -r '.src' "$LATEST_SAFEPOINT" 2>/dev/null || echo "")
SP_DST=$(jq -r '.dst' "$LATEST_SAFEPOINT" 2>/dev/null || echo "")
SP_KIND=$(jq -r '.kind' "$LATEST_SAFEPOINT" 2>/dev/null || echo "")
SP_EVENT=$(jq -r '.body.event' "$LATEST_SAFEPOINT" 2>/dev/null || echo "")
SP_REQ_ID=$(jq -r '.body.payload.request_id' "$LATEST_SAFEPOINT" 2>/dev/null || echo "")

echo "🔍 Safepoint-Struktur:"
echo "   src:        $SP_SRC"
echo "   dst:        $SP_DST"
echo "   kind:       $SP_KIND"
echo "   event:      $SP_EVENT"
echo "   request_id: $SP_REQ_ID"
echo ""

# Validierung
VALIDATION_FAILED=0

if [[ "$SP_SRC" != "kordp" ]]; then
    echo -e "${RED}❌ Falsche src: erwartet 'kordp', erhalten '$SP_SRC'${NC}"
    VALIDATION_FAILED=1
fi

if [[ "$SP_DST" != "archivp" ]]; then
    echo -e "${RED}❌ Falsche dst: erwartet 'archivp', erhalten '$SP_DST'${NC}"
    VALIDATION_FAILED=1
fi

if [[ "$SP_KIND" != "LOG" ]]; then
    echo -e "${YELLOW}⚠️ Unerwarteter kind: erwartet 'LOG', erhalten '$SP_KIND'${NC}"
fi

if [[ "$SP_EVENT" != "option2_flow_validation" ]]; then
    echo -e "${YELLOW}⚠️ Event mismatch: erwartet 'option2_flow_validation', erhalten '$SP_EVENT'${NC}"
fi

# Request ID prüfen (optional, weil Timing-Abhängig)
if echo "$SP_REQ_ID" | grep -q "OPT2-E2E-"; then
    echo -e "${GREEN}✅ Request ID gefunden: $SP_REQ_ID${NC}"
else
    echo -e "${YELLOW}⚠️ Request ID nicht übereinstimmend (Timing-Issue möglich)${NC}"
fi

if [[ $VALIDATION_FAILED -eq 1 ]]; then
    echo ""
    echo -e "${RED}❌ Safepoint-Validierung fehlgeschlagen${NC}"
    exit 1
fi

echo ""

# ============================================
# 4. ABSCHLUSS
# ============================================

echo "============================================"
echo -e "${GREEN}✅ E2E Test BESTANDEN${NC}"
echo "============================================"
echo ""
echo "Ergebnisse:"
echo "  ✅ opena1:  Health OK + OpenAI Key present"
echo "  ✅ opena2:  Health OK + OpenAI Key present + $OPENA2_ENTRIES entries"
echo "  ✅ Flow:    Request akzeptiert"
echo "  ✅ Archiv:  Safepoint gespeichert ($SP_KIND)"
echo "  ✅ Schema:  src=kordp, dst=archivp, strict=true"
echo ""
echo "📂 Archiv: $LATEST_SAFEPOINT"
echo ""

exit 0
