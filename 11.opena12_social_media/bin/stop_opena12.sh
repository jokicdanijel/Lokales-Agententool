#!/bin/bash
#
# Stop opena12 (Social Media Automation Agent)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PID_FILE="$PROJECT_ROOT/logs/opena12.pid"
SERVICE_NAME="opena12"

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1" >&2
}

stop_service() {
    if [ ! -f "$PID_FILE" ]; then
        log_error "$SERVICE_NAME is not running (PID file not found)"
        exit 1
    fi

    PID=$(cat "$PID_FILE")

    if ! kill -0 "$PID" 2>/dev/null; then
        log_error "$SERVICE_NAME is not running (process $PID does not exist)"
        rm -f "$PID_FILE"
        exit 1
    fi

    log_info "Stopping $SERVICE_NAME (PID: $PID)..."

    kill -TERM "$PID"

    # Wait for graceful shutdown (max 10 seconds)
    for i in {1..10}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            log_info "✅ $SERVICE_NAME stopped gracefully"
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
    done

    # Force kill if still running
    log_info "Forcing shutdown..."
    kill -KILL "$PID" 2>/dev/null || true
    rm -f "$PID_FILE"

    log_info "✅ $SERVICE_NAME stopped (forced)"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    log_info "🛑 Stopping opena12 (smp)"
    stop_service
}

main "$@"
