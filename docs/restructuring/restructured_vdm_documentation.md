# Visual DM Module Restructuring Documentation

## Overview

This document explains the new module-based folder structure for Visual DM. The restructuring follows the system architecture outlined in the Development Bible, organizing code into logically separated modules that correspond to the systems described in the documentation.

## Module Structure

The new structure organizes code into these main modules, each responsible for a specific aspect of the game:

### Core Game Systems
- **Events**: Central event bus system and event handlers
- **Analytics**: Game event tracking and analytics 
- **Memory**: Entity memory management and relevance scoring
- **Rumor**: Information diffusion and mutation systems
- **WorldState**: Global state management and tracking
- **Time**: Calendar, time progression, and scheduled events
- **Population**: NPC generation and population management
- **Motif**: Narrative motif handling and rotation

### World Elements
- **Region**: Region management and properties
- **POI**: Points of interest management
- **Faction**: Faction mechanics and attributes
- **War**: Tension and conflict systems
- **NPC**: NPC behavior and attributes

### Game Features
- **Quest**: Quest and narrative arc management
- **Combat**: Combat mechanics and resolution
- **Relationship**: Character relationship tracking
- **Religion**: Religious systems (placeholder)
- **Diplomacy**: Diplomatic mechanics (placeholder)
- **Economy**: Economic and trade systems
- **Dialogue**: Conversation and dialogue systems

### Technical Systems
- **Storage**: Save/load and persistence
- **Networking**: Remote API communication
- **WorldGen**: Procedural world generation
- **Core**: Shared utilities and helpers

## Module Dependencies

Modules follow a layered architecture with the following general dependencies:

1. **Foundation Layer**: Core, Events
2. **Systems Layer**: Memory, WorldState, Time, Analytics
3. **World Layer**: Region, POI, Faction, NPC
4. **Feature Layer**: Quest, Combat, War, Economy, etc.

Modules should only depend on modules in their own layer or layers below.

## Naming Conventions

- Class names should reflect their module when appropriate (e.g., `MemoryManager`, `FactionRelationship`)
- Namespaces should follow the pattern: `VisualDM.ModuleName`
- Files should use PascalCase and be descriptive of their purpose

## File Organization

Each module is organized with this internal structure:

1. **Interfaces**: Interface declarations (`IMemoryService.cs`)
2. **Models**: Data structures and DTOs (`MemoryData.cs`)
3. **Core**: Main implementation files (`MemoryManager.cs`)
4. **Utils**: Module-specific helper functions

## Future Work

After this restructuring, the next steps will be:

1. Resolve duplicate files and dependencies
2. Update namespaces across the codebase
3. Refactor code to properly respect module boundaries
4. Update build configurations to reflect the new structure

## Scripts

Three scripts were created to facilitate this restructuring:

- `restructure_vdm_folders.sh`: Creates the new directory structure
- `move_vdm_files.sh`: Moves files to their appropriate modules
- `check_duplicates.sh`: Identifies duplicate files and potential issues

## Maintenance Guidelines

When adding new functionality:

1. Identify the appropriate module for the new code
2. Follow the namespace conventions of that module
3. Be mindful of dependencies between modules
4. Update documentation when creating new types of files

When making changes to existing code:

1. Respect module boundaries
2. Maintain namespace consistency
3. Keep dependency direction from higher to lower layers 