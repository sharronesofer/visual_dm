# Data System Migration Notes

## Overview

The data system has been restructured to align with the Development Bible's specifications for a modular, event-driven architecture. This document summarizes the changes made and provides guidance for working with the new system.

## Key Changes

1. **Directory Structure Reorganization**
   - Moved from flat structure in `backend/data/rules_json` to domain-based organization in `backend/data/*`
   - Created specialized subdirectories for biomes, entities, items, systems, etc.
   - Organized systems data in dedicated subdirectories (memory, motif, rumor, faction, etc.)

2. **File Format Standardization**
   - Added metadata to all JSON data files (version, last_updated, description)
   - Wrapped actual data in a "data" field for better separation from metadata
   - Example:
     ```json
     {
       "version": "1.0.0",
       "last_updated": "2023-10-18T10:00:00Z",
       "description": "Descriptions of all biome types",
       "data": {
         // Actual data here
       }
     }
     ```

3. **Data Loading Utilities**
   - Created centralized utilities in `backend.systems.data.utils.data_file_loader`
   - Added support for loading data with metadata validation
   - Standardized error handling for missing or malformed files
   - Added utilities for bulk loading of directory contents

4. **GameDataRegistry Changes**
   - Updated to use the new directory structure and file format
   - Enhanced to use the new data loading utilities
   - Simplified loading code with the standard utilities

## Migration Tools

A migration script has been provided to help convert existing data files to the new format:

```bash
# Show what would be migrated without making changes
python backend/scripts/migrate_data_to_new_format.py --dry-run

# Run automatic migration for known files
python backend/scripts/migrate_data_to_new_format.py

# Run interactive migration for unmapped files
python backend/scripts/migrate_data_to_new_format.py --interactive
```

## Working with the New System

### Adding New Data Files

1. Create your data in the appropriate subdirectory under `backend/data/`
2. Use the standard format with metadata fields
3. Register the file in the `GameDataRegistry` if needed

### Loading Data

Always use the `GameDataRegistry` or the utility functions in `data_file_loader.py` to load data files. This ensures proper handling of the metadata wrapper and standardized error handling.

Example:
```python
from backend.systems.data.loaders.game_data_registry import GameDataRegistry

# Create registry
registry = GameDataRegistry()

# Load all data
registry.load_all()

# Access specific data
biome = registry.get_biome("Forest")
```

Or using the utilities directly:
```python
from backend.systems.data.utils.data_file_loader import load_data_file

# Load a specific file
biome_data = load_data_file("backend/data/biomes/land_types.json")
```

## Alignment with Development Bible

These changes bring the data system in line with the Development Bible by:

1. **Modular Organization**: Data is now organized by domain/responsibility
2. **Standardized Interface**: The GameDataRegistry provides a consistent interface
3. **Extensibility**: The directory structure makes it easy to add new data domains
4. **Versioning**: All data files now include version information
5. **Clear Responsibility Boundaries**: Each data domain has its own directory space

## Legacy Support

The system includes fallbacks for loading legacy-format data files, but all files should be migrated to the new format as soon as possible. 