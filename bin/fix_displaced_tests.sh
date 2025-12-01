#!/usr/bin/env bash
# Fix 5 displaced tests from _conflicts/ to 19.opena20_dashboard_agent/tests/

set -euo pipefail

PROJECT_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
CONFLICTS_DIR="$PROJECT_ROOT/_conflicts/2025-11-09_032949"
TARGET_DIR="$PROJECT_ROOT/19.opena20_dashboard_agent/tests"

echo "🔧 Fixing displaced tests..."
echo ""

# Create target directory if not exists
mkdir -p "$TARGET_DIR"

# Move 4 displaced tests (test_jwt_auth.py not found)
TESTS=(
    "test_phase5.py"
    "test_openwebui.py"
    "test_agent.py"
    "test_phase_4_agents.py"
)

MOVED=0
FAILED=0

for test in "${TESTS[@]}"; do
    SOURCE="$CONFLICTS_DIR/$test"
    if [ -f "$SOURCE" ]; then
        echo "✅ Moving $test..."
        mv "$SOURCE" "$TARGET_DIR/"
        ((MOVED++))
    else
        echo "❌ File not found: $test"
        ((FAILED++))
    fi
done

echo ""
echo "📊 Summary:"
echo "  Moved: $MOVED"
echo "  Failed: $FAILED"
echo ""

if [ $MOVED -gt 0 ]; then
    echo "✅ Tests successfully moved to $TARGET_DIR"
else
    echo "⚠️  No tests were moved"
fi
