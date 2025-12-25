# opena7 — CI/CD Pipeline Documentation

## 🚀 GitHub Actions Workflow

opena7 hat ein **vollautomatisches CI/CD-System** via GitHub Actions. Das Workflow lädt automatisch bei jedem Push/PR.

### Workflow-Stages

```
┌─────────────────────────────────────────────────────────┐
│              opena7 CI/CD Pipeline                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. LINT (Parallel)          4. API TESTS              │
│     ├─ Black                 ├─ Health check           │
│     ├─ Ruff                  ├─ Status endpoint        │
│     └─ Pre-commit            ├─ Info endpoint          │
│                              └─ UI loading             │
│  2. PYTHON CHECK             5. SECURITY SCAN          │
│     ├─ Syntax                └─ Trivy vulnerability    │
│     ├─ Imports               6. CODE METRICS           │
│     └─ Type hints            7. DEPLOYMENT READY       │
│                              8. SUMMARY REPORT         │
│  3. DOCKER BUILD                                       │
│     └─ Test image                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### ✅ Job-Beschreibungen

#### 1️⃣ **LINT** — Code Quality

```yaml
- Black formatting
- Ruff linting
- Pre-commit hooks (isort, trailing-whitespace, end-of-file-fixer)
```

**Trigger:** Every push/PR
**Timeout:** 2 min
**Status:** Must pass before other jobs

#### 2️⃣ **PYTHON-CHECK** — Syntax & Dependencies

```yaml
- Python 3.12 syntax validation
- Import check (from app.main import app)
- Requirements.txt validation
```

**Depends on:** LINT passed
**Timeout:** 1 min

#### 3️⃣ **DOCKER-BUILD** — Container Build Test

```bash
docker-compose build --no-cache opena7
docker run --rm opena7_opena7 python -c "from app.main import app"
```

**Depends on:** LINT + PYTHON-CHECK
**Build time:** ~2 min
**Output:** Docker image size verification

#### 4️⃣ **API-TEST** — Live Endpoint Testing

```yaml
- Start opena7 container (port 12352)
- Test GET /health
- Test GET /api/status
- Test GET /api/info (dashboard integration)
- Test GET / (HTML UI loading)
- Test GET /workflows
- Cleanup
```

**Depends on:** DOCKER-BUILD
**Duration:** ~30 sec
**Critical:** All endpoints must respond 200 OK

#### 5️⃣ **SECURITY** — Vulnerability Scan

```bash
trivy scan:filesystem 6.opena7_email
# Outputs SARIF for GitHub Security tab
```

**Non-blocking:** Runs parallel, results in GitHub Security
**Scanning:** Base image, Python packages

#### 6️⃣ **METRICS** — Code Analysis

```bash
wc -l 6.opena7_email/app/main.py
wc -l 6.opena7_email/app/html/index.html
wc -l 6.opena7_email/app/static/app.js
wc -l 6.opena7_email/app/static/app.css
```

**Output:** LOC (Lines of Code) report
**Purpose:** Track codebase growth

#### 7️⃣ **PUBLISH** — Docker Registry (main branch only)

```yaml
Only runs on:
  - Branch: main
  - Event: push (not PR)
Requires: All tests passed

Actions:
  - Extract version from app/main.py
  - Build production image
  - Tag: opena7:6.0.0 + opena7:latest
  - Image size check
```

#### 8️⃣ **DEPLOY-READY** — Deployment Report

```yaml
Generates: Deployment readiness report
Includes:
  - All verified endpoints
  - Configuration (port, host, version)
  - Status badge: READY FOR PRODUCTION
Posts comment on PR (if applicable)
```

---

## 📋 Workflow Trigger-Bedingungen

### Automatic Trigger

```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - "6.opena7_email/**"
      - "dist/opena7/**"
      - ".github/workflows/opena7.yml"
  pull_request:
    branches: [main]
    paths:
      - "6.opena7_email/**"
```

**Heißt:** Workflow lädt NUR, wenn relevante Dateien geändert werden!

---

## 🔍 Überwachung & Status

### GitHub Status Checks

Jeder Commit zeigt visuelle Status-Indicators:

```
✅ lint — Code Quality (Black, Ruff, Pre-commit)
✅ python-check — Python Syntax & Imports
✅ docker-build — Docker Build Test
✅ api-test — API Endpoint Tests
✅ security — Security Scan (Trivy)
✅ metrics — Code Metrics
✅ deploy-ready — Deployment Readiness
```

### PR-Status

Wenn PR offen: Workflow-Status wird in PR-Timeline angezeigt.
Wenn Test fehlschlägt: **PR kann nicht gemergt werden** (branch protection).

### Release-Tracking

- **main branch:** Automatischer Docker-Build & Publish
- **develop branch:** Tests nur, kein Docker-Publish
- **PRs:** Tests + Security Scan

---

## 🛠️ Lokal testen (vor Push)

```bash
# Pre-commit hooks lokal laufen lassen
pre-commit run --all-files

# Docker bauen (lokal)
cd dist/opena7
docker-compose build opena7

# API Tests manuell
docker-compose up -d opena7
sleep 5
curl http://localhost:12352/health | jq
docker-compose down
```

---

## 📊 Beispiel: Erfolgreicher Run

```
├─ PASSED: lint (2min)
│  └─ Black formatting ✅
│  └─ Ruff checks ✅
│  └─ Pre-commit hooks ✅
├─ PASSED: python-check (1min)
│  └─ Syntax validation ✅
│  └─ Import check ✅
├─ PASSED: docker-build (2min)
│  └─ Image size: 356 MB ✅
├─ PASSED: api-test (30sec)
│  └─ /health → 200 OK ✅
│  └─ /api/status → 200 OK ✅
│  └─ /api/info → 200 OK ✅
│  └─ / (UI) → 200 OK ✅
├─ PASSED: security (1min)
│  └─ No critical vulnerabilities ✅
├─ PASSED: metrics
│  └─ LOC report ✅
├─ PASSED: publish (on main)
│  └─ Image tagged opena7:6.0.0 ✅
└─ SUMMARY
   └─ All checks passed ✅ READY FOR PRODUCTION
```

---

## ⚠️ Häufige Fehler & Lösungen

### ❌ "lint failed: Black formatting"

```bash
# Local fix:
black 6.opena7_email/app/main.py
git add .
git commit -m "style: Black formatting"
git push
```

### ❌ "api-test failed: /health → 404"

```bash
# Check logs:
docker-compose logs opena7 | tail -20

# Likely: Python import error
# Solution: Check app/main.py syntax
python -m py_compile 6.opena7_email/app/main.py
```

### ❌ "docker-build failed: no such file"

```bash
# Check file paths in Dockerfile:
cat dist/opena7/Dockerfile | grep COPY

# Make sure:
# - app/main.py exists
# - app/html/ exists
# - requirements.txt exists
```

### ❌ "security: Trivy vulnerability found"

```bash
# Review in GitHub Security tab:
# https://github.com/YOUR_REPO/security/code-scanning

# Update packages:
pip-compile requirements.txt
```

---

## 🔐 Secrets & Environment

### GitHub Secrets (optional for future)

```yaml
# Not used in current setup, but ready for:
DOCKER_USERNAME: <your-docker-username>
DOCKER_TOKEN: <your-docker-token>
# For: docker login + push to registry
```

### Environment Variables (in workflow)

```yaml
REGISTRY: docker.io
IMAGE_NAME: opena7
DOCKER_BUILDKIT: 1 # Faster builds
```

---

## 📈 Dashboard Integration

opena7 ist **opena20-kompatibel**:

```
GET /api/info
→ Returns agent metadata
→ Dashboard can auto-discover & monitor
```

**Monitoring via dashboard:**

1. opena20 polls `/api/info` → finds opena7
2. opena20 polls `/health` → checks status
3. opena20 shows status in UI
4. opena20 logs all requests

---

## 🚀 Deployment aus CI/CD

### Option 1: Manual Deploy (nach PR merge)

```bash
cd dist/opena7
docker-compose pull  # Latest image
docker-compose up -d opena7
```

### Option 2: Automated Deploy (future)

Add step to workflow:

```yaml
deploy:
  needs: publish
  runs-on: [self-hosted] # Your server
  steps:
    - run: |
        cd /app/opena7
        docker-compose pull
        docker-compose up -d opena7
```

---

## 📞 Support & Debugging

### Workflow Logs einsehen

1. Push machen
2. GitHub → Actions tab
3. Workflow "opena7 CI/CD Pipeline" klicken
4. Job auswählen → Logs anschauen

### Lokal debuggen

```bash
# Run specific test locally:
python -m pytest tests/

# Or manually:
python -c "from app.main import app; print(app.routes)"
```

---

**Status: ✅ PRODUCTION READY**

Workflow ist live und automatisiert! 🎉
