#!/bin/bash
################################################################################
# validate_agent_directories.sh
# Validiere alle 21 OPENA-Agenten gegen kanonisches Mapping
#
# Nutzung:
#   bash scripts/validate_agent_directories.sh
#   bash scripts/validate_agent_directories.sh --fix
#
################################################################################

set -euo pipefail

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_success() { echo -e "${GREEN}✅ $*${NC}"; }
log_error() { echo -e "${RED}❌ $*${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $*${NC}"; }
log_info() { echo -e "${BLUE}ℹ️  $*${NC}"; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT_MAP="$REPO_ROOT/agent_directories.json"
FIX_MODE=${1:-}

# Kanonisches Mapping (aus agent_directories.json)
declare -A CANONICAL=(
    [opena1]="1.opena1&2_portier/opena1:12344"
    [opena2]="1.opena1&2_portier/opena2:12345"
    [opena3]="2.opena3_openwebui:12347"
    [opena4]="3.opena4_telegram:12346"
    [opena5]="4.opena5_vscode:12350"
    [opena6]="5.opena6_browser:12351"
    [opena7]="6.opena7_email:12352"
    [opena8]="7.opena8_whatsapp:12353"
    [opena9]="8.opena9_telephone:12354"
    [opena10]="9.opena10_call_tracking:12355"
    [opena11]="10.opena11_unlock:12356"
    [opena12]="11.opena12_social_media:12357"
    [opena13]="12.opena13_influencer:12358"
    [opena14]="13.opena14_calendar:12359"
    [opena15]="14.opena15_html:12360"
    [opena16]="15.opena16_shop:12361"
    [opena17]="16.opena17_homepagecreator:12362"
    [opena18]="17.opena18_CMR:12363"
    [opena19]="18.opena19_Aktien&Crypto:12364"
    [opena20]="19.opena20_dashboard_agent:12349"
    [opena21]="20.opena21_workflow:12367"
)

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}► AGENT DIRECTORY VALIDATION (21 Agents)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Counter
VALID=0
MISSING=0
INVALID=0

# Validiere jeden Agent
for agent in "${!CANONICAL[@]}"; do
    IFS=':' read -r folder port <<< "${CANONICAL[$agent]}"
    fullpath="$REPO_ROOT/$folder"

    # Prüfe ob Verzeichnis existiert
    if [[ -d "$fullpath" ]]; then
        log_success "$agent → $folder (Port: $port) ✓"
        ((VALID++))
    else
        log_error "$agent → $folder (MISSING!)"
        ((MISSING++))

        # Fix-Mode: Versuche zu erstellen
        if [[ "$FIX_MODE" == "--fix" ]]; then
            log_warning "  Erstelle Verzeichnis..."
            mkdir -p "$fullpath"
            # Erstelle placeholder
            touch "$fullpath/main.py"
            touch "$fullpath/.env.example"
            log_success "  Verzeichnis erstellt: $fullpath"
        fi
    fi
done

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}► VALIDATION SUMMARY${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Total Agents: 21"
echo -e "Valid:   ${GREEN}$VALID${NC}"
echo -e "Missing: ${RED}$MISSING${NC}"
echo ""

if [[ $MISSING -eq 0 ]]; then
    log_success "✅ Alle 21 Agent-Verzeichnisse sind korrekt strukturiert!"
    exit 0
else
    log_error "❌ $MISSING Agenten haben falsche oder fehlende Verzeichnisse"
    log_info "Führe aus: bash scripts/validate_agent_directories.sh --fix"
    exit 1
fi
