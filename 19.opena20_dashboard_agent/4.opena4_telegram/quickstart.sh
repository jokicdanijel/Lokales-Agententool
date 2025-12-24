#!/bin/bash
# Quick Start Guide for opena4 (Telegram Agent)
# ============================================

echo "🤖 OPENA4 TELEGRAM AGENT - QUICK START"
echo "======================================"
echo ""

# Step 1: Get Telegram Bot Token
echo "📱 STEP 1: Get Telegram Bot Token"
echo "----------------------------------"
echo "1. Open Telegram and search for: @BotFather"
echo "2. Send command: /newbot"
echo "3. Follow the instructions to create your bot"
echo "4. Copy the API token"
echo ""
read -p "Do you have your bot token? (y/n): " has_token

if [ "$has_token" != "y" ]; then
    echo ""
    echo "❌ Please get a bot token first from @BotFather"
    echo "   Then run this script again"
    exit 1
fi

# Step 2: Configure .env
echo ""
echo "🔧 STEP 2: Configure Environment"
echo "--------------------------------"

if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Overwrite? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Using existing .env file"
    else
        cp .env.example .env
    fi
else
    cp .env.example .env
fi

echo ""
read -p "Enter your Telegram Bot Token: " bot_token
sed -i "s/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$bot_token/" .env

echo "✓ Environment configured"

# Step 3: Install Dependencies
echo ""
echo "📦 STEP 3: Install Dependencies"
echo "-------------------------------"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✓ Dependencies installed"

# Step 4: Test Configuration
echo ""
echo "🧪 STEP 4: Test Bot Token"
echo "-------------------------"

source .env
token_test=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe")

if echo "$token_test" | grep -q '"ok":true'; then
    bot_name=$(echo "$token_test" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Bot token is valid!"
    echo "   Bot username: @$bot_name"
else
    echo "❌ Bot token is invalid"
    echo "   Please check your token and try again"
    exit 1
fi

# Step 5: Get Chat ID
echo ""
echo "💬 STEP 5: Get Your Chat ID"
echo "--------------------------"
echo "1. Open Telegram and search for: @$bot_name"
echo "2. Send a message: /start"
echo "3. Press Enter here to get your chat ID"
read -p "Press Enter when done..."

updates=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates")
chat_id=$(echo "$updates" | grep -o '"chat":{"id":[0-9]*' | head -1 | grep -o '[0-9]*$')

if [ -n "$chat_id" ]; then
    echo "✅ Your Chat ID: $chat_id"
    echo ""
    echo "💡 You can use this chat ID to send messages:"
    echo "   curl -X POST http://localhost:12346/send \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"chat_id\": $chat_id, \"text\": \"Hello from ELION!\"}'"
else
    echo "⚠️  No chat ID found. Make sure you sent /start to the bot"
fi

# Step 6: Ready to start
echo ""
echo "🚀 STEP 6: Start the Agent"
echo "-------------------------"
echo ""
echo "Everything is ready! To start opena4:"
echo ""
echo "  ./start.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "The agent will run on: http://localhost:12346"
echo ""
echo "📚 Documentation: README.md"
echo "🧪 Tests: pytest tests/"
echo ""

read -p "Start opena4 now? (y/n): " start_now

if [ "$start_now" == "y" ]; then
    echo ""
    echo "🚀 Starting opena4..."
    echo ""
    python main.py
else
    echo ""
    echo "✅ Setup complete! Run './start.sh' when ready."
fi
