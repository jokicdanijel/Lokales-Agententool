# GitHub Copilot Instructions - ELION Hyper-Dashboard

This file provides context and guidelines for GitHub Copilot when working in this repository.

## 1. Project Overview

**ELION Hyper-Dashboard (PORTIER 3.0)** is a distributed multi-agent orchestration system built in Python. The project consists of 21 specialized agents ("opena1" through "opena21") that communicate via HTTP APIs and follow a strict message flow architecture (Option-2 pattern).

**Key Features:**

- Multi-agent orchestration with centralized coordination
- FastAPI-based microservices architecture
- Real-time status monitoring and SSE (Server-Sent Events)
- MCP (Model Context Protocol) tool server integration
- OpenTelemetry tracing support
- Strict port policy and security controls
- Append-only archive system with safepoints

**Target Audience:** System administrators, backend developers, AI/ML engineers working with agent-based systems.

## 2. Tech Stack

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

## 3. Coding Guidelines

### Architecture Principles

- **Option-2 Message Flow (SACRED):** All requests must follow: `OpenAI → opena1 → opena2 → kordp → Tool` and return via: `Tool → opena2 → opena1 → OpenAI`
- **No shortcuts allowed:** Never bypass opena1 (coordinator) or opena2 (archivator)
- **Stateless services:** Each agent is independently startable with its own `.venv`

### Code Style

- **Line length:** 120 characters (black, flake8)
- **Python version:** Target 3.12+ features
- **Formatting:** Run `black --line-length 120 .` before committing
- **Linting:** `flake8 --max-line-length=120 --ignore=E203,W503`
- **Type hints:** Preferred but not strictly required
- **Imports:** Use `isort` for consistent import ordering

### Pydantic Models

All data models must use Pydantic v2 with strict mode:

```python
from pydantic import BaseModel, ConfigDict

class YourModel(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Strict mode - REQUIRED
    # fields...
```

### Port Policy (IMMUTABLE)

- **Backend services:** ONLY ports 12344–12399 allowed
- **Port 8080:** FORBIDDEN for internal services (reserved for OpenWebUI UI)
- **Enforcement:** Use `PORT_POLICY_MIDDLEWARE` in all FastAPI apps
- **Port mapping:** See `bin/ops.sh` AGENTS array (source of truth)

### Security Rules

- **Never hardcode secrets** - Always use environment variables
- **Never commit `.env`** - Use `.env.example` templates
- **Token validation:** All API endpoints must verify `BEARER_TOKEN` or `DASHBOARD_ADMIN_TOKEN`
- **Secret masking:** Use `SafepointWriter30.SECRET_KEYS` pattern for logging

### Error Handling

- Always return structured JSON error responses
- Use appropriate HTTP status codes
- Log errors at ERROR/WARNING level with structlog
- Never fail silently

### Testing

- Write tests in `tests/` directory
- Use descriptive module docstrings
- Include `sys.exit()` for standalone execution
- Maintain minimum 85% code coverage (configured in pyproject.toml)
- Run: `pytest -v --cov=src --cov-report=html`

## 4. Project Structure

### Key Directories

```
├── bin/                          # Operational scripts
│   └── ops.sh                   # Main stack controller (START HERE)
├── src/                         # Core implementation
│   ├── pkg/                     # Shared packages
│   │   ├── main_dashboard.py   # Dashboard service (full)
│   │   └── agent_registry.py   # Agent dispatch logic
│   └── services/                # Individual service implementations
├── mcp_server/                  # MCP Tool Server (port 12398)
│   ├── mcp_tool_server.py      # JSON-RPC endpoint
│   └── logs/mcp_audit.jsonl    # Audit trail
├── scripts/                     # Wrapper scripts for CI/CD
│   └── register_agents.py      # Agent registration
├── docs/                        # Documentation
│   ├── OPERATIONS.md           # Runtime commands reference
│   ├── README_STACK_START.md   # Quick start guide
│   └── ARCHITECTURE.md         # System design
├── logs/                        # Runtime logs (*.nohup.log)
├── tests/                       # Test suite
├── .github/                     # GitHub configuration
│   ├── copilot-instructions.md # This file
│   ├── agents/                 # Custom Copilot agents
│   └── workflows/              # CI/CD pipelines
└── archivp/                     # Append-only archive (safepoints)
    └── YYYY/MM/DD/             # Date-based structure
```

### Agent Folders (21 total - IMMUTABLE)

Each agent has its own folder with standardized structure:

- `1.opena1&2_portier/` - Coordinator (12344) + Archivator (12345)
- `2.opena3_openwebui/` - OpenWebUI Bridge (12347)
- `3.opena4_telegram/` - Telegram Agent (12348)
- `4.opena5_vscode/` through `20.opena21_workflow/` - Specialized agents
- `19.opena20_dashboard_agent/` - Dashboard Backend (12349) - NOTE: opena20 IS the Dashboard service

**NEVER create new top-level agent folders without explicit approval.**

### Important Files

- `bin/ops.sh` - Stack orchestrator (ports, start order, health checks)
- `.env` - Environment variables (created from `mcp_server/.env.example`)
- `pyproject.toml` - Python dependencies and tool configuration
- `Makefile` - Infrastructure targets (venv, scan, verify, release)
- `requirements.txt` - Pip dependencies (fallback)

## 5. Development Workflows

### Initial Setup

```bash
# Create virtual environment and install dependencies
make venv && make deps

# Copy environment template and configure secrets
cp mcp_server/.env.example .env
# Edit .env with your API keys and tokens
```

### Starting the Stack

```bash
# Start all agents in correct order
./bin/ops.sh start

# Register agents with dashboard
./bin/ops.sh agents:register

# Check status
./bin/ops.sh status | jq .
```

### Stopping the Stack

```bash
./bin/ops.sh stop
```

### Verifying Health

```bash
# Check all health endpoints
./bin/ops.sh verify

# Check specific ports
./bin/check_ports.sh
```

### Viewing Logs

```bash
# Show all logs
./bin/ops.sh logs

# Follow specific agent log
tail -f logs/opena1.nohup.log
```

### Running Tests

```bash
# Run all tests with coverage
pytest -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_service_folders.py -v

# Run with parallel execution
pytest -v -n auto
```

### Code Quality Checks

```bash
# Format code
black --line-length 120 .

# Lint
flake8 --max-line-length=120 --ignore=E203,W503

# Sort imports
isort .

# Type checking
mypy src/

# Security scan
bandit -r src/
```

### Project Structure Management

```bash
# Validate structure (dry-run)
make dry

# Apply structure normalization
make apply

# Verify consistency
make verify

# Scan project for documentation
make scan  # Generates project_map/
```

### Tracing (OpenTelemetry)

```bash
# Start local OTLP collector
./bin/start_tracing_collector.sh

# Check tracing status
python3 tracing/check_tracing.py

# Configure in .env:
# OTEL_ENABLED=true
# OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
# OTEL_SERVICE_NAME=<agent_name>
```

## 6. Resources

### Documentation

- **Operations Guide:** [`docs/OPERATIONS.md`](../docs/OPERATIONS.md)
- **Stack Start:** [`docs/README_STACK_START.md`](../docs/README_STACK_START.md)
- **Architecture:** [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- **OpenWebUI Integration:** [`docs/OPENWEBUI_INTEGRATION.md`](../docs/OPENWEBUI_INTEGRATION.md)
- **Troubleshooting:** [`docs/TROUBLESHOOTING.md`](../docs/TROUBLESHOOTING.md)

### Configuration Reference

- **Copilot Config:** [`.copilot-config`](../.copilot-config) - Detailed architecture (German)
- **System Instructions:** [`.copilot-system-instructions`](../.copilot-system-instructions) - System constraints
- **Protection Rules:** [`.copilot-instructions`](../.copilot-instructions) - Port mappings and restrictions

### External Links

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Pydantic V2:** https://docs.pydantic.dev/latest/
- **OpenTelemetry Python:** https://opentelemetry.io/docs/languages/python/
- **Structlog:** https://www.structlog.org/

### GitHub Resources

- **Workflows:** `.github/workflows/` - CI/CD automation
- **Custom Agents:** `.github/agents/` - Specialized Copilot agents
  - `HTML.agent.md` - HTML/frontend assistance
  - `Plan.agent.md` - Multi-step planning (research & outlining)
  - `TeleAGENT.agent.md` - Telegram integration
  - `LocalServerBrowserAgent` - Browser automation and local testing

## 7. Common Tasks

### Adding a New Endpoint

1. Define Pydantic models with `extra="forbid"`
2. Implement handler in appropriate agent's `main.py`
3. Add authentication/authorization checks
4. Include in agent's router with proper HTTP method
5. Update health check if needed
6. Add tests for new endpoint
7. Document in relevant `docs/*.md`

### Modifying Message Flow

⚠️ **EXTREME CAUTION REQUIRED**

- Option-2 flow is sacred: opena1 → opena2 → kordp → Tool
- Any changes require architecture review
- Must preserve safepoint logging in archivp
- Never bypass coordinator or archivator

### Debugging Agent Communication

```bash
# Check agent is running
curl http://127.0.0.1:<PORT>/health

# Check dashboard can reach agent
./bin/ops.sh status | jq '.agents[] | select(.id=="opena<N>")'

# Review agent logs
tail -f logs/opena<N>.nohup.log

# Check safepoints for message flow
ls -lrt archivp/$(date +%Y/%m/%d)/
```

### Working with Secrets

1. Never commit secrets to git
2. Always use `.env` file (listed in `.gitignore`)
3. Reference via `os.getenv("KEY_NAME")`
4. Use `SafepointWriter30.SECRET_KEYS` for masking in logs
5. Whitelist environment reads in `bin/ops.sh`

## 8. Important Constraints

### NEVER Do These

- ❌ Create new top-level agent folders
- ❌ Bind services to port 8080
- ❌ Use ports outside 12344-12399 range
- ❌ Bypass opena1 or opena2 in message flow
- ❌ Modify or delete safepoint archives
- ❌ Hardcode API keys or secrets
- ❌ Change agent names (opena1-opena21 are fixed)
- ❌ Source `.env` file directly in bash scripts

### ALWAYS Do These

- ✅ Follow Option-2 message flow
- ✅ Use `extra="forbid"` in Pydantic models
- ✅ Implement `GET /health` on all services
- ✅ Log with structlog for structured output
- ✅ Validate bearer tokens on protected endpoints
- ✅ Run tests before committing
- ✅ Check `bin/ops.sh` for port assignments
- ✅ Use isolated `.venv` per agent

---

**Version:** 3.0
**Last Updated:** 2025-12-22
**Maintainer:** ELION Team
**Status:** ✅ Production-Ready

For questions or clarifications, refer to [`docs/OPERATIONS.md`](../docs/OPERATIONS.md) or the existing codebase patterns.
