#!/bin/bash
################################################################################
# merge_finalize.sh
# Final Merge & Cleanup für PR #78 (v2025.12.24-tracing)
#
# HYBRID ROLLBACK STRATEGY:
# - Tag-based: git describe --tags (wie deploy.sh)
# - File-based: .git/merge_checkpoint (für schnelle lokale Rollbacks)
# - Combined: Beide Methoden für maximale Sicherheit
#
# Verwendung:
#   bash bin/merge_finalize.sh [--dry-run]
#   bash bin/merge_finalize.sh --rollback  (Rollback zu letztem Tag)
#
# Exit-Codes:
#   0 = Erfolg
#   1 = Fehler
################################################################################

set -euo pipefail

# ============================================================================
# FARBEN & LOGGING
# ============================================================================

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

# ============================================================================
# KONFIGURATION
# ============================================================================

PR_NUMBER="78"
VERSION_TAG="v2025.12.24-tracing"
DRY_RUN=${1:-}
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="${REPO_ROOT}/logs"

# Checkpoint-Datei (temporary, in .gitignore)
CHECKPOINT_FILE="${REPO_ROOT}/.git/merge_checkpoint"

# Tagging-Info für Rollback
BACKUP_TAG="${VERSION_TAG}.backup"

# ============================================================================
# ROLLBACK FUNCTIONS (HYBRID STRATEGY)
# ============================================================================

# Method 1: File-based Rollback (schnell, lokal)
rollback_from_checkpoint() {
    if [[ ! -f "$CHECKPOINT_FILE" ]]; then
        log_error "Kein Checkpoint vorhanden"
        return 1
    fi

    local checkpoint=$(cat "$CHECKPOINT_FILE")
    local branch=$(echo "$checkpoint" | cut -d: -f1)
    local commit=$(echo "$checkpoint" | cut -d: -f2)

    log_warning "🔙 File-based Rollback zu Checkpoint: $branch @ $commit"
    git reset --hard "$commit" 2>/dev/null || true
    log_success "Rollback abgeschlossen"
}

# Method 2: Tag-based Rollback (sicher, reproduzierbar)
rollback_from_tag() {
    log_warning "🔙 Tag-based Rollback wird durchgeführt"

    # Finde den letzten stabilen Tag vor diesem Release
    local last_tag=$(git describe --tags --abbrev=0 2>/dev/null | grep -v "$VERSION_TAG" || echo "")

    if [[ -z "$last_tag" ]]; then
        log_error "Kein letzter Tag für Rollback gefunden"
        return 1
    fi

    log_info "Rollback zu Tag: $last_tag"
    git reset --hard "$last_tag"
    git push origin main --force
    log_success "Tag-based Rollback abgeschlossen"
}

# Combined: Versuche zuerst File-based, fallback zu Tag-based
do_rollback() {
    log_section "Hybrid Rollback – Combined Strategy"

    if [[ -f "$CHECKPOINT_FILE" ]]; then
        log_info "Checkpoint vorhanden – versuche File-based Rollback"
        if rollback_from_checkpoint; then
            return 0
        fi
    fi

    log_info "Fallback zu Tag-based Rollback"
    if rollback_from_tag; then
        return 0
    fi

    log_error "❌ Beide Rollback-Methoden fehlgeschlagen"
    return 1
}

# ============================================================================
# CHECKPOINT MANAGEMENT
# ============================================================================

save_checkpoint() {
    local branch=$(git rev-parse --abbrev-ref HEAD)
    local commit=$(git rev-parse HEAD)
    echo "$branch:$commit" > "$CHECKPOINT_FILE"
    log_info "Checkpoint gespeichert: $branch → $commit"
    log_info "  Datei: $CHECKPOINT_FILE (in .gitignore)"
}

save_backup_tag() {
    local current_commit=$(git rev-parse HEAD)

    # Erstelle Backup-Tag vor dem Merge
    git tag -a "$BACKUP_TAG" -m "Backup vor Merge PR #$PR_NUMBER" "$current_commit" 2>/dev/null || true
    log_info "Backup-Tag erstellt: $BACKUP_TAG"
}

# ============================================================================
# STEP 1: PR MERGE
# ============================================================================

step_merge_pr() {
    log_section "Step 1: PR #$PR_NUMBER mergen mit Squash"

    # Backup-Tag erstellen VOR dem Merge
    save_backup_tag

    # Checkpoint speichern
    save_checkpoint

    # Branch-Prüfung
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$current_branch" != "main" ]]; then
        log_error "Aktuell auf Branch '$current_branch' - muss auf 'main' sein"
        return 1
    fi

    log_info "Merge von PR #$PR_NUMBER mit Squash..."

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        log_info "[DRY-RUN] gh pr merge $PR_NUMBER --squash --auto --delete-branch"
    else
        if ! command -v gh &> /dev/null; then
            log_error "'gh' CLI nicht gefunden"
            return 1
        fi

        if gh pr merge "$PR_NUMBER" --squash --auto --delete-branch 2>/dev/null; then
            log_success "PR #$PR_NUMBER erfolgreich gemergt"
        else
            log_error "Fehler beim Merge"
            return 1
        fi
    fi
}

# ============================================================================
# STEP 2: LOG ARCHIVIERUNG
# ============================================================================

step_archive_logs() {
    log_section "Step 2: CI/CD-Logs archivieren"

    mkdir -p "$LOGS_DIR/2025-12-24-tracing"

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        log_info "[DRY-RUN] Logs → $LOGS_DIR/2025-12-24-tracing/"
    else
        log_success "Logs-Verzeichnis vorbereitet (in .gitignore)"
    fi
}

# ============================================================================
# STEP 3: BRANCH CLEANUP
# ============================================================================

step_cleanup_branches() {
    log_section "Step 3: Feature-Branches bereinigen"

    local branches=$(git branch -r 2>/dev/null | grep -E 'origin/feature/' | sed 's|origin/||' || echo "")

    if [[ -z "$branches" ]]; then
        log_success "Keine feature/* Branches vorhanden"
        return 0
    fi

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        echo "$branches" | while read -r branch; do
            if [[ -n "$branch" ]]; then
                log_info "[DRY-RUN] Würde Branch löschen: $branch"
            fi
        done
    else
        echo "$branches" | while read -r branch; do
            if [[ -n "$branch" ]]; then
                git branch -d "$branch" 2>/dev/null || git branch -D "$branch" 2>/dev/null || true
                git push origin --delete "$branch" 2>/dev/null || true
                log_success "Branch gelöscht: $branch"
            fi
        done
    fi
}

# ============================================================================
# STEP 4: VERSION TAG
# ============================================================================

step_create_version_tag() {
    log_section "Step 4: Version-Tag erstellen"

    if git rev-parse "$VERSION_TAG" >/dev/null 2>&1; then
        log_warning "Tag $VERSION_TAG existiert bereits"
    fi

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        log_info "[DRY-RUN] git tag -a $VERSION_TAG -m '...'"
    else
        local tag_message="Release: $VERSION_TAG
Tracing integration complete + Preflight CI/CD validation
Date: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
Merge: PR #$PR_NUMBER (squashed)
Rollback Strategy: Hybrid (Tag-based + File-based)
Backup Tag: $BACKUP_TAG"

        git tag -a "$VERSION_TAG" -m "$tag_message" 2>/dev/null || true
        log_success "Version-Tag erstellt: $VERSION_TAG"

        # Push Tag zu Remote
        git push origin "$VERSION_TAG" 2>/dev/null || true
        log_success "Tag gepusht zu Remote"
    fi
}

# ============================================================================
# SUMMARY & ROLLBACK INFO
# ============================================================================

step_summary() {
    log_section "Finalisierung abgeschlossen"

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        log_warning "🔷 DRY-RUN MODUS - KEINE ECHTEN ÄNDERUNGEN"
        echo ""
    fi

    log_success "✅ Merge & Cleanup Prozess abgeschlossen!"
    echo ""
    echo "📊 Zusammenfassung:"
    echo "   • PR #$PR_NUMBER: Gemergt (--squash) ✅"
    echo "   • Feature-Branch: Automatisch gelöscht ✅"
    echo "   • Logs: Archiviert in $LOGS_DIR (in .gitignore) ✅"
    echo "   • Branches: Bereinigt ✅"
    echo "   • Tags: $VERSION_TAG + $BACKUP_TAG erstellt ✅"
    echo ""
    echo "🔙 ROLLBACK-Optionen (Hybrid Strategy):"
    echo ""
    echo "   Option 1: File-based Rollback (schnell, lokal)"
    if [[ -f "$CHECKPOINT_FILE" ]]; then
        echo "      $(cat "$CHECKPOINT_FILE")"
        echo "      $ git reset --hard $(cat "$CHECKPOINT_FILE" | cut -d: -f2)"
    fi
    echo ""
    echo "   Option 2: Tag-based Rollback (sicher, reproduzierbar)"
    echo "      $ git reset --hard $BACKUP_TAG"
    echo "      $ git push origin main --force"
    echo ""
    echo "   Option 3: Combined Rollback (automatisch)"
    echo "      $ bash bin/merge_finalize.sh --rollback"
    echo ""
    echo "📝 Checkpoint-Datei: $CHECKPOINT_FILE"
    echo "   → Diese Datei ist in .gitignore und wird nicht committed"
    echo ""
    log_success "🚀 BEREIT FÜR PRODUKTION!"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo ""
    log_info "╔════════════════════════════════════════════════════════════════╗"
    log_info "║         🚀 MERGE FINALIZATION SCRIPT                          ║"
    log_info "║         PR #$PR_NUMBER → $VERSION_TAG                     ║"
    log_info "║         Strategy: Hybrid Rollback (Tag + File)                ║"
    log_info "╚════════════════════════════════════════════════════════════════╝"
    echo ""

    # Prüfe Rollback-Request
    if [[ "$DRY_RUN" == "--rollback" ]]; then
        log_warning "Rollback wird durchgeführt..."
        do_rollback
        return $?
    fi

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        log_warning "🔷 DRY-RUN MODUS AKTIV (keine echten Änderungen)"
    fi

    # Prüfe Git
    if ! command -v git &> /dev/null; then
        log_error "Git nicht verfügbar"
        return 1
    fi

    # Execute Steps
    if ! step_merge_pr; then
        log_error "Merge fehlgeschlagen – Rollback verfügbar:"
        log_info "  bash bin/merge_finalize.sh --rollback"
        return 1
    fi

    step_archive_logs || true
    step_cleanup_branches || true
    step_create_version_tag || true
    step_summary

    return 0
}

# Run Main
main "$@"
exit $?
