#!/bin/bash
#
# opena20 Systemd Installation Script
# Für Ubuntu 25.04 - PORTIER 3.0 Enterprise Konform
#
# Features:
# - Systemd Service Installation & Configuration
# - Health Check Validation
# - Security Hardening & Permissions
# - Comprehensive Error Handling
# - Post-Installation Verification
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

log "🚀 Installing opena20 Dashboard Agent as systemd service..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "This script should not be run as root directly. Use sudo for individual commands."
    exit 1
fi

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/opena20.service"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_NAME="opena20.service"
SERVICE_USER="opena20"

# Dependency checks
check_dependencies() {
    local missing_deps=()

    # Check required commands
    for cmd in systemctl curl jq python3; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing required dependencies: ${missing_deps[*]}"
        info "Install with: sudo apt update && sudo apt install -y ${missing_deps[*]}"
        exit 1
    fi

    # Check Python version
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        error "Python 3.8+ required"
        exit 1
    fi

    log "✅ All dependencies satisfied"
}

# Pre-installation checks
pre_install_checks() {
    info "Performing pre-installation checks..."

    # Check if service file exists
    if [[ ! -f "$SERVICE_FILE" ]]; then
        error "Service file not found: $SERVICE_FILE"
        exit 1
    fi

    # Validate service file syntax
    if ! systemd-analyze verify "$SERVICE_FILE" 2>/dev/null; then
        warn "Service file validation warnings (continuing anyway)"
    fi

    # Check if user has sudo privileges
    if ! sudo -n true 2>/dev/null; then
        error "This script requires sudo privileges"
        exit 1
    fi

    # Check if ports are available
    if ss -tuln | grep -q ":12349 "; then
        warn "Port 12349 is already in use"
    fi

    log "✅ Pre-installation checks passed"
}

# Create service user if needed
create_service_user() {
    if ! id "$SERVICE_USER" &>/dev/null; then
        log "Creating service user: $SERVICE_USER"
        sudo useradd --system --no-create-home --shell /bin/false --comment "opena20 Dashboard Service" "$SERVICE_USER"
    else
        info "Service user $SERVICE_USER already exists"
    fi

    # Set up proper permissions for service directories
    sudo mkdir -p /var/log/opena20 /var/lib/opena20
    sudo chown "$SERVICE_USER:$SERVICE_USER" /var/log/opena20 /var/lib/opena20
    sudo chmod 755 /var/log/opena20 /var/lib/opena20
}

# Install service
install_service() {
    info "Installing systemd service..."

    # Stop existing service if running
    if systemctl is-active --quiet opena20 2>/dev/null; then
        log "🛑 Stopping existing opena20 service..."
        sudo systemctl stop opena20
    fi

    # Copy service file
    log "📁 Installing service file..."
    sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME"

    # Set proper permissions
    sudo chmod 644 "$SYSTEMD_DIR/$SERVICE_NAME"
    sudo chown root:root "$SYSTEMD_DIR/$SERVICE_NAME"

    # Reload systemd
    log "🔄 Reloading systemd daemon..."
    sudo systemctl daemon-reload

    # Enable service for auto-start
    log "✅ Enabling opena20 service for auto-start..."
    sudo systemctl enable opena20

    log "✅ Service installation completed"
}

# Start and verify service
start_and_verify_service() {
    info "Starting and verifying opena20 service..."

    # Start service
    log "🚀 Starting opena20 service..."
    if ! sudo systemctl start opena20; then
        error "Failed to start opena20 service"
        log "Checking service logs..."
        sudo journalctl -u opena20 --no-pager -n 20
        exit 1
    fi

    # Wait for service to become healthy
    log "⏳ Waiting for opena20 service to become healthy..."
    local max_attempts=40  # 20 seconds total
    local attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s -f http://127.0.0.1:12349/health >/dev/null 2>&1; then
            log "✅ Service is healthy after $((attempt/2)) seconds"
            break
        fi

        if [[ $attempt -eq $((max_attempts-1)) ]]; then
            error "Service failed to become healthy within 20 seconds"
            log "Service status:"
            sudo systemctl status opena20 --no-pager -l
            log "Recent logs:"
            sudo journalctl -u opena20 --no-pager -n 10
            exit 1
        fi

        sleep 0.5
        ((attempt++))
    done
}

# Comprehensive endpoint testing
test_endpoints() {
    info "🧪 Testing opena20 endpoints..."

    local base_url="http://127.0.0.1:12349"
    local bearer_token

    # Try to read bearer token from .env
    if [[ -f "$SCRIPT_DIR/.env" ]]; then
        bearer_token=$(grep "^BEARER_TOKEN=" "$SCRIPT_DIR/.env" | cut -d'=' -f2 | tr -d '"')
    fi

    # Test health endpoint
    if curl -s -f "$base_url/health" >/dev/null; then
        log "✅ Health endpoint responding"
    else
        warn "❌ Health endpoint not responding"
    fi

    # Test dashboard
    if curl -s -f "$base_url/self_cleaning_dashboard.html" >/dev/null; then
        log "✅ Dashboard HTML accessible"
    else
        warn "❌ Dashboard HTML not accessible"
    fi

    # Test API status (with token if available)
    local auth_header=""
    if [[ -n "$bearer_token" ]]; then
        auth_header="-H \"Authorization: Bearer $bearer_token\""
    fi

    if eval curl -s -f $auth_header "$base_url/api/status/all" >/dev/null; then
        log "✅ API status endpoint responding"
    else
        warn "❌ API status endpoint not responding (may need authentication)"
    fi
}

# Display service status and management info
display_service_info() {
    info "📊 Service Status:"
    sudo systemctl status opena20 --no-pager -l

    echo ""
    log "✅ opena20 Dashboard Agent is running successfully!"
    echo ""
    echo -e "${BLUE}🔗 Access URLs:${NC}"
    echo "  📡 Base URL:     http://127.0.0.1:12349"
    echo "  🏥 Health Check: http://127.0.0.1:12349/health"
    echo "  📊 Dashboard:    http://127.0.0.1:12349/self_cleaning_dashboard.html"
    echo "  📈 Metrics:      http://127.0.0.1:9090/metrics (if monitoring enabled)"

    echo ""
    echo -e "${BLUE}📋 Service Management Commands:${NC}"
    echo "  Start:    sudo systemctl start opena20"
    echo "  Stop:     sudo systemctl stop opena20"
    echo "  Restart:  sudo systemctl restart opena20"
    echo "  Status:   sudo systemctl status opena20"
    echo "  Logs:     sudo journalctl -u opena20 -f"
    echo "  Disable:  sudo systemctl disable opena20"

    echo ""
    echo -e "${BLUE}🔧 Maintenance Commands:${NC}"
    echo "  Health:   curl -s http://127.0.0.1:12349/health | jq ."
    echo "  Monitor:  python3 $SCRIPT_DIR/monitoring_dashboard.py --dashboard"
    echo "  Update:   python3 $SCRIPT_DIR/auto_updater.py --check"
    echo "  Maintain: python3 $SCRIPT_DIR/maintenance_tools.py full-maintenance"

    echo ""
    log "🎉 opena20 systemd installation complete!"

    # Show next steps
    echo ""
    echo -e "${GREEN}🚀 Next Steps:${NC}"
    echo "  1. Configure monitoring: nano $SCRIPT_DIR/monitoring_config.json"
    echo "  2. Setup auto-updater: sudo $SCRIPT_DIR/manage_auto_updater.sh install"
    echo "  3. Run E2E tests: python3 $SCRIPT_DIR/e2e_test.py"
    echo "  4. Access dashboard: http://127.0.0.1:12349/self_cleaning_dashboard.html"
}

# Cleanup function for error handling
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        error "Installation failed with exit code $exit_code"
        if systemctl is-active --quiet opena20 2>/dev/null; then
            warn "Service is running but installation had issues"
            log "Check logs: sudo journalctl -u opena20 -f"
        fi
    fi
}

# Main installation flow
main() {
    trap cleanup EXIT

    log "Starting opena20 systemd installation..."

    # Run installation steps
    check_dependencies
    pre_install_checks
    create_service_user
    install_service
    start_and_verify_service
    test_endpoints
    display_service_info

    log "Installation completed successfully!"
}

# Run main installation
main "$@"
