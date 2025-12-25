# Telegram Multi-Bot Project

## Features

- ✅ Webhook-based Telegram integration (Port 8000)
- ✅ Multi-bot orchestration (browser_opena6_bot, open2tele_bot, etc.)
- ✅ PostgreSQL + SQLModel for persistence
- ✅ Redis queue for background tasks (RQ)
- ✅ Bearer token auth + webhook secret validation
- ✅ Update deduplication (bot_id + update_id)
- ✅ Command routing & extensible handlers
- ✅ Docker & docker-compose ready
- ✅ Pytest test suite included

## Quick Start

```bash
# Copy .env
cp .env.example .env

# Edit .env with your Telegram bot tokens
# BOT_TOKENS_MAPPING={"browser_opena6_bot": "YOUR_TOKEN", "open2tele_bot": "YOUR_TOKEN"}

# Start services
docker-compose up -d

# Wait for services to initialize (~5 sec)
sleep 5

# Register bots (replace WEBHOOK_URL with your domain)
curl -X POST http://127.0.0.1:8000/admin/set-webhooks \
  -H "X-Admin-Key: admin-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"webhook_base_url": "https://api.hyperdashboard-one.de"}'

# Health check
curl http://127.0.0.1:8000/health
```

## Project Structure

```
telegram_multi/
├── app/
│   ├── main.py            # FastAPI app entry
│   ├── config.py          # Settings (strict mode)
│   ├── db/
│   │   ├── session.py     # AsyncSession factory
│   │   └── models.py      # SQLModel tables (Bot, Chat, Update, etc.)
│   ├── telegram/
│   │   └── webhooks.py    # Webhook handler + deduplication
│   ├── bots/
│   │   └── router.py      # BotRouter dispatcher
│   ├── commands/
│   │   └── registry.py    # CommandRegistry + handlers
│   ├── admin/
│   │   └── routes.py      # Admin endpoints (/register-bot, /set-webhooks)
│   └── jobs/
│       └── worker.py      # RQ worker stub
├── tests/
│   ├── test_api.py        # API tests
│   ├── test_commands.py   # Command handler tests
│   └── requirements.txt    # Test dependencies
├── docker-compose.yml     # Multi-service orchestration
├── Dockerfile             # Container image
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Architecture

### Option-2 Flow (Telegram → opena1 → opena2 → kordp)

```
Telegram Webhook
    ↓
/telegram/webhook/{bot_key}  (Port 8000)
    ↓
BotRouter → CommandRegistry
    ↓
Handler (browser_opena6_bot, open2tele_bot, etc.)
    ↓
RQ Job → Background Task
    ↓
opena1 (Coordinator) → opena2 (Archivator) → opena6 (Browser)
```

### Security

- ✅ Bearer token validation in headers
- ✅ Webhook secret token (X-Telegram-Bot-Api-Secret-Token)
- ✅ Admin key for protected endpoints (X-Admin-Key)
- ✅ Pydantic strict schemas (`extra="forbid"`)
- ✅ SQL injection prevention (SQLModel + async execution)

## Deployment

### Tracing (OpenTelemetry) 🔧

This service supports optional OpenTelemetry tracing via `pkg.observability.init_tracing`.
To enable tracing, set these environment variables in `.env` or via your orchestrator:

```
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-otel-collector:4318
OTEL_SERVICE_NAME=telegram_multi
```

You can verify tracing with the helper script:

```bash
python3 tracing/check_tracing.py
```

If required packages are missing the service will still run but tracing will be skipped.

### Behind Nginx Proxy

```nginx
location /telegram {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### Environment Variables

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db
REDIS_URL=redis://redis:6379
BOT_TOKENS_MAPPING={"bot_key": "TOKEN"}
BEARER_TOKEN=uuid-token-here
ADMIN_KEY=admin-secret
WEBHOOK_SECRET=secret-token
```

## Testing

```bash
# Run tests
pytest tests/ -v

# Coverage
pytest --cov=app tests/
```

## Monitoring

Logs are written to:

- stdout (console)
- `logs/telegram_multi.log` (file, rotated)

## Known Limitations

- [ ] Persistent chat history
- [ ] Multi-turn conversation state
- [ ] Rate limiting per bot
- [ ] Message encryption at rest
- [ ] Alembic migrations (manual schema updates)

## Next Steps

1. **Register bots** via `/admin/register-bot` endpoint
2. **Set webhooks** via `/admin/set-webhooks`
3. **Send test message** to any registered bot
4. **Check logs** for webhook delivery confirmation
5. **Verify Option-2 flow** (opena1 → opena2 → kordp)
