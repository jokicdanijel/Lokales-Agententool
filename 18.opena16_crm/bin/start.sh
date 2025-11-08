#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$AGENT_DIR")")"

if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

if [ -f "$AGENT_DIR/.env" ]; then
    set -a
    source "$AGENT_DIR/.env"
    set +a
fi

AGENT_ID="${AGENT_ID:=opena16}"
PORT="${PORT:=12364}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

echo "🚀 Starting ${AGENT_ID} on port ${PORT}..."
cd "$AGENT_DIR"
exec python main.py
