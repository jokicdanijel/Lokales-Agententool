#!/usr/bin/env python3
"""
validate_baseline.py — Enterprise-Grade Baseline Validation (PORTIER 3.0)

GESETZ-KONFORM:
- IDs exakt opena1..opena21
- Ports fix/unique, allow_range 12344..12399, forbidden 8080
- Jeder Agent: folder_path existiert und ist nicht leer
- Frontend + Backend required (per Policy)
- Artifact: artifacts/Baseline_validation.json
"""

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
    print("ERROR: Missing dependency 'pyyaml'. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "system_baseline.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_PATH = ARTIFACTS_DIR / "Baseline_validation.json"


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def expected_agent_ids() -> list[str]:
    return [f"opena{i}" for i in range(1, 22)]


def load_yaml(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("baseline yaml is not a dict")
    return data


def parse_allowed_range(port_policy: dict[str, Any]) -> tuple[int, int]:
    """Parse port range (allow_range dict or allowed_range string)"""
    ar = port_policy.get("allow_range")
    if isinstance(ar, dict):
        return int(ar.get("min", 12344)), int(ar.get("max", 12399))

    # Fallback: string format "12344-12399"
    allowed = port_policy.get("allowed_range", "12344-12399")
    if isinstance(allowed, str):
        parts = allowed.split("-")
        if len(parts) == 2:
            try:
                return int(parts[0].strip()), int(parts[1].strip())
            except ValueError:
                pass
    return 12344, 12399


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    errors: list[str] = []

    if not BASELINE_PATH.exists():
        fail(errors, f"Missing system_baseline.yaml at: {BASELINE_PATH}")
        write_artifact({"timestamp_utc": utc_now(), "success": False, "errors": errors})
        print("BASELINE VALIDATION: FAIL", file=sys.stderr)
        return 1

    raw = BASELINE_PATH.read_text(encoding="utf-8")
    baseline_hash = sha256_text(raw)

    try:
        data = load_yaml(BASELINE_PATH)
    except Exception as e:
        fail(errors, f"Failed to parse system_baseline.yaml: {e}")
        write_artifact({
            "timestamp_utc": utc_now(),
            "success": False,
            "baseline_hash_sha256": baseline_hash,
            "errors": errors
        })
        print("BASELINE VALIDATION: FAIL", file=sys.stderr)
        return 1

    port_policy = data.get("port_policy") or {}
    if not isinstance(port_policy, dict):
        fail(errors, "port_policy must be a dict")
        port_policy = {}

    min_p, max_p = parse_allowed_range(port_policy)
    forbidden_ports = set(port_policy.get("forbidden_ports") or [])

    agents = data.get("agents") or []
    if not isinstance(agents, list):
        fail(errors, "agents must be a list")
        agents = []

    # Must be exactly opena1..opena21
    exp = expected_agent_ids()
    got = [str(a.get("id", "")).strip() for a in agents if isinstance(a, dict)]
    got_sorted = sorted(got)

    missing = [i for i in exp if i not in got]
    extra = [i for i in got if i not in exp]
    if missing:
        fail(errors, f"Missing agent IDs: {missing}")
    if extra:
        fail(errors, f"Unexpected agent IDs: {sorted(extra)}")
    if len(got) != 21:
        fail(errors, f"Expected exactly 21 agents, got {len(got)}")
    if got != got_sorted:
        fail(errors, "agents list is not sorted by id (recommend deterministic sort in file).")

    # Ports: uniqueness + range + forbidden
    port_map: dict[int, list[str]] = {}
    for a in agents:
        if not isinstance(a, dict):
            continue
        aid = str(a.get("id", "")).strip()

        try:
            p = int(a.get("port"))
        except Exception:
            fail(errors, f"{aid}: port is missing or not an int")
            continue

        port_map.setdefault(p, []).append(aid)

        if p in forbidden_ports:
            fail(errors, f"{aid}: port {p} is forbidden")
        if not (min_p <= p <= max_p):
            fail(errors, f"{aid}: port {p} out of allow_range {min_p}-{max_p}")

        folder = str(a.get("folder_path", "")).strip()
        if not folder:
            fail(errors, f"{aid}: folder_path missing")
        else:
            abs_path = (ROOT / folder).resolve()
            if not abs_path.exists():
                fail(errors, f"{aid}: folder_path not found: {folder}")
            elif not abs_path.is_dir():
                fail(errors, f"{aid}: folder_path is not a directory: {folder}")
            else:
                try:
                    nonempty = any(abs_path.iterdir())
                except Exception:
                    nonempty = False
                if not nonempty:
                    fail(errors, f"{aid}: folder_path empty: {folder}")
                else:
                    # Frontend + Backend required check
                    frontend_ok = (abs_path / "frontend").exists() or (abs_path / "templates").exists()
                    backend_ok = (abs_path / "backend").exists() or any(p.suffix == ".py" for p in abs_path.glob("*.py"))

                    if not frontend_ok:
                        fail(errors, f"{aid}: frontend missing (expected frontend/ or templates/ in {folder})")
                    if not backend_ok:
                        fail(errors, f"{aid}: backend missing (expected backend/ or *.py in {folder})")

    dups = {p: ids for p, ids in port_map.items() if len(ids) > 1}
    if dups:
        fail(errors, f"Duplicate backend ports detected: {dups}")

    ok = len(errors) == 0
    payload = {
        "timestamp_utc": utc_now(),
        "success": ok,
        "baseline_path": str(BASELINE_PATH),
        "baseline_hash_sha256": baseline_hash,
        "errors": errors,
    }
    write_artifact(payload)

    if not ok:
        print("BASELINE VALIDATION: FAIL", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        print(f"Artifact written: {ARTIFACT_PATH}", file=sys.stderr)
        return 1

    print("BASELINE VALIDATION: OK")
    print(f"Artifact written: {ARTIFACT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
