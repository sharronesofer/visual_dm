# Canonical Magic System Documentation

## Overview

The magic system implements the Development Bible's canonical MP-based spellcasting system, replacing traditional D&D spell slots with a more flexible and intuitive Matrix Points (MP) system.

## Core Principles

### 1. MP-Based Spellcasting
- **No Spell Slots**: Characters use Matrix Points (MP) instead of daily spell slots
- **Flexible Casting**: Any spell can be cast as long as MP is available
- **MP Regeneration**: MP restores over time through rest, not daily resets

### 2. Domain-Based Magic
- **Four Canonical Domains**:
  - **Arcane** (Intelligence): 1.0 MP efficiency, pure magical theory
  - **Divine** (Wisdom): 0.9 MP efficiency, divine power channeling  
  - **Nature** (Wisdom): 0.8 MP efficiency, natural force manipulation
  - **Occult** (Charisma): 1.2 MP efficiency, forbidden/costly knowledge

### 3. Permanent Spell Learning
- **No Daily Preparation**: Once learned, spells are permanently known
- **Domain Restrictions**: Spells can only be learned through compatible domains
- **Progressive Mastery**: Spell mastery reduces MP costs over time

### 4. Concentration System
- **Active Effect Tracking**: Concentration spells tracked with duration
- **Single Concentration**: Only one concentration spell active per caster
- **Automatic Cleanup**: Effects end when concentration is broken

## Database Schema

### Core Tables

#### Spells
```sql
- id: UUID (Primary Key)
- name: VARCHAR(255) UNIQUE
- school: VARCHAR(50) -- Traditional D&D schools for categorization
- mp_cost: INTEGER -- MP cost instead of spell level
- valid_domains: TEXT[] -- Array of domains that can cast this spell
- casting_time: VARCHAR(100)
- range_feet: INTEGER -- Range in feet
- components: TEXT[] -- Array of component types
- duration: VARCHAR(100)
- description: TEXT
- base_damage: INTEGER -- Numeric damage (not dice)
- base_healing: INTEGER -- Numeric healing (not dice)
- mp_scaling: INTEGER -- Extra damage/healing per extra MP
- damage_type: VARCHAR(50)
- save_type: VARCHAR(50) -- none, fortitude, reflex, will
- save_for_half: BOOLEAN
- concentration: BOOLEAN
- duration_seconds: INTEGER -- Duration in seconds
- area_of_effect: VARCHAR(100)
- target: VARCHAR(100)
- auto_hit: BOOLEAN
```

#### Character MP Tracking
```sql
- character_id: INTEGER (Foreign Key to characters)
- current_mp: INTEGER
- max_mp: INTEGER
- mp_regeneration_rate: FLOAT -- MP per hour of rest
- last_rest: TIMESTAMP
```

#### Character Domain Access
```sql
- character_id: INTEGER (Foreign Key)
- domain: VARCHAR(50) -- arcane, divine, nature, occult
- access_level: INTEGER -- Mastery level in domain
- unlocked_at: TIMESTAMP
```

#### Learned Spells
```sql
- character_id: INTEGER (Foreign Key)
- spell_id: UUID (Foreign Key to spells)
- domain_learned: VARCHAR(50) -- Domain through which spell was learned
- learned_at: TIMESTAMP
- mastery_level: INTEGER -- Affects MP cost efficiency
```

#### Concentration Tracking
```sql
- caster_id: INTEGER (Foreign Key)
- spell_id: UUID (Foreign Key)
- target_id: INTEGER (Optional Foreign Key)
- cast_at: TIMESTAMP
- expires_at: TIMESTAMP
- domain_used: VARCHAR(50)
- mp_spent: INTEGER
- effect_data: JSONB -- Spell-specific data
```

## API Endpoints

### Spell Management

#### GET `/spells`
Get all spells with optional filtering:
- `?domain=arcane` - Filter by domain
- `?school=evocation` - Filter by school
- `?max_mp_cost=15` - Filter by MP cost

#### GET `/spells/available/{character_id}`
Get spells available to character based on domain access:
- `?domain=arcane` - Filter by specific domain

#### POST `/spells/learn`
Learn a new spell permanently:
```json
{
  "spell_id": "uuid",
  "domain": "arcane",
  "learning_method": "study"
}
```

### Spell Casting

#### POST `/spells/cast`
Cast a spell using MP:
```json
{
  "spell_id": "uuid",
  "domain": "arcane",
  "target_id": "uuid",
  "extra_mp": 5
}
```

### MP Management

#### GET `/mp/{character_id}`
Get character's current MP status:
```json
{
  "character_id": 1,
  "current_mp": 45,
  "max_mp": 100,
  "mp_regeneration_rate": 2.0,
  "mp_percentage": 45.0
}
```

#### POST `/mp/{character_id}/rest`
Restore MP through rest:
```json
{
  "rest_type": "short|long|full",
  "hours_rested": 8.0
}
```

### Domain Management

#### GET `/domains/{character_id}`
Get character's domain access levels:
```json
[
  {
    "domain": "arcane",
    "access_level": 3,
    "efficiency_bonus": 1.0
  }
]
```

#### POST `/domains/{character_id}`
Update domain access:
```json
{
  "domain": "occult",
  "access_level": 2
}
```

### Concentration Tracking

#### GET `/concentration/{character_id}`
Get active concentration effects

#### DELETE `/concentration/{effect_id}`
End a concentration effect

## Business Logic

### MP Cost Calculation
```python
def calculate_mp_cost(base_cost: int, extra_mp: int, domain_efficiency: float, mastery_level: int) -> int:
    # Apply domain efficiency
    domain_cost = base_cost * domain_efficiency
    
    # Apply mastery reduction (10% per level above 1)
    mastery_multiplier = 1.0 - ((mastery_level - 1) * 0.1)
    
    # Calculate final cost
    final_cost = int((domain_cost * mastery_multiplier) + extra_mp)
    
    return max(1, final_cost)  # Minimum 1 MP
```

### Spell Attack Resolution
```python
def resolve_spell_attack(spell_attack_bonus: int, target_ac: int) -> bool:
    import random
    roll = random.randint(1, 20)
    return (roll + spell_attack_bonus) >= target_ac
```

### Damage Calculation
```python
def calculate_spell_damage(base_damage: int, extra_mp: int, mp_scaling: int) -> int:
    return base_damage + (extra_mp * mp_scaling)
```

## Configuration Files

### Domain Configuration (`data/systems/magic/magic_domains.json`)
```json
{
  "domains": {
    "arcane": {
      "name": "Arcane",
      "description": "Pure magical theory and manipulation",
      "primary_ability": "intelligence",
      "mp_efficiency": 1.0,
      "color": "#4a90e2"
    },
    "divine": {
      "name": "Divine",
      "description": "Power channeled through divine entities",
      "primary_ability": "wisdom", 
      "mp_efficiency": 0.9,
      "color": "#f5d76e"
    },
    "nature": {
      "name": "Nature",
      "description": "Manipulation of natural forces",
      "primary_ability": "wisdom",
      "mp_efficiency": 0.8,
      "color": "#7cb342"
    },
    "occult": {
      "name": "Occult",
      "description": "Forbidden knowledge with hidden costs",
      "primary_ability": "charisma",
      "mp_efficiency": 1.2,
      "color": "#8e24aa"
    }
  }
}
```

### Spell Configuration (`data/systems/magic/spells.json`)
```json
{
  "spells": {
    "fireball": {
      "mp_cost": 15,
      "school": "evocation",
      "valid_domains": ["arcane", "occult"],
      "base_damage": 28,
      "mp_scaling": 3,
      "damage_type": "fire",
      "save_type": "reflex",
      "save_for_half": true,
      "concentration": false,
      "range_feet": 400,
      "area_of_effect": "20ft_radius"
    }
  }
}
```

## Migration from D&D System

The system includes a migration script (`backend/migrations/001_migrate_magic_to_canonical_mp_system.py`) that:

1. **Backs up existing data** from D&D spell slot tables
2. **Drops old tables**: `spell_slots`, `spellbooks`, `prepared_spells`, etc.
3. **Updates spell structure** to use MP costs and domains
4. **Creates canonical tables** for MP tracking and domain access
5. **Migrates data** from spell slots to MP system

### Running Migration
```bash
cd backend/migrations
python 001_migrate_magic_to_canonical_mp_system.py
```

## Testing

### Test Categories

#### Unit Tests (`backend/tests/systems/magic/test_business_logic.py`)
- MP cost calculations
- Domain efficiency application
- Spell attack resolution
- Damage calculations
- Concentration management

#### Model Tests (`backend/tests/systems/magic/test_models.py`)
- Database model validation
- Relationship integrity
- Constraint enforcement

#### Integration Tests (`backend/tests/integration/test_magic_full_stack.py`)
- End-to-end API workflows
- Database persistence
- Error handling
- Character integration

### Running Tests
```bash
# Run all magic system tests
pytest backend/tests/systems/magic/ -v

# Run integration tests
pytest backend/tests/integration/test_magic_full_stack.py -v

# Run with coverage
pytest backend/tests/systems/magic/ --cov=backend.systems.magic
```

## Performance Considerations

### Database Indexing
```sql
-- Spell lookups
CREATE INDEX idx_spells_domain ON spells USING GIN(valid_domains);
CREATE INDEX idx_spells_mp_cost ON spells(mp_cost);
CREATE INDEX idx_spells_school ON spells(school);

-- Character queries
CREATE INDEX idx_character_mp_character_id ON character_mp(character_id);
CREATE INDEX idx_domain_access_character_id ON character_domain_access(character_id);
CREATE INDEX idx_learned_spells_character_id ON learned_spells(character_id);
CREATE INDEX idx_concentration_caster_id ON concentration_tracking(caster_id);
```

### Caching Strategy
- **Spell definitions**: Cache in Redis with 1-hour TTL
- **Domain configurations**: Cache in memory (rarely change)
- **Character MP status**: Cache for 5 minutes
- **Active concentrations**: Cache for 1 minute

## Security Considerations

### Domain Access Validation
- Always verify character has domain access before spell operations
- Check spell domain compatibility before learning
- Validate MP availability before casting

### Input Validation
- Sanitize all spell and character IDs
- Validate MP costs and extra MP amounts
- Check concentration effect data for malicious content

### Rate Limiting
- Limit spell casting attempts per character per minute
- Throttle spell learning operations
- Monitor for unusual MP deduction patterns

## Development Guidelines

### Adding New Spells
1. Define spell in `data/systems/magic/spells.json`
2. Specify valid domains and MP costs
3. Add damage/healing values (numeric, not dice)
4. Test with integration test suite

### Domain Extensions
1. Update domain configuration JSON
2. Add domain to `MagicDomain` enum
3. Update business logic for domain-specific rules
4. Test efficiency calculations

### Business Logic Changes
1. Implement in business services layer
2. Add comprehensive unit tests
3. Update integration tests
4. Document API changes

## Troubleshooting

### Common Issues

#### Character Can't Cast Spells
- Check character has MP tracking record
- Verify domain access permissions
- Confirm spell is learned through accessible domain

#### MP Not Deducting
- Check database transaction commits
- Verify business logic calculations
- Ensure no rollbacks on spell cast errors

#### Concentration Not Working
- Verify concentration tracking table exists
- Check for proper effect cleanup on new concentration
- Validate duration calculations

### Debug Commands
```bash
# Check character MP status
curl GET /magic/mp/{character_id}

# List character domains
curl GET /magic/domains/{character_id}

# View available spells
curl GET /magic/spells/available/{character_id}

# Check active concentration
curl GET /magic/concentration/{character_id}
```

## Future Enhancements

### Planned Features
- **Metamagic Effects**: Spell modifications using extra MP
- **Spell Combinations**: Combining multiple spells for enhanced effects
- **MP Pool Sharing**: Party-wide MP sharing mechanics
- **Dynamic Difficulty**: MP costs based on environmental factors

### Optimization Opportunities
- **Batch Spell Operations**: Multiple spell casts in single transaction
- **Predictive Caching**: Pre-load likely-to-be-cast spells
- **MP Regeneration Scheduling**: Background tasks for MP restoration
- **Spell Effect Pooling**: Reuse common spell effect objects 