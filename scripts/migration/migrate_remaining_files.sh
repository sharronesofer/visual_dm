#!/bin/bash

# Script to move all remaining files from VDM/Assets/VisualDM to the appropriate locations

# Base directories
SRC_DIR="VDM/Assets/VisualDM"
BASE_DIR="VDM/Assets"
MODULES_DIR="$BASE_DIR/Scripts/Modules"

# Create standard Unity directories if they don't exist
ensure_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo "Created directory: $1"
    fi
}

ensure_dir "$BASE_DIR/Prefabs"
ensure_dir "$BASE_DIR/Resources"
ensure_dir "$BASE_DIR/Scenes"
ensure_dir "$BASE_DIR/Examples"
ensure_dir "$MODULES_DIR/Core"
ensure_dir "$MODULES_DIR/Consolidated"
ensure_dir "$MODULES_DIR/Legacy"

# Move remaining Examples
echo "Moving Examples..."
cp -R "$SRC_DIR/Examples"/* "$BASE_DIR/Examples/"

# Move Prefabs 
echo "Moving Prefabs..."
cp -R "$SRC_DIR/Prefabs"/* "$BASE_DIR/Prefabs/" 2>/dev/null

# Move Resources
echo "Moving Resources..."
cp -R "$SRC_DIR/Resources"/* "$BASE_DIR/Resources/" 2>/dev/null

# Move Scenes
echo "Moving Scenes..."
cp -R "$SRC_DIR/Scenes"/* "$BASE_DIR/Scenes/" 2>/dev/null

# Move Consolidated files to the appropriate module
echo "Moving Consolidated files..."
cp -R "$SRC_DIR/Consolidated"/* "$MODULES_DIR/Consolidated/"

# Check if there are any files left in Systems directory
echo "Checking remaining System files..."
if [ -d "$SRC_DIR/Systems" ]; then
    # Create a legacy migration directory for any system files not yet categorized
    ensure_dir "$MODULES_DIR/Legacy/Systems"
    cp -R "$SRC_DIR/Systems"/* "$MODULES_DIR/Legacy/Systems/" 2>/dev/null
    echo "Moved remaining system files to $MODULES_DIR/Legacy/Systems/"
fi

# Check if there are any files left in Core directory
echo "Checking remaining Core files..."
if [ -d "$SRC_DIR/Core" ]; then
    cp -R "$SRC_DIR/Core"/* "$MODULES_DIR/Core/" 2>/dev/null
    echo "Moved remaining core files to $MODULES_DIR/Core/"
fi

# Check for UI files
echo "Checking UI files..."
if [ -d "$SRC_DIR/UI" ]; then
    ensure_dir "$MODULES_DIR/UI"
    cp -R "$SRC_DIR/UI"/* "$MODULES_DIR/UI/" 2>/dev/null
    echo "Moved UI files to $MODULES_DIR/UI/"
fi

# Check for Data files
echo "Checking Data files..."
if [ -d "$SRC_DIR/Data" ]; then
    ensure_dir "$MODULES_DIR/Data"
    cp -R "$SRC_DIR/Data"/* "$MODULES_DIR/Data/" 2>/dev/null
    echo "Moved Data files to $MODULES_DIR/Data/"
fi

# Check for Network files
echo "Checking Network files..."
if [ -d "$SRC_DIR/Network" ]; then
    ensure_dir "$MODULES_DIR/Networking"
    cp -R "$SRC_DIR/Network"/* "$MODULES_DIR/Networking/" 2>/dev/null
    echo "Moved Network files to $MODULES_DIR/Networking/"
fi

# Move Documentation to docs folder
echo "Moving Documentation..."
ensure_dir "docs/api"
cp -R "$SRC_DIR/Documentation"/* "docs/api/" 2>/dev/null

# List any remaining directories in the VisualDM folder
echo "Checking for any remaining directories in $SRC_DIR..."
REMAINING_DIRS=$(find "$SRC_DIR" -type d -depth 1 | grep -v "Meta\|\.git")

if [ -n "$REMAINING_DIRS" ]; then
    echo "Found these remaining directories: $REMAINING_DIRS"
    # Move them to a catch-all location
    ensure_dir "$BASE_DIR/MigratedContent"
    
    for DIR in $REMAINING_DIRS; do
        DIR_NAME=$(basename "$DIR")
        echo "Moving $DIR_NAME to $BASE_DIR/MigratedContent/"
        cp -R "$DIR" "$BASE_DIR/MigratedContent/"
    done
fi

# Update module index (this assumes module_index.md exists from previous script)
echo "Updating module index document..."
MODULE_INDEX="module_index.md"

# Update the module index
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

echo "Migration complete. Updated $MODULE_INDEX with new files."
echo "You can now remove the original VisualDM directory if you wish." 