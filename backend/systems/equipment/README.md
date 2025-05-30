# Equipment System

## Overview

The Equipment System manages the equipping, unequipping, and effects of wearable/usable items in the game world. It builds upon the Inventory System but focuses specifically on equipment-related functionality.

## Key Components

- **Equipment Service**: Manages equipment operations like equipping and unequipping items
- **Equipment Stats**: Calculates bonuses and effects from equipped items
- **Equipment Compatibility**: Determines what items can be equipped by which characters
- **Equipment Slot Management**: Handles equipment slot availability and restrictions
- **Set Bonus Management**: Tracks equipment sets and applies bonuses when multiple pieces from the same set are equipped
- **Durability System**: Manages equipment wear, damage, repair, and performance degradation

## Relationship with Inventory System

The Equipment and Inventory systems have distinct but complementary responsibilities:

### Equipment System Responsibilities
- Handling equipment slot management
- Managing equipment stats and effects
- Handling equip/unequip operations
- Calculating derived stats from equipped items
- Defining equipment-specific properties and requirements
- Managing set bonuses and equipment synergies
- Tracking equipment durability and handling repairs

### Inventory System Responsibilities
- Storing and tracking all items (including equipment)
- Managing inventory constraints
- Providing item transfer operations
- Validating inventory operations
- Defining base item properties

The Equipment System relies on the Inventory System to:
1. Verify item existence and ownership
2. Manage the storage of equipment items
3. Provide base item properties
4. Handle general inventory operations

## Data Structure

The Equipment System uses models from both its own domain and the Inventory System:

### From Inventory System
```python
# Item model with equipment-specific properties
class Item(db.Model):
    # Base properties
    id: Mapped[int]
    name: Mapped[str]
    # ... other base properties ...
    
    # Equipment-specific properties in the 'properties' JSON field:
    # {
    #    "equipment_type": "weapon",
    #    "slot": "main_hand",
    #    "damage": 10,
    #    "requirements": {"strength": 12}
    # }
```

### Equipment-specific Models
```python
# Equipment slots with validation logic
class EquipmentSlot(db.Model):
    id: Mapped[int]
    character_id: Mapped[int]
    slot_type: Mapped[str]
    item_id: Mapped[int]

# Current equipment configuration
class Equipment(db.Model):
    id: Mapped[int]
    character_id: Mapped[int]
    slot: Mapped[str]
    item_id: Mapped[int]
    current_durability: Mapped[float]
    max_durability: Mapped[float]
    is_broken: Mapped[bool]

# Equipment sets for set bonuses
class EquipmentSet(db.Model):
    id: Mapped[int]
    name: Mapped[str]
    description: Mapped[str]
    set_bonuses: Mapped[Dict]  # Maps number of pieces to bonuses
    item_ids: Mapped[List[int]]  # List of item IDs that belong to this set

# Equipment durability history
class EquipmentDurabilityLog(db.Model):
    id: Mapped[int]
    equipment_id: Mapped[int]
    previous_durability: Mapped[float]
    new_durability: Mapped[float]
    change_amount: Mapped[float]
    change_reason: Mapped[str]
    event_details: Mapped[Dict]
    timestamp: Mapped[datetime]
```

## Usage

The Equipment System exposes an API for managing character equipment:

```python
# Equip an item from inventory to character
result = await equipment_service.equip_item(
    character_id=character_id,
    item_id=sword_id,
    slot="main_hand"
)

# Unequip an item
result = await equipment_service.unequip_item(
    character_id=character_id,
    slot="main_hand"
)

# Swap equipped items
result = await equipment_service.swap_equipment(
    character_id=character_id,
    slot="main_hand",
    new_item_id=better_sword_id
)

# Get equipment stats
stats = await equipment_service.get_equipment_stats(character_id=character_id)

# Get active set bonuses
bonuses = await equipment_service.get_character_set_bonuses(character_id=character_id)

# Create equipment set
result = await equipment_service.create_new_equipment_set(
    name="Dragon Slayer Set",
    description="Powerful set for dragon hunters",
    item_ids=[sword_id, armor_id, helmet_id, boots_id],
    set_bonuses={
        "2": {"stats": {"strength": 5}, "effects": [{"name": "Fire Resistance"}]},
        "4": {"stats": {"strength": 10, "vitality": 10}, "effects": [{"name": "Dragon Slayer"}]}
    }
)

# Apply combat damage to equipment
result = await equipment_service.apply_combat_damage(
    equipment_id=sword_id,
    equipment_type="weapon",
    combat_intensity=1.5,  # Harder combat
    is_critical=True       # Critical hit causes more damage
)

# Repair equipment
result = await equipment_service.repair_equipment_item(
    equipment_id=sword_id,
    full_repair=True       # Fully repair the item
)
```

## Integration Points

The Equipment System interfaces with several other systems:

- **Inventory System**: Sources items and manages storage
- **Character System**: Equipment affects character stats and abilities
- **Combat System**: Equipment determines combat capabilities
- **Crafting System**: Creates equipable items
- **Magic System**: Some equipment has magical properties and effects

## Implementation Notes

1. **Slot System**: Characters have a finite number of equipment slots, each accepting specific item types
2. **Requirements**: Equipment may have requirements (stats, skills, etc.) that must be met before equipping
3. **Effects**: Equipped items can provide passive effects and bonuses
4. **Sets**: Some equipment items form sets that provide additional bonuses when worn together
5. **Durability**: Equipment has durability that decreases with use and affects performance

## Equipment Set Bonuses

The Equipment Set system enables powerful combinations of gear that grant additional bonuses when multiple pieces from the same set are equipped:

1. **Scalable Bonuses**: Different bonuses can be defined for different numbers of set pieces (e.g., 2-piece, 4-piece bonuses)
2. **Stat Bonuses**: Direct stat increases (strength, vitality, etc.)
3. **Special Effects**: Unique abilities or resistances that activate with set bonuses
4. **Dynamic Calculation**: Set bonuses are recalculated whenever equipment changes
5. **API Integration**: Full REST API for creating, updating, and managing equipment sets

### Set Bonus Structure

```json
{
  "set_bonuses": {
    "2": {
      "stats": {"strength": 5, "agility": 3},
      "effects": [{"name": "Frost Resistance", "description": "Reduces frost damage by 20%"}]
    },
    "4": {
      "stats": {"strength": 10, "agility": 5, "critical_chance": 5},
      "effects": [
        {"name": "Frost Aura", "description": "Deals frost damage to nearby enemies"}
      ]
    }
  }
}
```

## Durability System

The Durability System models realistic wear and tear on equipment, affecting item performance over time:

1. **Durability Tracking**: Each equipment item has current and maximum durability values
2. **Combat Damage**: Equipment takes damage during combat based on intensity and critical hits
3. **Wear and Tear**: Equipment degrades slowly over time with regular use
4. **Environmental Factors**: Weather, terrain, and other conditions affect wear rates
5. **Stat Degradation**: As durability decreases, equipment provides reduced bonuses
6. **Repair System**: Items can be repaired at varying costs based on damage severity
7. **Breaking Point**: Equipment with zero durability is considered broken and provides no benefits
8. **Historical Tracking**: All durability changes are logged for analytics and narrative purposes

### Durability Status Levels

The system defines several durability status levels that affect item performance:

- **Perfect** (100%): No penalties, full stats
- **Excellent** (90-99%): No penalties, full stats
- **Good** (75-89%): No penalties, full stats
- **Worn** (50-74%): 10% stat reduction
- **Damaged** (25-49%): 25% stat reduction
- **Very Damaged** (10-24%): 50% stat reduction
- **Broken** (0-9%): Item cannot be equipped, provides no benefits

### Repair Cost Formula

Repair costs are calculated based on item value and damage severity:

```
repair_percentage = repair_amount / max_durability
base_cost = item_value * repair_percentage

# Apply cost multiplier based on how damaged the item is
if durability_percentage < 10%:  # Very damaged items cost more to repair
    cost_multiplier = 1.5
elif durability_percentage < 30%:
    cost_multiplier = 1.25
else:
    cost_multiplier = 1.0
    
total_cost = base_cost * cost_multiplier
```

## Data Flow

1. Item exists in inventory (managed by Inventory System)
2. Character attempts to equip item (Equipment System)
3. Equipment System validates compatibility, requirements, and durability
4. If valid, Equipment System updates equipment slots
5. Character stats are recalculated with new equipment bonuses and set bonuses, adjusted for durability
6. Equipment takes damage during use (combat, regular wear)
7. Durability status affects equipment performance
8. Repairs restore durability and performance
9. Events are emitted to notify other systems of equipment changes and durability updates
