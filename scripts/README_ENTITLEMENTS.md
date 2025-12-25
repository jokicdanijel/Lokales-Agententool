# 🔐 Entitlements System

**Vollständig datengetriebenes Plan-Berechtigungssystem für ELION Hyper-Dashboard**

---

## 📋 Überblick

Das Entitlements-System generiert maschinell alle Plan-Berechtigungen aus:

- `system_baseline.yaml` (Agent-Definitionen, Plan-Struktur)
- `artifacts/agent_inventory.json` (Discovery-Output)

**Ziel:** Keine hardkodierten Berechtigungen im Code, alles aus Daten.

---

## 🏗️ Komponenten

### 1. Build-Script (`scripts/build_entitlements.py`)

Generiert `build/entitlements.json` mit vollständigen Berechtigungen für alle Pläne.

**Features:**

- Plan-Hierarchie (basic → pro → premium → ultimum)
- Inclusion-Regel (höhere Pläne enthalten niedrigere)
- Basic-Constraint: EXAKT 4 klickbare Agenten
- Core-Agenten: immer sichtbar, nie klickbar
- System-Agenten: sichtbar, nicht klickbar
- Plan-spezifische Limits (workflows, logs, tasks, API-calls)

**Usage:**

```bash
python3 scripts/build_entitlements.py
```

### 2. Validierungs-Script (`scripts/validate_entitlements.py`)

Validiert `build/entitlements.json` gegen alle Constraints.

**Validierungen:**

1. Struktur (alle 4 Pläne vorhanden)
2. Basic-Constraint (4 klickbare Agenten)
3. Inclusion-Ordering (ultimum ⊇ premium ⊇ pro ⊇ basic)
4. Core-Agenten (visible, not clickable)
5. System-Agenten (never clickable)
6. Baseline-Coverage (keine Agenten außerhalb baseline)
7. Limits-Monotonicity (Limits steigen mit Plan)

**Exit-Codes:**

- `0`: Alle Validierungen bestanden
- `1`: Validierung fehlgeschlagen (CI fails)

**Usage:**

```bash
python3 scripts/validate_entitlements.py
```

---

## 📦 Output-Dateien

### `build/entitlements.json` (24 KB)

Vollständige Entitlements für alle Pläne und Agenten.

**Struktur:**

```json
{
  "basic": {
    "name": "Basic Plan",
    "clickable_count": 4,
    "limits": {
      "workflows_per_agent": 4,
      "logs_access": "read-only",
      "max_concurrent_tasks": 2,
      "api_calls_per_day": 1000
    },
    "agents": {
      "opena1": {
        "visible": true,
        "clickable": false,
        "gates": {
          "plan_required": "basic",
          "reason": "Core infrastructure"
        },
        "limits": {}
      }
    }
  }
}
```

### `artifacts/entitlements_validation.json` (2 KB)

Validierungsergebnis mit Details.

**Struktur:**

```json
{
  "status": "passed",
  "summary": {
    "total_validations": 9,
    "passed": 9,
    "failed": 0,
    "errors": 0,
    "warnings": 0
  },
  "validations": [...],
  "errors": [],
  "warnings": []
}
```

---

## 🚀 Quick Start

### Full Pipeline

```bash
# Build + Validate
make -f Makefile.entitlements test-entitlements
```

### Einzelne Schritte

```bash
# 1. Build entitlements
make -f Makefile.entitlements entitlements

# 2. Validate
make -f Makefile.entitlements validate

# 3. View results
make -f Makefile.entitlements view-validation
```

---

## 🔍 Makefile Targets

```bash
make -f Makefile.entitlements help              # Show all targets
make -f Makefile.entitlements entitlements      # Build entitlements
make -f Makefile.entitlements validate          # Validate entitlements
make -f Makefile.entitlements test-entitlements # Full pipeline
make -f Makefile.entitlements view-basic        # Show Basic plan
make -f Makefile.entitlements view-validation   # Show validation results
make -f Makefile.entitlements view-clickable    # Show clickable agents per plan
make -f Makefile.entitlements clean-entitlements # Clean generated files
make -f Makefile.entitlements ci-validate       # CI validation (fails on error)
```

---

## 📊 Plan-Übersicht

| Plan    | Clickable Agents | Workflows/Agent | Logs Access | Max Tasks | API Calls/Day |
| ------- | ---------------- | --------------- | ----------- | --------- | ------------- |
| Basic   | 4                | 4               | read-only   | 2         | 1,000         |
| Pro     | 8                | 10              | read-write  | 5         | 5,000         |
| Premium | 12               | 25              | read-write  | 10        | 20,000        |
| Ultimum | 17               | unlimited       | full        | unlimited | unlimited     |

### Basic (4 clickable)

- opena3 (OpenWebUI)
- opena4 (Telegram)
- opena7 (Email)
- opena11 (Access Control)

### Pro (Basic + 4)

- opena8 (WhatsApp)
- opena12 (Social Media)
- opena14 (Calendar)
- opena18 (CRM)

### Premium (Pro + 4)

- opena6 (Browser)
- opena9 (Phone)
- opena15 (HTML Generator)
- opena16 (Shop)

### Ultimum (Premium + 5)

- opena5 (VSCode)
- opena10 (Call Tracking)
- opena13 (Influencer)
- opena17 (Homepage)
- opena19 (Finance)

---

## 🔐 Constraints (Hard Rules)

### Core Agents (IMMER visible, NIE clickable)

- `opena1` (Koordinator)
- `opena2` (Archive)

### System Agents (sichtbar, nicht clickable)

- `opena20` (Dashboard)
- `opena21` (Workflow)

### Basic Plan (EXAKT 4 clickable)

- `opena3`, `opena4`, `opena7`, `opena11`
- Keine Abweichung erlaubt!

### Inclusion-Regel

```
ultimum ⊇ premium ⊇ pro ⊇ basic
```

Jeder höhere Plan MUSS alle niedrigeren Pläne enthalten.

---

## 🧪 CI Integration

### GitHub Actions

Das Workflow-File `.github/workflows/validate-entitlements.yml` führt automatisch aus:

1. Build entitlements
2. Validate entitlements
3. Check validation results
4. Upload artifacts
5. Comment PR with results

**Trigger:**

- Push to `main`, `develop`, `ci/**`
- PR to `main`
- Changes to:
  - `system_baseline.yaml`
  - `artifacts/agent_inventory.json`
  - `scripts/build_entitlements.py`
  - `scripts/validate_entitlements.py`

### Exit Codes

```bash
# Run validation
python3 scripts/validate_entitlements.py
echo $?

# 0 = success (CI passes)
# 1 = failure (CI fails)
```

---

## 📝 Integration in Code

### opena20 (Dashboard Agent)

```python
import json

# Load entitlements
with open('build/entitlements.json', 'r') as f:
    entitlements = json.load(f)

def is_agent_clickable(agent_id: str, plan: str) -> bool:
    """Check if agent is clickable for plan"""
    plan_data = entitlements.get(plan, {})
    agent_data = plan_data.get('agents', {}).get(agent_id, {})
    return agent_data.get('clickable', False)

def get_plan_limits(plan: str) -> dict:
    """Get plan-specific limits"""
    return entitlements.get(plan, {}).get('limits', {})

def get_clickable_agents(plan: str) -> list:
    """Get all clickable agents for plan"""
    plan_data = entitlements.get(plan, {})
    agents = plan_data.get('agents', {})
    return [
        agent_id for agent_id, data in agents.items()
        if data.get('clickable', False)
    ]
```

### opena1 (Koordinator - API Gates)

```python
def check_agent_access(agent_id: str, user_plan: str) -> bool:
    """Check if user can access agent"""
    plan_data = entitlements.get(user_plan, {})
    agent_data = plan_data.get('agents', {}).get(agent_id, {})

    if not agent_data.get('clickable', False):
        reason = agent_data.get('gates', {}).get('reason', 'Not available')
        raise PermissionError(f"Access denied: {reason}")

    return True

def check_workflow_limit(user_plan: str, current_workflows: int) -> bool:
    """Check if user can create more workflows"""
    limits = entitlements.get(user_plan, {}).get('limits', {})
    max_workflows = limits.get('workflows_per_agent', 0)

    if max_workflows == -1:  # unlimited
        return True

    return current_workflows < max_workflows
```

---

## 🔄 Workflow

```
1. Agent-Discovery (agent_discovery.py)
   → artifacts/agent_inventory.json

2. Entitlements-Build (build_entitlements.py)
   → build/entitlements.json

3. Validation (validate_entitlements.py)
   → artifacts/entitlements_validation.json

4. CI-Check (GitHub Actions)
   → Exit Code 0/1

5. Integration (opena20, opena1)
   → Load entitlements.json
```

---

## 📚 Dokumentation

- **[ENTITLEMENTS_BUILDER_COMPLETE.md](../docs/ENTITLEMENTS_BUILDER_COMPLETE.md)** - Vollständige Dokumentation
- **[COPILOT_HANDOFF.md](../docs/COPILOT_HANDOFF.md)** - Copilot Integration Rules

---

## ✅ Validation Results

```
✅ Structure: All 4 required plans present
✅ Basic constraint: Exactly 4 clickable
✅ Inclusion: ultimum ⊇ premium ⊇ pro ⊇ basic
✅ Core agents: visible, not clickable
✅ System agents: never clickable
✅ Baseline coverage: All 21 agents
✅ Limits monotonicity: Workflows 4 → 10 → 25 → ∞
```

---

**Status:** ✅ Production Ready
**Last Updated:** 2025-12-23
**Version:** 1.0.0
