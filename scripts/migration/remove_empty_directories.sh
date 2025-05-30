#!/bin/bash

# Script to identify and remove empty directories in the VDM project
# Run this script after moving all files to the new module structure

set -e  # Exit on any error

SCRIPTS_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts"
ROOT_DIR="/Users/Sharrone/Visual_DM"
LOG_FILE="$ROOT_DIR/empty_directories_log.txt"

echo "Empty Directories Log - $(date)" > "$LOG_FILE"

# Function to check if directory is empty (only contains .meta files or other empty directories)
is_effectively_empty() {
  local dir=$1
  
  # Check if directory contains no files or only .meta files
  local non_meta_files=$(find "$dir" -type f -not -name "*.meta" | wc -l | tr -d ' ')
  
  if [ "$non_meta_files" -eq 0 ]; then
    # No non-meta files, but check if it has subdirectories
    local subdirs=$(find "$dir" -mindepth 1 -type d | wc -l | tr -d ' ')
    
    if [ "$subdirs" -eq 0 ]; then
      # No subdirectories, definitely empty
      return 0
    else
      # Check each subdirectory
      for subdir in $(find "$dir" -mindepth 1 -type d); do
        if ! is_effectively_empty "$subdir"; then
          # At least one subdirectory is not empty
          return 1
        fi
      done
      # All subdirectories are empty
      return 0
    fi
  else
    # Has non-meta files
    return 1
  fi
}

# Find empty directories in Scripts directory (excluding Modules)
echo "Scanning for empty directories..." | tee -a "$LOG_FILE"

# First, create a list of directories to check
dirs_to_check=()
while IFS= read -r dir; do
  # Skip the Modules directory
  if [[ "$dir" != "$SCRIPTS_DIR/Modules"* ]]; then
    dirs_to_check+=("$dir")
  fi
done < <(find "$SCRIPTS_DIR" -type d | sort -r)

# Check each directory and log empty ones
empty_dirs=()
for dir in "${dirs_to_check[@]}"; do
  if is_effectively_empty "$dir"; then
    echo "Empty directory: $dir" | tee -a "$LOG_FILE"
    empty_dirs+=("$dir")
  fi
done

# Display summary
echo "" | tee -a "$LOG_FILE"
echo "Found ${#empty_dirs[@]} empty directories" | tee -a "$LOG_FILE"

# Ask for confirmation to delete
if [ ${#empty_dirs[@]} -gt 0 ]; then
  echo "" | tee -a "$LOG_FILE"
  echo "The following directories are empty and can be removed:" | tee -a "$LOG_FILE"
  for dir in "${empty_dirs[@]}"; do
    echo "  $dir" | tee -a "$LOG_FILE"
  done
  
  echo ""
  read -p "Do you want to remove these empty directories? (y/n): " confirm
  
  if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "Removing empty directories..." | tee -a "$LOG_FILE"
    
    # Remove empty directories and their .meta files
    for dir in "${empty_dirs[@]}"; do
      rm -rf "$dir"
      meta_file="${dir}.meta"
      if [ -f "$meta_file" ]; then
        rm -f "$meta_file"
      fi
      echo "Removed: $dir" | tee -a "$LOG_FILE"
    done
    
    echo "Empty directories removed successfully."
  else
    echo "Operation cancelled. No directories were removed."
  fi
else
  echo "No empty directories found."
fi

echo "Complete. Results saved to $LOG_FILE" 