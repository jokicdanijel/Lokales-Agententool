#!/bin/bash
# ============================================================
# ELION PORTIER 3.0 - Systemd Service Installer
# Installiert alle Agent Services (opena17-opena21)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ELION PORTIER 3.0 - Systemd Service Installer           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Root-Check
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ Dieses Script muss als root ausgeführt werden${NC}"
   echo -e "${YELLOW}   Verwende: sudo $0${NC}"
   exit 1
fi

# Service-Definitionen
declare -A SERVICES
SERVICES["opena17"]="16.opena17_homepagecreator"
SERVICES["opena18"]="17.opena18_CMR"
SERVICES["opena19"]="18.opena19_Aktien&Crypto"
SERVICES["opena20"]="19.opena20_dashboard_agent"
SERVICES["opena21"]="20.opena21_workflow"

# Installation
install_service() {
    local service_name=$1
    local service_dir=$2
    local service_file="${PROJECT_ROOT}/${service_dir}/${service_name}.service"

    if [[ -f "$service_file" ]]; then
        echo -e "${YELLOW}📦 Installiere ${service_name}...${NC}"

        # Kopiere Service-Datei
        cp "$service_file" "/etc/systemd/system/${service_name}.service"

        # Log-Verzeichnis erstellen
        local log_dir="${PROJECT_ROOT}/${service_dir}/logs"
        mkdir -p "$log_dir"
        chown -R danijel-jd:danijel-jd "$log_dir"

        # Data-Verzeichnis erstellen
        local data_dir="${PROJECT_ROOT}/${service_dir}/data"
        mkdir -p "$data_dir"
        chown -R danijel-jd:danijel-jd "$data_dir"

        echo -e "${GREEN}   ✅ ${service_name} installiert${NC}"
    else
        echo -e "${RED}   ❌ Service-Datei nicht gefunden: ${service_file}${NC}"
    fi
}

# Alle Services installieren
echo -e "${BLUE}📋 Installiere Services...${NC}"
echo ""

for service in "${!SERVICES[@]}"; do
    install_service "$service" "${SERVICES[$service]}"
done

echo ""

# Systemd neu laden
echo -e "${YELLOW}🔄 Lade systemd daemon neu...${NC}"
systemctl daemon-reload
echo -e "${GREEN}   ✅ Daemon neugeladen${NC}"
echo ""

# Services aktivieren (optional)
read -p "Services automatisch starten beim Boot aktivieren? (j/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    echo -e "${YELLOW}🔧 Aktiviere Services für Autostart...${NC}"
    for service in "${!SERVICES[@]}"; do
        systemctl enable "${service}.service" 2>/dev/null || true
        echo -e "${GREEN}   ✅ ${service} aktiviert${NC}"
    done
fi

echo ""

# Services starten (optional)
read -p "Services jetzt starten? (j/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    echo -e "${YELLOW}🚀 Starte Services...${NC}"
    for service in "${!SERVICES[@]}"; do
        systemctl start "${service}.service" 2>/dev/null || true
        echo -e "${GREEN}   ✅ ${service} gestartet${NC}"
    done
fi

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Installation abgeschlossen!                             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Verfügbare Befehle:${NC}"
echo -e "  ${YELLOW}systemctl status opena17${NC}  - Status prüfen"
echo -e "  ${YELLOW}systemctl start opena17${NC}   - Service starten"
echo -e "  ${YELLOW}systemctl stop opena17${NC}    - Service stoppen"
echo -e "  ${YELLOW}systemctl restart opena17${NC} - Service neustarten"
echo -e "  ${YELLOW}journalctl -u opena17 -f${NC}  - Logs ansehen"
echo ""
echo -e "${GREEN}Port-Übersicht:${NC}"
echo -e "  opena17 (Homepage Creator): ${BLUE}http://127.0.0.1:12362${NC}"
echo -e "  opena18 (CRM Agent):        ${BLUE}http://127.0.0.1:12363${NC}"
echo -e "  opena19 (Stocks & Crypto):  ${BLUE}http://127.0.0.1:12365${NC}"
echo -e "  opena20 (Dashboard):        ${BLUE}http://127.0.0.1:12349${NC}"
echo -e "  opena21 (Workflow Engine):  ${BLUE}http://127.0.0.1:12364${NC}"
