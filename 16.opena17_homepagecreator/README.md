# 🤖 opena17 - Homepage Creator

**Agent-ID:** `opena17`  
**Port:** 12363  
**Kürzel:** `hpcreatep`  
**Version:** 3.0  
**Status:** 🟡 **Planned** (PORTIER 3.0 Architecture Ready)  
**Letzte Aktualisierung:** 29. November 2025

---

## 📖 Überblick

**opena17** ist der **Homepage Creator** im ELION Hyper-Dashboard System - ein spezialisierter Agent für die PORTIER 3.0 Multi-Agent-Architektur.

### 🎯 PORTIER 3.0 Integration

opena17 ist architektonisch vorbereitet für die PORTIER 3.0 Integration:

- ✅ **Option-2-Flow Ready:** OpenAI → opena1 → opena2 → kordp → opena17
- ✅ **Port Policy Compliant:** Port 12363 (Backend-Range 12344-12399)
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
curl http://127.0.0.1:12363/health | jq .
```

### `POST /invoke`

Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12363/invoke \
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
cd 16.opena17_homepagecreator
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12363/health | jq .
```

---

## 🔗 Integration mit PORTIER 3.0

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena17",
    "endpoint": "http://127.0.0.1:12363",
    "program_target": "hpcreatep"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "hpcreatep",
    "action": "service_action",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur (Planned)

```txt
16.opena17_homepagecreator/
├── main.py                  # FastAPI Agent Entry Point (planned)
├── config.py                # Konfiguration (planned)
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script (planned)
├── tests/
│   └── test_opena17.py  # Unit-Tests (planned)
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
pytest tests/test_opena17.py -v

# Health-Check
curl http://127.0.0.1:12363/health

# Integration-Test via Portier
python3 ../scripts/test_opena17_integration.py
```

---

## 📊 Monitoring (Planned)

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12363/metrics
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

**opena17** ist der **Homepage Creator Agent** - spezialisiert auf Website-Generierung, CMS-Integration und Deployment.

### Kernfunktionen

- 🏗️ **Site Generator** - Statische Websites generieren (STATIC, 11ty, Hugo)
- 🎨 **Multi-Page Support** - Mehrere Seiten, Navigation, Branding
- 📝 **Custom Styling** - Custom CSS/JS injection, SEO meta tags
- 📦 **Export** - ZIP/TAR.GZ Export mit Assets
- 🚀 **Deployment** - Local, FTP, S3, Netlify, Vercel
- 👁️ **Preview** - Live-Preview ohne Auth

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena17 (12362) ← Dieser Agent
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
curl http://127.0.0.1:12362/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena17",
  "kuerzel": "hpcreatep",
  "port": 12362,
  "uptime_seconds": 317.88,
  "total_sites": 4
}
```

### `POST /site/generate`
Website generieren.

```bash
curl -X POST http://127.0.0.1:12362/site/generate \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "generator": "static",
    "template": "default",
    "pages": [
      {
        "slug": "home",
        "title": "Welcome",
        "content": "<p>Homepage content</p>",
        "is_homepage": true
      }
    ],
    "branding": {
      "site_name": "My Site",
      "tagline": "A great website",
      "color_primary": "#007bff"
    }
  }'
```

### `POST /site/export`
Site als ZIP exportieren.

```bash
curl -X POST http://127.0.0.1:12362/site/export \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "<site_id>",
    "format": "zip",
    "include_assets": true
  }'
```

### `POST /site/deploy`
Site deployen.

```bash
curl -X POST http://127.0.0.1:12362/site/deploy \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "<site_id>",
    "target": "local",
    "target_path": "/var/www/sites"
  }'
```

### `GET /site/structure/{site_id}`
Site-Struktur abrufen.

```bash
curl -X GET http://127.0.0.1:12362/site/structure/<site_id> \
  -H "Authorization: Bearer $BEARER_TOKEN"
```

### `GET /preview/{site_id}/{file_path}`
Preview (ohne Auth).

```bash
open http://127.0.0.1:12362/preview/<site_id>/index.html
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 16.opena17_homepagecreator
./bin/start_opena17.sh

# Oder via ops.sh (root)
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12362/health | jq .
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
    "endpoint": "http://127.0.0.1:12362",
    "program_target": "hpcreatep"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "hpcreatep",
    "action": "generate_site",
    "params": {
      "generator": "static",
      "pages": [
        {
          "slug": "home",
          "title": "Home",
          "content": "<p>Content</p>",
          "is_homepage": true
        }
      ],
      "branding": {
        "site_name": "Test Site"
      }
    }
  }'
```

---

## 📁 Verzeichnisstruktur

```
16.opena17_homepagecreator/
├── main_homepage_agent.py   # FastAPI Entry Point (850 LOC)
├── bin/
│   ├── start_opena17.sh     # Start-Script
│   └── stop_opena17.sh      # Stop-Script
├── test_opena17.py          # Integration Tests (12 Tests, 100%)
├── data/
│   ├── sites/               # Site Metadata (JSON)
│   ├── output/              # Generated Sites (HTML)
│   ├── templates/           # Template Files
│   ├── preview/             # Preview Cache
│   └── homepage_history.jsonl  # Append-only History
├── logs/
│   ├── opena17.pid
│   └── opena17.nohup.log
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
python3 test_opena17.py

# Health-Check
curl http://127.0.0.1:12362/health | jq .

# Stop Service
./bin/stop_opena17.sh
```

---

## 📊 Monitoring

```bash
# Service Logs (real-time)
tail -f logs/opena17.nohup.log

# Homepage History (JSONL)
tail -f data/homepage_history.jsonl | jq .
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 27. November 2025
