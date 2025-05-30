#!/bin/bash

# Script to move remaining files from old directories to the new module structure and clean up
# Run this script after the main restructuring is complete

set -e  # Exit on any error

SCRIPTS_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts"
MODULES_DIR="$SCRIPTS_DIR/Modules"
ROOT_DIR="/Users/Sharrone/Visual_DM"
LOG_FILE="$ROOT_DIR/cleanup_remaining_files_log.txt"

echo "Cleanup Log - $(date)" > "$LOG_FILE"

# Function to move a file to the appropriate module
move_file() {
  source_file=$1
  target_module=$2
  
  if [ -f "$source_file" ]; then
    filename=$(basename "$source_file")
    target_dir="$MODULES_DIR/$target_module"
    target_file="$target_dir/$filename"
    meta_file="${source_file}.meta"
    target_meta_file="$target_dir/${filename}.meta"
    
    # Create target directory if it doesn't exist
    mkdir -p "$target_dir"
    
    # Copy the file if it doesn't already exist in target
    if [ ! -f "$target_file" ]; then
      echo "Moving $filename to $target_dir/" | tee -a "$LOG_FILE"
      cp "$source_file" "$target_dir/"
    else
      echo "Skipping $filename (already exists in $target_dir/)" | tee -a "$LOG_FILE"
    fi
    
    # Copy meta file if it exists and doesn't already exist in target
    if [ -f "$meta_file" ] && [ ! -f "$target_meta_file" ]; then
      cp "$meta_file" "$target_meta_file"
    fi
  else
    echo "Warning: Source file $source_file not found." | tee -a "$LOG_FILE"
  fi
}

# Check for remaining GameLoader.cs file and move it to Storage module
if [ -f "$SCRIPTS_DIR/GameLoader.cs" ]; then
  move_file "$SCRIPTS_DIR/GameLoader.cs" "Storage"
fi

# Process remaining directories
echo "Looking for remaining files in old directories..." | tee -a "$LOG_FILE"

# Process old directories and map them to new module locations
DIRECTORIES=(
  "Core:Core"
  "Systems:Legacy/Systems"
  "Data:Data"
  "World:World"
  "NPC:NPC"
  "Character:NPC"
  "UI:UI"
  "Networking:Networking"
  "Net:Networking"
  "POI:POI"
  "Combat:Combat"
  "Tests:Testing"
  "Motifs:Motif"
  "Inventory:Items"
  "Prompt:Dialogue"
  "Services:Core"
  "Debug:Core"
  "Editor:Core"
  "Entities:Data"
  "Examples:Core"
  "VDM:Core"
  "VisualDM:Core"
)

for mapping in "${DIRECTORIES[@]}"; do
  old_dir=$(echo $mapping | cut -d':' -f1)
  new_module=$(echo $mapping | cut -d':' -f2)
  
  if [ -d "$SCRIPTS_DIR/$old_dir" ]; then
    echo "Processing remaining files in $old_dir -> $new_module" | tee -a "$LOG_FILE"
    
    # Find all CS files in the directory and move them
    find "$SCRIPTS_DIR/$old_dir" -type f -name "*.cs" 2>/dev/null | while read file; do
      move_file "$file" "$new_module"
    done
  fi
done

# Create a backup directory for any other files
BACKUP_DIR="$ROOT_DIR/vdm_old_structure_backup"
mkdir -p "$BACKUP_DIR"

echo "Backing up any remaining files to $BACKUP_DIR" | tee -a "$LOG_FILE"

# Copy any remaining CS files to the backup dir with full path structure
find "$SCRIPTS_DIR" -path "$SCRIPTS_DIR/Modules" -prune -o -type f -name "*.cs" -print | while read file; do
  rel_path=$(echo "$file" | sed "s|$SCRIPTS_DIR/||")
  backup_path="$BACKUP_DIR/$rel_path"
  backup_dir=$(dirname "$backup_path")
  
  mkdir -p "$backup_dir"
  cp "$file" "$backup_path"
  echo "Backed up $file to $backup_path" | tee -a "$LOG_FILE"
done

echo "Cleanup completed. Results saved to $LOG_FILE"
echo ""
echo "Next steps:"
echo "1. Review the log file at $LOG_FILE"
echo "2. Build the project to check for any issues"
echo "3. Once everything is working, you can delete the old directories manually" 