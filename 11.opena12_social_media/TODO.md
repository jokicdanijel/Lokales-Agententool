# TODO – opena12 Social Media Agent

**Port:** 12357
**Status:** 🟡 Planned
**Kürzel:** `smp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_socialmedia_agent.py` erstellen (Port 12357)
- [ ] Config-Modul für Plattform-APIs (LinkedIn, X, Facebook, Instagram)
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] OAuth-Clients für jede Plattform integrieren
- [ ] Post-Queue-System (Redis/SQLite) für Scheduling
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena12.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/post` – Sofort posten (POST)
- [ ] `/schedule` – Post planen (POST)
- [ ] `/status` – Post-Status abfragen (GET)
- [ ] `/delete` – Post löschen (DELETE)
- [ ] `/platforms/list` – Verbundene Plattformen auflisten (GET)
- [ ] Pydantic-Schemas für:
  - `PostRequest` (platforms, text, media, hashtags)
  - `ScheduleRequest` (platforms, text, media, scheduled_at)
  - `StatusResponse` (post_id, platform, status, url)
  - `DeleteRequest` (post_id, platform)
- [ ] Error-Handling für:
  - Rate Limit Exceeded (429)
  - Auth Token Expired (401)
  - Post Too Long (413)
  - Platform API Down (502)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `smp`
- [ ] kordp-Routing konfigurieren (Decision72 → smp)
- [ ] CMD-Safepoint für Post-Erstellung (CMD mit Text/Media)
- [ ] RESP-Safepoint mit Post-IDs/URLs
- [ ] Integration mit opena1 für orchestrierte Content-Kampagnen
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Posts
- [ ] Nohup-Log (`logs/opena12.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Gesendete Posts (CMD mit Content, RESP mit Post-ID)
  - Geplante Posts (CMD mit Schedule, RESP mit Queue-ID)
  - Gelöschte Posts (CMD mit Post-ID, RESP mit Status)
- [ ] Secret-Masking für OAuth-Tokens in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Keine vollen Post-Inhalte in Safepoints (nur Metadaten)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Post-Validation, Media-Upload-Logic
- [ ] Integration-Tests gegen Sandbox-Accounts
- [ ] Tests für Edge-Cases:
  - Character-Limits (280 für X, 3000 für LinkedIn)
  - Mehrere Plattformen gleichzeitig
  - Schedule-Collision
  - Ungültige Media-Formate
- [ ] Mock für Platform-APIs (keine echten Posts in CI/CD)
- [ ] E2E-Test: Post erstellen → Plattform bestätigen → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - OAuth-Setup pro Plattform
  - Character-Limits und Best Practices
  - Scheduling-Queue-Konzept
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - OAuth-Tokens niemals hardcoden
  - Rate-Limiting beachten
  - Test-Accounts für Entwicklung nutzen
- [ ] Architekturdiagramm (Plattformen ↔ opena12 ↔ Queue ↔ Portier)
- [ ] Troubleshooting-Guide (Auth-Fehler, Rate-Limits, Post-Rejection)
- [ ] Deployment-Anleitung (Docker, OAuth-Token-Rotation, Redis)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
