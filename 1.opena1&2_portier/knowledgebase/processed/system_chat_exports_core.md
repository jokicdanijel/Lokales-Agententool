# System-Chat-Exports - Processed Core Version

## 1. Inhalte

### Chat-Verlaeufe
- Vollstaendige Chat-Verlaeufe
- Chronologische Reihenfolge
- User-Prompts
- Assistant-Responses
- Tool-Invocations

### Systemvorgaben
- System-Prompts
- Policy-Definitionen
- Architektur-Vorgaben
- Konventionen
- Regeln

### Toolsignale
- Tool-Calls
- Tool-Responses
- Error-Messages
- Success-Confirmations
- State-Transitions

### Fehlererklärungen
- Error-Codes
- Stack-Traces
- Debug-Informationen
- Resolution-Steps
- Workarounds

### Build-Anweisungen
- Setup-Steps
- Deployment-Commands
- Configuration-Changes
- Dependency-Updates
- Migration-Scripts

## 2. Verwendung

### Debugging
- Error-Reproduktion
- State-Rekonstruktion
- Flow-Analyse
- Anomalie-Detektion
- Root-Cause-Analysis

### Training
- LLM-Fine-Tuning
- Pattern-Recognition
- Best-Practices-Extraction
- Anti-Pattern-Detection
- Quality-Benchmarking

### Validierung von Workflows
- Process-Verification
- Compliance-Checks
- Option-2-Flow-Validation
- Safepoint-Verification
- Port-Policy-Checks

### Konsistenzanalyse
- Naming-Consistency
- Schema-Consistency
- Architecture-Consistency
- Policy-Compliance
- Convention-Adherence

## 3. Struktur

### Chat-Historie
- Timestamps (ISO-8601 Zulu)
- Message-IDs (UUID v4)
- User-Role ("user"|"assistant"|"system")
- Content (Text + Code)
- Metadata (Tool-Calls, Attachments)

### System-Antworten
- Response-Type (Text|Code|Error)
- Tool-Results
- Execution-Status
- Validation-Results
- Feedback-Messages

### User-Prompts
- Natural-Language-Requests
- Code-Snippets
- File-Attachments
- Context-References
- Follow-Up-Questions

### Projektbefehle
- CLI-Commands
- Script-Executions
- File-Operations
- Service-Controls
- Configuration-Changes

## 4. Schutzregeln

### Keine sensiblen Schluessel
- Keine API-Keys
- Keine OPENAI_API_KEY
- Keine BEARER_TOKEN
- Keine Credentials
- Nur Platzhalter (sk-..., $BEARER_TOKEN)

### Keine Passwoerter
- Keine DB-Passwoerter
- Keine SSH-Keys
- Keine Private-Keys
- Keine Tokens
- Nur Referenzen (.env, ENV-Vars)

### Archivierung nur unter archivp
- Format: archivp/YYYY/MM/DD/chat_export_<timestamp>.json
- Append-Only
- Index in index.jsonl
- Verschluesselung optional
- Zugriffskontrolle via Permissions

## 5. Export-Format

### JSON-Schema
```json
{
  "export_id": "uuid-v4",
  "timestamp": "2025-11-21T12:00:00Z",
  "session_id": "uuid-v4",
  "messages": [
    {
      "id": "uuid-v4",
      "timestamp": "2025-11-21T12:00:01Z",
      "role": "user|assistant|system",
      "content": "...",
      "tool_calls": [],
      "attachments": []
    }
  ],
  "metadata": {
    "total_messages": 100,
    "duration_seconds": 3600,
    "agents_involved": ["opena1", "opena2"],
    "tools_used": ["tool_file_searcher"]
  },
  "strict": true
}
```

### Felder
- export_id (UUID v4)
- timestamp (ISO-8601 Zulu)
- session_id (Session-Identifier)
- messages[] (Array von Message-Objekten)
- metadata (Session-Metadata)

## 6. Privacy & Security

### Redaction
- Automatische Key-Redaction
- Password-Masking
- Token-Replacement
- PII-Removal (optional)

### Encryption
- Optional AES-256 Encryption
- Key-Management via .env
- Encrypted-at-Rest
- Decryption nur auf Anfrage

### Access-Control
- File-Permissions 600
- Owner-Only Read/Write
- Group/Other keine Permissions
- Audit-Log fuer Zugriffe

## 7. Retention-Policy

### Speicherdauer
- 90 Tage Standard
- 1 Jahr fuer wichtige Sessions
- Unbegrenzt fuer Training-Data
- Automatische Cleanup-Scripts

### Cleanup
```bash
find archivp/ -name "chat_export_*.json" -mtime +90 -delete
```

## 8. Use-Cases

### Error-Analysis
1. Export problematischen Chat
2. Analysiere Tool-Calls
3. Identifiziere Error-Point
4. Extrahiere Stack-Trace
5. Reproduziere Fehler
6. Implementiere Fix

### Training-Data-Preparation
1. Exportiere erfolgreiche Chats
2. Redact sensitive Data
3. Extract Tool-Usage-Patterns
4. Create Fine-Tuning-Dataset
5. Validate Quality
6. Upload to Training-Pipeline

### Compliance-Audit
1. Export alle Chats (Zeitraum)
2. Validiere Option-2-Flow
3. Pruefe Port-Policy-Compliance
4. Checke Safepoint-Vollstaendigkeit
5. Generiere Audit-Report
6. Archiviere Report

## 9. Integration

### Mit Archivator
- Exports als Safepoints
- CMD: EXPORT_CHAT
- RESP: EXPORT_COMPLETE
- Index-Update automatisch

### Mit Dashboard
- Export-Button im UI
- Download als JSON
- Redacted-Preview
- Export-History-View

### Mit Knowledge-Base
- Processed Chats als Training-Data
- Semantic-Search ueber Chats
- Pattern-Extraction
- Best-Practice-Mining
