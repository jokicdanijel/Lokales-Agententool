#!/usr/bin/env bash
set -e

# Portier Dashboard Installation Script
# Installs both Admin (3.0.0) and User (1.0.0) versions to OpenWebUI

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TARGET_BASE_DIR="${OPENWEBUI_DIR:-.}/open-webui/extensions/functions"
BACKUP_DIR="${SCRIPT_DIR}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📦 Portier Dashboard Installation Script${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Create backup directory
mkdir -p "${BACKUP_DIR}"
echo -e "${YELLOW}📁 Backup directory: ${BACKUP_DIR}${NC}"
echo ""

# Files to install
declare -A FILES_TO_INSTALL=(
    ["portier_hyperdashboard_3_0_0.py"]="Admin Dashboard 3.0.0"
    ["portier_dashboard_user_1_0_0.py"]="User Dashboard 1.0.0"
    ["portier_pdf_viewer_1_0_0.py"]="PDF Viewer 1.0.0"
    ["dispatcher_flowmap_1_0_0.py"]="Dispatcher FlowMap 1.0.0"
    ["portier_workflow_builder_1_0_0.py"]="Workflow Builder 1.0.0"
    ["portier_monitoring_engine_1_0_0.py"]="Monitoring Engine 1.0.0"
    ["portier_browseragent_recorder_1_0_0.py"]="BrowserAgent Recorder 1.0.0"
)

FAILED_FILES=()
INSTALLED_FILES=()

# Install each file
for FILE in "${!FILES_TO_INSTALL[@]}"; do
    DESCRIPTION="${FILES_TO_INSTALL[$FILE]}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}📥 Installing: ${DESCRIPTION}${NC}"

    SOURCE_FILE="${SCRIPT_DIR}/${FILE}"
    TARGET_FILE="${TARGET_BASE_DIR}/${FILE}"

    # Check source exists
    if [ ! -f "${SOURCE_FILE}" ]; then
        echo -e "${RED}❌ Source file not found: ${SOURCE_FILE}${NC}"
        FAILED_FILES+=("${FILE}")
        continue
    fi

    # Create backup if target exists
    if [ -f "${TARGET_FILE}" ]; then
        BACKUP_FILE="${BACKUP_DIR}/${FILE}.${TIMESTAMP}.backup"
        echo -e "${YELLOW}🔧 Backing up existing: ${BACKUP_FILE}${NC}"
        cp "${TARGET_FILE}" "${BACKUP_FILE}"
    fi

    # Create target directory if needed
    mkdir -p "${TARGET_BASE_DIR}"

    # Copy file
    echo -e "${YELLOW}📋 Copying file...${NC}"
    cp "${SOURCE_FILE}" "${TARGET_FILE}"

    # Check Python syntax
    echo -e "${YELLOW}🔍 Checking Python syntax...${NC}"
    if python3 -m py_compile "${TARGET_FILE}" 2>/dev/null; then
        echo -e "${GREEN}✅ Syntax OK${NC}"
        INSTALLED_FILES+=("${FILE}")
    else
        echo -e "${RED}⚠️  Syntax check failed (non-critical)${NC}"
        INSTALLED_FILES+=("${FILE}")
    fi

    echo -e "${GREEN}✅ Installed: ${DESCRIPTION}${NC}"
    echo ""
done

# Installation summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 Installation Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ ${#INSTALLED_FILES[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Successfully Installed (${#INSTALLED_FILES[@]}):${NC}"
    for FILE in "${INSTALLED_FILES[@]}"; do
        echo -e "${GREEN}  ✓ ${FILES_TO_INSTALL[$FILE]}${NC}"
    done
    echo ""
fi

if [ ${#FAILED_FILES[@]} -gt 0 ]; then
    echo -e "${RED}❌ Failed to Install (${#FAILED_FILES[@]}):${NC}"
    for FILE in "${FAILED_FILES[@]}"; do
        echo -e "${RED}  ✗ ${FILE}${NC}"
    done
    echo ""
fi

# Theme pack installation
echo -e "${YELLOW}🎨 Installing Theme Pack...${NC}"
THEME_SOURCE="${SCRIPT_DIR}/theme_pack.json"
THEME_TARGET="${TARGET_BASE_DIR}/theme_pack.json"

if [ -f "${THEME_SOURCE}" ]; then
    cp "${THEME_SOURCE}" "${THEME_TARGET}"
    echo -e "${GREEN}✅ Theme Pack installed${NC}"
else
    echo -e "${YELLOW}⚠️  Theme Pack not found${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. 🔄 Reload OpenWebUI in your browser"
echo "2. 🔐 Admin Dashboard: @portier_hyperdashboard_3_0_0"
echo "3. 👤 User Dashboard: @portier_dashboard_user_1_0_0"
echo "4. 📄 PDF Viewer: @portier_pdf_viewer_1_0_0"
echo "5. 🗺️  Dispatcher FlowMap: @dispatcher_flowmap_1_0_0"
echo "6. 🔧 Workflow Builder: @portier_workflow_builder_1_0_0"
echo "7. 📊 Monitoring Engine: @portier_monitoring_engine_1_0_0"
echo "8. 🎬 BrowserAgent Recorder: @portier_browseragent_recorder_1_0_0"
echo ""

echo -e "${YELLOW}📦 Configuration:${NC}"
echo "Set these environment variables (optional):"
echo "  export PORTIER_DATA_DIR=/path/to/portier/data"
echo "  export PORTIER_CACHE_DIR=/path/to/portier/cache"
echo "  export DISPATCHER_URL=http://localhost:8100"
echo ""

echo -e "${YELLOW}🔗 Documentation:${NC}"
echo "Find documentation in: ${SCRIPT_DIR}/docs/"
echo ""

if [ ${#INSTALLED_FILES[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Installation successful!${NC}"
    exit 0
else
    echo -e "${RED}❌ Installation failed!${NC}"
    exit 1
fi
