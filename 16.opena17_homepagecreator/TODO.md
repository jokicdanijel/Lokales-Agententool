# TODO – opena17 Homepage Creator Agent

**Port:** 12362
**Status:** 🟡 Planned
**Kürzel:** `hpcreatep`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_homepage_agent.py` erstellen (Port 12362)
- [ ] Config-Modul für Site-Generator (Static/SSR), Template-Library, Deployment-Targets
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] Site-Generator (11ty, Hugo, oder Custom) integrieren
- [ ] Deployment-Module (FTP, S3, Netlify, Vercel) implementieren
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena17.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/site/generate` – Website generieren (POST)
- [ ] `/site/export` – Website exportieren (POST, returns ZIP)
- [ ] `/site/preview` – Live-Preview starten (POST)
- [ ] `/site/deploy` – Website deployen (POST)
- [ ] `/site/structure` – Site-Struktur abrufen (GET)
- [ ] Pydantic-Schemas für:
  - `SiteGenerate` (template, pages, navigation, branding)
  - `SiteExport` (format, include_assets)
  - `SiteDeploy` (target, credentials, invalidate_cache)
  - `SiteStructure` (pages, routes, assets)
- [ ] Error-Handling für:
  - Template Not Found (404)
  - Build Failed (500)
  - Deployment Failed (502)
  - Invalid Page Structure (422)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `hpcreatep`
- [ ] kordp-Routing konfigurieren (Decision72 → hpcreatep)
- [ ] CMD-Safepoint für Site-Generation
- [ ] RESP-Safepoint mit Build-Output-Pfad oder Deployment-URL
- [ ] Integration mit opena15 (HTML) für Komponenten-Generierung
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Build-Operationen
- [ ] Nohup-Log (`logs/opena17.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Site-Generation (CMD mit Template/Pages, RESP mit Build-Path)
  - Deployment (CMD mit Target, RESP mit URL)
  - Export (CMD mit Format, RESP mit ZIP-Path)
- [ ] Secret-Masking für Deployment-Credentials in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Build-Artifacts extern speichern (nicht in Safepoints)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Page-Validation, Navigation-Logic
- [ ] Integration-Tests mit verschiedenen Templates
- [ ] Tests für Edge-Cases:
  - Fehlende Assets
  - Broken Links
  - Large Sites (>100 Pages)
  - Multi-Language-Support
- [ ] Mock für Deployment-Targets (keine echten Deploys in CI/CD)
- [ ] E2E-Test: Site generieren → Preview → Deploy → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - Site-Generator-Setup (11ty, Hugo)
  - Template-Struktur
  - Deployment-Targets (S3, Netlify, Vercel)
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - Deployment-Credentials niemals hardcoden
  - Preview-URLs zeitlich begrenzt
  - XSS-Schutz für User-Input
- [ ] Architekturdiagramm (opena15 ↔ opena17 ↔ Site-Generator ↔ Deployment)
- [ ] Troubleshooting-Guide (Build-Fehler, Deployment-Fails, Asset-Errors)
- [ ] Deployment-Anleitung (Docker, CI/CD-Integration, Rollbacks)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
