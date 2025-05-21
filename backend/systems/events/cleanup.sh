#!/bin/bash
# Cleanup script for the refactored events system
# This removes duplicate files and directories after the refactoring

set -e  # Exit on error

echo "===== Beginning Events System Cleanup ====="

# Make sure we're in the events directory
cd "$(dirname "$0")"
EVENTS_DIR=$(pwd)
echo "Working in directory: $EVENTS_DIR"

# Create backup of the current state
echo "Creating backup..."
BACKUP_DIR="$EVENTS_DIR/../events_backup_$(date +%Y%m%d%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r "$EVENTS_DIR" "$BACKUP_DIR"
echo "Backup created at: $BACKUP_DIR"

# List of directories to preserve (our new structure)
PRESERVE=(
  "$EVENTS_DIR/core"
  "$EVENTS_DIR/middleware"
  "$EVENTS_DIR/utils"
  "$EVENTS_DIR/tests"
  "$EVENTS_DIR/__pycache__"
  "$EVENTS_DIR/__init__.py"
  "$EVENTS_DIR/README.md"
  "$EVENTS_DIR/cleanup.sh"
)

# List of files that might still be needed for reference
# We'll move these to a 'legacy' directory for now
LEGACY_FILES=(
  "$EVENTS_DIR/base.py"
  "$EVENTS_DIR/models.py"
)

# Create a legacy directory
echo "Creating legacy directory..."
mkdir -p "$EVENTS_DIR/legacy"

# Move legacy files
echo "Moving legacy files..."
for file in "${LEGACY_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "Moving to legacy: $(basename "$file")"
    mv "$file" "$EVENTS_DIR/legacy/"
  fi
done

# Function to check if a path should be preserved
should_preserve() {
  local path="$1"
  for p in "${PRESERVE[@]}"; do
    if [[ "$path" == "$p" || "$path" == "$p/"* ]]; then
      return 0  # true - should preserve
    fi
  done
  return 1  # false - should not preserve
}

# Delete all other files and directories
echo "Removing old files and directories..."
find "$EVENTS_DIR" -mindepth 1 | while read path; do
  if should_preserve "$path"; then
    echo "Preserving: $path"
  else
    if [ -f "$path" ]; then
      echo "Removing file: $path"
      rm "$path"
    elif [ -d "$path" -a "$path" != "$EVENTS_DIR/legacy" ]; then
      echo "Removing directory: $path"
      rm -rf "$path"
    fi
  fi
done

echo "===== Cleanup Complete ====="
echo "The events system has been successfully refactored and cleaned up."
echo "The original files have been backed up to: $BACKUP_DIR"
echo "Any potentially useful legacy files have been moved to: $EVENTS_DIR/legacy" 