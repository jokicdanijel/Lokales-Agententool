#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

BASE = Path.cwd()
BASELINE_PATH = BASE / "system_baseline.yaml"

PORT_RANGE_MIN_DEFAULT = 12344
PORT_RANGE_MAX_DEFAULT = 12399
ALLOWED_PORT_POLICY_KEYS: set[str] = {"allowed_range", "allow_range", "forbidden_ports", "no_deviations", "rule_text"}


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_allowed_range(port_policy: dict[str, Any], errors: list[str]) -> tuple[int, int]:
    """Parse port range from BOTH formats:
    A) allowed_range: "12344-12399" (string)
    B) allow_range: {min: 12344, max: 12399} (dict)
    """
    # Format B: allow_range dict
    if isinstance(port_policy.get("allow_range"), dict):
        ar = port_policy["allow_range"]
        try:
            mn = int(ar.get("min", PORT_RANGE_MIN_DEFAULT))
            mx = int(ar.get("max", PORT_RANGE_MAX_DEFAULT))
            return mn, mx
        except Exception:
            errors.append(f"port_policy.allow_range must contain int min/max, got: {ar!r}")
            return PORT_RANGE_MIN_DEFAULT, PORT_RANGE_MAX_DEFAULT

    # Format A: allowed_range string
    allowed = port_policy.get("allowed_range", f"{PORT_RANGE_MIN_DEFAULT}-{PORT_RANGE_MAX_DEFAULT}")
    if not isinstance(allowed, str) or "-" not in allowed:
        errors.append(f"port_policy.allowed_range must be 'min-max' string, got: {allowed!r}")
        return PORT_RANGE_MIN_DEFAULT, PORT_RANGE_MAX_DEFAULT

    parts = allowed.split("-")
    if len(parts) != 2:
        errors.append(f"port_policy.allowed_range must be 'min-max', got: {allowed!r}")
        return PORT_RANGE_MIN_DEFAULT, PORT_RANGE_MAX_DEFAULT

    try:
        mn = int(parts[0].strip())
        mx = int(parts[1].strip())
        return mn, mx
    except ValueError:
        errors.append(f"port_policy.allowed_range contains non-int bounds: {allowed!r}")
        return PORT_RANGE_MIN_DEFAULT, PORT_RANGE_MAX_DEFAULT


def load_baseline():
    import yaml  # type: ignore

    with open(BASELINE_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_yaml_simple(path: Path):
    # Minimal fallback parser if PyYAML is unavailable
    agents = []
    current = None
    in_agents = False
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.rstrip("\n")
            if s.strip() == "agents:":
                in_agents = True
                continue
            if in_agents:
                if s.strip().startswith("- id:"):
                    if current:
                        agents.append(current)
                    key = s.strip()[2:].strip()
                    current = {}
                    current["id"] = key.split(":", 1)[1].strip() if ":" in key else None
                    # next lines will fill in
                    continue
                if ":" in s:
                    k, v = (x.strip() for x in s.split(":", 1))
                    if current is not None:
                        current[k] = v
    if current:
        agents.append(current)
    return {"agents": agents}


def main():
    # Load baseline
    try:
        import yaml

        with open(BASELINE_PATH, encoding="utf-8") as f:
            baseline = json.loads("")  # intentionally fail to force PyYAML path below
    except Exception:
        pass
    try:
        import yaml

        with open(BASELINE_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            baseline = data
    except Exception:
        # Fallback simple parser
        fallback = load_yaml_simple(BASELINE_PATH)
        baseline = {"agents": fallback.get("agents", [])}

    if not isinstance(baseline, dict) or "agents" not in baseline:
        print("[baseline] Ungültiges Baseline-Format; Abbruch", file=sys.stderr)
        sys.exit(1)

    agents = baseline.get("agents", [])
    errors = []
    seen_ports = set()
    ids = set()

    # Validate port_policy if present
    port_policy = baseline.get("port_policy")
    if port_policy:
        if not isinstance(port_policy, dict):
            errors.append("port_policy must be a dict")
        else:
            # Check for unexpected keys
            unexpected = set(port_policy.keys()) - ALLOWED_PORT_POLICY_KEYS
            if unexpected:
                errors.append(f"port_policy contains unexpected keys: {unexpected}")
            # Parse range (accepts both formats)
            range_min, range_max = parse_allowed_range(port_policy, errors)
    else:
        range_min, range_max = PORT_RANGE_MIN_DEFAULT, PORT_RANGE_MAX_DEFAULT

    for a in agents:
        aid = a.get("id")
        port = a.get("port")
        folder = a.get("folder_path") or a.get("folder")
        # ID checks
        if not isinstance(aid, str) or not re.match(r"^opena(?:[1-9]|1[0-9]|2[01])$", aid or ""):
            errors.append(f"Ungültige Agent-ID: {aid}")
        if not isinstance(port, int) or port < range_min or port > range_max:
            errors.append(f"Port außerhalb des erlaubten Bereichs ({range_min}-{range_max}): {port}")
        if aid in ids:
            errors.append(f"Duplizierte Agent-ID: {aid}")
        ids.add(aid)
        if port in seen_ports:
            errors.append(f"Port bereits verwendet: {port}")
        seen_ports.add(port)
        # folder existence check
        if folder:
            p = Path(BASE / folder)
            if not p.exists():
                errors.append(f"Missing agent folder: {folder}")
        else:
            errors.append(f"Missing folder_path for agent {aid}")

    # Core/system enforcement
    core = [a for a in agents if a.get("id") in ("opena1", "opena2")]
    if not core:
        errors.append("Core agents missing: opena1 and opena2 required")

    # Baseline hash
    with open(BASELINE_PATH, "rb") as f:
        baseline_bytes = f.read()
    baseline_hash = hashlib.sha256(baseline_bytes).hexdigest()

    out = {"baseline_hash": baseline_hash, "valid": len(errors) == 0, "errors": errors}
    artifacts = BASE / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    out_path = artifacts / "baseline_validation.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({**out}, f, indent=2)

    if errors:
        print("Baseline-Validation fehlgeschlagen:")
        for e in errors:
            print("-", e)
        sys.exit(1)
    else:
        print("Baseline-Validation erfolgreich.")
        sys.exit(0)


if __name__ == "__main__":
    main()
