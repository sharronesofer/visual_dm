# Equipment Durability System

## Overview

The Equipment Durability System provides comprehensive management of equipment wear, damage, and repair throughout Visual DM. This system consolidates previously scattered durability logic into a centralized, efficient architecture.

## Architecture

### Core Services

#### 1. `DurabilityService` - Core Calculations
**Purpose:** Centralized durability calculations and condition management  
**Location:** `backend/systems/equipment/services/durability_service.py`

**Key Features:**
- Time-based degradation calculations
- Combat damage modeling
- Environmental wear simulation
- Condition status mapping
- Stat penalty application
- Repair cost estimation

**Usage Example:**
```python
from backend.systems.equipment.services.durability_service import DurabilityService

durability_service = DurabilityService(db_session)

# Calculate time-based degradation
decay, details = durability_service.calculate_time_degradation(
    equipment_id="sword_001",
    quality=EquipmentQuality.MILITARY,
    last_update=datetime.now() - timedelta(days=1),
    usage_intensity=1.5,
    environment="desert"
)

# Get condition effects
condition = durability_service.get_condition_effects(durability=45.5)
print(f"Status: {condition['status']}, Effectiveness: {condition['effectiveness_percentage']}%")
```

#### 2. `EquipmentDurabilityIntegration` - System Integration
**Purpose:** Unified interface for cross-system durability management  
**Location:** `backend/systems/equipment/services/equipment_durability_integration.py`

**Key Features:**
- Cross-system durability updates
- Combat integration
- Stat penalty integration
- Repair recommendations
- Bulk operations

**Usage Example:**
```python
from backend.systems.equipment.services.equipment_durability_integration import EquipmentDurabilityIntegration

integration = EquipmentDurabilityIntegration(db_session)

# Process comprehensive durability update
result = integration.process_equipment_durability_update(
    character_id="char_123",
    time_elapsed_hours=24.0,
    combat_events=[...],
    environmental_exposure={'environment': 'swamp', 'exposure_hours': 24.0},
    usage_intensity=1.2
)

# Get repair recommendations
recommendations = integration.get_repair_recommendations(
    character_id="char_123",
    max_total_cost=500.0,
    priority_threshold="urgent"
)
```

#### 3. `RepairService` - Repair Management
**Purpose:** Equipment repair workflow and mechanics  
**Location:** `backend/systems/repair/services/repair_service.py`

**Key Features:**
- Repair request management
- Success/failure mechanics
- Cost and time estimation
- Repairer management
- Economic integration

**Usage Example:**
```python
from backend.systems.repair.services.repair_service import RepairService

repair_service = RepairService(db_session)

# Create repair request
request = repair_service.create_repair_request(
    equipment_id="sword_001",
    character_id="char_123",
    target_durability=100.0,
    max_cost=200.0
)

# Execute repair
result = repair_service.execute_repair(
    repair_request_id=request["repair_request_id"],
    repairer_id="blacksmith_001",
    repairer_skill_level="expert"
)
```

## Equipment Condition System

### Condition Thresholds

| Condition | Durability Range | Stat Penalty | Description |
|-----------|------------------|--------------|-------------|
| Perfect | 100% | 0% | No wear, maximum effectiveness |
| Excellent | 90-99% | 0% | Minimal wear, no penalties |
| Good | 75-89% | 0% | Normal wear, fully functional |
| Worn | 50-74% | 10% | Visible wear, slight reduction |
| Damaged | 25-49% | 25% | Significant damage, reduced effectiveness |
| Very Damaged | 10-24% | 50% | Heavily damaged, barely functional |
| Broken | 0-9% | 100% | Cannot be equipped or used |

### Stat Penalty Calculation

Equipment stats are automatically reduced based on condition:

```python
effective_stat = base_stat * (1 - penalty_multiplier)
```

Example:
- Base Attack Bonus: +5
- Durability: 30% (Damaged condition)
- Penalty Multiplier: 0.25 (25%)
- Effective Attack Bonus: +5 * (1 - 0.25) = +3.75 → +4

## Degradation Mechanics

### Time-Based Degradation

Equipment degrades over time based on:
- **Quality Level:** Higher quality lasts longer
- **Usage Intensity:** Heavy use accelerates wear
- **Environment:** Harsh conditions increase degradation
- **Random Variance:** Natural wear variation

**Environmental Factors:**
- Normal: 1.0x degradation
- Rain: 1.3x degradation
- Desert: 1.4x degradation
- Swamp: 1.5x degradation
- Magic Zone: 1.6x degradation
- Underground: 0.9x degradation

### Combat Degradation

Equipment takes damage during combat:
- **Weapons:** 0.5% base damage per hit
- **Armor:** 0.2% base damage when struck
- **Shields:** 0.3% base damage when blocking
- **Accessories:** 0.1% base damage

**Modifiers:**
- Critical hits deal 2x weapon durability damage
- Armor stress scales with damage taken (5% of damage dealt)
- Shield stress scales with blocks made (0.2% per block)

### Environmental Degradation

Extended exposure to harsh environments causes additional wear:
- Material resistance affects degradation rate
- Exposure duration accumulates damage
- Equipment type vulnerability varies

## Integration Guide

### Combat System Integration

```python
# In combat processing
combat_result = integration.process_combat_durability_damage(
    combat_participants=[
        {
            'character_id': 'char_123',
            'combat_events': [
                {
                    'equipment_id': 'sword_001',
                    'equipment_type': 'weapon',
                    'intensity': 1.2,
                    'is_critical': True
                }
            ]
        }
    ],
    combat_duration_rounds=8,
    combat_intensity=1.3
)
```

### Time System Integration

```python
# In time advancement processing
for character_id in active_characters:
    result = integration.process_equipment_durability_update(
        character_id=character_id,
        time_elapsed_hours=hours_passed,
        environmental_exposure={
            'environment': get_character_environment(character_id),
            'exposure_hours': hours_passed
        },
        usage_intensity=get_character_activity_level(character_id)
    )
```

### Equipment System Integration

```python
# In equipment stat calculation
def get_equipment_stats(equipment_id):
    base_stats = get_base_equipment_stats(equipment_id)
    effective_stats = integration.get_equipment_effective_stats(
        equipment_id=equipment_id,
        base_stats=base_stats
    )
    return effective_stats
```

## Best Practices

### 1. Use Integration Service for Cross-System Operations
Always use `EquipmentDurabilityIntegration` when multiple systems need durability updates:

```python
# ✅ Good: Use integration service
integration.process_equipment_durability_update(...)

# ❌ Avoid: Direct service calls from other systems
durability_service.calculate_time_degradation(...)
```

### 2. Check Equipment Usability Before Actions
Validate equipment condition before use:

```python
is_usable, reason, condition = integration.validate_equipment_usability(
    equipment_id="sword_001",
    action_type="combat"
)

if not is_usable:
    return {"error": f"Cannot use equipment: {reason}"}
```

### 3. Provide Repair Recommendations
Help players maintain their equipment:

```python
recommendations = integration.get_repair_recommendations(
    character_id="char_123",
    priority_threshold="recommended"
)

if recommendations['recommendations_count'] > 0:
    notify_player_repair_needed(recommendations)
```

### 4. Batch Process for Performance
Use bulk operations for multiple characters:

```python
# Process time degradation for all characters
bulk_result = integration.bulk_process_time_degradation(
    character_ids=all_character_ids,
    hours_elapsed=24.0,
    environmental_conditions=character_environments
)
```

## Testing

### Unit Tests
Test individual durability calculations:

```python
def test_durability_calculation():
    service = DurabilityService(mock_db)
    decay, details = service.calculate_time_degradation(
        equipment_id="test_001",
        quality=EquipmentQuality.BASIC,
        last_update=datetime.now() - timedelta(days=1)
    )
    assert decay > 0
    assert 'total_decay' in details
```

### Integration Tests
Test cross-system durability updates:

```python
def test_combat_durability_integration():
    integration = EquipmentDurabilityIntegration(mock_db)
    result = integration.process_combat_durability_damage(
        combat_participants=test_participants,
        combat_duration_rounds=5
    )
    assert result['combat_durability_updates']
```

## Performance Considerations

### 1. Bulk Operations
- Use bulk processing for time-based updates
- Batch database updates when possible
- Cache frequently accessed equipment data

### 2. Conditional Processing
- Skip broken equipment in degradation calculations
- Only process equipped items for character-specific updates
- Use early returns for unnecessary calculations

### 3. Database Optimization
- Index equipment_id and character_id columns
- Use prepared statements for repeated queries
- Consider read replicas for heavy query loads

## Troubleshooting

### Common Issues

**Equipment stats not updating after durability change:**
```python
# Ensure you're using the integration service
effective_stats = integration.get_equipment_effective_stats(equipment_id, base_stats)
```

**Repair costs seem incorrect:**
```python
# Check that quality and base_value are correct
repair_info = durability_service.calculate_repair_cost(
    equipment_id=equipment_id,
    current_durability=current_durability,
    target_durability=target_durability,
    quality=EquipmentQuality(quality_string),  # Ensure proper enum conversion
    base_item_value=base_value
)
```

**Durability degrading too fast/slow:**
```python
# Verify environmental factors and usage intensity
degradation_factors = {
    'usage_intensity': 1.0,  # Check this value
    'environment': 'normal',  # Verify environment string
    'combat_events': [],
    'environmental_exposure': {}
}
```

## Migration Guide

### From Old Scattered System

1. **Replace direct durability calculations:**
   ```python
   # Old way
   decay = calculate_equipment_decay(equipment, time_passed)
   
   # New way
   decay, details = durability_service.calculate_time_degradation(
       equipment_id, quality, last_update, usage_intensity
   )
   ```

2. **Update combat damage application:**
   ```python
   # Old way
   apply_combat_damage(equipment, damage_amount)
   
   # New way
   integration.process_combat_durability_damage(combat_participants, duration, intensity)
   ```

3. **Use centralized condition checking:**
   ```python
   # Old way
   if equipment.durability < 10:
       equipment.broken = True
   
   # New way
   is_usable, reason, condition = integration.validate_equipment_usability(equipment_id, "use")
   ```

### Database Schema Updates

Ensure equipment tables include:
- `current_durability` (DECIMAL(5,2))
- `last_durability_update` (TIMESTAMP)
- `quality` (VARCHAR(20))
- Proper indexes on equipment_id and character_id

## Future Enhancements

- **Material System:** Different materials with unique durability properties
- **Enchantment Preservation:** Risk/reward for repairing magical items
- **Regional Specializations:** Different repair capabilities by region
- **Skill Progression:** Character advancement in equipment maintenance
- **Automated Repair:** AI-driven repair scheduling and recommendations 