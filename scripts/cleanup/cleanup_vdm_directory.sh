#!/bin/bash

# Script to verify that /vdm and /VDM are identical and then remove the lowercase /vdm directory

echo "===== VDM Cleanup Script ====="
echo "This script will verify that /vdm and /VDM are identical, then remove the lowercase /vdm directory."
echo

# Check if both directories exist
if [ ! -d "vdm" ]; then
    echo "Error: /vdm directory does not exist."
    exit 1
fi

if [ ! -d "VDM" ]; then
    echo "Error: /VDM directory does not exist."
    echo "Cannot proceed without verifying content."
    exit 1
fi

# Create a backup directory with timestamp
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_DIR="vdm_backup_${TIMESTAMP}"
NEED_BACKUP=false

echo "1. Verifying that /vdm and /VDM are identical..."

# Quick comparison of a few key files
echo "   Comparing VDM.sln..."
if ! diff -q vdm/VDM.sln VDM/VDM.sln > /dev/null; then
    echo "   WARNING: VDM.sln files differ between directories."
    NEED_BACKUP=true
else
    echo "   VDM.sln files match."
fi

echo "   Comparing README.md..."
if ! diff -q vdm/README.md VDM/README.md > /dev/null; then
    echo "   WARNING: README.md files differ between directories."
    NEED_BACKUP=true
else
    echo "   README.md files match."
fi

# Check directory size
VDM_SIZE=$(du -sh VDM | cut -f1)
vdm_SIZE=$(du -sh vdm | cut -f1)

echo "   Directory sizes:"
echo "   - VDM: ${VDM_SIZE}"
echo "   - vdm: ${vdm_SIZE}"

# Create backup if needed
if [ "$NEED_BACKUP" = true ]; then
    echo "   Creating backup in ${BACKUP_DIR} before proceeding."
    mkdir -p "${BACKUP_DIR}"
    cp -r vdm/* "${BACKUP_DIR}/"
    echo "   Backup created in ${BACKUP_DIR}"
fi

echo
echo "2. Removing lowercase /vdm directory..."
echo "   The /VDM directory will be preserved and contains the restructured codebase."

# Remove the directory
rm -rf vdm

# Check if removal was successful
if [ $? -eq 0 ]; then
    echo "   Successfully removed the lowercase /vdm directory."
    
    # If we created a backup, let the user know
    if [ "$NEED_BACKUP" = true ]; then
        echo "   A backup of the original content was created in ${BACKUP_DIR}."
    else
        echo "   No backup was created as the directories appeared to be identical."
    fi
    
    echo
    echo "Cleanup completed successfully."
else
    echo "   Error: Failed to remove the lowercase /vdm directory."
    echo "   Please check permissions and try again."
    exit 1
fi

exit 0 