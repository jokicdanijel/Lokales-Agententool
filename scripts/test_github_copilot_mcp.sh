#!/bin/bash
# Test GitHub Copilot MCP API connection
# Usage: ./scripts/test_github_copilot_mcp.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load environment
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
else
    echo "⚠️  No .env file found. Using .env.example as reference."
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        source "$PROJECT_ROOT/.env.example"
    fi
fi

# Default endpoint if not set
GITHUB_COPILOT_MCP_ENDPOINT="${GITHUB_COPILOT_MCP_ENDPOINT:-https://api.githubcopilot.com/mcp/}"

echo "============================================"
echo "🧪 GitHub Copilot MCP API Test"
echo "============================================"
echo "Endpoint: $GITHUB_COPILOT_MCP_ENDPOINT"
echo ""

# Check if API key is set
if [ -z "$GITHUB_COPILOT_API_KEY" ]; then
    echo "❌ GITHUB_COPILOT_API_KEY not set in .env"
    echo ""
    echo "Please add your GitHub Copilot API key to .env:"
    echo "  GITHUB_COPILOT_API_KEY=your-key-here"
    echo ""
    echo "To obtain an API key:"
    echo "  1. Visit: https://github.com/settings/tokens"
    echo "  2. Generate new token with 'copilot' scope"
    echo "  3. Add to .env file"
    exit 1
fi

# Mask the key for display
MASKED_KEY="${GITHUB_COPILOT_API_KEY:0:10}...${GITHUB_COPILOT_API_KEY: -4}"
echo "API Key: $MASKED_KEY"
echo ""

# Test connection
echo "🔍 Testing API connection..."
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $GITHUB_COPILOT_API_KEY" \
    -H "Accept: application/json" \
    "$GITHUB_COPILOT_MCP_ENDPOINT" 2>/dev/null || echo "000")

echo ""
echo "Response Code: $response"

if [ "$response" = "200" ]; then
    echo "✅ API connection successful"
    echo ""
    echo "Your GitHub Copilot MCP API key is valid and working."
    exit 0
elif [ "$response" = "401" ]; then
    echo "❌ Authentication failed"
    echo ""
    echo "Possible causes:"
    echo "  - Invalid API key"
    echo "  - Expired token"
    echo "  - Missing 'copilot' scope"
    echo ""
    echo "Please regenerate your API key at:"
    echo "  https://github.com/settings/tokens"
    exit 1
elif [ "$response" = "404" ]; then
    echo "⚠️  Endpoint not found"
    echo ""
    echo "The API endpoint may have changed or is incorrect."
    echo "Please check the GitHub Copilot documentation."
    exit 1
elif [ "$response" = "000" ]; then
    echo "❌ Connection failed"
    echo ""
    echo "Could not connect to the API endpoint."
    echo "Please check your internet connection."
    exit 1
else
    echo "⚠️  Received HTTP $response"
    echo ""
    echo "Unexpected response from API."
    echo "Please check the endpoint and API key."
    exit 1
fi
