#!/bin/bash

# Restructure directories script for Visual DM project
# This script reorganizes the project directory structure
# to consolidate duplicate files and create a cleaner organization.

set -e  # Exit on any error

# Display colorful heading
print_heading() {
    echo -e "\e[1;34m==== $1 ====\e[0m"
}

# Display step information
print_step() {
    echo -e "\e[0;32m>> $1\e[0m"
}

# Display warning
print_warning() {
    echo -e "\e[0;33mWARNING: $1\e[0m"
}

# Display error and exit
print_error() {
    echo -e "\e[0;31mERROR: $1\e[0m"
    exit 1
}

# Parse arguments
PROJECT_ROOT="$1"
if [ -z "$PROJECT_ROOT" ]; then
    print_error "Project root directory not specified. Usage: ./restructure_directories.sh <project_root>"
fi

# Get absolute path
PROJECT_ROOT=$(realpath "$PROJECT_ROOT")

print_heading "Visual DM Directory Restructuring"
echo "Project root: $PROJECT_ROOT"

# Create timestamp for backups
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$PROJECT_ROOT/backups/restructure_${TIMESTAMP}"

# Create backup
print_step "Creating backup in $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Check for Unity project structure 
if [ ! -d "$PROJECT_ROOT/VDM/Assets" ]; then
    print_error "Unity project directory not found at $PROJECT_ROOT/VDM/Assets"
fi

# Create the consolidated directories structure
print_step "Creating consolidated directory structure"

# Create Unity consolidated directories
mkdir -p "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Managers"
mkdir -p "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Core"
mkdir -p "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/UI"
mkdir -p "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Data"
mkdir -p "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Utils"
mkdir -p "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Events"

# Create Python consolidated directories
mkdir -p "$PROJECT_ROOT/backend/modules/core"
mkdir -p "$PROJECT_ROOT/backend/modules/api"
mkdir -p "$PROJECT_ROOT/backend/modules/data"
mkdir -p "$PROJECT_ROOT/backend/modules/utils"

# Create meta files for Unity directories (if needed)
touch "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated.meta"
touch "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Managers.meta"
touch "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Core.meta" 
touch "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/UI.meta"
touch "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Data.meta"
touch "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Utils.meta"
touch "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated/Events.meta"

# Backup original directories if they exist
if [ -d "$PROJECT_ROOT/VDM/Assets/VisualDM" ]; then
    print_step "Backing up Assets/VisualDM directory"
    cp -r "$PROJECT_ROOT/VDM/Assets/VisualDM" "$BACKUP_DIR/"
fi

# Function to copy consolidated files based on the merge plan
apply_merge_plan() {
    local merge_plan="$PROJECT_ROOT/scripts/consolidation/merge_plan.json"
    if [ ! -f "$merge_plan" ]; then
        print_warning "Merge plan not found at $merge_plan. Skipping file copy operations."
        return 1
    fi
    
    print_step "Applying merge plan from $merge_plan"
    
    # Use Python to extract and copy files based on the merge plan
    python3 -c "
import json
import os
import shutil

merge_plan_file = '$merge_plan'
project_root = '$PROJECT_ROOT'

with open(merge_plan_file, 'r') as f:
    plan = json.load(f)

# Get the merge operations
operations = plan.get('merge_operations', {})
copied_files = []

for source_file, info in operations.items():
    # Ensure source file path is relative to project root
    if not source_file.startswith('/'):
        source_path = os.path.join(project_root, source_file)
    else:
        source_path = source_file
    
    # Determine destination based on file type
    language = info.get('language', '')
    file_type = info.get('type', '')
    
    if language == 'cs':
        # C# file - determine appropriate subdirectory
        if file_type == 'manager_duplicate':
            dest_dir = os.path.join(project_root, 'VDM/Assets/Scripts/VisualDM/Consolidated/Managers')
        elif file_type == 'singleton_duplicate':
            dest_dir = os.path.join(project_root, 'VDM/Assets/Scripts/VisualDM/Consolidated/Core')
        elif 'UI' in source_file or 'Interface' in source_file:
            dest_dir = os.path.join(project_root, 'VDM/Assets/Scripts/VisualDM/Consolidated/UI')
        elif 'Data' in source_file or 'Model' in source_file:
            dest_dir = os.path.join(project_root, 'VDM/Assets/Scripts/VisualDM/Consolidated/Data')
        elif 'Event' in source_file:
            dest_dir = os.path.join(project_root, 'VDM/Assets/Scripts/VisualDM/Consolidated/Events')
        elif 'Util' in source_file or 'Helper' in source_file:
            dest_dir = os.path.join(project_root, 'VDM/Assets/Scripts/VisualDM/Consolidated/Utils')
        else:
            dest_dir = os.path.join(project_root, 'VDM/Assets/Scripts/VisualDM/Consolidated/Core')
    
    elif language == 'python':
        # Python file - determine appropriate subdirectory
        if 'api' in source_file:
            dest_dir = os.path.join(project_root, 'backend/modules/api')
        elif 'data' in source_file or 'model' in source_file:
            dest_dir = os.path.join(project_root, 'backend/modules/data')
        elif 'util' in source_file or 'helper' in source_file:
            dest_dir = os.path.join(project_root, 'backend/modules/utils')
        else:
            dest_dir = os.path.join(project_root, 'backend/modules/core')
    else:
        # Unknown file type - skip
        continue
    
    # Ensure destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    
    # Extract filename
    filename = os.path.basename(source_path)
    dest_path = os.path.join(dest_dir, filename)
    
    # Copy the file
    try:
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            copied_files.append((source_file, dest_path))
            print(f'Copied {source_file} to {dest_path}')
        else:
            print(f'Source file not found: {source_path}')
    except Exception as e:
        print(f'Error copying {source_path}: {e}')

print(f'Copied {len(copied_files)} files according to merge plan')

# Generate meta files for Unity files if needed
for _, dest_path in copied_files:
    if dest_path.endswith('.cs'):
        meta_path = dest_path + '.meta'
        if not os.path.exists(meta_path):
            # Create a basic meta file if needed
            with open(meta_path, 'w') as meta_file:
                meta_file.write('fileFormatVersion: 2\\nguid: ' + os.urandom(16).hex() + '\\nMonoImporter:\\n  externalObjects: {}\\n  serializedVersion: 2\\n  defaultReferences: []\\n  executionOrder: 0\\n  icon: {instanceID: 0}\\n  userData: \\n  assetBundleName: \\n  assetBundleVariant: \\n')
"
}

# Clean up deprecated or duplicate directories
cleanup_directories() {
    print_step "Cleaning up duplicate directories"
    
    # Identify duplicate directories from the analysis
    # We'll only remove empty directories or directories that have been consolidated
    
    # Check if /VDM/Assets/VisualDM is redundant with /VDM/Assets/Scripts/VisualDM
    if [ -d "$PROJECT_ROOT/VDM/Assets/VisualDM" ] && [ -d "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM" ]; then
        # Count files in Assets/VisualDM that are not in the consolidated directory
        non_consolidated_files=$(find "$PROJECT_ROOT/VDM/Assets/VisualDM" -type f -name "*.cs" | grep -v "Consolidated" | wc -l)
        
        if [ "$non_consolidated_files" -eq 0 ]; then
            print_step "Assets/VisualDM appears to be fully consolidated. Creating backup and replacing with symbolic link"
            # Backup the directory if not already done
            if [ ! -d "$BACKUP_DIR/Assets/VisualDM" ]; then
                mkdir -p "$BACKUP_DIR/Assets"
                cp -r "$PROJECT_ROOT/VDM/Assets/VisualDM" "$BACKUP_DIR/Assets/"
            fi
            
            # Remove the directory and create a symbolic link
            rm -rf "$PROJECT_ROOT/VDM/Assets/VisualDM"
            ln -s "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM" "$PROJECT_ROOT/VDM/Assets/VisualDM"
            echo "Created symbolic link from Assets/Scripts/VisualDM to Assets/VisualDM"
        else
            print_warning "Assets/VisualDM contains $non_consolidated_files non-consolidated files. Not replacing with symbolic link."
        fi
    fi
}

# Update .gitignore to exclude consolidated backups
update_gitignore() {
    print_step "Updating .gitignore to exclude consolidation backups"
    
    if [ -f "$PROJECT_ROOT/.gitignore" ]; then
        if ! grep -q "# Consolidation backups" "$PROJECT_ROOT/.gitignore"; then
            echo -e "\n# Consolidation backups\nbackups/\n" >> "$PROJECT_ROOT/.gitignore"
            echo "Added consolidation backups to .gitignore"
        fi
    else
        echo "# Consolidation backups\nbackups/\n" > "$PROJECT_ROOT/.gitignore"
        echo "Created .gitignore with consolidation backups"
    fi
}

# Generate summary report
generate_summary() {
    print_step "Generating directory restructuring summary"
    
    summary_file="$PROJECT_ROOT/scripts/directory_restructure_summary.md"
    
    echo "# Directory Restructuring Summary" > "$summary_file"
    echo "" >> "$summary_file"
    echo "Date: $(date)" >> "$summary_file"
    echo "Backup created at: $BACKUP_DIR" >> "$summary_file"
    echo "" >> "$summary_file"
    
    echo "## Consolidated Directories" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "### C# Code" >> "$summary_file"
    echo "- /VDM/Assets/Scripts/VisualDM/Consolidated/Managers - Manager classes" >> "$summary_file"
    echo "- /VDM/Assets/Scripts/VisualDM/Consolidated/Core - Core classes and singletons" >> "$summary_file"
    echo "- /VDM/Assets/Scripts/VisualDM/Consolidated/UI - UI-related classes" >> "$summary_file"
    echo "- /VDM/Assets/Scripts/VisualDM/Consolidated/Data - Data models and structures" >> "$summary_file"
    echo "- /VDM/Assets/Scripts/VisualDM/Consolidated/Utils - Utility classes and helpers" >> "$summary_file"
    echo "- /VDM/Assets/Scripts/VisualDM/Consolidated/Events - Event-related classes" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "### Python Code" >> "$summary_file"
    echo "- /backend/modules/core - Core Python modules" >> "$summary_file"
    echo "- /backend/modules/api - API-related modules" >> "$summary_file"
    echo "- /backend/modules/data - Data-related modules" >> "$summary_file"
    echo "- /backend/modules/utils - Utility modules" >> "$summary_file"
    echo "" >> "$summary_file"
    
    # Add file counts
    echo "## File Counts" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "- C# consolidated files: $(find "$PROJECT_ROOT/VDM/Assets/Scripts/VisualDM/Consolidated" -type f -name "*.cs" | wc -l)" >> "$summary_file"
    echo "- Python consolidated files: $(find "$PROJECT_ROOT/backend/modules" -type f -name "*.py" | wc -l)" >> "$summary_file"
    echo "" >> "$summary_file"
    
    echo "## Next Steps" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "1. Review the consolidated files in their new locations" >> "$summary_file"
    echo "2. Update any Unity references to use the consolidated assets" >> "$summary_file"
    echo "3. Update import statements in Python code to use the new module structure" >> "$summary_file"
    echo "4. Run automated tests to verify the consolidation hasn't broken functionality" >> "$summary_file"
    echo "" >> "$summary_file"
    
    echo "Directory restructuring summary written to $summary_file"
}

# Execute the main functions
apply_merge_plan
cleanup_directories
update_gitignore
generate_summary

print_heading "Directory Restructuring Complete"
echo "See $PROJECT_ROOT/scripts/directory_restructure_summary.md for details"
echo "Backup of original directories is available at $BACKUP_DIR" 