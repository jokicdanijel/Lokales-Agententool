# opena8 WhatsApp Chatbot Agent

**Port:** 12351  
**Component:** WhatsApp Business API Integration  
**Protocol:** FastAPI + Meta Webhooks + Async HTTPX

---

## Overview

**opena8** is a high-performance WhatsApp automation agent that:
- ✅ Receives inbound messages via Meta Webhook (verified and deduped)
- ✅ Classifies messages (sentiment, urgency, language: DE/EN)
- ✅ Sends outbound text + media messages (image, document, audio, video)
- ✅ Archives all conversations to opena2 (Safepoints)
- ✅ Monitors health via opena1 + opena2 dependencies
- ✅ Exports Prometheus metrics for observability
- ✅ Scales from 0 to 10k+ messages/day

---

## Installation

### Option 1: Local Development (Recommended)

```bash
# 1. Clone/navigate to workspace
cd /path/to/Gesamtprojekt

# 2. Create virtual environment (if needed)
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r 8.opena8_whatsapp/requirements.txt

# 4. Copy config template
cp 8.opena8_whatsapp/.env.example 8.opena8_whatsapp/.env

# 5. Edit .env with Meta credentials
# IMPORTANT: See "Configuration" section below
```

### Option 2: Docker (Production)

```bash
cd 8.opena8_whatsapp
docker-compose up -d
```

### Option 3: systemd (Traditional)

```bash
# Copy to /opt/opena8/
sudo cp -r 8.opena8_whatsapp /opt/
sudo chown -R opena8:opena8 /opt/opena8

# Install service
sudo cp deploy/opena8_whatsapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable opena8_whatsapp
sudo systemctl start opena8_whatsapp
```

---

## Configuration

### Essential Settings (.env)

```env
# Meta API (get from https://developers.facebook.com/)
META_PHONE_NUMBER_ID=123456789012345
META_BUSINESS_ACCOUNT_ID=123456789012345
META_ACCESS_TOKEN=EAAxxxxxxxxxx...YOUR_VERY_LONG_TOKEN
META_WEBHOOK_VERIFY_TOKEN=webhook_secret_at_least_32_chars_long

# Message limits
MESSAGE_MAX_LENGTH=4096  # WhatsApp limit
MEDIA_MAX_SIZE_MB=100

# Feature flags
ENABLE_SENTIMENT=true
ENABLE_CLASSIFICATION=true

# Security
WHATSAPP_ALLOWLIST=+49123456789,+43987654321  # Comma-separated
WHATSAPP_BLOCKLIST=

# Archivator & Coordinator
OPENA2_URL=http://127.0.0.1:12345
OPENA1_URL=http://127.0.0.1:12344
```

### How to Get Meta Credentials

1. **Create Business Account:** https://business.facebook.com
2. **Create App:** App Type = "Business"
3. **Add WhatsApp Product:** Product → WhatsApp Business
4. **Get Phone Number ID:**
   - WhatsApp > API Setup
   - Copy: `Phone Number ID`
5. **Generate Access Token:**
   - Settings → System Users → Create System User
   - Assign Business Admin role
   - Generate Access Token (select "WhatsApp Business Account" app)
   - Token: `EAA...` (typically 300+ characters)
6. **Set Webhook Verify Token:**
   - Use any strong string (32+ chars)
   - Will use to verify incoming webhooks

---

## Quick Start

### 1. Health Check

```bash
curl http://127.0.0.1:12351/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena8",
  "meta_api_connected": true,
  "opena2_connected": true,
  "opena1_connected": true
}
```

### 2. Register with Coordinator

```bash
bash scripts/register_opena8.sh
```

**Output:**
```
✅ opena8 (WhatsApp Agent) registered successfully!
   Route: opena8@12351
   Webhook: /webhook
```

### 3. Receive a Message (via Webhook)

**Meta sends POST to:** `https://your-domain.com/webhook`

**Example webhook payload:**
```json
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "id": "wamid.HBEUxxxxxxxxxxx",
          "from": "49123456789",
          "timestamp": "1699500000",
          "type": "text",
          "text": {"body": "Hello, need help urgently!"}
        }],
        "contacts": [{
          "profile": {"name": "John Doe"}
        }]
      }
    }]
  }]
}
```

**opena8 processes:**
- ✅ Parses message structure
- ✅ Classifies: sentiment=URGENT, urgency=9, language=EN
- ✅ Archives as Safepoint to opena2
- ✅ Returns 200 OK (non-blocking)

### 4. Send a Message

```bash
curl -X POST http://127.0.0.1:12351/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_phone": "+49123456789",
    "message_type": "text",
    "body": "Thanks for reaching out! We received your message."
  }'
```

**Response:**
```json
{
  "success": true,
  "message_id": "wamid.HBEUxxxxxxxxxxx",
  "error": null,
  "sent_at": "2025-11-10T15:30:00Z"
}
```

### 5. Send Media

```bash
curl -X POST http://127.0.0.1:12351/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_phone": "+49123456789",
    "message_type": "image",
    "media_url": "https://example.com/image.jpg",
    "media_type": "image"
  }'
```

---

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (opena2/opena1 status) |
| `/webhook` | GET | Webhook verification (Meta) |
| `/webhook` | POST | Inbound message handler (Meta) |
| `/send` | POST | Send message/media |
| `/run` | POST | Generic action (ingest, send, etc.) |
| `/metrics` | GET | Prometheus metrics |
| `/api/status` | GET | Agent status |
| `/` | GET | API info |

### Message Types

```python
MessageType.TEXT
MessageType.IMAGE
MessageType.DOCUMENT
MessageType.AUDIO
MessageType.VIDEO
MessageType.LOCATION
MessageType.CONTACTS
```

### Sentiment Classification

```python
SentimentType.POSITIVE    # "thank", "excellent", "happy"
SentimentType.NEGATIVE    # "problem", "error", "angry"
SentimentType.URGENT      # "urgent", "critical", "emergency"
SentimentType.NEUTRAL     # default
```

---

## Architecture

### Message Flow

```
Meta Webhook (HTTPS)
    ↓
GET /webhook [verify] → return challenge
    ↓
POST /webhook [handler]
    ├─ Parse entry → WhatsAppMessage
    ├─ Classify (sentiment, language, urgency)
    ├─ Check allowlist/blocklist
    ├─ Background: Archive to opena2 (Safepoint)
    └─ Return 200 OK
```

### Safepoint Structure (Archived to opena2)

```json
{
  "ts": "2025-11-10T15:30:00Z",
  "src": "opena8",
  "dst": "opena2",
  "kind": "MSG",
  "payload": {
    "message_id": "wamid.HBEUxxxxxxxxxxx",
    "phone_number": "+49123456789",
    "name": "John Doe",
    "type": "text",
    "body": "Hello!",
    "sentiment": "positive",
    "urgency": 5,
    "language": "EN"
  }
}
```

---

## Security & Compliance

### Authentication

- **Webhook:** Verified via `hub.verify_token` (GET only)
- **Send Endpoints:** Bearer token (recommended in production)
- **opena1/opena2:** Internal loopback (127.0.0.1 only, no auth required)

### Data Protection

- ✅ **Allowlist/Blocklist:** Filter phone numbers
- ✅ **Media Scanning:** Validate size (default 100MB), MIME type
- ✅ **Audit Trail:** Every message archived to opena2
- ✅ **PII Handling:** Phone numbers + names stored (encrypted in production)
- ✅ **Rate Limiting:** Per-phone number (implement in load balancer)

### Compliance

- ✅ **GDPR:** Audit trail in opena2, retention policy configurable
- ✅ **Meta ToS:** Webhook verification, message type validation
- ✅ **Logging:** Structured JSON logs (JSONL format in production)

---

## Monitoring & Observability

### Health Check

```bash
# Simple
curl http://127.0.0.1:12351/health

# Detailed (with dependencies)
curl http://127.0.0.1:12351/health | jq .
```

### Metrics (Prometheus)

```bash
curl http://127.0.0.1:12351/metrics | grep whatsapp
```

**Exported Metrics:**
- `whatsapp_in_total` — Inbound messages by type
- `whatsapp_out_total` — Outbound messages by type
- `whatsapp_errors_total` — Errors by category (webhook_parse, send_failed, etc.)
- `whatsapp_latency_seconds` — Request latency by endpoint

### Logging

**Log files:**
- `logs/opena8.nohup.log` — stdout/stderr (if started via nohup)
- `logs/opena8/` — Structured logs (if enabled)

**Log levels:** DEBUG, INFO, WARNING, ERROR

```bash
# View logs (tail)
tail -f logs/opena8.nohup.log

# Filter errors
grep "ERROR\|❌" logs/opena8.nohup.log
```

---

## Deployment Patterns

### Development (Single Machine)

```bash
# Terminal 1: Start opena1 + opena2
bin/ops.sh start

# Terminal 2: opena8
cd 8.opena8_whatsapp
source ../../.venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 12351
```

### Production (Docker)

```bash
cd 8.opena8_whatsapp
docker-compose -f docker-compose.yml up -d

# Verify
curl http://localhost:12351/health
```

### Production (Kubernetes)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opena8-whatsapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: opena8
  template:
    metadata:
      labels:
        app: opena8
    spec:
      containers:
      - name: opena8
        image: registry.example.com/opena8:latest
        ports:
        - containerPort: 12351
        env:
        - name: META_ACCESS_TOKEN
          valueFrom:
            secretKeyRef:
              name: meta-secrets
              key: access_token
        livenessProbe:
          httpGet:
            path: /health
            port: 12351
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 12351
          initialDelaySeconds: 5
          periodSeconds: 10
```

---

## Performance & SLOs

### Targets

- **Latency p95:** < 1s (webhook processing)
- **Availability:** 99.9% (3 nines)
- **Error Rate:** < 0.1% (4xx/5xx / total)
- **Throughput:** 10k+ messages/day (1000 msgs/hour peak)

### Bottlenecks

1. **Meta API rate limits:** 80 requests/second per business account
2. **opena2 throughput:** Archive write latency (async, non-blocking)
3. **Database:** Safepoint storage (JSONL append-only, no index required)

---

## Troubleshooting

### Issue: "Meta API not connected"

**Symptom:** Health check shows `meta_api_connected: false`

**Solution:**
```bash
# 1. Verify credentials
grep META_ACCESS_TOKEN 8.opena8_whatsapp/.env

# 2. Check token validity
curl -H "Authorization: Bearer $TOKEN" \
  "https://graph.instagram.com/me?fields=id" | jq .

# 3. If expired, regenerate
# → Facebook Developer Dashboard → Tools → System Users → Regenerate Token
```

### Issue: Webhook not receiving messages

**Symptom:** No messages appear in logs after sending WhatsApp message

**Solution:**
```bash
# 1. Verify webhook URL in Meta dashboard
# → WhatsApp > API Setup > Webhook URL
# URL should be: https://your-domain.com/webhook

# 2. Verify token
# → Verify Token should match META_WEBHOOK_VERIFY_TOKEN

# 3. Test webhook verification
curl "https://your-domain.com/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=<YOUR_TOKEN>"
# Should return: test123

# 4. Check nginx/TLS
curl -v https://your-domain.com/webhook
# Should be: 200 OK (or 400 if no params)
```

### Issue: Messages not archived to opena2

**Symptom:** Safepoints not appearing in opena2 archive

**Solution:**
```bash
# 1. Verify opena2 is running
curl http://127.0.0.1:12345/health

# 2. Check logs
tail -f logs/opena8.nohup.log | grep "Archive"

# 3. Verify opena2 can store
curl -X POST http://127.0.0.1:12345/store/archivp \
  -H "Content-Type: application/json" \
  -d '{
    "ts": "2025-11-10T15:30:00Z",
    "src": "opena8",
    "dst": "test",
    "kind": "TEST",
    "payload": {}
  }'
# Should return: {"written": true, "path": "..."}
```

---

## Best Practices

1. **Never commit .env** → Add to `.gitignore`
2. **Rotate tokens regularly** → Monthly or on suspect access
3. **Use allowlist** → Only accept from trusted phone numbers
4. **Monitor metrics** → Set alerts on error rate > 0.5%
5. **Backup archives** → Daily export from opena2 to cold storage
6. **Rate limiting** → Implement in nginx/load balancer (10 req/min per phone)
7. **Test locally first** → Use Meta's webhook simulator before production
8. **Incident runbook** → Document escalation path (who to call at 3am)

---

## Testing

### Unit Tests

```bash
source .venv/bin/activate
pytest tests/test_whatsapp_service.py -v
```

**Coverage:**
- `TestHealthEndpoints` — Health response structure
- `TestMessageClassifier` — Sentiment, language, allowlist
- `TestMediaHandler` — Size validation, SHA256
- `TestWhatsAppMessage` — Message model creation
- `TestSendMessageRequest` — Request validation
- `TestConfiguration` — Config defaults
- `TestMockWhatsAppClient` — Webhook parsing, mock sends

### Integration Tests

```bash
# 1. Health checks
bash scripts/register_opena8.sh

# 2. Manual webhook test
curl -X POST http://127.0.0.1:12351/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{...}],
          "contacts": [{...}]
        }
      }]
    }]
  }'

# 3. Send test
curl -X POST http://127.0.0.1:12351/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_phone": "+49123456789",
    "message_type": "text",
    "body": "Integration test message"
  }'
```

---

## References

- **Meta Webhook API:** https://developers.facebook.com/docs/whatsapp/webhooks
- **Business Message Types:** https://developers.facebook.com/docs/whatsapp/message-types
- **Rate Limits:** https://developers.facebook.com/docs/whatsapp/api-overview/rate-limits
- **Error Codes:** https://developers.facebook.com/docs/whatsapp/webhooks/errors

---

## Support

For issues, feature requests, or documentation improvements:

1. Check this README's Troubleshooting section
2. Review logs: `tail -f logs/opena8.nohup.log`
3. Open GitHub issue with logs + reproduction steps
4. Contact opena team (opena@example.com)

---

**Last Updated:** 2025-11-10  
**Maintained by:** ELION Team  
**Status:** Production Ready ✅
