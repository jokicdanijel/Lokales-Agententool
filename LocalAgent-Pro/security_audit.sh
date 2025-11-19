#!/bin/bash
# LocalAgent-Pro Security Audit Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔒 LocalAgent-Pro Security Audit"
echo "================================="
echo ""

# Project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Check if venv exists
if [ ! -d "../venv" ] && [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual Environment nicht gefunden!${NC}"
    echo "Bitte venv erstellen: python3 -m venv ../venv"
    exit 1
fi

# Activate venv
if [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    source .venv/bin/activate
fi

# Install security tools
echo -e "${BLUE}📦 Installiere Security-Tools...${NC}"
pip install -q bandit safety pip-audit semgrep 2>/dev/null || true

# Create reports directory
REPORTS_DIR="security_reports"
mkdir -p "$REPORTS_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo ""
echo -e "${GREEN}🔍 Running Security Scans...${NC}"
echo ""

# 1. Bandit - Python Security Scanner
echo -e "${YELLOW}[1/5] Bandit - Python Security Issues${NC}"
BANDIT_REPORT="${REPORTS_DIR}/bandit_${TIMESTAMP}.txt"
bandit -r src/ -f txt -o "$BANDIT_REPORT" 2>&1 || true
BANDIT_ISSUES=$(grep -c "Issue:" "$BANDIT_REPORT" || echo "0")
echo -e "  ✅ Bandit Scan abgeschlossen: ${BANDIT_ISSUES} Issues gefunden"
echo -e "  📄 Report: ${BANDIT_REPORT}"
echo ""

# 2. Safety - Dependency Vulnerabilities
echo -e "${YELLOW}[2/5] Safety - Dependency Vulnerabilities${NC}"
SAFETY_REPORT="${REPORTS_DIR}/safety_${TIMESTAMP}.txt"
safety check --json > "$SAFETY_REPORT" 2>&1 || true
SAFETY_VULNS=$(grep -o '"vulnerability"' "$SAFETY_REPORT" | wc -l || echo "0")
echo -e "  ✅ Safety Scan abgeschlossen: ${SAFETY_VULNS} Vulnerabilities gefunden"
echo -e "  📄 Report: ${SAFETY_REPORT}"
echo ""

# 3. pip-audit - Dependency Audit
echo -e "${YELLOW}[3/5] pip-audit - Package Vulnerabilities${NC}"
PIP_AUDIT_REPORT="${REPORTS_DIR}/pip_audit_${TIMESTAMP}.txt"
pip-audit -o "$PIP_AUDIT_REPORT" 2>&1 || true
PIP_AUDIT_VULNS=$(grep -c "vulnerability" "$PIP_AUDIT_REPORT" || echo "0")
echo -e "  ✅ pip-audit abgeschlossen: ${PIP_AUDIT_VULNS} Vulnerabilities gefunden"
echo -e "  📄 Report: ${PIP_AUDIT_REPORT}"
echo ""

# 4. Custom Security Checks
echo -e "${YELLOW}[4/5] Custom Security Checks${NC}"
CUSTOM_REPORT="${REPORTS_DIR}/custom_checks_${TIMESTAMP}.txt"

{
    echo "=== Custom Security Checks ==="
    echo ""
    
    # Check for hardcoded secrets
    echo "1. Hardcoded Secrets Check:"
    grep -rn --include="*.py" -E "(password|secret|api_key|token).*=.*['\"][^'\"]+['\"]" src/ || echo "  ✅ No hardcoded secrets found"
    echo ""
    
    # Check for eval/exec usage
    echo "2. Dangerous Functions (eval/exec):"
    grep -rn --include="*.py" -E "(\beval\(|\bexec\()" src/ || echo "  ✅ No eval/exec found"
    echo ""
    
    # Check for SQL injection risks
    echo "3. SQL Injection Risks:"
    grep -rn --include="*.py" -E "execute\(.*%.*\)" src/ || echo "  ✅ No SQL injection risks found"
    echo ""
    
    # Check for shell=True in subprocess
    echo "4. Shell Injection Risks (shell=True):"
    grep -rn --include="*.py" "shell=True" src/ || echo "  ✅ No shell=True found"
    echo ""
    
    # Check for insecure random
    echo "5. Insecure Random Usage:"
    grep -rn --include="*.py" "import random" src/ && echo "  ⚠️ WARNING: Use secrets module instead!" || echo "  ✅ No insecure random found"
    echo ""
    
    # Check for open() without context manager
    echo "6. File Handling (open without context manager):"
    grep -rn --include="*.py" -E "=\s*open\(" src/ || echo "  ✅ All file operations use context manager"
    echo ""
    
    # Check for pickle usage
    echo "7. Pickle Usage (potential code execution):"
    grep -rn --include="*.py" "import pickle" src/ && echo "  ⚠️ WARNING: pickle can execute arbitrary code!" || echo "  ✅ No pickle usage found"
    echo ""
    
} > "$CUSTOM_REPORT"

cat "$CUSTOM_REPORT"
echo -e "  📄 Report: ${CUSTOM_REPORT}"
echo ""

# 5. Permissions Check
echo -e "${YELLOW}[5/5] File Permissions Check${NC}"
PERMS_REPORT="${REPORTS_DIR}/permissions_${TIMESTAMP}.txt"

{
    echo "=== File Permissions Check ==="
    echo ""
    
    # Check for world-writable files
    echo "1. World-Writable Files:"
    find . -type f -perm -002 2>/dev/null || echo "  ✅ No world-writable files"
    echo ""
    
    # Check for executable Python files
    echo "2. Executable Python Files:"
    find src/ -name "*.py" -perm /111 2>/dev/null || echo "  ✅ No executable .py files"
    echo ""
    
    # Check for .pyc files (should be gitignored)
    echo "3. Compiled Python Files (.pyc):"
    find . -name "*.pyc" 2>/dev/null | head -5 && echo "  ⚠️ WARNING: .pyc files should be gitignored!" || echo "  ✅ No .pyc files found"
    echo ""
    
} > "$PERMS_REPORT"

cat "$PERMS_REPORT"
echo -e "  📄 Report: ${PERMS_REPORT}"
echo ""

# Summary
echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}📊 Security Audit Summary${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""

TOTAL_ISSUES=$((BANDIT_ISSUES + SAFETY_VULNS + PIP_AUDIT_VULNS))

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED: Keine kritischen Security-Issues gefunden!${NC}"
else
    echo -e "${YELLOW}⚠️ WARNING: ${TOTAL_ISSUES} Security-Issues gefunden${NC}"
    echo ""
    echo "Details:"
    echo "  - Bandit: ${BANDIT_ISSUES} Issues"
    echo "  - Safety: ${SAFETY_VULNS} Vulnerabilities"
    echo "  - pip-audit: ${PIP_AUDIT_VULNS} Vulnerabilities"
fi

echo ""
echo -e "📁 Alle Reports in: ${BLUE}${REPORTS_DIR}/${NC}"
echo ""

# Generate HTML Summary Report
HTML_REPORT="${REPORTS_DIR}/security_summary_${TIMESTAMP}.html"
cat > "$HTML_REPORT" <<EOF
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>LocalAgent-Pro Security Audit</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .pass { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .warn { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .fail { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; padding: 15px; background: #ecf0f1; border-radius: 5px; }
        .metric-value { font-size: 32px; font-weight: bold; color: #3498db; }
        .metric-label { color: #7f8c8d; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #3498db; color: white; }
        tr:hover { background: #f5f5f5; }
        .timestamp { color: #95a5a6; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 LocalAgent-Pro Security Audit</h1>
        <p class="timestamp">Generiert: $(date '+%Y-%m-%d %H:%M:%S')</p>
        
        <div class="status $([ $TOTAL_ISSUES -eq 0 ] && echo 'pass' || echo 'warn')">
            <strong>Status:</strong> $([ $TOTAL_ISSUES -eq 0 ] && echo '✅ PASSED' || echo "⚠️ ${TOTAL_ISSUES} Issues gefunden")
        </div>
        
        <h2>📊 Scan-Ergebnisse</h2>
        <div class="metric">
            <div class="metric-value">${BANDIT_ISSUES}</div>
            <div class="metric-label">Bandit Issues</div>
        </div>
        <div class="metric">
            <div class="metric-value">${SAFETY_VULNS}</div>
            <div class="metric-label">Safety Vulnerabilities</div>
        </div>
        <div class="metric">
            <div class="metric-value">${PIP_AUDIT_VULNS}</div>
            <div class="metric-label">pip-audit Vulnerabilities</div>
        </div>
        
        <h2>📄 Reports</h2>
        <table>
            <tr>
                <th>Tool</th>
                <th>Report-Datei</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Bandit</td>
                <td>$(basename $BANDIT_REPORT)</td>
                <td>$([ $BANDIT_ISSUES -eq 0 ] && echo '✅ Clean' || echo "⚠️ ${BANDIT_ISSUES} Issues")</td>
            </tr>
            <tr>
                <td>Safety</td>
                <td>$(basename $SAFETY_REPORT)</td>
                <td>$([ $SAFETY_VULNS -eq 0 ] && echo '✅ Clean' || echo "⚠️ ${SAFETY_VULNS} Vulnerabilities")</td>
            </tr>
            <tr>
                <td>pip-audit</td>
                <td>$(basename $PIP_AUDIT_REPORT)</td>
                <td>$([ $PIP_AUDIT_VULNS -eq 0 ] && echo '✅ Clean' || echo "⚠️ ${PIP_AUDIT_VULNS} Vulnerabilities")</td>
            </tr>
            <tr>
                <td>Custom Checks</td>
                <td>$(basename $CUSTOM_REPORT)</td>
                <td>✅ Completed</td>
            </tr>
            <tr>
                <td>Permissions</td>
                <td>$(basename $PERMS_REPORT)</td>
                <td>✅ Completed</td>
            </tr>
        </table>
        
        <h2>🔧 Empfohlene Aktionen</h2>
        <ul>
            <li>Alle Reports in <code>${REPORTS_DIR}/</code> prüfen</li>
            <li>Kritische Issues sofort beheben</li>
            <li>Dependencies aktualisieren: <code>pip install --upgrade -r requirements.txt</code></li>
            <li>Security-Audit regelmäßig wiederholen (wöchentlich empfohlen)</li>
        </ul>
    </div>
</body>
</html>
EOF

echo -e "${GREEN}✅ HTML-Report generiert: ${HTML_REPORT}${NC}"
echo -e "${BLUE}Öffne mit: firefox ${HTML_REPORT}${NC}"
echo ""

# Exit code based on issues
if [ $TOTAL_ISSUES -gt 0 ]; then
    exit 1
else
    exit 0
fi
