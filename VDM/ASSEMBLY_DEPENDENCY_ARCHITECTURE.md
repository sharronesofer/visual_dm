# Assembly Dependency Architecture

## Overview
This document defines the Unity assembly dependency hierarchy for VDM (Visual Dungeon Master) to prevent circular dependencies and maintain a clean, scalable architecture.

## Dependency Hierarchy (Bottom to Top)

### Level 1: Foundation (No Dependencies)
```
VDM.Common       - Shared utilities, extensions, constants
VDM.DTOs         - Data Transfer Objects for API communication
```

### Level 2: Core Infrastructure
```
VDM.Services     - HTTP client, WebSocket, networking services
                 Dependencies: VDM.Common, VDM.DTOs

VDM.Core         - Core game logic, managers, base classes
                 Dependencies: VDM.Common, VDM.DTOs
```

### Level 3: Game Systems
```
VDM.Systems      - Game systems (time, inventory, etc.)
                 Dependencies: VDM.Core, VDM.Services, VDM.DTOs, VDM.Common
```

### Level 4: Domain-Specific Modules
```
VDM.Character    - Character management, stats, progression
                 Dependencies: VDM.Core, VDM.Services, VDM.Systems, VDM.DTOs, VDM.Common

VDM.Combat       - Combat mechanics, damage, abilities
                 Dependencies: VDM.Core, VDM.Services, VDM.Systems, VDM.DTOs, VDM.Common

VDM.Modules      - Modding system, world generation
                 Dependencies: VDM.Core, VDM.Services, VDM.Systems, VDM.DTOs, VDM.Common
```

### Level 5: Presentation Layer (Independent)
```
VDM.UI           - User interface, menus, HUD
                 Dependencies: VDM.Core, VDM.Services, VDM.Systems, VDM.Character, VDM.Combat, VDM.Modules, VDM.DTOs, VDM.Common

VDM.Runtime      - Main runtime integration, scene management
                 Dependencies: VDM.Core, VDM.Services, VDM.Systems, VDM.Character, VDM.Combat, VDM.Modules, VDM.DTOs, VDM.Common
```

### Level 6: Testing (Top Level)
```
VDM.Tests        - Unit tests, integration tests
                 Dependencies: All assemblies + Unity Test Framework
```

## Assembly Dependency Rules

### ✅ ALLOWED Dependencies
1. **Upward Dependencies Only**: Assemblies can only reference assemblies at lower levels
2. **Same Level Independence**: Assemblies at the same level should not reference each other
3. **Foundation Dependencies**: All assemblies can depend on `VDM.Common` and `VDM.DTOs`
4. **Infrastructure Access**: Most assemblies can depend on `VDM.Core` and `VDM.Services`
5. **Testing Access**: `VDM.Tests` can reference all assemblies

### ❌ FORBIDDEN Dependencies
1. **Circular References**: No assembly should create circular dependency chains
2. **Downward Dependencies**: Higher-level assemblies should not be referenced by lower-level ones
3. **Same Level Cross-References**: Assemblies at the same level should not reference each other
4. **Core-Runtime Cycle**: `VDM.Core` must NEVER reference `VDM.Runtime`
5. **Service-Core Cycle**: `VDM.Services` must NEVER reference `VDM.Core`
6. **UI-Runtime Cross-Reference**: `VDM.UI` and `VDM.Runtime` should not reference each other

## Common Circular Dependency Patterns to Avoid

### Anti-Pattern 1: Core ↔ Runtime Cycle
```
❌ VDM.Core → VDM.Runtime → VDM.Core
```

### Anti-Pattern 2: Service ↔ Core Cycle
```
❌ VDM.Services → VDM.Core → VDM.Services
```

### Anti-Pattern 3: Cross-Domain Dependencies
```
❌ VDM.Character → VDM.Combat → VDM.Character
```

### Anti-Pattern 4: Same Level Cross-References
```
❌ VDM.UI → VDM.Runtime (both at Level 5)
```

## Best Practices

### 1. Interface Segregation
- Define interfaces in lower-level assemblies (VDM.Core)
- Implement interfaces in higher-level assemblies
- Use dependency injection to wire implementations

### 2. Event-Driven Communication
- Use events for upward communication (lower → higher level)
- Use direct calls for downward communication (higher → lower level)
- Use events for same-level communication (UI ↔ Runtime)

### 3. Shared Data Access
- Place shared data models in `VDM.DTOs`
- Place shared utilities in `VDM.Common`
- Keep core business logic in `VDM.Core`

### 4. Service Layer Pattern
- Network services in `VDM.Services`
- Business services in `VDM.Core`
- Game system services in `VDM.Systems`

### 5. Presentation Layer Independence
- `VDM.UI` and `VDM.Runtime` are independent at Level 5
- Both can access all lower-level assemblies
- Communication between them should use events or shared services

## Validation Checklist

Before modifying assembly references, verify:

- [ ] No circular dependencies exist
- [ ] Dependencies flow upward in hierarchy
- [ ] Core assemblies don't reference Runtime
- [ ] Services don't reference Core
- [ ] Domain modules don't cross-reference each other
- [ ] UI and Runtime don't reference each other
- [ ] Tests can reference everything needed

## Recovery Process

If circular dependencies are detected:

1. **Identify the Cycle**: Map out the dependency chain
2. **Find the Break Point**: Identify which reference creates the cycle
3. **Refactor Architecture**: Move shared code to lower-level assembly
4. **Use Interfaces**: Replace direct references with interface-based communication
5. **Implement Events**: Use event-driven patterns for upward communication
6. **Validate**: Ensure Unity compiles without assembly errors

## Architecture Diagram

```
    VDM.Tests (Level 6)
         |
    ┌────┴────┐
    │         │
VDM.UI   VDM.Runtime (Level 5 - Independent)
    │         │
    └────┬────┘
         │
   ┌─────┼─────┐
   │     │     │
VDM.Character VDM.Combat VDM.Modules (Level 4)
   │     │     │
   └─────┼─────┘
         │
    VDM.Systems (Level 3)
         │
    ┌────┼────┐
    │         │
VDM.Core  VDM.Services (Level 2)
    │         │
    └────┬────┘
         │
   ┌─────┼─────┐
   │           │
VDM.Common  VDM.DTOs (Level 1)
```

This architecture ensures a stable, maintainable codebase without circular dependencies. 