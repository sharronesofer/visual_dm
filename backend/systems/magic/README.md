# Magic System

The Magic System is a comprehensive subsystem that handles all magic-related functionality in the Visual DM, including spells, magical abilities, spellbooks, spell effects, and spell slots.

## Core Features

- **Spells**: Create, cast, and manage spells with various effects
- **Magic Abilities**: Define and use innate or acquired magical abilities
- **Spellbooks**: Manage collections of spells for characters and NPCs
- **Spell Effects**: Track active magical effects on characters, objects, and locations
- **Spell Slots**: Resource management for spell casting
- **Magic Schools**: Categorize spells and abilities by traditional magic schools
- **Spell Components**: Define material, somatic, and verbal requirements for spells
- **Magic System Tick**: Process ongoing magical effects and regeneration

## Services

- **MagicService**: Core orchestrator that provides access to all magic functionalities
- **SpellService**: Manages spell creation, casting, and modifications
- **SpellbookService**: Handles spellbook operations like adding/removing spells
- **SpellEffectService**: Manages active spell effects including creation, updates, and ending effects
- **SpellSlotService**: Manages spell slot resources including creation, consumption, and refreshing

## Utility Functions

The magic system includes powerful utility functions for consistent rules enforcement:

- `calculate_spell_power`: Calculate spell power based on caster level and spell base power
- `validate_spell_requirements`: Check if a character meets the requirements to cast a spell
- `check_spell_compatibility`: Validate class and alignment compatibility with a spell
- `can_cast_spell`: Comprehensive check including requirements, compatibility, and resources
- `apply_spell_effect`: Apply a spell's effect to a target and generate resulting changes
- `calculate_spell_duration`: Determine effect duration based on spell and caster level
- `check_spell_slot_availability`: Verify slot availability for casting
- `calculate_spell_difficulty`: Determine save DC for spell effects
- `parse_spell_target_area`: Parse and normalize target area information
- `calculate_magic_learning_time`: Calculate time required to learn new spells
- `format_spell_duration`: Convert round-based durations to human-readable format
- `generate_effect_description`: Create human-readable descriptions of active effects

## API Endpoints

### Magic Abilities
- `POST /magic/abilities`: Create a new magic ability
- `GET /magic/abilities`: List magic abilities
- `GET /magic/abilities/{id}`: Get a specific magic ability
- `PUT /magic/abilities/{id}`: Update a magic ability
- `DELETE /magic/abilities/{id}`: Delete a magic ability

### Spells
- `POST /magic/spells`: Create a new spell
- `GET /magic/spells`: List spells with optional filtering
- `GET /magic/spells/{id}`: Get a specific spell
- `PUT /magic/spells/{id}`: Update a spell
- `DELETE /magic/spells/{id}`: Delete a spell
- `POST /magic/spells/{id}/cast`: Cast a spell

### Spellbooks
- `POST /magic/spellbooks`: Create a new spellbook
- `GET /magic/spellbooks`: List all spellbooks
- `GET /magic/spellbooks/{id}`: Get a specific spellbook
- `GET /magic/characters/{id}/spellbook`: Get a character's spellbook
- `POST /magic/spellbooks/{id}/spells/{spell_id}`: Add a spell to a spellbook
- `DELETE /magic/spellbooks/{id}/spells/{spell_id}`: Remove a spell from a spellbook

### Spell Effects
- `GET /magic/effects`: List active spell effects
- `GET /magic/effects/{id}`: Get a specific spell effect
- `DELETE /magic/effects/{id}`: End a spell effect
- `POST /magic/effects/{id}/dispel`: Attempt to dispel a spell effect
- `PUT /magic/effects/{id}/modify-duration`: Modify a spell effect's duration

### Spell Slots
- `POST /magic/characters/{id}/spell-slots`: Create spell slots for a character
- `GET /magic/characters/{id}/spell-slots`: Get a character's spell slots
- `GET /magic/characters/{id}/spell-slots/available`: Get a character's available spell slots
- `POST /magic/spell-slots/{id}/use`: Use a spell slot
- `POST /magic/characters/{id}/spell-slots/refresh`: Refresh a character's spell slots

### Magic System Utilities
- `POST /magic/system/process-tick`: Process a tick of the magic system
- `GET /magic/characters/{id}/magic-summary`: Get a summary of a character's magical abilities and resources

## Events

The magic system publishes the following events that other systems can subscribe to:

- **MagicAbilityEvent**: When a magic ability is used
- **SpellCastEvent**: When a spell is cast
- **SpellEffectEvent**: When a spell effect starts or ends
- **MagicSystemTickEvent**: When the magic system processes a tick

## Integration with Other Systems

The Magic System integrates with:

- **Character System**: For accessing character stats and applying spell effects
- **Combat System**: For spell casting in combat and effect processing during rounds
- **Item System**: For magic items and spell components
- **Event System**: For publishing and subscribing to magic-related events

## Data Model

- **MagicModel**: Base model for magical abilities
- **SpellModel**: Represents a spell with its effects and requirements
- **SpellEffect**: Tracks an active spell effect on a target
- **SpellSlot**: Resource for spell casting
- **Spellbook**: Collection of spells for a character or NPC
- **SpellComponent**: Components required for spell casting
- **SpellSchool**: Categories of magical disciplines

## Future Enhancements

Planned future enhancements include:

- **Ritual Casting**: Extended casting time for more powerful effects
- **Spell Preparation**: Daily preparation mechanics
- **Magic Items**: Integration with item enchantment system
- **Spell Creation**: Allow characters to research and create new spells
- **Spell Modification**: Allow characters to modify existing spells
