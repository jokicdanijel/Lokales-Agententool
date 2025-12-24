#!/usr/bin/env python3
"""
System Baseline Validator
- Validates `system_baseline.yaml` invariants
- Writes `artifacts/baseline_validation.json` with timestamp, baseline_hash, success, errors
Exit codes: 0 = valid, 1 = violations found
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).parent.parent
BASELINE_PATH = ROOT / "system_baseline.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACT_PATH = ARTIFACTS_DIR / "baseline_validation.json"


def load_baseline(path: Path) -> dict[str, Any]:
    with open(path, "rb") as f:
        raw = f.read()
    try:
        data = yaml.safe_load(raw)
    except Exception as e:
        raise RuntimeError(f"Failed to parse YAML: {e}")
    return data, raw


def compute_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate(baseline: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []

    # Check basic structure
    agents = baseline.get("agents")
    if not isinstance(agents, list):
        errors.append("'agents' must be a list in baseline")
        return errors

    # 1) count
    if len(agents) != 21:
        errors.append(f"Expected 21 agents, found {len(agents)}")

    # 2) ID pattern and uniqueness
    ids = set()
    ports = set()
    for a in agents:
        aid = a.get("id")
        if not isinstance(aid, str) or not aid.startswith("opena") or not aid[5:].isdigit():
            errors.append(f"Invalid agent id: {aid}")
            continue
        if aid in ids:
            errors.append(f"Duplicate agent id: {aid}")
        ids.add(aid)

        # port checks
        port = a.get("port")
        if not isinstance(port, int):
            errors.append(f"Agent {aid}: port must be integer")
        else:
            if port in ports:
                errors.append(f"Duplicate port: {port} (agent {aid})")
            ports.add(port)

            # port range
            pr = baseline.get("port_policy", {}).get("allowed_range")
            if pr and (port < pr[0] or port > pr[1]):
                errors.append(f"Agent {aid}: port {port} outside allowed range {pr}")

            # forbidden ports
            forbidden = baseline.get("port_policy", {}).get("forbidden_ports", [])
            if port in forbidden:
                errors.append(f"Agent {aid}: port {port} is forbidden by port_policy")

        # folder existence
        folder = a.get("folder")
        if not isinstance(folder, str) or not folder:
            errors.append(f"Agent {aid}: folder missing or invalid")
        else:
            folder_path = root / folder
            if not folder_path.exists():
                errors.append(f"Agent {aid}: folder not found: {folder}")

    # 3) plans: referenced agents must exist
    plans = baseline.get("plans", {})
    plan_agent_ids = set()
    for plan_name, p in plans.items():
        for ref in p.get("agents", []):
            plan_agent_ids.add(ref)
            if ref not in ids:
                errors.append(f"Plan '{plan_name}': Unknown agent {ref}")

    # 4) core/system agents presence
    core = set(baseline.get("core_agents", []))
    system = set(baseline.get("system_agents", []))
    for req in [("core_agents", core), ("system_agents", system)]:
        for aid in req[1]:
            if aid not in ids:
                errors.append(f"{req[0]} contains unknown agent id: {aid}")

    # 5) domain policy
    domain = baseline.get("domain_policy", {}).get("primary_domain")
    if not domain:
        errors.append("domain_policy.primary_domain must be set")

    return errors


def write_artifact(hash: str, success: bool, errors: list[str]) -> None:
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    payload = {
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "baseline_hash": hash,
        "success": success,
        "errors": errors,
    }
    with open(ARTIFACT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    # Also print brief summary to stdout
    if success:
        print("✅ Baseline validation passed — artifacts/baseline_validation.json written")
    else:
        print(f"❌ Baseline validation failed — {len(errors)} errors. See {ARTIFACT_PATH}")


def main() -> int:
    if not BASELINE_PATH.exists():
        print(f"❌ FATAL: {BASELINE_PATH} not found")
        return 1

    try:
        baseline, raw = load_baseline(BASELINE_PATH)
    except Exception as e:
        print(f"❌ ERROR reading baseline: {e}")
        write_artifact("", False, [str(e)])
        return 1

    hash = compute_hash(raw)
    errors = validate(baseline, ROOT)

    success = len(errors) == 0
    write_artifact(hash, success, errors)

    if success:
        return 0
    else:
        for e in errors:
            print("  -", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
