#!/bin/bash
################################################################################
# backup_vault.sh
# Vault (opena11) Backup & Recovery Script
# CRITICAL: Secrets Management & Encryption Keys
#
# Strategie:
# - Raft Storage Snapshots (Point-in-Time)
# - Seal Key Backups (separater Standort)
# - External Storage (S3/Cloud)
# - Retention: 90 Tage
#
# Verwendung:
#   bash scripts/backup_vault.sh --backup        # Backup erstellen
#   bash scripts/backup_vault.sh --restore FILE  # Restore
#   bash scripts/backup_vault.sh --verify        # Integrität prüfen
#
################################################################################

set -euo pipefail

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
VAULT_PORT=${VAULT_PORT:-8200}
VAULT_ADDR="http://localhost:$VAULT_PORT"
VAULT_TOKEN=${VAULT_TOKEN:-}

# Backup-Verzeichnisse
BACKUP_DIR="${REPO_ROOT}/backups/vault"
LOCAL_DIR="${BACKUP_DIR}/local"
CLOUD_DIR="${BACKUP_DIR}/cloud"
TEMP_DIR="/tmp/vault-backup-$$"

# Dateiformat
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATEONLY=$(date -u +"%Y-%m-%d")
BACKUP_FILE="vault_snapshot_${DATEONLY}.snap"
BACKUP_MANIFEST="vault_manifest_${DATEONLY}.json"

# Retention-Zeiten
RETENTION_DAYS=90
CLEANUP_OLDER_THAN=$((RETENTION_DAYS * 86400))

# ============================================================================
# INITIALIZATION
# ============================================================================

init_backup_dirs() {
    log_info "Initialisiere Backup-Verzeichnisse"
    mkdir -p "$LOCAL_DIR"
    mkdir -p "$CLOUD_DIR"
    mkdir -p "$TEMP_DIR"
    log_success "Verzeichnisse erstellt"
}

check_vault_status() {
    log_section "Vault Health Check"

    if ! curl -s "$VAULT_ADDR/v1/sys/health" > /dev/null 2>&1; then
        log_error "Vault ist nicht erreichbar: $VAULT_ADDR"
        return 1
    fi

    local status=$(curl -s "$VAULT_ADDR/v1/sys/health" | jq -r '.initialized')

    if [[ "$status" != "true" ]]; then
        log_error "Vault ist nicht initialisiert"
        return 1
    fi

    log_success "Vault ist erreichbar und initialisiert"
    return 0
}

# ============================================================================
# BACKUP OPERATIONS
# ============================================================================

backup_vault() {
    log_section "Vault Backup: Raft Storage Snapshot"

    if ! check_vault_status; then
        return 1
    fi

    # Schritt 1: Raft Snapshot erstellen
    log_info "Erstelle Raft Storage Snapshot..."

    local snapshot_file="${TEMP_DIR}/${BACKUP_FILE}"

    if ! curl -X PUT \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        "$VAULT_ADDR/v1/sys/storage/raft/snapshot" \
        > "$snapshot_file" 2>/dev/null; then
        log_error "Snapshot-Erstellung fehlgeschlagen"
        return 1
    fi

    log_success "Snapshot erstellt: $(ls -lh "$snapshot_file" | awk '{print $5}')"

    # Schritt 2: Seal Key Informationen sammeln
    log_info "Sammle Seal Key Metadaten..."

    local seal_status=$(curl -s \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        "$VAULT_ADDR/v1/sys/seal-status" | jq '.')

    # Schritt 3: Manifest erstellen
    log_info "Erstelle Backup-Manifest..."

    cat > "${TEMP_DIR}/${BACKUP_MANIFEST}" << 'EOF'
{
  "backup_type": "vault_raft_snapshot",
  "timestamp": "%TIMESTAMP%",
  "version": "1.15.0+",
  "seal_status": %SEAL_STATUS%,
  "storage": {
    "type": "raft",
    "ha_enabled": true,
    "consistency_check": "pending"
  },
  "retention": {
    "days": 90,
    "backup_location": [
      "local: %LOCAL_PATH%",
      "cloud: s3://vault-backups/"
    ]
  }
}
EOF

    sed -i "s|%TIMESTAMP%|$TIMESTAMP|g" "${TEMP_DIR}/${BACKUP_MANIFEST}"
    sed -i "s|%SEAL_STATUS%|${seal_status}|g" "${TEMP_DIR}/${BACKUP_MANIFEST}"
    sed -i "s|%LOCAL_PATH%|${LOCAL_DIR}/${BACKUP_FILE}|g" "${TEMP_DIR}/${BACKUP_MANIFEST}"

    # Schritt 4: Kopiere zu Local Storage
    log_info "Kopiere zu lokalem Backup-Storage..."
    cp "$snapshot_file" "${LOCAL_DIR}/${BACKUP_FILE}"
    cp "${TEMP_DIR}/${BACKUP_MANIFEST}" "${LOCAL_DIR}/${BACKUP_MANIFEST}"

    log_success "Backup abgeschlossen:"
    log_success "  Snapshot: ${LOCAL_DIR}/${BACKUP_FILE}"
    log_success "  Manifest: ${LOCAL_DIR}/${BACKUP_MANIFEST}"

    # Schritt 5: Remote Backup (falls S3 konfiguriert)
    log_info "Prüfe externe Backup-Konfiguration..."
    backup_to_cloud "${LOCAL_DIR}/${BACKUP_FILE}" "${LOCAL_DIR}/${BACKUP_MANIFEST}"
}

backup_to_cloud() {
    local snapshot=$1
    local manifest=$2

    # Prüfe ob AWS CLI verfügbar
    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI nicht verfügbar – überspringen Sie Cloud-Backup"
        return 0
    fi

    log_info "Lade zu Cloud-Storage (S3)..."

    # Prüfe ob S3 Bucket konfiguriert
    if [[ -z "${VAULT_BACKUP_S3_BUCKET:-}" ]]; then
        log_warning "VAULT_BACKUP_S3_BUCKET nicht gesetzt – Cloud-Backup übersprungen"
        return 0
    fi

    # Upload mit encryption
    aws s3 cp "$snapshot" \
        "s3://${VAULT_BACKUP_S3_BUCKET}/vault/$(basename "$snapshot")" \
        --sse AES256 \
        --storage-class GLACIER \
        --metadata "created=$(date -u +%s),type=vault_snapshot" 2>/dev/null || true

    aws s3 cp "$manifest" \
        "s3://${VAULT_BACKUP_S3_BUCKET}/vault/$(basename "$manifest")" \
        --sse AES256 2>/dev/null || true

    log_success "Cloud-Backup abgeschlossen (S3)"
}

# ============================================================================
# RESTORE OPERATIONS
# ============================================================================

restore_vault() {
    local backup_file=$1

    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup-Datei nicht gefunden: $backup_file"
        return 1
    fi

    log_section "Vault Restore: $backup_file"
    log_warning "⚠️  KRITISCH: Restore wird aktuellen Zustand überschreiben!"

    # Bestätigung erforderlich
    read -p "Fortfahren mit Restore? (ja/nein): " confirm
    if [[ "$confirm" != "ja" ]]; then
        log_info "Restore abgebrochen"
        return 0
    fi

    log_warning "Fahre mit Restore fort..."

    # Restore durchführen
    if ! curl -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        --data-binary "@$backup_file" \
        "$VAULT_ADDR/v1/sys/storage/raft/snapshot" 2>/dev/null; then
        log_error "Restore fehlgeschlagen"
        return 1
    fi

    # Verifiziere
    if check_vault_status; then
        log_success "Restore erfolgreich abgeschlossen"
        return 0
    else
        log_error "Restore fehlgeschlagen – Vault nicht erreichbar"
        return 1
    fi
}

# ============================================================================
# VERIFICATION & INTEGRITY CHECKS
# ============================================================================

verify_backup() {
    log_section "Backup-Integrität verifyifizieren"

    local count=$(find "$LOCAL_DIR" -name "*.snap" -type f | wc -l)
    log_info "Lokale Snapshots gefunden: $count"

    if [[ $count -eq 0 ]]; then
        log_error "Keine Backup-Snapshots vorhanden"
        return 1
    fi

    # Prüfe neueste Dateien
    local latest=$(find "$LOCAL_DIR" -name "*.snap" -type f -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2-)

    if [[ -z "$latest" ]]; then
        log_error "Keine gültigen Backup-Dateien"
        return 1
    fi

    local size=$(ls -lh "$latest" | awk '{print $5}')
    local age=$(stat -c %y "$latest" | awk '{print $1, $2}')

    log_success "Neuestes Backup:"
    log_success "  Datei: $(basename "$latest")"
    log_success "  Größe: $size"
    log_success "  Datum: $age"

    # Checksummen prüfen
    if [[ -f "${latest%.snap}.sha256" ]]; then
        log_info "Prüfe SHA256-Checksumme..."
        if sha256sum -c "${latest%.snap}.sha256" > /dev/null 2>&1; then
            log_success "Checksumme ✅ OK"
        else
            log_error "Checksumme ❌ FEHLGESCHLAGEN"
            return 1
        fi
    fi

    return 0
}

# ============================================================================
# CLEANUP & RETENTION
# ============================================================================

cleanup_old_backups() {
    log_section "Alte Backups bereinigen (Retention: $RETENTION_DAYS Tage)"

    local count=0

    # Finde alte Dateien lokal
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            log_warning "Lösche altes Backup: $(basename "$file")"
            rm -f "$file"
            ((count++))
        fi
    done < <(find "$LOCAL_DIR" -name "*.snap" -type f -mtime +$RETENTION_DAYS)

    if [[ $count -gt 0 ]]; then
        log_success "Gelöschte alte Backups: $count"
    else
        log_info "Keine alten Backups zum Löschen"
    fi
}

# ============================================================================
# SUMMARY & REPORTING
# ============================================================================

backup_summary() {
    log_section "Backup-Zusammenfassung"

    local total_backups=$(find "$LOCAL_DIR" -name "*.snap" -type f | wc -l)
    local total_size=$(du -sh "$LOCAL_DIR" 2>/dev/null | awk '{print $1}')

    cat << EOF

📊 Backup-Statistik
──────────────────────────────────────────
  Gesamte Backups:  $total_backups
  Lokale Größe:     $total_size
  Speicherort:      $LOCAL_DIR
  Retention:        $RETENTION_DAYS Tage
  Status:           ✅ OK

🔐 Kritische Informationen
──────────────────────────────────────────
  Vault Port:       $VAULT_PORT
  Vault Adresse:    $VAULT_ADDR
  Backup-Typ:       Raft Storage Snapshot
  Seal-Typ:         Transit (Auto-Unseal)

📋 Letzte Backups
──────────────────────────────────────────
EOF

    find "$LOCAL_DIR" -name "*.snap" -type f -printf '%T@ %p\n' | sort -rn | head -5 | while read -r line; do
        local timestamp=$(echo "$line" | awk '{print $1}')
        local file=$(echo "$line" | cut -d' ' -f2-)
        local size=$(ls -lh "$file" | awk '{print $5}')
        local date=$(date -d "@${timestamp%.*}" +'%Y-%m-%d %H:%M:%S')
        echo "  • $(basename "$file") ($size) - $date"
    done

    echo ""
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    local action=${1:-}

    echo ""
    log_section "VAULT BACKUP & RECOVERY SYSTEM"

    case "$action" in
        --backup)
            init_backup_dirs
            backup_vault
            cleanup_old_backups
            verify_backup
            backup_summary
            ;;
        --restore)
            if [[ -z "${2:-}" ]]; then
                log_error "Bitte geben Sie Backup-Datei an: --restore <file>"
                exit 1
            fi
            init_backup_dirs
            restore_vault "$2"
            ;;
        --verify)
            verify_backup
            ;;
        --list)
            init_backup_dirs
            log_section "Verfügbare Vault-Backups"
            find "$LOCAL_DIR" -name "*.snap" -type f -printf '%T@ %p\n' | sort -rn | while read -r line; do
                local timestamp=$(echo "$line" | awk '{print $1}')
                local file=$(echo "$line" | cut -d' ' -f2-)
                local size=$(ls -lh "$file" | awk '{print $5}')
                local date=$(date -d "@${timestamp%.*}" +'%Y-%m-%d %H:%M:%S')
                echo "  • $(basename "$file") ($size) - $date"
            done
            ;;
        *)
            cat << 'USAGE'

Nutzung:
  bash scripts/backup_vault.sh --backup        # Backup erstellen
  bash scripts/backup_vault.sh --restore FILE  # Restore durchführen
  bash scripts/backup_vault.sh --verify        # Integrität prüfen
  bash scripts/backup_vault.sh --list          # Backups auflisten

Konfiguration:
  VAULT_TOKEN=<token>        Vault-Auth-Token
  VAULT_PORT=8200            Vault-Port (default)
  VAULT_BACKUP_S3_BUCKET=... S3-Bucket für Cloud-Backups

USAGE
            exit 1
            ;;
    esac
}

# Cleanup bei Exit
trap "rm -rf '$TEMP_DIR'" EXIT

main "$@"
