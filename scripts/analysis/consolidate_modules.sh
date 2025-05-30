#!/bin/bash

# Script to consolidate duplicate functionality between modules
# This script creates a backup and then consolidates similar modules based on standard rules

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
BACKUP_DIR="/Users/Sharrone/Visual_DM/module_backups/$(date +%Y%m%d_%H%M%S)"
CONSOLIDATED_DIR="$MODULES_DIR/Consolidated"
LOG_FILE="/Users/Sharrone/Visual_DM/consolidation_log.md"

# Create directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$CONSOLIDATED_DIR"

# Initialize log
echo "# Module Consolidation Log" > "$LOG_FILE"
echo "Generated on $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Module pairs to consolidate (source:target)
# The target module will be kept, and unique functionality from source will be merged into it
declare -a MODULE_PAIRS=(
  "NPCs:Characters"
  "NPC:Characters"
  "Factions:Faction"
  "Quests:Quest"
  "TimeSystem:Time"
  "WorldGen:World"
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

# Backup all modules first
echo "Backing up all modules to $BACKUP_DIR"
for pair in "${MODULE_PAIRS[@]}"; do
  # Split the pair
  IFS=':' read -r source_module target_module <<< "$pair"
  
  backup_module "$source_module"
  backup_module "$target_module"
done

# Create a Consolidated directory if it doesn't exist
mkdir -p "$CONSOLIDATED_DIR"
echo "Created Consolidated directory at $CONSOLIDATED_DIR"

# Process each module pair
for pair in "${MODULE_PAIRS[@]}"; do
  # Split the pair
  IFS=':' read -r source_module target_module <<< "$pair"
  
  echo "Consolidating $source_module into $target_module..."
  copy_unique_files "$source_module" "$target_module"
done

echo "Module consolidation complete."
echo "- Backup created at: $BACKUP_DIR"
echo "- Merged files are in: $CONSOLIDATED_DIR"
echo "- Log file: $LOG_FILE"
echo "Next steps:"
echo "1. Review the merged files in the Consolidated directory"
echo "2. Manually integrate merged functionality"
echo "3. Move finalized files to appropriate target modules"
echo "4. Test thoroughly before removing source modules" 