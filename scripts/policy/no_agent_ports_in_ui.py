#!/usr/bin/env python3
import re
import subprocess
import sys


def git_staged_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    return [line for line in out.stdout.splitlines() if line.strip()]


def git_show(path):
    p = subprocess.run(["git", "show", f":{path}"], capture_output=True, text=True)
    return p.stdout


def main():
    files = git_staged_files()
    if not files:
        return 0

    targets = [f for f in files if re.search(r"^apps/.*\.html$", f)]
    if not targets:
        return 0

    bad = False
    for f in targets:
        content = git_show(f)
        if re.search(r":(123[4-9][0-9]|1239[0-9])", content):
            print(f"❌ direct agent-port link detected in {f} (must route via opena20)")
            bad = True
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
