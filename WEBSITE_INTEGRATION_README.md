# 🌐 Website Integration für ELION Hyper-Dashboard

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Erstellt:** 21. Dezember 2025

---

## 📚 Dokumentations-Übersicht

Diese Dokumentation beschreibt, wie Websites und Web-Services in das ELION Hyper-Dashboard 3.0.0 System integriert werden.

### 🎯 Hauptdokumente

1. **[Website Integration Master Prompt](docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md)** (⭐ START HERE)
   - Umfassender Guide für alle Website-Integrationen
   - System-Architektur & Option-2-Flow
   - Alle Web-Agenten (opena15, opena16, opena17, opena6)
   - Security, Testing, Deployment

2. **[External API Integration](docs/EXTERNAL_WEBSITE_API_INTEGRATION.md)**
   - REST, GraphQL, SOAP, WebSocket
   - OAuth 2.0 & API-Key Authentication
   - Stripe, SendGrid, Google Maps, Shopify
   - Webhooks & Signature-Validation

3. **[Quick Reference](docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md)**
   - Schnelle Code-Beispiele für häufige Szenarien
   - Landing Pages, E-Commerce, Contact Forms
   - Copy & Paste ready

4. **[Documentation Index](docs/WEBSITE_INTEGRATION_INDEX.md)**
   - Zentrale Übersicht aller Dokumentation
   - Feature-Matrix & Troubleshooting-Index

---

## 🤖 Web-Agenten

| Agent | Port | Funktion | Dokumentation |
|-------|------|----------|---------------|
| **opena15** | 12361 | HTML Creator | `14.opena15_html/MASTER_PROMPT.md` |
| **opena16** | 12362 | Shop Creator | `15.opena16_shop/` |
| **opena17** | 12366 | Homepage Creator | `16.opena17_homepagecreator/MASTER_PROMPT.md` |
| **opena6** | 12352 | Browser Automation | `5.opena6_browser/MASTER_PROMPT.md` |

---

## 🚀 Quick Start

### Landing Page erstellen
```python
# Siehe: docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md
import httpx
import asyncio

async def create_landing_page():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json={
                "request_id": "lp-001",
                "user_query": "Erstelle Landing Page",
                "context": {"template": "modern", "title": "Meine Website"}
            }
        )
        return response.json()

asyncio.run(create_landing_page())
```

### E-Commerce-Shop einrichten
```python
# Siehe: docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md
# opena16 (Shop Creator) verwenden
# Stripe-Integration verfügbar
```

### Website scrapen
```python
# Siehe: docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md
# opena6 (Browser Automation) verwenden
# Playwright/Selenium-Integration
```

---

## 🔐 Security

✅ **Option-2-Flow:** Alle Requests durch opena1 → opena2 → kordp  
✅ **Port-Policy:** Nur 12344-12399 (Backend)  
✅ **Secrets:** Nur aus ENV, nie hardcoded  
✅ **Safepoints:** CMD & RESP für jeden Request  
✅ **Validation:** Input-Sanitization & XSS-Prevention  

---

## 🎯 Für GitHub Copilot

### Kontext laden
```
@docs/WEBSITE_INTEGRATION_MASTER_PROMPT.md
@docs/WEBSITE_INTEGRATION_QUICK_REFERENCE.md

Erstelle eine Landing Page mit Hero-Section und Kontaktformular.
```

---

## 📖 Weitere Dokumentation

- **System-Architektur:** `README.md` (Root)
- **Operations:** `docs/OPERATIONS.md`
- **Copilot-Prompts:** `.github/copilot-master-prompt.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`

---

## 🤝 Support

**Dokumentation-Fehler?** → GitHub Issue  
**Fragen?** → ELION Team kontaktieren  
**Verbesserungen?** → Pull Request

---

**Maintainer:** Danijel Jokic (ELION Team)  
**Repository:** [jokicdanijel/Gesamtprojekt-start](https://github.com/jokicdanijel/Gesamtprojekt-start)  
**Dashboard:** http://127.0.0.1:12349/dashboard
