#!/usr/bin/env python3
"""
Ports & IDs Compliance Scanner (Enhanced)
==========================================
Context-aware validation with false-positive reduction.

FAIL-HARD RULES:
1. Exactly opena1..opena21 in baseline
2. Ports unique and in allowed range (12344-12399)
3. Forbidden host ports (8080, 3000) only in allowed services
4. Line-based ID<->port mismatch (only when exactly 1 ID + 1 port on same line)
5. Docker-compose host port validation

EXIT CODES:
- 0: Compliance passed
- 1: Violations found (CI breaks)

Usage:
  python3 scripts/ports_ids_compliance_scanner_v2.py
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
SCANS_DIR = ROOT / "artifacts" / "scans"
SCANS_DIR.mkdir(parents=True, exist_ok=True)

BASELINE_FILE = ROOT / "system_baseline.yaml"
INVENTORY_CANDIDATES = [
    ROOT / "artifacts" / "agent_inventory.json",
    ROOT / "artifacts" / "agent_discovery.json",
]

# Policy
EXPECTED_AGENT_IDS = {f"opena{i}" for i in range(1, 22)}
FORBIDDEN_HOST_PORTS = {8080, 3000}
ALLOWED_PORT_MIN = 12344
ALLOWED_PORT_MAX = 12399

# Allowlist: these services may bind forbidden host ports
ALLOW_HOST_PORTS_FOR_SERVICE: dict[int, set[str]] = {
    8080: {"public-gateway", "nginx", "traefik"},
    3000: {"public-gateway", "nginx", "traefik"},
}

# Policy/validator files are allowed to mention forbidden ports in documentation
ALLOWLIST_POLICY_PATHS = {
    "system_baseline.yaml",
    "docs/PORTS_POLICY.md",
    "scripts/ports_ids_compliance_scanner.py",
    "scripts/ports_ids_compliance_scanner_v2.py",
    "scripts/validate_baseline.py",
}

# Scan settings
IGNORE_DIRS = {
    ".git",
    "venv",
    "venv313",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "build",
    "dist",
}
SCAN_EXTS = {".py", ".yaml", ".yml", ".json", ".md", ".txt", ".sh", ".bash"}
COMPOSE_FILENAMES = {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}

RE_OPENA = re.compile(r"\b(opena)(\d{1,3})\b", flags=re.IGNORECASE)
RE_NUMBER = re.compile(r"\b(\d{2,5})\b")
RE_LINE_SPLIT = re.compile(r"\r?\n")


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass(frozen=True)
class Occurrence:
    path: str
    line: int
    snippet: str


@dataclass
class ScanResult:
    timestamp: str
    passed: bool
    findings: dict[str, Any]
    messages: list[str]


# ============================================================================
# HELPERS
# ============================================================================


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)


def _is_ignored(path: Path) -> bool:
    parts = set(path.parts)
    return any(d in parts for d in IGNORE_DIRS)


def _read_text(path: Path, max_bytes: int = 1_000_000) -> str | None:
    try:
        raw = path.read_bytes()
    except Exception:
        return None
    if len(raw) > max_bytes:
        raw = raw[:max_bytes]
    return raw.decode("utf-8", errors="ignore")


def _safe_int(s: str) -> int | None:
    try:
        return int(s)
    except Exception:
        return None


def _extract_opena_ids(line: str) -> list[str]:
    ids: list[str] = []
    for m in RE_OPENA.finditer(line):
        ids.append(f"opena{int(m.group(2))}")
    return ids


def _extract_ports(line: str) -> list[int]:
    ports: list[int] = []
    for m in RE_NUMBER.finditer(line):
        n = _safe_int(m.group(1))
        if n is None:
            continue
        if n in FORBIDDEN_HOST_PORTS or (ALLOWED_PORT_MIN <= n <= ALLOWED_PORT_MAX) or n in (80, 443):
            ports.append(n)
    return ports


# ============================================================================
# LOADING
# ============================================================================


def load_baseline(path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    msgs: list[str] = []
    if not path.exists():
        return {}, [f"baseline file missing: {path}"]

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        agents = data.get("agents") or []
        out: dict[str, dict[str, Any]] = {}
        for a in agents:
            aid = str(a.get("id", "")).strip()
            if not aid:
                continue
            try:
                port = int(a.get("port"))
            except Exception:
                port = None
            out[aid] = {"port": port, "meta": a}
        return out, msgs
    except Exception as e:
        msgs.append(f"failed to parse baseline via PyYAML: {e}")
        return {}, msgs


def load_inventory_ids() -> tuple[list[str] | None, list[str]]:
    msgs: list[str] = []
    for p in INVENTORY_CANDIDATES:
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            msgs.append(f"failed to parse {p.name}: {e}")
            continue

        ids: list[str] = []
        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict) and entry.get("id"):
                    ids.append(str(entry["id"]))
        elif isinstance(data, dict):
            agents = data.get("agents")
            if isinstance(agents, list):
                for entry in agents:
                    if isinstance(entry, dict) and entry.get("id"):
                        ids.append(str(entry["id"]))
        msgs.append(f"loaded inventory from {p.name}")
        return ids, msgs

    msgs.append("no inventory file found")
    return None, msgs


# ============================================================================
# SCANNING
# ============================================================================


def iter_scan_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if _is_ignored(p):
            continue
        if p.is_dir():
            continue
        rel = _rel(p)
        if rel in ALLOWLIST_POLICY_PATHS:
            # still scanned for IDs/ports, but forbidden ports won't fail validation for allowlisted paths
            yield p
            continue
        if p.name in COMPOSE_FILENAMES:
            yield p
            continue
        if p.suffix.lower() in SCAN_EXTS or p.name.lower().startswith(".env"):
            yield p


def parse_compose_host_ports(compose_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Parse docker-compose YAML and extract host-published ports.
    Returns: (entries, messages)
    entries: [{service, host_port, container_port, raw}]
    """
    msgs: list[str] = []
    entries: list[dict[str, Any]] = []
    text = _read_text(compose_path)
    if text is None:
        return [], [f"failed to read compose: {_rel(compose_path)}"]

    try:
        import yaml  # type: ignore

        doc = yaml.safe_load(text) or {}
    except Exception as e:
        return [], [f"failed to parse compose YAML: {_rel(compose_path)}: {e}"]

    if not isinstance(doc, dict):
        return [], [f"compose not a mapping: {_rel(compose_path)}"]

    services = doc.get("services")
    if not isinstance(services, dict):
        return [], [f"compose missing services: {_rel(compose_path)}"]

    for service_name, svc in services.items():
        if not isinstance(service_name, str) or not isinstance(svc, dict):
            continue
        ports = svc.get("ports")
        if not ports:
            continue

        # ports can be list of strings ("12390:3000") or dicts (published/target) depending on compose version
        if isinstance(ports, list):
            for item in ports:
                if isinstance(item, str):
                    # Formats: "HOST:CONTAINER", "IP:HOST:CONTAINER", "HOST:CONTAINER/PROTO"
                    raw = item.strip().strip('"').strip("'")
                    proto = None
                    if "/" in raw:
                        raw, proto = raw.split("/", 1)
                    parts = raw.split(":")
                    host_port = None
                    container_port = None
                    if len(parts) == 2:
                        host_port = _safe_int(parts[0])
                        container_port = _safe_int(parts[1])
                    elif len(parts) == 3:
                        host_port = _safe_int(parts[1])
                        container_port = _safe_int(parts[2])
                    if host_port is not None and container_port is not None:
                        entries.append(
                            {
                                "service": service_name,
                                "host_port": host_port,
                                "container_port": container_port,
                                "raw": item,
                                "proto": proto,
                                "path": _rel(compose_path),
                            }
                        )
                elif isinstance(item, dict):
                    published = item.get("published")
                    target = item.get("target")
                    host_port = _safe_int(str(published)) if published is not None else None
                    container_port = _safe_int(str(target)) if target is not None else None
                    if host_port is not None and container_port is not None:
                        entries.append(
                            {
                                "service": service_name,
                                "host_port": host_port,
                                "container_port": container_port,
                                "raw": item,
                                "proto": item.get("protocol"),
                                "path": _rel(compose_path),
                            }
                        )
        else:
            msgs.append(f"compose ports unsupported type in {service_name}: {type(ports).__name__}")

    return entries, msgs


def scan_text_references(files: Sequence[Path]) -> tuple[dict[str, list[Occurrence]], dict[int, list[Occurrence]]]:
    opena_refs: dict[str, list[Occurrence]] = {}
    port_refs: dict[int, list[Occurrence]] = {}

    for p in files:
        rel = _rel(p)
        text = _read_text(p)
        if text is None:
            continue

        for idx, line in enumerate(RE_LINE_SPLIT.split(text), start=1):
            ids = _extract_opena_ids(line)
            ports = _extract_ports(line)
            if ids:
                for aid in ids:
                    opena_refs.setdefault(aid, []).append(Occurrence(rel, idx, line.strip()))
            if ports:
                for port in ports:
                    port_refs.setdefault(port, []).append(Occurrence(rel, idx, line.strip()))

    return opena_refs, port_refs


# ============================================================================
# VALIDATION
# ============================================================================


def validate(
    baseline: dict[str, dict[str, Any]],
    inventory_ids: list[str] | None,
    opena_refs: dict[str, list[Occurrence]],
    port_refs: dict[int, list[Occurrence]],
    compose_ports: list[dict[str, Any]],
) -> tuple[dict[str, Any], bool]:
    ok = True
    findings: dict[str, Any] = {}

    baseline_ids = set(baseline.keys())
    findings["baseline_ids"] = sorted(baseline_ids)

    id_mismatch = {
        "missing": sorted(EXPECTED_AGENT_IDS - baseline_ids),
        "extra": sorted(baseline_ids - EXPECTED_AGENT_IDS),
    }
    findings["baseline_id_mismatch"] = id_mismatch
    if id_mismatch["missing"] or id_mismatch["extra"]:
        ok = False

    # Baseline port constraints + duplicates
    port_map: dict[int, list[str]] = {}
    baseline_errors: list[str] = []
    baseline_id_to_port: dict[str, int] = {}

    for aid, info in baseline.items():
        port = info.get("port")
        if port is None:
            baseline_errors.append(f"{aid}: missing port")
            continue
        if not isinstance(port, int):
            baseline_errors.append(f"{aid}: port not int")
            continue
        baseline_id_to_port[aid] = port
        if port in FORBIDDEN_HOST_PORTS:
            baseline_errors.append(f"{aid}: forbidden port {port} in baseline")
        if not (ALLOWED_PORT_MIN <= port <= ALLOWED_PORT_MAX):
            baseline_errors.append(f"{aid}: port {port} out of allowed range")
        port_map.setdefault(port, []).append(aid)

    dup_ports = {p: ids for p, ids in port_map.items() if len(ids) > 1}
    findings["duplicate_ports_in_baseline"] = dup_ports
    if dup_ports:
        ok = False
    if baseline_errors:
        ok = False
    findings["baseline_errors"] = sorted(set(baseline_errors))

    # opena outside range in code
    outside: dict[str, Any] = {}
    for aid, occ in opena_refs.items():
        m = re.match(r"opena(\d{1,3})$", aid)
        if not m:
            continue
        n = int(m.group(1))
        if not (1 <= n <= 21):
            outside[aid] = [o.__dict__ for o in occ[:50]]
    findings["opena_outside_range"] = outside
    if outside:
        ok = False

    # Forbidden host ports (compose-driven, authoritative)
    forbidden_host_hits: list[dict[str, Any]] = []
    for entry in compose_ports:
        host_port = entry.get("host_port")
        service = str(entry.get("service", "")).strip().lower()
        if host_port is None:
            continue
        if host_port in FORBIDDEN_HOST_PORTS:
            allowed_services = ALLOW_HOST_PORTS_FOR_SERVICE.get(host_port, set())
            if service not in allowed_services:
                forbidden_host_hits.append(entry)
    findings["forbidden_host_ports_compose"] = forbidden_host_hits
    if forbidden_host_hits:
        ok = False

    # Forbidden ports referenced in code/config (heuristic; allow policy/validator paths)
    forbidden_literal_hits: dict[int, list[dict[str, Any]]] = {}
    for p in sorted(FORBIDDEN_HOST_PORTS):
        occ = port_refs.get(p, [])
        if not occ:
            continue
        bad: list[dict[str, Any]] = []
        for o in occ:
            if o.path in ALLOWLIST_POLICY_PATHS:
                continue
            # ignore docs mentioning policy
            if o.path.startswith("docs/"):
                continue
            # ignore mention inside yaml where it's clearly a container port (e.g., "12390:3000") - compose already handles
            if o.path.endswith((".yml", ".yaml")) and ":" in o.snippet:
                continue
            # ignore benign policy language
            lowered = o.snippet.lower()
            if "forbidden" in lowered or "verbot" in lowered or "policy" in lowered or "forbid" in lowered:
                continue
            bad.append(o.__dict__)
        if bad:
            forbidden_literal_hits[p] = bad[:200]
    findings["forbidden_port_literals_runtime"] = forbidden_literal_hits
    if forbidden_literal_hits:
        ok = False

    # Line-based ID<->Port mismatch detection (ONLY if exactly 1 ID and 1 port in line)
    mismatches: list[dict[str, Any]] = []
    # Build file->lines with id/port occurrences from the occurrences lists
    file_lines: dict[tuple[str, int], dict[str, Any]] = {}

    for aid, occs in opena_refs.items():
        for o in occs:
            key = (o.path, o.line)
            file_lines.setdefault(key, {"ids": set(), "ports": set(), "snippet": o.snippet})
            file_lines[key]["ids"].add(aid)

    for port, occs in port_refs.items():
        for o in occs:
            key = (o.path, o.line)
            file_lines.setdefault(key, {"ids": set(), "ports": set(), "snippet": o.snippet})
            file_lines[key]["ports"].add(port)

    for (path, line), info in file_lines.items():
        ids: set[str] = set(info.get("ids", set()))
        ports: set[int] = set(info.get("ports", set()))
        if len(ids) != 1 or len(ports) != 1:
            continue
        aid = next(iter(ids))
        port = next(iter(ports))
        if aid not in baseline_id_to_port:
            continue
        expected_port = baseline_id_to_port[aid]
        # Only mismatch on ports that look like agent ports (allowed range)
        if ALLOWED_PORT_MIN <= port <= ALLOWED_PORT_MAX and port != expected_port:
            mismatches.append(
                {
                    "file": path,
                    "line": line,
                    "id": aid,
                    "found_port": port,
                    "expected_port": expected_port,
                    "snippet": info.get("snippet", "").strip(),
                }
            )

    findings["id_port_mismatches_linelocal"] = mismatches[:200]
    if mismatches:
        ok = False

    # Inventory check
    if inventory_ids is not None:
        inv_set = set(inventory_ids)
        findings["inventory_ids"] = sorted(inv_set)
        inv_mismatch = {
            "missing": sorted(EXPECTED_AGENT_IDS - inv_set),
            "extra": sorted(inv_set - EXPECTED_AGENT_IDS),
        }
        findings["inventory_id_mismatch"] = inv_mismatch
        if inv_mismatch["missing"] or inv_mismatch["extra"]:
            ok = False
    else:
        findings["inventory_ids"] = None

    findings["summary"] = {
        "ok": ok,
        "baseline_agent_count": len(baseline_ids),
        "opena_refs_found": len(opena_refs),
        "ports_found": len(port_refs),
        "compose_entries": len(compose_ports),
    }

    return findings, ok


# ============================================================================
# REPORT
# ============================================================================


def render_md(findings: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Ports & IDs Compliance Scan (Enhanced)")
    lines.append("")
    lines.append(f"**Status:** {'✅ PASS' if findings.get('summary', {}).get('ok') else '❌ FAIL'}")
    lines.append("")

    lines.append("## Summary")
    summary = findings.get("summary", {})
    lines.append(f"- Baseline agents: {summary.get('baseline_agent_count', 0)}")
    lines.append(f"- opena references found: {summary.get('opena_refs_found', 0)}")
    lines.append(f"- Ports found: {summary.get('ports_found', 0)}")
    lines.append(f"- Compose entries: {summary.get('compose_entries', 0)}")
    lines.append("")

    id_mismatch = findings.get("baseline_id_mismatch", {})
    if id_mismatch.get("missing") or id_mismatch.get("extra"):
        lines.append("## ❌ Baseline ID mismatch")
        lines.append(f"- Missing: {id_mismatch.get('missing', [])}")
        lines.append(f"- Extra: {id_mismatch.get('extra', [])}")
        lines.append("")

    baseline_errors = findings.get("baseline_errors", [])
    if baseline_errors:
        lines.append("## ❌ Baseline errors")
        for e in baseline_errors[:50]:
            lines.append(f"- {e}")
        lines.append("")

    dup_ports = findings.get("duplicate_ports_in_baseline", {})
    if dup_ports:
        lines.append("## ❌ Duplicate ports in baseline")
        for p, ids in dup_ports.items():
            lines.append(f"- Port {p}: {ids}")
        lines.append("")

    outside = findings.get("opena_outside_range", {})
    if outside:
        lines.append("## ❌ opena IDs outside 1..21")
        for aid, occ in outside.items():
            lines.append(f"- {aid} in {len(occ)} locations")
        lines.append("")

    forbidden_compose = findings.get("forbidden_host_ports_compose", [])
    if forbidden_compose:
        lines.append("## ❌ Forbidden host ports in docker-compose")
        for entry in forbidden_compose[:50]:
            lines.append(
                f"- Service {entry.get('service')}: host port {entry.get('host_port')} (raw: {entry.get('raw')})"
            )
        lines.append("")

    forbidden_literal = findings.get("forbidden_port_literals_runtime", {})
    if forbidden_literal:
        lines.append("## ❌ Forbidden port literals in code")
        for p, occ in forbidden_literal.items():
            lines.append(f"### Port {p} ({len(occ)} occurrences)")
            for o in occ[:10]:
                lines.append(f"- {o.get('path')}:{o.get('line')} — `{o.get('snippet', '')[:100]}`")
            lines.append("")

    mismatches = findings.get("id_port_mismatches_linelocal", [])
    if mismatches:
        lines.append("## ⚠️ ID<->Port mismatches (line-local)")
        lines.append("*Only lines with exactly 1 ID and 1 port are checked*")
        lines.append("")
        for m in mismatches[:50]:
            lines.append(
                f"- {m.get('file')}:{m.get('line')}: {m.get('id')} found port {m.get('found_port')}, expected {m.get('expected_port')}"
            )
            lines.append(f"  ```{m.get('snippet', '')[:100]}```")
        lines.append("")

    inv_mismatch = findings.get("inventory_id_mismatch")
    if inv_mismatch:
        lines.append("## ⚠️ Inventory mismatch")
        lines.append(f"- Missing: {inv_mismatch.get('missing', [])}")
        lines.append(f"- Extra: {inv_mismatch.get('extra', [])}")
        lines.append("")

    if findings.get("summary", {}).get("ok"):
        lines.append("---")
        lines.append("✅ All compliance checks passed")

    lines.append("")
    lines.append("---")
    lines.append(f"*Generated by {Path(__file__).name}*")
    return "\n".join(lines)


# ============================================================================
# MAIN
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    print("=" * 60)
    print("PORTS & IDS COMPLIANCE SCANNER (Enhanced)")
    print("=" * 60)
    print()

    messages: list[str] = []

    # Load baseline
    baseline, b_msgs = load_baseline(BASELINE_FILE)
    messages.extend(b_msgs)
    if not baseline:
        print("❌ Failed to load baseline")
        for m in b_msgs:
            print(f"   {m}")
        return 1
    print(f"✓ Loaded baseline ({len(baseline)} agents)")

    # Load inventory (optional)
    inventory_ids, i_msgs = load_inventory_ids()
    messages.extend(i_msgs)
    if inventory_ids:
        print(f"✓ Loaded inventory ({len(inventory_ids)} agents)")
    else:
        print("ℹ No inventory found (optional)")

    # Scan files
    print("\nScanning files...")
    scan_files = list(iter_scan_files(ROOT))
    print(f"  {len(scan_files)} files to scan")

    opena_refs, port_refs = scan_text_references(scan_files)
    print(f"  Found {len(opena_refs)} opena references")
    print(f"  Found {len(port_refs)} port references")

    # Parse compose files
    compose_ports: list[dict[str, Any]] = []
    compose_msgs: list[str] = []
    for p in ROOT.rglob("*"):
        if p.name in COMPOSE_FILENAMES and not _is_ignored(p):
            entries, msgs = parse_compose_host_ports(p)
            compose_ports.extend(entries)
            compose_msgs.extend(msgs)
    messages.extend(compose_msgs)
    if compose_ports:
        print(f"  Found {len(compose_ports)} compose host port mappings")

    # Validate
    print("\nValidating compliance...")
    findings, ok = validate(baseline, inventory_ids, opena_refs, port_refs, compose_ports)

    # Write reports
    result = ScanResult(
        timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        passed=ok,
        findings=findings,
        messages=messages,
    )

    json_out = SCANS_DIR / "ports_ids_scan.json"
    md_out = SCANS_DIR / "ports_ids_scan.md"

    json_out.write_text(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    md_out.write_text(render_md(findings))

    print(f"\n✓ JSON: {_rel(json_out)}")
    print(f"✓ MD: {_rel(md_out)}")

    # Summary
    print("\n" + "=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)

    if ok:
        print("✅ COMPLIANCE PASSED")
        print(f"   All {len(baseline)} agents validated")
        print("   No policy violations found")
        return 0
    else:
        print("❌ COMPLIANCE FAILED")
        print("   Violations detected (see reports)")
        print("\n⚠️  CI MUST BREAK")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
