# Entity Data

This directory contains data files for all living entities in Visual DM, including NPCs, races, and abilities.

## Directory Structure

- `abilities/`: Character abilities, stats, and related mechanics
- `races/`: Race definitions, traits, and bonuses
- `npcs/`: NPC templates, behavior patterns, and generation rules
- `monsters/`: Monster definitions and stats (Note: Currently in separate `/monsters` directory)

## Usage

These data files define the properties and behaviors of all living entities in the game world. They are consumed by entity-related systems, character generation, and NPC behavior systems.

The NPC and monster generation systems use these data files to create dynamic, interesting characters and creatures for the game world.

## Integration with Other Systems

Entities interact with nearly all other game systems, including:

- Memory System: Entities store and retrieve memories
- Faction System: Entities belong to factions and have reputation values
- Rumor System: Entities spread and receive rumors
- Relationship System: Entities form relationships with each other

For detailed implementation information, see the relevant sections in the Development Bible. 