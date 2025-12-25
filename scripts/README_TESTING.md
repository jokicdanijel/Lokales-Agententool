# Test Automation

This directory contains automation scripts for running tests with coverage.

## Quick Start

```bash
# Run all tests with coverage
make test

# Run tests with verbose output
make test-verbose

# Run tests without coverage (faster)
make test-fast

# Generate HTML coverage report
make coverage
```

## Test Script

### `run_tests.sh`

Automated test runner that uses the coverage settings from `pyproject.toml`.

**Configuration (from pyproject.toml):**
- Coverage source: `src/` directory only
- Minimum threshold: 85%
- Test discovery: `test_*.py` and `*_test.py` patterns
- Test path: `tests/` directory

**Usage:**
```bash
# Basic usage
./scripts/run_tests.sh

# With additional pytest arguments
./scripts/run_tests.sh -v
./scripts/run_tests.sh -k "test_specific"
./scripts/run_tests.sh --no-cov  # Skip coverage
./scripts/run_tests.sh -x  # Stop on first failure
```

**Features:**
- ✅ Automatically checks for virtual environment
- ✅ Installs pytest if missing
- ✅ Reads configuration from pyproject.toml
- ✅ Color-coded output
- ✅ Generates HTML coverage report in `htmlcov/`

## Coverage Requirements

As documented in `.github/copilot-instructions.md`, this project requires:
- **Minimum 85% code coverage** for production code in `src/`
- Coverage reports must be generated for all test runs
- Tests must pass before merging PRs

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_*.py                # Unit tests
├── *_test.py                # Alternative test pattern
└── test_*.sh                # Shell-based tests
```

## Coverage Reports

After running tests, coverage reports are available:
- **Terminal:** Summary printed to stdout
- **HTML:** Open `htmlcov/index.html` in browser for detailed report

## CI/CD Integration

The GitHub Actions workflows in `.github/workflows/` run tests automatically on:
- Pull request creation/updates
- Push to main branch
- Manual workflow dispatch

See `.github/workflows/ci.yml` for the CI test configuration.
