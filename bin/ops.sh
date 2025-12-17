ops.sh

#!/usr/bin/env bash
# ==============================================================================
# ops.sh (ELION Hyper-Dashboard Stack Controller)
# Einheitliche CLI für alle Stack-Operationen + HTML-Startanleitung Generator
# ==============================================================================
set -euo pipefail
IFS=$'\n\t'

# Detect script directory and project root
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source common library if available
if [[ -f "$SCRIPT_DIR/../scripts/_lib.sh" ]]; then
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/../scripts/_lib.sh"
  load_env
else
  # Fallback: set basic defaults
  DASHBOARD_PORT="${DASHBOARD_PORT:-12349}"
  OPENA1_PORT="${OPENA1_PORT:-12344}"
  OPENA2_PORT="${OPENA2_PORT:-12345}"

  # Read token from .env if exists
  if [[ -f "$PROJECT_ROOT/.env" ]]; then
    TOK="$(grep -m1 "^DASHBOARD_ADMIN_TOKEN=" "$PROJECT_ROOT/.env" 2>/dev/null | cut -d= -f2- || true)"
    TOK="${TOK:-}"
    if [[ -z "$TOK" ]]; then
      echo "⚠️  DASHBOARD_ADMIN_TOKEN not found in .env" >&2
    fi
  else
    TOK=""
  fi
fi

cd "$PROJECT_ROOT"

# Endpoints
DASH="http://127.0.0.1:${DASHBOARD_PORT}"
OPENA1="http://127.0.0.1:${OPENA1_PORT}"
OPENA2="http://127.0.0.1:${OPENA2_PORT}"

# ---------------------------------------------------------------------------
# Agent mapping: agent_id:folder:port
# ---------------------------------------------------------------------------
AGENTS=(
  "opena1:1.opena1&2_portier:12344"
  "opena2:1.opena1&2_portier:12345"
  "opena3:2.opena3_openwebui:12347"
  "opena4:3.opena4_telegram:12348"
  "opena5:4.opena5_vscode:12351"
  "opena6:5.opena6_browser:12352"
  "opena7:6.opena7_email:12353"
  "opena8:7.opena8_whatsapp:12354"
  "opena9:8.opena9_telephone:12355"
  "opena10:9.opena10_call_tracking:12356"
  "opena11:10.opena11_unlock:12357"
  "opena12:11.opena12_social_media:12358"
  "opena13:12.opena13_influencer:12359"
  "opena14:13.opena14_calendar:12360"
  "opena15:14.opena15_html:12361"
  "opena16:15.opena16_shop:12362"
  "opena17:16.opena17_homepagecreator:12366"
  "opena18:17.opena18_CMR:12363"
  "opena19:18.opena19_Aktien&Crypto:12365"
  "browsep:6.browsep_portier:12370"
  "opena20:19.opena20_dashboard_agent:12349"
  "opena21:20.opena21_workflow:12367"
)

# Helper: iterate agents
run_for_agents() {
  # callback receives agent, folder, port
  for e in "${AGENTS[@]}"; do
    agent="${e%%:*}"
    rest="${e#*:}"
    folder="${rest%%:*}"
    port="${rest##*:}"
    "$@" "$agent" "$folder" "$port"
  done
}
# ---------------------------------------------------------------------------

# ==============================================================================
# Helper Functions
# ==============================================================================
need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "❌ Required command not found: $1"; exit 1; }
}

need_token() {
  [[ -n "${TOK:-}" ]] || { echo "❌ No token found. Create/fill $PROJECT_ROOT/.env"; exit 1; }
}

usage() {
  cat <<'USAGE'
ELION Hyper-Dashboard OPS – Stack Controller

Commands:
  start             - Start all services (opena1, opena2, Dashboard) + best-effort agents
  stop              - Stop all services (graceful shutdown via PID files)
  restart           - Stop and start all services
  health            - Quick health check (all agents)
  status            - Full system status (requires Bearer token)
  monitor           - Continuous health monitoring (Ctrl+C to stop)
  agents:register   - Register agents with dashboard
  verify            - Run integration verification + E2E test
  logs              - Show recent service logs (tail -100)
  logs:follow       - Follow logs in real-time
  e2e               - Run Option-2-Flow E2E test
  eval              - Run workspace evaluation and produce report
  doc:agents        - Generate HTML start guide for all agents (docs/agent_startanleitung.html)
  help              - Show this help

Examples:
  bin/ops.sh start
  bin/ops.sh monitor
  bin/ops.sh e2e
  bin/ops.sh eval
  bin/ops.sh logs:follow
  bin/ops.sh doc:agents
USAGE
}

# ==============================================================================
# HTML Doc Generator (agents)
# ==============================================================================
generate_agents_doc() {
  local out_dir="$PROJECT_ROOT/docs"
  local out="$out_dir/agent_startanleitung.html"
  local env_example="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/mcp_server/.env.example"
  local domain="https://hyperdashboard-one.de"

  mkdir -p "$out_dir"

  {
    cat <<'HTML_HEAD'
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ELION Hyper-Dashboard – Startanleitung aller Agenten</title>
  <style>
    :root{--bg:#0b0f14;--panel:#111824;--panel2:#0f1621;--txt:#e6edf3;--muted:#9fb0c3;--acc:#6ee7ff;--acc2:#a7f3d0;--warn:#ffd166;--bad:#ff5c7a;--ok:#5cffb0;--border:#223044}
    *{box-sizing:border-box}
    body{margin:0;background:linear-gradient(180deg,var(--bg),#06090d);color:var(--txt);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Arial}
    header{padding:26px 16px;border-bottom:1px solid var(--border);background:radial-gradient(1200px 400px at 15% 0%,rgba(110,231,255,.12),transparent),radial-gradient(800px 320px at 70% 10%,rgba(167,243,208,.10),transparent)}
    header h1{margin:0 0 6px;font-size:20px}
    header p{margin:0;color:var(--muted);max-width:1100px}
    main{max-width:1200px;margin:0 auto;padding:16px}
    .card{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--border);border-radius:14px;padding:14px;margin-top:14px}
    .card h2{margin:0 0 10px;font-size:16px}
    .pill{display:inline-block;padding:3px 10px;border:1px solid var(--border);border-radius:999px;color:var(--muted);margin:0 6px 8px 0}
    .pill b{color:var(--txt)}
    .pill.ok{border-color:rgba(92,255,176,.35);color:var(--acc2)}
    .pill.bad{border-color:rgba(255,92,122,.35);color:var(--bad)}
    .pill.warn{border-color:rgba(255,209,102,.35);color:var(--warn)}
    .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}
    pre{margin:10px 0 0;padding:12px;border-radius:12px;background:#0a0f16;border:1px solid var(--border);overflow:auto}
    code{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}
    table{width:100%;border-collapse:separate;border-spacing:0;overflow:hidden;border-radius:12px;border:1px solid var(--border)}
    th,td{padding:10px 10px;border-bottom:1px solid var(--border);vertical-align:top}
    th{background:#0a0f16;color:var(--muted);text-align:left;font-weight:600}
    tr:last-child td{border-bottom:none}
    a{color:var(--acc);text-decoration:none}
    a:hover{text-decoration:underline}
    details{border:1px solid var(--border);border-radius:12px;padding:10px;background:#0a0f16}
    details + details{margin-top:10px}
    summary{cursor:pointer;color:var(--txt);font-weight:700}
    .small{font-size:12px;color:var(--muted)}
    .note{border-left:3px solid var(--acc);padding:8px 10px;background:rgba(110,231,255,.06);border-radius:10px;color:var(--muted);margin-top:10px}
    .note strong{color:var(--txt)}
    .danger{border-left:3px solid var(--bad);background:rgba(255,92,122,.06)}
    .okbox{border-left:3px solid var(--ok);background:rgba(92,255,176,.05)}
    .toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 0}
    input[type="search"]{flex:1;min-width:240px;background:#0a0f16;color:var(--txt);border:1px solid var(--border);border-radius:10px;padding:10px}
    .btn{background:#0a0f16;color:var(--txt);border:1px solid var(--border);border-radius:10px;padding:10px 12px;cursor:pointer}
    .btn:hover{border-color:#2b3d58}
  </style>
</head>
<body>
<header>
  <h1>ELION Hyper-Dashboard – Startanleitung aller Agenten (opena1–opena21 + browsep)</h1>
  <p>
    Ziel: Jeder Agent läuft lokal auf seinem Port (<span class="mono">127.0.0.1:PORT</span>) und ist extern erreichbar über
    <span class="mono">https://hyperdashboard-one.de/openaX/</span> (Reverse Proxy / Pfad-Routing).
    Port-Policy: <span class="mono">12344–12399</span> ✅, <span class="mono">&lt;OPENWEBUI_UI_PORT&gt;</span> ❌.
  </p>
</header>
<main>
HTML_HEAD

    cat <<HTML_ENV
  <section class="card">
    <h2>0) Pflicht: .env Setup (Vorlage)</h2>
    <span class="pill ok"><b>Quelle</b>: <span class="mono">${env_example}</span></span>
    <span class="pill warn"><b>Hinweis</b>: ops.sh liest <span class="mono">PROJECT_ROOT/.env</span></span>
    <div class="note okbox">
      <strong>Vorgehen:</strong> Kopiere die Vorlage ins Projekt-Root und setze Token/Keys. Ohne <span class="mono">.env</span> bricht <span class="mono">ops.sh start</span> ab.
    </div>
    <pre><code>cd ${PROJECT_ROOT}

cp ${env_example} .env
nano .env

# Minimal-Check (Keys/Token)
grep -E '^(DASHBOARD_ADMIN_TOKEN|OPENAI_API_KEY_OPENA1|OPENAI_API_KEY_OPENA2)=' .env</code></pre>
    <div class="note danger"><strong>Security:</strong> .env nicht committen. Secrets gehören in CI/CD Secret Store.</div>
  </section>
HTML_ENV

    cat <<'HTML_QS'
  <section class="card">
    <h2>1) Quickstart (zentrale Steuerung)</h2>
    <pre><code># Projekt-Root
chmod +x bin/ops.sh

# Start: opena1, opena2, opena20 (Dashboard) + best-effort alle weiteren Agenten
bin/ops.sh start

# Health über alle Agenten
bin/ops.sh health

# Live Monitoring
bin/ops.sh monitor</code></pre>
  </section>
HTML_QS

    cat <<'HTML_TABLE_HEAD'
  <section class="card">
    <h2>2) Agentenübersicht (Ports, Health, Public URLs)</h2>
    <div class="toolbar">
      <input id="filter" type="search" placeholder="Filter… z.B. opena8, whatsapp, 12349, browsep" />
      <button class="btn" onclick="resetFilter()">Reset</button>
      <button class="btn" onclick="expandAll()">Expand all</button>
      <button class="btn" onclick="collapseAll()">Collapse all</button>
    </div>
    <p class="small" style="margin:10px 0 0">
      Start-Logik: <span class="mono">bin/start_AGENT.sh</span> → <span class="mono">bin/start.sh</span> → <span class="mono">python3 main_*.py</span>. Health: <span class="mono">/health</span>.
    </p>
    <table id="agentsTable">
      <thead>
        <tr>
          <th>Agent</th>
          <th>Ordner</th>
          <th>Port</th>
          <th>Lokal Health</th>
          <th>Extern (Proxy)</th>
          <th>Manual Start (Fallback)</th>
        </tr>
      </thead>
      <tbody>
HTML_TABLE_HEAD

    # Table rows
    for e in "${AGENTS[@]}"; do
      agent="${e%%:*}"
      rest="${e#*:}"
      folder="${rest%%:*}"
      port="${rest##*:}"

      # HTML escape minimal (&)
      folder_html="${folder//&/&amp;}"
      folder_cmd="$folder"

      # Default start
      start_cmd="cd ${folder_cmd} && (bin/start_${agent}.sh || bin/start.sh || python3 main_*.py)"
      if [[ "$agent" == "opena1" ]]; then
        start_cmd="cd ${folder_cmd} && bin/start_opena1_with_key.sh"
      elif [[ "$agent" == "opena2" ]]; then
        start_cmd="cd ${folder_cmd} && bin/start_opena2_with_key.sh"
      elif [[ "$agent" == "opena20" ]]; then
        start_cmd="cd ${folder_cmd} && python3 main_dashboard.py"
      fi

      cat <<HTML_ROW
        <tr>
          <td class="mono">${agent}</td>
          <td class="mono">${folder_html}</td>
          <td class="mono">${port}</td>
          <td class="mono"><a href="http://127.0.0.1:${port}/health">127.0.0.1:${port}/health</a></td>
          <td class="mono">/${agent}/</td>
          <td class="mono">${start_cmd//&/&amp;}</td>
        </tr>
HTML_ROW
    done

    cat <<'HTML_TABLE_TAIL'
      </tbody>
    </table>
  </section>
HTML_TABLE_TAIL

    cat <<'HTML_RUNBOOK_HEAD'
  <section class="card">
    <h2>3) Pro Agent – Runbook (einzeln startbar)</h2>
    <p class="small">Wenn “best-effort start” nicht reicht: nimm die Sektion deines Agenten und starte gezielt.</p>
HTML_RUNBOOK_HEAD

    for e in "${AGENTS[@]}"; do
      agent="${e%%:*}"
      rest="${e#*:}"
      folder="${rest%%:*}"
      port="${rest##*:}"

      folder_html="${folder//&/&amp;}"
      folder_cmd="$folder"

      start_cmd="cd ${folder_cmd} && (bin/start_${agent}.sh || bin/start.sh || python3 main_*.py)"
      if [[ "$agent" == "opena1" ]]; then
        start_cmd="cd ${folder_cmd} && bin/start_opena1_with_key.sh"
      elif [[ "$agent" == "opena2" ]]; then
        start_cmd="cd ${folder_cmd} && bin/start_opena2_with_key.sh"
      elif [[ "$agent" == "opena20" ]]; then
        start_cmd="cd ${folder_cmd} && python3 main_dashboard.py"
      fi

      cat <<HTML_DETAIL
    <details class="agentDetail">
      <summary>${agent} (${port}) – Ordner: <span class="mono">${folder_html}</span></summary>
      <pre><code>Start:
${start_cmd}

Health:
curl -s http://127.0.0.1:${port}/health | (command -v jq >/dev/null 2>&1 && jq . || cat)

Extern (Proxy):
${domain}/${agent}/</code></pre>
    </details>
HTML_DETAIL
    done

    cat <<'HTML_E2E'
  </section>

  <section class="card">
    <h2>4) E2E Test</h2>
    <pre><code># Via Dashboard API
curl -X POST http://127.0.0.1:12349/api/e2e

# Via opena1 direkt
curl -X POST http://127.0.0.1:12344/log/opena1 \
  -H "Content-Type: application/json" \
  -d '{
    "request_id":"test-123",
    "timestamp":"2025-11-24T12:00:00Z",
    "source":"openai",
    "user_query":"Test",
    "context":{},
    "metadata":{}
  }'</code></pre>
  </section>

<script>
  const filter = document.getElementById('filter');
  const table = document.getElementById('agentsTable');
  const details = () => Array.from(document.querySelectorAll('.agentDetail'));

  function rowText(tr){ return tr.innerText.toLowerCase(); }

  function applyFilter(){
    const q = (filter.value || '').trim().toLowerCase();
    Array.from(table.querySelectorAll('tbody tr')).forEach(tr=>{
      tr.style.display = (!q || rowText(tr).includes(q)) ? '' : 'none';
    });
    details().forEach(d=>{
      const txt = (d.innerText || '').toLowerCase();
      const show = (!q || txt.includes(q));
      d.style.display = show ? '' : 'none';
      if(show && q) d.open = true;
    });
  }
  function resetFilter(){ filter.value=''; applyFilter(); }
  function expandAll(){ details().forEach(d=> d.open = true); }
  function collapseAll(){ details().forEach(d=> d.open = false); }

  if(filter){
    filter.addEventListener('input', applyFilter);
    window.resetFilter = resetFilter;
    window.expandAll = expandAll;
    window.collapseAll = collapseAll;
  }
</script>

</main>
</body>
</html>
HTML_E2E
  } > "$out"

  echo "✅ HTML Startanleitung erzeugt: $out"
}

# Preflight checks (generates runbook and validates policy)
preflight_checks() {
  echo "🔎 Running preflight checks..."

  # Ensure .env.example exists
  if [[ ! -f "$PROJECT_ROOT/mcp_server/.env.example" ]]; then
    echo "❌ mcp_server/.env.example not found" >&2
    return 2
  fi

  # Generate runbook
  "$0" doc:agents || { echo "❌ Failed to generate agents runbook" >&2; return 2; }

  out="$PROJECT_ROOT/docs/agent_startanleitung.html"
  if [[ ! -f "$out" || ! -s "$out" ]]; then
    echo "❌ Runbook missing or empty: $out" >&2
    return 2
  fi

  if ! grep -qi '<!doctype html>' "$out"; then
    echo "❌ Runbook missing <!doctype html>" >&2
    return 2
  fi

  if ! grep -qi '</html>' "$out"; then
    echo "❌ Runbook missing </html>" >&2
    return 2
  fi

  # Ensure all agents present
  missing=()
  for a in opena{1..21} browsep; do
    if ! grep -q "$a" "$out"; then missing+=("$a"); fi
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "❌ Runbook missing agents: ${missing[*]}" >&2
    return 2
  fi

  # Ensure no forbidden port 8080 is referenced in configuration/runtime files
  # Collect all matches, then filter out allowed OpenWebUI references (various naming variants)
  matches=$(grep -R --line-number --exclude-dir=.git --exclude-dir='*openwebui*' --exclude-dir='open-webui*' --exclude-dir='docs' --include='*.yml' --include='*.yaml' --include='Dockerfile' --include='*.env' --include='*.py' --include='*.sh' --include='docker-compose*' -n -e ':8080\b' . 2>/dev/null || true)
  if [[ -n "$matches" ]]; then
    # Allow matches that explicitly reference OpenWebUI or common OpenWebUI env vars/labels
    bad=$(printf "%s" "$matches" | grep -v -i -E 'openwebui|open-webui|open_webui|open webui|OPENWEBUI|OPEN_WEBUI|OPENWEBUI_URL|OPENWEBUI_BASE|OPEN_WEBUI_URL|CORS|origins|OPENWEBUI_BASE_URL|/venv|\.venv|venv_local|openapi-servers|^\./configs/|127\\.0\\.0\\.1:8080|http:\\/\\/127\\.0\\.0\\.1:8080|localhost:8080|http:\\/\\/localhost:8080|\:3000:8080|3000:8080|api_base|main_dashboard|^\./scripts/|/bin/check_ports\.sh' || true)
    if [[ -n "$bad" ]]; then
      echo "❌ Forbidden port 8080 found in configuration files (outside allowed OpenWebUI references or known envs):" >&2
      printf "%s\n" "$bad" >&2
      return 2
    fi
  fi

  # Ensure ports used in runbook are within 12344-12399
  ports_found=$(grep -oE '127\.0\.0\.1:[0-9]{4,5}' "$out" | sed -E 's/.*://g' | sort -u)
  if [[ -z "$ports_found" ]]; then
    echo "❌ No agent ports found in runbook" >&2
    return 2
  fi
  for p in $ports_found; do
    if ((p < 12344 || p > 12399)); then
      echo "❌ Port $p in runbook is outside allowed range (12344-12399)" >&2
      return 2
    fi
  done

  echo "✅ Preflight OK"
  return 0
}

# ==============================================================================
# Command Handlers
# ==============================================================================

[[ $# -lt 1 ]] && { usage; exit 1; }
cmd="$1"; shift || true

case "$cmd" in
  start)
    echo "🚀 Starting ELION Hyper-Dashboard services..."

    echo "🔎 Running preflight checks before start..."
    "$0" preflight || { echo "❌ Preflight failed; aborting start."; exit 1; }

    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
      echo "❌ .env nicht gefunden. Bitte aus mcp_server/.env.example kopieren:"
      echo "   cp /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/mcp_server/.env.example $PROJECT_ROOT/.env"
      exit 1
    fi

    # Export OpenAI Keys aus .env (robust: grep kann leer sein, cut -f2- lässt '=' im Key zu)
    OPENAI_API_KEY_OPENA1="$(grep -m1 '^OPENAI_API_KEY_OPENA1=' "$PROJECT_ROOT/.env" 2>/dev/null | cut -d= -f2- | tr -d '"' || true)"
    OPENAI_API_KEY_OPENA2="$(grep -m1 '^OPENAI_API_KEY_OPENA2=' "$PROJECT_ROOT/.env" 2>/dev/null | cut -d= -f2- | tr -d '"' || true)"
    export OPENAI_API_KEY_OPENA1 OPENAI_API_KEY_OPENA2

    if [[ -z "${OPENAI_API_KEY_OPENA1}" ]] || [[ -z "${OPENAI_API_KEY_OPENA2}" ]]; then
      echo "⚠️  OpenAI Keys nicht vollständig in .env"
      echo "    Benötigt: OPENAI_API_KEY_OPENA1 und OPENAI_API_KEY_OPENA2"
    fi

    echo ""
    echo "=== Starting Core Services ==="

    cd "$PROJECT_ROOT/1.opena1&2_portier"
    if [[ -x "bin/start_opena1_with_key.sh" ]]; then
      echo "🔹 opena1 (Port 12344)..."
      bin/start_opena1_with_key.sh
    else
      echo "⚠️  bin/start_opena1_with_key.sh nicht gefunden"
    fi

    if [[ -x "bin/start_opena2_with_key.sh" ]]; then
      echo "🔹 opena2 (Port 12345)..."
      bin/start_opena2_with_key.sh
    else
      echo "⚠️  bin/start_opena2_with_key.sh nicht gefunden"
    fi

    cd "$PROJECT_ROOT"
    if [[ -f "19.opena20_dashboard_agent/main_dashboard.py" ]]; then
      echo "🔹 Dashboard (Port 12349)..."
      cd 19.opena20_dashboard_agent
      mkdir -p ../logs
      nohup python3 main_dashboard.py > ../logs/dashboard.nohup.log 2>&1 &
      echo "✅ Dashboard gestartet (PID: $!)"
      cd "$PROJECT_ROOT"
    fi

    sleep 3

    echo ""
    echo "=== Health Check ==="
    curl -s http://127.0.0.1:12344/health 2>/dev/null | jq -c '{service, status, openai_key_present}' || echo "❌ opena1 nicht erreichbar"
    curl -s http://127.0.0.1:12345/health 2>/dev/null | jq -c '{service, status, entries, openai_key_present}' || echo "❌ opena2 nicht erreichbar"
    curl -s http://127.0.0.1:12349/health 2>/dev/null | jq -c '{service, status}' || echo "⚠️  Dashboard nicht erreichbar"

    echo ""
    echo "=== Starting available agents (best-effort) ==="
    mkdir -p "$PROJECT_ROOT/logs"
    for e in "${AGENTS[@]}"; do
      agent="${e%%:*}"
      rest="${e#*:}"
      folder="${rest%%:*}"
      port="${rest##*:}"
      AGENT_DIR="$PROJECT_ROOT/$folder"
      if [[ -d "$AGENT_DIR" ]]; then
        if [[ -x "$AGENT_DIR/bin/start_${agent}.sh" ]]; then
          echo "🔹 $agent via $folder/bin/start_${agent}.sh"
          (cd "$AGENT_DIR" && "bin/start_${agent}.sh") || true
        elif [[ -x "$AGENT_DIR/bin/start.sh" ]]; then
          echo "🔹 $agent via $folder/bin/start.sh"
          (cd "$AGENT_DIR" && bin/start.sh) || true
        elif ls "$AGENT_DIR"/main_*.py >/dev/null 2>&1; then
          mainpy="$(ls "$AGENT_DIR"/main_*.py | head -n1)"
          echo "🔹 $agent via python $mainpy"
          nohup python3 "$mainpy" > "$PROJECT_ROOT/logs/${agent}.nohup.log" 2>&1 &
          echo "   PID: $!"
        else
          echo "⚠️  Kein Startskript für $agent in $folder gefunden"
        fi
      else
        echo "⚠️  Verzeichnis $folder für $agent nicht gefunden"
      fi
    done

    echo ""
    echo "✅ Stack gestartet. Verwende 'bin/ops.sh status' für Details."
    ;;

  stop)
    echo "🛑 Stopping ELION Hyper-Dashboard services..."

    if [[ -f "$PROJECT_ROOT/logs/opena1.pid" ]]; then
      PID="$(cat "$PROJECT_ROOT/logs/opena1.pid")"
      kill "$PID" 2>/dev/null && echo "✅ opena1 gestoppt (PID: $PID)" || echo "⚠️  opena1 PID $PID nicht gefunden"
      rm -f "$PROJECT_ROOT/logs/opena1.pid"
    fi

    if [[ -f "$PROJECT_ROOT/logs/opena2.pid" ]]; then
      PID="$(cat "$PROJECT_ROOT/logs/opena2.pid")"
      kill "$PID" 2>/dev/null && echo "✅ opena2 gestoppt (PID: $PID)" || echo "⚠️  opena2 PID $PID nicht gefunden"
      rm -f "$PROJECT_ROOT/logs/opena2.pid"
    fi

    echo "Stoppe bekannte Prozesse (best-effort)..."
    for e in "${AGENTS[@]}"; do
      agent="${e%%:*}"
      rest="${e#*:}"
      folder="${rest%%:*}"
      if [[ -f "$PROJECT_ROOT/logs/${agent}.pid" ]]; then
        PID="$(cat "$PROJECT_ROOT/logs/${agent}.pid")"
        kill "$PID" 2>/dev/null && echo "✅ $agent gestoppt (PID: $PID)" || echo "⚠️  $agent PID $PID nicht gefunden"
        rm -f "$PROJECT_ROOT/logs/${agent}.pid"
      else
        pkill -f "$folder" 2>/dev/null && echo "✅ $agent processes killed by folder match" || true
        pkill -f "$agent" 2>/dev/null && echo "✅ $agent processes killed by name" || true
      fi
    done

    echo "✅ Services gestoppt"
    ;;

  health)
    need_cmd curl
    echo "🏥 Checking all agents health..."
    for e in "${AGENTS[@]}"; do
      agent="${e%%:*}"
      rest="${e#*:}"
      port="${rest##*:}"
      printf "\n🔹 %-8s (port %s):\n" "$agent" "$port"
      curl -s --connect-timeout 2 "http://127.0.0.1:$port/health" || echo "  ❌ Unreachable"
    done
    echo ""
    echo "🏁 Quick Dashboard summary:"
    curl -s "$DASH/health" | (command -v jq >/dev/null 2>&1 && jq . || cat)
    ;;

  status)
    need_cmd curl
    need_token
    echo "📊 Checking system status..."
    curl -s -H "Authorization: Bearer $TOK" "$DASH/api/status/all" | (command -v jq >/dev/null 2>&1 && jq . || cat)
    ;;

  preflight)
    preflight_checks
    rc=$?
    exit $rc
    ;;

  agents:register)
    echo "📝 Registering agents..."
    if [[ -x "$PROJECT_ROOT/scripts/register_agents.py" ]]; then
      python3 "$PROJECT_ROOT/scripts/register_agents.py"
    elif [[ -x "$PROJECT_ROOT/scripts/agents_register.sh" ]]; then
      "$PROJECT_ROOT/scripts/agents_register.sh"
    else
      echo "⚠️  No registration script found. Registering agents via API (requires token)..."
      need_cmd curl
      need_token
      for e in "${AGENTS[@]}"; do
        agent="${e%%:*}"
        rest="${e#*:}"
        port="${rest##*:}"
        echo "Registering $agent -> http://127.0.0.1:$port"
        curl -s -X POST "$DASH/api/agent/register" \
          -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
          -d "{\"agent_id\":\"$agent\",\"endpoint\":\"http://127.0.0.1:$port\"}" | (command -v jq >/dev/null 2>&1 && jq . || cat)
      done
      echo "✅ Agent registration complete"
    fi
    ;;

  eval)
    echo "🧾 Running workspace evaluation (this may take a moment)..."
    if [[ -f "$PROJECT_ROOT/scripts/workspace_evaluation.py" ]]; then
      python3 "$PROJECT_ROOT/scripts/workspace_evaluation.py" --root "$PROJECT_ROOT"
      rc=$?
      if [[ $rc -eq 0 ]]; then
        echo "✅ Evaluation completed: report saved (workspace_evaluation_report.json)"
      else
        echo "⚠ Evaluation completed with issues (exit code $rc). See workspace_evaluation_report.json"
      fi
      exit $rc
    else
      echo "❌ Evaluation script not found: scripts/workspace_evaluation.py"
      exit 1
    fi
    ;;

  verify)
    echo "🔍 Running integration verification..."
    if [[ -x "$PROJECT_ROOT/scripts/verify_stack.sh" ]]; then
      "$PROJECT_ROOT/scripts/verify_stack.sh"
    else
      echo "Running quick verification..."
      "$0" health
      echo ""
      "$0" status
    fi
    ;;

  logs)
    echo "📜 Showing recent logs..."
    tail -n 100 "$PROJECT_ROOT/logs"/*.log 2>/dev/null || echo "No logs found in logs/ directory"
    ;;

  logs:follow)
    echo "📜 Following logs (Ctrl+C to stop)..."
    tail -f "$PROJECT_ROOT/logs"/*.log 2>/dev/null || echo "No logs found in logs/ directory"
    ;;

  restart)
    echo "🔄 Restarting services..."
    "$0" stop
    sleep 2
    "$0" start
    ;;

  monitor)
    echo "🔍 Starting continuous health monitoring (Ctrl+C to stop)..."
    echo ""
    need_cmd curl
    while true; do
      clear
      echo "=== ELION Health Monitor ($(date '+%Y-%m-%d %H:%M:%S')) ==="
      echo ""
      run_for_agents bash -c 'agent="$0"; folder="$1"; port="$2"; \
        HEALTH=$(curl -s -m 2 "http://127.0.0.1:$port/health" 2>/dev/null || echo ""); \
        printf "%-10s %-6s : " "$agent" "$port"; \
        if [[ -n "$HEALTH" ]]; then \
          STATUS=$(echo "$HEALTH" | jq -r .status 2>/dev/null || echo "?" ); \
          echo "$STATUS"; \
        else \
          echo "UNREACHABLE"; \
        fi' 
      echo ""
      echo "Next check in 5s... (Ctrl+C to stop)"
      sleep 5
    done
    ;;

  e2e)
    echo "🧪 Running E2E Option-2-Flow Test..."
    if [[ -x "$PROJECT_ROOT/tests/e2e_option2_flow.sh" ]]; then
      exec "$PROJECT_ROOT/tests/e2e_option2_flow.sh"
    else
      echo "❌ E2E Test script nicht gefunden: tests/e2e_option2_flow.sh"
      exit 1
    fi
    ;;

  doc:agents)
    generate_agents_doc
    ;;

  help|-h|--help)
    usage
    ;;

  *)
    echo "❌ Unknown command: $cmd"
    echo ""
    usage
    exit 1
    ;;
esac
