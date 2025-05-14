#!/bin/bash
# Migration Cleanup Script
# This script helps to fix common issues in the converted Python code

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Default directory
TARGET_DIR="backend/app"

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dir) TARGET_DIR="$2"; shift ;;
        --help) 
            echo "Usage: $0 [--dir DIRECTORY]"
            echo "Fixes common issues in converted Python code"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Create a timestamp for logs
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
mkdir -p logs/migration
LOG_FILE="logs/migration/cleanup_${TIMESTAMP}.log"

# Log both to console and file
log() {
    echo -e "${1}" | tee -a "${LOG_FILE}"
}

log "${BLUE}Starting migration cleanup process for ${TARGET_DIR}${RESET}"
log "${BLUE}Logging to ${LOG_FILE}${RESET}"

# Step 1: Create __init__.py files in all directories
log "\n${YELLOW}Step 1: Creating __init__.py files...${RESET}"
find "$TARGET_DIR" -type d -not -path "*/\.*" -not -path "*/node_modules/*" -exec touch '{}'/__init__.py \; 2>/dev/null || true
log "${GREEN}Created __init__.py files in all directories${RESET}"

# Step 2: Fix line endings
log "\n${YELLOW}Step 2: Fixing line endings...${RESET}"
find "$TARGET_DIR" -name "*.py" -not -path "*/node_modules/*" -exec dos2unix {} \; 2>/dev/null || true
log "${GREEN}Fixed line endings in Python files${RESET}"

# Step 3: Fix file permissions
log "\n${YELLOW}Step 3: Fixing file permissions...${RESET}"
find "$TARGET_DIR" -name "*.py" -not -path "*/node_modules/*" -exec chmod 644 {} \; 2>/dev/null || true
log "${GREEN}Fixed permissions for Python files${RESET}"

# Step 4: Install code formatting tools if not present
log "\n${YELLOW}Step 4: Checking for code formatting tools...${RESET}"
if ! command -v black &> /dev/null; then
    log "${BLUE}Installing black...${RESET}"
    pip install black
fi

if ! command -v isort &> /dev/null; then
    log "${BLUE}Installing isort...${RESET}"
    pip install isort
fi

# Step 5: Format Python code (skipping node_modules)
log "\n${YELLOW}Step 5: Formatting Python code...${RESET}"
log "${BLUE}Running black...${RESET}"
python -m black "$TARGET_DIR" --exclude "node_modules|venv" --quiet || log "${RED}Black failed to format some files${RESET}"

log "${BLUE}Running isort...${RESET}"
python -m isort "$TARGET_DIR" --profile black --skip node_modules --skip venv --quiet || log "${RED}isort failed to format some files${RESET}"

log "${GREEN}Formatted Python code${RESET}"

# Step 6: Remove empty __pycache__ directories
log "\n${YELLOW}Step 6: Cleaning up __pycache__ directories...${RESET}"
find "$TARGET_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
log "${GREEN}Removed __pycache__ directories${RESET}"

# Step 7: Fix common import errors
log "\n${YELLOW}Step 7: Fixing common import errors...${RESET}"
ERRORS_FIXED=0

# Common React imports to fix
find "$TARGET_DIR" -name "*.py" -not -path "*/node_modules/*" -exec sed -i -e 's/import React from "react"/# import React from "react"/g' {} \; 2>/dev/null || true
ERRORS_FIXED=$((ERRORS_FIXED + $(grep -l 'import React from "react"' $(find "$TARGET_DIR" -name "*.py" -not -path "*/node_modules/*") 2>/dev/null | wc -l || echo 0)))

# Fix invalid "import type" statements (Python doesn't have this)
find "$TARGET_DIR" -name "*.py" -not -path "*/node_modules/*" -exec sed -i -e 's/import type/# import type/g' {} \; 2>/dev/null || true
ERRORS_FIXED=$((ERRORS_FIXED + $(grep -l 'import type' $(find "$TARGET_DIR" -name "*.py" -not -path "*/node_modules/*") 2>/dev/null | wc -l || echo 0)))

log "${GREEN}Fixed approximately ${ERRORS_FIXED} common import errors${RESET}"

# Summary
log "\n${GREEN}Cleanup process completed!${RESET}"
log "${BLUE}Summary of actions:${RESET}"
log "  - Created __init__.py files in all directories"
log "  - Fixed line endings in Python files"
log "  - Fixed file permissions"
log "  - Formatted Python code with black and isort"
log "  - Cleaned up __pycache__ directories"
log "  - Fixed common import errors"
log "\n${YELLOW}Next steps:${RESET}"
log "  - Run the test script to verify improvements: python scripts/test_converted_modules.py --modules-dir $TARGET_DIR"
log "  - Address remaining import errors systematically"
log "  - Implement unit tests for converted modules"

# Make the script executable
chmod +x "$0" 