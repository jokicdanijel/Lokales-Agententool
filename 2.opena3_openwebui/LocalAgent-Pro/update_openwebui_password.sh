#!/bin/bash
# OpenWebUI Password Reset Script
# Usage: ./update_openwebui_password.sh

set -e

echo "🔐 OpenWebUI Password Reset"
echo "============================"
echo ""

# Check if running with sudo/root for Docker access
if ! docker ps &> /dev/null; then
    echo "❌ Error: Cannot access Docker. Try running with sudo:"
    echo "   sudo ./update_openwebui_password.sh"
    exit 1
fi

# Find OpenWebUI container
CONTAINER_ID=$(docker ps --filter "ancestor=ghcr.io/open-webui/open-webui:main" --format "{{.ID}}" | head -n 1)

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ Error: OpenWebUI container not found!"
    echo "   Make sure OpenWebUI is running:"
    echo "   docker-compose up -d"
    exit 1
fi

echo "✅ Found OpenWebUI container: $CONTAINER_ID"
echo ""

# Get new password
read -sp "Enter new password: " NEW_PASSWORD
echo ""
read -sp "Confirm password: " CONFIRM_PASSWORD
echo ""
echo ""

# Check if passwords match
if [ "$NEW_PASSWORD" != "$CONFIRM_PASSWORD" ]; then
    echo "❌ Passwords don't match!"
    exit 1
fi

# Check password strength
if [ ${#NEW_PASSWORD} -lt 8 ]; then
    echo "⚠️  Warning: Password should be at least 8 characters long!"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Generate bcrypt hash inside container
echo "🔄 Generating password hash..."
PASSWORD_HASH=$(docker exec -i $CONTAINER_ID python3 -c "
import bcrypt
import sys
password = '''$NEW_PASSWORD'''.encode('utf-8')
hash = bcrypt.hashpw(password, bcrypt.gensalt())
print(hash.decode('utf-8'))
")

if [ -z "$PASSWORD_HASH" ]; then
    echo "❌ Error: Failed to generate password hash!"
    exit 1
fi

echo "✅ Password hash generated"
echo ""

# Update database
echo "🔄 Updating database..."
docker exec -i $CONTAINER_ID sqlite3 /app/backend/data/webui.db <<EOF
UPDATE auth SET password = '$PASSWORD_HASH' WHERE id = 1;
SELECT 'Updated user ID: ' || id || ', Email: ' || email FROM auth WHERE id = 1;
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Password updated successfully!"
    echo ""
    echo "📝 Details:"
    echo "   Container: $CONTAINER_ID"
    echo "   Hash: ${PASSWORD_HASH:0:30}..."
    echo ""
    echo "🔄 Restarting OpenWebUI container..."
    docker restart $CONTAINER_ID > /dev/null 2>&1
    echo "✅ Container restarted"
    echo ""
    echo "🎉 Done! You can now login with your new password at:"
    echo "   http://localhost:3000"
else
    echo "❌ Error: Failed to update database!"
    exit 1
fi
