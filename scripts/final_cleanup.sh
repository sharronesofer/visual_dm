#!/bin/bash

# Script to move remaining files from VDM directory to backup and delete the VDM directory
# Run this after all other cleanup scripts have been executed

set -e  # Exit on any error

VDM_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/VDM"
BACKUP_DIR="/Users/Sharrone/Visual_DM/vdm_remaining_files_backup"
LOG_FILE="/Users/Sharrone/Visual_DM/final_cleanup_log.txt"

echo "Final Cleanup Log - $(date)" > "$LOG_FILE"

# Check if VDM directory exists
if [ ! -d "$VDM_DIR" ]; then
  echo "VDM directory not found at $VDM_DIR" | tee -a "$LOG_FILE"
  exit 0
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "Created backup directory at $BACKUP_DIR" | tee -a "$LOG_FILE"

# Copy all remaining files to backup
echo "Copying remaining files to backup directory..." | tee -a "$LOG_FILE"
cp -r "$VDM_DIR"/* "$BACKUP_DIR"/ 2>/dev/null || true
echo "Backup complete" | tee -a "$LOG_FILE"

# Count files and directories
file_count=$(find "$VDM_DIR" -type f | wc -l | tr -d ' ')
dir_count=$(find "$VDM_DIR" -mindepth 1 -type d | wc -l | tr -d ' ')

echo "Found $file_count files and $dir_count directories in $VDM_DIR" | tee -a "$LOG_FILE"

# Check if backup has files
backup_file_count=$(find "$BACKUP_DIR" -type f | wc -l | tr -d ' ')
if [ "$backup_file_count" -eq 0 ]; then
  echo "Warning: No files were copied to backup directory" | tee -a "$LOG_FILE"
fi

# Prompt to delete VDM directory
echo "" | tee -a "$LOG_FILE"
echo "All files have been backed up to $BACKUP_DIR" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
read -p "Do you want to delete the VDM directory? (y/n): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
  echo "Deleting VDM directory..." | tee -a "$LOG_FILE"
  rm -rf "$VDM_DIR"
  echo "VDM directory deleted successfully" | tee -a "$LOG_FILE"
  
  # Also delete the .meta file if it exists
  vdm_meta_file="${VDM_DIR}.meta"
  if [ -f "$vdm_meta_file" ]; then
    rm -f "$vdm_meta_file"
    echo "VDM.meta file deleted" | tee -a "$LOG_FILE"
  fi
else
  echo "Operation cancelled. VDM directory not deleted." | tee -a "$LOG_FILE"
fi

echo "Final cleanup completed. Results saved to $LOG_FILE" 