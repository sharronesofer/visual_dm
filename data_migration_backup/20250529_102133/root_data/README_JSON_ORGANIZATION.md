# JSON File Organization in Visual DM

This document outlines the canonical organization structure for JSON files in the Visual DM project. All JSON data files should be placed in the appropriate subdirectory under `/data` based on their domain and purpose.

## Canonical JSON Structure

```
/data
├── biomes/                # World geography, biome rules
│   ├── land_types.json    # Land/biome type definitions
│   └── adjacency.json     # Biome adjacency rules
├── entities/              # All living entities
│   ├── races/             # Race definitions
│   │   └── races.json     # Player/NPC races
│   └── monsters/          # Monster definitions
│       ├── level_1_monsters.json
│       └── level_20_monsters.json
├── items/                 # Item definitions
│   ├── item_types.json    # Item type definitions
│   ├── equipment.json     # Equipment definitions
│   └── item_effects.json  # Item effect definitions
├── crafting/              # Crafting rules
│   ├── recipes/           # Crafting recipes
│   └── stations/          # Crafting station definitions
├── world/                 # World generation, regions, POIs
│   ├── generation/        # World generation rules
│   │   └── world_seed.schema.json # Schema for world seeds
│   ├── poi/               # Point of Interest definitions
│   │   └── building_profiles_corrected.json # Building definitions
│   └── world_state/       # World state tracking
│       ├── global_state.json   # Global world state
│       ├── regional_state.json # Regional world state
│       └── poi_state.json      # POI state tracking
├── systems/               # Core mechanical systems data
│   ├── memory/            # Memory system data
│   ├── motif/             # Motif definitions
│   │   └── motif_types.json # Motif type definitions
│   ├── rumor/             # Rumor generation data
│   ├── faction/           # Faction data
│   │   └── faction_types.json # Faction type definitions
│   ├── religion/          # Religion templates
│   │   └── religion_templates.json # Religion definition templates
│   ├── combat/            # Combat rules
│   │   └── combat_rules.json # Combat system rules
│   ├── spells/            # Spell definitions
│   │   ├── level_0_spells.json # Cantrips
│   │   ├── level_1_spells.json # Level 1 spells
│   │   └── ...            # Higher level spells
│   ├── economy/           # Economy rules
│   ├── time/              # Calendar and time data
│   ├── weather/           # Weather types and patterns
│   │   └── weather_types.json # Weather type definitions
│   └── events/            # Event definitions
│       └── event_types.json # Event type definitions
├── gameplay/              # Abilities, combat, progression
│   ├── spells/            # Spell gameplay rules
│   ├── feats/             # Feat definitions
│   └── skills/            # Skill definitions
├── narrative/             # Dialogue, quests, narrative arcs
│   ├── dialogue/          # Dialogue templates
│   └── quests/            # Quest definitions
└── modding/               # Modding tools and schemas
    ├── schemas/           # JSON schemas for modding
    │   └── example.schema.json # Example schema for modders
    └── worlds/            # World definitions
        └── example_world_seed.json # Example world seed
```

## Best Practices

1. **Placement**: Always place new JSON files in the appropriate subdirectory based on their domain
2. **Naming**: Use clear, descriptive filenames in snake_case
3. **Versioning**: Include version information in JSON files
4. **Schemas**: Create and maintain schemas for all JSON files
5. **Documentation**: Document any exceptions or special cases

## Unity-Specific Files

Some JSON files need to remain in Unity-specific locations:
- `/VDM/Assets/StreamingAssets/Data/` - For Unity runtime-loaded data
- `/VDM/Assets/StreamingAssets/Schemas/` - For Unity runtime validation schemas

These files may duplicate data in the canonical structure but are necessary for Unity integration.

## Maintenance

Regular maintenance should be performed to ensure JSON files remain properly organized:
1. Run the organization validation script periodically
2. Move any misplaced files to their canonical locations
3. Update this document if new categories are added 