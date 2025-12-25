#!/bin/bash
# 🚨 GOVERNANCE FIX #1: ARCHIV → configs/ ROLLBACK
# Datum: 27. November 2025
# Zweck: Safepoints zurück von configs/ nach ARCHIV/archivp/ (YYYY/MM/DD)
# Quelle: rename_map.csv (Zeilen 295-544)

set -euo pipefail

# ============================================================================
# KONFIGURATION
# ============================================================================
PROJECT_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
RENAME_MAP="$PROJECT_ROOT/rename_map.csv"
CONFIGS_DIR="$PROJECT_ROOT/configs"
LOG_FILE="$PROJECT_ROOT/GOVERNANCE_FIX_ARCHIV.log"
DRY_RUN="${DRY_RUN:-true}"  # Default: DRY-RUN (setze DRY_RUN=false für Execution)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# SAFETY CHECKS (ZWINGEND VOR AUSFÜHRUNG)
# ============================================================================
safety_checks() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🔒 SAFETY CHECKS${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    local all_passed=true

    # Check 1: Git-Repository
    if ! git -C "$PROJECT_ROOT" rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}✗ FEHLER: Kein Git-Repository gefunden${NC}"
        echo -e "${YELLOW}  → Initializiere Git oder wechsle Branch${NC}"
        all_passed=false
    else
        echo -e "${GREEN}✓ Git-Repository vorhanden${NC}"
    fi

    # Check 2: Uncommitted Changes
    if [[ -n $(git -C "$PROJECT_ROOT" status --porcelain) ]]; then
        echo -e "${YELLOW}⚠ Uncommitted Changes vorhanden${NC}"
        echo -e "${YELLOW}  → Empfohlen: git commit vor Ausführung${NC}"
    else
        echo -e "${GREEN}✓ Working Directory clean${NC}"
    fi

    # Check 3: Branch Check
    local current_branch
    current_branch=$(git -C "$PROJECT_ROOT" branch --show-current)
    echo -e "${BLUE}ℹ Current Branch: ${YELLOW}$current_branch${NC}"
    if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "master" ]]; then
        echo -e "${YELLOW}⚠ Du bist auf $current_branch – sicherer wäre ein Feature-Branch${NC}"
    fi

    # Check 4: rename_map.csv vorhanden
    if [[ ! -f "$RENAME_MAP" ]]; then
        echo -e "${RED}✗ FEHLER: $RENAME_MAP nicht gefunden${NC}"
        all_passed=false
    else
        echo -e "${GREEN}✓ rename_map.csv vorhanden ($(wc -l < "$RENAME_MAP") Zeilen)${NC}"
    fi

    # Check 5: configs/ existiert
    if [[ ! -d "$CONFIGS_DIR" ]]; then
        echo -e "${YELLOW}⚠ configs/ existiert nicht – Script wird nichts tun${NC}"
    else
        local sp_count
        sp_count=$(find "$CONFIGS_DIR" -name "SP*.json" 2>/dev/null | wc -l)
        echo -e "${BLUE}ℹ Safepoints in configs/: ${YELLOW}$sp_count${NC}"
    fi

    # Check 6: DRY-RUN Mode
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${GREEN}✓ DRY-RUN Mode aktiv – keine Dateien werden verändert${NC}"
    else
        echo -e "${RED}⚠ LIVE Mode – Dateien werden WIRKLICH verschoben!${NC}"
        echo -e "${YELLOW}  → Setze DRY_RUN=false nur nach Review!${NC}"
    fi

    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    if [[ "$all_passed" == "false" ]]; then
        echo -e "${RED}❌ SAFETY CHECKS FEHLGESCHLAGEN – ABBRUCH${NC}"
        exit 1
    fi

    if [[ "$DRY_RUN" == "false" ]]; then
        echo -e "${YELLOW}▶ Drücke ENTER zum Fortfahren oder CTRL+C zum Abbrechen${NC}"
        read -r
    fi
}

# ============================================================================
# MAIN: ARCHIV-ROLLBACK
# ============================================================================
rollback_archiv() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}📦 ARCHIV-ROLLBACK (configs/ → ARCHIV/archivp/)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    local count_moved=0
    local count_skipped=0
    local count_errors=0

    # Parse rename_map.csv: Zeilen mit "ARCHIV.*configs/SP"
    grep -E "ARCHIV.*,configs/SP.*\.json" "$RENAME_MAP" | while IFS=',' read -r src dst _rest; do
        # Bereinige Pfade (entferne führende/trailing Leerzeichen)
        src=$(echo "$src" | xargs)
        dst=$(echo "$dst" | xargs)

        # Vollständige Pfade
        local src_full="$PROJECT_ROOT/$src"
        local dst_full="$PROJECT_ROOT/$dst"

        # Prüfe: dst existiert (in configs/)
        if [[ ! -f "$dst_full" ]]; then
            echo -e "${YELLOW}⚠ Übersprungen (Datei nicht in configs/): $(basename "$dst")${NC}" | tee -a "$LOG_FILE"
            count_skipped=$((count_skipped + 1))
            continue
        fi

        # Prüfe: src-Ziel existiert bereits (Konflikt)
        if [[ -f "$src_full" ]]; then
            echo -e "${YELLOW}⚠ Konflikt (Ziel existiert bereits): $src${NC}" | tee -a "$LOG_FILE"
            echo -e "${YELLOW}  → Verwende mv -n (no-clobber) oder manuelle Review${NC}" | tee -a "$LOG_FILE"
            count_skipped=$((count_skipped + 1))
            continue
        fi

        # Erstelle Zielverzeichnis
        local src_dir
        src_dir=$(dirname "$src_full")

        if [[ "$DRY_RUN" == "true" ]]; then
            echo -e "${BLUE}[DRY-RUN] mkdir -p $src_dir${NC}"
            echo -e "${BLUE}[DRY-RUN] mv $dst_full → $src_full${NC}"
        else
            mkdir -p "$src_dir"
            if mv -n "$dst_full" "$src_full"; then
                echo -e "${GREEN}✓ Verschoben: $(basename "$dst") → $src${NC}" | tee -a "$LOG_FILE"
                count_moved=$((count_moved + 1))
            else
                echo -e "${RED}✗ FEHLER beim Verschieben: $dst → $src${NC}" | tee -a "$LOG_FILE"
                count_errors=$((count_errors + 1))
            fi
        fi
    done

    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Verschoben: $count_moved${NC}"
    echo -e "${YELLOW}⚠ Übersprungen: $count_skipped${NC}"
    echo -e "${RED}✗ Fehler: $count_errors${NC}"
}

# ============================================================================
# VALIDIERUNG
# ============================================================================
validate() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🔍 VALIDIERUNG${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    local sp_in_configs
    sp_in_configs=$(find "$CONFIGS_DIR" -name "SP*.json" 2>/dev/null | wc -l)

    local sp_in_archiv
    sp_in_archiv=$(find "$PROJECT_ROOT" -path "*/ARCHIV/*.json" -o -path "*/archivp/*.json" 2>/dev/null | wc -l)

    echo -e "${BLUE}Safepoints in configs/: ${YELLOW}$sp_in_configs${NC} (Soll: 0)"
    echo -e "${BLUE}Safepoints in ARCHIV/archivp/: ${YELLOW}$sp_in_archiv${NC}"

    if [[ $sp_in_configs -eq 0 ]]; then
        echo -e "${GREEN}✅ configs/ ist sauber (keine Safepoints)${NC}"
    else
        echo -e "${RED}❌ configs/ enthält noch Safepoints → manuelle Review${NC}"
    fi
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🚨 GOVERNANCE FIX #1: ARCHIV → configs/ ROLLBACK${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Start: $(date -u +"%Y-%m-%d %H:%M:%S UTC")${NC}"
    echo -e "${BLUE}DRY-RUN: ${YELLOW}$DRY_RUN${NC}"
    echo ""

    safety_checks
    rollback_archiv
    validate

    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Ende: $(date -u +"%Y-%m-%d %H:%M:%S UTC")${NC}"
    echo -e "${BLUE}Log: $LOG_FILE${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        echo -e "${YELLOW}ℹ DRY-RUN abgeschlossen. Für echte Ausführung:${NC}"
        echo -e "${YELLOW}  DRY_RUN=false ./GOVERNANCE_FIX_ARCHIV.sh${NC}"
    fi
}

main "$@"
