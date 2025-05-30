# Armor Data

This directory contains the data files for Visual DM's armor system, which defines all armor types, properties, and protection values.

## Files

- `armor.json`: The canonical armor definitions in the game

## Legacy Files

The original armor file is preserved in `/backend/data/armor/` for historical and development reference.

## Related Data

Armor is also referenced in other data files:

- Equipment: `/backend/data/gameplay/equipment/`
- Combat: `/backend/data/gameplay/combat/`
- Classes: `/backend/data/gameplay/classes/` (for proficiencies)

## Usage

The armor system uses these files to define the armor available for characters, NPCs, and monsters. They are referenced by the character sheet, combat, and inventory systems.

For implementation details, see the relevant sections in the Development Bible. 