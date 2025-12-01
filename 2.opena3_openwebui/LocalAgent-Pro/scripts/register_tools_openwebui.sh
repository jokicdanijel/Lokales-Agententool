#!/usr/bin/env bash
# OpenWebUI Tool Registration Script
# Registers all LocalAgentPro tools with OpenWebUI API
# Usage: ./register_tools_openwebui.sh [base_url] [auth_token]

set -e

# Configuration
BASE_URL="${1:-http://localhost:3000/api/v1}"
TOKEN="${2:-sk-localagent-pro-default}"
TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../openwebui_tools" && pwd)"
LOG_FILE="$(dirname "$0")/tools_registration.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Verify configuration
log "🔗 OpenWebUI Tool Registration"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Base URL: $BASE_URL"
log "Auth Token: ${TOKEN:0:10}..."
log "Tools Directory: $TOOLS_DIR"
echo ""

# Check if tools directory exists
if [ ! -d "$TOOLS_DIR" ]; then
    error "Tools directory not found: $TOOLS_DIR"
    exit 1
fi

# Test API connection
log "Testing API connection..."
if ! curl -s -f -X GET "$BASE_URL/health" -H "Authorization: Bearer $TOKEN" > /dev/null 2>&1; then
    error "Cannot connect to OpenWebUI API at $BASE_URL"
    error "Make sure OpenWebUI is running and token is valid"
    exit 1
fi
success "API connection successful"
echo ""

# Register each tool
register_tool() {
    local tool_file="$1"
    local tool_name=$(basename "$tool_file" .json)

    if [ ! -f "$tool_file" ]; then
        error "Tool file not found: $tool_file"
        return 1
    fi

    log "Registering tool: $tool_name..."

    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/tools" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d @"$tool_file")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        success "Tool registered: $tool_name (HTTP $http_code)"
        return 0
    else
        error "Failed to register $tool_name (HTTP $http_code)"
        echo "Response: $body" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Register all tools
registration_failed=0

for tool_file in "$TOOLS_DIR"/*.json; do
    if [ -f "$tool_file" ]; then
        if ! register_tool "$tool_file"; then
            registration_failed=$((registration_failed + 1))
        fi
    fi
done

echo ""
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $registration_failed -eq 0 ]; then
    success "✅ All tools registered successfully!"
    log "You can now use these tools in OpenWebUI:"
    log "  • @vscode_copilot_bridge"
    log "  • @browser_agent"
    log "  • @dispatcher_controller"
    exit 0
else
    error "❌ $registration_failed tool(s) failed to register"
    error "Check $LOG_FILE for details"
    exit 1
fi
