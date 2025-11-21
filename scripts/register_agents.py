#!/usr/bin/env python3
"""
Register agents with the ELION Hyper-Dashboard.

This script registers opena1 and opena2 agents with the dashboard
by making POST requests to the /api/agent/register endpoint.

Usage:
    python3 scripts/register_agents.py
"""
import sys
import json
import os
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV = os.path.join(ROOT, ".env")
PORT_DASH = "12349"

# Check for custom port file
if os.path.exists(os.path.join(ROOT, ".runtime/port")):
    PORT_DASH = open(os.path.join(ROOT, ".runtime/port")).read().strip()


def token():
    """Read the admin token from .env file."""
    if os.path.isfile(ENV):
        # Read the first line or DASHBOARD_ADMIN_TOKEN from .env
        with open(ENV, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('DASHBOARD_ADMIN_TOKEN='):
                    return line.split('=', 1)[1]
                elif not line.startswith('#') and '=' in line and not line.startswith('TELEGRAM_') and not line.startswith('OPENAI_'):
                    # Fallback: return first non-comment token
                    return line.split('=', 1)[1]
        # If no DASHBOARD_ADMIN_TOKEN found, return first line
        with open(ENV, 'r') as f:
            first_line = f.readline().strip()
            if '=' in first_line:
                return first_line.split('=', 1)[1]
    print("No .env token", file=sys.stderr)
    sys.exit(1)


def post(path, payload):
    """Make a POST request to the dashboard API."""
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT_DASH}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token()}"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        return {"error": f"HTTP {e.code}", "details": error_body}
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return {"error": str(e)}


if __name__ == "__main__":
    print("Registering agents with ELION Hyper-Dashboard...")
    print(f"Dashboard URL: http://127.0.0.1:{PORT_DASH}")
    print()
    
    # Register opena1 (Portier/Coordinator)
    print("Registering opena1 (Portier)...")
    result1 = post("/api/agent/register", {
        "agent_id": "opena1",
        "endpoint": "http://127.0.0.1:12344"
    })
    print(json.dumps(result1, indent=2))
    print()
    
    # Register opena2 (Archivator)
    print("Registering opena2 (Archivator)...")
    result2 = post("/api/agent/register", {
        "agent_id": "opena2",
        "endpoint": "http://127.0.0.1:12345"
    })
    print(json.dumps(result2, indent=2))
    print()
    
    # Check for errors
    if "error" in result1 or "error" in result2:
        print("⚠️  Some registrations failed. Please check if services are running.", file=sys.stderr)
        sys.exit(1)
    else:
        print("✅ Agent registration complete!")
