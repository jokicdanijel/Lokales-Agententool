#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

fail() { echo "❌ $*" >&2; exit 1; }

# Required files
required=(
    ".github/workflows/portier-ci.yml"
    "1.opena1&2_portier/opena1_app.py"
    "1.opena1&2_portier/opena2_app.py"
)

echo "🔎 Policy validation running..."
for f in "${required[@]}"; do
    if [ ! -f "$REPO_ROOT/$f" ]; then
        fail "Missing required file: $f"
    fi
done

# Validate JSON if tools_registry exists
if [ -f "$REPO_ROOT/1.opena1&2_portier/config/tools_registry.json" ]; then
    if ! python3 -m json.tool "$REPO_ROOT/1.opena1&2_portier/config/tools_registry.json" >/dev/null 2>&1; then
        fail "Invalid JSON: 1.opena1&2_portier/config/tools_registry.json"
    fi
fi

echo "✅ Policy checks passed."
exit 0
