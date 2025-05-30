#!/bin/bash

# List of folders identified as likely unused
UNUSED_FOLDERS=(
  "AIBackend"
  "arc"
  "asset_generation"
  "code_quality"
  "component-audit" 
  "combat"
  "factions"
  "game"
  "hexmap"
  "item"
  "load-tests"
  "loot"
  "motifs"
  "pois"
  "python_converted"
  "python_demo"
  "screens"
  "search"
  "social"
  "ts_analysis"
  "ts_conversion"
  "visuals"
  "websocket"
)

# Create archive directory if it doesn't exist
mkdir -p backend/archive

# Move each folder to archive
for folder in "${UNUSED_FOLDERS[@]}"; do
  if [ -d "backend/$folder" ]; then
    echo "Moving backend/$folder to backend/archive/$folder"
    mv "backend/$folder" "backend/archive/$folder"
  else
    echo "Warning: backend/$folder does not exist, skipping"
  fi
done

echo "Done! Moved unused folders to backend/archive/" 