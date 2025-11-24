#!/usr/bin/env bash
# bin/env_bootstrap.sh — Generate .env with UUID token
# Usage: bash bin/env_bootstrap.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    echo "⚠️  .env already exists at $ENV_FILE"
    echo "   Delete it first if you want to regenerate."
    exit 0
fi

echo "🔧 Generating .env file..."

BEARER_TOKEN=$(uuidgen || python3 -c "import uuid; print(uuid.uuid4())")

cat > "$ENV_FILE" <<EOF
# ELION Hyper-Dashboard Environment Variables
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Security
BEARER_TOKEN=$BEARER_TOKEN

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
OPENAI_ORG=org-YOUR_ORG_HERE
OPENAI_BASE_URL=https://api.openai.com/v1

# Dashboard
DASHBOARD_ADMIN_TOKEN=$BEARER_TOKEN

# Telegram (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_SECRET=
TELEGRAM_ALLOWED_USERS=

# Paths
ARCHIVP_ROOT=$ROOT/1.opena1&2_portier/archivp_store
DB_PATH=$ROOT/data/db.sqlite
EOF

chmod 600 "$ENV_FILE"

echo "✅ .env created at $ENV_FILE"
echo ""
echo "🔑 Bearer Token: $BEARER_TOKEN"
echo ""
echo "⚠️  Remember to set your OPENAI_API_KEY in .env"
