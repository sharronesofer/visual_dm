# Region System

The Region System manages geographical divisions of the game world, their properties, and relationships. Regions provide the spatial framework for the game world and influence many other systems.

## Features

- Geographical region definition and boundaries
- Region-specific properties (biome, resources, etc.)
- Region relationships (borders, trade routes, etc.)
- Region-level events and state tracking

## Module Structure

- `schemas.py` - Data models for regions and coordinates
- `repository.py` - Data access layer for region persistence
- `service.py` - Business logic for region management
- `router.py` - FastAPI endpoints for region operations
- `utils.py` - Utility functions for world generation, tension management, and other region-related calculations

## Key Components

- `WorldGenerator` - Creates and manages world regions
- `TensionManager` - Handles tension levels between regions and factions
- Region APIs for creating, retrieving, and updating region data
- Location mapping and weather simulation utilities

## Integration Points

- Provides spatial context for game events
- Defines travel routes and distances
- Influences faction control and conflicts
- Affects resource availability and trade

Refer to the Development Bible for detailed design documentation.
