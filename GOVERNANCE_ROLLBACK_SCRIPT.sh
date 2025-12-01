#!/bin/bash
# 🚨 PORTIER 3.0 GOVERNANCE ROLLBACK SCRIPT
# Automatisierte Korrektur der 3 kritischen Verstöße aus rename_map.csv
# Datum: 27. November 2025
# Auditor: AI Repo Governance Auditor

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ============================================================================
# KONFIGURATION
# ============================================================================
PROJECT_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
CONFIGS_DIR="$PROJECT_ROOT/configs"
CONFLICTS_DIR="$PROJECT_ROOT/_conflicts/2025-11-09_032949"
SRC_PKG_DIR="$PROJECT_ROOT/src/pkg"
TESTS_DIR="$PROJECT_ROOT/19.dashboard_agent/tests"
SCRIPTS_DIR="$PROJECT_ROOT/19.dashboard_agent/scripts"
DOCS_DIR="$PROJECT_ROOT/docs"

LOG_FILE="$PROJECT_ROOT/GOVERNANCE_ROLLBACK.log"
DRY_RUN=false  # Auf 'true' setzen für Simulation

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# LOGGING-FUNKTIONEN
# ============================================================================
log() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[⚠]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

# ============================================================================
# HELPER-FUNKTIONEN
# ============================================================================
backup_file() {
    local file="$1"
    local backup="${file}.backup_$(date +%Y%m%d_%H%M%S)"
    if [[ -f "$file" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            cp "$file" "$backup"
            log "Backup erstellt: $backup"
        else
            log "[DRY-RUN] Würde Backup erstellen: $backup"
        fi
    fi
}

move_file() {
    local src="$1"
    local dst="$2"
    
    # Sicherstellen, dass Zielverzeichnis existiert
    local dst_dir
    dst_dir=$(dirname "$dst")
    
    if [[ "$DRY_RUN" == "false" ]]; then
        mkdir -p "$dst_dir"
        if [[ -f "$src" ]]; then
            mv "$src" "$dst"
            success "Verschoben: $(basename "$src") → $dst"
        else
            warning "Datei nicht gefunden (übersprungen): $src"
        fi
    else
        log "[DRY-RUN] mkdir -p $dst_dir"
        log "[DRY-RUN] mv $src $dst"
    fi
}

# ============================================================================
# SECTION 1: ARCHIV → configs/ ROLLBACK (84 Dateien)
# ============================================================================
rollback_archiv_violations() {
    log "═══════════════════════════════════════════════════════════════"
    log "SECTION 1: ARCHIV → configs/ ROLLBACK (KRITISCH)"
    log "═══════════════════════════════════════════════════════════════"
    
    local count=0
    
    # 19.dashboard_agent/ARCHIV/ → configs/ (26 Dateien)
    log "Rollback: 19.dashboard_agent/ARCHIV/ (26 Dateien)..."
    
    # 2025/11/06
    mkdir -p "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/06"
    move_file "$CONFIGS_DIR/SP1762419411_kordp→opena2_CMD.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/06/SP1762419411_kordp→opena2_CMD.json"
    move_file "$CONFIGS_DIR/SP1762419397_kordp→opena2_CMD.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/06/SP1762419397_kordp→opena2_CMD.json"
    count=$((count + 2))
    
    # 2025/11/08
    mkdir -p "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08"
    move_file "$CONFIGS_DIR/SP1762625396_opena4_telegram→opena2_MESSAGE.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762625396_opena4_telegram→opena2_MESSAGE.json"
    move_file "$CONFIGS_DIR/SP1762636655_opena18_dashboard→opena2_DASHBOARD_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762636655_opena18_dashboard→opena2_DASHBOARD_OP.json"
    move_file "$CONFIGS_DIR/SP1762636655_opena19_workflow→opena2_WORKFLOW_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762636655_opena19_workflow→opena2_WORKFLOW_OP.json"
    move_file "$CONFIGS_DIR/SP1762630921_opena10_unlock→opena2_SECURITY_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630921_opena10_unlock→opena2_SECURITY_OP.json"
    move_file "$CONFIGS_DIR/SP1762625448_opena4_telegram→opena2_MESSAGE.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762625448_opena4_telegram→opena2_MESSAGE.json"
    move_file "$CONFIGS_DIR/SP1762636654_opena16_crm→opena2_CRM_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762636654_opena16_crm→opena2_CRM_OP.json"
    move_file "$CONFIGS_DIR/SP1762630831_opena8_telephone→opena2_CALL_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630831_opena8_telephone→opena2_CALL_OP.json"
    move_file "$CONFIGS_DIR/SP1762625447_opena4_telegram→opena2_MESSAGE.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762625447_opena4_telegram→opena2_MESSAGE.json"
    move_file "$CONFIGS_DIR/SP1762630782_opena8_telephone→opena2_CALL_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630782_opena8_telephone→opena2_CALL_OP.json"
    move_file "$CONFIGS_DIR/SP1762625404_opena4_telegram→opena2_MESSAGE.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762625404_opena4_telegram→opena2_MESSAGE.json"
    move_file "$CONFIGS_DIR/SP1762630756_opena8_telephone→opena2_CALL_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630756_opena8_telephone→opena2_CALL_OP.json"
    move_file "$CONFIGS_DIR/SP1762622903_opena_finance→opena2_TRANSACTION.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762622903_opena_finance→opena2_TRANSACTION.json"
    move_file "$CONFIGS_DIR/SP1762630783_opena8_telephone→opena2_CALL_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630783_opena8_telephone→opena2_CALL_OP.json"
    move_file "$CONFIGS_DIR/SP1762622941_opena_finance→opena2_TRANSACTION.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762622941_opena_finance→opena2_TRANSACTION.json"
    move_file "$CONFIGS_DIR/SP1762630896_opena9_call_tracking→opena2_ANALYTICS_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630896_opena9_call_tracking→opena2_ANALYTICS_OP.json"
    move_file "$CONFIGS_DIR/SP1762630830_opena8_telephone→opena2_CALL_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630830_opena8_telephone→opena2_CALL_OP.json"
    move_file "$CONFIGS_DIR/SP1762636655_opena17_analytics→opena2_ANALYTICS_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762636655_opena17_analytics→opena2_ANALYTICS_OP.json"
    move_file "$CONFIGS_DIR/SP1762630893_opena9_call_tracking→opena2_ANALYTICS_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630893_opena9_call_tracking→opena2_ANALYTICS_OP.json"
    move_file "$CONFIGS_DIR/SP1762622898_opena_finance→opena2_TRANSACTION.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762622898_opena_finance→opena2_TRANSACTION.json"
    move_file "$CONFIGS_DIR/SP1762630744_opena8_telephone→opena2_CALL_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630744_opena8_telephone→opena2_CALL_OP.json"
    move_file "$CONFIGS_DIR/SP1762630931_opena10_unlock→opena2_SECURITY_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630931_opena10_unlock→opena2_SECURITY_OP.json"
    move_file "$CONFIGS_DIR/SP1762636627_kordp→opena2_CMD.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762636627_kordp→opena2_CMD.json"
    move_file "$CONFIGS_DIR/SP1762630918_opena9_call_tracking→opena2_ANALYTICS_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630918_opena9_call_tracking→opena2_ANALYTICS_OP.json"
    move_file "$CONFIGS_DIR/SP1762630755_opena8_telephone→opena2_CALL_OP.json" "$PROJECT_ROOT/19.dashboard_agent/ARCHIV/2025/11/08/SP1762630755_opena8_telephone→opena2_CALL_OP.json"
    count=$((count + 24))
    
    # 1.portier_openai/ARCHIV/ → configs/ (10 Dateien)
    log "Rollback: 1.portier_openai/ARCHIV/ (10 Dateien)..."
    
    mkdir -p "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08"
    move_file "$CONFIGS_DIR/SP1762631529_opena9_call_tracking→opena2_ANALYTICS_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762631529_opena9_call_tracking→opena2_ANALYTICS_OP.json"
    move_file "$CONFIGS_DIR/SP1762631953_opena12_influencer→opena2_INFLUENCER_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762631953_opena12_influencer→opena2_INFLUENCER_OP.json"
    move_file "$CONFIGS_DIR/SP1762631953_opena13_calendar→opena2_CALENDAR_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762631953_opena13_calendar→opena2_CALENDAR_OP.json"
    move_file "$CONFIGS_DIR/SP1762631525_opena8_telephone→opena2_CALL_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762631525_opena8_telephone→opena2_CALL_OP.json"
    move_file "$CONFIGS_DIR/SP1762631953_opena14_html_generator→opena2_HTML_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762631953_opena14_html_generator→opena2_HTML_OP.json"
    move_file "$CONFIGS_DIR/SP1762631532_opena10_unlock→opena2_SECURITY_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762631532_opena10_unlock→opena2_SECURITY_OP.json"
    move_file "$CONFIGS_DIR/SP1762632454_opena11_social_media→opena2_SOCIAL_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762632454_opena11_social_media→opena2_SOCIAL_OP.json"
    move_file "$CONFIGS_DIR/SP1762631953_opena15_shop→opena2_SHOP_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762631953_opena15_shop→opena2_SHOP_OP.json"
    move_file "$CONFIGS_DIR/SP1762631953_opena11_social_media→opena2_SOCIAL_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762631953_opena11_social_media→opena2_SOCIAL_OP.json"
    move_file "$CONFIGS_DIR/SP1762631526_opena8_telephone→opena2_CALL_OP.json" "$PROJECT_ROOT/1.portier_openai/ARCHIV/2025/11/08/SP1762631526_opena8_telephone→opena2_CALL_OP.json"
    count=$((count + 10))
    
    # 1.portier_openai/archivp/ → configs/ (6 Dateien)
    log "Rollback: 1.portier_openai/archivp/ (6 Dateien)..."
    
    mkdir -p "$PROJECT_ROOT/1.portier_openai/archivp/2025/11/03"
    move_file "$CONFIGS_DIR/SP1762143131_kordp→opena2_CMD.json" "$PROJECT_ROOT/1.portier_openai/archivp/2025/11/03/SP1762143131_kordp→opena2_CMD.json"
    move_file "$CONFIGS_DIR/SP1762143089_kordp→opena2_CMD.json" "$PROJECT_ROOT/1.portier_openai/archivp/2025/11/03/SP1762143089_kordp→opena2_CMD.json"
    move_file "$CONFIGS_DIR/SP1762145568_opena1→opena2_CMD.json" "$PROJECT_ROOT/1.portier_openai/archivp/2025/11/03/SP1762145568_opena1→opena2_CMD.json"
    count=$((count + 3))
    
    mkdir -p "$PROJECT_ROOT/1.portier_openai/archivp/2025/11/02"
    move_file "$CONFIGS_DIR/SP1762120025_opena1→opena2_CMD.json" "$PROJECT_ROOT/1.portier_openai/archivp/2025/11/02/SP1762120025_opena1→opena2_CMD.json"
    move_file "$CONFIGS_DIR/SP1762120019_opena1→opena2_CMD.json" "$PROJECT_ROOT/1.portier_openai/archivp/2025/11/02/SP1762120019_opena1→opena2_CMD.json"
    move_file "$CONFIGS_DIR/SP1762120040_opena1→opena2_CMD.json" "$PROJECT_ROOT/1.portier_openai/archivp/2025/11/02/SP1762120040_opena1→opena2_CMD.json"
    count=$((count + 3))
    
    success "ARCHIV-Rollback abgeschlossen: $count Dateien verschoben"
}

# ============================================================================
# SECTION 2: venv → src/pkg CLEANUP (6 Dateien)
# ============================================================================
cleanup_venv_leaks() {
    log "═══════════════════════════════════════════════════════════════"
    log "SECTION 2: venv → src/pkg CLEANUP (HIGH)"
    log "═══════════════════════════════════════════════════════════════"
    
    local count=0
    
    # typing_extensions.py (Python 3.13 builtin)
    if [[ -f "$SRC_PKG_DIR/typing_extensions.py" ]]; then
        backup_file "$SRC_PKG_DIR/typing_extensions.py"
        if [[ "$DRY_RUN" == "false" ]]; then
            rm "$SRC_PKG_DIR/typing_extensions.py"
            success "Entfernt: typing_extensions.py (Python 3.13 builtin)"
        else
            log "[DRY-RUN] rm $SRC_PKG_DIR/typing_extensions.py"
        fi
        count=$((count + 1))
    fi
    
    # py.py (pytest dependency)
    if [[ -f "$SRC_PKG_DIR/py.py" ]]; then
        backup_file "$SRC_PKG_DIR/py.py"
        if [[ "$DRY_RUN" == "false" ]]; then
            rm "$SRC_PKG_DIR/py.py"
            success "Entfernt: py.py (pytest dependency)"
        else
            log "[DRY-RUN] rm $SRC_PKG_DIR/py.py"
        fi
        count=$((count + 1))
    fi
    
    # socks.py + sockshandler.py (PySocks package)
    if [[ -f "$SRC_PKG_DIR/socks.py" ]]; then
        backup_file "$SRC_PKG_DIR/socks.py"
        if [[ "$DRY_RUN" == "false" ]]; then
            rm "$SRC_PKG_DIR/socks.py"
            success "Entfernt: socks.py (PySocks package)"
        else
            log "[DRY-RUN] rm $SRC_PKG_DIR/socks.py"
        fi
        count=$((count + 1))
    fi
    
    if [[ -f "$SRC_PKG_DIR/sockshandler.py" ]]; then
        backup_file "$SRC_PKG_DIR/sockshandler.py"
        if [[ "$DRY_RUN" == "false" ]]; then
            rm "$SRC_PKG_DIR/sockshandler.py"
            success "Entfernt: sockshandler.py (PySocks package)"
        else
            log "[DRY-RUN] rm $SRC_PKG_DIR/sockshandler.py"
        fi
        count=$((count + 1))
    fi
    
    # requirements.txt aktualisieren
    if [[ "$DRY_RUN" == "false" ]]; then
        cat >> "$PROJECT_ROOT/requirements.txt" <<'EOF'

# ============================================================================
# Vendor-Leak-Cleanup (2025-11-27)
# Ersetzt kopierte venv-Site-Packages durch korrekte Dependencies
# ============================================================================
PySocks>=1.7.1  # Ersetzt src/pkg/socks*.py
pytest>=7.4.0   # Ersetzt src/pkg/py.py
# typing-extensions nicht mehr nötig (Python 3.13 builtin)
EOF
        success "requirements.txt aktualisiert mit Dependencies"
    else
        log "[DRY-RUN] Würde requirements.txt aktualisieren"
    fi
    
    success "venv-Cleanup abgeschlossen: $count Dateien entfernt"
}

# ============================================================================
# SECTION 3: tests → _conflicts/ RESCUE (30+ Dateien)
# ============================================================================
rescue_quarantined_tests() {
    log "═══════════════════════════════════════════════════════════════"
    log "SECTION 3: tests → _conflicts/ RESCUE (HIGH)"
    log "═══════════════════════════════════════════════════════════════"
    
    local count=0
    
    # Sicherstellen, dass Zielverzeichnisse existieren
    mkdir -p "$TESTS_DIR"
    mkdir -p "$SCRIPTS_DIR"
    mkdir -p "$DOCS_DIR/testing"
    
    # KRITISCHE Tests zurückholen
    log "Rescue: Kritische Tests..."
    
    move_file "$CONFLICTS_DIR/test_archivator.py" "$TESTS_DIR/test_archivator.py"
    move_file "$CONFLICTS_DIR/test_openwebui_agent.py" "$TESTS_DIR/test_openwebui_agent.py"
    move_file "$CONFLICTS_DIR/test_opena4_telegram.sh" "$TESTS_DIR/test_opena4_telegram.sh"
    move_file "$CONFLICTS_DIR/test_opena5_browser.py" "$TESTS_DIR/test_opena5_browser.py"
    move_file "$CONFLICTS_DIR/test_opena8_telephone.py" "$TESTS_DIR/test_opena8_telephone.py"
    move_file "$CONFLICTS_DIR/test_opena9_call_tracking.py" "$TESTS_DIR/test_opena9_call_tracking.py"
    move_file "$CONFLICTS_DIR/test_opena10_unlock.py" "$TESTS_DIR/test_opena10_unlock.py"
    move_file "$CONFLICTS_DIR/test_opena_finance.sh" "$TESTS_DIR/test_opena_finance.sh"
    move_file "$CONFLICTS_DIR/test_opena4_vscode.py" "$TESTS_DIR/test_opena4_vscode.py"
    move_file "$CONFLICTS_DIR/test_bridge_api.py" "$TESTS_DIR/test_bridge_api.py"
    count=$((count + 10))
    
    # Scripts zurückholen
    log "Rescue: Scripts..."
    move_file "$CONFLICTS_DIR/verify_phase2.sh" "$SCRIPTS_DIR/verify_phase2.sh"
    move_file "$CONFLICTS_DIR/e2e_integration.sh" "$SCRIPTS_DIR/e2e_integration.sh"
    count=$((count + 2))
    
    # Doku übernehmen
    log "Rescue: Dokumentation..."
    move_file "$CONFLICTS_DIR/TESTS_TELEMETRIE_ROLLOUT.md" "$DOCS_DIR/testing/TESTS_TELEMETRIE_ROLLOUT_2025-11-09.md"
    count=$((count + 1))
    
    # README in _conflicts/ erstellen
    if [[ "$DRY_RUN" == "false" ]]; then
        cat > "$CONFLICTS_DIR/README.md" <<'EOF'
# Konflikt-Quarantäne vom 9. November 2025 03:29:49

**Status:** Legacy-Archive  
**Grund:** Struktur-Cleanup während Phase 5  
**Datum:** 9. November 2025 03:29:49 UTC

## Zweck

Dieser Ordner diente als temporäre Quarantäne für Dateien, die während der 
automatisierten Struktur-Bereinigung von `rename_map.csv` verschoben wurden.

## Wiederherstellung

Alle **produktiv benötigten Dateien** wurden am **27. November 2025** mittels
`GOVERNANCE_ROLLBACK_SCRIPT.sh` in ihre korrekten Verzeichnisse zurückverschoben:

- ✅ Tests → `tests/`
- ✅ Scripts → `scripts/`
- ✅ Dokumentation → `docs/testing/`

## Verbleibende Dateien

Dateien, die hier verbleiben, sind:
- Legacy-Code ohne produktiven Einsatz
- Duplikate
- Obsolete Konfigurationen

## Archivierung

Dieser Ordner kann nach **1. Dezember 2025** vollständig archiviert oder 
gelöscht werden, sofern keine weiteren Abhängigkeiten bestehen.

---
**Erstellt durch:** `GOVERNANCE_ROLLBACK_SCRIPT.sh`  
**Datum:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF
        success "README in _conflicts/ erstellt"
    fi
    
    success "Test-Rescue abgeschlossen: $count Dateien wiederhergestellt"
}

# ============================================================================
# SECTION 4: VALIDIERUNG
# ============================================================================
validate_compliance() {
    log "═══════════════════════════════════════════════════════════════"
    log "SECTION 4: COMPLIANCE-VALIDIERUNG"
    log "═══════════════════════════════════════════════════════════════"
    
    local all_passed=true
    
    # Check 1: Keine Safepoints in configs/
    log "Check 1: Keine SP*.json in configs/..."
    local sp_count
    sp_count=$(find "$CONFIGS_DIR" -name "SP*.json" 2>/dev/null | wc -l)
    if [[ $sp_count -eq 0 ]]; then
        success "✓ Keine Safepoints in configs/ ($sp_count Dateien)"
    else
        error "✗ FEHLER: $sp_count Safepoint-Dateien verbleiben in configs/"
        all_passed=false
    fi
    
    # Check 2: Safepoints zurück in ARCHIV/
    log "Check 2: Safepoints in ARCHIV/ vorhanden..."
    local archiv_count
    archiv_count=$(find "$PROJECT_ROOT" -path "*/ARCHIV/*.json" -o -path "*/archivp/*.json" 2>/dev/null | wc -l)
    if [[ $archiv_count -ge 42 ]]; then
        success "✓ $archiv_count Safepoints in ARCHIV/archivp/"
    else
        error "✗ FEHLER: Nur $archiv_count Safepoints gefunden (erwartet: ≥42)"
        all_passed=false
    fi
    
    # Check 3: Keine venv-Leaks in src/pkg/
    log "Check 3: Keine venv-Leaks in src/pkg/..."
    local venv_leaks=0
    [[ -f "$SRC_PKG_DIR/typing_extensions.py" ]] && venv_leaks=$((venv_leaks + 1))
    [[ -f "$SRC_PKG_DIR/socks.py" ]] && venv_leaks=$((venv_leaks + 1))
    [[ -f "$SRC_PKG_DIR/py.py" ]] && venv_leaks=$((venv_leaks + 1))
    
    if [[ $venv_leaks -eq 0 ]]; then
        success "✓ Keine venv-Leaks in src/pkg/"
    else
        error "✗ FEHLER: $venv_leaks venv-Leak-Dateien gefunden"
        all_passed=false
    fi
    
    # Check 4: Tests zurück in tests/
    log "Check 4: Kritische Tests in tests/..."
    local critical_tests=(
        "test_archivator.py"
        "test_openwebui_agent.py"
        "test_opena4_telegram.sh"
    )
    local missing_tests=0
    for test in "${critical_tests[@]}"; do
        if [[ ! -f "$TESTS_DIR/$test" ]]; then
            error "  ✗ Fehlt: $test"
            missing_tests=$((missing_tests + 1))
        fi
    done
    
    if [[ $missing_tests -eq 0 ]]; then
        success "✓ Alle kritischen Tests vorhanden (${#critical_tests[@]} Dateien)"
    else
        error "✗ FEHLER: $missing_tests Tests fehlen"
        all_passed=false
    fi
    
    # Gesamtergebnis
    log "═══════════════════════════════════════════════════════════════"
    if [[ "$all_passed" == "true" ]]; then
        success "✅ ALLE CHECKS BESTANDEN - REPO IST KONFORM"
        log ""
        log "Nächste Schritte:"
        log "  1. CI/CD-Pipeline testen: pytest tests/"
        log "  2. opena2 Config prüfen: grep ARCHIV 1.portier_openai/config/*.json"
        log "  3. Dependencies installieren: pip install -r requirements.txt"
        return 0
    else
        error "❌ COMPLIANCE-FEHLER - MANUELLE REVIEW ERFORDERLICH"
        log ""
        log "Siehe Log-Datei für Details: $LOG_FILE"
        return 1
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
main() {
    log "═══════════════════════════════════════════════════════════════"
    log "🚨 PORTIER 3.0 GOVERNANCE ROLLBACK SCRIPT"
    log "═══════════════════════════════════════════════════════════════"
    log "Start: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    log "Projekt-Root: $PROJECT_ROOT"
    log "DRY-RUN: $DRY_RUN"
    log "═══════════════════════════════════════════════════════════════"
    
    # Backup .env (falls vorhanden)
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        backup_file "$PROJECT_ROOT/.env"
    fi
    
    # Section 1: ARCHIV-Rollback
    rollback_archiv_violations
    
    # Section 2: venv-Cleanup
    cleanup_venv_leaks
    
    # Section 3: Test-Rescue
    rescue_quarantined_tests
    
    # Section 4: Validierung
    validate_compliance
    local validation_result=$?
    
    log "═══════════════════════════════════════════════════════════════"
    log "Ende: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    log "Log-Datei: $LOG_FILE"
    log "═══════════════════════════════════════════════════════════════"
    
    exit $validation_result
}

# ============================================================================
# ENTRY POINT
# ============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
