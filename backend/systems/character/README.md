# Character System

A comprehensive character management system for Visual DM, supporting player characters (PCs), non-player characters (NPCs), and full relationship management. The system uses JSON-driven configuration for validation, skills, personality traits, and progression rules.

## Features

- **Character Creation & Management**: Create, update, and manage character entities with comprehensive validation
- **JSON-Driven Configuration**: All validation rules, skills, personality traits, and progression rules are loaded from JSON configuration files
- **Relationship System**: Manage relationships between characters, factions, and quests
- **Mood & Goal Tracking**: Advanced emotional state and goal management
- **Hidden Personality System**: 6-attribute personality system (ambition, integrity, discipline, impulsivity, pragmatism, resilience)
- **Visual DM Attribute System**: Direct attribute assignment from -3 to +5 (no traditional ability score modifiers)
- **Equipment Integration**: Full integration with inventory and equipment systems
- **Database Compliance**: Uses standardized field naming (`stats` instead of `ability_scores`)

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

## JSON Configuration System

The character system now uses JSON configuration files for all validation and rules:

### Configuration Files

1. **`validation_rules.json`**: Core validation rules for character creation
   - Attribute value ranges (min/max/default)
   - Required fields for character creation
   - Name length restrictions
   - Skill selection limits
   - Personality attribute ranges

2. **`skills.json`**: Available skills and their properties
   - Skill names and descriptions
   - Associated ability scores
   - Skill categories and groupings

3. **`personality_traits.json`**: Personality trait definitions
   - Trait descriptions and behavioral indicators
   - Used for character development and NPC behavior

4. **`progression_rules.json`**: Character advancement rules
   - Experience point thresholds
   - Ability progression (7 base + 3 per level)
   - Level-based improvements

5. **`equipment_integration.json`**: Equipment system integration
   - Equipment slot definitions
   - Stat bonus calculations
   - Proficiency requirements

### Configuration Loading

Both `CharacterService` and `CharacterBuilder` now include `_load_json_config()` methods that:
- Load configuration files from `data/systems/character/`
- Handle missing files gracefully (return empty dict)
- Log errors for malformed JSON
- Provide fallback values when configuration is unavailable

## API Integration

### CharacterService

The main service class provides comprehensive character management:

```python
from backend.systems.character.services.character_service import CharacterService

# Initialize with database repository
service = CharacterService(character_repository)

# Create character using builder pattern
builder = CharacterBuilder()
builder.set_name("Adventurer").set_race("human").assign_attribute("STR", 2)
character = service.create_character_from_builder(builder)

# Validation uses JSON configuration automatically
service.validate_character_creation_data(character_data)
```

### CharacterBuilder

Enhanced builder pattern with JSON configuration validation:

```python
from backend.systems.character.services.character_builder import CharacterBuilder

# Builder automatically loads JSON configuration
builder = CharacterBuilder()

# All validation uses JSON rules
builder.set_name("Hero").set_race("elf")
builder.assign_attribute("INT", 3)  # Validates against JSON rules
builder.add_ability("arcane_initiate")  # Validates against ability limits

# Finalization includes comprehensive validation
character_data = builder.finalize()
```

## Database Schema Compliance

The system now uses standardized database field names:
- **`stats`**: Character attribute scores (was `ability_scores`)
- **`skills`**: Skill proficiencies and bonuses
- **`hidden_personality`**: 6-attribute personality system
- **`level`**, **`experience_points`**: Progression tracking

Database schema documentation has been updated to reflect actual implementation.

## Testing

Comprehensive test suite includes:
- JSON configuration loading tests
- Validation rule compliance testing
- Character creation and update operations
- Error handling for malformed configurations
- Integration tests with database and services

### Running Tests

```bash
# Run character system tests
pytest backend/systems/character/tests/

# Run specific configuration tests
pytest backend/systems/character/tests/test_character_service.py::TestCharacterConfigurationLoading
```

## Development Bible Compliance

This system is fully compliant with the Development Bible requirements:

✅ **Complete Implementation**: All core functionality implemented
✅ **JSON Configuration**: Rules and validation driven by JSON files
✅ **Database Standards**: Uses standardized field naming
✅ **Test Coverage**: Comprehensive test suite for all functionality
✅ **Documentation**: Complete API and usage documentation
✅ **Error Handling**: Graceful degradation for missing/malformed configs

## Example Usage

### Basic Character Creation

```python
# Create a character using the builder pattern
builder = CharacterBuilder()
character_data = (builder
    .set_name("Elara Moonwhisper")
    .set_race("elf")
    .assign_attribute("INT", 4)
    .assign_attribute("WIS", 3)
    .assign_attribute("CHA", 2)
    .add_ability("arcane_initiate")
    .add_ability("keen_senses")
    .assign_skill("Arcana")
    .assign_skill("Investigation")
    .finalize())

# Create in database
character = character_service.create_character_from_builder(builder)
```

### Validation with JSON Configuration

```python
# Validation automatically uses JSON configuration
character_data = {
    'name': 'Test Character',
    'race': 'human',
    'stats': {'STR': 2, 'DEX': 1, 'CON': 3, 'INT': 0, 'WIS': 1, 'CHA': -1},
    'skills': {'Athletics': {'proficient': True}, 'Stealth': {'proficient': True}},
    'hidden_personality': {'ambition': 4, 'integrity': 3, 'discipline': 2}
}

# This will validate against JSON rules automatically
character_service.validate_character_creation_data(character_data)
```

## Migration Notes

When upgrading existing characters:
1. **Field Names**: `ability_scores` → `stats` in database
2. **Configuration**: Validation now uses JSON files instead of hardcoded constants
3. **Skills**: Skill validation checks against `skills.json`
4. **Personality**: Hidden personality validation uses JSON configuration ranges

The system maintains backward compatibility while providing enhanced validation and configuration flexibility. 