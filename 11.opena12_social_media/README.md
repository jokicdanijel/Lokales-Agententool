# 📱 opena12 - Social Media Automatisierung

**Agent-ID:** `opena12`  
**Port:** 12354  
**Kürzel:** `somep`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena12** ist der **Social Media Automatisierung** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 📱 **Post Automation** - Posts planen & veröffentlichen
- 📊 **Analytics** - Engagement-Metriken
- 👥 **Multi-Platform** - Twitter, Facebook, Instagram, LinkedIn
- 🔔 **Notifications** - Social Media Alerts

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena12 (12354) ← Dieser Agent
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
curl http://127.0.0.1:12354/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena12",
  "port": 12354,
  "program_target": "somep",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12354/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "post",
    "params": {...}
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
curl http://127.0.0.1:12354/health | jq .
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
    "endpoint": "http://127.0.0.1:12354",
    "program_target": "somep"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "somep",
    "action": "post",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
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
curl http://127.0.0.1:12354/health

# Integration-Test via Portier
python3 ../scripts/test_opena12_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12354/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
