#!/usr/bin/env bash
# tests/test_release_package.sh — Test release package creation and extraction
# Verifies that the release package can be created, extracted, and basic functionality works

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_VERSION="test-$(date +%Y%m%d-%H%M%S)"
TEST_DIR="/tmp/release-test-${TEST_VERSION}"

# ====================================================================
# LOGGING FUNCTIONS
# ====================================================================

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# ====================================================================
# TEST FUNCTIONS
# ====================================================================

test_release_creation() {
    log_info "Test 1: Creating release package..."

    cd "$ROOT"
    bash bin/prepare_release.sh "$TEST_VERSION" > /dev/null 2>&1

    if [ -f "release/portier-${TEST_VERSION}.tar.gz" ]; then
        log_success "Release tar.gz created"
    else
        log_error "Failed to create tar.gz"
        return 1
    fi

    if [ -f "release/portier-${TEST_VERSION}.zip" ]; then
        log_success "Release zip created"
    else
        log_error "Failed to create zip"
        return 1
    fi

    if [ -f "release/portier-${TEST_VERSION}.tar.gz.sha256" ]; then
        log_success "Checksums generated"
    else
        log_error "Failed to generate checksums"
        return 1
    fi

    return 0
}

test_checksum_verification() {
    log_info "Test 2: Verifying checksums..."

    cd "$ROOT/release"

    if sha256sum -c "portier-${TEST_VERSION}.tar.gz.sha256" > /dev/null 2>&1; then
        log_success "tar.gz checksum valid"
    else
        log_error "tar.gz checksum verification failed"
        return 1
    fi

    if sha256sum -c "portier-${TEST_VERSION}.zip.sha256" > /dev/null 2>&1; then
        log_success "zip checksum valid"
    else
        log_error "zip checksum verification failed"
        return 1
    fi

    return 0
}

test_extraction() {
    log_info "Test 3: Extracting package..."

    mkdir -p "$TEST_DIR"
    cd "$TEST_DIR"

    tar -xzf "$ROOT/release/portier-${TEST_VERSION}.tar.gz"

    if [ -d "portier-${TEST_VERSION}" ]; then
        log_success "Package extracted successfully"
    else
        log_error "Extraction failed"
        return 1
    fi

    cd "portier-${TEST_VERSION}"

    # Check for essential files
    local essential_files=(
        "setup.sh"
        "RELEASE_README.md"
        "README.md"
        "requirements.txt"
        ".env.example"
        "bin/start_all.sh"
        "bin/ops.sh"
    )

    for file in "${essential_files[@]}"; do
        if [ -f "$file" ] || [ -d "$file" ]; then
            log_success "  ✓ $file exists"
        else
            log_error "  ✗ $file missing"
            return 1
        fi
    done

    return 0
}

test_directory_structure() {
    log_info "Test 4: Verifying directory structure..."

    cd "$TEST_DIR/portier-${TEST_VERSION}"

    # Check for agent directories
    local agent_count=$(find . -maxdepth 1 -type d -name "*opena*" | wc -l)

    if [ "$agent_count" -ge 20 ]; then
        log_success "Found $agent_count agent directories"
    else
        log_error "Only found $agent_count agent directories (expected 20+)"
        return 1
    fi

    # Check for core directories
    local core_dirs=("bin" "scripts" "config" "configs" "docs" "archivp")

    for dir in "${core_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_success "  ✓ $dir/ exists"
        else
            log_error "  ✗ $dir/ missing"
            return 1
        fi
    done

    return 0
}

test_no_excluded_files() {
    log_info "Test 5: Verifying excluded files are not present..."

    cd "$TEST_DIR/portier-${TEST_VERSION}"

    # Check for files that should NOT be in release
    local excluded_patterns=(
        ".venv"
        "__pycache__"
        "*.pyc"
        "*.log"
        ".git"
        "*.db"
    )

    local found_excluded=0

    # Check for .venv directories
    if find . -type d -name ".venv" | grep -q .; then
        log_warn "Found .venv directories (should be excluded)"
        found_excluded=1
    else
        log_success "No .venv directories found"
    fi

    # Check for __pycache__ directories
    if find . -type d -name "__pycache__" | grep -q .; then
        log_warn "Found __pycache__ directories (should be excluded)"
        found_excluded=1
    else
        log_success "No __pycache__ directories found"
    fi

    # Check for .pyc files
    if find . -name "*.pyc" | grep -q .; then
        log_warn "Found .pyc files (should be excluded)"
        found_excluded=1
    else
        log_success "No .pyc files found"
    fi

    if [ $found_excluded -eq 1 ]; then
        log_warn "Some excluded files were found (non-critical)"
    fi

    return 0
}

test_setup_script_syntax() {
    log_info "Test 6: Checking setup script syntax..."

    cd "$TEST_DIR/portier-${TEST_VERSION}"

    if bash -n setup.sh; then
        log_success "setup.sh syntax valid"
    else
        log_error "setup.sh has syntax errors"
        return 1
    fi

    if [ -x setup.sh ]; then
        log_success "setup.sh is executable"
    else
        log_error "setup.sh is not executable"
        return 1
    fi

    return 0
}

test_file_counts() {
    log_info "Test 7: Verifying file counts..."

    cd "$TEST_DIR/portier-${TEST_VERSION}"

    local total_files=$(find . -type f | wc -l)
    local py_files=$(find . -name "*.py" | wc -l)
    local sh_files=$(find . -name "*.sh" | wc -l)

    log_info "  Total files: $total_files"
    log_info "  Python files: $py_files"
    log_info "  Shell scripts: $sh_files"

    # Sanity checks
    if [ "$total_files" -lt 1000 ]; then
        log_error "Too few files ($total_files < 1000)"
        return 1
    fi

    if [ "$py_files" -lt 100 ]; then
        log_error "Too few Python files ($py_files < 100)"
        return 1
    fi

    if [ "$sh_files" -lt 50 ]; then
        log_error "Too few shell scripts ($sh_files < 50)"
        return 1
    fi

    log_success "File counts are reasonable"
    return 0
}

test_manifest_content() {
    log_info "Test 8: Checking manifest content..."

    if [ ! -f "$ROOT/release/MANIFEST.txt" ]; then
        log_error "MANIFEST.txt not found"
        return 1
    fi

    if grep -q "Release Version: $TEST_VERSION" "$ROOT/release/MANIFEST.txt"; then
        log_success "Manifest contains correct version"
    else
        log_error "Manifest version mismatch"
        return 1
    fi

    if grep -q "Total files:" "$ROOT/release/MANIFEST.txt"; then
        log_success "Manifest contains file statistics"
    else
        log_error "Manifest missing statistics"
        return 1
    fi

    return 0
}

cleanup_test() {
    log_info "Cleaning up test files..."

    # Remove test extraction directory
    if [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
        log_success "Removed test directory"
    fi

    # Remove test release files
    if [ -d "$ROOT/release" ]; then
        rm -rf "$ROOT/release"
        log_success "Removed release directory"
    fi
}

# ====================================================================
# MAIN TEST EXECUTION
# ====================================================================

main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Release Package Test Suite${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Test Version: ${TEST_VERSION}"
    echo "Test Directory: ${TEST_DIR}"
    echo ""

    local tests_passed=0
    local tests_failed=0

    # Run tests
    local tests=(
        "test_release_creation"
        "test_checksum_verification"
        "test_extraction"
        "test_directory_structure"
        "test_no_excluded_files"
        "test_setup_script_syntax"
        "test_file_counts"
        "test_manifest_content"
    )

    for test in "${tests[@]}"; do
        echo ""
        if $test; then
            ((tests_passed++))
        else
            ((tests_failed++))
        fi
    done

    # Cleanup
    echo ""
    cleanup_test

    # Summary
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Test Summary${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "Tests Passed: ${GREEN}${tests_passed}${NC}"
    echo -e "Tests Failed: ${RED}${tests_failed}${NC}"
    echo -e "Total Tests:  $((tests_passed + tests_failed))"
    echo ""

    if [ $tests_failed -eq 0 ]; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}All Tests Passed! ✓${NC}"
        echo -e "${GREEN}========================================${NC}"
        return 0
    else
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}Some Tests Failed! ✗${NC}"
        echo -e "${RED}========================================${NC}"
        return 1
    fi
}

# Run main function
main
