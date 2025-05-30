# Visual DM Data Structure Documentation

This document provides complete documentation of the Visual DM data organization structure. It explains how data is organized, formatted, and versioned throughout the system.

## Data Organization Principles

The Visual DM data system is organized according to these key principles:

1. **Domain Separation**: Data is organized by functional domain (biomes, entities, items, etc.)
2. **Hierarchical Structure**: Related data is grouped in subdirectories
3. **Consistent Naming**: Files and directories follow consistent naming conventions
4. **Versioning**: All data files include version information
5. **Schema Validation**: All data conforms to defined JSON schemas
6. **Modular Design**: Each subsystem's data is self-contained but can reference other domains

## File Format Standards

All data files follow these standards:

1. **JSON Format**: All data is stored in JSON format
2. **Required Metadata**: All files include:
   - `version`: Semantic version number (e.g., "1.0.0")
   - `last_updated`: ISO-8601 date string
   - `description`: Brief description of the file's contents
3. **Schema Validation**: All files conform to their respective JSON schema
4. **UTF-8 Encoding**: All files use UTF-8 encoding
5. **Indentation**: 2-space indentation for readability

Example file template:
```json
{
  "version": "1.0.0",
  "last_updated": "2023-10-15T10:30:00Z",
  "description": "Example data file for the Visual DM system",
  "data": {
    // Domain-specific data here
  }
}
```

## Directory Structure Details

### Biomes Directory (`/biomes/`)

Contains all biome-related data:
- `land_types.json`: Definitions of all land biome types
- `water_types.json`: Definitions of all water biome types
- `adjacency.json`: Rules for biome adjacency and transitions
- `spawn_tables.json`: Biome-specific spawn tables for entities and resources

### Entities Directory (`/entities/`)

Contains all entity-related data:
- `races.json`: Definitions of playable and non-playable races
- `npcs/`: Templates for NPCs organized by type
- `monsters/`: Monster templates and properties
- `animals/`: Animal and creature templates

### Items Directory (`/items/`)

Contains all item-related data:
- `weapons.json`: Weapon definitions and properties
- `armor.json`: Armor and protective equipment
- `consumables.json`: Food, potions, and other consumables
- `materials.json`: Crafting materials and resources
- `quest_items.json`: Special items related to quests

### Systems Subdirectories

Each system subdirectory contains domain-specific data files:
- **Memory**: Memory type definitions, decay rates, relevance scoring
- **Motif**: Motif definitions, effects, and relationships
- **Rumor**: Rumor templates, spread patterns, mutation rules
- **Faction**: Faction definitions, relationships, and attributes
- **Religion**: Religion templates, beliefs, practices
- **Economy**: Resource definitions, trade rules, value tables
- **Time**: Calendar definitions, event scheduling, season effects
- **Weather**: Weather types, patterns, and effects
- **Events**: Event definitions, triggers, and outcomes

## Cross-References and Relationships

Data files can reference other domains using standardized ID formats:

1. **Biome References**: `biome:{biome_id}`
2. **Entity References**: `entity:{entity_id}`
3. **Item References**: `item:{item_id}`
4. **System References**: `system:{system_type}:{element_id}`

Example:
```json
{
  "spawn_tables": {
    "biome:desert": {
      "entities": ["entity:desert_scorpion", "entity:cactus_spirit"],
      "items": ["item:sand_crystal", "item:desert_herb"]
    }
  }
}
```

## Versioning Strategy

1. **Semantic Versioning**: All data files use semantic versioning (MAJOR.MINOR.PATCH)
2. **Version History**: Changes that affect data structure increment at least the MINOR version
3. **Migration Paths**: Major version changes include migration documentation
4. **Backwards Compatibility**: The system attempts to handle older versions gracefully

## Schema Documentation

All data schemas are documented in `/modding/schemas/`. These schemas define:
- Required and optional fields
- Data types and validation rules
- Relationships between data entities
- Default values and constraints

For more information on working with these data structures, see `DEVELOPER_GUIDE.md`.
