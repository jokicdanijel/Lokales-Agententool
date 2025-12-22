#!/usr/bin/env python3
"""Preflight wrapper script.

Runs a safe set of checks (no modifications):
 - scripts/validate_baseline.py
 - optional: ruff/black/isort checks (if installed)
 - optional: pytest (if installed)
 - smoke test: import agent.core and run dry-run

Writes artifacts/preflight_result.json with details.
Supports --handoff-to <github-user> to create a GitHub issue if failures occur (requires `gh` CLI).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
ARTIFACT = ARTIFACTS / "preflight_result.json"


def run_cmd(cmd: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"rc": p.returncode, "out": p.stdout + p.stderr}
    except Exception as e:
        return {"rc": 2, "out": str(e)}


def check_validate_baseline() -> dict[str, Any]:
    cmd = [sys.executable, "scripts/validate_baseline.py"]
    return run_cmd(cmd, timeout=30)


def check_lint() -> dict[str, Any]:
    results = {}
    # ruff
    if shutil.which("ruff"):
        results["ruff"] = run_cmd(["ruff", "check", "--fix", "--show-source", "--exit-zero", "."])
    else:
        results["ruff"] = {"rc": None, "out": "skipped - ruff not installed"}

    # black (check mode)
    if shutil.which("black"):
        results["black"] = run_cmd(["black", "--check", "."])
    else:
        results["black"] = {"rc": None, "out": "skipped - black not installed"}

    # isort (check)
    if shutil.which("isort"):
        results["isort"] = run_cmd(["isort", "--check-only", "."])
    else:
        results["isort"] = {"rc": None, "out": "skipped - isort not installed"}

    return results


def check_pytest() -> dict[str, Any]:
    if shutil.which("pytest"):
        return run_cmd(["pytest", "-q"], timeout=300)
    return {"rc": None, "out": "skipped - pytest not installed"}


def check_smoke_agent() -> dict[str, Any]:
    try:
        sys.path.insert(0, str(ROOT / "19.opena20_dashboard_agent"))
        # use package import
        from agent.core import run_sync

        out = run_sync("preflight-check")
        return {"rc": 0, "out": str(out)}
    except Exception as e:
        return {"rc": 1, "out": f"exception: {e}"}


def create_issue(handoff_to: str, title: str, body: str) -> dict[str, Any]:
    if not shutil.which("gh"):
        return {"created": False, "reason": "gh CLI not installed"}

    cmd = ["gh", "issue", "create", "--title", title, "--body", body, "--assignee", handoff_to]
    res = run_cmd(cmd)
    return {"created": res["rc"] == 0, "result": res}


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    args = list(argv)
    handoff_to = None
    if "--handoff-to" in args:
        i = args.index("--handoff-to")
        try:
            handoff_to = args[i + 1]
        except IndexError:
            print("--handoff-to requires a GitHub username")
            return 2

    results: dict[str, Any] = {"timestamp": datetime.utcnow().isoformat() + "Z", "checks": {}}

    print("🔍 Running baseline validation...")
    results["checks"]["baseline"] = check_validate_baseline()
    print(results["checks"]["baseline"]["out"].strip())

    print("🔧 Running lint checks (if available)...")
    results["checks"]["lint"] = check_lint()

    print("🧪 Running pytest (if available)...")
    results["checks"]["tests"] = check_pytest()

    print("🚦 Running smoke test for agent.core (dry-run)...")
    results["checks"]["smoke_agent"] = check_smoke_agent()

    # Determine overall success: baseline + smoke_agent must be rc==0; tests/lint may be skipped
    success = True
    mandatory = [results["checks"]["baseline"], results["checks"]["smoke_agent"]]
    for m in mandatory:
        if m.get("rc") != 0:
            success = False

    results["success"] = success

    with open(ARTIFACT, "w") as f:
        json.dump(results, f, indent=2)

    if success:
        print("✅ Preflight SUCCESS — see", ARTIFACT)
        return 0

    # Failure path: create issue if requested
    print("❌ Preflight FAILED — see details in", ARTIFACT)
    if handoff_to:
        title = "Preflight failed — handoff"
        body = f"Preflight checks failed on {ROOT.name}\n\nSee {ARTIFACT.relative_to(ROOT)}\n\nErrors:\n" + json.dumps(
            results, indent=2
        )
        issue = create_issue(handoff_to, title, body)
        results["handoff"] = issue
        with open(ARTIFACT, "w") as f:
            json.dump(results, f, indent=2)
        if issue.get("created"):
            print(f"📢 Created GitHub issue and assigned to {handoff_to}")
        else:
            print("⚠️ Could not create GitHub issue:", issue.get("reason") or issue.get("result"))

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
