# ELION Entitlements System

## Übersicht

Das Entitlements-System generiert maschinenlesbare Gates für Plan-basierte Zugriffskontrolle auf Agents. Es vermeidet Hardcoding in HTML und stellt sicher, dass alle Entitlement-Regeln datengesteuert und deterministisch sind.

## Architektur

```
system_baseline.yaml       →  [build_entitlements.py]  →  build/entitlements.json
artifacts/agent_inventory.json  ↗                          ↓
                                                    [validate_entitlements.py]
                                                           ↓
                                                 artifacts/entitlements_validation.json
```

## Komponenten

### 1. `scripts/build_entitlements.py`

**Zweck**: Erstellt `build/entitlements.json` aus Baseline + Inventory

**Eingaben**:

- `system_baseline.yaml` - Plan-Definitionen
- `artifacts/agent_inventory.json` - Entdeckte Agents

**Ausgabe**:

- `build/entitlements.json` - Plan → Agent → {visible, clickable, limits, gates}

**Nutzung**:

```bash
python3 scripts/build_entitlements.py
```

### 2. `scripts/validate_entitlements.py`

**Zweck**: Validiert Entitlements gegen Policy-Regeln

**Validierungen**:

1. ✓ Keine Agents außerhalb der Baseline
2. ✓ Plan-Inklusionsordnung: ultimum ⊇ premium ⊇ pro ⊇ basic
3. ✓ Basic hat genau 4 klickbare (non-core) Agents
4. ✓ Core agents immer klickbar
5. ✓ System agents immer sichtbar
6. ✓ Basic plan Limits korrekt

**Nutzung**:

```bash
python3 scripts/validate_entitlements.py
```

**Exit Codes**:

- `0` - Alle Validierungen bestanden
- `1` - Validierung fehlgeschlagen (CI bricht ab!)

## Plan-Hierarchie

### Basic Plan

- **Klickbare Agents**: opena3, opena4, opena7, opena11 (+ Core agents)
- **Limits**:
  - `logs_access: read_only`
  - `workflow_limit: 4`
- **Total klickbar**: 6 agents

### Pro Plan

- **Zusätzlich**: opena8, opena12, opena14, opena18
- **Limits**: Full access
- **Total klickbar**: 10 agents

### Premium Plan

- **Zusätzlich**: opena6, opena9, opena15, opena16
- **Total klickbar**: 14 agents

### Ultimum Plan

- **Zusätzlich**: opena5, opena10, opena13, opena17, opena19
- **Total klickbar**: 19 agents

## Entitlement-Struktur

```json
{
  "plans": {
    "basic": {
      "agents": {
        "opena3": {
          "visible": true,
          "clickable": true,
          "reason": "included_in_basic",
          "limits": {
            "logs_access": "read_only",
            "workflow_limit": 4
          },
          "gates": []
        },
        "opena5": {
          "visible": true,
          "clickable": false,
          "reason": "not_in_plan",
          "limits": {},
          "gates": ["requires_upgrade"]
        }
      }
    }
  }
}
```

## Policy-Regeln (Unveränderlich)

### Core Agents

- **IDs**: opena1, opena2
- **Regel**: Immer sichtbar und klickbar in allen Plans

### System Agents

- **IDs**: opena20, opena21
- **Regel**: Immer sichtbar, aber nicht zwingend klickbar

### Basic Plan Constraints

- **Genau 4 klickbare non-core agents**: opena3, opena4, opena7, opena11
- **Logs**: Read-only
- **Workflows**: Max 4 pro Agent

### Plan-Inklusion

- Höhere Plans beinhalten ALLE klickbaren Agents niedrigerer Plans
- `ultimum ⊇ premium ⊇ pro ⊇ basic`

## CI/CD Integration

### Build Step

```bash
# Generiere Entitlements
python3 scripts/build_entitlements.py

# Validiere
python3 scripts/validate_entitlements.py

# Bei Fehler: Exit Code 1 → CI bricht ab
```

### GitHub Actions Beispiel

```yaml
- name: Build Entitlements
  run: python3 scripts/build_entitlements.py

- name: Validate Entitlements
  run: python3 scripts/validate_entitlements.py
```

## Nutzung in Frontend

```javascript
// Lade entitlements.json
const entitlements = await fetch("/build/entitlements.json").then((r) =>
  r.json(),
);

// Prüfe Zugriff
const userPlan = "basic";
const agentId = "opena5";

const access = entitlements.plans[userPlan].agents[agentId];

if (!access.clickable) {
  // Zeige Upgrade-Gate
  showUpgradeModal(access.gates);
}

// Prüfe Limits
const limits = access.limits;
if (limits.logs_access === "read_only") {
  disableLogEditing();
}
```

## Fehlerbehandlung

Wenn Validierung fehlschlägt:

```
✗ Validation FAILED - CI must break!

VALIDATION SUMMARY
==================
✗ 2 ERROR(S) FOUND:
  1. Agent 'opena99' in plan 'basic' not found in baseline
  2. Basic plan must have exactly 4 clickable non-core agents, found 5
```

## Testing

```bash
# Quick Test
python3 -c "
import json
with open('build/entitlements.json') as f:
    ent = json.load(f)
    basic = ent['plans']['basic']['agents']
    clickable = [k for k,v in basic.items() if v['clickable']]
    print(f'Basic clickable: {clickable}')
"
```

## Wartung

### Neuen Plan hinzufügen

1. In `system_baseline.yaml` definieren
2. `PLAN_HIERARCHY` in beiden Scripts aktualisieren
3. Rebuild + Validate

### Neuen Agent hinzufügen

1. Agent-Ordner erstellen
2. `agent_discovery.py` ausführen
3. In `system_baseline.yaml` einem Plan zuweisen
4. Rebuild + Validate

## Abhängigkeiten

```bash
pip install pyyaml
```

## Ausgaben

- `build/entitlements.json` - Maschinenlesbare Entitlements
- `artifacts/entitlements_validation.json` - Validierungsreport

## Status

✅ **DONE CRITERIA ERFÜLLT**:

- ✓ Entitlements sind rein datengesteuert und deterministisch
- ✓ Jede Regelverletzung führt zu CI-Fehler (Exit Code 1)
- ✓ Keine Hardcoding in HTML erforderlich
- ✓ Basic Plan hat genau 4 klickbare Agents
- ✓ Plan-Inklusion korrekt implementiert
