#!/usr/bin/env bash

################################################################################
#  LocalAgent-Pro Health Check Script
#  Validiert System-Zustand und Abhängigkeiten
################################################################################

set -euo pipefail

# Farben
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Counter für Pass/Fail
passed=0
failed=0

# ======================== UTILITY FUNCTIONS ==================================

check_pass() {
    echo -e "${GREEN}✅ $*${NC}"
    ((passed++))
}

check_fail() {
    echo -e "${RED}❌ $*${NC}"
    ((failed++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $*${NC}"
}

section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}▶  $*${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
}

# ======================== CHECKS =============================================

check_vscode() {
    section "VSCode Installation"

    if command -v code &> /dev/null; then
        local version=$(code --version | head -1)
        check_pass "VSCode installiert: $version"
    else
        check_fail "VSCode nicht gefunden"
    fi
}

check_python() {
    section "Python Environment"

    if command -v python3 &> /dev/null; then
        local version=$(python3 --version)
        check_pass "Python3 vorhanden: $version"
    else
        check_fail "Python3 nicht gefunden"
        return
    fi

    # Prüfe Python-Version
    local py_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ "$py_version" > "3.7" ]]; then
        check_pass "Python-Version ausreichend: $py_version"
    else
        check_fail "Python-Version zu alt: $py_version (min: 3.8)"
    fi

    # Prüfe pip
    if python3 -m pip --version &> /dev/null; then
        check_pass "pip vorhanden"
    else
        check_fail "pip nicht gefunden"
    fi
}

check_dependencies() {
    section "Python Dependencies"

    local deps=("flask" "requests" "pyyaml" "pytest" "flask_cors")

    for dep in "${deps[@]}"; do
        if python3 -c "import $(echo $dep | tr '-' '_')" 2>/dev/null; then
            check_pass "Modul vorhanden: $dep"
        else
            check_warn "Modul nicht installiert: $dep"
        fi
    done
}

check_git() {
    section "Git Repository"

    if command -v git &> /dev/null; then
        check_pass "Git installiert: $(git --version)"
    else
        check_fail "Git nicht gefunden"
        return
    fi

    # Prüfe Git-Repository
    if git -C . rev-parse --git-dir > /dev/null 2>&1; then
        local branch=$(git -C . rev-parse --abbrev-ref HEAD)
        local commit=$(git -C . rev-parse --short HEAD)
        check_pass "Git-Repository: branch=$branch, commit=$commit"
    else
        check_warn "Nicht in Git-Repository"
    fi
}

check_directories() {
    section "Verzeichnis-Struktur"

    local dirs=(
        "src"
        "tests"
        "docs"
        "scripts"
        "config"
        "logs"
    )

    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            local file_count=$(find "$dir" -type f | wc -l)
            check_pass "Verzeichnis vorhanden: $dir ($file_count Dateien)"
        else
            check_warn "Verzeichnis fehlt: $dir"
        fi
    done
}

check_files() {
    section "Kritische Dateien"

    local files=(
        "requirements.txt"
        "README.md"
        "setup.py"
    )

    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            local size=$(du -h "$file" | cut -f1)
            check_pass "Datei vorhanden: $file ($size)"
        else
            check_warn "Datei fehlt: $file"
        fi
    done
}

check_permissions() {
    section "Datei-Berechtigungen"

    # Prüfe .sh Scripts
    local scripts=$(find ./scripts -name "*.sh" -type f 2>/dev/null | wc -l)
    if [ "$scripts" -gt 0 ]; then
        local executable=$(find ./scripts -name "*.sh" -type f -executable 2>/dev/null | wc -l)
        if [ "$executable" -eq "$scripts" ]; then
            check_pass "Alle $scripts Shell-Skripte sind ausführbar"
        else
            check_warn "$executable von $scripts Shell-Skripten ausführbar"
        fi
    fi
}

check_ports() {
    section "Port Availability"

    local ports=(8000 8001 8765 5001)

    for port in "${ports[@]}"; do
        if ! nc -z localhost "$port" 2>/dev/null; then
            check_pass "Port $port verfügbar"
        else
            check_warn "Port $port wird bereits verwendet"
        fi
    done
}

check_disk_space() {
    section "Disk Space"

    local space=$(df -h . | awk 'NR==2 {print $4}')
    check_pass "Verfügbarer Speicher: $space"
}

check_system_info() {
    section "System Information"

    local os=$(uname -s)
    local kernel=$(uname -r)
    local uptime=$(uptime -p)

    check_pass "Betriebssystem: $os"
    check_pass "Kernel: $kernel"
    check_pass "Uptime: $uptime"
}

check_network() {
    section "Network Connectivity"

    if ping -c 1 8.8.8.8 &> /dev/null; then
        check_pass "Internet-Verbindung verfügbar"
    else
        check_warn "Keine Internet-Verbindung"
    fi

    # Prüfe localhost
    if nc -z localhost 80 2>/dev/null || nc -z localhost 443 2>/dev/null; then
        check_pass "Lokal erreichbar"
    else
        check_warn "Lokale Ports nicht verfügbar"
    fi
}

check_tests() {
    section "Test Suite"

    local test_files=$(find tests -name "test_*.py" 2>/dev/null | wc -l)
    if [ "$test_files" -gt 0 ]; then
        check_pass "Test-Dateien vorhanden: $test_files"
    else
        check_warn "Keine Test-Dateien gefunden"
    fi

    # Prüfe pytest
    if python3 -m pytest --version 2>/dev/null; then
        local pytest_version=$(python3 -m pytest --version | awk '{print $2}')
        check_pass "pytest installiert: $pytest_version"
    else
        check_warn "pytest nicht installiert"
    fi
}

check_code_quality() {
    section "Code Quality Tools"

    # Black (Code Formatter)
    if python3 -c "import black" 2>/dev/null; then
        check_pass "black (Code Formatter) installiert"
    else
        check_warn "black nicht installiert"
    fi

    # Flake8 (Linter)
    if python3 -c "import flake8" 2>/dev/null; then
        check_pass "flake8 (Linter) installiert"
    else
        check_warn "flake8 nicht installiert"
    fi

    # MyPy (Type Checker)
    if python3 -c "import mypy" 2>/dev/null; then
        check_pass "mypy (Type Checker) installiert"
    else
        check_warn "mypy nicht installiert"
    fi
}

check_docker() {
    section "Docker"

    if command -v docker &> /dev/null; then
        local version=$(docker --version)
        check_pass "Docker installiert: $version"

        # Prüfe docker-compose
        if command -v docker-compose &> /dev/null; then
            local compose_version=$(docker-compose --version)
            check_pass "docker-compose installiert: $compose_version"
        else
            check_warn "docker-compose nicht installiert"
        fi
    else
        check_warn "Docker nicht installiert"
    fi
}

check_copilot() {
    section "Copilot Integration"

    if [ -f ".github/copilot-instructions.md" ]; then
        local lines=$(wc -l < .github/copilot-instructions.md)
        check_pass "copilot-instructions.md vorhanden ($lines Zeilen)"
    else
        check_warn "copilot-instructions.md fehlt"
    fi

    if [ -f "COPILOT_SYSTEM_PROMPT.md" ]; then
        local lines=$(wc -l < COPILOT_SYSTEM_PROMPT.md)
        check_pass "COPILOT_SYSTEM_PROMPT.md vorhanden ($lines Zeilen)"
    else
        check_warn "COPILOT_SYSTEM_PROMPT.md fehlt"
    fi
}

# ======================== SUMMARY =============================================

print_summary() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}HEALTH CHECK SUMMARY${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

    local total=$((passed + failed))
    local percent=$((passed * 100 / total))

    echo ""
    echo -e "  ${GREEN}✅ Passed: $passed${NC}"
    echo -e "  ${RED}❌ Failed: $failed${NC}"
    echo -e "  ${BLUE}Total: $total${NC}"
    echo ""
    echo -e "  System Health: ${BLUE}$percent%${NC}"
    echo ""

    if [ "$failed" -eq 0 ]; then
        echo -e "${GREEN}🎉 ALLES IN ORDNUNG! System ist bereit.${NC}"
    elif [ "$failed" -lt 3 ]; then
        echo -e "${YELLOW}⚠️  WARNUNG: Ein paar Probleme gefunden, aber nicht kritisch.${NC}"
    else
        echo -e "${RED}🚨 FEHLER: Mehrere kritische Probleme gefunden.${NC}"
    fi

    echo ""
}

# ======================== MAIN ===============================================

main() {
    clear

    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║  LocalAgent-Pro HEALTH CHECK                          ║"
    echo "║  System Status Validator v1.0                         ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # Führe alle Checks aus
    check_system_info
    check_vscode
    check_python
    check_dependencies
    check_git
    check_directories
    check_files
    check_permissions
    check_ports
    check_disk_space
    check_network
    check_tests
    check_code_quality
    check_docker
    check_copilot

    # Zusammenfassung
    print_summary
}

# Starte Health Check
main "$@"
