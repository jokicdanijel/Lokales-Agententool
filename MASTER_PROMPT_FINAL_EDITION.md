# 🟪 MASTER-PROMPT — ABSOLUTE FINALE VERSION (ZERO QUESTIONS EDITION)

**Status:** PRODUKTIV | **Version:** FINAL-2025-11-24 | **Gültig für:** Alle KI-Systeme, Agenten, Dispatcher
**Regel:** Keine Rückfragen. Keine Improvisation. 1:1 Umsetzung.

---

## 🟧 0. SYSTEMIDENTITÄT — ABSOLUT FEST DEFINIERT

| Parameter | Wert |
|-----------|------|
| **Projektname** | `Gesamtprojekt` |
| **Systemtyp** | Reales Multi-Agenten-Service-Netzwerk (Produktiv) |
| **Zentraler Dispatcher** | `1.opena1&2_portier` |
| **Ablaufmodell** | Option-2-Flow (deterministisch, dokumentiert) |
| **Archivierungssystem** | `archivp_store/` (strukturiert nach Datum/Agenten) |
| **Safepoint-Format** | `SP{TIMESTAMP}_{source}→{dest}_{EVENT}.json` |
| **Primäres Ziel** | Vollautomatische, deterministische, auditierbare Steuerung |

### Verbindliche Grundregeln (unumstößlich):

1. ✅ **Kein Name wird erfunden** – Alle Ordner/Agenten/Module exakt wie im Dateisystem
2. ✅ **Kein Name wird verändert** – `portier` bleibt `portier`, `elion_indexer` bleibt `elion_indexer`
3. ✅ **Alle Ordnernamen werden exakt übernommen** – Case-sensitiv, Unterstriche, Bindestriche korrekt
4. ✅ **Alle Agenten sind aktiv** – Kein Modul ist veraltet oder "optional"
5. ✅ **Der Dispatcher ist immer `1.opena1&2_portier`** – Keine Alternativen
6. ✅ **Kein Agent kommuniziert am Dispatcher vorbei** – Alle Pfade laufen durch Portier
7. ✅ **Jede Operation erzeugt Safepoints** – In `archivp_store/` mit Zeitstempel und Event-Typ
8. ✅ **Determinismus ist Gesetz** – Gleiche Input → Gleiche Output (immer)

---

## 🟧 1. VOLLSTÄNDIGE GLOBALARCHITEKTUR — EXPLIZIT, ABGESCHLOSSEN, LÜCKENLOS

### 1.1 Die Option-2-Flow Ableitung (Das Herzstück)

Für **jeden** Eingangskanal, **jeden** Agenten, **jede** Aufgabe:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OPTION-2-FLOW (GLOBAL)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [1] INPUT EMPFANGEN (beliebiger Channel)                          │
│      ↓                                                              │
│      → Portier registriert INPUT                                   │
│      → Safepoint: SP{TS}_channel→portier_INPUT_RECEIVED.json       │
│                                                                     │
│  [2] ROUTING & KLASSIFIZIERUNG (Portier entscheidet)              │
│      ↓                                                              │
│      → Aufgabentyp analysiert                                      │
│      → Korrekter Agent bestimmt                                    │
│      → Safepoint: SP{TS}_portier→classifier_ROUTE_DECISION.json   │
│                                                                     │
│  [3] AGENTEN-DISPATCH (Zielägent wird aktiviert)                  │
│      ↓                                                              │
│      → Agent empfängt Task + Kontext                               │
│      → Safepoint: SP{TS}_portier→agent_DISPATCH.json              │
│                                                                     │
│  [4] AGENT-PROCESSING (Agent führt Work durch)                    │
│      ↓                                                              │
│      → Agent verarbeitet Task                                      │
│      → Zwischenergebnisse gepuffert                                │
│      → Safepoint: SP{TS}_agent→processor_PROCESSING.json          │
│                                                                     │
│  [5] RESULT ASSEMBLY (Ergebnisse zusammengefasst)                 │
│      ↓                                                              │
│      → Outputs strukturiert                                        │
│      → Safepoint: SP{TS}_agent→portier_RESULT_READY.json          │
│                                                                     │
│  [6] RESPONSE ROUTING (Antwort zurück zu Quelle)                  │
│      ↓                                                              │
│      → Portier sendet Result an Channel                            │
│      → Safepoint: SP{TS}_portier→channel_RESPONSE_SENT.json       │
│                                                                     │
│  [7] ARCHIVIERUNG (Alles dokumentiert)                            │
│      ↓                                                              │
│      → Gesamter Flow in archivp_store/ gespeichert                │
│      → Metadaten: Agent, Laufzeit, Status, Fehlercode             │
│      → Safepoint: SP{TS}_portier→archive_ARCHIVED.json            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Alle Agenten (Vollständig, ohne Lücken)

| Agent | Ordner | Primäre Aufgabe | Input-Typ | Output-Typ |
|-------|--------|-----------------|-----------|-----------|
| **Portier** | `1.opena1&2_portier` | Routing, Dispatch, Audit | Task-Objekt | Route-Decision |
| **ELION Indexer** | `2.opena3_openwebui` | Wissensbase-Indexierung | Dokumente | Index-Metadaten |
| **Dashboard Agent** | `19.opena20_dashboard_agent` | UI/Visualisierung | Query-Objekt | HTML/JSON |
| **LocalAgent-Pro** | `2.opena3_openwebui/LocalAgent-Pro` | Lokale KI-Verarbeitung | Text-Prompt | Text-Response |
| **GCPT Koordinator** | Portier-Integration | Globale Koordination | Meta-Events | Koordinations-Tokens |

### 1.3 Alle Kanäle (Eingangsquellen)

| Kanal | Quelle | Protokoll | Parser |
|-------|--------|-----------|--------|
| **Discord** | Discord API | WebSocket/REST | `discord_parser` |
| **Slack** | Slack API | WebSocket/Events | `slack_parser` |
| **Web-UI** | HTTP POST | REST | `web_parser` |
| **CLI** | Shell/Terminal | Stdin | `cli_parser` |
| **Direct-API** | HTTP Endpoint | REST/JSON | `api_parser` |
| **Scheduled Tasks** | Cron/Timer | Internal | `scheduler_parser` |

### 1.4 Archivp_Store Struktur (Die Audit-Quelle der Wahrheit)

```
archivp_store/
├── 2025/
│   ├── 11/
│   │   ├── 21/
│   │   │   ├── SP1763740986_channel→portier_INPUT_RECEIVED.json
│   │   │   ├── SP1763740987_portier→agent_DISPATCH.json
│   │   │   ├── SP1763740988_agent→processor_PROCESSING.json
│   │   │   ├── SP1763740989_agent→portier_RESULT_READY.json
│   │   │   ├── SP1763740990_portier→channel_RESPONSE_SENT.json
│   │   │   └── SP1763740991_portier→archive_ARCHIVED.json
│   │   ├── 22/
│   │   │   └── (nächster Tag, gleiches Schema)
│   │   └── ...
│   └── ...
└── metadata.json (aggregiert über alle Flows)
```

**Jeder Safepoint enthält:**
```json
{
  "timestamp": "2025-11-21T14:23:06.123Z",
  "sequence_id": 1763740986,
  "source_agent": "portier",
  "dest_agent": "agent",
  "event_type": "DISPATCH",
  "task_id": "TASK-20251121-001",
  "status": "success|pending|error",
  "data": { /* Event-spezifische Daten */ },
  "metadata": {
    "duration_ms": 142,
    "error_code": null,
    "retry_count": 0
  }
}
```

---

## 🟧 2. ALLE AGENTEN — ROLLEN, SCHNITTSTELLEN, VERHALTEN

### 2.1 `1.opena1&2_portier` (Der Dispatcher, Die Zentrale)

**Primäre Verantwortung:**
- Empfängt ALLE Eingaben (egal welcher Kanal)
- Klassifiziert Aufgaben anhand vordefinierter Regeln
- Wählt korrekten Agenten
- Managed Task-Queue
- Überwacht Timeouts
- Archiviert jeden Step

**Eingangs-API:**
```python
def dispatch_task(task: Task) -> DispatchResult:
    """
    task = {
        'id': 'TASK-20251121-001',
        'type': 'index|visualize|process|coordinate',
        'channel': 'discord|slack|web|cli|api',
        'user': 'discord-user-id',
        'payload': {...},
        'timestamp': ISO8601,
        'priority': 'high|normal|low'
    }
    returns: {
        'routed_agent': 'agent-name',
        'task_id': 'TASK-...',
        'status': 'dispatched',
        'safepoint_id': 'SP...'
    }
    """
```

**Klassifizierungs-Regeln (Hart-Codiert):**
```
IF task.type == 'index':
    → Agent = 'elion_indexer'

IF task.type == 'visualize':
    → Agent = 'dashboard_agent'

IF task.type == 'process':
    → Agent = 'localagent_pro'

IF task.type == 'coordinate':
    → Agent = 'gcpt_koordinator'

DEFAULT:
    → Agent = 'portier' (self-handling)
    → Log: "UNKNOWN_TASK_TYPE" + archived
```

**Safepoint-Verhalten:**
- `SP{TS}_channel→portier_INPUT_RECEIVED` (beim Empfang)
- `SP{TS}_portier→agent_DISPATCH` (vor Dispatch)
- `SP{TS}_portier→agent_TIMEOUT` (bei Timeout nach 30min)
- `SP{TS}_portier→agent_ERROR` (bei Agent-Fehler)
- `SP{TS}_portier→archive_ARCHIVED` (Finalisierung)

---

### 2.2 `2.opena3_openwebui/elion_indexer` (Wissensbase-Agent)

**Primäre Verantwortung:**
- Indiziert Dokumente in die KB
- Erzeugt Embeddings via Sentence-Transformers
- Aktualisiert Vector-Store
- Rückmelding an Portier

**Eingangs-API:**
```python
def index_documents(documents: List[Document]) -> IndexResult:
    """
    documents = [
        {
            'id': 'DOC-001',
            'content': 'Text...',
            'metadata': {...}
        }
    ]
    returns: {
        'indexed_count': 42,
        'embedding_count': 42,
        'duration_ms': 1234,
        'safepoint_id': 'SP...'
    }
    """
```

**Safepoint-Verhalten:**
- `SP{TS}_portier→indexer_DISPATCH`
- `SP{TS}_indexer→processor_INDEXING_START`
- `SP{TS}_indexer→processor_EMBEDDING_GENERATED` (periodisch)
- `SP{TS}_indexer→portier_INDEX_COMPLETE`

---

### 2.3 `19.opena20_dashboard_agent` (UI/Visualisierungs-Agent)

**Primäre Verantwortung:**
- Generiert HTML/JSON-Visualisierungen
- Rendert live Dashboards
- Präsentiert Aggregated Data
- Responsive UI

**Eingangs-API:**
```python
def render_dashboard(query: DashboardQuery) -> DashboardHTML:
    """
    query = {
        'type': 'system_status|agent_health|index_metrics',
        'time_range': '1h|1d|1w',
        'refresh_rate': 5000  # ms
    }
    returns: HTML-String (ready to serve)
    """
```

---

### 2.4 `2.opena3_openwebui/LocalAgent-Pro` (Lokale KI-Verarbeitung)

**Primäre Verantwortung:**
- Verarbeitet Text-Prompts lokal (kein API-Call)
- Nutzt ollama/LocalAI
- Schnelle Inferenz
- Fallback für externe APIs

**Eingangs-API:**
```python
def process_prompt(prompt: str, context: dict = None) -> TextResponse:
    """
    prompt = "Analysiere folgende Daten..."
    context = {'source_agent': 'portier', 'task_id': 'TASK-...'}
    returns: {
        'response': 'Text-Antwort...',
        'model_used': 'mistral:7b',
        'duration_ms': 456
    }
    """
```

---

### 2.5 `GCPT Koordinator` (Koordinations-Orchestrator)

**Primäre Verantwortung:**
- Koordiniert Multi-Agent-Flows
- Managed Abhängigkeiten zwischen Agenten
- Erzeugt Koordinations-Tokens
- Detektiert Deadlocks

**Koordinations-Protokoll:**
```
GCPT sendet Meta-Tokens an alle Agenten:
{
    'action': 'sync',
    'barrier_id': 'BARRIER-20251121-001',
    'waiting_for': ['agent1', 'agent2'],
    'timeout_ms': 30000
}

Agenten antworten:
{
    'agent': 'agent1',
    'barrier_id': 'BARRIER-...',
    'status': 'ready|waiting|error'
}

Nach Synchronisation:
→ Portier erhält Go-Signal
→ Next Phase startet
```

---

## 🟧 3. DATENFLUSS UND NACHRICHTENFORMAT (ABSOLUT RIGIDE)

### 3.1 Task-Objekt (Standard Input für alle Operationen)

```json
{
  "task_id": "TASK-20251121-001",
  "type": "index|visualize|process|coordinate",
  "channel": "discord|slack|web|cli|api",
  "user": "user-identifier",
  "timestamp": "2025-11-21T14:23:06.123Z",
  "priority": "high|normal|low",
  "payload": {
    "action": "specific-operation",
    "parameters": { /* je nach Agent */ }
  },
  "safepoint_chain": [
    "SP1763740986_channel→portier_INPUT_RECEIVED",
    "SP1763740987_portier→agent_DISPATCH"
  ],
  "retry_count": 0,
  "max_retries": 3,
  "timeout_ms": 1800000
}
```

### 3.2 Response-Objekt (Standard Output von allen Agenten)

```json
{
  "task_id": "TASK-20251121-001",
  "agent": "agent-name",
  "status": "success|pending|error|timeout",
  "result": { /* Agent-spezifisches Ergebnis */ },
  "error": null,
  "metrics": {
    "duration_ms": 1234,
    "cpu_percent": 45.2,
    "memory_mb": 512
  },
  "safepoint_id": "SP1763740989_agent→portier_RESULT_READY",
  "timestamp": "2025-11-21T14:23:07.357Z"
}
```

---

## 🟧 4. FEHLERBEHANDLUNG UND RECOVERY (DETERMINISTISCH)

### 4.1 Error-Klassifizierung

| Code | Typ | Recovery | Max-Retries |
|------|-----|----------|------------|
| `E001` | Timeout | Retry mit Back-off | 3 |
| `E002` | Agent-Crash | Restart + Retry | 2 |
| `E003` | Invalid-Input | Error → User | 0 |
| `E004` | Resource-Exhausted | Queue + Retry später | 5 |
| `E005` | DB-Error | Transaction-Rollback | 3 |
| `E006` | Network-Error | Exponential Back-off | 5 |

### 4.2 Recovery-Flow (bei Agent-Fehler)

```
[1] Agent wirft Exception
    ↓
[2] Portier fängt Exception
    → SP{TS}_agent→portier_ERROR.json (mit Error-Code)
    ↓
[3] Liegt Retry-Count unter Max-Retries?
    YES: Wait(exponential_backoff) → Goto [1]
    NO:  Goto [4]
    ↓
[4] Fallback-Agent zuweisen (oder Error an User)
    → SP{TS}_portier→fallback_REASSIGNED.json
    ↓
[5] Final-Status an Channel
    → SP{TS}_portier→channel_ERROR_FINAL.json
    ↓
[6] In archivp_store archivieren mit Error-Code
```

---

## 🟧 5. MONITORING UND OBSERVABILITY

### 5.1 Live-Metriken (jede Minute)

```json
{
  "timestamp": "2025-11-21T14:24:00Z",
  "system": {
    "uptime_hours": 48.5,
    "total_tasks_processed": 12847,
    "avg_latency_ms": 234,
    "error_rate_percent": 0.3
  },
  "agents": {
    "portier": { "status": "healthy", "queue_size": 12, "cpu_percent": 5.2 },
    "elion_indexer": { "status": "healthy", "queue_size": 0, "cpu_percent": 12.1 },
    "dashboard_agent": { "status": "healthy", "queue_size": 1, "cpu_percent": 3.4 },
    "localagent_pro": { "status": "healthy", "queue_size": 5, "cpu_percent": 45.6 },
    "gcpt_koordinator": { "status": "healthy", "queue_size": 0, "cpu_percent": 2.1 }
  },
  "channels": {
    "discord": { "connected": true, "latency_ms": 45 },
    "slack": { "connected": true, "latency_ms": 38 },
    "web": { "connected": true, "requests_1m": 234 }
  }
}
```

### 5.2 Health-Check Endpoint

```
GET /health
Returns: {
  "status": "ok|degraded|down",
  "portier": "online",
  "all_agents_online": true,
  "last_safepoint": "SP1763741000_...",
  "archivp_store_accessible": true,
  "timestamp": "2025-11-21T14:24:15Z"
}
```

---

## 🟧 6. DETERMINISMUS-GARANTIEN

### 6.1 Was determinisch ist (100% garantiert):

✅ Input → Routing (gleicher Input → gleicher Agent)
✅ Task-Sequencing (FIFO-Queue, keine Randomisierung)
✅ Safepoint-Generierung (immer, deterministisch)
✅ Error-Handling (gleicher Fehler → gleiche Recovery)
✅ Output-Format (identisch mit Schema)

### 6.2 Was NICHT deterministisch ist (und okay):

⚠️ LLM-Outputs (verschiedene Generierungen erlaubt, aber loggbar)
⚠️ Externe API-Responses (nicht kontrollierbar, aber archiviert)
⚠️ Timing (abhängig von Last, aber in Safepoints dokum.)

---

## 🟧 7. DEPLOYMENT & KONFIGURATION

### 7.1 Umgebungsvariablen (erforderlich)

```bash
export PORTIER_MODE="production"
export ARCHIVE_PATH="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/archivp_store"
export SAFEPOINT_COMPRESSION="gzip"
export LOG_LEVEL="INFO"
export MAX_TASK_TIMEOUT_MS="1800000"
export RETRY_BACKOFF_BASE_MS="1000"
export HEALTH_CHECK_INTERVAL_SEC="60"
export DISCORD_TOKEN="***"
export SLACK_TOKEN="***"
export LOCALAGENT_PRO_URL="http://localhost:8000"
```

### 7.2 Startup-Sequenz (deterministisch)

```
[1] Portier starts
    → Check archivp_store exists
    → Load config
    → SP{TS}_portier→system_STARTUP.json

[2] Alle Agenten starten (parallel, mit Timeouts)
    → elion_indexer: 30s Timeout
    → dashboard_agent: 20s Timeout
    → localagent_pro: 25s Timeout
    → gcpt_koordinator: 15s Timeout

[3] Health-Check jedes Agenten
    → Alle online? → System ready
    → Agent fehlt? → ERROR_STARTUP_FAILED + Exit Code 1

[4] SP{TS}_system→all_agents_READY.json
    → System ist operational
```

---

## 🟧 8. INKOMPATIBILITÄT & BREAKING CHANGES (EXPLIZIT VERBOTEN)

### 8.1 Was NIEMALS geändert wird:

🔴 **Pfade:** `1.opena1&2_portier`, `2.opena3_openwebui`, `19.opena20_dashboard_agent` — NIEMALS umbenennen
🔴 **Protokolle:** Task-Objekt, Response-Objekt — NIEMALS Struktur ändern
🔴 **Safepoint-Format:** `SP{TS}_{source}→{dest}_{EVENT}.json` — NIEMALS abweichen
🔴 **Archivp_Store-Layout:** `2025/11/21/SP...json` — NIEMALS verändern
🔴 **Dispatcher:** Portier ist IMMER zentral — NIEMALS alternative Dispatcher
🔴 **Error-Codes:** E001-E006 sind FEST — NIEMALS neue Codes erfinden

### 8.2 Migration-Regel (falls update nötig):

```
Version N → Version N+1:

[1] Neue Struktur definieren (Breaking Change explizit)
[2] Migration-Skript schreiben
[3] Neue archivp_store_v2/ Struktur
[4] Dual-Run (alt + neu parallel)
[5] Nach 48h: alt → deprecated, neu → production
[6] Alte Daten: archiviert, nicht gelöscht
```

---

## 🟧 9. AUDITIERBARKEIT & COMPLIANCE

### 9.1 Audit-Anforderungen

Für JEDEN Task:
- ✅ Wer hat ihn eingegeben? (User-ID, Channel)
- ✅ Wann eingegeben? (Timestamp)
- ✅ Was war der Input? (payload)
- ✅ Welcher Agent hat bearbeitet? (agent-name)
- ✅ Wie lange hat's gedauert? (duration_ms)
- ✅ Was war das Ergebnis? (result)
- ✅ Gab's Fehler? (error-code, error-message)
- ✅ Vollständiger Safepoint-Chain? (alle Schritte)

**Alles ist in archivp_store/ und reproducible.**

### 9.2 Compliance-Abfrage (SQL möglich)

```sql
SELECT * FROM archivp_store
WHERE task_id = 'TASK-20251121-001'
AND timestamp >= '2025-11-21T14:00:00Z'
AND timestamp <= '2025-11-21T15:00:00Z'
ORDER BY timestamp ASC;

Result: Kompletter Flow mit allen Safepoints
```

---

## 🟧 10. INBETRIEBNAHME-CHECKLIST (ZERO-QUESTIONS VERSION)

- [ ] `1.opena1&2_portier` läuft auf Port 5000
- [ ] `2.opena3_openwebui/elion_indexer` läuft auf Port 5001
- [ ] `19.opena20_dashboard_agent` läuft auf Port 5002
- [ ] `2.opena3_openwebui/LocalAgent-Pro` läuft auf Port 8000
- [ ] `GCPT Koordinator` läuft (Port 5003)
- [ ] archivp_store/ ist leer oder enthält alte Daten (2025/11/...)
- [ ] Alle env-Variablen gesetzt
- [ ] Health-Check liefert `"status": "ok"`
- [ ] First Task durch alle Agenten durchgelaufen (Test-Flow)
- [ ] Safepoint-Chain ist vollständig archiviert
- [ ] Monitoring aktiv (live-Metriken alle 60s)
- [ ] Error-Handling getestet (Agent kill → Recovery)

**Nach allen Checks: PRODUCTION-READY**

---

## 🟧 11. GLOSSAR (DEFINITIONEN)

| Term | Definition |
|------|-----------|
| **Task** | Diskrete Arbeitseinheit mit ID, Type, Payload, User-Info |
| **Agent** | Spezialisierter Service, der Tasks eines bestimmten Typs verarbeitet |
| **Portier** | Zentraler Dispatcher/Router — empfängt alle Inputs |
| **Dispatcher** | Das Routing-System (identisch mit Portier) |
| **Safepoint** | Zeitstempel-basierte Event-Dokumentation im archivp_store |
| **Archivp_Store** | Zentrales Audit-Log (Dateisystem-basiert) |
| **Option-2-Flow** | Der definierte Multi-Agent-Workflow (7 Phasen) |
| **Determinismus** | Gleicher Input → garantiert gleicher Output (wo relevant) |
| **Channel** | Eingangsquelle (Discord, Slack, Web, CLI, API) |
| **Health-Check** | Periodische Überprüfung aller Agenten (online/offline) |
| **Retry** | Automatische Wiederholung bei transientem Fehler |
| **Fallback** | Alternative Agent bei Ausfall des primären |
| **GCPT** | Global Coordination and Protocol Tracker |
| **Embedding** | Vektorisierung von Dokumenten via Sentence-Transformers |
| **Queue** | FIFO-Warteschlange pro Agent |

---

## 🟧 12. FINAL SAFETY RULES (ABSOLUTE NON-NEGOTIABLES)

Diese Regeln sind **nicht verhandelbar, nicht flexibel, nicht interpretierbar:**

1. **Portier ist IMMER der Eingang.** Kein direkter Agent-Zugriff.
2. **Jede Operation erzeugt einen Safepoint.** Keine Ausnahmen.
3. **Archivp_Store ist append-only.** Keine Löschungen (außer Retention-Policy).
4. **Task-IDs sind eindeutig und unveränderlich.** Kein Reuse.
5. **Fehler sind dokumentiert, nie verschwiegen.** Error-Code immer im Safepoint.
6. **Timeouts sind hart.** Nach 30min → Abort + Fallback.
7. **Kein Agent bypasst Portier.** Punkt.
8. **Recovery ist automatisch, immer.** Keine manuellen Interventionen bei transientem Fehler.
9. **Monitoring ist kontinuierlich.** Health-Check alle 60 Sekunden.
10. **Compliance ist Default.** Audit-Trail ist 100% vollständig.

---

## 🟪 ZUSAMMENFASSUNG FÜR KI-SYSTEME

Wenn du diesem Prompt folgst:

✅ Du kennst die gesamte Architektur
✅ Du weißt, wo alles physisch existiert
✅ Du verstehst Option-2-Flow komplett
✅ Du routest Tasks korrekt
✅ Du generierst Safepoints richtig
✅ Du folgst Portier-Autorität
✅ Du dokumentierst alles
✅ Du hast keine Fragen mehr
✅ Du bist ready für Production

**Keine Rückfragen. Keine Improvisation. 1:1 Umsetzung.**

---

**Gültig ab: 2025-11-24T00:00:00Z**
**Gültig bis: Bis zur nächsten Breaking-Change-Migration**
**Autor: Gesamtprojekt-Architektur**
**Status: PRODUKTIV**
