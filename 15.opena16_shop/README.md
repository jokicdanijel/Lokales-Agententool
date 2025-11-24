# 🛒 opena16 - Shop Creator & Servicetool

**Agent-ID:** `opena16`  
**Port:** 12358  
**Kürzel:** `shopp`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena16** ist der **Shop Creator & Servicetool** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 🛒 **Product Management** - Produkte verwalten
- 💳 **Payment Integration** - Zahlungsabwicklung
- 📦 **Order Processing** - Bestellungen bearbeiten
- 📊 **Inventory** - Lagerverwaltung

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena16 (12358) ← Dieser Agent
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
curl http://127.0.0.1:12358/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena16",
  "port": 12358,
  "program_target": "shopp",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12358/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_product",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 15.opena16_shop
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12358/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena16",
    "endpoint": "http://127.0.0.1:12358",
    "program_target": "shopp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "shopp",
    "action": "add_product",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
15.opena16_shop/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena16.py      # Unit-Tests
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
pytest tests/test_opena16.py -v

# Health-Check
curl http://127.0.0.1:12358/health

# Integration-Test via Portier
python3 ../scripts/test_opena16_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12358/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
