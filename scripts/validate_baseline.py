#!/usr/bin/env python3
"""
validate_baseline.py

Gesetz-konformer Baseline-Validator für PORTIER 3.0.

Validiert:
 - system_baseline.yaml Struktur und Agent-Matrix (IDs, folder_path, port)
 - Ports: Range + forbidden + uniqueness
 - Agent-Folders existieren und sind nicht leer
 - Frontend+Backend Pflicht (für die meisten Agenten, dashboard special-case)
 - Schreibt deterministisches Artefakt: artifacts/baseline_validation.json

Eigenschaften:
 - Read-only: verändert nichts
 - Fail-fast: Exit 1 bei Fehler
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:
    print("FEHLER: Fehlende Abhängigkeit 'pyyaml'. Installation über: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "system_baseline.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_PATH = ARTIFACTS_DIR / "baseline_validation.json"


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def expected_agent_ids() -> list[str]:
    return [f"opena{i}" for i in range(1, 22)]


@dataclass(frozen=True)
class PortPolicy:
    min_port: int
    max_port: int
    forbidden: tuple
    unique: bool


def parse_port_policy(b: dict[str, Any]) -> PortPolicy:
    p = (b.get("port_policy") or {}) if isinstance(b.get("port_policy"), dict) else {}
    rng = p.get("allow_range") or {}
    min_p = int(rng.get("min", 12344))
    max_p = int(rng.get("max", 12399))
    forbidden = p.get("forbidden_ports") or [8080]
    try:
        forbidden_t = tuple(int(x) for x in forbidden)
    except Exception:
        forbidden_t = (8080,)
    unique = bool(p.get("enforce_unique", True))
    return PortPolicy(min_port=min_p, max_port=max_p, forbidden=forbidden_t, unique=unique)


def load_baseline() -> dict[str, Any]:
    raw = BASELINE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("system_baseline.yaml is not a dict")
    return data


def has_any_children(path: Path) -> bool:
    try:
        return any(path.iterdir())
    except Exception:
        return False


def validate_frontend_backend(aid: str, folder: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    # Skip core/simple agents
    if aid in ("opena1", "opena2", "opena3"):
        return issues

    if aid == "opena20":
        t = folder / "templates"
        s = folder / "static"
        if not t.exists():
            issues.append({"severity": "error", "id": aid, "issue": "templates/ fehlt (Dashboard-Frontend)", "path": str(t.relative_to(ROOT))})
        if not s.exists():
            issues.append({"severity": "error", "id": aid, "issue": "static/ fehlt (Dashboard-Assets)", "path": str(s.relative_to(ROOT))})
        return issues

    # Default: opena4..opena19 + opena21 require frontend/ and backend/
    fe = folder / "frontend"
    be = folder / "backend"
    if not fe.exists():
        issues.append({"severity": "error", "id": aid, "issue": "frontend/ fehlt (Gesetz: Frontend=ja)", "path": str(fe.relative_to(ROOT))})
    if not be.exists():
        issues.append({"severity": "error", "id": aid, "issue": "backend/ fehlt (Gesetz: Backend=ja)", "path": str(be.relative_to(ROOT))})
    return issues


def validate_agents(agents: list[dict[str, Any]], policy: PortPolicy) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []

    exp = expected_agent_ids()
    got = [str(a.get("id", "")).strip() for a in agents if str(a.get("id", "")).strip()]
    missing = [i for i in exp if i not in got]
    extra = [i for i in got if i not in exp]
    if missing:
        issues.append({"severity": "error", "issue": f"Missing agent IDs (Gesetz): {missing}"})
    if extra:
        issues.append({"severity": "error", "issue": f"Unexpected agent IDs (Gesetz): {extra}"})

    seen_ids = set()
    seen_ports: dict[int, str] = {}

    for a in sorted(agents, key=lambda x: str(x.get("id", ""))):
        aid = str(a.get("id", "")).strip()
        folder = str(a.get("folder_path", "")).strip()
        port = a.get("port", None)
        name = str(a.get("name", "")).strip() if a.get("name") else ""

        if not aid:
            issues.append({"severity": "error", "id": None, "issue": "agent.id fehlt"})
            continue
        if aid in seen_ids:
            issues.append({"severity": "error", "id": aid, "issue": "duplicate agent.id"})
        seen_ids.add(aid)

        if not folder:
            issues.append({"severity": "error", "id": aid, "issue": "folder_path fehlt"})
        else:
            p = ROOT / folder
            if not p.exists():
                issues.append({"severity": "error", "id": aid, "issue": "folder_path existiert nicht", "expected_path": folder})
            else:
                if not has_any_children(p):
                    issues.append({"severity": "error", "id": aid, "issue": "folder_path ist leer", "expected_path": folder})
                issues.extend(validate_frontend_backend(aid, p))

        if port is None:
            issues.append({"severity": "error", "id": aid, "issue": "port fehlt"})
        else:
            try:
                port_i = int(port)
            except Exception:
                issues.append({"severity": "error", "id": aid, "issue": f"port ist nicht int: {port!r}"})
                continue

            if port_i in policy.forbidden:
                issues.append({"severity": "error", "id": aid, "issue": f"port {port_i} ist verboten"})
            if not (policy.min_port <= port_i <= policy.max_port):
                issues.append({"severity": "error", "id": aid, "issue": f"port {port_i} out of allow_range {policy.min_port}-{policy.max_port}"})

            if policy.unique:
                if port_i in seen_ports:
                    issues.append({"severity": "error", "id": aid, "issue": f"port {port_i} kollidiert mit {seen_ports[port_i]}", "port": port_i})
                else:
                    seen_ports[port_i] = aid

        if not name:
            issues.append({"severity": "warn", "id": aid, "issue": "name ist leer"})

    return {"issues": issues}


def validate() -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    if not BASELINE_PATH.exists():
        errors.append({"severity": "error", "issue": f"Missing system_baseline.yaml at: {BASELINE_PATH}"})
        return {"success": False, "errors": errors}

    raw = BASELINE_PATH.read_text(encoding="utf-8")
    baseline_hash = sha256_text(raw)

    try:
        data = load_baseline()
    except Exception as e:
        errors.append({"severity": "error", "issue": f"Failed to parse system_baseline.yaml: {e}"})
        return {"success": False, "errors": errors, "baseline_hash": baseline_hash}

    policy = parse_port_policy(data)
    agents = data.get("agents") or []
    if not isinstance(agents, list):
        errors.append({"severity": "error", "issue": "agents must be a list"})
        agents = []

    res = validate_agents(agents, policy)
    for i in res.get("issues", []):
        errors.append(i)

    ok = len(errors) == 0
    result = {
        "timestamp_utc": utc_now(),
        "baseline_path": str(BASELINE_PATH),
        "baseline_hash_sha256": baseline_hash,
        "success": ok,
        "errors": errors,
    }
    ARTIFACT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    payload = validate()
    if not payload.get("success"):
        print("BASELINE VALIDATION: FAIL", file=sys.stderr)
        for e in payload.get("errors", []):
            print(f"- {e}", file=sys.stderr)
        sys.exit(1)

    print("BASELINE VALIDATION: OK")
    print(f"Artifact written: {ARTIFACT_PATH}")
    sys.exit(0)
