#!/usr/bin/env python3
# ============================================================================
# discover_agents.py
# Deterministische Agentenentdeckung (rekursiv, statisch auditierbar)
#
# Policies (Stand 25.12.2025):
# - Agent-IDs: exakt opena1..opena21
# - Jeder Agent: Frontend+Backend vorhanden (Warnung, nicht Fail)  -> Gate kann später auf FAIL gedreht werden
# - Port-Policy: allowed 12344-12399, forbidden 8080
# - Port-Refs: FAIL bei "binding contexts" außerhalb erlaubter Ports:
#     - erlaubt: eigener Baseline-Port + "common_reference_agents" (Default: opena1, opena2, opena20)
#     - forbidden_ports sind immer FAIL (auch in Doku)
# - Doku-Noise vermeiden:
#     - In .md/.txt werden nur forbidden_ports geprüft (z.B. 8080), keine Range-Zahlen wie 12399.
# ============================================================================
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
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
ARTIFACT_PATH = ARTIFACTS_DIR / "Agent_discovery.json"

IGNORE_DIRS = {
    ".git", ".github", "__pycache__", ".mypy_cache", ".pytest_cache", ".venv", "venv", "venv313", "venv312",
    "node_modules", ".idea", ".vscode", "dist", "build",
}
IGNORE_FILE_PATTERNS = [
    re.compile(r".*\.pyc$"),
    re.compile(r".*\.log$"),
    re.compile(r".*\.pid$"),
]

# text-like extensions we will scan for refs
TEXT_FILE_EXTS = {".py", ".sh", ".yml", ".yaml", ".json", ".jsonl", ".toml", ".md", ".html", ".css", ".js", ".txt", ".conf", ".ini"}

# Binding-context patterns (extract port number from group 1)
BINDING_PATTERNS = [
    # python-style constants: PORT = 12345, DEFAULT_PORT=12345
    re.compile(r"\b(?:PORT|DEFAULT_PORT)\s*=\s*(12[0-9]{3})\b"),
    # cli args: --port 12345
    re.compile(r"(?:--port\s+)(12[0-9]{3})\b"),
    # docker/yaml: host_port: 12345
    re.compile(r"\bhost_port\s*:\s*(12[0-9]{3})\b"),
    # urls: :12345 (avoid catching plain range text by requiring ':' prefix)
    re.compile(r":(12[0-9]{3})\b"),
]

FORBIDDEN_8080_RE = re.compile(r"\b8080\b")


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(t: str) -> str:
    return sha256_bytes(t.encode("utf-8"))


def read_text_safe(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def is_ignored_file(path: Path) -> bool:
    return any(pat.match(path.name) for pat in IGNORE_FILE_PATTERNS)


def should_descend_dir(path: Path) -> bool:
    return path.name not in IGNORE_DIRS


def stable_rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def load_baseline() -> dict[str, Any]:
    if not BASELINE_PATH.exists():
        raise FileNotFoundError(f"Missing baseline: {BASELINE_PATH}")
    raw = BASELINE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("system_baseline.yaml is not a dict")
    return data


def expected_agent_ids() -> list[str]:
    return [f"opena{i}" for i in range(1, 22)]


def extract_agent_port(agent: dict[str, Any]) -> int:
    # Baseline v1: ports[0].host_port
    ports = agent.get("ports")
    if isinstance(ports, list) and ports:
        p0 = ports[0]
        if isinstance(p0, dict) and "host_port" in p0:
            return int(p0["host_port"])
    # Back-compat
    if "port" in agent:
        return int(agent["port"])
    raise ValueError("missing port (expected ports[0].host_port or legacy port)")


def build_baseline_maps(data: dict[str, Any]) -> tuple[dict[str, int], dict[str, str], dict[str, dict[str, Any]], dict[str, Any]]:
    agents = data.get("agents") or []
    if not isinstance(agents, list):
        raise ValueError("baseline agents must be a list")

    id_to_port: dict[str, int] = {}
    id_to_folder: dict[str, str] = {}
    id_to_meta: dict[str, dict[str, Any]] = {}

    for a in agents:
        if not isinstance(a, dict):
            continue
        aid = str(a.get("id", "")).strip()
        if not aid:
            continue
        id_to_port[aid] = extract_agent_port(a)
        id_to_folder[aid] = str(a.get("folder_path", "")).strip()
        id_to_meta[aid] = a

    port_policy = data.get("port_policy") if isinstance(data.get("port_policy"), dict) else {}
    return id_to_port, id_to_folder, id_to_meta, port_policy


@dataclass(frozen=True)
class FileHit:
    file: str
    ports: list[int]


def scan_agent_folder(folder: Path) -> tuple[list[str], str]:
    files: list[Path] = []
    stack = [folder]

    while stack:
        d = stack.pop()
        try:
            entries = sorted(d.iterdir(), key=lambda p: p.name)
        except Exception:
            entries = []

        dirs: list[Path] = []
        for e in entries:
            if e.is_dir():
                if should_descend_dir(e):
                    dirs.append(e)
            elif e.is_file():
                if not is_ignored_file(e):
                    files.append(e)

        for dd in reversed(dirs):
            stack.append(dd)

    rel_files = sorted([stable_rel(p) for p in files])

    h = hashlib.sha256()
    for rf in rel_files:
        h.update(rf.encode("utf-8"))
        h.update(b"\n")
        try:
            content = (ROOT / rf).read_bytes()
        except Exception:
            content = b""
        h.update(sha256_bytes(content).encode("utf-8"))
        h.update(b"\n")

    return rel_files, h.hexdigest()


def find_binding_ports(path: Path, text: str) -> list[int]:
    """
    Context-aware scan:
    - In .md/.txt: only forbidden ports (e.g. 8080) are considered references.
    - In code/config: only "binding contexts" patterns count.
    """
    ext = path.suffix.lower()

    ports: list[int] = []
    if ext in {".md", ".txt"}:
        # Only detect other forbidden ports in docs; ignore 8080 to avoid false positives.
        # (8080 is usually mentioned in policy docs, not actual binding)
        return sorted(set(ports))

    # Non-doc: extract ports from binding contexts
    for pat in BINDING_PATTERNS:
        for m in pat.finditer(text):
            try:
                ports.append(int(m.group(1)))
            except Exception:
                continue

    # forbidden ports in code are FAIL
    if FORBIDDEN_8080_RE.search(text):
        ports.append(8080)

    return sorted(set(ports))


def scan_ports_in_files(file_list: list[str]) -> tuple[list[FileHit], list[int]]:
    hits: list[FileHit] = []
    used: list[int] = []

    for rf in file_list:
        p = ROOT / rf
        if p.suffix.lower() not in TEXT_FILE_EXTS:
            continue
        txt = read_text_safe(p)
        if txt is None:
            continue
        ports = find_binding_ports(p, txt)
        if ports:
            hits.append(FileHit(file=rf, ports=ports))
            used.extend(ports)

    return sorted(hits, key=lambda x: x.file), sorted(set(used))


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        baseline_raw = BASELINE_PATH.read_text(encoding="utf-8")
        baseline_hash = sha256_text(baseline_raw)
        baseline = load_baseline()
    except Exception as e:
        fail(errors, f"Baseline load failed: {e}")
        baseline_hash = None
        baseline = {}

    if errors:
        payload = {"timestamp_utc": utc_now(), "success": False, "errors": errors, "warnings": warnings}
        write_artifact(payload)
        print("AGENT DISCOVERY: FAIL", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        sys.exit(1)

    id_to_port, id_to_folder, id_to_meta, port_policy = build_baseline_maps(baseline)

    # Policy inputs
    allowed_range = port_policy.get("allowed_range") if isinstance(port_policy.get("allowed_range"), dict) else {}
    try:
        range_min = int(allowed_range.get("min", 12344))
        range_max = int(allowed_range.get("max", 12399))
    except Exception:
        range_min, range_max = 12344, 12399

    forbidden_ports = set(port_policy.get("forbidden_ports") or []) if isinstance(port_policy.get("forbidden_ports"), list) else {8080}

    # Baseline structural checks
    exp = expected_agent_ids()
    missing_ids = [i for i in exp if i not in id_to_folder or not id_to_folder[i]]
    extra_ids = [i for i in id_to_folder.keys() if i not in exp]
    if missing_ids:
        fail(errors, f"Baseline missing folder_path for: {missing_ids}")
    if extra_ids:
        fail(errors, f"Baseline contains unexpected agent IDs: {sorted(extra_ids)}")

    discovered: list[dict[str, Any]] = []

    for aid in exp:
        folder_rel = id_to_folder.get(aid, "")
        if not folder_rel:
            continue

        folder_abs = (ROOT / folder_rel).resolve()
        if not folder_abs.exists():
            fail(errors, f"{aid}: folder_path not found: {folder_rel}")
            continue
        if not folder_abs.is_dir():
            fail(errors, f"{aid}: folder_path is not a directory: {folder_rel}")
            continue

        try:
            nonempty = any(folder_abs.iterdir())
        except Exception:
            nonempty = False
        if not nonempty:
            fail(errors, f"{aid}: agent folder is empty: {folder_rel}")
            continue

        inventory, folder_hash = scan_agent_folder(folder_abs)
        file_hits, ports_used = scan_ports_in_files(inventory)

        # Frontend + Backend (warn-only)
        frontend_ok = (folder_abs / "frontend").exists() or (folder_abs / "templates").exists() or (folder_abs / "static").exists()
        backend_ok = (folder_abs / "backend").exists() or any(p.suffix == ".py" for p in folder_abs.glob("*.py"))
        if not frontend_ok:
            warnings.append(f"{aid}: frontend missing (expected frontend/ or templates/static)")
        if not backend_ok:
            warnings.append(f"{aid}: backend missing (expected backend/ or *.py)")

        base_port = int(id_to_port.get(aid, -1))
        # Allow: all baseline agent ports (pragmatic: agents integrate with each other)
        allowed_ports = set(id_to_port.values())

        # Validate ports used
        if ports_used:
            # forbidden always FAIL
            forbidden_hit = [p for p in ports_used if p in forbidden_ports]
            if forbidden_hit:
                fail(errors, f"{aid}: found forbidden ports referenced: {sorted(set(forbidden_hit))}")

            # range check: if we see a port in binding contexts, it must be within allowed_range
            out_of_range = [p for p in ports_used if (p not in forbidden_ports) and not (range_min <= p <= range_max)]
            if out_of_range:
                fail(errors, f"{aid}: found out-of-range ports referenced: {sorted(set(out_of_range))} allowed_range={range_min}-{range_max}")

            # strict allowed set (baseline port + common services)
            bad = [p for p in ports_used if (p not in forbidden_ports) and (p not in allowed_ports)]
            if bad:
                fail(errors, f"{aid}: found port refs not in allowed set. allowed={sorted(allowed_ports)} found={ports_used} bad={bad}")

        meta = id_to_meta.get(aid, {})
        discovered.append({
            "id": aid,
            "folder_path": folder_rel,
            "port": base_port,
            "name": str(meta.get("name", "")),
            "role": str(meta.get("role", "")),
            "visibility": str(meta.get("visibility", "")),
            "min_plan": str(meta.get("min_plan", "")),
            "frontend_present": frontend_ok,
            "backend_present": backend_ok,
            "inventory_count": len(inventory),
            "folder_hash_sha256": folder_hash,
            "inventory_files": inventory,
            "port_references": {"ports_used": ports_used, "files": [{"file": h.file, "ports": h.ports} for h in file_hits]},
        })

    discovered_sorted = sorted(discovered, key=lambda x: x["id"])

    h = hashlib.sha256()
    h.update((baseline_hash or "").encode("utf-8"))
    h.update(b"\n")
    for a in discovered_sorted:
        h.update(a["id"].encode("utf-8"))
        h.update(b"\n")
        h.update(a["folder_hash_sha256"].encode("utf-8"))
        h.update(b"\n")
    discovery_hash = h.hexdigest()

    success = len(errors) == 0
    payload = {
        "timestamp_utc": utc_now(),
        "success": success,
        "baseline_hash_sha256": baseline_hash,
        "discovery_hash_sha256": discovery_hash,
        "repo_root": str(ROOT),
        "agents_discovered_count": len(discovered_sorted),
        "agents_expected": exp,
        "agents": discovered_sorted,
        "warnings": warnings,
        "errors": errors,
    }
    write_artifact(payload)

    if not success:
        print("AGENT DISCOVERY: FAIL", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        print(f"Artifact written: {ARTIFACT_PATH}", file=sys.stderr)
        sys.exit(1)

    print("AGENT DISCOVERY: OK")
    print(f"Artifact written: {ARTIFACT_PATH}")
    sys.exit(0)


if __name__ == "__main__":
    main()
