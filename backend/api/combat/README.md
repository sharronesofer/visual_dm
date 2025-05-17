# Combat Management System

This module implements a turn-based combat system for the Visual DM application, providing a robust API for managing combat encounters, tracking initiative, handling attacks, and managing status effects.

## Architecture

The combat system consists of the following components:

1. **Core Classes**
   - `CombatManager`: Manages the overall combat state, including initiative order, turns, and rounds
   - `Combatant`: Represents a character or creature in combat
   - `StatusEffect`: Represents a temporary effect applied to a combatant
   - `CombatLog`: Records combat events and provides a history of actions

2. **API Routes**
   - RESTful endpoints for interacting with the combat system
   - JSON-based request/response format for interoperability

3. **Utilities**
   - Dice rolling and parsing utilities
   - Data serialization/deserialization

## Key Features

- **Session-based combat management**: Create, manage, and end separate combat encounters
- **Initiative system**: Automatic or manual initiative tracking
- **Turn management**: Track whose turn it is and advance through combat rounds
- **Status effects**: Apply, manage, and automatically expire temporary effects
- **Attack resolution**: Handle attack rolls, damage calculation, and target HP changes
- **Terrain tracking**: Manage battlefield positions and terrain types
- **Combat log**: Detailed recording of all combat actions and events
- **Dice mechanics**: Support for standard dice notation, advantage/disadvantage, and critical hits

## API Usage

### Creating a Combat Session

```http
POST /combat/
```

Response:
```json
{
  "combat_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Adding Combatants

```http
POST /combat/{combat_id}/combatants
```

Request:
```json
{
  "name": "Aragorn",
  "type": "player",
  "initiative_bonus": 3,
  "hp": 45,
  "max_hp": 45,
  "armor_class": 16,
  "stats": {
    "strength": 16,
    "dexterity": 14,
    "constitution": 15,
    "intelligence": 12,
    "wisdom": 13,
    "charisma": 14
  },
  "position": [0, 0]
}
```

### Starting Combat

```http
POST /combat/{combat_id}/start
```

Response:
```json
{
  "status": "success",
  "initiative_order": ["combatant_1", "combatant_2", "combatant_3"],
  "current_turn": {
    "id": "combatant_1",
    "name": "Aragorn",
    ...
  }
}
```

### Advancing to Next Turn

```http
POST /combat/{combat_id}/next-turn
```

### Performing an Attack

```http
POST /combat/{combat_id}/attack
```

Request:
```json
{
  "attacker_id": "combatant_1",
  "target_id": "combatant_3",
  "attack_bonus": 5,
  "damage_dice": "1d8+3",
  "damage_type": "slashing",
  "advantage": false,
  "disadvantage": false
}
```

### Adding Status Effects

```http
POST /combat/{combat_id}/combatants/{combatant_id}/status-effects
```

Request:
```json
{
  "effect_type": "poisoned",
  "duration": 3,
  "source_id": "combatant_2",
  "intensity": 1,
  "effects": {
    "damage_per_turn": 5
  }
}
```

## Status Effect Types

The system supports the following status effects:

- `blinded`: Target has disadvantage on attacks and attackers have advantage
- `charmed`: Cannot attack the source and has disadvantage on social checks against source
- `deafened`: Cannot hear and has disadvantage on perception checks
- `frightened`: Has disadvantage on attacks and ability checks while source is visible
- `grappled`: Speed is 0 and cannot benefit from bonuses to speed
- `incapacitated`: Cannot take actions or reactions
- `invisible`: Attacker has advantage, and target has disadvantage on attacks
- `paralyzed`: Incapacitated and automatically fails Strength and Dexterity saves
- `petrified`: Transformed into solid substance, incapacitated, and resistant to all damage
- `poisoned`: Has disadvantage on attack rolls and ability checks
- `prone`: Has disadvantage on attack rolls and melee attackers have advantage
- `restrained`: Speed is 0, has disadvantage on attacks, and attackers have advantage
- `stunned`: Incapacitated, cannot move, and automatically fails Strength and Dexterity saves
- `unconscious`: Incapacitated, cannot move or speak, and automatically fails Strength and Dexterity saves

## Terrain Types

The system tracks the following terrain types:

- `normal`: Standard terrain with no special effects
- `difficult`: Costs double movement to traverse
- `cover_half`: Provides +2 AC and Dexterity saving throws
- `cover_three_quarters`: Provides +5 AC and Dexterity saving throws
- `cover_full`: Cannot be targeted directly by attacks or many spells
- `obscured`: Provides disadvantage on perception checks
- `hazardous`: Deals damage when entered or when ending turn there
- `liquid`: Requires swimming or special movement

## Testing

The module includes comprehensive unit tests in `tests.py` that demonstrate the functionality of all components.

## Future Improvements

- Spell casting and magical effects
- Area of effect attacks
- Opportunity attacks
- Cover calculations based on positions
- Line of sight calculations
- More sophisticated AI for monster decision making
- Support for custom status effects and terrain types 