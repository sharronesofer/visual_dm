#!/bin/bash

# Script to specifically handle files in the /vdm/Assets/Scripts/VDM directory
# Run this script after the main restructuring scripts

set -e  # Exit on any error

VDM_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/VDM"
SCRIPTS_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts"
MODULES_DIR="$SCRIPTS_DIR/Modules"
ROOT_DIR="/Users/Sharrone/Visual_DM"
LOG_FILE="$ROOT_DIR/cleanup_vdm_subdir_log.txt"

echo "VDM Subdirectory Cleanup Log - $(date)" > "$LOG_FILE"

# Check if the VDM directory exists
if [ ! -d "$VDM_DIR" ]; then
  echo "VDM directory not found at $VDM_DIR" | tee -a "$LOG_FILE"
  exit 0
fi

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

# Create a backup of the entire VDM directory
VDM_BACKUP_DIR="$ROOT_DIR/vdm_subdir_backup"
mkdir -p "$VDM_BACKUP_DIR"

echo "Creating backup of entire VDM directory to $VDM_BACKUP_DIR" | tee -a "$LOG_FILE"
cp -r "$VDM_DIR" "$VDM_BACKUP_DIR/"
echo "Backup complete" | tee -a "$LOG_FILE"

# Map files to modules based on naming patterns
echo "Processing files in VDM directory..." | tee -a "$LOG_FILE"

# First look for subdirectories that might map directly to modules
find "$VDM_DIR" -mindepth 1 -type d | while read subdir; do
  subdir_name=$(basename "$subdir")
  
  # Determine target module based on directory name
  target_module=""
  case "$subdir_name" in
    "Core"|"Utils"|"Utilities"|"Common") target_module="Core" ;;
    "Events"|"Event") target_module="Events" ;;
    "Memory") target_module="Memory" ;;
    "Analytics") target_module="Analytics" ;;
    "Rumor"|"Rumors") target_module="Rumor" ;;
    "WorldState"|"State") target_module="WorldState" ;;
    "Time"|"Calendar") target_module="Time" ;;
    "Faction"|"Factions") target_module="Factions" ;;
    "NPC"|"NPCs"|"Character"|"Characters") target_module="NPC" ;;
    "Quest"|"Quests") target_module="Quest" ;;
    "POI"|"Location"|"Locations") target_module="POI" ;;
    "World"|"WorldGen") target_module="World" ;;
    "Storage"|"Save"|"Load"|"Persistence") target_module="Storage" ;;
    "UI"|"Interface") target_module="UI" ;;
    "Dialogue"|"Dialog"|"Conversation") target_module="Dialogue" ;;
    "Combat"|"Battle") target_module="Combat" ;;
    "Economy"|"Trade"|"Market") target_module="Economy" ;;
    "Test"|"Tests"|"Testing") target_module="Testing" ;;
    "Network"|"Networking") target_module="Networking" ;;
    "Relationship"|"Relationships") target_module="Relationship" ;;
    "Population") target_module="Population" ;;
    "Motif"|"Motifs") target_module="Motif" ;;
    *) target_module="Legacy" ;;  # Default to Legacy for unknown subdirectories
  esac
  
  echo "Processing subdirectory: $subdir_name -> $target_module" | tee -a "$LOG_FILE"
  
  # Move all CS files from this subdirectory to the target module
  find "$subdir" -type f -name "*.cs" | while read file; do
    move_file "$file" "$target_module"
  done
done

# Process any remaining direct files in the VDM directory
find "$VDM_DIR" -maxdepth 1 -type f -name "*.cs" | while read file; do
  filename=$(basename "$file")
  
  # Determine target module based on filename patterns
  target_module="Core"  # Default to Core
  
  if [[ "$filename" == *"Event"* ]]; then
    target_module="Events"
  elif [[ "$filename" == *"Memory"* ]]; then
    target_module="Memory"
  elif [[ "$filename" == *"Analytic"* ]]; then
    target_module="Analytics"
  elif [[ "$filename" == *"Rumor"* ]]; then
    target_module="Rumor"
  elif [[ "$filename" == *"State"* ]]; then
    target_module="WorldState"
  elif [[ "$filename" == *"Time"* || "$filename" == *"Calendar"* ]]; then
    target_module="Time"
  elif [[ "$filename" == *"Faction"* ]]; then
    target_module="Factions"
  elif [[ "$filename" == *"NPC"* || "$filename" == *"Character"* ]]; then
    target_module="NPC"
  elif [[ "$filename" == *"Quest"* || "$filename" == *"Mission"* ]]; then
    target_module="Quest"
  elif [[ "$filename" == *"POI"* || "$filename" == *"Location"* ]]; then
    target_module="POI"
  elif [[ "$filename" == *"World"* ]]; then
    target_module="World"
  elif [[ "$filename" == *"Save"* || "$filename" == *"Load"* || "$filename" == *"Persistence"* ]]; then
    target_module="Storage"
  elif [[ "$filename" == *"UI"* || "$filename" == *"Interface"* ]]; then
    target_module="UI"
  elif [[ "$filename" == *"Dialog"* || "$filename" == *"Conversation"* ]]; then
    target_module="Dialogue"
  elif [[ "$filename" == *"Combat"* || "$filename" == *"Battle"* ]]; then
    target_module="Combat"
  elif [[ "$filename" == *"Economy"* || "$filename" == *"Trade"* || "$filename" == *"Market"* ]]; then
    target_module="Economy"
  elif [[ "$filename" == *"Test"* ]]; then
    target_module="Testing"
  elif [[ "$filename" == *"Network"* ]]; then
    target_module="Networking"
  fi
  
  echo "Processing file: $filename -> $target_module" | tee -a "$LOG_FILE"
  move_file "$file" "$target_module"
done

echo "Processing complete. Results saved to $LOG_FILE"
echo "A backup of the VDM directory has been created at $VDM_BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Review the log file at $LOG_FILE"
echo "2. Build the project to check for any issues"
echo "3. Once everything is working, run remove_empty_directories.sh to clean up empty directories" 