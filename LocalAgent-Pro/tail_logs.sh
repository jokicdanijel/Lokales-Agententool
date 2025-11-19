
#!/bin/bash
# Tail verschiedene Log-Dateien von LocalAgent-Pro

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       LocalAgent-Pro Live-Logging                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Prüfe ob Log-Verzeichnis existiert
if [ ! -d "$LOG_DIR" ]; then
    echo -e "${RED}❌ Log-Verzeichnis nicht gefunden: $LOG_DIR${NC}"
    echo -e "${YELLOW}💡 Starte erst den Server, um Logs zu generieren${NC}"
    exit 1
fi

# Funktion zum Anzeigen verfügbarer Logs
show_available_logs() {
    echo -e "${GREEN}📋 Verfügbare Log-Dateien:${NC}"
    echo ""
    
    local i=1
    for log_file in "$LOG_DIR"/*.log; do
        if [ -f "$log_file" ]; then
            local filename=$(basename "$log_file")
            local size=$(du -h "$log_file" | cut -f1)
            local lines=$(wc -l < "$log_file")
            echo -e "  ${BLUE}[$i]${NC} $filename (${size}, ${lines} Zeilen)"
            ((i++))
        fi
    done
    
    echo ""
    echo -e "  ${BLUE}[a]${NC} Alle Logs (kombiniert)"
    echo -e "  ${BLUE}[q]${NC} Beenden"
    echo ""
}

# Funktion zum Tail einer Log-Datei
tail_log() {
    local log_file="$1"
    local filename=$(basename "$log_file")
    
    echo -e "${GREEN}📖 Folge Log: $filename${NC}"
    echo -e "${YELLOW}⏹️  Drücke Ctrl+C zum Beenden${NC}"
    echo ""
    
    # Tail mit Farben
    tail -f "$log_file" | while IFS= read -r line; do
        # Farbige Ausgabe basierend auf Log-Level
        if [[ $line == *"ERROR"* ]] || [[ $line == *"CRITICAL"* ]]; then
            echo -e "${RED}$line${NC}"
        elif [[ $line == *"WARNING"* ]]; then
            echo -e "${YELLOW}$line${NC}"
        elif [[ $line == *"INFO"* ]]; then
            echo -e "${GREEN}$line${NC}"
        elif [[ $line == *"DEBUG"* ]]; then
            echo -e "${BLUE}$line${NC}"
        else
            echo "$line"
        fi
    done
}

# Funktion zum Tail aller Logs
tail_all_logs() {
    echo -e "${GREEN}📖 Folge alle Logs (kombiniert)${NC}"
    echo -e "${YELLOW}⏹️  Drücke Ctrl+C zum Beenden${NC}"
    echo ""
    
    # Tail alle .log Dateien gleichzeitig
    tail -f "$LOG_DIR"/*.log 2>/dev/null | while IFS= read -r line; do
        # Farbige Ausgabe
        if [[ $line == *"ERROR"* ]] || [[ $line == *"CRITICAL"* ]]; then
            echo -e "${RED}$line${NC}"
        elif [[ $line == *"WARNING"* ]]; then
            echo -e "${YELLOW}$line${NC}"
        elif [[ $line == *"INFO"* ]]; then
            echo -e "${GREEN}$line${NC}"
        elif [[ $line == *"DEBUG"* ]]; then
            echo -e "${BLUE}$line${NC}"
        else
            echo "$line"
        fi
    done
}

# Hauptlogik
if [ $# -eq 0 ]; then
    # Interaktiver Modus
    while true; do
        show_available_logs
        
        read -p "Wähle eine Log-Datei: " choice
        
        case $choice in
            q|Q)
                echo -e "${GREEN}👋 Auf Wiedersehen!${NC}"
                exit 0
                ;;
            a|A)
                tail_all_logs
                ;;
            [1-9])
                # Hole n-te Log-Datei
                log_file=$(ls "$LOG_DIR"/*.log 2>/dev/null | sed -n "${choice}p")
                if [ -n "$log_file" ] && [ -f "$log_file" ]; then
                    tail_log "$log_file"
                else
                    echo -e "${RED}❌ Ungültige Auswahl${NC}"
                    sleep 2
                fi
                ;;
            *)
                echo -e "${RED}❌ Ungültige Eingabe${NC}"
                sleep 1
                ;;
        esac
    done
else
    # Direkter Modus mit Argument
    log_name="$1"
    log_file="$LOG_DIR/$log_name"
    
    if [ ! -f "$log_file" ]; then
        # Versuche .log anzuhängen
        log_file="$LOG_DIR/$log_name.log"
    fi
    
    if [ -f "$log_file" ]; then
        tail_log "$log_file"
    else
        echo -e "${RED}❌ Log-Datei nicht gefunden: $log_name${NC}"
        echo ""
        show_available_logs
        exit 1
    fi
fi
