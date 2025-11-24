# 💾 opena18 - Lokaler Archiv Agent

**Agent-ID:** `opena18`  
**Port:** 12360  
**Kürzel:** `locp`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena18** ist der **Lokaler Archiv Agent** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 💾 **Local Storage** - Dateien lokal speichern
- 📂 **File Indexing** - Suchindex erstellen
- 🔍 **Full-Text Search** - Volltextsuche
- 🗄️ **Archive Management** - Archivverwaltung

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena18 (12360) ← Dieser Agent
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
curl http://127.0.0.1:12360/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena18",
  "port": 12360,
  "program_target": "locp",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12360/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "store_file",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 17.opena18_CMR
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12360/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena18",
    "endpoint": "http://127.0.0.1:12360",
    "program_target": "locp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "locp",
    "action": "store_file",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
17.opena18_CMR/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena18.py      # Unit-Tests
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
pytest tests/test_opena18.py -v

# Health-Check
curl http://127.0.0.1:12360/health

# Integration-Test via Portier
python3 ../scripts/test_opena18_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12360/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
