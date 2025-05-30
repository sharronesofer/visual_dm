#!/bin/bash

# Script to identify, compare, and migrate test files from system directories to the centralized test directory
# Author: AI Assistant
# Date: $(date +%Y-%m-%d)

echo "=== Visual DM Test Migration Tool ==="
echo "This script identifies test files in system directories and moves or updates them in the centralized test structure."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file setup
LOG_FILE="test_migration_log.md"
echo "# Test Migration Log - $(date)" > $LOG_FILE
echo "" >> $LOG_FILE
echo "This log records the actions taken during test file migration." >> $LOG_FILE
echo "" >> $LOG_FILE

# Dry run mode - set to true to preview changes without making them
DRY_RUN=false

# Function to check if two files are identical
compare_files() {
    local source_file=$1
    local target_file=$2
    
    if [ -f "$target_file" ]; then
        if cmp -s "$source_file" "$target_file"; then
            echo -e "${GREEN}IDENTICAL${NC}: $source_file and $target_file are identical"
            echo "- ✅ **IDENTICAL**: \`$source_file\` and \`$target_file\` are identical" >> $LOG_FILE
            return 0
        else
            echo -e "${YELLOW}DIFFERENT${NC}: $source_file and $target_file have differences"
            echo "- ⚠️ **DIFFERENT**: \`$source_file\` and \`$target_file\` have differences" >> $LOG_FILE
            # Show a brief diff summary
            echo -e "${YELLOW}DIFF:${NC}"
            diff -u --color "$source_file" "$target_file" | head -n 20
            return 1
        fi
    else
        echo -e "${BLUE}NEW${NC}: $target_file does not exist yet"
        echo "- 🆕 **NEW**: \`$target_file\` does not exist yet" >> $LOG_FILE
        return 2
    fi
}

# Function to ensure a directory exists
ensure_directory() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        echo -e "${BLUE}Creating directory${NC}: $dir"
        echo "- 📁 Created directory: \`$dir\`" >> $LOG_FILE
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$dir"
        fi
    fi
}

# Function to migrate a file
migrate_file() {
    local source_file=$1
    local target_file=$2
    local action=$3 # "copy" or "remove"
    
    case $action in
        "copy")
            echo -e "${GREEN}Copying${NC}: $source_file -> $target_file"
            echo "- 📋 Copied: \`$source_file\` -> \`$target_file\`" >> $LOG_FILE
            if [ "$DRY_RUN" = false ]; then
                cp "$source_file" "$target_file"
            fi
            ;;
        "remove")
            echo -e "${RED}Removing${NC}: $source_file (already exists in target location)"
            echo "- 🗑️ Removed: \`$source_file\` (already exists in target location)" >> $LOG_FILE
            if [ "$DRY_RUN" = false ]; then
                rm "$source_file"
            fi
            ;;
        *)
            echo -e "${RED}Unknown action${NC}: $action"
            echo "- ❌ Unknown action: $action" >> $LOG_FILE
            ;;
    esac
}

# Function to count lines in a file
count_lines() {
    wc -l < "$1" | tr -d ' '
}

# Function to determine if one file is more complete than another
is_more_complete() {
    local file1=$1
    local file2=$2
    local count1=$(count_lines "$file1")
    local count2=$(count_lines "$file2")
    
    # If file1 has at least 10% more lines than file2, consider it more complete
    local threshold=$(echo "$count2 * 1.1" | bc -l)
    if (( $(echo "$count1 > $threshold" | bc -l) )); then
        return 0
    else
        return 1
    fi
}

# Function to capitalize the first letter of each word
capitalize() {
    local string="$1"
    echo "$(tr '_' ' ' <<< "$string" | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1')"
}

# Generate a summary for systems with tests
generate_system_summary() {
    local system_name=$1
    local target_dir=$2
    local system_title=$(capitalize "$system_name")
    
    if [ -f "$target_dir/README.md" ] && [ -s "$target_dir/README.md" ]; then
        echo -e "${BLUE}README already exists${NC}: $target_dir/README.md"
        echo "- ℹ️ README already exists: \`$target_dir/README.md\`" >> $LOG_FILE
        return
    fi
    
    echo -e "${BLUE}Generating README${NC}: $target_dir/README.md"
    echo "- 📝 Generated README: \`$target_dir/README.md\`" >> $LOG_FILE
    
    # Create file entries
    local file_entries=""
    if [ -d "$target_dir" ]; then
        for test_file in "$target_dir"/test_*.py; do
            if [ -f "$test_file" ]; then
                local filename=$(basename "$test_file")
                # Extract a brief description from the file's docstring if available
                local description=$(grep -m 1 -A 1 '"""' "$test_file" | tail -1 | sed 's/^[[:space:]]*//')
                if [ -z "$description" ]; then
                    description="Tests for the ${system_name} system"
                fi
                file_entries="${file_entries}- \`$filename\`: $description\n"
            fi
        done
    fi
    
    # Create README with proper variable substitution
    if [ "$DRY_RUN" = false ]; then
        {
            echo "# ${system_title} System Tests"
            echo ""
            echo "This directory contains tests for the ${system_name} system."
            echo ""
            echo "## Test Files"
            echo ""
            echo -e "$file_entries"
            echo "## Running Tests"
            echo ""
            echo "Tests are run as part of the standard test suite. You can also run them individually:"
            echo ""
            echo "\`\`\`bash"
            echo "# Run all ${system_name} tests"
            echo "pytest backend/tests/systems/${system_name}/"
            echo ""
            echo "# Run a specific test file"
            echo "pytest backend/tests/systems/${system_name}/test_file.py"
            echo "\`\`\`"
        } > "$target_dir/README.md"
    fi
}

# Main function to process a system's tests
process_system_tests() {
    local system_name=$1
    local source_dir="backend/systems/$system_name/tests"
    local target_dir="backend/tests/systems/$system_name"
    local system_title=$(capitalize "$system_name")
    
    if [ ! -d "$source_dir" ]; then
        # No tests directory in this system
        return
    fi
    
    echo -e "\n${BLUE}=== Processing $system_name system tests ===${NC}"
    echo -e "\n## $system_title System Tests" >> $LOG_FILE
    
    # Make sure the target directory exists
    ensure_directory "$target_dir"
    
    # Process each test file
    for source_file in "$source_dir"/test_*.py; do
        if [ -f "$source_file" ]; then
            filename=$(basename "$source_file")
            target_file="$target_dir/$filename"
            
            # Compare files
            compare_files "$source_file" "$target_file"
            comparison_result=$?
            
            if [ $comparison_result -eq 0 ]; then
                # Files are identical, can remove the source
                migrate_file "$source_file" "$target_file" "remove"
            elif [ $comparison_result -eq 2 ]; then
                # Target doesn't exist, copy the source
                migrate_file "$source_file" "$target_file" "copy"
            else
                # Files are different
                echo -e "${YELLOW}WARNING${NC}: Manual review needed for $source_file and $target_file"
                echo "- ⚠️ **WARNING**: Manual review needed for \`$source_file\` and \`$target_file\`" >> $LOG_FILE
                
                # Check if one file is significantly more complete than the other
                if is_more_complete "$source_file" "$target_file"; then
                    echo -e "${YELLOW}SOURCE APPEARS MORE COMPLETE${NC} - recommend reviewing and updating target"
                    echo "- 📊 Source file appears more complete than target" >> $LOG_FILE
                elif is_more_complete "$target_file" "$source_file"; then
                    echo -e "${YELLOW}TARGET APPEARS MORE COMPLETE${NC} - recommend removing source after review"
                    echo "- 📊 Target file appears more complete than source" >> $LOG_FILE
                fi
            fi
        fi
    done
    
    # Check for __init__.py and copy if needed
    if [ -f "$source_dir/__init__.py" ] && [ ! -f "$target_dir/__init__.py" ]; then
        echo -e "${BLUE}Copying __init__.py${NC}"
        echo "- 📋 Copied: \`$source_dir/__init__.py\` -> \`$target_dir/__init__.py\`" >> $LOG_FILE
        if [ "$DRY_RUN" = false ]; then
            cp "$source_dir/__init__.py" "$target_dir/__init__.py"
        fi
    elif [ ! -f "$target_dir/__init__.py" ]; then
        # Create a basic __init__.py file
        echo -e "${BLUE}Creating __init__.py${NC}"
        echo "- 📝 Created: \`$target_dir/__init__.py\`" >> $LOG_FILE
        if [ "$DRY_RUN" = false ]; then
            echo '"""Tests for the '$system_name' system."""' > "$target_dir/__init__.py"
        fi
    fi
    
    # Generate a summary README for the system
    generate_system_summary "$system_name" "$target_dir"
    
    # Check if source directory is now empty (except for README/documentation)
    if [ ! "$(find "$source_dir" -maxdepth 1 -name 'test_*.py' -print -quit)" ]; then
        echo -e "${GREEN}All test files migrated${NC} from $source_dir"
        echo "- ✅ All test files migrated from \`$source_dir\`" >> $LOG_FILE
        
        # We can remove the directory or leave a README explaining where tests moved
        if [ -f "$source_dir/README.md" ] || [ "$DRY_RUN" = true ]; then
            echo -e "${BLUE}Updating README${NC} in $source_dir"
            echo "- 📝 Updated README in \`$source_dir\`" >> $LOG_FILE
            if [ "$DRY_RUN" = false ]; then
                {
                    echo "# ${system_title} System Tests"
                    echo ""
                    echo "## NOTICE: Tests Relocated"
                    echo ""
                    echo "The test files that were previously in this directory have been moved to the centralized test structure:"
                    echo ""
                    echo "\`\`\`"
                    echo "backend/tests/systems/${system_name}/"
                    echo "\`\`\`"
                    echo ""
                    echo "Please update any references to these test files."
                } > "$source_dir/README.md"
            fi
        fi
    fi
}

# Main script execution
echo "Starting test migration..."
echo "## Migration Summary" >> $LOG_FILE
echo "" >> $LOG_FILE

# Check if we're in dry run mode
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}DRY RUN MODE${NC} - No changes will be made"
    echo "- ⚠️ **DRY RUN MODE** - No changes will be made" >> $LOG_FILE
fi

# Get list of all systems
systems=$(ls -d backend/systems/*/ | cut -d'/' -f3)

# Process each system's tests
for system in $systems; do
    process_system_tests "$system"
done

echo -e "\n${GREEN}Test migration complete!${NC}"
echo -e "See $LOG_FILE for a complete log of actions taken."
echo -e "\n## Conclusion" >> $LOG_FILE
echo -e "Test migration completed on $(date)" >> $LOG_FILE 