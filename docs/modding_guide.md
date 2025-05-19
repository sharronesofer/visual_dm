# Visual DM Modding Guide

Visual DM is designed with modding in mind, allowing players and developers to extend the game with custom content. This guide explains how to create and distribute mods for Visual DM.

## Overview

The modding system in Visual DM is based on JSON files that follow defined schemas. These files define various game elements such as:

- Weapons
- Armor
- Races
- Biomes
- Land types
- Items
- Spells
- NPCs
- Buildings
- Quests
- Resources
- Effects

## Modding Directory Structure

Mods are organized into categories, with each category having its own directory containing:

1. A schema file that defines the structure of the data
2. Individual JSON files for each item in that category

The standard directory structure is:

```
backend/data/modding/
├── README.md
├── biomes/
│   ├── biome.schema.json
│   ├── temperate_forest.json
│   └── ...
├── weapons/
│   ├── weapon.schema.json
│   ├── longsword.json
│   └── ...
├── races/
│   ├── race.schema.json
│   ├── dwarf.json
│   └── ...
├── land_types/
│   ├── land_type.schema.json
│   ├── forest.json
│   └── ...
└── ...
```

## Creating a Mod

To create a mod for Visual DM:

1. **Understand the Schema**: Each mod category has a schema file (e.g., `weapon.schema.json`) that defines the structure and requirements for data in that category.

2. **Create a JSON File**: Create a new JSON file in the appropriate category directory that conforms to the schema.

3. **Test Your Mod**: Launch the game to test your mod. Any valid JSON files in the mod directories will be loaded automatically.

### Example: Creating a Custom Weapon

Here's an example of creating a custom weapon:

1. Look at the weapon schema in `backend/data/modding/weapons/weapon.schema.json` to understand the required structure.

2. Create a new file `backend/data/modding/weapons/my_custom_sword.json`:

```json
{
    "id": "my_custom_sword",
    "name": "Blade of the Ancients",
    "description": "A mysterious blade forged by an ancient civilization, glowing with ethereal energy.",
    "type": "sword",
    "damage": {
        "min": 2,
        "max": 8,
        "type": "slashing"
    },
    "attack_bonus": 2,
    "critical": {
        "threshold": 19,
        "multiplier": 2
    },
    "range": {
        "short": 5,
        "long": 0
    },
    "hands": 1,
    "properties": [
        "magical",
        "ancient"
    ],
    "weight": 3,
    "cost": {
        "value": 500,
        "currency": "gold"
    },
    "rarity": "rare",
    "requirements": {
        "strength": 10,
        "proficiency": "martial"
    },
    "effects": [
        {
            "id": "ancient_glow",
            "name": "Ancient Glow",
            "description": "The blade emits a soft blue light, illuminating a 20-foot radius.",
            "type": "passive"
        },
        {
            "id": "ethereal_damage",
            "name": "Ethereal Damage",
            "description": "Deals an extra 1d4 force damage against undead creatures.",
            "type": "conditional"
        }
    ]
}
```

3. Launch the game and your custom sword will be available.

## Distribution of Mods

To distribute your mods to other players:

1. **Package Your Mod**: Create a ZIP file containing your JSON files organized in the correct directory structure.

2. **Include Documentation**: Create a README file explaining what your mod does and any special instructions.

3. **Share Your Mod**: Upload your mod package to mod sharing sites or the game's community forums.

## Installation of Mods

To install mods created by others:

1. **Extract the Mod Package**: Unzip the mod package.

2. **Place Files in the Correct Directory**: Copy the JSON files to their respective directories in `backend/data/modding/`.

3. **Launch the Game**: The mod will be loaded automatically when you start the game.

## Synchronization Between Client and Server

Visual DM automatically synchronizes mod data between the backend server and the Unity client. This means:

1. Mods installed on the server will be automatically downloaded to clients.
2. The client will maintain a local cache of mod data for offline play.
3. When connecting to a server, the client will update its mod data to match the server.

This synchronization happens automatically and ensures all players have the same mod experience when playing together.

## Mod Development Best Practices

When developing mods for Visual DM, consider the following:

1. **Follow the Schema**: Always validate your JSON files against the schema to ensure compatibility.

2. **Use Unique IDs**: Ensure all your mod items have unique IDs to avoid conflicts with other mods.

3. **Balance Your Content**: Try to create balanced content that doesn't disrupt game mechanics.

4. **Test Thoroughly**: Test your mods in various scenarios to ensure they work as expected.

5. **Provide Documentation**: Include clear documentation explaining what your mod does and how to use it.

6. **Be Compatible**: Consider compatibility with other mods and avoid making changes that would break existing content.

## Schema Reference

Each mod category has a schema file that defines the structure of the data. The schema files are located in each category directory and are named `<category>.schema.json`.

For detailed information about each schema, refer to the schema files themselves, which contain descriptions for each field.

## Advanced Modding

For advanced modding scenarios, such as creating new game mechanics or modifying core game behavior, you may need to:

1. **Understand the Game's Codebase**: Familiarize yourself with the game's source code to understand how different systems work.

2. **Create Custom Code Mods**: Develop custom code mods that extend or modify the game's functionality.

3. **Use the Modding API**: Visual DM provides an API for more advanced mods to interact with the game engine.

Advanced modding is beyond the scope of this guide, but the game's developer documentation provides more details for those interested.

## Troubleshooting

If you encounter issues with your mods:

1. **Check JSON Validity**: Ensure your JSON files are valid and follow the schema.

2. **Check Log Files**: Check the game's log files for error messages that might indicate what's wrong.

3. **Validate IDs**: Ensure all your mod items have unique IDs that don't conflict with existing content.

4. **Check Dependencies**: If your mod depends on other mods, ensure they are installed and loaded correctly.

5. **Ask for Help**: Reach out to the modding community or the game's forums for assistance.

## Conclusion

Modding Visual DM allows you to customize your gaming experience and share your creations with others. By following this guide and the established schemas, you can create mods that enhance the game while maintaining compatibility with other mods and future game updates.

Happy modding! 