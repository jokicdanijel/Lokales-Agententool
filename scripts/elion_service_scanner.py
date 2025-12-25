#!/usr/bin/env python3
"""
ELION Service Scanner (infra/app/monitoring)
- Recursively scans a service folder to infer:
  service_name, container_port, host_port (optional), exposure, route_prefix, plan_min, dependencies
- Enforces port policy: host ports must be in 12344-12399; 8080 forbidden everywhere.
- Produces deterministic terminal output with embedded artifacts for compose-merger.

Output Contract (terminal):
=== ELION_SCAN_BEGIN ===
...
--- COMPOSE_FRAGMENT_YAML_BEGIN ---
...
--- COMPOSE_FRAGMENT_YAML_END ---
--- DASHBOARD_MANIFEST_JSON_BEGIN ---
...
--- DASHBOARD_MANIFEST_JSON_END ---
--- ENTITLEMENT_HINT_JSON_BEGIN ---
...
--- ENTITLEMENT_HINT_JSON_END ---
=== ELION_SCAN_END ===
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

ALLOWED_HOST_PORT_MIN = 12344
ALLOWED_HOST_PORT_MAX = 12399
FORBIDDEN_PORTS = {8080}

TEXT_EXT = {
    ".py",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".env",
    ".ini",
    ".toml",
    ".sh",
    ".conf",
    ".html",
}

RE_DIRECT_AGENT_LINK = re.compile(r"http[s]?://[^ \n\"']+:(12\d{3})\b")
RE_ANY_PORT_LITERAL = re.compile(r"\b(\d{2,5})\b")
RE_LISTEN = re.compile(r"\blisten\s+(\d{2,5})\b", re.IGNORECASE)
RE_EXPOSE = re.compile(r"\bexpose\b|\bports\b", re.IGNORECASE)
RE_SECRET = re.compile(
    r"(API[_-]?KEY|SECRET|PASSWORD|PASSWD|TOKEN)\s*=\s*['\"]?[^'\"\s]{6,}['\"]?",
    re.IGNORECASE,
)
RE_PRIVATE_KEY = re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")

# Common service hints
SERVICE_HINTS = {
    "postgres": {
        "container_port": 5432,
        "default_host_port": 12380,
        "exposure": "edge_only",
        "dependencies": [],
        "route_prefix": "",
        "plan_min": "basic",
    },
    "redis": {
        "container_port": 6379,
        "default_host_port": 12381,
        "exposure": "edge_only",
        "dependencies": [],
        "route_prefix": "",
        "plan_min": "basic",
    },
    "vault": {
        "container_port": 8200,
        "default_host_port": 12382,
        "exposure": "edge_only",
        "dependencies": [],
        "route_prefix": "",
        "plan_min": "basic",
    },
    "nginx": {
        "container_port": 80,
        "default_host_port": 12383,
        "exposure": "edge_only",
        "dependencies": [],
        "route_prefix": "/",
        "plan_min": "basic",
    },
    "prometheus": {
        "container_port": 9090,
        "default_host_port": 12390,
        "exposure": "edge_only",
        "dependencies": [],
        "route_prefix": "/ops/prometheus",
        "plan_min": "pro",
    },
    "grafana": {
        "container_port": 3000,
        "default_host_port": 12391,
        "exposure": "edge_only",
        "dependencies": [],
        "route_prefix": "/ops/grafana",
        "plan_min": "pro",
    },
    "auth": {
        "container_port": 12370,
        "default_host_port": 12370,
        "exposure": "edge_only",
        "dependencies": ["postgres", "redis", "vault"],
        "route_prefix": "/auth",
        "plan_min": "basic",
    },
    "billing": {
        "container_port": 12371,
        "default_host_port": 12371,
        "exposure": "edge_only",
        "dependencies": ["postgres", "vault"],
        "route_prefix": "/billing",
        "plan_min": "basic",
    },
    "website": {
        "container_port": 12372,
        "default_host_port": 12372,
        "exposure": "edge_only",
        "dependencies": [],
        "route_prefix": "/",
        "plan_min": "basic",
    },
    "opena20": {
        "container_port": 12349,
        "default_host_port": 12349,
        "exposure": "edge_only",
        "dependencies": ["opena1", "opena2", "opena11"],
        "route_prefix": "/dashboard",
        "plan_min": "basic",
    },
    "opena21": {
        "container_port": 12367,
        "default_host_port": 12367,
        "exposure": "internal_only",
        "dependencies": ["opena1", "opena2", "redis"],
        "route_prefix": "/api/v1/workflows",
        "plan_min": "pro",
    },
}

PLAN_ORDER = {"basic": 0, "pro": 1, "premium": 2, "ultimum": 3}


@dataclasses.dataclass
class ScanResult:
    service_name: str
    plan: str
    scan_root: str
    timestamp_utc: str
    status: str
    findings: list[str]
    container_port: int | None
    host_port: int | None
    exposure: str
    route_prefix: str
    plan_min: str
    dependencies: list[str]
    compose_fragment_yaml: str
    dashboard_manifest_json: str
    entitlement_hint_json: str


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def read_text_safely(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def iter_text_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file():
            if p.suffix.lower() in TEXT_EXT or p.name.lower() == "dockerfile":
                out.append(p)
    return out


def infer_service_name(explicit: str | None, root: Path) -> str:
    if explicit:
        return explicit.strip()
    name = root.name.strip()
    name = name.replace(" ", "_").replace("-", "_")
    name = re.sub(r"^\d+[\._-]+", "", name)
    return name


def find_manifest_json(root: Path) -> dict[str, object] | None:
    for cand in ("service_manifest.json", "manifest.json", "service.json"):
        p = root / cand
        if p.exists() and p.is_file():
            t = read_text_safely(p)
            try:
                return json.loads(t)
            except Exception:
                return None
    return None


def infer_ports_from_files(root: Path) -> tuple[int | None, int | None]:
    container_candidates: list[int] = []
    host_candidates: list[int] = []

    for p in iter_text_files(root):
        t = read_text_safely(p)

        for m in re.finditer(r"\b(\d{2,5})\s*:\s*(\d{2,5})\b", t):
            hp = int(m.group(1))
            cp = int(m.group(2))
            host_candidates.append(hp)
            container_candidates.append(cp)

        for m in RE_LISTEN.finditer(t):
            container_candidates.append(int(m.group(1)))

        for m in re.finditer(r"\bPORT\s*=\s*(\d{2,5})\b", t):
            container_candidates.append(int(m.group(1)))

        for m in re.finditer(r"--port\s+(\d{2,5})\b", t):
            container_candidates.append(int(m.group(1)))

    def pick_most_frequent(vals: list[int]) -> int | None:
        if not vals:
            return None
        return max(set(vals), key=vals.count)

    return pick_most_frequent(container_candidates), pick_most_frequent(host_candidates)


def infer_exposure(service_name: str, host_port: int | None, default_exposure: str) -> str:
    if host_port is not None:
        return "edge_only"
    return default_exposure


def infer_dependencies(service_name: str, root: Path, default_deps: list[str]) -> list[str]:
    deps = set(default_deps)
    corpus = ""
    for p in iter_text_files(root):
        corpus += "\n" + read_text_safely(p)

    if re.search(r"\bpostgres\b|\bpg_isready\b|\bpsycopg\b", corpus, re.IGNORECASE):
        deps.add("postgres")
    if re.search(r"\bredis\b|\bredis-cli\b", corpus, re.IGNORECASE):
        deps.add("redis")
    if re.search(r"\bvault\b|\bVAULT_\w+\b", corpus, re.IGNORECASE):
        deps.add("vault")

    if service_name == "opena20":
        deps.update({"opena1", "opena2", "opena11"})

    return sorted(deps)


def infer_route_prefix(service_name: str, default_prefix: str) -> str:
    if default_prefix:
        return default_prefix
    if service_name in ("prometheus", "grafana"):
        return f"/ops/{service_name}"
    if service_name in ("auth", "billing"):
        return f"/{service_name}"
    if service_name == "opena20":
        return "/dashboard"
    return ""


def infer_plan_min(service_name: str, explicit: str | None, default_plan_min: str) -> str:
    if explicit:
        p = explicit.strip().lower()
        if p in PLAN_ORDER:
            return p
    if service_name in ("prometheus", "grafana"):
        return "pro"
    return default_plan_min


def compliance_scan(root: Path, container_port: int | None, host_port: int | None) -> tuple[str, list[str]]:
    findings: list[str] = []
    status = "PASS"

    for p in iter_text_files(root):
        t = read_text_safely(p)

        if "8080" in t:
            findings.append(f"FAIL: Forbidden port mention '8080' in {p.relative_to(root)}")
            status = "FAIL"

        for m in RE_DIRECT_AGENT_LINK.finditer(t):
            direct_port = int(m.group(1))
            if ALLOWED_HOST_PORT_MIN <= direct_port <= ALLOWED_HOST_PORT_MAX:
                findings.append(f"FAIL: Direct agent-port URL found ({direct_port}) in {p.relative_to(root)}")
                status = "FAIL"

        if RE_SECRET.search(t) or RE_PRIVATE_KEY.search(t):
            findings.append(f"FAIL: Possible cleartext secret/private key material in {p.relative_to(root)}")
            status = "FAIL"

    if host_port is not None:
        if host_port in FORBIDDEN_PORTS:
            findings.append(f"FAIL: Host port is forbidden: {host_port}")
            status = "FAIL"
        if not (ALLOWED_HOST_PORT_MIN <= host_port <= ALLOWED_HOST_PORT_MAX):
            findings.append(
                f"FAIL: Host port outside allowed range: {host_port} "
                f"(allowed {ALLOWED_HOST_PORT_MIN}-{ALLOWED_HOST_PORT_MAX})"
            )
            status = "FAIL"

    if container_port is None:
        findings.append("WARN: container_port not detected; compose fragment may be incomplete.")
        if status != "FAIL":
            status = "WARN"

    return status, findings


def make_entitlement_hint(service_name: str, plan_min: str) -> dict[str, object]:
    return {
        "service_name": service_name,
        "plan_min": plan_min,
        "exposure_contract": "host_ports_must_be_123xx_if_mapped",
        "ui_routing": {
            "no_direct_ports": True,
            "via": ["opena20", "opena1"],
            "audit": "opena2",
        },
        "auth_routes": ["/login", "/regist", "/forgot-password"],
        "legal_routes": ["/legal/privacy", "/legal/terms", "/legal/imprint"],
    }


def make_dashboard_manifest(service_name: str, route_prefix: str, plan_min: str) -> dict[str, object]:
    ui_route = route_prefix if route_prefix else f"/apps/{service_name}"
    return {
        "service_name": service_name,
        "plan_min": plan_min,
        "ui_route": ui_route,
        "routing": {"no_direct_ports": True, "via": ["opena20", "opena1"], "audit": "opena2"},
    }


def make_compose_fragment(
    service_name: str,
    image: str,
    container_port: int | None,
    host_port: int | None,
    exposure: str,
    dependencies: list[str],
    env_keys: list[str],
    volumes: list[str],
    health_path: str,
) -> str:
    cp = container_port
    hp = host_port

    env_lines: list[str] = []
    if cp is not None:
        env_lines.append(f'      PORT: "{cp}"')
    else:
        env_lines.append('      PORT: "${PORT:?set_port}"')

    for k in env_keys:
        if k == "PORT":
            continue
        env_lines.append(f'      {k}: "${{{k}:-}}"')

    depends_yaml = ""
    if dependencies:
        depends_yaml = "    depends_on:\n" + "\n".join([f"      - {d}" for d in dependencies]) + "\n"

    vols_yaml = ""
    if volumes:
        vols_yaml = "    volumes:\n" + "\n".join([f"      - {v}" for v in volumes]) + "\n"

    ports_yaml = ""
    expose_yaml = ""
    if exposure == "edge_only":
        if hp is not None and cp is not None:
            ports_yaml = f'    ports:\n      - "{hp}:{cp}"\n'
        elif hp is not None and cp is None:
            ports_yaml = f'    ports:\n      - "{hp}:${{PORT}}"\n'
        elif hp is None and cp is not None:
            expose_yaml = f'    expose:\n      - "{cp}"\n'
        else:
            expose_yaml = '    expose:\n      - "${PORT}"\n'
    elif exposure == "internal_only":
        if cp is not None:
            expose_yaml = f'    expose:\n      - "{cp}"\n'
        else:
            expose_yaml = '    expose:\n      - "${PORT}"\n'
    else:
        pass

    if cp is not None:
        health_cmd = f"wget -qO- http://127.0.0.1:{cp}{health_path} | grep -q healthy"
    else:
        health_cmd = f"wget -qO- http://127.0.0.1:${{PORT}}{health_path} | grep -q healthy"

    return (
        f"{service_name}:\n"
        f"    image: {image}\n"
        f"    container_name: {service_name}\n"
        f"    environment:\n"
        f"{os.linesep.join(env_lines)}\n"
        f"{ports_yaml}"
        f"{expose_yaml}"
        f"{depends_yaml}"
        f"{vols_yaml}"
        f"    networks:\n"
        f"      - internal_net\n"
        f"    healthcheck:\n"
        f'      test: ["CMD-SHELL", "{health_cmd}"]\n'
        f"      interval: 10s\n"
        f"      timeout: 3s\n"
        f"      retries: 30\n"
        f"    restart: unless-stopped\n"
    )


def infer_env_keys(root: Path) -> list[str]:
    keys = set()
    patterns = [
        re.compile(r"os\.environ\[\s*['\"]([A-Z0-9_]+)['\"]\s*\]"),
        re.compile(r"os\.getenv\(\s*['\"]([A-Z0-9_]+)['\"]"),
        re.compile(r"\$\{([A-Z0-9_]+)(?::[^}]*)?\}"),
        re.compile(r"ENV\s+([A-Z0-9_]+)\s*="),
    ]
    for p in iter_text_files(root):
        t = read_text_safely(p)
        for pat in patterns:
            for m in pat.finditer(t):
                keys.add(m.group(1))
    noise = {"PATH", "HOME", "SHELL", "PWD"}
    keys = {k for k in keys if k not in noise}
    return sorted(keys)


def infer_volumes(root: Path) -> list[str]:
    volumes = []
    for d in ("data", "storage", "logs", "archive", "uploads"):
        if (root / d).exists() and (root / d).is_dir():
            volumes.append(f"./{d}:/app/{d}")
    return volumes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--service-name", default=None)
    ap.add_argument("--service-dir", required=True)
    ap.add_argument("--plan", required=True, choices=["basic", "pro", "premium", "ultimum"])
    ap.add_argument("--plan-min", default=None, choices=["basic", "pro", "premium", "ultimum"])
    ap.add_argument("--route-prefix", default=None)
    ap.add_argument("--exposure", default=None, choices=["none", "internal_only", "edge_only"])
    ap.add_argument("--host-port", type=int, default=None)
    ap.add_argument("--container-port", type=int, default=None)
    ap.add_argument("--image", default=None)
    ap.add_argument("--health-path", default="/health")
    args = ap.parse_args()

    root = Path(args.service_dir).resolve()
    service_name = infer_service_name(args.service_name, root)

    manifest = find_manifest_json(root) or {}
    hint = SERVICE_HINTS.get(service_name, {})

    default_cp = int(hint["container_port"]) if "container_port" in hint else None
    default_hp = int(hint["default_host_port"]) if "default_host_port" in hint else None
    default_exposure = str(hint.get("exposure", "internal_only"))
    default_deps = list(hint.get("dependencies", []))
    default_route = str(hint.get("route_prefix", ""))
    default_plan_min = str(hint.get("plan_min", "basic"))

    inferred_cp, inferred_hp = infer_ports_from_files(root)

    # Precedence: args > manifest > inferred > default
    container_port = args.container_port
    if container_port is None and isinstance(manifest.get("container_port"), int):
        container_port = int(manifest.get("container_port"))
    if container_port is None:
        container_port = inferred_cp
    if container_port is None:
        container_port = default_cp

    # Precedence: args > manifest > inferred > default
    host_port = args.host_port
    if host_port is None and isinstance(manifest.get("host_port"), int):
        host_port = int(manifest.get("host_port"))
    if host_port is None:
        host_port = inferred_hp
    if host_port is None:
        host_port = default_hp

    route_prefix = args.route_prefix or str(manifest.get("route_prefix") or "") or default_route
    route_prefix = infer_route_prefix(service_name, route_prefix)

    exposure = args.exposure or str(manifest.get("exposure") or "") or default_exposure
    exposure = infer_exposure(service_name, host_port if exposure != "internal_only" else None, exposure)

    plan_min = infer_plan_min(
        service_name, args.plan_min or str(manifest.get("plan_min") or "") or None, default_plan_min
    )

    dependencies = infer_dependencies(service_name, root, default_deps)
    env_keys = infer_env_keys(root)
    volumes = infer_volumes(root)

    compliance_status, compliance_findings = compliance_scan(root, container_port, host_port)
    status = compliance_status

    if plan_min not in PLAN_ORDER:
        compliance_findings.append(f"FAIL: Invalid plan_min '{plan_min}'")
        status = "FAIL"

    if host_port is not None and exposure != "edge_only":
        compliance_findings.append("FAIL: host_port set but exposure != edge_only")
        status = "FAIL"

    if exposure == "edge_only" and host_port is None:
        compliance_findings.append("WARN: exposure=edge_only but host_port missing; will not map ports.")
        if status != "FAIL":
            status = "WARN"

    image = args.image or str(manifest.get("image") or "").strip()
    if not image:
        image = f"elion/{service_name}:latest"

    compose_fragment = make_compose_fragment(
        service_name=service_name,
        image=image,
        container_port=container_port,
        host_port=host_port if exposure == "edge_only" else None,
        exposure=exposure,
        dependencies=dependencies,
        env_keys=env_keys,
        volumes=volumes,
        health_path=args.health_path,
    )

    dashboard_manifest = make_dashboard_manifest(service_name, route_prefix, plan_min)
    entitlement_hint = make_entitlement_hint(service_name, plan_min)

    print("=== ELION_SCAN_BEGIN ===")
    print(f"service_name: {service_name}")
    print(f"plan: {args.plan}")
    print(f"scan_root: {root!s}")
    print(f"timestamp_utc: {utc_now()}")
    print(f"status: {status}")
    print("findings:")
    if compliance_findings:
        for f in compliance_findings:
            print(f"  - {f}")
    else:
        print("  - (none)")
    print("artifacts:")
    print("--- COMPOSE_FRAGMENT_YAML_BEGIN ---")
    print(compose_fragment.rstrip())
    print("--- COMPOSE_FRAGMENT_YAML_END ---")
    print("--- DASHBOARD_MANIFEST_JSON_BEGIN ---")
    print(json.dumps(dashboard_manifest, ensure_ascii=False, indent=2).rstrip())
    print("--- DASHBOARD_MANIFEST_JSON_END ---")
    print("--- ENTITLEMENT_HINT_JSON_BEGIN ---")
    print(json.dumps(entitlement_hint, ensure_ascii=False, indent=2).rstrip())
    print("--- ENTITLEMENT_HINT_JSON_END ---")
    print("=== ELION_SCAN_END ===")

    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
