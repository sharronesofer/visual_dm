# Visual DM Modding Documentation

This directory contains resources for modding Visual DM through its JSON data structure. The modding system allows you to extend or modify game content without changing the core codebase.

## Modding Guidelines

### Data Structure

All game data is stored in JSON files organized by category. When creating mods, you should follow the same structure to ensure compatibility:

```
/data
├── biomes/          # World geography, biome rules
├── entities/        # Characters, NPCs, monsters  
├── items/           # Items and equipment
... etc
```

### Schema Validation

The `/modding/schemas/` directory contains JSON schema files that define the expected structure for each data file. Your mods should validate against these schemas to ensure compatibility.

Example schema usage:
```json
{
  "$schema": "file:///schemas/weather_types.schema.json",
  "version": "1.0",
  "weather_types": [
    // Your custom weather types here
  ]
}
```

### Custom World Creation

The `/modding/worlds/` directory is where you can define custom world seeds that can be used to generate new game worlds. See the example in `/data/world/generation/example_world_seed.json` for reference.

## Creating Mods

1. **Extend Existing Data**: Create new JSON files that add to existing game data (new items, characters, etc.)
2. **Override Default Data**: Replace default game data with your own versions
3. **Create New Content Types**: Add entirely new categories of content

## Mod Loading Priority

The game loads data in the following order:
1. Base game data
2. Official expansion data (if any)
3. User-created mods (alphabetically by mod name)

When conflicts occur, later loaded data takes precedence.

## Best Practices

1. **Versioning**: Always include a version field in your mod files
2. **Documentation**: Document what your mod does and any dependencies
3. **Compatibility**: Test your mods against the current game version
4. **Modular Design**: Create small, focused mods that can work independently
5. **Unique IDs**: Use a prefix for your mod IDs to avoid conflicts (e.g., "mymod_new_sword")

## Example Mod Structure

A complete mod might have this structure:
```
my_awesome_mod/
├── mod.json                  # Mod metadata
├── biomes/
│   └── new_biomes.json       # Custom biomes
├── entities/
│   └── npcs/
│       └── custom_npcs.json  # Custom NPCs
└── items/
    └── legendary_items.json  # New items
```

Refer to the schema files in the `/modding/schemas/` directory for detailed information about data structures. 