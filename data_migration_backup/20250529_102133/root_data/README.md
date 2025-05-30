# Visual DM Data Organization

This directory contains the centralized JSON data structure for the Visual DM system. The organization follows logical domain boundaries and supports the modular architecture described in the Development Bible.

## Directory Structure

```
/data
├── biomes/          # World geography, biome rules
├── entities/        # All living entities (races, NPCs, monsters)
├── items/           # Item definitions and properties
├── crafting/        # Crafting stations and recipes
├── world/           # World generation, regions, POIs
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
├── gameplay/        # Abilities, combat, progression
├── narrative/       # Dialogue, quests, narrative arcs
└── modding/         # Modding tools and schemas
```

## Purpose

This data structure supports:

1. **Modularity**: Each subsystem has its own data domain
2. **Extensibility**: New types can be added without restructuring
3. **Versioning**: All data files include version information
4. **Schema Validation**: JSON schemas define the structure
5. **Modding**: The structure facilitates user modding

For more detailed information about working with this data structure, see:

- `DATA_STRUCTURE.md` - Complete documentation of the data organization
- `DEVELOPER_GUIDE.md` - Practical guide for developers working with the data
