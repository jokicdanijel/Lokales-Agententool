# 📊 Workspace Evaluation Framework

## Overview

The Workspace Evaluation Framework is a comprehensive assessment tool for the PORTIER 3.0 multi-agent platform. It validates workspace health, configuration, security compliance, and operational readiness across multiple dimensions.

## Features

### Evaluation Categories

1. **File Structure Evaluation**
   - Validates presence of critical directories (`scripts/`, `tests/`, `src/`, `docs/`, `configs/`)
   - Checks configuration files (`pyproject.toml`, `requirements.txt`, `.gitignore`)
   - Verifies CI/CD infrastructure (`.github/workflows/`)

2. **Service Port Evaluation**
   - Checks availability of all PORTIER 3.0 service ports (12344-12365)
   - Detects port conflicts
   - Identifies services that may be running or blocked
   - Covers core services: opena1-opena20, kordp, archivp

3. **Configuration Files Evaluation**
   - Validates `configs/routing_matrix.yaml` structure
   - Checks YAML/TOML syntax validity
   - Verifies presence of required configuration keys

4. **Test Coverage Evaluation**
   - Scans `tests/` directory for test files
   - Lists all discovered test files
   - Reports test file count and coverage

5. **Security Compliance Evaluation**
   - Verifies `.gitignore` patterns for sensitive files (`.env`, `*.key`, `*.pem`, `*.pub`)
   - Checks for accidentally committed secrets
   - Validates security best practices

6. **Scripts Executability Evaluation**
   - Checks if critical scripts have executable permissions
   - Validates presence of essential operational scripts
   - Covers: `start_all.sh`, `stop_all.sh`, `check_health.sh`, `verify_stack.sh`, `structure_manager.py`

## Usage

### Basic Usage

```bash
# Run evaluation with default settings
python scripts/workspace_evaluation.py

# Run without saving report
python scripts/workspace_evaluation.py --no-save

# Specify custom root directory
python scripts/workspace_evaluation.py --root /path/to/workspace

# Custom output filename
python scripts/workspace_evaluation.py --output my_report.json
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--root` | Project root directory | Current directory (`.`) |
| `--no-save` | Don't save report to file | Reports are saved by default |
| `--output` | Output report filename | `workspace_evaluation_report.json` |

### Exit Codes

- `0` - Workspace status is "excellent" or "good"
- `1` - Workspace status is "fair" or "poor"

## Output

### Console Output

The framework provides color-coded console output:

- 🟢 **GREEN** - Passed checks
- 🟡 **YELLOW** - Warnings or partial failures
- 🔴 **RED** - Failed checks

Example:
```
======================================================================
                      File Structure Evaluation                       
======================================================================

✓ PASS Scripts directory
     /path/to/scripts
✓ PASS Test directory
     /path/to/tests
```

### JSON Report

The framework generates a detailed JSON report with:

```json
{
  "timestamp": "2025-12-04T05:48:14.298545",
  "evaluations": {
    "file_structure": {
      "passed": 9,
      "failed": 0,
      "details": [...]
    },
    "service_ports": {
      "passed": 10,
      "failed": 0,
      "in_use": [],
      "available": [...]
    },
    ...
  },
  "score": 38,
  "max_score": 38,
  "status": "excellent"
}
```

### Status Levels

| Status | Score Range | Description |
|--------|-------------|-------------|
| **Excellent** | ≥ 90% | Workspace is in optimal condition |
| **Good** | 75-89% | Minor issues detected |
| **Fair** | 60-74% | Several issues need attention |
| **Poor** | < 60% | Critical issues detected |

## Integration

### CI/CD Integration

Add to `.github/workflows/workspace-evaluation.yml`:

```yaml
name: Workspace Evaluation

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install pyyaml
      
      - name: Run workspace evaluation
        run: |
          python scripts/workspace_evaluation.py
      
      - name: Upload evaluation report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: workspace-evaluation-report
          path: workspace_evaluation_report.json
          retention-days: 30
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python scripts/workspace_evaluation.py --no-save
exit $?
```

### Make Integration

Add to `Makefile`:

```makefile
.PHONY: evaluate
evaluate:
	@python scripts/workspace_evaluation.py

.PHONY: evaluate-quiet
evaluate-quiet:
	@python scripts/workspace_evaluation.py --no-save > /dev/null
```

### Ops.sh Integration

You can run the evaluation directly from the central operations script:

```bash
# Run evaluation and save JSON report
bin/ops.sh eval

# The command exits with code 0 when status is "excellent" or "good".
# If status is "fair" or "poor" the exit code will be non-zero and
# `workspace_evaluation_report.json` will contain the details.
```

## Customization

### Adding New Evaluation Categories

To add a new evaluation category:

1. Create a new method in `WorkspaceEvaluator` class:

```python
def evaluate_custom_category(self) -> Dict:
    """Evaluate custom aspect of workspace"""
    self.print_header("Custom Category Evaluation")
    
    results = {"passed": 0, "failed": 0, "details": []}
    
    # Your evaluation logic here
    
    self.results["evaluations"]["custom_category"] = results
    return results
```

2. Call it in `run_full_evaluation()`:

```python
def run_full_evaluation(self, save_report: bool = True):
    # ... existing evaluations ...
    self.evaluate_custom_category()
    # ... rest of method ...
```

### Customizing Evaluation Criteria

Edit the evaluation methods to adjust criteria:

```python
# Example: Add more critical paths
critical_paths = {
    "scripts/": "Scripts directory",
    "tests/": "Test directory",
    # Add your custom paths here
    "custom/path/": "Custom directory",
}
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'yaml'`
```bash
# Solution: Install PyYAML
pip install pyyaml
```

**Issue**: Permission denied when running script
```bash
# Solution: Make script executable
chmod +x scripts/workspace_evaluation.py
```

**Issue**: All service ports show as "in use"
```bash
# Solution: Stop services or verify ports
./scripts/stop_all.sh
```

## Examples

### Example 1: Quick Health Check

```bash
# Fast health check without saving report
python scripts/workspace_evaluation.py --no-save
```

### Example 2: Automated Testing

```bash
# Run evaluation and check exit code
if python scripts/workspace_evaluation.py --no-save; then
    echo "Workspace is healthy!"
else
    echo "Workspace needs attention!"
    exit 1
fi
```

### Example 3: Daily Monitoring

```bash
# Save daily reports with timestamps
DATE=$(date +%Y%m%d)
python scripts/workspace_evaluation.py --output "reports/evaluation_${DATE}.json"
```

## Related Documentation

- [OPERATIONS.md](../docs/OPERATIONS.md) - Operations guide for PORTIER 3.0
- [README.md](../README.md) - Main project documentation
- [PORTIER_3.0_ENTERPRISE_README.md](../PORTIER_3.0_ENTERPRISE_README.md) - Enterprise features
- [.github/copilot-instructions.md](../.github/copilot-instructions.md) - Development guidelines

## Changelog

### Version 1.0.0 (2025-12-04)

- Initial release
- File structure evaluation
- Service port checking
- Configuration validation
- Test coverage analysis
- Security compliance checks
- Scripts executability verification
- JSON report generation
- Color-coded console output
- Comprehensive scoring system

## License

MIT + Internal Use Only (Enterprise Components)

## Author

Danijel Jokic - PORTIER 3.0 Platform

## Support

For issues or questions, please refer to:
- Project documentation in `docs/`
- GitHub Issues: [jokicdanijel/Gesamtprojekt-start](https://github.com/jokicdanijel/Gesamtprojekt-start)
