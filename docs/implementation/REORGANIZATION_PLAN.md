# Backend Directory Reorganization Plan

## Current Structure
The backend currently has the following main directories:
- `backend/systems/` - Core functional systems organized by domain
- `backend/app/` - Contains core/analytics service
- `backend/core/` - Contains shared utilities like GPT client and config
- `backend/data/` - Contains JSON data files for the application

## Proposed Changes

### 1. Move Analytics to Systems

Move `backend/app/core/analytics/analytics_service.py` to `backend/systems/analytics/services/analytics_service.py`

This aligns with the domain-driven organization of other systems and follows the established pattern of having services within each system.

### 2. Reorganize Core Utilities

Move core utilities to appropriate system directories or a shared utilities system:

- `backend/core/ai/gpt_client.py` → `backend/systems/ai/services/gpt_client.py`
- Any other core utilities → Either to relevant system directories or to `backend/systems/shared/`

### 3. Keep Data Directory Separate

Data files should remain in the `/backend/data` directory since they are static resources used by multiple systems rather than code that belongs to a specific system.

### 4. Update Imports

After moving files, update all import statements to reflect the new locations. For example:
- `from backend.core.ai.gpt_client import GPTClient` → `from backend.systems.ai.services.gpt_client import GPTClient`
- `from backend.app.core.analytics.analytics_service import AnalyticsService` → `from backend.systems.analytics.services.analytics_service import AnalyticsService`

### 5. Deprecation Strategy

To ensure backward compatibility:
1. Create redirect modules in the old locations that import from the new locations and issue deprecation warnings
2. Give time for all code to be updated to use the new imports
3. Remove the redirect modules after a deprecation period

## Implementation Steps

1. Create new directory structures
2. Copy files to new locations (don't delete originals yet)
3. Update imports in the moved files
4. Create backward compatibility modules
5. Update imports in other files
6. Test thoroughly
7. Remove old files after deprecation period

## Benefits

- More consistent and intuitive directory structure
- Better organization following domain-driven design principles
- Easier to find related functionality
- Clearer separation of concerns
- More maintainable codebase 

# JSON Data Organization Plan

## Overview
This document outlines the plan for centralizing and organizing all JSON data files in the `/data` directory. The goal is to create a logical, maintainable structure that supports modding, world generation, and all game systems described in the Development Bible.

## Directory Structure

```
/data
├── biomes/                  # World geography, biome rules
│   ├── land_types.json      # Biome definitions
│   ├── adjacency.json       # Biome adjacency rules
│   └── transitions.json     # Biome transition rules
│   
├── entities/                # All living entities
│   ├── races/               # Character races
│   │   └── races.json       # Race definitions
│   ├── npcs/                # NPC definitions
│   │   └── npc_types.json   # NPC type definitions
│   └── monsters/            # Monster definitions
│       ├── monsters_1.json  # Monster set 1
│       ├── monsters_2.json  # Monster set 2
│       └── ...
│   
├── items/                   # All items and equipment
│   ├── weapons.json         # Weapon definitions
│   ├── armor.json           # Armor definitions
│   ├── items.json           # General item definitions
│   └── equipment.json       # Equipment definitions
│   
├── crafting/                # Crafting and recipes
│   ├── stations/            # Crafting stations
│   │   └── crafting_stations.json
│   └── recipes/             # Crafting recipes
│       ├── weapons.json     # Weapon recipes
│       ├── alchemy.json     # Alchemy recipes
│       └── ...
│   
├── world/                   # World generation data
│   ├── pois/                # Points of interest
│   │   ├── poi_types.json   # POI type definitions
│   │   └── building_types.json # Building type definitions
│   ├── regions/             # Region definitions
│   │   └── region_templates.json # Region templates
│   └── generation/          # World generation rules
│       ├── world_seed.schema.json # Schema for world seeds
│       └── example_world_seed.json # Example world seed
│   
├── systems/                 # Game system data
│   ├── memory/              # Memory system
│   │   └── memory_types.json # Memory type definitions
│   ├── motif/               # Motif system
│   │   └── motifs.json      # Motif definitions
│   ├── rumor/               # Rumor system
│   │   └── rumor_types.json # Rumor type definitions
│   ├── faction/             # Faction system
│   │   └── faction_types.json # Faction type definitions
│   ├── religion/            # Religion system
│   │   └── religion_templates.json # Religion templates
│   ├── economy/             # Economy system
│   │   ├── resources.json   # Resource definitions
│   │   └── trade_goods.json # Trade good definitions
│   ├── time/                # Time system
│   │   └── calendar.json    # Calendar definitions
│   ├── weather/             # Weather system
│   │   └── weather_types.json # Weather type definitions
│   └── events/              # Event system
│       └── event_types.json # Event type definitions
│   
├── gameplay/                # Gameplay mechanics
│   ├── abilities/           # Abilities and spells
│   │   ├── abilities.json   # Ability definitions
│   │   └── spells.json      # Spell definitions
│   ├── combat/              # Combat system
│   │   ├── combat_rules.json # Combat rule definitions
│   │   └── effect_types.json # Combat effect definitions
│   └── progression/         # Character progression
│       ├── skills.json      # Skill definitions
│       ├── feats.json       # Feat definitions
│       └── leveling.json    # Leveling rules
│   
├── narrative/               # Narrative content
│   ├── dialogue/            # Dialogue system
│   │   └── dialogue_templates.json # Dialogue templates
│   ├── quests/              # Quest system
│   │   └── quest_templates.json # Quest templates
│   └── arcs/                # Story arcs
│       └── arc_templates.json # Arc templates
│   
├── ui/                      # UI-related data
│   ├── sprite_manifest.json # Sprite mapping 
│   └── ui_config.json       # UI configuration
│   
└── modding/                 # Modding infrastructure
    ├── schemas/             # JSON schemas for validation
    │   ├── biome.schema.json
    │   ├── item.schema.json
    │   └── ...
    └── worlds/              # World definition files
        ├── world_seed.schema.json # Schema for world seeds
        └── example_world.json # Example world definition
```

## Implementation Plan

1. **Create Directory Structure**: Create the directory structure as outlined above.

2. **Migrate Existing JSON Files**: Move all existing JSON files from their current locations to the appropriate directories in the new structure.

3. **Create Missing Files**: Create placeholder files for important JSON files that don't yet exist.

4. **Update Code References**: Update all code references to point to the new file locations.

5. **Add README files**: Add README.md files to each directory explaining its purpose and the structure of the JSON files it contains.

6. **Validate JSON Structure**: Ensure all JSON files follow consistent patterns and are valid.

7. **Document Schema**: Create JSON schema files for validation and documentation purposes.

## Benefits

- **Improved Organization**: Clear, logical structure makes it easier to find and maintain data files.
- **Modding Support**: Structured data with schemas facilitates modding and custom content.
- **Extensibility**: Well-defined directories make it easy to add new data for new systems.
- **Consistency**: Standardized locations and naming conventions improve code maintainability.
- **Documentation**: Self-documenting structure with READMEs helps new developers understand the system.

## Next Steps

1. Implement the directory structure.
2. Migrate existing JSON files.
3. Update code references.
4. Add schema validation. 