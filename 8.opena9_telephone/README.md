# ☎️ opena9 - Telefonie Agent (Twilio)

**Agent-ID:** `opena9`  
**Port:** 12354  
**Kürzel:** `telphonep`  
**Status:** ✅ RUNNING (PID: siehe logs/opena9.pid)  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena9** ist der **Telefon Antwort Chatbot (Ton)** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- ☎️ **Voice Response** - Sprachantworten generieren
- 🎙️ **Speech-to-Text** - Anrufe transkribieren
- 📞 **Call Handling** - Anrufe annehmen/beenden
- 📊 **Call Analytics** - Anruf-Statistiken

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena9 (12351) ← Dieser Agent
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
curl http://127.0.0.1:12351/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena9",
  "port": 12351,
  "program_target": "calp",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12351/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "answer_call",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 8.opena9_telephone
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12351/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena9",
    "endpoint": "http://127.0.0.1:12351",
    "program_target": "calp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "calp",
    "action": "answer_call",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
8.opena9_telephone/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena9.py      # Unit-Tests
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
pytest tests/test_opena9.py -v

# Health-Check
curl http://127.0.0.1:12351/health

# Integration-Test via Portier
python3 ../scripts/test_opena9_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12351/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
