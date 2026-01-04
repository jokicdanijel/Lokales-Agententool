#!/usr/bin/env python3
"""Deterministic project map generator (no extra dependencies)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]

OUT_DIR = ROOT / "project_map"
OUT_TREE = OUT_DIR / "repo_tree.txt"
OUT_JSON = OUT_DIR / "project_map.json"
OUT_MD = OUT_DIR / "PROJECT_MAP.md"

IGNORE_DIRS = {
    ".git", ".github", "__pycache__", ".mypy_cache", ".pytest_cache",
    ".venv", "venv", "venv312", "venv313",
    "node_modules", ".idea", ".vscode",
    "dist", "build", "artifacts", "logs",
}

TEXT_EXTS = {".md", ".py", ".sh", ".yaml", ".yml", ".json", ".toml", ".html", ".css", ".js", ".txt"}

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def should_skip_dir(p: Path) -> bool:
    return p.name in IGNORE_DIRS

def walk_repo(root: Path) -> List[str]:
    files: List[str] = []
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            entries = sorted(d.iterdir(), key=lambda x: x.name)
        except Exception:
            continue

        dirs = []
        for e in entries:
            if e.is_dir():
                if not should_skip_dir(e):
                    dirs.append(e)
            elif e.is_file():
                rel = e.relative_to(root).as_posix()
                files.append(rel)

        for dd in reversed(dirs):
            stack.append(dd)

    files.sort()
    return files

def render_tree(files: List[str], max_lines: int = 2000) -> str:
    lines: List[str] = []
    prev_parts: List[str] = []
    for f in files:
        parts = f.split("/")
        common = 0
        for a, b in zip(prev_parts, parts):
            if a == b:
                common += 1
            else:
                break
        indent = "  " * (len(parts) - 1)
        lines.append(f"{indent}- {parts[-1]}")
        prev_parts = parts
        if len(lines) >= max_lines:
            lines.append("... (truncated)")
            break
    return "\n".join(lines) + "\n"

def build_summary(files: List[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for f in files:
        ext = Path(f).suffix.lower()
        counts[ext] = counts.get(ext, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: (-x[1], x[0])))

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = walk_repo(ROOT)
    tree = render_tree(files)
    counts = build_summary(files)
    inventory_hash = sha256_text("\n".join(files))

    payload = {
        "repo_root": str(ROOT),
        "file_count": len(files),
        "inventory_sha256": inventory_hash,
        "extensions": counts,
        "files": files,
    }

    OUT_TREE.write_text(tree, encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md = [
        "# Auto Project Map",
        "",
        f"- Repo root: `{ROOT}`",
        f"- Files discovered: **{len(files)}**",
        f"- Inventory sha256: `{inventory_hash}`",
        "",
        "## Top extensions",
        "",
    ]
    for ext, n in list(counts.items())[:15]:
        md.append(f"- `{ext or '<noext>'}`: {n}")
    md.append("")
    md.append("## Repo tree (excerpt)")
    md.append("")
    md.append("```")
    md.append(tree[:20000])
    md.append("```")
    md.append("")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"[MAP] Wrote: {OUT_TREE}")
    print(f"[MAP] Wrote: {OUT_JSON}")
    print(f"[MAP] Wrote: {OUT_MD}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
