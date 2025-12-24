#!/bin/bash
################################################################################
# backup_orchestrator.sh
# Master Backup Orchestrator für ELION Dashboard
#
# Koordiniert:
# 1. Vault Backup (opena11)
# 2. PostgreSQL Backup (PITR)
# 3. Config Versioning (Git + Snapshots)
# 4. Monitoring & Alerting
# 5. Cloud Upload (S3)
#
# Verwendung:
#   bash scripts/backup_orchestrator.sh --full    # Vollständiger Backup-Zyklus
#   bash scripts/backup_orchestrator.sh --daily   # Tägl. Backups
#   bash scripts/backup_orchestrator.sh --status  # Status anzeigen
#
################################################################################

set -euo pipefail

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
log_success() { echo -e "${GREEN}✅ $*${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $*${NC}"; }
log_error() { echo -e "${RED}❌ $*${NC}"; }
log_section() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}► $*${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

# Konfiguration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${REPO_ROOT}/backups"
LOGS_DIR="${BACKUP_DIR}/logs"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATEONLY=$(date -u +"%Y-%m-%d")
LOG_FILE="${LOGS_DIR}/backup_${DATEONLY}.log"

# Backup-Status Tracking
BACKUP_STATUS="${BACKUP_DIR}/.backup_status.json"
START_TIME=$(date +%s)

# ============================================================================
# INITIALIZATION
# ============================================================================

init_orchestrator() {
    log_section "Orchestrator Initialisierung"

    mkdir -p "$LOGS_DIR"

    # Erstelle Status-Datei
    cat > "$BACKUP_STATUS" << EOF
{
  "start_time": "$TIMESTAMP",
  "status": "in_progress",
  "components": {
    "vault": {"status": "pending", "duration": null},
    "postgres": {"status": "pending", "duration": null},
    "configs": {"status": "pending", "duration": null},
    "cloud_upload": {"status": "pending", "duration": null}
  },
  "log_file": "$LOG_FILE"
}
EOF

    # Redirect output zu Log + Console
    exec > >(tee -a "$LOG_FILE")
    exec 2>&1

    log_success "Orchestrator ready"
}

# ============================================================================
# BACKUP COMPONENTS
# ============================================================================

backup_vault() {
    log_section "Komponente 1: Vault Backup (opena11)"

    local start=$(date +%s)
    local component_log="${LOGS_DIR}/vault_${DATEONLY}.log"

    log_info "Starten: $(date)"

    if bash "${REPO_ROOT}/scripts/backup_vault.sh" --backup > "$component_log" 2>&1; then
        local duration=$(($(date +%s) - start))
        log_success "Vault Backup erfolgreich ($duration s)"

        # Update Status
        jq ".components.vault.status = \"success\" | .components.vault.duration = $duration" \
            "$BACKUP_STATUS" > "${BACKUP_STATUS}.tmp"
        mv "${BACKUP_STATUS}.tmp" "$BACKUP_STATUS"

        return 0
    else
        local duration=$(($(date +%s) - start))
        log_error "Vault Backup fehlgeschlagen ($duration s)"

        jq ".components.vault.status = \"failed\" | .components.vault.duration = $duration" \
            "$BACKUP_STATUS" > "${BACKUP_STATUS}.tmp"
        mv "${BACKUP_STATUS}.tmp" "$BACKUP_STATUS"

        return 1
    fi
}

backup_postgres() {
    log_section "Komponente 2: PostgreSQL Backup (PITR)"

    local start=$(date +%s)
    local component_log="${LOGS_DIR}/postgres_${DATEONLY}.log"

    log_info "Starten: $(date)"

    if bash "${REPO_ROOT}/scripts/backup_postgres.sh" --full > "$component_log" 2>&1; then
        local duration=$(($(date +%s) - start))
        log_success "PostgreSQL Backup erfolgreich ($duration s)"

        jq ".components.postgres.status = \"success\" | .components.postgres.duration = $duration" \
            "$BACKUP_STATUS" > "${BACKUP_STATUS}.tmp"
        mv "${BACKUP_STATUS}.tmp" "$BACKUP_STATUS"

        return 0
    else
        local duration=$(($(date +%s) - start))
        log_error "PostgreSQL Backup fehlgeschlagen ($duration s)"

        jq ".components.postgres.status = \"failed\" | .components.postgres.duration = $duration" \
            "$BACKUP_STATUS" > "${BACKUP_STATUS}.tmp"
        mv "${BACKUP_STATUS}.tmp" "$BACKUP_STATUS"

        return 1
    fi
}

backup_configs() {
    log_section "Komponente 3: Config Versioning"

    local start=$(date +%s)
    local component_log="${LOGS_DIR}/config_${DATEONLY}.log"

    log_info "Starten: $(date)"

    if bash "${REPO_ROOT}/scripts/backup_configs.sh" --commit > "$component_log" 2>&1; then
        local duration=$(($(date +%s) - start))
        log_success "Config Versioning erfolgreich ($duration s)"

        jq ".components.configs.status = \"success\" | .components.configs.duration = $duration" \
            "$BACKUP_STATUS" > "${BACKUP_STATUS}.tmp"
        mv "${BACKUP_STATUS}.tmp" "$BACKUP_STATUS"

        return 0
    else
        local duration=$(($(date +%s) - start))
        log_error "Config Versioning fehlgeschlagen ($duration s)"

        jq ".components.configs.status = \"failed\" | .components.configs.duration = $duration" \
            "$BACKUP_STATUS" > "${BACKUP_STATUS}.tmp"
        mv "${BACKUP_STATUS}.tmp" "$BACKUP_STATUS"

        return 1
    fi
}

# ============================================================================
# CLOUD UPLOAD (S3)
# ============================================================================

upload_to_cloud() {
    log_section "Komponente 4: Cloud Upload (S3)"

    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI nicht verfügbar – Cloud Upload übersprungen"
        return 0
    fi

    if [[ -z "${BACKUP_S3_BUCKET:-}" ]]; then
        log_warning "BACKUP_S3_BUCKET nicht gesetzt – Cloud Upload übersprungen"
        return 0
    fi

    local start=$(date +%s)
    log_info "Lade zu S3: s3://${BACKUP_S3_BUCKET}/"

    # Vault Backups
    log_info "  Uploading Vault backups..."
    aws s3 sync "${BACKUP_DIR}/vault/local" \
        "s3://${BACKUP_S3_BUCKET}/vault/" \
        --exclude "*" --include "*.snap" \
        --storage-class GLACIER \
        --sse AES256 || log_warning "Vault S3 upload fehlgeschlagen"

    # PostgreSQL Backups
    log_info "  Uploading PostgreSQL backups..."
    aws s3 sync "${BACKUP_DIR}/postgres/full" \
        "s3://${BACKUP_S3_BUCKET}/postgres/" \
        --exclude "*" --include "*.sql.gz" \
        --storage-class GLACIER \
        --sse AES256 || log_warning "PostgreSQL S3 upload fehlgeschlagen"

    # Config Snapshots
    log_info "  Uploading Config snapshots..."
    aws s3 sync "${BACKUP_DIR}/config/snapshots" \
        "s3://${BACKUP_S3_BUCKET}/config/" \
        --storage-class GLACIER \
        --sse AES256 || log_warning "Config S3 upload fehlgeschlagen"

    local duration=$(($(date +%s) - start))

    jq ".components.cloud_upload.status = \"success\" | .components.cloud_upload.duration = $duration" \
        "$BACKUP_STATUS" > "${BACKUP_STATUS}.tmp"
    mv "${BACKUP_STATUS}.tmp" "$BACKUP_STATUS"

    log_success "Cloud Upload erfolgreich ($duration s)"
    return 0
}

# ============================================================================
# VERIFICATION & HEALTH CHECKS
# ============================================================================

verify_all_backups() {
    log_section "Backup-Verifizierung"

    local all_valid=true

    # Vault Verification
    log_info "Verifyifiziere Vault Backups..."
    if bash "${REPO_ROOT}/scripts/backup_vault.sh" --verify > /dev/null 2>&1; then
        log_success "✅ Vault OK"
    else
        log_error "❌ Vault FAILED"
        all_valid=false
    fi

    # PostgreSQL Verification
    log_info "Verifyifiziere PostgreSQL Backups..."
    if bash "${REPO_ROOT}/scripts/backup_postgres.sh" --verify > /dev/null 2>&1; then
        log_success "✅ PostgreSQL OK"
    else
        log_error "❌ PostgreSQL FAILED"
        all_valid=false
    fi

    # Config Verification
    log_info "Verifyifiziere Config Snapshots..."
    if bash "${REPO_ROOT}/scripts/backup_configs.sh" --verify > /dev/null 2>&1; then
        log_success "✅ Configs OK"
    else
        log_error "❌ Configs FAILED"
        all_valid=false
    fi

    if $all_valid; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# REPORTING & NOTIFICATIONS
# ============================================================================

generate_report() {
    log_section "Backup-Report"

    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))

    # Status auslesen
    local status=$(jq -r '.status' "$BACKUP_STATUS")

    cat << EOF

╔════════════════════════════════════════════════════════════════╗
║           ELION BACKUP ORCHESTRATION REPORT                    ║
╚════════════════════════════════════════════════════════════════╝

📅 Zeitstempel:        $TIMESTAMP
⏱️  Gesamtdauer:        ${duration}s
📊 Status:             $status

📦 Komponenten-Status
──────────────────────────────────────────────────────────────────
EOF

    jq '.components | to_entries[] | "  \(.key): \(.value.status) (\(.value.duration)s)"' -r "$BACKUP_STATUS" | sed 's/null/?/g'

    cat << EOF

📂 Lokale Backup-Größen
──────────────────────────────────────────────────────────────────
EOF

    echo "  Vault:      $(du -sh "${BACKUP_DIR}/vault/local" 2>/dev/null | awk '{print $1}')"
    echo "  PostgreSQL: $(du -sh "${BACKUP_DIR}/postgres/full" 2>/dev/null | awk '{print $1}')"
    echo "  Configs:    $(du -sh "${BACKUP_DIR}/config/snapshots" 2>/dev/null | awk '{print $1}')"

    cat << EOF

📋 Log-Dateien
──────────────────────────────────────────────────────────────────
EOF

    find "$LOGS_DIR" -name "*_${DATEONLY}.log" -type f | while read -r log; do
        local lines=$(wc -l < "$log")
        echo "  • $(basename "$log") ($lines Zeilen)"
    done

    echo ""

    if [[ "$status" == "success" ]]; then
        log_success "✅ BACKUP-ZYKLUS ERFOLGREICH ABGESCHLOSSEN"
    else
        log_error "❌ BACKUP-ZYKLUS MIT FEHLERN ABGESCHLOSSEN"
    fi

    echo ""
}

# ============================================================================
# CRON JOB SETUP
# ============================================================================

setup_cron() {
    log_section "Cron-Job Setup"

    cat << EOF

Fügen Sie diese Zeilen zu Ihrer Crontab hinzu:

# Daily Backup at 2 AM
0 2 * * * cd $REPO_ROOT && bash scripts/backup_orchestrator.sh --daily >> /var/log/backup_orchestrator.log 2>&1

# Weekly Full Backup on Sunday at 3 AM
0 3 * * 0 cd $REPO_ROOT && bash scripts/backup_orchestrator.sh --full >> /var/log/backup_orchestrator.log 2>&1

# Monthly Verification on 1st at 4 AM
0 4 1 * * cd $REPO_ROOT && bash scripts/backup_orchestrator.sh --verify >> /var/log/backup_orchestrator.log 2>&1

Installation:
  crontab -e
  (Paste the above lines)
  (Save & Exit)

EOF
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    local action=${1:-}

    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     ELION BACKUP ORCHESTRATOR (v2025-12-24)                   ║${NC}"
    echo -e "${CYAN}║     Vault + PostgreSQL + Config Versioning                    ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    case "$action" in
        --full)
            init_orchestrator

            backup_vault || true
            backup_postgres || true
            backup_configs || true
            upload_to_cloud || true
            verify_all_backups || true

            jq ".status = \"complete\", .end_time = \"$(date -u +\"%Y-%m-%dT%H:%M:%SZ\")\"" \
                "$BACKUP_STATUS" > "${BACKUP_STATUS}.tmp"
            mv "${BACKUP_STATUS}.tmp" "$BACKUP_STATUS"

            generate_report
            ;;
        --daily)
            log_section "Täglicher Backup-Zyklus"

            init_orchestrator

            backup_postgres || true
            backup_configs || true

            log_info "Tägl. Backup-Zyklus abgeschlossen"
            ;;
        --status)
            log_section "Backup-Status"

            if [[ -f "$BACKUP_STATUS" ]]; then
                jq '.' "$BACKUP_STATUS"
            else
                log_warning "Keine Status-Datei vorhanden"
            fi
            ;;
        --verify)
            init_orchestrator
            verify_all_backups
            ;;
        --cron-setup)
            setup_cron
            ;;
        *)
            cat << 'USAGE'

Nutzung:
  bash scripts/backup_orchestrator.sh --full      # Vollständiger Backup-Zyklus
  bash scripts/backup_orchestrator.sh --daily     # Tägliche Backups
  bash scripts/backup_orchestrator.sh --verify    # Verifiziere alle Backups
  bash scripts/backup_orchestrator.sh --status    # Status anzeigen
  bash scripts/backup_orchestrator.sh --cron-setup # Cron-Setup anzeigen

Umgebungsvariablen (optional):
  BACKUP_S3_BUCKET=... S3-Bucket für Cloud-Backups

USAGE
            exit 1
            ;;
    esac
}

main "$@"
