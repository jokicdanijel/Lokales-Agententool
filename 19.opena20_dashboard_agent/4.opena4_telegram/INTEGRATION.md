# opena4 Integration Guide

## Integration ins ELION Hyper-Dashboard

opena4 ist vollständig in das ELION Hyper-Dashboard integriert.

### 1. System-Baseline Integration

opena4 ist bereits im Canonical Registry definiert:

```yaml
# system_baseline.yaml (bereits vorhanden)
agents:
  opena4:
    port: 12346
    name: "Telegram Agent"
    plan: "basic"
```

### 2. Agent Discovery

Der Agent wird automatisch vom Discovery-System gefunden:

```bash
cd /path/to/Gesamtprojekt
python3 scripts/agent_discovery.py
```

Das generiert `artifacts/agent_capabilities.json` mit opena4-Daten.

### 3. Plan Entitlements

opena4 ist im Basic Plan verfügbar:

```json
{
  "plans": {
    "basic": {
      "agents": ["opena3", "opena4", "opena7", "opena11"]
    }
  }
}
```

### 4. Dashboard Integration (opena20)

opena20 generiert automatisch HTML für opena4:

```python
# In opena20/main.py
with open('artifacts/agent_capabilities.json') as f:
    manifest = json.load(f)

agent = manifest['agents']['opena4']  # Auto-discovered
html = generate_agent_page(agent)
```

### 5. Workflow Integration (opena21)

opena4 kann in Workflows verwendet werden:

```python
# Beispiel Workflow
workflow = {
    "name": "User Notification",
    "steps": [
        {
            "agent": "opena4",
            "action": "send",
            "params": {
                "chat_id": "{user.telegram_id}",
                "text": "Ihre Bestellung wurde versandt!"
            }
        }
    ]
}
```

### 6. Docker Compose Integration

opena4 ist bereits in `docker-compose.yml` integriert:

```yaml
services:
  opena4:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.agent
      args:
        AGENT_ID: opena4
    container_name: eden-opena4
    ports:
      - "12346:12346"
    environment:
      AGENT_ID: opena4
      PORT: 12346
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      DB_HOST: postgres
      REDIS_HOST: redis
    depends_on:
      - postgres
      - redis
    networks:
      - eden-network
    restart: unless-stopped
```

### 7. Nginx Routing (optional)

Füge zu `infrastructure/nginx/nginx.conf` hinzu:

```nginx
# opena4 upstream
upstream opena4 {
    server opena4:12346;
}

# Route für Telegram Webhook (optional)
location /telegram/webhook {
    proxy_pass http://opena4/telegram/webhook;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Verwendung im System

### Via opena1 (Coordinator)

Alle Agent-zu-Agent-Kommunikation läuft über opena1:

```python
import httpx

async def send_telegram_via_coordinator(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://opena1:12344/forward",
            json={
                "target": "opena4",
                "endpoint": "/send",
                "data": {
                    "chat_id": chat_id,
                    "text": text
                }
            }
        )
        return response.json()
```

### Direct Access (Development)

Für Entwicklung/Testing direkt:

```bash
curl -X POST http://localhost:12346/send \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "text": "Test von ELION!"
  }'
```

### Via Auth Service

Mit Session-Token:

```python
headers = {"Authorization": f"Bearer {session_token}"}
response = requests.post(
    "http://localhost:12346/send",
    json={"chat_id": user.telegram_id, "text": "Nachricht"},
    headers=headers
)
```

## Monitoring Integration

### Prometheus Metrics

opena4 exportiert Metriken via `/health`:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "opena4"
    static_configs:
      - targets: ["opena4:12346"]
    metrics_path: "/health"
    scrape_interval: 30s
```

### Grafana Dashboard

Erstelle Dashboard mit Panels für:

- Total Messages
- Messages per Chat
- Response Time
- Error Rate

## Testing Integration

### Preflight Check

```bash
python3 scripts/preflight_check.py
# Sollte opena4 validieren:
# ✓ Port: 12346
# ✓ Agent ID: opena4
# ✓ Health endpoint exists
```

### Unit Tests

```bash
cd 4.opena4_telegram
pytest tests/test_opena4.py -v
```

### Integration Tests

```bash
# Start opena4
./start.sh &

# Test health
curl http://localhost:12346/health

# Test capabilities
curl http://localhost:12346/capabilities

# Test send (requires bot token)
curl -X POST http://localhost:12346/send \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 123456789, "text": "Test"}'
```

## Deployment Steps

### 1. Environment Setup

```bash
# In root .env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 2. Build & Deploy

```bash
# Full system deployment
make deploy

# Or just opena4
docker-compose up -d opena4
```

### 3. Verify

```bash
# Check status
docker ps | grep opena4

# Check logs
docker logs eden-opena4

# Test endpoint
curl http://localhost:12346/health
```

## Troubleshooting

### Agent nicht erreichbar

```bash
# Check Docker
docker ps | grep opena4

# Check logs
docker logs eden-opena4

# Restart
docker-compose restart opena4
```

### Bot Token ungültig

```bash
# Test token
curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe

# Update .env
nano .env
# TELEGRAM_BOT_TOKEN=new_token

# Restart
docker-compose restart opena4
```

### Database Connection Error

```bash
# Check PostgreSQL
docker exec eden-postgres psql -U eden_user -d eden -c "SELECT 1;"

# Check tables
docker exec eden-postgres psql -U eden_user -d eden -c "\dt"
```

## Best Practices

1. **Secrets Management**: Niemals Bot Token im Code
2. **Error Handling**: Nutze Try-Catch für alle API-Calls
3. **Rate Limiting**: Beachte Telegram API Limits
4. **Logging**: Alle Nachrichten in opena2 Archive loggen
5. **Monitoring**: Health-Checks regelmäßig durchführen

## Support

- **Docs**: [README.md](README.md)
- **Tests**: `pytest tests/`
- **Issues**: GitHub Issues
- **ELION Docs**: `docs/COPILOT_HANDOFF.md`

---

**Version**: 1.0.0
**Last Updated**: 2025-12-23
**Status**: ✅ Production Ready
