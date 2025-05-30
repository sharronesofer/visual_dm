#!/bin/bash

# Script to update file path references in code files (Simplified V3)
# This script finds and updates namespace, import, and path references 
# to match the new module structure

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
LOG_FILE="/Users/Sharrone/Visual_DM/reference_updates_log_v3.md"

# Initialize log
echo "# Reference Updates Log (V3)" > "$LOG_FILE"
echo "Generated on $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Module mappings as pairs
MODULE_PAIRS=(
  "NPC:Characters"
  "NPCs:Characters"
  "Factions:Faction"
  "Quests:Quest"
  "TimeSystem:Time"
  "WorldGen:World"
  "WorldState:World"
)

# Function to update namespace references in file
update_references() {
  local file=$1
  local old_module=$2
  local new_module=$3
  local file_changed_by_this_call=false # Renamed for clarity
  
  if [ ! -f "$file" ]; then
    echo "File $file doesn't exist. Skipping." | tee -a "$LOG_FILE"
    return 1 # Indicate no change made by this specific call
  fi
  
echo "Checking $file for references to $old_module..." | tee -a "$LOG_FILE"
  
  original_content=$(cat "$file")
  updated_content="$original_content"
  
  # Namespace: VisualDM.OldModule -> VisualDM.NewModule
  if grep -q "namespace VisualDM.$old_module" "$file"; then
    updated_content=$(echo "$updated_content" | sed "s/namespace VisualDM.$old_module\b/namespace VisualDM.$new_module/g")
    file_changed_by_this_call=true
    echo "  - Updated namespace: VisualDM.$old_module -> VisualDM.$new_module" | tee -a "$LOG_FILE"
  fi
  
  # Using: VisualDM.OldModule -> VisualDM.NewModule
  if grep -q "using VisualDM.$old_module" "$file"; then
    updated_content=$(echo "$updated_content" | sed "s/using VisualDM.$old_module\b/using VisualDM.$new_module/g")
    file_changed_by_this_call=true
    echo "  - Updated using: VisualDM.$old_module -> VisualDM.$new_module" | tee -a "$LOG_FILE"
  fi

  # Path-like references: /OldModule/ -> /NewModule/
  if grep -q "/$old_module/" "$file"; then
    updated_content=$(echo "$updated_content" | sed "s|/$old_module/|/$new_module/|g")
    file_changed_by_this_call=true
    echo "  - Updated path: /$old_module/ -> /$new_module/" | tee -a "$LOG_FILE"
  fi
  
  # Other direct references: OldModule.SomeClass -> NewModule.SomeClass
  # Using \b for word boundary to avoid partial matches like OldModuleExtra -> NewModuleExtra
  if grep -q "\b$old_module\.[A-Z]" "$file"; then 
    updated_content=$(echo "$updated_content" | sed "s/\b$old_module\(\.[A-Z][A-Za-z0-9_]*\)/$new_module\1/g")
    file_changed_by_this_call=true
    echo "  - Updated class reference: $old_module.Class -> $new_module.Class" | tee -a "$LOG_FILE"
  fi
  
  if [ "$file_changed_by_this_call" = true ]; then
    # Only write if there was a change in THIS call to prevent re-writing for multiple patterns in one file if one didn't match.
    if [ "$original_content" != "$updated_content" ]; then 
        echo "$updated_content" > "$file"
        echo "  -> Successfully updated $file with changes for $old_module" | tee -a "$LOG_FILE"
    fi
    return 0 # Indicate change made by this call
  else
    echo "  -> No changes needed for $old_module in $file" | tee -a "$LOG_FILE"
    return 1 # Indicate no change made by this specific call
  fi
}

# Process all C# files in the modules directory
echo "Updating references in all modules..." | tee -a "$LOG_FILE"

changed_files_count=0

# Use process substitution if available, or a temporary file for `find` results
# This avoids the subshell issue with pipelines for the main loop.
while IFS= read -r file_path; do
  file_has_been_modified_overall=false # Tracks if the file was modified by ANY of the pairs
  for pair in "${MODULE_PAIRS[@]}"; do
    IFS=':' read -r old_m new_m <<< "$pair"
    # Call update_references. If it returns 0, a change was made.
    if update_references "$file_path" "$old_m" "$new_m"; then
      file_has_been_modified_overall=true
    fi
  done
  
  if [ "$file_has_been_modified_overall" = true ]; then
    changed_files_count=$((changed_files_count + 1))
  fi
done < <(find "$MODULES_DIR" -type f -name "*.cs") # Process substitution

echo "" >> "$LOG_FILE"
echo "## Summary" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
TOTAL_FILES=$(find "$MODULES_DIR" -type f -name "*.cs" | wc -l | tr -d ' ')
echo "- Files checked: $TOTAL_FILES" >> "$LOG_FILE"
echo "- Files with updated references: $changed_files_count" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "Reference update complete."
echo "- Log file: $LOG_FILE"

echo "IMPORTANT: You should test your project thoroughly after this operation."
echo "Compile the project to check for any remaining reference issues." 