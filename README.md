# SCTA – Self-Contextualizing Task Agent System

**Version:** 0.1.0  
**Status:** 🚀 **In Development** (Phases 1-3 complete, Phase 4+ queued)  
**License:** MIT

---

## 📖 Overview

SCTA is a **distributed orchestration system** for decomposing and executing complex tasks across multiple agents. Built with FastAPI, Redis, Postgres, and Qdrant, it provides:

- **Task Orchestration** – Intelligent routing and delegation
- **Adaptive Decomposition** – Break tasks into manageable subtasks
- **Distributed Execution** – Scale task processing across workers
- **State Management** – Persistent tracking of all operations
- **Observability** – Full tracing, logging, and monitoring

---

## 🎯 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Poetry (for dependency management)

### Setup (5 minutes)
```bash
# 1. Clone repository
git clone <repo-url>
cd Gesamtprojekt

# 2. Install dependencies
poetry install

# 3. Create configuration
cp .env.example .env
# Edit .env with your secrets (Telegram tokens, etc.)

# 4. Start infrastructure
docker compose up -d

# 5. Run migrations
poetry run alembic upgrade head

# 6. Start API (in new terminal)
poetry run uvicorn src.api.http.app:app --host 127.0.0.1 --port 3000
```

### Verify Installation
```bash
# Check health
curl http://localhost:3000/health

# Create a task
curl -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Sample Task","description":"Test task"}'
```

---

## 🏗️ Architecture

### System Components

```
┌──────────────┐
│  HTTP API    │  :3000  ← Client interface
│ (FastAPI)    │
└──────┬───────┘
       │
       ├──────────────────────┐
       │                      │
  ┌────▼────┐         ┌──────▼──────┐
  │Orchestr. │         │   Workers   │
  │ :5000    │         │  :5001-5002 │
  └────┬─────┘         └──────┬──────┘
       │                      │
  ┌────┴──────────────────────┴──┐
  │                               │
┌─▼───┐  ┌──────┐  ┌────┐  ┌───┐  │
│Redis│  │Psql  │  │Qdrt│  │OTel  │
│:6379│  │:5432 │  │:633│  │:4318  │
└──────┘  └──────┘  └────┘  └───┘   │
```

### Key Services

| Service | Port | Purpose |
|---------|------|---------|
| **API** | 3000 | REST interface for task management |
| **Orchestrator** | 5000 | Task routing & delegation |
| **Planner Worker** | 5001 | Task decomposition |
| **Executor Worker** | 5002 | Subtask execution |
| **Redis** | 6379 | Queue & caching |
| **Postgres** | 5432 | Persistent state |
| **Qdrant** | 6333 | Vector embeddings (optional) |

---

## 📚 Documentation

- **[Structure Runbook](docs/structure_runbook.md)** – System architecture, startup sequences, deployment
- **[Security Threat Model](docs/security_threat_model.md)** _(Coming in Phase 8)_
- **[Operations Runbook](docs/ops_runbook.md)** _(Coming in Phase 8)_
- **[API Reference](docs/api_reference.md)** _(Coming in Phase 6)_

---

## 🔐 Security

- **JWT Authentication** – Token-based API access
- **Secret Management** – Environment-based configuration
- **SAST Scanning** – Bandit + safety in CI/CD
- **Pre-commit Hooks** – Blocks secrets from git
- **Observability** – OpenTelemetry tracing for audit

### Secrets Management
Sensitive configuration goes in `.env` (git-ignored):
```bash
cp .env.example .env
# Edit with:
# - DASHBOARD_ADMIN_TOKEN
# - TELEGRAM_BOT_TOKEN (if used)
# - Database passwords
# - JWT secret keys
```

---

## 🚀 Development

### Install & Run Tests
```bash
# Install dev dependencies
poetry install --with dev

# Run tests (target: ≥85% coverage)
poetry run pytest -v --cov=src --cov-report=html

# Format code
poetry run black src/ tests/

# Lint
poetry run ruff check src/ tests/

# Type check
poetry run mypy src/ tests/
```

### Folder Structure
```
src/
├── agents/
│   ├── core_orchestrator/  ← Task routing logic
│   ├── worker_planner/     ← Task decomposition
│   └── worker_executor/    ← Task execution
├── api/
│   └── http/               ← FastAPI REST API
└── pkg/
    ├── shared/             ← Config, schemas, auth, queue, db
    └── models/             ← ORM models

tests/
├── test_api.py
├── test_orchestrator.py
├── test_workers.py
└── integration/
    └── test_e2e.py

docs/
├── structure_runbook.md    ← Architecture guide
├── ops_runbook.md
└── security_threat_model.md
```

---

## 🔄 Workflow Example

### Task Lifecycle
```
1. CREATE TASK
   Client → POST /tasks
   ↓
   API creates Task in Postgres, publishes to Redis

2. ROUTE TASK
   Orchestrator receives task.created event
   ↓
   Orchestrator queues decomposition job

3. DECOMPOSE
   Planner Worker receives decompose job
   ↓
   Planner breaks task into 5 subtasks

4. EXECUTE
   Executor Worker processes subtasks in parallel
   ↓
   Results collected and stored in Postgres

5. RETRIEVE
   Client → GET /tasks/{task_id}
   ↓
   API returns completed task with results
```

---

## 📊 Monitoring & Observability

### Health Check
```bash
curl http://localhost:3000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-09T12:00:00Z",
  "version": "0.1.0",
  "dependencies": {
    "postgres": "healthy",
    "redis": "healthy",
    "orchestrator": "healthy",
    "workers": ["planner", "executor"]
  }
}
```

### Logs
```bash
# Follow all logs
docker compose logs -f

# Specific service
docker compose logs -f scta-api
```

### Metrics (OpenTelemetry)
- Task processing latency
- Worker utilization
- Database query times
- Queue depth

---

## 🧪 Testing

### Test Coverage
Target: **≥85% coverage** (enforced by CI/CD)

### Running Tests
```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/test_api.py -v

# With coverage report
poetry run pytest --cov=src --cov-report=html
```

### Test Types
- **Unit Tests** – Individual module functionality
- **Integration Tests** – Database + Redis interactions
- **E2E Tests** – Full task workflows

---

## 🐳 Docker & Deployment

### Local Development
```bash
# Start all services
docker compose up -d

# Stop services
docker compose down

# Reset everything (WARNING: deletes data)
docker compose down -v
docker compose up -d
```

### Production Deployment
```bash
# Build image
docker build -t scta:latest .

# Run with environment
docker run -e POSTGRES_HOST=db.example.com \
           -e REDIS_HOST=redis.example.com \
           -p 3000:3000 \
           scta:latest
```

---

## 📦 Dependencies

### Production
- **fastapi** 0.121.1 – Web framework
- **pydantic** 2.12.4 – Validation
- **sqlalchemy** 2.0.23 – ORM
- **redis** 5.0.1 – Queue/cache
- **psycopg2** 2.9.9 – Postgres driver
- **celery** 5.3.4 – Distributed tasks
- **pyjwt** 2.8.1 – JWT tokens

### Development
- **pytest** 7.4.3 – Testing
- **black** 24.1.1 – Formatting
- **ruff** 0.2.0 – Linting
- **mypy** 1.7.1 – Type checking

See `pyproject.toml` for full list with pinned versions.

---

## 🤝 Contributing

### Code Standards
- Type hints on all functions (mypy strict)
- Docstrings for public APIs
- 85%+ test coverage
- Follow PEP 8 via black
- Use custom exception hierarchy

### PR Process
1. Create feature branch
2. Make changes with tests
3. Run `poetry run pytest --cov=src`
4. Run `poetry run ruff check`
5. Run `poetry run mypy`
6. Create PR with test results

---

## 📖 License

MIT License – See [LICENSE](LICENSE) file for details

---

## 🚦 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Architecture | ✅ Complete | Phases 1-3 done |
| Core Agents | ⏳ In Progress | Phase 4 queued |
| HTTP API | ⏳ In Progress | Phase 6 queued |
| Tests | ⏳ Planned | Phase 6 target: ≥85% |
| Docker | ⏳ Planned | Phase 7 |
| CI/CD | ⏳ Planned | Phase 8 |
| Security Model | ⏳ Planned | Phase 8 |
| Production Ready | ⏳ Q4 2025 | All phases targeted |

---

## 🆘 Troubleshooting

### Services won't start
```bash
# Check logs
docker compose logs scta-api

# Verify ports available
lsof -i :3000 :5000 :5432 :6379

# Reset infrastructure
docker compose down -v
docker compose up -d
```

### Database migrations fail
```bash
# Check migration status
docker compose exec scta-api alembic current

# Rollback last migration
docker compose exec scta-api alembic downgrade -1

# Run migrations fresh
docker compose exec scta-api alembic upgrade head
```

### Tests failing
```bash
# Run with verbose output
poetry run pytest -vv

# Run specific test
poetry run pytest tests/test_api.py::test_create_task -v

# Check coverage gaps
poetry run pytest --cov=src --cov-report=term-missing
```

---

## 📞 Support

- **Issues:** Create GitHub issue with logs
- **Questions:** Check [docs/](docs/) directory
- **Security:** Email security concern privately

---

## 🗺️ Roadmap

### Phase 4 (Completed Next Session)
- Core agent implementation
- Task routing logic

### Phase 5-6 (Following Sessions)
- API endpoints
- Test suite (≥85% coverage)

### Phase 7-8 (Later Sessions)
- Docker & CI/CD
- Security hardening
- Production documentation

### Phase 9 (Final)
- Integration testing
- Performance tuning
- Release preparation

---

**Last Updated:** 2025-11-09  
**Next Release:** Phase 4 (Core Agents)
