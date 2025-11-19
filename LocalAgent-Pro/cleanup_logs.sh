#!/bin/bash
# Räume alte Log-Dateien auf

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       LocalAgent-Pro Log-Cleanup                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Prüfe ob Log-Verzeichnis existiert
if [ ! -d "$LOG_DIR" ]; then
    echo -e "${YELLOW}ℹ️  Log-Verzeichnis existiert nicht: $LOG_DIR${NC}"
    exit 0
fi

# Zeige aktuelle Logs
echo -e "${CYAN}📋 Aktuelle Log-Dateien:${NC}"
echo ""

total_size=0
file_count=0

for log_file in "$LOG_DIR"/*.log*; do
    if [ -f "$log_file" ]; then
        filename=$(basename "$log_file")
        size=$(du -b "$log_file" | cut -f1)
        size_h=$(du -h "$log_file" | cut -f1)
        lines=$(wc -l < "$log_file" 2>/dev/null || echo 0)
        modified=$(stat -c %y "$log_file" | cut -d'.' -f1)
        
        total_size=$((total_size + size))
        file_count=$((file_count + 1))
        
        echo -e "  • ${BLUE}$filename${NC}: $size_h, $lines Zeilen (geändert: $modified)"
    fi
done

echo ""
echo -e "${CYAN}📊 Gesamt: $file_count Dateien, $(numfmt --to=iec-i --suffix=B $total_size)${NC}"
echo ""

# Frage nach Aktion
echo -e "${YELLOW}Was möchtest du tun?${NC}"
echo ""
echo -e "  ${BLUE}[1]${NC} Alte Log-Dateien archivieren (*.log.X)"
echo -e "  ${BLUE}[2]${NC} Alle Logs löschen (inkl. Backups)"
echo -e "  ${BLUE}[3]${NC} Nur Backups löschen (*.log.X)"
echo -e "  ${BLUE}[4]${NC} Logs komprimieren und archivieren"
echo -e "  ${BLUE}[q]${NC} Abbrechen"
echo ""

read -p "Wähle eine Option: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🗑️  Lösche alte Backup-Logs...${NC}"
        
        deleted=0
        for log_file in "$LOG_DIR"/*.log.*; do
            if [ -f "$log_file" ]; then
                rm -f "$log_file"
                echo -e "  ${RED}✗${NC} Gelöscht: $(basename "$log_file")"
                deleted=$((deleted + 1))
            fi
        done
        
        if [ $deleted -eq 0 ]; then
            echo -e "${YELLOW}ℹ️  Keine Backup-Logs gefunden${NC}"
        else
            echo -e "${GREEN}✅ $deleted Backup-Logs gelöscht${NC}"
        fi
        ;;
    
    2)
        echo ""
        echo -e "${RED}⚠️  WARNUNG: Alle Logs werden gelöscht!${NC}"
        read -p "Bist du sicher? (ja/nein): " confirm
        
        if [ "$confirm" = "ja" ]; then
            echo ""
            echo -e "${GREEN}🗑️  Lösche alle Logs...${NC}"
            
            rm -rf "$LOG_DIR"/*.log*
            
            echo -e "${GREEN}✅ Alle Logs gelöscht${NC}"
        else
            echo -e "${YELLOW}ℹ️  Abgebrochen${NC}"
        fi
        ;;
    
    3)
        echo ""
        echo -e "${GREEN}🗑️  Lösche nur Backups...${NC}"
        
        deleted=0
        for log_file in "$LOG_DIR"/*.log.[0-9]*; do
            if [ -f "$log_file" ]; then
                rm -f "$log_file"
                echo -e "  ${RED}✗${NC} Gelöscht: $(basename "$log_file")"
                deleted=$((deleted + 1))
            fi
        done
        
        if [ $deleted -eq 0 ]; then
            echo -e "${YELLOW}ℹ️  Keine Backup-Logs gefunden${NC}"
        else
            echo -e "${GREEN}✅ $deleted Backup-Logs gelöscht${NC}"
        fi
        ;;
    
    4)
        echo ""
        echo -e "${GREEN}📦 Komprimiere und archiviere Logs...${NC}"
        
        timestamp=$(date +%Y%m%d_%H%M%S)
        archive_name="logs_archive_${timestamp}.tar.gz"
        archive_path="$SCRIPT_DIR/$archive_name"
        
        # Erstelle Archiv
        tar -czf "$archive_path" -C "$SCRIPT_DIR" logs/
        
        if [ $? -eq 0 ]; then
            archive_size=$(du -h "$archive_path" | cut -f1)
            echo -e "${GREEN}✅ Archiv erstellt: $archive_name ($archive_size)${NC}"
            
            # Frage ob alte Logs gelöscht werden sollen
            read -p "Alte Logs löschen? (ja/nein): " delete_confirm
            
            if [ "$delete_confirm" = "ja" ]; then
                rm -rf "$LOG_DIR"/*.log*
                echo -e "${GREEN}✅ Alte Logs gelöscht${NC}"
            fi
        else
            echo -e "${RED}❌ Fehler beim Erstellen des Archivs${NC}"
        fi
        ;;
    
    q|Q)
        echo -e "${YELLOW}ℹ️  Abgebrochen${NC}"
        exit 0
        ;;
    
    *)
        echo -e "${RED}❌ Ungültige Auswahl${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Fertig!${NC}"
