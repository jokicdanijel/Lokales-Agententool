#!/usr/bin/env python3
"""
fix_agent_structure.py

Deterministischer Strukturfikser für PORTIER 3.0
- Dry-run (Standard): listet vorgeschlagene Moves auf
- --apply: führt Moves aus via `git mv`, erstellt Branch + Commit und pusht

Designprinzipien:
- Read-only Analyse bis --apply
- Deterministisch, stable sorting
- Keine Überschreibungen ohne Explizitentscheidung (bei Namenskonflikt: suffix .orig)
- Audit-Artifact: artifacts/Agent_structure_fix_proposal.json (dry-run) oder artifacts/Agent_structure_fix_result.json (apply)

Usage:
  python3 scripts/fix_agent_structure.py       # dry-run
  python3 scripts/fix_agent_structure.py --apply --branch chore/fix-agent-structure-20251226 --yes

"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "system_baseline.yaml"
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
PROPOSAL_PATH = ARTIFACTS / "Agent_structure_fix_proposal.json"
RESULT_PATH = ARTIFACTS / "Agent_structure_fix_result.json"

# heuristic patterns
NON_VISIBLE_DIRS = {".git", ".github", "node_modules", "dist", "build", "artifacts"}


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    p = subprocess.Popen(cmd, cwd=(cwd or ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out.strip(), err.strip()


def load_baseline() -> dict[str, Any]:
    try:
        import yaml
    except Exception:
        print("FEHLER: Missing dependency 'pyyaml'. Install: pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    if not BASELINE.exists():
        print(f"FEHLER: Missing baseline: {BASELINE}", file=sys.stderr)
        sys.exit(1)
    raw = BASELINE.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        print("FEHLER: baseline is not a dict", file=sys.stderr)
        sys.exit(1)
    return data


@dataclass
class MoveOp:
    src: str
    dst: str
    reason: str


def find_candidate_paths(agent_id: str, folder_path: str, agent_name: str | None) -> list[Path]:
    # search for directories or files that look like they belong to this agent
    candidates: list[Path] = []
    target_basename = Path(folder_path).name.lower()
    tokens = [agent_id.lower()]
    if agent_name:
        tokens += [re.sub(r"[^a-z0-9]+", "_", agent_name.lower())]
    tokens.append(target_basename)

    for p in sorted(ROOT.rglob("*")):
        try:
            if any(part in NON_VISIBLE_DIRS for part in p.parts):
                continue
        except Exception:
            continue
        lname = p.name.lower()
        lower = str(p).lower()
        # prefer directories that match folder name or agent id or agent name
        if p.is_dir():
            if any(t in lower for t in tokens):
                # skip if it's the exact desired path
                if str(p.resolve()) == str((ROOT / folder_path).resolve()):
                    continue
                candidates.append(p)
        else:
            # files: if name contains tokens, consider parent dir as candidate
            if any(t in lname for t in tokens):
                candidates.append(p.parent)
    # deduplicate and keep unique
    uniq = []
    seen = set()
    for c in candidates:
        r = str(c.resolve())
        if r not in seen:
            seen.add(r)
            uniq.append(c)
    return uniq


def propose_moves(baseline: dict[str, Any]) -> dict[str, Any]:
    agents = baseline.get("agents") or []
    proposals: list[dict[str, Any]] = []

    for a in sorted(agents, key=lambda x: str(x.get("id", ""))):
        aid = str(a.get("id", "")).strip()
        folder = str(a.get("folder_path", "")).strip()
        name = str(a.get("name", "")).strip() if a.get("name") else None
        if not folder:
            proposals.append({"id": aid, "issue": "missing folder_path in baseline"})
            continue
        expected = ROOT / folder
        if expected.exists() and any(expected.iterdir()):
            # exists and non-empty -> nothing to do
            continue
        # find candidates to move
        cand = find_candidate_paths(aid, folder, name)
        if not cand:
            proposals.append({"id": aid, "status": "no_candidates_found", "expected": folder})
            continue
        # propose moving the first candidate (best) into expected
        ops = []
        for c in cand:
            # if candidate is a dir, propose move entire dir into expected
            rel = c.relative_to(ROOT).as_posix()
            ops.append({"src": rel, "dst": folder, "type": "move_dir", "reason": f"matched tokens for {aid}"})
        proposals.append({"id": aid, "expected": folder, "candidates": ops})
    return {
        "timestamp_utc": utc_now(),
        "repo_root": str(ROOT),
        "proposals": proposals,
    }


def apply_moves(proposals: dict[str, Any], branch: str, auto_yes: bool = False) -> dict[str, Any]:
    # create branch
    code, out, err = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if code != 0:
        raise SystemError("git not available or not a repo")
    # create branch
    code, out, err = run(["git", "checkout", "-b", branch])
    if code != 0:
        raise SystemError(f"failed to create branch {branch}: {err}")

    applied: list[dict[str, Any]] = []
    errors: list[str] = []

    for p in proposals.get("proposals", []):
        if p.get("candidates"):
            for c in p["candidates"]:
                src = ROOT / c["src"]
                dst = ROOT / p["expected"]
                try:
                    dst_parent = dst.parent
                    dst_parent.mkdir(parents=True, exist_ok=True)
                    if dst.exists():
                        # move contents into dst
                        # avoid overwriting: for each file, if exists, suffix with .orig
                        if src.is_dir():
                            # move each child into dst
                            for child in sorted(src.iterdir()):
                                target = dst / child.name
                                if target.exists():
                                    target = Path(str(target) + ".orig")
                                run(["git", "mv", str(child), str(target)])
                        else:
                            target = dst / src.name
                            if target.exists():
                                target = Path(str(target) + ".orig")
                            run(["git", "mv", str(src), str(target)])
                        # remove empty src dir if possible
                        try:
                            if src.is_dir() and not any(src.iterdir()):
                                run(["git", "rm", "-r", "--ignore-unmatch", str(src)])
                        except Exception:
                            pass
                        applied.append({"src": c["src"], "dst": p["expected"], "status": "moved"})
                    else:
                        # move dir to dst
                        dst_parent.mkdir(parents=True, exist_ok=True)
                        run(["git", "mv", str(src), str(dst)])
                        applied.append({"src": c["src"], "dst": p["expected"], "status": "moved_dir"})
                except Exception as e:
                    errors.append(f"failed to move {c['src']} -> {p['expected']}: {e}")
    # commit
    try:
        run(["git", "add", "-A"])
        run(["git", "commit", "-m", "chore(fixer): move misplaced agent files into baseline paths"])
        run(["git", "push", "-u", "origin", branch])
    except Exception as e:
        errors.append(f"commit/push failed: {e}")
    return {
        "timestamp_utc": utc_now(),
        "applied": applied,
        "errors": errors,
        "branch": branch,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply", action="store_true", help="Apply the proposed moves via git mv and commit to a branch"
    )
    parser.add_argument("--branch", default=f"chore/fix-agent-structure-{datetime.now().strftime('%Y%m%d')}")
    parser.add_argument("--yes", action="store_true", help="Auto-confirm applying changes")
    args = parser.parse_args()

    baseline = load_baseline()
    proposal = propose_moves(baseline)
    PROPOSAL_PATH.write_text(json.dumps(proposal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Proposal written: {PROPOSAL_PATH}")

    # Pretty print summary
    total = 0
    for p in proposal["proposals"]:
        if p.get("candidates"):
            total += len(p["candidates"])
    if total == 0:
        print("No candidates found for any missing agent folders. Nothing to do.")
        sys.exit(0)

    print(f"Found {total} candidate moves. Details in {PROPOSAL_PATH}")

    if not args.apply:
        print("DRY-RUN only. Run with --apply --branch <name> --yes to perform moves and commit them.")
        sys.exit(0)

    if not args.yes:
        confirm = input(f"Apply {total} moves and commit on branch {args.branch}? [y/N]: ")
        if confirm.lower() != "y":
            print("ABORTED")
            sys.exit(2)

    result = apply_moves(proposal, args.branch, auto_yes=args.yes)
    RESULT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Apply result written: {RESULT_PATH}")
    if result.get("errors"):
        print("Completed with errors:")
        for e in result["errors"]:
            print(f"- {e}")
        sys.exit(1)
    print("All moves applied and pushed. Please open a PR for review.")


if __name__ == "__main__":
    main()
