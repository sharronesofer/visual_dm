#!/bin/bash

# Script to update file path references in code files
# This script finds and updates namespace, import, and path references 
# to match the new module structure

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
LOG_FILE="/Users/Sharrone/Visual_DM/reference_updates_log.md"

# Initialize log
echo "# Reference Updates Log" > "$LOG_FILE"
echo "Generated on $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Map of old module names to new module names
declare -A MODULE_MAP=(
  ["NPC"]="Characters"
  ["NPCs"]="Characters"
  ["Factions"]="Faction"
  ["Quests"]="Quest"
  ["TimeSystem"]="Time"
  ["WorldGen"]="World"
  ["WorldState"]="World"
)

# Function to update namespace references in file
update_references() {
  local file=$1
  local old_module=$2
  local new_module=$3
  
  # Make sure file exists
  if [ ! -f "$file" ]; then
    echo "File $file doesn't exist. Skipping."
    return
  fi
  
  echo "Checking $file for references to $old_module"
  
  # Store the original file content
  original_content=$(cat "$file")
  updated_content="$original_content"
  
  # Replace namespace references
  has_namespace_ref=$(grep -q "namespace.*$old_module" "$file" && echo "true" || echo "false")
  if [ "$has_namespace_ref" = "true" ]; then
    updated_content=$(echo "$updated_content" | sed "s/namespace.*$old_module/namespace VisualDM.$new_module/g")
    echo "- Updated namespace reference in $file" >> "$LOG_FILE"
  fi
  
  # Replace using statements
  has_using_ref=$(grep -q "using.*$old_module" "$file" && echo "true" || echo "false")
  if [ "$has_using_ref" = "true" ]; then
    updated_content=$(echo "$updated_content" | sed "s/using.*$old_module/using VisualDM.$new_module/g")
    echo "- Updated using statement in $file" >> "$LOG_FILE"
  fi
  
  # Replace path references
  has_path_ref=$(grep -q "/$old_module/" "$file" && echo "true" || echo "false")
  if [ "$has_path_ref" = "true" ]; then
    updated_content=$(echo "$updated_content" | sed "s|/$old_module/|/$new_module/|g")
    echo "- Updated path reference in $file" >> "$LOG_FILE"
  fi
  
  # Replace other references (like class imports or type references)
  has_other_ref=$(grep -q "$old_module\.[A-Za-z0-9]\+" "$file" && echo "true" || echo "false")
  if [ "$has_other_ref" = "true" ]; then
    updated_content=$(echo "$updated_content" | sed "s/$old_module\([\.][A-Za-z0-9]\+\)/$new_module\1/g")
    echo "- Updated class reference in $file" >> "$LOG_FILE"
  fi
  
  # Write back to file only if changes were made
  if [ "$original_content" != "$updated_content" ]; then
    echo "$updated_content" > "$file"
    echo "Updated references in $file"
    echo "- Updated references in $file" >> "$LOG_FILE"
  fi
}

# Process all C# files in the modules directory
echo "Updating references in all modules..."

# Keep count of changed files
changed_files=0

# Update all C# files
find "$MODULES_DIR" -type f -name "*.cs" | while read -r file; do
  updated=false
  
  # Check each module mapping
  for old_module in "${!MODULE_MAP[@]}"; do
    new_module=${MODULE_MAP[$old_module]}
    
    # Update references for this module
    update_references "$file" "$old_module" "$new_module"
    
    # Check if the file was updated
    if grep -q "Updated references in $file" "$LOG_FILE"; then
      updated=true
    fi
  done
  
  # Count changed files
  if [ "$updated" = true ]; then
    changed_files=$((changed_files + 1))
  fi
done

echo "" >> "$LOG_FILE"
echo "## Summary" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "- Files checked: $(find "$MODULES_DIR" -type f -name "*.cs" | wc -l | tr -d ' ')" >> "$LOG_FILE"
echo "- Files with updated references: $changed_files" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "Reference update complete."
echo "- Log file: $LOG_FILE"
echo ""
echo "IMPORTANT: You should test your project thoroughly after this operation."
echo "Compile the project to check for any remaining reference issues." 