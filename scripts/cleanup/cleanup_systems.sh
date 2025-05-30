#!/bin/bash
# Script to normalize and cleanup system folders

echo "Cleaning up system folders..."

# First, let's handle duplicate systems by merging them
echo "Consolidating duplicate systems..."

# NPC + Character systems (merge into character system)
mkdir -p backend/systems/character/temp
cp -r backend/systems/npc/* backend/systems/character/temp/ 2>/dev/null
cp -r backend/systems/player_character/* backend/systems/character/temp/ 2>/dev/null
rm -rf backend/systems/npc backend/systems/player_character
mv backend/systems/character/temp/* backend/systems/character/ 2>/dev/null
rm -rf backend/systems/character/temp

# Inventory + Inventory Item (merge into inventory system)
mkdir -p backend/systems/inventory/temp
cp -r backend/systems/inventory_item/* backend/systems/inventory/temp/ 2>/dev/null
cp -r backend/systems/storage/* backend/systems/inventory/temp/ 2>/dev/null
rm -rf backend/systems/inventory_item backend/systems/storage
mv backend/systems/inventory/temp/* backend/systems/inventory/ 2>/dev/null
rm -rf backend/systems/inventory/temp

# Quest systems (merge into quest system)
mkdir -p backend/systems/quest/models backend/systems/quest/services backend/systems/quest/repositories backend/systems/quest/schemas backend/systems/quest/utils
cp -r backend/systems/arc_quest/* backend/systems/quest/ 2>/dev/null
cp -r backend/systems/quest_event/* backend/systems/quest/ 2>/dev/null
rm -rf backend/systems/arc_quest backend/systems/quest_event

# Faction systems (merge into faction system)
mkdir -p backend/systems/faction/temp
cp -r backend/systems/npc_faction/* backend/systems/faction/temp/ 2>/dev/null
rm -rf backend/systems/npc_faction
mv backend/systems/faction/temp/* backend/systems/faction/ 2>/dev/null
rm -rf backend/systems/faction/temp

# Time systems (merge into time system)
mkdir -p backend/systems/time/temp
cp -r backend/systems/time_calendar/* backend/systems/time/temp/ 2>/dev/null
cp -r backend/systems/time_weather/* backend/systems/time/temp/ 2>/dev/null
rm -rf backend/systems/time_calendar backend/systems/time_weather
mkdir -p backend/systems/time/models backend/systems/time/services backend/systems/time/repositories backend/systems/time/schemas backend/systems/time/utils
mv backend/systems/time/temp/* backend/systems/time/ 2>/dev/null
rm -rf backend/systems/time/temp

# Normalize folder structure for all systems
echo "Normalizing folder structure for all systems..."

for system in backend/systems/*/; do
  system_name=$(basename "$system")
  
  # Create standard folders if they don't exist
  mkdir -p "$system/models"
  mkdir -p "$system/services"
  mkdir -p "$system/repositories"
  mkdir -p "$system/schemas"
  mkdir -p "$system/utils"
  
  # Create __init__.py files 
  touch "$system/__init__.py"
  touch "$system/models/__init__.py"
  touch "$system/services/__init__.py"
  touch "$system/repositories/__init__.py"
  touch "$system/schemas/__init__.py"
  touch "$system/utils/__init__.py"
  
  # Create README if it doesn't exist
  if [ ! -f "$system/README.md" ]; then
    # Convert first letter to uppercase for README title
    system_title=$(echo "$system_name" | sed 's/^./\U&/')
    
    cat > "$system/README.md" << EOF
# $system_title System

This directory contains the $system_name system implementation.

## Structure

- **models/** - Data models and domain objects
- **services/** - Business logic and operations
- **repositories/** - Data persistence and storage
- **schemas/** - API schemas and data transfer objects
- **utils/** - Helper functions and utilities
EOF
  fi
done

# Remove any obviously redundant systems
echo "Removing redundant systems..."
rm -rf backend/systems/core_shared
rm -rf backend/systems/crafting_ability
rm -rf backend/systems/integration

# Add .gitkeep to empty directories
find backend -type d -empty -not -path "*/\.*" -exec touch {}/.gitkeep \;

echo "System cleanup complete!" 