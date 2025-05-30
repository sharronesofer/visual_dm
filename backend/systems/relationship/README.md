# Relationship System

This directory contains the relationship system implementation for managing all entity-to-entity relationships in the game.

## Overview

The relationship system handles connections between entities like:
- Character-to-Faction (membership, reputation)
- Character-to-Quest (status, progress)
- Character-to-Character (interpersonal relationships)
- Character-to-Location (spatial relationships)
- User-to-Character (authentication, permissions)

All relationships are managed through a standardized interface following the same data structure.

## Structure

The system follows a simplified, flat architecture with these main components:

- **relationship_model.py** - Data models and schemas for relationships
- **relationship_service.py** - Business logic for creating, updating, and querying relationships

## Usage Examples

```python
# Create a new relationship service
from backend.systems.relationship import RelationshipService, RelationshipType
service = RelationshipService()

# Create a faction relationship
faction_rel = service.add_relationship(
    character_id=character_uuid,
    target_id=faction_uuid,
    type=RelationshipType.FACTION,
    data={"reputation": 10, "standing": "Friendly"}
)

# Update faction reputation
updated_rel = service.update_faction_reputation(
    character_id=character_uuid,
    faction_id=faction_uuid,
    reputation_change=5
)

# Get all faction relationships for a character
faction_rels = service.get_character_faction_relationships(character_uuid)

# Update quest progress
quest_rel = service.update_quest_progress(
    character_id=character_uuid,
    quest_id=quest_uuid,
    progress=0.75,
    status="active"
)
```

## Key Features

- Typed relationship system with extensible data payloads
- Support for common relationship types: faction, quest, spatial, auth, interpersonal
- In-memory implementation with SQLAlchemy ORM comments for future persistence
- Helper methods for common operations (faction reputation, quest progress)
- Standardized relationship management across all entity types
