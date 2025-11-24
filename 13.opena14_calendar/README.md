# 📅 opena14 - Kalender Agent

**Agent-ID:** `opena14`  
**Port:** 12356  
**Kürzel:** `kalp`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena14** ist der **Kalender Agent** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 📅 **Event Management** - Termine erstellen/bearbeiten
- 🔔 **Reminders** - Erinnerungen senden
- 👥 **Shared Calendars** - Kalender teilen
- 🔄 **Sync Support** - Google/Outlook Integration

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena14 (12356) ← Dieser Agent
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
  "service": "opena14",
  "port": 12356,
  "program_target": "kalp",
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
    "action": "create_event",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 13.opena14_calendar
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

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena14",
    "endpoint": "http://127.0.0.1:12356",
    "program_target": "kalp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "kalp",
    "action": "create_event",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
13.opena14_calendar/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena14.py      # Unit-Tests
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
pytest tests/test_opena14.py -v

# Health-Check
curl http://127.0.0.1:12356/health

# Integration-Test via Portier
python3 ../scripts/test_opena14_integration.py
```

---

## 📊 Monitoring

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

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
