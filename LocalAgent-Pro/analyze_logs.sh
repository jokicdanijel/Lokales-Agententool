#!/bin/bash
# Analysiere Log-Dateien und zeige Statistiken

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       LocalAgent-Pro Log-Analyse                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Prüfe ob Log-Verzeichnis existiert
if [ ! -d "$LOG_DIR" ]; then
    echo -e "${RED}❌ Log-Verzeichnis nicht gefunden: $LOG_DIR${NC}"
    exit 1
fi

# Hauptlog
MAIN_LOG="$LOG_DIR/localagent-pro.log"

if [ ! -f "$MAIN_LOG" ]; then
    echo -e "${RED}❌ Hauptlog nicht gefunden: $MAIN_LOG${NC}"
    exit 1
fi

echo -e "${GREEN}📊 Analysiere Logs...${NC}"
echo ""

# Dateiinformationen
echo -e "${CYAN}📁 Log-Dateien:${NC}"
for log_file in "$LOG_DIR"/*.log; do
    if [ -f "$log_file" ]; then
        filename=$(basename "$log_file")
        size=$(du -h "$log_file" | cut -f1)
        lines=$(wc -l < "$log_file")
        modified=$(stat -c %y "$log_file" | cut -d'.' -f1)
        echo -e "  • ${BLUE}$filename${NC}: $size, $lines Zeilen (geändert: $modified)"
    fi
done

echo ""
echo -e "${CYAN}📈 Log-Level Statistiken (Hauptlog):${NC}"

# Zähle Log-Levels
debug_count=$(grep -c " DEBUG " "$MAIN_LOG" 2>/dev/null || echo 0)
info_count=$(grep -c " INFO " "$MAIN_LOG" 2>/dev/null || echo 0)
warning_count=$(grep -c " WARNING " "$MAIN_LOG" 2>/dev/null || echo 0)
error_count=$(grep -c " ERROR " "$MAIN_LOG" 2>/dev/null || echo 0)
critical_count=$(grep -c " CRITICAL " "$MAIN_LOG" 2>/dev/null || echo 0)

total=$((debug_count + info_count + warning_count + error_count + critical_count))

echo -e "  ${BLUE}DEBUG:${NC}    $debug_count"
echo -e "  ${GREEN}INFO:${NC}     $info_count"
echo -e "  ${YELLOW}WARNING:${NC}  $warning_count"
echo -e "  ${RED}ERROR:${NC}    $error_count"
echo -e "  ${RED}CRITICAL:${NC} $critical_count"
echo -e "  ─────────────────"
echo -e "  ${CYAN}TOTAL:${NC}    $total Einträge"

echo ""
echo -e "${CYAN}🔍 Top 10 häufigste Meldungen:${NC}"
grep -oP '(?<=\| )[A-Za-z_-]+(?= \|)' "$MAIN_LOG" 2>/dev/null | sort | uniq -c | sort -rn | head -10 | while read count module; do
    echo -e "  • ${BLUE}$module${NC}: $count mal"
done

echo ""
echo -e "${CYAN}⚠️ Letzte Fehler:${NC}"
grep " ERROR \| CRITICAL " "$MAIN_LOG" | tail -5 | while IFS= read -r line; do
    echo -e "  ${RED}$line${NC}"
done

echo ""
echo -e "${CYAN}🕐 Zeitbereich:${NC}"
first_line=$(head -1 "$MAIN_LOG")
last_line=$(tail -1 "$MAIN_LOG")

first_time=$(echo "$first_line" | grep -oP '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' || echo "unbekannt")
last_time=$(echo "$last_line" | grep -oP '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' || echo "unbekannt")

echo -e "  ${BLUE}Von:${NC} $first_time"
echo -e "  ${BLUE}Bis:${NC} $last_time"

# API-Request-Statistik (falls vorhanden)
API_LOG="$LOG_DIR/api_requests.log"
if [ -f "$API_LOG" ]; then
    echo ""
    echo -e "${CYAN}📡 API-Requests:${NC}"
    
    total_requests=$(wc -l < "$API_LOG")
    echo -e "  • ${BLUE}Total:${NC} $total_requests Requests"
    
    # Endpoints zählen
    echo -e "  • ${BLUE}Top Endpoints:${NC}"
    grep -oP '(GET|POST|PUT|DELETE) /[^ ]*' "$API_LOG" 2>/dev/null | sort | uniq -c | sort -rn | head -5 | while read count endpoint; do
        echo -e "    - $endpoint: $count mal"
    done
fi

# Tool-Execution-Statistik
TOOL_LOG="$LOG_DIR/tool_executions.log"
if [ -f "$TOOL_LOG" ]; then
    echo ""
    echo -e "${CYAN}🛠️ Tool-Ausführungen:${NC}"
    
    total_tools=$(wc -l < "$TOOL_LOG")
    echo -e "  • ${BLUE}Total:${NC} $total_tools Tool-Calls"
    
    # Tools zählen
    echo -e "  • ${BLUE}Top Tools:${NC}"
    grep -oP "Tool '[^']+'" "$TOOL_LOG" 2>/dev/null | sort | uniq -c | sort -rn | head -5 | while read count tool; do
        echo -e "    - $tool: $count mal"
    done
fi

# Ollama-Statistik
OLLAMA_LOG="$LOG_DIR/ollama_integration.log"
if [ -f "$OLLAMA_LOG" ]; then
    echo ""
    echo -e "${CYAN}🤖 Ollama-Integration:${NC}"
    
    total_ollama=$(wc -l < "$OLLAMA_LOG")
    echo -e "  • ${BLUE}Total:${NC} $total_ollama Log-Einträge"
    
    # Generate/Chat Requests
    generate_count=$(grep -c "Generate Request" "$OLLAMA_LOG" 2>/dev/null || echo 0)
    chat_count=$(grep -c "Chat Request" "$OLLAMA_LOG" 2>/dev/null || echo 0)
    
    echo -e "  • ${BLUE}Generate Requests:${NC} $generate_count"
    echo -e "  • ${BLUE}Chat Requests:${NC} $chat_count"
    
    # Durchschnittliche Response-Zeit (falls vorhanden)
    avg_time=$(grep -oP '\d+\.\d+(?=s)' "$OLLAMA_LOG" 2>/dev/null | awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print 0}')
    echo -e "  • ${BLUE}Ø Response-Zeit:${NC} ${avg_time}s"
fi

echo ""
echo -e "${GREEN}✅ Analyse abgeschlossen!${NC}"
echo ""
echo -e "${YELLOW}💡 Tipp: Nutze './tail_logs.sh' zum Live-Monitoring${NC}"
