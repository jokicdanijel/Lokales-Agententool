# ⭐ opena13 - Social Media Influencer

**Agent-ID:** `opena13`  
**Port:** 12355  
**Kürzel:** `infmep`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena13** ist der **Social Media Influencer** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- ⭐ **Influencer Tracking** - Influencer überwachen
- 📈 **Campaign Management** - Kampagnen steuern
- 💬 **Engagement Analysis** - Interaktionsanalyse
- 🎯 **Target Audience** - Zielgruppenanalyse

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena13 (12355) ← Dieser Agent
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
curl http://127.0.0.1:12355/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena13",
  "port": 12355,
  "program_target": "infmep",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12355/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "track_influencer",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 12.opena13_influencer
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12355/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena13",
    "endpoint": "http://127.0.0.1:12355",
    "program_target": "infmep"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "infmep",
    "action": "track_influencer",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
12.opena13_influencer/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena13.py      # Unit-Tests
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
pytest tests/test_opena13.py -v

# Health-Check
curl http://127.0.0.1:12355/health

# Integration-Test via Portier
python3 ../scripts/test_opena13_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12355/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
