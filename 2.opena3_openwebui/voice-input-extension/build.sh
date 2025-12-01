#!/bin/bash

# Voice Input Extension - Build Script
# Comprehensive build and setup automation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BUILD_DIR="$PROJECT_ROOT/out"
SRC_DIR="$PROJECT_ROOT/src"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main build process
main() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Voice Input Extension - Build System${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo ""

    # Check Node.js
    print_status "Checking Node.js..."
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Please install Node.js first."
        exit 1
    fi
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"

    # Check npm
    print_status "Checking npm..."
    if ! command -v npm &> /dev/null; then
        print_error "npm not found. Please install npm first."
        exit 1
    fi
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"

    # Check TypeScript
    print_status "Checking TypeScript..."
    if [ ! -d "$PROJECT_ROOT/node_modules/typescript" ]; then
        print_warning "TypeScript not installed. Installing dependencies..."
        npm install
    fi
    print_success "TypeScript ready"

    # Install dependencies if needed
    if [ ! -d "$PROJECT_ROOT/node_modules" ]; then
        print_status "Installing dependencies..."
        npm install
        print_success "Dependencies installed"
    else
        print_status "Dependencies already installed"
    fi

    # Clean build directory
    print_status "Cleaning build directory..."
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR"
    print_success "Build directory ready"

    # Compile TypeScript
    print_status "Compiling TypeScript..."
    if npm run compile; then
        print_success "TypeScript compilation successful"
    else
        print_error "TypeScript compilation failed"
        exit 1
    fi

    # Verify build
    print_status "Verifying build..."
    if [ -f "$BUILD_DIR/extension-advanced.js" ]; then
        print_success "Extension file generated: extension-advanced.js"
    else
        print_error "Extension file not found!"
        exit 1
    fi

    if [ -f "$BUILD_DIR/recognition-engine.js" ]; then
        print_success "Recognition engine file generated"
    fi

    if [ -f "$BUILD_DIR/settings.js" ]; then
        print_success "Settings module file generated"
    fi

    if [ -f "$BUILD_DIR/copilot-integration.js" ]; then
        print_success "Copilot integration file generated"
    fi

    if [ -f "$BUILD_DIR/commands.js" ]; then
        print_success "Commands module file generated"
    fi

    if [ -f "$BUILD_DIR/analytics.js" ]; then
        print_success "Analytics module file generated"
    fi

    # Count files
    FILE_COUNT=$(find "$BUILD_DIR" -name "*.js" | wc -l)
    print_success "$FILE_COUNT JavaScript files compiled"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Build Complete! ✅${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""

    # Build stats
    TOTAL_SIZE=$(du -sh "$BUILD_DIR" | cut -f1)
    print_status "Build Output Directory: $BUILD_DIR"
    print_status "Total Size: $TOTAL_SIZE"
    echo ""

    # Next steps
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "   1. Open command palette (Ctrl+Shift+P)"
    echo "   2. Search for 'Debug: Start Debugging' or press F5"
    echo "   3. Select 'Run Extension' configuration"
    echo "   4. Test voice input with Ctrl+Shift+V"
    echo ""
}

# Handle arguments
case "${1:-build}" in
    clean)
        print_status "Cleaning build directory..."
        rm -rf "$BUILD_DIR"
        print_success "Clean complete"
        ;;
    watch)
        print_status "Starting TypeScript watch mode..."
        npm run watch
        ;;
    test)
        print_status "Running tests..."
        npm test
        ;;
    lint)
        print_status "Running linter..."
        npm run lint
        ;;
    build|*)
        main
        ;;
esac
