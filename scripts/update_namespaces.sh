#!/bin/bash

# Script to update namespaces in files to match their new module location
# This is a follow-up script after running move_vdm_files.sh

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
NAMESPACE_LOG="/Users/Sharrone/Visual_DM/namespace_updates_log.txt"

echo "Namespace Update Log - $(date)" > "$NAMESPACE_LOG"

# Function to update namespaces in a file
update_namespace() {
  local file=$1
  local module_name=$2
  
  # Skip if file doesn't exist
  if [ ! -f "$file" ]; then
    echo "Warning: File $file doesn't exist." | tee -a "$NAMESPACE_LOG"
    return
  }
  
  # Check if file has a namespace declaration
  if grep -q "namespace" "$file"; then
    # Get the current namespace
    current_namespace=$(grep -o "namespace [^{;]*" "$file" | sed 's/namespace //')
    
    # Target namespace
    target_namespace="VisualDM.${module_name}"
    
    # Check if namespace needs updating
    if [[ "$current_namespace" != *"$module_name"* ]]; then
      echo "Updating namespace in $file from '$current_namespace' to '$target_namespace'" | tee -a "$NAMESPACE_LOG"
      
      # Make a backup of the file
      cp "$file" "${file}.bak"
      
      # Update the namespace
      # This handles both "namespace X {" and "namespace X;" formats
      sed -i '' -E "s/namespace [^{;]*/namespace ${target_namespace}/g" "$file"
    else
      echo "Namespace already correct in $file: $current_namespace" >> "$NAMESPACE_LOG"
    fi
  else
    echo "No namespace declaration found in $file" >> "$NAMESPACE_LOG"
  fi
}

# Process each module directory
echo "Processing module directories..." | tee -a "$NAMESPACE_LOG"

for module_dir in "$MODULES_DIR"/*; do
  if [ -d "$module_dir" ]; then
    module_name=$(basename "$module_dir")
    echo "Processing module: $module_name" | tee -a "$NAMESPACE_LOG"
    
    # Find all C# files in the module directory
    find "$module_dir" -type f -name "*.cs" | while read file; do
      update_namespace "$file" "$module_name"
    done
  fi
done

echo "Namespace updating complete. Results saved to $NAMESPACE_LOG"
echo "Note: This is a first pass - manual review will be needed for special cases."
echo "      Backup files (.bak) have been created for all modified files." 