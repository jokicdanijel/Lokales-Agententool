#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_project: Rekursiver Repo-Scanner für ChatGPT-freundliche Projekt-Maps.
Erzeugt: STRUCTURE.md, TREE.txt, files.csv, path_index.json, stats.json, violations.md
Nur Python-Stdlib, performant für große Repos, cross-platform.
"""
from __future__ import annotations

import os
import sys
import json
import csv
import argparse
import time
import platform
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple

# Lokale Utils
sys.path.insert(0, os.path.dirname(__file__))
try:
    from _common import (
        relpath_posix,
        iso_utc,
        file_ext,
        path_depth,
        is_executable,
        is_probably_binary,
        sha256_limited,
        load_gitignore_patterns,
        should_exclude,
        render_tree,
        human_bytes,
    )
except ImportError as e:
    print(f"[ERROR] Could not import _common: {e}", file=sys.stderr)
    sys.exit(1)

# Harte Excludes (Standard-Verzeichnisse, Dateimuster)
DEFAULT_EXCLUDES = {
    ".git/",
    ".github/",
    ".gitlab/",
    ".idea/",
    ".vscode/",
    "node_modules/",
    "venv/",
    ".venv/",
    "env/",
    "dist/",
    "build/",
    "__pycache__/",
    "coverage/",
    "backups/",
    "_conflicts/",
    "*.log",
    "*.lock",
    "*.tmp",
    "*.bin",
    "*.min.*",
    "*.class",
    "*.o",
    "*.so",
    "*.dll",
    "*.dylib",
    "*.iso",
    "*.img",
}

VIOLATION_MAX_DEPTH = 6
VIOLATION_LARGE_BYTES = 25 * 1024 * 1024  # 25 MB


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Scan repository and build ChatGPT-friendly project map."
    )
    p.add_argument("--root", default=".", help="Root directory to scan")
    p.add_argument("--out", default="project_map", help="Output directory")
    p.add_argument(
        "--max-tree-depth",
        type=int,
        default=4,
        help="Max depth for STRUCTURE tree section",
    )
    p.add_argument(
        "--hash-limit-mb",
        type=int,
        default=5,
        help="Max size for sha256 hashing per file (MB)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    t0 = time.time()

    root = os.path.abspath(args.root)
    outdir = os.path.abspath(args.out)

    # Erstelle Output-Verzeichnis
    try:
        os.makedirs(outdir, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Cannot create {outdir}: {e}", file=sys.stderr)
        return 1

    # Lade .gitignore
    gitignore_patterns = load_gitignore_patterns(root)
    hard_excludes = set(DEFAULT_EXCLUDES)

    files: List[Dict[str, Any]] = []
    errors: List[str] = []
    skipped: int = 0
    processed: int = 0

    print(f"[INFO] Starting scan of {root}", file=sys.stderr)
    print(f"[INFO] Output → {outdir}", file=sys.stderr)

    # Walk mit Pruning
    for cur, dirs, fnames in os.walk(root, topdown=True, followlinks=False):
        rel_dir = relpath_posix(cur, root)

        # Verzeichnispruning (harte + gitignore)
        pruned_dirs = []
        for d in list(dirs):
            try:
                ap = os.path.join(cur, d)
                rel_path = relpath_posix(ap, root)
                rel_posix = rel_path + "/"
                if should_exclude(rel_posix, True, gitignore_patterns, hard_excludes):
                    pruned_dirs.append(d)
            except Exception:
                pruned_dirs.append(d)

        for d in pruned_dirs:
            dirs.remove(d)

        # Dateiverarbeitung
        for fn in fnames:
            processed += 1
            if processed % 1000 == 0:
                print(f"[PROGRESS] {processed} files processed...", file=sys.stderr)

            ap = os.path.join(cur, fn)
            rel = relpath_posix(ap, root)

            try:
                if should_exclude(rel, False, gitignore_patterns, hard_excludes):
                    skipped += 1
                    continue

                st = os.lstat(ap)  # Symlink-Info inklusive
                is_link = os.path.islink(ap)
                mode = st.st_mode

                ext = file_ext(ap)
                depth = path_depth(rel)
                size = st.st_size if not is_link and os.path.isfile(ap) else 0
                mtime = st.st_mtime
                executable = is_executable(mode)
                binary = False
                symlink_target = None

                if is_link:
                    try:
                        symlink_target = os.readlink(ap)
                    except Exception:
                        pass
                elif os.path.isfile(ap):
                    binary = is_probably_binary(ap)

                # SHA256 (limit)
                limit_bytes = args.hash_limit_mb * 1024 * 1024
                sha = None
                if not is_link and os.path.isfile(ap):
                    sha = sha256_limited(ap, limit_bytes)

                record = {
                    "path": rel,
                    "size_bytes": int(size),
                    "mtime_iso": iso_utc(mtime),
                    "ext": ext,
                    "depth": int(depth),
                    "is_symlink": bool(is_link),
                    "symlink_target": symlink_target,
                    "is_executable": bool(executable),
                    "is_binary": bool(binary),
                    "sha256": sha,
                }
                files.append(record)
            except Exception as e:
                skipped += 1
                errors.append(f"{rel}: {type(e).__name__}: {e}")

    # Summaries
    total_size = sum(f["size_bytes"] for f in files)
    by_ext = Counter(f["ext"] for f in files)
    by_top = Counter(
        (f["path"].split("/", 1)[0] if "/" in f["path"] else f["path"])
        for f in files
    )

    # Hotspots
    largest = sorted(files, key=lambda x: x["size_bytes"], reverse=True)[:20]
    youngest = sorted(files, key=lambda x: x["mtime_iso"], reverse=True)[:20]

    # Violations
    violations: List[str] = []

    too_deep = [f for f in files if f["depth"] > VIOLATION_MAX_DEPTH]
    for f in too_deep:
        violations.append(f"[DEPTH >{VIOLATION_MAX_DEPTH}] {f['path']} (depth={f['depth']})")

    too_large = [f for f in files if f["size_bytes"] >= VIOLATION_LARGE_BYTES]
    for f in too_large:
        sz = human_bytes(f["size_bytes"])
        violations.append(
            f"[SIZE ≥{human_bytes(VIOLATION_LARGE_BYTES)}] {f['path']} ({sz})"
        )

    bin_in_src = [f for f in files if f["is_binary"] and f["path"].startswith("src/")]
    for f in bin_in_src:
        violations.append(f"[BINARY_IN_SRC] {f['path']}")

    # Duplizierte Dateinamen
    name_map: Dict[str, List[str]] = defaultdict(list)
    for f in files:
        name_map[os.path.basename(f["path"])].append(f["path"])
    dup_names = {k: v for k, v in name_map.items() if len(v) > 1}
    for base, paths in sorted(dup_names.items()):
        examples = ", ".join(paths[:3])
        violations.append(f"[DUP_NAME] {base} (appears {len(paths)}x: {examples})")

    # Sortierung stabil (case-insensitive)
    files.sort(key=lambda r: r["path"].lower())

    # === TREE.txt (vollständig, kein Pruning) ===
    print("[PROGRESS] Generating TREE.txt", file=sys.stderr)
    tree_full = render_tree(root, (f["path"] for f in files), max_depth=None)
    with open(os.path.join(outdir, "TREE.txt"), "w", encoding="utf-8") as f:
        f.write(tree_full + "\n")

    # === STRUCTURE.md (kompakt) ===
    print("[PROGRESS] Generating STRUCTURE.md", file=sys.stderr)
    struct_tree = render_tree(
        root, (f["path"] for f in files), max_depth=args.max_tree_depth
    )
    struct_md: List[str] = []
    struct_md.append("# Project Structure\n")
    struct_md.append(f"- **Root**: `{os.path.basename(root)}`")
    struct_md.append(f"- **Scanned**: `{iso_utc(time.time())}`")
    struct_md.append(
        f"- **Host**: `{platform.system()} {platform.release()}` · Python: `{platform.python_version()}`\n"
    )
    struct_md.append(
        f"| Metric | Value |"
    )
    struct_md.append(
        f"|---|---|"
    )
    struct_md.append(
        f"| **Files** | {len(files)} |"
    )
    struct_md.append(
        f"| **Total Size** | {human_bytes(total_size)} |"
    )
    struct_md.append(
        f"| **Skipped** | {skipped} |"
    )
    struct_md.append(
        f"| **Duration** | {time.time() - t0:.1f}s |\n"
    )

    # Directory Tree
    struct_md.append("## Directory Tree (depth ≤ {})\n".format(args.max_tree_depth))
    struct_md.append("```text")
    struct_md.append(struct_tree)
    struct_md.append("```\n")

    # Key Areas
    key_roots = ["src", "app", "services", "packages", "configs", "scripts", "docs", "tests"]
    key_rows = []
    for kr in key_roots:
        count = sum(1 for f in files if f["path"] == kr or f["path"].startswith(kr + "/"))
        if count > 0:
            key_rows.append((f"`{kr}/`", f"{count} files"))
    if key_rows:
        struct_md.append("## Key Areas\n")
        struct_md.append("| Area | Count |")
        struct_md.append("|---|---|")
        for k, v in key_rows:
            struct_md.append(f"| {k} | {v} |")
        struct_md.append("")

    # Hotspots: Largest
    if largest:
        struct_md.append("## Hotspots: Largest Files (Top 20)\n")
        struct_md.append("| File | Size |")
        struct_md.append("|---|---|")
        for x in largest:
            struct_md.append(f"| `{x['path']}` | {human_bytes(x['size_bytes'])} |")
        struct_md.append("")

    # Hotspots: Youngest
    if youngest:
        struct_md.append("## Hotspots: Newest Files (Top 20)\n")
        struct_md.append("| File | Modified |")
        struct_md.append("|---|---|")
        for x in youngest:
            struct_md.append(f"| `{x['path']}` | {x['mtime_iso']} |")
        struct_md.append("")

    # By Extension
    if by_ext:
        struct_md.append("## Files by Extension\n")
        struct_md.append("| Extension | Count |")
        struct_md.append("|---|---|")
        for ext in sorted(by_ext.keys(), key=lambda e: (e or "(no ext)").lower()):
            ext_label = f"`{ext}`" if ext else "(no ext)"
            struct_md.append(f"| {ext_label} | {by_ext[ext]} |")
        struct_md.append("")

    # By Top-Level
    if by_top:
        struct_md.append("## Files by Top-Level Folder\n")
        struct_md.append("| Folder | Count |")
        struct_md.append("|---|---|")
        for folder in sorted(by_top.keys(), key=lambda f: (f or "(root)").lower()):
            folder_label = f"`{folder}/`" if folder else "(root)"
            struct_md.append(f"| {folder_label} | {by_top[folder]} |")
        struct_md.append("")

    with open(os.path.join(outdir, "STRUCTURE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(struct_md) + "\n")

    # === CSV ===
    print("[PROGRESS] Generating files.csv", file=sys.stderr)
    csv_path = os.path.join(outdir, "files.csv")
    fieldnames = [
        "path",
        "size_bytes",
        "mtime_iso",
        "ext",
        "depth",
        "is_symlink",
        "symlink_target",
        "is_executable",
        "is_binary",
        "sha256",
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in files:
            w.writerow(r)

    # === JSON Index ===
    print("[PROGRESS] Generating path_index.json", file=sys.stderr)
    with open(os.path.join(outdir, "path_index.json"), "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=2)

    # === Stats ===
    print("[PROGRESS] Generating stats.json", file=sys.stderr)
    stats = {
        "scanned_at": iso_utc(time.time()),
        "root": os.path.basename(root),
        "file_count": len(files),
        "total_size_bytes": total_size,
        "by_extension": dict(by_ext),
        "by_top_level": dict(by_top),
        "hash_limit_bytes": args.hash_limit_mb * 1024 * 1024,
        "violations_count": len(violations),
        "errors_count": len(errors),
        "duration_sec": round(time.time() - t0, 3),
    }
    with open(os.path.join(outdir, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # === Violations ===
    print("[PROGRESS] Generating violations.md", file=sys.stderr)
    with open(os.path.join(outdir, "violations.md"), "w", encoding="utf-8") as f:
        if not (violations or errors):
            f.write("# Violations & Findings\n\n_No violations detected._ ✓\n")
        else:
            f.write("# Violations & Findings\n\n")
            if violations:
                f.write("## Policy Violations\n\n")
                for line in violations:
                    f.write(f"- {line}\n")
                f.write("\n")
            if errors:
                f.write("## Scan Errors\n\n")
                for e in errors[:200]:
                    f.write(f"- {e}\n")
                if len(errors) > 200:
                    f.write(f"- ... and {len(errors) - 200} more errors\n")

    # Verifiziere Output-Artefakte
    required = [
        "STRUCTURE.md",
        "TREE.txt",
        "files.csv",
        "path_index.json",
        "stats.json",
        "violations.md",
    ]
    missing = [p for p in required if not os.path.exists(os.path.join(outdir, p))]

    if missing:
        print(f"[ERROR] Missing outputs: {', '.join(missing)}", file=sys.stderr)
        return 2

    # Success Summary
    duration = time.time() - t0
    print(f"\n[OK] Scan complete → {relpath_posix(outdir, root)}", file=sys.stderr)
    print(
        f"Files: {len(files)} | Size: {human_bytes(total_size)} | Skipped: {skipped} | Duration: {duration:.1f}s",
        file=sys.stderr,
    )
    if violations:
        print(f"⚠ {len(violations)} violations found (see violations.md)", file=sys.stderr)
    if errors:
        print(f"⚠ {len(errors)} scan errors (see violations.md)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
