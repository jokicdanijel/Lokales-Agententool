# Schritt 5 – opena5 · VS Code Bridge

**Erstellt am:** 2025-11-09 UTC
**Verantwortlich:** *(Team/Person eintragen)*
**Version:** 1.0
**Regeln:** Append-only · Dedupe (SHA-256/IDs) · keine Doppelblobs · Auditierbarkeit durchgängig

---

## 0) Zweck & Rolle

„opena5" ist die **VS Code-Integration** des Agenten-Systems. Sie verbindet deinen Quellcode-Editor mit dem Agent-Stack und ermöglicht:

- **Eingang:** EDIT/DIFF-Aufgaben von UI (opena3) oder Bot (opena4)
- **Verarbeitung:** VS Code öffnet Workspace, zeigt Änderungen, Entwickler bearbeitet
- **Rückmeldung:** Status/Bestätigung ins Archiv (opena2) und UI

### Datenfluss

```
┌──────────┐    (Edit-Aufgabe)     ┌──────────┐
│  opena3  │ ───────────────────▶ │  opena5  │
│  (UI)    │                        │  (VSCode)│
└──────────┘                        └────┬─────┘
     ▲                                    │
     │                                    │
     │          (Status zurück)           ▼
     └────────────────────────────────┐
                                      │
                              ┌──────────┐
                              │  opena2  │ (Archivator)
                              └────┬─────┘
                                   │
                                   ▼
                              ┌──────────┐
                              │  opena1  │ (Koordinator)
                              └──────────┘
```

**Alle Aktionen** laufen über **opena2 (Archivator)** als "Single Source of Truth" und **opena1 (Koordinator)** als Ausführungssteuerung. VS Code (opena5) ist Teil des Rückflusses: erhält Aufgaben, macht Änderungen, spielt zurück.

---

## 1) Topologie & Verbindungen

### Port-Binding

- **opena5 API-Port:** Typischerweise im Bereich 12344–12349 (z.B. **12348**)
- **Keine** Bindung auf Port 8080 erlaubt (ausschließlich für opena3 UI)
- **Loopback-Binding:** 127.0.0.1:12348 (nur lokal im Workspace-Container)

### Port-Leases

In `.runtime/port_leases.json` wird eingetragen:

```json
{
  "leases": [
    {
      "agent": "opena5",
      "port": 12348,
      "ts": "2025-11-09T12:00:00Z",
      "state": "ide-bridge",
      "owner": "vscode-integration"
    }
  ],
  "pool": "12344-12399",
  "forbidden": [8080]
}
```

### Netzwerk-Topologie

```
VS Code (local)
    │
    ├─ Extension Hook → http://127.0.0.1:12348/tasks/apply
    │
    └─ CLI Integration: `vscode-agent --patch <file>`
              │
              ▼
    opena5 API Server (Port 12348)
              │
              ├─ Safepoint CMD → opena2/archiv/...
              │
              └─ Safepoint RESP ← opena2/archiv/...
```

---

## 2) Aufgaben-Workflow & Persistenz

### 2.1 Aufgaben kommen rein (von opena3/opena4)

Wenn über **UI (opena3)** oder **Bot (opena4)** eine Edit/DIFF-Aufgabe generiert wird:

| Feld | Wert | Beschreibung |
|------|------|-------------|
| `event_type` | `EDIT_TASK` | Aufgabentyp |
| `file_path` | `src/main.py` | Zieldatei im Workspace |
| `diff_content` | `@@ -5,3 +5,5 @@ ...` | Unified Diff Format |
| `diff_sha256` | `a1b2c3d4...` | SHA-256 Hash des Diffs (für Dedupe) |
| `request_id` | UUID v4 | Eindeutige Anfrage-ID |
| `timestamp` | ISO-8601 Z | Erstellungszeit |
| `source` | `opena3` oder `opena4` | Ursprung |
| `target_preference` | `opena5` (optional) | Bevorzugter Ziel-Agent |
| `project` | `{"id": "proj-001", "name": "Gesamtprojekt"}` | Projekt-Metadaten |
| `strict` | `true` | Compliance-Flag |

### 2.2 Persistierung (Append-Only)

**Pfadschema:**

```
archivp/2025/11/09/
  ├── SP1731156000_opena3→opena5_EDIT_TASK.json
  │   {
  │     "event_type": "EDIT_TASK",
  │     "file_path": "src/main.py",
  │     "diff_sha256": "a1b2c3d4...",
  │     "request_id": "11111111-1111-4111-8111-111111111111",
  │     "timestamp": "2025-11-09T12:00:00Z",
  │     "payload": {...}
  │   }
  │
  └── SP1731156001_opena5→opena2_CMD.json
      {
        "event_type": "EDIT_APPLY",
        "file_path": "src/main.py",
        "diff_sha256": "a1b2c3d4...",
        "author": "vscode-integration",
        "status": "applied",
        "details": {"lines_changed": 5, "applied_at": "2025-11-09T12:00:01Z"}
      }
```

**Dateiname-Format:** `SP<unix_ts>_<src>→<dst>_<event_type>.json`

### 2.3 Dedupe-Logik

- **Before Write:** Berechne `SHA-256(diff_content)`
- **Lookup:** Frage `.dedup_index` nach diesem Hash
  - **Hit:** Datei existiert bereits → nur Audit-Eintrag anhängen (Referenz)
  - **Miss:** Schreibe neue Datei, trage Hash in Dedupe-Index ein

```json
{
  ".dedup_index": {
    "a1b2c3d4e5f6g7h8...": "archivp/2025/11/09/SP1731156000_opena3→opena5_EDIT_TASK.json"
  }
}
```

### 2.4 Audit-Index

Jedes Event wird in `index.jsonl` logarithmisch festgehalten (Append-Only):

```jsonl
{"ts":"2025-11-09T12:00:00Z","event":"EDIT_TASK","source":"opena3","target":"opena5","file":"src/main.py","hash":"a1b2c3d4...","request_id":"11111...","status":"received"}
{"ts":"2025-11-09T12:00:01Z","event":"EDIT_APPLY","source":"opena5","target":"opena2","file":"src/main.py","hash":"a1b2c3d4...","request_id":"11111...","status":"applied"}
{"ts":"2025-11-09T12:00:02Z","event":"EDIT_RESP","source":"opena2","target":"opena5","file":"src/main.py","hash":"a1b2c3d4...","request_id":"11111...","status":"ok","details":"File updated in archiv"}
```

---

## 3) VS Code Bridge – API-Endpoints

### 3.1 Task-Polling

```http
GET /tasks/poll
Host: 127.0.0.1:12348
Authorization: Bearer <token>
Content-Type: application/json
```

**Response (200):**

```json
{
  "tasks": [
    {
      "request_id": "11111111-1111-4111-8111-111111111111",
      "event_type": "EDIT_TASK",
      "file_path": "src/main.py",
      "diff_content": "@@ -5,3 +5,5 @@ ...",
      "diff_sha256": "a1b2c3d4...",
      "timestamp": "2025-11-09T12:00:00Z",
      "source": "opena3",
      "project": {"id": "proj-001", "name": "Gesamtprojekt"},
      "strict": true
    }
  ],
  "count": 1
}
```

**Response (204):** Keine Aufgaben vorhanden

---

### 3.2 Task-Anwendung

```http
POST /tasks/apply
Host: 127.0.0.1:12348
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "request_id": "11111111-1111-4111-8111-111111111111",
  "file_path": "src/main.py",
  "diff_sha256": "a1b2c3d4...",
  "action": "apply",
  "timestamp": "2025-11-09T12:00:01Z"
}
```

**Response (200):**

```json
{
  "request_id": "11111111-1111-4111-8111-111111111111",
  "timestamp": "2025-11-09T12:00:01Z",
  "source": "opena5",
  "status": "applied",
  "safepoint": "SP1731156001_opena5→opena2_CMD.json",
  "details": {
    "file_path": "src/main.py",
    "lines_changed": 5,
    "applied_at": "2025-11-09T12:00:01Z"
  },
  "strict": true
}
```

**Response (400):** Schema-Fehler (8.3 Format)

```json
{
  "request_id": "11111111-1111-4111-8111-111111111111",
  "timestamp": "2025-11-09T12:00:01Z",
  "source": "opena5",
  "error": {
    "code": "INVALID_DIFF",
    "message": "Diff konnte nicht auf Datei angewendet werden",
    "details": {
      "file_path": "src/main.py",
      "reason": "Hunks do not apply cleanly"
    }
  },
  "strict": true
}
```

---

### 3.3 Status-Abfrage

```http
GET /tasks/status/<request_id>
Host: 127.0.0.1:12348
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "request_id": "11111111-1111-4111-8111-111111111111",
  "status": "applied",
  "file_path": "src/main.py",
  "events": [
    {"ts": "2025-11-09T12:00:00Z", "event": "EDIT_TASK", "source": "opena3"},
    {"ts": "2025-11-09T12:00:01Z", "event": "EDIT_APPLY", "source": "opena5"}
  ]
}
```

---

### 3.4 Health-Endpoint

```http
GET /health
Host: 127.0.0.1:12348
```

**Response (200):**

```json
{
  "service": "opena5",
  "status": "ok",
  "timestamp": "2025-11-09T12:00:00Z",
  "port_policy": {
    "window": [12344, 12349],
    "forbidden": [8080]
  },
  "vscode_workspace": "/path/to/workspace",
  "archivp_connected": true
}
```

---

## 4) Implementierungs-Checkliste

### Phase 1: Core Struktur

- [ ] `1.opena1&2_portier/vscode_integration.py` – VS Code Bridge API
- [ ] Pydantic Schemas für EDIT_TASK, EDIT_APPLY, EDIT_RESP
- [ ] Task-Queue (in-Memory oder Redis-backed)
- [ ] Safepoint-Generator (CMD/RESP Persistierung)

### Phase 2: Integration

- [ ] opena5 in Port-Leases registrieren
- [ ] Health-Endpoint mit Port-Policy
- [ ] Dedupe-Logik für Diffs
- [ ] Audit-Index Schreiben

### Phase 3: Sicherheit & Validierung

- [ ] Authorization Header Check
- [ ] Diff-Validierung (patch-Apply-Sicherheit)
- [ ] Secrets in Logs maskieren
- [ ] HTTPS/TLS für Webhook (falls extern)

### Phase 4: Testing & Dokumentation

- [ ] Unit Tests für Diff-Parser & Dedupe
- [ ] Integration Tests (opena3 → opena5 → opena2)
- [ ] Dokumentation: VS Code Extension Hook
- [ ] Fehlerszenarien + Recovery

---

## 5) Sicherheit & Compliance

### 5.1 Strikte Port-Policy

- ✅ Nur Ports 12344–12349 erlaubt
- ❌ Port 8080 strikt verboten
- ✅ Loopback-Binding (127.0.0.1) nur
- ✅ Port-Lease in `.runtime/port_leases.json`

### 5.2 Secrets & Authentifizierung

- Authorization-Token in Header
- Masking in Logs: `token=***...***`
- Keine Tokens in Safepoints/Blobs
- .env-basierte Token-Verwaltung

### 5.3 Append-Only Garantie

- Keine Überschreibungen von Safepoints
- Nur neue Dateien oder Referenzen erlaubt
- Audit-Index ist nur Lesbar nach Write
- HEADS.json für Integrity Checks

### 5.4 Dedupe & Integrity

- SHA-256 Hash aller Diffs
- Dedupe-Index pflegen
- Hash-Mismatch → Error
- INTEGRITY.json mit Checksums

---

## 6) Fehlerbehandlung & Recovery

| Fehler | Code | HTTP | Behandlung |
|--------|------|------|-----------|
| Diff ungültig | `INVALID_DIFF` | 400 | Safepoint mit ERROR-Flag, Audit-Log |
| Authentifizierung fehlgeschlagen | `UNAUTHORIZED` | 401 | Request ablehnen, Log |
| Port-Policy verletzt | `PORT_POLICY_VIOLATION` | 403 | Server startet nicht |
| Archiv unerreichbar | `ARCHIV_UNREACHABLE` | 503 | Health-Check FAILED, Retry-Logic |
| Datei nicht gefunden | `FILE_NOT_FOUND` | 404 | Error-Safepoint, Audit |

---

## 7) Beispiel-Workflow

### Szenario: UI (opena3) schickt Edit-Task

**Schritt 1:** User klickt in UI auf "Edit this file"

```json
{
  "request_id": "11111111-1111-4111-8111-111111111111",
  "file_path": "src/models/user.py",
  "diff_content": "@@ -10,3 +10,5 @@ class User: ...",
  "source": "opena3",
  "target_preference": "opena5"
}
```

↓ wird in `archivp/2025/11/09/SP1731156000_opena3→opena5_EDIT_TASK.json` gespeichert

**Schritt 2:** opena5 (VS Code) pollt `/tasks/poll`

- Erhält EDIT_TASK
- Öffnet `src/models/user.py` im Workspace
- Entwickler bearbeitet, speichert

**Schritt 3:** opena5 sendet `/tasks/apply`

```json
{
  "request_id": "11111111-1111-4111-8111-111111111111",
  "file_path": "src/models/user.py",
  "action": "apply",
  "timestamp": "2025-11-09T12:00:01Z"
}
```

↓ wird in `archivp/2025/11/09/SP1731156001_opena5→opena2_CMD.json` (Safepoint CMD) gespeichert

**Schritt 4:** opena2 (Archivator) verarbeitet, antwortet

```json
{
  "request_id": "11111111-1111-4111-8111-111111111111",
  "status": "ok",
  "message": "File persisted in archiv"
}
```

↓ wird in `archivp/2025/11/09/SP1731156001_opena2→opena5_RESP.json` (Safepoint RESP) gespeichert

**Schritt 5:** opena5 zeigt Status an VS Code, opena3 wird über Update benachrichtigt

---

## 8) Referenzen & Links

- **Schritt 1:** opena1 Koordinator & 7.1-Validierung
- **Schritt 2:** Tool-Registry & Mapping
- **Schritt 3:** Safepoint-Format & Audit-Trail
- **Schritt 4:** opena4 Telegram-Bridge
- **Schritt 6:** opena2 Archivator Deep Dive
- **Schritt 7:** opena3 UI & Routing

---

**Status:** 🔧 In Spezifikation · Ready für Implementierung
**Nächste Phase:** Implementierung opena5 Core mit Pydantic Schemas & API-Endpoints
