# Visual DM Assets

This directory contains all assets for the Visual DM project. The project follows Unity best practices for directory structure and organization.

## Directory Structure

### Scripts
- **Core/**: Core framework code (non-game-specific)
- **Runtime/**: Game-specific implementation
  - **Systems/**: Major game systems (Memory, Rumor, Motif, etc.)
  - **Entities/**: Character, NPC classes
  - **World/**: World generation, regions, POIs
  - **UI/**: User interface components
- **Tests/**: Unit and integration tests
  - **EditMode/**: Editor-only tests
  - **PlayMode/**: Runtime tests
- **Editor/**: Editor extensions and tools

### Resources
- **Data/**: JSON files, scriptable objects
- **Prefabs/**: Prefabs that need to be loaded at runtime
- **Materials/**: Materials that need to be loaded at runtime
- **UI/**: UI elements that need to be loaded at runtime

### ScriptableObjects
- **Biomes/**: Biome definitions
- **Items/**: Item definitions
- **Motifs/**: Motif definitions
- **Systems/**: System configuration

### Prefabs
- **UI/**: UI prefabs
  - **Screens/**: Full UI screens
  - **Elements/**: Reusable UI components
  - **Popups/**: Dialog boxes, notifications
- **World/**: World prefabs
  - **POIs/**: Points of interest
  - **Terrain/**: Terrain prefabs
  - **Effects/**: Visual effects
- **Characters/**: Character prefabs
  - **NPCs/**: NPC prefabs
  - **Player/**: Player prefabs
  - **Animals/**: Animal prefabs
- **Systems/**: System-related prefabs

### Scenes
- **Main/**: Main gameplay scenes
- **UI/**: UI-only scenes (title, options, etc.)
- **Bootstrap/**: Loading and initialization scenes
- **Tests/**: Test scenes

## Naming Conventions

- **Scripts**: PascalCase (e.g., `MemoryManager.cs`)
- **Folders**: PascalCase (e.g., `Scripts/Systems/Memory/`)
- **Prefabs**: Category_PrefabName (e.g., `NPC_Merchant.prefab`)
- **Scenes**: Category_SceneName (e.g., `Main_Town.unity`)

## Assembly Definition Overview

- **VDM.Core**: Core framework code
- **VDM.Runtime**: Game-specific implementation
- **VDM.Runtime.Systems**: Game systems
- **VDM.Editor**: Editor tools
- **VDM.Tests.EditMode**: Edit mode tests
- **VDM.Tests.PlayMode**: Play mode tests 