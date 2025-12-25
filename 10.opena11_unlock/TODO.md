# TODO – opena11 Unlock Master Agent

**Port:** 12356
**Status:** 🟡 Planned
**Kürzel:** `unlockp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_unlock_agent.py` erstellen (Port 12356)
- [ ] Config-Modul für RBAC-Regeln, Default-Policies, Session-Timeout
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token + RBAC-Layer) einrichten
- [ ] Permission-Store (JSON/YAML oder SQLite)
- [ ] Audit-Log für alle Grant/Revoke-Operationen
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena11.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/grant` – Berechtigung erteilen (POST)
- [ ] `/revoke` – Berechtigung entziehen (POST)
- [ ] `/check` – Berechtigung prüfen (POST)
- [ ] `/list` – Alle Berechtigungen auflisten (GET)
- [ ] `/audit` – Audit-Log abrufen (GET)
- [ ] Pydantic-Schemas für:
  - `GrantRequest` (subject, resource, action, expires_at)
  - `RevokeRequest` (subject, resource, action)
  - `CheckRequest` (subject, resource, action)
  - `CheckResponse` (allowed, reason)
  - `AuditLogEntry` (timestamp, operation, subject, resource, actor)
- [ ] Error-Handling für:
  - Unauthorized (401)
  - Forbidden (403)
  - Resource Not Found (404)
  - Permission Already Exists (409)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `unlockp`
- [ ] kordp-Routing konfigurieren (Decision72 → unlockp)
- [ ] CMD-Safepoint für Grant/Revoke-Operationen
- [ ] RESP-Safepoint mit Audit-Informationen
- [ ] Integration mit anderen Agenten (z.B. opena5 für File-Ops)
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Permission-Ops
- [ ] Nohup-Log (`logs/opena11.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Grant-Operationen (CMD mit Subject/Resource, RESP mit Permission-ID)
  - Revoke-Operationen (CMD mit Permission-ID, RESP mit Status)
  - Check-Operationen (CMD mit Query, RESP mit Allow/Deny)
- [ ] Secret-Masking für sensible Resource-Namen
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Audit-Log extern archivieren (WORM-Storage für Compliance)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für RBAC-Logic, Permission-Checks
- [ ] Integration-Tests mit In-Memory-Permission-Store
- [ ] Tests für Edge-Cases:
  - Expired Permissions
  - Hierarchische Ressourcen (z.B. `/files/*`)
  - Wildcard-Permissions
  - Konflikt-Resolution
- [ ] Mock für Permission-Store (keine echten DB-Writes in CI/CD)
- [ ] E2E-Test: Grant → Check → Revoke → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - RBAC-Konzept (Subjects, Resources, Actions)
  - Permission-Format (JSON/YAML)
  - Expiration-Handling
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - Least-Privilege-Prinzip
  - Keine Default-Permissions ohne Audit
  - Regelmäßige Permission-Reviews
- [ ] Architekturdiagramm (Agents ↔ opena11 ↔ Permission-Store ↔ Portier)
- [ ] Troubleshooting-Guide (Permission-Denial, Expiration, Audit-Log-Fehler)
- [ ] Deployment-Anleitung (Docker, Permission-Store-Backup, Compliance)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
