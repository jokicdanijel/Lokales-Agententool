# ELION Hyper-Dashboard – Evaluation Framework

**Version:** 1.1 (Dec 2025)  
**Purpose:** Automated workspace health assessment & Production-Readiness certification

---

## 🎯 Quick Start

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Run complete evaluation
bin/ops.sh eval

# Or directly
python3 scripts/workspace_evaluation.py

# View full JSON report
cat workspace_evaluation_report.json | jq .
```

---

## 📊 Evaluation Categories (7 Areas)

### 1. **Policy & Governance** (Weight: 2.5x)
**Purpose:** Enforce critical infrastructure policies  
**Checks:**
- ✅ No forbidden port 8080 in ops.sh
- ✅ AGENTS mapping exists (Single Source of Truth)
- ✅ .env NOT sourced in agent start scripts
- ✅ All agent ports within 12344–12399 range
- ✅ .env file permissions secure (not world-readable)

**Readiness Impact:** HIGHEST – Policy violations block production

---

### 2. **Python Environment** (Weight: 1.5x)
**Purpose:** Ensure reproducible, clean Python setup  
**Checks:**
- ✅ `.venv/` directory exists and properly initialized
- ✅ `requirements.txt` present with pinned versions
- ✅ `pydantic` listed (data validation)
- ✅ `pydantic-settings` listed (config management)
- ✅ `fastapi` listed (async web framework)
- ✅ venv Python executable exists & is usable

**Common Issues:**
- ❌ ~/.local contamination (use `export PYTHONNOUSERSITE=1`)
- ❌ Missing venv (run `python3 -m venv .venv`)
- ❌ Dependency conflicts (pip freeze & compare)

---

### 3. **Infrastructure & Operations** (Weight: 1.5x)
**Purpose:** Operational excellence & automation  
**Checks:**
- ✅ `bin/ops.sh` syntax valid (bash -n check)
- ✅ `bin/ops.sh` executable (+x permission)
- ✅ `logs/` directory exists for service output
- ✅ HTML Runbook generated (`docs/agent_startanleitung.html`)
- ✅ HTML Runbook is valid (DOCTYPE, closing tags)
- ✅ Core startup scripts present (opena1, opena20)

**Generate Runbook:**
```bash
bin/ops.sh doc:agents
```

---

### 4. **Configuration & Secrets** (Weight: 2.5x – HIGHEST)
**Purpose:** Secure credential management  
**Checks:**
- ✅ `.env` file readable and accessible
- ✅ `DASHBOARD_ADMIN_TOKEN` configured
- ✅ `OPENAI_API_KEY_OPENA1` & `OPENA2` present
- ✅ No placeholder values (`YOUR_`, `CHANGE_ME`, etc.)
- ✅ `.env` file permissions: NOT world-readable

**Setup .env:**
```bash
# Copy template
cp .env.example .env
chmod 600 .env

# Edit with secrets
nano .env

# Verify
grep -E "^(DASHBOARD_ADMIN_TOKEN|OPENAI_API_KEY)" .env | head -3
```

---

### 5. **Code Quality & Standards** (Weight: 1.0x)
**Purpose:** Maintainability & best practices  
**Checks:**
- ✅ `tests/` directory exists
- ✅ `.gitignore` present with proper exclusions
- ✅ `.gitignore` covers `.env`, `.venv`, `__pycache__`
- ✅ `README.md` or similar documentation
- ✅ Docker files present (optional but recommended)
- ✅ No `__pycache__` proliferation (< 5 dirs)

**Setup .gitignore:**
```bash
# Ensure covers:
.env
.venv/
__pycache__/
*.pyc
*.pyo
logs/
*.pid
```

---

### 6. **Documentation & Accessibility** (Weight: 0.8x)
**Purpose:** Onboarding & operations knowledge  
**Checks:**
- ✅ `docs/` directory exists
- ✅ Documentation files present (.md, .rst, .html)
- ✅ HTML Runbook (`docs/agent_startanleitung.html`)
- ✅ Architecture/API documentation (optional)

**Key Documents:**
- `docs/agent_startanleitung.html` – Interactive startup guide
- `docs/OPERATIONS.md` – Daily operations manual
- `docs/TROUBLESHOOTING.md` – Common issues & fixes

---

### 7. **Deployment Readiness** (Weight: 1.2x)
**Purpose:** Production operability  
**Checks:**
- ✅ Logging infrastructure (`logs/` directory)
- ✅ Health check logic in `ops.sh`
- ✅ Reverse proxy config (Nginx example)
- ✅ `.env.example` for onboarding
- ✅ Container orchestration hints (docker-compose)

**Reverse Proxy Setup (Nginx):**
```nginx
# Example: opena1 at 127.0.0.1:12344
location ^~ /opena1/ {
  proxy_pass http://127.0.0.1:12344;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  rewrite ^/opena1/(.*) /$1 break;  # Remove prefix
}
```

---

## 🎯 Readiness Levels

| Score | Level | Meaning |
|-------|-------|---------|
| 90–100% | ✅ **PRODUCTION_READY** | Deploy to production immediately |
| 75–89% | ⚠️ **PRODUCTION_READY_WITH_REVIEW** | Production-ready but review checklist first |
| 60–74% | 🔶 **STAGING_READY** | Deploy to staging; fix before production |
| < 60% | ❌ **DEVELOPMENT_ONLY** | Not ready; development/testing only |

---

## 📋 Checklist: Before Each Deploy

```bash
#!/bin/bash
# Pre-deploy checklist

cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# 1. Run evaluation
python3 scripts/workspace_evaluation.py

# 2. Check overall score
SCORE=$(jq .overall_score workspace_evaluation_report.json)
READY=$(jq -r .readiness_level workspace_evaluation_report.json)

echo "Readiness: $READY (Score: $SCORE/100)"

# 3. If not PRODUCTION_READY, show failures
if [[ "$READY" != "PRODUCTION_READY"* ]]; then
  echo "❌ Failed checks:"
  jq '.categories[] | select(.score < 100) | {category, checks: [.checks[] | select(.passed == false)]}' \
    workspace_evaluation_report.json
  exit 1
fi

# 4. Run stack tests
bin/ops.sh verify:local

# 5. Deploy
echo "✅ Ready to deploy"
```

---

## 🔧 Common Failures & Fixes

### ❌ ".env: No placeholders" fails
**Problem:** `.env` has template values  
**Fix:**
```bash
nano .env
# Find and replace: YOUR_, CHANGE_ME, FIXME, etc.
# Add real values for:
#   - DASHBOARD_ADMIN_TOKEN (strong random string)
#   - OPENAI_API_KEY_OPENA1 (sk-proj-...)
#   - OPENAI_API_KEY_OPENA2 (sk-proj-...)
```

### ❌ "ops.sh: Syntax valid" fails
**Problem:** ops.sh has syntax errors  
**Fix:**
```bash
bash -n bin/ops.sh  # Detailed error
# Usually: line 1 garbage, CRLF, BOM
sed -i '1{/^ops\.sh$/d;}' bin/ops.sh
sed -i 's/\r$//' bin/ops.sh
bash -n bin/ops.sh  # Should pass now
```

### ❌ ".env: Not sourced in agent scripts" fails
**Problem:** Agent start scripts still use `source .env`  
**Fix:**
```bash
# Find offenders
find . -name "start_*.sh" -exec grep -l "source.*\.env" {} \;

# Remove sourcing (only ops.sh loads .env)
sed -i '/source.*\.env/d' <file>
```

### ❌ "Agent ports within policy" fails
**Problem:** Port outside 12344–12399 or using 8080  
**Fix:**
```bash
# Check ops.sh AGENTS mapping
grep "openaX:" bin/ops.sh | grep -v "12344\|12345\|1234[7-9]\|1235[0-9]\|1236[0-9]\|1236[7-9]"

# Correct offending port in:
# - bin/ops.sh (AGENTS array)
# - agent/main_openaX.py (PORT = ...)
# - agent/bin/start_openaX.sh (port assignment)
```

### ❌ "Python Environment" failures
**Problem:** venv missing or incomplete dependencies  
**Fix:**
```bash
# Rebuild venv from scratch
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel
pip install -r requirements.txt

# Verify
python3 -c "import pydantic, fastapi; print('OK')"
```

---

## 📈 Scoring Algorithm

Each category has multiple checks. Score = `(passed_checks / total_checks) * 100`

**Overall Score** = Weighted average across 7 categories:

```
Score = Σ(category_score × category_weight) / Σ(category_weight)

Weights:
  Policy & Governance:     2.5x (CRITICAL – failures block production)
  Python Environment:      1.5x (Important – reproducibility)
  Infrastructure & Ops:    1.5x (Important – automation)
  Configuration & Secrets: 2.5x (CRITICAL – security)
  Code Quality:            1.0x (Nice-to-have)
  Documentation:           0.8x (Nice-to-have)
  Deployment Readiness:    1.2x (Important – operations)
```

**Example:**
```
Policy:           95% × 2.5 = 237.5
Python:           90% × 1.5 = 135.0
Infrastructure:   100% × 1.5 = 150.0
Configuration:    80% × 2.5 = 200.0
Code Quality:     85% × 1.0 = 85.0
Documentation:    90% × 0.8 = 72.0
Deployment:       95% × 1.2 = 114.0
                  ─────────────────
Total Weight:                = 11.5
Overall Score:   (993.5 / 11.5) = 86.4%  → "PRODUCTION_READY_WITH_REVIEW"
```

---

## 🚀 Automation: CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/evaluate.yml
name: Workspace Evaluation

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Run evaluation
        run: |
          python3 scripts/workspace_evaluation.py
      
      - name: Check readiness
        run: |
          READY=$(jq -r .readiness_level workspace_evaluation_report.json)
          if [[ "$READY" != "PRODUCTION_READY"* ]]; then
            echo "❌ Not production-ready: $READY"
            exit 1
          fi
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: evaluation-report
          path: workspace_evaluation_report.json
```

---

## 📞 Support

**Issues?** Run the full evaluation and share:
```bash
# Generate report
python3 scripts/workspace_evaluation.py

# Show all failures
jq '.categories[] | select(.score < 100)' workspace_evaluation_report.json

# Include in issue/ticket
cat workspace_evaluation_report.json
```

---

**Last Updated:** 2025-12-18  
**Framework Version:** 1.1 (Enterprise Edition)
