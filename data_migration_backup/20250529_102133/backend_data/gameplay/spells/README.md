# Spells Data

This directory contains the master data file for Visual DM's spell system, which defines magical abilities, rituals, and powers.

## Files

- `spells_master.json`: The canonical master list of all spells in the game

## Level-Based Organization

Spells are also organized by level in `/backend/data/spells/` with individual files per spell level:

- `level_0_spells.json`: Cantrips and level 0 spells
- `level_1_spells.json`: Level 1 spells
- `level_2_spells.json`: Level 2 spells
- ... (and so on through level 9)

## Other Spell Files

Additional spell-related files in `/backend/data/spells/`:

- `spells.json`: The original comprehensive spell list
- `more_spells.json`: Additional spells added during development

## Usage

The spell system uses these files to provide magical abilities for characters, NPCs, and monsters. Spells are referenced by the character sheet, combat, and magic systems.

For implementation details, see the Development Bible section on the Magic System. 