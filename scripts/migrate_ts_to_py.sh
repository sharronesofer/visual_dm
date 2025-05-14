#!/bin/bash
# TypeScript to Python Migration Script
# Follows the implementation plan in docs/typescript_to_python_migration_plan.md

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Create directory structure
mkdir -p scripts/ts_analysis
mkdir -p scripts/ts_conversion
mkdir -p logs/migration

# Track start time
START_TIME=$(date +%s)

# Timestamp for logs
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="logs/migration/migration_${TIMESTAMP}.log"

# Helper function to log messages
log() {
    local msg=$1
    local level=${2:-INFO}
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} [${level}] ${msg}" | tee -a "$LOG_FILE"
}

# Step 1: Create inventory of TypeScript files
step1_create_inventory() {
    log "${BLUE}STEP 1: Creating inventory of TypeScript files${RESET}" "STEP"
    
    # Find TypeScript files and save to inventory
    log "Finding TypeScript files..."
    find . -name "*.ts" | grep -v "node_modules\|dist\|build\|\.git" > scripts/ts_conversion/ts_files_inventory.txt
    
    # Count files
    FILE_COUNT=$(wc -l < scripts/ts_conversion/ts_files_inventory.txt)
    log "${GREEN}Found ${FILE_COUNT} TypeScript files${RESET}" "SUCCESS"
    
    # Analyze files
    log "Analyzing TypeScript files..."
    python scripts/analyze_ts_dependencies.py
    
    # Check if analysis was successful
    if [[ $? -eq 0 ]]; then
        log "${GREEN}Analysis complete. Results in scripts/ts_analysis/...${RESET}" "SUCCESS"
    else
        log "${RED}Analysis failed${RESET}" "ERROR"
        exit 1
    fi
}

# Step 2: Create migration batches by complexity
step2_create_batches() {
    log "${BLUE}STEP 2: Creating migration batches by complexity${RESET}" "STEP"
    
    # Directory for batches
    mkdir -p scripts/ts_conversion/batches
    
    # Parse CSV to create batches 
    log "Creating batches based on complexity..."
    python -c '
import csv
from collections import defaultdict

# Load analysis CSV
batches = defaultdict(list)
with open("scripts/ts_analysis/ts_analysis.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        path = row["path"]
        complexity = float(row["complexity"])
        
        # Skip .d.ts files
        if path.endswith(".d.ts"):
            continue
            
        # Assign to batch based on complexity
        if complexity < 2:
            batches["01_low_complexity"].append(path)
        elif complexity < 5:
            batches["02_medium_complexity"].append(path)
        elif complexity < 10:
            batches["03_high_complexity"].append(path)
        else:
            batches["04_very_high_complexity"].append(path)

# Save batches to files
for batch_name, files in batches.items():
    with open(f"scripts/ts_conversion/batches/{batch_name}.txt", "w") as f:
        for file_path in files:
            f.write(f"{file_path}\n")
    print(f"Created batch {batch_name} with {len(files)} files")
'
    
    # Count files in each batch
    log "Batch statistics:"
    for batch_file in scripts/ts_conversion/batches/*.txt; do
        COUNT=$(wc -l < "$batch_file")
        BATCH_NAME=$(basename "$batch_file")
        log "  - ${BATCH_NAME%.txt}: ${COUNT} files"
    done
    
    log "${GREEN}Batches created successfully${RESET}" "SUCCESS"
}

# Step 3: Run conversions for each batch
step3_run_conversions() {
    log "${BLUE}STEP 3: Running conversions${RESET}" "STEP"
    
    # Create output directory
    mkdir -p python_converted
    
    # Convert each batch
    for batch_file in scripts/ts_conversion/batches/*.txt; do
        BATCH_NAME=$(basename "$batch_file" .txt)
        log "Processing batch: ${BATCH_NAME}..."
        
        # Run the conversion
        python scripts/ts2py.py --batch "$batch_file" --output-dir python_converted
        
        # Check result
        if [[ $? -eq 0 ]]; then
            log "${GREEN}Batch ${BATCH_NAME} converted successfully${RESET}" "SUCCESS"
        else
            log "${YELLOW}Some files in batch ${BATCH_NAME} failed to convert${RESET}" "WARNING"
        fi
    done
    
    # Count converted files
    CONVERTED_COUNT=$(find python_converted -name "*.py" | wc -l)
    log "Converted ${CONVERTED_COUNT} files to Python"
}

# Step 4: Convert TypeScript files to Python
step4_convert_typescript_to_python() {
    log "Step 4: Converting TypeScript files to Python" "INFO"
    
    # Create output directory
    mkdir -p python_converted
    
    # Check if we have previously-generated batch files
    if [ -d "scripts/ts_conversion/batches" ]; then
        batch_count=$(ls -1 scripts/ts_conversion/batches/*.txt 2>/dev/null | wc -l)
        
        if [ "$batch_count" -gt 0 ]; then
            log "Found $batch_count batch files for conversion" "INFO"
            
            # Convert each batch
            for batch_file in scripts/ts_conversion/batches/*.txt; do
                batch_name=$(basename "$batch_file" .txt)
                output_dir="python_converted/${batch_name}"
                
                log "Converting batch $batch_name to $output_dir" "INFO"
                python scripts/ts2py.py --batch "$batch_file" --output-dir "$output_dir"
                
                # Fix common issues in the converted files
                log "Fixing common issues in $output_dir" "INFO"
                python scripts/fix_py_conversions.py --dir "$output_dir"
            done
        else
            # No batch files, create default batches
            log "No batch files found, creating default batches" "INFO"
            mkdir -p scripts/ts_conversion/batches
            
            # Create batches by directory pattern to limit batch size
            log "Creating batch: models" "INFO"
            find . -name "*.ts" | grep -v "node_modules" | grep -v "dist" | grep -v ".d.ts" | grep "/models/" > scripts/ts_conversion/batches/models.txt
            
            log "Creating batch: types" "INFO"
            find . -name "*.ts" | grep -v "node_modules" | grep -v "dist" | grep -v ".d.ts" | grep "/types/" > scripts/ts_conversion/batches/types.txt
            
            log "Creating batch: services" "INFO"
            find . -name "*.ts" | grep -v "node_modules" | grep -v "dist" | grep -v ".d.ts" | grep "/services/" > scripts/ts_conversion/batches/services.txt
            
            log "Creating batch: utils" "INFO"
            find . -name "*.ts" | grep -v "node_modules" | grep -v "dist" | grep -v ".d.ts" | grep "/utils/" > scripts/ts_conversion/batches/utils.txt
            
            log "Creating batch: components" "INFO"
            find . -name "*.ts" | grep -v "node_modules" | grep -v "dist" | grep -v ".d.ts" | grep "/components/" > scripts/ts_conversion/batches/components.txt
            
            # Convert each batch
            for batch_file in scripts/ts_conversion/batches/*.txt; do
                batch_name=$(basename "$batch_file" .txt)
                output_dir="python_converted/${batch_name}"
                
                log "Converting batch $batch_name to $output_dir" "INFO"
                python scripts/ts2py.py --batch "$batch_file" --output-dir "$output_dir"
                
                # Fix common issues in the converted files
                log "Fixing common issues in $output_dir" "INFO"
                python scripts/fix_py_conversions.py --dir "$output_dir"
            done
        fi
    else
        # No batch directory, create it
        mkdir -p scripts/ts_conversion/batches
        
        # Create a single batch file with all TypeScript files (limited to first 100)
        log "Creating a single batch with all TypeScript files (limited to 100)" "INFO"
        find . -name "*.ts" | grep -v "node_modules" | grep -v "dist" | grep -v ".d.ts" | head -n 100 > scripts/ts_conversion/batches/all.txt
        
        # Convert the batch
        log "Converting batch all to python_converted/all" "INFO"
        python scripts/ts2py.py --batch scripts/ts_conversion/batches/all.txt --output-dir python_converted/all
        
        # Fix common issues in the converted files
        log "Fixing common issues in python_converted/all" "INFO"
        python scripts/fix_py_conversions.py --dir python_converted/all
    fi
    
    log "TypeScript to Python conversion complete" "INFO"
}

# Step 5: Generate conversion report
step5_generate_report() {
    log "${BLUE}STEP 5: Generating conversion report${RESET}" "STEP"
    
    # Count files
    TS_COUNT=$(wc -l < scripts/ts_conversion/ts_files_inventory.txt)
    PY_COUNT=$(find python_converted -name "*.py" | wc -l)
    SUCCESS_RATE=$(echo "scale=2; ($PY_COUNT / $TS_COUNT) * 100" | bc)
    
    # Time elapsed
    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))
    HOURS=$((ELAPSED / 3600))
    MINUTES=$(( (ELAPSED % 3600) / 60 ))
    SECONDS=$((ELAPSED % 60))
    
    # Generate report
    REPORT_FILE="logs/migration/conversion_report_${TIMESTAMP}.md"
    
    cat > "$REPORT_FILE" <<EOF
# TypeScript to Python Conversion Report

**Date:** $(date +"%Y-%m-%d %H:%M:%S")
**Duration:** ${HOURS}h ${MINUTES}m ${SECONDS}s

## Summary

* Total TypeScript files: ${TS_COUNT}
* Successfully converted: ${PY_COUNT}
* Success rate: ${SUCCESS_RATE}%

## Conversion Details

| Batch | Files | Success | Failure |
|-------|-------|---------|---------|
EOF
    
    # Add batch details
    for batch_file in scripts/ts_conversion/batches/*.txt; do
        BATCH_NAME=$(basename "$batch_file" .txt)
        TS_FILES=$(wc -l < "$batch_file")
        
        # Count converted files from this batch
        CONVERTED=0
        while read -r ts_file; do
            py_file="python_converted/$(echo "$ts_file" | sed 's/\.ts$/.py/')"
            if [[ -f "$py_file" ]]; then
                CONVERTED=$((CONVERTED + 1))
            fi
        done < "$batch_file"
        
        FAILED=$((TS_FILES - CONVERTED))
        SUCCESS_PCT=$(echo "scale=2; ($CONVERTED / $TS_FILES) * 100" | bc)
        
        echo "| ${BATCH_NAME} | ${TS_FILES} | ${CONVERTED} (${SUCCESS_PCT}%) | ${FAILED} |" >> "$REPORT_FILE"
    done
    
    # Add next steps
    cat >> "$REPORT_FILE" <<EOF

## Next Steps

1. Review converted Python files for correctness
2. Implement manual fixes for failed conversions
3. Run tests to verify functionality
4. Update import statements and dependencies
5. Remove original TypeScript files once verified

## Common Conversion Issues

- Complex type definitions
- Decorators and advanced TypeScript features
- React/UI components
- External library dependencies

EOF
    
    log "${GREEN}Report generated: ${REPORT_FILE}${RESET}" "SUCCESS"
}

# Main execution
main() {
    log "Starting TypeScript to Python migration" "INFO"
    
    # Execute steps in order
    step1_create_inventory
    step2_create_batches
    step3_run_conversions
    step4_convert_typescript_to_python
    step5_generate_report
    
    # Report completion
    log "Migration process completed successfully" "SUCCESS"
    log "Converted Python files are in the 'python_converted/' directory" "INFO"
    log "Please review and integrate these files into your backend structure" "INFO"
}

main "$@" 