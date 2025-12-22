#!/usr/bin/env python3
"""
Deterministic Agent Discovery
- Read-only static analysis (no execution, no network)
- Stable ordering & hashing
- Emits artifacts/agent_inventory.json
- Exits with code 1 on any violation

Usage:
  python3 scripts/agent_discovery.py
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).parent.parent
BASELINE_PATH = ROOT / "system_baseline.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)
ARTIFACT_PATH = ARTIFACTS_DIR / "agent_inventory.json"

INT_RE = re.compile(r"\b(\d{2,5})\b")
AGENT_REF_RE = re.compile(r"\b(opena\d{1,2})\b", re.IGNORECASE)
FASTAPI_DECORATOR_RE = re.compile(r"@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*[\'\"]([^\'\"]+)")
FLASK_ROUTE_RE = re.compile(r"@app\.route\(\s*[\'\"]([^\'\"]+)")
DATA_ATTR_RE = re.compile(r"data-[a-zA-Z0-9_-]+")

# Port filtering globals (will be set from baseline in main)
ALLOWED_MIN = 1
ALLOWED_MAX = 65535
FORBIDDEN_PORTS: set = set()


@dataclass
class FileInfo:
    relpath: str
    size: int
    sha256: str


@dataclass
class AgentReport:
    id: str
    folder: str
    file_count: int
    files: list[FileInfo]
    imports: list[str]
    endpoints: list[str]
    ports_detected: list[int]
    agent_references: list[str]
    flags: dict[str, bool]


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_ints(seq):
    return sorted(set(int(x) for x in seq))


def extract_from_py(path: Path) -> tuple[set[str], list[str], set[int], set[str]]:
    imports: set[str] = set()
    endpoints: list[str] = []
    ports: set[int] = set()
    agent_refs: set[str] = set()

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        text = ""

    # Find ints that look like ports (filter to allowed/baseline range or forbidden ports)
    for m in INT_RE.findall(text):
        try:
            num = int(m)
            # consider it a port candidate only if it lies inside the allowed range
            # or it is explicitly a forbidden port (we still want to detect it)
            if (ALLOWED_MIN <= num <= ALLOWED_MAX) or (num in FORBIDDEN_PORTS):
                ports.add(num)
        except ValueError:
            continue

    # Agent references
    for m in AGENT_REF_RE.findall(text):
        agent_refs.add(m.lower())

    # Endpoints via regex (fast, deterministic)
    for m in FASTAPI_DECORATOR_RE.findall(text):
        endpoints.append(f"{m[0].upper()} {m[1]}")
    for m in FLASK_ROUTE_RE.findall(text):
        endpoints.append(f"GET {m}")

    # AST for imports
    try:
        node = ast.parse(text)
        for n in ast.walk(node):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(n, ast.ImportFrom):
                if n.module:
                    imports.add(n.module.split(".")[0])
    except Exception:
        # parsing error -> skip AST
        pass

    return imports, sorted(set(endpoints)), ports, agent_refs


def extract_from_text(path: Path) -> tuple[list[str], set[int], set[str], list[str]]:
    """Generic extractor for html/json/yaml/text files"""
    endpoints = []
    ports: set[int] = set()
    agent_refs: set[str] = set()
    data_attrs: list[str] = []

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        text = ""

    for m in INT_RE.findall(text):
        try:
            num = int(m)
            if (ALLOWED_MIN <= num <= ALLOWED_MAX) or (num in FORBIDDEN_PORTS):
                ports.add(num)
        except ValueError:
            continue

    for m in AGENT_REF_RE.findall(text):
        agent_refs.add(m.lower())

    # html specifics
    if path.suffix.lower() in {".html", ".htm"}:
        for m in DATA_ATTR_RE.findall(text):
            data_attrs.append(m)
        if "<form" in text.lower():
            endpoints.append("form")
        if "<nav" in text.lower():
            endpoints.append("nav")

    return endpoints, ports, agent_refs, data_attrs


def main() -> int:
    if not BASELINE_PATH.exists():
        print(f"❌ Baseline not found: {BASELINE_PATH}")
        return 1

    raw = BASELINE_PATH.read_bytes()
    baseline_hash = hashlib.sha256(raw).hexdigest()
    baseline = yaml.safe_load(raw)

    agents = baseline.get("agents", [])
    agent_map = {a["id"]: a for a in agents}
    pr = baseline.get("port_policy", {}).get("allowed_range", [1, 65535])
    global ALLOWED_MIN, ALLOWED_MAX, FORBIDDEN_PORTS
    ALLOWED_MIN, ALLOWED_MAX = pr[0], pr[1]
    FORBIDDEN_PORTS = set(baseline.get("port_policy", {}).get("forbidden_ports", []))
    forbidden_ports = FORBIDDEN_PORTS

    inventory: dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "baseline_hash": baseline_hash,
        "agents": [],
        "errors": [],
    }

    errors: list[str] = []

    # deterministic order
    for aid in sorted(agent_map.keys(), key=lambda x: int(x[5:])):
        a = agent_map[aid]
        folder = ROOT / a["folder"]
        report = {
            "id": aid,
            "folder": a["folder"],
            "file_count": 0,
            "files": [],
            "imports": [],
            "endpoints": [],
            "ports_detected": [],
            "agent_references": [],
            "flags": {
                "has_main": False,
                "has_requirements": False,
                "has_readme": False,
                "has_tests": False,
                "has_dockerfile": False,
            },
        }

        if not folder.exists():
            errors.append(f"Agent {aid}: folder missing: {a['folder']}")
            inventory["agents"].append(report)
            continue

        # recursively enumerate files in deterministic order
        all_files = sorted([p for p in folder.rglob("*") if p.is_file()], key=lambda p: str(p.relative_to(ROOT)))
        if not all_files:
            errors.append(f"Agent {aid}: folder empty: {a['folder']}")

        report["file_count"] = len(all_files)

        imports_set: set[str] = set()
        endpoints_set: set[str] = set()
        ports_set: set[int] = set()
        agent_refs_set: set[str] = set()

        for p in all_files:
            rel = str(p.relative_to(ROOT))
            sha = compute_sha256(p)
            size = p.stat().st_size
            report["files"].append({"relpath": rel, "size": size, "sha256": sha})

            # flags
            if p.name == "main.py":
                report["flags"]["has_main"] = True
            if p.name == "requirements.txt":
                report["flags"]["has_requirements"] = True
            if p.name.lower().startswith("readme"):
                report["flags"]["has_readme"] = True
            if p.match("**/tests/**") or p.name.lower().startswith("test_"):
                report["flags"]["has_tests"] = True
            if p.name == "Dockerfile":
                report["flags"]["has_dockerfile"] = True

            # extract based on suffix
            sfx = p.suffix.lower()
            if sfx == ".py":
                imps, ends, ports_found, agent_refs = extract_from_py(p)
                imports_set.update(imps)
                endpoints_set.update(ends)
                ports_set.update(ports_found)
                agent_refs_set.update(agent_refs)
            elif sfx in {".html", ".htm", ".json", ".yaml", ".yml", ".env", ".txt"}:
                ends, ports_found, agent_refs, data_attrs = extract_from_text(p)
                endpoints_set.update(ends)
                ports_set.update(ports_found)
                agent_refs_set.update(agent_refs)
            else:
                # generic text scan for agent refs and ports
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    text = ""
                for m in AGENT_REF_RE.findall(text):
                    agent_refs_set.add(m.lower())
                for m in INT_RE.findall(text):
                    try:
                        num = int(m)
                        if (ALLOWED_MIN <= num <= ALLOWED_MAX) or (num in FORBIDDEN_PORTS):
                            ports_set.add(num)
                    except Exception:
                        continue

        report["imports"] = sorted(imports_set)
        report["endpoints"] = sorted(endpoints_set)
        report["ports_detected"] = sorted(ports_set)
        report["agent_references"] = sorted(agent_refs_set)

        # validations per-agent
        # unknown agent references
        for ref in report["agent_references"]:
            if ref not in agent_map:
                errors.append(f"Agent {aid}: unknown agent reference detected: {ref}")

        # forbidden ports
        for pnum in report["ports_detected"]:
            if pnum in forbidden_ports:
                errors.append(f"Agent {aid}: forbidden port detected in files: {pnum}")

        # port mismatch vs baseline: if any ports detected and any differ from baseline port -> fail
        if report["ports_detected"]:
            baseline_port = a.get("port")
            non_matching = [pnum for pnum in report["ports_detected"] if pnum != baseline_port]
            if non_matching:
                errors.append(f"Agent {aid}: port mismatch; baseline={baseline_port} found={report['ports_detected']}")

        inventory["agents"].append(report)

    inventory["errors"] = errors

    # write artifact in deterministic ordering
    # to ensure stable JSON, sort agents by id
    inventory["agents"] = sorted(inventory["agents"], key=lambda x: int(x["id"][5:]))

    with open(ARTIFACT_PATH, "w") as f:
        json.dump(inventory, f, indent=2, sort_keys=True)

    if errors:
        print(f"❌ Agent discovery completed with {len(errors)} errors. See {ARTIFACT_PATH}")
        for e in errors:
            print(" -", e)
        return 1

    print(f"✅ Agent discovery completed successfully. Inventory: {ARTIFACT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
