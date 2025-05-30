# Visual DM Data Organization

This directory contains the centralized JSON data structure for Visual DM, organized according to the Development Bible. The structure follows logical domain boundaries and supports the modular architecture of the game.

## Directory Structure

```
/data
├── biomes/          # World geography, biome rules
├── entities/        # All living entities (races, NPCs, monsters)
│   ├── abilities/   # Character abilities and stats
│   ├── races/       # Race definitions and traits
│   └── npcs/        # NPC templates and behavior
├── items/           # Item definitions and properties
├── crafting/        # Crafting stations and recipes
├── world/           # World generation, regions, POIs
│   ├── regions/     # Region definitions
│   ├── pois/        # Point of Interest data
│   └── generation/  # World generation parameters
├── systems/         # Core mechanical systems data 
│   ├── memory/      # Memory system data
│   ├── motif/       # Motif definitions
│   ├── rumor/       # Rumor generation data
│   ├── faction/     # Faction data
│   ├── religion/    # Religion templates
│   ├── economy/     # Economy rules
│   ├── time/        # Calendar and time data
│   ├── weather/     # Weather types and patterns
│   └── events/      # Event definitions
├── gameplay/        # Primary gameplay mechanics (CONSOLIDATED)
│   ├── combat/      # Combat rules and mechanics
│   ├── skills/      # Skill definitions
│   ├── feats/       # Feat and ability definitions (master file)
│   ├── classes/     # Character class definitions
│   ├── weapons/     # Weapon data (master file)
│   ├── armor/       # Armor data (master file)
│   ├── equipment/   # Equipment definitions (master file)
│   └── spells/      # Spell definitions (master file)
├── monsters/        # Monster definitions by level (legacy)
├── weapons/         # Weapon data by type (legacy)
├── armor/           # Armor data (legacy)
├── equipment/       # Equipment data (legacy)
├── feats/           # Feat definitions (legacy)
├── spells/          # Spell definitions by level (legacy)
├── classes/         # Class definitions (legacy)
├── leveling/        # Level progression data
├── skills/          # Skill definitions (legacy)
├── narrative/       # Dialogue, quests, narrative arcs
├── world_state/     # World state persistence
└── modding/         # Modding tools and schemas
```

## Primary vs. Legacy Data

This data structure includes two main organizational approaches:

1. **Primary Data** (for active development): 
   - The `/gameplay` directory is the consolidated location for all primary gameplay mechanics
   - It contains master files that represent the canonical versions for game elements
   - Use these files for all new development and feature work

2. **Legacy Data** (for reference):
   - Original JSON files are preserved in their respective directories
   - These are kept for historical reference and backward compatibility
   - They may contain alternative formats or earlier iterations of the data

## Data Organization Benefits

This organization provides several benefits:

1. **Modularity**: Each subsystem has its own data domain
2. **Extensibility**: New types can be added without restructuring
3. **Versioning**: All data files include version information
4. **Schema Validation**: JSON schemas define the structure
5. **Modding**: The structure facilitates user modding

## Working with the Data Structure

- Use the consolidated master files in `/gameplay` for new development
- Include version information in all new data files
- Follow existing file naming conventions
- Add appropriate README files to new directories

For detailed information about specific data domains, see the README files in each subdirectory. 