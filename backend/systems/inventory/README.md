# Inventory System

## Overview

The Inventory System manages item storage, tracking, and basic operations for all entities in the game world. It serves as the foundation for item management but delegates equipment-specific logic to the Equipment System.

## Directory Structure

The inventory system uses a simple, flattened structure for maintainability:

- `models.py`: Core database models for Item, Inventory, and InventoryItem
- `schemas.py`: Pydantic schemas for API validation and serialization
- `repository.py`: Data access layer for CRUD operations
- `service.py`: Business logic and service operations
- `validator.py`: Validation logic for inventory operations
- `utils.py`: Utility functions and helper classes
- `router.py`: FastAPI routes for inventory API

For backward compatibility, there is a `models/` subdirectory with an `__init__.py` that re-exports models from the parent module.

## Key Components

- **Inventory Models**: Core data structures for inventories and items
- **Inventory Validator**: Enforces constraints like weight limits and slot constraints
- **Inventory Service**: Business logic for item management operations
- **Inventory Repository**: Storage and retrieval for inventory data

## Relationship with Equipment System

The Inventory and Equipment systems have distinct but related responsibilities:

### Inventory System Responsibilities
- Storing and tracking all items (equipment, consumables, quest items, etc.)
- Managing inventory constraints (weight limits, slot limits)
- Providing item transfer operations (add, remove, move)
- Validating inventory operations
- Defining base item properties shared by all item types

### Equipment System Responsibilities
- Handling equipment slot management
- Managing equipment stats and effects
- Handling equip/unequip operations
- Calculating derived stats from equipped items
- Defining equipment-specific properties 

## Data Model

The key models in the Inventory System include:

1. **Item**: Represents any item in the game world
   ```python
   class Item(db.Model):
       id: Mapped[int]
       name: Mapped[str]
       description: Mapped[str]
       item_type: Mapped[str]
       rarity: Mapped[str]
       value: Mapped[int]
       weight: Mapped[float]
       properties: Mapped[dict]
   ```

2. **Inventory**: Contains items owned by an entity
   ```python
   class Inventory(db.Model):
       id: Mapped[int]
       owner_id: Mapped[int]
       owner_type: Mapped[str]
       capacity: Mapped[int]
       weight_limit: Mapped[float]
       items: Mapped[dict]
   ```

3. **InventoryItem**: Represents a specific item instance in an inventory
   ```python
   class InventoryItem(db.Model):
       id: Mapped[int]
       inventory_id: Mapped[int]
       item_id: Mapped[int]
       quantity: Mapped[int]
       position: Mapped[dict]
       is_equipped: Mapped[bool]
   ```

## Usage

The Inventory System exposes an API for managing inventories:

```python
# Create an inventory
inventory_id = await inventory_service.create_inventory(
    owner_id=character_id,
    owner_type="character",
    capacity=50,
    weight_limit=100.0
)

# Add an item to inventory
success = await inventory_service.add_item(
    inventory_id=inventory_id,
    item_id=sword_id,
    quantity=1
)

# Transfer an item between inventories
success = await inventory_service.transfer_item(
    source_inventory_id=character_inventory_id,
    target_inventory_id=chest_inventory_id,
    item_id=potion_id,
    quantity=5
)
```

## Integration Points

The Inventory System interfaces with several other systems:

- **Character System**: Characters own inventories
- **Equipment System**: Uses inventory data for equipment operations
- **Crafting System**: Creates items in inventories
- **Loot System**: Generates items to add to inventories
- **Economy System**: Handles item value and trading

## Implementation Details

- The `InventoryValidator` class provides robust validation logic for all inventory operations
- JSON-based item properties allow for flexible item attributes
- Inventory operations emit events that other systems can subscribe to
- The system supports different inventory types (character, container, shop)
