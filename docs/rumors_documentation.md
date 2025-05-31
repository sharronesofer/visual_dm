# Rumor System Documentation

## Overview

The Rumor System provides a dynamic way to create, spread, and mutate information throughout the game world. Rumors are pieces of information that can change as they spread between entities, reflecting how real information often transforms as it passes from person to person.

This document outlines the key concepts, API endpoints, implementation details, and usage examples for the Rumor System.

## Key Concepts

### Rumors

A **Rumor** is a piece of information with the following characteristics:
- **Original Content**: The initial text content of the rumor
- **Categories**: Types of information (political, personal, danger, etc.)
- **Severity**: Impact level (trivial, minor, moderate, major, critical)
- **Truth Value**: How factually accurate the rumor is (0.0-1.0)
- **Originator**: The entity that created the rumor
- **Variants**: Modified versions of the rumor that emerge as it spreads
- **Spread**: Record of which entities know the rumor and how strongly they believe it

### Rumor Variants

As rumors spread, they can mutate into **Variants**:
- Each variant has its own content, which may differ from the original
- Variants are connected to their source (either the original or another variant)
- Entities may know different variants of the same rumor
- Variants track their mutation strength (how different they are from their source)

### Believability

Entities have varying levels of belief in rumors they've heard:
- **Believability** is measured on a scale from 0.0 (complete disbelief) to 1.0 (complete belief)
- The originator of a rumor typically has high believability
- Believability can be influenced by relationship factors when rumors spread
- Believability naturally decays over time if not reinforced

### Categories and Severity

Rumors are classified by both category and severity:
- **Categories** describe the subject matter (see `/data/builders/rumors/rumor_categories.json`)
- **Severity** indicates the impact or importance (see `/data/builders/rumors/rumor_severity.json`)
- These classifications affect how rumors spread and how entities respond to them

## API Endpoints

The Rumor System exposes the following FastAPI endpoints:

### Creating and Managing Rumors

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rumors` | POST | Create a new rumor in the system |
| `/rumors` | GET | Query rumors with optional filtering |
| `/rumors/{rumor_id}` | GET | Get detailed information about a specific rumor |
| `/rumors/{rumor_id}` | DELETE | Permanently delete a rumor and all its variants |

### Rumor Interactions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rumors/{rumor_id}/spread` | POST | Spread a rumor from one entity to another |
| `/rumors/{rumor_id}/believability` | POST | Update how believable an entity finds a rumor |
| `/rumors/decay` | POST | Apply natural decay to believability of all rumors |

## Usage Examples

### Creating a New Rumor

```python
# Python client example
import requests

response = requests.post(
    "http://localhost:8000/rumors",
    json={
        "originator_id": "npc_58",
        "content": "The duke plans to raise taxes next month.",
        "categories": ["political", "economic"],
        "severity": "moderate",
        "truth_value": 0.7,
        "initial_entities": ["npc_58", "npc_62", "npc_73"]
    }
)

rumor_id = response.json()["rumor"]["id"]
print(f"Created rumor with ID: {rumor_id}")
```

### Spreading a Rumor

```python
# Python client example
import requests

response = requests.post(
    f"http://localhost:8000/rumors/{rumor_id}/spread",
    json={
        "from_entity_id": "npc_58",
        "to_entity_id": "npc_104",
        "mutate": True,
        "mutation_strength": 0.3,
        "believe_modifier": 0.2
    }
)

result = response.json()
if result.get("mutated"):
    print(f"Rumor mutated to: {result['new_variant']['content']}")
else:
    print("Rumor spread without mutation")
```

### Querying Rumors

```python
# Python client example
import requests

# Get rumors about political matters with high truth value
response = requests.get(
    "http://localhost:8000/rumors",
    params={
        "categories": "political",
        "min_truth": 0.6,
        "limit": 10
    }
)

rumors = response.json()["rumors"]
for rumor in rumors:
    print(f"- {rumor['original_content']} (Truth: {rumor['truth_value']})")
```

## Implementation Details

### Rumor Storage

Rumors are stored as JSON files in the configured storage directory:
- Each rumor has its own file named with its UUID
- Files contain the full rumor data including variants and spread information
- The system maintains an in-memory cache for performance
- Changes are persisted to disk immediately

### Event Integration

The Rumor System integrates with the global event system:
- Events are fired when rumors are created, spread, or significantly mutated
- Other systems can subscribe to these events to react to rumor-related activities
- Event types include: `rumor.created`, `rumor.spread`, `rumor.mutated`, etc.

### Mutation Mechanism

Rumor mutation can occur in several ways:
1. **Template-based**: Using patterns from `/data/builders/rumors/rumor_mutation_templates.json`
2. **Random word substitution**: Replacing key words while preserving meaning
3. **AI-powered** (if configured): Using a language model to create realistic mutations

The mutation strength parameter (0.0-1.0) controls how dramatically rumors change.

## Extending the System

### Custom Mutation Handlers

You can provide a custom mutation handler function when initializing the RumorSystem:

```python
from backend.app.core.rumors.rumor_system import RumorSystem

async def my_custom_mutation(content, strength):
    # Custom logic to mutate content based on strength
    return modified_content

rumor_system = RumorSystem(
    storage_path="data/rumors/",
    default_decay_rate=0.05,
    gpt_mutation_handler=my_custom_mutation
)
```

### Adding New Categories

To add new rumor categories:
1. Edit `/data/builders/rumors/rumor_categories.json`
2. Add a new category entry with id, name, description, examples, and spread factors
3. Restart the application for changes to take effect

## Performance Considerations

- Rumor queries use in-memory filtering for optimal performance
- For large numbers of rumors (>10,000), consider implementing database storage
- Decay operations process all entity-rumor relationships and may be resource-intensive

## Testing

The system includes comprehensive unit tests in `/backend/app/core/tests/rumors/test_rumor_system.py` covering:
- Rumor creation and management
- Spreading mechanics with and without mutation
- Believability updates and decay
- Persistence and data integrity

## Integration with Other Systems

The Rumor System can be integrated with:

### Character Knowledge System
- Characters can learn rumors through conversation
- Knowledge can be tested in dialogue conditions
- Character personality traits can affect believability and spread

### Quest System
- Quests can be triggered by rumors reaching specific entities
- Quest objectives can include spreading or investigating rumors
- Rumors can provide clues for existing quests

### World Events
- Major events can automatically generate rumors
- Event outcomes can be influenced by what rumors entities believe
- Rumors can foreshadow upcoming events 