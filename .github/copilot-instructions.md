# GitHub Copilot Instructions — ELION Hyper-Dashboard (PORTIER 3.0)

This file provides **repository context, hard rules, and "how we do it here" conventions** for GitHub Copilot.

> **Authority stack (in order):**
> 1) `system_baseline.yaml` = **Single Source of Truth** (IDs, ports, paths, plans, secrets policy)
> 2) Gate layer (`bin/verify_baseline_and_discovery.sh`) = **PR blocker**
> 3) Docs (this file + `docs/*`) = guidance, but **must not contradict the baseline**

---

## 1) Project Overview

**ELION Hyper-Dashboard (PORTIER 3.0)** is a distributed multi-agent orchestration system built in Python. The project consists of **21 specialized agents** (`opena1` … `opena21`) that communicate via HTTP APIs and follow a strict message-flow architecture (**Option-2 pattern**).

**Key Features**
- Multi-agent orchestration with centralized coordination
- FastAPI-based microservices architecture
- Real-time status monitoring and SSE (Server-Sent Events)
- MCP (Model Context Protocol) tool server integration
- OpenTelemetry tracing support
- Strict port policy and security controls
- Append-only archive system with safepoints

**Target Audience**
System administrators, backend developers, AI/ML engineers working with agent-based systems.

---

## 2) Tech Stack

### Core Technologies
- **Language:** Python 3.12+ (configured for 3.13)
- **Web Framework:** FastAPI 0.121.1, Uvicorn 0.38.0
- **Data Validation:** Pydantic 2.12.4 (strict mode with `extra="forbid"`)
- **HTTP Clients:** httpx 0.25.2, aiohttp 3.9.1

### Data & Storage
- **Database:** SQLAlchemy 2.0.23, PostgreSQL (psycopg2-binary), Alembic migrations
- **Cache/Queue:** Redis 5.0.1, Celery 5.3.4
- **Vector DB:** Qdrant Client 1.7.0 (optional)

### Observability
- **Logging:** structlog 24.1.0, python-json-logger 2.0.7
- **Tracing:** OpenTelemetry API/SDK 1.21.0, OTLP exporter
- **Instrumentation:** FastAPI, SQLAlchemy, Redis auto-instrumentation

### Development Tools
- **Testing:** pytest 7.4.3, pytest-asyncio, pytest-cov (min 85% coverage)
- **Code Quality:** black (120 char line length), ruff 0.2.0, mypy 1.7.1, isort 5.13.2
- **Security:** bandit 1.7.5, safety 2.3.5
- **Utilities:** python-dotenv 1.0.0, typer 0.9.0, click 8.1.7

### Authentication & Security
- **JWT:** PyJWT 2.8.1
- **Bearer Token:** Used across all services via `Authorization: Bearer <token>`
- **Environment-based:** All secrets in `.env`, never hardcoded

---

## 3) Architecture & Coding Guidelines

### 3.1 Option-2 Message Flow (SACRED)
All requests must follow:

`OpenAI → opena1 → opena2 → kordp → Tool`

and return via:

`Tool → opena2 → opena1 → OpenAI`

**No shortcuts allowed**
- Never bypass **opena1** (coordinator) or **opena2** (archivator).
- Preserve safepoint logging in `archivp/` (append-only).

### 3.2 Services & Runtime Model
- **Stateless services:** each agent is independently startable (own `.venv`)
- **Mandatory endpoints:** every backend must implement `GET /health`
- **Structured logging:** use `structlog` and JSON-friendly log fields
- **Never fail silently:** always return structured JSON errors + correct HTTP codes

### 3.3 Code Style
- **Line length:** 120 chars (`black`)
- **Formatting:** `black --line-length 120 .`
- **Linting:** `ruff` (preferred) + `flake8` (legacy)
- **Type hints:** preferred
- **Imports:** `isort .`

### 3.4 Pydantic Models (Strict Mode)
All models must use Pydantic v2 with strict mode:

```python
from pydantic import BaseModel, ConfigDict

class YourModel(BaseModel):
    model_config = ConfigDict(extra="forbid")  # REQUIRED
    # fields...
```

---

## 4) Governance Rules (Non‑Negotiable)

### 4.1 Agent Identity Law (IMMUTABLE)
- Agent IDs are **exactly:** `opena1` … `opena21`
- No aliases, no renames, no "opena01", no "agent1".
- **kordp is a core service** but **NOT** an agent ID.

### 4.2 Every Agent Has Frontend + Backend (MANDATORY)
**Rule:** every agent provides:
- **Backend**: startable service entry (FastAPI/service/worker API)
- **Frontend**: minimal UI (admin/diagnostics)
  - If the UI is currently minimal, it still exists as:
    - `frontend/index.html` **or**
    - `templates/` + `static/` (FastAPI-style)

Recommended standard layout for `opena4`…`opena21`:
```
<agent_folder>/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

Core services keep their historical structure (don't "refactor for aesthetics").

---

## 5) Port Policy (IMMUTABLE)

- **Allowed range:** `12344–12399`
- **Forbidden:** `8080` (reserved for OpenWebUI UI)
- **No deviations**: ports are unique; collisions are a hard fail.

> **Port Authority:** if any port number in docs conflicts with `system_baseline.yaml`, **baseline wins**.

---

## 6) Repository Structure (Root Map)

```
Gesamtprojekt/
├── .github/
│   ├── copilot-instructions.md          # this file
│   ├── agents/                          # custom Copilot agents
│   └── workflows/
│       └── baseline-discovery-gate.yml  # PR gate workflow
├── 1.opena1&2_portier/                  # opena1, opena2, kordp + archivp
├── 2.opena3_openwebui/
├── 3.opena4_telegram/
├── 4.opena5_vscode/
├── 5.opena6_browser/
├── 6.opena7_email/
├── 7.opena8_whatsapp/
├── 8.opena9_telephone/
├── 9.opena10_call_tracking/
├── 10.opena11_unlock/
├── 11.opena12_social_media/
├── 12.opena13_influencer/
├── 13.opena14_calendar/
├── 14.opena15_html/
├── 15.opena16_shop/
├── 16.opena17_homepagecreator/
├── 17.opena18_CMR/
├── 18.opena19_Aktien&Crypto/
├── 19.opena20_dashboard_agent/
├── 20.opena21_workflow/
├── bin/                                 # root wrapper scripts
├── scripts/                             # gate scripts, registry, tools
├── docs/
├── logs/
├── src/
├── artifacts/                            # deterministic gate outputs
├── pyproject.toml
└── system_baseline.yaml                  # SSoT (IDs/ports/paths)
```

---

## 7) Ports & Roles (Reference Table)

This is a **human-readable reference**. The **baseline** remains the authority.

| ID | Service | Port | Plan |
|---|---:|---:|---|
| opena1 | Koordinator | 12344 | core |
| opena2 | Archivar | 12345 | core |
| kordp | Gateway / Tool-Resolver (core service, not an agent) | 12344 | core-service |
| opena3 | OpenWebUI Bridge | 12347 | basic |
| opena4 | Telegram | 12346 | basic |
| opena20 | Dashboard | 12349 | system |
| opena7 | E-Mail | 12350 | basic |
| opena6 | Browser | 12351 | premium |
| opena8 | WhatsApp | 12353 | pro |
| opena9 | Telefon | 12354 | premium |
| opena10 | Call Tracking | 12355 | ultimum |
| opena11 | Unlock/Auth | 12356 | basic |
| opena12 | Social Media | 12357 | pro |
| opena13 | Influencer | 12358 | ultimum |
| opena14 | Kalender | 12359 | pro |
| opena15 | HTML Generator | 12360 | premium |
| opena16 | Shop | 12361 | premium |
| opena17 | Homepage Creator | 12362 | ultimum |
| opena18 | CRM | 12363 | pro |
| opena19 | Finanzen | 12364 | ultimum |
| opena5 | VSCode | 12365 | ultimum |
| opena21 | Workflow | 12368 | system |

---

## 8) Baseline (SSoT) — Required Schema

The gate scripts (`scripts/validate_baseline.py` and `scripts/discover_agents.py`) expect this **canonical baseline schema**:

- `version` (string)
- `generated_at` (string, ISO-ish)
- `port_policy.allowed_range` (string `"12344-12399"`)
- `port_policy.forbidden_ports` (list of ints, e.g. `[8080]`)
- `domain_policy.primary_domain` (string)
- `agents` (list; each agent requires **all** keys below)
  - `id`, `port`, `name`, `role`, `plan`, `visibility`, `folder_path`, `description`
- `plans` (dict; each plan has `name`, `description`, `agents`)
- `core_agents` / `system_agents` (list of strings)
- optional: `secrets` policy block (see below)

**Important:** `kordp` is **not** listed under `agents:` in `system_baseline.yaml`.

### 8.1 Secrets Policy (Baseline Optional, but Supported)
Baseline may define:

- `secrets.secrets_file`
- `secrets.required_secrets`
- `secrets.optional_secrets`
- `secrets.validation.min_token_length`
- `secrets.validation.allowed_env_files`

**Hard rule:** never hardcode secrets in YAML, code, or docs. Only `$VAR` or `${VAR}` references.

---

## 9) Gate Layer (Baseline + Discovery) — PR Blocker

### 9.1 Single Entry Point (Dev/Ops/CI)
Run:

```bash
./bin/verify_baseline_and_discovery.sh
```

What it does (deterministic + fail-fast):
1) Validates `system_baseline.yaml` in **CI mode**
2) Runs deterministic agent discovery
3) Writes deterministic artifacts under `artifacts/`

### 9.2 Files (Must Exist)
- `bin/verify_baseline_and_discovery.sh`
- `scripts/validate_baseline.py`  *(PyYAML-only, CI-safe; no .env required)*
- `scripts/discover_agents.py`    *(deterministic inventory; optional strict paths)*
- `.github/workflows/baseline-discovery-gate.yml` *(CI job: installs PyYAML only)*

### 9.3 Artifacts (Always Produced)
- `artifacts/Baseline_validation.json` (baseline schema validation result)
- `artifacts/Agent_discovery.json` (folder inventory + hashes + findings)

**Determinism rule:** no timestamps in artifacts that are used as stable inputs.
(If you add timestamps for audit, keep them out of hash inputs.)

### 9.4 Exit Codes
- `0` = OK
- `1` = Gate failure (wrapper / discovery failure)
- `2` = Baseline schema validation failure (validator)

---

## 10) Development Workflows

### Initial Setup
```bash
make venv && make deps
cp mcp_server/.env.example .env
# Edit .env with your keys/tokens
```

### Start Stack
```bash
./bin/ops.sh start
./bin/ops.sh agents:register
./bin/ops.sh status | jq .
```

### Stop Stack
```bash
./bin/ops.sh stop
```

### Verify Health
```bash
./bin/ops.sh verify
./bin/check_ports.sh
```

### Logs
```bash
./bin/ops.sh logs
tail -f logs/opena1.nohup.log
```

### Tests
```bash
pytest -v --cov=src --cov-report=html
pytest tests/test_service_folders.py -v
pytest -v -n auto
```

### Code Quality
```bash
black --line-length 120 .
flake8 --max-line-length=120 --ignore=E203,W503
isort .
mypy src/
bandit -r src/
```

### Tracing (OpenTelemetry)
```bash
./bin/start_tracing_collector.sh
python3 tracing/check_tracing.py
# .env:
# OTEL_ENABLED=true
# OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
# OTEL_SERVICE_NAME=<agent_name>
```

---

## 11) HTML Frontend Conventions

### 11.1 Minimal HTML Skeleton (Recommended)
Use this when a frontend folder exists but needs a clean entry page:

```html
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="PORTIER 3.0 Agent UI" />
  <title>PORTIER Agent UI</title>
  <link rel="stylesheet" href="./style.css" />
</head>
<body>
  <header>
    <nav aria-label="Hauptnavigation">
      <a href="../../frontend/sitemap.html">Sitemap</a>
      <a href="#status">Status</a>
      <a href="#logs">Logs</a>
      <a href="#actions">Actions</a>
    </nav>
  </header>

  <main id="main">
    <h1 id="title">Agent UI</h1>

    <section id="status">
      <h2>Status</h2>
      <pre id="health">loading…</pre>
    </section>

    <section id="actions">
      <h2>Actions</h2>
      <button id="btnRefresh">Refresh</button>
    </section>
  </main>

  <footer>
    <small>© <span id="year"></span> ELION / PORTIER</small>
  </footer>

  <script src="./config.js"></script>
  <script src="./app.js"></script>
  <script>
    document.getElementById("year").textContent = String(new Date().getFullYear());
  </script>
</body>
</html>
```

### 11.2 Frontend `config.js` (Baseline-Aligned)
**Never hardcode ports in JS.**
Prefer environment injection or server-side templating. For local prototypes only, keep a *single* place:

```js
// config.js (prototype only)
// In production: inject via template or env->build step.
window.PORTIER_UI = {
  agentId: "openaX",
  baseUrl: "http://127.0.0.1:123XX"
};
```

---

## 12) HTML Sitemap / Navigation Map (Frontend)

### 12.1 Human Map (What exists / where to click)
- Root Dashboard UI: `19.opena20_dashboard_agent/`
- Per Agent UI (standard):
  - `*/frontend/index.html` **or**
  - `templates/*.html` + `static/*`

### 12.2 `frontend/sitemap.html` (Repo‑Relative Links)
Create a small navigation page at `frontend/sitemap.html` (repo root-level `frontend/` folder):

```html
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PORTIER 3.0 — UI Sitemap</title>
</head>
<body>
  <h1>PORTIER 3.0 — UI Sitemap</h1>
  <p>Repo-relative Links (für Dev/Review). In Produktion routet das Dashboard (opena20) die UIs.</p>

  <h2>Core</h2>
  <ul>
    <li><a href="../1.opena1&2_portier/opena1/">opena1 (Coordinator)</a></li>
    <li><a href="../1.opena1&2_portier/opena2/">opena2 (Archivator)</a></li>
    <li><a href="../1.opena1&2_portier/kordp/">kordp (Gateway / Tool Resolver)</a></li>
  </ul>

  <h2>Agents opena3..opena21</h2>
  <ul>
    <li><a href="../2.opena3_openwebui/frontend/index.html">opena3</a></li>
    <li><a href="../3.opena4_telegram/frontend/index.html">opena4</a></li>
    <li><a href="../4.opena5_vscode/frontend/index.html">opena5</a></li>
    <li><a href="../5.opena6_browser/frontend/index.html">opena6</a></li>
    <li><a href="../6.opena7_email/frontend/index.html">opena7</a></li>
    <li><a href="../7.opena8_whatsapp/frontend/index.html">opena8</a></li>
    <li><a href="../8.opena9_telephone/frontend/index.html">opena9</a></li>
    <li><a href="../9.opena10_call_tracking/frontend/index.html">opena10</a></li>
    <li><a href="../10.opena11_unlock/frontend/index.html">opena11</a></li>
    <li><a href="../11.opena12_social_media/frontend/index.html">opena12</a></li>
    <li><a href="../12.opena13_influencer/frontend/index.html">opena13</a></li>
    <li><a href="../13.opena14_calendar/frontend/index.html">opena14</a></li>
    <li><a href="../14.opena15_html/frontend/index.html">opena15</a></li>
    <li><a href="../15.opena16_shop/frontend/index.html">opena16</a></li>
    <li><a href="../16.opena17_homepagecreator/frontend/index.html">opena17</a></li>
    <li><a href="../17.opena18_CMR/frontend/index.html">opena18</a></li>
    <li><a href="../18.opena19_Aktien&Crypto/frontend/index.html">opena19</a></li>
    <li><a href="../19.opena20_dashboard_agent/templates/dashboard.html">opena20 (Dashboard)</a></li>
    <li><a href="../20.opena21_workflow/frontend/index.html">opena21</a></li>
  </ul>
</body>
</html>
```

---

## 13) Important Constraints

### NEVER Do These
- ❌ Create new top-level agent folders without explicit approval
- ❌ Bind internal services to port **8080**
- ❌ Use ports outside `12344–12399`
- ❌ Bypass opena1/opena2 in message flow
- ❌ Modify or delete safepoint archives
- ❌ Hardcode API keys/secrets
- ❌ Change agent IDs (`opena1..opena21` are fixed)
- ❌ Source `.env` directly in bash scripts

### ALWAYS Do These
- ✅ Follow Option-2 message flow
- ✅ `extra="forbid"` in Pydantic models
- ✅ Implement `GET /health` in every backend
- ✅ Structured logging via `structlog`
- ✅ Validate bearer tokens on protected endpoints
- ✅ Run tests before committing
- ✅ Check `system_baseline.yaml` and `bin/ops.sh` for ports
- ✅ Keep `.env` out of git; use `.env.example`

---

## 14) Resources

### Documentation
- `docs/OPERATIONS.md`
- `docs/README_STACK_START.md`
- `docs/ARCHITECTURE.md`
- `docs/OPENWEBUI_INTEGRATION.md`
- `docs/TROUBLESHOOTING.md`

### External Links
- FastAPI: https://fastapi.tiangolo.com/
- Pydantic v2: https://docs.pydantic.dev/latest/
- OpenTelemetry Python: https://opentelemetry.io/docs/languages/python/
- Structlog: https://www.structlog.org/

---

## 15) Legacy / Audit (Do Not Use as Authority)

The following older baseline formatting appeared in earlier drafts (kept here **only** for audit history).
**Do not implement tooling against it.** The gate scripts use the canonical schema from section **8**.

```yaml
# DEPRECATED (audit only)
port_policy:
  allow_range:
    min: 12344
    max: 12399
```

---

**Version:** 3.0
**Last Updated:** 2026-01-04
**Maintainer:** ELION Team
**Status:** ✅ Production-Ready
