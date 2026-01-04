#!/usr/bin/env python3
"""Deterministic baseline schema validation for PORTIER 3.0."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except Exception:
    print("ERROR: Missing 'pyyaml'. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "system_baseline.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_PATH = ARTIFACTS_DIR / "Baseline_validation.json"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_yaml(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("baseline yaml is not a dict")
    return data

def write_artifact(payload: Dict[str, Any]) -> None:
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def stable_sort_agents(agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(agents, key=lambda a: str(a.get("id", "")))

def validate() -> Tuple[bool, Dict[str, Any]]:
    errors: List[str] = []

    if not BASELINE_PATH.exists():
        errors.append(f"Missing system_baseline.yaml at: {BASELINE_PATH}")
        return False, {"errors": errors}

    raw = BASELINE_PATH.read_text(encoding="utf-8")
    baseline_hash = sha256_text(raw)

    try:
        data = load_yaml(BASELINE_PATH)
    except Exception as e:
        errors.append(f"Failed to parse system_baseline.yaml: {e}")
        return False, {"errors": errors, "baseline_hash": baseline_hash}

    port_policy = data.get("port_policy") or {}
    # Support both "allowed_range" and "allow_range" (case-insensitive)
    allow_range = port_policy.get("allowed_range") or port_policy.get("allow_range") or {}
    forbidden_ports = set(port_policy.get("forbidden_ports") or [])
    min_port = int(allow_range.get("min", 0))
    max_port = int(allow_range.get("max", 0))

    agents = data.get("agents") or []
    if not isinstance(agents, list):
        errors.append("agents must be a list")
        agents = []

    agents = stable_sort_agents([a for a in agents if isinstance(a, dict)])

    # Check: exactly opena1..opena21
    expected_ids = [f"opena{i}" for i in range(1, 22)]
    got_ids = [str(a.get("id", "")).strip() for a in agents]

    missing = [i for i in expected_ids if i not in got_ids]
    extra = [i for i in got_ids if i not in expected_ids]
    if missing:
        errors.append(f"Missing agent IDs: {missing}")
    if extra:
        errors.append(f"Unexpected agent IDs: {extra}")
    if len(got_ids) != 21:
        errors.append(f"Expected exactly 21 agents, got {len(got_ids)}")

    # Check: ports unique + in range + not forbidden
    ports: List[int] = []
    port_map: Dict[int, List[str]] = {}
    for a in agents:
        aid = str(a.get("id", "")).strip()
        try:
            p = int(a.get("port"))
        except Exception:
            errors.append(f"{aid}: port is missing or not an int")
            continue

        ports.append(p)
        port_map.setdefault(p, []).append(aid)

        if p in forbidden_ports:
            errors.append(f"{aid}: port {p} is forbidden")
        if not (min_port <= p <= max_port):
            errors.append(f"{aid}: port {p} out of allow_range {min_port}-{max_port}")

    duplicates = {p: ids for p, ids in port_map.items() if len(ids) > 1}
    if duplicates:
        errors.append(f"Duplicate ports detected: {duplicates}")

    ok = len(errors) == 0
    result = {
        "timestamp_utc": utc_now(),
        "baseline_path": str(BASELINE_PATH),
        "baseline_hash_sha256": baseline_hash,
        "success": ok,
        "errors": errors,
    }
    return ok, result

def main() -> None:
    ok, payload = validate()
    write_artifact(payload)

    if not ok:
        print("BASELINE VALIDATION: FAIL", file=sys.stderr)
        for e in payload.get("errors", []):
            print(f"- {e}", file=sys.stderr)
        sys.exit(1)

    print("BASELINE VALIDATION: OK")
    print(f"Artifact written: {ARTIFACT_PATH}")
    sys.exit(0)

if __name__ == "__main__":
    main()
