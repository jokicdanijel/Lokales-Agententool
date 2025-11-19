#!/bin/bash
# Run LocalAgent-Pro Test Suite

set -e

echo "🧪 LocalAgent-Pro Test Suite Runner"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to project directory
cd "$(dirname "$0")"

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated!${NC}"
    echo "Activating venv..."
    source ../venv/bin/activate || source .venv/bin/activate || {
        echo -e "${RED}❌ Could not activate virtual environment${NC}"
        exit 1
    }
fi

# Install test dependencies
echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
pip install -q -r requirements-dev.txt

# Run tests based on argument
case "${1:-all}" in
    "unit")
        echo -e "${GREEN}🧪 Running Unit Tests...${NC}"
        pytest tests/unit/ -v --tb=short --cov=src --cov-report=html --cov-report=term-missing
        ;;
    
    "integration")
        echo -e "${GREEN}🔗 Running Integration Tests...${NC}"
        pytest tests/integration/ -v --tb=short
        ;;
    
    "security")
        echo -e "${GREEN}🔒 Running Security Tests...${NC}"
        pytest -m security -v --tb=short
        ;;
    
    "fast")
        echo -e "${GREEN}⚡ Running Fast Tests (excluding slow)...${NC}"
        pytest -m "not slow" -v --tb=short --cov=src --cov-report=term-missing
        ;;
    
    "coverage")
        echo -e "${GREEN}📊 Running Tests with Full Coverage Report...${NC}"
        pytest tests/ -v --cov=src --cov-report=html --cov-report=xml --cov-report=term-missing
        echo -e "${GREEN}✅ Coverage report generated: htmlcov/index.html${NC}"
        ;;
    
    "all")
        echo -e "${GREEN}🚀 Running ALL Tests...${NC}"
        pytest tests/ -v --tb=short --cov=src --cov-report=html --cov-report=term-missing
        ;;
    
    *)
        echo -e "${RED}❌ Unknown test type: $1${NC}"
        echo "Usage: $0 [unit|integration|security|fast|coverage|all]"
        exit 1
        ;;
esac

# Test exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi
