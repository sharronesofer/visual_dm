#!/bin/bash

# Script to remove the original VisualDM directory 
# after all files have been migrated to their new locations

echo "WARNING: This will permanently remove the VDM/Assets/VisualDM directory."
echo "Make sure you have verified that all files have been properly migrated."
echo "Enter 'yes' to proceed or anything else to cancel:"
read CONFIRMATION

if [ "$CONFIRMATION" != "yes" ]; then
    echo "Operation cancelled."
    exit 0
fi

echo "Removing VDM/Assets/VisualDM directory..."
rm -rf VDM/Assets/VisualDM

echo "Checking if directory was successfully removed..."
if [ ! -d "VDM/Assets/VisualDM" ]; then
    echo "✅ VDM/Assets/VisualDM directory has been successfully removed."
    
    # Remove the .meta file as well
    if [ -f "VDM/Assets/VisualDM.meta" ]; then
        rm VDM/Assets/VisualDM.meta
        echo "✅ VDM/Assets/VisualDM.meta file has been removed."
    fi
else
    echo "❌ Failed to remove VDM/Assets/VisualDM directory."
fi

echo "Cleanup complete." 