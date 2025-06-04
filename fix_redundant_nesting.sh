#!/bin/bash

# Fix redundant folder nesting in Unity frontend systems
# This script moves files from nested directories like Models/Models to proper Models directories

SYSTEMS_DIR="VDM/Assets/Scripts/Runtime/Systems"

echo "Fixing redundant folder nesting in Unity frontend systems..."

# Get list of all system directories
for system_dir in "$SYSTEMS_DIR"/*; do
    if [ -d "$system_dir" ]; then
        system_name=$(basename "$system_dir")
        echo "Processing system: $system_name"
        
        # Fix Models/Models nesting
        if [ -d "$system_dir/Models/Models" ]; then
            echo "  Fixing Models/Models nesting in $system_name"
            find "$system_dir/Models/Models" -name "*.cs" -exec mv {} "$system_dir/Models/" \; 2>/dev/null
            rm -rf "$system_dir/Models/Models"
        fi
        
        # Fix Services/Services nesting
        if [ -d "$system_dir/Services/Services" ]; then
            echo "  Fixing Services/Services nesting in $system_name"
            find "$system_dir/Services/Services" -name "*.cs" -exec mv {} "$system_dir/Services/" \; 2>/dev/null
            rm -rf "$system_dir/Services/Services"
        fi
        
        # Fix UI/UI nesting
        if [ -d "$system_dir/UI/UI" ]; then
            echo "  Fixing UI/UI nesting in $system_name"
            find "$system_dir/UI/UI" -name "*.cs" -exec mv {} "$system_dir/UI/" \; 2>/dev/null
            rm -rf "$system_dir/UI/UI"
        fi
        
        # Fix Integration/Integration nesting
        if [ -d "$system_dir/Integration/Integration" ]; then
            echo "  Fixing Integration/Integration nesting in $system_name"
            find "$system_dir/Integration/Integration" -name "*.cs" -exec mv {} "$system_dir/Integration/" \; 2>/dev/null
            rm -rf "$system_dir/Integration/Integration"
        fi
    fi
done

echo "Redundant folder nesting cleanup complete!" 