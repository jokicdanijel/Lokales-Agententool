# TODO – opena5 VS Code Agent

**Port:** 12351  
**Status:** 🟡 Planned  
**Kürzel:** `vscop`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_vscode_agent.py` erstellen (Port 12351)
- [ ] Config-Modul für Workspace-Pfade, Allowed Extensions, Max File Size
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] File-System-Watcher für Workspace-Änderungen (watchdog)
- [ ] VS Code Extension API Integration (falls Remote Development)
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena5.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/workspace/list` – Dateien/Ordner im Workspace auflisten
- [ ] `/file/read` – Datei lesen (POST mit Pfad)
- [ ] `/file/write` – Datei schreiben/bearbeiten (POST)
- [ ] `/search` – Code-Suche (grep/ripgrep-basiert)
- [ ] `/analyze` – Code-Analyse (AST, Linting)
- [ ] Pydantic-Schemas für:
  - `FileReadRequest` (path, encoding)
  - `FileWriteRequest` (path, content, mode)
  - `SearchRequest` (pattern, file_types, max_results)
  - `AnalyzeRequest` (path, analyzers)
- [ ] Error-Handling für:
  - File Not Found (404)
  - Permission Denied (403)
  - File Too Large (413)
  - Invalid Path (400)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `vscop`
- [ ] kordp-Routing konfigurieren (Decision72 → vscop)
- [ ] CMD-Safepoint für File-Operations (Read, Write, Search)
- [ ] RESP-Safepoint mit Datei-Metadaten (keine vollen Inhalte bei großen Files)
- [ ] Integration mit opena1 für orchestrierte Code-Analysen
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle File-Ops
- [ ] Nohup-Log (`logs/opena5.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Datei-Lesevorgänge (CMD mit Pfad, RESP mit Dateiinhalt)
  - Datei-Schreibvorgänge (CMD mit Änderungen, RESP mit Status)
  - Suchen (CMD mit Pattern, RESP mit Treffern)
- [ ] Secret-Masking für Pfade mit sensiblen Namen (`.env`, `secrets/`)
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Keine vollständigen Dateiinhalte in Safepoints (nur Metadaten + Diffs)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für File-Read/Write-Logic
- [ ] Integration-Tests gegen Dummy-Workspace
- [ ] Tests für Edge-Cases:
  - Große Dateien (>10 MB)
  - Binärdateien
  - Symlinks
  - Geschützte Dateien
- [ ] Mock für Filesystem (keine echten File-Ops in CI/CD)
- [ ] E2E-Test: File-Read → Analyse → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - Workspace-Setup-Anleitung
  - Allowed File Extensions
  - Max File Size Policy
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - Path-Traversal-Schutz (`../` blockieren)
  - Keine destruktiven Ops ohne Confirmation
  - Workspace außerhalb kritischer System-Pfade
- [ ] Architekturdiagramm (VS Code ↔ opena5 ↔ Portier)
- [ ] Troubleshooting-Guide (Permission-Fehler, Encoding-Probleme)
- [ ] Deployment-Anleitung (Docker, Read-Only-Modus)

---

**Letzte Aktualisierung:** 27. November 2025  
**Maintainer:** Danijel Jokic (ELION Team)
