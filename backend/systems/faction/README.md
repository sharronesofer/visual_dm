# Faction System

This directory contains the faction system for Visual DM. The faction system is responsible for managing factions, their relationships, and diplomatic interactions in the game world.

## Structure

The faction system is organized using a layered architecture:

- **Models**: Data models for factions and faction relationships
- **Schemas**: Schema definitions and types
- **Services**: Business logic services
- **Repositories**: Data access layer
- **Utils**: Utility functions and validators

## Key Components

- **FactionManager**: Main entry point for other systems to interact with the faction system
- **Faction**: Represents a faction in the game world
- **FactionRelationship**: Represents diplomatic relationships between factions
- **FactionService**: Service for managing faction operations
- **FactionRelationshipService**: Service for managing faction relationships

## Usage

To use the faction system from another part of the codebase:

```python
from backend.systems.faction import FactionManager

# Initialize the manager with a database session
faction_manager = FactionManager(db_session)

# Create a faction
new_faction = faction_manager.create_faction(
    name="Kingdom of Eldoria",
    description="A prosperous kingdom in the western lands.",
    faction_type="KINGDOM",
    alignment="LAWFUL_GOOD",
    influence=75.0
)

# Set diplomatic stance between factions
faction_manager.set_diplomatic_stance(
    faction_id=1,
    other_faction_id=2,
    stance="FRIENDLY"
)
```

## Notes on Refactoring

This module has been refactored for better organization:

1. Simplified directory structure by removing unnecessary nested folders
2. Consolidated scattered functionality into core files
3. Introduced clear responsibility separation between layers
4. Standardized interfaces for better maintainability

The refactoring prioritized:
- Better code organization
- Clear separation of concerns
- Reduction of code duplication
- Consistent interface design
