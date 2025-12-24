#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from pathlib import Path

BASE = Path.cwd()
BASELINE_PATH = BASE / "system_baseline.yaml"


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
    for a in agents:
        aid = a.get("id")
        port = a.get("port")
        folder = a.get("folder_path") or a.get("folder")
        # ID checks
        if not isinstance(aid, str) or not re.match(r"^opena(?:[1-9]|1[0-9]|2[01])$", aid or ""):
            errors.append(f"Ungültige Agent-ID: {aid}")
        if not isinstance(port, int) or port < 12344 or port > 12399:
            errors.append(f"Port außerhalb des erlaubten Bereichs (12344-12399): {port}")
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
