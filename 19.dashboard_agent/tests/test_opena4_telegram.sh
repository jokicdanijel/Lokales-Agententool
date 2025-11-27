#!/usr/bin/env bash
# Test opena4_telegram REST API
# Usage: bash test_opena4_telegram.sh

set -euo pipefail

BASE_URL="http://127.0.0.1:12348"
SECRET="webhook_secret_16plus_chars_min"
TOKEN=$(head -1 .env | cut -d= -f2 2>/dev/null || echo "MEIN_SUPER_TOKEN_123")

echo "🧪 Testing opena4_telegram API..."
echo ""

# 1. Health Check
echo "1️⃣  Health Check..."
curl -s "$BASE_URL/health" | jq .
echo ""

# 2. Config
echo "2️⃣  Configuration..."
curl -s "$BASE_URL/config" | jq .
echo ""

# 3. Webhook - /help Command
echo "3️⃣  Webhook Test - /help Command..."
curl -s -X POST "$BASE_URL/webhook/telegram" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "chat": {"id": 123456789},
      "from": {"id": 987654321},
      "text": "/help"
    }
  }' | jq .
echo ""

# 4. Webhook - /balance Command
echo "4️⃣  Webhook Test - /balance Command..."
curl -s -X POST "$BASE_URL/webhook/telegram" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "chat": {"id": 123456789},
      "from": {"id": 987654321},
      "text": "/balance"
    }
  }' | jq .
echo ""

# 5. Webhook - /accounts Command
echo "5️⃣  Webhook Test - /accounts Command..."
curl -s -X POST "$BASE_URL/webhook/telegram" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "chat": {"id": 123456789},
      "from": {"id": 987654321},
      "text": "/accounts"
    }
  }' | jq .
echo ""

# 6. Webhook - Invalid Secret (should fail)
echo "6️⃣  Webhook Test - Invalid Secret (should fail)..."
curl -s -X POST "$BASE_URL/webhook/telegram" \
  -H "X-Telegram-Bot-Api-Secret-Token: wrong_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "chat": {"id": 123456789},
      "from": {"id": 987654321},
      "text": "/balance"
    }
  }' || echo "✅ Correctly rejected"
echo ""

# 7. Recent Messages from Archive
echo "7️⃣  Recent Messages (from Archive)..."
curl -s "$BASE_URL/messages/recent?limit=5&token=$TOKEN" | jq .
echo ""

# 8. Send Message (programmatic)
echo "8️⃣  Send Message (programmatic)..."
curl -s -X POST "$BASE_URL/message/send" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": 123456789, \"text\": \"Test from API\", \"token\": \"$TOKEN\"}" | jq .
echo ""

echo "✅ All tests completed!"
