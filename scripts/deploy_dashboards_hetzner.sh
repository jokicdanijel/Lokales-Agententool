#!/usr/bin/env bash
# ==============================================================================
# Deploy PORTIER Agent Dashboards to Hetzner Server
# Paketiert lokale Dashboards und deployt sie auf Hetzner Production
# ==============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OPENA20_DIR="$PROJECT_ROOT/19.opena20_dashboard_agent"
DASHBOARD_DIR="$OPENA20_DIR/data/dashboard_pages"

# Hetzner Config (aus .env oder als Parameter)
HETZNER_HOST="${HETZNER_HOST:-}"
HETZNER_USER="${HETZNER_USER:-root}"
HETZNER_PROJECT_PATH="${HETZNER_PROJECT_PATH:-/opt/Gesamtprojekt}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 PORTIER Dashboard Hetzner Deployment"
echo "========================================"

# Validierung
if [ -z "$HETZNER_HOST" ]; then
    echo -e "${RED}❌ HETZNER_HOST nicht gesetzt!${NC}"
    echo "   Exportiere: export HETZNER_HOST=your-server.com"
    echo "   Oder nutze .env: HETZNER_HOST=your-server.com"
    exit 1
fi

if [ ! -d "$DASHBOARD_DIR" ]; then
    echo -e "${RED}❌ Dashboard-Ordner nicht gefunden: $DASHBOARD_DIR${NC}"
    exit 1
fi

DASHBOARD_COUNT=$(ls -1 "$DASHBOARD_DIR"/*.html 2>/dev/null | wc -l)
if [ "$DASHBOARD_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Keine Dashboards gefunden in $DASHBOARD_DIR${NC}"
    echo "   Führe zuerst aus: python3 scripts/generate_agent_dashboards.py"
    exit 1
fi

echo -e "${GREEN}✓${NC} Gefunden: $DASHBOARD_COUNT Dashboards"

# Timestamp für eindeutige Archive
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TAR_NAME="portier_dashboards_${TIMESTAMP}.tar.gz"
TAR_PATH="/tmp/$TAR_NAME"

# 1. Paketieren
echo ""
echo "📦 Paketiere Dashboards..."
cd "$OPENA20_DIR"
tar -czf "$TAR_PATH" data/dashboard_pages/*.html
TAR_SIZE=$(du -h "$TAR_PATH" | cut -f1)
echo -e "${GREEN}✅${NC} Archiv erstellt: $TAR_PATH ($TAR_SIZE)"

# 2. Upload via SCP
echo ""
echo "📤 Upload zu Hetzner ($HETZNER_HOST)..."
scp "$TAR_PATH" "${HETZNER_USER}@${HETZNER_HOST}:/tmp/portier_dashboards.tar.gz"
echo -e "${GREEN}✅${NC} Upload abgeschlossen"

# 3. Remote Deployment
echo ""
echo "🔧 Deployment auf Hetzner..."
ssh "${HETZNER_USER}@${HETZNER_HOST}" <<EOSSH
set -e
echo "📂 Entpacke Dashboards..."
cd ${HETZNER_PROJECT_PATH}/19.opena20_dashboard_agent
tar -xzf /tmp/portier_dashboards.tar.gz -C .
echo "✅ Dashboards extrahiert"

echo "🔄 Starte opena20 neu..."
cd ${HETZNER_PROJECT_PATH}
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.prod.yml restart opena20
    echo "✅ opena20 (Docker Compose) neu gestartet"
elif command -v docker &> /dev/null && docker ps | grep -q opena20; then
    docker restart opena20
    echo "✅ opena20 (Docker) neu gestartet"
else
    # Fallback: systemd oder bin/ops.sh
    if [ -f bin/ops.sh ]; then
        bash bin/ops.sh restart opena20
        echo "✅ opena20 (ops.sh) neu gestartet"
    else
        echo "⚠️  Konnte opena20 nicht neu starten (kein Docker/ops.sh gefunden)"
    fi
fi

echo "🧹 Räume temporäre Dateien auf..."
rm -f /tmp/portier_dashboards.tar.gz
echo "✅ Cleanup abgeschlossen"
EOSSH

echo ""
echo -e "${GREEN}✅ Deployment erfolgreich abgeschlossen!${NC}"
echo ""
echo "🌐 Dashboards verfügbar unter:"
echo "   https://${HETZNER_HOST}:12349/  (Hauptdashboard)"
echo "   https://${HETZNER_HOST}:12349/agent/opena16  (Beispiel)"
echo ""
echo "🧹 Lokale Archivdatei löschen:"
echo "   rm $TAR_PATH"
