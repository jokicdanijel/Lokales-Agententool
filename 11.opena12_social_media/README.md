# 🤖 opena12 - Social Media

**Agent-ID:** `opena12`
**Port:** 12358
**Kürzel:** `smp`
**Version:** 3.0
**Status:** 🟡 **Planned** (PORTIER 3.0 Architecture Ready)
**Letzte Aktualisierung:** 29. November 2025

---

## 📖 Überblick

**opena12** ist der **Social Media** im ELION Hyper-Dashboard System - ein spezialisierter Agent für die PORTIER 3.0 Multi-Agent-Architektur.

### 🎯 PORTIER 3.0 Integration

opena12 ist architektonisch vorbereitet für die PORTIER 3.0 Integration:

- ✅ **Option-2-Flow Ready:** OpenAI → opena1 → opena2 → kordp → opena12
- ✅ **Port Policy Compliant:** Port 12358 (Backend-Range 12344-12399)
- ✅ **Safepoint Integration:** Automatische Archivierung via opena2
- ✅ **Bearer Token Security:** Authentifizierung vorbereitet
- 🟡 **Implementation Status:** Ordnerstruktur vorhanden, Code pending

### 🚀 Zukünftige Features

- 🔄 **Multi-Agent Coordination:** Integration mit anderen Agenten
- 📊 **Real-time Monitoring:** Dashboard-Integration (opena20)
- 🛡️ **Security First:** Vollständige Bearer Token Implementation
- ⚡ **High Performance:** Async FastAPI Architecture

---

## 📡 API-Endpoints (Planned)

### `GET /health`

Health-Check des Agents.

```bash
curl http://127.0.0.1:12358/health | jq .
```

### `POST /invoke`

Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12358/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "service_action",
    "params": {...}
  }'
```

---

## 🚀 Quick Start (When Implemented)

### Agent starten

```bash
cd 11.opena12_social_media
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12358/health | jq .
```

---

## 🔗 Integration mit PORTIER 3.0

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena12",
    "endpoint": "http://127.0.0.1:12358",
    "program_target": "smp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "smp",
    "action": "service_action",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur (Planned)

```txt
11.opena12_social_media/
├── main.py                  # FastAPI Agent Entry Point (planned)
├── config.py                # Konfiguration (planned)
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script (planned)
├── tests/
│   └── test_opena12.py  # Unit-Tests (planned)
└── README.md                # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer `/health`
- ✅ **Port-Policy** Enforcement (12344-12399)
- ✅ **Strict JSON** (Pydantic `extra="forbid"`)
- ✅ **Option-2-Flow** Compliance

---

## 🧪 Testing (Planned)

```bash
# Unit-Tests
pytest tests/test_opena12.py -v

# Health-Check
curl http://127.0.0.1:12358/health

# Integration-Test via Portier
python3 ../scripts/test_opena12_integration.py
```

---

## 📊 Monitoring (Planned)

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12358/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** Danijel Jokic (ELION Team)
**Letzte Aktualisierung:** 29. November 2025
**Status:** 🟡 **Architecture Ready** (Implementation Pending)

## 📖 Überblick

**opena12** ist der **Social Media Automation Agent** - ein spezialisierter Agent für Multi-Platform Social Media Management im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 📝 **Multi-Platform Posting** - LinkedIn, X/Twitter, Facebook, Instagram
- 🗓️ **Post Scheduling** - Queue-basierte Zeitplanung
- ✅ **Character Validation** - Plattform-spezifische Limits (280 X, 3000 LinkedIn)
- 🖼️ **Media Upload** - Bilder & Videos (bis zu 10 pro Post)
- 🔐 **OAuth Management** - Sichere Token-Verwaltung
- 📊 **Analytics Ready** - Engagement-Metriken (Mock)

---

## 🏗️ Architektur

```text
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena12 (12357) ← Dieser Agent
    ↓
OpenA2 (12345) → Portier (12344)
    ↓
Client/UI
```

**Integration:** Vollständig in Option-2-Flow integriert.

---

## 📡 API-Endpoints

### `GET /health`

Health-Check des Agents.

```bash
curl http://127.0.0.1:12357/health | jq .
```

**Response:**

```json
{
  "status": "ok",
  "service": "opena12",
  "kürzel": "smp",
  "port": 12357,
  "uptime_seconds": 3661.23,
  "queued_posts": 5,
  "platforms": ["linkedin", "x", "facebook", "instagram"],
  "timestamp": "2025-11-27T12:00:00Z"
}
```

### `POST /post`

Post sofort auf Plattformen veröffentlichen.

```bash
curl -X POST http://127.0.0.1:12357/post \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["linkedin", "x"],
    "text": "Check out our new product! 🚀",
    "hashtags": ["innovation", "tech"]
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 11.opena12_social_media
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12357/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena12",
    "endpoint": "http://127.0.0.1:12357",
    "program_target": "smp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "smp",
    "action": "post",
    "params": {
      "platforms": ["linkedin"],
      "text": "Hello from Portier!"
    }
  }'
```

---

## 📁 Verzeichnisstruktur

```text
11.opena12_social_media/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena12.py      # Unit-Tests
└── README.md                # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer `/health`
- ✅ **Port-Policy** Enforcement (12344-12399)
- ✅ **Strict JSON** (Pydantic `extra="forbid"`)
- ✅ **Option-2-Flow** Compliance

---

## 🧪 Testing

```bash
# Unit-Tests
pytest tests/test_opena12.py -v

# Health-Check
curl http://127.0.0.1:12357/health

# Integration-Test via Portier
python3 ../scripts/test_opena12_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12357/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team
**Letzte Aktualisierung:** 27. November 2025
