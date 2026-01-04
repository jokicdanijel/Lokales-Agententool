# YAML Secrets Management

## PORTIER 3.0 Compliance (binding)

This module MUST comply with PORTIER 3.0 baseline laws:

- **Agent IDs:** exactly `opena1..opena21` (no aliases, no renames)
- **Ports:** Single Source of Truth is `system_baseline.yaml` (baseline port table)
- **Port policy:** allowed range `12344–12399`, forbidden `8080`
- **Frontend/Backend:** every agent has both (UI can be minimal)
- **Domains:** `hyperdashboard-one.de` and `www.hyperdashboard-one.de` (primary)

### Canonical Port Table Rule

Do not copy port mappings from PR summaries, scripts, or comments unless they match the baseline.
If there is a conflict, the baseline wins and CI must fail until aligned.

---

## Module: src/pkg/yaml_secrets_manager.py

Handles YAML configuration and secrets integration with Pydantic v2.

### Features

- Deterministic YAML loading
- `.env` / envvar integration
- Hardcoded secret detection
- Port policy validation
- Agent ID validation

### Usage

```python
from src.pkg.yaml_secrets_manager import YAMLSecretsManager

manager = YAMLSecretsManager("system_baseline.yaml")
config = manager.load()
# Returns: validated config dict with secrets from .env
```

### Configuration Structure

```yaml
port_policy:
  allowed_range:
    min: 12344
    max: 12399
  forbidden_ports:
    - 8080

agents:
  - id: "opena1"
    port: 12344
    folder_path: "1.opena1&2_portier/opena1"
    # ... more fields
```

### Error Handling

- Missing `.env` keys → Error (fails fast)
- Hardcoded secrets in YAML → Detected + warned
- Port conflicts → Validation error
- Invalid agent IDs → Validation error

---

## Tests: tests/test_yaml_secrets_manager.py

Comprehensive test suite covering:

- YAML parsing (deterministic)
- Secrets validation
- Port policy enforcement
- Agent ID validation
- Error cases

Run:
```bash
pytest tests/test_yaml_secrets_manager.py -v
```

---

## Best Practices

1. **Never hardcode secrets in YAML** → Use `.env` or envvars
2. **Always validate ports against baseline** → Before code review
3. **Agent IDs are immutable** → No aliases or renames
4. **Baseline is the source of truth** → Not PR summaries or comments

---

## Changelog

### 2025-01-02

- Initial implementation (Pydantic v2)
- Secrets manager module
- Test suite
- Documentation
