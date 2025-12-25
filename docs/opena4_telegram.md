# 🤖 opena4 – Telegram Multi-Bot Orchestrator

**API Docs:** https://hyperdashboard-one.de/opena4/docs**External URL:** https://hyperdashboard-one.de/opena4 **Documentation:** [opena4_telegram.md](./opena4_telegram.md) 5. ✅ Set up monitoring4. ✅ Configure webhooks for Telegram3. ✅ Test external URL2. ✅ Set up SSL certificate1. ✅ Configure Nginx (see above)**Next Steps:**---`docker compose down# Stopdocker compose up -ddocker compose pull# Updatedocker compose logs -f api# Logscurl https://hyperdashboard-one.de/opena4/health | jq .# Verifydocker compose -f docker-compose.yml -f docker-compose.prod.yml up -dcd /opt/hyperdashboard-one/telegram_multi# Deploy`bash## 🚀 Production Commands---- [ ] Tracing aktiviert (optional)- [ ] Logs monitoriert- [ ] Test-Message zum Bot gesendet- [ ] Test-Workflow erstellt & funktioniert- [ ] Webhooks konfiguriert in Telegram- [ ] Health Check erfolgreich: `curl https://hyperdashboard-one.de/opena4/health`- [ ] opena4 Service läuft (`docker compose ps`)- [ ] Nginx Reverse Proxy konfiguriert- [ ] SSL Certificate aktiv und gültig- [ ] `.env` konfiguriert mit Secrets## 📝 Deployment Checklist---| **Slow response times** | Monitor: `curl https://hyperdashboard-one.de/opena4/metrics` || **Workflows not triggering** | Checke Telegram webhook status in Telegram Bot API || **Webhook returns 404** | Überprüfe bot_key in URL vs. DB || **HTTPS Certificate Error** | Erneuere: `sudo certbot renew --force-renewal` || **502 Bad Gateway** | Überprüfe: `curl http://127.0.0.1:12348/health` ||---------|----------|| Problem | Solution |## 🆘 Troubleshooting---``` EOF docker compose exec -T api pytest tests/ docker compose up -d docker pull ${{ secrets.REGISTRY }}/opena4:latest          cd /opt/hyperdashboard-one          ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} << 'EOF' run: | - name: Deploy to server docker push ${{ secrets.REGISTRY }}/opena4:latest docker tag opena4:latest ${{ secrets.REGISTRY }}/opena4:latest docker login -u ${{ secrets.DOCKER_USER }} -p ${{ secrets.DOCKER_TOKEN }} run: | - name: Push to registry docker build -t opena4:latest . cd telegram_multi run: | - name: Build Docker image - uses: actions/checkout@v3 steps: runs-on: ubuntu-latest deploy:jobs: - 'telegram_multi/**' paths: branches: [main] push:on:name: Deploy opena4`yaml### GitHub Actions Example## 🔄 CI/CD Deployment Pipeline---`Endpoint contains "/workflows" or "/telegram/webhook"Service = "telegram_multi"``Query:Traces accessible at: http://localhost:3000 (Grafana Tempo)### 3. OpenTelemetry Tracing  - `webhook_deliveries_total` (Telegram updates received)  - `api_response_time_ms` (response time)  - `workflows_triggered_total` (workflows executed)  - `telegram_messages_total` (total messages processed)- **Metrics:**- **Data Source:** PrometheusImport or create dashboard:### 2. Grafana Dashboard`` - targets: ['https://hyperdashboard-one.de:9090/metrics'] static_configs:- job_name: 'opena4'# Add to Prometheus scrape_configs`yaml### 1. Prometheus Metrics## 📊 Production Monitoring---`docker logs telegram_multi-api-1 -fssh user@hyperdashboard-one.de# SSH into server and checksudo journalctl -u docker -f# Production systemddocker compose logs -f api# Local logs`bash### 4. Monitor Logs- Expect: "✅ Workflow working from production!"- Send: "hello"- Open [@browser_opena6_bot](https://t.me/browser_opena6_bot)### 3. Send Test Message to Telegram` }' "enabled": true "action": {"response": "✅ Workflow working from production!"}, "trigger": {"keywords": ["test", "hello"]}, "type": "auto_reply", "name": "Test Workflow", "bot_key": "browser_opena6_bot", -d '{ -H "Content-Type: application/json" \ -H "Authorization: Bearer YOUR_TOKEN" \curl -X POST https://hyperdashboard-one.de/opena4/workflows \```bash### 2. Create Test Workflow```curl https://hyperdashboard-one.de/opena4/health# Productioncurl http://127.0.0.1:12348/health# Local```bash### 1. Health Check## 🧪 Testing & Verification---```docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d```bashStart mit:```    restart: always  redis:        restart: always  postgres:        restart: always      - OTEL_ENABLED=true      - WEBHOOK_BASE_URL=https://hyperdashboard-one.de      - OPENA4_EXTERNAL_URL=https://hyperdashboard-one.de/opena4    environment:  api:services:version: '3.8'```yamlErstelle `telegram_multi/docker-compose.prod.yml`:### 2. Docker Compose Override (for production)```OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318OTEL_ENABLED=true# OpenTelemetryREDIS_URL=redis://localhost:6379/0# RedisDATABASE_URL=postgresql://telegram_user:telegram_pass@localhost:5432/telegram_multi_db# DatabaseWEBHOOK_SECRET=<strong-webhook-secret>ADMIN_KEY=<strong-secret-key># Admin SecurityWEBHOOK_BASE_URL=https://hyperdashboard-one.deOPENA4_EXTERNAL_URL=https://hyperdashboard-one.de/opena4# External URLsOPENA4_HOST=127.0.0.1OPENA4_PORT=12348# opena4 Configuration```bash### 1. Environment Variables (.env)## 🔐 Security Configuration---```}  ]    }      "webhook_url": "https://hyperdashboard-one.de/telegram/webhook/open2tele_bot"      "status": "ok",      "bot_key": "open2tele_bot",    {    },      "webhook_url": "https://hyperdashboard-one.de/telegram/webhook/browser_opena6_bot"      "status": "ok",      "bot_key": "browser_opena6_bot",    {  "webhooks_set": [{# Expected response  }'    "webhook_base_url": "https://hyperdashboard-one.de"  -d '{  -H "Content-Type: application/json" \  -H "X-Admin-Key: YOUR_ADMIN_KEY" \curl -X POST https://hyperdashboard-one.de/opena4/admin/set-webhooks \# Via opena4 Admin API```bashNach dem Deployment die Webhooks aktualisieren:## 📋 Webhook Configuration for Telegram---```curl https://hyperdashboard-one.de/opena4/workflows | jq .# Test Workflow Listopen https://hyperdashboard-one.de/opena4/docs# Test Swagger UI{"status": "ok", "service": "telegram_multi", "port": 12348}# Expected responsecurl -X GET https://hyperdashboard-one.de/opena4/health# Test from local machine```bash### 3. Verify Deployment```sudo systemctl reload nginx# Reload Nginx           /etc/nginx/sites-enabled/hyperdashboard-one.desudo ln -s /etc/nginx/sites-available/hyperdashboard-one.de \# Enable sitesudo nginx -t# Test Nginx configsudo certbot certonly --webroot -w /var/www/html -d hyperdashboard-one.de# Obtain SSL certificate (if not exists)```bash### 2. SSL Certificate Setup```}    return 301 https://$server_name$request_uri;    server_name hyperdashboard-one.de;    listen 80;server {# Redirect HTTP to HTTPS}    }        proxy_set_header X-Forwarded-Proto $scheme;        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;        proxy_set_header X-Real-IP $remote_addr;        proxy_set_header Host $host;        proxy_http_version 1.1;        proxy_pass http://opena4/telegram/webhook/;    location /telegram/webhook/ {    # Telegram Webhook Endpoint        }        proxy_set_header X-Forwarded-Proto $scheme;        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;        proxy_set_header X-Real-IP $remote_addr;        proxy_set_header Host $host;        proxy_http_version 1.1;        proxy_pass http://opena4/;    location /opena4/api/ {    # API directly under /opena4/api/*        }        proxy_send_timeout 86400;        proxy_read_timeout 86400;        # WebSocket support (for future real-time features)                proxy_set_header X-Forwarded-Proto $scheme;        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;        proxy_set_header X-Real-IP $remote_addr;        proxy_set_header Host $host;        proxy_set_header Connection "upgrade";        proxy_set_header Upgrade $http_upgrade;        proxy_http_version 1.1;        proxy_pass http://opena4/;    location /opena4/ {    # opena4 – Telegram Multi-Bot Orchestrator        ssl_prefer_server_ciphers on;    ssl_ciphers HIGH:!aNULL:!MD5;    ssl_protocols TLSv1.2 TLSv1.3;        ssl_certificate_key /etc/letsencrypt/live/hyperdashboard-one.de/privkey.pem;    ssl_certificate /etc/letsencrypt/live/hyperdashboard-one.de/fullchain.pem;        server_name hyperdashboard-one.de;    listen 443 ssl http2;server {}    server 127.0.0.1:12348;upstream opena4 {```nginxErstelle/Aktualisiere `/etc/nginx/sites-available/hyperdashboard-one.de`:### 1. Nginx Reverse Proxy Configuration## 🚀 Deployment Steps---**Full URL:** https://hyperdashboard-one.de/opena4**External Path:** /opena4 **Local Port:** 12348 **Service:** Telegram Multi-Bot Orchestrator (opena4) **Status:** Ready for Deployment **Service:** Telegram Multi-Bot Management
**Port:** 12348
**External URL:** https://hyperdashboard-one.de/opena4
**Status:\*\* ✅ Operational

---

## Overview

opena4 ist der **Telegram Multi-Bot Orchestrator** des ELION Hyper-Dashboard. Es verwaltet mehrere Telegram-Bots, deren Webhooks, Chat-Historie und wendet Workflows darauf an.

### Access

| Zugriffsart          | URL                                                    | Status        |
| -------------------- | ------------------------------------------------------ | ------------- |
| **Lokal (API)**      | http://127.0.0.1:12348                                 | ✅ Production |
| **Swagger Docs**     | http://127.0.0.1:12348/docs                            | ✅ Available  |
| **External (Proxy)** | https://hyperdashboard-one.de/opena4                   | ✅ Configured |
| **Workflows UI**     | file:///$(pwd)/telegram_multi/ui_opena4_workflows.html | 🖥️ Local      |

### Kernfunktionen

| Feature                   | Status | Beschreibung                           |
| ------------------------- | ------ | -------------------------------------- |
| **Bot Management**        | ✅     | Add/edit/delete Telegram bots          |
| **Webhook Handler**       | ✅     | Receive & deduplicate Telegram updates |
| **Chat History**          | ✅     | SQLite/PostgreSQL storage              |
| **Workflows**             | ✅     | Rule-based message processing          |
| **OpenTelemetry Tracing** | ✅     | Distributed trace collection           |
| **Admin API**             | ✅     | Register bots, configure webhooks      |

---

## Architecture

```
┌─────────────────────────────────────┐
│  Telegram Bot (@BotFather)          │
│  Token: 8521041310:AAGAQpvjUH-...   │
└──────────────┬──────────────────────┘
               │
         HTTPS (webhook)
               │
      ┌────────▼────────┐
      │  opena4:12348   │
      │  FastAPI        │
      ├─────────────────┤
      │ POST /telegram/ │
      │ webhook/{key}   │
      └────────┬────────┘
               │
        ┌──────┼──────┐
        │      │      │
    ┌───▼──┐ ┌─▼──┬──▼──┐
    │Redis │ │PgSQL Workflows
    └──────┘ └─────┴──────┘
```

---

## Workflows

### Workflow System

Jeder registrierte Bot kann ein oder mehrere **Workflows** haben. Workflows sind Regeln, die:

1. **Inbound-Nachrichten** (von Telegram) prüfen
2. **Bedingungen** anwenden (z.B. Keywords, Sender, Time)
3. **Aktionen** ausführen (z.B. Antwort senden, Log, Forward)

### Workflow Types

#### 1. **Auto-Reply Workflow**

```json
{
  "bot_key": "browser_opena6_bot",
  "name": "Auto-Reply Demo",
  "type": "auto_reply",
  "trigger": {
    "keywords": ["hello", "hi", "hola"],
    "case_sensitive": false
  },
  "action": {
    "response": "👋 Hello! Thanks for reaching out. How can I help?"
  },
  "enabled": true
}
```

#### 2. **Forward Workflow**

```json
{
  "bot_key": "open2tele_bot",
  "name": "Forward to Support",
  "type": "forward",
  "trigger": {
    "keywords": ["support", "help", "issue"]
  },
  "action": {
    "forward_to_chat_id": 123456789,
    "include_original": true
  },
  "enabled": true
}
```

#### 3. **Webhook Workflow** (Chaining)

```json
{
  "bot_key": "browser_opena6_bot",
  "name": "Send to AI Service",
  "type": "webhook",
  "trigger": {
    "keywords": ["ask", "tell"],
    "min_words": 3
  },
  "action": {
    "webhook_url": "http://127.0.0.1:12344/log/opena1",
    "method": "POST",
    "body_template": {
      "request_id": "$message_id",
      "user_query": "$message_text",
      "source": "opena4_telegram"
    }
  },
  "enabled": true
}
```

#### 4. **Scheduled Workflow**

```json
{
  "bot_key": "browser_opena6_bot",
  "name": "Daily Reminder",
  "type": "scheduled",
  "trigger": {
    "schedule": "0 09 * * *", // 9 AM every day (cron)
    "chat_ids": [123456789]
  },
  "action": {
    "message": "📌 Daily reminder: Check your tasks!"
  },
  "enabled": true
}
```

---

## API Endpoints

### Admin API

#### 1. **Register Bot**

```bash
POST /admin/register-bot?bot_key=browser_bot&token=TOKEN

# Response
{"bot_id": 1, "bot_key": "browser_bot", "status": "registered"}
```

#### 2. **Set Webhooks**

```bash
POST /admin/set-webhooks?webhook_base_url=https://api.your-domain.com

# Response
{
  "webhooks_set": [
    {"bot_key": "browser_bot", "status": "ok", "webhook_url": "..."},
    {"bot_key": "open2tele_bot", "status": "ok", "webhook_url": "..."}
  ]
}
```

#### 3. **Create Workflow**

```bash
POST /workflows

{
  "bot_key": "browser_opena6_bot",
  "name": "Auto-Reply",
  "type": "auto_reply",
  "trigger": {"keywords": ["hello"]},
  "action": {"response": "Hi there!"},
  "enabled": true
}

# Response
{"workflow_id": 1, "status": "created"}
```

#### 4. **List Workflows**

```bash
GET /workflows?bot_key=browser_opena6_bot

# Response
[
  {"workflow_id": 1, "bot_key": "browser_opena6_bot", "name": "Auto-Reply", "enabled": true},
  {"workflow_id": 2, "bot_key": "browser_opena6_bot", "name": "Forward", "enabled": false}
]
```

#### 5. **Update Workflow**

```bash
PUT /workflows/1

{
  "enabled": false,
  "action": {"response": "Updated response"}
}

# Response
{"workflow_id": 1, "status": "updated"}
```

#### 6. **Delete Workflow**

```bash
DELETE /workflows/1

# Response
{"status": "deleted"}
```

### Webhook Endpoint

#### Telegram Update Handler

```bash
POST /telegram/webhook/browser_opena6_bot

# Telegram sends:
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {"id": 987654321, "first_name": "User"},
    "chat": {"id": 987654321, "type": "private"},
    "date": 1234567890,
    "text": "hello world"
  }
}

# Response
{"status": "ok", "workflows_triggered": 2}
```

---

## Configuration

### .env Variables

```bash
# Telegram Bot Tokens (JSON mapping)
BOT_TOKENS_MAPPING='{"browser_opena6_bot": "8521041310:AAGAQpvjUH-...", "open2tele_bot": "8559430186:AAHvPZMA2TTBT8-..."}'

# Admin Security
ADMIN_KEY=admin-secret-key-12345

# Webhook
WEBHOOK_SECRET=webhook-secret-key

# Database
DATABASE_URL=postgresql://telegram_user:telegram_pass@localhost:5432/telegram_multi_db

# Redis (for job queue)
REDIS_URL=redis://localhost:6379/0

# OpenTelemetry
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
OTEL_SERVICE_NAME=telegram_multi
```

---

## Quick Start

### 1. Start Services

```bash
cd telegram_multi
docker compose up -d
```

### 2. Register Bots

```bash
bash ../scripts/register_bots.sh https://api.hyperdashboard-one.de
```

### 3. Create a Workflow

```bash
curl -X POST http://127.0.0.1:12348/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "bot_key": "browser_opena6_bot",
    "name": "Auto-Reply",
    "type": "auto_reply",
    "trigger": {"keywords": ["hello"]},
    "action": {"response": "👋 Hello! How can I help?"},
    "enabled": true
  }'
```

### 4. Send Test Message

- Open Telegram: [@browser_opena6_bot](https://t.me/browser_opena6_bot)
- Send: "hello"
- Expect: Auto-reply response

### 5. View Workflows

```bash
curl http://127.0.0.1:12348/workflows?bot_key=browser_opena6_bot | jq .
```

---

## Monitoring & Debugging

### Health Check

```bash
curl http://127.0.0.1:12348/health | jq .
```

### View Logs

```bash
docker compose logs -f api
```

### Database Queries

```bash
# List all bots
docker compose exec postgres psql -U telegram_user -d telegram_multi_db -c "SELECT * FROM bots;"

# List all workflows
docker compose exec postgres psql -U telegram_user -d telegram_multi_db -c "SELECT * FROM workflows;"

# List recent messages
docker compose exec postgres psql -U telegram_user -d telegram_multi_db -c "SELECT * FROM updates ORDER BY created_at DESC LIMIT 10;"
```

### Tracing

```bash
# Check if tracing is enabled
python3 check_tracing.py

# Access Grafana (if OTLP running)
# http://localhost:3000
# Query: Service="telegram_multi" in Tempo datasource
```

---

## Workflow Examples

### Example 1: Customer Support Bot

```json
{
  "bot_key": "support_bot",
  "workflows": [
    {
      "name": "Greeting",
      "type": "auto_reply",
      "trigger": { "keywords": ["hi", "hello"] },
      "action": { "response": "👋 Welcome to Support! How can I help?" }
    },
    {
      "name": "Escalate to Agent",
      "type": "forward",
      "trigger": { "keywords": ["agent", "human", "speak to someone"] },
      "action": { "forward_to_chat_id": 123456789 }
    },
    {
      "name": "Send to AI",
      "type": "webhook",
      "trigger": { "keywords": ["question", "issue"] },
      "action": {
        "webhook_url": "http://127.0.0.1:12344/log/opena1",
        "body_template": { "user_query": "$message_text" }
      }
    }
  ]
}
```

### Example 2: Notification Bot

```json
{
  "bot_key": "notifications_bot",
  "workflows": [
    {
      "name": "Daily Report",
      "type": "scheduled",
      "trigger": { "schedule": "0 08 * * *", "chat_ids": [111, 222, 333] },
      "action": { "message": "📊 Daily Report:\n- Tasks: 5\n- Completed: 3" }
    }
  ]
}
```

---

## File Structure

```
telegram_multi/
├── app/
│   ├── main.py                  # FastAPI app
│   ├── db/
│   │   ├── models.py            # SQLModel tables (Bot, Chat, Update, Workflow)
│   │   └── session.py           # Database connection
│   ├── admin/
│   │   └── routes.py            # /admin/* endpoints
│   ├── telegram/
│   │   ├── webhooks.py          # Webhook handler
│   │   ├── workflows.py         # Workflow processor
│   │   └── client.py            # Telegram API client
│   └── tracing/
│       └── config.py            # OpenTelemetry setup
├── docker-compose.yml           # Services (API, PostgreSQL, Redis)
├── Dockerfile                   # API & Worker images
└── requirements.txt             # Python dependencies
```

---

## Troubleshooting

| Issue                         | Solution                                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------------------------ |
| **API won't start**           | Check logs: `docker compose logs api`                                                            |
| **Webhooks not working**      | 1. Verify webhook URL in @BotFather 2. Check firewall 3. Ensure HTTPS                            |
| **Workflows not triggering**  | 1. Check if `enabled: true` 2. Test with `/admin/test-workflow` endpoint 3. Check logs           |
| **Database connection error** | Verify DATABASE_URL in .env, check PostgreSQL running                                            |
| **Tracing not collecting**    | 1. Enable `OTEL_ENABLED=true` 2. Start collector: `docker compose -f docker-compose.otel.yml up` |

---

## Next Steps

1. ✅ Services running (telegram_multi:12348)
2. ✅ Bots registered (browser_opena6_bot, open2tele_bot)
3. ⏳ **TODO:** Create & test workflows
4. ⏳ **TODO:** Integrate with opena1 (logging) for AI processing
5. ⏳ **TODO:** Set up scheduler for scheduled workflows

---

**Documentation:** [opena4_workflows.md](./opena4_workflows.md)
**API Docs:** http://127.0.0.1:12348/docs (Swagger UI)
**External URL:** https://hyperdashboard-one.de/opena4
