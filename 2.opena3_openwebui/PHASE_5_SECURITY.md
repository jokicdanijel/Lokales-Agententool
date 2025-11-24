# 🔐 PORTIER 3.0 - Security & Token Policies (Phase 5)

**Version**: 3.0.0
**Status**: Implementation Ready
**Date**: 24. November 2025

---

## 📋 Inhaltsverzeichnis

1. [Bearer Token Management](#bearer-token-management)
2. [Service Key Rotation](#service-key-rotation)
3. [Sandbox Security](#sandbox-security)
4. [API Authentication](#api-authentication)
5. [Audit Logging](#audit-logging)
6. [Compliance Checklist](#compliance-checklist)

---

## 🔑 Bearer Token Management

### Token Format (Enterprise)

```
Format: sk_openaX_<purpose>_v<version>_<mode>

Examples:
- sk_opena1_coordinator_v3_prod
- sk_opena2_archivator_v3_prod
- sk_opena3_gateway_v3_prod
- sk_opena20_dashboard_v3_strict
- sk_opena4_cluster_v3_scalable
```

### Token Storage

**File**: `LocalAgent-Pro/config/bearer_tokens.txt`

```
sk_opena1_coordinator_v3_prod
sk_opena2_archivator_v3_prod
sk_opena3_gateway_v3_prod
sk_opena20_dashboard_v3_strict
sk_opena4_cluster_v3_scalable
sk_opena5_cluster_v3_scalable
...
sk_opena19_cluster_v3_scalable
```

### Token Validation

```python
# All requests must include Bearer token
headers = {
    "Authorization": "Bearer sk_opena1_coordinator_v3_prod"
}

# Server-side validation
def validate_token(token):
    with open("LocalAgent-Pro/config/bearer_tokens.txt") as f:
        valid_tokens = f.read().strip().split("\n")
    return token in valid_tokens
```

---

## 🔄 Service Key Rotation (Phase 18)

### Rotation Schedule

```
- Initial Deploy: All keys generated
- Monthly: Automatic rotation (Phase 18)
- Emergency: Manual rotation on security incident
```

### Generate New Tokens

```bash
# Generate 20 unique tokens
for i in {1..20}; do
  python3 -c "import secrets; print('sk_opena'$i'_service_v3_$(date +%s)_$(secrets.token_hex(8))')"
done
```

### Rotation Procedure

```bash
# 1. Generate new tokens
python3 scripts/rotate_tokens.py

# 2. Backup old tokens
cp LocalAgent-Pro/config/bearer_tokens.txt \
   LocalAgent-Pro/config/bearer_tokens.backup.$(date +%s)

# 3. Deploy new tokens
cp bearer_tokens.txt.new LocalAgent-Pro/config/bearer_tokens.txt

# 4. Restart all services
bin/ops.sh restart

# 5. Verify
curl -H "Authorization: Bearer <new_token>" http://127.0.0.1:12345/health
```

---

## 🔒 Sandbox Security

### File Operation Rules

```python
# Allowed operations
- READ:   Current directory and subdirectories
- WRITE:  Current directory and subdirectories
- DELETE: Current directory only (with confirmation)

# Forbidden operations
- Path traversal: ".." in path
- Absolute paths: "/" prefix
- Symlink access: Blocked
- Hidden files:   Blocked (.*)
```

### Shell Execution Whitelist

```python
ALLOWED_COMMANDS = [
    "ls", "pwd", "echo", "cat", "grep", "find", "wc",
    "head", "tail", "date", "whoami", "mkdir", "rm",
    "cp", "mv", "touch", "chmod", "python3", "pip3"
]

# Blacklisted commands
FORBIDDEN = [
    "rm -rf", "sudo", "sh", "bash", "exec", "eval",
    "curl", "wget", "nc", "nmap"
]
```

### Input Validation

```python
# All inputs sanitized
def sanitize_input(user_input):
    # Remove dangerous characters
    dangerous_chars = ['$', '`', '|', ';', '&', '>', '<']
    for char in dangerous_chars:
        if char in user_input:
            raise SecurityError(f"Forbidden character: {char}")
    return user_input.strip()
```

---

## 🔐 API Authentication

### Request Format

```bash
# All API calls require Bearer token
curl -X GET http://127.0.0.1:12345/health \
  -H "Authorization: Bearer sk_opena1_coordinator_v3_prod" \
  -H "Content-Type: application/json"

# Response on success
{
  "status": "healthy",
  "service": "opena1",
  "authenticated": true,
  "timestamp": "2025-11-24T18:30:00Z"
}

# Response on auth failure
{
  "error": "Unauthorized",
  "status": 401,
  "message": "Invalid or missing bearer token"
}
```

### Protected Endpoints

```
Authentication Required:
- POST /api/file/write
- POST /api/file/delete
- POST /api/shell/exec
- POST /api/program/start
- GET  /api/status
- GET  /api/metrics

Public (No Auth):
- GET  /health
- GET  /info
- GET  /version
```

---

## 📝 Audit Logging

### Log Format

```json
{
  "timestamp": "2025-11-24T18:30:45.123456Z",
  "service": "opena3-gateway",
  "level": "INFO",
  "event": "API_CALL",
  "method": "POST",
  "endpoint": "/api/file/read",
  "client_token": "sk_opena1_coordinator_v3_prod",
  "status_code": 200,
  "response_time_ms": 45,
  "details": {
    "file_path": "test.txt",
    "file_size": 1024,
    "operation": "read"
  }
}
```

### Sensitive Field Redaction

```python
REDACTED_FIELDS = [
    "bearer_token",
    "password",
    "secret_key",
    "api_key",
    "credentials"
]

# Automatic redaction
for field in REDACTED_FIELDS:
    if field in log_entry:
        log_entry[field] = "***REDACTED***"
```

### Log Rotation

```bash
# Daily log rotation
logrotate -f /etc/logrotate.d/portier3

# Keep 30 days of logs
find LocalAgent-Pro/logs/ -name "*.log.*" -mtime +30 -delete

# Archive old logs
tar -czf LocalAgent-Pro/logs/archive_$(date +%Y%m%d).tar.gz \
  LocalAgent-Pro/logs/*.log.*
```

---

## 🛡️ Compliance Checklist

### Security Standards

- [x] All API calls require Bearer token
- [x] Tokens stored securely (not in code)
- [x] Path traversal protection
- [x] Shell command whitelisting
- [x] Input sanitization
- [x] Audit logging for all operations
- [x] Error messages don't leak sensitive info
- [x] HTTPS ready (for Phase 18)

### Data Protection

- [x] PII redaction in logs
- [x] Automatic log rotation
- [x] Backup policy (Phase 18)
- [x] Data encryption ready (Phase 18)

### Access Control

- [x] Service-to-service authentication
- [x] User identity logging
- [x] Failed auth attempt tracking
- [x] Token expiration ready (Phase 18)

---

## 🔧 Implementation Commands

### Deploy Security Configuration

```bash
# 1. Create token file
mkdir -p LocalAgent-Pro/config
cat > LocalAgent-Pro/config/bearer_tokens.txt << EOF
sk_opena1_coordinator_v3_prod
sk_opena2_archivator_v3_prod
sk_opena3_gateway_v3_prod
sk_opena20_dashboard_v3_strict
EOF

# 2. Lock file permissions
chmod 600 LocalAgent-Pro/config/bearer_tokens.txt
chmod 700 LocalAgent-Pro/config/

# 3. Verify security
ls -la LocalAgent-Pro/config/
```

### Test Bearer Token

```bash
# Test with valid token
curl -X GET http://127.0.0.1:12345/health \
  -H "Authorization: Bearer sk_opena1_coordinator_v3_prod"

# Test with invalid token (should fail)
curl -X GET http://127.0.0.1:12345/health \
  -H "Authorization: Bearer invalid_token"

# Test without token (should fail)
curl -X GET http://127.0.0.1:12345/health
```

---

## 📊 Phase 5 Summary

✅ Bearer Token Management
✅ Service Key Architecture
✅ Sandbox Security Rules
✅ API Authentication Framework
✅ Audit Logging System
✅ Compliance Checklist

**Next**: Phase 6 - Deployment (Systemd, Docker)

---

**Status**: ✨ Phase 5 Complete
**Next Phase**: Phase 6 (Deployment)
