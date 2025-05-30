# Unity Frontend Directory Structure

This directory structure mirrors the backend/systems/ architecture exactly, with Unity-specific additions.

## Structure Overview

### Core Systems (Mirror Backend)
These directories mirror backend/systems/ exactly:

**Foundation Layer:**
- Analytics/ - Performance and usage tracking UI
- Data/ - Data management and import/export tools  
- Events/ - Event notification and handling
- Storage/ - Persistent storage management
- AuthUser/ - Authentication and user management

**Game Systems:**
- Character/ - Character creation and management
- Combat/ - Combat interface and animations
- Magic/ - Spell casting and magic systems
- Equipment/ - Gear management and customization
- Inventory/ - Item storage and organization

**World Systems:**
- WorldGeneration/ - World creation tools
- WorldState/ - Global state management
- Region/ - Regional map and exploration
- Time/ - Time progression and calendar
- Poi/ - Point of interest exploration

**Social Systems:**
- Faction/ - Faction management and politics
- Npc/ - NPC interaction and management
- Dialogue/ - Conversation UI and voice systems
- Memory/ - Character memory and history
- Religion/ - Religious system management

**Narrative Systems:**
- Quest/ - Quest tracking and management
- Arc/ - Narrative arc progression UI
- Motif/ - Narrative theme management
- Rumor/ - Information and rumor spreading

**Economic Systems:**
- Economy/ - Trade, markets, and economic interfaces
- Crafting/ - Crafting interface and recipes
- Loot/ - Loot generation and rewards display

**Advanced Systems:**
- Llm/ - AI integration interfaces
- Diplomacy/ - Faction relationship management
- Population/ - Settlement and population display

### Unity-Specific Systems
These provide Unity-specific functionality:

- **Bootstrap/** - Game initialization and startup
- **Core/** - Unity-specific core systems and utilities
- **UI/** - User interface framework and components
- **Integration/** - System integration and communication layers
- **Services/** - Unity service layer for backend communication

## Standard System Structure

Each core system follows this pattern:

```
SystemName/
├── Models/      # DTOs and data models for API communication
├── Services/    # HTTP/WebSocket communication services
├── UI/          # User interface components
└── Integration/ # Unity-specific integration logic
```

## Architecture Principles

1. **Backend Alignment**: Core systems mirror backend structure exactly
2. **Separation of Concerns**: Clear boundaries between data, services, UI, and integration
3. **Unity Integration**: Unity-specific code isolated in Integration/ subdirectories
4. **API Communication**: Services handle all backend communication
5. **UI Components**: Reusable UI components for each system domain

## Migration Strategy

This structure supports gradual migration:
1. Create new structure (this step)
2. Define standard patterns and templates
3. Migrate foundational systems first (Data, Events, Time)
4. Migrate core gameplay systems
5. Update all namespace references
6. Comprehensive testing and validation

## Development Guidelines

- Follow the established patterns for each system type
- Maintain clear separation between Unity and business logic
- Use dependency injection for system communication
- Implement comprehensive testing for all components
- Document all public APIs and integration points
