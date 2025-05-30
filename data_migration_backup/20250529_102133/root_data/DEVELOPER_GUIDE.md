# Visual DM Developer Guide

This guide provides practical information for developers working with the Visual DM data structure. It covers common tasks, best practices, and integration patterns.

## Getting Started

### Accessing Data

All data access should go through the `GameDataRegistry` class, which provides a centralized interface for loading and accessing data:

```python
from backend.systems.data.loaders.game_data_registry import GameDataRegistry

# Create a registry instance
registry = GameDataRegistry()

# Load all data
registry.load_all()

# Access specific data domains
biome = registry.get_biome("Forest")
item = registry.get_item("iron_sword")
faction = registry.get_faction("merchant_guild")
```

### Adding New Data Files

To add a new data file to an existing domain:

1. Place the JSON file in the appropriate directory (e.g., `/data/items/`)
2. Follow the file format standards (see `DATA_STRUCTURE.md`)
3. Ensure the file has the required metadata fields
4. Create or update the corresponding JSON schema in `/data/modding/schemas/`
5. Register the new file in the appropriate data loader

Example new item file (`/data/items/magical_items.json`):
```json
{
  "version": "1.0.0",
  "last_updated": "2023-10-15T14:20:00Z",
  "description": "Magical item definitions for the Visual DM system",
  "data": {
    "staff_of_fire": {
      "name": "Staff of Fire",
      "type": "weapon",
      "damage": 5,
      "effects": ["fire_damage", "light"],
      "rarity": "rare"
    }
  }
}
```

### Updating Existing Data

When updating existing data files:

1. Increment the version number according to the change impact
2. Update the `last_updated` timestamp
3. Document any breaking changes in the file's description
4. Ensure the file still validates against its schema
5. Consider creating migration scripts for major changes

## Best Practices

### Data Access Patterns

1. **Use the Registry**: Always access data through the `GameDataRegistry` rather than loading files directly
2. **Cache Wisely**: Cache data that is accessed frequently, but be mindful of memory usage
3. **Handle Missing Data**: Always handle the case where data might not be found
4. **Validate References**: Verify that cross-references between domains are valid

```python
# Good practice - handle missing data
biome = registry.get_biome(biome_id)
if biome:
    # Use the biome data
else:
    # Handle the case where the biome doesn't exist
```

### Data Modification

1. **Preserve Structure**: When modifying data at runtime, preserve the original structure
2. **Validation**: Validate modified data against the schema before using it
3. **Journaling**: Keep a record of modifications for potential rollback
4. **Event Emission**: Emit events when data is modified for other systems to react

### Cross-Domain References

When working with cross-domain references:

1. **Use Standard Formats**: Follow the reference format standards (see `DATA_STRUCTURE.md`)
2. **Resolving References**: Use the registry to resolve references to their actual data
3. **Circular References**: Be careful of circular references between domains
4. **Lazy Loading**: Consider lazy loading referenced data to improve performance

## Common Tasks

### Creating a New Domain

To create a new data domain:

1. Create a new directory in the appropriate location
2. Create a JSON schema for the domain in `/data/modding/schemas/`
3. Create an initial data file with the required metadata
4. Add a loader class to `/systems/data/loaders/`
5. Register the new domain in the `GameDataRegistry`
6. Add access methods to the registry

### Extending Existing Domains

To extend an existing domain:

1. Review the existing schema and data structure
2. Add new fields according to the schema's extension points
3. Update the schema if necessary, incrementing its version
4. Ensure backwards compatibility with existing data
5. Update any code that accesses this domain

### Working with Modding

To support modding:

1. Design domains with extension points in mind
2. Document schema constraints for modders
3. Provide validation tools for mod authors
4. Support overrides and additions to core data
5. Implement a load order for resolving conflicts

## Troubleshooting

### Common Issues

1. **Schema Validation Failures**: Check for missing required fields or incorrect data types
2. **Missing Data**: Verify file paths and registry initialization
3. **Cross-Reference Errors**: Ensure referenced IDs exist in their respective domains
4. **Performance Issues**: Look for excessive file I/O or deep object graphs

### Debugging Tools

1. **Schema Validation**: Use the validation tools in `/systems/data/utils/validation.py`
2. **Data Browser**: The built-in data browser can help inspect loaded data
3. **Logging**: Enable DEBUG logging for data access operations
4. **Event Listeners**: Register event listeners for data modification events

## API Reference

See the inline documentation in the following modules:

- `systems/data/loaders/game_data_registry.py`: Main data access interface
- `systems/data/models/`: Data model classes
- `systems/data/schemas/`: Pydantic schemas for validation
- `systems/data/utils/`: Utility functions for data processing

## Resources

- [JSON Schema Documentation](https://json-schema.org/learn/getting-started-step-by-step)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Visual DM Development Bible](../docs/Development_Bible.md) - See "Data Organization" section
