#!/bin/bash

# Script to restructure VDM folder organization based on Development Bible
# This creates the necessary folders and moves files to their respective module folders

set -e  # Exit on any error

SCRIPTS_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts"
TARGET_DIR="$SCRIPTS_DIR/Modules"

# Create main module directories as listed in the Development Bible
echo "Creating main module directories..."
mkdir -p "$TARGET_DIR/Events"          # Events System
mkdir -p "$TARGET_DIR/Analytics"       # Analytics System
mkdir -p "$TARGET_DIR/Memory"          # Memory System
mkdir -p "$TARGET_DIR/Rumor"           # Rumor System
mkdir -p "$TARGET_DIR/WorldState"      # World State System
mkdir -p "$TARGET_DIR/Time"            # Time System, Calendar, and Recurring Events
mkdir -p "$TARGET_DIR/Population"      # Population Control System
mkdir -p "$TARGET_DIR/Motif"           # Motif System
mkdir -p "$TARGET_DIR/Region"          # Region System
mkdir -p "$TARGET_DIR/POI"             # POI System
mkdir -p "$TARGET_DIR/Faction"         # Faction System
mkdir -p "$TARGET_DIR/War"             # Tension and War System
mkdir -p "$TARGET_DIR/Quest"           # Arc and Quest System
mkdir -p "$TARGET_DIR/Religion"        # Religion System
mkdir -p "$TARGET_DIR/Diplomacy"       # Diplomacy System
mkdir -p "$TARGET_DIR/Economy"         # Economy System
mkdir -p "$TARGET_DIR/Combat"          # Combat System
mkdir -p "$TARGET_DIR/Relationship"    # Character Relationship System
mkdir -p "$TARGET_DIR/Storage"         # Storage System
mkdir -p "$TARGET_DIR/Networking"      # Backend WebSocket Integration
mkdir -p "$TARGET_DIR/WorldGen"        # World Generation & Geography
mkdir -p "$TARGET_DIR/NPC"             # NPC-related functionality
mkdir -p "$TARGET_DIR/Dialogue"        # Dialogue-related functionality
mkdir -p "$TARGET_DIR/Core"            # Core utilities and shared functionality

# Create necessary meta files
echo "Creating module meta files..."
for dir in "$TARGET_DIR"/*; do
  if [ -d "$dir" ]; then
    dirname=$(basename "$dir")
    metafile="$dir.meta"
    
    if [ ! -f "$metafile" ]; then
      cat > "$metafile" << EOF
fileFormatVersion: 2
guid: $(uuidgen | tr '[:upper:]' '[:lower:]' | tr -d '-')
folderAsset: yes
DefaultImporter:
  externalObjects: {}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
EOF
    fi
  fi
done

echo "Directory structure created successfully."
echo "Next step: Run the file sorting script to move files to the appropriate directories." 