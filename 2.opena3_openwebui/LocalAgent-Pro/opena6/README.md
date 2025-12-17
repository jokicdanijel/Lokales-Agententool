# opena6 – Browser Automation Agent

**Kanal:** Portier
**Prefix:** `browsep`
**Port:** `12352`
**Status:** ✅ Online

## 1. Rolle im PORTIER 3.0 – Multi-Agent-Stack

opena6 ist der **Browser Automation Agent** im **PORTIER 3.0 – Multi-Agent-Stack**.

**Kernaufgaben:**

- Automatisierte Browser-Steuerung via Selenium/Playwright
- Web-Scraping & Datenextraktion
- UI-Testing & Automatisierte Workflows
- Screenshot-Erstellung & Page-Monitoring
- Integration in Option-2-Flow über `browsep`
- Safepoint-Archivierung über opena2

## Datenfluss (Option-2-Flow)

```
opena1 → Decision72 → CMD → opena2 (Safepoint CMD)
→ 5.opena6_browser (Ausführung)
→ opena2 (Safepoint RESP) → opena1 → User
```

## CMD-Schema

Der Agent akzeptiert strikt das JSON-Schema `BrowserAgentCMD`.

Siehe: `CMD_SCHEMA.md`

## Sicherheit

- Keine Ausführung von nicht autorisierten Scripts
- Keine Fantasieaktionen
- Absolute Trackbarkeit via archivp_store

## config.json

Die Modulkonfiguration befindet sich unter `config.json`.

## 7. Status & Roadmap

- ✅ Selenium/Playwright Integration funktional
- ✅ Browser-Pool-Management implementiert
- ✅ Screenshot & DOM-Extraction
- ✅ Option-2-Flow-Integration
- ⏳ Geplant: Headless-Mode-Optimierung (Phase 18)
- ⏳ Geplant: Multi-Browser-Support (Chrome, Firefox, Safari)
