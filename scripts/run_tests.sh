#!/usr/bin/env bash
# ============================================================================
# run_tests.sh - Test Automation Script
# ============================================================================
# Runs pytest with coverage according to pyproject.toml settings
# Usage: ./scripts/run_tests.sh [pytest-args]
# ============================================================================

set -euo pipefail

# Colors
BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Run 'make venv' first.${RESET}"
    exit 1
fi

# Check if pytest is installed
if ! .venv/bin/python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}⚠ pytest not found. Installing test dependencies...${RESET}"
    .venv/bin/pip install pytest pytest-cov pytest-asyncio pytest-mock >/dev/null 2>&1 || {
        echo -e "${RED}❌ Failed to install pytest${RESET}"
        exit 1
    }
fi

echo -e "${BOLD}Running tests with coverage...${RESET}"
echo -e "${YELLOW}Configuration from pyproject.toml:${RESET}"
echo -e "  Coverage target: ${GREEN}src${RESET}"
echo -e "  Minimum coverage: ${GREEN}85%${RESET}"
echo -e "  Test paths: ${GREEN}tests/${RESET}"
echo ""

# Run pytest with any additional arguments passed to script
# Configuration is read from pyproject.toml [tool.pytest.ini_options]
.venv/bin/pytest "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${RESET}"
    echo -e "${YELLOW}Coverage report: htmlcov/index.html${RESET}"
else
    echo ""
    echo -e "${RED}❌ Tests failed or coverage below threshold${RESET}"
fi

exit $exit_code
