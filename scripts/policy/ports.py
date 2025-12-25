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

    targets = [f for f in files if re.search(r"^(docker-compose.*\.ya?ml|infrastructure/nginx/.*\.conf)$", f)]
    if not targets:
        return 0

    bad = False
    for f in targets:
        content = git_show(f)
        if re.search(r"(^|[^0-9])8080(:|[^0-9])", content):
            print(f"❌ Forbidden port 8080 detected in {f}")
            bad = True
        for line in content.splitlines():
            m = re.search(r"^- *\"?([0-9]{2,5}):([0-9]{2,5})", line)
            if m:
                host = int(m.group(1))
                if host < 12344 or host > 12399:
                    print(f"❌ Host port out of range (12344-12399): {host} in {f}")
                    bad = True
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
