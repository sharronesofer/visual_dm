# Rumor System

A comprehensive system for managing the creation, spread, and mutation of rumors between entities in Visual DM.

## Overview

The Rumor System models information diffusion through a social network of entities, with sophisticated mechanics for:

- Rumor creation with categories, severity, and truth values
- Realistic mutation as rumors spread
- Believability tracking per entity
- Decay over time for inactive rumors
- Extensible event system integration

## Architecture

The Rumor System uses a layered architecture:

1. **Models** (`models/rumor.py`): Core data structures for rumors and variants
2. **Repository** (`repository.py`): Data storage and retrieval
3. **Service** (`service.py`): Business logic for rumor operations
4. **API** (`api.py`): FastAPI endpoints for external integration
5. **Utilities** (`decay_and_propagation.py`): Helper functions for calculations

## Components

### Rumor Models

- `Rumor`: Main class with variants, spread tracking, and metadata
- `RumorVariant`: Individual rumor versions as they mutate
- `RumorSpread`: Tracks rumor spread to specific entities
- `RumorCategory`: Enumeration of rumor types
- `RumorSeverity`: Enumeration of severity levels

### Rumor Repository

Handles persistent storage of rumors using JSON files with:
- CRUD operations for rumors
- Query methods for entity-specific rumors
- Category filtering

### Rumor Service

Implements business logic for:
- Creating rumors with appropriate metadata
- Spreading rumors between entities with mutation
- Calculating believability based on relationships
- Applying decay over time
- Event emission for analytics

### Rumor API

FastAPI endpoints for:
- Creating new rumors
- Querying rumors by ID/entity/category
- Spreading rumors
- Managing rumor decay
- Listing all rumors

## Usage Examples

### Creating a New Rumor

```python
from backend.systems.rumor import RumorService, RumorCategory, RumorSeverity

service = RumorService()
rumor = service.create_rumor(
    originator_id="character_123",
    content="The king has hidden treasure in the castle basement.",
    categories=[RumorCategory.TREASURE],
    severity=RumorSeverity.MODERATE,
    truth_value=0.3  # Mostly false
)
```

### Spreading a Rumor

```python
success = service.spread_rumor(
    rumor_id=rumor.id,
    from_entity_id="character_123",
    to_entity_id="character_456",
    mutation_chance=0.2,
    relationship_factor=0.8,  # Strong positive relationship
    believability_modifier=0.1
)
```

### Querying Entity-Known Rumors

```python
rumors = service.get_rumors_by_entity(entity_id="character_456")
for rumor in rumors:
    content = rumor.get_current_content_for_entity("character_456")
    believability = rumor.get_believability_for_entity("character_456")
    print(f"Believes {believability:.1%}: {content}")
```

### Applying Rumor Decay

```python
decayed_count = service.decay_rumors(days_since_active=7)
print(f"Applied decay to {decayed_count} rumors")
```

## API Endpoints

| Endpoint                   | Method | Description                            |
|----------------------------|--------|----------------------------------------|
| `/rumors/`                 | POST   | Create a new rumor                     |
| `/rumors/`                 | GET    | List all rumors (optional category filter) |
| `/rumors/{rumor_id}`       | GET    | Get a specific rumor by ID             |
| `/rumors/{rumor_id}`       | DELETE | Delete a rumor                         |
| `/rumors/spread`           | POST   | Spread a rumor from one entity to another |
| `/rumors/entity/{entity_id}` | GET  | Get all rumors known by an entity      |
| `/rumors/decay`            | POST   | Apply decay to all rumors              |

## Integration With Other Systems

The Rumor System integrates with other systems through:

1. **Event Dispatcher**: Emits `RumorEvent` objects for other systems to consume
2. **Entity Interactions**: Connects entities through rumor spread
3. **Analytics**: Events can be captured for tracking rumor flow

## Future Improvements

1. Add LLM/GPT integration for realistic mutation generation
2. Implement network-based spread mechanics
3. Add visualization tools for rumor spread patterns
4. Extend category system with sub-categories

For more details, see code documentation in individual modules. 