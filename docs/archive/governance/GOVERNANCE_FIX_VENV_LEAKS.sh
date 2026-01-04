#!/bin/bash
# 🚨 GOVERNANCE FIX #2: venv → src/pkg CLEANUP
# Datum: 27. November 2025
# Zweck: Third-Party-Pakete aus src/pkg/ entfernen + requirements.txt aktualisieren

set -euo pipefail

# ============================================================================
# KONFIGURATION
# ============================================================================
PROJECT_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
SRC_PKG_DIR="$PROJECT_ROOT/src/pkg"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
LOG_FILE="$PROJECT_ROOT/GOVERNANCE_FIX_VENV_LEAKS.log"
DRY_RUN="${DRY_RUN:-true}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# SAFETY CHECKS
# ============================================================================
safety_checks() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🔒 SAFETY CHECKS${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    # Check 1: Python Version
    local python_version
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${BLUE}ℹ Python Version: ${YELLOW}$python_version${NC}"

    if [[ "$python_version" < "3.13" ]]; then
        echo -e "${YELLOW}⚠ Python < 3.13 – typing_extensions evtl. weiter nötig${NC}"
        echo -e "${YELLOW}  → Prüfe requirements.txt nach Cleanup${NC}"
    fi

    # Check 2: Import-Scan
    echo -e "${BLUE}ℹ Import-Scan (src.pkg.* Verwendung):${NC}"
    local import_count
    import_count=$(grep -R "src\.pkg\.\(typing_extensions\|socks\|py\)" "$PROJECT_ROOT" 2>/dev/null | grep -v ".git" | wc -l)

    if [[ $import_count -gt 0 ]]; then
        echo -e "${YELLOW}⚠ $import_count Imports auf src.pkg.* gefunden:${NC}"
        grep -R "src\.pkg\.\(typing_extensions\|socks\|py\)" "$PROJECT_ROOT" 2>/dev/null | grep -v ".git" | head -5
        echo -e "${YELLOW}  → Diese müssen VOR dem Löschen angepasst werden!${NC}"
        echo -e "${YELLOW}  → Beispiel: 'from src.pkg import socks' → 'import socks'${NC}"
    else
        echo -e "${GREEN}✓ Keine direkten src.pkg-Imports gefunden${NC}"
    fi

    # Check 3: Dateien vorhanden
    echo -e "${BLUE}ℹ Zu löschende Dateien:${NC}"
    local files_to_delete=(
        "typing_extensions.py"
        "py.py"
        "socks.py"
        "sockshandler.py"
    )

    local found_count=0
    for file in "${files_to_delete[@]}"; do
        if [[ -f "$SRC_PKG_DIR/$file" ]]; then
            echo -e "${YELLOW}  → $file${NC}"
            found_count=$((found_count + 1))
        fi
    done

    if [[ $found_count -eq 0 ]]; then
        echo -e "${GREEN}✓ Keine venv-Leaks in src/pkg/ gefunden – nichts zu tun${NC}"
        exit 0
    fi

    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    if [[ "$DRY_RUN" == "false" ]]; then
        echo -e "${YELLOW}▶ Drücke ENTER zum Fortfahren oder CTRL+C zum Abbrechen${NC}"
        read -r
    fi
}

# ============================================================================
# CLEANUP
# ============================================================================
cleanup_venv_leaks() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🧹 VENV-LEAK CLEANUP${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    local count_deleted=0

    # typing_extensions.py
    if [[ -f "$SRC_PKG_DIR/typing_extensions.py" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo -e "${BLUE}[DRY-RUN] rm $SRC_PKG_DIR/typing_extensions.py${NC}"
        else
            cp "$SRC_PKG_DIR/typing_extensions.py" "$SRC_PKG_DIR/typing_extensions.py.backup_$(date +%Y%m%d_%H%M%S)"
            rm "$SRC_PKG_DIR/typing_extensions.py"
            echo -e "${GREEN}✓ Gelöscht: typing_extensions.py${NC}" | tee -a "$LOG_FILE"
            count_deleted=$((count_deleted + 1))
        fi
    fi

    # py.py
    if [[ -f "$SRC_PKG_DIR/py.py" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo -e "${BLUE}[DRY-RUN] rm $SRC_PKG_DIR/py.py${NC}"
        else
            cp "$SRC_PKG_DIR/py.py" "$SRC_PKG_DIR/py.py.backup_$(date +%Y%m%d_%H%M%S)"
            rm "$SRC_PKG_DIR/py.py"
            echo -e "${GREEN}✓ Gelöscht: py.py${NC}" | tee -a "$LOG_FILE"
            count_deleted=$((count_deleted + 1))
        fi
    fi

    # socks.py
    if [[ -f "$SRC_PKG_DIR/socks.py" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo -e "${BLUE}[DRY-RUN] rm $SRC_PKG_DIR/socks.py${NC}"
        else
            cp "$SRC_PKG_DIR/socks.py" "$SRC_PKG_DIR/socks.py.backup_$(date +%Y%m%d_%H%M%S)"
            rm "$SRC_PKG_DIR/socks.py"
            echo -e "${GREEN}✓ Gelöscht: socks.py${NC}" | tee -a "$LOG_FILE"
            count_deleted=$((count_deleted + 1))
        fi
    fi

    # sockshandler.py
    if [[ -f "$SRC_PKG_DIR/sockshandler.py" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo -e "${BLUE}[DRY-RUN] rm $SRC_PKG_DIR/sockshandler.py${NC}"
        else
            cp "$SRC_PKG_DIR/sockshandler.py" "$SRC_PKG_DIR/sockshandler.py.backup_$(date +%Y%m%d_%H%M%S)"
            rm "$SRC_PKG_DIR/sockshandler.py"
            echo -e "${GREEN}✓ Gelöscht: sockshandler.py${NC}" | tee -a "$LOG_FILE"
            count_deleted=$((count_deleted + 1))
        fi
    fi

    echo -e "${GREEN}✅ Gelöscht: $count_deleted Dateien${NC}"
}

# ============================================================================
# REQUIREMENTS.TXT UPDATE
# ============================================================================
update_requirements() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}📝 REQUIREMENTS.TXT UPDATE${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    # Prüfe: PySocks bereits vorhanden?
    if grep -q "PySocks" "$REQUIREMENTS_FILE" 2>/dev/null; then
        echo -e "${YELLOW}⚠ PySocks bereits in requirements.txt – überspringe${NC}"
    else
        if [[ "$DRY_RUN" == "true" ]]; then
            echo -e "${BLUE}[DRY-RUN] Würde PySocks>=1.7.1 hinzufügen${NC}"
        else
            cat >> "$REQUIREMENTS_FILE" <<'EOF'

# ============================================================================
# Vendor-Leak-Cleanup (2025-11-27)
# Ersetzt kopierte venv-Site-Packages durch korrekte Dependencies
# ============================================================================
PySocks>=1.7.1  # Ersetzt src/pkg/socks*.py
EOF
            echo -e "${GREEN}✓ requirements.txt aktualisiert (PySocks>=1.7.1)${NC}" | tee -a "$LOG_FILE"
        fi
    fi

    echo -e "${YELLOW}ℹ Hinweis: typing-extensions NICHT hinzugefügt (Python 3.13 builtin)${NC}"
    echo -e "${YELLOW}  Falls Python < 3.13: Manuell 'typing-extensions>=4.0.0' ergänzen${NC}"
}

# ============================================================================
# VALIDIERUNG
# ============================================================================
validate() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🔍 VALIDIERUNG${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    # Check: Dateien wirklich weg
    local remaining_count=0
    for file in typing_extensions.py py.py socks.py sockshandler.py; do
        if [[ -f "$SRC_PKG_DIR/$file" ]]; then
            echo -e "${RED}✗ Noch vorhanden: $file${NC}"
            remaining_count=$((remaining_count + 1))
        fi
    done

    if [[ $remaining_count -eq 0 ]]; then
        echo -e "${GREEN}✅ Alle venv-Leaks entfernt${NC}"
    else
        echo -e "${RED}❌ $remaining_count Dateien verbleiben${NC}"
    fi

    # Check: Imports noch vorhanden?
    local bad_imports
    bad_imports=$(grep -R "src\.pkg\.\(typing_extensions\|socks\|py\)" "$PROJECT_ROOT" 2>/dev/null | grep -v ".git" | wc -l)

    if [[ $bad_imports -gt 0 ]]; then
        echo -e "${RED}❌ $bad_imports src.pkg-Imports gefunden – Code muss angepasst werden${NC}"
    else
        echo -e "${GREEN}✅ Keine src.pkg-Imports gefunden${NC}"
    fi
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🚨 GOVERNANCE FIX #2: venv → src/pkg CLEANUP${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Start: $(date -u +"%Y-%m-%d %H:%M:%S UTC")${NC}"
    echo -e "${BLUE}DRY-RUN: ${YELLOW}$DRY_RUN${NC}"
    echo ""

    safety_checks
    cleanup_venv_leaks
    update_requirements
    validate

    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Ende: $(date -u +"%Y-%m-%d %H:%M:%S UTC")${NC}"
    echo -e "${BLUE}Log: $LOG_FILE${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        echo -e "${YELLOW}ℹ DRY-RUN abgeschlossen. Für echte Ausführung:${NC}"
        echo -e "${YELLOW}  DRY_RUN=false ./GOVERNANCE_FIX_VENV_LEAKS.sh${NC}"
    fi
}

main "$@"
