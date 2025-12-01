#!/usr/bin/env bash
# bin/print_token.sh — Display current bearer token
# Usage: bash bin/print_token.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env file not found"
    echo "   Run: bin/env_bootstrap.sh"
    exit 1
fi

if grep -q "BEARER_TOKEN=" "$ENV_FILE"; then
    token=$(grep "BEARER_TOKEN=" "$ENV_FILE" | cut -d'=' -f2)
    echo "🔑 Bearer Token:"
    echo ""
    echo "   $token"
    echo ""
    echo "Use in Authorization header:"
    echo "   Authorization: Bearer $token"
else
    echo "❌ BEARER_TOKEN not found in .env"
    exit 1
fi
