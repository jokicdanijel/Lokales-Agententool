#!/usr/bin/env python3
# ============================================================================
# discover_agents.py
# Deterministische Agentenentdeckung (rekursiv, statisch auditierbar)
# KORRIGIERTE PORT-POLICY: Erlaubt opena1 (Koordinator), opena2 (Archivar),
# opena20 (Dashboard) als Common Services + eigenen Port
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
    ".git",
    ".github",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "venv",
    "venv313",
    "venv312",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "build",
}
IGNORE_FILE_PATTERNS = [
    re.compile(r".*\.pyc$"),
    re.compile(r".*\.log$"),
    re.compile(r".*\.pid$"),
]

TEXT_FILE_EXTS = {
    ".py",
    ".sh",
    ".yml",
    ".yaml",
    ".json",
    ".jsonl",
    ".toml",
    ".md",
    ".html",
    ".css",
    ".js",
    ".txt",
    ".conf",
    ".ini",
}

PORT_RANGE_MIN = 12344
PORT_RANGE_MAX = 12399
PORT_NUM_RE = re.compile(r"\b(12[0-9]{3})\b")
URL_PORT_RE = re.compile(r":(12[0-9]{3})\b")


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(t: str) -> str:
    return sha256_bytes(t.encode("utf-8"))


def parse_allowed_range(port_policy: dict[str, Any]) -> tuple[int, int]:
    """Parse port range from BOTH formats:
    A) allowed_range: \"12344-12399\" (string)
    B) allow_range: {min: 12344, max: 12399} (dict)
    """
    # Format B: allow_range dict
    if isinstance(port_policy.get("allow_range"), dict):
        ar = port_policy["allow_range"]
        try:
            return int(ar.get("min", PORT_RANGE_MIN)), int(ar.get("max", PORT_RANGE_MAX))
        except Exception:
            print(f"ERROR: port_policy.allow_range must contain int min/max, got: {ar}", file=sys.stderr)
            sys.exit(1)

    # Format A: allowed_range string
    allowed = str(port_policy.get("allowed_range", f"{PORT_RANGE_MIN}-{PORT_RANGE_MAX}"))
    parts = allowed.split("-")
    if len(parts) != 2:
        print(f"ERROR: port_policy.allowed_range must be 'min-max', got: {allowed}", file=sys.stderr)
        sys.exit(1)
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        print(f"ERROR: port_policy.allowed_range must be ints, got: {allowed}", file=sys.stderr)
        sys.exit(1)


def read_text_safe(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def is_ignored_file(path: Path) -> bool:
    for pat in IGNORE_FILE_PATTERNS:
        if pat.match(path.name):
            return True
    return False


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


def build_baseline_maps(data: dict[str, Any]) -> tuple[dict[str, int], dict[str, str]]:
    agents = data.get("agents") or []
    if not isinstance(agents, list):
        raise ValueError("baseline agents must be a list")
    id_to_port: dict[str, int] = {}
    id_to_folder: dict[str, str] = {}
    for a in agents:
        if not isinstance(a, dict):
            continue
        aid = str(a.get("id", "")).strip()
        if not aid:
            continue
        id_to_port[aid] = int(a.get("port"))
        id_to_folder[aid] = str(a.get("folder_path", "")).strip()
    return id_to_port, id_to_folder


@dataclass(frozen=True)
class FileHit:
    file: str
    ports: list[int]


def scan_agent_folder(agent_id: str, folder: Path) -> tuple[list[str], str]:
    files: list[Path] = []
    stack = [folder]

    while stack:
        d = stack.pop()
        try:
            entries = sorted(d.iterdir(), key=lambda p: p.name)
        except Exception:
            entries = []

        dirs = []
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


def find_port_references_in_text(text: str) -> list[int]:
    hits: list[int] = []
    for m in PORT_NUM_RE.finditer(text):
        try:
            p = int(m.group(1))
        except Exception:
            continue
        if PORT_RANGE_MIN <= p <= PORT_RANGE_MAX:
            hits.append(p)

    for m in URL_PORT_RE.finditer(text):
        try:
            p = int(m.group(1))
        except Exception:
            continue
        if PORT_RANGE_MIN <= p <= PORT_RANGE_MAX:
            hits.append(p)

    return sorted(set(hits))


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
        ports = find_port_references_in_text(txt)
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
        payload = {
            "timestamp_utc": utc_now(),
            "success": False,
            "errors": errors,
            "warnings": warnings,
        }
        write_artifact(payload)
        print("AGENT DISCOVERY: FAIL", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        sys.exit(1)

    id_to_port, id_to_folder = build_baseline_maps(baseline)

    exp = expected_agent_ids()
    missing_ids = [i for i in exp if i not in id_to_folder or not id_to_folder[i]]
    extra_ids = [i for i in id_to_folder.keys() if i not in exp]

    if missing_ids:
        fail(errors, f"Baseline missing folder_path for: {missing_ids}")
    if extra_ids:
        fail(errors, f"Baseline contains unexpected agent IDs: {sorted(extra_ids)}")

    discovered: list[dict[str, Any]] = []

    # Common services alle Agents dürfen referenzieren
    common_ports = {
        int(id_to_port.get("opena1", 12344)),  # Koordinator
        int(id_to_port.get("opena2", 12345)),  # Archivar
        int(id_to_port.get("opena20", 12349)),  # Dashboard
    }

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

        inventory, folder_hash = scan_agent_folder(aid, folder_abs)
        file_hits, ports_used = scan_ports_in_files(inventory)

        base_port = int(id_to_port.get(aid, -1))
        allowed = common_ports | {base_port}

        if ports_used:
            bad = [p for p in ports_used if p not in allowed]
            if bad:
                fail(
                    errors,
                    f"{aid}: found port references not in allowed set. "
                    f"allowed={sorted(allowed)} found={ports_used} bad={bad}",
                )

        discovered.append(
            {
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
            }
        )

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
