#!/bin/bash
#
# PREFLIGHT GATE - Production Hardening
# ======================================
# Executes all 8 scanners in EXACT order with fail-fast behavior.
#
# RULES:
# 1. SEQUENTIAL execution (NO parallelism)
# 2. BLOCKING on each failure (|| exit 1)
# 3. NO steps can be skipped
# 4. EXIT CODE 1 = CI MUST break
#
# SCANNER ORDER (FIXED):
# 1. Ports & IDs Compliance    - Foundation check
# 2. Folder Coverage           - Completeness check
# 3. Secrets & Vault           - Security check
# 4. HTML Contract             - Structure check
# 5. Public Website            - Content check
# 6. Entitlements Consistency  - Logic check
# 7. API Binding               - Routing check
# 8. Preflight Gate            - Self-check
#
# Usage:
#   ./scripts/preflight.sh
#

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "================================================================"
echo "  PREFLIGHT GATE - Production Hardening"
echo "================================================================"
echo ""
echo "Project: $PROJECT_ROOT"
echo "Scanners: 8"
echo "Mode: FAIL-FAST (exit 1 on violations)"
echo ""

# Ensure artifacts directory exists
mkdir -p "$PROJECT_ROOT/artifacts/scans"

# =============================================================================
# SCANNER 1: Ports & IDs Compliance
# =============================================================================
echo "▶ [1/8] Ports & IDs Compliance Scanner"
echo "────────────────────────────────────────────────────────────────"
python3 "$SCRIPT_DIR/ports_ids_compliance_scanner.py" || exit 1
echo ""

# =============================================================================
# SCANNER 2: Folder Coverage
# =============================================================================
echo "▶ [2/8] Folder Coverage Scanner"
echo "────────────────────────────────────────────────────────────────"
python3 "$SCRIPT_DIR/folder_coverage_scanner.py" || exit 1
echo ""

# =============================================================================
# SCANNER 3: Secrets & Vault
# =============================================================================
echo "▶ [3/8] Secrets & Vault Policy Scanner"
echo "────────────────────────────────────────────────────────────────"
python3 "$SCRIPT_DIR/secrets_vault_scanner.py" || exit 1
echo ""

# =============================================================================
# SCANNER 4: HTML Contract
# =============================================================================
echo "▶ [4/8] HTML Contract Scanner"
echo "────────────────────────────────────────────────────────────────"
python3 "$SCRIPT_DIR/html_contract_scanner.py" || exit 1
echo ""

# =============================================================================
# SCANNER 5: Public Website
# =============================================================================
echo "▶ [5/8] Public Website Scanner"
echo "────────────────────────────────────────────────────────────────"
python3 "$SCRIPT_DIR/public_website_scanner.py" || exit 1
echo ""

# =============================================================================
# SCANNER 6: Entitlements Consistency
# =============================================================================
echo "▶ [6/8] Entitlements Consistency Scanner"
echo "────────────────────────────────────────────────────────────────"
python3 "$SCRIPT_DIR/entitlements_consistency_scanner.py" || exit 1
echo ""

# =============================================================================
# SCANNER 7: API Binding
# =============================================================================
echo "▶ [7/8] API Binding Scanner"
echo "────────────────────────────────────────────────────────────────"
python3 "$SCRIPT_DIR/api_binding_scanner.py" || exit 1
echo ""

# =============================================================================
# SCANNER 8: Preflight Gate (Self-Check)
# =============================================================================
echo "▶ [8/8] Preflight Gate Scanner (Self-Check)"
echo "────────────────────────────────────────────────────────────────"
python3 "$SCRIPT_DIR/preflight_gate_scanner.py" || exit 1
echo ""

# =============================================================================
# SUCCESS
# =============================================================================
echo "================================================================"
echo "✅ ALL PREFLIGHT CHECKS PASSED"
echo "================================================================"
echo ""
echo "✓ Ports & IDs:           Compliant"
echo "✓ Folder Coverage:       Complete"
echo "✓ Secrets & Vault:       Secure"
echo "✓ HTML Contract:         Valid"
echo "✓ Public Website:        Complete"
echo "✓ Entitlements:          Consistent"
echo "✓ API Binding:           Proper routing"
echo "✓ Preflight Gate:        Configured correctly"
echo ""
echo "Reports generated in: artifacts/scans/"
echo ""
echo "🚀 READY FOR DEPLOYMENT"
echo ""

exit 0
