# 🏠 opena17 - Homepage Creator & Servicetool

**Agent-ID:** `opena17`  
**Port:** 12359  
**Kürzel:** `homep`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena17** ist der **Homepage Creator & Servicetool** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 🏠 **Page Builder** - Webseiten erstellen
- 🎨 **Design Templates** - Vorlagen nutzen
- 📝 **CMS Integration** - Content-Management
- 🚀 **Deployment** - Hosting & Veröffentlichung

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena17 (12359) ← Dieser Agent
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
curl http://127.0.0.1:12359/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena17",
  "port": 12359,
  "program_target": "homep",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12359/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "build_page",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 16.opena17_homepagecreator
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12359/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena17",
    "endpoint": "http://127.0.0.1:12359",
    "program_target": "homep"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "homep",
    "action": "build_page",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
16.opena17_homepagecreator/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena17.py      # Unit-Tests
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
pytest tests/test_opena17.py -v

# Health-Check
curl http://127.0.0.1:12359/health

# Integration-Test via Portier
python3 ../scripts/test_opena17_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12359/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
