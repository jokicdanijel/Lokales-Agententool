# opena6 — Browser Automation Agent

**Deterministic Web Automation mit Compliance-Enforcement**

## Überblick

opena6 ist ein FastAPI-basierter Agent zur automatisierten Web-Automation. Er führt Browser-Playbooks deterministisch aus, archiviert alle Artefakte (Screenshots, HTML, HAR, PDFs) und unterliegt strikten Compliance-Kontrollen (Domain-Allowlist, robots.txt-Beachtung, Rate-Limiting).

**Kernmerkmale:**
- 🎬 Playwright-basierte Browser-Automation (Chromium, Firefox, WebKit)
- 🔐 Domain-Allowlist + robots.txt-Enforcement
- 📦 Artifact-Capture (Screenshots, HTML, HAR, PDFs)
- ♻️ Deterministische Playbook-Ausführung (wiederholbar)
- 📊 Prometheus-Metriken + strukturierte JSONL-Logs
- 🔗 Safepoint-Integration mit opena2 (Archivator)

---

## Installation

### 1. Lokale Entwicklung

```bash
# Repository navigieren
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Virtual Environment aktivieren
source .venv/bin/activate

# Dependencies installieren
pip install -r 5.opena6_browser/requirements.txt

# Browser-Runtime installieren
python3 -m playwright install chromium
```

### 2. Docker-Deployment

```bash
# Bau des Images
cd 5.opena6_browser
docker build -t opena6:latest .

# Container starten
docker run -d \
  --name opena6 \
  -p 127.0.0.1:12349:12349 \
  -e OPENA1_URL=http://opena1:12344 \
  -e OPENA2_URL=http://opena2:12345 \
  opena6:latest

# Compose (mit opena1 + opena2)
docker-compose up -d
```

### 3. systemd-Service

```bash
# Service installieren
sudo cp 5.opena6_browser/deploy/opena6_browser.service /etc/systemd/system/

# Service starten
sudo systemctl daemon-reload
sudo systemctl start opena6_browser
sudo systemctl enable opena6_browser

# Status prüfen
sudo systemctl status opena6_browser
```

---

## Quickstart

### 1. Health-Check

```bash
curl http://127.0.0.1:12349/health | jq .
# Erwartung:
# {
#   "service": "opena6",
#   "status": "ok",
#   "component": "browser",
#   "port": 12349,
#   "browser": "playwright-chromium",
#   "ts": "2025-11-10T13:37:15.512Z"
# }
```

### 2. Playbook ausführen (Einfaches Beispiel)

```bash
curl -X POST http://127.0.0.1:12349/run \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-001",
    "steps": [
      {
        "action": "goto",
        "url": "https://example.org",
        "wait": "load"
      },
      {
        "action": "screenshot",
        "label": "homepage",
        "full_page": false
      },
      {
        "action": "extract",
        "mode": "text",
        "selector": "h1",
        "label": "page_title"
      }
    ],
    "compliance": {
      "allow_domains": ["example.org"],
      "obey_robots": true
    },
    "archiv": {
      "attach_screenshot": true,
      "attach_html": true
    }
  }' | jq .
```

Erwartete Antwort:
```json
{
  "request_id": "test-001",
  "status": "success",
  "artifacts": {
    "screenshots": [
      {
        "label": "homepage",
        "path": "archivp/2025/11/10/screenshot_homepage_1731225435.png",
        "sha256": "abc123def456...",
        "size_bytes": 65536,
        "mime_type": "image/png"
      }
    ],
    "html": [
      {
        "label": "page_1",
        "path": "archivp/2025/11/10/page_page_1_1731225435.html",
        "mime_type": "text/html"
      }
    ],
    "extractions": {
      "page_title": "Example Domain"
    }
  },
  "timings": {
    "total_ms": 3840
  }
}
```

---

## Playbook-Referenz

### Verfügbare Aktionen

| Action | Beschreibung | Parameter |
|--------|-------------|-----------|
| `goto` | Navigiere zu URL | `url`, `wait` (networkidle/load/domcontentloaded) |
| `fill` | Fülle Formularfeld | `selector`, `text` |
| `click` | Klick auf Element | `selector` |
| `submit` | Absenden von Formular | `selector` |
| `wait_for` | Warte auf Selektor | `selector`, `timeout_ms` |
| `screenshot` | Mache Screenshot | `label`, `full_page` |
| `extract` | Extrahiere Inhalt | `selector`, `mode` (text/html/attribute) |
| `select` | Wähle aus Dropdown | `selector`, `text` |
| `hover` | Hover über Element | `selector` |
| `keyboard` | Keyboard-Input | `keys` |
| `wait` | Warte (Pause) | `timeout_ms` |

### Extract-Modi

```bash
# Text-Extraktion
{
  "action": "extract",
  "mode": "text",
  "selector": "#kpi",
  "label": "kpi_value"
}
# → Extrahiert: "123.45"

# HTML-Extraktion
{
  "action": "extract",
  "mode": "html",
  "selector": "#section",
  "label": "section_html"
}

# Attribute
{
  "action": "extract",
  "mode": "attribute",
  "selector": "img",
  "attribute": "src",
  "label": "image_url"
}

# Count
{
  "action": "extract",
  "mode": "count",
  "selector": "tr",
  "label": "row_count"
}
```

### Komplexes Beispiel (Login + Datenextraktion)

```json
{
  "request_id": "prod-001",
  "steps": [
    {
      "action": "goto",
      "url": "https://app.example.org/login",
      "wait": "load"
    },
    {
      "action": "screenshot",
      "label": "login_page"
    },
    {
      "action": "fill",
      "selector": "input[name=username]",
      "text": "sealed_user_123"
    },
    {
      "action": "fill",
      "selector": "input[name=password]",
      "text": "sealed_pass_456"
    },
    {
      "action": "click",
      "selector": "button[type=submit]"
    },
    {
      "action": "wait_for",
      "selector": "#dashboard",
      "timeout_ms": 15000
    },
    {
      "action": "screenshot",
      "label": "after_login"
    },
    {
      "action": "extract",
      "mode": "text",
      "selector": "#account-balance",
      "label": "balance"
    },
    {
      "action": "extract",
      "mode": "html",
      "selector": "#transactions-table",
      "label": "transactions_html"
    }
  ],
  "compliance": {
    "allow_domains": ["app.example.org"],
    "obey_robots": true,
    "legal_basis": "contractual"
  },
  "archiv": {
    "attach_screenshot": true,
    "attach_html": true,
    "attach_har": true,
    "attach_pdf": false
  },
  "strict": true
}
```

---

## Compliance & Sicherheit

### Domain-Allowlist

```bash
# Nur erlaubte Domänen dürfen besucht werden
"compliance": {
  "allow_domains": ["example.org", "app.example.org"],
  "obey_robots": true
}
```

**Enforcement:** Vor Ausführung wird jeder `goto`-Schritt geprüft. Bei Domain-Mismatch: NACK (keine Ausführung).

### robots.txt-Beachtung

```bash
"compliance": {
  "obey_robots": true
}
```

**Behavior:**
- Fetcht `robots.txt` vom Server
- Prüft Disallow-Pfade
- Blockt zuwiderlaufende Requests mit Policy-Fehler

### Rate-Limiting

```bash
"rate_limit": {
  "per_domain_rps": 1.0  # 1 Request pro Sekunde
}
```

Automatische Verzögerung zwischen Domain-Requests.

### Secrets Handling

**WICHTIG:** Passwörter, Tokens, IBANs werden **NICHT** im Klartext übergeben. Der Koordinator (opena1) entschlüsselt versiegelte Geheimnisse zur Laufzeit:

```bash
# ❌ FALSCH (Klartext)
"text": "mypassword123"

# ✅ RICHTIG (sealed/encrypted)
"text": "sealed_abc123def456xyz789"
```

### Credential Masking

Logs + HAR werden automatisch bereinigt:
- Authorization-Header entfernt
- Cookie-Header maskiert
- Password-Felder anonymisiert

---

## Archivierung & Artefakte

### Safepoints (opena2)

Nach erfolgreichem Run wird ein RESP-Safepoint geschrieben:

```bash
# Dateiname: SP<timestamp>_opena6→opena2_RESP.json
# Ablage: archivp/2025/11/10/

{
  "ts": "2025-11-10T13:37:15.512Z",
  "src": "opena6",
  "dst": "opena2",
  "kind": "RESP",
  "request_id": "test-001",
  "payload": {
    "status": "success",
    "artifacts": {...},
    "timings": {...}
  }
}
```

### Artefakt-Typen

| Typ | Format | Nutzung |
|-----|--------|--------|
| Screenshots | PNG | Visuelle Dokumentation |
| HTML-Dumps | HTML | Seitenstruktur-Archiv |
| HAR | JSON | Netzwerk-Traffic-Analyse |
| PDF | PDF | Druck/Export (optional) |
| Extractions | JSON | Strukturierte Daten |

---

## Monitoring & Observability

### Health-Endpoints

```bash
# Health
curl http://127.0.0.1:12349/health

# Readiness
curl http://127.0.0.1:12349/ready

# Metriken (Prometheus)
curl http://127.0.0.1:12349/metrics

# Status
curl http://127.0.0.1:12349/api/status
```

### Logs (JSONL)

```bash
# Abrufen
ls logs/opena6/2025/11/10/

# Format (jede Zeile ein Event):
{
  "ts": "2025-11-10T13:37:15.512Z",
  "request_id": "test-001",
  "step": 1,
  "action": "click",
  "selector": "button[type=submit]",
  "elapsed_ms": 142,
  "note": "ok"
}
```

### Metriken

```
opena6_runs_total{status="success|failed|canceled"} X
opena6_duration_ms_bucket{le="1000|5000|10000"} X
opena6_artifacts_bytes_total X
opena6_rate_limit_delays_total X
```

---

## Tests

### Unit Tests (ohne Browser)

```bash
pytest tests/test_browser_service.py -v

# Nur Mock-Tests
pytest tests/test_browser_service.py::TestMockExecutor -v

# Coverage
pytest tests/test_browser_service.py --cov=5.opena6_browser
```

### Integration Tests (mit Browser)

```bash
# Benötigt laufenden opena6
pytest tests/test_browser_service.py::TestBrowserExecution -v

# Test gegen Staging-Site
curl -X POST http://127.0.0.1:12349/api/test-playbook | jq .
```

---

## Fehlerbehebung

### Browser startet nicht

```bash
# Logs prüfen
tail -f logs/opena6.nohup.log

# Playwright-Runtime check
python3 -m playwright install chromium

# Manual test
python3 -c "
from playwright.async_api import async_playwright
import asyncio

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        print('✅ Browser OK')
        await browser.close()

asyncio.run(test())
"
```

### Domain-Fehler (Policy Violation)

```bash
# ✗ Fehler: "Domain not in allowlist"
# Lösung: Domain in compliance.allow_domains hinzufügen

# ✗ Fehler: "robots.txt disallows"
# Lösung: obey_robots=false ODER mit Domänen-Owner abstimmen
```

### Timeout bei Seite

```bash
# Step-Timeout erhöhen
{
  "action": "wait_for",
  "selector": "#element",
  "timeout_ms": 30000  # 30s
}
```

### Artefakte zu groß

```bash
# Artifact-Limit in Config
MAX_ARTIFACT_SIZE_MB=50

# Full-page Screenshots begrenzen
{
  "action": "screenshot",
  "full_page": false  # Nur Viewport
}
```

---

## Best Practices

✅ **DO:**
- Stabile Selektoren verwenden (`data-testid` > CSS-Akrobatik)
- Explizit warten (`wait_for` vor kritischen Steps)
- Atomic Steps (ein Step = eine Aktion)
- Secrets versiegeln (sealed secrets)
- Nur erforderliche Artefakte archivieren

❌ **DON'T:**
- Passwörter im Klartext übergeben
- Zu lange Playbooks (>50 Steps)
- Rate-Limits ignorieren
- robots.txt-Verletzungen
- Seiten-Layout-Annahmen treffen

---

## Performance-SLOs

| Metrik | Ziel |
|--------|------|
| Erfolgsquote | ≥ 95% (bei stabilen Zielen) |
| P95-Latenz | ≤ 6 s (7-Schritt-Playbook) |
| Policy-NACK-Rate | 0% (Pre-Validation) |
| Artifact-Upload | < 2s (pro Datei) |

---

## API-Referenz

Siehe [API Docs](http://127.0.0.1:12349/docs) (Swagger UI) oder [ReDoc](http://127.0.0.1:12349/redoc).

---

## Support & Debugging

```bash
# Logs streamen
tail -f logs/opena6.nohup.log

# Metriken live
watch -n 1 'curl -s http://127.0.0.1:12349/metrics | head -20'

# Healthcheck loop
while true; do
  curl -s http://127.0.0.1:12349/health | jq .
  sleep 2
done

# opena2 Archiv-Index
curl http://127.0.0.1:12345/archiv/last?n=5 | jq .
```

---

**Letzte Aktualisierung:** 10. November 2025  
**Status:** Production-Ready ✅
