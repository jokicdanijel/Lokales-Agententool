#!/usr/bin/env python3
"""Preflight checks for ELION Hyper-Dashboard

Checks implemented:
 - .github/copilot-master-prompt.md exists
 - mcp_server/.env.example exists
 - docs/agent_startanleitung.html exists and validates (doctype, </html>, agents present, no 8080)
 - repository does not contain forbidden port 8080
 - ports in HTML are within 12344-12399

Exit code: 0 = OK, 2 = fatal checks failed
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_AGENTS = [f"opena{i}" for i in range(1, 22)] + ["browsep"]


def fail(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(2)


def run_cmd(cmd, **kwargs):
    try:
        out = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, **kwargs)
        return out.stdout
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr)
        fail(f"Command failed: {cmd}")


def check_files():
    if not (ROOT / ".github" / "copilot-master-prompt.md").is_file():
        fail("Missing .github/copilot-master-prompt.md")
    # Accept either mcp_server/.env.example or mcp-server/.env.example to be tolerant
    # of small repo layout differences (migration from mcp-server → mcp_server).
    env1 = ROOT / "mcp_server" / ".env.example"
    env2 = ROOT / "mcp-server" / ".env.example"
    if not (env1.is_file() or env2.is_file()):
        fail("Missing mcp_server/.env.example (or mcp-server/.env.example)")


def generate_doc():
    print("🔧 Generating agents runbook (bin/ops.sh doc:agents)...")
    # Use the wrapper script to generate doc
    run_cmd(f"bash {ROOT}/bin/ops.sh doc:agents")


def validate_html():
    doc = ROOT / "docs" / "agent_startanleitung.html"
    if not doc.is_file() or doc.stat().st_size == 0:
        fail(f"Runbook missing or empty: {doc}")

    text = doc.read_text(encoding="utf-8", errors="ignore").lower()
    if "<!doctype html>" not in text:
        fail("Runbook missing <!doctype html>")
    if "</html>" not in text:
        fail("Runbook missing </html>")

    missing = [a for a in EXPECTED_AGENTS if a not in text]
    if missing:
        fail(f"Runbook is missing agent entries: {', '.join(missing)}")

    if "8080" in text:
        fail("Runbook contains forbidden port 8080")

    # check that ports found in file are within allowed range
    ports = set(re.findall(r"127\.0\.0\.1:(\d{4,5})", text))
    if not ports:
        fail("No agent ports found in runbook (expected '127.0.0.1:PORT')")
    bad = [p for p in ports if not (12344 <= int(p) <= 12399)]
    if bad:
        fail(f"Found ports out of allowed range in runbook: {', '.join(bad)}")


def repo_forbidden_port_scan():
    print("🔎 Scanning repository for forbidden port references (8080) in configuration files...")
    # Limit scanning to configuration and runtime files where a hard-coded port would be problematic
    cmd = "grep -R --line-number --exclude-dir=.git --include=*.yml --include=*.yaml --include=Dockerfile --include=*.env --include=*.py --include=docker-compose* -e ':8080\b' . || true"
    res = run_cmd(cmd)
    if res.strip():
        print(res)
        fail("Forbidden port '8080' found in configuration files. Please remove or replace.")


def main():
    print("🧭 Preflight checks starting...")
    check_files()
    generate_doc()
    validate_html()
    repo_forbidden_port_scan()
    print("✅ Preflight checks passed")


if __name__ == "__main__":
    main()
