#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV = os.path.join(ROOT, ".env")
PORT_DASH = "12349"
if os.path.exists(os.path.join(ROOT, ".runtime/port")):
    PORT_DASH = open(os.path.join(ROOT, ".runtime/port")).read().strip()


def token():
    if os.path.isfile(ENV):
        return open(ENV).read().strip()
    print("No .env token", file=sys.stderr)
    sys.exit(1)


def post(path, payload):
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT_DASH}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token()}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


if __name__ == "__main__":
    print(post("/api/agent/register", {"agent_id": "opena1", "endpoint": "http://127.0.0.1:12344"}))
    print(post("/api/agent/register", {"agent_id": "opena2", "endpoint": "http://127.0.0.1:12345"}))
