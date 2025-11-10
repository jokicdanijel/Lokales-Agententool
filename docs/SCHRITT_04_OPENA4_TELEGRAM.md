# SCHRITT 4 – opena4 Telegram Agent (Messenger Interface)

**Version:** 1.0  
**Status:** ✅ Implementation Complete  
**Commit:** 84c2b00  
**Date:** 2025-11-10 UTC  

---

## 0) Purpose & Role

**opena4** ist das **Telegram-Interface** des Portier-Systems – der Messenger-Eingang/Ausgang für Chat-basierte Interaktion.

**Kernaufgaben:**
- Empfangen von Telegram-Nachrichten (Long-Polling oder Webhook)
- Validierung gegen RBAC (authorized user IDs)
- Weiterleitung als **CMD** an opena2 (Archivator)
- Empfang von **RESP** und Rückleitung an Telegram
- Append-only Persistenz aller Interaktionen als **Safepoints**
- GitHub-Webhook Integration für CI/CD-Benachrichtigungen

**Kommunikationsfluss:**
```
┌─ Telegram User ─────────────┐
│                              │
│  /browse <url>              │
│  /analyze <file>            │
│  /status                    │
│  <free text message>        │
│                              │
└──────────┬──────────────────┘
           │
        opena4 (HTTP:12347)
           │
      ┌────┴─────┐
      │           │
    CMD           CMD
  (validate)    (forward)
      │           │
      └───────────┤
                  │
            opena2 (Archivator)
                  │
             RESP (reply)
                  │
              opena4
                  │
         Telegram Chat
             (reply_text)
```

---

## 1) Topology & Network

### Port Assignment

| Service | Port | Host | Protocol | Purpose |
|---------|------|------|----------|---------|
| opena4 | 12347 | 127.0.0.1 | HTTP | Telegram Interface |
| opena2 | 12348 | 127.0.0.1 | HTTP | Archivator |
| opena1 | 12344 | 127.0.0.1 | HTTP | Koordinator |

### Port-Policy Enforcement

- **Allowed Window:** [12344, 12399]
- **Forbidden:** 8080 (exclusive for opena3)
- **Enforcement:** `sys.exit(1)` if port == 8080

### Network Binding

- **Loopback Only:** 127.0.0.1 (no external exposure)
- **Reverse-Proxy Ready:** HTTPS/TLS at boundary (nginx)

---

## 2) API Endpoints

### GET /

Root endpoint with service info.

**Response:**
```json
{
  "service": "opena4",
  "name": "Telegram Agent",
  "version": "1.0.0",
  "description": "Portier Telegram interface with Safepoint persistence"
}
```

### GET /health

Health-check with port-policy.

**Response:**
```json
{
  "service": "opena4",
  "status": "ok",
  "timestamp": "2025-11-10T12:34:56.789Z",
  "port_policy": {
    "window": [12344, 12345, 12346, 12347, 12348, 12349],
    "forbidden": [8080]
  },
  "uptime_seconds": 3661.23
}
```

### POST /telegram/message

Receive Telegram message.

**Request:**
```json
{
  "chat_id": 12345,
  "user_id": 123456789,
  "message_id": 1,
  "text": "Browse https://example.com",
  "timestamp": "2025-11-10T12:34:56Z"
}
```

**Validation:**
- `chat_id`: integer
- `user_id`: integer (must be in TELEGRAM_ALLOWED_USERS if configured)
- `message_id`: integer
- `text`: non-empty string
- `timestamp`: ISO-8601 Z format

**Response (Success):**
```json
{
  "ok": true,
  "request_id": "1_1731245696",
  "response": {
    "preview": "..."
  }
}
```

**Response (Auth Failure):**
```json
{
  "ok": false,
  "error": "User not authorized"
}
```

**Response (Schema Error – 8.3 Format):**
```json
{
  "request_id": null,
  "timestamp": "2025-11-10T12:34:56.789Z",
  "source": "opena4",
  "error": {
    "code": "SCHEMA_VIOLATION",
    "message": "Invalid message schema",
    "details": {
      "validation_errors": [
        {"field": "text", "message": "Field required"}
      ]
    }
  },
  "strict": true
}
```

### POST /github/webhook

GitHub webhook receiver for CI/CD events.

**Request (GitHub Payload):**
```json
{
  "ref": "refs/heads/main",
  "repository": {"full_name": "user/repo"},
  "head_commit": {"message": "feat: new feature"}
}
```

**Response:**
```json
{
  "ok": true,
  "message": "🛠️ GitHub push: user/repo @ main\nfeat: new feature"
}
```

### GET /status

Service status with recent safepoints.

**Response:**
```json
{
  "service": "opena4",
  "status": "operational",
  "config": {
    "service": "opena4",
    "host": "127.0.0.1",
    "port": 12347,
    "port_policy": {
      "allowed": [12344, 12345, 12346, 12347, 12348, 12349],
      "forbidden": [8080]
    },
    "telegram": {
      "bot_token_configured": true,
      "allowed_users_count": 2,
      "webhook_url": "(none)"
    },
    "endpoints": {
      "opena2": "http://127.0.0.1:12348/store/archivp",
      "opena1": "http://127.0.0.1:12344/invoke"
    },
    "archive_dir": "/path/to/4.opena4_telegram/archivp",
    "log_level": "INFO"
  },
  "recent_safepoints": [
    {
      "sp": "SP1731245696_opena4→opena2_CMD.json",
      "src": "opena4",
      "dst": "opena2",
      "kind": "CMD",
      "ts": "2025-11-10T12:34:56.789123Z",
      "request_id": "1_1731245696"
    }
  ]
}
```

---

## 3) Safepoint Format & Persistence

### Safepoint Naming

```
SP<unix_ts>_<src>→<dst>_<KIND>.json
```

**Example:**
```
SP1731245696_opena4→opena2_CMD.json
SP1731245698_opena2→opena4_RESP.json
SP1731245700_opena4→opena4_ERR.json
```

### Safepoint Structure

```json
{
  "timestamp": "2025-11-10T12:34:56.789123Z",
  "src": "opena4",
  "dst": "opena2",
  "kind": "CMD",
  "payload": {
    "request_id": "1_1731245696",
    "timestamp": "2025-11-10T12:34:56Z",
    "command": "BROWSE",
    "payload": {"url": "https://example.com"},
    "routing": {"resolved_path": "https://example.com"},
    "project": {"name": "telegram_relay"},
    "strict": true
  },
  "strict": true
}
```

### Archive Directory Structure

```
archivp/
├── YYYY/MM/DD/
│   ├── SP1731245696_opena4→opena2_CMD.json
│   ├── SP1731245698_opena2→opena4_RESP.json
│   └── SP1731245700_opena4→opena4_ERR.json
│
└── index.jsonl  (append-only log, all events)
```

### Index Format (JSONL)

```
{"sp":"SP1731245696_opena4→opena2_CMD.json","src":"opena4","dst":"opena2","kind":"CMD","ts":"2025-11-10T12:34:56.789123Z","request_id":"1_1731245696"}
{"sp":"SP1731245698_opena2→opena4_RESP.json","src":"opena2","dst":"opena4","kind":"RESP","ts":"2025-11-10T12:34:58.123456Z","request_id":"1_1731245696"}
{"sp":"SP1731245700_opena4→opena4_ERR.json","src":"opena4","dst":"opena4","kind":"ERR","ts":"2025-11-10T12:34:59.999Z","request_id":null}
```

### Append-Only Guarantee

- Never overwrite existing safepoints
- Index entries appended, never deleted
- SHA-256 dedupe check (planned for Schritt 3)
- INTEGRITY.json manifest maintained

---

## 4) Configuration (.env)

### Required Settings

```bash
# Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Allowed Telegram User IDs (comma-separated, or empty for all)
TELEGRAM_ALLOWED_USERS=123456789,987654321

# Port Configuration
PORTIER_PORT=12347
PORTIER_HOST=127.0.0.1
PORTIER_BASE_DIR=/path/to/4.opena4_telegram

# Port-Policy
PORTIER_ALLOWED_PORTS=12344,12345,12346,12347,12348,12349
PORTIER_FORBIDDEN_PORTS=8080

# Integration Endpoints
OPENA2_URL=http://127.0.0.1:12348/store/archivp
OPENA1_URL=http://127.0.0.1:12344/invoke

# Logging
LOG_LEVEL=INFO
```

### Optional Settings

```bash
# Webhook URL (for Telegram webhook mode instead of polling)
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/telegram/webhook
```

---

## 5) Implementation Checklist

### Phase 1: Core Setup ✅

- [x] Create `schemas.py` with Pydantic v2 models
- [x] Create `config.py` with Port-Policy enforcement
- [x] Create `main_telegram_agent.py` with FastAPI + Telegram bot
- [x] Create `requirements.txt` with dependencies
- [x] Create `.env.example` template
- [x] Setup venv and install dependencies
- [x] Symlink root `.env` to agent directory

### Phase 2: Testing ✅

- [x] Start server on port 12347/12350
- [x] Test GET /health endpoint
- [x] Test POST /telegram/message with valid user
- [x] Test POST /telegram/message with invalid user (auth failure)
- [x] Test invalid schema (returns 8.3 error format)
- [x] Verify safepoint creation (archivp/YYYY/MM/DD/)
- [x] Verify append-only index.jsonl
- [x] Test GET /status endpoint
- [x] Check port-policy enforcement (8080 rejection)

### Phase 3: Integration (Ready)

- [ ] Configure TELEGRAM_BOT_TOKEN
- [ ] Set TELEGRAM_ALLOWED_USERS with your Telegram ID
- [ ] Test Telegram command: /start
- [ ] Test Telegram command: /browse <url>
- [ ] Test Telegram command: /analyze <file>
- [ ] Verify opena2 integration (forward CMD → receive RESP)
- [ ] Setup GitHub webhook (Settings → Webhooks)
- [ ] Test CI/CD notifications via Telegram

### Phase 4: Production (Planned)

- [ ] Setup HTTPS/TLS reverse proxy (nginx)
- [ ] Configure Telegram webhook mode (vs polling)
- [ ] Enable monitoring/alerting
- [ ] Load test (concurrent users)
- [ ] Security audit (token exposure, input validation)
- [ ] Performance optimization (safepoint write latency)

---

## 6) Security & Compliance

### RBAC (Role-Based Access Control)

- **TELEGRAM_ALLOWED_USERS:** Whitelist of authorized Telegram user IDs
- **Default:** If empty, all users allowed (not recommended for production)
- **Enforcement:** Checked on every POST /telegram/message

### Secrets Management

- **Token Storage:** .env file (not in git, .gitignore'd)
- **Token Masking:** Logs never show full token
- **Example:** `.env.example` has placeholder values only

### Port-Policy Compliance

- **Binding:** Loopback 127.0.0.1 only (no external)
- **Forbidden Port Check:** Port 8080 rejected with `sys.exit(1)`
- **Allowed Range:** [12344, 12399]
- **Enforcement:** Runtime + CI/CD validation

### Data Integrity

- **Append-Only:** Never overwrite safepoints
- **Index Consistency:** index.jsonl append-only
- **Dedupe Ready:** SHA-256 hashing (Schritt 3)
- **Audit Trail:** Complete request/response logged

### Input Validation

- **Pydantic v2:** `extra='forbid'` rejects unknown fields
- **Type Hints:** All endpoints fully annotated
- **Message Validation:** chat_id, user_id, text, timestamp checked
- **Error Responses:** Always schema 8.3 format

### TLS/HTTPS

- **Current:** HTTP only (loopback safe)
- **Production:** Reverse-proxy with TLS 1.2+ (nginx)
- **Webhook:** HTTPS required for GitHub/Telegram webhooks

---

## 7) Error Handling

### Error Codes (Schema 8.3)

| Code | HTTP | Meaning | Recovery |
|------|------|---------|----------|
| SCHEMA_VIOLATION | 400 | Invalid request schema | Check field types, required fields |
| UNAUTHORIZED | 403 | User not in whitelist | Add user ID to TELEGRAM_ALLOWED_USERS |
| FORWARD_ERROR | 502 | opena2 unreachable | Check opena2 health, OPENA2_URL |
| ANALYZE_ERROR | 500 | File analysis failed | Check file permissions, path |
| WEBHOOK_ERROR | 500 | GitHub webhook failed | Check webhook configuration |
| INTERNAL_ERROR | 500 | Server error | Check logs, restart agent |

### Error Response Example

```json
{
  "request_id": "1_1731245696",
  "timestamp": "2025-11-10T12:34:56.789Z",
  "source": "opena4",
  "error": {
    "code": "FORWARD_ERROR",
    "message": "Failed to forward to opena2: Connection refused",
    "details": {
      "opena2_url": "http://127.0.0.1:12348/store/archivp",
      "timeout_seconds": 30
    }
  },
  "strict": true
}
```

---

## 8) Deployment

### Quick Start

```bash
# 1. Navigate to agent directory
cd /home/.../4.opena4_telegram

# 2. Create and activate venv
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure .env (copy from .env.example)
cp .env.example .env
# Edit .env: set TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS

# 5. Start server
python main_telegram_agent.py --port 12347

# 6. Test health endpoint
curl http://127.0.0.1:12347/health | jq .
```

### Telegram Bot Setup

```bash
# 1. Open https://t.me/BotFather
# 2. Send /newbot
# 3. Follow instructions, get BOT_TOKEN
# 4. Add to .env: TELEGRAM_BOT_TOKEN=<token>

# 5. Get your user ID
# 6. Open https://t.me/userinfobot, send /start
# 7. Add to .env: TELEGRAM_ALLOWED_USERS=<your_id>

# 8. Restart opena4
# 9. Send /start to your bot
```

### Systemd Service (Optional)

```ini
[Unit]
Description=opena4 Telegram Agent
After=network.target

[Service]
Type=simple
User=danijel-jd
WorkingDirectory=/path/to/4.opena4_telegram
ExecStart=/path/to/4.opena4_telegram/venv/bin/python main_telegram_agent.py --port 12347
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 9) Testing Scenarios

### Scenario 1: Valid User, Browse Command

```bash
curl -X POST http://127.0.0.1:12347/telegram/message \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id": 12345,
    "user_id": 123456789,
    "message_id": 1,
    "text": "/browse https://github.com",
    "timestamp": "2025-11-10T12:34:56Z"
  }'
```

**Expected:**
- ✅ HTTP 200 OK
- ✅ CMD safepoint created
- ✅ Response forwarded to opena2
- ✅ RESP safepoint created

### Scenario 2: Unauthorized User

```bash
curl -X POST http://127.0.0.1:12347/telegram/message \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id": 12345,
    "user_id": 999999999,
    "message_id": 2,
    "text": "/browse https://example.com",
    "timestamp": "2025-11-10T12:34:57Z"
  }'
```

**Expected:**
- ✅ HTTP 403 Forbidden
- ✅ Error safepoint created (opena4→opena4_ERR)
- ✅ Message: "User not authorized"

### Scenario 3: Invalid Schema

```bash
curl -X POST http://127.0.0.1:12347/telegram/message \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id": 12345,
    "user_id": 123456789,
    "text": "Missing message_id"
  }'
```

**Expected:**
- ✅ HTTP 400 Bad Request
- ✅ Schema 8.3 error response
- ✅ Validation errors listed

---

## 10) Integration with Portier Chain

### Flow: Telegram → opena2 → opena1 → opena3

1. **User sends:** `/browse https://example.com` in Telegram
2. **opena4 receives:** POST /telegram/message
3. **opena4 validates:** User ID, schema
4. **opena4 creates:** CMD safepoint (opena4→opena2)
5. **opena4 forwards:** CMD to opena2 (POST /store/archivp)
6. **opena2 creates:** CMD safepoint, processes
7. **opena2 invokes:** opena1 (POST /invoke)
8. **opena1 delegates:** to opena3 (browse tool)
9. **opena3 responds:** with preview HTML
10. **opena2 creates:** RESP safepoint, returns to opena4
11. **opena4 creates:** RESP safepoint
12. **opena4 sends:** Reply text to Telegram bot
13. **Telegram sends:** Message to user

**All safepoints persisted:**
- `SP<ts>_opena4→opena2_CMD.json`
- `SP<ts>_opena2→opena1_CMD.json`
- `SP<ts>_opena1→opena3_CMD.json`
- `SP<ts>_opena3→opena1_RESP.json`
- `SP<ts>_opena1→opena2_RESP.json`
- `SP<ts>_opena2→opena4_RESP.json`

---

## 11) Monitoring & Debugging

### Health Check

```bash
curl -s http://127.0.0.1:12347/health | jq .
```

### Recent Safepoints

```bash
curl -s http://127.0.0.1:12347/status | jq '.recent_safepoints[-5:]'
```

### View Safepoint File

```bash
tail -5 /path/to/4.opena4_telegram/archivp/2025/11/10/*.json | jq .
```

### View Index Log

```bash
tail -10 /path/to/4.opena4_telegram/archivp/index.jsonl | jq .
```

### Check Logs

```bash
tail -50 /path/to/4.opena4_telegram/logs/opena4.log
```

### Port-Policy Test

```bash
# Should fail (exit 1)
python main_telegram_agent.py --port 8080 --no-telegram
```

---

## References & Next Steps

**Completed:**
- ✅ Schritt 1 (7.1 Validation for opena1)
- ✅ Schritt 4 (opena4 Telegram Agent)

**In Progress:**
- ⏳ Schritt 2 (Tool-Registry & Mapping)
- ⏳ Schritt 3 (Safepoint Format & Dedupe)

**Coming Next:**
- 📋 Schritt 5 (opena5 VS Code Bridge)
- 📋 Schritt 6 (opena2 Archivator Deep-Dive)
- 📋 Schritt 7 (Monitoring & Release)

---

**Version:** 1.0 | **Status:** ✅ Complete | **Commit:** 84c2b00 | **Date:** 2025-11-10 UTC
