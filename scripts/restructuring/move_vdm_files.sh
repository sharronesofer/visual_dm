#!/bin/bash

# Script to move VDM files to their respective module folders
# Run this script after creating the directory structure with restructure_vdm_folders.sh

set -e  # Exit on any error

SCRIPTS_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts"
MODULES_DIR="$SCRIPTS_DIR/Modules"
SYSTEMS_DIR="$SCRIPTS_DIR/Systems"
WORLD_DIR="$SCRIPTS_DIR/World"
ENTITIES_DIR="$SCRIPTS_DIR/Entities"
CORE_DIR="$SCRIPTS_DIR/Core"

# Helper function to copy a file and its meta file
move_file() {
  source_file=$1
  target_dir=$2
  
  if [ -f "$source_file" ]; then
    filename=$(basename "$source_file")
    target_file="$target_dir/$filename"
    meta_file="${source_file}.meta"
    target_meta_file="$target_dir/${filename}.meta"
    
    # Create target directory if it doesn't exist
    mkdir -p "$target_dir"
    
    # Copy the file if it doesn't already exist in target
    if [ ! -f "$target_file" ]; then
      echo "Moving $filename to $target_dir/"
      cp "$source_file" "$target_dir/"
    else
      echo "Skipping $filename (already exists in $target_dir/)"
    fi
    
    # Copy meta file if it exists and doesn't already exist in target
    if [ -f "$meta_file" ] && [ ! -f "$target_meta_file" ]; then
      cp "$meta_file" "$target_meta_file"
    fi
  else
    echo "Warning: Source file $source_file not found."
  fi
}

# Helper function to find and move files based on pattern
find_and_move() {
  source_dir=$1
  pattern=$2
  target_dir=$3
  
  # Find files matching pattern and move them
  find "$source_dir" -type f -name "$pattern" 2>/dev/null | while read file; do
    move_file "$file" "$target_dir"
  done
}

# Create a log of moved files
LOG_FILE="/Users/Sharrone/Visual_DM/moved_files_log.txt"
echo "File Movement Log - $(date)" > "$LOG_FILE"

echo "Moving files to their new module folders..."

# Memory System
echo "Moving Memory System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Memory*.cs" "$MODULES_DIR/Memory"
echo "Moved Memory files" >> "$LOG_FILE"

# Rumor System
echo "Moving Rumor System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Rumor*.cs" "$MODULES_DIR/Rumor"
echo "Moved Rumor files" >> "$LOG_FILE"

# Events System
echo "Moving Events System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Event*.cs" "$MODULES_DIR/Events"
find_and_move "$SCRIPTS_DIR" "*Hook*.cs" "$MODULES_DIR/Events"
find_and_move "$SCRIPTS_DIR" "*Dispatcher*.cs" "$MODULES_DIR/Events"
echo "Moved Events files" >> "$LOG_FILE"

# Analytics System
echo "Moving Analytics System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Analytics*.cs" "$MODULES_DIR/Analytics"
find_and_move "$SCRIPTS_DIR" "*Metrics*.cs" "$MODULES_DIR/Analytics"
echo "Moved Analytics files" >> "$LOG_FILE"

# World State System
echo "Moving World State System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*WorldState*.cs" "$MODULES_DIR/WorldState"
find_and_move "$SCRIPTS_DIR" "*GameState*.cs" "$MODULES_DIR/WorldState"
find_and_move "$WORLD_DIR" "*State*.cs" "$MODULES_DIR/WorldState"
echo "Moved WorldState files" >> "$LOG_FILE"

# Time System
echo "Moving Time System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Time*.cs" "$MODULES_DIR/Time"
find_and_move "$SCRIPTS_DIR" "*Calendar*.cs" "$MODULES_DIR/Time"
find_and_move "$SCRIPTS_DIR" "*Date*.cs" "$MODULES_DIR/Time"
echo "Moved Time files" >> "$LOG_FILE"

# Population Control System
echo "Moving Population System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Population*.cs" "$MODULES_DIR/Population"
echo "Moved Population files" >> "$LOG_FILE"

# Motif System
echo "Moving Motif System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Motif*.cs" "$MODULES_DIR/Motif"
echo "Moved Motif files" >> "$LOG_FILE"

# Region System
echo "Moving Region System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Region*.cs" "$MODULES_DIR/Region"
find_and_move "$WORLD_DIR" "*Region*.cs" "$MODULES_DIR/Region"
echo "Moved Region files" >> "$LOG_FILE"

# POI System
echo "Moving POI System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*POI*.cs" "$MODULES_DIR/POI"
find_and_move "$SCRIPTS_DIR" "*Location*.cs" "$MODULES_DIR/POI"
echo "Moved POI files" >> "$LOG_FILE"

# Faction System
echo "Moving Faction System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Faction*.cs" "$MODULES_DIR/Faction"
echo "Moved Faction files" >> "$LOG_FILE"

# War System
echo "Moving War System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*War*.cs" "$MODULES_DIR/War"
find_and_move "$SCRIPTS_DIR" "*Tension*.cs" "$MODULES_DIR/War"
find_and_move "$SCRIPTS_DIR" "*Conflict*.cs" "$MODULES_DIR/War"
echo "Moved War files" >> "$LOG_FILE"

# Quest System
echo "Moving Quest System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Quest*.cs" "$MODULES_DIR/Quest"
find_and_move "$SCRIPTS_DIR" "*Arc*.cs" "$MODULES_DIR/Quest"
find_and_move "$SCRIPTS_DIR" "*Mission*.cs" "$MODULES_DIR/Quest"
echo "Moved Quest files" >> "$LOG_FILE"

# Economy System
echo "Moving Economy System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Economy*.cs" "$MODULES_DIR/Economy"
find_and_move "$SCRIPTS_DIR" "*Trade*.cs" "$MODULES_DIR/Economy"
find_and_move "$SCRIPTS_DIR" "*Market*.cs" "$MODULES_DIR/Economy"
echo "Moved Economy files" >> "$LOG_FILE"

# Combat System
echo "Moving Combat System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Combat*.cs" "$MODULES_DIR/Combat"
find_and_move "$SCRIPTS_DIR" "*Damage*.cs" "$MODULES_DIR/Combat"
find_and_move "$SCRIPTS_DIR" "*Battle*.cs" "$MODULES_DIR/Combat"
echo "Moved Combat files" >> "$LOG_FILE"

# Relationship System
echo "Moving Relationship System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Relationship*.cs" "$MODULES_DIR/Relationship"
echo "Moved Relationship files" >> "$LOG_FILE"

# Storage System
echo "Moving Storage System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Storage*.cs" "$MODULES_DIR/Storage"
find_and_move "$SCRIPTS_DIR" "*Save*.cs" "$MODULES_DIR/Storage"
find_and_move "$SCRIPTS_DIR" "*Load*.cs" "$MODULES_DIR/Storage"
find_and_move "$SCRIPTS_DIR" "*Persistence*.cs" "$MODULES_DIR/Storage"
echo "Moved Storage files" >> "$LOG_FILE"

# Networking
echo "Moving Networking System files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Network*.cs" "$MODULES_DIR/Networking"
find_and_move "$SCRIPTS_DIR" "*WebSocket*.cs" "$MODULES_DIR/Networking"
find_and_move "$SCRIPTS_DIR" "*Http*.cs" "$MODULES_DIR/Networking"
find_and_move "$SCRIPTS_DIR" "*API*.cs" "$MODULES_DIR/Networking"
echo "Moved Networking files" >> "$LOG_FILE"

# World Generation
echo "Moving World Generation files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*WorldGen*.cs" "$MODULES_DIR/WorldGen"
find_and_move "$SCRIPTS_DIR" "*Generator*.cs" "$MODULES_DIR/WorldGen"
find_and_move "$SCRIPTS_DIR" "*Biome*.cs" "$MODULES_DIR/WorldGen"
echo "Moved World Generation files" >> "$LOG_FILE"

# NPC
echo "Moving NPC files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*NPC*.cs" "$MODULES_DIR/NPC"
find_and_move "$ENTITIES_DIR" "*NPC*.cs" "$MODULES_DIR/NPC"
find_and_move "$SCRIPTS_DIR" "*Character*.cs" "$MODULES_DIR/NPC"
echo "Moved NPC files" >> "$LOG_FILE"

# Dialogue
echo "Moving Dialogue files..." | tee -a "$LOG_FILE"
find_and_move "$SCRIPTS_DIR" "*Dialogue*.cs" "$MODULES_DIR/Dialogue"
find_and_move "$SCRIPTS_DIR" "*Conversation*.cs" "$MODULES_DIR/Dialogue"
echo "Moved Dialogue files" >> "$LOG_FILE"

# Core
echo "Moving Core files..." | tee -a "$LOG_FILE"
find_and_move "$CORE_DIR" "*.cs" "$MODULES_DIR/Core"
find_and_move "$SCRIPTS_DIR" "*Singleton*.cs" "$MODULES_DIR/Core"
find_and_move "$SCRIPTS_DIR" "*Utility*.cs" "$MODULES_DIR/Core"
find_and_move "$SCRIPTS_DIR" "*Helper*.cs" "$MODULES_DIR/Core"
# We'll move Manager files last to avoid moving system-specific managers that should stay in their modules
find_and_move "$SCRIPTS_DIR" "*Manager*.cs" "$MODULES_DIR/Core"
echo "Moved Core files" >> "$LOG_FILE"

echo "File moving complete. Please check the log at $LOG_FILE"
echo "Next step: Review the new structure and resolve duplicate files" 