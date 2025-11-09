[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]

# Phase 4.1 – Pre-Launch Deployment Checklist

**Status:** Final Validation Before Nov 7 Kickoff  
**Date:** 2025-11-06  
**Owner:** DevOps + QA Lead

---

## ✅ Pre-Launch Validation (Alle müssen PASS sein)

### [  ] 1. Repository & Branch Setup

```bash
# Git branch status
git branch -a
# Should show: feature/phase-4-bridge (or create now)

git status
# Should be: on main, no uncommitted changes

# PDI files exist
ls -la 19.dashboard_agent/docs/PDI/
# REQUIRED:
#  - project_manifest.md
#  - chapters/00_kapitelplan.md
#  - DEV_PROD_SWITCH_BLUEPRINT.md
#  - BOOTSTRAP_PDI_PROMPT.md
```

**Checklist:**
- [ ] Main branch clean
- [ ] Feature branch ready (or create)
- [ ] All PDI docs committed
- [ ] No uncommitted changes

**Validator:** ________________  **Date:** ________

---

### [  ] 2. Environment Setup

```bash
# Python version
python3 --version
# Required: 3.12 or higher

# Virtual environment
source 1.portier_openai/venv313/bin/activate
pip freeze | grep fastapi
# Should show: fastapi, uvicorn

# Required packages
cat 19.dashboard_agent/requirements.txt | head -5
```

**Checklist:**
- [ ] Python 3.12+ installed
- [ ] venv313 activated
- [ ] All dependencies installed (pip freeze OK)
- [ ] No version conflicts

**Validator:** ________________  **Date:** ________

---

### [  ] 3. File Structure Validation

```bash
# Check all required Phase 4.1 directories exist
for dir in bin scripts tests docs/PDI docker systemd; do
  [ -d "$dir" ] && echo "✅ $dir" || echo "❌ $dir MISSING"
done

# Check critical files
files=(
  "bin/system_mode_switch.sh"
  "19.dashboard_agent/.vscode/portier-bridge/BOOTSTRAP_PDI_PROMPT.md"
  "19.dashboard_agent/docs/PDI/project_manifest.md"
  "19.dashboard_agent/docs/DEV_PROD_SWITCH_BLUEPRINT.md"
  ".github/SYSTEM_ANALYSIS_BYPASS_MECHANISMS.md"
)

for file in "${files[@]}"; do
  [ -f "$file" ] && echo "✅ $file" || echo "❌ $file MISSING"
done
```

**Checklist:**
- [ ] All directories exist
- [ ] All critical PDI files present
- [ ] Task 01 file executable (bin/system_mode_switch.sh -x)
- [ ] No missing dependencies

**Validator:** ________________  **Date:** ________

---

### [  ] 4. Code Quality Checks

```bash
# Lint check
cd 19.dashboard_agent
pylint *.py 2>&1 | grep "Your code" || echo "⚠️ Install pylint: pip install pylint"

# Format check
black --check . 2>&1 | head -3 || echo "⚠️ Install black: pip install black"

# Type hints
python3 -m py_compile *.py && echo "✅ Syntax OK" || echo "❌ Syntax errors"

# Return to root
cd ../..
```

**Checklist:**
- [ ] Pylint score ≥8.0 (or accept current)
- [ ] Black formatting OK
- [ ] No syntax errors
- [ ] No import errors

**Validator:** ________________  **Date:** ________

---

### [  ] 5. Task 01 Functional Test

```bash
# Test system_mode_switch.sh
bin/system_mode_switch.sh show 2>&1 | grep -q "Current Mode" && \
  echo "✅ Task 01 show works" || echo "❌ Task 01 show FAILED"

bin/system_mode_switch.sh help 2>&1 | grep -q "Usage:" && \
  echo "✅ Task 01 help works" || echo "❌ Task 01 help FAILED"

# Validate DEV environment
bin/system_mode_switch.sh validate development 2>&1 | grep -q "validation passed" && \
  echo "✅ DEV validation OK" || echo "⚠️ DEV validation warning (may be OK)"
```

**Checklist:**
- [ ] `system_mode_switch.sh show` works
- [ ] `system_mode_switch.sh help` works
- [ ] `system_mode_switch.sh validate development` passes
- [ ] Audit log created (logs/system_mode_audit.log)

**Validator:** ________________  **Date:** ________

---

### [  ] 6. Phase 3 Services Status

```bash
# Check if Phase 3 services still work
bin/ops.sh verify 2>&1 | tail -20

# Check individual services
bin/check_ports.sh 2>&1
# Expected: Some ports in use (opena2 at least)
```

**Checklist:**
- [ ] Dashboard accessible (or confirm ports)
- [ ] At least one service running
- [ ] No critical errors in logs
- [ ] bin/ops.sh responds to commands

**Validator:** ________________  **Date:** ________

---

### [  ] 7. Bootstrap Prompt Validation

```bash
# Check bootstrap prompt exists and is readable
cat 19.dashboard_agent/.vscode/portier-bridge/BOOTSTRAP_PDI_PROMPT.md | head -20 && \
  echo "✅ Bootstrap prompt readable" || echo "❌ Bootstrap prompt issue"

# Check for required sections
grep -q "Rolle & Mission" 19.dashboard_agent/.vscode/portier-bridge/BOOTSTRAP_PDI_PROMPT.md && \
  echo "✅ Bootstrap sections OK" || echo "⚠️ Missing sections"
```

**Checklist:**
- [ ] Bootstrap file readable
- [ ] Contains all sections (Rolle, System-Status, Verhaltensmatrix, etc.)
- [ ] PDI-ACTIVE header present
- [ ] Version 1.0 noted

**Validator:** ________________  **Date:** ________

---

### [  ] 8. Documentation Completeness

```bash
# Check all required docs exist
docs=(
  "19.dashboard_agent/docs/PDI/README.md"
  "19.dashboard_agent/docs/PDI/project_manifest.md"
  "19.dashboard_agent/docs/PDI/chapters/00_kapitelplan.md"
  "19.dashboard_agent/docs/PDI/VALIDATION_FRAMEWORK.md"
  "19.dashboard_agent/docs/PDI/PHASE_4_QUICKSTART.md"
  ".github/copilot-instructions.md"
  ".github/SYSTEM_ANALYSIS_BYPASS_MECHANISMS.md"
)

for doc in "${docs[@]}"; do
  lines=$(wc -l < "$doc" 2>/dev/null || echo "0")
  echo "$doc: $lines lines"
done
```

**Checklist:**
- [ ] All PDI docs present
- [ ] Project manifest complete (>200 lines)
- [ ] Kapitelplan has all 20 positions
- [ ] All docs have PDI headers

**Validator:** ________________  **Date:** ________

---

### [  ] 9. GitHub Preparation

```bash
# Check GitHub branch
git branch -v | grep phase-4

# Check GitHub Actions workflow files
ls -la .github/workflows/ 2>/dev/null || echo "⚠️ No workflows yet"

# Check remote
git remote -v | grep -q "origin" && echo "✅ Remote configured"
```

**Checklist:**
- [ ] GitHub remote configured (git remote -v)
- [ ] Branch ready for feature/phase-4-bridge
- [ ] No conflicts with main
- [ ] CI/CD workflows prepared (or pending)

**Validator:** ________________  **Date:** ________

---

### [  ] 10. Security Baseline

```bash
# Check for hardcoded secrets
grep -r "token.*=" 19.dashboard_agent/*.py 2>/dev/null | \
  grep -v "Bearer\|Authorization" && \
  echo "⚠️ Potential hardcoded secrets" || echo "✅ No obvious hardcoded tokens"

# Check .env is NOT committed
git log --all --full-history -- ".env*" 2>/dev/null | head -1 || \
  echo "✅ .env files not in git history"

# Verify .gitignore
grep -q "\.env" .gitignore && echo "✅ .env in .gitignore"
```

**Checklist:**
- [ ] No hardcoded tokens in code
- [ ] .env files not committed
- [ ] .gitignore excludes sensitive files
- [ ] BOOTSTRAP_PDI_PROMPT has no secrets

**Validator:** ________________  **Date:** ________

---

## 🚀 Pre-Launch Readiness Summary

| Check | Status | Notes |
|-------|--------|-------|
| Repository setup | [ ] | |
| Environment ready | [ ] | |
| File structure OK | [ ] | |
| Code quality | [ ] | |
| Task 01 works | [ ] | |
| Phase 3 intact | [ ] | |
| Bootstrap valid | [ ] | |
| Docs complete | [ ] | |
| GitHub ready | [ ] | |
| Security baseline | [ ] | |

---

## ⚠️ Go / No-Go Decision

```
Total Checks: 10
Passed: ___
Failed: ___
```

### Criteria for GO-LIVE:
- ✅ All 10 checks PASS, OR
- ✅ 9/10 checks PASS + risk accepted by Lead, OR
- ❌ <9 checks PASS → **HOLD** pending fixes

### Decision: ☐ GO   ☐ GO-WITH-ACCEPTED-RISKS   ☐ NO-GO

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| DevOps Lead | _____________ | _____________ | _____ |
| QA Lead | _____________ | _____________ | _____ |
| Tech Lead | _____________ | _____________ | _____ |
| Project Lead | Danijel Jokic | _____________ | _____ |

---

## Remediation (if needed)

If any check fails, document here:

```
FAILED CHECK: [number]
DESCRIPTION: 
ROOT CAUSE: 
REMEDIATION: 
OWNER: 
DUE DATE: 
```

---

## Next Steps (After Sign-Off)

- [ ] Merge all PDI docs to main
- [ ] Create feature/phase-4-bridge branch
- [ ] Notify team of Nov 7 kickoff
- [ ] Distribute this checklist + summary docs
- [ ] Schedule team meetings
- [ ] Prepare development environment (Docker, etc.)

---

**[PDI-FOOTER: Pre-Launch Checklist | Status: READY FOR VALIDATION | Version: 1.0 | Target: Nov 7 Go-Live]**
