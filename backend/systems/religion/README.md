# Religion System

This module implements the canonical religion system for Visual DM as described in the Development Bible. It manages religion entities, membership, and narrative hooks, with integration points for faction and quest systems.

## Core Features

- **Religion Management**: Create, retrieve, update, and delete religions with various attributes (type, tenets, holy places, etc.)
- **Membership Tracking**: Manage entity membership in religions, including devotion levels, roles, and public/private status
- **Narrative Integration**: Hooks for religion events to trigger narrative arcs, quests, and motif changes
- **Faction Synchronization**: Link religions with factions, supporting cross-faction membership
- **Persistence**: JSON-based data storage for religions and memberships

## Usage Examples

```python
# Get the religion service singleton
from backend.systems.religion import get_religion_service

religion_service = get_religion_service()

# Create a new religion
sun_cult = religion_service.create_religion({
    "name": "Sun Cult",
    "description": "Worshippers of the sun god Ra",
    "type": ReligionType.POLYTHEISTIC,
    "tenets": ["Honor the sunrise", "Sacrifice at noon", "Pray for light"],
    "holy_places": ["Temple of Ra"],
    "region_ids": ["region1", "region2"]
})

# Create a membership
membership = religion_service.create_membership({
    "entity_id": "character123",
    "religion_id": sun_cult.id,
    "devotion_level": 75,
    "status": "priest",
    "role": "sun caller"
})

# Update devotion level
religion_service.update_devotion("character123", sun_cult.id, 10)  # Increase by 10

# Trigger a narrative hook
religion_service.trigger_narrative_hook(
    "character123", 
    sun_cult.id, 
    "promotion", 
    {"new_role": "high priest"}
)

# Synchronize with faction
religion_service.sync_with_faction("faction_sun_empire", sun_cult.id)
```

## Integration Points

- **Faction System**: Links religions to factions, allowing religious factions with shared membership
- **Quest/Narrative System**: Religion events can trigger narrative arcs and quests
- **Entity System**: Entities (characters, NPCs) can join religions with varying devotion levels
- **Region System**: Religions can be linked to specific regions for geographic distribution

## Architecture

The Religion System follows a modular architecture with clear separation of concerns:

### Repository Layer
- **ReligionRepository**: Handles data persistence and retrieval for religions and memberships

### Service Layer
- **ReligionService**: Main facade service integrating all specialized services
- **ReligionMembershipService**: Manages membership operations and devotion calculation
- **ReligionNarrativeService**: Handles narrative hooks and event generation
- **ReligionFactionService**: Manages integration with the faction system

### Model Layer
- **models.py**: Core data models (Religion, ReligionType, ReligionMembership)
- **schemas.py**: API schemas for data validation and serialization

### Utility Layer
- **utils.py**: Helper functions for calculations and text generation

## Directory Structure

```
backend/systems/religion/
├── __init__.py            # Public exports
├── models.py              # Core data models
├── schemas.py             # API schemas
├── services.py            # Main service facade
├── repository.py          # Data persistence layer
├── membership_service.py  # Membership operations
├── narrative_service.py   # Narrative hooks and events
├── faction_service.py     # Faction integration
├── utils.py               # Utility functions
├── data/                  # Data storage directory
│   └── religion_templates.json  # Template data
└── README.md              # Documentation
```

## Future Enhancements

- Add support for religious calendar events and holidays
- Implement religious spread mechanics across regions
- Develop schism mechanics similar to faction schisms
- Add deeper integration with the motif system for narrative impact
