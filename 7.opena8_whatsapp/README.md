# 💬 opena8 - WhatsApp Chatbot

**Agent-ID:** `opena8`  
**Port:** 12350  
**Kürzel:** `whatp`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena8** ist der **WhatsApp Chatbot** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 💬 **Send Message** - WhatsApp-Nachrichten senden
- 📥 **Receive Messages** - Eingehende Nachrichten
- 📎 **Media Support** - Bilder, Videos, Dokumente
- 👥 **Group Management** - Gruppen-Interaktion

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena8 (12350) ← Dieser Agent
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
curl http://127.0.0.1:12350/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena8",
  "port": 12350,
  "program_target": "whatp",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12350/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "send_message",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 7.opena8_whatsapp
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12350/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena8",
    "endpoint": "http://127.0.0.1:12350",
    "program_target": "whatp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "whatp",
    "action": "send_message",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
7.opena8_whatsapp/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena8.py      # Unit-Tests
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
pytest tests/test_opena8.py -v

# Health-Check
curl http://127.0.0.1:12350/health

# Integration-Test via Portier
python3 ../scripts/test_opena8_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12350/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
