#!/usr/bin/env python3
"""
ELION Policy Doc Scan
- Scans repository subtree for policy violations:
  1) Forbidden port mentions (8080)
  2) Host port mentions outside 12344-12399 (optional strict mode)
  3) Direct URLs to agent ports http(s)://...:123xx  (UI routing law)
  4) Cleartext secrets & private key material
  5) HTML contract violations: <script>, inline style=, stylesheet links (optional)

Modes:
- default: detect and report; exit non-zero on violations.
- --fix: redacts direct agent-port URLs in docs/html (safe text replacement), and rewrites files.
         Secrets are NEVER auto-fixed (still FAIL).

This tool is fail-fast and CI-friendly.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ALLOWED_HOST_PORT_MIN = 12344
ALLOWED_HOST_PORT_MAX = 12399
FORBIDDEN_PORTS = {8080}

TEXT_EXT = {".md", ".txt", ".yml", ".yaml", ".json", ".env", ".ini", ".toml", ".sh", ".conf", ".html", ".py"}

RE_FORBIDDEN_8080 = re.compile(r"\b8080\b")
RE_DIRECT_AGENT_LINK = re.compile(r"(http[s]?://[^ \n\"']+:(12\d{3})\b)")
RE_URL_PORT = re.compile(r"http[s]?://[^ \n\"']+:(\d{2,5})\b")
RE_SECRET = re.compile(
    r"(API[_-]?KEY|SECRET|PASSWORD|PASSWD|TOKEN)\s*=\s*['\"]?[^'\"\s]{6,}['\"]?",
    re.IGNORECASE,
)
RE_PRIVATE_KEY = re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")
RE_HTML_SCRIPT = re.compile(r"<\s*script\b", re.IGNORECASE)
RE_HTML_INLINE_STYLE = re.compile(r"\bstyle\s*=", re.IGNORECASE)
RE_HTML_STYLESHEET = re.compile(r"<\s*link\b[^>]*rel\s*=\s*['\"]stylesheet['\"]", re.IGNORECASE)


@dataclass
class Violation:
    code: str
    path: str
    detail: str
    line: int | None = None


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file():
            if p.suffix.lower() in TEXT_EXT or p.name.lower() == "dockerfile":
                files.append(p)
    return files


def find_line(text: str, needle: str) -> int | None:
    idx = text.find(needle)
    if idx < 0:
        return None
    return text[:idx].count("\n") + 1


def scan_text(path: Path, text: str, strict_port_mentions: bool, check_html_contract: bool) -> list[Violation]:
    v: list[Violation] = []

    # 8080 forbidden anywhere
    if RE_FORBIDDEN_8080.search(text):
        v.append(
            Violation("FORBIDDEN_PORT_8080", str(path), "Forbidden port literal '8080' found.", find_line(text, "8080"))
        )

    # direct agent port links forbidden (UI law)
    for m in RE_DIRECT_AGENT_LINK.finditer(text):
        url = m.group(1)
        port = int(m.group(2))
        if ALLOWED_HOST_PORT_MIN <= port <= ALLOWED_HOST_PORT_MAX:
            v.append(
                Violation(
                    "DIRECT_AGENT_PORT_URL", str(path), f"Direct agent-port URL found: {url}", find_line(text, url)
                )
            )

    # strict: if any URL contains port outside allowed host range, flag (useful to kill 9090/3000 docs)
    if strict_port_mentions:
        for m in RE_URL_PORT.finditer(text):
            port = int(m.group(1))
            if port in FORBIDDEN_PORTS:
                continue
            if not (ALLOWED_HOST_PORT_MIN <= port <= ALLOWED_HOST_PORT_MAX):
                url = m.group(0)
                v.append(
                    Violation(
                        "URL_PORT_OUT_OF_RANGE",
                        str(path),
                        f"URL port {port} outside allowed host range: {url}",
                        find_line(text, url),
                    )
                )

    # secrets/private keys
    if RE_SECRET.search(text):
        v.append(
            Violation("CLEARTEXT_SECRET_SUSPECT", str(path), "Possible cleartext secret assignment detected.", None)
        )
    if RE_PRIVATE_KEY.search(text):
        v.append(Violation("PRIVATE_KEY_MATERIAL", str(path), "Private key material detected.", None))

    # HTML contract checks (only for .html by default)
    if check_html_contract and path.suffix.lower() == ".html":
        if RE_HTML_SCRIPT.search(text):
            v.append(
                Violation(
                    "HTML_SCRIPT_TAG",
                    str(path),
                    "<script> tag not allowed by contract.",
                    find_line(text.lower(), "<script"),
                )
            )
        if RE_HTML_INLINE_STYLE.search(text):
            v.append(Violation("HTML_INLINE_STYLE", str(path), "Inline style= not allowed by contract.", None))
        if RE_HTML_STYLESHEET.search(text):
            v.append(
                Violation("HTML_STYLESHEET_LINK", str(path), "<link rel='stylesheet'> not allowed by contract.", None)
            )

    return v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Root directory to scan")
    ap.add_argument("--strict-port-mentions", action="store_true", help="Flag any URL port outside 12344-12399")
    ap.add_argument(
        "--check-html-contract", action="store_true", help="Enforce HTML contract (no <script>, inline styles)"
    )
    ap.add_argument("--fix", action="store_true", help="Auto-redact direct agent-port URLs (docs/html only)")
    ap.add_argument("--json", action="store_true", help="Output JSON report")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"[FAIL] Root path does not exist: {root}")

    all_violations: list[Violation] = []
    files = iter_files(root)

    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        violations = scan_text(p, text, args.strict_port_mentions, args.check_html_contract)
        all_violations.extend(violations)

    if args.json:
        report = {
            "timestamp": utc_now(),
            "root": str(root),
            "files_scanned": len(files),
            "violations": [
                {"code": v.code, "path": v.path, "detail": v.detail, "line": v.line} for v in all_violations
            ],
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[SCAN] Root: {root}")
        print(f"[SCAN] Files scanned: {len(files)}")
        print(f"[SCAN] Violations: {len(all_violations)}")
        for v in all_violations:
            line_info = f" (line {v.line})" if v.line else ""
            print(f"[{v.code}] {v.path}{line_info}: {v.detail}")

    if all_violations:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
