#!/bin/bash

# Script to integrate files from VDM/Assets/VisualDM into the new module structure

# Base directories
SRC_DIR="VDM/Assets/VisualDM"
MODULES_DIR="VDM/Assets/Scripts/Modules"

# Create a backup of current structure
echo "Creating backup..."
BACKUP_DIR="vdm_visualdm_backup_$(date +%Y%m%d%H%M%S)"
mkdir -p $BACKUP_DIR
cp -R $SRC_DIR $BACKUP_DIR
echo "Backup created at $BACKUP_DIR"

# Function to create module directory if it doesn't exist
ensure_module_dir() {
    if [ ! -d "$MODULES_DIR/$1" ]; then
        mkdir -p "$MODULES_DIR/$1"
        echo "Created module directory: $MODULES_DIR/$1"
    fi
}

# Map systems to modules
echo "Integrating system files..."

# Core system files
ensure_module_dir "Core"
cp $SRC_DIR/Core/NamespaceCompatibility.cs $MODULES_DIR/Core/

# Quest system
ensure_module_dir "Quests"
cp $SRC_DIR/Systems/QuestManager.cs $MODULES_DIR/Quests/

# State system
ensure_module_dir "World"
cp $SRC_DIR/Systems/StateManager.cs $MODULES_DIR/World/
cp $SRC_DIR/Systems/StateManagerClient.cs $MODULES_DIR/World/

# Event system
ensure_module_dir "Events"
cp $SRC_DIR/Systems/EventManager.cs $MODULES_DIR/Events/
cp $SRC_DIR/Systems/EventAndQuestManagers.cs $MODULES_DIR/Events/
cp -R $SRC_DIR/Systems/Events/* $MODULES_DIR/Events/

# Time system
ensure_module_dir "TimeSystem"
cp $SRC_DIR/Systems/TimeManager.cs $MODULES_DIR/TimeSystem/

# Weather system 
ensure_module_dir "World"
cp $SRC_DIR/Systems/WeatherManager.cs $MODULES_DIR/World/

# WebSocket system
ensure_module_dir "Networking"
mkdir -p $MODULES_DIR/Networking
cp $SRC_DIR/Systems/WebSocketManager.cs $MODULES_DIR/Networking/

# Analytics system
ensure_module_dir "Analytics"
cp -R $SRC_DIR/Systems/Analytics/* $MODULES_DIR/Analytics/

# Base system management
ensure_module_dir "Core"
cp $SRC_DIR/Systems/BaseSystem.cs $MODULES_DIR/Core/
cp $SRC_DIR/Systems/SystemInitializer.cs $MODULES_DIR/Core/
cp $SRC_DIR/Systems/SystemManager.cs $MODULES_DIR/Core/

# WorldGen system
ensure_module_dir "World"
cp -R $SRC_DIR/Systems/WorldGen/* $MODULES_DIR/World/

# Modding system
ensure_module_dir "Modding"
mkdir -p $MODULES_DIR/Modding
cp -R $SRC_DIR/Systems/Modding/* $MODULES_DIR/Modding/

# Testing utilities
ensure_module_dir "Testing"
mkdir -p $MODULES_DIR/Testing
cp -R $SRC_DIR/Systems/Testing/* $MODULES_DIR/Testing/

# UI components
ensure_module_dir "UI"
cp -R $SRC_DIR/UI/* $MODULES_DIR/UI/

# Data files (if they contain code, not just assets)
ensure_module_dir "Data"
cp -R $SRC_DIR/Data/* $MODULES_DIR/Data/

# Network components
ensure_module_dir "Networking"
cp -R $SRC_DIR/Network/* $MODULES_DIR/Networking/

# Documentation - copy to a docs folder at the root
mkdir -p "docs/api"
cp -R $SRC_DIR/Documentation/* docs/api/

echo "Updating module index document..."
MODULE_INDEX="module_index.md"

# Update the module index (appending to the existing one)
for MODULE in $(ls $MODULES_DIR); do
  # Check if the module section already exists
  if ! grep -q "^## $MODULE Module$" $MODULE_INDEX; then
    echo -e "\n## $MODULE Module" >> $MODULE_INDEX
    echo "" >> $MODULE_INDEX
    echo "Files:" >> $MODULE_INDEX
    echo "" >> $MODULE_INDEX
  fi
  
  # Find new files and add them to the index
  if [ -d "$MODULES_DIR/$MODULE" ]; then
    find "$MODULES_DIR/$MODULE" -type f -name "*.cs" | sort | while read -r FILE; do
      FILENAME=$(basename "$FILE")
      # Only add if not already in the list
      if ! grep -q "^- $FILENAME$" $MODULE_INDEX; then
        # Find the position where we should add this file (after the file list section)
        LINE_NUM=$(grep -n "^## $MODULE Module$" $MODULE_INDEX | cut -d: -f1)
        FILE_SECTION=$((LINE_NUM + 4))
        sed -i '' "${FILE_SECTION}a\\
- $FILENAME
" $MODULE_INDEX
      fi
    done
  fi
done

echo "Integration complete. Updated $MODULE_INDEX with new files." 