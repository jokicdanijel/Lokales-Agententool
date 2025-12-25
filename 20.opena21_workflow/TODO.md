# TODO – opena21 Workflow Engine Agent

**Port:** 12365
**Status:** 🟡 Planned
**Kürzel:** `workflowp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_workflow_agent.py` erstellen (Port 12365)
- [ ] Config-Modul für Workflow-Definitions (YAML/JSON), Execution-Mode, Timeout
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] Workflow-Engine (State-Machine) implementieren
- [ ] Task-Queue (Celery/Redis) für asynchrone Steps integrieren
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena21.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/workflows/list` – Workflows auflisten (GET)
- [ ] `/workflows/create` – Workflow erstellen (POST)
- [ ] `/workflows/execute` – Workflow starten (POST)
- [ ] `/workflows/status` – Workflow-Status abfragen (GET)
- [ ] `/workflows/cancel` – Workflow abbrechen (POST)
- [ ] Pydantic-Schemas für:
  - `WorkflowDefinition` (name, steps, triggers, timeout)
  - `ExecuteRequest` (workflow_id, inputs, mode)
  - `StatusResponse` (workflow_id, state, current_step, outputs)
  - `Step` (name, action, inputs, outputs, retry_policy)
- [ ] Error-Handling für:
  - Workflow Not Found (404)
  - Step Failed (500)
  - Timeout Exceeded (504)
  - Invalid Transition (422)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `workflowp`
- [ ] kordp-Routing konfigurieren (Decision72 → workflowp)
- [ ] CMD-Safepoint für Workflow-Start
- [ ] RESP-Safepoint mit Execution-ID
- [ ] Integration mit allen Agenten (opena3-opena20) als Workflow-Steps
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Workflow-Events
- [ ] Nohup-Log (`logs/opena21.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Workflow-Start (CMD mit Definition, RESP mit Execution-ID)
  - Step-Execution (CMD mit Step-Name, RESP mit Output)
  - Workflow-Completion (CMD mit Final-State, RESP mit Outputs)
- [ ] Secret-Masking für Step-Inputs (z.B. API-Keys)
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Workflow-History in DB persistieren (für Replay/Debugging)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für State-Machine, Step-Validation
- [ ] Integration-Tests mit Multi-Step-Workflows
- [ ] Tests für Edge-Cases:
  - Step-Retry (3x)
  - Timeout während Step
  - Circular Dependencies
  - Conditional Branches
- [ ] Mock für Agent-Calls (keine echten Agent-Aufrufe in CI/CD)
- [ ] E2E-Test: Workflow definieren → Starten → 3 Steps → Completion → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - Workflow-Definition-Format (YAML/JSON)
  - State-Machine-Diagramm
  - Retry-Policies und Timeout-Handling
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - Workflow-Definitions validieren (keine Code-Injection)
  - Step-Outputs sanitizen
  - Execution-Timeout strikt enforgen
- [ ] Architekturdiagramm (Workflow-Engine ↔ Task-Queue ↔ Agents ↔ Portier)
- [ ] Troubleshooting-Guide (Step-Failures, Timeouts, Retry-Loops)
- [ ] Deployment-Anleitung (Docker, Celery-Worker, Redis-Setup)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
