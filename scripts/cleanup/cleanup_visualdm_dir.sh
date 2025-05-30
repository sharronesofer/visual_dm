#!/bin/bash

# Script to remove the vdm/assets/scripts/visualdm directory
# after confirming its contents are duplicated in VDM/Assets/Scripts/VisualDM

echo "Removing vdm/assets/scripts/visualdm directory and all its contents..."

# Check if the directory exists
if [ -d "vdm/assets/scripts/visualdm" ]; then
    # Remove the directory and all its contents
    rm -rf vdm/assets/scripts/visualdm
    
    # Check if the removal was successful
    if [ $? -eq 0 ]; then
        echo "Directory vdm/assets/scripts/visualdm has been successfully removed."
    else
        echo "Error: Failed to remove directory vdm/assets/scripts/visualdm."
        exit 1
    fi
else
    echo "Directory vdm/assets/scripts/visualdm does not exist or has already been removed."
fi

echo "Cleanup completed successfully."
echo "Note: Parent directories (vdm/assets/scripts, vdm/assets, vdm) have been preserved as they contain other important content."

exit 0 