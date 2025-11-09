#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScanPython – Installer + Scanner + Starter (final, mit ENV-Varianten)

OS: Linux (Mint/Ubuntu) · Python 3.12+ (empfohlen 3.13)
Projektpfad (Default): /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.portier_openai
Venv: venv313 (Default, via $PORTIER_VENV überschreibbar)
Port-Policy: 12344–12399 erlaubt; 8080 ausschließlich OpenWebUI (Loopback)

Subkommandos:
  install         – venv anlegen/auffrischen, Pakete installieren, env.sh & .env schreiben, MAC erzeugen
  generate-mac    – MAC_DIR_SYSTEM.json deterministisch erzeugen/aktualisieren
  scan            – Read-only Projekt-/Systemscan; optional Safepoints schreiben
  serve           – integrierten opena1-Koordinator (FastAPI) starten (Port in 12344–12399) + Landingpage
  preflight       – Archiv-Check (heute CMD+RESP, strict:true), Git-Check, MAC-Check
  help            – Kurzhilfe
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ===== einfache .env-Unterstützung (ohne externe Pakete) =====
def _load_dotenv_simple(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)  # vorhandene ENV nicht überschreiben

# ===== Defaults einlesen (inkl. .env) =====
_DEFAULT_ROOT = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.portier_openai").resolve()
_load_dotenv_simple(_DEFAULT_ROOT / ".env")  # vorab versuchen

# ENV lesen
ENV_ROOT = Path(os.environ.get("PORTIER_ROOT", str(_DEFAULT_ROOT))).resolve()
ENV_VENV = os.environ.get("PORTIER_VENV", "venv313")
ENV_PORT_RANGE = os.environ.get("PORTIER_ALLOWED_PORTS", "12344-12399")
ENV_CONNECTOR_PORT = int(os.environ.get("PORTIER_CONNECTOR_PORT", "12355"))
ENV_MODE = os.environ.get("PORTIER_ENV", "production")

# .env erneut aus effektivem ROOT laden (falls abweichend)
if ENV_ROOT != _DEFAULT_ROOT:
    _load_dotenv_simple(ENV_ROOT / ".env")
    ENV_VENV = os.environ.get("PORTIER_VENV", ENV_VENV)
    ENV_PORT_RANGE = os.environ.get("PORTIER_ALLOWED_PORTS", ENV_PORT_RANGE)
    ENV_CONNECTOR_PORT = int(os.environ.get("PORTIER_CONNECTOR_PORT", str(ENV_CONNECTOR_PORT)))
    ENV_MODE = os.environ.get("PORTIER_ENV", ENV_MODE)

# Portbereich parsen
m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", ENV_PORT_RANGE)
if not m:
    raise SystemExit("PORTIER_ALLOWED_PORTS muss das Format LOW-HIGH haben, z. B. 12344-12399.")
ALLOWED_LOW = int(m.group(1))
ALLOWED_HIGH = int(m.group(2))
if ALLOWED_LOW > ALLOWED_HIGH:
    raise SystemExit("PORTIER_ALLOWED_PORTS: LOW darf nicht größer als HIGH sein.")

RESERVED_OPENWEBUI = 8080  # fix, Loopback-only

# ===== ab hier Policy/Objekte =====
PROJECT_ROOT = ENV_ROOT
VENV_DIR = PROJECT_ROOT / ENV_VENV
PY_BIN = VENV_DIR / "bin" / "python"
PIP_BIN = VENV_DIR / "bin" / "pip"
ENV_SH = PROJECT_ROOT / "env.sh"
DOTENV = PROJECT_ROOT / ".env"
MAC_PATH = PROJECT_ROOT / "MAC_DIR_SYSTEM.json"
ARCHIV_ROOT = PROJECT_ROOT / "archivp"
INDEX_JSONL = ARCHIV_ROOT / "index.jsonl"

OPENAI_ENDPOINTS = {
    "opena1": {"label": "Koordinator", "route": "/log/opena1"},
    "opena2": {"label": "Archivator",  "route": "/finalize/opena2"},
    "kordp":  {"label": "Kordinatport","route": "/dispatch/kordp"},
    "archivp":{"label": "Archivport",  "route": "/store/archivp"},
}

REQUIRED_PKGS = [
    "fastapi>=0.111",
    "pydantic>=2",
    "uvicorn[standard]>=0.30",
]

SAFEPOINT_SRC = "opena1"
SAFEPOINT_DST = "opena2"

# ===== Utils =====
def iso_z(dt: Optional[datetime] = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")

def run_cmd(cmd: str, timeout: int = 45) -> Tuple[int, str, str]:
    proc = subprocess.run(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def check_port_allowed(port: int) -> None:
    if not (ALLOWED_LOW <= port <= ALLOWED_HIGH):
        raise SystemExit(f"Port {port} ist nicht erlaubt (muss in {ALLOWED_LOW}–{ALLOWED_HIGH} liegen).")
    if port == RESERVED_OPENWEBUI:
        raise SystemExit("Port 8080 ist ausschließlich für OpenWebUI reserviert (Loopback).")

def venv_ready() -> bool:
    return PY_BIN.exists() and PIP_BIN.exists()

def pip_install(pkgs: List[str]) -> None:
    args = " ".join(shlex.quote(p) for p in pkgs)
    rc, out, err = run_cmd(f"{shlex.quote(str(PIP_BIN))} install --upgrade {args}")
    if rc != 0:
        print(out)
        print(err, file=sys.stderr)
        raise SystemExit("Paketinstallation fehlgeschlagen.")

def create_env_files() -> None:
    # env.sh
    env_sh_content = f"""# Autogeneriert – Portier/ELION
export PORTIER_ROOT="{PROJECT_ROOT}"
export PORTIER_ALLOWED_PORTS="{ALLOWED_LOW}-{ALLOWED_HIGH}"
export PORTIER_CONNECTOR_PORT="{ENV_CONNECTOR_PORT}"
export PORTIER_ENV="{ENV_MODE}"
export PORTIER_VENV="{ENV_VENV}"
# 8080 ist exklusiv für OpenWebUI (Loopback, nicht exponiert)
"""
    ENV_SH.write_text(env_sh_content, encoding="utf-8")
    os.chmod(ENV_SH, 0o644)

    # .env (nur setzen, wenn nicht vorhanden – Nutzer darf bearbeiten)
    if not DOTENV.exists():
        dotenv_content = (
            f"PORTIER_ROOT={PROJECT_ROOT}\n"
            f"PORTIER_ALLOWED_PORTS={ALLOWED_LOW}-{ALLOWED_HIGH}\n"
            f"PORTIER_CONNECTOR_PORT={ENV_CONNECTOR_PORT}\n"
            f"PORTIER_ENV={ENV_MODE}\n"
            f"PORTIER_VENV={ENV_VENV}\n"
        )
        DOTENV.write_text(dotenv_content, encoding="utf-8")

def generate_mac() -> None:
    data = {
        "strict": True,
        "system": {
            "id": "portier-elion",
            "name": "Portier / ELION Hyper-Dashboard 2.0",
            "created": iso_z(),
            "environment": {
                "os": "Linux Mint",
                "python": "3.12+ (empf. 3.13)",
                "venv": ENV_VENV,
                "mode": ENV_MODE,
            },
            "paths": {
                "root": str(PROJECT_ROOT),
                "archivp": str(ARCHIV_ROOT),
                "opena1": str(PROJECT_ROOT / "opena1"),
                "opena2": str(PROJECT_ROOT / "opena2"),
                "kordp":  str(PROJECT_ROOT / "kordp"),
                "connector": str(PROJECT_ROOT / "connector"),
                "docs": str(PROJECT_ROOT / "docs"),
            },
            "endpoints": OPENAI_ENDPOINTS,
            "ports": {
                "allowed_range": f"{ALLOWED_LOW}-{ALLOWED_HIGH}",
                "connector": ENV_CONNECTOR_PORT,
                "forbidden": [RESERVED_OPENWEBUI],
                "note": "8080 ausschließlich OpenWebUI (Loopback)",
            },
            "safepoints": {
                "pattern": "SP<number>_src→dst_(CMD|RESP).json",
                "daily_dir": "archivp/YYYY/MM/DD",
                "index_file": "archivp/index.jsonl",
                "timezone": "UTC",
            },
            "integrity": {
                "git_required": True,
                "pydantic_v2_required": True,
                "fastapi_required": True,
            },
            "notes": "Zeitformat stets ISO-8601 (UTC, 'Z').",
        },
    }
    MAC_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def list_listening_ports() -> List[int]:
    rc, out, _ = run_cmd("ss -ltn")
    ports: List[int] = []
    if rc == 0 and out:
        for line in out.splitlines():
            m = re.search(r":(\d+)\s", line)
            if m:
                try:
                    p = int(m.group(1))
                    if p not in ports:
                        ports.append(p)
                except ValueError:
                    pass
    return sorted(ports)

def safepoint_write(kind: str, payload: Dict[str, Any]) -> Path:
    now = datetime.now(timezone.utc)
    day_dir = ARCHIV_ROOT / f"{now:%Y/%m/%d}"
    ensure_dir(day_dir)
    spn = int(now.timestamp())
    name = f"SP{spn}_{SAFEPOINT_SRC}→{SAFEPOINT_DST}_{kind}.json"
    fp = day_dir / name
    payload = dict(payload)
    payload.setdefault("strict", True)
    payload.setdefault("timestamp", iso_z(now))
    fp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    ensure_dir(INDEX_JSONL.parent)
    with INDEX_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "sp": name, "ts": iso_z(now), "src": SAFEPOINT_SRC, "dst": SAFEPOINT_DST,
            "kind": kind, "path": str(fp)
        }, ensure_ascii=False) + "\n")
    return fp

# ===== Scan (read-only) =====
@dataclass
class PortCheck:
    port: int
    in_allowed_pool: bool
    is_reserved_8080: bool
    listening: bool

@dataclass
class ScanReport:
    strict: bool
    ts: str
    project_root: str
    venv_exists: bool
    python_exe: str
    ports_summary: Dict[str, Any]
    port_details: List[PortCheck]
    mac_dir_system_exists: bool
    mac_dir_system_valid: bool

def perform_scan() -> ScanReport:
    listening = list_listening_ports()
    port_details = [
        PortCheck(
            port=p,
            in_allowed_pool=(ALLOWED_LOW <= p <= ALLOWED_HIGH),
            is_reserved_8080=(p == RESERVED_OPENWEBUI),
            listening=True,
        ) for p in listening
    ]
    ports_summary = {
        "listening_count": len(listening),
        "in_pool": [p for p in listening if ALLOWED_LOW <= p <= ALLOWED_HIGH],
        "out_of_policy": [p for p in listening if p != RESERVED_OPENWEBUI and not (ALLOWED_LOW <= p <= ALLOWED_HIGH)],
        "openwebui_8080_in_use": (RESERVED_OPENWEBUI in listening),
        "policy": {"allowed_pool": f"{ALLOWED_LOW}-{ALLOWED_HIGH}", "reserved_openwebui": RESERVED_OPENWEBUI},
    }
    mac_ok = MAC_PATH.exists()
    mac_valid = False
    if mac_ok:
        try:
            data = json.loads(MAC_PATH.read_text(encoding="utf-8"))
            mac_valid = isinstance(data, dict) and data.get("strict") is True and "system" in data
        except Exception:
            mac_valid = False

    rep = ScanReport(
        strict=True,
        ts=iso_z(),
        project_root=str(PROJECT_ROOT),
        venv_exists=venv_ready(),
        python_exe=sys.executable,
        ports_summary=ports_summary,
        port_details=port_details,
        mac_dir_system_exists=mac_ok,
        mac_dir_system_valid=mac_valid,
    )
    return rep

def print_scan(rep: ScanReport) -> None:
    print("== ScanPython – Kurzbericht ==")
    print(f"Zeit:         {rep.ts}")
    print(f"Projektpfad:  {rep.project_root}")
    print(f"venv:         {'OK' if rep.venv_exists else 'FEHLT'} ({VENV_DIR.name})")
    print(f"Python:       {rep.python_exe}")
    print(f"Ports:        listening={rep.ports_summary['listening_count']}  "
          f"in_pool={rep.ports_summary['in_pool']}  "
          f"out_of_policy={rep.ports_summary['out_of_policy']}  "
          f"8080_in_use={rep.ports_summary['openwebui_8080_in_use']}")
    print(f"MAC_DIR_SYSTEM.json: {'OK' if rep.mac_dir_system_valid else ('FEHLT' if not rep.mac_dir_system_exists else 'UNGÜLTIG')}")
    print("\n-- JSON --")
    out = asdict(rep)
    out["port_details"] = [asdict(p) for p in rep.port_details]
    print(json.dumps(out, ensure_ascii=False, indent=2))

# ===== Installer =====
def do_install() -> None:
    ensure_dir(PROJECT_ROOT)
    ensure_dir(ARCHIV_ROOT)
    ensure_dir(PROJECT_ROOT / "opena1")
    ensure_dir(PROJECT_ROOT / "opena2")
    ensure_dir(PROJECT_ROOT / "kordp")
    ensure_dir(PROJECT_ROOT / "connector")
    ensure_dir(PROJECT_ROOT / "docs")

    if not venv_ready():
        rc, out, err = run_cmd(f"{shlex.quote(sys.executable)} -m venv {shlex.quote(str(VENV_DIR))}")
        if rc != 0:
            print(out)
            print(err, file=sys.stderr)
            raise SystemExit("Venv-Erstellung fehlgeschlagen.")
    pip_install(REQUIRED_PKGS)
    create_env_files()
    generate_mac()

    print("[OK] Installation abgeschlossen.")
    print(f"- venv: {VENV_DIR}")
    print(f"- env.sh: {ENV_SH}")
    print(f"- .env: {DOTENV if DOTENV.exists() else '(nicht erzeugt)'}")
    print(f"- MAC_DIR_SYSTEM.json: {MAC_PATH}")

# ===== Integrierter opena1-Server (FastAPI) + Landingpage =====
def serve_opena1(port: int, host: str = "127.0.0.1") -> None:
    check_port_allowed(port)

    try:
        from fastapi import FastAPI, HTTPException, Request
        from fastapi.responses import HTMLResponse
        from pydantic import BaseModel, UUID4, Field, ConfigDict, ValidationError
        import uvicorn
    except Exception:
        if not venv_ready():
            raise SystemExit("Pakete fehlen und venv ist nicht bereit. Führe zuerst 'install' aus.")
        pip_install(REQUIRED_PKGS)
        from fastapi import FastAPI, HTTPException, Request
        from fastapi.responses import HTMLResponse
        from pydantic import BaseModel, UUID4, Field, ConfigDict, ValidationError
        import uvicorn

    class Routing(BaseModel):
        resolved_path: Optional[str] = None
        notes: Optional[str] = None
        model_config = ConfigDict(extra="forbid")

    class Project(BaseModel):
        id: str
        name: str
        model_config = ConfigDict(extra="forbid")

    class Request71(BaseModel):
        request_id: UUID4
        timestamp: datetime
        command: str = Field(min_length=1)
        target_preference: Optional[str] = None
        payload: Dict[str, Any] = Field(default_factory=dict)
        routing: Routing = Field(default_factory=Routing)
        project: Project
        strict: bool = True
        model_config = ConfigDict(extra="forbid")

    def error_83(code: str, message: str, request_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "request_id": request_id or "unknown",
            "timestamp": iso_z(),
            "source": "opena1",
            "error": {"code": code, "message": message, "details": details or {}},
            "strict": True,
        }

    app = FastAPI(title="Portier / opena1 (Koordinator)")

    # --- Landingpage (GET "/") ---
    @app.get("/", response_class=HTMLResponse)
    def landing() -> str:
        return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><title>Portier opena1</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font:16px/1.5 system-ui,Segoe UI,Roboto,Ubuntu,Arial,sans-serif;margin:2rem;}}
code,pre{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.card{{border:1px solid #ddd;border-radius:8px;padding:16px;max-width:920px}}
.badge{{display:inline-block;background:#222;color:#fff;border-radius:6px;padding:.15rem .45rem;font-size:.85rem}}
.kv td{{padding:.15rem .5rem;vertical-align:top}}
hr{{border:none;border-top:1px solid #eee;margin:1rem 0}}
</style>
</head><body>
<div class="card">
  <h1>Portier / opena1 <span class="badge">online</span></h1>
  <p>Koordinator-API läuft. Nützliche Links & Beispiele:</p>
  <ul>
    <li><a href="/health">/health</a> – Service-Status</li>
    <li><a href="/docs">/docs</a> – OpenAPI UI</li>
  </ul>
  <hr>
  <h3>Beispiel-Request (curl)</h3>
  <pre>curl -s -X POST http://127.0.0.1:{port}/log/opena1 \
  -H 'Content-Type: application/json' \
  -d '{{"request_id":"11111111-1111-4111-8111-111111111111",
       "timestamp":"{iso_z()}",
       "command":"MONITOR",
       "payload":{{}},
       "routing":{{}},
       "project":{{"id":"proj-001","name":"Gesamtprojekt"}},
       "strict":true}}'</pre>
  <hr>
  <table class="kv">
    <tr><td><b>Port-Policy</b></td><td>{ALLOWED_LOW}-{ALLOWED_HIGH} (8080 reserviert für OpenWebUI)</td></tr>
    <tr><td><b>Pfad</b></td><td>{PROJECT_ROOT}</td></tr>
  </table>
</div>
</body></html>"""

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"service": "opena1", "status": "ok", "ts": iso_z()}

    @app.post("/log/opena1")
    async def log_opena1(request: Request) -> Dict[str, Any]:
        """
        Erwartet JSON-Body gemäß Request71.
        """
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail=error_83("SCHEMA_VIOLATION", "Kein gültiger JSON-Body."))

        rid = str(body.get("request_id")) if isinstance(body, dict) and "request_id" in body else None
        try:
            parsed = Request71(**body)
            if parsed.strict is not True:
                raise HTTPException(status_code=400, detail=error_83("STRICT_REQUIRED", "Feld 'strict' muss True sein.", rid))
        except ValidationError as ve:
            raise HTTPException(status_code=400, detail=error_83("SCHEMA_VIOLATION", "Payload verletzt das 7.1-Schema.", rid, {"errors": ve.errors()}))

        # Safepoints
        safepoint_write("CMD", {"source": "opena1", "target": "opena2", "action": "LOG", "payload": {"command": parsed.command}})
        safepoint_write("RESP", {"source": "opena2", "result": "ACCEPTED", "notes": "opena1 ack"})

        return {
            "request_id": str(parsed.request_id),
            "timestamp": iso_z(),
            "source": "opena1",
            "ack": {"status": "accepted", "command": parsed.command},
            "strict": True,
        }

    uvicorn.run(app, host=host, port=port, reload=False)

# ===== Preflight =====
def preflight() -> None:
    today = datetime.now(timezone.utc)
    day_dir = ARCHIV_ROOT / f"{today:%Y/%m/%d}"
    if not day_dir.is_dir():
        raise SystemExit(f"[Archiv] Tagesordner fehlt: {day_dir}")
    cmd = list(day_dir.glob("*_CMD.json"))
    resp = list(day_dir.glob("*_RESP.json"))
    if not cmd or not resp:
        raise SystemExit("[Archiv] CMD/RESP Safepoints fehlen.")
    sample_files = cmd[:1] + resp[:1]
    for fp in sample_files:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            raise SystemExit(f"[Archiv] JSON defekt: {fp}")
        if data.get("strict") is not True:
            raise SystemExit(f"[Archiv] strict:true fehlt in {fp.name}")

    rc, _, _ = run_cmd("git rev-parse --is-inside-work-tree")
    if rc == 0:
        rc2, out2, _ = run_cmd("git status --porcelain=v1")
        if out2.strip():
            raise SystemExit("[Git] Arbeitsverzeichnis ist nicht sauber.")
        rc3, out3, _ = run_cmd("git log -1 --oneline")
        if rc3 != 0 or not out3.strip():
            raise SystemExit("[Git] Kein letzter Commit gefunden.")
    else:
        raise SystemExit("[Git] Kein Repository im Projektordner.")

    if not MAC_PATH.exists():
        raise SystemExit("[MAC] MAC_DIR_SYSTEM.json fehlt.")
    try:
        data = json.loads(MAC_PATH.read_text(encoding="utf-8"))
    except Exception:
        raise SystemExit("[MAC] MAC_DIR_SYSTEM.json ist nicht lesbar/kein JSON.")
    if not (isinstance(data, dict) and data.get("strict") is True and "system" in data):
        raise SystemExit("[MAC] Struktur ungültig (strict/system).")

    print("PREFLIGHT OK")

# ===== CLI =====
def main() -> None:
    os.chdir(PROJECT_ROOT)

    parser = argparse.ArgumentParser(
        description="ScanPython – Installer, Scanner und Starter (final, mit ENV-Varianten)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("install", help="Venv, Pakete, env.sh & .env, MAC_DIR_SYSTEM.json, Struktur anlegen")
    sub.add_parser("generate-mac", help="MAC_DIR_SYSTEM.json erzeugen/aktualisieren")

    p_scan = sub.add_parser("scan", help="Read-only Projekt-/Systemscan")
    p_scan.add_argument("--write-safepoint", action="store_true", help="CMD/RESP-Safepoints schreiben")

    p_serve = sub.add_parser("serve", help="Integrierten opena1-Koordinator starten")
    p_serve.add_argument("--port", type=int, default=12345, help=f"Listen-Port ({ALLOWED_LOW}-{ALLOWED_HIGH}, 8080 verboten)")
    p_serve.add_argument("--host", default="127.0.0.1")

    sub.add_parser("preflight", help="Archiv-/Git-/MAC-Prüfung (hart)")
    sub.add_parser("help", help="Kurzhilfe")

    args = parser.parse_args()

    if args.cmd == "install":
        do_install()
    elif args.cmd == "generate-mac":
        ensure_dir(PROJECT_ROOT); ensure_dir(ARCHIV_ROOT); generate_mac()
        print(f"[OK] {MAC_PATH} aktualisiert.")
    elif args.cmd == "scan":
        rep = perform_scan(); print_scan(rep)
        if getattr(args, "write_safepoint", False):
            safepoint_write("CMD", {"source": SAFEPOINT_SRC, "target": SAFEPOINT_DST, "action": "SCAN"})
            safepoint_write("RESP", {"source": SAFEPOINT_DST, "result": "SCAN_RECORDED"})
    elif args.cmd == "serve":
        serve_opena1(port=int(getattr(args, "port", 12345)), host=str(getattr(args, "host", "127.0.0.1")))
    elif args.cmd == "preflight":
        preflight()
    elif args.cmd == "help":
        parser.print_help()
    else:
        parser.print_help(); raise SystemExit(2)

if __name__ == "__main__":
    main()

