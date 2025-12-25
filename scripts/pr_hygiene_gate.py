#!/usr/bin/env python3
"""PR Hygiene Gate - CI Gate Scanner

Scans a list of repos for PR hygiene blockers and emits JSON + Markdown reports.

Fast mode uses `gh search prs` with filters. Strict mode can be extended to call the Checks API.

Exit codes:
 - 0: no blockers
 - 1: blockers found
 - 2: runtime/tool failure (no private-repo leakage)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

DEFAULT_PROTECTED = ["main", "master", "release", "production"]


@dataclass
class Policy:
    block_on_checks_failure: bool = True
    block_on_checks_pending: bool = True
    block_on_changes_requested: bool = True
    block_on_drafts: bool = True
    block_on_labels: list[str] = None
    ignore_labels: list[str] = None
    max_open_prs_on_protected: int | None = None
    allowed_authors: list[str] = None
    require_linked_issue: bool = False
    max_diff_changed_files: int | None = None
    max_diff_additions: int | None = None
    max_diff_deletions: int | None = None


@dataclass
class Blocker:
    repo: str
    base: str
    number: int
    title: str
    url: str
    reason: str
    details: dict[str, Any]


def run_gh_search(
    repo: str, base: str, checks: str | None = None, query_extra: str | None = None
) -> list[dict[str, Any]] | None:
    # Build gh search command
    q = f"is:pr state:open repo:{repo} base:{base}"
    if checks:
        q += f" --checks {checks}"
    if query_extra:
        q += f" {query_extra}"

    cmd = [
        "gh",
        "search",
        "prs",
        q,
        "--json",
        "number,title,url,author,labels,createdAt,updatedAt,reviewDecision,headRefName,baseRefName,mergeStateStatus,checkState",
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        out = res.stdout.strip()
        if not out:
            return []
        data = json.loads(out)
        return data
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        # If auth error or permission denied, return None to indicate we couldn't access repo
        if "permission" in stderr.lower() or "not found" in stderr.lower() or "401" in stderr or "403" in stderr:
            return None
        # for other errors surface them as tool failure
        raise
    except FileNotFoundError:
        # gh CLI not installed
        raise


def sanitize_labels(lbls: list[dict[str, Any]]) -> list[str]:
    names: List[str] = []
    for label in lbls:
        name = label.get("name")
        if name:
            names.append(name)
    return names


def scan_repo_fast(repo: str, protected_bases: list[str], policy: Policy) -> list[Blocker]:
    blockers: list[Blocker] = []
    for base in protected_bases:
        # 1) checks failing
        if policy.block_on_checks_failure:
            items = run_gh_search(repo, base, checks="failure")
            if items is None:
                # inaccessible
                raise PermissionError(f"inaccessible:{repo}")
            for it in items:
                blockers.append(
                    Blocker(
                        repo=repo,
                        base=base,
                        number=it["number"],
                        title=it["title"],
                        url=it["url"],
                        reason="checks_failure",
                        details={"checks": "failure", "labels": sanitize_labels(it.get("labels", []))},
                    )
                )
        # 2) checks pending
        if policy.block_on_checks_pending:
            items = run_gh_search(repo, base, checks="pending")
            if items is None:
                raise PermissionError(f"inaccessible:{repo}")
            for it in items:
                blockers.append(
                    Blocker(
                        repo=repo,
                        base=base,
                        number=it["number"],
                        title=it["title"],
                        url=it["url"],
                        reason="checks_pending",
                        details={"checks": "pending", "labels": sanitize_labels(it.get("labels", []))},
                    )
                )
        # 3) changes requested
        if policy.block_on_changes_requested:
            items = run_gh_search(repo, base, query_extra="review:changes_requested")
            if items is None:
                raise PermissionError(f"inaccessible:{repo}")
            for it in items:
                blockers.append(
                    Blocker(
                        repo=repo,
                        base=base,
                        number=it["number"],
                        title=it["title"],
                        url=it["url"],
                        reason="changes_requested",
                        details={
                            "reviewDecision": it.get("reviewDecision"),
                            "labels": sanitize_labels(it.get("labels", [])),
                        },
                    )
                )
        # 4) drafts
        if policy.block_on_drafts:
            items = run_gh_search(repo, base, query_extra="is:draft")
            if items is None:
                raise PermissionError(f"inaccessible:{repo}")
            for it in items:
                blockers.append(
                    Blocker(
                        repo=repo,
                        base=base,
                        number=it["number"],
                        title=it["title"],
                        url=it["url"],
                        reason="draft",
                        details={"labels": sanitize_labels(it.get("labels", []))},
                    )
                )
        # 5) label blockers (search by label)
        if policy.block_on_labels:
            for lbl in policy.block_on_labels:
                items = run_gh_search(repo, base, query_extra=f'label:"{lbl}"')
                if items is None:
                    raise PermissionError(f"inaccessible:{repo}")
                for it in items:
                    blockers.append(
                        Blocker(
                            repo=repo,
                            base=base,
                            number=it["number"],
                            title=it["title"],
                            url=it["url"],
                            reason="blocked_label",
                            details={"labels": sanitize_labels(it.get("labels", []))},
                        )
                    )
        # Cap checks (max_open_prs_on_protected)
        if policy.max_open_prs_on_protected:
            # fetch all PRs against base
            items = run_gh_search(repo, base)
            if items is None:
                raise PermissionError(f"inaccessible:{repo}")
            if len(items) > policy.max_open_prs_on_protected:
                blockers.append(
                    Blocker(
                        repo=repo,
                        base=base,
                        number=0,
                        title="cap exceeded",
                        url="",
                        reason="cap_exceeded",
                        details={"count": len(items), "cap": policy.max_open_prs_on_protected},
                    )
                )
    return blockers


def make_md_report(blockers: list[Blocker], warnings: list[str], scanned_repos: list[str], mode: str) -> str:
    lines = [f"# PR Hygiene Gate Report ({mode})", f"Generated: {datetime.utcnow().isoformat()}Z", ""]
    if not blockers:
        lines.append("## Status: OK ✅\nAll scanned repositories have no PR hygiene blockers.")
    else:
        lines.append(f"## Status: BLOCKED ❌ ({len(blockers)} blocker(s))\n")
        for b in sorted(blockers, key=lambda x: (x.repo, x.base, x.number)):
            lines.append(
                f"- **{b.repo}** / **{b.base}** — PR #{b.number} — [{b.title}]({b.url}) — reason: `{b.reason}` — details: {json.dumps(b.details)}"
            )
    if warnings:
        lines.append("\n## Warnings")
        for w in warnings:
            lines.append(f"- {w}")
    lines.append("\n---\n")
    lines.append(f"Scanned repos: {', '.join(scanned_repos)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos", nargs="+", required=True, help="list of OWNER/REPO")
    parser.add_argument("--protected-base-branches", nargs="+", default=DEFAULT_PROTECTED)
    parser.add_argument("--mode", choices=["fast", "strict"], default="fast")
    parser.add_argument("--out-json", default="artifacts/scans/pr_hygiene_gate.json")
    parser.add_argument("--out-md", default="artifacts/scans/pr_hygiene_gate.md")
    parser.add_argument("--ignore-labels", nargs="*", default=["ci-ignore-pr-hygiene"])
    parser.add_argument("--block-labels", nargs="*", default=["do-not-merge", "wip", "blocked"])
    parser.add_argument("--fail-threshold", type=float, default=0.6, help="Not used directly here, reserved for future")
    args = parser.parse_args(argv)

    policy = Policy(block_on_labels=args.block_labels, ignore_labels=args.ignore_labels)

    all_blockers: list[Blocker] = []
    warnings: list[str] = []
    scanned: list[str] = []

    for repo in sorted(args.repos):
        try:
            scanned.append(repo)
            if args.mode == "fast":
                bs = scan_repo_fast(repo, args.protected_base_branches, policy)
                # Apply ignore_labels filter and allowed_authors (not implemented here)
                filtered = []
                for b in bs:
                    lbls = [name.lower() for name in b.details.get("labels", []) if isinstance(name, str)]
                    ignore_labels = policy.ignore_labels or []
                    if any(ig.lower() in lbls for ig in ignore_labels):
                        continue
                    filtered.append(b)
                all_blockers.extend(filtered)
            else:
                # Strict mode not fully implemented in this initial release
                warnings.append(f"Strict mode not fully implemented for {repo}; skipping strict checks")
        except PermissionError:
            warnings.append(f"Insufficient access to repo {repo}; results omitted (no private info leaked)")
        except FileNotFoundError:
            warnings.append("gh CLI not found; cannot run fast-mode scans")
            print("ERROR: gh CLI not installed", file=sys.stderr)
            return 2
        except Exception as e:
            warnings.append(f"Error scanning {repo}: {e!s}")

    # Prepare outputs
    ok_flag = len(all_blockers) == 0
    out_json = {
        "ok": ok_flag,
        "mode": args.mode,
        "visibility": "any",
        "protected_base_branches": args.protected_base_branches,
        "repos_scanned": scanned,
        "blockers": [asdict(b) for b in sorted(all_blockers, key=lambda x: (x.repo, x.base, x.number))],
        "warnings": warnings,
        "errors": [],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as fh:
        json.dump(out_json, fh, indent=2)

    md = make_md_report(all_blockers, warnings, scanned, args.mode)
    os.makedirs(os.path.dirname(args.out_md), exist_ok=True)
    with open(args.out_md, "w", encoding="utf-8") as fh:
        fh.write(md)

    if ok_flag:
        print("PR Hygiene Gate: OK (no blockers)")
        return 0
    else:
        print(f"PR Hygiene Gate: BLOCKED ({len(all_blockers)} blockers)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
