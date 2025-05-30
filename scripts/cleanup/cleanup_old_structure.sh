#!/bin/bash

# Script to clean up the old file structure after fully transitioning to the modular architecture
# IMPORTANT: Only run this after ensuring the new structure works correctly and all references are updated!

echo "WARNING: This will remove files from the old structure. Make sure you have:"
echo "1. Updated all code references to the new structure"
echo "2. Verified the project compiles and runs correctly"
echo "3. Committed your changes to version control"
echo ""
echo "Are you sure you want to proceed? (Type 'yes' to confirm)"
read CONFIRMATION

if [ "$CONFIRMATION" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

SRC_DIR="VDM/Assets/Scripts"

# Create a list of directories to be cleaned up (old structure)
DIRS_TO_CLEAN=(
    "$SRC_DIR/Systems/Memory"
    "$SRC_DIR/Systems/Rumor"
    "$SRC_DIR/Systems/Events"
    "$SRC_DIR/Systems/Motif"
    "$SRC_DIR/Systems/World"
    "$SRC_DIR/Systems/Population"
    "$SRC_DIR/Systems/Analytics"
    "$SRC_DIR/Systems/War"
    "$SRC_DIR/Systems/Economy"
    "$SRC_DIR/Systems/Storage"
    "$SRC_DIR/Systems/Combat"
    "$SRC_DIR/Character"
    "$SRC_DIR/NPC"
    "$SRC_DIR/POI"
    "$SRC_DIR/Combat"
    "$SRC_DIR/World/Time"
    "$SRC_DIR/Motifs"
)

# Create a list of loose files to be cleaned up (old structure)
FILES_TO_CLEAN=(
    "$SRC_DIR/Systems/MemoryManager.cs"
    "$SRC_DIR/Systems/MemoryQuery.cs"
    "$SRC_DIR/Systems/MemoryEventDispatcher.cs"
    "$SRC_DIR/Systems/MemoryIntegrationPoints.cs"
    "$SRC_DIR/Systems/NPCMemorySystem.cs"
    "$SRC_DIR/Systems/RumorManager.cs"
    "$SRC_DIR/Systems/RumorPropagationManager.cs"
    "$SRC_DIR/Systems/BelievabilityCalculator.cs"
    "$SRC_DIR/Systems/Motif.cs"
    "$SRC_DIR/Systems/MotifPool.cs"
    "$SRC_DIR/Systems/MotifEventDispatcher.cs"
    "$SRC_DIR/Systems/MotifRuleEngine.cs"
    "$SRC_DIR/Systems/MotifTransactionManager.cs"
    "$SRC_DIR/Systems/MotifTriggerManager.cs"
    "$SRC_DIR/Systems/MotifValidator.cs"
    "$SRC_DIR/Systems/WarManager.cs"
    "$SRC_DIR/Systems/Quest.cs"
    "$SRC_DIR/Systems/QuestState.cs"
    "$SRC_DIR/Systems/QuestVersionHistory.cs"
    "$SRC_DIR/Systems/ArcToQuestMapper.cs"
    "$SRC_DIR/Systems/ArcToQuestDebugTools.cs"
    "$SRC_DIR/Systems/GlobalArc.cs"
    "$SRC_DIR/Systems/GlobalArcManager.cs"
    "$SRC_DIR/Systems/GlobalArcMapper.cs"
    "$SRC_DIR/Systems/FactionArcMapper.cs"
)

# Function to clean up a directory if it exists
clean_directory() {
    DIR=$1
    if [ -d "$DIR" ]; then
        echo "Cleaning directory: $DIR"
        rm -rf "$DIR"
        echo "✓ Directory removed"
    else
        echo "Directory doesn't exist, skipping: $DIR"
    fi
}

# Function to clean up a file if it exists
clean_file() {
    FILE=$1
    if [ -f "$FILE" ]; then
        echo "Cleaning file: $FILE"
        rm "$FILE"
        META_FILE="${FILE}.meta"
        if [ -f "$META_FILE" ]; then
            rm "$META_FILE"
            echo "✓ File and meta file removed"
        else
            echo "✓ File removed (no meta file found)"
        fi
    else
        echo "File doesn't exist, skipping: $FILE"
    fi
}

# Clean up directories
echo "=== Cleaning up directories ==="
for DIR in "${DIRS_TO_CLEAN[@]}"; do
    clean_directory "$DIR"
done

# Clean up files
echo "=== Cleaning up individual files ==="
for FILE in "${FILES_TO_CLEAN[@]}"; do
    clean_file "$FILE"
done

echo ""
echo "Cleanup completed. Please check the project for any remaining references or empty directories."
echo "Remember to update your .asmdef files and regenerate project files if needed." 