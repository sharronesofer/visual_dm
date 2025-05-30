# Weapons Data

This directory contains the data files for Visual DM's weapon system, which defines all weapon types, properties, and combat statistics.

## Files

- `weapons_master.json`: The consolidated master list of all weapons in the game
- `melee_weapons.json`: Melee weapon definitions
- `ranged_weapons.json`: Ranged weapon definitions

## Legacy Files

The original weapon files are preserved in `/backend/data/weapons/` for historical and development reference.

## Related Data

Weapons are also referenced in other data files:

- Equipment: `/backend/data/gameplay/equipment/`
- Combat: `/backend/data/gameplay/combat/`
- Classes: `/backend/data/gameplay/classes/` (for proficiencies)

## Usage

The weapon system uses these files to define the weapons available for characters, NPCs, and monsters. They are referenced by the character sheet, combat, and inventory systems.

For implementation details, see the relevant sections in the Development Bible. 