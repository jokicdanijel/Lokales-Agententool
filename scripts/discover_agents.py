#!/usr/bin/env python3
"""Deterministic agent discovery for PORTIER 3.0 (read-only, no network)."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except Exception:
    print("ERROR: Missing 'pyyaml'. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "system_baseline.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_PATH = ARTIFACTS_DIR / "Agent_discovery.json"

IGNORE_DIRS = {
    ".git", ".github", "__pycache__", ".mypy_cache", ".pytest_cache",
    ".venv", "venv", "venv312", "venv313",
    "node_modules", ".idea", ".vscode", "dist", "build",
}

TEXT_FILE_EXTS = {
    ".py", ".sh", ".yml", ".yaml", ".json", ".jsonl", ".toml", ".md",
    ".html", ".css", ".js", ".txt", ".conf", ".ini",
}

PORT_RANGE_MIN, PORT_RANGE_MAX = 12344, 12399
PORT_NUM_RE = re.compile(r"\b(12[0-9]{3})\b")

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_text(t: str) -> str:
    return sha256_bytes(t.encode("utf-8"))

def read_text_safe(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

def should_descend_dir(path: Path) -> bool:
    return path.name not in IGNORE_DIRS

def stable_rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()

def load_baseline() -> Dict[str, Any]:
    if not BASELINE_PATH.exists():
        raise FileNotFoundError(f"Missing baseline: {BASELINE_PATH}")
    raw = BASELINE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("system_baseline.yaml is not a dict")
    return data

def expected_agent_ids() -> List[str]:
    return [f"opena{i}" for i in range(1, 22)]

def build_baseline_maps(data: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, str]]:
    agents = data.get("agents") or []
    id_to_port: Dict[str, int] = {}
    id_to_folder: Dict[str, str] = {}
    for a in agents:
        if not isinstance(a, dict):
            continue
        aid = str(a.get("id", "")).strip()
        if not aid:
            continue
        id_to_port[aid] = int(a.get("port", 0))
        id_to_folder[aid] = str(a.get("folder_path", "")).strip()
    return id_to_port, id_to_folder

@dataclass(frozen=True)
class FileHit:
    file: str
    ports: List[int]

def scan_agent_folder(agent_id: str, folder: Path) -> Tuple[List[str], str]:
    files: List[Path] = []
    stack = [folder]
    while stack:
        d = stack.pop()
        try:
            entries = sorted(list(d.iterdir()), key=lambda p: p.name)
        except Exception:
            entries = []
        dirs = []
        for e in entries:
            if e.is_dir():
                if should_descend_dir(e):
                    dirs.append(e)
            elif e.is_file():
                files.append(e)
        for dd in reversed(dirs):
            stack.append(dd)

    rel_files = [stable_rel(p) for p in files]
    rel_files.sort()

    h = hashlib.sha256()
    for rf in rel_files:
        h.update(rf.encode("utf-8"))
        h.update(b"\n")
        absp = ROOT / rf
        try:
            content = absp.read_bytes()
        except Exception:
            content = b""
        h.update(sha256_bytes(content).encode("utf-8"))
        h.update(b"\n")
    return rel_files, h.hexdigest()

def find_port_references_in_text(text: str) -> List[int]:
    hits: List[int] = []
    for m in PORT_NUM_RE.finditer(text):
        try:
            p = int(m.group(1))
        except Exception:
            continue
        if PORT_RANGE_MIN <= p <= PORT_RANGE_MAX:
            hits.append(p)
    return sorted(set(hits))

def scan_ports_in_files(file_list: List[str]) -> Tuple[List[FileHit], List[int]]:
    hits: List[FileHit] = []
    used: List[int] = []

    for rf in file_list:
        p = ROOT / rf
        if p.suffix.lower() not in TEXT_FILE_EXTS:
            continue
        txt = read_text_safe(p)
        if txt is None:
            continue
        ports = find_port_references_in_text(txt)
        if ports:
            hits.append(FileHit(file=rf, ports=ports))
            used.extend(ports)

    return sorted(hits, key=lambda x: x.file), sorted(set(used))

def write_artifact(payload: Dict[str, Any]) -> None:
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def main() -> None:
    errors: List[str] = []

    try:
        baseline_raw = BASELINE_PATH.read_text(encoding="utf-8")
        baseline_hash = sha256_text(baseline_raw)
        baseline = load_baseline()
    except Exception as e:
        errors.append(f"Baseline load failed: {e}")
        baseline_hash = None
        baseline = {}

    if errors:
        write_artifact({"timestamp_utc": utc_now(), "success": False, "errors": errors, "warnings": []})
        print("AGENT DISCOVERY: FAIL", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        sys.exit(1)

    id_to_port, id_to_folder = build_baseline_maps(baseline)
    exp = expected_agent_ids()
    discovered: List[Dict[str, Any]] = []

    for aid in exp:
        folder_rel = id_to_folder.get(aid, "")
        if not folder_rel:
            errors.append(f"{aid}: folder_path missing")
            continue
        folder_abs = (ROOT / folder_rel).resolve()

        if not folder_abs.exists():
            errors.append(f"{aid}: folder_path not found: {folder_rel}")
            continue

        try:
            nonempty = any(folder_abs.iterdir())
        except Exception:
            nonempty = False
        if not nonempty:
            errors.append(f"{aid}: agent folder is empty: {folder_rel}")
            continue

        inventory, folder_hash = scan_agent_folder(aid, folder_abs)
        file_hits, ports_used = scan_ports_in_files(inventory)
        base_port = int(id_to_port.get(aid, -1))

        discovered.append({
            "id": aid,
            "folder_path": folder_rel,
            "baseline_port": base_port,
            "inventory_count": len(inventory),
            "folder_hash_sha256": folder_hash,
            "inventory_files": inventory,
            "port_references": {
                "ports_used": ports_used,
                "files": [{"file": h.file, "ports": h.ports} for h in file_hits],
            },
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
        "warnings": [],
        "errors": errors,
    }

    write_artifact(payload)

    if not success:
        print("AGENT DISCOVERY: FAIL", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        sys.exit(1)

    print("AGENT DISCOVERY: OK")
    print(f"Discovered {len(discovered_sorted)} agents")
    print(f"Artifact written: {ARTIFACT_PATH}")
    sys.exit(0)

if __name__ == "__main__":
    main()
