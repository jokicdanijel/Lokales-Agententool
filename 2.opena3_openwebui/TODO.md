# TODO – opena3 OpenWebUI Terminal Agent

**Port:** 12347  
**Status:** ✅ Running  
**Kürzel:** `owuip`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [x] FastAPI-Service `main_openwebui_agent.py` implementiert (Port 12347)
- [x] OpenWebUI Adapter implementiert (Port 12350, HTTP-Forwarder)
- [x] Config-Modul für Ports, Tokens, OpenWebUI-URL erstellt
- [x] Health-Endpoint `/health` implementiert
- [ ] Erweiterte Config für Multi-Model-Support
- [ ] Rate-Limiting-Konfiguration verfeinern
- [ ] Logging-Levels konfigurierbar machen

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [x] `/health` – Health-Check-Endpoint
- [x] `/command` – Command-Execution-Endpoint
- [x] `/invoke` – Direct Tool Invocation
- [x] Pydantic-Schemas mit `extra="forbid"`
- [ ] `/chat/stream` – SSE-basierter Chat-Stream
- [ ] `/models/list` – Verfügbare Modelle auflisten
- [ ] Error-Handling für OpenWebUI-Ausfälle (502, 504)
- [ ] Retry-Mechanismen mit Exponential Backoff

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [x] Registrierung in `tool_registry.json` als `owuip`
- [x] Adapter-Service für HTTP-Forwarding zu OpenWebUI (8080)
- [ ] Idempotente Agent-Registrierung via `register_if_absent()`
- [ ] Integration in kordp-Routing (Decision72 → owuip)
- [ ] Test des vollständigen Option-2-Flows
- [ ] CMD/RESP-Safepoints für Chat-Requests

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [x] Nohup-Logs (`logs/opena3.nohup.log`, `logs/openwebui_adapter.nohup.log`)
- [ ] Strukturiertes JSON-Logging implementieren
- [ ] Safepoint-Erstellung für alle Chat-Interaktionen
- [ ] Secret-Masking für Bearer-Tokens in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Integration mit zentralem Logging-System

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [x] Health-Check-Tests (`scripts/test_openwebui.py`)
- [x] Command-Endpoint-Tests
- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Integrationstests gegen echte OpenWebUI-Instanz
- [ ] Load-Tests (100+ parallele Chat-Requests)
- [ ] Mocking für externe OpenWebUI-Abhängigkeit
- [ ] CI/CD-Integration (GitHub Actions)

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [x] README.md mit Grundstruktur vorhanden
- [x] API-Dokumentation in `docs/OPENWEBUI_API.md`
- [ ] Vollständige Endpoint-Beschreibungen mit cURL-Beispielen
- [ ] Security-Hinweise (Bearer-Token-Handling, TLS-Empfehlungen)
- [ ] Troubleshooting-Guide erweitern
- [ ] Architekturdiagramm (OpenWebUI ↔ Adapter ↔ opena3)
- [ ] Deployment-Anleitung (Docker, systemd)

---

**Letzte Aktualisierung:** 27. November 2025  
**Maintainer:** Danijel Jokic (ELION Team)
