#!/bin/bash

# Migration script for VDM Unity project directory structure

echo "Starting VDM Unity directory structure migration..."

# Create necessary directories if they don't exist
mkdir -p VDM/Assets/Scripts/Core/{Events,Utils,Managers}
mkdir -p VDM/Assets/Scripts/Runtime/Systems/{Memory,Rumor,Motif,Events,Population,Faction,Combat,Time,World,Analytics,POI}
mkdir -p VDM/Assets/Scripts/Runtime/{Entities,World,UI}
mkdir -p VDM/Assets/Scripts/Tests/{EditMode,PlayMode}
mkdir -p VDM/Assets/Scripts/Editor
mkdir -p VDM/Assets/Resources/{Data,Prefabs,Materials,UI}
mkdir -p VDM/Assets/ScriptableObjects/{Biomes,Items,Motifs,Systems}
mkdir -p VDM/Assets/Prefabs/{UI/{Screens,Elements,Popups},World/{POIs,Terrain,Effects},Characters/{NPCs,Player,Animals},Systems}
mkdir -p VDM/Assets/Scenes/{Main,UI,Bootstrap,Tests}

# Functions
migrate_system() {
    system_name=$1
    source_patterns=$2
    target_dir="VDM/Assets/Scripts/Runtime/Systems/$system_name"
    
    echo "Migrating $system_name system files..."
    
    for pattern in $source_patterns; do
        find VDM/Assets/Scripts -path "$pattern" -type f -name "*$system_name*" | while read file; do
            echo "  Copying $file to $target_dir/"
            cp "$file" "$target_dir/"
        done
    done
}

# Memory System
migrate_system "Memory" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# Rumor System
migrate_system "Rumor" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# Motif System
migrate_system "Motif" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# Events System
migrate_system "Events" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# Population System
migrate_system "Population" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# Faction System
migrate_system "Faction" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# Time System
migrate_system "Time" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# World System
migrate_system "World" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# Analytics System
migrate_system "Analytics" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# POI System
migrate_system "POI" "VDM/Assets/Scripts/Systems VDM/Assets/Scripts/Modules"

# Core Utils
echo "Migrating Core utility files..."
find VDM/Assets/Scripts -path "VDM/Assets/Scripts/Core" -type f -name "*.cs" | grep -v "Test" | while read file; do
    echo "  Copying $file to VDM/Assets/Scripts/Core/Utils/"
    cp "$file" "VDM/Assets/Scripts/Core/Utils/"
done

# UI components
echo "Migrating UI components..."
find VDM/Assets/Scripts -path "VDM/Assets/Scripts/UI" -type f -name "*.cs" | while read file; do
    echo "  Copying $file to VDM/Assets/Scripts/Runtime/UI/"
    cp "$file" "VDM/Assets/Scripts/Runtime/UI/"
done

# Entity-related files
echo "Migrating entity-related files..."
find VDM/Assets/Scripts -path "VDM/Assets/Scripts/Character" -o -path "VDM/Assets/Scripts/NPC" -type f -name "*.cs" | while read file; do
    echo "  Copying $file to VDM/Assets/Scripts/Runtime/Entities/"
    cp "$file" "VDM/Assets/Scripts/Runtime/Entities/"
done

# Editor tools
echo "Migrating editor tools..."
find VDM/Assets/Scripts -path "VDM/Assets/Scripts/Editor" -type f -name "*.cs" | while read file; do
    echo "  Copying $file to VDM/Assets/Scripts/Editor/"
    cp "$file" "VDM/Assets/Scripts/Editor/"
done

# Test files
echo "Migrating test files..."
find VDM/Assets/Scripts -path "VDM/Assets/Scripts/Tests" -type f -name "*Test*.cs" | while read file; do
    if [[ $file == *"EditMode"* ]]; then
        echo "  Copying $file to VDM/Assets/Scripts/Tests/EditMode/"
        cp "$file" "VDM/Assets/Scripts/Tests/EditMode/"
    else
        echo "  Copying $file to VDM/Assets/Scripts/Tests/PlayMode/"
        cp "$file" "VDM/Assets/Scripts/Tests/PlayMode/"
    fi
done

echo "Creating .meta files for directories..."
find VDM/Assets -type d -not -path "*.git*" | while read dir; do
    if [ ! -f "$dir.meta" ]; then
        echo "  Creating .meta file for $dir"
        touch "$dir.meta"
    fi
done

echo "Migration completed successfully!"
echo "Note: This script copies files to their new locations but does not delete the old files."
echo "After verifying everything works correctly, you may want to manually delete the old files." 