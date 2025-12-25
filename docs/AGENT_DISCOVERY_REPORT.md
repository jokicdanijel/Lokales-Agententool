# Agent Discovery - Deterministic Analysis

## Übersicht

Das `scripts/agent_discovery.py` Script führt eine vollständige, deterministische Analyse aller Agent-Ordner durch und generiert ein umfassendes Inventar.

## Eigenschaften

### HARD CONSTRAINTS (wie gefordert)

✅ **Read-only**: Keine Code-Ausführung, keine Netzwerk-Calls
✅ **Deterministisch**: SHA256-Hashing + stabile Sortierung
✅ **Fail-fast**: Fehlende/leere Ordner → Exit 1
✅ **Port-Validierung**: Mismatches vs. Baseline → Violation

### Features

- **Rekursive Datei-Enumeration** mit SHA256-Hashing
- **AST-basierte Python-Analyse**:
  - Import-Extraktion
  - Endpoint-Erkennung (FastAPI/Flask)
  - Port-Literale
  - Agent-Referenzen (opena1, opena2, ...)
- **HTML-Parsing**:
  - data-\* Attribute
  - Form/Nav-Präsenz
  - Port-Literale
  - Agent-Referenzen
- **Config-Analyse** (JSON/YAML/ENV):
  - Port-Literale
  - Agent-Referenzen

### Validierung

Das Script validiert gegen folgende Regeln:

1. **Verbotene Ports**: 8080, 3000 → FAIL
2. **Port-Range**: 12344-12399 (erlaubt) → außerhalb FAIL
3. **Port-Mismatch**: Code-Ports ≠ Baseline-Port → FAIL
4. **Unbekannte Agent-Refs**: Referenzen auf nicht-existierende Agents → FAIL
5. **Fehlende Ordner**: Agent-Ordner existiert nicht → FAIL
6. **Leere Ordner**: Agent-Ordner ohne Dateien → FAIL

## Verwendung

### Ausführung

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
python3 scripts/agent_discovery.py
```

### Exit Codes

- **0**: Discovery erfolgreich, keine Violations
- **1**: Discovery fehlgeschlagen mit Violations

### Outputs

**Datei**: `artifacts/agent_inventory.json`

**Struktur**:

```json
{
  "baseline_hash": "6dd1fc4c2f638860...",
  "discovery_timestamp": "2025-12-23T04:40:20.527304Z",
  "summary": {
    "total_agents": 21,
    "agents_scanned": 21,
    "agents_with_violations": 17,
    "total_files": 7476,
    "total_violations": 61
  },
  "agents": {
    "opena1": {
      "agent_id": "opena1",
      "baseline_port": 12344,
      "baseline_role": "service",
      "baseline_visibility": "public",
      "folder_path": "/path/to/1.opena1&2_portier/opena1",
      "file_count": 42,
      "total_size_bytes": 123456,
      "python_files": 15,
      "html_files": 5,
      "json_files": 3,
      "yaml_files": 2,
      "other_files": 17,
      "all_imports": ["fastapi", "pydantic", ...],
      "all_endpoints": ["/health", "/api/v1/..."],
      "ports_detected": [12344, 12345],
      "agent_references": ["opena2", "opena20"],
      "has_main": true,
      "has_requirements": true,
      "has_dockerfile": false,
      "has_config": true,
      "violations": [],
      "files": [
        {
          "path": "/full/path/to/file.py",
          "relative_path": "file.py",
          "sha256": "abc123...",
          "size_bytes": 1234,
          "file_type": "python",
          "imports": ["fastapi"],
          "endpoints": ["/health"],
          "ports_detected": [12344],
          "agent_references": ["opena2"],
          "has_main": true
        }
      ]
    }
  },
  "global_violations": [
    "[opena3] Forbidden port detected: 8080 (forbidden: [8080, 3000])",
    "[opena3] Port 8080 outside allowed range (12344-12399)"
  ]
}
```

## Aktuelle Ergebnisse

### Scan vom 2025-12-23T04:40:20Z

```
Total agents: 21
Agents scanned: 21
Total files: 7476
Total violations: 61
```

### Top 5 Agents nach Dateizahl

1. **opena3**: 6584 files (OpenWebUI)
2. **opena15**: 236 files
3. **opena4**: 114 files
4. **opena6**: 55 files
5. **opena9**: 47 files

### Violations Breakdown

| Agent           | Violations | Hauptproblem                                       |
| --------------- | ---------- | -------------------------------------------------- |
| opena3          | 19         | Viele nicht-konforme Ports (3000, 8080, 5000, ...) |
| opena4          | 4          | Ports 3000, 8080                                   |
| opena5          | 3          | Port 8080, 8000                                    |
| opena6          | 3          | Port 8080, 5000                                    |
| opena7-opena16  | 2-3        | Port 8080 + Port-Mismatches                        |
| opena17-opena19 | 1          | Port-Mismatches                                    |

## Behebung von Violations

### Schritt 1: Einzelnen Agent prüfen

```bash
python3 -c "
import json
with open('artifacts/agent_inventory.json') as f:
    data = json.load(f)
    agent = data['agents']['opena3']
    print(f\"Ports found: {agent['ports_detected']}\")
    print(f\"Expected: {agent['baseline_port']}\")
    for v in agent['violations']:
        print(f\"  - {v}\")
"
```

### Schritt 2: Dateien mit falschen Ports finden

```bash
grep -r "8080" 2.opena3_openwebui/ --include="*.py" --include="*.yaml" --include="*.json"
```

### Schritt 3: Ports korrigieren

Option 1: Manuelle Korrektur in den Agent-Dateien
Option 2: Legacy-Code zu `_legacy/` verschieben
Option 3: Dateien zu Exclusion-Liste hinzufügen (wenn Demo/Test-Code)

## Deterministik-Garantien

### Stable Hashing

Jede Datei erhält einen SHA256-Hash über ihren Inhalt. Bei gleichem Repository-Zustand → gleiche Hashes.

### Stable Ordering

- Agents alphabetisch sortiert
- Dateien innerhalb Agent alphabetisch sortiert
- Arrays (imports, endpoints, etc.) alphabetisch sortiert
- JSON-Output mit `sort_keys=True`

### Reproduzierbarkeit

```bash
# Run 1
python3 scripts/agent_discovery.py
sha256sum artifacts/agent_inventory.json > run1.hash

# Run 2 (ohne Änderungen am Code)
python3 scripts/agent_discovery.py
sha256sum artifacts/agent_inventory.json > run2.hash

# Vergleich
diff run1.hash run2.hash
# → Keine Unterschiede (außer discovery_timestamp)
```

## Integration mit Preflight

Das Discovery-Script wird automatisch von `scripts/preflight_check.py` aufgerufen:

```python
# In preflight_check.py
subprocess.run(["python3", "scripts/agent_discovery.py"], check=True)

# Bei Exit 1 → Preflight FAIL
# Bei Exit 0 → Preflight weiter
```

## Nächste Schritte

1. **Violations beheben**: 61 Port-Verstöße in 17 Agents
2. **Baseline aktualisieren**: Falls neue Ports legitim sind
3. **CI/CD Integration**: Discovery als GitHub Action
4. **Monitoring**: Violations im Dashboard anzeigen

## Technische Details

### AST-basierte Analyse

Statt Regex werden Python-Dateien mit dem `ast`-Modul geparst:

```python
tree = ast.parse(content)
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        # Extract import
    elif isinstance(node, ast.ImportFrom):
        # Extract from import
```

Vorteile:

- Kein False-Positive bei Kommentaren
- Exakte Syntax-Erkennung
- Fehlertoleranz (SyntaxError → Skip)

### Endpoint-Erkennung

Unterstützte Frameworks:

- **FastAPI**: `@app.get("/path")`, `@router.post("/path")`
- **Flask**: `@app.route("/path")`

Pattern:

```python
fastapi_pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)'
flask_pattern = r'@app\.route\(["\']([^"\']+)'
```

### Port-Erkennung

3 Patterns:

1. `port=12345` (Assignment)
2. `:12345` in URLs
3. `PORT = 12345` (Konstante)

Filter: Nur Ports 1024-65535

## Backup

Das alte Script wurde gesichert:

```bash
scripts/agent_discovery.py.backup
```

## Copilot-Integration

Für GitHub Copilot:

```markdown
CONTEXT: agent_inventory.json enthält vollständige Agent-Analyse
USE CASE: "Welche Agents nutzen Port 8080?"
QUERY: `jq '.agents | to_entries | map(select(.value.ports_detected | contains([8080]))) | .[].key' artifacts/agent_inventory.json`
```

## Compliance

✅ Alle HARD CONSTRAINTS erfüllt
✅ Deterministisch (SHA256 + Stable Sort)
✅ Read-only (kein `exec`, kein `eval`)
✅ Fail-fast (Exit 1 bei Violations)
✅ Auditierbar (JSON mit Timestamps & Hashes)

---

**Status**: ✅ PRODUCTION READY
**Version**: 1.0.0
**Datum**: 2025-12-23
