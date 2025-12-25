#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

# ---------- Defaults ----------
MAX_PREVIEW_LINES_DEFAULT = 120

DEFAULT_INCLUDE = [
    r"^\.github/workflows/.*\.ya?ml$",
    r"^docker-compose.*\.ya?ml$",
    r"^infrastructure/nginx/.*\.conf$",
    r"^apps/.*\.html$",
    r"^pyproject\.toml$",
    r"^\.pre-commit-config\.yaml$",
    r"^\.gitignore$",
]

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    ".venv-precommit",
    "node_modules",
    "dist",
    "build",
    ".ruff_cache",
    ".mypy_cache",
    "archivp_store",
    # vendor-ish (in your local output this is big)
    "open-webui-0.6.40",
}

# ---------- Redaction ----------
SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password|passwd)\b\s*[:=]\s*['\"]?([^\s'\"\\]+)"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(bearer)\s+[a-z0-9\-\._=]+"),
]

# ---------- Policy patterns ----------
FORBIDDEN_8080_RE = re.compile(r"(^|[^0-9])8080(:|[^0-9])")
HOST_PORT_RE = re.compile(r'^\s*-\s*"?(\d{2,5}):(\d{2,5})')  # compose published ports
AGENT_PORT_RE = re.compile(r":(123[4-9]\d|1239\d)\b")
SCRIPT_RE = re.compile(r"<\s*script\b", re.IGNORECASE)
INLINE_STYLE_RE = re.compile(r"\bstyle\s*=", re.IGNORECASE)
STYLESHEET_LINK_RE = re.compile(r"<\s*link\b[^>]*\brel\s*=\s*['\"]stylesheet['\"]", re.IGNORECASE)


@dataclass
class FileFinding:
    path: str
    bytes: int
    policy_hits: list[str]
    preview: list[str]


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def git_root() -> str:
    try:
        return run(["git", "rev-parse", "--show-toplevel"])
    except Exception:
        return os.getcwd()


def list_staged_files() -> list[str]:
    out = run(["git", "diff", "--cached", "--name-only"]) or ""
    return [x for x in out.splitlines() if x.strip()]


def list_tracked_files() -> list[str]:
    out = run(["git", "ls-files"]) or ""
    return [x for x in out.splitlines() if x.strip()]


def read_file_from_index(path: str) -> str:
    # staged content
    return subprocess.check_output(["git", "show", f":{path}"], text=True, errors="replace")


def read_file_from_fs(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def is_excluded(path: str, exclude_dirs: set[str]) -> bool:
    parts = Path(path).parts
    return any(p in exclude_dirs for p in parts)


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(re.search(p, path) for p in patterns)


def redact(text: str) -> str:
    redacted = text
    for pat in SECRET_PATTERNS:
        if "BEGIN" in pat.pattern:
            redacted = pat.sub("[REDACTED_PRIVATE_KEY_BLOCK]", redacted)
        else:
            redacted = pat.sub(lambda m: m.group(0).replace(m.group(m.lastindex), "[REDACTED]"), redacted)
    return redacted


def policy_scan(path: str, content: str) -> list[str]:
    hits: list[str] = []

    # forbidden 8080 anywhere relevant
    if FORBIDDEN_8080_RE.search(content):
        hits.append("forbidden_port_8080")

    # compose: host ports must be within 12344-12399 if published
    if path.startswith("docker-compose") and path.endswith((".yml", ".yaml")):
        for line in content.splitlines():
            m = HOST_PORT_RE.search(line)
            if not m:
                continue
            try:
                host = int(m.group(1))
            except Exception:
                continue
            if host < 12344 or host > 12399:
                hits.append(f"host_port_out_of_range:{host}")

    # html-only + UI routing law
    if path.startswith("apps/") and path.endswith(".html"):
        if SCRIPT_RE.search(content):
            hits.append("html_forbidden_script_tag")
        if INLINE_STYLE_RE.search(content):
            hits.append("html_forbidden_inline_style")
        if STYLESHEET_LINK_RE.search(content):
            hits.append("html_forbidden_stylesheet_link")
        if AGENT_PORT_RE.search(content):
            hits.append("ui_links_agent_port")

    return sorted(set(hits))


def preview_lines(text: str, max_lines: int) -> list[str]:
    lines = text.splitlines()
    return lines[:max_lines]


def write_reports(findings: list[FileFinding], out_dir: Path, max_preview_lines: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "repo_scan_report.md"
    json_path = out_dir / "repo_scan_report.json"

    # JSON
    payload = {
        "cwd": os.getcwd(),
        "git_root": git_root(),
        "file_count": len(findings),
        "max_preview_lines": max_preview_lines,
        "files": [asdict(f) for f in findings],
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Markdown
    policy_counts: dict[str, int] = {}
    for f in findings:
        for h in f.policy_hits:
            policy_counts[h] = policy_counts.get(h, 0) + 1

    md: list[str] = []
    md.append("# Repo Scan Report")
    md.append("")
    md.append(f"- Files captured: **{len(findings)}**")
    md.append(f"- Preview lines per file: **{max_preview_lines}**")
    md.append("")
    md.append("## Policy Summary")
    if policy_counts:
        for k in sorted(policy_counts):
            md.append(f"- `{k}`: {policy_counts[k]}")
    else:
        md.append("- No policy hits detected.")
    md.append("")
    md.append("## Files")
    for f in findings:
        md.append(f"### `{f.path}` ({f.bytes} bytes)")
        md.append(f"- Policy hits: {', '.join(f.policy_hits) if f.policy_hits else 'none'}")
        md.append("")
        md.append("```")
        md.extend(f.preview)
        md.append("```")
        md.append("")
    md_path.write_text("\n".join(md), encoding="utf-8")

    print(f"✅ Wrote {md_path}")
    print(f"✅ Wrote {json_path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate repo scan report (MD + JSON).")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true", help="Scan staged files (git index).")
    mode.add_argument("--tracked", action="store_true", help="Scan tracked files (git ls-files).")
    mode.add_argument("--paths", nargs="+", help="Scan only given paths (files or dirs).")

    ap.add_argument("--include", nargs="*", default=DEFAULT_INCLUDE, help="Regex patterns to include.")
    ap.add_argument("--max-preview-lines", type=int, default=MAX_PREVIEW_LINES_DEFAULT)
    ap.add_argument("--out-dir", default="build")
    args = ap.parse_args()

    include_patterns = args.include
    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)

    # build candidate list
    candidates: list[str] = []
    if args.staged:
        candidates = list_staged_files()
        read = read_file_from_index
    elif args.tracked:
        candidates = list_tracked_files()
        read = read_file_from_fs
    else:
        # expand paths
        expanded: list[str] = []
        for p in args.paths:
            pp = Path(p)
            if pp.is_dir():
                expanded.extend([x.as_posix() for x in pp.rglob("*") if x.is_file()])
            elif pp.is_file():
                expanded.append(pp.as_posix())
        candidates = expanded
        read = read_file_from_fs

    findings: list[FileFinding] = []
    for path in sorted(set(candidates)):
        if is_excluded(path, exclude_dirs):
            continue
        if not matches_any(path, include_patterns):
            continue

        try:
            content = read(path)
        except Exception:
            # skip unreadable
            continue

        content = redact(content)
        hits = policy_scan(path, content)
        prev = preview_lines(content, args.max_preview_lines)

        # size from FS if available; else estimate
        b = 0
        try:
            b = Path(path).stat().st_size
        except Exception:
            b = len(content.encode("utf-8", errors="ignore"))

        findings.append(FileFinding(path=path, bytes=b, policy_hits=hits, preview=prev))

    write_reports(findings, Path(args.out_dir), args.max_preview_lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
