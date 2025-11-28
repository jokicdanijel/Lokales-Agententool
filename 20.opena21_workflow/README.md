# ⚙️ opena21 - Workflow Engine

**Agent-ID:** `opena21`  
**Port:** 12364  
**Kürzel:** `workflowp`  
**Version:** 2.0  
**Status:** ✅ **Production** (Multi-Agent Workflow Orchestration)  
**Letzte Aktualisierung:** 28. November 2025

---

## 📖 Überblick

**opena21** ist die **Workflow Engine** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen (Geplant)

- ⚙️ **Process Automation** - Automatisierte Workflows
- 🔄 **Task Orchestration** - Aufgabensteuerung
- 📊 **State Management** - Zustandsverwaltung
- 🔗 **Integration Hub** - Service-Verbindungen

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena21 (12364) ← Dieser Agent
    ↓
OpenA2 (12345) → Portier (12344)
    ↓
Client/UI
```

**Integration:** Vollständig in Option-2-Flow integriert.

---

## 📡 API-Endpoints (Geplant)

### `GET /health`

Health-Check des Agents.

```bash
curl http://127.0.0.1:12364/health | jq .
```

**Response:**

```json
{
  "status": "ok",
  "service": "opena21",
  "port": 12364,
  "program_target": "workflowp",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`

Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12364/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "execute_workflow",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten (Wenn implementiert)

```bash
cd 20.opena21_workflow
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12364/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena21",
    "endpoint": "http://127.0.0.1:12364",
    "program_target": "workflowp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "workflowp",
    "action": "execute_workflow",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
20.opena21_workflow/
├── main.py                  # FastAPI Agent Entry Point (geplant)
├── config.py                # Konfiguration (geplant)
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script (geplant)
├── tests/
│   └── test_opena21.py      # Unit-Tests (geplant)
└── README.md                # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer `/health`
- ✅ **Port-Policy** Enforcement (12344-12399)
- ✅ **Strict JSON** (Pydantic `extra="forbid"`)
- ✅ **Option-2-Flow** Compliance

---

## 🧪 Testing (Geplant)

```bash
# Unit-Tests
pytest tests/test_opena21.py -v

# Health-Check
curl http://127.0.0.1:12364/health

# Integration-Test via Portier
python3 ../scripts/test_opena21_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12364/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 27. November 2025  
**Status:** 🟡 In Planung (Ordnerstruktur vorhanden, Implementierung ausstehend)
