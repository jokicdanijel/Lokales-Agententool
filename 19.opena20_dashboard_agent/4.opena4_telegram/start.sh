#!/bin/bash
# Start script for opena4 (Telegram Agent)

set -e

echo "🚀 Starting opena4 (Telegram Agent)"
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found, copying from .env.example"
    cp .env.example .env
    echo "❗ Please edit .env and add your TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Check if TELEGRAM_BOT_TOKEN is set
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_bot_token_here" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set in .env"
    echo ""
    echo "To get a token:"
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send /newbot and follow instructions"
    echo "3. Copy the token to .env file"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📡 Starting opena4 on port 12346..."
echo "🤖 Telegram Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo ""

# Start the agent
python main.py
