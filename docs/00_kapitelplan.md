# [PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]

# Kapitelplan & Nächste 20 Positionen (Phase 4)

**Copilot Bridge + VS Code Integration – Fully Executable Positions**

**Datum:** 2025-11-06
**Total Tasks:** 20 | **Target Completion:** Week 4
**Dependencies:** Phase 3 Complete ✅

---

## 📋 Struktur

Jede Position enthält:

- **Ziel:** Was wird gebaut
- **Scope:** Umfang + Grenzen
- **Dependencies:** Was vorher fertig sein muss
- **Akzeptanzkriterien:** Definition of Done (DoD)
- **Deliverables:** Dateien + Artefakte
- **Schätzung:** Aufwand (Tage)

---

## ✅ POSITION 01: Bridge-API Auth & RBAC

**Ziel:** Bearer-Token-basierte Authentifizierung für `copilot_bridge` (Port 12351) mit rollenbasierter Zugriffskontrolle (RBAC).

**Scope:**

- Endpoint: `POST /api/auth/token` (Rollen: `writer`, `reader`, `admin`)
- Middleware: Token validation auf allen Endpoints
- Rollen-Mapping: reader (nur GET), writer (POST/PUT), admin (alles)

**Dependencies:**

- Phase 3 complete (Dashboard auth pattern known)
- `security.py` existiert

**Akzeptanzkriterien:**

- [ ] Request ohne Token → `401 Unauthorized`
- [ ] Request mit ungültigem Token → `403 Forbidden`
- [ ] Request mit `reader` Token auf `/enqueue` → `403 Forbidden`
- [ ] Request mit `writer` Token auf `/enqueue` → `200 OK`
- [ ] Request mit `admin` Token auf alles → `200 OK`
- [ ] Token-Validation in `<1ms` (cached)

**Deliverables:**

- `bridge_auth.py` – Auth module (100 lines)
- `test_auth.py` – Pytest suite (50 lines)
- Updated `copilot_bridge.py` – Middleware hooks
- Updated `.env` – Auth token seeds (reader, writer, admin)

**Schätzung:** 1 Tag

---

## ✅ POSITION 02: Bridge OpenAPI Schema

**Ziel:** Generate OpenAPI 3.1 schema + Markdown-Referenz für Bridge API.

**Scope:**

- Endpoint: `GET /openapi.json` (auto-generated from FastAPI)
- Markdown docs: `bridge_api.md` (handwritten reference)
- Schema validation: All endpoints documented

**Dependencies:**

- Position 01 (endpoints defined)

**Akzeptanzkriterien:**

- [ ] `/openapi.json` serves valid OpenAPI 3.1
- [ ] All endpoints documented (method, params, responses)
- [ ] Example requests in Markdown (cURL + Python)
- [ ] Error codes documented (400, 401, 403, 429, 500)
- [ ] Schema validates with `openapi-spec-validator`

**Deliverables:**

- `bridge_schema.json` – Generated from Starlette/FastAPI
- `docs/bridge_api.md` – Markdown reference (200 lines)
- `tests/test_openapi.py` – Schema validation tests

**Schätzung:** 1 Tag

---

## ✅ POSITION 03: Queue-Monitor im Dashboard UI

**Ziel:** Live-Anzeige der Bridge-Queue im Dashboard UI + Manual Sync-Button.

**Scope:**

- New endpoint: `GET /api/bridge/status` (Dashboard API)
- UI Widget: Queue stats (pending, completed, errors)
- UI Control: "Sync Now" button (triggers manual poll)

**Dependencies:**

- Bridge service running (Port 12351)
- Dashboard frontend exists

**Akzeptanzkriterien:**

- [ ] `GET /api/bridge/status` returns: `{ queue_length, pending_tasks, completed_count, last_sync }`
- [ ] UI updates every 5 seconds (or manual sync)
- [ ] Shows last 5 tasks (ID, status, created_at)
- [ ] "Sync Now" button polls immediately
- [ ] Error state: "Bridge unreachable" → displays 🔴

**Deliverables:**

- Endpoint in `main_dashboard.py` (30 lines)
- Frontend JS/HTML snippet (50 lines)
- `test_bridge_status.py` – Integration test

**Schätzung:** 1 Day

---

## ✅ POSITION 04: Retry & Backoff in VS Code Extension

**Ziel:** Exponentielles Backoff + persistente Fehlerbehandlung in der VS Code Extension.

**Scope:**

- Max retries: 5 (backoff: 1s, 2s, 4s, 8s, 16s)
- Fallback: Save task locally (indexedDB alt. localStorage)
- Error notification: Toast + error log

**Dependencies:**

- Extension skeleton exists
- Bridge API stable

**Akzeptanzkriterien:**

- [ ] Network error → retry with exponential backoff
- [ ] After 5 failures → persist task locally + show error
- [ ] User can "Retry All" failed tasks
- [ ] Exponential backoff delay: 1s→2s→4s→8s→16s (verified via logs)
- [ ] Persistent storage survives VS Code restart

**Deliverables:**

- `extension/src/retry.ts` – Backoff logic (100 lines)
- `extension/src/storage.ts` – Local persistence (80 lines)
- `extension/test/retry.test.ts` – Jest tests

**Schätzung:** 1.5 Days

---

## ✅ POSITION 05: Konfliktstrategie (3-Way Merge)

**Ziel:** Unterstützung für 3-Way-Merge bei gleichzeitigen Änderungen + Konflikt-Dialog.

**Scope:**

- Mode: `append`, `overwrite`, `merge` (3-Way)
- Merge algorithm: LCS (Longest Common Subsequence)
- Conflict marker: `<<<<<<`, `|||||`, `======`, `>>>>>>`

**Dependencies:**

- File operations stable
- Task model defined

**Akzeptanzkriterien:**

- [ ] Mode `append`: Adds new lines without conflict
- [ ] Mode `overwrite`: Base wins (warnings shown)
- [ ] Mode `merge`: 3-Way merge with conflict markers
- [ ] Merge test: base + local + remote with overlapping changes
- [ ] Conflict markers properly formatted

**Deliverables:**

- `merge.py` – Merge algorithm (150 lines)
- `test_merge.py` – Pytest suite (100 lines)
- Documentation: `docs/merge_strategy.md` (50 lines)

**Schätzung:** 1.5 Days

---

## ✅ POSITION 06: Pfad-Sandboxing Härtung

**Ziel:** Absolute Sicherheit gegen Pfad-Traversal-Attacken + Symbollinks.

**Scope:**

- Whitelist: `allowed_dirs` (z.B. workspace root)
- Blacklist: `denied_patterns` (z.B. `.git`, `node_modules`)
- Enforcement: Jeder `open()`, `write()`, `delete()` prüft

**Dependencies:**

- File operations defined

**Akzeptanzkriterien:**

- [ ] Path `../../../etc/passwd` → `400 Bad Request`
- [ ] Path with `..` → normalized + validated
- [ ] Symlink → resolved + checked against whitelist
- [ ] All file ops log sandbox decision
- [ ] Security audit: 0 bypasses

**Deliverables:**

- `sandbox.py` – Path validation (100 lines)
- `test_sandbox.py` – Attack tests (80 lines)
- Security doc: `docs/security_sandbox.md`

**Schätzung:** 1.5 Days

---

## ✅ POSITION 07: Rate-Limit für Bridge

**Ziel:** Token-basiertes Token-Bucket Rate-Limiting (60 req/min pro Token).

**Scope:**

- Bucket size: 60 requests/minute
- Refill rate: 1 req/sec
- Strategy: Sliding Window (Redis alt. in-memory)

**Dependencies:**

- Auth middleware exists (Position 01)

**Akzeptanzkriterien:**

- [ ] 60 requests/min succeed
- [ ] 61st request in same minute → `429 Too Many Requests`
- [ ] After 1 minute, bucket refills
- [ ] Rate limit headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] Load test: 100 concurrent requests → correct limiting

**Deliverables:**

- Rate limiter middleware (80 lines)
- `test_ratelimit.py` – Pytest suite (60 lines)
- Redis alt. in-memory implementation

**Schätzung:** 1 Day

---

## ✅ POSITION 08: CLI `bridgectl` (Python-Click)

**Ziel:** Command-line tool zur Bridge-Verwaltung.

**Scope:**

- Commands: `list`, `drain`, `enqueue`, `retry`, `status`
- Format: Table output (tabulate alt. click.echo)
- Config: `.env` + `--token` flag

**Dependencies:**

- Bridge API stable

**Akzeptanzkriterien:**

- [ ] `bridgectl list` → shows pending tasks
- [ ] `bridgectl enqueue --file test.txt --prompt "summarize"` → creates task
- [ ] `bridgectl drain` → clears queue
- [ ] `bridgectl retry --task-id 123` → retries single task
- [ ] `bridgectl status` → overall health
- [ ] Tab completion works

**Deliverables:**

- `bin/bridgectl` – Click CLI (200 lines)
- `test_cli.py` – Pytest + click.testing
- `docs/bridgectl_reference.md` – Manual

**Schätzung:** 1 Day

---

## ✅ POSITION 09: Systemd Units

**Ziel:** Systemd service units für opena3, adapter, bridge, dashboard.

**Scope:**

- Units: `elion-dashboard.service`, `elion-opena3.service`, `elion-adapter.service`, `elion-bridge.service`
- RestartPolicy: `always`, RestartSec: 10s
- Environment: Python venv, `.env` sourcing

**Dependencies:**

- All services defined

**Akzeptanzkriterien:**

- [ ] `systemctl start elion-bridge` → service starts
- [ ] Service restarts on failure
- [ ] Logs in `journalctl -u elion-bridge`
- [ ] `systemctl stop` → graceful shutdown
- [ ] All 4 units work together

**Deliverables:**

- `systemd/elion-dashboard.service` (30 lines)
- `systemd/elion-opena3.service` (30 lines)
- `systemd/elion-adapter.service` (30 lines)
- `systemd/elion-bridge.service` (30 lines)
- Install script: `bin/install_systemd.sh`

**Schätzung:** 0.5 Days

---

## ✅ POSITION 10: Docker Compose Integration

**Ziel:** Complete Docker Compose stack (dashboard, opena3, adapter, bridge, OpenWebUI).

**Scope:**

- Services: 5 (dashboard, opena3, adapter, bridge, openwebui)
- Volumes: archivp/, logs/
- Network: custom bridge (elion-network)
- Healthchecks: all services

**Dependencies:**

- All services containerizable

**Akzeptanzkriterien:**

- [ ] `docker compose up` → all services start
- [ ] All healthchecks green within 30s
- [ ] Port forwarding: 12349, 12347, 12350, 12351, 8080
- [ ] Volumes persist across restarts
- [ ] `docker compose down` → clean shutdown
- [ ] `docker compose logs -f` → aggregated logs

**Deliverables:**

- `docker-compose.yml` (150 lines)
- `.dockerignore` + build context
- `Dockerfile` updates (all services)
- `docs/docker_guide.md` – Usage guide

**Schätzung:** 1.5 Days

---

## ✅ POSITION 11: E2E Test Pipeline (pytest)

**Ziel:** Full end-to-end test: Chat → Bridge → Extension → File Write.

**Scope:**

- Test flow: Create task → bridge queues → extension processes → file written
- Mocking: Extension backend stub
- Coverage: All happy path + error cases

**Dependencies:**

- All services running + testable

**Akzeptanzkriterien:**

- [ ] `pytest tests/test_e2e.py` → all green
- [ ] Test creates task via dashboard
- [ ] Bridge picks up task
- [ ] Stub extension processes task
- [ ] File written correctly
- [ ] All 5 error cases tested
- [ ] Coverage: >80%

**Deliverables:**

- `tests/test_e2e.py` (300 lines)
- Test fixtures (conftest.py, 100 lines)
- CI workflow: `.github/workflows/test_e2e.yml`

**Schätzung:** 2 Days

---

## ✅ POSITION 12: OpenWebUI Adapter Robustheit

**Ziel:** Circuit-Breaker + Timeout-Handling für OpenWebUI Adapter.

**Scope:**

- Circuit states: CLOSED (ok), OPEN (fail), HALF_OPEN (retry)
- Timeout: 30s (configurable)
- Fallback: Return cached last response alt. error

**Dependencies:**

- Adapter exists (Phase 2)

**Akzeptanzkriterien:**

- [ ] Healthy OpenWebUI: circuit CLOSED
- [ ] OpenWebUI down: circuit OPEN after 3 fails
- [ ] Circuit stays OPEN for 60s, then HALF_OPEN
- [ ] HALF_OPEN → success: CLOSED; fail: OPEN
- [ ] Timeout: requests >30s return 504
- [ ] Cached response serves if OpenWebUI down

**Deliverables:**

- `circuit_breaker.py` (120 lines)
- Updated `openwebui_adapter.py` (30 line changes)
- `test_circuit_breaker.py` (100 lines)

**Schätzung:** 1.5 Days

---

## ✅ POSITION 13: Bridge-to-Archivp Auto-Persistence

**Ziel:** Automatisches Speichern von Bridge-Tasks in archivp/ nach Completion.

**Scope:**

- On completion: Write task + response to `archivp/YYYY/MM/DD/`
- Format: JSON with metadata (status, duration, tokens_used)
- Retention: Auto-cleanup nach 30 Tagen

**Dependencies:**

- Bridge API stable
- archivp/ exists

**Akzeptanzkriterien:**

- [ ] Completed task → JSON in archivp/
- [ ] Filename: `{ts}_{task_id}_{status}.json`
- [ ] Metadata includes: task_id, prompt, response, duration_ms, created_at, completed_at
- [ ] Auto-cleanup: tasks >30 days old deleted
- [ ] Query endpoint: `GET /api/bridge/archive?days=7` (recent 7 days)

**Deliverables:**

- Archive manager: `archive_manager.py` (120 lines)
- Updated `copilot_bridge.py` (20 lines)
- `test_archive.py` (80 lines)

**Schätzung:** 1 Day

---

## ✅ POSITION 14: VS Code Extension Scaffold

**Ziel:** Fully functional VS Code Extension scaffold mit Command Palette integration.

**Scope:**

- Commands: "ELION: Enqueue Task", "ELION: Show Queue", "ELION: Open Dashboard"
- Views: Sidebar panel (queue monitor) + webview (task details)
- Configuration: `.vscode/settings.json` (bridge URL, token)

**Dependencies:**

- Bridge service stable

**Akzeptanzkriterien:**

- [ ] Extension activates (logs "ELION Bridge activated")
- [ ] Command "ELION: Enqueue Task" opens dialog
- [ ] Task dialog: prompt + file selection
- [ ] "Enqueue" button sends to bridge
- [ ] Sidebar shows queue (refreshes every 5s)
- [ ] Click task → shows details in webview

**Deliverables:**

- `extension/src/extension.ts` (200 lines)
- `extension/src/commands.ts` (150 lines)
- `extension/src/sidebar.ts` (100 lines)
- `extension/src/webview.ts` (150 lines)
- `extension/package.json` (manifest)

**Schätzung:** 2 Days

---

## ✅ POSITION 15: Task Execution & Result Streaming

**Ziel:** Bridge führt Tasks aus + streamt Results via SSE/WebSocket an Extension.

**Scope:**

- Task model: id, prompt, file, mode, status
- Execution: Calls opena3/OpenWebUI, streams response
- Streaming: SSE (alt. WebSocket) for real-time updates
- Result handling: Extension receives chunks + final result

**Dependencies:**

- Position 14 (extension exists)
- opena3 service stable

**Akzeptanzkriterien:**

- [ ] Task queued → immediate ACK to extension
- [ ] Bridge calls opena3 `/command` endpoint
- [ ] opena3 streams response chunks
- [ ] Bridge forwards chunks to extension via SSE
- [ ] Extension displays chunks real-time (progressive)
- [ ] Final result saved to file + archivp/
- [ ] Error handling: timeout, network failure, OpenWebUI down

**Deliverables:**

- `task_executor.py` (150 lines)
- SSE streaming: updated `copilot_bridge.py` (50 lines)
- `extension/src/streamer.ts` (120 lines)
- `test_executor.py` (100 lines)

**Schätzung:** 2 Days

---

## ✅ POSITION 16: Conflicts & Merging UI

**Ziel:** UI in Extension für Konflikt-Auflösung bei 3-Way Merges.

**Scope:**

- Conflict modal: base, local, remote, merged
- Actions: "Accept Local", "Accept Remote", "Accept Merge", "Manual Edit"
- Visual diff: Color-coded changes

**Dependencies:**

- Position 05 (merge algorithm)
- Position 14 (extension UI)

**Akzeptanzkriterien:**

- [ ] Conflict detected → modal appears
- [ ] Shows 3 versions (base, local, remote)
- [ ] "Accept Local/Remote/Merge" buttons work
- [ ] "Manual Edit" opens merged file + user edits
- [ ] Result saved correctly
- [ ] All conflict markers resolved

**Deliverables:**

- `extension/src/conflict.ts` (200 lines)
- CSS for conflict view (100 lines)
- `extension/test/conflict.test.ts` (80 lines)

**Schätzung:** 1.5 Days

---

## ✅ POSITION 17: Logging & Audit Trail

**Ziel:** Comprehensive Logging (Bridge, Extension) + Audit Trail für alle Operationen.

**Scope:**

- Logs: INFO, WARNING, ERROR levels
- Audit: All task operations (create, update, complete, fail)
- Retention: 7 days rolling (compress old logs)
- Query: `GET /api/bridge/audit?filter=...` (datetime, user, action)

**Dependencies:**

- All services

**Akzeptanzkriterien:**

- [ ] Bridge logs to `logs/bridge.log`
- [ ] Extension logs to VS Code console + file
- [ ] Audit entries include: timestamp, user_token, action, task_id, status, details
- [ ] Sensitive data (tokens) never logged (scrubbing)
- [ ] Log rotation: new file daily
- [ ] Query audit via API: works with filters

**Deliverables:**

- `logging_config.py` (100 lines)
- Audit middleware (50 lines)
- Log scrubber (40 lines)
- `test_logging.py` (80 lines)

**Schätzung:** 1 Day

---

## ✅ POSITION 18: Performance Benchmarking

**Ziel:** Benchmark-Suite für Bridge Performance unter Last.

**Scope:**

- Load test: 100 concurrent tasks
- Latency: measure queueing + execution + result delivery time
- Throughput: tasks/second
- Memory: peak usage during load

**Dependencies:**

- All services stable + E2E tests pass

**Akzeptanzkriterien:**

- [ ] Run `bin/benchmark.sh` → full report
- [ ] Latency <5s (enqueue + process + deliver)
- [ ] Throughput >50 tasks/min
- [ ] Memory stable (no leaks)
- [ ] No crashes under 100 concurrent tasks
- [ ] Report saved: `docs/benchmark_report.md`

**Deliverables:**

- `bin/benchmark.sh` (100 lines)
- `tests/benchmark.py` (150 lines)
- Benchmark report template

**Schätzung:** 1 Day

---

## ✅ POSITION 19: Deployment & Rollout Guide

**Ziel:** Production Deployment Playbook + Rollback Procedures.

**Scope:**

- Deployment: systemd alt. Docker Compose
- Health checks: All services + integration test
- Rollback: Previous version restore
- Monitoring: Alerts setup

**Dependencies:**

- Positions 09–10 (systemd + Docker)

**Akzeptanzkriterien:**

- [ ] Deployment playbook written (markdown)
- [ ] Step-by-step instructions
- [ ] Pre-checks: disk space, ports, network
- [ ] Post-deployment: health checks
- [ ] Rollback playbook: fast restore
- [ ] Monitoring examples: Prometheus alt. simple scripts
- [ ] All documented with examples

**Deliverables:**

- `docs/DEPLOYMENT.md` (200 lines)
- `docs/ROLLBACK.md` (100 lines)
- `scripts/health_check.sh` (80 lines)
- `monitoring/prometheus_config.yml` (alt. examples)

**Schätzung:** 1 Day

---

## ✅ POSITION 20: Release v1.0 & CI/CD Pipeline

**Ziel:** First production release (v1.0) + GitHub Actions CI/CD.

**Scope:**

- Version: 1.0.0 (semver)
- CI: Lint, build, test on every push
- CD: Auto-release to GitHub Releases + Docker Hub
- Changelog: Auto-generated from commits

**Dependencies:**

- All 19 positions complete
- Manifest validated

**Akzeptanzkriterien:**

- [ ] `.github/workflows/ci.yml` → lint, test, build all pass
- [ ] `.github/workflows/cd.yml` → release on tag
- [ ] Version bumped: `__version__ = "1.0.0"`
- [ ] CHANGELOG.md generated
- [ ] GitHub Release created + Docker image pushed
- [ ] All artifacts signed (alt. checksummed)
- [ ] v1.0.0 tag pushed

**Deliverables:**

- `.github/workflows/ci.yml` (50 lines)
- `.github/workflows/cd.yml` (50 lines)
- `CHANGELOG.md` (initial)
- `__version__.py` or `pyproject.toml` (version)
- Release notes on GitHub

**Schätzung:** 1 Day

---

## 📊 Timeline & Sequencing

### Week 1 (Positions 01–05)

```
Mon: Pos 01 + 02 (Auth + OpenAPI)
Tue: Pos 03 + 04 (Monitor + Retry)
Wed: Pos 05 (Merge)
Thu-Fri: Buffer + integration
```

### Week 2 (Positions 06–10)

```
Mon: Pos 06 + 07 (Sandbox + RateLimit)
Tue: Pos 08 (CLI)
Wed: Pos 09 + 10 (systemd + Docker)
Thu-Fri: Buffer + testing
```

### Week 3 (Positions 11–15)

```
Mon: Pos 11 (E2E tests)
Tue: Pos 12 + 13 (Adapter + Archive)
Wed: Pos 14 + 15 (Extension + Streaming)
Thu-Fri: Buffer + debugging
```

### Week 4 (Positions 16–20)

```
Mon: Pos 16 + 17 (Conflicts + Logging)
Tue: Pos 18 (Benchmarks)
Wed: Pos 19 (Deployment)
Thu: Pos 20 (Release)
Fri: Buffer + post-release
```

---

## ✅ Acceptance & Sign-Off

| Role               | Sign-Off | Target Date |
| ------------------ | -------- | ----------- |
| **Task Lead**      | —        | Week 4      |
| **QA**             | —        | Week 4      |
| **DevOps**         | —        | Week 4      |
| **Copilot Review** | —        | Ongoing     |
| **GitHub CI/CD**   | —        | Week 4      |

---

## 📚 Related Documentation

- **Project Manifest:** `project_manifest.md` (this directory)
- **Copilot Instructions:** `../../.github/copilot-instructions.md`
- **Phase 3 Complete:** `../../.github/COMPLETION_CHECKLIST.md`
- **OpenAPI Reference:** Will be in `docs/bridge_api.md` (Position 02)

---

**[PDI-FOOTER: All 20 positions defined, sequenced, and ready for Phase 4 implementation. Manifest version 1.0 validated.]**
