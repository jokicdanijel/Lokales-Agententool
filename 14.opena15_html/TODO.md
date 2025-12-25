# TODO – opena15 HTML Creator Agent

**Port:** 12360
**Status:** 🟡 Planned
**Kürzel:** `htmlp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_html_agent.py` erstellen (Port 12360)
- [ ] Config-Modul für Template-Pfade, Default-CSS-Framework, Output-Dir
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] Jinja2-Template-Engine integrieren
- [ ] HTML-Validator (BeautifulSoup/lxml) implementieren
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena15.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/generate` – HTML generieren (POST)
- [ ] `/preview` – HTML-Preview rendern (POST, returns HTML)
- [ ] `/validate` – HTML validieren (POST)
- [ ] `/templates/list` – Verfügbare Templates auflisten (GET)
- [ ] `/export` – HTML als Datei exportieren (POST)
- [ ] Pydantic-Schemas für:
  - `GenerateRequest` (template, variables, css_framework)
  - `PreviewRequest` (html, width, height)
  - `ValidateRequest` (html, strict_mode)
  - `ValidateResponse` (valid, errors, warnings)
- [ ] Error-Handling für:
  - Template Not Found (404)
  - Invalid Variables (400)
  - Validation Failed (422)
  - Render Timeout (504)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `htmlp`
- [ ] kordp-Routing konfigurieren (Decision72 → htmlp)
- [ ] CMD-Safepoint für Generate-Operationen
- [ ] RESP-Safepoint mit HTML-Output-Pfad oder Base64
- [ ] Integration mit opena1 für orchestrierte HTML-Erstellung
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Render-Operationen
- [ ] Nohup-Log (`logs/opena15.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Generate-Requests (CMD mit Template/Variables, RESP mit Output-Path)
  - Validate-Requests (CMD mit HTML, RESP mit Validation-Result)
- [ ] Secret-Masking für Template-Variables (z.B. API-Keys)
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Keine vollen HTML-Outputs in Safepoints (nur Metadaten)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Template-Rendering, Validation-Logic
- [ ] Integration-Tests mit verschiedenen Templates
- [ ] Tests für Edge-Cases:
  - Fehlende Template-Variables
  - Ungültige CSS-Selektoren
  - Große HTML-Outputs (>1 MB)
  - XSS-Injection-Versuche
- [ ] Mock für Template-Engine (keine echten Renders in CI/CD)
- [ ] E2E-Test: Template rendern → Validieren → Export → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - Template-Struktur (Jinja2-Syntax)
  - CSS-Framework-Integration (Bootstrap, Tailwind)
  - Validation-Standards (HTML5, WCAG)
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - XSS-Schutz (Template-Escaping)
  - Keine User-Input-Injection in Templates
  - CSP-Header für Preview
- [ ] Architekturdiagramm (Templates ↔ opena15 ↔ Validator ↔ Portier)
- [ ] Troubleshooting-Guide (Template-Fehler, Validation-Warnings)
- [ ] Deployment-Anleitung (Docker, Template-Versioning)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
