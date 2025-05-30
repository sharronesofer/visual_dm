#!/bin/bash

# Script to move consolidated files to their proper target modules
# This script moves merged files from the Consolidated directory to their target modules

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
CONSOLIDATED_DIR="$MODULES_DIR/Consolidated"
LOG_FILE="/Users/Sharrone/Visual_DM/move_consolidated_log.md"

# Initialize log
echo "# Consolidated Files Movement Log" > "$LOG_FILE"
echo "Generated on $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Map of consolidated files to target modules
# Format: "filename:target_module"
declare -a FILE_MAPPINGS=(
  "Factions_Faction_FactionArc.cs:Faction"
  "Quests_Quest_QuestManager.cs:Quest"
  "Quests_Quest_QuestSystemTests.cs:Quest"
)

# Function to move a consolidated file to its target module
move_consolidated_file() {
  local source_file="$CONSOLIDATED_DIR/$1"
  local target_module="$MODULES_DIR/$2"
  local target_filename=$(echo "$1" | sed 's/.*_\([^_]*\)\.cs$/\1.cs/')
  
  # Skip if source file doesn't exist
  if [ ! -f "$source_file" ]; then
    echo "Warning: Source file $source_file not found. Skipping."
    echo "- Warning: Source file $1 not found. Skipping." >> "$LOG_FILE"
    return
  fi
  
  # Create target module directory if it doesn't exist
  if [ ! -d "$target_module" ]; then
    echo "Creating target module directory: $target_module"
    mkdir -p "$target_module"
    echo "- Created target module directory: $2" >> "$LOG_FILE"
  fi
  
  # Move/copy the file
  echo "Moving $1 to $2/$target_filename"
  cp "$source_file" "$target_module/$target_filename"
  
  # Log the operation
  echo "- Moved consolidated file: $1 → $2/$target_filename" >> "$LOG_FILE"
}

echo "Moving consolidated files to their target modules..."

# Process each file mapping
for mapping in "${FILE_MAPPINGS[@]}"; do
  # Split the mapping
  IFS=':' read -r source_file target_module <<< "$mapping"
  
  move_consolidated_file "$source_file" "$target_module"
done

echo "File movement complete."
echo "- Log file: $LOG_FILE"
echo ""
echo "Next steps:"
echo "1. Review the target modules to ensure files are properly integrated"
echo "2. Test the functionality of the target modules"
echo "3. Run the remove_redundant_modules.sh script when you're confident everything works" 