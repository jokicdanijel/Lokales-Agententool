#!/usr/bin/env python3
"""
_common: Hilfsfunktionen für den Repo-Scanner (nur Python-Stdlib).
Cross-platform, keine externen Pakete.
Funktionen für Pfade, Zeit, Inhalte, .gitignore-Parsing, Tree-Rendering.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import stat
from collections.abc import Iterable
from fnmatch import fnmatch


# -------------------------
# Pfad & Zeit-Helfer
# -------------------------
def relpath_posix(path: str, root: str) -> str:
    """Relativer Pfad, POSIX-Separator (/)."""
    rel = os.path.relpath(path, root)
    return rel.replace(os.sep, "/")


def iso_utc(ts: float) -> str:
    """Zeitstempel als ISO 8601 UTC."""
    return dt.datetime.fromtimestamp(ts, dt.UTC).isoformat()


def file_ext(path: str) -> str:
    """Datei-Extension (Lowercased)."""
    base = os.path.basename(path)
    if base.startswith(".") and base.count(".") == 1:
        return ""  # .gitignore, .editorconfig etc.
    _, ext = os.path.splitext(base)
    return ext.lower()


def path_depth(path_rel_posix: str) -> int:
    """Verschachtelungstiefe (/ als Trennzeichen)."""
    if path_rel_posix in (".", ""):
        return 0
    return path_rel_posix.count("/") + 1


# -------------------------
# Inhalte & Eigenschaften
# -------------------------
def is_executable(mode: int) -> bool:
    """Ist Datei ausführbar (Unix-Bits)."""
    return bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def is_probably_binary(path: str, read_limit: int = 4096) -> bool:
    """Heuristik: Nullbytes oder viele Steuerzeichen → binär."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(read_limit)
        if b"\x00" in chunk:
            return True
        # Viele Nicht-Text-Bytes deuten auf Binär
        textish = sum(32 <= b <= 126 or b in (9, 10, 13) for b in chunk)
        return (len(chunk) - textish) > max(4, 0.30 * len(chunk))
    except Exception:
        return True


def sha256_limited(path: str, limit_bytes: int) -> str | None:
    """SHA256 nur wenn Datei ≤ limit_bytes, sonst None."""
    try:
        size = os.path.getsize(path)
        if size > limit_bytes:
            return None
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


# -------------------------
# .gitignore (Lightweight)
# -------------------------
def load_gitignore_patterns(root: str) -> list[str]:
    """Lade .gitignore aus Repo-Root."""
    patterns: list[str] = []
    root_gi = os.path.join(root, ".gitignore")
    if os.path.isfile(root_gi):
        try:
            with open(root_gi, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    patterns.append(s)
        except Exception:
            pass
    return patterns


def should_exclude(
    rel_posix: str,
    is_dir: bool,
    root_patterns: list[str],
    hard_excludes: set[str],
) -> bool:
    """Prüfe ob Pfad ausgeschlossen werden soll (harte + gitignore)."""
    # Harte Excludes (Verzeichnisse, Globs)
    for hx in hard_excludes:
        if hx.endswith("/"):
            hx_dir = hx[:-1]
            parts = rel_posix.split("/")
            if hx_dir in parts:
                return True
        else:
            if fnmatch(rel_posix, hx):
                return True

    # .gitignore-Light: simple fnmatch + Verzeichnis-Segmente
    for pat in root_patterns:
        negate = pat.startswith("!")
        p = pat[1:] if negate else pat

        hit = False

        # Verzeichnis-Pattern "dir/" → trifft wenn Segment existiert
        if p.endswith("/"):
            seg = p[:-1]
            if seg and seg in rel_posix.split("/"):
                hit = True
        else:
            # Ganzpfad-Match
            if fnmatch(rel_posix, p):
                hit = True
            else:
                # Komponenten-Match (gitignore-ähnlich)
                for comp in rel_posix.split("/"):
                    if fnmatch(comp, p):
                        hit = True
                        break

        if hit and not negate:
            return True
        if hit and negate:
            return False

    return False


# -------------------------
# Tree-Rendering
# -------------------------
def render_tree(root: str, include_files: Iterable[str], max_depth: int | None) -> str:
    """
    Rendere Ordnerbaum aus Dateiliste.
    include_files: relative POSIX-Pfade.
    """
    # Baue Baumstruktur (dict-nested)
    sep = "/"
    tree: dict[str, dict] = {}

    for rel in include_files:
        parts = [p for p in rel.split(sep) if p and p != "."]
        node = tree
        for part in parts:
            node = node.setdefault(part, {})

    # DFS Render
    lines: list[str] = []

    def _walk(node: dict, prefix: str, depth: int):
        if max_depth is not None and depth > max_depth:
            return
        keys = sorted(node.keys(), key=lambda s: s.lower())
        for i, k in enumerate(keys):
            is_last = i == len(keys) - 1
            branch = "└── " if is_last else "├── "
            lines.append(prefix + branch + k)
            new_prefix = prefix + ("    " if is_last else "│   ")
            _walk(node[k], new_prefix, depth + 1)

    lines.append(".")
    _walk(tree, "", 1)
    return "\n".join(lines)


# -------------------------
# Format Helpers
# -------------------------
def human_bytes(n: int) -> str:
    """Bytes → human-readable (B, KB, MB, GB, TB)."""
    step = 1024.0
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < step:
            return f"{n:,.0f} {unit}".replace(",", " ")
        n /= step
    return f"{n:.1f} PB"
