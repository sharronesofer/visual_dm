#!/bin/bash

# Script to remove duplicate files identified during deduplication efforts

set -e  # Exit on error

# Print header
echo "Visual DM Backend - Duplicate File Cleanup"
echo "==========================================="
echo "This script will remove duplicate files based on deduplication analysis."
echo ""

# Confirm before proceeding
read -p "Continue with duplicate file removal? (y/n) " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "Operation cancelled."
    exit 0
fi

# List of files to remove
declare -a files_to_remove=(
    "backend/systems/rumor/gpt_client.py"
    "backend/systems/events/services/event_dispatcher.py"
)

# List of compatibility files (to be kept for now)
declare -a transition_files=(
    "backend/systems/rumor/gpt_client_deprecated.py"
    "backend/systems/events/services/event_dispatcher_deprecated.py"
)

# Counter for removed files
removed=0

echo ""
echo "Removing duplicate files..."
for file in "${files_to_remove[@]}"; do
    if [ -f "$file" ]; then
        echo "  - Removing $file"
        rm "$file"
        ((removed++))
    else
        echo "  - File not found: $file (already removed or path incorrect)"
    fi
done

echo ""
echo "Transition files (keeping for backward compatibility):"
for file in "${transition_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  - Preserving $file (transitional file)"
    else
        echo "  - Not found: $file (must be created for backward compatibility)"
    fi
done

echo ""
echo "Cleanup complete: $removed files removed."
echo ""
echo "Next steps:"
echo "1. Verify that the application builds and tests pass"
echo "2. Continue monitoring for import errors related to removed files"
echo "3. Run tests to ensure the compatibility layers work correctly"
echo "4. After sufficient testing, remove the transition files in a future cleanup"
echo "5. Check the systems listed in deduplication_notes.md for further review"

exit 0 