# 📈 opena19 - Aktien & Crypto Trading Agent

**Agent-ID:** `opena19`  
**Port:** 12361  
**Kürzel:** `aktienp`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena19** ist der **Aktien & Crypto Trading Agent** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 📈 **Stock Tracking** - Aktienkurse überwachen
- 💰 **Crypto Trading** - Krypto-Handel
- 📊 **Portfolio Management** - Portfolio verwalten
- 🔔 **Price Alerts** - Kursalarme

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena19 (12361) ← Dieser Agent
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
curl http://127.0.0.1:12361/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena19",
  "port": 12361,
  "program_target": "aktienp",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12361/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "track_stock",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 18.opena19_Aktien&Crypto
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12361/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena19",
    "endpoint": "http://127.0.0.1:12361",
    "program_target": "aktienp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "aktienp",
    "action": "track_stock",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
18.opena19_Aktien&Crypto/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena19.py      # Unit-Tests
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
pytest tests/test_opena19.py -v

# Health-Check
curl http://127.0.0.1:12361/health

# Integration-Test via Portier
python3 ../scripts/test_opena19_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12361/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
