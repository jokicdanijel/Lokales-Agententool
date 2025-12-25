# Agent Discovery Script

## Quick Start

```bash
python3 scripts/agent_discovery.py
```

**Output**: `artifacts/agent_inventory.json` (5+ MB detailliertes Inventar)

## Was es macht

Scannt alle 21 Agent-Ordner rekursiv und extrahiert:

- **Dateien**: SHA256, Größe, Typ
- **Python**: Imports, Endpoints, Ports, Agent-Refs (via AST)
- **HTML**: data-\* Attribute, Ports, Agent-Refs
- **Config**: Ports, Agent-Refs (JSON/YAML/ENV)

## Validierungen

- ❌ Verbotene Ports (8080, 3000)
- ❌ Ports außerhalb Range (12344-12399)
- ❌ Port-Mismatches vs. `system_baseline.yaml`
- ❌ Unbekannte Agent-Referenzen
- ❌ Fehlende/leere Agent-Ordner

## Exit Codes

- **0**: Erfolg, keine Violations
- **1**: Fehler mit Violations

## Beispiel-Output

```
=== DETERMINISTIC AGENT DISCOVERY ===
Project root: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
Baseline: system_baseline.yaml
Output: artifacts/agent_inventory.json

Scanning opena1...
Scanning opena2...
...
Scanning opena21...

=== DISCOVERY SUMMARY ===
Total agents: 21
Agents scanned: 21
Total files: 7476
Total violations: 61

=== VIOLATIONS ===
  - [opena3] Forbidden port detected: 8080
  - [opena4] Port mismatch: expected 12347, found [3000, 8080]
  ...
```

## Verwendung in CI/CD

```yaml
# .github/workflows/discovery.yml
- name: Run Agent Discovery
  run: python3 scripts/agent_discovery.py

- name: Upload Inventory
  uses: actions/upload-artifact@v4
  with:
    name: agent-inventory
    path: artifacts/agent_inventory.json
```

## Determinismus

- **Stable Hashing**: SHA256 über Dateiinhalt
- **Stable Ordering**: Alphabetische Sortierung aller Listen
- **Reproduzierbar**: Gleicher Repo-Zustand → Gleiche Hashes

## Datenmodell

```python
@dataclass
class FileInfo:
    path: str
    sha256: str
    size_bytes: int
    file_type: str
    imports: List[str]
    endpoints: List[str]
    ports_detected: List[int]
    agent_references: List[str]

@dataclass
class AgentInventory:
    agent_id: str
    baseline_port: int
    file_count: int
    all_imports: List[str]
    all_endpoints: List[str]
    ports_detected: Set[int]
    violations: List[str]
    files: List[FileInfo]
```

## Integration

**Preflight Check**: Automatisch aufgerufen
**GitHub Actions**: CI-Pipeline
**Copilot**: Query-Unterstützung für `agent_inventory.json`

## Compliance

✅ Read-only (keine Code-Ausführung)
✅ Deterministisch (SHA256 + Stable Sort)
✅ Fail-fast (Exit 1 bei Violations)
✅ Auditierbar (JSON mit Timestamps)

---

**Siehe auch**: [AGENT_DISCOVERY_REPORT.md](../docs/AGENT_DISCOVERY_REPORT.md)
