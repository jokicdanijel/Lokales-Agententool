#!/usr/bin/env bash
# ==============================================================================
# bin/ops.sh (ELION Hyper-Dashboard Stack Controller) — Production-grade
#
# Contract:
# - Preflight: .env + Port Policy + venv isolation (per agent) + doc generate/validate
# - Start: Core order -> Agent pool best-effort -> verify local -> verify server (best-effort)
# - Ports: only 12344–12399, 8080 forbidden
# - Security: never source .env, whitelist-read keys only
# ==============================================================================

set -euo pipefail
IFS=$'\n\t'

# ------------------------------------------------------------------------------
# Root
# ------------------------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# ------------------------------------------------------------------------------
# ENV (Source of Truth)
# ------------------------------------------------------------------------------
ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/mcp_server/.env.example"

DASHBOARD_PORT="${DASHBOARD_PORT:-12349}"
OPENA1_PORT="${OPENA1_PORT:-12344}"
OPENA2_PORT="${OPENA2_PORT:-12345}"

PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-}"
PUBLIC_BASE_URL_ALT="${PUBLIC_BASE_URL_ALT:-}"

DASH="http://127.0.0.1:${DASHBOARD_PORT}"
OPENA1="http://127.0.0.1:${OPENA1_PORT}"
OPENA2="http://127.0.0.1:${OPENA2_PORT}"

DOC_DIR="$PROJECT_ROOT/docs"
DOC_HTML="$DOC_DIR/agent_startanleitung.html"
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# ------------------------------------------------------------------------------
# Agent mapping: agent_id:folder:port (KANON)
# ------------------------------------------------------------------------------
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

# ==============================================================================
# Helpers
# ==============================================================================
need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "❌ Required command not found: $1"; exit 1; }
}

read_env_kv() {
  local key="$1"
  [[ -f "$ENV_FILE" ]] || return 0
  grep -m1 "^${key}=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'" || true
}

load_env_from_file() {
  [[ -f "$ENV_FILE" ]] || return 0
  DASHBOARD_PORT="$(read_env_kv DASHBOARD_PORT || true)"; [[ -n "${DASHBOARD_PORT:-}" ]] || DASHBOARD_PORT="12349"
  OPENA1_PORT="$(read_env_kv OPENA1_PORT || true)"; [[ -n "${OPENA1_PORT:-}" ]] || OPENA1_PORT="12344"
  OPENA2_PORT="$(read_env_kv OPENA2_PORT || true)"; [[ -n "${OPENA2_PORT:-}" ]] || OPENA2_PORT="12345"

  TOK="$(read_env_kv DASHBOARD_ADMIN_TOKEN || true)"; TOK="${TOK:-}"
  PUBLIC_BASE_URL="$(read_env_kv PUBLIC_BASE_URL || true)"; PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-}"
  PUBLIC_BASE_URL_ALT="$(read_env_kv PUBLIC_BASE_URL_ALT || true)"; PUBLIC_BASE_URL_ALT="${PUBLIC_BASE_URL_ALT:-}"

  DASH="http://127.0.0.1:${DASHBOARD_PORT}"
  OPENA1="http://127.0.0.1:${OPENA1_PORT}"
  OPENA2="http://127.0.0.1:${OPENA2_PORT}"
}

need_token() {
  [[ -n "${TOK:-}" ]] || { echo "❌ No token found. Create/fill $PROJECT_ROOT/.env (DASHBOARD_ADMIN_TOKEN)"; exit 1; }
}

ensure_env_prepared() {
  echo "🔐 Preflight: .env prüfen..."
  if [[ ! -f "$ENV_FILE" ]]; then
    echo "⚠️  .env nicht gefunden: $ENV_FILE"
    echo "➡️  Kopiere Vorlage:"
    echo "    cp \"$ENV_EXAMPLE\" \"$ENV_FILE\""
    if [[ -f "$ENV_EXAMPLE" ]]; then
      cp "$ENV_EXAMPLE" "$ENV_FILE"
      chmod 600 "$ENV_FILE" || true
      echo "✅ .env aus Vorlage erstellt."
      echo "⚠️  WICHTIG: Jetzt Secrets setzen:"
      echo "    - DASHBOARD_ADMIN_TOKEN"
      echo "    - OPENAI_API_KEY_OPENA1"
      echo "    - OPENAI_API_KEY_OPENA2"
      echo "➡️  Edit: nano \"$ENV_FILE\""
      exit 1
    else
      echo "❌ Vorlage fehlt: $ENV_EXAMPLE"
      exit 1
    fi
  fi
  chmod 600 "$ENV_FILE" || true
  load_env_from_file
  echo "✅ .env vorhanden."
}

policy_port_range_check() {
  echo "🔍 Policy: Port Range prüfen (12344–12399), 8080 verboten..."
  local bad=0

  for e in "${AGENTS[@]}"; do
    local rest="${e#*:}"
    local port="${rest##*:}"
    if [[ "$port" == "8080" ]]; then
      echo "❌ Policy-Fail: 8080 in Agent-Mapping"
      bad=1
    fi
    if (( port < 12344 || port > 12399 )); then
      echo "❌ Policy-Fail: Port außerhalb Range im Mapping: $port"
      bad=1
    fi
  done

  for p in "${DASHBOARD_PORT}" "${OPENA1_PORT}" "${OPENA2_PORT}"; do
    [[ -z "${p:-}" ]] && continue
    if [[ "$p" == "8080" ]]; then
      echo "❌ Policy-Fail: 8080 in .env"
      bad=1
    fi
    if (( p < 12344 || p > 12399 )); then
      echo "❌ Policy-Fail: Port außerhalb Range in .env: $p"
      bad=1
    fi
  done

  [[ "$bad" -eq 0 ]] || exit 1
  echo "✅ Port-Policy ok."
}

port_listening() {
  local port="$1"
  # Portable: avoid awk (some awk variants choke on gawk-only features used elsewhere)
  ss -H -ltn "( sport = :${port} )" 2>/dev/null | grep -q .
}

pid_for_port() {
  # best-effort parse from ss -ltnp output
  local port="$1"
  ss -H -ltnp 2>/dev/null \
    | grep -F ":${port}" \
    | grep -oE 'pid=[0-9]+' \
    | head -n 1 \
    | cut -d= -f2 || true
}

health_ok_local() {
  local port="$1"
  curl -fsS --connect-timeout 2 "http://127.0.0.1:${port}/health" >/dev/null 2>&1
}

health_ok_external() {
  local base="$1"
  local agent="$2"
  curl -fsS --connect-timeout 4 "${base}/${agent}/health" >/dev/null 2>&1
}

agent_lookup() {
  # prints: folder port
  local want="$1"
  for e in "${AGENTS[@]}"; do
    local agent="${e%%:*}"
    local rest="${e#*:}"
    local folder="${rest%%:*}"
    local port="${rest##*:}"
    if [[ "$agent" == "$want" ]]; then
      echo "$folder $port"
      return 0
    fi
  done
  return 1
}

# ------------------------------------------------------------------------------
# Per-agent venv (Isolation = weniger Chaos)
# ------------------------------------------------------------------------------
agent_venv_paths() {
  local agent_dir="$1"
  # returns on separate lines
  echo "$agent_dir/.venv"
  echo "$agent_dir/.venv/bin/python"
  echo "$agent_dir/.venv/bin/pip"
}

ensure_agent_venv() {
  local agent="$1"
  local agent_dir="$2"

  need_cmd python3

  # Build paths directly
  local venv_dir="$agent_dir/.venv"
  local vpy="$agent_dir/.venv/bin/python"
  local vpip="$agent_dir/.venv/bin/pip"

  if [[ ! -x "$vpy" ]]; then
    echo "🐍 [$agent] Erzeuge venv: $venv_dir"
    python3 -m venv "$venv_dir"
    "$vpy" -m pip install -U pip wheel setuptools >/dev/null
  fi

  # Install deps best-effort (requirements.txt preferred)
  if [[ -f "$agent_dir/requirements.txt" ]]; then
    echo "📦 [$agent] pip install -r requirements.txt"
    PYTHONNOUSERSITE=1 "$vpip" install -r "$agent_dir/requirements.txt" >/dev/null
  elif [[ -f "$agent_dir/pyproject.toml" ]]; then
    echo "📦 [$agent] pip install . (pyproject)"
    PYTHONNOUSERSITE=1 "$vpip" install "$agent_dir" >/dev/null
  else
    # Minimal baseline to avoid pydantic drift for typical agents (safe)
    echo "📦 [$agent] Baseline deps (minimal)"
    PYTHONNOUSERSITE=1 "$vpip" install "pydantic>=2.6,<3" "pydantic-settings>=2.2,<3" >/dev/null || true
  fi
}

# ------------------------------------------------------------------------------
# Start/Stop: generic agent runner
# ------------------------------------------------------------------------------
start_agent_generic() {
  local agent="$1"
  local folder="$2"
  local port="$3"
  local agent_dir="$PROJECT_ROOT/$folder"
  local pidfile="$LOG_DIR/${agent}.pid"
  local logfile="$LOG_DIR/${agent}.nohup.log"

  if [[ ! -d "$agent_dir" ]]; then
    echo "⚠️  [$agent] Verzeichnis fehlt: $folder"
    return 0
  fi

  # already running?
  if port_listening "$port"; then
    echo "✅ [$agent] already listening on :$port"
    local p; p="$(pid_for_port "$port" || true)"
    [[ -n "$p" ]] && echo "$p" > "$pidfile" || true
    return 0
  fi

  # Prefer explicit start scripts
  if [[ -x "$agent_dir/bin/start_${agent}.sh" ]]; then
    echo "🔹 [$agent] via $folder/bin/start_${agent}.sh"
    (
      cd "$agent_dir"
      # Run start script with explicit per-command env (no global side effects)
      env \
        BEARER_TOKEN="${BEARER_TOKEN:-}" \
        OPENA3_BEARER_TOKEN="${OPENA3_BEARER_TOKEN:-}" \
        OPENA4_BEARER_TOKEN="${OPENA4_BEARER_TOKEN:-}" \
        OPENA5_BEARER_TOKEN="${OPENA5_BEARER_TOKEN:-}" \
        OPENA6_BEARER_TOKEN="${OPENA6_BEARER_TOKEN:-}" \
        OPENA7_BEARER_TOKEN="${OPENA7_BEARER_TOKEN:-}" \
        OPENA8_BEARER_TOKEN="${OPENA8_BEARER_TOKEN:-}" \
        OPENA9_BEARER_TOKEN="${OPENA9_BEARER_TOKEN:-}" \
        ./bin/start_"${agent}".sh
    ) || true
    sleep 1
    if port_listening "$port"; then
      local p; p="$(pid_for_port "$port" || true)"
      [[ -n "$p" ]] && echo "$p" > "$pidfile" || true
      echo "✅ [$agent] started (port :$port)"
    else
      echo "⚠️  [$agent] start script finished but port :$port not listening (check logs)"
    fi
    return 0
  fi

  if [[ -x "$agent_dir/bin/start.sh" ]]; then
    echo "🔹 [$agent] via $folder/bin/start.sh"
    (
      cd "$agent_dir"
      # Run start script with explicit per-command env (no global side effects)
      env \
        BEARER_TOKEN="${BEARER_TOKEN:-}" \
        OPENA3_BEARER_TOKEN="${OPENA3_BEARER_TOKEN:-}" \
        OPENA4_BEARER_TOKEN="${OPENA4_BEARER_TOKEN:-}" \
        OPENA5_BEARER_TOKEN="${OPENA5_BEARER_TOKEN:-}" \
        OPENA6_BEARER_TOKEN="${OPENA6_BEARER_TOKEN:-}" \
        OPENA7_BEARER_TOKEN="${OPENA7_BEARER_TOKEN:-}" \
        OPENA8_BEARER_TOKEN="${OPENA8_BEARER_TOKEN:-}" \
        OPENA9_BEARER_TOKEN="${OPENA9_BEARER_TOKEN:-}" \
        bin/start.sh
    ) || true
    sleep 1
    if port_listening "$port"; then
      local p; p="$(pid_for_port "$port" || true)"
      [[ -n "$p" ]] && echo "$p" > "$pidfile" || true
      echo "✅ [$agent] started (port :$port)"
    else
      echo "⚠️  [$agent] start.sh finished but port :$port not listening (check logs)"
    fi
    return 0
  fi

  # Otherwise run Python main_*.py via isolated venv
  ensure_agent_venv "$agent" "$agent_dir"

  # Build venv paths directly
  local venv_dir="$agent_dir/.venv"
  local vpy="$agent_dir/.venv/bin/python"
  local vpip="$agent_dir/.venv/bin/pip"

  local mainpy
  mainpy="$(ls "$agent_dir"/main_*.py 2>/dev/null | head -n1 || true)"
  if [[ -z "$mainpy" ]]; then
    echo "⚠️  [$agent] Kein Startskript und keine main_*.py gefunden."
    return 0
  fi

  echo "🔹 [$agent] via venv python $(basename "$mainpy") (port :$port)"
  # Make script-style imports reliable
  # Also pass PORT both as env and as --port (agents can pick either).
  (
    cd "$agent_dir"
    export PYTHONNOUSERSITE=1
    export PORT="$port"
    export AGENT_ID="$agent"
    export PYTHONPATH="$agent_dir:${PYTHONPATH:-}"
    nohup "$vpy" "$mainpy" --port "$port" > "$logfile" 2>&1 &
    echo $! > "$pidfile"
  )
  echo "✅ [$agent] launched (PID: $(cat "$pidfile"))"
}

stop_agent_generic() {
  local agent="$1"
  local folder="$2"
  local port="$3"
  local pidfile="$LOG_DIR/${agent}.pid"

  # Try pidfile first
  if [[ -f "$pidfile" ]]; then
    local pid
    pid="$(cat "$pidfile" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 0.8
      kill -9 "$pid" 2>/dev/null || true
      rm -f "$pidfile"
      echo "✅ [$agent] stopped via pidfile (PID: $pid)"
      return 0
    fi
    rm -f "$pidfile" || true
  fi

  # Fallback: kill by port PID (more precise than pkill folder-name nuking)
  local p; p="$(pid_for_port "$port" || true)"
  if [[ -n "$p" ]] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 0.8
    kill -9 "$p" 2>/dev/null || true
    echo "✅ [$agent] stopped via port :$port (PID: $p)"
    return 0
  fi

  # last resort: pkill by agent name (best-effort)
  pkill -f "$agent" 2>/dev/null || true
  echo "⚠️  [$agent] no pid found; best-effort pkill executed"
}

# ------------------------------------------------------------------------------
# Iterate agents
# ------------------------------------------------------------------------------
run_for_agents() {
  # callback receives agent folder port
  for e in "${AGENTS[@]}"; do
    local agent="${e%%:*}"
    local rest="${e#*:}"
    local folder="${rest%%:*}"
    local port="${rest##*:}"
    "$@" "$agent" "$folder" "$port"
  done
}

# ==============================================================================
# HTML Runbook Generator
# ==============================================================================
generate_agents_doc() {
  mkdir -p "$DOC_DIR"
  load_env_from_file
  [[ -n "${PUBLIC_BASE_URL:-}" ]] || PUBLIC_BASE_URL="https://hyperdashboard-one.de"

  {
    cat <<'HTML'
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
    .pill.warn{border-color:rgba(255,209,102,.35);color:var(--warn)}
    .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}
    pre{margin:10px 0 0;padding:12px;border-radius:12px;background:#0a0f16;border:1px solid var(--border);overflow:auto}
    table{width:100%;border-collapse:separate;border-spacing:0;overflow:hidden;border-radius:12px;border:1px solid var(--border)}
    th,td{padding:10px 10px;border-bottom:1px solid var(--border);vertical-align:top}
    th{background:#0a0f16;color:var(--muted);text-align:left;font-weight:600}
    tr:last-child td{border-bottom:none}
    a{color:var(--acc);text-decoration:none}
    a:hover{text-decoration:underline}
    .toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 0}
    input[type="search"]{flex:1;min-width:240px;background:#0a0f16;color:var(--txt);border:1px solid var(--border);border-radius:10px;padding:10px}
    .btn{background:#0a0f16;color:var(--txt);border:1px solid var(--border);border-radius:10px;padding:10px 12px;cursor:pointer}
    .btn:hover{border-color:#2b3d58}
    .note{border-left:3px solid var(--acc);padding:8px 10px;background:rgba(110,231,255,.06);border-radius:10px;color:var(--muted);margin-top:10px}
    .note strong{color:var(--txt)}
  </style>
</head>
<body>
<header>
  <h1>ELION Hyper-Dashboard – Agenten Runbook (Local + Server)</h1>
  <p>
    Offline-fähiges Runbook (keine externen Assets). "Gestaltung" extern kommt durch Reverse Proxy Routing:
    <b>/openaX/</b> → <span class="mono">127.0.0.1:PORT</span> mit Prefix-Stripping.
  </p>
</header>

<main>
  <section class="card">
    <h2>0) ENV Setup (bindend)</h2>
    <span class="pill ok"><b>Quelle</b>: <span class="mono">mcp_server/.env.example</span></span>
    <span class="pill warn"><b>Wichtig</b>: <span class="mono">.env</span> enthält Secrets</span>
    <pre><code>cd PROJECT_ROOT

# Falls .env fehlt:
cp mcp_server/.env.example .env
nano .env

# Muss gesetzt sein:
# - DASHBOARD_ADMIN_TOKEN
# - OPENAI_API_KEY_OPENA1
# - OPENAI_API_KEY_OPENA2</code></pre>
  </section>

  <section class="card">
    <h2>1) Standard-Flow (Production)</h2>
    <pre><code>cd PROJECT_ROOT

bin/ops.sh doc:agents
bin/ops.sh venv:sync opena4
bin/ops.sh start:agent opena4
curl -s http://127.0.0.1:12348/health | jq .</code></pre>
  </section>

  <section class="card">
    <h2>2) Agentenübersicht (Ports, Links, Start)</h2>
    <div class="toolbar">
      <input id="filter" type="search" placeholder="Filter… z.B. opena8, whatsapp, 12349, browsep" />
      <button class="btn" onclick="resetFilter()">Reset</button>
    </div>

    <table id="agentsTable">
      <thead>
        <tr>
          <th>Agent</th>
          <th>Ordner</th>
          <th>Port</th>
          <th>Lokal /health</th>
          <th>Server URL (PUBLIC_BASE_URL)</th>
          <th>Start (exakt)</th>
        </tr>
      </thead>
      <tbody>
HTML

    for e in "${AGENTS[@]}"; do
      agent="${e%%:*}"
      rest="${e#*:}"
      folder="${rest%%:*}"
      port="${rest##*:}"
      folder_html="${folder//&/&amp;}"
      base="${PUBLIC_BASE_URL%/}"

      cat <<ROW
        <tr>
          <td class="mono">${agent}</td>
          <td class="mono">${folder_html}</td>
          <td class="mono">${port}</td>
          <td class="mono"><a href="http://127.0.0.1:${port}/health">http://127.0.0.1:${port}/health</a></td>
          <td class="mono"><a href="${base}/${agent}/">${base}/${agent}/</a></td>
          <td class="mono">bin/ops.sh start:agent ${agent}</td>
        </tr>
ROW
    done

    cat <<'HTML2'
      </tbody>
    </table>

    <div class="note">
      <strong>Pro Tip:</strong> Wenn ein Agent als Script läuft, dürfen keine <span class="mono">from .xyz</span> Imports drin sein.
      Nutze absolute Imports (aus dem Agent-Ordner) + <span class="mono">sys.path.insert(0, os.path.dirname(__file__))</span>.
    </div>
  </section>

  <section class="card">
    <h2>3) Per-Agent Workflow</h2>
    <pre><code># venv isolation + deps
bin/ops.sh venv:sync opena4

# Start einzelner Agent
bin/ops.sh start:agent opena4

# Health check
curl -s http://127.0.0.1:12348/health | jq .

# Logs
tail -n 200 logs/opena4.nohup.log

# Stop
bin/ops.sh stop:agent opena4</code></pre>
  </section>

<script>
  const filter = document.getElementById('filter');
  const table = document.getElementById('agentsTable');

  function rowText(tr){ return tr.innerText.toLowerCase(); }
  function applyFilter(){
    const q = (filter.value || '').trim().toLowerCase();
    Array.from(table.querySelectorAll('tbody tr')).forEach(tr=>{
      tr.style.display = (!q || rowText(tr).includes(q)) ? '' : 'none';
    });
  }
  function resetFilter(){ filter.value=''; applyFilter(); }

  if(filter){
    filter.addEventListener('input', applyFilter);
    window.resetFilter = resetFilter;
  }
</script>

</main>
</body>
</html>
HTML2
  } > "$DOC_HTML"

  echo "✅ HTML erzeugt: $DOC_HTML"
}

validate_agents_doc() {
  echo "🔍 Validierung: $DOC_HTML"
  [[ -f "$DOC_HTML" ]] || { echo "❌ HTML fehlt: $DOC_HTML"; exit 1; }
  [[ -s "$DOC_HTML" ]] || { echo "❌ HTML ist leer: $DOC_HTML"; exit 1; }

  grep -q "<!doctype html>" "$DOC_HTML" || { echo "❌ HTML invalid: missing <!doctype html>"; exit 1; }
  grep -q "</html>" "$DOC_HTML" || { echo "❌ HTML invalid: missing </html>"; exit 1; }

  for i in $(seq 1 20); do
    grep -q "opena${i}" "$DOC_HTML" || { echo "❌ HTML invalid: missing opena${i}"; exit 1; }
  done

  grep -q "http://127.0.0.1:12344/health" "$DOC_HTML" || { echo "❌ HTML invalid: missing local health link for opena1"; exit 1; }
  grep -q "/opena1/" "$DOC_HTML" || { echo "❌ HTML invalid: missing /opena1/ route"; exit 1; }

  if grep -qE '(^|[^0-9])8080([^0-9]|$)' "$DOC_HTML"; then
    echo "❌ HTML invalid: contains forbidden port 8080"
    exit 1
  fi

  local bad_ports=""
  while IFS= read -r p; do
    [[ -z "$p" ]] && continue
    if (( p < 12344 || p > 12399 )); then
      bad_ports+="$p"$'\n'
    fi
  done < <(grep -oE '127\.0\.0\.1:[0-9]{4,5}' "$DOC_HTML" | cut -d: -f2 | sort -n | uniq)

  if [[ -n "$bad_ports" ]]; then
    echo "❌ HTML invalid: ports outside 12344–12399 found:"
    echo "$bad_ports" | sed '/^$/d'
    exit 1
  fi

  echo "✅ HTML valid."
}

# ==============================================================================
# Verify (Local/Server)
# ==============================================================================
verify_local() {
  need_cmd curl
  echo "🏥 Verify Local: opena1–opena20 /health"
  local degraded=0

  for e in "${AGENTS[@]}"; do
    local agent="${e%%:*}"
    local rest="${e#*:}"
    local port="${rest##*:}"

    if [[ "$agent" =~ ^opena([1-9]|1[0-9]|20)$ ]]; then
      if health_ok_local "$port"; then
        echo "  ✅ ${agent} (127.0.0.1:${port})"
      else
        echo "  ❌ ${agent} (127.0.0.1:${port}) not responding"
        degraded=1
      fi
    fi
  done

  [[ "$degraded" -eq 0 ]] || { echo "❌ Local verification failed."; exit 1; }
  echo "✅ Local verification OK."
}

verify_server() {
  need_cmd curl
  load_env_from_file
  [[ -n "${PUBLIC_BASE_URL:-}" ]] || PUBLIC_BASE_URL="https://hyperdashboard-one.de"
  local base="${PUBLIC_BASE_URL%/}"
  local alt="${PUBLIC_BASE_URL_ALT%/}"

  echo "🌍 Verify Server: opena1–opena20 /openaX/health"
  echo "  Base: ${base}"
  [[ -n "${PUBLIC_BASE_URL_ALT:-}" ]] && echo "  Alt:  ${alt}"

  local any_fail=0
  for i in $(seq 1 20); do
    local agent="opena${i}"
    if health_ok_external "$base" "$agent"; then
      echo "  ✅ ${agent} via ${base}/${agent}/health"
    else
      if [[ -n "${PUBLIC_BASE_URL_ALT:-}" ]] && health_ok_external "$alt" "$agent"; then
        echo "  ✅ ${agent} via ${alt}/${agent}/health"
      else
        echo "  ⚠️  ${agent} external check failed (Proxy 404/502/timeout)"
        any_fail=1
      fi
    fi
  done

  if [[ "$any_fail" -eq 1 ]]; then
    echo "⚠️  External verification has failures. Typical causes:"
    echo "   - 502: Proxy maps to wrong port or service down"
    echo "   - 404: Missing location block or missing rewrite"
    echo "   - timeout: firewall/network/service hang"
    echo "ℹ️  Local stack can still be OK."
  else
    echo "✅ Server verification OK."
  fi
}

# ==============================================================================
# Usage
# ==============================================================================
usage() {
  cat <<'USAGE'
ELION Hyper-Dashboard OPS – Stack Controller

Commands:
  start                 - Preflight + docs + core + pool + verify local + verify server (best-effort)
  stop                  - Stop all (PID->port PID->best-effort)
  restart               - Stop then start

  start:agent <id>      - Start a single agent (e.g. opena4)
  stop:agent <id>       - Stop a single agent
  restart:agent <id>    - Restart a single agent

  venv:sync <id|all>    - Ensure per-agent venv + install deps

  verify                - verify:local then verify:server
  verify:local          - Local health verification opena1–opena20
  verify:server         - External verification /openaX/health (PUBLIC_BASE_URL)

  doc:agents            - Generate docs/agent_startanleitung.html
  doc:validate          - Validate docs/agent_startanleitung.html

  health                - Quick health dump for all mapped agents
  status                - Dashboard status via API (requires DASHBOARD_ADMIN_TOKEN)
  agents:register       - Register agents with dashboard
  logs                  - Tail recent logs
  logs:follow           - Follow logs
  monitor               - Continuous health monitor

  help                  - Show this help
USAGE
}

# ==============================================================================
# Command Handlers
# ==============================================================================
[[ $# -lt 1 ]] && { usage; exit 1; }
cmd="$1"; shift || true

case "$cmd" in
  doc:agents)
    ensure_env_prepared
    policy_port_range_check
    generate_agents_doc
    ;;

  doc:validate)
    validate_agents_doc
    ;;

  verify:local)
    verify_local
    ;;

  verify:server)
    verify_server
    ;;

  verify)
    verify_local
    verify_server
    ;;

  venv:sync)
    ensure_env_prepared
    policy_port_range_check
    target="${1:-all}"
    if [[ "$target" == "all" ]]; then
      echo "🐍 venv:sync all agents..."
      for e in "${AGENTS[@]}"; do
        agent="${e%%:*}"
        rest="${e#*:}"
        folder="${rest%%:*}"
        dir="$PROJECT_ROOT/$folder"
        [[ -d "$dir" ]] || continue
        ensure_agent_venv "$agent" "$dir"
      done
      echo "✅ venv sync all done."
    else
      if ! result="$(agent_lookup "$target")"; then
        echo "❌ Unknown agent: $target"
        exit 3
      fi
      read -r folder port <<<"$result"
      dir="$PROJECT_ROOT/$folder"
      ensure_agent_venv "$target" "$dir"
      echo "✅ venv sync done for $target."
    fi
    ;;

  start:agent)
    need_cmd curl
    need_cmd ss
    ensure_env_prepared
    policy_port_range_check
    agent_id="${1:-}"
    [[ -n "$agent_id" ]] || { echo "❌ Missing agent id"; exit 1; }
    if ! result="$(agent_lookup "$agent_id")"; then
      echo "❌ Unknown agent: $agent_id"
      exit 3
    fi
    read -r folder port <<<"$result"
    start_agent_generic "$agent_id" "$folder" "$port"
    ;;

  stop:agent)
    need_cmd ss
    ensure_env_prepared
    policy_port_range_check
    agent_id="${1:-}"
    [[ -n "$agent_id" ]] || { echo "❌ Missing agent id"; exit 1; }
    if ! result="$(agent_lookup "$agent_id")"; then
      echo "❌ Unknown agent: $agent_id"
      exit 3
    fi
    read -r folder port <<<"$result"
    stop_agent_generic "$agent_id" "$folder" "$port"
    ;;

  restart:agent)
    need_cmd curl
    need_cmd ss
    ensure_env_prepared
    policy_port_range_check
    agent_id="${1:-}"
    [[ -n "$agent_id" ]] || { echo "❌ Missing agent id"; exit 1; }
    if ! result="$(agent_lookup "$agent_id")"; then
      echo "❌ Unknown agent: $agent_id"
      exit 3
    fi
    read -r folder port <<<"$result"
    stop_agent_generic "$agent_id" "$folder" "$port"
    sleep 1
    start_agent_generic "$agent_id" "$folder" "$port"
    ;;

  start)
    need_cmd curl
    need_cmd ss

    ensure_env_prepared
    policy_port_range_check

    echo "📄 Runbook: Generiere HTML..."
    generate_agents_doc
    echo "🔍 Runbook: Validierung..."
    validate_agents_doc

    # Export OpenAI Keys whitelisted
    OPENAI_API_KEY_OPENA1="$(read_env_kv OPENAI_API_KEY_OPENA1 || true)"
    OPENAI_API_KEY_OPENA2="$(read_env_kv OPENAI_API_KEY_OPENA2 || true)"
    export OPENAI_API_KEY_OPENA1 OPENAI_API_KEY_OPENA2

    if [[ -z "${OPENAI_API_KEY_OPENA1:-}" ]] || [[ -z "${OPENAI_API_KEY_OPENA2:-}" ]]; then
      echo "⚠️  OpenAI Keys nicht vollständig in .env (opena1/opena2)."
    fi

    echo ""
    echo "=== Starting Core Services (Order matters) ==="

    # opena1 + opena2 (folder has its own scripts)
    cd "$PROJECT_ROOT/1.opena1&2_portier"
    if [[ -x "bin/start_opena1_with_key.sh" ]]; then
      echo "🔹 opena1 (Port 12344)..."
      ./bin/start_opena1_with_key.sh || true
      sleep 1
      p="$(pid_for_port 12344 || true)"; [[ -n "$p" ]] && echo "$p" > "$LOG_DIR/opena1.pid" || true
    else
      echo "⚠️  bin/start_opena1_with_key.sh nicht gefunden"
    fi

    if [[ -x "bin/start_opena2_with_key.sh" ]]; then
      echo "🔹 opena2 (Port 12345)..."
      ./bin/start_opena2_with_key.sh || true
      sleep 1
      p="$(pid_for_port 12345 || true)"; [[ -n "$p" ]] && echo "$p" > "$LOG_DIR/opena2.pid" || true
    else
      echo "⚠️  bin/start_opena2_with_key.sh nicht gefunden"
    fi

    # Dashboard opena20 (run via isolated venv too)
    cd "$PROJECT_ROOT"
    if [[ -f "19.opena20_dashboard_agent/main_dashboard.py" ]]; then
      echo "🔹 Dashboard (opena20) (Port 12349)..."
      start_agent_generic "opena20" "19.opena20_dashboard_agent" "12349" || true
    fi

    sleep 2

    echo ""
    echo "=== Starting available agents (best-effort) ==="

    # Export all BEARER_TOKENs for child processes
    export BEARER_TOKEN="${BEARER_TOKEN:-}"
    export OPENA3_BEARER_TOKEN="$(read_env_kv OPENA3_BEARER_TOKEN || true)"
    export OPENA4_BEARER_TOKEN="$(read_env_kv OPENA4_BEARER_TOKEN || true)"
    export OPENA5_BEARER_TOKEN="$(read_env_kv OPENA5_BEARER_TOKEN || true)"
    export OPENA6_BEARER_TOKEN="$(read_env_kv OPENA6_BEARER_TOKEN || true)"
    export OPENA7_BEARER_TOKEN="$(read_env_kv OPENA7_BEARER_TOKEN || true)"
    export OPENA8_BEARER_TOKEN="$(read_env_kv OPENA8_BEARER_TOKEN || true)"
    export OPENA9_BEARER_TOKEN="$(read_env_kv OPENA9_BEARER_TOKEN || true)"

    for e in "${AGENTS[@]}"; do
      agent="${e%%:*}"
      rest="${e#*:}"
      folder="${rest%%:*}"
      port="${rest##*:}"

      # skip duplicates core already started
      if [[ "$agent" == "opena1" || "$agent" == "opena2" || "$agent" == "opena20" ]]; then
        continue
      fi

      start_agent_generic "$agent" "$folder" "$port" || true
    done

    echo ""
    echo "=== Verify Local ==="
    verify_local

    echo ""
    echo "=== Verify Server (best-effort) ==="
    verify_server

    echo ""
    echo "✅ Stack gestartet. Runbook: docs/agent_startanleitung.html"
    ;;

  stop)
    need_cmd ss
    echo "🛑 Stopping ELION Hyper-Dashboard services..."
    for e in "${AGENTS[@]}"; do
      agent="${e%%:*}"
      rest="${e#*:}"
      folder="${rest%%:*}"
      port="${rest##*:}"
      stop_agent_generic "$agent" "$folder" "$port" || true
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
    ensure_env_prepared
    need_token
    echo "📊 Checking system status..."
    curl -s -H "Authorization: Bearer $TOK" "$DASH/api/status/all" | (command -v jq >/dev/null 2>&1 && jq . || cat)
    ;;

  agents:register)
    echo "📝 Registering agents..."
    need_cmd curl
    ensure_env_prepared
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
    ;;

  logs)
    echo "📜 Showing recent logs..."
    tail -n 120 "$LOG_DIR"/*.log 2>/dev/null || echo "No logs found in logs/ directory"
    ;;

  logs:follow)
    echo "📜 Following logs (Ctrl+C to stop)..."
    tail -f "$LOG_DIR"/*.log 2>/dev/null || echo "No logs found in logs/ directory"
    ;;

  restart)
    echo "🔄 Restarting services..."
    "$0" stop
    sleep 2
    "$0" start
    ;;

  monitor)
    need_cmd curl
    echo "🔍 Starting continuous health monitoring (Ctrl+C to stop)..."
    while true; do
      clear
      echo "=== ELION Health Monitor ($(date '+%Y-%m-%d %H:%M:%S')) ==="
      echo ""
      for e in "${AGENTS[@]}"; do
        agent="${e%%:*}"
        rest="${e#*:}"
        port="${rest##*:}"
        HEALTH="$(curl -s -m 2 "http://127.0.0.1:$port/health" 2>/dev/null || true)"
        printf "%-10s %-6s : " "$agent" "$port"
        if [[ -n "$HEALTH" ]]; then
          if command -v jq >/dev/null 2>&1; then
            echo "$HEALTH" | jq -r '.status // "OK"' 2>/dev/null || echo "OK"
          else
            echo "OK"
          fi
        else
          echo "UNREACHABLE"
        fi
      done
      echo ""
      echo "Next check in 5s... (Ctrl+C to stop)"
      sleep 5
    done
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
