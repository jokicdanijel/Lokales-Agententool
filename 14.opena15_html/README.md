# 📝 opena15 - HTML Creator Tool

**Agent-ID:** `opena15`  
**Port:** 12357  
**Kürzel:** `htmlp`  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

**opena15** ist der **HTML Creator Tool** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

- 📝 **HTML Generation** - HTML-Code generieren
- 🎨 **Template Engine** - Vorlagen verwenden
- 🔍 **SEO Optimization** - Meta-Tags, Keywords
- 📱 **Responsive Design** - Mobile-optimiert

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena15 (12357) ← Dieser Agent
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
curl http://127.0.0.1:12357/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena15",
  "port": 12357,
  "program_target": "htmlp",
  "uptime_seconds": 3661.23
}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12357/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_html",
    "params": {...}
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 14.opena15_html
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12357/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena15",
    "endpoint": "http://127.0.0.1:12357",
    "program_target": "htmlp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "htmlp",
    "action": "generate_html",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur

```
14.opena15_html/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_opena15.py      # Unit-Tests
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
pytest tests/test_opena15.py -v

# Health-Check
curl http://127.0.0.1:12357/health

# Integration-Test via Portier
python3 ../scripts/test_opena15_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12357/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
