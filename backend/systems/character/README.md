# Character System

This directory contains the refactored, consolidated character system for Visual DM. The system provides models, services, repositories, and utilities for handling all character-related functionality including statistics, traits, skills, and visual representation.

## Directory Structure

```
character/
├── models/                 # Data models
│   ├── character.py        # Core Character ORM model
│   ├── character_builder.py # Character creation builder pattern
│   ├── visual_model.py     # 3D visual representation models
│   └── __init__.py
├── services/               # Business logic
│   ├── character_service.py # Character operations
│   └── __init__.py
├── repositories/           # Data access
│   ├── character_repository.py # Database operations
│   └── __init__.py
├── utils/                  # Utility functions
│   ├── character_utils.py  # Character stat calculations
│   ├── visual_utils.py     # Visual model helpers
│   └── __init__.py
└── __init__.py             # Root package exports
```

## Usage Examples

### Creating a Character

```python
from backend.systems.character import CharacterBuilder, CharacterService

# Create a character builder
builder = CharacterBuilder()
builder.character_name = "Tordek"
builder.set_race("dwarf")
builder.assign_attribute("STR", 16)
builder.assign_attribute("CON", 16)
builder.assign_skill("survival")
builder.apply_starter_kit("warrior")

# Save the character
service = CharacterService()
character = service.create_character_from_builder(builder)
```

### Retrieving a Character

```python
from backend.systems.character import CharacterService

service = CharacterService()
character = service.get_character_by_id(character_id)
```

### Creating a Visual Model

```python
from backend.systems.character import CharacterModel, MeshSlot, BlendShape

# Create a visual model for rendering
model = CharacterModel(
    race="dwarf",
    base_mesh="dwarf_male",
    mesh_slots={
        "hair": MeshSlot("hair", "dwarf_hair_long"),
        "beard": MeshSlot("beard", "dwarf_beard_full")
    },
    blendshapes={
        "browThickness": BlendShape("browThickness", 0.7),
        "noseWidth": BlendShape("noseWidth", 0.6)
    }
)

# Swap a mesh
model.swap_mesh("beard", "dwarf_beard_braided")

# Adjust a blend shape
model.set_blendshape("noseWidth", 0.8)
```

### Serialization and Randomization

```python
from backend.systems.character import (
    serialize_character, deserialize_character, RandomCharacterGenerator
)

# Serialize to JSON
json_data = serialize_character(model)

# Deserialize from JSON
model = deserialize_character(json_data, CharacterModel)

# Generate random features
generator = RandomCharacterGenerator({
    "hair_color": {"blonde": 0.2, "brown": 0.5, "black": 0.3},
    "skin_tone": {"light": 0.3, "medium": 0.5, "dark": 0.2}
})
random_features = generator.generate()
```

## Refactoring Notes

The character system has been refactored to consolidate duplicate functionality and improve organization:

1. Eliminated duplicate character model files
2. Consolidated visual model files into a single coherent module
3. Separated concerns into models, services, repositories, and utilities
4. Standardized naming conventions and import paths
5. Added proper documentation and type hints
6. Ensured backward compatibility through the public API

## Integration Points

- **ORM Integration**: Character and Skill models are SQLAlchemy ORM models
- **Frontend Integration**: Visual models provide serialization to JSON for frontend rendering
- **Service Layer**: CharacterService provides the main entry point for character operations
- **Builder Pattern**: CharacterBuilder simplifies character creation with a fluent API 