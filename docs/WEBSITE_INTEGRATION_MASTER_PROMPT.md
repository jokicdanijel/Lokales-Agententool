# 🌐 WEBSITE INTEGRATION MASTER PROMPT — ELION Hyper-Dashboard 3.0.0

**Projekt:** ELION Hyper-Dashboard 3.0.0  
**System:** Portier OpenAI / Agenten-Stack  
**Zweck:** Website-Anbindungen & Web-Integration  
**Status:** ✅ Production Ready  
**Letzte Aktualisierung:** 21. Dezember 2025

---

## 🎯 Mission

Du bist GitHub Copilot im Repo **Gesamtprojekt-start**. Deine Aufgabe: **produktionsreife** Website-Integrationen entwickeln, die **Policy**, **Ports**, **Option-2-Flow**, **Security** und **Web-Standards** strikt einhalten.

**Keine Platzhalter:** Keine Dummies, keine TODOs, keine halben Implementierungen. Wenn etwas fehlt: implementiere es **final** oder stoppe mit klarem Policy-Grund.

---

## 📋 Systemumgebung (bindend)

### Basis-Konfiguration
- **OS:** Ubuntu 25.04
- **Python:** 3.13.x
- **venv:** venv313 (immer verwenden)
- **Projekt-Root:** `/home/runner/work/Gesamtprojekt-start/Gesamtprojekt-start`

### Port-Policy (erzwingen)
- **Erlaubt:** `12344–12399` (Backend-Services)
- **Verboten:** `8080` (keine Ausnahmen, CI blockt 8080)
- **Externes UI:** Port 8080 darf nur für externe UI-Services (z.B. OpenWebUI) genutzt werden, nie für Backend-Agenten

### Web-Agenten Ports
| Agent | Port | Service | Status |
|-------|------|---------|--------|
| **opena15** | 12361 | HTML Creator | 🟢 Online |
| **opena16** | 12362 | Shop Creator | 🟢 Online |
| **opena17** | 12366 | Homepage Creator | 🟢 Online |
| **opena6** | 12352 | Browser Automation | 🟢 Online |
| **browsep** | 12370 | Browser Portier | 🟢 Online |

---

## 🏗️ Option-2-Flow für Web-Integrationen

### Architektur-Flow (Heilige Regel)

```
┌────────────────────────────────────────────────────────────────┐
│                  WEBSITE INTEGRATION FLOW                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Website/Browser → opena1:12344 → opena2:12345 → kordp:12346  │
│                    ↓ Request71    ↓ CMD Safepoint              │
│                    ↓ Decision72   ↓ RESP Safepoint             │
│                    ↓              ↓                             │
│                    ↓              → Web Agent (opena15/16/17/6) │
│                    ↓                ↓ HTML/CSS/JS Generation    │
│                    ↓                ↓ Browser Automation        │
│                    ↓                ↓ API Calls                 │
│                    ↓                ↓ Result                    │
│                    ↓                ↓                           │
│                    ←────────────────┴────────────────           │
│                    ↓ Response                                   │
│                    ↓                                            │
│                 Website/Browser                                 │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Verboten
- ❌ **Direktcalls:** Website → Web-Agent ohne opena1/opena2
- ❌ **Shortcuts:** opena1 → Web-Agent ohne opena2
- ❌ **Port 8080** für Backend-Services
- ❌ Logging/Safepoints außerhalb opena2
- ❌ Hardcoded Credentials/API Keys

### Pflicht
- ✅ **Jeder Request** muss durch opena1 → opena2 → kordp
- ✅ **CMD & RESP Safepoints** für jede Website-Interaktion
- ✅ **Unicode-Pfeil →** in Safepoint-Dateinamen (U+2192)
- ✅ **Strict JSON Schemas** (`extra="forbid"`)
- ✅ **Secret Masking** in Logs und Responses

---

## 🌐 Web-Agenten Übersicht

### 1. opena15 — HTML Creator (Port 12361)
**Zweck:** HTML-Generierung, Jinja2-Templates, Validierung

**Hauptfunktionen:**
- HTML5/CSS3/JavaScript-Generierung
- Jinja2-Template-Rendering
- HTML-Validierung (W3C)
- Responsive Design
- SEO-Optimierung

**Endpoints:**
```bash
POST /command
  - action: "generate_html"
  - action: "validate_html"
  - action: "render_template"

GET /health
```

**Beispiel-Request:**
```json
{
  "action": "generate_html",
  "params": {
    "template": "landing_page",
    "title": "Meine Website",
    "content": {...},
    "style": "modern"
  }
}
```

### 2. opena16 — Shop Creator (Port 12362)
**Zweck:** E-Commerce-Integration, Shop-Systeme, Payment

**Hauptfunktionen:**
- Produkt-Katalog-Management
- Warenkorb-Integration
- Payment-Gateway-Anbindung (Stripe, PayPal)
- Bestellverwaltung
- Inventar-Tracking

**Endpoints:**
```bash
POST /command
  - action: "create_product"
  - action: "process_order"
  - action: "update_inventory"
  - action: "handle_payment"

GET /health
```

**Beispiel-Request:**
```json
{
  "action": "create_product",
  "params": {
    "name": "Produkt Name",
    "price": 29.99,
    "currency": "EUR",
    "stock": 100,
    "description": "Produktbeschreibung",
    "images": ["url1", "url2"]
  }
}
```

### 3. opena17 — Homepage Creator (Port 12366)
**Zweck:** Vollständige Website-Erstellung, Multi-Page-Sites

**Hauptfunktionen:**
- Multi-Page-Website-Generierung
- CMS-Integration
- Blog-System
- Kontaktformulare
- Analytics-Integration

**Endpoints:**
```bash
POST /command
  - action: "create_website"
  - action: "add_page"
  - action: "update_content"
  - action: "deploy_site"

GET /health
```

**Beispiel-Request:**
```json
{
  "action": "create_website",
  "params": {
    "domain": "example.com",
    "pages": ["home", "about", "contact"],
    "theme": "professional",
    "features": ["blog", "contact_form"]
  }
}
```

### 4. opena6 — Browser Automation (Port 12352)
**Zweck:** Browser-Steuerung, Scraping, Testing

**Hauptfunktionen:**
- Playwright/Selenium-Integration
- Web-Scraping
- Automated Testing
- Screenshot-Generierung
- Form-Automation

**Endpoints:**
```bash
POST /command
  - action: "navigate"
  - action: "click"
  - action: "scrape"
  - action: "screenshot"
  - action: "fill_form"

GET /health
```

**Beispiel-Request:**
```json
{
  "action": "scrape",
  "params": {
    "url": "https://example.com",
    "selectors": ["h1", ".content", "#main"],
    "wait_for": "load"
  }
}
```

---

## 🔒 Security & Compliance

### Secrets Management
```python
# ✅ RICHTIG: Secrets aus ENV
import os
API_KEY = os.getenv("WEBSITE_API_KEY")
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")

# ❌ FALSCH: Hardcoded Secrets
API_KEY = "sk_live_123456789"  # NIEMALS!
```

### Secret Masking in Safepoints
```python
# Automatisch maskiert in opena2:
SECRET_KEYS = [
    "password", "api_key", "token", "secret",
    "stripe_key", "paypal_secret", "auth_token"
]
```

### HTTPS & TLS
- ✅ Alle externen API-Calls über HTTPS
- ✅ Certificate-Validation aktiviert
- ✅ TLS 1.2+ minimum

### Input Validation
```python
from pydantic import BaseModel, Field, validator

class WebsiteRequest(BaseModel, extra="forbid"):
    url: str = Field(..., regex=r'^https?://')
    method: str = Field(..., pattern=r'^(GET|POST|PUT|DELETE)$')
    
    @validator('url')
    def validate_url(cls, v):
        # XSS-Prevention
        if '<script' in v.lower():
            raise ValueError("XSS attempt detected")
        return v
```

---

## 📊 Safepoint-Archivierung für Web-Requests

### Safepoint-Struktur
```
archivp_store/YYYY/MM/DD/
├── SP001234_opena1→opena15_CMD.json      # Request
├── SP001234_opena15→opena2_RESP.json     # Response
├── SP001235_opena1→opena16_CMD.json      # Shop Request
└── SP001235_opena16→opena2_RESP.json     # Shop Response
```

### CMD Safepoint (Website-Request)
```json
{
  "safepoint_id": "SP001234",
  "timestamp": "2025-12-21T10:30:00Z",
  "src": "opena1",
  "dst": "opena15",
  "kind": "CMD",
  "body": {
    "action": "generate_html",
    "params": {
      "template": "landing_page",
      "title": "Beispiel Website",
      "content": {...}
    }
  },
  "strict": true
}
```

### RESP Safepoint (Website-Response)
```json
{
  "safepoint_id": "SP001234",
  "timestamp": "2025-12-21T10:30:05Z",
  "src": "opena15",
  "dst": "opena2",
  "kind": "RESP",
  "body": {
    "status": "success",
    "html": "<html>...</html>",
    "validation": {
      "w3c_valid": true,
      "errors": []
    }
  },
  "strict": true
}
```

---

## 🎨 HTML/CSS/JS Best Practices

### HTML5 Struktur
```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seitentitel</title>
    <meta name="description" content="SEO-Beschreibung">
    <!-- CSS -->
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <header>...</header>
    <main>...</main>
    <footer>...</footer>
    <!-- JS am Ende -->
    <script src="/static/js/main.js"></script>
</body>
</html>
```

### CSS-Konventionen
```css
/* BEM-Namenskonvention */
.block__element--modifier {
    /* Responsive Design */
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
}

/* Mobile-First */
@media (min-width: 768px) {
    .block__element {
        display: flex;
    }
}
```

### JavaScript-Standards
```javascript
// ES6+ Syntax
const apiCall = async (endpoint, data) => {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};
```

---

## 🔌 API-Integration Patterns

### REST-API-Calls
```python
import httpx
from typing import Dict, Any

async def call_external_api(
    url: str,
    method: str = "POST",
    data: Dict[str, Any] = None,
    headers: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Standard-Pattern für externe API-Calls.
    
    ✅ HTTPS-only
    ✅ Timeout: 30s
    ✅ Retry: 3x
    ✅ Error-Handling
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=method,
            url=url,
            json=data,
            headers=headers or {}
        )
        response.raise_for_status()
        return response.json()
```

### GraphQL-Integration
```python
async def graphql_query(
    endpoint: str,
    query: str,
    variables: Dict[str, Any] = None
) -> Dict[str, Any]:
    """GraphQL-Query-Pattern für Website-APIs."""
    payload = {
        "query": query,
        "variables": variables or {}
    }
    return await call_external_api(
        url=endpoint,
        method="POST",
        data=payload
    )
```

### Webhook-Empfang
```python
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.post("/webhook/payment")
async def handle_payment_webhook(request: Request):
    """
    Webhook-Handler für Payment-Events.
    
    ✅ Signature-Validation
    ✅ Replay-Protection
    ✅ Safepoint-Archivierung
    """
    # Validate webhook signature
    signature = request.headers.get("X-Webhook-Signature")
    if not validate_signature(signature, await request.body()):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook
    data = await request.json()
    
    # Archive to opena2
    await save_safepoint(
        src="external_api",
        dst="opena16",
        kind="WEBHOOK",
        body=data
    )
    
    return {"status": "received"}
```

---

## 🧪 Testing & Validation

### Unit-Tests für Web-Agenten
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_html_generation():
    """Test opena15 HTML-Generierung."""
    async with AsyncClient(base_url="http://127.0.0.1:12361") as client:
        response = await client.post("/command", json={
            "action": "generate_html",
            "params": {
                "template": "simple",
                "title": "Test"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "<html" in data["html"]
        assert data["validation"]["w3c_valid"] is True
```

### E2E-Tests (Option-2-Flow)
```python
@pytest.mark.asyncio
async def test_option2_flow_html():
    """Test vollständiger Option-2-Flow für HTML-Generation."""
    # 1. Request an opena1
    opena1_response = await client.post(
        "http://127.0.0.1:12344/log/opena1",
        json={
            "request_id": "test-001",
            "user_query": "Generiere Landing Page",
            "context": {"template": "landing"}
        }
    )
    assert opena1_response.status_code == 200
    
    # 2. Verify Safepoint in opena2
    safepoints = await client.get(
        "http://127.0.0.1:12345/archiv/last?n=1"
    )
    assert len(safepoints.json()) > 0
    
    # 3. Verify Result
    result = opena1_response.json()
    assert result["html"] is not None
```

### Performance-Tests
```python
import asyncio
import time

async def load_test_web_agent(
    agent_port: int,
    num_requests: int = 100
):
    """Load-Test für Web-Agenten."""
    start_time = time.time()
    
    async with AsyncClient() as client:
        tasks = [
            client.post(
                f"http://127.0.0.1:{agent_port}/command",
                json={"action": "health_check"}
            )
            for _ in range(num_requests)
        ]
        responses = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    success_rate = sum(1 for r in responses if r.status_code == 200) / num_requests
    
    print(f"✅ {num_requests} Requests in {elapsed:.2f}s")
    print(f"📈 Throughput: {num_requests/elapsed:.2f} req/s")
    print(f"✓ Success Rate: {success_rate*100:.1f}%")
```

---

## 🚀 Deployment & Operations

### Service-Start (via ops.sh)
```bash
# Einzelner Web-Agent
bin/ops.sh start opena15

# Alle Web-Agenten
bin/ops.sh start opena15 opena16 opena17 opena6

# Vollständiger Stack
bin/ops.sh start
```

### Health-Monitoring
```bash
# Health-Check für alle Web-Agenten
for port in 12361 12362 12366 12352; do
  echo "Port $port:"
  curl -s http://127.0.0.1:$port/health | jq .
done
```

### Logs
```bash
# Tail Web-Agent Logs
tail -f logs/opena15.nohup.log
tail -f logs/opena16.nohup.log
tail -f logs/opena17.nohup.log

# Combined Logs
bin/ops.sh logs
```

---

## 📚 Beispiel-Workflows

### Workflow 1: Landing Page erstellen
```python
async def create_landing_page(title: str, content: dict):
    """Vollständiger Workflow für Landing Page."""
    
    # 1. Request an opena1 (Coordinator)
    request = {
        "request_id": generate_id(),
        "timestamp": datetime.utcnow().isoformat(),
        "source": "api",
        "user_query": f"Erstelle Landing Page: {title}",
        "context": {"template": "landing", "content": content}
    }
    
    # 2. opena1 leitet an opena2 (Archivator)
    # opena2 speichert CMD Safepoint
    
    # 3. opena2 leitet an kordp (Gateway)
    # kordp dispatched an opena15 (HTML Creator)
    
    # 4. opena15 generiert HTML
    html = await generate_html(template="landing", data=content)
    
    # 5. opena15 sendet RESP an opena2
    # opena2 speichert RESP Safepoint
    
    # 6. opena2 sendet zurück an opena1
    # opena1 sendet Response an Client
    
    return html
```

### Workflow 2: E-Commerce-Produkt anlegen
```python
async def create_shop_product(product_data: dict):
    """Workflow für Shop-Produkt-Erstellung."""
    
    # Validierung
    if not validate_product_data(product_data):
        raise ValueError("Invalid product data")
    
    # Option-2-Flow durchlaufen
    result = await execute_option2_flow(
        agent="opena16",
        action="create_product",
        params=product_data
    )
    
    # Inventory aktualisieren
    await execute_option2_flow(
        agent="opena16",
        action="update_inventory",
        params={"product_id": result["product_id"]}
    )
    
    return result
```

### Workflow 3: Website-Scraping
```python
async def scrape_website(url: str, selectors: list):
    """Workflow für Website-Scraping."""
    
    # Security: URL-Validation
    if not url.startswith("https://"):
        raise ValueError("Only HTTPS URLs allowed")
    
    # Browser-Agent aufrufen
    result = await execute_option2_flow(
        agent="opena6",
        action="scrape",
        params={
            "url": url,
            "selectors": selectors,
            "wait_for": "load"
        }
    )
    
    return result["data"]
```

---

## 🔧 Troubleshooting

### Häufige Fehler

#### 1. Port-Konflikte
```bash
# Problem: Port bereits belegt
Error: Address already in use (Port 12361)

# Lösung:
lsof -i :12361
kill -9 <PID>
bin/ops.sh start opena15
```

#### 2. Option-2-Flow verletzt
```bash
# Problem: Direktcall ohne opena2
Error: Safepoint missing for request XYZ

# Lösung: Immer über opena1 routen
# ❌ FALSCH:
curl http://127.0.0.1:12361/command

# ✅ RICHTIG:
curl http://127.0.0.1:12344/log/opena1 \
  -H "Content-Type: application/json" \
  -d '{"user_query": "..."}'
```

#### 3. Secrets nicht geladen
```bash
# Problem: API-Key fehlt
Error: WEBSITE_API_KEY not found

# Lösung: .env prüfen
grep WEBSITE_API_KEY .env
# Falls fehlt:
echo "WEBSITE_API_KEY=your_key_here" >> .env
bin/ops.sh restart opena15
```

#### 4. HTML-Validierung fehlgeschlagen
```python
# Problem: W3C-Validierung schlägt fehl
Error: HTML validation failed: Unclosed tag <div>

# Lösung: Template korrigieren
# Validierung deaktivieren (nur Development):
{
  "action": "generate_html",
  "params": {
    "validate": false  # Nur für Development!
  }
}
```

---

## 📖 Referenzen

### Wichtige Dateien
- **Master Prompt:** `.github/copilot-master-prompt.md`
- **Operations:** `bin/ops.sh`
- **ENV-Template:** `mcp_server/.env.example`
- **Agent-Mapping:** `bin/ops.sh` (AGENTS array)

### Dokumentation
- **System-Architektur:** `README.md`
- **Operations Guide:** `docs/OPERATIONS.md`
- **API-Dokumentation:** `docs/README_STACK_START.md`

### Web-Agenten
- **opena15:** `14.opena15_html/MASTER_PROMPT.md`
- **opena16:** `15.opena16_shop/`
- **opena17:** `16.opena17_homepagecreator/MASTER_PROMPT.md`
- **opena6:** `5.opena6_browser/MASTER_PROMPT.md`

---

## ✅ Checkliste für neue Website-Integration

- [ ] Port aus Range 12344-12399 gewählt
- [ ] Port NICHT 8080
- [ ] FastAPI-Service mit `/health` und `/command` Endpoints
- [ ] Option-2-Flow implementiert (opena1 → opena2 → kordp → Agent)
- [ ] Safepoint-Archivierung aktiviert (CMD + RESP)
- [ ] Unicode-Pfeil → in Safepoint-Namen
- [ ] Strict JSON Schemas (`extra="forbid"`)
- [ ] Secrets aus ENV geladen (nicht hardcoded)
- [ ] Bearer-Token-Auth implementiert
- [ ] Input-Validierung (XSS, SQL-Injection)
- [ ] HTTPS für externe APIs
- [ ] Error-Handling & Logging
- [ ] Unit-Tests geschrieben
- [ ] E2E-Tests (Option-2-Flow)
- [ ] README.md und MASTER_PROMPT.md erstellt
- [ ] Agent in `bin/ops.sh` AGENTS-Array registriert

---

**Maintainer:** Danijel Jokic (ELION Team)  
**Letzte Aktualisierung:** 21. Dezember 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
