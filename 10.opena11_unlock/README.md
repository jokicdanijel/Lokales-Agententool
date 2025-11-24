# 🔓 opena11 - Unlock Master (Aufsperr-Decode)

**Agent-ID:** `opena11`  
**Port:** 12353  
**Kürzel:** `onlockp`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena11** ist der **Unlock Master (Aufsperr-Decode)** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 🔓 **Decode** - Verschlüsselte Daten entschlüsseln
- 🔑 **Key Management** - Schlüsselverwaltung
- 🛡️ **Security Analysis** - Sicherheitsanalyse
- 📜 **Audit Logging** - Zugriffsprotokolle

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena11 (12353) ← Dieser Agent
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
curl http://127.0.0.1:12353/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena11",
  "port": 12353,
  "program_target": "onlockp",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12353/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "decode",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 10.opena11_unlock
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12353/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena11",
    "endpoint": "http://127.0.0.1:12353",
    "program_target": "onlockp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "onlockp",
    "action": "decode",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
10.opena11_unlock/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena11.py      # Unit-Tests
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
pytest tests/test_opena11.py -v

# Health-Check
curl http://127.0.0.1:12353/health

# Integration-Test via Portier
python3 ../scripts/test_opena11_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12353/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
