# Location Type Migration Guide

This document explains how to migrate from hardcoded LocationType enums to the new modular JSON-based location types system in Visual DM.

## Overview

Visual DM has moved from using hardcoded enums for location types to a modular JSON-based system. This change enables:

1. **Modding support**: Add new location types without changing code
2. **Rich metadata**: Attach additional properties to location types
3. **Data-driven approach**: Easier to update and maintain
4. **Backward compatibility**: Existing code continues to work

## For Developers

### How it Works

The migration system consists of several components:

1. **JSON Schema**: Defines the structure of location type data
2. **Loader Classes**: Load and provide access to location type data
3. **Compatibility Layer**: Makes the new system work with existing code
4. **Migration Tools**: Convert hardcoded enums to JSON files

### Architecture Changes

Old approach:
```csharp
public enum LocationType
{
    UNDEFINED = 0,
    CITY = 1,
    TOWN = 2,
    // etc.
}
```

New approach:
```json
{
  "id": "city",
  "name": "City",
  "enum_name": "CITY",
  "value": 1,
  "description": "A large urban settlement with significant infrastructure",
  "icon": "city_icon",
  "color": "#0000FF",
  "flags": ["POPULATED", "URBAN", "HAS_SERVICES"]
}
```

### Migration Process

To migrate existing code from using the hardcoded `LocationType` enum to the new modular system:

1. **No immediate changes required**: The compatibility layer ensures existing code continues to work
2. **Gradual migration**: Update code to use the new system as convenient

### Compatibility Support

The compatibility layer provides:

- `LocationType` enum (maintained for backward compatibility)
- `LocationTypeEnum` compatibility class 
- `GetLocationTypeEnum()` method to convert from string ID to enum
- Attribute access in loader classes that mimics enum behavior

### Usage Examples

#### Old code (still works):

```csharp
// Set a location type using the enum
location.type = LocationType.CITY;

// Check a location type using the enum
if (location.type == LocationType.CITY) {
    // ...
}
```

#### New code (preferred):

```csharp
// Set a location type using the string ID
location.type = "city";

// Check a location type using the ModularDataSystem
if (ModularDataSystem.Instance.LocationTypeHasFlag(location.type, "POPULATED")) {
    // ...
}

// Get rich metadata
string icon = ModularDataSystem.Instance.GetLocationTypeIcon(location.type);
string color = ModularDataSystem.Instance.GetLocationTypeColor(location.type);
```

### Adding New Location Types

To add a new location type:

1. Create a JSON file in the appropriate directory (e.g., `data/builders/building_types/types/`)
2. Follow the schema format (see example below)
3. Add the location type ID to a world seed or reference it directly

Example new location type JSON:
```json
{
  "id": "metropolis",
  "name": "Metropolis",
  "enum_name": "METROPOLIS",
  "value": "metropolis",
  "description": "A very large and sprawling city with advanced infrastructure",
  "icon": "metropolis_icon",
  "color": "#000080",
  "flags": ["POPULATED", "URBAN", "HAS_SERVICES", "CAPITAL"],
  "size_range": {
    "min": 100,
    "max": 500,
    "unit": "square_km"
  }
}
```

## For Modders

### Location Type Structure

Each location type is defined in a JSON file with the following structure:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase with underscores) |
| `name` | string | Human-readable display name |
| `enum_name` | string | Original enum name (uppercase) for compatibility |
| `value` | string/int | Value used in the database |
| `description` | string | Detailed description |
| `icon` | string | Icon identifier for UI display |
| `color` | string | Hex color code for map display |
| `flags` | array | Array of characteristic flags |
| `size_range` | object | Typical size range with min, max, and unit |
| `typical_features` | array | Features typically found in this location type |
| `typical_npcs` | array | NPC types typically found in this location type |
| `typical_resources` | array | Resources typically found in this location type |
| `can_be_parent` | boolean | Whether this location can contain other locations |
| `can_have_parent` | boolean | Whether this location can be inside other locations |
| `valid_parent_types` | array | Location types that can be parents of this type |
| `valid_child_types` | array | Location types that can be children of this type |

### How to Create Mods

To create a mod that adds new location types:

1. Create a folder in the mod directory (`ModData/`)
2. Add a `LocationTypes/` subdirectory
3. Create a file for each location type
4. Create a `location_types.json` index file listing all location type IDs

Example mod structure:
```
ModData/
  └── MyMod/
      ├── manifest.json
      └── LocationTypes/
          ├── location_types.json
          └── types/
              ├── fortress.json
              ├── stronghold.json
              └── trading_post.json
```

Example `location_types.json`:
```json
[
  "fortress",
  "stronghold",
  "trading_post"
]
```

### Integration with World Seeds

World seeds can specify which location types to include:

```json
{
  "id": "my_world",
  "name": "My Custom World",
  "version": "1.0.0",
  "location_types": [
    "city",
    "town",
    "village",
    "fortress",
    "stronghold",
    "trading_post"
  ],
  "world_rules": {
    "density": {
      "city": 0.1,
      "town": 0.3,
      "village": 0.5,
      "fortress": 0.2
    }
  }
}
```

## Migration Tools

The following tools are available to assist with migration:

### `location_types_migrator.py`

Extracts hardcoded location type enums and converts them to JSON files. The tool:

1. Parses the codebase to find the `LocationType` enum
2. Extracts all enum values and their attributes
3. Creates JSON files for each location type
4. Generates an index file for all location types

Usage:
```bash
python data/builders/migration_tools/location_types_migrator.py
```

### `extract_hardcoded_data.py`

A general tool for extracting various types of hardcoded data to JSON files.

Usage:
```bash
python data/builders/migration_tools/extract_hardcoded_data.py --type location_types
```

### `run_all_migrations.py`

Runs all migration tools to extract all hardcoded data to JSON files.

Usage:
```bash
python data/builders/migration_tools/run_all_migrations.py
```

## Troubleshooting

### Common Issues

1. **Missing location types**: Ensure the location type JSON file exists and is referenced in the index file.
2. **Incompatible types**: Make sure the `value` field matches the expected type in the database.
3. **Schema validation errors**: Check that your JSON files conform to the schema.

### Debugging Tips

1. Enable debug logging to see detailed information about loaded location types.
2. Use the `validate_json.py` tool to check your JSON files against the schema.
3. Check the `modular_data_system.log` file for loading errors.

## More Information

- See the full schema at `data/builders/schemas/location_types.schema.json`
- Review examples in `data/builders/building_types/types/`
- The main compatibility layer is in `data/builders/loaders/location_type_loader.py`
- The Unity integration is in `VDM/Assets/Scripts/Data/ModularDataSystem.cs` 