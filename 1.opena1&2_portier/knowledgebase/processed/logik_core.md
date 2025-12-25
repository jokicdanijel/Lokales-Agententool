# LLM-Systemlogik - Processed Core Version

## 1. Basisprinzip

### Deterministische Verarbeitung

- Alle Eingaben durchlaufen gleichen Flow
- Keine Zufallselemente
- Reproduzierbare Ergebnisse
- Traceable Decision-Path

### Strikte Schema-Validierung

- JSON Schema Draft 2020-12
- additionalProperties: false
- Required-Fields enforced
- Type-Validation strict

### Kein Zustand ausserhalb archivp/ & Knowledge-Base

- Stateless Services
- Alle Persistenz in archivp/
- Knowledge-Base als Read-Only-State
- Keine In-Memory-State ohne Backup

### Jede Bewegung → Safepoint

- CMD-Safepoint beim Hinweg
- RESP-Safepoint beim Rueckweg
- Append-Only Logging
- Vollstaendiger Audit-Trail

## 2. Entscheidungslogik

### opena1 analysiert command + payload

```python
def analyze_request(request):
    command = request.get("command")
    payload = request.get("payload")
    target_preference = request.get("target_preference")

    # Validate
    validate_schema_71(request)

    # Decide
    selected_tool = decide_tool(command, target_preference)

    return selected_tool
```

### ermittelt target_preference

- Explizit via target_preference Field
- Implizit via command-Mapping
- Fallback via tool_registry Default
- Validation gegen Port-Policy

### validiert resolved_path

- Path-Validation gegen Filesystem
- Security-Check (Traversal)
- Existence-Check
- Permission-Check

### waehlt Tool gemaess Registry

- Lookup in config/registry.json
- Port-Availability-Check
- Health-Check vor Dispatch
- Fallback zu tool_default

## 3. Fehlerlogik

### Invalid Schema → sofortige RESP mit Fehler

```python
try:
    validate_schema_71(request)
except ValidationError as e:
    return {
        "error": {
            "code": "SCHEMA_VALIDATION_FAILED",
            "message": str(e),
            "details": e.errors()
        }
    }
```

### Ungueltige Ports → Blockade

```python
if port in FORBIDDEN_PORTS:
    raise Forbidden("Port verboten")
if port not in ALLOWED_PORTS:
    raise Forbidden("Port ausserhalb Bereich")
```

### Fehlende Pfade → Safe-FAIL mit Archivierung

- Error-Response generieren
- Safepoint trotzdem schreiben
- Error-Type in Safepoint
- Index aktualisieren

### Kein Tool → tool_default

```python
if selected_tool is None:
    selected_tool = "tool_default"
    reason = "No matching tool found, using default"
```

## 4. Rueckweg-Logik

### Jede Tool-Antwort → RESP

```
Tool → kordp → opena2 (RESP-Safepoint) → opena1 → OpenAI
```

### opena2 erstellt Safepoint

- Filename: SP<n>\_kordp→opena1_RESP.json
- Content: Full Response Envelope
- Index-Update: index.jsonl
- Timestamp: UTC

### opena2 → opena1

- Forward Response-Envelope
- Include Archival-Info
- Preserve Request-ID
- Add Archival-Status

### opena1 → OpenAI

- Build 7.2 Response
- Include Decision-Info
- Include Archival-Info
- strict: true

## 5. Policy Enforcement

### Strict:true

```python
class RequestSchema(BaseModel):
    class Config:
        extra = "forbid"
```

### JSON only

- Kein XML
- Kein YAML
- Kein Plain-Text
- Nur JSON (UTF-8)

### Keine zusaetzlichen Felder

- additionalProperties: false
- Validation rejects unknown fields
- Error bei Extra-Fields
- Strict Mode enforced

### Konsistenter Unicode-Pfeil

- → (U+2192) in allen Safepoint-Namen
- Keine ASCII-Alternativen
- Validation bei Safepoint-Creation
- Error bei falschem Pfeil

## 6. Decision-Tree

### Command-Routing

```
command == "ANALYZE" → tool_text_analyzer
command == "SEARCH"  → tool_file_searcher
command == "SCHEDULE"→ tool_scheduler
command == "MONITOR" → tool_monitor
else                 → target_preference oder tool_default
```

### Target-Preference

```
if target_preference:
    if tool_exists(target_preference):
        return target_preference
    else:
        log_warning("Target not found")
        return tool_default
```

### Fallback-Chain

```
1. Explicit target_preference
2. Command-Mapping
3. tool_default
```

## 7. State-Management

### Stateless-Principle

- Keine Session-State
- Keine User-State
- Keine Tool-State
- Nur Request-State (via Safepoint)

### Persistence

- Alle State in archivp/
- JSON-Format
- Append-Only
- Indexed

### Recovery

- Bei Restart: Load from archivp/
- Reconstruct State from Safepoints
- Replay if needed
- Consistent State guaranteed

## 8. Error-Recovery

### Retry-Logic

```python
def dispatch_with_retry(tool, command, max_retries=3):
    for attempt in range(max_retries):
        try:
            return dispatch(tool, command)
        except TemporaryError:
            wait(2 ** attempt)
    raise PermanentError("Max retries exceeded")
```

### Fallback

- Primary-Tool fails → Fallback-Tool
- Fallback fails → Error-Response
- Error-Response → Safepoint
- User notified

### Logging

- All errors logged (ERROR level)
- All retries logged (WARNING level)
- All fallbacks logged (INFO level)
- All successes logged (DEBUG level)
