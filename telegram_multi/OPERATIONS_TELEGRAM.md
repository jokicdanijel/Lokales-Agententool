# Telegram Multi-Bot – Complete Setup & Operations Guide

## Overview

Telegram Multi-Bot ist ein FastAPI-basiertes System zur Verwaltung mehrerer Telegram-Bots gleichzeitig. Es unterstützt:

- ✅ Multi-Bot Orchestration (mehrere Bots in einer Anwendung)
- ✅ Webhook-basierte Updates (statt Polling)
- ✅ PostgreSQL-Persistierung mit SQLModel
- ✅ Redis Queue für Background Jobs
- ✅ Bearer Token & Webhook Secret Validation
- ✅ OpenTelemetry Tracing (optional)
- ✅ Docker & Docker-Compose ready

---

## Quick Start

### Prerequisites
- Docker & Docker-Compose
- Python 3.11+ (falls lokal laufen soll)
- Telegram Bot Token(s) von [@BotFather](https://t.me/BotFather)

### 1. Konfiguration

Erstelle/aktualisiere `.env` im Projekt-Root:

```env
# Telegram Multi-Bot Config
ADMIN_KEY=admin-secret-key-12345
BEARER_TOKEN=sk-telegram-multi-bearer-token-uuid
WEBHOOK_SECRET=telegram-webhook-secret-token-xyz

# Bot Tokens (JSON format)
BOT_TOKENS_MAPPING={"bot_key_1": "8521041310:AAGAQpvjUH-huQDihQF-...", "bot_key_2": "8559430186:AAHvPZMA2TTBT8-qU5eUMb_..."}

# Optional: OpenTelemetry Tracing
OTEL_ENABLED=false
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
```

### 2. Services Starten

```bash
cd telegram_multi
docker-compose up -d

# Überprüfe Health
curl http://127.0.0.1:8000/health | jq .
```

### 3. Bots Registrieren

```bash
# Vom Projekt-Root
bash scripts/register_bots.sh http://127.0.0.1:8000

# Für Production mit Domain
bash scripts/register_bots.sh https://api.your-domain.com
```

---

## API Endpoints

### Health & Status
```bash
GET /health
GET /
```

### Admin (X-Admin-Key required)
```bash
# Register a bot
POST /admin/register-bot?bot_key={bot_key}&token={token}

# Set webhooks for all bots
POST /admin/set-webhooks?webhook_base_url={base_url}
```

### Webhook (Telegram-only)
```bash
POST /telegram/webhook/{bot_key}
# Telegram sends updates here (from setWebhook)
```

---

## Tracing (OpenTelemetry) 🔧

### Enable Local Tracing

1. **Start Collector:**

```bash
# Option 1: Use provided script
./bin/start_tracing_collector.sh

# Option 2: Manual docker-compose
docker-compose -f docker-compose.otel.yml up -d
```

This starts a local OTLP-compatible collector (Grafana LGTM) on:
- Port **4317** (gRPC)
- Port **4318** (HTTP OTLP)
- Port **3000** (Grafana UI - if available)

2. **Enable in Services:**

Update `.env`:

```env
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
OTEL_SERVICE_NAME=telegram_multi
```

Restart services:

```bash
cd telegram_multi
docker-compose down
docker-compose up -d
```

3. **Verify Tracing:**

```bash
python3 tracing/check_tracing.py
```

Output should show:
```
Tracing enabled: True
```

### Accessing Traces

If Grafana is available (from docker-compose.otel.yml):
- **Grafana UI:** http://localhost:3000
- **Tempo Traces:** http://localhost:3000/explore (select Tempo datasource)

Manual OTLP verification:
```bash
# Check if OTLP endpoint is receiving data
curl -v http://127.0.0.1:4318/v1/traces
```

---

## Troubleshooting

### API Won't Start

```bash
cd telegram_multi
docker-compose logs api

# Common issues:
# - asyncpg not installed → rebuild with: docker-compose build --no-cache
# - Port 8000 in use → docker-compose down && docker-compose up -d
# - Database connection error → ensure postgres is running
```

### Bot Registration Fails

```bash
# Check admin key matches .env
grep ADMIN_KEY .env

# Check tokens are valid
curl -X POST "http://127.0.0.1:8000/admin/register-bot" \
  -H "X-Admin-Key: admin-secret-key-12345" \
  -d "bot_key=test_bot&token=YOUR_TOKEN"

# Check logs
docker-compose logs api | grep -i error
```

### Webhook Not Set

```bash
# Ensure webhook URL is publicly accessible
curl https://api.your-domain.com/telegram/webhook/your_bot_key

# Check webhook secret
grep WEBHOOK_SECRET .env

# Verify via Telegram Bot API
curl "https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo" | jq .
```

### Tracing Not Working

```bash
# Check if OTEL packages installed
python3 -c "import opentelemetry; print('OK')"

# Check OTLP endpoint is reachable
curl http://127.0.0.1:4318/v1/traces

# Check OpenTelemetry logs
python3 tracing/check_tracing.py

# Enable debug logging in .env
LOG_LEVEL=DEBUG
```

---

## Docker-Compose Services

| Service | Port | Image | Purpose |
|---------|------|-------|---------|
| **api** | 8000 | `telegram_multi_api` | FastAPI application |
| **postgres** | 5432 | `postgres:16-alpine` | SQLModel persistence |
| **redis** | 6379 | `redis:7-alpine` | Job queue backend |
| **worker** | - | `telegram_multi_worker` | RQ background jobs |

---

## File Structure

```
telegram_multi/
├── app/
│   ├── main.py            # FastAPI app, lifespan events
│   ├── config.py          # Settings (Pydantic strict mode)
│   ├── db/
│   │   ├── session.py     # AsyncSession factory
│   │   └── models.py      # SQLModel tables (Bot, Chat, Update)
│   ├── telegram/
│   │   └── webhooks.py    # Webhook handler + dedup
│   ├── bots/
│   │   └── router.py      # Bot management routes
│   ├── admin/
│   │   └── routes.py      # Admin endpoints (/register-bot, /set-webhooks)
│   └── jobs/
│       └── worker.py      # RQ worker for async tasks
├── docker-compose.yml     # Compose config (env_file from root)
├── Dockerfile             # Python 3.11-slim + requirements
├── requirements.txt       # Python packages + OpenTelemetry
└── tests/
    ├── test_api.py        # API unit tests
    └── test_commands.py   # Command handler tests
```

---

## Environment Variables Reference

### Required

| Variable | Default | Purpose |
|----------|---------|---------|
| `ADMIN_KEY` | (none) | Header value for admin endpoints |
| `BOT_TOKENS_MAPPING` | `{}` | JSON mapping: `{"bot_key": "token"}` |

### Optional

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_PORT` | 8000 | FastAPI listen port |
| `API_HOST` | 0.0.0.0 | FastAPI bind address |
| `DEBUG` | false | Enable debug mode |
| `BEARER_TOKEN` | (default) | Auth token for bot operations |
| `WEBHOOK_SECRET` | (default) | Telegram webhook secret token |
| `TELEGRAM_API_TIMEOUT` | 30 | Seconds timeout for Telegram API calls |
| `LOG_LEVEL` | INFO | Python logging level |
| `LOG_FILE` | logs/telegram_multi.log | Log file path |
| `OTEL_ENABLED` | false | Enable OpenTelemetry tracing |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | http://localhost:4318 | OTLP collector endpoint |
| `OTEL_SERVICE_NAME` | telegram_multi | Service name for traces |

---

## Testing

### Unit Tests

```bash
cd telegram_multi

# Install test deps
pip install -r requirements.txt
pip install pytest pytest-asyncio

# Run tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_api.py::test_health -v
```

### Integration Tests

```bash
# Register bots
bash ../scripts/register_bots.sh http://127.0.0.1:8000

# Simulate webhook
curl -X POST http://127.0.0.1:8000/telegram/webhook/your_bot_key \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: telegram-webhook-secret-token-xyz" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {"id": 12345, "first_name": "Test"},
      "chat": {"id": 12345, "type": "private"},
      "text": "/start"
    }
  }'

# Check response
curl http://127.0.0.1:8000/health | jq .
```

---

## Production Checklist

- [ ] Real Telegram bot tokens configured in `.env`
- [ ] Admin key changed from default
- [ ] Webhook secret updated
- [ ] Public domain + SSL certificate
- [ ] Webhook URL reachable from Telegram servers
- [ ] Database backups configured
- [ ] Logging enabled (LOG_LEVEL=INFO)
- [ ] OpenTelemetry tracing configured (optional)
- [ ] Rate limiting configured (if needed)
- [ ] Monitoring alerts set up

---

## Support & Debugging

### Enable verbose logging

```bash
LOG_LEVEL=DEBUG docker-compose up api
```

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 50 lines
docker-compose logs --tail=50
```

### Database inspection

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U telegram_user -d telegram_multi_db

# List tables
\dt

# Sample queries
SELECT * FROM bots;
SELECT * FROM chats WHERE bot_id = 1;
SELECT * FROM updates LIMIT 10;
```

### Redis inspection

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check keys
KEYS *

# Monitor commands
MONITOR

# Queue info
LLEN rq:queue:default
```

---

**Last Updated:** 2025-12-17  
**Version:** 1.0.0  
**Status:** Production Ready ✅
