# 🤖 opena10 - Call Tracking

**Agent-ID:** `opena10`
**Port:** 12356
**Kürzel:** `calltrackp`
**Version:** 3.0
**Status:** 🟡 **Planned** (PORTIER 3.0 Architecture Ready)
**Letzte Aktualisierung:** 29. November 2025

---

## 📖 Überblick

**opena10** ist der **Call Tracking** im ELION Hyper-Dashboard System - ein spezialisierter Agent für die PORTIER 3.0 Multi-Agent-Architektur.

### 🎯 PORTIER 3.0 Integration

opena10 ist architektonisch vorbereitet für die PORTIER 3.0 Integration:

- ✅ **Option-2-Flow Ready:** OpenAI → opena1 → opena2 → kordp → opena10
- ✅ **Port Policy Compliant:** Port 12356 (Backend-Range 12344-12399)
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
curl http://127.0.0.1:12356/health | jq .
```

### `POST /invoke`

Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12356/invoke \
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
cd 9.opena10_call_tracking
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12356/health | jq .
```

---

## 🔗 Integration mit PORTIER 3.0

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena10",
    "endpoint": "http://127.0.0.1:12356",
    "program_target": "calltrackp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "calltrackp",
    "action": "service_action",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur (Planned)

```txt
9.opena10_call_tracking/
├── main.py                  # FastAPI Agent Entry Point (planned)
├── config.py                # Konfiguration (planned)
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script (planned)
├── tests/
│   └── test_opena10.py  # Unit-Tests (planned)
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
pytest tests/test_opena10.py -v

# Health-Check
curl http://127.0.0.1:12356/health

# Integration-Test via Portier
python3 ../scripts/test_opena10_integration.py
```

---

## 📊 Monitoring (Planned)

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12356/metrics
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

**opena10** ist der **Telefon Anruf Chatbot** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 📞 **Outbound Calls** - Ausgehende Anrufe tätigen
- 🤖 **IVR Integration** - Interactive Voice Response
- 📋 **Call Logging** - Anrufprotokolle
- 🔊 **TTS Support** - Text-to-Speech

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena10 (12356) ← Dieser Agent
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
curl http://127.0.0.1:12356/health | jq .
```

**Response:**

```json
{
  "status": "ok",
  "service": "opena10",
  "port": 12356,
  "program_target": "calltrackp",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`

Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12356/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "make_call",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 9.opena10_call_tracking
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12352/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena10",
    "endpoint": "http://127.0.0.1:12352",
    "program_target": "answp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "answp",
    "action": "make_call",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
9.opena10_call_tracking/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena10.py      # Unit-Tests
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
pytest tests/test_opena10.py -v

# Health-Check
curl http://127.0.0.1:12352/health

# Integration-Test via Portier
python3 ../scripts/test_opena10_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12352/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team
**Letzte Aktualisierung:** 21. November 2025
