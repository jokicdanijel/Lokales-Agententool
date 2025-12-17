#!/usr/bin/env bash
set -euo pipefail

# Telegram Multi-Bot Registration Script

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env"
API_URL="${1:-http://127.0.0.1:8000}"

echo "=========================================="
echo "Telegram Multi-Bot Registration"
echo "=========================================="
echo "API URL: $API_URL"
echo ""

# Load .env
if [ -f "$ENV_FILE" ]; then
    echo "📄 Loading .env..."
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
        value="${value%\"}"
        value="${value#\"}"
        export "$key"="$value"
    done < "$ENV_FILE"
    echo "✅ .env loaded"
fi

# Check required vars
[ -z "${ADMIN_KEY:-}" ] && echo "❌ ADMIN_KEY missing" && exit 1
[ -z "${BOT_TOKENS_MAPPING:-}" ] && echo "❌ BOT_TOKENS_MAPPING missing" && exit 1

echo ""
echo "📦 Parsing BOT_TOKENS_MAPPING..."
MAPPING="$BOT_TOKENS_MAPPING"

# If it looks like JSON, try jq
if echo "$MAPPING" | grep -q "{"; then
    if command -v jq &> /dev/null; then
        PARSED=$(echo "$MAPPING" | jq -r 'to_entries[] | "\(.key)=\(.value)"' 2>/dev/null || echo "")
    else
        # Manual JSON parsing
        PARSED=$(echo "$MAPPING" | sed 's/[{}"]//g; s/, /\n/g; s/: /=/g')
    fi
else
    # Simple key:value format
    PARSED="$MAPPING"
fi

echo "$PARSED" | head -3
echo ""

echo "🔐 Registering bots..."
while IFS='=' read -r bot_key token; do
    [ -z "$bot_key" ] && continue
    
    echo ""
    echo "  📌 $bot_key"
    
    # URL-encode
    BOT_KEY_ENC=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$bot_key'))" 2>/dev/null || echo "$bot_key")
    TOKEN_ENC=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$token'))" 2>/dev/null || echo "$token")
    
    RESP=$(curl -s -X POST "$API_URL/admin/register-bot?bot_key=$BOT_KEY_ENC&token=$TOKEN_ENC" -H "X-Admin-Key: $ADMIN_KEY" 2>/dev/null || echo '{}')
    
    if echo "$RESP" | grep -q '"bot_id"'; then
        echo "    ✅ Registered"
    else
        echo "    Response: $(echo "$RESP" | head -c 100)"
    fi
done <<< "$PARSED"

echo ""
echo "📍 Setting webhooks..."
WH_URL="${WEBHOOK_BASE_URL:-$API_URL}"
WH_URL_ENC=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$WH_URL'))" 2>/dev/null || echo "$WH_URL")

RESP=$(curl -s -X POST "$API_URL/admin/set-webhooks?webhook_base_url=$WH_URL_ENC" -H "X-Admin-Key: $ADMIN_KEY" 2>/dev/null || echo '{}')

echo "Response: $(echo "$RESP" | head -c 100)"
echo ""
echo "=========================================="
echo "✅ Done"
echo "=========================================="
