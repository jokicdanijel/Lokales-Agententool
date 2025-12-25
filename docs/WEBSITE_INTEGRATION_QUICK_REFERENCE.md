# 🚀 Website Integration Quick Reference — ELION System

**Zweck:** Schnellreferenz für häufige Website-Integrations-Szenarien
**Zielgruppe:** Entwickler, die mit ELION Hyper-Dashboard arbeiten
**Letzte Aktualisierung:** 21. Dezember 2025

---

## 📋 Inhaltsverzeichnis

1. [Landing Page erstellen](#landing-page-erstellen)
2. [E-Commerce-Shop einrichten](#e-commerce-shop-einrichten)
3. [Contact Form integrieren](#contact-form-integrieren)
4. [Blog-System aufsetzen](#blog-system-aufsetzen)
5. [API-Endpoint hinzufügen](#api-endpoint-hinzufügen)
6. [Webhook empfangen](#webhook-empfangen)
7. [Website scrapen](#website-scrapen)
8. [Automatisierte Tests](#automatisierte-tests)

---

## 🎯 Landing Page erstellen

### Szenario

Eine moderne Landing Page mit Formular und Call-to-Action erstellen.

### Agent

**opena15** (HTML Creator) — Port 12361

### Code

```python
import httpx
import asyncio

async def create_landing_page():
    """Erstelle Landing Page via opena15."""

    # Request-Daten
    request_data = {
        "request_id": "lp-001",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "api",
        "user_query": "Erstelle moderne Landing Page",
        "context": {
            "template": "landing_modern",
            "title": "Willkommen bei ELION",
            "sections": [
                {
                    "type": "hero",
                    "heading": "Revolutionäre KI-Lösungen",
                    "subheading": "Für Ihr Business",
                    "cta_text": "Jetzt starten",
                    "cta_link": "#contact"
                },
                {
                    "type": "features",
                    "items": [
                        {"icon": "🚀", "title": "Schnell", "desc": "Blitzschnelle Integration"},
                        {"icon": "🔒", "title": "Sicher", "desc": "Enterprise-Security"},
                        {"icon": "📊", "title": "Skalierbar", "desc": "Wächst mit Ihnen"}
                    ]
                },
                {
                    "type": "contact_form",
                    "fields": ["name", "email", "message"]
                }
            ]
        }
    }

    # Option-2-Flow: Request an opena1
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=request_data,
            timeout=30.0
        )

        result = response.json()

        # HTML ausgeben
        html = result.get("html", "")

        # Speichern
        with open("landing_page.html", "w") as f:
            f.write(html)

        print("✅ Landing Page erstellt: landing_page.html")
        return html

# Ausführen
if __name__ == "__main__":
    asyncio.run(create_landing_page())
```

### Erwartetes Ergebnis

```html
<!DOCTYPE html>
<html lang="de">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Willkommen bei ELION</title>
    <style>
      /* Modern CSS */
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      body {
        font-family: "Segoe UI", sans-serif;
      }
      .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 100px 20px;
        text-align: center;
      }
      /* ... */
    </style>
  </head>
  <body>
    <section class="hero">
      <h1>Revolutionäre KI-Lösungen</h1>
      <p>Für Ihr Business</p>
      <a href="#contact" class="cta-button">Jetzt starten</a>
    </section>
    <!-- ... -->
  </body>
</html>
```

---

## 🛒 E-Commerce-Shop einrichten

### Szenario

Produkt-Katalog mit Warenkorb und Checkout einrichten.

### Agent

**opena16** (Shop Creator) — Port 12362

### Code

```python
async def setup_ecommerce_shop():
    """Richte E-Commerce-Shop ein."""

    # 1. Shop erstellen
    shop_config = {
        "request_id": "shop-001",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "api",
        "user_query": "Erstelle E-Commerce-Shop",
        "context": {
            "shop_name": "ELION Store",
            "currency": "EUR",
            "payment_methods": ["stripe", "paypal"],
            "shipping_zones": ["DE", "EU", "WORLD"]
        }
    }

    async with httpx.AsyncClient() as client:
        # Shop erstellen via opena1 (Option-2-Flow)
        shop_response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=shop_config
        )

        shop = shop_response.json()
        shop_id = shop["shop_id"]

        # 2. Produkte hinzufügen
        products = [
            {
                "name": "Premium AI Agent",
                "price": 99.99,
                "stock": 50,
                "description": "Vollautomatisierter KI-Agent",
                "images": ["ai-agent-1.jpg"],
                "category": "Software"
            },
            {
                "name": "Enterprise Dashboard",
                "price": 299.99,
                "stock": 25,
                "description": "Vollständiges Monitoring-System",
                "images": ["dashboard-1.jpg"],
                "category": "Software"
            }
        ]

        for product in products:
            product_request = {
                "request_id": f"prod-{product['name']}",
                "timestamp": "2025-12-21T10:00:00Z",
                "source": "api",
                "user_query": f"Füge Produkt hinzu: {product['name']}",
                "context": {
                    "shop_id": shop_id,
                    "action": "add_product",
                    "product": product
                }
            }

            await client.post(
                "http://127.0.0.1:12344/log/opena1",
                json=product_request
            )

        print(f"✅ Shop erstellt: {shop_id}")
        print(f"✅ {len(products)} Produkte hinzugefügt")

        return shop

# Ausführen
if __name__ == "__main__":
    asyncio.run(setup_ecommerce_shop())
```

### Stripe-Integration

```python
async def setup_stripe_payment():
    """Stripe-Payment-Gateway einrichten."""

    # .env: STRIPE_SECRET_KEY=sk_test_...

    payment_config = {
        "request_id": "payment-001",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "api",
        "user_query": "Konfiguriere Stripe-Payment",
        "context": {
            "provider": "stripe",
            "webhook_url": "https://yourdomain.com/webhook/stripe",
            "success_url": "https://yourdomain.com/success",
            "cancel_url": "https://yourdomain.com/cancel"
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=payment_config
        )

        result = response.json()
        print("✅ Stripe konfiguriert")
        print(f"   Publishable Key: {result['publishable_key']}")
        print(f"   Webhook Secret: whsec_...")
```

---

## 📧 Contact Form integrieren

### Szenario

Kontaktformular mit E-Mail-Benachrichtigung.

### Agents

- **opena15** (HTML) — Port 12361
- **opena7** (Email) — Port 12353

### Code

```python
async def create_contact_form():
    """Erstelle Kontaktformular mit E-Mail-Integration."""

    # 1. HTML-Formular generieren
    form_request = {
        "request_id": "form-001",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "api",
        "user_query": "Erstelle Kontaktformular",
        "context": {
            "type": "contact_form",
            "fields": [
                {"name": "name", "type": "text", "required": True},
                {"name": "email", "type": "email", "required": True},
                {"name": "subject", "type": "text", "required": True},
                {"name": "message", "type": "textarea", "required": True}
            ],
            "submit_endpoint": "/api/contact",
            "success_message": "Vielen Dank! Wir melden uns bald.",
            "validation": True
        }
    }

    async with httpx.AsyncClient() as client:
        # HTML generieren
        form_response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=form_request
        )

        html = form_response.json()["html"]

        # 2. Backend-Handler erstellen
        # (In FastAPI-App des entsprechenden Agents)

        print("✅ Kontaktformular erstellt")
        print("   HTML: contact_form.html")
        print("   Endpoint: POST /api/contact")

        return html

# Backend-Handler (in FastAPI-App)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()

class ContactFormData(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

@router.post("/api/contact")
async def handle_contact_form(data: ContactFormData):
    """Handle contact form submission."""

    # Validierung
    if len(data.message) < 10:
        raise HTTPException(
            status_code=400,
            detail="Message too short"
        )

    # E-Mail senden (via opena7)
    email_request = {
        "request_id": f"email-{data.email}",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "contact_form",
        "user_query": f"Sende Kontaktformular-E-Mail: {data.subject}",
        "context": {
            "to": "info@example.com",
            "from": data.email,
            "subject": f"Kontaktanfrage: {data.subject}",
            "html": f"""
                <h2>Neue Kontaktanfrage</h2>
                <p><strong>Von:</strong> {data.name} ({data.email})</p>
                <p><strong>Betreff:</strong> {data.subject}</p>
                <p><strong>Nachricht:</strong></p>
                <p>{data.message}</p>
            """
        }
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=email_request
        )

    return {"status": "success", "message": "E-Mail gesendet"}
```

---

## 📝 Blog-System aufsetzen

### Szenario

Multi-Post-Blog mit Kategorien und Kommentaren.

### Agent

**opena17** (Homepage Creator) — Port 12366

### Code

```python
async def setup_blog_system():
    """Richte Blog-System ein."""

    blog_config = {
        "request_id": "blog-001",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "api",
        "user_query": "Erstelle Blog-System",
        "context": {
            "blog_name": "ELION Tech Blog",
            "theme": "modern",
            "features": [
                "categories",
                "tags",
                "comments",
                "search",
                "rss_feed"
            ],
            "categories": [
                "AI & Machine Learning",
                "Web Development",
                "DevOps",
                "Tutorials"
            ]
        }
    }

    async with httpx.AsyncClient() as client:
        # Blog erstellen
        response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=blog_config
        )

        blog = response.json()
        blog_id = blog["blog_id"]

        # Ersten Post erstellen
        post_request = {
            "request_id": "post-001",
            "timestamp": "2025-12-21T10:00:00Z",
            "source": "api",
            "user_query": "Erstelle Blog-Post",
            "context": {
                "blog_id": blog_id,
                "title": "Willkommen auf dem ELION Tech Blog",
                "content": """
                    <p>Willkommen! In diesem Blog teilen wir...</p>
                    <h2>Was Sie erwarten können</h2>
                    <ul>
                        <li>Tutorials</li>
                        <li>Best Practices</li>
                        <li>News & Updates</li>
                    </ul>
                """,
                "category": "AI & Machine Learning",
                "tags": ["announcement", "welcome"],
                "author": "ELION Team",
                "publish": True
            }
        }

        await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=post_request
        )

        print(f"✅ Blog erstellt: {blog_id}")
        print("✅ Erster Post veröffentlicht")
        print(f"   URL: /blog/{blog_id}")

        return blog

# Ausführen
if __name__ == "__main__":
    asyncio.run(setup_blog_system())
```

---

## 🔌 API-Endpoint hinzufügen

### Szenario

Custom REST-API-Endpoint für Website-Daten.

### Code

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/v1")

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = None,
    limit: int = 10
):
    """
    Get products via Option-2-Flow.

    Query Parameters:
        - category: Filter by category
        - limit: Max results (default: 10)
    """

    # Request an opena16 (Shop)
    request_data = {
        "request_id": f"api-products-{category or 'all'}",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "api",
        "user_query": "Liste Produkte",
        "context": {
            "action": "list_products",
            "filters": {
                "category": category,
                "limit": limit
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=request_data
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch products"
            )

        result = response.json()
        products = result.get("products", [])

        return [
            ProductResponse(**p) for p in products
        ]

@router.post("/products")
async def create_product(product: ProductResponse):
    """Create new product."""

    request_data = {
        "request_id": f"api-create-{product.name}",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "api",
        "user_query": f"Erstelle Produkt: {product.name}",
        "context": {
            "action": "create_product",
            "product": product.dict()
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=request_data
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Failed to create product"
            )

        return response.json()
```

### API-Dokumentation (Auto-generiert)

```bash
# OpenAPI/Swagger UI verfügbar unter:
http://127.0.0.1:12362/docs

# ReDoc verfügbar unter:
http://127.0.0.1:12362/redoc
```

---

## 📥 Webhook empfangen

### Szenario

Stripe-Webhook für Payment-Events empfangen.

### Code

```python
from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
import os

router = APIRouter()

@router.post("/webhook/stripe")
async def handle_stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.

    Security:
        - Signature validation
        - Replay protection
        - Safepoint archiving
    """

    # 1. Signature-Validierung
    signature = request.headers.get("Stripe-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    payload = await request.body()

    # Verify signature
    try:
        expected_sig = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Parse signature header
        sig_parts = dict(
            item.split("=")
            for item in signature.split(",")
        )

        if not hmac.compare_digest(sig_parts["v1"], expected_sig):
            raise HTTPException(status_code=401, detail="Invalid signature")

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    # 2. Parse event
    event = await request.json()
    event_type = event["type"]

    # 3. Safepoint-Archivierung (Option-2-Flow)
    webhook_request = {
        "request_id": f"webhook-{event['id']}",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "stripe_webhook",
        "user_query": f"Stripe Event: {event_type}",
        "context": {
            "event_type": event_type,
            "event_data": event["data"],
            "webhook_id": event["id"]
        }
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=webhook_request
        )

    # 4. Event-spezifische Verarbeitung
    if event_type == "payment_intent.succeeded":
        await process_payment_success(event["data"]["object"])

    elif event_type == "payment_intent.payment_failed":
        await process_payment_failed(event["data"]["object"])

    elif event_type == "customer.subscription.created":
        await process_subscription_created(event["data"]["object"])

    return {"status": "received"}

async def process_payment_success(payment_intent):
    """Process successful payment."""
    amount = payment_intent["amount"] / 100  # Convert cents to euros
    customer_email = payment_intent.get("receipt_email")

    # Send confirmation email
    email_request = {
        "request_id": f"email-payment-{payment_intent['id']}",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "webhook",
        "user_query": "Sende Payment-Bestätigung",
        "context": {
            "to": customer_email,
            "subject": "Zahlungsbestätigung",
            "html": f"""
                <h2>Zahlung erfolgreich</h2>
                <p>Betrag: {amount} EUR</p>
                <p>Zahlungs-ID: {payment_intent['id']}</p>
            """
        }
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=email_request
        )
```

---

## 🕷️ Website scrapen

### Szenario

Daten von externer Website extrahieren.

### Agent

**opena6** (Browser Automation) — Port 12352

### Code

```python
async def scrape_website():
    """Scrape Daten von Website."""

    scrape_request = {
        "request_id": "scrape-001",
        "timestamp": "2025-12-21T10:00:00Z",
        "source": "api",
        "user_query": "Scrape Website-Daten",
        "context": {
            "url": "https://example.com/products",
            "selectors": {
                "products": ".product-card",
                "title": "h2.product-title",
                "price": ".product-price",
                "image": "img.product-image@src"
            },
            "wait_for": "networkidle",
            "screenshot": True
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json=scrape_request
        )

        result = response.json()

        products = result["data"]["products"]
        screenshot = result["screenshot"]  # Base64

        print(f"✅ {len(products)} Produkte gescraped")
        print(f"   Screenshot: {len(screenshot)} bytes")

        # Daten speichern
        import json
        with open("scraped_products.json", "w") as f:
            json.dump(products, f, indent=2)

        return products

# Ausführen
if __name__ == "__main__":
    asyncio.run(scrape_website())
```

### Erwartetes Ergebnis

```json
[
  {
    "title": "Produkt 1",
    "price": "€29.99",
    "image": "https://example.com/img/product1.jpg"
  },
  {
    "title": "Produkt 2",
    "price": "€49.99",
    "image": "https://example.com/img/product2.jpg"
  }
]
```

---

## 🧪 Automatisierte Tests

### E2E-Test für Landing Page

```python
import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_landing_page_e2e():
    """E2E-Test für Landing Page."""

    # 1. Landing Page erstellen
    html = await create_landing_page()

    # 2. Playwright-Browser starten
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 3. HTML laden
        await page.set_content(html)

        # 4. Elemente prüfen
        assert await page.locator("h1").text_content() == \
            "Revolutionäre KI-Lösungen"

        assert await page.locator(".cta-button").is_visible()

        # 5. Formular testen
        await page.fill('input[name="name"]', "Test User")
        await page.fill('input[name="email"]', "test@example.com")
        await page.fill('textarea[name="message"]', "Test-Nachricht")

        # 6. Submit
        await page.click('button[type="submit"]')

        # 7. Success-Message prüfen
        success = await page.locator(".success-message").is_visible()
        assert success

        await browser.close()

@pytest.mark.asyncio
async def test_shop_checkout_flow():
    """E2E-Test für Shop-Checkout."""

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 1. Shop-Seite öffnen
        await page.goto("http://localhost:12362/shop")

        # 2. Produkt zum Warenkorb
        await page.click(".product-card:first-child .add-to-cart")

        # 3. Warenkorb prüfen
        cart_count = await page.locator(".cart-count").text_content()
        assert cart_count == "1"

        # 4. Checkout
        await page.click(".cart-icon")
        await page.click(".checkout-button")

        # 5. Formular ausfüllen
        await page.fill('input[name="email"]', "customer@example.com")
        await page.fill('input[name="card"]', "4242424242424242")  # Stripe test card
        await page.fill('input[name="exp"]', "12/25")
        await page.fill('input[name="cvc"]', "123")

        # 6. Payment
        await page.click('button[type="submit"]')

        # 7. Success-Page
        await page.wait_for_url("**/success")
        assert "Vielen Dank" in await page.locator("h1").text_content()

        await browser.close()
```

---

## 📚 Zusätzliche Ressourcen

### Dokumentation

- **Master Prompt:** `docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md`
- **External APIs:** `docs/EXTERNAL_WEBSITE_API_INTEGRATION.md`
- **Operations:** `docs/OPERATIONS.md`

### Code-Beispiele

- **HTML Agent:** `14.opena15_html/main_html_agent.py`
- **Shop Agent:** `15.opena16_shop/`
- **Homepage Agent:** `16.opena17_homepagecreator/main_homepage_agent.py`
- **Browser Agent:** `5.opena6_browser/`

### Testing

- **E2E-Tests:** `tests/e2e_option2_flow.sh`
- **Unit-Tests:** `tests/test_*.py`

---

## 🔍 Troubleshooting

### Problem: Port bereits belegt

```bash
# Lösung
lsof -i :12361
kill -9 <PID>
bin/ops.sh start opena15
```

### Problem: Secrets fehlen

```bash
# Lösung
grep API_KEY .env
echo "MISSING_API_KEY=your_key" >> .env
bin/ops.sh restart
```

### Problem: Safepoint nicht gespeichert

```bash
# Lösung: Prüfe Option-2-Flow
curl http://127.0.0.1:12345/archiv/last?n=5 | jq .

# Falls leer: Requests müssen durch opena1 gehen!
# ❌ FALSCH: curl http://127.0.0.1:12361/command
# ✅ RICHTIG: curl http://127.0.0.1:12344/log/opena1
```

---

**Maintainer:** Danijel Jokic (ELION Team)
**Letzte Aktualisierung:** 21. Dezember 2025
**Version:** 1.0.0
**Status:** ✅ Production Ready
