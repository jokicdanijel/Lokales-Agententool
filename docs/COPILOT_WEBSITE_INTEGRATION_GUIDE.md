# 🤖 GitHub Copilot — Website Integration Guide

**Zweck:** Optimale Nutzung von GitHub Copilot für Website-Integrationen im ELION System  
**Zielgruppe:** Entwickler mit GitHub Copilot  
**Letzte Aktualisierung:** 21. Dezember 2025

---

## 🎯 Copilot-Kontext richtig laden

### Methode 1: Spezifische Dateien referenzieren

```
@docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md
@14.opena15_html/MASTER_PROMPT.md

Erstelle eine moderne Landing Page mit Hero-Section, Features-Grid und Kontaktformular.
Verwende opena15 (HTML Creator) und halte Option-2-Flow ein.
```

### Methode 2: Multiple Context Files

```
@docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md
@docs/EXTERNAL_WEBSITE_API_INTEGRATION.md
@.github/copilot-master-prompt.md

Integriere Stripe Payment API in opena16 (Shop Creator) mit:
- Webhook-Handler
- Signature-Validation
- Payment-Intent-Erstellung
- Error-Handling
```

### Methode 3: Agent-Spezifisch

```
@5.opena6_browser/MASTER_PROMPT.md
@docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md

Schreibe Web-Scraping-Script mit Playwright:
- Scrape Produktdaten von example.com
- Extrahiere Titel, Preis, Bilder
- Speichere als JSON
- Halte Option-2-Flow ein
```

---

## 📋 Use-Case Templates

### 1. Landing Page erstellen

**Prompt:**
```
@docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md
@14.opena15_html/MASTER_PROMPT.md

Erstelle eine Landing Page für eine SaaS-App:

Anforderungen:
- Hero-Section mit Gradient-Background
- Features-Grid (3 Spalten)
- Pricing-Tabelle (3 Pläne)
- FAQ-Section (Accordion)
- Kontaktformular
- Footer mit Social-Links

Technische Anforderungen:
- Responsive Design (Mobile-First)
- HTML5/CSS3/Vanilla JS
- W3C-validiert
- Option-2-Flow via opena15 (Port 12361)
- Safepoint-Archivierung

Output: Python-Script das HTML generiert
```

**Erwartetes Ergebnis:**
- Vollständiges Python-Script
- FastAPI-Integration
- Option-2-Flow-compliant
- Produktionsreif

---

### 2. E-Commerce-Shop mit Stripe

**Prompt:**
```
@docs/EXTERNAL_WEBSITE_API_INTEGRATION.md
@15.opena16_shop/
@.github/copilot-master-prompt.md

Implementiere E-Commerce-Shop mit Stripe-Integration:

Features:
- Produkt-Katalog (REST-API)
- Warenkorb (Session-basiert)
- Stripe Checkout
- Webhook für Payment-Events
- E-Mail-Bestätigung via opena7

Technische Details:
- opena16 (Shop Creator, Port 12362)
- Stripe Secret Key aus ENV
- Webhook-Signature-Validation
- Option-2-Flow für alle Requests
- Safepoint-Archivierung

Inkludiere:
1. FastAPI-Router
2. Pydantic-Models
3. Stripe-Client-Wrapper
4. Webhook-Handler
5. Unit-Tests
```

**Erwartetes Ergebnis:**
- Vollständige Shop-Implementation
- Security-hardened
- Production-ready
- Getestet

---

### 3. Blog-System mit CMS

**Prompt:**
```
@docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md
@16.opena17_homepagecreator/MASTER_PROMPT.md

Erstelle Blog-System für Tech-Blog:

Features:
- Multi-Post-Blog
- Kategorien & Tags
- Markdown-Support
- Kommentar-System
- RSS-Feed
- Search-Funktion
- Admin-Interface

Technische Details:
- opena17 (Homepage Creator, Port 12366)
- SQLite für Posts
- Markdown → HTML (Python-Markdown)
- Option-2-Flow
- REST-API für Posts

Inkludiere:
1. Database-Schema
2. CRUD-Operations
3. Template-Rendering
4. Admin-UI
5. Public-Blog-View
```

---

### 4. Website-Scraping mit Playwright

**Prompt:**
```
@docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md
@5.opena6_browser/MASTER_PROMPT.md

Implementiere Web-Scraping-System mit Playwright:

Ziel: Scrape E-Commerce-Website für Preisvergleich

Features:
- Headless-Browser (Playwright)
- Multi-Page-Scraping
- Screenshot für Dokumentation
- JSON-Export
- Error-Handling & Retries
- Rate-Limiting

Technische Details:
- opena6 (Browser Automation, Port 12352)
- Option-2-Flow
- Async/Await
- Safepoint-Archivierung

Selektoren:
- Produktliste: ".product-card"
- Titel: "h2.product-title"
- Preis: ".product-price"
- Bild: "img.product-image"

Output: Python-Script mit FastAPI-Endpoint
```

---

### 5. Contact Form mit E-Mail

**Prompt:**
```
@docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md
@14.opena15_html/MASTER_PROMPT.md
@6.opena7_email/

Erstelle Contact Form mit E-Mail-Integration:

Frontend (opena15):
- HTML-Formular mit Validierung
- Fields: Name, Email, Subject, Message
- Client-Side-Validation (JS)
- AJAX-Submit
- Success/Error-Messages

Backend:
- FastAPI-Endpoint: POST /api/contact
- Pydantic-Validation
- Spam-Protection (Rate-Limiting)
- E-Mail via opena7 (Email Agent)
- Option-2-Flow

Security:
- Input-Sanitization
- CSRF-Protection
- Rate-Limiting (10 req/hour pro IP)

Inkludiere:
1. HTML/CSS/JS (Frontend)
2. FastAPI-Router (Backend)
3. E-Mail-Template
4. Unit-Tests
5. E2E-Test (Playwright)
```

---

### 6. API-Integration (Drittanbieter)

**Prompt:**
```
@docs/EXTERNAL_WEBSITE_API_INTEGRATION.md
@.github/copilot-master-prompt.md

Integriere Google Maps API in Website:

Features:
- Geocoding (Adresse → Koordinaten)
- Directions (Route A → B)
- Places-Search
- Map-Embed

Technische Details:
- Google Maps API Client
- API-Key aus ENV
- Caching (5min TTL)
- Error-Handling
- Rate-Limiting
- Option-2-Flow

Inkludiere:
1. API-Client-Wrapper
2. Caching-Layer
3. Error-Handling
4. Unit-Tests
5. Integration-Tests
```

---

## 🎨 Code-Style-Präferenzen für Copilot

### Python-Code

```python
# ✅ BEVORZUGT: Async/Await, Type-Hints, Pydantic

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import httpx

class WebsiteRequest(BaseModel, extra="forbid"):
    """Request model mit strict schema."""
    request_id: str = Field(..., min_length=1)
    user_query: str
    context: Dict[str, Any]

async def call_agent(
    agent_port: int,
    request: WebsiteRequest
) -> Dict[str, Any]:
    """
    Call agent via Option-2-Flow.
    
    Args:
        agent_port: Agent port (12344-12399)
        request: Request data
    
    Returns:
        Agent response
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"http://127.0.0.1:{agent_port}/command",
            json=request.dict()
        )
        response.raise_for_status()
        return response.json()
```

### FastAPI-Endpoints

```python
# ✅ BEVORZUGT: Type-Hints, Dependency-Injection, Error-Handling

from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(prefix="/api/v1")

@router.post("/products")
async def create_product(
    product: ProductRequest,
    token: str = Depends(verify_token)
) -> ProductResponse:
    """
    Create new product.
    
    Security:
        - Bearer token required
        - Input validation via Pydantic
        - Option-2-Flow enforcement
    """
    try:
        # Option-2-Flow: Request an opena1
        result = await execute_option2_flow(
            agent="opena16",
            action="create_product",
            params=product.dict()
        )
        return ProductResponse(**result)
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🧪 Testing mit Copilot

### Unit-Test-Template

```
@docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md

Schreibe Unit-Tests für WebsiteRequest-Klasse:

Tests:
1. Valid request → Success
2. Missing request_id → ValidationError
3. Extra fields → ValidationError (extra="forbid")
4. Empty user_query → ValidationError

Framework: pytest
Style: AAA (Arrange, Act, Assert)
```

### E2E-Test-Template

```
@docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md

Schreibe E2E-Test für Landing-Page-Creation:

Schritte:
1. Create landing page via opena1
2. Verify HTML generated
3. Verify Safepoint in opena2
4. Validate HTML (W3C)
5. Test responsive design (Playwright)

Framework: pytest + Playwright
```

---

## 📊 Best Practices für Copilot-Prompts

### ✅ DO

1. **Spezifische Dateien referenzieren**
   ```
   @docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md
   ```

2. **Technische Requirements klar definieren**
   ```
   - opena15 (Port 12361)
   - Option-2-Flow einhalten
   - Safepoint-Archivierung
   ```

3. **Gewünschten Output spezifizieren**
   ```
   Output: Vollständiges Python-Script mit FastAPI, inkl. Tests
   ```

4. **Security-Requirements nennen**
   ```
   Security:
   - Input-Validierung
   - Secrets aus ENV
   - Rate-Limiting
   ```

### ❌ DON'T

1. **Vage Anfragen**
   ```
   ❌ "Erstelle eine Website"
   ✅ "Erstelle Landing Page mit opena15, Hero-Section, Features-Grid"
   ```

2. **Fehlende Kontext-Dateien**
   ```
   ❌ Keine @-Referenzen
   ✅ @docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md
   ```

3. **Port-Policy ignorieren**
   ```
   ❌ Port 8080 verwenden
   ✅ Port 12344-12399
   ```

4. **Option-2-Flow übergehen**
   ```
   ❌ Direktcall an Agent
   ✅ Via opena1 → opena2 → kordp → Agent
   ```

---

## 🔍 Copilot Debug-Tipps

### Problem: Copilot generiert falschen Port

**Lösung:**
```
WICHTIG: Port-Policy beachten!
- Erlaubt: 12344-12399
- Verboten: 8080
- opena15: 12361
- opena16: 12362
- opena17: 12366
- opena6: 12352
```

### Problem: Option-2-Flow nicht eingehalten

**Lösung:**
```
KRITISCH: Option-2-Flow ist Pflicht!

Richtig:
Request → opena1:12344 → opena2:12345 → kordp:12346 → Agent

Falsch:
Request → Agent direkt ❌
```

### Problem: Secrets hardcoded

**Lösung:**
```
NIEMALS Secrets hardcoden!

❌ FALSCH:
API_KEY = "sk_live_123456789"

✅ RICHTIG:
import os
API_KEY = os.getenv("API_KEY")
```

---

## 📚 Weitere Ressourcen

- **Master Prompt:** `docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md`
- **Quick Reference:** `docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md`
- **API Integration:** `docs/EXTERNAL_WEBSITE_API_INTEGRATION.md`
- **System Prompt:** `.github/copilot-master-prompt.md`

---

**Maintainer:** Danijel Jokic (ELION Team)  
**Letzte Aktualisierung:** 21. Dezember 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
