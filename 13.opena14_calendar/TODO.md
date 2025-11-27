# TODO – opena14 Calendar Agent

**Port:** 12359  
**Status:** 🟡 Planned  
**Kürzel:** `calp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_calendar_agent.py` erstellen (Port 12359)
- [ ] Config-Modul für Google Calendar API, iCal-Dateien, Exchange-Integration
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] OAuth-Client für Google Calendar integrieren
- [ ] iCalendar-Parser (icalendar-Library) implementieren
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena14.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/events/list` – Events auflisten (GET/POST mit Filter)
- [ ] `/events/create` – Event erstellen (POST)
- [ ] `/events/update` – Event aktualisieren (PUT)
- [ ] `/events/delete` – Event löschen (DELETE)
- [ ] `/calendars/list` – Verfügbare Kalender auflisten (GET)
- [ ] Pydantic-Schemas für:
  - `EventListRequest` (calendar_id, start_date, end_date, max_results)
  - `EventCreate` (summary, start, end, attendees, location, description)
  - `EventUpdate` (event_id, summary, start, end)
  - `EventResponse` (id, summary, start, end, attendees, status)
- [ ] Error-Handling für:
  - Event Not Found (404)
  - Conflict (409, z.B. doppelte Buchung)
  - Invalid Timezone (400)
  - Auth Expired (401)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `calp`
- [ ] kordp-Routing konfigurieren (Decision72 → calp)
- [ ] CMD-Safepoint für Event-Operationen (Create/Update/Delete)
- [ ] RESP-Safepoint mit Event-IDs/Status
- [ ] Integration mit opena1 für orchestrierte Terminplanung
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Calendar-Ops
- [ ] Nohup-Log (`logs/opena14.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Event-Erstellung (CMD mit Summary/Time, RESP mit Event-ID)
  - Event-Aktualisierung (CMD mit Changes, RESP mit Status)
  - Event-Löschung (CMD mit Event-ID, RESP mit Confirmation)
- [ ] Secret-Masking für OAuth-Tokens in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Datenschutz: Keine personenbezogenen Event-Details im Klartext

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Timezone-Handling, Recurrence-Rules
- [ ] Integration-Tests gegen Test-Google-Calendar
- [ ] Tests für Edge-Cases:
  - Ganztägige Events
  - Serientermine (RRULE)
  - Mehrere Zeitzonen
  - Overlap-Detection
- [ ] Mock für Google Calendar API (keine echten Events in CI/CD)
- [ ] E2E-Test: Event erstellen → Kalender sync → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - Google Calendar OAuth-Setup
  - iCal-Datei-Import
  - Timezone-Handling-Best-Practices
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - OAuth-Tokens niemals hardcoden
  - Read-Only-Zugriff für Reporting
  - Kalender-Sharing-Berechtigungen prüfen
- [ ] Architekturdiagramm (Google Calendar ↔ opena14 ↔ Portier)
- [ ] Troubleshooting-Guide (Auth-Fehler, Timezone-Konflikte, Sync-Issues)
- [ ] Deployment-Anleitung (Docker, OAuth-Token-Rotation)

---

**Letzte Aktualisierung:** 27. November 2025  
**Maintainer:** Danijel Jokic (ELION Team)
