#!/usr/bin/env bash
# Copilot Guard Shell Wrapper
# Idempotent. Führt die strikte Validierung durch, ohne Ordner zu erzeugen.
# Exit-Codes: 0=OK, 1=Missing, 2=Illegal, 3=Error

set -euo pipefail

ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
CFG="${ROOT}/configs/agent_dirs.yaml"
GUARD="${ROOT}/src/tools/copilot_guard.py"
# Fallback: Versuche venv313 in verschiedenen Pfaden
if [ -x "${ROOT}/1.opena1&2_portier/venv313/bin/python3" ]; then
    PY="${ROOT}/1.opena1&2_portier/venv313/bin/python3"
elif [ -x "${ROOT}/1.openai1&2_.portier/venv313/bin/python3" ]; then
    PY="${ROOT}/1.openai1&2_.portier/venv313/bin/python3"
elif [ -x "${ROOT}/.venv/bin/python3" ]; then
    PY="${ROOT}/.venv/bin/python3"
else
    PY="python3"
fi

# ============================================================================
# Hilfsfunktionen
# ============================================================================

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
  --mode validate           Validate all directories (default)
  --mode check_name NAME    Check if directory name is allowed
  --help, -h               Show this help message

Exit Codes:
  0 -> OK
  1 -> Fehlende Soll-Ordner
  2 -> Unerlaubte Ordner gefunden
  3 -> Konfigurations-/Laufzeitfehler

Examples:
  $0 --mode validate
  $0 --mode check_name "3.opena4_telegram"
EOF
}

ensure_python() {
    if [ ! -x "${PY}" ]; then
        echo "ERROR: Python venv313 nicht gefunden unter ${PY}" >&2
        exit 3
    fi
}

ensure_pyyaml() {
    ensure_python
    "${PY}" -m pip install --quiet PyYAML 2>/dev/null || true
}

# ============================================================================
# Main
# ============================================================================

MODE="validate"
NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --name)
            NAME="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            usage
            exit 3
            ;;
    esac
done

ensure_pyyaml

case "$MODE" in
    validate)
        "${PY}" "${GUARD}" --config "${CFG}" --mode validate
        exit $?
        ;;
    check_name)
        if [ -z "$NAME" ]; then
            echo "ERROR: --name is required for mode=check_name" >&2
            exit 3
        fi
        "${PY}" "${GUARD}" --config "${CFG}" --mode check_name --name "$NAME"
        exit $?
        ;;
    *)
        echo "ERROR: Unknown mode: $MODE" >&2
        exit 3
        ;;
esac
