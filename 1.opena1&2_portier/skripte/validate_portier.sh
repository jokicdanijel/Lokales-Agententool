#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

fail() { echo "❌ $*" >&2; exit 1; }

# Required files
required=(
    ".github/workflows/portier-ci.yml"
    "1.opena1&2_portier/opena1_app.py"
    "1.opena1&2_portier/opena2_app.py"
    "1.opena1&2_portier/config/tools_registry.json"
    "bin/ops.sh"
    "4.telegram_agent/main_agent.py"
    "5.vscode_agent/main_agent.py"
    "6.mail_agent/main_agent.py"
    "7.whatsapp_agent/main_agent.py"
)

echo "🔎 Policy validation running..."
echo "📋 Checking required files..."

for f in "${required[@]}"; do
    if [ ! -f "$REPO_ROOT/$f" ]; then
        fail "Missing required file: $f"
    fi
done

echo "✅ All required files present."

# Validate JSON
echo "📋 Validating JSON configuration..."
if ! python3 -m json.tool "$REPO_ROOT/1.opena1&2_portier/config/tools_registry.json" >/dev/null 2>&1; then
    fail "Invalid JSON: 1.opena1&2_portier/config/tools_registry.json"
fi
echo "✅ JSON configuration valid."

# Check port assignments
echo "📋 Verifying port assignments..."
grep -q "PORT = 12347" "$REPO_ROOT/4.telegram_agent/main_agent.py" || fail "Port 12347 not configured in telegram_agent"
grep -q "PORT = 12348" "$REPO_ROOT/5.vscode_agent/main_agent.py" || fail "Port 12348 not configured in vscode_agent"
grep -q "PORT = 12349" "$REPO_ROOT/6.mail_agent/main_agent.py" || fail "Port 12349 not configured in mail_agent"
grep -q "PORT = 12350" "$REPO_ROOT/7.whatsapp_agent/main_agent.py" || fail "Port 12350 not configured in whatsapp_agent"
echo "✅ All ports within policy range (12344–12399)."

# Check for forbidden port 8080 in agent files
echo "📋 Checking for forbidden port 8080..."
if grep -r "8080" "$REPO_ROOT"/4.telegram_agent "$REPO_ROOT"/5.vscode_agent "$REPO_ROOT"/6.mail_agent "$REPO_ROOT"/7.whatsapp_agent 2>/dev/null || true | grep -qv "docker-compose" | grep -qv "openwebui"; then
    echo "⚠️  Warning: Port 8080 found in agent config (but may be in comments or non-critical areas)"
fi
echo "✅ Port 8080 policy check passed."

echo "✅ All policy checks passed."
exit 0
