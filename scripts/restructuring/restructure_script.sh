#!/bin/bash

# Script to restructure VDM codebase based on the Development Bible
# This script will move files to the appropriate module folders

# Base directories
SRC_DIR="VDM/Assets/Scripts"
MODULES_DIR="$SRC_DIR/Modules"

# Create backup of current structure
echo "Creating backup..."
BACKUP_DIR="vdm_backup_$(date +%Y%m%d%H%M%S)"
mkdir -p $BACKUP_DIR
cp -R $SRC_DIR $BACKUP_DIR
echo "Backup created at $BACKUP_DIR"

# Memory Module
echo "Organizing Memory Module..."
mkdir -p $MODULES_DIR/Memory
cp -R $SRC_DIR/Systems/Memory/* $MODULES_DIR/Memory/
mv $SRC_DIR/Systems/MemoryManager.cs $MODULES_DIR/Memory/ 2>/dev/null
mv $SRC_DIR/Systems/MemoryQuery.cs $MODULES_DIR/Memory/ 2>/dev/null
mv $SRC_DIR/Systems/MemoryEventDispatcher.cs $MODULES_DIR/Memory/ 2>/dev/null
mv $SRC_DIR/Systems/MemoryIntegrationPoints.cs $MODULES_DIR/Memory/ 2>/dev/null
mv $SRC_DIR/Systems/NPCMemorySystem.cs $MODULES_DIR/Memory/ 2>/dev/null

# Rumor Module
echo "Organizing Rumor Module..."
mkdir -p $MODULES_DIR/Rumor
cp -R $SRC_DIR/Systems/Rumor/* $MODULES_DIR/Rumor/
mv $SRC_DIR/Systems/RumorManager.cs $MODULES_DIR/Rumor/ 2>/dev/null
mv $SRC_DIR/Systems/RumorPropagationManager.cs $MODULES_DIR/Rumor/ 2>/dev/null
mv $SRC_DIR/Systems/BelievabilityCalculator.cs $MODULES_DIR/Rumor/ 2>/dev/null

# Events Module
echo "Organizing Events Module..."
mkdir -p $MODULES_DIR/Events
cp -R $SRC_DIR/Systems/Events/* $MODULES_DIR/Events/

# Motif Module
echo "Organizing Motif Module..."
mkdir -p $MODULES_DIR/Motif
cp -R $SRC_DIR/Systems/Motif/* $MODULES_DIR/Motif/
mv $SRC_DIR/Systems/Motif.cs $MODULES_DIR/Motif/ 2>/dev/null
mv $SRC_DIR/Systems/MotifPool.cs $MODULES_DIR/Motif/ 2>/dev/null
mv $SRC_DIR/Systems/MotifEventDispatcher.cs $MODULES_DIR/Motif/ 2>/dev/null
mv $SRC_DIR/Systems/MotifRuleEngine.cs $MODULES_DIR/Motif/ 2>/dev/null
mv $SRC_DIR/Systems/MotifTransactionManager.cs $MODULES_DIR/Motif/ 2>/dev/null
mv $SRC_DIR/Systems/MotifTriggerManager.cs $MODULES_DIR/Motif/ 2>/dev/null
mv $SRC_DIR/Systems/MotifValidator.cs $MODULES_DIR/Motif/ 2>/dev/null
mv $SRC_DIR/Motifs/* $MODULES_DIR/Motif/ 2>/dev/null

# World Module
echo "Organizing World Module..."
mkdir -p $MODULES_DIR/World
cp -R $SRC_DIR/Systems/World/* $MODULES_DIR/World/
cp -R $SRC_DIR/World/* $MODULES_DIR/World/ 2>/dev/null

# Population Module
echo "Organizing Population Module..."
mkdir -p $MODULES_DIR/Population
cp -R $SRC_DIR/Systems/Population/* $MODULES_DIR/Population/

# Analytics Module
echo "Organizing Analytics Module..."
mkdir -p $MODULES_DIR/Analytics
cp -R $SRC_DIR/Systems/Analytics/* $MODULES_DIR/Analytics/

# War Module
echo "Organizing War Module..."
mkdir -p $MODULES_DIR/War
cp -R $SRC_DIR/Systems/War/* $MODULES_DIR/War/
mv $SRC_DIR/Systems/WarManager.cs $MODULES_DIR/War/ 2>/dev/null

# Economy Module
echo "Organizing Economy Module..."
mkdir -p $MODULES_DIR/Economy
cp -R $SRC_DIR/Systems/Economy/* $MODULES_DIR/Economy/

# Storage Module
echo "Organizing Storage Module..."
mkdir -p $MODULES_DIR/Storage
cp -R $SRC_DIR/Systems/Storage/* $MODULES_DIR/Storage/

# Combat Module
echo "Organizing Combat Module..."
mkdir -p $MODULES_DIR/Combat
cp -R $SRC_DIR/Combat/* $MODULES_DIR/Combat/
cp -R $SRC_DIR/Systems/Combat/* $MODULES_DIR/Combat/ 2>/dev/null

# Characters Module
echo "Organizing Characters Module..."
mkdir -p $MODULES_DIR/Characters
cp -R $SRC_DIR/Character/* $MODULES_DIR/Characters/

# NPCs Module
echo "Organizing NPCs Module..."
mkdir -p $MODULES_DIR/NPCs
cp -R $SRC_DIR/NPC/* $MODULES_DIR/NPCs/

# POI Module
echo "Organizing POI Module..."
mkdir -p $MODULES_DIR/POI
cp -R $SRC_DIR/POI/* $MODULES_DIR/POI/

# Factions Module
echo "Organizing Factions Module..."
mkdir -p $MODULES_DIR/Factions
# Find files related to factions
find $SRC_DIR -name "*Faction*.cs" -exec cp {} $MODULES_DIR/Factions/ \; 2>/dev/null
mv $SRC_DIR/Systems/FactionArcMapper.cs $MODULES_DIR/Factions/ 2>/dev/null

# Region Module
echo "Organizing Region Module..."
mkdir -p $MODULES_DIR/Region
# Find files related to regions
find $SRC_DIR -name "*Region*.cs" -exec cp {} $MODULES_DIR/Region/ \; 2>/dev/null

# Quests Module
echo "Organizing Quests Module..."
mkdir -p $MODULES_DIR/Quests
mv $SRC_DIR/Systems/Quest.cs $MODULES_DIR/Quests/ 2>/dev/null
mv $SRC_DIR/Systems/QuestState.cs $MODULES_DIR/Quests/ 2>/dev/null
mv $SRC_DIR/Systems/QuestVersionHistory.cs $MODULES_DIR/Quests/ 2>/dev/null
mv $SRC_DIR/Systems/ArcToQuestMapper.cs $MODULES_DIR/Quests/ 2>/dev/null
mv $SRC_DIR/Systems/ArcToQuestDebugTools.cs $MODULES_DIR/Quests/ 2>/dev/null
mv $SRC_DIR/Systems/GlobalArc.cs $MODULES_DIR/Quests/ 2>/dev/null
mv $SRC_DIR/Systems/GlobalArcManager.cs $MODULES_DIR/Quests/ 2>/dev/null
mv $SRC_DIR/Systems/GlobalArcMapper.cs $MODULES_DIR/Quests/ 2>/dev/null
find $SRC_DIR -name "*Quest*.cs" -exec cp {} $MODULES_DIR/Quests/ \; 2>/dev/null

# Religion Module
echo "Organizing Religion Module..."
mkdir -p $MODULES_DIR/Religion
find $SRC_DIR -name "*Religion*.cs" -exec cp {} $MODULES_DIR/Religion/ \; 2>/dev/null

# Diplomacy Module
echo "Organizing Diplomacy Module..."
mkdir -p $MODULES_DIR/Diplomacy
find $SRC_DIR -name "*Diplomacy*.cs" -exec cp {} $MODULES_DIR/Diplomacy/ \; 2>/dev/null

# TimeSystem Module
echo "Organizing TimeSystem Module..."
mkdir -p $MODULES_DIR/TimeSystem
cp -R $SRC_DIR/World/Time/* $MODULES_DIR/TimeSystem/ 2>/dev/null
find $SRC_DIR -name "*Time*.cs" -not -path "*Timeline*" -exec cp {} $MODULES_DIR/TimeSystem/ \; 2>/dev/null
find $SRC_DIR -name "*Calendar*.cs" -exec cp {} $MODULES_DIR/TimeSystem/ \; 2>/dev/null

# Create a module index file for documentation
echo "Creating module index document..."
MODULE_INDEX="module_index.md"
echo "# Visual DM Module Index" > $MODULE_INDEX
echo "" >> $MODULE_INDEX
echo "This document provides an overview of the restructured Visual DM codebase." >> $MODULE_INDEX
echo "" >> $MODULE_INDEX

for MODULE in $(ls $MODULES_DIR); do
  echo "## $MODULE Module" >> $MODULE_INDEX
  echo "" >> $MODULE_INDEX
  echo "Files:" >> $MODULE_INDEX
  echo "" >> $MODULE_INDEX
  if [ -d "$MODULES_DIR/$MODULE" ]; then
    find "$MODULES_DIR/$MODULE" -type f -name "*.cs" | sort | while read -r FILE; do
      FILENAME=$(basename "$FILE")
      echo "- $FILENAME" >> $MODULE_INDEX
    done
  fi
  echo "" >> $MODULE_INDEX
done

echo "Restructuring complete. See $MODULE_INDEX for an overview of the new structure." 