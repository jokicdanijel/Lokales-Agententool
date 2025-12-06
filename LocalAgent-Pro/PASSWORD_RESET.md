# 🔐 OpenWebUI Password Reset Guide

## Overview

This guide explains how to reset or update passwords in OpenWebUI when you've lost access to your account or need to change a password directly in the database.

## Quick Start

### Basic Usage

```bash
./update_openwebui_password.sh -e EMAIL -p PASSWORD_HASH
```

### Example

```bash
./update_openwebui_password.sh -e jokicdanijel@gmail.com -p '$2b$12$abc123...'
```

## Options

| Option | Description | Required |
|--------|-------------|----------|
| `-e EMAIL` | Email address of the user | Yes |
| `-p PASSWORD_HASH` | Bcrypt password hash | Yes |
| `-v VOLUME_NAME` | Docker volume name | No (default: `openwebui_openwebui_data`) |
| `-h` | Show help message | No |

## Generating a Password Hash

OpenWebUI uses bcrypt for password hashing. You can generate a bcrypt hash using:

### Python Method

```bash
python3 -c "import bcrypt; print(bcrypt.hashpw(b'your_new_password', bcrypt.gensalt()).decode())"
```

**Example:**
```bash
# Generate hash for password "myNewPassword123"
python3 -c "import bcrypt; print(bcrypt.hashpw(b'myNewPassword123', bcrypt.gensalt()).decode())"
# Output: $2b$12$AbCdEfGhIjKlMnOpQrStUvWxYz...
```

### Using the Script

```bash
# Generate and use in one command
NEW_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'myNewPassword123', bcrypt.gensalt()).decode())")
./update_openwebui_password.sh -e user@example.com -p "$NEW_HASH"
```

## Prerequisites

1. **Docker must be installed and running**
   ```bash
   docker --version
   ```

2. **User must have Docker permissions**
   - The script automatically detects if `sg` command is available and uses it for Docker group access
   - If `sg` is not available, it falls back to running `docker` directly
   - Ensure your user is in the `docker` group:
     ```bash
     sudo usermod -aG docker $USER
     ```
   - Log out and back in for changes to take effect

3. **Python bcrypt library (for generating hashes)**
   ```bash
   pip install bcrypt
   ```

4. **OpenWebUI Docker volume must exist**
   - Default volume name: `openwebui_openwebui_data`
   - Check available volumes:
     ```bash
     docker volume ls | grep webui
     ```

## Common Scenarios

### Scenario 1: Forgot Admin Password

```bash
# 1. Generate a new password hash
NEW_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode())")

# 2. Update the admin account
./update_openwebui_password.sh -e admin@example.com -p "$NEW_HASH"

# 3. Log in with the new password
```

### Scenario 2: Reset User Password

```bash
# Reset password for a specific user
./update_openwebui_password.sh \
  -e jokicdanijel@gmail.com \
  -p '$2b$12$AbCdEfGhIjKlMnOpQrStUv...'
```

### Scenario 3: Custom Docker Volume

If your OpenWebUI uses a different volume name:

```bash
# List volumes to find the correct name
docker volume ls

# Use custom volume name
./update_openwebui_password.sh \
  -e user@example.com \
  -p '$2b$12$...' \
  -v custom_webui_data
```

## Troubleshooting

### Error: Docker is not installed

**Solution:**
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### Error: Docker volume does not exist

**Problem:** The specified volume name is incorrect or doesn't exist.

**Solution:**
```bash
# List all Docker volumes
docker volume ls

# Look for OpenWebUI-related volumes
docker volume ls | grep -i webui

# Use the correct volume name with -v option
./update_openwebui_password.sh -e user@example.com -p '$2b$...' -v correct_volume_name
```

### Error: Permission denied

**Problem:** User doesn't have Docker permissions.

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or use:
newgrp docker

# Verify
docker ps
```

### Error: Invalid email format

**Problem:** Email address is not in a valid format.

**Solution:** Use a valid email address (e.g., `user@example.com`)

## Security Considerations

⚠️ **Important Security Notes:**

1. **Backup First:** Always backup your database before making changes
   ```bash
   docker run --rm -v openwebui_openwebui_data:/data -v $(pwd):/backup \
     alpine cp /data/webui.db /backup/webui.db.backup
   ```

2. **Secure Password Storage:** Never store plain-text passwords
   - Always use bcrypt hashes
   - Use strong passwords (minimum 12 characters)

3. **Limit Access:** Keep this script secure
   - Only authorized administrators should have access
   - Set proper file permissions: `chmod 750 update_openwebui_password.sh`

4. **Audit Changes:** Keep track of password changes
   - Log who changed passwords and when
   - Monitor for unauthorized access attempts

## Advanced Usage

### Batch Password Reset

Create a script for multiple users:

```bash
#!/bin/bash
# batch_password_reset.sh

declare -A users
users=(
  ["user1@example.com"]="password1"
  ["user2@example.com"]="password2"
  ["user3@example.com"]="password3"
)

for email in "${!users[@]}"; do
  password="${users[$email]}"
  hash=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'$password', bcrypt.gensalt()).decode())")
  ./update_openwebui_password.sh -e "$email" -p "$hash"
done
```

### Verify Database Changes

After updating, verify the change:

```bash
# View the auth table
docker run --rm -v openwebui_openwebui_data:/data nouchka/sqlite3 \
  /data/webui.db "SELECT email, password FROM auth WHERE email='user@example.com';"
```

### Direct SQL Approach (Advanced)

For advanced users who want to run SQL directly:

```bash
# Using the original command format
sg docker -c "docker run --rm -v openwebui_openwebui_data:/data nouchka/sqlite3 \
  /data/webui.db \"UPDATE auth SET password='\$2b\$12\$...' WHERE email='user@example.com';\""
```

## Integration with OpenWebUI Documentation

This password reset utility complements the main OpenWebUI integration. For more information:

- **OpenWebUI Setup:** See `OPENWEBUI_INTEGRATION.md`
- **Installation Guide:** See `INSTALLATION.md`
- **Testing:** See `openwebui_test.sh`

## Related Scripts

- `install_openwebui_prompts.sh` - Install custom prompts
- `openwebui_check.sh` - Quick health check
- `openwebui_test.sh` - Comprehensive testing

## Support

If you encounter issues:

1. Check the Docker logs:
   ```bash
   docker logs open-webui
   ```

2. Verify the database structure:
   ```bash
   docker run --rm -v openwebui_openwebui_data:/data nouchka/sqlite3 \
     /data/webui.db ".schema auth"
   ```

3. Ensure OpenWebUI is running:
   ```bash
   docker ps | grep webui
   ```

---

**Last Updated:** November 2025  
**Maintainer:** LocalAgent-Pro Team
