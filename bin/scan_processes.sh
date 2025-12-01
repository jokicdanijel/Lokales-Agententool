#!/bin/bash
# Script: Scanne nach laufenden ELION-Prozessen und pausiere bei Fund
# Datum: 21. November 2025

set -euo pipefail

# Farbcodes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Konfiguration
PROCESS_NAMES=(
    "opena1_app.py"
    "opena2_app.py"
    "main_openwebui_agent.py"
    "main.py"
    "agent_server.py"
    "uvicorn"
)

PORTS=(12344 12345 12346 12347 12348 12349 12350 12351 12352 12353 12354 12355 12356 12357 12358 12359 12360 12361 12362 12363 3000)

LOG_FILE="logs/process_scan_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

# Logging-Funktion
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "${timestamp} [${level}] ${message}" >> "$LOG_FILE"
}

# Banner
print_banner() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  🔍 ELION Process Scanner - Laufende Prozesse erkennen       ║${NC}"
    echo -e "${BLUE}║  Version: 2.0 | Datum: $(date '+%Y-%m-%d %H:%M:%S')           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Prozesse nach Namen scannen
scan_processes_by_name() {
    local count=0
    
    log "INFO" "Scanne nach Prozessen: ${PROCESS_NAMES[*]}"
    
    for proc in "${PROCESS_NAMES[@]}"; do
        local pids=$(pgrep -f "$proc" 2>/dev/null || true)
        if [[ -n "$pids" ]]; then
            for pid in $pids; do
                local cmd=$(ps -p "$pid" -o cmd= 2>/dev/null || echo "unknown")
                log "WARN" "Gefunden: PID=$pid, Prozess=$proc"
                echo -e "${YELLOW}  ⚠️  PID $pid: $cmd${NC}" >&2
                count=$((count + 1))
            done
        fi
    done
    
    echo "$count"
}

# Ports scannen
scan_ports() {
    local count=0
    
    log "INFO" "Scanne Ports: ${PORTS[*]}"
    
    for port in "${PORTS[@]}"; do
        if lsof -i ":$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            local pid=$(lsof -i ":$port" -sTCP:LISTEN -t 2>/dev/null | head -1)
            local cmd=$(ps -p "$pid" -o cmd= 2>/dev/null || echo "unknown")
            log "WARN" "Port $port belegt: PID=$pid"
            echo -e "${YELLOW}  📡 Port $port: PID $pid - $cmd${NC}" >&2
            count=$((count + 1))
        fi
    done
    
    echo "$count"
}

# Prozess-Details anzeigen
show_process_details() {
    local pid="$1"
    
    echo -e "${BLUE}┌─ Prozess-Details für PID $pid ─────────────────────────────┐${NC}"
    
    if ps -p "$pid" >/dev/null 2>&1; then
        echo -e "${BLUE}│${NC} Command:    $(ps -p "$pid" -o cmd= 2>/dev/null)"
        echo -e "${BLUE}│${NC} User:       $(ps -p "$pid" -o user= 2>/dev/null)"
        echo -e "${BLUE}│${NC} CPU:        $(ps -p "$pid" -o %cpu= 2>/dev/null)%"
        echo -e "${BLUE}│${NC} Memory:     $(ps -p "$pid" -o %mem= 2>/dev/null)%"
        echo -e "${BLUE}│${NC} Start Time: $(ps -p "$pid" -o lstart= 2>/dev/null)"
        
        # Ports des Prozesses
        local ports=$(lsof -Pan -p "$pid" -i 2>/dev/null | grep LISTEN | awk '{print $9}' | cut -d: -f2 | sort -u | tr '\n' ',' | sed 's/,$//')
        if [[ -n "$ports" ]]; then
            echo -e "${BLUE}│${NC} Ports:      $ports"
        fi
    else
        echo -e "${BLUE}│${NC} ${RED}Prozess nicht mehr vorhanden${NC}"
    fi
    
    echo -e "${BLUE}└────────────────────────────────────────────────────────────┘${NC}"
}

# Interaktive Pause
pause_interactive() {
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  ⚠️  WARNUNG: Laufende Prozesse gefunden!${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}Optionen:${NC}"
    echo -e "  ${GREEN}[1]${NC} Prozesse anzeigen"
    echo -e "  ${GREEN}[2]${NC} Alle stoppen (via bin/ops.sh stop)"
    echo -e "  ${GREEN}[3]${NC} Fortfahren (ignorieren)"
    echo -e "  ${GREEN}[4]${NC} Abbrechen"
    echo ""
    read -p "Ihre Wahl [1-4]: " choice
    
    case "$choice" in
        1)
            echo ""
            list_all_processes
            pause_interactive
            ;;
        2)
            stop_all_processes
            ;;
        3)
            log "INFO" "Benutzer hat gewählt fortzufahren (Prozesse ignorieren)"
            echo -e "${GREEN}✓ Fortfahren...${NC}"
            ;;
        4)
            log "INFO" "Benutzer hat Abbruch gewählt"
            echo -e "${RED}✗ Abgebrochen.${NC}"
            exit 1
            ;;
        *)
            echo -e "${RED}Ungültige Wahl. Bitte erneut versuchen.${NC}"
            pause_interactive
            ;;
    esac
}

# Alle Prozesse auflisten
list_all_processes() {
    echo -e "${BLUE}┌─ Laufende ELION-Prozesse ──────────────────────────────────┐${NC}"
    
    for proc in "${PROCESS_NAMES[@]}"; do
        local pids=$(pgrep -f "$proc" 2>/dev/null || true)
        if [[ -n "$pids" ]]; then
            for pid in $pids; do
                show_process_details "$pid"
            done
        fi
    done
    
    echo ""
    echo -e "${BLUE}┌─ Belegte Ports ─────────────────────────────────────────────┐${NC}"
    
    for port in "${PORTS[@]}"; do
        if lsof -i ":$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            local pid=$(lsof -i ":$port" -sTCP:LISTEN -t 2>/dev/null | head -1)
            local cmd=$(ps -p "$pid" -o cmd= 2>/dev/null || echo "unknown")
            echo -e "${BLUE}│${NC} Port ${YELLOW}$port${NC}: PID $pid"
            echo -e "${BLUE}│${NC}   → $cmd"
        fi
    done
    
    echo -e "${BLUE}└────────────────────────────────────────────────────────────┘${NC}"
}

# Alle Prozesse stoppen
stop_all_processes() {
    echo ""
    echo -e "${YELLOW}⏸️  Stoppe alle ELION-Prozesse...${NC}"
    
    if [[ -f "bin/ops.sh" ]]; then
        log "INFO" "Führe bin/ops.sh stop aus"
        bash bin/ops.sh stop
        
        # Warte und verifiziere
        sleep 2
        
        local remaining=$(scan_processes_by_name)
        if [[ "$remaining" -eq 0 ]]; then
            echo -e "${GREEN}✓ Alle Prozesse erfolgreich gestoppt.${NC}"
            log "INFO" "Alle Prozesse gestoppt"
        else
            echo -e "${YELLOW}⚠️  $remaining Prozesse noch aktiv. Versuche SIGKILL...${NC}"
            kill_remaining_processes
        fi
    else
        echo -e "${RED}✗ bin/ops.sh nicht gefunden. Versuche manuelles Stoppen...${NC}"
        kill_remaining_processes
    fi
}

# Verbleibende Prozesse mit SIGKILL stoppen
kill_remaining_processes() {
    for proc in "${PROCESS_NAMES[@]}"; do
        local pids=$(pgrep -f "$proc" 2>/dev/null || true)
        if [[ -n "$pids" ]]; then
            for pid in $pids; do
                echo -e "${YELLOW}  Killing PID $pid ($proc)${NC}"
                kill -9 "$pid" 2>/dev/null || true
                log "WARN" "SIGKILL gesendet an PID $pid"
            done
        fi
    done
    
    sleep 1
    
    local final_count=$(scan_processes_by_name)
    if [[ "$final_count" -eq 0 ]]; then
        echo -e "${GREEN}✓ Alle Prozesse erfolgreich beendet.${NC}"
    else
        echo -e "${RED}✗ $final_count Prozesse konnten nicht beendet werden.${NC}"
        exit 1
    fi
}

# Hauptfunktion
main() {
    print_banner
    
    log "INFO" "Starte Prozess-Scan..."
    
    # Scan durchführen
    echo -e "${BLUE}🔍 Scanne nach laufenden Prozessen...${NC}"
    echo ""
    
    local proc_count=$(scan_processes_by_name)
    echo ""
    
    echo -e "${BLUE}🔍 Scanne nach belegten Ports...${NC}"
    echo ""
    
    local port_count=$(scan_ports)
    echo ""
    
    # Ergebnis
    local total_findings=$((proc_count + port_count))
    
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  Scan-Ergebnisse:"
    echo -e "${BLUE}║${NC}    • Prozesse gefunden:    ${YELLOW}$proc_count${NC}"
    echo -e "${BLUE}║${NC}    • Ports belegt:         ${YELLOW}$port_count${NC}"
    echo -e "${BLUE}║${NC}    • Gesamt:               ${YELLOW}$total_findings${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    
    log "INFO" "Scan abgeschlossen: $total_findings Findings"
    
    if [[ "$total_findings" -gt 0 ]]; then
        pause_interactive
    else
        echo ""
        echo -e "${GREEN}✓ Keine laufenden ELION-Prozesse gefunden.${NC}"
        log "INFO" "System sauber - keine Prozesse gefunden"
    fi
    
    echo ""
    echo -e "${BLUE}Log gespeichert: $LOG_FILE${NC}"
}

# Script ausführen
main "$@"
