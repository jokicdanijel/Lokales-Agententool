#!/usr/bin/env bash
set -euo pipefail

# Quick Start Guide for Telegram Multi-Bot Registration
# This script helps you register Telegram bots and set up webhooks

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Telegram Multi-Bot Quick Start"
echo "=========================================="
echo ""

# Check if docker-compose is running
echo "🔍 Checking services..."
if ! curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "❌ API not running on port 8000"
    echo "   Starting services..."
    cd telegram_multi
    docker-compose up -d
    cd ..
    echo "   Waiting 15 seconds for services to initialize..."
    sleep 15
fi

echo "✅ Services are running"
echo ""

# Show registration instructions
echo "📝 Registration Instructions"
echo "=========================================="
echo ""
echo "1. Update your bot tokens in .env:"
echo "   BOT_TOKENS_MAPPING={\"your_bot_key\": \"YOUR_BOT_TOKEN\", ...}"
echo ""
echo "2. Run the registration script:"
echo "   bash scripts/register_bots.sh http://127.0.0.1:8000"
echo ""
echo "3. For production with public domain:"
echo "   bash scripts/register_bots.sh https://api.your-domain.com"
echo ""
echo "=========================================="
echo ""

# Show status
echo "📊 Current Status"
echo "=========================================="
curl -s http://127.0.0.1:8000/health | jq .
echo ""
echo "API Endpoints:"
echo "  - Health: http://127.0.0.1:8000/health"
echo "  - Webhook: http://127.0.0.1:8000/telegram/webhook/{bot_key}"
echo "  - Admin: http://127.0.0.1:8000/admin/register-bot"
echo ""
