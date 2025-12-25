# 🚀 OPENA15 HTML Creator - Production Prompt

**Version:** 1.0
**Datum:** 27. November 2025
**Status:** ✅ PRODUCTION-READY
**Architektur:** Option-2-Flow konform

---

## 🎯 Systemübersicht

**opena15** ist ein **FastAPI-basierter HTML-Generator-Service**, der:

- **Jinja2-Templates** rendert
- **CSS-Frameworks** integriert (Bootstrap, Tailwind, Bulma)
- **HTML validiert** (BeautifulSoup4)
- **SEO-Optimierung** durchführt
- **Export-Funktionen** bereitstellt

**WICHTIG:** opena15 ist **KEIN** autonomer File-Scanner, sondern ein **API-Service** mit strict Endpoints!

---

## 📡 API-Endpoints (Vollständig)

### 1. Health-Check

```bash
GET http://127.0.0.1:12360/health
```

**Response:**

```json
{
  "status": "ok",
  "service": "opena15",
  "kuerzel": "htmlp",
  "port": 12360,
  "uptime_seconds": 12345.67,
  "templates_available": 3,
  "jinja2_support": true
}
```

---

### 2. HTML generieren (KERN-ENDPOINT)

```bash
POST http://127.0.0.1:12360/generate
Content-Type: application/json
Authorization: Bearer c899b90d-faf8-485b-afa4-078357cf5313
```

**Request Body (strict Schema):**

```json
{
  "template_name": "agent_dashboard.html.j2",
  "variables": {
    "agent_id": "opena16",
    "agent_name": "Shop Agent",
    "port": 12362,
    "features": ["Feature 1", "Feature 2"]
  },
  "css_framework": "bootstrap",
  "custom_css": "body { margin: 0; }",
  "title": "Shop Agent Dashboard",
  "description": "E-Commerce Management",
  "keywords": ["shop", "ecommerce", "portier"]
}
```

**Response:**

```json
{
  "html": "<!DOCTYPE html>...",
  "template_used": "agent_dashboard.html.j2",
  "variables_applied": 4,
  "css_framework": "bootstrap",
  "validation": "passed",
  "file_path": "/path/to/output/file.html"
}
```

**Schema-Regeln (STRIKT):**

- `template_name`: **Pflicht**, max 200 Zeichen, muss in `data/templates/` existieren
- `variables`: **Optional**, Dict mit beliebigen Variablen
- `css_framework`: **Optional**, Enum: `none|bootstrap|tailwind|bulma|custom`
- `custom_css`: **Optional**, max 10000 Zeichen
- `title`: **Optional**, max 200 Zeichen, Default: "Generated Page"
- `description`: **Optional**, max 500 Zeichen
- `keywords`: **Optional**, Liste max 20 Einträge
- **`extra="forbid"`** → Keine zusätzlichen Felder erlaubt!

---

### 3. Template validieren

```bash
POST http://127.0.0.1:12360/validate
Content-Type: application/json
Authorization: Bearer c899b90d-faf8-485b-afa4-078357cf5313
```

**Request:**

```json
{
  "html": "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>",
  "validation_level": "standard"
}
```

**Response:**

```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Missing meta viewport tag"],
  "validation_level": "standard",
  "stats": {
    "tags_total": 5,
    "tags_closed": 5,
    "meta_tags": 1
  }
}
```

---

### 4. Template-Liste abrufen

```bash
GET http://127.0.0.1:12360/templates
Authorization: Bearer c899b90d-faf8-485b-afa4-078357cf5313
```

**Response:**

```json
{
  "templates": [
    {
      "name": "agent_dashboard.html.j2",
      "size": 7824,
      "modified": "2025-11-27T16:44:00Z"
    },
    {
      "name": "simple.html.j2",
      "size": 1234,
      "modified": "2025-11-20T10:00:00Z"
    }
  ],
  "total": 2
}
```

---

## 🔧 Production Workflow (KORREKT)

### Schritt 1: Template erstellen/kopieren

```bash
# Template in opena15/data/templates/ ablegen
cp my_template.html.j2 /path/to/14.opena15_html/data/templates/
```

**Template-Beispiel (Jinja2):**

```html
<!DOCTYPE html>
<html lang="de">
  <head>
    <meta charset="UTF-8" />
    <title>{{ title }}</title>
    {% if css_framework == 'bootstrap' %}
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    {% endif %}
  </head>
  <body>
    <h1>{{ heading }}</h1>
    <ul>
      {% for item in items %}
      <li>{{ item }}</li>
      {% endfor %}
    </ul>
  </body>
</html>
```

---

### Schritt 2: Templates auflisten

```bash
curl -s http://127.0.0.1:12360/templates \
  -H "Authorization: Bearer c899b90d-faf8-485b-afa4-078357cf5313" | jq .
```

---

### Schritt 3: HTML generieren

```bash
curl -X POST http://127.0.0.1:12360/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer c899b90d-faf8-485b-afa4-078357cf5313" \
  -d '{
    "template_name": "my_template.html.j2",
    "variables": {
      "title": "Mein Produktions-HTML",
      "heading": "Willkommen",
      "items": ["Feature 1", "Feature 2", "Feature 3"]
    },
    "css_framework": "bootstrap",
    "title": "Production Page",
    "description": "Automatisch generierte Seite",
    "keywords": ["production", "html", "portier"]
  }' | jq .
```

**Resultat:**

- ✅ HTML generiert
- ✅ Bootstrap eingebunden
- ✅ Variablen gerendert
- ✅ Validiert
- ✅ Gespeichert in `data/output/`

---

### Schritt 4: HTML validieren (optional)

```bash
curl -X POST http://127.0.0.1:12360/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer c899b90d-faf8-485b-afa4-078357cf5313" \
  -d '{
    "html": "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>",
    "validation_level": "strict"
  }' | jq .
```

---

## 🤖 Python-Automatisierung (Production-Script)

```python
#!/usr/bin/env python3
"""
Production HTML Generator via opena15 API
"""
import requests
import json
from pathlib import Path

OPENA15_URL = "http://127.0.0.1:12360"
BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

def generate_html(template_name: str, variables: dict, **kwargs):
    """
    Generiere HTML via opena15 /generate Endpoint

    Args:
        template_name: Template-Dateiname (in data/templates/)
        variables: Dict mit Jinja2-Variablen
        **kwargs: css_framework, title, description, keywords, custom_css
    """
    payload = {
        "template_name": template_name,
        "variables": variables,
        **kwargs
    }

    response = requests.post(
        f"{OPENA15_URL}/generate",
        json=payload,
        headers=HEADERS,
        timeout=10
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ HTML generiert: {result['file_path']}")
        print(f"   Template: {result['template_used']}")
        print(f"   Framework: {result['css_framework']}")
        print(f"   Validierung: {result['validation']}")
        return result
    else:
        print(f"❌ Fehler: HTTP {response.status_code}")
        print(response.text)
        return None

# Beispiel 1: Dashboard für Agent
generate_html(
    template_name="agent_dashboard.html.j2",
    variables={
        "agent_id": "opena16",
        "agent_name": "Shop Agent",
        "port": 12362,
        "features": [
            "Product Management",
            "Order Processing",
            "Inventory Tracking"
        ]
    },
    css_framework="bootstrap",
    title="Shop Agent Dashboard",
    keywords=["shop", "agent", "portier"]
)

# Beispiel 2: Landing Page
generate_html(
    template_name="landing_page.html.j2",
    variables={
        "company": "ELION Systems",
        "tagline": "Enterprise Multi-Agent Platform",
        "cta_text": "Get Started"
    },
    css_framework="tailwind",
    title="ELION - Enterprise Platform",
    description="Powerful multi-agent system for automation"
)

# Beispiel 3: Bulk-Generierung (17 Agenten)
AGENTS = [
    {"id": "opena3", "name": "OpenWebUI Terminal", "port": 12347},
    {"id": "opena4", "name": "Telegram Agent", "port": 12348},
    # ... weitere Agenten
]

for agent in AGENTS:
    generate_html(
        template_name="agent_dashboard.html.j2",
        variables={
            "agent_id": agent["id"],
            "agent_name": agent["name"],
            "port": agent["port"]
        },
        css_framework="bootstrap"
    )
```

---

## 📊 Batch-Processing (Production)

**Skript:** `batch_generate.py`

```python
#!/usr/bin/env python3
"""
Batch HTML Generation für Production
"""
import requests
import json
import time
from pathlib import Path

OPENA15_URL = "http://127.0.0.1:12360"
BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"

def batch_generate(tasks: list):
    """
    Generiere mehrere HTML-Dateien in einem Batch

    Args:
        tasks: Liste von Dicts mit {template_name, variables, ...}
    """
    results = []

    for i, task in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] Generiere {task['template_name']}...", end=" ")

        try:
            response = requests.post(
                f"{OPENA15_URL}/generate",
                json=task,
                headers={
                    "Authorization": f"Bearer {BEARER_TOKEN}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ {Path(result['file_path']).name}")
                results.append({"task": task, "success": True, "result": result})
            else:
                print(f"❌ HTTP {response.status_code}")
                results.append({"task": task, "success": False, "error": response.text})

        except Exception as e:
            print(f"❌ Fehler: {e}")
            results.append({"task": task, "success": False, "error": str(e)})

        time.sleep(0.05)  # Rate limiting

    # Zusammenfassung
    success = sum(1 for r in results if r["success"])
    print(f"\n{'='*60}")
    print(f"✅ Erfolgreich: {success}/{len(tasks)}")
    print(f"❌ Fehler: {len(tasks) - success}/{len(tasks)}")

    return results

# Production Tasks
tasks = [
    {
        "template_name": "agent_dashboard.html.j2",
        "variables": {"agent_id": "opena3", "agent_name": "OpenWebUI", "port": 12347},
        "css_framework": "bootstrap"
    },
    {
        "template_name": "agent_dashboard.html.j2",
        "variables": {"agent_id": "opena4", "agent_name": "Telegram", "port": 12348},
        "css_framework": "bootstrap"
    },
    # ... weitere Tasks
]

batch_generate(tasks)
```

---

## ✅ Validierung & Quality Assurance

### 1. HTML-Validierung

```bash
curl -X POST http://127.0.0.1:12360/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -d @generated.html
```

### 2. Template-Syntax-Check

```python
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

try:
    env = Environment(loader=FileSystemLoader('data/templates'))
    template = env.get_template('my_template.html.j2')
    print("✅ Template-Syntax korrekt")
except TemplateSyntaxError as e:
    print(f"❌ Syntax-Fehler: {e}")
```

### 3. Regression-Tests

```bash
# Test-Suite ausführen
pytest tests/test_html_generation.py -v
```

---

## 🔐 Security & Best Practices

### 1. Bearer Token NIEMALS hardcoden

```python
# ❌ FALSCH:
BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"

# ✅ RICHTIG:
import os
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
```

### 2. Input-Validierung

```python
# Variablen sanitizen
variables = {
    "user_input": user_input.strip()[:200]  # Max 200 chars
}
```

### 3. Error-Handling

```python
try:
    response = requests.post(...)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    logger.error(f"API-Fehler: {e}")
except requests.exceptions.Timeout:
    logger.error("Timeout - opena15 antwortet nicht")
```

---

## 📈 Monitoring & Logging

### opena15 Logs

```bash
# Live-Logs
tail -f 14.opena15_html/logs/opena15.nohup.log

# API-Calls filtern
grep "POST /generate" 14.opena15_html/logs/opena15.nohup.log
```

### Metriken sammeln

```python
import time

start = time.time()
result = generate_html(...)
duration = time.time() - start

print(f"Generierung: {duration:.2f}s")
```

---

## 🚀 Deployment

### 1. opena15 starten

```bash
./bin/start_opena15.sh
# oder
cd 14.opena15_html
nohup python3 main_html_agent.py > logs/opena15.nohup.log 2>&1 &
```

### 2. Health-Check

```bash
curl http://127.0.0.1:12360/health | jq .
```

### 3. Production-Script ausführen

```bash
python3 production_generate.py
```

---

## 🔮 Advanced Features

### 1. Template-Versionierung

```bash
# Templates in Git tracken
cd 14.opena15_html/data/templates
git add *.j2
git commit -m "feat: neue Dashboard-Templates"
```

### 2. Caching

```python
# HTML-Cache
from functools import lru_cache

@lru_cache(maxsize=100)
def generate_cached(template_name, variables_json):
    return generate_html(template_name, json.loads(variables_json))
```

### 3. Preview-Server

```bash
# HTML-Output serven
cd 14.opena15_html/data/output
python3 -m http.server 8000
# → http://localhost:8000
```

---

## 📝 Troubleshooting

### Problem: 422 Unprocessable Entity

**Ursache:** Schema-Validierung fehlgeschlagen

**Lösung:**

```python
# Prüfe Payload gegen Schema
payload = {
    "template_name": "file.j2",  # ✅ Pflichtfeld
    "variables": {},             # ✅ Muss Dict sein
    # "extra_field": "value"     # ❌ Verboten (extra="forbid")
}
```

### Problem: Template not found

**Ursache:** Template nicht in `data/templates/`

**Lösung:**

```bash
ls 14.opena15_html/data/templates/
cp my_template.j2 14.opena15_html/data/templates/
```

### Problem: opena15 offline

**Ursache:** Service nicht gestartet

**Lösung:**

```bash
./bin/start_opena15.sh
curl http://127.0.0.1:12360/health
```

---

## 🎓 Zusammenfassung

**opena15 ist:**

- ✅ FastAPI-Service mit strict Endpoints
- ✅ Jinja2-Template-Renderer
- ✅ HTML-Validator
- ✅ API-basiert (kein File-Scanner)

**opena15 ist NICHT:**

- ❌ Autonomer File-Browser
- ❌ Selbst-modifizierendes System
- ❌ Symlink-Generator

**Production Workflow:**

1. Template in `data/templates/` ablegen
2. POST zu `/generate` mit strict Schema
3. HTML wird in `data/output/` gespeichert
4. Validierung via `/validate` (optional)

**Status:** ✅ **PRODUCTION-READY**

---

**Erstellt:** 27. November 2025
**Version:** 1.0
**Autor:** ELION/Portier System
