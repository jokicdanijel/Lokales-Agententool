#!/bin/bash
#
# Auto-Updater Installation & Management Script
# PORTIER 3.0 Enterprise Auto-Update System
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="opena20-auto-updater"
SERVICE_USER="opena20"
INSTALL_DIR="/opt/opena20"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
        exit 1
    fi
}

install_auto_updater() {
    log "Installing opena20 Auto-Updater..."
    
    # Create service user if not exists
    if ! id "$SERVICE_USER" &>/dev/null; then
        log "Creating service user: $SERVICE_USER"
        useradd --system --no-create-home --shell /bin/false "$SERVICE_USER"
    fi
    
    # Create directories
    mkdir -p "$INSTALL_DIR"/{bin,config,logs,backups}
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    
    # Copy auto-updater script
    cp "$SCRIPT_DIR/auto_updater.py" "$INSTALL_DIR/bin/"
    chmod +x "$INSTALL_DIR/bin/auto_updater.py"
    
    # Copy configuration
    if [[ ! -f "$INSTALL_DIR/config/auto_update_config.json" ]]; then
        cp "$SCRIPT_DIR/auto_update_config.json" "$INSTALL_DIR/config/"
    fi
    
    # Create systemd service
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=opena20 Auto-Updater Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/bin/auto_updater.py --daemon --config $INSTALL_DIR/config/auto_update_config.json
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$INSTALL_DIR
CapabilityBoundingSet=CAP_NET_BIND_SERVICE

# Environment
Environment=PYTHONPATH=$INSTALL_DIR
Environment=LOG_LEVEL=INFO

[Install]
WantedBy=multi-user.target
EOF
    
    # Set permissions
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    chmod 644 "/etc/systemd/system/$SERVICE_NAME.service"
    
    # Reload systemd
    systemctl daemon-reload
    
    log "Auto-updater installed successfully"
}

start_service() {
    log "Starting $SERVICE_NAME service..."
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
    
    sleep 2
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "Service started successfully"
        systemctl status "$SERVICE_NAME" --no-pager
    else
        error "Service failed to start"
        systemctl status "$SERVICE_NAME" --no-pager
        exit 1
    fi
}

stop_service() {
    log "Stopping $SERVICE_NAME service..."
    systemctl stop "$SERVICE_NAME" || true
    systemctl disable "$SERVICE_NAME" || true
    log "Service stopped"
}

status_service() {
    echo "=== Service Status ==="
    systemctl status "$SERVICE_NAME" --no-pager || true
    
    echo -e "\n=== Recent Logs ==="
    journalctl -u "$SERVICE_NAME" --no-pager -n 20 || true
    
    echo -e "\n=== Configuration ==="
    if [[ -f "$INSTALL_DIR/config/auto_update_config.json" ]]; then
        cat "$INSTALL_DIR/config/auto_update_config.json" | jq . 2>/dev/null || cat "$INSTALL_DIR/config/auto_update_config.json"
    else
        warn "Configuration file not found"
    fi
}

logs_service() {
    log "Following $SERVICE_NAME logs (Ctrl+C to exit)..."
    journalctl -u "$SERVICE_NAME" -f
}

check_updates() {
    log "Checking for updates..."
    if [[ -f "$INSTALL_DIR/bin/auto_updater.py" ]]; then
        sudo -u "$SERVICE_USER" python3 "$INSTALL_DIR/bin/auto_updater.py" --check --config "$INSTALL_DIR/config/auto_update_config.json"
    else
        error "Auto-updater not installed"
        exit 1
    fi
}

force_update() {
    log "Forcing update..."
    if [[ -f "$INSTALL_DIR/bin/auto_updater.py" ]]; then
        sudo -u "$SERVICE_USER" python3 "$INSTALL_DIR/bin/auto_updater.py" --update --config "$INSTALL_DIR/config/auto_update_config.json"
    else
        error "Auto-updater not installed"
        exit 1
    fi
}

list_backups() {
    log "Available backups:"
    if [[ -d "$INSTALL_DIR/backups" ]]; then
        ls -la "$INSTALL_DIR/backups/" | grep "opena20_backup_" || echo "No backups found"
    else
        warn "Backup directory not found"
    fi
}

rollback() {
    local backup_name="$1"
    log "Rolling back to backup: $backup_name"
    
    if [[ -f "$INSTALL_DIR/bin/auto_updater.py" ]]; then
        sudo -u "$SERVICE_USER" python3 "$INSTALL_DIR/bin/auto_updater.py" --rollback "$backup_name" --config "$INSTALL_DIR/config/auto_update_config.json"
    else
        error "Auto-updater not installed"
        exit 1
    fi
}

configure() {
    log "Opening configuration file for editing..."
    if [[ -f "$INSTALL_DIR/config/auto_update_config.json" ]]; then
        ${EDITOR:-nano} "$INSTALL_DIR/config/auto_update_config.json"
        log "Configuration updated. Restart service to apply changes."
    else
        error "Configuration file not found"
        exit 1
    fi
}

uninstall() {
    warn "This will completely remove the auto-updater service and files"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Uninstalling auto-updater..."
        
        # Stop and disable service
        systemctl stop "$SERVICE_NAME" 2>/dev/null || true
        systemctl disable "$SERVICE_NAME" 2>/dev/null || true
        
        # Remove service file
        rm -f "/etc/systemd/system/$SERVICE_NAME.service"
        systemctl daemon-reload
        
        # Remove installation directory
        rm -rf "$INSTALL_DIR"
        
        # Remove service user
        userdel "$SERVICE_USER" 2>/dev/null || true
        
        log "Auto-updater uninstalled successfully"
    else
        log "Uninstall cancelled"
    fi
}

show_help() {
    cat << EOF
opena20 Auto-Updater Management Script

Usage: $0 [COMMAND]

Commands:
    install     Install auto-updater service
    start       Start the service
    stop        Stop the service
    restart     Restart the service
    status      Show service status
    logs        Follow service logs
    check       Check for updates
    update      Force update now
    backups     List available backups
    rollback    Rollback to specific backup
    config      Edit configuration
    uninstall   Remove auto-updater completely
    help        Show this help

Examples:
    $0 install          # Install and setup auto-updater
    $0 start            # Start the service
    $0 check            # Check for available updates
    $0 rollback backup_20251129_120000  # Rollback to specific backup
    $0 config           # Edit configuration file

EOF
}

main() {
    case "${1:-help}" in
        install)
            check_root
            install_auto_updater
            start_service
            ;;
        start)
            check_root
            start_service
            ;;
        stop)
            check_root
            stop_service
            ;;
        restart)
            check_root
            stop_service
            sleep 2
            start_service
            ;;
        status)
            status_service
            ;;
        logs)
            logs_service
            ;;
        check)
            check_updates
            ;;
        update)
            force_update
            ;;
        backups)
            list_backups
            ;;
        rollback)
            if [[ -z "${2:-}" ]]; then
                error "Please specify backup name"
                list_backups
                exit 1
            fi
            rollback "$2"
            ;;
        config)
            check_root
            configure
            ;;
        uninstall)
            check_root
            uninstall
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: ${1:-}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"