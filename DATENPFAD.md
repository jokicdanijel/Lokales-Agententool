# 🔄 Datenpfad des ELION-Systems

**Detaillierte Dokumentation der Datenflüsse und Verarbeitungspipelines**

- 📅 **Datum:** 24. November 2025
- 🎯 **Zweck:** Referenz für Integrations-Architekten und DevOps-Teams
- 📍 **Scope:** Nur Abschnitt 2 aus `ELION_SYSTEM_ARCHITECTURE.md`

---

## Datenpfad

Der Datenpfad beschreibt die komplexe Bewegung von Informationen durch das System, vom initialen Input bis zur endgültigen Persistierung und Auditierung.

### Eingangsquellen und Eingabepunkte

Daten treten über vier primäre Kanäle ein:

1. **OpenWebUI-Frontend** (Port 3000) → HTTP-Requests an LocalAgent-Pro (Port 8001)
2. **Telegram Bot** → opena3-Bridge (Port 12347) als Message Relay
3. **GitHub Webhooks** → opena3-Bridge für Push/PR-Events
4. **Lokale Shell-Befehle & Dateioperationen** → `/api/file/*` und `/api/shell/exec` Endpoints

### Verarbeitungspipeline (Hauptflow)

```
Eingabe (Frontend/Telegram/GitHub/Shell)
    ↓
LocalAgent-Pro API (Port 8001)
    ├─ Security Check (Sandbox-Isolation, Whitelisting)
    ├─ Request Deduplication (MD5-Hash)
    ├─ Tool Selection (write_file, read_file, shell_exec, etc.)
    ↓
Tool Execution (mit Error-Handling)
    ├─ Dateioperationen → Sandbox Dir (~/ localagent_sandbox)
    ├─ Shell-Befehle → whitelistete Commands
    ├─ Ollama/OpenAI API Calls → externe AI-Services
    ↓
Safepoint Recording (opena3-Bridge, Port 12347)
    ├─ Snapshot vor/nach Operation
    ├─ SHA-256 Hash (Integrität & Unveränderbarkeit)
    ├─ Timestamp & Metadata
    ↓
Persistierung (Archiv & Audit)
    ├─ Event in archivp_store/index.jsonl
    ├─ Eintrag in audit_hashes.log
    ├─ Bei Fehler: Rollback & Notification
    ↓
Monitoring & Logging
    ├─ Health-Check (5s Interval) → HealthRecords in SQLite
    ├─ Prometheus Metrics Export
    ├─ Koordinator-Aggregation (Port 12344)
    ↓
Ausgabe (Frontend/API/Logs)
```

### Spezifische Datenbewegungen nach Use-Case

**Use-Case 1 – Datei-Operation (z. B. write_file):**

```
OpenWebUI → LocalAgent-Pro /api/file/write
  → Sanitization (path traversal check)
  → Sandbox-Schreiboperation
  → Safepoint (opena3)
  → archivp_store/index.jsonl
  → Audit-Hash
  → Response zu OpenWebUI
```

**Use-Case 2 – Telegram-Nachricht:**

```
Telegram Bot
  → opena3-Bridge /message/relay
  → Nachricht zu OpenWebUI API forwarden
  → Safepoint-Checkpoint
  → archive.db Eintrag
  → Health-Update
  → Dashboard-Refresh
```

**Use-Case 3 – Patch-Delivery (GitHub Guard):**

```
Patch-Block (Unified-Diff)
  → Guardian vor-Sync-Check
  → Git-Pull (wenn synchronized)
  → Patch anwenden (git apply)
  → Datei-Update
  → Syntax-Validierung
  → AuditLog (Vorher/Nachher Hash)
  → CI/CD-Tests
  → Erfolg/Failure Notification
```

**Use-Case 4 – Voice-Programm-Ausführung (z. B. voice_scheduler):**

```
Frontend /api/program/start
  → tools/voice_scheduler.py Launch
  → Sprach-Input/Menu-Navigation
  → Task in tasks.json persistent
  → Status-Poll via /api/status
  → Dashboard-Update mit Completion-Status
```

### Sicherheits- und Integritäts-Layer

Alle Datenbewegungen unterliegen mehreren Schutzmechanismen:

- **Loop-Protection**: MD5-Request-Deduplication verhindert Rekursionen
- **Escape-Prevention**: Sandbox-Isolation für alle Dateioperationen
- **Secret-Masking**: OPENAI_API_KEY_VSCODE wird nie geloggt
- **TLS-Plan**: Für zukünftige HTTPS-Kommunikation
- **RBAC-Entwurf**: Rollenbasierte Zugriffskontrolle vorgesehen

---

## 🔗 Weiterführende Dokumentation

- **Gesamtübersicht:** `../ELION_SYSTEM_ARCHITECTURE.md`
- **Datenstruktur:** `DATENSTRUKTUR.md`
- **Projektstruktur:** `PROJEKTSTRUKTUR.md`

---

**Letztes Update:** 24. November 2025
