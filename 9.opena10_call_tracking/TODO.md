# TODO – opena10 Call Tracking Agent

**Port:** 12355
**Status:** 🟡 Planned
**Kürzel:** `calltrackp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_calltracking_agent.py` erstellen (Port 12355)
- [ ] Config-Modul für DB-Anbindung (SQLite/PostgreSQL), Kampagnen-IDs, Tracking-Nummern
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] SQLAlchemy-Models für CallEvent, Campaign, TrackingNumber
- [ ] Integration mit opena9 (Telefonie) für Event-Ingestion
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena10.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/events/ingest` – Call-Event aufnehmen (POST)
- [ ] `/stats/summary` – Gesamtstatistik (GET)
- [ ] `/stats/by_campaign` – Statistik pro Kampagne (GET)
- [ ] `/tracking_numbers/list` – Tracking-Nummern auflisten (GET)
- [ ] `/tracking_numbers/create` – Tracking-Nummer erstellen (POST)
- [ ] Pydantic-Schemas für:
  - `CallEventIngest` (call_id, tracking_number, duration, status, timestamp)
  - `StatsResponse` (total_calls, avg_duration, success_rate)
  - `CampaignStatsResponse` (campaign_id, calls, conversions, ctr)
  - `TrackingNumberCreate` (number, campaign_id, description)
- [ ] Error-Handling für:
  - Invalid Call-ID (400)
  - Campaign Not Found (404)
  - Duplicate Event (409)
  - DB Connection Failed (500)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `calltrackp`
- [ ] kordp-Routing konfigurieren (Decision72 → calltrackp)
- [ ] CMD-Safepoint für Event-Ingestion (CMD mit Call-ID/Kampagne)
- [ ] RESP-Safepoint mit Aggregations-Ergebnissen
- [ ] Integration mit opena9 (Telefonie) für automatische Event-Erfassung
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Events
- [ ] Nohup-Log (`logs/opena10.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Ingest-Events (CMD mit Event-Daten, RESP mit Insert-ID)
  - Statistik-Abfragen (CMD mit Filter, RESP mit Aggregationen)
- [ ] Secret-Masking für Tracking-Nummern in Logs (optional)
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Backup-Strategie für Call-Event-DB

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Event-Validation, Statistik-Berechnung
- [ ] Integration-Tests mit In-Memory-DB (SQLite)
- [ ] Tests für Edge-Cases:
  - Duplicate Events
  - Fehlende Kampagnen-IDs
  - Zeitzone-Handling
  - Hohe Event-Raten (>1000/min)
- [ ] Mock für DB (keine echten DB-Writes in CI/CD)
- [ ] E2E-Test: Event-Ingestion → Statistik-Abfrage → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - DB-Setup (Schema, Migrationen)
  - Kampagnen-Tracking-Konzept
  - Tracking-Nummern-Zuweisung
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - DB-Credentials niemals hardcoden
  - Read-Only-Zugriff für Reporting-User
  - Retention-Policy für alte Events
- [ ] Architekturdiagramm (opena9 ↔ opena10 ↔ DB ↔ Portier)
- [ ] Troubleshooting-Guide (DB-Performance, Event-Loss, Zeitzone-Fehler)
- [ ] Deployment-Anleitung (Docker, DB-Backup, Grafana-Integration)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
