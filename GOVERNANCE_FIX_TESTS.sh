#!/bin/bash
# 🚨 GOVERNANCE FIX #3: tests → _conflicts/ RESCUE
# Datum: 27. November 2025
# Zweck: Produktive Tests & Doku aus Quarantäne zurückholen

set -euo pipefail

# ============================================================================
# KONFIGURATION
# ============================================================================
PROJECT_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
CONFLICTS_DIR="$PROJECT_ROOT/_conflicts/2025-11-09_032949"
TESTS_DIR="$PROJECT_ROOT/19.dashboard_agent/tests"
SCRIPTS_DIR="$PROJECT_ROOT/19.dashboard_agent/scripts"
DOCS_DIR="$PROJECT_ROOT/docs/testing"
LOG_FILE="$PROJECT_ROOT/GOVERNANCE_FIX_TESTS.log"
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
    
    # Check 1: _conflicts/ existiert
    if [[ ! -d "$CONFLICTS_DIR" ]]; then
        echo -e "${YELLOW}⚠ $CONFLICTS_DIR existiert nicht – nichts zu tun${NC}"
        exit 0
    fi
    
    local conflict_count
    conflict_count=$(find "$CONFLICTS_DIR" -type f | wc -l)
    echo -e "${BLUE}ℹ Dateien in _conflicts/: ${YELLOW}$conflict_count${NC}"
    
    # Check 2: Zielverzeichnisse existieren
    mkdir -p "$TESTS_DIR" "$SCRIPTS_DIR" "$DOCS_DIR"
    echo -e "${GREEN}✓ Zielverzeichnisse vorbereitet${NC}"
    
    # Check 3: Konfliktrisiko (Dateien bereits vorhanden?)
    local critical_tests=(
        "test_archivator.py"
        "test_openwebui_agent.py"
        "test_opena4_telegram.sh"
    )
    
    local conflicts_found=false
    for test in "${critical_tests[@]}"; do
        if [[ -f "$TESTS_DIR/$test" ]] && [[ -f "$CONFLICTS_DIR/$test" ]]; then
            echo -e "${YELLOW}⚠ Konflikt: $test existiert bereits in tests/ UND _conflicts/${NC}"
            conflicts_found=true
        fi
    done
    
    if [[ "$conflicts_found" == "true" ]]; then
        echo -e "${YELLOW}  → Script verwendet mv -n (no-clobber)${NC}"
    fi
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        echo -e "${YELLOW}▶ Drücke ENTER zum Fortfahren oder CTRL+C zum Abbrechen${NC}"
        read -r
    fi
}

# ============================================================================
# TEST RESCUE
# ============================================================================
rescue_tests() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🔧 TEST RESCUE (_conflicts/ → tests/)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    local count_moved=0
    local count_skipped=0
    
    local critical_tests=(
        "test_archivator.py"
        "test_openwebui_agent.py"
        "test_opena4_telegram.sh"
        "test_opena5_browser.py"
        "test_opena8_telephone.py"
        "test_opena9_call_tracking.py"
        "test_opena10_unlock.py"
        "test_opena_finance.sh"
        "test_opena4_vscode.py"
        "test_bridge_api.py"
    )
    
    for test in "${critical_tests[@]}"; do
        local src="$CONFLICTS_DIR/$test"
        local dst="$TESTS_DIR/$test"
        
        if [[ ! -f "$src" ]]; then
            echo -e "${YELLOW}⚠ Nicht gefunden: $test${NC}" | tee -a "$LOG_FILE"
            count_skipped=$((count_skipped + 1))
            continue
        fi
        
        if [[ -f "$dst" ]]; then
            echo -e "${YELLOW}⚠ Existiert bereits: $test${NC}" | tee -a "$LOG_FILE"
            count_skipped=$((count_skipped + 1))
            continue
        fi
        
        if [[ "$DRY_RUN" == "true" ]]; then
            echo -e "${BLUE}[DRY-RUN] mv $src → $dst${NC}"
        else
            if mv -n "$src" "$dst"; then
                echo -e "${GREEN}✓ Verschoben: $test${NC}" | tee -a "$LOG_FILE"
                count_moved=$((count_moved + 1))
            else
                echo -e "${RED}✗ Fehler: $test${NC}" | tee -a "$LOG_FILE"
            fi
        fi
    done
    
    echo -e "${GREEN}✅ Tests verschoben: $count_moved${NC}"
    echo -e "${YELLOW}⚠ Übersprungen: $count_skipped${NC}"
}

# ============================================================================
# SCRIPTS RESCUE
# ============================================================================
rescue_scripts() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}📜 SCRIPTS RESCUE (_conflicts/ → scripts/)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    local scripts_to_rescue=(
        "verify_phase2.sh"
        "e2e_integration.sh"
    )
    
    local count_moved=0
    
    for script in "${scripts_to_rescue[@]}"; do
        local src="$CONFLICTS_DIR/$script"
        local dst="$SCRIPTS_DIR/$script"
        
        if [[ ! -f "$src" ]]; then
            echo -e "${YELLOW}⚠ Nicht gefunden: $script${NC}"
            continue
        fi
        
        if [[ "$DRY_RUN" == "true" ]]; then
            echo -e "${BLUE}[DRY-RUN] mv $src → $dst${NC}"
        else
            if mv -n "$src" "$dst"; then
                chmod +x "$dst"
                echo -e "${GREEN}✓ Verschoben & ausführbar: $script${NC}" | tee -a "$LOG_FILE"
                count_moved=$((count_moved + 1))
            fi
        fi
    done
    
    echo -e "${GREEN}✅ Scripts verschoben: $count_moved${NC}"
}

# ============================================================================
# DOCS RESCUE
# ============================================================================
rescue_docs() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}📚 DOCS RESCUE (_conflicts/ → docs/testing/)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    local src="$CONFLICTS_DIR/TESTS_TELEMETRIE_ROLLOUT.md"
    local dst="$DOCS_DIR/TESTS_TELEMETRIE_ROLLOUT_2025-11-09.md"
    
    if [[ ! -f "$src" ]]; then
        echo -e "${YELLOW}⚠ TESTS_TELEMETRIE_ROLLOUT.md nicht gefunden${NC}"
        return
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${BLUE}[DRY-RUN] mv $src → $dst${NC}"
    else
        if mv -n "$src" "$dst"; then
            echo -e "${GREEN}✓ Verschoben: TESTS_TELEMETRIE_ROLLOUT_2025-11-09.md${NC}" | tee -a "$LOG_FILE"
        fi
    fi
}

# ============================================================================
# CONFLICTS README
# ============================================================================
create_conflicts_readme() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}📝 _conflicts/ README${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    local readme="$CONFLICTS_DIR/README.md"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${BLUE}[DRY-RUN] Würde README erstellen in $CONFLICTS_DIR/${NC}"
        return
    fi
    
    cat > "$readme" <<EOF
# Konflikt-Quarantäne vom 9. November 2025 03:29:49

**Status:** Legacy-Archive  
**Grund:** Struktur-Cleanup während Phase 5  
**Datum:** 9. November 2025 03:29:49 UTC

## Zweck

Dieser Ordner diente als temporäre Quarantäne für Dateien, die während der 
automatisierten Struktur-Bereinigung von \`rename_map.csv\` verschoben wurden.

## Wiederherstellung

Alle **produktiv benötigten Dateien** wurden am **27. November 2025** mittels
\`GOVERNANCE_FIX_TESTS.sh\` in ihre korrekten Verzeichnisse zurückverschoben:

- ✅ Tests → \`19.dashboard_agent/tests/\`
- ✅ Scripts → \`19.dashboard_agent/scripts/\`
- ✅ Dokumentation → \`docs/testing/\`

## Verbleibende Dateien

Dateien, die hier verbleiben, sind:
- Legacy-Code ohne produktiven Einsatz
- Duplikate
- Obsolete Konfigurationen

## Archivierung

Dieser Ordner kann nach **1. Dezember 2025** vollständig archiviert oder 
gelöscht werden, sofern keine weiteren Abhängigkeiten bestehen.

---
**Erstellt durch:** \`GOVERNANCE_FIX_TESTS.sh\`  
**Datum:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")  
**Ausgeführt von:** $(whoami)
EOF
    
    echo -e "${GREEN}✓ README erstellt: $readme${NC}" | tee -a "$LOG_FILE"
}

# ============================================================================
# VALIDIERUNG
# ============================================================================
validate() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🔍 VALIDIERUNG${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    # Check: Tests in tests/
    local critical_tests=(
        "test_archivator.py"
        "test_openwebui_agent.py"
    )
    
    local missing_count=0
    for test in "${critical_tests[@]}"; do
        if [[ ! -f "$TESTS_DIR/$test" ]]; then
            echo -e "${RED}✗ Fehlt: $test${NC}"
            missing_count=$((missing_count + 1))
        fi
    done
    
    if [[ $missing_count -eq 0 ]]; then
        echo -e "${GREEN}✅ Alle kritischen Tests vorhanden${NC}"
    else
        echo -e "${RED}❌ $missing_count Tests fehlen${NC}"
    fi
    
    # Check: pytest verfügbar?
    if command -v pytest &> /dev/null; then
        echo -e "${GREEN}✓ pytest verfügbar${NC}"
        if [[ "$DRY_RUN" == "false" ]]; then
            echo -e "${YELLOW}ℹ Test-Durchlauf empfohlen: pytest $TESTS_DIR/${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ pytest nicht installiert – install via: pip install pytest${NC}"
    fi
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🚨 GOVERNANCE FIX #3: tests → _conflicts/ RESCUE${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Start: $(date -u +"%Y-%m-%d %H:%M:%S UTC")${NC}"
    echo -e "${BLUE}DRY-RUN: ${YELLOW}$DRY_RUN${NC}"
    echo ""
    
    safety_checks
    rescue_tests
    rescue_scripts
    rescue_docs
    create_conflicts_readme
    validate
    
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Ende: $(date -u +"%Y-%m-%d %H:%M:%S UTC")${NC}"
    echo -e "${BLUE}Log: $LOG_FILE${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        echo -e "${YELLOW}ℹ DRY-RUN abgeschlossen. Für echte Ausführung:${NC}"
        echo -e "${YELLOW}  DRY_RUN=false ./GOVERNANCE_FIX_TESTS.sh${NC}"
    fi
}

main "$@"
