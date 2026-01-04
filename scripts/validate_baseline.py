#!/usr/bin/env python3
# ============================================================================
# validate_baseline.py
# Deterministische Baseline-Validierung für PORTIER 3.0
# - Read-only Analyse: keine Codeausführung, kein Netzwerk
# - Fail fast: Exit-Code 1 bei jeder Verletzung
#
# Erwartetes Baseline-Schema (SSoT):
#   port_policy.allowed_range: {min:int, max:int}
#   port_policy.forbidden_ports: [int,...]
#   agents: list[dict] mit:
#     - id: opena1..opena21 (exakt 21)
#     - folder_path: str
#     - ports: list[dict] mit host_port:int (mindestens ein Eintrag)
#
# Output:
#   artifacts/Baseline_validation.json
# ============================================================================
from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:
    print("ERROR: Missing dependency 'pyyaml'. Install via: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "system_baseline.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_PATH = ARTIFACTS_DIR / "Baseline_validation.json"


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("system_baseline.yaml is not a dict")
    return data


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def err(errors: list[str], msg: str) -> None:
    errors.append(msg)


def stable_sort_agents(agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(agents, key=lambda a: str(a.get("id", "")).strip())


def extract_agent_port(agent: dict[str, Any]) -> tuple[bool, int]:
    """
    Baseline v1 (PORTIER 3.0) stores ports as:
      ports:
        - name: backend
          host_port: 12344
    We accept:
      - first ports[].host_port as the agent's canonical port
    """
    ports = agent.get("ports")
    if isinstance(ports, list) and ports:
        p0 = ports[0]
        if isinstance(p0, dict) and "host_port" in p0:
            try:
                return True, int(p0["host_port"])
            except Exception:
                return False, -1
    # Back-compat: allow legacy flat key "port"
    if "port" in agent:
        try:
            return True, int(agent["port"])
        except Exception:
            return False, -1
    return False, -1


def validate() -> tuple[bool, dict[str, Any]]:
    errors: list[str] = []

    if not BASELINE_PATH.exists():
        err(errors, f"Missing system_baseline.yaml at: {BASELINE_PATH}")
        return False, {"errors": errors}

    raw = BASELINE_PATH.read_text(encoding="utf-8")
    baseline_hash = sha256_text(raw)

    try:
        data = load_yaml(BASELINE_PATH)
    except Exception as e:
        err(errors, f"Failed to parse system_baseline.yaml: {e}")
        return False, {"errors": errors, "baseline_hash_sha256": baseline_hash}

    port_policy = data.get("port_policy") if isinstance(data.get("port_policy"), dict) else {}
    allowed_range = port_policy.get("allowed_range") if isinstance(port_policy.get("allowed_range"), dict) else {}
    forbidden_ports = set(port_policy.get("forbidden_ports") or []) if isinstance(port_policy.get("forbidden_ports"), list) else set()

    try:
        min_port = int(allowed_range.get("min", 0))
        max_port = int(allowed_range.get("max", 0))
    except Exception:
        min_port, max_port = 0, 0
        err(errors, "port_policy.allowed_range must contain int min/max")

    if min_port <= 0 or max_port <= 0 or min_port > max_port:
        err(errors, f"Invalid allowed_range: min={min_port} max={max_port}")

    agents = data.get("agents") or []
    if not isinstance(agents, list):
        err(errors, "agents must be a list")
        agents = []

    agents = stable_sort_agents([a for a in agents if isinstance(a, dict)])

    expected_ids = [f"opena{i}" for i in range(1, 22)]
    got_ids = [str(a.get("id", "")).strip() for a in agents]

    if len(got_ids) != 21:
        err(errors, f"Expected exactly 21 agents, got {len(got_ids)}")

    missing = [i for i in expected_ids if i not in got_ids]
    extra = [i for i in got_ids if i not in expected_ids]
    if missing:
        err(errors, f"Missing agent IDs: {missing}")
    if extra:
        err(errors, f"Unexpected agent IDs: {extra}")

    # Ports: uniqueness + range + forbidden
    port_map: dict[int, list[str]] = {}
    for a in agents:
        aid = str(a.get("id", "")).strip()

        ok_port, p = extract_agent_port(a)
        if not ok_port:
            err(errors, f"{aid}: missing/invalid port (expected ports[0].host_port:int or legacy port:int)")
            continue

        port_map.setdefault(p, []).append(aid)

        if p in forbidden_ports:
            err(errors, f"{aid}: port {p} is forbidden")
        if min_port and max_port and not (min_port <= p <= max_port):
            err(errors, f"{aid}: port {p} out of allowed_range {min_port}-{max_port}")

    duplicates = {p: ids for p, ids in port_map.items() if len(ids) > 1}
    if duplicates:
        err(errors, f"Duplicate ports detected: {duplicates}")

    # folder_path exists and not empty
    for a in agents:
        aid = str(a.get("id", "")).strip()
        folder_path = str(a.get("folder_path", "")).strip()
        if not folder_path:
            err(errors, f"{aid}: folder_path is missing")
            continue

        abs_path = (ROOT / folder_path).resolve()
        if not abs_path.exists():
            err(errors, f"{aid}: folder_path not found: {folder_path}")
            continue
        if not abs_path.is_dir():
            err(errors, f"{aid}: folder_path is not a directory: {folder_path}")
            continue

        try:
            has_any = any(abs_path.iterdir())
        except Exception:
            has_any = False
        if not has_any:
            err(errors, f"{aid}: folder_path is empty: {folder_path}")

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
        print(f"Artifact written: {ARTIFACT_PATH}", file=sys.stderr)
        sys.exit(1)

    print("BASELINE VALIDATION: OK")
    print(f"Artifact written: {ARTIFACT_PATH}")
    sys.exit(0)


if __name__ == "__main__":
    main()
