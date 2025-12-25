# 🤖 MASTER PROMPT - FINAL EDITION

## Vollständige Systemspezifikation für LocalAgent-Pro (opena1-20)

**Version:** 2.0
**Status:** Production Ready
**Last Updated:** 24. November 2025
**Architektur:** 20-Agent Ecosystem mit Strict Policy Enforcement

---

## 📋 INHALTSVERZEICHNIS

1. [Systemarchitektur](#systemarchitektur)
2. [Agent-Spezifikationen (opena1-20)](#agent-spezifikationen)
3. [Sicherheitsmodell (PHASE 15.4)](#sicherheitsmodell)
4. [API-Dokumentation](#api-dokumentation)
5. [Deployment-Richtlinien](#deployment-richtlinien)
6. [Integration LocalAgent-Pro](#integration-localagent-pro)
7. [Troubleshooting & Operations](#troubleshooting--operations)

---

## SYSTEMARCHITEKTUR

### 1.1 Gesamtübersicht

```
┌─────────────────────────────────────────────────────────────┐
│                         USER LAYER                          │
│               OpenWebUI (localhost:3000)                    │
│                  + VSCode Copilot Chat                      │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS/WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                      GATEWAY LAYER                          │
│  kordp (Koordinator-Proxy) - Port 12344                     │
│  ├─ Bearer Token Validation                                 │
│  ├─ Request Routing                                         │
│  └─ Load Balancing                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   ARCHIVATOR LAYER                          │
│  archivp (Archivator) - Port 12345                          │
│  ├─ Safepoint Logging (CMD/RESP/ERROR/SECURITY_EVENT)      │
│  ├─ Request Deduplication                                   │
│  ├─ Audit Trail Management                                  │
│  └─ Performance Metrics                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────────────────────────────┐
        │              │                                      │
        ▼              ▼              ▼         ▼    ▼   ...  ▼
   ┌────────┐   ┌────────┐     ┌────────┐  ┌─────┐       ┌─────────┐
   │ opena3 │   │ opena4 │     │ opena5 │  │ ... │       │ opena20 │
   │ WebUI  │   │Telegram│     │VSCode  │  │     │       │Dashboard│
   │ 12347  │   │ 12348  │     │ 12350  │  │     │       │ 12365   │
   └────────┘   └────────┘     └────────┘  └─────┘       └─────────┘

          AGENT LAYER (LocalAgent-Pro Instances)
          └─ 18 specialized services (opena3-opena20)
          └─ Each with dedicated port (12344-12399)
          └─ Each with unique bearer token
          └─ Each with role-based access control
```

### 1.2 Kommunikationsfluss

```
1. User Query (OpenWebUI/Copilot)
   │
   ├─→ HTTPS POST /request
   │
2. Gateway (kordp) - Port 12344
   │
   ├─→ Verify Bearer Token: "sk_opena1_coord_12344_strict_v1"
   ├─→ Extract client_id: "opena1-coordinator"
   ├─→ Log CMD safepoint (with client_id)
   │
3. Routing Decision
   │
   ├─→ Route to appropriate agent (opena3-opena20)
   │   OR local processing (opena1-opena2)
   │
4. Archivator (archivp) - Port 12345
   │
   ├─→ Store CMD safepoint
   ├─→ Wait for response
   ├─→ Store RESP safepoint (with client_id)
   │
5. Response to User
   │
   ├─→ metadata.policy: "strict"
   ├─→ metadata.auth_verified: true
   ├─→ metadata.source_origin: "opena1-coordinator"
```

---

## AGENT-SPEZIFIKATIONEN

### 2.1 CORE SERVICES (opena1-2)

#### opena1-coordinator (Port 12344)

**Rolle:** Gateway & Request Orchestration
**Status:** ✅ Production Ready (PHASE 15.4 Complete)
**Bearer Token:** `sk_opena1_coord_12344_strict_v1`

**Endpoints:**

- `POST /request` – Accept user queries (strict auth required)
- `GET /health` – Health check (diagnostic, no auth)
- `GET /log/opena1` – Retrieve safepoint logs
- `GET /status` – System status

**Capabilities:**

- Bearer token validation
- Request routing
- Load balancing
- Security event logging
- Client ID extraction & tracking

**Safepoints:** 150+ (CMD/RESP/ERROR/SECURITY_EVENT)

---

#### opena2-archivator (Port 12345)

**Rolle:** Safepoint Management & Audit Trail
**Status:** ✅ Production Ready
**Bearer Token:** `sk_opena2_arch_12345_strict_v1`

**Endpoints:**

- `POST /safepoint` – Store safepoint
- `GET /safepoint/<id>` – Retrieve safepoint
- `GET /audit/<client_id>` – Client audit trail
- `GET /stats` – Archive statistics

**Capabilities:**

- Safepoint persistence (JSON files)
- Request deduplication (MD5 hashing)
- Audit trail maintenance
- Performance metrics
- Archive cleanup

**Features:**

- Async logging (non-blocking)
- Client ID tracking in all records
- Security event correlation
- Timestamp standardization

---

### 2.2 INTERFACE AGENTS (opena3-opena20)

#### opena3-webui (Port 12347)

**Rolle:** OpenWebUI Terminal Integration
**Bearer Token:** `sk_opena3_web_12347_strict_v1`
**Status:** 🚀 Ready for Deployment (PHASE 15.5)

**Functionality:**

- OpenWebUI native chat interface
- Markdown rendering
- File upload/download
- Real-time streaming responses

---

#### opena4-telegram (Port 12348)

**Rolle:** Telegram Bot Integration
**Bearer Token:** `sk_opena4_tele_12348_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Telegram message handling
- Group chat support
- Inline query responses
- Media attachment processing

---

#### opena5-vscode (Port 12350)

**Rolle:** VSCode Copilot Integration
**Bearer Token:** `sk_opena5_vsc_12350_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- GitHub Copilot chat extension
- Code context awareness
- Inline suggestions
- Multi-file analysis

---

#### opena6-browser (Port 12351)

**Rolle:** Web Browser Control
**Bearer Token:** `sk_opena6_brow_12351_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Selenium/Playwright integration
- Page navigation
- Screenshot capture
- Form automation

---

#### opena7-email (Port 12352)

**Rolle:** Email Client Interface
**Bearer Token:** `sk_opena7_mail_12352_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- IMAP/SMTP support
- Email parsing
- Attachment handling
- Draft composition

---

#### opena8-whatsapp (Port 12353)

**Rolle:** WhatsApp Business API
**Bearer Token:** `sk_opena8_what_12353_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Message sending
- Group management
- Template messages
- Media support

---

#### opena9-call (Port 12354)

**Rolle:** VoIP & Phone Integration
**Bearer Token:** `sk_opena9_call_12354_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Incoming call handling
- DTMF tone recognition
- Call recording
- Voice transcription

---

#### opena10-answer (Port 12355)

**Rolle:** IVR System (Interactive Voice Response)
**Bearer Token:** `sk_opena10_answ_12355_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Menu trees
- Voice prompts
- Call routing
- Call logging

---

#### opena11-unlock (Port 12356)

**Rolle:** Authentication & Access Control
**Bearer Token:** `sk_opena11_lock_12356_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- 2FA verification
- Token validation
- Permission checking
- Session management

---

#### opena12-social (Port 12357)

**Rolle:** Social Media Integration (Generic)
**Bearer Token:** `sk_opena12_soc_12357_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Tweet/Post publishing
- Timeline fetching
- Engagement tracking
- Multi-platform support

---

#### opena13-influencer (Port 12358)

**Rolle:** Influencer Network Management
**Bearer Token:** `sk_opena13_infl_12358_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Influencer discovery
- Campaign management
- Performance analytics
- Contract tracking

---

#### opena14-calendar (Port 12359)

**Rolle:** Calendar & Scheduling
**Bearer Token:** `sk_opena14_cal_12359_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Event creation/deletion
- Meeting scheduling
- Reminder management
- Integration with Outlook/Google Calendar

---

#### opena15-html (Port 12360)

**Rolle:** HTML/CSS Generator
**Bearer Token:** `sk_opena15_html_12360_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Dynamic HTML generation
- CSS styling
- Component templates
- Responsive design

---

#### opena16-shop (Port 12361)

**Rolle:** E-Commerce Integration
**Bearer Token:** `sk_opena16_shop_12361_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Product management
- Shopping cart
- Payment processing
- Order tracking

---

#### opena17-homepage (Port 12362)

**Rolle:** Website Builder
**Bearer Token:** `sk_opena17_home_12362_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Page creation
- Drag-and-drop editing
- SEO optimization
- Analytics integration

---

#### opena18-archive (Port 12363)

**Rolle:** Local Archive Management
**Bearer Token:** `sk_opena18_arch_12363_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Document indexing
- Full-text search
- Version control
- Backup/restore

---

#### opena19-trading (Port 12364)

**Rolle:** Financial Trading Bot
**Bearer Token:** `sk_opena19_trade_12364_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Market data fetching
- Technical analysis
- Trade execution
- Portfolio tracking

---

#### opena20-dashboard (Port 12365)

**Rolle:** Central Monitoring Dashboard
**Bearer Token:** `sk_opena20_dash_12365_strict_v1`
**Status:** 🚀 Ready for Deployment

**Functionality:**

- Real-time metrics
- Agent health monitoring
- Performance graphs
- Alert management

---

## SICHERHEITSMODELL

### 3.1 PHASE 15.4: Strict Policy Enforcement

#### Bearer Token System

**Token Format:** `sk_<agent>_<function>_<port>_strict_v1`

```python
VALID_BEARER_TOKENS = {
    "opena1-coordinator": "sk_opena1_coord_12344_strict_v1",
    "opena2-archivator": "sk_opena2_arch_12345_strict_v1",
    "opena3-webui": "sk_opena3_web_12347_strict_v1",
    "opena4-telegram": "sk_opena4_tele_12348_strict_v1",
    # ... (18 more agents)
    "opena20-dashboard": "sk_opena20_dash_12365_strict_v1",
    "test-harness": "sk_test_harness_phase15_strict_v1",
}
```

#### Authentication Flow

```
1. Client sends request with Authorization header:
   Authorization: Bearer sk_opena1_coord_12344_strict_v1

2. Server validates token:
   ├─ Check header existence → 401 if missing
   ├─ Verify "Bearer " prefix → 401 if invalid format
   ├─ Lookup token in VALID_BEARER_TOKENS → 401 if not found
   └─ Extract client_id → Return to endpoint

3. Endpoint receives client_id:
   ├─ Includes in CMD safepoint (src: client_id)
   ├─ Includes in RESP safepoint (dst: client_id)
   └─ Response metadata shows auth_verified: true
```

#### Security Events

Logged in SECURITY_EVENT safepoints:

```json
{
  "timestamp": "2025-11-24T13:25:00Z",
  "kind": "SECURITY_EVENT",
  "event_type": "auth_invalid",
  "details": "Invalid bearer token provided",
  "attempted_token": "sk_invalid_xxx",
  "source_ip": "127.0.0.1",
  "attempted_endpoint": "/request"
}
```

### 3.2 Authorization Tiers (Future: PHASE 16)

```
Tier 1: PUBLIC
├─ /health (no auth required)
├─ /status (no auth required)
└─ /docs (no auth required)

Tier 2: AGENT
├─ /request (bearer token required)
├─ /log/* (bearer token required)
└─ /safepoint (bearer token required)

Tier 3: ADMIN
├─ /config/* (bearer token + admin role required)
├─ /agents/* (bearer token + admin role required)
└─ /cleanup (bearer token + admin role required)
```

### 3.3 Data Protection

```
✅ Transport Security:
  ├─ HTTPS enforced for production
  ├─ TLS 1.3 minimum
  └─ Certificate pinning (future)

✅ At-Rest Security:
  ├─ Safepoints stored with client_id
  ├─ Sensitive data encrypted (future)
  ├─ Access logs maintained
  └─ Audit trail immutable

✅ In-Process Security:
  ├─ Bearer token never logged in plain
  ├─ Request context isolated
  ├─ Memory cleared after processing
  └─ Timing attack resistant
```

---

## API-DOKUMENTATION

### 4.1 POST /request (opena1 - Port 12344)

**Authentication:** Bearer Token (Required)
**Policy:** Strict

**Request Format:**

```json
{
  "source": "string",
  "user_query": "string",
  "context": {
    "session_id": "string",
    "previous_messages": ["string"],
    "metadata": {}
  }
}
```

**Response Format (Success - 200):**

```json
{
  "request_id": "uuid-string",
  "status": "success",
  "response": "AI response text...",
  "metadata": {
    "source": "opena1",
    "timestamp": "2025-11-24T13:25:00Z",
    "source_origin": "opena1-coordinator",
    "safepoint_logged": true,
    "policy": "strict",
    "auth_verified": true
  }
}
```

**Response Format (Error - 401):**

```json
{
  "detail": "Missing Authorization header | Invalid bearer token | Malformed Authorization format"
}
```

**Example cURL:**

```bash
curl -X POST http://127.0.0.1:12344/request \
  -H "Authorization: Bearer sk_opena1_coord_12344_strict_v1" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "opena1",
    "user_query": "What is PHASE 15.4?",
    "context": {"session_id": "abc123"}
  }'
```

### 4.2 GET /health (opena1 - Port 12344)

**Authentication:** None (Diagnostic)
**Policy:** Public

**Response Format:**

```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "version": "2.0",
  "agents_online": 20,
  "safepoints_logged": 150
}
```

### 4.3 GET /log/opena1

**Authentication:** Bearer Token (Required)
**Policy:** Strict

**Response Format:**

```json
{
  "client_id": "opena1-coordinator",
  "total_safepoints": 150,
  "cmd_safepoints": 50,
  "resp_safepoints": 50,
  "error_safepoints": 20,
  "security_events": 30,
  "latest_safepoint": {
    "timestamp": "2025-11-24T13:25:00Z",
    "kind": "RESP",
    "client_id": "opena4-telegram"
  }
}
```

---

## DEPLOYMENT-RICHTLINIEN

### 5.1 Voraussetzungen

- **Python:** 3.10+ (erforderlich)
- **Docker:** 20.10+ (empfohlen für Production)
- **Ports:** 12344-12365 (20 Agents)
- **Speicher:** ≥8GB RAM
- **Disk:** ≥10GB für Safepoints & Archive
- **Network:** Private network oder VPN (recommended)

### 5.2 Deployment Varianten

#### Variante A: Docker Compose (Empfohlen)

```bash
cd LocalAgent-Pro
docker-compose up -d

# Verify
curl http://127.0.0.1:12344/health
curl http://127.0.0.1:12345/stats
```

#### Variante B: Systemd Services

```bash
# Create service file for each agent
sudo cp /tmp/opena1.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start opena1
sudo systemctl enable opena1

# Verify
systemctl status opena*
```

#### Variante C: Manual (Development)

```bash
# Terminal 1: opena1-coordinator
cd LocalAgent-Pro/opena1
python3 main.py

# Terminal 2: opena2-archivator
cd LocalAgent-Pro/opena2
python3 main.py

# Terminal 3+: Other agents (opena3-opena20)
cd LocalAgent-Pro/opena3
python3 main.py
# ... repeat for each
```

### 5.3 Health Checks

```bash
# All agents
for port in {12344..12365}; do
  curl -s http://127.0.0.1:$port/health | jq .
done

# Specific agent
curl http://127.0.0.1:12344/health | jq .status

# Full system status
curl http://127.0.0.1:12344/status | jq .
```

---

## INTEGRATION LocalAgent-Pro

### 6.1 Verzeichnisstruktur

```
/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/
├── LocalAgent-Pro/                          # Main project directory
│   ├── docker-compose.yml                   # Multi-agent orchestration
│   ├── Dockerfile                           # Agent container template
│   ├── opena1/                              # Coordinator service
│   │   ├── main.py                          # FastAPI server
│   │   ├── requirements.txt                 # Dependencies
│   │   └── config.json                      # Configuration
│   ├── opena2/                              # Archivator service
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── archiv/                          # Safepoint storage
│   ├── opena3/ through opena20/             # Specialized agents
│   │   ├── main.py                          # Agent-specific logic
│   │   ├── requirements.txt
│   │   └── integrations/                    # Third-party APIs
│   ├── shared/                              # Shared libraries
│   │   ├── auth.py                          # Bearer token validation
│   │   ├── safepoint.py                     # Safepoint logging
│   │   ├── models.py                        # Pydantic models
│   │   └── utils.py                         # Helper functions
│   ├── tests/                               # Test suite
│   │   ├── test_auth.py
│   │   ├── test_safepoint.py
│   │   └── test_integration.py
│   ├── docs/                                # Documentation
│   │   ├── API.md                           # API reference
│   │   ├── DEPLOYMENT.md                    # Deployment guide
│   │   └── SECURITY.md                      # Security guidelines
│   └── README.md                            # Main documentation
│
├── MASTER_PROMPT_FINAL_EDITION.md           # This file
├── PHASE_15_4_POLICY_HARDENING_REPORT.md   # Policy implementation report
└── ROOT_README.md                           # Project overview
```

### 6.2 Configuration Files

#### opena1/config.json

```json
{
  "service_name": "opena1-coordinator",
  "port": 12344,
  "bearer_token": "sk_opena1_coord_12344_strict_v1",
  "environment": "production",
  "logging_level": "INFO",
  "safepoint_enabled": true,
  "security_event_logging": true
}
```

#### opena2/config.json

```json
{
  "service_name": "opena2-archivator",
  "port": 12345,
  "bearer_token": "sk_opena2_arch_12345_strict_v1",
  "archiv_path": "/localagent_archive/safepoints",
  "max_safepoint_size": 10485760,
  "retention_days": 90
}
```

### 6.3 Bearer Token Configuration (All Services)

```python
# shared/auth.py

VALID_BEARER_TOKENS = {
    # Core Services
    "opena1-coordinator": "sk_opena1_coord_12344_strict_v1",
    "opena2-archivator": "sk_opena2_arch_12345_strict_v1",

    # Interface Agents
    "opena3-webui": "sk_opena3_web_12347_strict_v1",
    "opena4-telegram": "sk_opena4_tele_12348_strict_v1",
    "opena5-vscode": "sk_opena5_vsc_12350_strict_v1",
    "opena6-browser": "sk_opena6_brow_12351_strict_v1",
    "opena7-email": "sk_opena7_mail_12352_strict_v1",
    "opena8-whatsapp": "sk_opena8_what_12353_strict_v1",
    "opena9-call": "sk_opena9_call_12354_strict_v1",
    "opena10-answer": "sk_opena10_answ_12355_strict_v1",
    "opena11-unlock": "sk_opena11_lock_12356_strict_v1",
    "opena12-social": "sk_opena12_soc_12357_strict_v1",
    "opena13-influencer": "sk_opena13_infl_12358_strict_v1",
    "opena14-calendar": "sk_opena14_cal_12359_strict_v1",
    "opena15-html": "sk_opena15_html_12360_strict_v1",
    "opena16-shop": "sk_opena16_shop_12361_strict_v1",
    "opena17-homepage": "sk_opena17_home_12362_strict_v1",
    "opena18-archive": "sk_opena18_arch_12363_strict_v1",
    "opena19-trading": "sk_opena19_trade_12364_strict_v1",
    "opena20-dashboard": "sk_opena20_dash_12365_strict_v1",

    # Testing
    "test-harness": "sk_test_harness_phase15_strict_v1",
}

TOKEN_TO_CLIENT = {v: k for k, v in VALID_BEARER_TOKENS.items()}
```

---

## TROUBLESHOOTING & OPERATIONS

### 7.1 Common Issues

#### Problem: Agent not responding (Connection refused)

```bash
# Check if service is running
ps aux | grep "python3 main.py" | grep -v grep

# Check port binding
sudo netstat -tlnp | grep 1234

# Restart agent
systemctl restart opena1

# Check logs
tail -f /var/log/localagent/opena1.log
```

#### Problem: Bearer token validation failing

```bash
# Verify token format
grep "sk_opena1_" /etc/localagent/tokens.txt

# Check header format
curl -v -X POST http://127.0.0.1:12344/request \
  -H "Authorization: Bearer sk_opena1_coord_12344_strict_v1"

# Look for "Invalid bearer token" in response
```

#### Problem: Safepoints not being logged

```bash
# Check archiv directory
ls -lah /localagent_archive/safepoints/

# Verify archivator service
ps aux | grep opena2

# Check disk space
df -h /localagent_archive/

# Check permissions
ls -la /localagent_archive/ | grep danijel-jd
```

### 7.2 Monitoring Commands

```bash
# Real-time agent status
watch -n 5 'curl -s http://127.0.0.1:12344/status | jq .'

# Safepoint count
curl http://127.0.0.1:12345/stats | jq .total_safepoints

# Security events
curl http://127.0.0.1:12344/log/opena1 | jq .security_events

# Performance metrics
curl http://127.0.0.1:12344/metrics | jq '.request_latency_ms | {min, max, avg}'
```

### 7.3 Maintenance Tasks

#### Daily

- Monitor error logs: `grep ERROR /var/log/localagent/*.log`
- Verify all agents online: Check `/health` endpoints
- Disk space check: `df -h /localagent_archive/`

#### Weekly

- Backup safepoints: `tar -czf safepoints_backup_$(date +%Y%m%d).tar.gz /localagent_archive/`
- Review security events: `curl .../log/opena1 | jq .security_events`
- Performance analysis: `curl .../metrics`

#### Monthly

- Cleanup old safepoints (>90 days): Automated by archivp
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Security audit: Review bearer token usage patterns

---

## 🎯 SUCCESS CRITERIA - PHASE 15.5 (Next Phase)

✅ **Deployment Complete:**

- [ ] All 20 agents deployed and responding
- [ ] Each agent has bearer token authentication working
- [ ] Client IDs properly tracked in safepoints
- [ ] Inter-agent communication via gateway operational

✅ **Testing Complete:**

- [ ] End-to-end tests (user → gateway → archivator → agent → response)
- [ ] Security tests (401 errors for invalid tokens)
- [ ] Performance tests (<100ms latency maintained)
- [ ] Load tests (100+ concurrent requests)

✅ **Monitoring Active:**

- [ ] Prometheus metrics for all agents
- [ ] Grafana dashboard showing real-time status
- [ ] Alert rules for failures & anomalies
- [ ] Safepoint archival verified

✅ **Documentation Complete:**

- [ ] Each agent has README
- [ ] API documentation updated for all endpoints
- [ ] Deployment checklist completed
- [ ] Runbook for common operations

---

## 📞 SUPPORT & MAINTENANCE

**Contact:** Danijel Jokic
**Email:** jokicdanijel@protonmail.com
**GitHub:** https://github.com/jokicdanijel/Lokales-Agententool
**Repository:** Gesamtprojekt-start (main branch)

**Emergency:**

- Service down: Restart with `systemctl restart opena1 opena2 opena3` (all services)
- Data loss: Restore from safepoint backup
- Security breach: Rotate all bearer tokens immediately

---

## 📜 DOKUMENTVERSION

| Version | Datum      | Status     | Änderungen                                             |
| ------- | ---------- | ---------- | ------------------------------------------------------ |
| 2.0     | 24.11.2025 | Production | Bearer token impl., 20 agents spec., integration guide |
| 1.5     | 23.11.2025 | Review     | PHASE 15.4 policy hardening                            |
| 1.0     | 20.11.2025 | Draft      | Initial system architecture                            |

---

**🚀 MASTER PROMPT - FINAL EDITION - READY FOR DEPLOYMENT**

**Next Action:** Deploy opena4-opena20 services (PHASE 15.5)
**Repository:** git branch `masterprompt-v1` (ready to merge)
