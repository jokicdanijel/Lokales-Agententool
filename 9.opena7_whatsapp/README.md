# Agent: opena7_whatsapp

**Agent ID:** `opena7`  
**Port:** `12350`  
**Category:** `Integration`  
**Description:** WhatsApp Integration

## Quick Start

```bash
pip install -r requirements.txt
cp .env.template .env
bash bin/start.sh
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/status` | Agent status |
| POST | `/invoke` | Main invoke endpoint |

## Testing

```bash
curl -s http://127.0.0.1:12350/health | jq .
```

## Logging

```bash
tail -f logs/app.log
```

---

**Auto-generated:** 2025-11-08
