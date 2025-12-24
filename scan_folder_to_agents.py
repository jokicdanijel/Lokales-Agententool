#!/usr/bin/env python3
"""scan_folder_to_agents.py

Scans a local project folder ("existing ordner") and generates:
- folder_report.json (structure + detected capabilities)
- agent_prompts/ (one prompt per detected capability area)
- master_meta_prompt.md (project-level meta prompt)

Design goals:
- Works on plain HTML projects AND modern webapps (Next/React/Vue/Svelte/etc.)
- Pure heuristics: no execution, no dependency install.

Usage:
  python scan_folder_to_agents.py /path/to/project
  python scan_folder_to_agents.py . --out ./_agent_output

"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

BANNED_NAME_MARKERS = {
    "demo",
    "simulation",
    "phantom",
    "mock",
    "example",
    "fixture",
    "demos",
    "simulations",
    "phantoms",
    "mocks",
    "examples",
    "fixtures",
}

CAPABILITY_RULES = {
    "auth": [r"\bauth\b", r"\blogin\b", r"\bregister\b", r"\breset\b", r"\bmfa\b", r"\bsso\b"],
    "dashboard": [r"\bdashboard\b", r"\bwidgets?\b", r"\boverview\b", r"\bmetrics?\b"],
    "docs": [r"\bdocs?\b", r"\bknowledge\b", r"\bmanual\b", r"\bhandbook\b"],
    "settings": [r"\bsettings\b", r"\bpreferences\b", r"\bprofile\b", r"\baccount\b"],
    "admin": [r"\badmin\b", r"\buser management\b", r"\baudit\b", r"\bmoderation\b"],
    "rbac": [r"\brbac\b", r"\brole\b", r"\bpermission\b", r"\bauthorization\b"],
    "api": [r"openapi", r"swagger", r"/api/", r"\bendpoint\b"],
    "i18n": [r"\bi18n\b", r"\blocalization\b", r"\btranslations?\b", r"\blocale\b"],
    "billing": [r"\bbilling\b", r"\bsubscription\b", r"\bstripe\b", r"\binvoice\b"],
    "notifications": [r"\bnotification\b", r"\btoast\b", r"\balerts?\b"],
}

TECH_SIGNATURES = {
    "nextjs": ["next.config", "app/", "pages/", "next-auth"],
    "react": ["react", "jsx", "tsx"],
    "vue": ["vue", "nuxt"],
    "svelte": ["svelte", "sveltekit"],
    "angular": ["@angular"],
    "express": ["express"],
    "nestjs": ["@nestjs"],
    "django": ["django"],
    "flask": ["flask"],
}

TEXT_EXTS = {".md", ".txt", ".html", ".htm", ".js", ".ts", ".tsx", ".jsx", ".json", ".yml", ".yaml", ".py"}


@dataclass
class FileInfo:
    path: str
    size: int
    ext: str


@dataclass
class FolderReport:
    scanned_path: str
    generated_at: str
    file_count: int
    total_bytes: int
    max_depth_seen: int
    banned_name_hits: list[str]
    duplicate_name_groups: dict[str, list[FileInfo]]
    tech_stack_signals: dict[str, int]
    detected_capabilities: dict[str, float]
    page_candidates: list[str]
    shared_component_candidates: list[str]


def safe_read_text(p: Path, max_bytes: int = 200_000) -> str:
    try:
        data = p.read_bytes()
        data = data[:max_bytes]
        # Try utf-8, fallback latin1.
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return data.decode("latin-1", errors="ignore")
    except Exception:
        return ""


def compute_depth(base: Path, p: Path) -> int:
    try:
        rel = p.relative_to(base)
        return len(rel.parts)
    except Exception:
        return 0


def score_capabilities(text_blob: str, file_paths_blob: str) -> dict[str, float]:
    scores: dict[str, float] = {k: 0.0 for k in CAPABILITY_RULES.keys()}
    combined = (text_blob + "\n" + file_paths_blob).lower()
    for cap, patterns in CAPABILITY_RULES.items():
        hit = 0
        for pat in patterns:
            if re.search(pat, combined, flags=re.IGNORECASE):
                hit += 1
        # normalize: 0..1
        scores[cap] = min(1.0, hit / max(1, len(patterns)))
    # boost if folder names exist explicitly
    for folder_cap in ["auth", "dashboard", "docs", "settings", "admin"]:
        if re.search(rf"(^|/){folder_cap}(/|$)", file_paths_blob.lower()):
            scores[folder_cap] = min(1.0, scores[folder_cap] + 0.4)
    return scores


def detect_tech_stack(package_json_text: str, all_text: str, file_paths_blob: str) -> dict[str, int]:
    signals = Counter()
    blob = (package_json_text + "\n" + all_text + "\n" + file_paths_blob).lower()
    for tech, sigs in TECH_SIGNATURES.items():
        for s in sigs:
            if s.endswith("/"):
                if s in file_paths_blob.lower():
                    signals[tech] += 1
            else:
                if s in blob:
                    signals[tech] += 1
    return dict(signals)


def classify_pages_and_components(base: Path, files: list[Path]) -> tuple[list[str], list[str]]:
    page_candidates: list[str] = []
    components: list[str] = []

    for p in files:
        rel = str(p.relative_to(base)).replace("\\", "/")
        name = p.name.lower()

        # Pages: html entry points, route-ish files, docs pages
        if p.suffix.lower() in {".html", ".htm"}:
            # index.html in a feature folder = likely page
            page_candidates.append(rel)

        if any(seg in rel.lower() for seg in ["/pages/", "/app/", "/routes/", "/views/"]):
            if p.suffix.lower() in {".tsx", ".jsx", ".ts", ".js"}:
                # heuristic: treat as page if name suggests route
                if (
                    name in {"page.tsx", "page.jsx", "index.tsx", "index.jsx", "index.ts", "index.js"}
                    or "route" in name
                ):
                    page_candidates.append(rel)

        # Shared components: components folder, partials, includes
        if any(
            seg in rel.lower()
            for seg in ["/components/", "/shared/", "/shared_components/", "/partials/", "/includes/", "/layouts/"]
        ):
            if p.suffix.lower() in {".html", ".htm", ".tsx", ".jsx", ".ts", ".js"}:
                components.append(rel)

    # de-dup while preserving order
    def uniq(xs: list[str]) -> list[str]:
        seen = set()
        out = []
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    return uniq(page_candidates), uniq(components)


AGENT_PROMPT_TEMPLATES = {
    "auth": """# Agent: Auth & Session Architect\n\n## Mission\nDesign and maintain the authentication surface area: login, register, reset, MFA/SSO entry points.\n\n## Scope\n- Semantic page scaffolds for auth flows\n- Explicit markers for session handling, CSRF, rate limiting, lockouts\n- RBAC handoff points (post-login routing)\n\n## Output Contract\nFor each auth-related page: zones, happy-path + error branches, semantic HTML skeleton (no CSS/JS), and security comments (AUTH/VALIDATION/RBAC/AUDIT/PII).\n\n## Guardrails\n- Never implement auth; only place logic markers\n- Always highlight PII fields and audit-relevant events\n""",
    "dashboard": """# Agent: Dashboard Information Architect\n\n## Mission\nTranslate dashboard sketches into stable information architecture: navigation, widgets, KPIs, and dynamic zones.\n\n## Scope\n- Semantic layout shells (topbar/sidebar/main)\n- Widget grid as semantic sections/articles\n- Data provenance markers (DYNAMIC + source hints)\n\n## Output Contract\nOne page per run, with zones, user flow, and HTML skeleton annotated for dynamic content and permissions.\n""",
    "docs": """# Agent: Documentation & Knowledge Base Architect\n\n## Mission\nConvert docs/knowledge areas into navigable, semantic structures: categories, articles, search entry points, changelog.\n\n## Scope\n- Semantic doc layouts (toc, breadcrumbs, content article)\n- Mark search/indexing zones (DYNAMIC)\n- Versioning and access hints (RBAC)\n""",
    "settings": """# Agent: Settings & Profile Architect\n\n## Mission\nStructure settings surfaces: profile, org, security, API keys, preferences.\n\n## Scope\n- Forms with explicit VALIDATION markers\n- Sensitive actions tagged (AUDIT/PII/RBAC)\n- Clear grouping: account vs org vs security\n""",
    "admin": """# Agent: Admin & Control Plane Architect\n\n## Mission\nDefine admin interfaces: user management, audits, system configuration, moderation.\n\n## Scope\n- RBAC-first page skeletons\n- Audit log surfaces and filters\n- Dangerous actions flagged with explicit warnings\n""",
    "rbac": """# Agent: RBAC & Permissions Modeler\n\n## Mission\nExtract and formalize roles, permissions, and page/action visibility constraints.\n\n## Output Contract\n- RBAC matrix (roles x actions)\n- Page-level access assumptions\n- Markers to embed into HTML skeleton comments\n""",
    "api": """# Agent: Data Contract & API Surface Mapper\n\n## Mission\nMap dynamic UI zones to data contracts (not implementation).\n\n## Output Contract\n- For each DYNAMIC zone: expected data shape, source (API/DB), caching/latency concerns (comments only)\n- Identify PII and audit-relevant payloads\n""",
    "i18n": """# Agent: i18n & Content Localization Planner\n\n## Mission\nPlan structure for localization: string ownership, locale switching surfaces, RTL risks.\n\n## Output Contract\n- List UI zones requiring translation\n- Mark language switcher + locale persistence points\n""",
    "billing": """# Agent: Billing & Subscription Surface Architect\n\n## Mission\nStructure billing pages: plans, invoices, payment method, subscription lifecycle.\n\n## Output Contract\n- Semantic skeletons with security markers\n- Explicit audit/PII markers (payments, invoices)\n""",
    "notifications": """# Agent: Notifications & Messaging UX Architect\n\n## Mission\nDefine notification surfaces: inbox, toast area, system alerts, preferences.\n\n## Output Contract\n- Semantic placement + DYNAMIC markers\n- Preference flows in settings handoff\n""",
}

MASTER_META_PROMPT = """# Master Meta-Prompt: Surface System Architecture\n\nYou are a Digital Surface Architect. Your job is to translate sketches and existing project artifacts into semantic HTML page skeletons and a modular project structure.\n\n## Operating Rules\n- One page per iteration.\n- No CSS, no JS.\n- Use semantic tags and annotate future logic with comments: INTENT, AUTH, RBAC, VALIDATION, DYNAMIC, AUDIT, PII.\n\n## Project Goal\nMaintain a coherent, scalable information architecture where pages live inside an order (auth, dashboard, docs, settings, admin) and share reusable layouts/components.\n\n## Output\nFor each page: zones, user flow, patterns, semantic HTML skeleton, project placement, risks, and max 5 questions if ambiguity exists.\n"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=".", help="Project folder to scan")
    ap.add_argument("--out", default="_agent_output", help="Output folder")
    ap.add_argument("--max-files", type=int, default=6000, help="Safety cap")
    args = ap.parse_args()

    base = Path(args.path).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    files: list[Path] = []
    total_bytes = 0
    max_depth = 0
    banned_hits: list[str] = []

    # Walk
    for root, dirs, fnames in os.walk(base):
        # skip output folder if inside base
        if Path(root).resolve() == out_dir:
            continue

        for d in list(dirs):
            dn = d.lower()
            if dn in {"node_modules", ".git", ".next", "dist", "build", "venv", ".venv", "__pycache__"}:
                dirs.remove(d)

        for f in fnames:
            p = Path(root) / f
            try:
                if not p.is_file():
                    continue
            except Exception:
                continue

            files.append(p)
            if len(files) >= args.max_files:
                break

        if len(files) >= args.max_files:
            break

    # Collect file infos
    file_infos: list[FileInfo] = []
    by_name: dict[str, list[FileInfo]] = defaultdict(list)
    file_paths_blob_parts: list[str] = []

    for p in files:
        rel = str(p.relative_to(base)).replace("\\", "/")
        file_paths_blob_parts.append(rel)
        ext = p.suffix.lower()
        try:
            size = p.stat().st_size
        except Exception:
            size = 0

        total_bytes += size
        max_depth = max(max_depth, compute_depth(base, p))

        lower_rel = rel.lower()
        for marker in BANNED_NAME_MARKERS:
            if re.search(rf"(^|/|_)({re.escape(marker)})(/|_|\.)", lower_rel):
                banned_hits.append(rel)
                break

        fi = FileInfo(path=rel, size=size, ext=ext)
        file_infos.append(fi)
        by_name[p.name.lower()].append(fi)

    duplicate_groups = {k: v for k, v in by_name.items() if len(v) > 1}

    # Build text blob from small/medium text files
    text_parts: list[str] = []
    package_json_text = ""

    for p in files:
        ext = p.suffix.lower()
        if ext not in TEXT_EXTS:
            continue

        rel = str(p.relative_to(base)).replace("\\", "/")
        # Prioritize readme/docs/package
        if p.name.lower() == "package.json":
            package_json_text = safe_read_text(p)
            text_parts.append(package_json_text)
        elif p.name.lower() in {"readme.md", "readme.txt"} or rel.lower().startswith("docs/"):
            text_parts.append(safe_read_text(p))
        else:
            # sample a subset to keep it fast
            if len(text_parts) < 80:
                text_parts.append(safe_read_text(p))

    all_text = "\n".join(text_parts)
    file_paths_blob = "\n".join(file_paths_blob_parts)

    caps = score_capabilities(all_text, file_paths_blob)
    tech = detect_tech_stack(package_json_text, all_text, file_paths_blob)
    pages, components = classify_pages_and_components(base, files)

    report = FolderReport(
        scanned_path=str(base),
        generated_at=datetime.utcnow().isoformat() + "Z",
        file_count=len(file_infos),
        total_bytes=total_bytes,
        max_depth_seen=max_depth,
        banned_name_hits=sorted(set(banned_hits)),
        duplicate_name_groups={k: sorted(v, key=lambda x: (-x.size, x.path)) for k, v in duplicate_groups.items()},
        tech_stack_signals=tech,
        detected_capabilities=caps,
        page_candidates=pages[:400],
        shared_component_candidates=components[:400],
    )

    (out_dir / "folder_report.json").write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    # Generate agent prompts for detected capabilities above threshold
    agent_dir = out_dir / "agent_prompts"
    agent_dir.mkdir(parents=True, exist_ok=True)

    selected_caps = [k for k, v in caps.items() if v >= 0.35 and k in AGENT_PROMPT_TEMPLATES]
    if not selected_caps:
        # fallback: generate core agents
        selected_caps = ["auth", "dashboard", "docs", "settings", "admin"]

    for cap in selected_caps:
        (agent_dir / f"agent_{cap}.md").write_text(AGENT_PROMPT_TEMPLATES[cap], encoding="utf-8")

    # Master meta prompt
    (out_dir / "master_meta_prompt.md").write_text(MASTER_META_PROMPT, encoding="utf-8")

    # Quick index
    index_md = [
        "# Agent Output Index",
        "",
        f"Scanned: `{base}`",
        f"Generated: `{report.generated_at}`",
        "",
        "## Detected capabilities (0..1)",
    ]
    for k, v in sorted(caps.items(), key=lambda kv: (-kv[1], kv[0])):
        index_md.append(f"- **{k}**: {v:.2f}")
    index_md += [
        "",
        "## Tech stack signals",
    ]
    if tech:
        for k, v in sorted(tech.items(), key=lambda kv: (-kv[1], kv[0])):
            index_md.append(f"- {k}: {v}")
    else:
        index_md.append("- (no strong signals detected)")

    index_md += [
        "",
        "## Generated agent prompts",
    ]
    for cap in selected_caps:
        index_md.append(f"- agent_prompts/agent_{cap}.md")

    index_md += [
        "",
        "## Next steps",
        "1) Review folder_report.json for false positives.",
        "2) Edit the generated agent prompts to match your product language.",
        "3) Feed one sketch/page at a time to the relevant agent.",
    ]

    (out_dir / "INDEX.md").write_text("\n".join(index_md), encoding="utf-8")

    print(f"OK: wrote output to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
