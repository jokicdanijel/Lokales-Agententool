# 🚀 OpenWebUI Agent V2 (opena3) - PORTIER 3.0 Certified

**PORTIER 3.0 zertifizierter OpenWebUI Agent mit vollständiger Option-2-Flow Integration**

## 🎯 Features

✅ **Option-2-Flow konform**: `/cmd`, `/health`, `/native`, `/dispatch_ready`  
✅ **Safepoint-System**: CMD/RESP mit Unicode-Pfeil `→`  
✅ **Dispatcher-Anbindung**: kordp-kompatibel  
✅ **Tool-Registry**: Auto-Registration bei Start  
✅ **Dashboard Integration**: SSE Events + Live Status  
✅ **Bearer Auth**: Strict Security Model  
✅ **Chat Engine**: Context chaining + Model selection  
✅ **Dev-Friendly**: Mock-Mode, Self-Test, API Schema  

## 🏗️ Architektur

```
OpenAI → opena1 → opena2 → kordp → opena3 → OpenWebUI
                    ↓              ↑
              Safepoints      Live Results
```

### Ports
- **opena3 V2**: `12347` (FastAPI Agent)
- **OpenWebUI**: `3000` (UI only)

### Endpoints

| Endpoint | Beschreibung | Auth | Option-2 |
|----------|-------------|------|----------|
| `/cmd` | CMD-Envelope von opena1 | ✓ | ✓ |
| `/health` | Extended Health Check | - | ✓ |
| `/native` | Direkte UI-Calls | ✓ | - |
| `/dispatch_ready` | Live Routing Status | ✓ | ✓ |
| `/dispatch` | kordp-Kompatibilität | ✓ | ✓ |
| `/selftest` | Endpoint-Tests | ✓ | - |

## 🚀 Quick Start

### 1. Setup

```bash
cd 2.opena3_openwebui

# Virtual Environment (optional)
python3 -m venv .venv
source .venv/bin/activate

# Dependencies
pip install -r requirements_v2.txt
```

### 2. Environment

```bash
# .env erstellen
cat > .env << EOF
BEARER_TOKEN=c899b90d-faf8-485b-afa4-078357cf5313
OPENWEBUI_URL=http://127.0.0.1:8080
ARCHIVP_ROOT=/tmp/archivp
DEV_MODE=false
MOCK_MODE=false
EOF
```

### 3. Start Service

```bash
# Mit Start-Skript
./start_opena3_v2.sh start

# Oder direkt
python3 opena3_terminal_v2.py
```

### 4. Verify

```bash
# Health Check
curl -s http://127.0.0.1:12347/health | jq .

# Self-Test (mit Token)
./start_opena3_v2.sh test
```

## 🧪 Testing

### Option-2-Flow Test

```bash
# CMD-Envelope senden (simuliert opena1)
curl -X POST http://127.0.0.1:12347/cmd \
  -H "Authorization: Bearer c899b90d-faf8-485b-afa4-078357cf5313" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-123",
    "timestamp": "2025-11-29T12:00:00Z",
    "source": "opena1",
    "command": "chat",
    "payload": {"prompt": "Hello OpenWebUI"}
  }'
```

### Native Chat Test

```bash
# Direkter Chat (simuliert UI)
curl -X POST http://127.0.0.1:12347/native \
  -H "Authorization: Bearer c899b90d-faf8-485b-afa4-078357cf5313" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Wie geht es dir?",
    "model": "gpt-4"
  }'
```

## 🔧 Konfiguration

### Environment Variables

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `OPENA3_PORT` | `12347` | Service Port |
| `OPENWEBUI_URL` | `http://127.0.0.1:8080` | OpenWebUI Base URL |
| `OPENWEBUI_TIMEOUT` | `30` | Request Timeout (s) |
| `BEARER_TOKEN` | - | **Erforderlich**: Auth Token |
| `ARCHIVP_ROOT` | `/tmp/archivp` | Safepoint Storage |
| `DEV_MODE` | `false` | Development Features |
| `MOCK_MODE` | `false` | Mock OpenWebUI Calls |

### Logging

```
logs/
├── opena3_v2.log         # Structured service log
└── opena3_v2.nohup.log   # Startup/nohup output
```

## 🛡️ Security

### Bearer Authentication
Alle Endpoints (außer `/health`) erfordern Bearer Token:
```
Authorization: Bearer c899b90d-faf8-485b-afa4-078357cf5313
```

### CORS Policy
- **Production**: Nur Dashboard (`127.0.0.1:12349`)
- **DEV Mode**: Alle Origins

### Rate Limiting
- `/native`: 10 requests/minute
- Andere: Unbegrenzt (interne Calls)

## 📦 Safepoints

Alle Operationen werden als Safepoints archiviert:

```
archivp/
├── 2025/11/29/
│   ├── SP1732876800000_opena3→opena2_CMD.json
│   └── SP1732876800001_opena3→opena2_RESP.json
└── index.jsonl
```

### Format
- **Unicode-Pfeil**: `→` (U+2192)
- **Masked Secrets**: Bearer Tokens automatisch maskiert
- **Append-Only**: Keine Modifikation/Löschung

## 🔄 Integration

### PORTIER Stack
```bash
# Registrierung bei kordp (automatisch beim Start)
POST /dispatch/kordp/register
{
  "service_id": "opena3",
  "service_target": "openwebui3", 
  "capabilities": ["chat", "terminal", "openwebui"]
}
```

### Dashboard Events
```bash
# SSE Events an Dashboard
POST /sse/publish
{
  "event_type": "opena3_chat",
  "data": {...}
}
```

## 🎛️ Operations

### Service Control

```bash
# Start
./start_opena3_v2.sh start

# Stop
./start_opena3_v2.sh stop

# Status
./start_opena3_v2.sh status

# Logs
./start_opena3_v2.sh logs

# Test
./start_opena3_v2.sh test
```

### Health Monitoring

```bash
# Extended Health
curl -s http://127.0.0.1:12347/health | jq .

# Dispatch Readiness  
curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:12347/dispatch_ready | jq .

# Self-Test
curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:12347/selftest | jq .
```

## 🔍 Troubleshooting

### Häufige Probleme

1. **OpenWebUI nicht erreichbar**
   ```bash
   # OpenWebUI Status prüfen
   curl -s http://127.0.0.1:8080/api/config
   
   # Mock Mode aktivieren
   export MOCK_MODE=true
   ```

2. **Bearer Token fehlt**
   ```bash
   # Token aus .env laden
   source .env
   echo $BEARER_TOKEN
   ```

3. **Port bereits belegt**
   ```bash
   # Port-Konflikte prüfen  
   lsof -i :12347
   
   # Alternativen Port
   export OPENA3_PORT=12348
   ```

### Logs analysieren

```bash
# Service-Log (strukturiert)
tail -f logs/opena3_v2.log

# Nohup-Log (startup)
tail -f logs/opena3_v2.nohup.log

# Safepoint-Index
tail -f /tmp/archivp/index.jsonl
```

## 📊 Performance

### Benchmarks
- **Cold Start**: ~2 Sekunden
- **Health Check**: ~50ms
- **Native Chat**: ~500ms (+ OpenWebUI latency)
- **Option-2 CMD**: ~600ms (+ Safepoint overhead)

### Monitoring
```bash
# Request-Statistiken
curl -s http://127.0.0.1:12347/health | jq '.uptime_seconds, .last_dispatch'

# OpenWebUI-Status
curl -s http://127.0.0.1:12347/health | jq '.openwebui_status'
```

## 🎯 Migration von V1

### Unterschiede V1 → V2

| Feature | V1 | V2 |
|---------|----|----|
| Option-2-Flow | ❌ | ✅ |
| Safepoints | ❌ | ✅ |
| Auto-Registration | ❌ | ✅ |
| Bearer Auth | Basic | ✅ Strict |
| Rate Limiting | ❌ | ✅ |
| Mock Mode | ❌ | ✅ |

### Migration Steps

1. **Stoppe V1**: `pkill -f main_openwebui_agent.py`
2. **Starte V2**: `./start_opena3_v2.sh start`
3. **Verifiziere**: `./start_opena3_v2.sh test`

---

## 🏷️ Meta

- **Version**: 2.0.0
- **Status**: Production Ready
- **Maintainer**: ELION Team
- **License**: Internal Use Only
- **PORTIER**: 3.0 Certified ✅

**Last Updated**: 29. November 2025