# TODO – opena6 Browser Automation Agent

**Port:** 12350  
**Status:** 🟡 Planned (Adapter läuft auf 12350)  
**Kürzel:** `browsep`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_browser_agent.py` erstellen (Port 12350)
- [ ] Config-Modul für Browser-Engine (Playwright/Selenium), Headless-Modus, User-Agent
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] Playwright/Selenium-Client integrieren
- [ ] Browser-Pool-Management (max. N parallele Sessions)
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena6.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/navigate` – URL öffnen (POST)
- [ ] `/screenshot` – Screenshot erstellen (POST, returns Base64 oder File-Path)
- [ ] `/extract` – Element-Daten extrahieren (POST mit CSS-Selector)
- [ ] `/click` – Element klicken (POST)
- [ ] `/form/fill` – Formular ausfüllen (POST)
- [ ] Pydantic-Schemas für:
  - `NavigateRequest` (url, wait_until, timeout)
  - `ScreenshotRequest` (url, selector, full_page)
  - `ExtractRequest` (url, selectors, wait_for)
  - `ClickRequest` (url, selector, wait_after)
  - `FormFillRequest` (url, fields, submit)
- [ ] Error-Handling für:
  - Timeout (504)
  - Element Not Found (404)
  - Navigation Failed (502)
  - Browser Crash (500)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `browsep`
- [ ] kordp-Routing konfigurieren (Decision72 → browsep)
- [ ] CMD-Safepoint für Browser-Actions (Navigate, Extract, Screenshot)
- [ ] RESP-Safepoint mit Ergebnissen (keine großen Screenshots im Archiv)
- [ ] Integration mit opena1 für orchestrierte Web-Scraping-Flows
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Browser-Events
- [ ] Nohup-Log (`logs/opena6.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Navigate-Actions (CMD mit URL, RESP mit Status)
  - Extraction-Results (CMD mit Selektoren, RESP mit Daten)
  - Screenshots (CMD mit Params, RESP mit Pfad/Base64)
- [ ] Secret-Masking für URLs mit Tokens/API-Keys
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Screenshots extern speichern (nicht in Safepoints)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Selector-Parsing, Error-Handling
- [ ] Integration-Tests gegen kontrollierte Test-Website
- [ ] Tests für Edge-Cases:
  - CAPTCHA-Seiten
  - JavaScript-intensive SPAs
  - Infinite Scrolling
  - Auth-geschützte Seiten
- [ ] Mock für Browser-Engine (keine echten Browser-Starts in CI/CD)
- [ ] E2E-Test: Navigate → Extract → Screenshot → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - Browser-Engine-Setup (Playwright vs. Selenium)
  - Headless vs. Headed-Modus
  - User-Agent-Konfiguration
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - Rate-Limiting pro Ziel-Domain
  - Keine Massen-Scraping ohne Zustimmung
  - Robots.txt respektieren
- [ ] Architekturdiagramm (Browser Engine ↔ opena6 ↔ Portier)
- [ ] Troubleshooting-Guide (Timeouts, Element-Selektoren, CAPTCHA)
- [ ] Deployment-Anleitung (Docker mit Browser-Binary, Resource-Limits)

---

**Letzte Aktualisierung:** 27. November 2025  
**Maintainer:** Danijel Jokic (ELION Team)
