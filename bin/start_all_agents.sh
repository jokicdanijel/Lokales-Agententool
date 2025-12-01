#!/usr/bin/env bash
"""
ELION Agent Ecosystem Starter
Startet alle verfügbaren Agenten (opena1-opena21)

Version: 2.0
Datum: 29. November 2025
"""

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${ROOT}/.venv/bin/python"
LOGS="${ROOT}/logs"

# Farben für Terminal-Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

mkdir -p "$LOGS"

echo -e "${CYAN}🚀 ELION Agent Ecosystem Starter${NC}"
echo -e "${CYAN}=====================================${NC}"

# Agent definitions: name, port, script path (aktualisierte Pfade)
declare -a AGENTS=(
    "opena1:12344:1.opena1&2_portier/main_opena1.py"
    "opena2:12345:1.opena1&2_portier/main_opena2.py" 
    "opena3:12347:2.opena3_openwebui/main_opena3.py"
    "opena4:12348:3.opena4_telegram/main_opena4.py"
    "opena5:12351:4.opena5_vscode/main_opena5.py"
    "opena6:12350:5.opena6_browser/main_opena6.py"
    "opena7:12352:6.opena7_email/main_opena7.py"
    "opena8:12353:7.opena8_whatsapp/main_opena8.py"
    "opena9:12354:8.opena9_phone_answer/main_opena9.py"
    "opena10:12355:9.opena10_phone_call/main_opena10.py"
    "opena11:12356:10.opena11_door_unlock/main_opena11.py"
    "opena12:12357:11.opena12_social_automation/main_opena12.py"
    "opena13:12358:12.opena13_social_influencer/main_opena13.py"
    "opena14:12359:13.opena14_calendar/main_opena14.py"
    "opena16:12360:14.opena16_shop/main_opena16.py"
    "opena17:12361:15.opena17_homepage/main_opena17.py"
    "opena18:12362:16.opena18_storage/main_opena18.py"
    "opena19:12363:17.opena19_trading/main_opena19.py"
    "dashboard:12349:19.opena20_dashboard_agent/main_dashboard_agent.py"
    "opena21:12364:20.opena21_workflow/main_opena21.py"
)

# Funktion: Agent starten
start_agent() {
    local name="$1"
    local port="$2"
    local script="$3"
    
    # PID-Check
    local pid_file="$LOGS/${name}.pid"
    if [[ -f "$pid_file" ]]; then
        local existing_pid=$(cat "$pid_file")
        if kill -0 "$existing_pid" 2>/dev/null; then
            echo -e "${YELLOW}⚡ $name already running (PID: $existing_pid)${NC}"
            return 0
        else
            rm -f "$pid_file"
        fi
    fi
    
    # Port-Check
    if lsof -i ":$port" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  $name (port $port): Port already in use${NC}"
        return 1
    fi
    
    # Script-Check
    if [ ! -f "$ROOT/$script" ]; then
        echo -e "${YELLOW}⚠️ $name: Script not found ($script) - skipping${NC}"
        return 1
    fi
    
    # Agent starten
    echo -e "${BLUE}🔄 Starting $name (Port: $port)...${NC}"
    
    log_file="$LOGS/${name}.nohup.log"
    nohup "$VENV" "$ROOT/$script" > "$log_file" 2>&1 &
    local pid=$!
    echo "$pid" > "$pid_file"
    
    # Kurz warten und prüfen
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${GREEN}✅ $name started successfully (PID: $pid)${NC}"
        return 0
    else
        echo -e "${RED}❌ $name failed to start${NC}"
        rm -f "$pid_file"
        return 1
    fi
}

# Hauptstartlogik
STARTED=0
SKIPPED=0
FAILED=0

# Kern-Agenten zuerst (wichtige Reihenfolge)
echo -e "${PURPLE}📡 Starting Core Agents...${NC}"

for agent_def in "${AGENTS[@]:0:3}"; do  # opena1, opena2, opena3
    IFS=':' read -r name port script <<< "$agent_def"
    if start_agent "$name" "$port" "$script"; then
        ((STARTED++))
    else
        ((FAILED++))
    fi
    sleep 1
done

# Dashboard
IFS=':' read -r name port script <<< "${AGENTS[18]}"  # dashboard
if start_agent "$name" "$port" "$script"; then
    ((STARTED++))
else
    ((FAILED++))
fi

sleep 2

echo -e "${PURPLE}🌐 Starting Extended Agents...${NC}"

# Alle anderen Agenten
for agent_def in "${AGENTS[@]:3:15}" "${AGENTS[@]:19}"; do
    IFS=':' read -r name port script <<< "$agent_def"
    if start_agent "$name" "$port" "$script"; then
        ((STARTED++))
    else
        ((FAILED++))
    fi
done

echo -e "${CYAN}=====================================${NC}"
echo -e "${GREEN}📊 Startup Summary:"
echo -e "${GREEN}   ✅ Started: $STARTED agents"
echo -e "${RED}   ❌ Failed: $FAILED agents"
echo -e "${BLUE}   📈 Total Attempted: $((STARTED + FAILED))"
echo -e "${CYAN}=====================================${NC}"

# Health Check
if [ $STARTED -gt 0 ]; then
    echo -e "${PURPLE}🏥 Health Check (Core Services):${NC}"
    sleep 3
    
    for check_agent in "opena1:12344" "opena2:12345" "dashboard:12349"; do
        IFS=':' read -r name port <<< "$check_agent"
        if curl -s "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}  ✅ $name${NC}"
        else
            echo -e "${RED}  ❌ $name (not responding)${NC}"
        fi
    done
fi

echo ""
echo -e "${CYAN}✅ ELION Agent Ecosystem Startup Complete!${NC}"
echo -e "${BLUE}   📁 Logs: $LOGS/${NC}"
echo -e "${BLUE}   🌐 Dashboard: http://127.0.0.1:12349/ui_index.html${NC}"
echo -e "${BLUE}   📊 Health Check: curl http://127.0.0.1:12344/health${NC}"
