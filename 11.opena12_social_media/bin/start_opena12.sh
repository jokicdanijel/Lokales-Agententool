#!/bin/bash
#
# Start opena12 (Social Media Automation Agent)
# Port: 12357
# Kürzel: smp
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENT_DIR="$PROJECT_ROOT/11.opena12_social_media"

PID_FILE="$PROJECT_ROOT/logs/opena12.pid"
LOG_FILE="$PROJECT_ROOT/logs/opena12.nohup.log"

PORT=12357
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

log_warn() {
    echo -e "\033[0;33m[WARN]\033[0m $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "python3 not found"
        exit 1
    fi
}

load_env() {
    # Try project root first
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_info "Loading .env from project root"
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
    elif [ -f "$AGENT_DIR/.env" ]; then
        log_info "Loading .env from agent directory"
        set -a
        source "$AGENT_DIR/.env"
        set +a
    else
        log_warn ".env file not found"
    fi
    
    if [ -z "$BEARER_TOKEN" ]; then
        log_error "BEARER_TOKEN not set in .env"
        exit 1
    fi
}

check_port() {
    log_info "Checking if port $PORT is available..."
    
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "Port $PORT is already in use"
        exit 1
    fi
    
    log_info "Port $PORT is available ✓"
}

check_existing_process() {
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            log_error "$SERVICE_NAME is already running (PID: $OLD_PID)"
            exit 1
        else
            log_warn "Removing stale PID file"
            rm -f "$PID_FILE"
        fi
    fi
}

install_dependencies() {
    log_info "Checking Python dependencies..."
    
    cd "$AGENT_DIR"
    
    # Check if dependencies are already installed
    if python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null; then
        log_info "Dependencies already installed ✓"
        return 0
    fi
    
    log_info "Installing Python dependencies..."
    
    # Use --break-system-packages (PEP 668 override)
    pip3 install --user --break-system-packages -q fastapi uvicorn pydantic 2>/dev/null || {
        log_warn "Failed to install dependencies via pip (continuing anyway)"
    }
    
    # Final check
    if python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null; then
        log_info "Dependencies verified ✓"
    else
        log_error "Required dependencies (fastapi, uvicorn, pydantic) not available"
        exit 1
    fi
}

start_service() {
    log_info "Starting $SERVICE_NAME on port $PORT..."
    
    cd "$AGENT_DIR"
    
    nohup python3 main_socialmedia_agent.py > "$LOG_FILE" 2>&1 &
    PID=$!
    
    echo "$PID" > "$PID_FILE"
    
    log_info "Started $SERVICE_NAME with PID $PID"
    log_info "Logs: $LOG_FILE"
    
    # Wait for service to start
    sleep 2
    
    # Verify process is still running
    if ! kill -0 "$PID" 2>/dev/null; then
        log_error "$SERVICE_NAME failed to start (check logs: $LOG_FILE)"
        rm -f "$PID_FILE"
        exit 1
    fi
    
    # Health check
    log_info "Performing health check..."
    if curl -s -f "http://127.0.0.1:$PORT/health" > /dev/null 2>&1; then
        log_info "✅ $SERVICE_NAME is healthy"
    else
        log_warn "Health check failed (service may still be starting)"
    fi
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    log_info "🚀 Starting opena12 (smp)"
    
    check_dependencies
    load_env
    check_port
    check_existing_process
    install_dependencies
    start_service
    
    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "✅ opena12 started successfully"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Service:  $SERVICE_NAME (smp)"
    log_info "Port:     $PORT"
    log_info "PID:      $(cat $PID_FILE)"
    log_info "Logs:     $LOG_FILE"
    log_info "Health:   http://127.0.0.1:$PORT/health"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

main "$@"
