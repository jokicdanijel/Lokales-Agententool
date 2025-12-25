#!/bin/bash
# Install hdctl bash completion
# Usage: bash scripts/install_completion.sh [--system|--user|--help]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPLETION_FILE="$PROJECT_ROOT/contrib/completion/hdctl.bash"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default installation mode
INSTALL_MODE="user"

# Parse arguments
case "${1:-}" in
    --system)
        INSTALL_MODE="system"
        ;;
    --user)
        INSTALL_MODE="user"
        ;;
    --help|-h)
        cat << 'EOF'
hdctl bash completion installer

Usage: bash scripts/install_completion.sh [OPTION]

Options:
    --user       Install for current user only (default)
                 Installs to ~/.bash_completion.d/hdctl

    --system     Install system-wide (requires sudo)
                 Installs to /etc/bash_completion.d/hdctl

    --help       Show this help message

Environment Variables:
    HDCTL_TOKEN     Bearer token for API (default: 250886)
    HDCTL_API       API base URL (default: http://127.0.0.1:12399)

Examples:
    # Install for current user
    bash scripts/install_completion.sh --user

    # Install system-wide
    sudo bash scripts/install_completion.sh --system

    # Use custom API endpoint
    HDCTL_API=http://api.example.com bash scripts/install_completion.sh

After Installation:
    1. Start a new terminal session OR
    2. Source bash completion:
       source ~/.bash_completion.d/hdctl

    3. Test completion:
       hdctl <TAB><TAB>
EOF
        exit 0
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

# Check if completion file exists
if [[ ! -f "$COMPLETION_FILE" ]]; then
    echo -e "${RED}✗ Error: Completion file not found at $COMPLETION_FILE${NC}"
    exit 1
fi

# Installation function
install_for_user() {
    local target_dir="$HOME/.bash_completion.d"
    local target_file="$target_dir/hdctl"

    echo -e "${BLUE}Installing completion for current user...${NC}"
    echo -e "  Source: $COMPLETION_FILE"
    echo -e "  Target: $target_file"

    # Create directory if it doesn't exist
    mkdir -p "$target_dir"

    # Copy completion file
    cp "$COMPLETION_FILE" "$target_file"
    chmod 644 "$target_file"

    echo -e "${GREEN}✓ Installed successfully${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Start a new terminal session, OR"
    echo "  2. Source completion in current session:"
    echo "     source ~/.bash_completion.d/hdctl"
    echo ""
    echo -e "${YELLOW}Test completion:${NC}"
    echo "  hdctl <TAB><TAB>"
}

install_system_wide() {
    local target_file="/etc/bash_completion.d/hdctl"

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}✗ System-wide installation requires sudo${NC}"
        echo ""
        echo "Run with sudo:"
        echo "  sudo bash scripts/install_completion.sh --system"
        exit 1
    fi

    echo -e "${BLUE}Installing completion system-wide...${NC}"
    echo -e "  Source: $COMPLETION_FILE"
    echo -e "  Target: $target_file"

    # Create directory if needed
    mkdir -p "$(dirname "$target_file")"

    # Copy completion file
    cp "$COMPLETION_FILE" "$target_file"
    chmod 644 "$target_file"

    echo -e "${GREEN}✓ Installed system-wide${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Start a new terminal session"
    echo ""
    echo -e "${YELLOW}Test completion:${NC}"
    echo "  hdctl <TAB><TAB>"
}

# Uninstall function
uninstall() {
    local user_file="$HOME/.bash_completion.d/hdctl"
    local system_file="/etc/bash_completion.d/hdctl"

    local removed=0

    if [[ -f "$user_file" ]]; then
        rm "$user_file"
        echo -e "${GREEN}✓ Removed user completion: $user_file${NC}"
        removed=1
    fi

    if [[ -f "$system_file" ]]; then
        if [[ $EUID -ne 0 ]]; then
            echo -e "${YELLOW}⚠ System completion requires sudo to remove${NC}"
            echo "  sudo rm $system_file"
        else
            rm "$system_file"
            echo -e "${GREEN}✓ Removed system completion: $system_file${NC}"
            removed=1
        fi
    fi

    if [[ $removed -eq 0 ]]; then
        echo -e "${YELLOW}No existing installation found${NC}"
    fi
}

# Verify installation
verify_installation() {
    echo -e "${BLUE}Verifying installation...${NC}"

    if [[ -f "$HOME/.bash_completion.d/hdctl" ]]; then
        echo -e "${GREEN}✓ User completion found${NC}"
        return 0
    fi

    if [[ -f "/etc/bash_completion.d/hdctl" ]]; then
        echo -e "${GREEN}✓ System completion found${NC}"
        return 0
    fi

    echo -e "${YELLOW}⚠ No installation found${NC}"
    return 1
}

# Main execution
case $INSTALL_MODE in
    user)
        install_for_user
        ;;
    system)
        install_system_wide
        ;;
esac

echo ""
echo -e "${BLUE}Environment Variables${NC} (optional for dynamic completion):"
echo "  export HDCTL_TOKEN=your_token"
echo "  export HDCTL_API=http://api.example.com"
echo ""
echo -e "${YELLOW}Additional commands:${NC}"
echo "  # Verify installation:"
echo "  bash scripts/install_completion.sh verify"
echo ""
echo "  # Uninstall:"
echo "  bash scripts/install_completion.sh uninstall"
