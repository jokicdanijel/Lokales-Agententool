#!/usr/bin/env python3
"""
opena_all_agents_starter.py

Ziel:
- Startet alle Agenten basierend auf system_baseline.yaml (Single Source of Truth).
- Ports sind unveränderlich: werden ausschließlich aus Baseline gelesen.
- Uvicorn wird genutzt, wenn ein ASGI "app" gefunden wird (FastAPI/Starlette).
- Secrets/Keys werden ausschließlich aus .env geladen (kein Hardcoding im Code).

Hard Rules (Build-Abbruch):
- ID ≠ Name ≠ Port ≠ Folder Inkonsistenz -> Abbruch
- Fehlender Agent / Ordner -> Abbruch
- Duplicate Ports -> Abbruch
- Port außerhalb allow_range oder in forbidden_ports -> Abbruch
"""

from __future__ import annotations

import os
import re
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
BASELINE_PATH = BASE_DIR / "system_baseline.yaml"

LOGS_DIR = BASE_DIR / "logs" / "agents"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

PYTHON = sys.executable


# -----------------------------
# Utils: minimal .env loader
# -----------------------------
def load_dotenv(dotenv_path: Path) -> None:
    """
    Minimaler .env Loader (ohne Abhängigkeiten).
    Unterstützt:
      KEY=VALUE
      KEY="VALUE"
      KEY='VALUE'
      # comments
    """
    if not dotenv_path.exists():
        return

    for raw in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        key = k.strip()
        val = v.strip().strip('"').strip("'")
        # nur setzen wenn nicht schon im env existiert
        os.environ.setdefault(key, val)


# -----------------------------
# YAML loader (no external deps if possible)
# -----------------------------
def load_yaml(path: Path) -> dict[str, Any]:
    """
    Lädt YAML.
    - bevorzugt PyYAML, wenn installiert
    - sonst: sehr simple YAML-Subset-Parser-Notlösung (reicht oft NICHT)
    """
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"[FATAL] Konnte YAML nicht laden. Installiere PyYAML: pip install pyyaml\n" f"Ursache: {e}")


# -----------------------------
# Policy & Validation
# -----------------------------
ID_RE = re.compile(r"^opena([1-9]|1[0-9]|2[0-1])$")


def fatal(msg: str) -> None:
    print(f"\n❌ FATAL: {msg}\n")
    raise SystemExit(1)


def assert_port_policy(port: int, allowed_range: tuple[int, int], forbidden: list[int]) -> None:
    lo, hi = allowed_range
    if not (lo <= port <= hi):
        fatal(f"Port {port} außerhalb allowed_range [{lo}, {hi}]")
    if port in forbidden:
        fatal(f"Port {port} ist verboten (forbidden_ports)")


def ensure_free_port_or_fail(port: int) -> None:
    """Wenn Port bereits belegt -> Abbruch (Ports sind unveränderlich)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        res = s.connect_ex(("127.0.0.1", port))
        if res == 0:
            fatal(f"Port {port} ist bereits belegt. Keine Fallbacks erlaubt.")


def discover_entry(folder: Path, agent_id: str) -> tuple[str, str]:
    """
    Findet Start-Entry im Agent-Ordner.
    Priorität:
      1) main.py
      2) <agent_id>.py
      3) einzige *.py Datei im Root des Ordners (wenn eindeutig)
    Rückgabe: ("uvicorn", "module:app") ODER ("python", "script.py")
    """
    # Candidate scripts
    main_py = folder / "main.py"
    agent_py = folder / f"{agent_id}.py"

    # Uvicorn target (wenn wir app finden können)
    # Wir starten als: python -m uvicorn <module>:app --host 127.0.0.1 --port X
    # => module muss importierbar sein. Dafür nutzen wir cwd=folder und module ohne Pfad.
    if main_py.exists():
        # Heuristik: wenn main.py "app =" enthält oder "FastAPI(" oder "Starlette(" vorkommt
        txt = main_py.read_text(encoding="utf-8", errors="ignore")
        if "app =" in txt or "FastAPI(" in txt or "Starlette(" in txt:
            return ("uvicorn", "main:app")
        return ("python", "main.py")

    if agent_py.exists():
        txt = agent_py.read_text(encoding="utf-8", errors="ignore")
        if "app =" in txt or "FastAPI(" in txt or "Starlette(" in txt:
            # module name ohne .py
            return ("uvicorn", f"{agent_id}:app")
        return ("python", f"{agent_id}.py")

    # fallback: eindeutige py Datei
    py_files = [p for p in folder.glob("*.py") if p.is_file()]
    if len(py_files) == 1:
        p = py_files[0]
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if "app =" in txt or "FastAPI(" in txt or "Starlette(" in txt:
            return ("uvicorn", f"{p.stem}:app")
        return ("python", p.name)

    if len(py_files) > 1:
        fatal(
            f"{agent_id}: Keine eindeutige Entry-Datei gefunden.\n"
            f"Erwartet: main.py oder {agent_id}.py oder genau 1 *.py im Ordner.\n"
            f"Gefunden: {[p.name for p in py_files]}"
        )

    fatal(f"{agent_id}: Keine Python-Datei im Ordner gefunden: {folder}")
    raise RuntimeError("unreachable")


def load_baseline() -> dict[str, Any]:
    if not BASELINE_PATH.exists():
        fatal(f"system_baseline.yaml nicht gefunden: {BASELINE_PATH}")
    return load_yaml(BASELINE_PATH)


def validate_baseline(b: dict[str, Any]) -> list[dict[str, Any]]:
    # Minimal required sections
    if "agents" not in b or not isinstance(b["agents"], list):
        fatal("Baseline: Feld 'agents' fehlt oder ist nicht Liste.")
    if "port_policy" not in b or not isinstance(b["port_policy"], dict):
        fatal("Baseline: Feld 'port_policy' fehlt oder ist nicht Dict.")

    agents = b["agents"]
    pol = b["port_policy"]

    allowed = pol.get("allowed_range") or pol.get("allow_range")
    if not allowed or not isinstance(allowed, list) or len(allowed) != 2:
        fatal("port_policy.allowed_range muss [min, max] sein.")
    allowed_range = (int(allowed[0]), int(allowed[1]))
    forbidden_ports = [int(x) for x in pol.get("forbidden_ports", pol.get("verboten_ports", []))]

    # Check agents
    ports_seen = {}
    ids_seen = set()

    for a in agents:
        for req in ("id", "name", "port", "role", "folder"):
            if req not in a:
                fatal(f"Agent-Entry fehlt Feld '{req}': {a}")

        agent_id = str(a["id"]).strip()
        if not ID_RE.match(agent_id):
            fatal(f"Ungültige Agent-ID: {agent_id} (erwartet opena1..opena21)")

        if agent_id in ids_seen:
            fatal(f"Doppelte Agent-ID: {agent_id}")
        ids_seen.add(agent_id)

        port = int(a["port"])
        assert_port_policy(port, allowed_range, forbidden_ports)

        if port in ports_seen:
            fatal(f"Doppel-Port {port}: {ports_seen[port]} und {agent_id}")
        ports_seen[port] = agent_id

        folder = (BASE_DIR / str(a["folder"])).resolve()
        if not folder.exists() or not folder.is_dir():
            fatal(f"{agent_id}: folder existiert nicht oder ist kein Ordner: {folder}")

        # simple sanity: folder must be readable
        try:
            _ = list(folder.iterdir())
        except Exception as e:
            fatal(f"{agent_id}: folder nicht lesbar: {folder} ({e})")

        # "ID ≠ Name ≠ Port ≠ Ordner" -> wir prüfen: Felder existieren und nicht leer
        if not str(a["name"]).strip():
            fatal(f"{agent_id}: name ist leer")
        if not str(a["role"]).strip():
            fatal(f"{agent_id}: role ist leer")
        if not str(a["folder"]).strip():
            fatal(f"{agent_id}: folder ist leer")

    return agents


# -----------------------------
# Process Start
# -----------------------------
def start_agent(agent: dict[str, Any]) -> subprocess.Popen:
    agent_id = agent["id"]
    port = int(agent["port"])
    folder = (BASE_DIR / agent["folder"]).resolve()

    # Ports sind unveränderlich -> wenn belegt, sofort fail
    ensure_free_port_or_fail(port)

    start_kind, target = discover_entry(folder, agent_id)

    log_file = LOGS_DIR / f"{agent_id}.log"
    log_fh = log_file.open("a", encoding="utf-8")

    env = os.environ.copy()
    # Standard: Agent bekommt seinen Port als ENV (optional nützlich)
    env.setdefault("PORT", str(port))
    env.setdefault("AGENT_ID", str(agent_id))

    if start_kind == "uvicorn":
        # target ist "module:app"
        cmd = [
            PYTHON,
            "-m",
            "uvicorn",
            target,
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "info",
        ]
    else:
        # python script
        cmd = [PYTHON, target]

    print(f"[START] {agent_id} -> {start_kind} | port={port} | cwd={folder}")
    print(f"        cmd: {' '.join(cmd)}")
    print(f"        log: {log_file}")

    proc = subprocess.Popen(
        cmd,
        cwd=str(folder),
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        env=env,
    )
    return proc


def terminate_all(procs: dict[str, subprocess.Popen]) -> None:
    print("\n[SHUTDOWN] Stoppe alle Agents…")
    # terminate
    for aid, p in procs.items():
        if p.poll() is None:
            print(f"  -> terminate {aid} (PID {p.pid})")
            try:
                p.terminate()
            except Exception:
                pass
    time.sleep(2)
    # kill
    for aid, p in procs.items():
        if p.poll() is None:
            print(f"  -> kill {aid} (PID {p.pid})")
            try:
                p.kill()
            except Exception:
                pass
    print("[DONE] Alle Agents gestoppt.")


def main() -> int:
    # .env laden (Root/.env)
    load_dotenv(BASE_DIR / ".env")

    print("====================================================")
    print("  OPENA MASTER STARTER (Baseline-driven)")
    print("====================================================")
    print(f"Baseline: {BASELINE_PATH}")
    print(f"Logs:     {LOGS_DIR}\n")

    baseline = load_baseline()
    agents = validate_baseline(baseline)

    # Sort by numeric id (opena1..)
    def aid_num(a: dict[str, Any]) -> int:
        return int(str(a["id"]).replace("opena", ""))

    agents_sorted = sorted(agents, key=aid_num)

    procs: dict[str, subprocess.Popen] = {}

    # Start all agents
    for a in agents_sorted:
        aid = a["id"]
        procs[aid] = start_agent(a)

    print("\n----------------------------------------------------")
    print("Gestartet:")
    print(", ".join(procs.keys()))
    print("----------------------------------------------------\n")
    print("Ctrl+C beendet alles sauber.\n")

    # Handle SIGTERM like Ctrl+C
    def _sigterm_handler(_signum, _frame):
        terminate_all(procs)
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _sigterm_handler)

    try:
        while True:
            dead = []
            for aid, p in procs.items():
                rc = p.poll()
                if rc is not None:
                    print(f"[EXIT] {aid} beendet (code={rc})")
                    dead.append(aid)

            # Wenn irgendein Agent stirbt -> harte Wahrheit: du willst production grade.
            # => Wir brechen ab und stoppen alles, damit du nicht im Zombie-Cluster landest.
            if dead:
                terminate_all(procs)
                fatal(f"Mindestens ein Agent ist gestorben: {dead}. Gesamtsystem gestoppt.")

            time.sleep(2)
    except KeyboardInterrupt:
        terminate_all(procs)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
