#!/bin/bash

# Script to remove redundant modules after consolidation (non-interactive version)
# This automatically removes modules that have been consolidated

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
ARCHIVE_DIR="/Users/Sharrone/Visual_DM/archived_modules/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/Users/Sharrone/Visual_DM/module_removal_log.md"

# Create archive directory
mkdir -p "$ARCHIVE_DIR"

# Initialize log
echo "# Redundant Module Removal Log" > "$LOG_FILE"
echo "Generated on $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# List of modules to remove (these should have been consolidated into others)
declare -a REDUNDANT_MODULES=(
  "NPCs"
  "NPC"
  "Factions"
  "Quests"
  "TimeSystem"
  "Legacy"  # Assuming Legacy is no longer needed
)

# Function to archive and remove a module
archive_module() {
  local module_name=$1
  local source_dir="$MODULES_DIR/$module_name"
  local archive_dir="$ARCHIVE_DIR/$module_name"
  
  if [ ! -d "$source_dir" ]; then
    echo "Module $module_name does not exist, skipping"
    echo "- Module not found: $module_name" >> "$LOG_FILE"
    return
  fi
  
  # Archive the module first
  echo "Archiving $module_name to $archive_dir"
  mkdir -p "$archive_dir"
  cp -r "$source_dir"/* "$archive_dir"/ 2>/dev/null || true
  
  # Count files for logging
  file_count=$(find "$source_dir" -type f -name "*.cs" | wc -l | tr -d ' ')
  
  # Remove the module
  echo "Removing module $module_name"
  rm -rf "$source_dir"
  
  # Log the operation
  echo "- Archived and removed module: $module_name ($file_count C# files)" >> "$LOG_FILE"
}

echo "WARNING: This script will remove the following modules:"
printf "  - %s\n" "${REDUNDANT_MODULES[@]}"
echo "These should have been consolidated into other modules."
echo "Files will be archived to $ARCHIVE_DIR before removal."
echo ""
echo "Proceeding automatically in 5 seconds..."
sleep 5

# Process each redundant module
for module in "${REDUNDANT_MODULES[@]}"; do
  archive_module "$module"
done

echo "Module removal complete."
echo "- Archive created at: $ARCHIVE_DIR"
echo "- Log file: $LOG_FILE"
echo ""
echo "IMPORTANT: You should test your project thoroughly after this operation."
echo "If you need to restore any modules, they are available in the archive." 