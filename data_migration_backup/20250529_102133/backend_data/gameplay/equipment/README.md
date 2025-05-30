# Equipment Data

This directory contains the master data file for Visual DM's equipment system, which defines all equippable items, their properties, and effects.

## Files

- `equipment_master.json`: The canonical, expanded schema for all equipment in the game

## Related Data

Equipment is also referenced in other directories:

- Weapons: `/backend/data/weapons/`
- Armor: `/backend/data/armor/`
- Items: `/backend/data/items/`

## Legacy Files

The original equipment files are preserved in `/backend/data/equipment/` for historical and development reference:

- `equipment.json`: Basic equipment definitions
- `equipment_expanded.json`: Expanded equipment data
- `effects.json`: Equipment effect definitions
- `items.json`: General item definitions

## Usage

The master equipment file is consumed by the inventory, crafting, and loot generation systems. It defines the items that characters can equip, use, and craft.

For implementation details, see the Development Bible section on the Equipment and Inventory Systems. 