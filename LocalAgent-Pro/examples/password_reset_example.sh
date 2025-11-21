#!/usr/bin/env bash
# Example: Reset OpenWebUI password for a user
# This is a demonstration of how to use the password update utility

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}OpenWebUI Password Reset Example${NC}"
echo ""

# Check if Python and bcrypt are available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Error: Python 3 is required${NC}"
    exit 1
fi

if ! python3 -c "import bcrypt" 2>/dev/null; then
    echo -e "${YELLOW}Error: bcrypt library is not installed${NC}"
    echo "Install it with: pip install bcrypt"
    exit 1
fi

# Example 1: Generate a password hash
echo -e "${BLUE}Example 1: Generate a password hash${NC}"
echo "Command: python3 -c \"import bcrypt; print(bcrypt.hashpw(b'myNewPassword123', bcrypt.gensalt()).decode())\""
echo ""

EXAMPLE_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'myNewPassword123', bcrypt.gensalt()).decode())")
echo -e "${GREEN}Generated hash:${NC} ${EXAMPLE_HASH}"
echo ""

# Example 2: Show how to use the update script
echo -e "${BLUE}Example 2: Update password in OpenWebUI${NC}"
echo "Command:"
echo "./update_openwebui_password.sh \\"
echo "  -e jokicdanijel@gmail.com \\"
echo "  -p '${EXAMPLE_HASH}'"
echo ""

# Example 3: Using custom volume
echo -e "${BLUE}Example 3: Using a custom Docker volume${NC}"
echo "Command:"
echo "./update_openwebui_password.sh \\"
echo "  -e user@example.com \\"
echo "  -p '${EXAMPLE_HASH}' \\"
echo "  -v custom_webui_volume"
echo ""

# Example 4: Complete workflow
echo -e "${BLUE}Example 4: Complete workflow (one-liner)${NC}"
echo "Command:"
cat << 'EOF'
NEW_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'yourPassword', bcrypt.gensalt()).decode())") && \
./update_openwebui_password.sh -e user@example.com -p "$NEW_HASH"
EOF
echo ""

echo -e "${GREEN}✅ See PASSWORD_RESET.md for detailed documentation${NC}"
