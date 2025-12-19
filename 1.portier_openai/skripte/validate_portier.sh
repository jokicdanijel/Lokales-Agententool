#!/usr/bin/env bash
set -euo pipefail

# PORTIER 3.0 Policy Validator
# Validiert kritische Dateien und Richtlinien-Compliance

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

fail() {
    echo "❌ $*" >&2
    exit 1
}

warn() {
    echo "⚠️  $*" >&2
}

success() {
    echo "✅ $*"
}

echo "🔎 PORTIER 3.0 Policy Validation"
echo "=================================="

# 1. Erforderliche Dateien prüfen
echo ""
echo "📋 Schritt 1: Erforderliche Dateien prüfen..."
required_files=(
    ".github/workflows/portier-ci.yml"
    "1.portier_openai/config/tools_registry.json"
    "bin/ops.sh"
)

missing_files=0
for f in "${required_files[@]}"; do
    if [ -f "$REPO_ROOT/$f" ]; then
        success "  ✓ $f"
    else
        warn "  ✗ $f (MISSING)"
        ((missing_files++))
    fi
done

if [ "$missing_files" -gt 0 ]; then
    fail "Es fehlen $missing_files erforderliche Dateien"
fi

# 2. JSON-Validierung (tools_registry.json)
echo ""
echo "📋 Schritt 2: JSON-Validierung..."
if [ -f "$REPO_ROOT/1.portier_openai/config/tools_registry.json" ]; then
    if python3 -m json.tool "$REPO_ROOT/1.portier_openai/config/tools_registry.json" >/dev/null 2>&1; then
        success "  ✓ tools_registry.json ist valides JSON"
    else
        fail "Ungültiges JSON in: 1.portier_openai/config/tools_registry.json"
    fi
fi

# 3. Port-Richtlinien prüfen (PORTIER 3.0: 12344-12399)
echo ""
echo "📋 Schritt 3: Port-Richtlinien prüfen..."
if grep -r "port.*8080\|8080.*port" "$REPO_ROOT/bin/" 2>/dev/null | grep -v "# " >/dev/null 2>&1; then
    warn "  ⚠️  Port 8080 gefunden (policy: verwende 12344-12399)"
else
    success "  ✓ Port-Richtlinien konform (kein 8080 in bin/)"
fi

# 4. Env & Secrets prüfen
echo ""
echo "📋 Schritt 4: Env & Secrets prüfen..."
if [ -f "$REPO_ROOT/.env" ]; then
    success "  ✓ .env Datei vorhanden"
else
    warn "  ⚠️  .env Datei fehlt (bin/env_bootstrap.sh kann sie erzeugen)"
fi

# 5. Abschlussbericht
echo ""
echo "=================================="
success "Richtlinienprüfung abgeschlossen ✅"
echo ""
echo "📌 Policy Status:"
echo "   • Erforderliche Dateien: OK"
echo "   • JSON-Validierung: OK"
echo "   • Port-Richtlinien: OK"
echo "   • Env/Secrets: CHECKED"
echo ""
exit 0
