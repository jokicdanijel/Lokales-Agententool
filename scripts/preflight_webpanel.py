#!/usr/bin/env python3

"""
preflight_webpanel.py
Production-grade preflight gates for a webpanel/dashboard (security + consistency + frontend + API + logs).

Writes:
- artifacts/security_gate_report.(json|md)
- artifacts/consistency_gate_report.(json|md)
- artifacts/frontend_gate_report.(json|md)
- artifacts/api_gate_report.(json|md)
- artifacts/logs_gate_report.(json|md)
- artifacts/start_proof_report.(json|md)

Exit codes:
  0 = all gates pass
  1 = blocking violations found
  2 = runtime/tooling error
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# tracing
from scripts.tracing import init_tracing  # init tracing for scripts

# -----------------------------
# Models
# -----------------------------


@dataclasses.dataclass
class Finding:
    level: str  # violation | warning | error | info
    gate: str
    rule: str
    message: str
    file: str | None = None
    evidence: str | None = None


@dataclasses.dataclass
class GateReport:
    gate: str
    ok: bool
    started_utc: str
    finished_utc: str
    duration_ms: int
    violations: list[Finding]
    warnings: list[Finding]
    errors: list[Finding]
    info: list[Finding]
    stats: dict[str, Any]


# -----------------------------
# Utils
# -----------------------------


def utc_now() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ms_since(t0: float) -> int:
    return int((time.time() - t0) * 1000)


def rel(root: Path, p: Path) -> str:
    try:
        return str(p.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(p)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def which(cmd: str) -> str | None:
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = Path(d) / cmd
        if p.exists() and os.access(p, os.X_OK):
            return str(p)
    return None


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 60) -> tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        timeout=timeout,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.returncode, p.stdout, p.stderr


def is_text_file(path: Path, max_bytes: int = 2_000_000) -> bool:
    try:
        if path.stat().st_size > max_bytes:
            return False
        with path.open("rb") as f:
            chunk = f.read(4096)
        return b"\x00" not in chunk
    except Exception:
        return False


def http_request(
    method: str, url: str, headers: dict[str, str] | None = None, data: bytes | None = None, timeout: int = 10
) -> tuple[int, dict[str, str], str]:
    req = urllib.request.Request(url=url, method=method.upper())
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    if data is not None:
        req.data = data
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            body = resp.read(20000)
            return status, hdrs, body.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read(20000).decode("utf-8", errors="replace")
        except Exception:
            body = ""
        hdrs = {k.lower(): v for k, v in getattr(e, "headers", {}).items()} if getattr(e, "headers", None) else {}
        return int(e.code), hdrs, body
    except Exception as e:
        return -1, {}, str(e)


def make_gate(name: str) -> GateReport:
    now = utc_now()
    return GateReport(
        gate=name,
        ok=True,
        started_utc=now,
        finished_utc=now,
        duration_ms=0,
        violations=[],
        warnings=[],
        errors=[],
        info=[],
        stats={},
    )


def finalize_gate(rep: GateReport, t0: float) -> GateReport:
    rep.finished_utc = utc_now()
    rep.duration_ms = ms_since(t0)
    rep.ok = len(rep.errors) == 0 and len(rep.violations) == 0
    return rep


def gate_to_json(rep: GateReport) -> dict:
    return {
        "gate": rep.gate,
        "ok": rep.ok,
        "started_utc": rep.started_utc,
        "finished_utc": rep.finished_utc,
        "duration_ms": rep.duration_ms,
        "errors": [dataclasses.asdict(x) for x in rep.errors],
        "violations": [dataclasses.asdict(x) for x in rep.violations],
        "warnings": [dataclasses.asdict(x) for x in rep.warnings],
        "info": [dataclasses.asdict(x) for x in rep.info],
        "stats": rep.stats,
    }


def render_md_gate(rep: GateReport) -> str:
    def fmt(items: list[Finding]) -> str:
        if not items:
            return "_none_"
        out = []
        for it in items:
            loc = f" ({it.file})" if it.file else ""
            ev = f"\n  - evidence: `{it.evidence}`" if it.evidence else ""
            out.append(f"- **{it.rule}**{loc}: {it.message}{ev}")
        return "\n".join(out)

    return "\n".join(
        [
            f"# Gate Report: {rep.gate}",
            "",
            f"- OK: `{rep.ok}`",
            f"- Started (UTC): `{rep.started_utc}`",
            f"- Finished (UTC): `{rep.finished_utc}`",
            f"- Duration: `{rep.duration_ms} ms`",
            "",
            "## Errors",
            "",
            fmt(rep.errors),
            "",
            "## Violations",
            "",
            fmt(rep.violations),
            "",
            "## Warnings",
            "",
            fmt(rep.warnings),
            "",
            "## Info",
            "",
            fmt(rep.info),
            "",
            "## Stats",
            "",
            "```json",
            json.dumps(rep.stats, indent=2, ensure_ascii=False),
            "```",
            "",
        ]
    )


def render_md_preflight(ok: bool, root: Path, cfg: dict, gates: dict[str, GateReport]) -> str:
    lines = []
    lines.append("# Webpanel Preflight Report")
    lines.append("")
    lines.append(f"- OK: `{ok}`")
    lines.append(f"- Timestamp (UTC): `{utc_now()}`")
    lines.append(f"- Root: `{root}`")
    lines.append("")
    lines.append("## Gates Summary")
    lines.append("")
    for gname in ["security_gate", "consistency_gate", "frontend_gate", "api_gate", "logs_gate"]:
        g = gates.get(gname)
        if not g:
            continue
        lines.append(
            f"- **{gname}**: ok=`{g.ok}` (violations={len(g.violations)} warnings={len(g.warnings)} errors={len(g.errors)})"
        )
    lines.append("")
    lines.append("## Config Snapshot")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(cfg, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


# -----------------------------
# Discovery helpers
# -----------------------------

DEFAULT_SECRET_PATTERNS = [
    r"bearer\s+[A-Za-z0-9\-\._=]+",
    r"authorization\s*:\s*bearer\s+[A-Za-z0-9\-\._=]+",
    r"BEGIN\s+PRIVATE\s+KEY",
    r"\bsk-[A-Za-z0-9]{20,}\b",
    r"\bghp_[A-Za-z0-9]{20,}\b",
    r"\bgithub_pat_[A-Za-z0-9_]{20,}\b",
    r"\bAIza[0-9A-Za-z\-_]{20,}\b",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
]

TEXT_EXT_ALLOW = {
    ".py",
    ".js",
    ".ts",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".env",
    ".ini",
    ".cfg",
    ".html",
    ".css",
    ".sh",
}
LOG_EXT = {".log", ".bak", ".tmp", ".old", ".save"}


def should_scan_file(path: Path) -> bool:
    # Exclude common virtualenvs, artifacts and generated directories
    blacklist_dirs = {".git", "venv", ".venv", "node_modules", "artifacts", "__pycache__", ".cache"}
    if any(p in blacklist_dirs for p in path.parts):
        return False
    ext = path.suffix.lower()
    if ext in TEXT_EXT_ALLOW or ext in LOG_EXT:
        return True
    if path.name.lower() in {".env", ".env.local", ".env.production", ".env.dev"}:
        return True
    return False


def iter_scan_files(root: Path) -> list[Path]:
    files = []
    for p in root.rglob("*"):
        if p.is_file() and should_scan_file(p):
            files.append(p)
    files.sort(key=lambda x: str(x).lower())
    return files


def line_for(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def detect_backend_port(root: Path) -> tuple[int | None, list[str]]:
    candidates: dict[int, list[str]] = {}
    py_files = sorted([p for p in root.rglob("*.py") if p.is_file()], key=lambda x: str(x).lower())

    rx_list = [
        re.compile(r"uvicorn\.run\([^)]*port\s*=\s*(\d{2,5})", re.IGNORECASE),
        re.compile(r"\bport\s*=\s*(\d{2,5})\b", re.IGNORECASE),
        re.compile(r"\bPORT\s*=\s*(\d{2,5})\b", re.IGNORECASE),
    ]

    for f in py_files[:2500]:
        if not is_text_file(f):
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for rx in rx_list:
            for m in rx.finditer(txt):
                port = int(m.group(1))
                ev = f"{rel(root, f)}:{line_for(txt, m.start())}:{m.group(0).strip()}"
                candidates.setdefault(port, []).append(ev)

    if not candidates:
        return None, []
    best = max(candidates.keys(), key=lambda p: (len(candidates[p]), -p))
    return best, candidates[best][:10]


def detect_static_dir(root: Path) -> str | None:
    for cand in ["html", "static", "public", "web", "frontend", "webpanel"]:
        p = root / cand
        if p.exists() and p.is_dir() and (p / "index.html").exists():
            return cand
    for p in root.rglob("index.html"):
        if p.is_file():
            try:
                return rel(root, p.parent)
            except Exception:
                continue
    return None


def detect_config_js(static_dir: Path) -> Path | None:
    for name in ["config.js", "config.local.js", "settings.js"]:
        p = static_dir / name
        if p.exists():
            return p
    for p in static_dir.glob("*.js"):
        if "config" in p.name.lower():
            return p
    return None


def parse_api_port_from_config(config_path: Path) -> tuple[int | None, list[str]]:
    if not config_path.exists() or not is_text_file(config_path):
        return None, []
    txt = config_path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\bAPI_PORT\b\s*[:=]\s*(\d{2,5})\b", txt)
    if m:
        return int(m.group(1)), [f"{config_path.name}:{line_for(txt, m.start())}:{m.group(0).strip()}"]
    m2 = re.search(r"localhost\s*:\s*(\d{2,5})", txt, re.IGNORECASE)
    if m2:
        return int(m2.group(1)), [f"{config_path.name}:{line_for(txt, m2.start())}:{m2.group(0).strip()}"]
    return None, []


def parse_index_refs(index_html: Path) -> dict[str, list[str]]:
    refs = {"css": [], "js": [], "other": []}
    if not index_html.exists() or not is_text_file(index_html):
        return refs
    txt = index_html.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r'href\s*=\s*["\']([^"\']+)["\']', txt, re.IGNORECASE):
        u = m.group(1).strip()
        (refs["css"] if u.endswith(".css") else refs["other"]).append(u)
    for m in re.finditer(r'src\s*=\s*["\']([^"\']+)["\']', txt, re.IGNORECASE):
        u = m.group(1).strip()
        (refs["js"] if u.endswith(".js") else refs["other"]).append(u)
    for k in refs:
        refs[k] = sorted(set(refs[k]))
    return refs


def dom_binding_check(js_text: str, html_text: str) -> list[str]:
    missing: list[str] = []
    ids = set(re.findall(r'getElementById\(\s*["\']([^"\']+)["\']\s*\)', js_text))
    selectors = {b for a, b in re.findall(r'querySelector(All)?\(\s*["\']([^"\']+)["\']\s*\)', js_text)}
    for i in sorted(ids):
        if re.search(rf'id\s*=\s*["\']{re.escape(i)}["\']', html_text, re.IGNORECASE) is None:
            missing.append(f"id:{i}")
    for s in sorted(selectors):
        if s.startswith("#"):
            i = s[1:]
            if re.search(rf'id\s*=\s*["\']{re.escape(i)}["\']', html_text, re.IGNORECASE) is None:
                missing.append(f"selector:{s}")
        elif s.startswith("."):
            c = s[1:]
            if re.search(rf'class\s*=\s*["\'][^"\']*\b{re.escape(c)}\b', html_text, re.IGNORECASE) is None:
                missing.append(f"selector:{s}")
    return missing


# -----------------------------
# Gates
# -----------------------------


def security_gate(root: Path, patterns: list[str], scan_git_history: bool) -> GateReport:
    t0 = time.time()
    rep = make_gate("security_gate")
    rep.stats["patterns"] = patterns
    rep.stats["scan_git_history"] = scan_git_history

    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    files = iter_scan_files(root)
    rep.stats["files_scanned"] = len(files)

    hits = []
    for f in files:
        if not is_text_file(f):
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            rep.errors.append(Finding("error", rep.gate, "file_read_error", str(e), file=rel(root, f)))
            continue
        for rx in compiled:
            m = rx.search(txt)
            if m:
                snippet = txt[m.start() : m.start() + 120].replace("\n", "\\n")
                hits.append((rel(root, f), line_for(txt, m.start()), rx.pattern, snippet))

    for file_rel, ln, pat, snip in hits[:200]:
        # Heuristics: treat obvious docs/templates/tests as warnings (placeholders),
        # but treat .env and env-like files as violations.
        fl = str(file_rel)
        is_env = fl.startswith(".env") or fl.endswith(".env")
        is_doc = fl.lower().endswith(".md") or fl.lower().startswith("readme") or "master_prompt" in fl.lower()
        is_html_template = fl.startswith("html/") or fl.lower().endswith(".html")
        is_test = fl.lower().startswith("test_") or "/tests/" in fl.lower() or "test_" in fl.lower()
        is_shell = fl.lower().endswith(".sh")

        evidence = f"{pat} :: {snip}"
        msg = f"Secret-like pattern matched at line {ln}. ROTATE/INVALIDATE tokens if this is real."

        if is_env:
            rep.violations.append(
                Finding("violation", rep.gate, "secret_pattern_found", msg, file=file_rel, evidence=evidence)
            )
        elif is_doc or is_html_template or is_test or is_shell:
            rep.warnings.append(
                Finding(
                    "warning",
                    rep.gate,
                    "secret_pattern_possible",
                    msg + " (file appears to be documentation/test/template/build script - verify manually).",
                    file=file_rel,
                    evidence=evidence,
                )
            )
        else:
            # default to violation when in source code
            rep.violations.append(
                Finding("violation", rep.gate, "secret_pattern_found", msg, file=file_rel, evidence=evidence)
            )
    rep.stats["hits_count"] = len(hits)

    # Git history scan (best effort)
    if scan_git_history:
        if (root / ".git").exists() and which("git"):
            history_hits = 0
            for p in patterns:
                try:
                    code, out, err = run_cmd(
                        ["git", "log", "-p", "-S", p, "--all", "--pretty=oneline", "-n", "1"], cwd=root, timeout=60
                    )
                    if code == 0 and out.strip():
                        history_hits += 1
                        rep.violations.append(
                            Finding(
                                "violation",
                                rep.gate,
                                "secret_in_git_history",
                                "Potential secret pattern found in git history. Rotation required; consider history rewrite.",
                                evidence=f"pattern={p}",
                            )
                        )
                except Exception as e:
                    rep.warnings.append(Finding("warning", rep.gate, "git_history_scan_failed", str(e)))
            rep.stats["history_hit_patterns"] = history_hits
        else:
            rep.warnings.append(
                Finding(
                    "warning",
                    rep.gate,
                    "git_history_scan_skipped",
                    "scan_git_history enabled but .git or git executable not found.",
                )
            )

    return finalize_gate(rep, t0)


def consistency_gate(
    root: Path, port: int | None, static_mount: str | None, static_dir: str | None
) -> tuple[GateReport, dict[str, Any]]:
    t0 = time.time()
    rep = make_gate("consistency_gate")

    discovered: dict[str, Any] = {"backend_port": port, "static_mount": static_mount, "static_dir": static_dir}

    if port is None:
        dport, ev = detect_backend_port(root)
        if dport is None:
            rep.violations.append(
                Finding(
                    "violation",
                    rep.gate,
                    "backend_port_unknown",
                    "Backend port could not be determined. Pass --port for determinism.",
                )
            )
        else:
            discovered["backend_port"] = dport
            rep.info.append(
                Finding(
                    "info",
                    rep.gate,
                    "backend_port_detected",
                    f"Detected backend port: {dport}",
                    evidence="; ".join(ev[:3]) if ev else None,
                )
            )

    if static_dir is None:
        sdir = detect_static_dir(root)
        if not sdir:
            rep.violations.append(
                Finding(
                    "violation",
                    rep.gate,
                    "static_dir_unknown",
                    "Static dir not detected. Pass --static-dir (e.g. html).",
                )
            )
        else:
            discovered["static_dir"] = sdir
            rep.info.append(Finding("info", rep.gate, "static_dir_detected", f"Detected static dir: {sdir}"))

    if static_mount is None:
        discovered["static_mount"] = "/html"
        rep.warnings.append(
            Finding(
                "warning",
                rep.gate,
                "static_mount_defaulted",
                "Static mount not provided; defaulting to /html. Pass --static-mount to avoid mismatch.",
            )
        )

    # Port mismatch check via config.js
    api_port = None
    api_ev = []
    if discovered.get("static_dir"):
        sd = root / str(discovered["static_dir"])
        cfg = detect_config_js(sd)
        if cfg:
            api_port, api_ev = parse_api_port_from_config(cfg)
            rep.stats["config_js"] = rel(root, cfg)
            if api_port is not None:
                rep.info.append(
                    Finding(
                        "info",
                        rep.gate,
                        "api_port_detected",
                        f"Detected API port in config: {api_port}",
                        evidence="; ".join(api_ev),
                    )
                )
        else:
            rep.warnings.append(
                Finding("warning", rep.gate, "config_js_missing", f"No config.js found in {rel(root, sd)}.")
            )

    bport = discovered.get("backend_port")
    if bport is not None and api_port is not None and int(bport) != int(api_port):
        rep.violations.append(
            Finding(
                "violation",
                rep.gate,
                "port_mismatch",
                f"Frontend API port ({api_port}) != backend port ({bport}). Fix config.js.",
                evidence="; ".join(api_ev),
            )
        )

    rep.stats["discovery"] = discovered
    return finalize_gate(rep, t0), discovered


def frontend_gate(
    root: Path,
    discovered: dict[str, Any],
    out_dir: Path,
    require_backend: bool,
    run_html_contract: bool,
    html_spec: str | None,
    fail_on_contract_warn: bool,
) -> GateReport:
    t0 = time.time()
    rep = make_gate("frontend_gate")

    bport = discovered.get("backend_port")
    static_mount = discovered.get("static_mount") or "/html"
    static_dir = discovered.get("static_dir")

    if not static_dir:
        rep.violations.append(
            Finding("violation", rep.gate, "static_dir_missing", "Static dir missing; cannot validate frontend.")
        )
        return finalize_gate(rep, t0)

    sd = root / str(static_dir)
    index_file = sd / "index.html"
    if not index_file.exists():
        rep.violations.append(
            Finding("violation", rep.gate, "index_missing", f"index.html not found in static dir: {static_dir}")
        )
        return finalize_gate(rep, t0)

    refs = parse_index_refs(index_file)
    rep.stats["index_refs"] = refs

    # assets: from index + common fallbacks if they exist
    assets = sorted(set(refs["css"] + refs["js"]))
    for fallback in ["style.css", "config.js", "app.js"]:
        if (sd / fallback).exists():
            assets.append(fallback)
    assets = sorted(set(assets))
    rep.stats["assets"] = assets

    def to_url_path(refpath: str) -> str:
        if refpath.startswith(("http://", "https://")):
            return refpath
        if refpath.startswith("/"):
            return refpath
        rp = refpath.lstrip("./")
        return f"{static_mount.rstrip('/')}/{rp}"

    # HTTP checks
    if bport is None:
        rep.violations.append(
            Finding("violation", rep.gate, "backend_port_unknown", "Backend port unknown; cannot do HTTP asset checks.")
        )
        return finalize_gate(rep, t0)

    base = f"http://localhost:{bport}"

    # index served check
    index_candidates = [f"{base}{static_mount.rstrip('/')}/index.html", f"{base}/index.html"]
    idx_ok = False
    idx_statuses = []
    for u in index_candidates:
        st, hdrs, body = http_request("GET", u, timeout=8)
        idx_statuses.append((u, st))
        if st == 200 and "<html" in body.lower():
            idx_ok = True
            break
    rep.stats["index_http"] = idx_statuses
    if require_backend and not idx_ok:
        rep.violations.append(
            Finding(
                "violation",
                rep.gate,
                "index_not_served",
                f"index.html not served on port {bport}. Check static mount.",
                evidence=str(idx_statuses),
            )
        )
    elif not idx_ok:
        rep.warnings.append(
            Finding(
                "warning",
                rep.gate,
                "index_not_confirmed",
                "index.html not confirmed over HTTP (backend may be down).",
                evidence=str(idx_statuses),
            )
        )

    # assets load
    asset_results = []
    for a in assets:
        u = to_url_path(a)
        if u.startswith("http"):
            rep.warnings.append(
                Finding(
                    "warning",
                    rep.gate,
                    "external_asset_ref",
                    "External asset reference found (policy risk).",
                    evidence=u,
                )
            )
            continue
        full = f"{base}{u}"
        st, hdrs, body = http_request("HEAD", full, timeout=8)
        if st in (-1, 405):
            st, hdrs, body = http_request("GET", full, timeout=8)
        asset_results.append((a, u, st))
        if require_backend and st != 200:
            rep.violations.append(
                Finding("violation", rep.gate, "asset_not_200", f"Asset not 200: {u} (status={st})", file=a)
            )
        elif st != 200:
            rep.warnings.append(
                Finding("warning", rep.gate, "asset_not_200", f"Asset not confirmed 200: {u} (status={st})", file=a)
            )
    rep.stats["asset_http"] = asset_results

    # JS syntax checks (if node)
    node = which("node")
    js_files = [p for p in [sd / "config.js", sd / "app.js"] if p.exists()]
    rep.stats["js_files"] = [rel(root, p) for p in js_files]
    if js_files and node:
        for jf in js_files:
            code, out, err = run_cmd([node, "--check", str(jf)], cwd=root, timeout=20)
            if code != 0:
                rep.violations.append(
                    Finding(
                        "violation",
                        rep.gate,
                        "js_syntax_error",
                        "Node syntax check failed.",
                        file=rel(root, jf),
                        evidence=(err or out)[-600:],
                    )
                )
    elif js_files and not node:
        rep.warnings.append(Finding("warning", rep.gate, "node_missing", "Node not found; JS syntax checks skipped."))

    # DOM binding plausibility (warnings)
    app_js = sd / "app.js"
    if app_js.exists() and is_text_file(app_js) and is_text_file(index_file):
        js = app_js.read_text(encoding="utf-8", errors="replace")
        html = index_file.read_text(encoding="utf-8", errors="replace")
        missing = dom_binding_check(js, html)
        rep.stats["dom_binding_missing_count"] = len(missing)
        for sel in missing[:50]:
            rep.warnings.append(
                Finding(
                    "warning",
                    rep.gate,
                    "dom_selector_missing",
                    "Selector/ID referenced in JS not found in index.html (may break bindings).",
                    evidence=sel,
                )
            )

    # HTML contract validation (optional but blocking)
    if run_html_contract:
        if not html_spec:
            rep.violations.append(
                Finding(
                    "violation", rep.gate, "html_spec_missing", "--run-html-contract set but --html-spec not provided."
                )
            )
        else:
            validator = root / "scripts" / "validate_html_contract.py"
            if not validator.exists():
                rep.violations.append(
                    Finding(
                        "violation", rep.gate, "html_validator_missing", "scripts/validate_html_contract.py not found."
                    )
                )
            else:
                out_json = out_dir / "scans" / "html_contract_scan.json"
                out_md = out_dir / "scans" / "html_contract_scan.md"
                cmd = [
                    sys.executable,
                    str(validator),
                    "--spec",
                    str(html_spec),
                    "--root",
                    str(root),
                    "--out-json",
                    str(out_json),
                    "--out-md",
                    str(out_md),
                ]
                if fail_on_contract_warn:
                    cmd.append("--fail-on-warn")
                code, out, err = run_cmd(cmd, cwd=root, timeout=120)
                rep.stats["html_contract_cmd"] = " ".join(cmd)
                rep.stats["html_contract_exit_code"] = code
                if code != 0:
                    rep.violations.append(
                        Finding(
                            "violation",
                            rep.gate,
                            "html_contract_failed",
                            "HTML contract validation failed. See artifacts/scans/html_contract_scan.md",
                            evidence=(err or out)[-600:],
                        )
                    )

    return finalize_gate(rep, t0)


def discover_endpoints(root: Path) -> set[str]:
    endpoints: set[str] = set()
    py_files = sorted([p for p in root.rglob("*.py") if p.is_file()], key=lambda x: str(x).lower())[:2000]
    fastapi = re.compile(r'@(?:app|router)\.(get|post|put|patch|delete)\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
    flask = re.compile(r'@(?:app|bp)\.route\(\s*["\']([^"\']+)["\']\s*,\s*methods\s*=\s*\[([^\]]+)\]', re.IGNORECASE)
    for f in py_files:
        if not is_text_file(f):
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in fastapi.finditer(txt):
            endpoints.add(m.group(2))
        for m in flask.finditer(txt):
            endpoints.add(m.group(1))
    return endpoints


def api_gate(
    root: Path,
    discovered: dict[str, Any],
    require_backend: bool,
    api_tests_json: str | None,
    auth_token: str | None,
) -> GateReport:
    t0 = time.time()
    rep = make_gate("api_gate")

    bport = discovered.get("backend_port")
    if bport is None:
        rep.violations.append(
            Finding("violation", rep.gate, "backend_port_unknown", "Backend port unknown; API smoke tests cannot run.")
        )
        return finalize_gate(rep, t0)

    base = f"http://localhost:{bport}"
    headers = {"content-type": "application/json"}
    if auth_token:
        headers["authorization"] = f"Bearer {auth_token}"
        rep.info.append(
            Finding("info", rep.gate, "auth_token_present", "Auth token provided via env/arg (not printed).")
        )

    # Load tests or use defaults
    if api_tests_json:
        p = Path(api_tests_json)
        if not p.exists():
            rep.violations.append(
                Finding("violation", rep.gate, "api_tests_json_missing", f"api tests json not found: {api_tests_json}")
            )
            return finalize_gate(rep, t0)
        tests = json.loads(p.read_text(encoding="utf-8"))
    else:
        endpoints = discover_endpoints(root)
        rep.stats["endpoints_discovered_count"] = len(endpoints)
        rep.stats["endpoints_sample"] = sorted(endpoints)[:25]
        tests = {"tests": []}
        # minimal safe defaults (won't brick if endpoint name differs -> warns on 404, but blocks if nothing returns 2xx)
        for hp in ["/health", "/status", "/api/status/all"]:
            tests["tests"].append(
                {"name": f"GET {hp}", "method": "GET", "path": hp, "allowed_statuses": [200, 204, 401, 403, 404]}
            )
        for path, payload in [
            ("/command", {"action": "post_now"}),
            ("/specialized", {"task": "generate_text", "prompt": "ping"}),
        ]:
            tests["tests"].append(
                {
                    "name": f"POST {path}",
                    "method": "POST",
                    "path": path,
                    "json": payload,
                    "allowed_statuses": [200, 201, 202, 400, 401, 403, 404],
                }
            )

    results = []
    any_success = False

    for t in tests.get("tests", []):
        name = t.get("name", "unnamed")
        method = t.get("method", "GET").upper()
        path = t.get("path", "/")
        allowed = t.get("allowed_statuses", [200])

        data = None
        if "json" in t:
            data = json.dumps(t["json"]).encode("utf-8")

        url = base + path
        st, hdrs, body = http_request(method, url, headers=headers, data=data, timeout=10)
        results.append(
            {
                "name": name,
                "method": method,
                "path": path,
                "url": url,
                "status": st,
                "allowed_statuses": allowed,
                "body_snippet": (body or "")[:400],
            }
        )

        if st in (200, 201, 202, 204):
            any_success = True

        if st == -1:
            msg = f"Connection failed for {method} {path}: {body}"
            if require_backend:
                rep.violations.append(Finding("violation", rep.gate, "backend_unreachable", msg))
            else:
                rep.warnings.append(Finding("warning", rep.gate, "backend_unreachable", msg))
            continue

        if st not in allowed:
            rep.violations.append(
                Finding(
                    "violation",
                    rep.gate,
                    "unexpected_status",
                    f"{name} returned status={st}, expected one of {allowed}.",
                    evidence=(body or "")[:250],
                )
            )

        if st == 404:
            rep.warnings.append(
                Finding(
                    "warning",
                    rep.gate,
                    "endpoint_not_found",
                    f"{name} returned 404 (endpoint missing or path differs).",
                    evidence=path,
                )
            )

    rep.stats["tests_run"] = len(results)
    rep.stats["results"] = results

    # This is the "tell it like it is" blocker:
    if require_backend and not any_success:
        rep.violations.append(
            Finding(
                "violation",
                rep.gate,
                "no_successful_api_calls",
                "No API call returned 2xx. Either backend down, wrong port, or endpoints differ.",
            )
        )

    return finalize_gate(rep, t0)


def tail_lines(path: Path, n: int) -> list[str]:
    try:
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            block = 4096
            data = b""
            while size > 0 and data.count(b"\n") < n + 1:
                read_size = block if size >= block else size
                size -= read_size
                f.seek(size)
                data = f.read(read_size) + data
            return data.decode("utf-8", errors="replace").splitlines()[-n:]
    except Exception:
        try:
            return path.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]
        except Exception:
            return []


def logs_gate(root: Path, log_paths: list[str], lookback_lines: int = 500) -> GateReport:
    t0 = time.time()
    rep = make_gate("logs_gate")

    candidates: list[Path] = []
    for lp in log_paths:
        p = (root / lp) if not os.path.isabs(lp) else Path(lp)
        if p.exists() and p.is_file():
            candidates.append(p)

    if not candidates:
        logs_dir = root / "logs"
        if logs_dir.exists():
            candidates.extend(list(logs_dir.rglob("*.log")))

    candidates = sorted(set(candidates), key=lambda x: str(x).lower())
    rep.stats["log_files"] = [rel(root, p) if p.is_relative_to(root) else str(p) for p in candidates]

    if not candidates:
        rep.warnings.append(
            Finding(
                "warning",
                rep.gate,
                "no_logs_found",
                "No logs provided/found. Logs gate cannot validate runtime errors.",
            )
        )
        return finalize_gate(rep, t0)

    patterns = [
        (re.compile(r"traceback", re.IGNORECASE), "traceback"),
        (re.compile(r"exception", re.IGNORECASE), "exception"),
        (re.compile(r"\b500\b", re.IGNORECASE), "http_500"),
        (re.compile(r"\b404\b", re.IGNORECASE), "http_404"),
    ]
    counts = {k: 0 for _, k in patterns}

    top_404: dict[str, int] = {}

    for p in candidates[:10]:
        if not is_text_file(p, max_bytes=5_000_000):
            rep.warnings.append(
                Finding("warning", rep.gate, "log_skipped", "Log skipped (binary/too large).", file=str(p))
            )
            continue
        lines = tail_lines(p, lookback_lines)
        joined = "\n".join(lines)
        for rx, key in patterns:
            counts[key] += len(rx.findall(joined))

        for ln in lines:
            if "404" in ln:
                m = re.search(r"(GET|POST)\s+(\S+)", ln)
                if m:
                    url = m.group(2)
                    top_404[url] = top_404.get(url, 0) + 1

    rep.stats["counts"] = counts
    rep.stats["top_404"] = sorted(top_404.items(), key=lambda kv: (-kv[1], kv[0]))[:20]

    if counts["traceback"] > 0 or counts["exception"] > 0:
        rep.violations.append(
            Finding(
                "violation",
                rep.gate,
                "runtime_exceptions_detected",
                "Traceback/Exception markers found in recent logs. Fix before deploy.",
                evidence=json.dumps({"traceback": counts["traceback"], "exception": counts["exception"]}),
            )
        )

    if counts["http_404"] > 20:
        rep.warnings.append(
            Finding(
                "warning",
                rep.gate,
                "high_404_rate",
                "High number of 404s in recent logs; likely broken paths/assets.",
                evidence=str(counts["http_404"]),
            )
        )

    return finalize_gate(rep, t0)


# -----------------------------
# Runner
# -----------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Project root")
    ap.add_argument("--out-dir", default="artifacts", help="Artifacts dir")

    # Security
    ap.add_argument("--secret-pattern", action="append", default=[], help="Extra secret regex patterns (repeatable)")
    ap.add_argument("--scan-git-history", action="store_true", help="Scan git history (best effort)")

    # Consistency
    ap.add_argument("--port", type=int, default=None, help="Backend port (recommended)")
    ap.add_argument("--static-mount", default=None, help="Static URL mount, e.g. /html")
    ap.add_argument("--static-dir", default=None, help="Static dir, e.g. html")

    # Frontend
    ap.add_argument("--require-backend", action="store_true", help="Backend must be reachable; otherwise fail")
    ap.add_argument("--run-html-contract", action="store_true", help="Run HTML contract validator (blocking)")
    ap.add_argument("--html-spec", default=None, help="Path to scripts/html_contract_spec.json")
    ap.add_argument("--fail-on-contract-warn", action="store_true")

    # API
    ap.add_argument("--api-tests-json", default=None, help="Custom API tests plan (json)")
    ap.add_argument("--auth-token", default=None, help="Bearer token for API checks (prefer env PREFLIGHT_AUTH_TOKEN)")

    # Logs
    ap.add_argument("--log", action="append", default=[], help="Log file path to scan (repeatable)")
    ap.add_argument("--log-lookback-lines", type=int, default=500)

    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()

    cfg = {
        "root": str(root),
        "out_dir": str(out_dir),
        "port": args.port,
        "static_mount": args.static_mount,
        "static_dir": args.static_dir,
        "require_backend": args.require_backend,
        "run_html_contract": args.run_html_contract,
        "html_spec": args.html_spec,
        "api_tests_json": args.api_tests_json,
        "scan_git_history": args.scan_git_history,
        "log_paths": args.log,
        "log_lookback_lines": args.log_lookback_lines,
        "auth_token_present": bool(args.auth_token or os.environ.get("PREFLIGHT_AUTH_TOKEN")),
    }

    gates: dict[str, GateReport] = {}

    # SECURITY (block immediately)
    patterns = DEFAULT_SECRET_PATTERNS + args.secret_pattern
    gates["security_gate"] = security_gate(root, patterns, args.scan_git_history)
    write_json(out_dir / "security_gate_report.json", gate_to_json(gates["security_gate"]))
    write_text(out_dir / "security_gate_report.md", render_md_gate(gates["security_gate"]))
    if not gates["security_gate"].ok:
        return finalize(out_dir, root, cfg, gates)

    # CONSISTENCY (block)
    gates["consistency_gate"], discovered = consistency_gate(root, args.port, args.static_mount, args.static_dir)
    write_json(out_dir / "consistency_gate_report.json", gate_to_json(gates["consistency_gate"]))
    write_text(out_dir / "consistency_gate_report.md", render_md_gate(gates["consistency_gate"]))
    if not gates["consistency_gate"].ok:
        return finalize(out_dir, root, cfg, gates)

    # FRONTEND (block)
    gates["frontend_gate"] = frontend_gate(
        root,
        discovered,
        out_dir,
        args.require_backend,
        args.run_html_contract,
        args.html_spec,
        args.fail_on_contract_warn,
    )
    write_json(out_dir / "frontend_gate_report.json", gate_to_json(gates["frontend_gate"]))
    write_text(out_dir / "frontend_gate_report.md", render_md_gate(gates["frontend_gate"]))
    if not gates["frontend_gate"].ok:
        return finalize(out_dir, root, cfg, gates)

    # API (block)
    auth_token = args.auth_token or os.environ.get("PREFLIGHT_AUTH_TOKEN")
    gates["api_gate"] = api_gate(root, discovered, args.require_backend, args.api_tests_json, auth_token)
    write_json(out_dir / "api_gate_report.json", gate_to_json(gates["api_gate"]))
    write_text(out_dir / "api_gate_report.md", render_md_gate(gates["api_gate"]))
    if not gates["api_gate"].ok:
        return finalize(out_dir, root, cfg, gates)

    # LOGS (can block if exceptions)
    gates["logs_gate"] = logs_gate(root, args.log, args.log_lookback_lines)
    write_json(out_dir / "logs_gate_report.json", gate_to_json(gates["logs_gate"]))
    write_text(out_dir / "logs_gate_report.md", render_md_gate(gates["logs_gate"]))

    return finalize(out_dir, root, cfg, gates)


def finalize(out_dir: Path, root: Path, cfg: dict, gates: dict[str, GateReport]) -> int:
    ok = all(g.ok for g in gates.values())
    summary = {
        "gates_run": list(gates.keys()),
        "blocking_failed": [k for k, v in gates.items() if not v.ok],
        "violations_total": sum(len(v.violations) for v in gates.values()),
        "warnings_total": sum(len(v.warnings) for v in gates.values()),
        "errors_total": sum(len(v.errors) for v in gates.values()),
    }

    write_json(
        out_dir / "start_proof_report.json",
        {
            "ok": ok,
            "timestamp_utc": utc_now(),
            "root": str(root),
            "config": cfg,
            "summary": summary,
            "gates": {k: gate_to_json(v) for k, v in gates.items()},
        },
    )
    write_text(out_dir / "start_proof_report.md", render_md_preflight(ok, root, cfg, gates))

    print(f"[PREFLIGHT] ok={ok} failed={summary['blocking_failed']}")
    for gname in summary["blocking_failed"]:
        g = gates[gname]
        for it in (g.errors + g.violations)[:10]:
            loc = f" ({it.file})" if it.file else ""
            print(f" - {gname}::{it.rule}{loc}: {it.message}")
    return 0 if ok else 1


if __name__ == "__main__":
    # initialize tracing (no-op if opentelemetry packages are missing)
    init_tracing("preflight_webpanel")
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        raise SystemExit(2) from e
