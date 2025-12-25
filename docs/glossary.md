[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]

# Glossar – Phase 4 Terminology

**ELION Hyper-Dashboard Copilot Bridge Project**

---

## Core Concepts

### PDI (Project Documentation Intelligence)

**Definition:** Meta-Governance-Framework, das textuelle Projektideen deterministisch in produktionsreife Artefakte überführt.

**Anwendung:**

- Manifest (Ziele, Constraints, DoD)
- Kapitelplan (20 Positionen, sequenziert)
- Validierung (Struktur, Konsistenz, Audit)
- Automatisierte Checks (Lint, Build, GitHub/Copilot)

**Beispiel:** PDI-Header: `[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]`

---

### Safepoint

**Definition:** Unveränderliche JSON-Protokolldatei im Archiv (`archivp/YYYY/MM/DD/`), die den Status einer Operation dokumentiert.

**Struktur:**

```json
{
  "timestamp": "2025-11-07T10:30:00Z",
  "task_id": "task_12345",
  "operation": "prompt_execution",
  "status": "SUCCESS|ERROR|PENDING",
  "source": "bridge|extension|dashboard",
  "payload": {...},
  "metadata": {
    "duration_ms": 1250,
    "prompt_hash": "sha256_...",
    "model": "opena3",
    "workspace": "/home/.../project"
  }
}
```

**Verwendung:**

- Audit Trail für alle Operationen
- Debugging und Retrospektive
- Compliance + Security
- Determinismus-Validierung

---

### Bridge (Copilot Bridge Service)

**Definition:** FastAPI-Queue-Service (Port 12351), der Prompts entgegennimmt, diese an opena3 weiterleitet und Results zur VS Code Extension zurückstreamt.

**Verantwortlichkeiten:**

- Task-Queueing (`POST /api/enqueue`)
- Task-Status (`GET /api/tasks`)
- Result-Streaming (SSE/WebSocket)
- Auto-Persistence zu archivp/
- Error-Handling + Circuit-Breaker

**Integration:**

```
VS Code Extension
  ↓ HTTP POST /api/enqueue
Bridge (12351)
  ↓ Dequeue + call opena3
opena3 (12347)
  ↓ Stream response chunks
Bridge → Extension (SSE)
  ↓ Write result + Safepoint
archivp/ + local file
```

---

### Extension (VS Code Extension)

**Definition:** TypeScript-basierte VS Code-Erweiterung (`portier-bridge`), die mit Bridge kommuniziert und Dateien schreibt.

**Features:**

- Command: "ELION: Enqueue Task"
- Sidebar Queue-Monitor
- Retry with exponential backoff
- Conflict resolution UI (3-Way Merge)
- Multi-Root Workspace support

**Package:** `vscode-extension-tester` + Extension API

---

### Determinismus

**Definition:** Garantie, dass **gleiche Eingaben → gleiche Ausgaben** erzeugen.

**Implementierung:**

- Seed-Header in Prompts
- Normalisierte Pfade + Encoding
- Versionierter Model-State
- Output-Hash-Validierung
- Deterministische Prompts (Pos. 13)

**Prüfung:**

```bash
# Gleicher Prompt 2x ausführen → gleicher Hash
hash1=$(prompt_to_file "Summarize X" | sha256sum)
hash2=$(prompt_to_file "Summarize X" | sha256sum)
assert hash1 == hash2
```

---

### RBAC (Role-Based Access Control)

**Definition:** Zugriffsmodell basierend auf Rollen (reader, writer, admin).

**Rollen:**

- **reader:** GET `/api/bridge/*`, `GET /api/metrics`
- **writer:** reader + POST `/api/enqueue`, PUT `/api/tasks/{id}`
- **admin:** writer + DELETE, systemctl commands, audit logs

**Implementation:** JWT Token + Role Claim in Payload

---

### Queue (Task Queue)

**Definition:** FIFO/Priority-basierte Warteschlange für Prompts.

**Struktur:**

```json
{
  "task_id": "task_123",
  "prompt": "Summarize this...",
  "file_path": "/workspace/src/main.py",
  "mode": "append|overwrite|merge",
  "priority": 1,
  "created_at": "2025-11-07T10:00:00Z",
  "status": "queued|processing|completed|error",
  "result": {...}
}
```

**Policies:**

- Max queue size: 1000 tasks
- Task timeout: 300s
- Retry count: 5 (with backoff)
- Dead-Letter-Queue (DLQ): für Fehler

---

### DLQ (Dead-Letter-Queue)

**Definition:** Spezielle Queue für Tasks, die nach allen Retry-Versuchen fehlschlagen.

**Verwendung:**

- Forensics (Fehleranalyse)
- Manual Intervention Queue
- Error Dashboard Widget
- Safepoints mit Status = "ERROR"

---

### Circuit Breaker

**Definition:** Pattern zur Fehlerbehandlung: CLOSED (ok) → OPEN (fail) → HALF_OPEN (retry) → CLOSED (recover).

**Anwendung (Pos. 12):**

- OpenWebUI nicht erreichbar → OPEN
- Nach 60s: HALF_OPEN (test request)
- Success → CLOSED; Fail → OPEN (erneut 60s)

---

### 3-Way Merge

**Definition:** Konflikt-Auflösungs-Algorithmus, der base, local, remote vergleicht.

**Algorithmik:**

```
base: "hello world"
local: "hello there world"
remote: "hello beautiful world"

→ Conflict marker:
<<<<<<< LOCAL
hello there world
||||||| BASE
hello world
=======
hello beautiful world
>>>>>>> REMOTE
```

**Implementation:** LCS (Longest Common Subsequence) oder Diff3

---

### Pfad-Sandboxing

**Definition:** Sicherheitsmechanismus, der verhindert, dass Tasks außerhalb eines erlaubten Verzeichnisses Dateien schreiben/lesen.

**Enforcement:**

```python
BASE_DIR = "/workspace"
DENY_PATTERNS = [".git", "node_modules", "__pycache__"]

def validate_path(file_path):
    # 1. Normalize (resolve symlinks)
    real_path = Path(file_path).resolve()
    # 2. Check base_dir
    if not str(real_path).startswith(BASE_DIR):
        raise SecurityError("Path outside sandbox")
    # 3. Check deny-list
    if any(p in str(real_path) for p in DENY_PATTERNS):
        raise SecurityError("Denied path")
    return real_path
```

---

### Rate-Limit (Token Bucket)

**Definition:** Mechanismus zur Begrenzung von Anfragen pro Token (60 req/min).

**Implementation:**

```python
bucket = {token: 60}  # requests available
refill_rate = 1 / sec  # 1 request per second

def is_allowed(token):
    if bucket[token] > 0:
        bucket[token] -= 1
        return True
    return False  # → 429 Too Many Requests
```

---

### OpenAPI Schema

**Definition:** Maschinenlesbare API-Spezifikation (OpenAPI 3.1) für Bridge API.

**Generierung:**

```bash
# FastAPI auto-generiert bei /openapi.json
curl http://127.0.0.1:12351/openapi.json | jq . > bridge_schema.json
```

**Verwendung:**

- API-Dokumentation (Swagger UI)
- Client-Code-Generator (openapi-generator)
- Contract Testing

---

### Telemetry

**Definition:** Metrics + KPIs über Tasks, Fehler, Performance.

**KPIs:**

- Total tasks queued, completed, errored
- Avg response time (ms)
- Error rate (%)
- Queue depth (live)
- Uptime (%)

**Export:** JSONL + Prometheus metrics

---

### Multi-Root Workspace

**Definition:** VS Code-Feature, dass mehrere Ordner in einem Workspace verwalten kann.

**Relevanz (Pos. 17):**

- Task kann Ziel-Workspace spezifizieren
- Result geschrieben in korrektem Root
- Extension zeigt Workspace-Context

---

### CLI (Command-Line Interface)

**Definition:** `bridgectl` — Python-Click-Tool zur Bridge-Verwaltung vom Terminal.

**Commands:**

- `bridgectl list` – Zeige Queued Tasks
- `bridgectl enqueue --file test.txt --prompt "summarize"` – Neue Task
- `bridgectl drain` – Leere Queue
- `bridgectl retry --task-id 123` – Retry failed task
- `bridgectl status` – Health + Metrics

---

### Systemd Units

**Definition:** Linux-Service-Definitionen für opena3, adapter, bridge, dashboard.

**Dateiformat:**

```ini
[Unit]
Description=ELION Bridge Service
After=network-online.target

[Service]
Type=simple
User=danijel-jd
ExecStart=/home/.../venv313/bin/python -m copilot_bridge
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

---

### Docker Compose

**Definition:** YAML-Definitionen für vollständige Service-Stack (dashboard, opena3, adapter, bridge, openwebui).

**Services:**

- dashboard (12349)
- opena3 (12347)
- adapter (12350)
- bridge (12351)
- openwebui (8080)

**Netzwerk:** `elion-network` (bridge)

---

### E2E Test (End-to-End)

**Definition:** Integrationtest, der komplette Flow validiert: Chat → Bridge → Extension → Datei.

**Sequenz:**

1. Start services
2. Create task via dashboard
3. Bridge picks up + calls opena3
4. Extension stub processes
5. File written
6. Safepoint created
7. Assert all OK

---

### DoD (Definition of Done)

**Definition:** Klare Akzeptanzkriterien für jede Position.

**Allgemein:**

- Lint clean (Python, Bash, TS)
- Tests passing (>80% coverage)
- ≥1 Safepoint geschrieben
- Documentation updated
- GitHub CI green
- No TODOs/Platzhalter

---

### Manifest

**Definition:** Master-Dokument mit Mission, Constraints, DoD, Risiken, Governance.

**Versionen:**

- v0.1: Initial (user input)
- v1.0: Nach Pos. 01–05 Complete (validiert)
- v2.0: Nach komplette Phase 4 (released)

---

### Kapitelplan

**Definition:** Sequenzierter Roadmap mit 20 ausführbaren Positionen.

**Struktur pro Position:**

- Ziel
- Scope
- Dependencies
- Akzeptanzkriterien (DoD)
- Deliverables
- Schätzung

---

### Validation Framework

**Definition:** Governance-Checks für Struktur, Konsistenz, Audit.

**Checks:**

- Structure: Directory tree + file manifest OK
- Consistency: Ports, Tokens, Error format consistent
- Audit: All operations logged + Safepoints created
- GitHub: Lint + Build + Tests green

---

## Abkürzungen

| Abk.     | Bedeutung                          |
| -------- | ---------------------------------- |
| **PDI**  | Project Documentation Intelligence |
| **DoD**  | Definition of Done                 |
| **RBAC** | Role-Based Access Control          |
| **DLQ**  | Dead-Letter-Queue                  |
| **SSE**  | Server-Sent Events                 |
| **E2E**  | End-to-End                         |
| **CLI**  | Command-Line Interface             |
| **YAML** | YAML Ain't Markup Language         |
| **JWT**  | JSON Web Token                     |
| **LCS**  | Longest Common Subsequence         |
| **KPI**  | Key Performance Indicator          |
| **CORS** | Cross-Origin Resource Sharing      |

---

## Semantische Relationen

```
PDI
├── Manifest (Governance)
├── Kapitelplan (20 Positionen)
├── Glossar (Terminology) ← this file
├── Validation Framework
│   ├── Structure Check
│   ├── Consistency Report
│   └── Audit Trail (Safepoints)
└── Operationalisierung (Code + Tests + Docs)
    ├── Bridge (Queue Service)
    ├── Extension (VS Code)
    ├── CLI (bridgectl)
    ├── Deployment (Systemd + Compose)
    └── Release (v1.0)
```

---

**[PDI-FOOTER: Glossar complete. Alle Begriffe für Phase 4 definiert. Ready for Implementation.]**
