#!/usr/bin/env bash
# bin/prepare_release.sh — Prepare compressed, runnable version for new repository
# Creates a clean, minimal, production-ready release package
# Usage: bash bin/prepare_release.sh [VERSION]

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERSION="${1:-$(date +%Y%m%d-%H%M%S)}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RELEASE_DIR="$ROOT/release"
PACKAGE_NAME="portier-${VERSION}"
PACKAGE_DIR="$RELEASE_DIR/$PACKAGE_NAME"
ARCHIVE_NAME="$PACKAGE_NAME.tar.gz"

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
# PREPARATION FUNCTIONS
# ====================================================================

cleanup_old_releases() {
    log_info "Cleaning up old release directory..."
    rm -rf "$RELEASE_DIR"
    mkdir -p "$PACKAGE_DIR"
    log_success "Release directory created: $PACKAGE_DIR"
}

copy_essential_directories() {
    log_info "Copying essential service directories..."

    # Core agent directories (opena1-opena21)
    for dir in "$ROOT"/*opena*; do
        if [ -d "$dir" ] && [[ ! "$dir" =~ BROKEN ]]; then
            dirname=$(basename "$dir")
            log_info "  → $dirname"
            mkdir -p "$PACKAGE_DIR/$dirname"

            # Copy only essential files (exclude venv, cache, logs)
            rsync -a --exclude='.venv' \
                     --exclude='venv' \
                     --exclude='__pycache__' \
                     --exclude='*.pyc' \
                     --exclude='*.log' \
                     --exclude='logs/' \
                     --exclude='.pytest_cache' \
                     --exclude='*.db' \
                     --exclude='*.sqlite' \
                     "$dir/" "$PACKAGE_DIR/$dirname/"
        fi
    done

    log_success "Agent directories copied"
}

copy_core_infrastructure() {
    log_info "Copying core infrastructure..."

    # Essential directories
    local essential_dirs=("bin" "scripts" "config" "configs" "schemas" "systemd" "tools" "src")

    for dir in "${essential_dirs[@]}"; do
        if [ -d "$ROOT/$dir" ]; then
            log_info "  → $dir/"
            mkdir -p "$PACKAGE_DIR/$dir"
            rsync -a --exclude='*.pyc' \
                     --exclude='__pycache__' \
                     --exclude='*.log' \
                     "$ROOT/$dir/" "$PACKAGE_DIR/$dir/"
        fi
    done

    # Copy archivp structure (create empty)
    mkdir -p "$PACKAGE_DIR/archivp"

    log_success "Core infrastructure copied"
}

copy_configuration_files() {
    log_info "Copying configuration and setup files..."

    # Essential root files
    local essential_files=(
        "README.md"
        "requirements.txt"
        "pyproject.toml"
        "Makefile"
        ".gitignore"
        ".env.example"
        "docker-compose.prod.yml"
        "LICENSE"
        "SECURITY.md"
    )

    for file in "${essential_files[@]}"; do
        if [ -f "$ROOT/$file" ]; then
            log_info "  → $file"
            cp "$ROOT/$file" "$PACKAGE_DIR/"
        fi
    done

    log_success "Configuration files copied"
}

copy_essential_documentation() {
    log_info "Copying essential documentation..."

    mkdir -p "$PACKAGE_DIR/docs"

    # Only copy key documentation files
    local essential_docs=(
        "PORTIER_3.0_SYSTEM_ARCHITECTURE.md"
        "ELION_SYSTEM_ARCHITECTURE.md"
        "PROJEKTSTRUKTUR.md"
        "SYSTEM_OVERVIEW.md"
        "OPERATIONS_COMPLETE.md"
        "PORTIER_3.0_RELEASE.md"
    )

    for doc in "${essential_docs[@]}"; do
        if [ -f "$ROOT/$doc" ]; then
            log_info "  → $doc"
            cp "$ROOT/$doc" "$PACKAGE_DIR/docs/"
        fi
    done

    log_success "Essential documentation copied"
}

create_setup_script() {
    log_info "Creating setup script for new repository..."

    cat > "$PACKAGE_DIR/setup.sh" << 'EOF'
#!/usr/bin/env bash
# Automated setup script for PORTIER 3.0
# Run this script after extracting the release package

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PORTIER 3.0 - Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}1. Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠ Python 3 not found. Please install Python 3.11 or later${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo -e "${BLUE}2. Creating virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment created and activated"

# Install dependencies
echo ""
echo -e "${BLUE}3. Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${YELLOW}⚠ requirements.txt not found${NC}"
fi

# Setup directories
echo ""
echo -e "${BLUE}4. Setting up directories...${NC}"
mkdir -p logs archivp/{YYYY/MM/DD}
chmod +x bin/*.sh scripts/*.sh 2>/dev/null || true
echo -e "${GREEN}✓${NC} Directory structure created"

# Bootstrap environment
echo ""
echo -e "${BLUE}5. Bootstrapping environment...${NC}"
if [ -f bin/env_bootstrap.sh ]; then
    bash bin/env_bootstrap.sh
    echo -e "${GREEN}✓${NC} Environment bootstrapped"
else
    echo -e "${YELLOW}⚠ Creating default .env file${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓${NC} .env file created from template"
    fi
fi

# Verify installation
echo ""
echo -e "${BLUE}6. Verifying installation...${NC}"
if [ -f bin/health_check.sh ]; then
    bash bin/health_check.sh || true
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys and configuration"
echo "  2. Start services: bash bin/start_all.sh"
echo "  3. Check status: bash bin/ops.sh status"
echo "  4. View dashboard: http://127.0.0.1:12349"
echo ""
echo "For more information, see docs/PORTIER_3.0_SYSTEM_ARCHITECTURE.md"
echo ""
EOF

    chmod +x "$PACKAGE_DIR/setup.sh"
    log_success "Setup script created"
}

create_readme_for_release() {
    log_info "Creating README for release package..."

    cat > "$PACKAGE_DIR/RELEASE_README.md" << EOF
# PORTIER 3.0 - Release Package

**Version:** ${VERSION}
**Release Date:** $(date +"%Y-%m-%d %H:%M:%S UTC")
**Package:** ${ARCHIVE_NAME}

## 📦 What's Included

This is a clean, minimal, production-ready release of the PORTIER 3.0 Multi-Agent Intelligence Platform.

### Components

- **20+ Specialized AI Agents** (opena1-opena21)
- **Core Infrastructure** (bin/, scripts/, configs/)
- **Documentation** (essential docs only)
- **Setup Scripts** (automated installation)
- **Docker Compose** (production deployment)

### Excluded from This Release

The following have been excluded to minimize package size:

- Virtual environments (.venv, venv)
- Python cache files (\_\_pycache\_\_, *.pyc)
- Log files (*.log, logs/)
- Database files (*.db, *.sqlite)
- Large development files
- Git history
- Backup files
- Broken/deprecated components

## 🚀 Quick Start

### 1. Extract the Package

\`\`\`bash
tar -xzf ${ARCHIVE_NAME}
cd ${PACKAGE_NAME}
\`\`\`

### 2. Run Setup Script

\`\`\`bash
bash setup.sh
\`\`\`

This will:
- Create virtual environment
- Install Python dependencies
- Set up directory structure
- Bootstrap environment with tokens
- Verify installation

### 3. Configure Environment

Edit the \`.env\` file with your API keys:

\`\`\`bash
nano .env
\`\`\`

Required variables:
- \`OPENAI_API_KEY_OPENA1\`
- \`BEARER_TOKEN_MASTER\`
- Additional API keys for specific agents

### 4. Start Services

\`\`\`bash
# Start all services
bash bin/start_all.sh

# Check status
bash bin/ops.sh status

# View logs
bash bin/ops.sh logs
\`\`\`

### 5. Access Dashboard

Open your browser to:
- **Dashboard UI:** http://127.0.0.1:12349
- **Health Check:** http://127.0.0.1:12349/health

## 📚 Documentation

Essential documentation is included in the \`docs/\` directory:

- **PORTIER_3.0_SYSTEM_ARCHITECTURE.md** - Complete system architecture
- **OPERATIONS_COMPLETE.md** - Operations guide
- **PORTIER_3.0_RELEASE.md** - Release notes

Full documentation is available at:
https://github.com/jokicdanijel/Gesamtprojekt-start

## 🔒 Security

- Never commit the \`.env\` file
- Rotate all API keys before production use
- Review \`SECURITY.md\` for best practices
- Keep all dependencies updated

## 📊 System Requirements

- **OS:** Linux, macOS, or WSL2 on Windows
- **Python:** 3.11 or later
- **Memory:** 4GB minimum, 8GB recommended
- **Disk:** 2GB for installation + storage for archives
- **Ports:** 12344-12399 (configurable)

## 🛠️ Troubleshooting

If services don't start:

1. Check port conflicts: \`bash bin/check_ports.sh\`
2. Verify environment: \`cat .env\`
3. Check logs: \`tail -f logs/*.log\`
4. Run health check: \`bash bin/health_check.sh\`

For more help, see the troubleshooting section in the documentation.

## 📞 Support

- **Repository:** https://github.com/jokicdanijel/Gesamtprojekt-start
- **Issues:** https://github.com/jokicdanijel/Gesamtprojekt-start/issues
- **Email:** jokicdanijel@gmail.com

## 📄 License

MIT License - See LICENSE file for details

---

**Generated:** $(date +"%Y-%m-%d %H:%M:%S UTC")
**Package:** ${ARCHIVE_NAME}
**Version:** ${VERSION}
EOF

    log_success "Release README created"
}

generate_checksums() {
    log_info "Generating checksums..."

    cd "$RELEASE_DIR"

    # Create tarball
    tar -czf "$ARCHIVE_NAME" "$PACKAGE_NAME"
    log_success "Archive created: $ARCHIVE_NAME"

    # Generate SHA256 checksum
    sha256sum "$ARCHIVE_NAME" > "$ARCHIVE_NAME.sha256"
    log_success "Checksum created: $ARCHIVE_NAME.sha256"

    # Create a zip version as well
    zip -r "${PACKAGE_NAME}.zip" "$PACKAGE_NAME" > /dev/null 2>&1
    sha256sum "${PACKAGE_NAME}.zip" > "${PACKAGE_NAME}.zip.sha256"
    log_success "ZIP archive created: ${PACKAGE_NAME}.zip"

    cd "$ROOT"
}

create_manifest() {
    log_info "Creating release manifest..."

    cat > "$RELEASE_DIR/MANIFEST.txt" << EOF
PORTIER 3.0 - Release Manifest
==============================

Release Version: ${VERSION}
Generated: $(date +"%Y-%m-%d %H:%M:%S UTC")
Generated by: $(whoami)@$(hostname)

Files in This Release
---------------------

1. ${ARCHIVE_NAME}
   - Complete release package (tar.gz)
   - Checksum: See ${ARCHIVE_NAME}.sha256

2. ${PACKAGE_NAME}.zip
   - Complete release package (zip format)
   - Checksum: See ${PACKAGE_NAME}.zip.sha256

3. MANIFEST.txt (this file)
   - Release metadata and verification instructions

Package Contents
----------------

$(cd "$PACKAGE_DIR" && find . -type d -maxdepth 1 | sort)

Total Size
----------

$(du -sh "$PACKAGE_DIR" | cut -f1) (unpacked)
$(du -sh "$RELEASE_DIR/$ARCHIVE_NAME" | cut -f1) (tar.gz)
$(du -sh "$RELEASE_DIR/${PACKAGE_NAME}.zip" | cut -f1) (zip)

File Counts
-----------

Total files: $(find "$PACKAGE_DIR" -type f | wc -l)
Python files: $(find "$PACKAGE_DIR" -name "*.py" | wc -l)
Shell scripts: $(find "$PACKAGE_DIR" -name "*.sh" | wc -l)
Config files: $(find "$PACKAGE_DIR" -name "*.json" -o -name "*.yml" -o -name "*.yaml" | wc -l)

Verification
------------

To verify the archive integrity:

  sha256sum -c ${ARCHIVE_NAME}.sha256
  sha256sum -c ${PACKAGE_NAME}.zip.sha256

Extraction
----------

  tar -xzf ${ARCHIVE_NAME}
  cd ${PACKAGE_NAME}
  bash setup.sh

---
End of Manifest
EOF

    log_success "Manifest created"
}

print_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Release Package Created Successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Release Information:${NC}"
    echo "  Version: ${VERSION}"
    echo "  Location: $RELEASE_DIR"
    echo ""
    echo -e "${BLUE}Generated Files:${NC}"
    echo "  → $ARCHIVE_NAME ($(du -sh "$RELEASE_DIR/$ARCHIVE_NAME" | cut -f1))"
    echo "  → $ARCHIVE_NAME.sha256"
    echo "  → ${PACKAGE_NAME}.zip ($(du -sh "$RELEASE_DIR/${PACKAGE_NAME}.zip" | cut -f1))"
    echo "  → ${PACKAGE_NAME}.zip.sha256"
    echo "  → MANIFEST.txt"
    echo ""
    echo -e "${BLUE}Package Contents:${NC}"
    echo "  → $(find "$PACKAGE_DIR" -type f | wc -l) files"
    echo "  → $(find "$PACKAGE_DIR" -type d | wc -l) directories"
    echo "  → $(find "$PACKAGE_DIR" -name "*.py" | wc -l) Python files"
    echo "  → $(find "$PACKAGE_DIR" -name "*.sh" | wc -l) Shell scripts"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Verify checksums:"
    echo "     cd $RELEASE_DIR && sha256sum -c $ARCHIVE_NAME.sha256"
    echo ""
    echo "  2. Test extraction:"
    echo "     tar -xzf $RELEASE_DIR/$ARCHIVE_NAME -C /tmp"
    echo "     cd /tmp/$PACKAGE_NAME && bash setup.sh"
    echo ""
    echo "  3. Create GitHub release:"
    echo "     gh release create v${VERSION} \\"
    echo "       $RELEASE_DIR/$ARCHIVE_NAME \\"
    echo "       $RELEASE_DIR/$ARCHIVE_NAME.sha256 \\"
    echo "       $RELEASE_DIR/${PACKAGE_NAME}.zip \\"
    echo "       $RELEASE_DIR/${PACKAGE_NAME}.zip.sha256 \\"
    echo "       $RELEASE_DIR/MANIFEST.txt"
    echo ""
    echo -e "${GREEN}========================================${NC}"
}

# ====================================================================
# MAIN EXECUTION
# ====================================================================

main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}PORTIER 3.0 - Release Package Builder${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Version: ${VERSION}"
    echo "Root: ${ROOT}"
    echo ""

    cleanup_old_releases
    copy_essential_directories
    copy_core_infrastructure
    copy_configuration_files
    copy_essential_documentation
    create_setup_script
    create_readme_for_release
    generate_checksums
    create_manifest
    print_summary
}

# Run main function
main
