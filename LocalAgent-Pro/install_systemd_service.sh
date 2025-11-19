#!/bin/bash
# Install LocalAgent-Pro systemd service

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 LocalAgent-Pro Systemd Service Installation"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Bitte als root ausführen (sudo ./install_systemd_service.sh)${NC}"
    exit 1
fi

# Get actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
echo -e "${YELLOW}📋 Installation für User: ${ACTUAL_USER}${NC}"

# Get project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_FILE="${PROJECT_DIR}/config/localagent-pro.service"

echo -e "${YELLOW}📁 Projekt-Verzeichnis: ${PROJECT_DIR}${NC}"

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}❌ Service-Datei nicht gefunden: ${SERVICE_FILE}${NC}"
    exit 1
fi

# Update service file with correct paths
echo -e "${GREEN}🔧 Aktualisiere Service-Datei mit korrekten Pfaden...${NC}"

# Create temporary service file
TMP_SERVICE="/tmp/localagent-pro.service"
cp "$SERVICE_FILE" "$TMP_SERVICE"

# Replace placeholders
sed -i "s|User=.*|User=${ACTUAL_USER}|g" "$TMP_SERVICE"
sed -i "s|Group=.*|Group=${ACTUAL_USER}|g" "$TMP_SERVICE"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=${PROJECT_DIR}|g" "$TMP_SERVICE"

# Find venv path
VENV_PATH=""
if [ -d "${PROJECT_DIR}/../venv" ]; then
    VENV_PATH="${PROJECT_DIR}/../venv/bin/python"
elif [ -d "${PROJECT_DIR}/.venv" ]; then
    VENV_PATH="${PROJECT_DIR}/.venv/bin/python"
else
    echo -e "${RED}❌ Virtual Environment nicht gefunden!${NC}"
    echo "Bitte venv erstellen: python3 -m venv venv"
    exit 1
fi

sed -i "s|ExecStart=.*|ExecStart=${VENV_PATH} -m flask run --host=0.0.0.0 --port=8001|g" "$TMP_SERVICE"
sed -i "s|ReadWritePaths=.*sandbox|ReadWritePaths=${PROJECT_DIR}/sandbox|g" "$TMP_SERVICE"
sed -i "s|ReadWritePaths=.*logs|ReadWritePaths=${PROJECT_DIR}/logs|g" "$TMP_SERVICE"

# Copy service file to systemd
echo -e "${GREEN}📦 Kopiere Service-Datei nach /etc/systemd/system/${NC}"
cp "$TMP_SERVICE" /etc/systemd/system/localagent-pro.service
rm "$TMP_SERVICE"

# Set permissions
chmod 644 /etc/systemd/system/localagent-pro.service

# Reload systemd
echo -e "${GREEN}🔄 Systemd neu laden...${NC}"
systemctl daemon-reload

# Enable service
echo -e "${GREEN}⚡ Service aktivieren (Auto-Start beim Booten)...${NC}"
systemctl enable localagent-pro.service

# Start service
echo -e "${GREEN}🚀 Service starten...${NC}"
systemctl start localagent-pro.service

# Wait for service to start
sleep 2

# Check status
echo ""
echo -e "${GREEN}✅ Installation abgeschlossen!${NC}"
echo ""
echo "📊 Service-Status:"
systemctl status localagent-pro.service --no-pager | head -20

echo ""
echo "🎯 Nützliche Befehle:"
echo "  sudo systemctl status localagent-pro    # Status anzeigen"
echo "  sudo systemctl stop localagent-pro      # Service stoppen"
echo "  sudo systemctl start localagent-pro     # Service starten"
echo "  sudo systemctl restart localagent-pro   # Service neu starten"
echo "  sudo systemctl disable localagent-pro   # Auto-Start deaktivieren"
echo "  sudo journalctl -u localagent-pro -f    # Logs anzeigen (live)"
echo "  sudo journalctl -u localagent-pro -n 50 # Letzte 50 Log-Zeilen"
echo ""
echo "🌐 Server läuft auf: http://localhost:8001"
echo "🏥 Health Check: curl http://localhost:8001/health"
echo ""
