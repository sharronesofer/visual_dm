# Visual DM - Unity Modding Framework

## Project Overview
Visual DM is a tool for managing and visualizing game worlds with a powerful Two-Tier Modding System for customizing world generation and game assets.

## Folder Structure

The project follows a well-organized architecture with the following key directories:

### Core Structure
- **Assets/VisualDM/** - Main project namespace
  - **Data/** - Data models and structures
    - **ModData/** - JSON data for world seed mods
    - **Schemas/** - JSON schemas for validating mod content
    - **WorldSeeds/** - Example and base world seed files
  - **Systems/** - Systems and managers
    - **Modding/** - Modding system core classes
    - **WorldGen/** - World generation from seed data
  - **UI/** - User interface components
    - **ModManager/** - UI for mod management
  - **Resources/** - Runtime resources and assets
  - **Prefabs/** - Reusable game objects
  - **Scenes/** - Unity scenes

## Two-Tier Modding System

Visual DM features a flexible modding architecture:

### Tier 1: World Seed Mods (Data-Only)
- Simple JSON-based mods that define world generation parameters
- Located in `Assets/VisualDM/Data/ModData`
- Validated against schemas in `Assets/VisualDM/Data/Schemas`
- Allows for non-programmers to create new world seeds without coding

### Tier 2: Asset/System Mods (Code & Assets)
- Full Unity asset bundles with custom code and assets
- Extends game functionality beyond data configuration
- Requires Unity development knowledge

## Mod Management

The system includes:

- **ModDataManager** (`VisualDM.Systems.ModDataManager`) - Manages loading and validating JSON world seed data
- **ModSynchronizer** (`VisualDM.Data.ModSynchronizer`) - Handles conflicts and synchronization between different mods
- **Mod UI** (`VisualDM.UI.ModManager`) - User interface for managing mods

## Getting Started

1. Open the project with Unity 2021.3 LTS or newer
2. Explore example world seeds in `Assets/VisualDM/Data/WorldSeeds`
3. Use the in-game mod manager to enable/disable mods
4. Create your own world seed by copying and modifying an existing one

## Creating a World Seed Mod

1. Create a new folder in `Assets/VisualDM/Data/ModData`
2. Add a `manifest.json` file with your mod metadata
3. Create JSON files for each data category (biomes, characters, items, etc.)
4. Validate your data against the schemas in `Assets/VisualDM/Data/Schemas`
5. Test your mod by enabling it in the mod manager

## License

See LICENSE.md for details. 