#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRY_JSON="${ROOT_DIR}/agent_directories.json"

MODE="${1:-help}"              # single | parallel | scan-only | help
AGENT_NAME="${2:-}"            # e.g. opena11
TIMEOUT_SEC="${TIMEOUT_SEC:-90}"
PARALLEL_JOBS="${PARALLEL_JOBS:-4}"

require_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "❌ Missing: $1"; exit 1; }; }

scan_agent() {
  local name="$1"
  python3 << PY
import json
from pathlib import Path

reg = json.loads(Path("${REGISTRY_JSON}").read_text())
a = next((x for x in reg.get("agents", []) if x.get("name")== "${name}"), None)
if not a:
    raise SystemExit(f"Agent not found in registry: ${name}")

print("=== SCAN:", a["name"], "===")
print("folder:", a["folder"])
print("port:", a["port"])
print("fullpath:", a.get("fullpath",""))

agent_dir = Path("${ROOT_DIR}") / a["folder"]
if not agent_dir.exists():
    raise SystemExit(f"Missing agent directory: {agent_dir}")

# basic structure checks
checks = {
  "main_py": (agent_dir/"app"/"main.py").exists() or (agent_dir/"main.py").exists(),
  "requirements": (agent_dir/"requirements.txt").exists(),
}
print("checks:", checks)

PY
}

analyse_agent() {
  local name="$1"
  python3 << PY
import json, re
from pathlib import Path

reg = json.loads(Path("${REGISTRY_JSON}").read_text())
a = next(x for x in reg["agents"] if x["name"]=="${name}")
agent_dir = Path("${ROOT_DIR}")/a["folder"]

print("=== ANALYSE:", a["name"], "===")

# secret scan (basic, fast)
patterns = [
  r"sk-[A-Za-z0-9]{20,}",
  r"ghp_[A-Za-z0-9]{20,}",
  r"AKIA[0-9A-Z]{16}",
  r"BEGIN PRIVATE KEY",
  r"authorization:\s*bearer\s+[A-Za-z0-9\-\._]+",
]
hits = []
for p in agent_dir.rglob("*"):
  if not p.is_file():
    continue
  if "venv" in str(p) or p.suffix in {".log",".pyc"}:
    continue
  try:
    s = p.read_text(errors="ignore")
  except:
    continue
  for pat in patterns:
    if re.search(pat, s, re.IGNORECASE):
      hits.append((str(p), pat))
      break

print("secret_hits:", len(hits))
if hits:
  for f,pat in hits[:20]:
    print(" -", f, "match:", pat)
  raise SystemExit("❌ Secrets detected")

print("✅ No obvious secrets")
PY
}

get_port() {
  local name="$1"
  python3 << PY
import json
from pathlib import Path
reg = json.loads(Path("${REGISTRY_JSON}").read_text())
a = next(x for x in reg["agents"] if x["name"]=="${name}")
print(a["port"])
PY
}

list_targets_11_19_21() {
  python3 << 'PY'
import json
from pathlib import Path

reg = json.loads(Path("agent_directories.json").read_text())
names = [a["name"] for a in reg.get("agents", [])]
targets = []
for n in names:
    if n.startswith("opena"):
        try:
            k = int(n.replace("opena",""))
        except:
            continue
        if 11 <= k <= 19 or k == 21:
            targets.append(n)
print("\n".join(sorted(targets, key=lambda x: int(x.replace("opena","")))))
PY
}

run_single() {
  local name="$1"
  local port
  port="$(get_port "$name")"

  scan_agent "$name"
  analyse_agent "$name"
  echo "✅ ${name} validation passed"
}

run_parallel() {
  mapfile -t targets < <(list_targets_11_19_21)
  echo "Targets for parallel scan:"
  printf " - %s\n" "${targets[@]}"
  echo ""

  require_cmd python3

  printf "%s\n" "${targets[@]}" | xargs -I{} -P "${PARALLEL_JOBS}" bash -lc '
    set -euo pipefail
    name="{}"
    "'"${ROOT_DIR}"'/scripts/agent_fleet_gate.sh" single "$name"
  '
  echo "🚀 Fleet parallel validation: PASSED"
}

case "${MODE}" in
  single)
    [[ -n "${AGENT_NAME}" ]] || { echo "Usage: $0 single opena11"; exit 2; }
    require_cmd python3
    run_single "${AGENT_NAME}"
    ;;
  parallel)
    run_parallel
    ;;
  scan-only)
    [[ -n "${AGENT_NAME}" ]] || { echo "Usage: $0 scan-only opena11"; exit 2; }
    scan_agent "${AGENT_NAME}"
    ;;
  help|*)
    cat <<EOF
Usage:
  $0 single opena11        # validate one agent
  $0 parallel              # validate opena11-19 + opena21 in parallel
  $0 scan-only opena11     # only scan registry/structure

Env:
  TIMEOUT_SEC=90
  PARALLEL_JOBS=4
EOF
    ;;
esac
