# 🤖 opena15 - HTML Creator

**Agent-ID:** `opena15`
**Port:** 12361
**Kürzel:** `htmlp`
**Version:** 3.0
**Status:** 🟡 **Planned** (PORTIER 3.0 Architecture Ready)
**Letzte Aktualisierung:** 29. November 2025

---

## 📖 Überblick

**opena15** ist der **HTML Creator** im ELION Hyper-Dashboard System - ein spezialisierter Agent für die PORTIER 3.0 Multi-Agent-Architektur.

### 🎯 PORTIER 3.0 Integration

opena15 ist architektonisch vorbereitet für die PORTIER 3.0 Integration:

- ✅ **Option-2-Flow Ready:** OpenAI → opena1 → opena2 → kordp → opena15
- ✅ **Port Policy Compliant:** Port 12361 (Backend-Range 12344-12399)
- ✅ **Safepoint Integration:** Automatische Archivierung via opena2
- ✅ **Bearer Token Security:** Authentifizierung vorbereitet
- 🟡 **Implementation Status:** Ordnerstruktur vorhanden, Code pending

### 🚀 Zukünftige Features

- 🔄 **Multi-Agent Coordination:** Integration mit anderen Agenten
- 📊 **Real-time Monitoring:** Dashboard-Integration (opena20)
- 🛡️ **Security First:** Vollständige Bearer Token Implementation
- ⚡ **High Performance:** Async FastAPI Architecture

---

## 📡 API-Endpoints (Planned)

### `GET /health`

Health-Check des Agents.

```bash
curl http://127.0.0.1:12361/health | jq .
```

### `POST /invoke`

Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12361/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "service_action",
    "params": {...}
  }'
```

---

## 🚀 Quick Start (When Implemented)

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
curl http://127.0.0.1:12361/health | jq .
```

---

## 🔗 Integration mit PORTIER 3.0

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena15",
    "endpoint": "http://127.0.0.1:12361",
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
    "action": "service_action",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur (Planned)

```txt
14.opena15_html/
├── main.py                  # FastAPI Agent Entry Point (planned)
├── config.py                # Konfiguration (planned)
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script (planned)
├── tests/
│   └── test_opena15.py  # Unit-Tests (planned)
└── README.md                # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer `/health`
- ✅ **Port-Policy** Enforcement (12344-12399)
- ✅ **Strict JSON** (Pydantic `extra="forbid"`)
- ✅ **Option-2-Flow** Compliance

---

## 🧪 Testing (Planned)

```bash
# Unit-Tests
pytest tests/test_opena15.py -v

# Health-Check
curl http://127.0.0.1:12361/health

# Integration-Test via Portier
python3 ../scripts/test_opena15_integration.py
```

---

## 📊 Monitoring (Planned)

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

**Maintainer:** Danijel Jokic (ELION Team)
**Letzte Aktualisierung:** 29. November 2025
**Status:** 🟡 **Architecture Ready** (Implementation Pending)

## 📖 Überblick

**opena15** ist der **HTML Creator Agent** - spezialisiert auf HTML-Generierung, Template-Management und Validierung.

### Kernfunktionen

- 📝 **HTML-Generierung** - Jinja2-Templates rendern mit Variablen
- 🎨 **CSS-Framework-Integration** - Bootstrap, Tailwind, Bulma Support
- ✅ **HTML-Validierung** - BeautifulSoup4-basierte Struktur-Checks
- 🔍 **SEO-Optimization** - Meta-Tags, Keywords, Description
- 👁️ **Preview-Rendering** - HTML-Vorschau mit Viewport-Injection
- 💾 **Export-Funktionen** - Datei, Base64, ZIP-Export

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena15 (12360) ← Dieser Agent
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
  "kuerzel": "htmlp",
  "port": 12360,
  "uptime_seconds": 12.96,
  "templates_available": 1,
  "jinja2_support": true
}
```

### `GET /templates/list`

Verfügbare Templates auflisten.

```bash
curl -X GET http://127.0.0.1:12360/templates/list \
  -H "Authorization: Bearer $BEARER_TOKEN" | jq .
```

### `POST /generate`

HTML aus Template generieren.

```bash
curl -X POST http://127.0.0.1:12360/generate \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "default.html",
    "variables": {
      "title": "My Page",
      "heading": "Welcome",
      "content": "This is generated content."
    },
    "css_framework": "bootstrap",
    "title": "My Page",
    "description": "Generated with opena15",
    "keywords": ["html", "bootstrap", "opena15"]
  }'
```

### `POST /validate`

HTML validieren.

```bash
curl -X POST http://127.0.0.1:12360/validate \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><head><title>Test</title></head><body><h1>Valid HTML</h1></body></html>",
    "validation_level": "strict"
  }'
```

### `POST /preview`

HTML-Vorschau rendern.

```bash
curl -X POST http://127.0.0.1:12360/preview \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><head><title>Preview</title></head><body><h1>Preview Content</h1></body></html>",
    "width": 1920,
    "height": 1080
  }'
```

### `POST /export`

HTML exportieren (file/base64/zip).

```bash
curl -X POST http://127.0.0.1:12360/export \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body>Export Test</body></html>",
    "filename": "export.html",
    "format": "html"
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 14.opena15_html
./bin/start_opena15.sh

# Oder via ops.sh (root)
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
    "service_name": "opena15",
    "endpoint": "http://127.0.0.1:12360",
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
    "params": {
      "template_name": "default.html",
      "variables": {"heading": "Test", "content": "Hello World"},
      "css_framework": "bootstrap",
      "title": "Test Page"
    }
  }'
```

---

## 📁 Verzeichnisstruktur

```
14.opena15_html/
├── main_html_agent.py       # FastAPI Agent Entry Point (750 LOC)
├── bin/
│   ├── start_opena15.sh     # Start-Script
│   └── stop_opena15.sh      # Stop-Script
├── test_opena15.py          # Integration Tests (12 Tests, 100%)
├── data/
│   ├── templates/           # Jinja2 Templates
│   │   └── default.html     # Default Template
│   ├── output/              # Generated HTML Files
│   └── html_history.jsonl  # Append-only History
├── logs/
│   ├── opena15.pid
│   └── opena15.nohup.log
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
# Integration Tests (12 Tests)
python3 test_opena15.py

# Health-Check
curl http://127.0.0.1:12360/health | jq .

# Stop Service
./bin/stop_opena15.sh
```

---

## 📊 Monitoring

```bash
# Service Logs (real-time)
tail -f logs/opena15.nohup.log

# HTML Generation History (JSONL)
tail -f data/html_history.jsonl | jq .
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team
**Letzte Aktualisierung:** 27. November 2025
