#!/bin/bash
# Complete TypeScript to Python Migration Runner
# This script orchestrates the entire TypeScript to Python migration process
# from analysis and conversion to testing, integration, and verification.

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Source directory
SOURCE_DIR="."

# Output directories
CONVERTED_DIR="python_converted"
TARGET_DIR="backend/app"
REPORT_DIR="docs/migration"

# Track start time
START_TIME=$(date +%s)

# Timestamp for logs
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="logs/migration/complete_migration_${TIMESTAMP}.log"

# Create required directories
mkdir -p logs/migration
mkdir -p "$REPORT_DIR"

# Helper function to log messages
log() {
    local msg=$1
    local level=${2:-INFO}
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} [${level}] ${msg}" | tee -a "$LOG_FILE"
}

# Helper function to run a step and log its status
run_step() {
    local step_name=$1
    local command=$2
    
    log "Starting: ${step_name}" "STEP"
    echo "$ $command" >> "$LOG_FILE"
    
    if eval "$command"; then
        log "${GREEN}Completed: ${step_name}${RESET}" "SUCCESS"
        return 0
    else
        local exit_code=$?
        log "${RED}Failed: ${step_name} (Exit code: ${exit_code})${RESET}" "ERROR"
        return $exit_code
    fi
}

# Helper function for printing a section header
print_header() {
    local title=$1
    log "\n${BLUE}=================================${RESET}" "HEADER"
    log "${BLUE}    $title${RESET}" "HEADER"
    log "${BLUE}=================================${RESET}" "HEADER"
}

# Step 1: Verify required files and initialize
print_header "STEP 1: Initialization and Verification"

log "Verifying required scripts exist..."
required_scripts=(
    "scripts/analyze_ts_dependencies.py"
    "scripts/ts2py.py"
    "scripts/fix_py_conversions.py"
    "scripts/integrate_py_modules.py"
    "scripts/test_converted_modules.py"
    "scripts/finalize_ts_migration.py"
    "scripts/migrate_ts_to_py.sh"
)

for script in "${required_scripts[@]}"; do
    if [[ ! -f "$script" ]]; then
        log "${RED}Missing required script: $script${RESET}" "ERROR"
        exit 1
    fi
done

log "${GREEN}All required scripts verified${RESET}" "SUCCESS"

# Create output directories
mkdir -p "$CONVERTED_DIR"
mkdir -p "$TARGET_DIR"

# Step 2: Run the analysis and conversion
print_header "STEP 2: Analysis and Conversion"

run_step "Running TypeScript file analysis" "python scripts/analyze_ts_dependencies.py"

run_step "Running TypeScript to Python migration" "bash scripts/migrate_ts_to_py.sh"

# Step 3: Run post-processing fixes
print_header "STEP 3: Post-Processing and Fixes"

run_step "Fixing common conversion issues" "python scripts/fix_py_conversions.py --dir $CONVERTED_DIR"

# Step 4: Test converted modules
print_header "STEP 4: Testing Converted Modules"

run_step "Testing converted Python modules" "python scripts/test_converted_modules.py --modules-dir $CONVERTED_DIR --report-file $REPORT_DIR/module_test_report.json"

# Step 5: Integrate with existing code
print_header "STEP 5: Integration with Existing Codebase"

run_step "Integrating Python modules with existing codebase" "python scripts/integrate_py_modules.py --source-dir $CONVERTED_DIR --target-dir $TARGET_DIR"

# Step 6: Final verification and cleanup
print_header "STEP 6: Final Verification and Cleanup"

run_step "Finalizing migration and cleanup" "python scripts/finalize_ts_migration.py --converted-dir $CONVERTED_DIR --source-dir $SOURCE_DIR --report-dir $REPORT_DIR"

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
HOURS=$((ELAPSED / 3600))
MINUTES=$(( (ELAPSED % 3600) / 60 ))
SECONDS=$((ELAPSED % 60))

# Print summary
print_header "Migration Complete"
log "Total migration time: ${HOURS}h ${MINUTES}m ${SECONDS}s"
log "Migration logs: $LOG_FILE"
log "Migration reports: $REPORT_DIR/"

# Print next steps
log "\n${YELLOW}Next Steps:${RESET}" "INFO"
log "1. Review conversion reports in $REPORT_DIR/" "INFO"
log "2. Verify functionality of converted modules in $TARGET_DIR/" "INFO"
log "3. Run comprehensive tests on the integrated codebase" "INFO"
log "4. Update documentation to reflect Python implementation" "INFO"
log "5. Remove original TypeScript files after verification" "INFO"

log "\nMigration process completed!" "SUCCESS" 