#!/bin/bash
################################################################################
# backup_configs.sh
# Config-Versionierung & Git-basierte Backups
#
# Strategie:
# - System Baseline (system_baseline.yaml)
# - Entitlements (entitlements.json)
# - Agent Configurations (*/config/)
# - Environment Files (.env variations)
# - Git Commits pro Release
#
# Verwendung:
#   bash scripts/backup_configs.sh --snapshot    # Config-Snapshot
#   bash scripts/backup_configs.sh --commit      # Git Commit
#   bash scripts/backup_configs.sh --verify      # Integrität prüfen
#   bash scripts/backup_configs.sh --restore TAG # Restore
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
CONFIG_DIR="${REPO_ROOT}/config"
BACKUPS_DIR="${REPO_ROOT}/backups/config"
SNAPSHOTS_DIR="${BACKUPS_DIR}/snapshots"
TEMPLATES_DIR="${CONFIG_DIR}/templates"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATEONLY=$(date -u +"%Y-%m-%d")
VERSION_TAG="config_$(date +%Y%m%d_%H%M%S)"

# Kritische Config-Dateien
CRITICAL_CONFIGS=(
    "system_baseline.yaml"
    "entitlements.json"
    ".env.production"
    ".env.staging"
    "docker-compose.yml"
    "pyproject.toml"
)

# ============================================================================
# INITIALIZATION
# ============================================================================

init_backup_dirs() {
    log_info "Initialisiere Backup-Verzeichnisse"
    mkdir -p "$BACKUPS_DIR"
    mkdir -p "$SNAPSHOTS_DIR"
    mkdir -p "$TEMPLATES_DIR"
    log_success "Verzeichnisse erstellt"
}

check_git_status() {
    log_section "Git-Status Prüfung"

    cd "$REPO_ROOT"

    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Git-Repository nicht gefunden"
        return 1
    fi

    local status=$(git status --porcelain)

    if [[ -n "$status" ]]; then
        log_warning "Lokale Änderungen vorhanden:"
        echo "$status" | head -10
    else
        log_success "Git working tree ist sauber"
    fi

    return 0
}

# ============================================================================
# CONFIG SNAPSHOT
# ============================================================================

create_snapshot() {
    log_section "Erstelle Config-Snapshot"

    local snapshot_dir="${SNAPSHOTS_DIR}/snapshot_${DATEONLY}"
    mkdir -p "$snapshot_dir"

    log_info "Snapshot-Verzeichnis: $snapshot_dir"

    # 1. Kopiere kritische Configs
    log_info "Kopiere kritische Config-Dateien..."

    for config in "${CRITICAL_CONFIGS[@]}"; do
        if [[ -f "${REPO_ROOT}/${config}" ]]; then
            cp "${REPO_ROOT}/${config}" "$snapshot_dir/"
            log_success "  ✓ $config"
        else
            log_warning "  ✗ $config (nicht vorhanden)"
        fi
    done

    # 2. Kopiere Agent-Configs
    log_info "Kopiere Agent-Konfigurationen..."

    for agent_dir in "${REPO_ROOT}"/*opena*/; do
        if [[ -d "${agent_dir}config" ]]; then
            agent_name=$(basename "$agent_dir")
            mkdir -p "$snapshot_dir/$agent_name"
            cp -r "${agent_dir}config" "$snapshot_dir/$agent_name/" 2>/dev/null || true
            log_success "  ✓ $agent_name/config"
        fi
    done

    # 3. Erstelle Snapshot-Manifest
    log_info "Erstelle Manifest..."

    cat > "$snapshot_dir/MANIFEST.json" << EOF
{
  "type": "config_snapshot",
  "timestamp": "$TIMESTAMP",
  "version_tag": "$VERSION_TAG",
  "repo_root": "$REPO_ROOT",
  "critical_files": $(printf '%s\n' "${CRITICAL_CONFIGS[@]}" | jq -Rs 'split("\n")[:-1]'),
  "file_count": $(find "$snapshot_dir" -type f ! -name "MANIFEST.json" | wc -l),
  "total_size": "$(du -sh "$snapshot_dir" | awk '{print $1}')",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "checksum": {
    "algorithm": "sha256",
    "date_created": "$TIMESTAMP"
  }
}
EOF

    log_success "Snapshot erstellt: $snapshot_dir"
    log_success "Manifest: $snapshot_dir/MANIFEST.json"

    # 4. Erstelle Checksummen
    log_info "Erstelle SHA256-Checksummen..."

    cd "$snapshot_dir"
    find . -type f ! -name "*.sha256" ! -name "MANIFEST.json" \
        -exec sha256sum {} \; > CHECKSUMS.sha256

    log_success "Checksummen erstellt: CHECKSUMS.sha256"

    echo "$snapshot_dir"
}

# ============================================================================
# GIT COMMIT & VERSIONING
# ============================================================================

commit_configs() {
    local snapshot_path=${1:-}

    log_section "Config-Versioning via Git"

    cd "$REPO_ROOT"

    if ! check_git_status; then
        return 1
    fi

    # Prüfe ob überhaupt Änderungen vorhanden sind
    if ! git status --porcelain | grep -qE "(config|\.env|baseline|entitlements)"; then
        log_warning "Keine Config-Änderungen seit letztem Commit"
        return 0
    fi

    # Sammle Config-Dateien
    log_info "Sammle Config-Dateien für Commit..."

    local files_to_add=()

    for config in "${CRITICAL_CONFIGS[@]}"; do
        if git diff --quiet "$config" 2>/dev/null; then
            :
        else
            files_to_add+=("$config")
            log_info "  • $config"
        fi
    done

    # Agent-Configs
    for agent_dir in *opena*/; do
        if [[ -d "${agent_dir}config" ]]; then
            if ! git diff --quiet "${agent_dir}config" 2>/dev/null; then
                files_to_add+=("${agent_dir}config")
                log_info "  • ${agent_dir}config"
            fi
        fi
    done

    if [[ ${#files_to_add[@]} -eq 0 ]]; then
        log_warning "Keine Änderungen zum Commit"
        return 0
    fi

    # Git Add
    log_info "Staging files..."
    git add "${files_to_add[@]}" || {
        log_error "Git add fehlgeschlagen"
        return 1
    }

    # Git Commit
    local commit_msg="chore(config): snapshot from $DATEONLY - $(echo "${files_to_add[@]}" | tr ' ' ',' | head -c 50)..."

    log_info "Committe mit Nachricht:"
    echo "  $commit_msg"

    git commit -m "$commit_msg" || {
        log_error "Git commit fehlgeschlagen"
        git reset HEAD "${files_to_add[@]}"
        return 1
    }

    # Git Tag
    git tag -a "$VERSION_TAG" -m "Config snapshot: $commit_msg" || true

    log_success "Config-Commit abgeschlossen"
    log_success "  Tag: $VERSION_TAG"
    log_success "  Commit: $(git rev-parse --short HEAD)"

    return 0
}

# ============================================================================
# VERIFICATION & INTEGRITY
# ============================================================================

verify_snapshots() {
    log_section "Snapshot-Integrität verifyifizieren"

    if [[ ! -d "$SNAPSHOTS_DIR" ]]; then
        log_error "Snapshots-Verzeichnis nicht gefunden"
        return 1
    fi

    local total=0
    local valid=0
    local invalid=0

    for snapshot_dir in "$SNAPSHOTS_DIR"/snapshot_*/; do
        if [[ ! -d "$snapshot_dir" ]]; then
            continue
        fi

        ((total++))
        local snapshot_name=$(basename "$snapshot_dir")
        local checksum_file="${snapshot_dir}CHECKSUMS.sha256"

        if [[ -f "$checksum_file" ]]; then
            cd "$snapshot_dir"
            if sha256sum -c "$checksum_file" > /dev/null 2>&1; then
                log_success "✅ $snapshot_name"
                ((valid++))
            else
                log_error "❌ $snapshot_name - Checksumme FEHLGESCHLAGEN"
                ((invalid++))
            fi
        else
            log_warning "⚠️  $snapshot_name - Keine Checksumme"
        fi
    done

    echo ""
    log_section "Snapshot-Verifizierungs-Zusammenfassung"
    echo "  Gesamt:   $total"
    echo "  Gültig:   $valid"
    echo "  Ungültig: $invalid"

    if [[ $invalid -eq 0 ]] && [[ $valid -gt 0 ]]; then
        log_success "Alle Snapshots sind intakt ✅"
        return 0
    else
        log_error "Einige Snapshots sind beschädigt ❌"
        return 1
    fi
}

# ============================================================================
# RESTORE FROM SNAPSHOT OR TAG
# ============================================================================

restore_config() {
    local restore_source=${1:-}

    if [[ -z "$restore_source" ]]; then
        log_error "Geben Sie Snapshot oder Git-Tag an"
        return 1
    fi

    log_section "Config Restore: $restore_source"
    log_warning "⚠️  Aktuelle Configs werden überschrieben!"

    # Bestätigung
    read -p "Wirklich fortfahren? (ja/nein): " confirm
    if [[ "$confirm" != "ja" ]]; then
        log_info "Restore abgebrochen"
        return 0
    fi

    cd "$REPO_ROOT"

    # Prüfe ob Snapshot oder Git-Tag
    if [[ -d "${SNAPSHOTS_DIR}/${restore_source}" ]]; then
        log_info "Restore von Snapshot: $restore_source"

        local snapshot_path="${SNAPSHOTS_DIR}/${restore_source}"

        # Kopiere Config-Dateien
        cp "$snapshot_path"/* "$REPO_ROOT/" 2>/dev/null || true

        # Kopiere Agent-Configs
        for agent_dir in "$snapshot_path"/*/; do
            if [[ -d "$agent_dir" ]]; then
                cp -r "$agent_dir" "$REPO_ROOT/" 2>/dev/null || true
            fi
        done

        log_success "Restore von Snapshot abgeschlossen"
    else
        log_info "Restore von Git-Tag: $restore_source"

        git checkout "$restore_source" -- . 2>/dev/null || {
            log_error "Git checkout fehlgeschlagen"
            return 1
        }

        log_success "Restore von Tag abgeschlossen"
    fi

    log_warning "Bitte starten Sie Services neu: docker-compose restart"
}

# ============================================================================
# SUMMARY & REPORTING
# ============================================================================

backup_summary() {
    log_section "Config-Backup Zusammenfassung"

    local snapshot_count=$(find "$SNAPSHOTS_DIR" -maxdepth 1 -type d -name "snapshot_*" | wc -l)
    local total_size=$(du -sh "$BACKUPS_DIR" 2>/dev/null | awk '{print $1}')

    cat << EOF

📊 Config-Backup Statistik
──────────────────────────────────────────
  Snapshots:        $snapshot_count
  Speicher:         $TOTAL_SIZE
  Speicherort:      $BACKUPS_DIR
  Methode:          Git + File Snapshots

📋 Letzte Snapshots
──────────────────────────────────────────
EOF

    find "$SNAPSHOTS_DIR" -maxdepth 1 -type d -name "snapshot_*" | sort | tail -5 | while read -r dir; do
        local name=$(basename "$dir")
        local size=$(du -sh "$dir" | awk '{print $1}')
        echo "  • $name ($size)"
    done

    echo ""

    # Git-Tags für Configs
    log_info "Config-Version Tags (Git):"
    cd "$REPO_ROOT"
    git tag -l "config_*" | sort | tail -5 | while read -r tag; do
        echo "  • $tag"
    done

    echo ""
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    local action=${1:-}

    echo ""
    log_section "CONFIG VERSIONING & BACKUP SYSTEM"

    case "$action" in
        --snapshot)
            init_backup_dirs
            local snapshot_path=$(create_snapshot)
            backup_summary
            ;;
        --commit)
            init_backup_dirs
            check_git_status
            local snapshot_path=$(create_snapshot)
            commit_configs "$snapshot_path"
            backup_summary
            ;;
        --verify)
            init_backup_dirs
            verify_snapshots
            ;;
        --restore)
            init_backup_dirs
            restore_config "${2:-}"
            ;;
        --list)
            log_section "Verfügbare Config-Snapshots"
            find "$SNAPSHOTS_DIR" -maxdepth 1 -type d -name "snapshot_*" | sort | tail -10 | while read -r dir; do
                local name=$(basename "$dir")
                local size=$(du -sh "$dir" | awk '{print $1}')
                echo "  • $name ($size)"
            done
            ;;
        *)
            cat << 'USAGE'

Nutzung:
  bash scripts/backup_configs.sh --snapshot    # Snapshot erstellen
  bash scripts/backup_configs.sh --commit      # Snapshot + Git Commit
  bash scripts/backup_configs.sh --verify      # Integrität prüfen
  bash scripts/backup_configs.sh --restore SRC # Restore von Snapshot/Tag
  bash scripts/backup_configs.sh --list        # Snapshots auflisten

USAGE
            exit 1
            ;;
    esac
}

main "$@"
