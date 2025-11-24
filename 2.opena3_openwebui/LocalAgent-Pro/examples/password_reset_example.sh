#!/bin/bash
# Example: OpenWebUI Password Reset
# This file demonstrates various password reset scenarios

echo "📝 OpenWebUI Password Reset Examples"
echo "====================================="
echo ""

# Example 1: Basic password reset
echo "Example 1: Basic Password Reset"
echo "--------------------------------"
echo "$ ./update_openwebui_password.sh"
echo "🔐 OpenWebUI Password Reset"
echo "Enter new password: ********"
echo "Confirm password: ********"
echo "✅ Password updated successfully!"
echo ""

# Example 2: Manual password reset with Python
echo "Example 2: Manual Reset (Python)"
echo "--------------------------------"
cat << 'EOF'
$ docker exec -it <container-id> python3
>>> import bcrypt
>>> password = "MyNewPassword123!".encode('utf-8')
>>> hash = bcrypt.hashpw(password, bcrypt.gensalt())
>>> print(hash.decode('utf-8'))
$2b$12$abcdefghijklmnopqrstuvwxyz1234567890
>>> exit()

$ docker exec -it <container-id> sqlite3 /app/backend/data/webui.db
sqlite> UPDATE auth SET password = '$2b$12$...' WHERE id = 1;
sqlite> .quit

$ docker restart <container-id>
EOF
echo ""

# Example 3: Automated reset with Python script
echo "Example 3: Automated Python Script"
echo "-----------------------------------"
cat << 'EOF'
$ cat reset_password.py
#!/usr/bin/env python3
import bcrypt
import sqlite3

new_password = input("New password: ")
hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

conn = sqlite3.connect('/path/to/webui.db')
conn.execute("UPDATE auth SET password = ? WHERE id = 1", (hash.decode('utf-8'),))
conn.commit()
print("✅ Password updated!")

$ python3 reset_password.py
EOF
echo ""

# Example 4: Docker Compose reset
echo "Example 4: Fresh Start (Docker Compose)"
echo "----------------------------------------"
cat << 'EOF'
$ docker-compose down
$ docker volume rm localagent-pro_openwebui-data
$ docker-compose up -d
# Create new admin account at http://localhost:3000
EOF
echo ""

# Example 5: Backup before reset
echo "Example 5: Backup Before Reset"
echo "-------------------------------"
cat << 'EOF'
# Backup database
$ docker cp openwebui:/app/backend/data/webui.db ./backup_$(date +%Y%m%d).db

# Reset password
$ ./update_openwebui_password.sh

# If something goes wrong, restore:
$ docker cp ./backup_20251121.db openwebui:/app/backend/data/webui.db
$ docker restart openwebui
EOF
echo ""

# Example 6: Environment-based password
echo "Example 6: Environment Variable"
echo "--------------------------------"
cat << 'EOF'
# .env file
OPENWEBUI_ADMIN_PASSWORD="SecurePassword123!"

# docker-compose.yml
services:
  openwebui:
    environment:
      - ADMIN_PASSWORD=${OPENWEBUI_ADMIN_PASSWORD}
EOF
echo ""

# Example 7: Check current password hash
echo "Example 7: Verify Current Hash"
echo "-------------------------------"
cat << 'EOF'
$ docker exec -it <container-id> sqlite3 /app/backend/data/webui.db
sqlite> SELECT id, email, password FROM auth;
1|admin@example.com|$2b$12$abcdefghijklmnopqrstuvwxyz...
sqlite> .quit
EOF
echo ""

# Example 8: Multi-user password reset
echo "Example 8: Reset Multiple Users"
echo "--------------------------------"
cat << 'EOF'
# List all users
$ docker exec -it <container-id> sqlite3 /app/backend/data/webui.db
sqlite> SELECT id, email FROM auth;

# Reset specific user
sqlite> UPDATE auth SET password = '$2b$12$...' WHERE email = 'user@example.com';
EOF
echo ""

# Example 9: Cron job for scheduled resets
echo "Example 9: Scheduled Password Rotation"
echo "---------------------------------------"
cat << 'EOF'
# Add to crontab
$ crontab -e

# Reset password monthly (requires non-interactive script)
0 0 1 * * /path/to/scheduled_password_reset.sh

# scheduled_password_reset.sh
#!/bin/bash
NEW_PASSWORD=$(openssl rand -base64 32)
echo "$NEW_PASSWORD" | /path/to/update_openwebui_password.sh
echo "New password: $NEW_PASSWORD" | mail -s "OpenWebUI Password Changed" admin@example.com
EOF
echo ""

# Example 10: API-based reset (future)
echo "Example 10: API Reset (Planned)"
echo "--------------------------------"
cat << 'EOF'
$ curl -X POST http://localhost:3000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "old_password": "OldPassword123!",
    "new_password": "NewPassword456!"
  }'

Response:
{
  "success": true,
  "message": "Password updated successfully"
}
EOF
echo ""

echo "📚 More examples:"
echo "   - See PASSWORD_RESET.md for detailed guide"
echo "   - Run: ./update_openwebui_password.sh"
echo "   - Check: docker logs <container-id>"
echo ""
echo "✅ Examples complete!"
