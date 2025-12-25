#!/bin/bash
#
# 🧹 PORTIER 3.0 Cleaner & Inspector Wrapper
# ==========================================
#
# Vereinfachte CLI-Schnittstelle für das Cleaner & Inspector System
#
# Usage:
#   ./clean_inspect.sh [inspect|clean|full|help]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLEANER_SCRIPT="$SCRIPT_DIR/cleaner_inspector.py"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "🧹 PORTIER 3.0 Cleaner & Inspector"
    echo "=================================="
    echo -e "${NC}"
}

print_help() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    inspect     Führt nur Inspektion durch
    clean       Führt nur Bereinigung durch
    full        Führt Inspektion + Bereinigung durch (default)
    help        Zeigt diese Hilfe an

OPTIONS:
    --quiet     Weniger Output
    --output    Output-Datei für Report
    --max-log-age DAYS    Max Alter für Log-Dateien (default: 7)

EXAMPLES:
    $0 inspect                    # Nur Inspektion
    $0 clean                      # Nur Bereinigung
    $0 full                       # Beides (default)
    $0 inspect --output report.txt # Inspektion mit Report-Datei
    $0 clean --max-log-age 3      # Bereinigung (Logs älter als 3 Tage)

KOMPONENTEN:
    📋 Safepoint-Client Validierung
    🔍 PORTIER 3.0 Compliance Checks
    ⚡ Performance Pattern Analysis
    📁 Archive Structure Inspection
    🧽 Python Cache Cleanup
    📝 Log File Cleanup
    🗑️  Temp File Cleanup

REPORT:
    Der Report wird standardmäßig auf der Konsole ausgegeben.
    Mit --output kann er in eine Datei geschrieben werden.

EOF
}

check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        log_error "python3 nicht gefunden"
        exit 1
    fi

    if [[ ! -f "$CLEANER_SCRIPT" ]]; then
        log_error "Cleaner-Skript nicht gefunden: $CLEANER_SCRIPT"
        exit 1
    fi

    # Python-Dependencies prüfen
    if ! python3 -c "import json, pathlib, asyncio" 2>/dev/null; then
        log_error "Python-Dependencies fehlen"
        exit 1
    fi
}

run_operation() {
    local operation="$1"
    shift
    local args=("$@")

    log_info "Starte $operation Operation..."

    # Timestamp für Report-Datei
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local default_output="cleaner_inspector_report_${timestamp}.txt"

    # Python-Skript ausführen
    if python3 "$CLEANER_SCRIPT" \
        "--${operation}" \
        --project-root "$PROJECT_ROOT" \
        "${args[@]}"; then

        log_success "$operation Operation erfolgreich abgeschlossen"

        # Report-Datei Info
        for arg in "${args[@]}"; do
            if [[ "$arg" == --output=* ]]; then
                local output_file="${arg#--output=}"
                log_info "Report gespeichert: $output_file"
                break
            fi
        done

        return 0
    else
        log_error "$operation Operation fehlgeschlagen"
        return 1
    fi
}

main() {
    print_header

    # Dependency Check
    check_dependencies

    # Default Operation
    local operation="full"
    local args=()

    # Argument Parsing
    while [[ $# -gt 0 ]]; do
        case $1 in
            inspect|clean|full)
                operation="$1"
                shift
                ;;
            help|--help|-h)
                print_help
                exit 0
                ;;
            --quiet)
                args+=("$1")
                shift
                ;;
            --output)
                if [[ -n "${2:-}" ]]; then
                    args+=("$1" "$2")
                    shift 2
                else
                    log_error "--output benötigt einen Dateinamen"
                    exit 1
                fi
                ;;
            --max-log-age)
                if [[ -n "${2:-}" && "$2" =~ ^[0-9]+$ ]]; then
                    args+=("$1" "$2")
                    shift 2
                else
                    log_error "--max-log-age benötigt eine Zahl"
                    exit 1
                fi
                ;;
            *)
                log_warning "Unbekannte Option: $1"
                shift
                ;;
        esac
    done

    # Operation ausführen
    log_info "Project Root: $PROJECT_ROOT"
    log_info "Operation: $operation"

    if run_operation "$operation" "${args[@]}"; then
        echo
        log_success "🎉 Cleaner & Inspector erfolgreich abgeschlossen!"
        echo
        echo "Nächste Schritte:"
        echo "  • Review der Inspection Results"
        echo "  • Behebung von Fehlern und Warnungen"
        echo "  • Regelmäßige Ausführung (z.B. täglich)"
        echo
    else
        echo
        log_error "❌ Cleaner & Inspector mit Fehlern beendet"
        echo
        echo "Troubleshooting:"
        echo "  • Prüfe Python-Dependencies"
        echo "  • Prüfe Dateiberechtigungen"
        echo "  • Prüfe Log-Ausgabe für Details"
        echo
        exit 1
    fi
}

# Trap für sauberes Exit
trap 'log_error "Operation abgebrochen"; exit 1' INT TERM

main "$@"
