# TODO – opena18 CRM Agent

**Port:** 12363  
**Status:** 🟡 Planned  
**Kürzel:** `crmp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_crm_agent.py` erstellen (Port 12363)
- [ ] Config-Modul für DB-Anbindung (SQLite/PostgreSQL), RBAC-Regeln
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token + RBAC) einrichten
- [ ] SQLAlchemy-Models für Contact, Organization, Deal, Activity
- [ ] Relations implementieren (Contact ↔ Organization ↔ Deal)
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena18.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/contacts` – Kontakte verwalten (GET/POST/PUT/DELETE)
- [ ] `/organizations` – Organisationen verwalten (GET/POST/PUT/DELETE)
- [ ] `/deals` – Deals verwalten (GET/POST/PUT/DELETE)
- [ ] `/activities` – Aktivitäten loggen (POST/GET)
- [ ] `/search` – Globale Suche (POST)
- [ ] Pydantic-Schemas für:
  - `Contact` (name, email, phone, organization_id, tags)
  - `Organization` (name, industry, size, website)
  - `Deal` (title, value, stage, contact_id, close_date)
  - `Activity` (type, subject, contact_id, deal_id, timestamp)
- [ ] Error-Handling für:
  - Contact Not Found (404)
  - Duplicate Email (409)
  - Invalid Stage Transition (422)
  - Permission Denied (403)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `crmp`
- [ ] kordp-Routing konfigurieren (Decision72 → crmp)
- [ ] CMD-Safepoint für CRUD-Operationen
- [ ] RESP-Safepoint mit Entity-IDs
- [ ] Integration mit opena9 (Telefonie), opena7 (E-Mail), opena12 (Social)
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle CRM-Ops
- [ ] Nohup-Log (`logs/opena18.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Contact-Erstellung (CMD mit Daten, RESP mit Contact-ID)
  - Deal-Update (CMD mit Changes, RESP mit New-Stage)
  - Activity-Logging (CMD mit Type/Subject, RESP mit Activity-ID)
- [ ] Secret-Masking für sensible Kontaktdaten
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] DSGVO-konforme Speicherung (Löschfristen, Einwilligungen)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Relations, Deal-Stage-Validation
- [ ] Integration-Tests mit In-Memory-DB
- [ ] Tests für Edge-Cases:
  - Circular Relations
  - Orphaned Deals
  - Duplicate Contacts
  - Permission-Checks
- [ ] Mock für DB (keine echten Writes in CI/CD)
- [ ] E2E-Test: Contact erstellen → Deal verknüpfen → Activity loggen → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - DB-Schema (Contacts, Orgs, Deals, Activities)
  - RBAC-Konzept (Sales, Admin, Read-Only)
  - Deal-Pipeline-Konfiguration
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - DSGVO-Compliance (Auskunftsrecht, Löschpflicht)
  - Sensitive-Data-Masking
  - Audit-Logs für CRUD-Ops
- [ ] Architekturdiagramm (opena7/opena9/opena12 ↔ opena18 ↔ DB ↔ Portier)
- [ ] Troubleshooting-Guide (Relation-Fehler, Permission-Issues)
- [ ] Deployment-Anleitung (Docker, DB-Backup, Migrations)

---

**Letzte Aktualisierung:** 27. November 2025  
**Maintainer:** Danijel Jokic (ELION Team)
