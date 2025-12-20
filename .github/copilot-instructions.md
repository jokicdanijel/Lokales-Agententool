## Copilot-Anweisungen (ELION Hyper-Dashboard)

Diese Repo ist ein Multi-Service-Agent-Stack ("opena\*") mit einem Ops-Orchestrator. Ziel: Änderungen so machen, dass die Stack-Tools (Start/Verify/Register) weiterhin funktionieren.

### Big Picture

- **Orchestrierung:** `bin/ops.sh` ist die Quelle der Wahrheit (Ports, Startreihenfolge, per-Agent `.venv`, Logs).
- **Kommunikation:** Agenten sprechen per HTTP auf `127.0.0.1` und sollten konsistent `GET /health` anbieten.
- **Port-Policy:** Services nur in **12344–12399** binden; **8080 nie binden** (OpenWebUI kann extern auf 8080 laufen, aber nicht als interner Service-Port).

### Wichtige Einstiegspunkte (Code)

- **Ops/Policy/Mapping:** `bin/ops.sh` (Array `AGENTS=...`, Preflight `.env`, `logs/*.nohup.log`, PID-Files).
- **Dashboard (voll, Registry+SSE+OpenWebUI):** `src/pkg/main_dashboard.py` (u.a. `POST /api/agent/register`, `GET /api/openwebui/status`).
- **Dashboard (schlank, Status-Aggregation):** `19.opena20_dashboard_agent/main_dashboard.py` (`GET /api/status/all`).
- **MCP Tool Server:** `mcp_server/mcp_tool_server.py` (Port **12398**, `POST /mcp` JSON-RPC, `POST /tools/list|call`, Audit-Log `mcp_server/logs/mcp_audit.jsonl`).

### Secrets & .env (konkret im Code gefunden)

- Ops erwartet `$PROJECT_ROOT/.env`; wenn sie fehlt, wird **`mcp_server/.env.example` kopiert** und der Lauf bricht ab, damit du Secrets setzt.
- Häufige Keys:
  - `DASHBOARD_ADMIN_TOKEN` (Auth für Dashboard-API; benutzt von `scripts/register_agents.py`)
  - `BEARER_TOKEN` (Auth-Header in mehreren Services; auch MCP prüft `Authorization: Bearer ...`)
  - `OPENAI_API_KEY_OPENA1`, `OPENAI_API_KEY_OPENA2`, `OPENAI_API_KEY_OPENA20`
- **Wichtig:** `.env` nicht sourcen; `bin/ops.sh` liest whitelisted Keys (Security-Policy im Script).

### Developer-Workflows (Repo-spezifisch)

- Start/Stop: `bin/ops.sh start` / `bin/ops.sh stop`
- Verify: `bin/ops.sh verify` (prüft lokale `/health`-Endpoints)
- Agent-Registration: `bin/ops.sh agents:register` oder `scripts/register_agents.py` (fordert `DASHBOARD_ADMIN_TOKEN`).
- Logs: `bin/ops.sh logs` (nohup-Logs unter `logs/`).

### Konventionen beim Implementieren

- Dashboard-Dispatch ist generisch: Agent-Kommandos laufen typischerweise über `POST {endpoint}/command` (siehe `src/pkg/agent_registry.py:execute_command`).
- MCP & einige Services nutzen **Pydantic v2 strict** mit `extra="forbid"` → neue Felder nur bewusst hinzufügen.
- Safepoints/Archivp: Secret-Masking orientiert sich an `SafepointWriter30.SECRET_KEYS` (siehe `19.opena20_dashboard_agent/main_dashboard.py`).

Weiterlesen (kanonisch): `docs/OPERATIONS.md`, `docs/README_STACK_START.md`, optional `.github/copilot-master-prompt.md`.

