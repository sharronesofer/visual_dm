# JSON Migration Summary

This document summarizes the migration of JSON files to their canonical locations according to the project's data organization guidelines.

## Moved Files

The following JSON files have been moved from their original locations to the canonical directory structure:

| Original Location | Canonical Location | Notes |
|-------------------|-------------------|-------|
| backend/data/adjacency.json | data/biomes/adjacency.json | More robust version in canonical location |
| backend/data/rules_json/adjacency.json | data/biomes/adjacency.json | Duplicated, canonical version preserved |
| backend/data/rules_json/land_types.json | data/biomes/land_types.json | More comprehensive version in canonical location |
| rules_json/monster_only_feats.json | data/entities/monsters/monster_only_feats.json | Identical content |
| backend/data/entities/races/races_detailed.json | data/entities/races/expanded/races_detailed.json | Extended race data |
| backend/data/combat/combat_menu.json | data/systems/combat/expanded/combat_menu.json | Combat menu options |
| backend/data/equipment/equipment_expanded.json | data/equipment/expanded/equipment_expanded.json | Extended equipment data |
| backend/data/gameplay/weapons/melee_weapons.json | data/gameplay/weapons/melee/melee_weapons.json | Melee weapons data |
| backend/data/gameplay/weapons/ranged_weapons.json | data/gameplay/weapons/ranged/ranged_weapons.json | Ranged weapons data |

## Symlinks Created

Symlinks have been created to maintain backward compatibility with existing code that might reference the old file locations:

| Symlink Location | Points To |
|-----------------|-----------|
| backend/data/adjacency.json | data/biomes/adjacency.json |
| backend/data/biomes/adjacency.json | data/biomes/adjacency.json |
| backend/data/biomes/land_types.json | data/biomes/land_types.json |
| backend/data/rules_json/adjacency.json | data/biomes/adjacency.json |
| backend/data/rules_json/land_types.json | data/biomes/land_types.json |
| rules_json/monster_only_feats.json | data/entities/monsters/monster_only_feats.json |
| backend/data/entities/races/races_detailed.json | data/entities/races/expanded/races_detailed.json |
| backend/data/combat/combat_menu.json | data/systems/combat/expanded/combat_menu.json |
| backend/data/equipment/equipment_expanded.json | data/equipment/expanded/equipment_expanded.json |
| backend/data/gameplay/weapons/melee_weapons.json | data/gameplay/weapons/melee/melee_weapons.json |
| backend/data/gameplay/weapons/ranged_weapons.json | data/gameplay/weapons/ranged/ranged_weapons.json |

## Archive

Original files were archived in `archives/json_migration/` before creating symlinks to preserve the history.

## Note on Duplicate Files

When duplicate files were found:
1. If the canonical version was more comprehensive, it was kept
2. If both versions had significant differences, the original was moved to the expanded subdirectory
3. If files were identical, only one copy was kept in the canonical location

This migration helps maintain a consistent directory structure while preserving backward compatibility. 