# Magic System

The Magic System is a comprehensive MP-based subsystem that handles all magic-related functionality in Visual DM, implementing the Development Bible's canonical magic system with Mana Points instead of spell slots.

## Core Features

- **MP-Based Spellcasting**: Uses Mana Points (MP) for resource management instead of D&D spell slots
- **Magic Domains**: Four domains (Arcane, Divine, Nature, Occult) with unique efficiency bonuses and primary abilities
- **Permanent Spell Learning**: Spells are learned permanently through abilities (no daily preparation)
- **Concentration Mechanics**: Advanced concentration tracking with break triggers and save mechanics  
- **Spell Effects**: Track active magical effects on characters, objects, and locations
- **Domain-Based Efficiency**: MP cost modifiers based on caster's domain specialization
- **Combat Integration**: Seamless integration with combat system for spell casting and effects

## Services

- **MagicBusinessService**: Core MP-based spell casting and domain mechanics
- **MagicCombatBusinessService**: Combat integration for spell casting and effect resolution
- **MetamagicService**: Advanced spell modification capabilities
- **SpellCombinationService**: Spell combination and synergy effects

## Utility Functions

The magic system includes powerful utility functions for consistent rules enforcement:

- `calculate_mp_cost`: Calculate MP cost with domain efficiency bonuses
- `can_cast_spell`: Comprehensive MP and domain compatibility checking
- `cast_spell`: Execute spell casting with full effect generation
- `calculate_spell_save_dc`: Calculate save DC using domain's primary ability
- `check_concentration`: Validate concentration requirements and triggers
- `apply_damage_with_resistances`: Handle damage type interactions and resistances
- `get_available_spells_for_domain`: Get spells available to specific magic domains

## API Endpoints

### Core Spellcasting (MP-Based)
- `GET /magic/spells`: List spells with domain and MP cost filtering
- `POST /magic/spells/cast`: Cast a spell using MP-based system
- `GET /magic/spells/available/{character_id}`: Get character's learned spells by domain

### MP Management (Canonical System)  
- `GET /magic/mp/{character_id}`: Get character's current MP status
- `POST /magic/mp/{character_id}/rest`: Restore MP through rest mechanics

### Domain Access (Permanent Learning)
- `GET /magic/domains/{character_id}`: Get character's domain access levels
- `POST /magic/domains/{character_id}`: Update domain access and mastery
- `POST /magic/spells/learn`: Learn a new spell permanently (no preparation)

### Concentration & Effects
- `GET /magic/concentration/{character_id}`: Get active concentration effects
- `DELETE /magic/concentration/{effect_id}`: End concentration effect
- `GET /magic/effects/{target_type}/{target_id}`: Get active effects on target

### Advanced Features
- `POST /magic/spells/cast-with-metamagic`: Cast spell with metamagic modifications
- `POST /magic/spells/cast-combination`: Cast spell combinations
- `GET /magic/metamagic/available/{spell_id}`: Get available metamagic options

### System Integration
- `POST /magic/system/process-tick`: Process magic system updates
- `GET /magic/characters/{id}/magic-summary`: Get character's magical capabilities

## Events

The Magic System publishes the following events to the EventDispatcher:

### MP-Based System Events
- `magic.mp.spent`: When MP is consumed for spellcasting
- `magic.mp.restored`: When MP is restored through rest or abilities  
- `magic.mp.insufficient`: When spell casting fails due to insufficient MP

### Spellcasting Events (Canonical)
- `magic.spell.cast.attempted`: When spell casting is initiated
- `magic.spell.cast.successful`: When spell casting succeeds with effects applied
- `magic.spell.cast.failed`: When spell casting fails due to validation or MP issues
- `magic.spell.learned`: When a character permanently learns a new spell

### Domain & Effect Events
- `magic.domain.accessed`: When a character gains access to a new magic domain
- `magic.concentration.started`: When a concentration effect begins
- `magic.concentration.broken`: When concentration is broken by damage/distraction
- `magic.effect.applied`: When a spell effect is successfully applied to a target
- `magic.effect.ended`: When an active spell effect expires or is ended

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
