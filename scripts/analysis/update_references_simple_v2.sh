#!/bin/bash

# Script to update file path references in code files (Simplified V2)
# This script finds and updates namespace, import, and path references 
# to match the new module structure

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
LOG_FILE="/Users/Sharrone/Visual_DM/reference_updates_log_v2.md"

# Initialize log
echo "# Reference Updates Log (V2)" > "$LOG_FILE"
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
  local file_changed=false
  
  if [ ! -f "$file" ]; then
    echo "File $file doesn't exist. Skipping." | tee -a "$LOG_FILE"
    return 1 # Indicate no change
  fi
  
  echo "Checking $file for references to $old_module..." | tee -a "$LOG_FILE"
  
  original_content=$(cat "$file")
  updated_content="$original_content"
  
  # Namespace: VisualDM.OldModule -> VisualDM.NewModule
  if grep -q "namespace VisualDM.$old_module" "$file"; then
    updated_content=$(echo "$updated_content" | sed "s/namespace VisualDM.$old_module\b/namespace VisualDM.$new_module/g")
    file_changed=true
    echo "  - Updated namespace: VisualDM.$old_module -> VisualDM.$new_module" | tee -a "$LOG_FILE"
  fi
  
  # Using: VisualDM.OldModule -> VisualDM.NewModule
  if grep -q "using VisualDM.$old_module" "$file"; then
    updated_content=$(echo "$updated_content" | sed "s/using VisualDM.$old_module\b/using VisualDM.$new_module/g")
    file_changed=true
    echo "  - Updated using: VisualDM.$old_module -> VisualDM.$new_module" | tee -a "$LOG_FILE"
  fi

  # Path-like references: /OldModule/ -> /NewModule/
  if grep -q "/$old_module/" "$file"; then
    updated_content=$(echo "$updated_content" | sed "s|/$old_module/|/$new_module/|g")
    file_changed=true
    echo "  - Updated path: /$old_module/ -> /$new_module/" | tee -a "$LOG_FILE"
  fi
  
  # Other direct references: OldModule.SomeClass -> NewModule.SomeClass
  if grep -q "$old_module\.[A-Z]" "$file"; then # Check for OldModule. followed by an uppercase letter (likely a class)
    updated_content=$(echo "$updated_content" | sed "s/\b$old_module\(\.[A-Z][A-Za-z0-9_]*\)/$new_module\1/g")
    file_changed=true
    echo "  - Updated class reference: $old_module.Class -> $new_module.Class" | tee -a "$LOG_FILE"
  fi
  
  if [ "$file_changed" = true ]; then
    echo "$updated_content" > "$file"
    echo "  -> Successfully updated $file" | tee -a "$LOG_FILE"
    return 0 # Indicate change made
  else
    echo "  -> No changes needed for $old_module in $file" | tee -a "$LOG_FILE"
    return 1 # Indicate no change
  fi
}

# Process all C# files in the modules directory
echo "Updating references in all modules..." | tee -a "$LOG_FILE"

changed_files_count=0

find "$MODULES_DIR" -type f -name "*.cs" | while read -r file_path; do
  file_was_modified_in_this_iteration=false
  for pair in "${MODULE_PAIRS[@]}"; do
    IFS=':' read -r old_m new_m <<< "$pair"
    update_references "$file_path" "$old_m" "$new_m"
    if [ $? -eq 0 ]; then
      file_was_modified_in_this_iteration=true
    fi
  done
  if [ "$file_was_modified_in_this_iteration" = true ]; then
    changed_files_count=$((changed_files_count + 1))
  fi
done

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