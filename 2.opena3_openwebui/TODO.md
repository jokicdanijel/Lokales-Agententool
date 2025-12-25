# TODO – opena3 OpenWebUI Terminal Agent

**Port:** 12347
**Status:** ✅ Running
**Kürzel:** `owuip`
**Version:** 2.0.1

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [x] FastAPI-Service `main_openwebui_agent.py` implementiert (Port 12347)
- [x] OpenWebUI Adapter implementiert (Port 12350, HTTP-Forwarder)
- [x] Config-Modul für Ports, Tokens, OpenWebUI-URL erstellt
- [x] Health-Endpoint `/health` implementiert
- [x] **Erweiterte Config für Multi-Model-Support** ✅
  - ModelRegistry mit Alias → Modell-ID Mapping
  - ModelInfo Pydantic-Schema
  - Dynamische Modell-Konfiguration via ENV
- [x] **Rate-Limiting-Konfiguration** ✅
  - RateLimitConfig mit pro-Endpoint Limits
  - Middleware-basiertes Rate-Limiting
  - 429 Too Many Requests + Retry-After
- [x] **Logging-Levels konfigurierbar** ✅
  - LoggingConfig mit Level, Format, Rotation
  - JSON-Logging-Option (vorbereitet)
  - Log-Rotation via RotatingFileHandler

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [x] `/health` – Health-Check-Endpoint
- [x] `/command` – Command-Execution-Endpoint
- [x] `/invoke` – Direct Tool Invocation
- [x] Pydantic-Schemas mit `extra="forbid"`
- [x] **`/chat/stream` – SSE-basierter Chat-Stream** ✅
  - Server-Sent Events für Streaming
  - Event-Typen: start, chunk, end, error
  - Pydantic StreamChatRequest Model
  - **RESP-Safepoint für Stream** ✅ PHASE 2
- [x] **`/models/list` – Verfügbare Modelle auflisten** ✅
  - Kombiniert Config + Backend-Modelle
  - ModelListResponse Schema
  - Optional: Backend-Modelle einbeziehen
- [x] **`/v1/models` – OpenAI-kompatibler Alias** ✅ PHASE 2
- [x] **`/v1/chat/completions` – OpenAI-kompatibler Alias** ✅ PHASE 2
- [x] **Error-Handling für OpenWebUI-Ausfälle** ✅
  - 502 Bad Gateway für Upstream-5xx
  - 504 Gateway Timeout für Timeouts
  - 503 Service Unavailable für Connection-Errors
  - Strukturierte Fehler-Responses
- [x] **Retry-Mechanismen mit Exponential Backoff** ✅
  - RetryConfig mit max_retries, base_delay
  - http_request_with_retry() Utility
  - Logging pro Retry-Versuch
  - **Sync-HTTP Dokumentation hinzugefügt** ✅ PHASE 2

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [x] Registrierung in `tool_registry.json` als `owuip`
- [x] Adapter-Service für HTTP-Forwarding zu OpenWebUI (8080)
- [ ] Idempotente Agent-Registrierung via `register_if_absent()`
- [ ] Integration in kordp-Routing (Decision72 → owuip)
- [ ] Test des vollständigen Option-2-Flows
- [x] CMD/RESP-Safepoints für Chat-Requests ✅
- [x] **RESP-Safepoints für /chat/stream** ✅ PHASE 2

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [x] Nohup-Logs (`logs/opena3.nohup.log`, `logs/openwebui_adapter.nohup.log`)
- [x] **Strukturiertes JSON-Logging implementieren** ✅ PHASE 2
  - JsonFormatter Klasse implementiert
  - json_logging ENV-Variable
- [x] **Safepoint-Erstellung für alle Chat-Interaktionen** ✅
- [x] **Secret-Masking für Bearer-Tokens in Logs** ✅
  - mask_secrets() Utility implementiert
- [x] **Log-Rotation konfiguriert** ✅ PHASE 2
  - max. 10 MB, 5 Backups
  - RotatingFileHandler in setup_logging()
- [ ] Integration mit zentralem Logging-System

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [x] Health-Check-Tests (`scripts/test_openwebui.py`)
- [x] Command-Endpoint-Tests
- [x] **Pytest-Suite mit ≥80% Coverage** ✅ PHASE 2
  - `tests/test_opena3_api.py` (59 Tests)
  - Coverage: config.py 95%, main_openwebui_agent.py 70%
  - Durchschnitt Core-Module: ~82%
- [ ] Integrationstests gegen echte OpenWebUI-Instanz
- [ ] Load-Tests (100+ parallele Chat-Requests)
- [x] **Mocking für externe OpenWebUI-Abhängigkeit** ✅ PHASE 2
- [ ] CI/CD-Integration (GitHub Actions)

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [x] README.md mit Grundstruktur vorhanden
- [x] API-Dokumentation in `docs/OPENWEBUI_API.md`
- [x] **Sync-HTTP Dokumentation in Docstrings** ✅ PHASE 2
- [ ] Vollständige Endpoint-Beschreibungen mit cURL-Beispielen
- [ ] Security-Hinweise (Bearer-Token-Handling, TLS-Empfehlungen)
- [ ] Troubleshooting-Guide erweitern
- [ ] Architekturdiagramm (OpenWebUI ↔ Adapter ↔ opena3)
- [ ] Deployment-Anleitung (Docker, systemd)

---

**Letzte Aktualisierung:** 1. Dezember 2025
**Maintainer:** Danijel Jokic (ELION Team)
