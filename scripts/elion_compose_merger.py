#!/usr/bin/env python3
"""
ELION Compose Merger
- Consumes ELION_SCAN outputs (from elion_agent_scanner.py and elion_service_scanner.py)
- Builds 4 plan-specific compose files and 4 route manifests:
  compose.basic.yml, compose.pro.yml, compose.premium.yml, compose.ultimum.yml
  routes.basic.json, routes.pro.json, routes.premium.json, routes.ultimum.json
- Enforces hard port policy on host mappings: host ports must be 12344-12399; 8080 forbidden.
- Enforces UI routing policy: no direct agent-port URLs in manifests.

Input formats:
- One or many scan output text files, each containing:
  --- COMPOSE_FRAGMENT_YAML_BEGIN --- ... --- COMPOSE_FRAGMENT_YAML_END ---
  --- DASHBOARD_MANIFEST_JSON_BEGIN --- ... --- DASHBOARD_MANIFEST_JSON_END ---
  --- ENTITLEMENT_HINT_JSON_BEGIN --- ... --- ENTITLEMENT_HINT_JSON_END ---
- Or read from STDIN with same format.

This tool is deterministic and fail-fast.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ALLOWED_HOST_PORT_MIN = 12344
ALLOWED_HOST_PORT_MAX = 12399
FORBIDDEN_PORTS = {8080}
PLAN_ORDER = {"basic": 0, "pro": 1, "premium": 2, "ultimum": 3}
PLANS = ["basic", "pro", "premium", "ultimum"]

RE_BLOCK = re.compile(
    r"--- (?P<name>[A-Z0-9_]+)_(?P<kind>YAML|JSON)_BEGIN ---\n(?P<body>.*?)\n--- (?P=name)_(?P=kind)_END ---",
    re.DOTALL,
)
RE_HOSTPORT_MAPPING = re.compile(r'^\s*-\s*"(?P<hp>\d{2,5}):(?P<cp>\d{2,5})"\s*$', re.MULTILINE)
RE_FORBIDDEN_8080 = re.compile(r"\b8080\b")
RE_DIRECT_AGENT_LINK = re.compile(r"http[s]?://[^ \n\"']+:(12\d{3})\b")


@dataclass
class Unit:
    name: str
    plan_min: str
    compose_fragment: str
    dashboard_manifest: dict
    entitlement_hint: dict
    source: str


def parse_blocks(text: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for m in RE_BLOCK.finditer(text):
        key = f"{m.group('name')}_{m.group('kind')}"
        blocks[key] = m.group("body").strip()
    return blocks


def normalize_service_key(manifest: dict, fallback_source: str) -> str:
    for k in ("agent_id", "service_name"):
        v = manifest.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return f"unknown_{Path(fallback_source).stem}"


def extract_plan_min(entitlement: dict, dashboard: dict) -> str:
    for src in (entitlement, dashboard):
        v = src.get("plan_min")
        if isinstance(v, str) and v.strip().lower() in PLAN_ORDER:
            return v.strip().lower()
    return "basic"


def enforce_policy_on_compose_fragment(fragment: str, source: str) -> None:
    if RE_FORBIDDEN_8080.search(fragment):
        raise ValueError(f"[FAIL] Forbidden port '8080' found in compose fragment ({source})")

    for m in RE_HOSTPORT_MAPPING.finditer(fragment):
        hp = int(m.group("hp"))
        if hp in FORBIDDEN_PORTS:
            raise ValueError(f"[FAIL] Forbidden host port {hp} found in compose fragment ({source})")
        if not (ALLOWED_HOST_PORT_MIN <= hp <= ALLOWED_HOST_PORT_MAX):
            raise ValueError(
                f"[FAIL] Host port {hp} outside allowed range {ALLOWED_HOST_PORT_MIN}-{ALLOWED_HOST_PORT_MAX} ({source})"
            )


def enforce_policy_on_manifest(obj: dict, source: str) -> None:
    blob = json.dumps(obj, ensure_ascii=False)
    if RE_FORBIDDEN_8080.search(blob):
        raise ValueError(f"[FAIL] Forbidden port '8080' found in manifest ({source})")
    if RE_DIRECT_AGENT_LINK.search(blob):
        raise ValueError(f"[FAIL] Direct agent-port URL found in manifest ({source})")


def load_units_from_text(text: str, source: str) -> list[Unit]:
    blocks = parse_blocks(text)

    if "COMPOSE_FRAGMENT_YAML" not in blocks:
        raise ValueError(f"[FAIL] Missing COMPOSE_FRAGMENT_YAML in {source}")
    if "DASHBOARD_MANIFEST_JSON" not in blocks:
        raise ValueError(f"[FAIL] Missing DASHBOARD_MANIFEST_JSON in {source}")
    if "ENTITLEMENT_HINT_JSON" not in blocks:
        raise ValueError(f"[FAIL] Missing ENTITLEMENT_HINT_JSON in {source}")

    compose_fragment = blocks["COMPOSE_FRAGMENT_YAML"]
    dashboard_manifest = json.loads(blocks["DASHBOARD_MANIFEST_JSON"])
    entitlement_hint = json.loads(blocks["ENTITLEMENT_HINT_JSON"])

    enforce_policy_on_compose_fragment(compose_fragment, source)
    enforce_policy_on_manifest(dashboard_manifest, source)
    enforce_policy_on_manifest(entitlement_hint, source)

    key = normalize_service_key(dashboard_manifest, source)
    plan_min = extract_plan_min(entitlement_hint, dashboard_manifest)

    return [
        Unit(
            name=key,
            plan_min=plan_min,
            compose_fragment=compose_fragment.rstrip() + "\n",
            dashboard_manifest=dashboard_manifest,
            entitlement_hint=entitlement_hint,
            source=source,
        )
    ]


def plan_includes(plan: str, plan_min: str) -> bool:
    return PLAN_ORDER[plan] >= PLAN_ORDER[plan_min]


def build_compose(plan: str, units: list[Unit]) -> str:
    services = []
    for u in units:
        if plan_includes(plan, u.plan_min):
            services.append(u.compose_fragment.rstrip())

    services_yaml = "\n\n".join(services).rstrip() + "\n" if services else ""

    return (
        'version: "3.9"\n\n'
        "networks:\n"
        "  edge_net:\n"
        "  internal_net:\n"
        "    internal: true\n\n"
        "volumes:\n"
        "  postgres_data:\n"
        "  redis_data:\n"
        "  vault_data:\n\n"
        "services:\n"
        f"{indent_services(services_yaml)}"
    )


def indent_services(s: str) -> str:
    if not s.strip():
        return ""
    lines = s.splitlines()
    return "\n".join(("  " + ln) if ln.strip() else "" for ln in lines) + "\n"


def build_routes_manifest(plan: str, units: list[Unit]) -> dict:
    routes = []
    for u in units:
        if plan_includes(plan, u.plan_min):
            routes.append(u.dashboard_manifest)
    return {
        "plan": plan,
        "generated_by": "elion_compose_merger",
        "routes": routes,
        "policy": {
            "no_direct_ports": True,
            "host_ports_range": [ALLOWED_HOST_PORT_MIN, ALLOWED_HOST_PORT_MAX],
            "forbidden_ports": sorted(FORBIDDEN_PORTS),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="*", default=[])
    ap.add_argument("--input-dir", default=None)
    ap.add_argument("--out-dir", default="artifacts/merged")
    ap.add_argument("--stdin", action="store_true")
    args = ap.parse_args()

    texts: list[tuple[str, str]] = []

    if args.stdin:
        data = sys.stdin.read()
        if data.strip():
            texts.append(("STDIN", data))

    for p in args.inputs:
        fp = Path(p)
        if not fp.exists() or not fp.is_file():
            raise SystemExit(f"[FAIL] Input file not found: {p}")
        texts.append((str(fp), fp.read_text(encoding="utf-8", errors="ignore")))

    if args.input_dir:
        d = Path(args.input_dir)
        if not d.exists() or not d.is_dir():
            raise SystemExit(f"[FAIL] input-dir not found: {args.input_dir}")
        for fp in sorted(d.glob("**/*")):
            if fp.is_file() and fp.suffix.lower() in {".txt", ".out", ".log"}:
                content = fp.read_text(encoding="utf-8", errors="ignore")
                if "--- COMPOSE_FRAGMENT_YAML_BEGIN ---" in content:
                    texts.append((str(fp), content))

    if not texts:
        raise SystemExit("[FAIL] No scan outputs provided.")

    units_by_name: dict[str, Unit] = {}
    for source, text in texts:
        for u in load_units_from_text(text, source):
            if u.name in units_by_name:
                prev = units_by_name[u.name]
                if prev.compose_fragment != u.compose_fragment or prev.plan_min != u.plan_min:
                    raise SystemExit(
                        f"[FAIL] Duplicate unit name '{u.name}' with differing content.\n"
                        f"  prev: {prev.source}\n  new:  {u.source}"
                    )
            units_by_name[u.name] = u

    units = [units_by_name[k] for k in sorted(units_by_name.keys())]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for plan in PLANS:
        compose_yml = build_compose(plan, units)
        if RE_FORBIDDEN_8080.search(compose_yml):
            raise SystemExit(f"[FAIL] Assembled compose contains forbidden 8080 for plan {plan}")

        for m in RE_HOSTPORT_MAPPING.finditer(compose_yml):
            hp = int(m.group("hp"))
            if hp in FORBIDDEN_PORTS or not (ALLOWED_HOST_PORT_MIN <= hp <= ALLOWED_HOST_PORT_MAX):
                raise SystemExit(f"[FAIL] Assembled compose has invalid host port {hp} for plan {plan}")

        (out_dir / f"compose.{plan}.yml").write_text(compose_yml, encoding="utf-8")
        routes = build_routes_manifest(plan, units)
        (out_dir / f"routes.{plan}.json").write_text(
            json.dumps(routes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print("[OK] Merge completed.")
    print(f"[OK] Units: {len(units)}")
    print(f"[OK] Output dir: {out_dir!s}")
    for plan in PLANS:
        print(f"[OK] Wrote: {out_dir / f'compose.{plan}.yml'}")
        print(f"[OK] Wrote: {out_dir / f'routes.{plan}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
