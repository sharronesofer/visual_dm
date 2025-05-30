#!/bin/bash

# Script to verify that all functionality has been preserved during consolidation
# This script checks that all source files have a counterpart either in the target module or consolidated directory

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
BACKUP_DIR="/Users/Sharrone/Visual_DM/module_backups"
CONSOLIDATED_DIR="$MODULES_DIR/Consolidated"
VERIFICATION_LOG="/Users/Sharrone/Visual_DM/consolidation_verification.md"

# Initialize log
echo "# Consolidation Verification Log" > "$VERIFICATION_LOG"
echo "Generated on $(date)" >> "$VERIFICATION_LOG"
echo "" >> "$VERIFICATION_LOG"

# Module pairs to check (source:target)
declare -a MODULE_PAIRS=(
  "NPCs:Characters"
  "NPC:Characters"
  "Factions:Faction"
  "Quests:Quest"
  "TimeSystem:Time"
  "WorldGen:World"
)

# Get the most recent backup directory
LATEST_BACKUP=$(find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d | sort -r | head -1)

if [ -z "$LATEST_BACKUP" ]; then
  echo "Error: No backup directory found in $BACKUP_DIR"
  echo "- Error: No backup directory found in $BACKUP_DIR" >> "$VERIFICATION_LOG"
  exit 1
fi

echo "Using backup directory: $LATEST_BACKUP"
echo "- Using backup directory: $LATEST_BACKUP" >> "$VERIFICATION_LOG"
echo "" >> "$VERIFICATION_LOG"

# Function to verify all source files are accounted for
verify_module_pair() {
  local source_module=$1
  local target_module=$2
  local source_backup="$LATEST_BACKUP/$source_module"
  local target_dir="$MODULES_DIR/$target_module"
  
  echo "## Verifying $source_module → $target_module" >> "$VERIFICATION_LOG"
  echo "" >> "$VERIFICATION_LOG"
  
  # Skip if source backup doesn't exist
  if [ ! -d "$source_backup" ]; then
    echo "Warning: Source backup $source_backup not found. Skipping."
    echo "- Warning: Source backup $source_module not found. Skipping." >> "$VERIFICATION_LOG"
    echo "" >> "$VERIFICATION_LOG"
    return
  fi
  
  # Count source files
  local source_files=$(find "$source_backup" -type f -name "*.cs" | sort)
  local source_count=$(echo "$source_files" | wc -l | tr -d ' ')
  
  echo "- Source module ($source_module) files: $source_count" >> "$VERIFICATION_LOG"
  
  # Initialize counters
  local preserved=0
  local missing=0
  local missing_files=""
  
  # Check each source file
  while IFS= read -r source_file; do
    if [ -z "$source_file" ]; then continue; fi
    
    local file_basename=$(basename "$source_file")
    local file_found=false
    
    # Check if file exists in target module
    if [ -f "$target_dir/$file_basename" ]; then
      file_found=true
      preserved=$((preserved + 1))
    else
      # Check if file exists in consolidated directory with a name pattern
      local consolidated_pattern="*${file_basename}"
      if find "$CONSOLIDATED_DIR" -name "$consolidated_pattern" | grep -q .; then
        file_found=true
        preserved=$((preserved + 1))
      fi
    fi
    
    # If file not found, add to missing list
    if [ "$file_found" = false ]; then
      missing=$((missing + 1))
      missing_files+="    - $file_basename\n"
    fi
  done <<< "$source_files"
  
  # Calculate preservation percentage
  local preservation_pct=0
  if [ $source_count -gt 0 ]; then
    preservation_pct=$(( (preserved * 100) / source_count ))
  fi
  
  echo "- Files preserved: $preserved/$source_count ($preservation_pct%)" >> "$VERIFICATION_LOG"
  
  if [ $missing -gt 0 ]; then
    echo "- Missing files: $missing" >> "$VERIFICATION_LOG"
    echo "" >> "$VERIFICATION_LOG"
    echo "### Missing files from $source_module:" >> "$VERIFICATION_LOG"
    echo "" >> "$VERIFICATION_LOG"
    echo -e "$missing_files" >> "$VERIFICATION_LOG"
  else
    echo "- **All files successfully preserved!**" >> "$VERIFICATION_LOG"
  fi
  
  echo "" >> "$VERIFICATION_LOG"
  echo "---" >> "$VERIFICATION_LOG"
  echo "" >> "$VERIFICATION_LOG"
}

echo "Verifying consolidation..."

# Process each module pair
for pair in "${MODULE_PAIRS[@]}"; do
  # Split the pair
  IFS=':' read -r source_module target_module <<< "$pair"
  
  echo "Verifying $source_module → $target_module..."
  verify_module_pair "$source_module" "$target_module"
done

echo "## Summary" >> "$VERIFICATION_LOG"
echo "" >> "$VERIFICATION_LOG"
echo "The following checks should be performed manually:" >> "$VERIFICATION_LOG"
echo "" >> "$VERIFICATION_LOG"
echo "1. Review any missing files to determine if their functionality is truly missing or has been incorporated differently" >> "$VERIFICATION_LOG"
echo "2. Compile the project to check for any broken references or missing functionality" >> "$VERIFICATION_LOG"
echo "3. Perform runtime testing to ensure all functionality works as expected" >> "$VERIFICATION_LOG"
echo "" >> "$VERIFICATION_LOG"

echo "Verification complete! Report saved to $VERIFICATION_LOG"
echo "Please review the verification log before proceeding with module removal." 