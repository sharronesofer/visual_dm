#!/bin/bash

# Script to continue refactoring the remaining redundant modules
# This script identifies and processes other potential duplicate module pairs

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
BACKUP_DIR="/Users/Sharrone/Visual_DM/module_backups/$(date +%Y%m%d_%H%M%S)"
CONSOLIDATED_DIR="$MODULES_DIR/Consolidated"
LOG_FILE="/Users/Sharrone/Visual_DM/continued_refactoring_log.md"

# Create directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$CONSOLIDATED_DIR"

# Initialize log
echo "# Continued Module Refactoring Log" > "$LOG_FILE"
echo "Generated on $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Module pairs to consolidate (source:target)
# The target module will be kept, and unique functionality from source will be merged into it
declare -a MODULE_PAIRS=(
  "WorldGen:World"
  "WorldState:World"
)

# Function to backup a module
backup_module() {
  local module_name=$1
  local source_dir="$MODULES_DIR/$module_name"
  local backup_dir="$BACKUP_DIR/$module_name"
  
  if [ -d "$source_dir" ]; then
    echo "Backing up $module_name to $backup_dir"
    mkdir -p "$backup_dir"
    cp -r "$source_dir"/* "$backup_dir"/ 2>/dev/null || true
    echo "- Backed up module: $module_name" >> "$LOG_FILE"
  else
    echo "Module $module_name does not exist, skipping backup"
  fi
}

# Function to copy unique files from source to target
copy_unique_files() {
  local source_module=$1
  local target_module=$2
  local source_dir="$MODULES_DIR/$source_module"
  local target_dir="$MODULES_DIR/$target_module"
  
  if [ ! -d "$source_dir" ] || [ ! -d "$target_dir" ]; then
    echo "One or both modules don't exist. Skipping."
    return
  fi
  
  echo "## Consolidating $source_module into $target_module" >> "$LOG_FILE"
  echo "" >> "$LOG_FILE"
  
  # Get lists of files in each module
  find "$source_dir" -type f -name "*.cs" > /tmp/source_files.txt
  find "$target_dir" -type f -name "*.cs" > /tmp/target_files.txt
  
  # Copy files that don't exist in target (by filename)
  while IFS= read -r source_file; do
    filename=$(basename "$source_file")
    target_file="$target_dir/$filename"
    
    if [ ! -f "$target_file" ]; then
      echo "Copying unique file $filename from $source_module to $target_module"
      cp "$source_file" "$target_dir/"
      if [ -f "${source_file}.meta" ]; then
        cp "${source_file}.meta" "${target_dir}/${filename}.meta"
      fi
      echo "- Copied unique file: $filename" >> "$LOG_FILE"
    fi
  done < /tmp/source_files.txt
  
  # Handle files with same name but different content (merge them)
  while IFS= read -r source_file; do
    filename=$(basename "$source_file")
    target_file="$target_dir/$filename"
    
    if [ -f "$target_file" ] && ! cmp -s "$source_file" "$target_file"; then
      echo "Merging functionality from $filename"
      
      # Create a merged file in the Consolidated directory
      merged_file="$CONSOLIDATED_DIR/${source_module}_${target_module}_${filename}"
      
      # Create a header for the merged file
      echo "// Merged file from $source_module and $target_module modules" > "$merged_file"
      echo "// Original source file: $source_file" >> "$merged_file"
      echo "// Original target file: $target_file" >> "$merged_file"
      echo "// Merge date: $(date)" >> "$merged_file"
      echo "" >> "$merged_file"
      
      # Extract namespace from source and target
      source_namespace=$(grep -E "namespace [a-zA-Z0-9_.]+" "$source_file" | head -1 | sed 's/namespace \([a-zA-Z0-9_.]\+\).*/\1/')
      target_namespace=$(grep -E "namespace [a-zA-Z0-9_.]+" "$target_file" | head -1 | sed 's/namespace \([a-zA-Z0-9_.]\+\).*/\1/')
      
      # Use target namespace as the consolidated namespace
      if [ -n "$target_namespace" ]; then
        consolidated_namespace="$target_namespace"
      elif [ -n "$source_namespace" ]; then
        consolidated_namespace="$source_namespace"
      else
        consolidated_namespace="VisualDM.${target_module}"
      fi
      
      # Start the merged file with the consolidated namespace
      echo "using System;" >> "$merged_file"
      echo "using System.Collections;" >> "$merged_file"
      echo "using System.Collections.Generic;" >> "$merged_file"
      echo "using UnityEngine;" >> "$merged_file"
      echo "" >> "$merged_file"
      
      # Add additional using statements from both files
      grep -E "using [a-zA-Z0-9_.]+" "$source_file" | sort | uniq >> "$merged_file"
      grep -E "using [a-zA-Z0-9_.]+" "$target_file" | sort | uniq >> "$merged_file"
      echo "" >> "$merged_file"
      
      echo "namespace $consolidated_namespace" >> "$merged_file"
      echo "{" >> "$merged_file"
      
      # Extract class name from source and target
      source_class=$(grep -E "class [a-zA-Z0-9_]+" "$source_file" | head -1 | sed 's/.*class \([a-zA-Z0-9_]\+\).*/\1/')
      target_class=$(grep -E "class [a-zA-Z0-9_]+" "$target_file" | head -1 | sed 's/.*class \([a-zA-Z0-9_]\+\).*/\1/')
      
      # Use target class name for the consolidated class
      if [ -n "$target_class" ]; then
        consolidated_class="$target_class"
      elif [ -n "$source_class" ]; then
        consolidated_class="$source_class"
      else
        consolidated_class="${filename%.cs}"
      fi
      
      # Extract class definition with attributes
      target_class_def=$(grep -E "^\s*(public|private|internal|protected)?.*(class|interface|struct)" "$target_file" | head -1)
      
      # Write the class definition to merged file
      echo "    $target_class_def" >> "$merged_file"
      echo "    {" >> "$merged_file"
      
      # Extract fields and properties from both files, excluding duplicate names
      echo "        // Fields and properties from both modules" >> "$merged_file"
      grep -E "^\s*(private|protected|public|internal).*;" "$target_file" | sort >> "$merged_file"
      grep -E "^\s*(private|protected|public|internal).*;" "$source_file" | sort >> "$merged_file"
      echo "" >> "$merged_file"
      
      # Extract methods from target file
      echo "        // Methods from target module ($target_module)" >> "$merged_file"
      awk '/public|private|protected/ && /\(/ && !/;/ {p=1; print; next} p==1 {print} /}/ && p==1 {p=0; print ""}' "$target_file" >> "$merged_file"
      
      # Extract methods from source file that aren't in target file (based on method signature)
      echo "        // Methods from source module ($source_module)" >> "$merged_file"
      echo "        // NOTE: These may need to be manually integrated with the methods above" >> "$merged_file"
      awk '/public|private|protected/ && /\(/ && !/;/ {p=1; print; next} p==1 {print} /}/ && p==1 {p=0; print ""}' "$source_file" >> "$merged_file"
      
      # Close class and namespace
      echo "    }" >> "$merged_file"
      echo "}" >> "$merged_file"
      
      echo "- Created merged file: ${source_module}_${target_module}_${filename}" >> "$LOG_FILE"
      echo "  - Source class: $source_class" >> "$LOG_FILE"
      echo "  - Target class: $target_class" >> "$LOG_FILE"
      echo "  - Consolidated namespace: $consolidated_namespace" >> "$LOG_FILE"
    fi
  done < /tmp/source_files.txt
  
  echo "" >> "$LOG_FILE"
}

# Function to archive and remove a module
archive_module() {
  local module_name=$1
  local source_dir="$MODULES_DIR/$module_name"
  local archive_dir="$BACKUP_DIR/$module_name"
  
  if [ ! -d "$source_dir" ]; then
    echo "Module $module_name does not exist, skipping"
    echo "- Module not found: $module_name" >> "$LOG_FILE"
    return
  fi
  
  # Archive the module first (should already be backed up, but just in case)
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

# Backup all modules first
echo "Backing up modules to $BACKUP_DIR"
for pair in "${MODULE_PAIRS[@]}"; do
  # Split the pair
  IFS=':' read -r source_module target_module <<< "$pair"
  
  backup_module "$source_module"
  backup_module "$target_module"
done

# Process each module pair
for pair in "${MODULE_PAIRS[@]}"; do
  # Split the pair
  IFS=':' read -r source_module target_module <<< "$pair"
  
  echo "Consolidating $source_module into $target_module..."
  copy_unique_files "$source_module" "$target_module"
done

# Move consolidated files to target modules
for pair in "${MODULE_PAIRS[@]}"; do
  # Split the pair
  IFS=':' read -r source_module target_module <<< "$pair"
  
  # Find merged files
  merged_files=$(find "$CONSOLIDATED_DIR" -name "${source_module}_${target_module}_*.cs")
  
  while IFS= read -r merged_file; do
    if [ -z "$merged_file" ]; then continue; fi
    
    basename=$(basename "$merged_file")
    target_filename=$(echo "$basename" | sed "s/${source_module}_${target_module}_//")
    
    echo "Moving merged file $basename to $target_module/$target_filename"
    cp "$merged_file" "$MODULES_DIR/$target_module/$target_filename"
    echo "- Moved merged file: $basename → $target_module/$target_filename" >> "$LOG_FILE"
  done <<< "$merged_files"
done

# Remove source modules (to be removed, based on pairs)
echo "" >> "$LOG_FILE"
echo "## Removing Redundant Modules" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

for pair in "${MODULE_PAIRS[@]}"; do
  # Split the pair
  IFS=':' read -r source_module target_module <<< "$pair"
  
  echo "Removing redundant module: $source_module"
  archive_module "$source_module"
done

echo "Continued refactoring complete."
echo "- Backup created at: $BACKUP_DIR"
echo "- Log file: $LOG_FILE"
echo ""
echo "IMPORTANT: You should test your project thoroughly after this operation."
echo "If you need to restore any modules, they are available in the archive." 