# ModSynchronizer Documentation

## Overview

The ModSynchronizer is a system for managing conflicts and dependencies between mods in Visual DM. It detects and resolves conflicts between mods that modify the same entities, handles dependencies between mods, and ensures that mods are loaded in the correct order.

## Architecture

The ModSynchronizer system consists of three main components:

1. **Unity ModSynchronizer (`VisualDM.Data.ModSynchronizer`)**: 
   - Manages the client-side synchronization process
   - Detects conflicts between loaded mods
   - Resolves conflicts automatically or with user input
   - Determines the optimal load order for mods

2. **Backend API (`backend.modsynchronizer`)**: 
   - FastAPI endpoints for mod synchronization
   - Provides conflict detection and resolution on the server side
   - Generates optimized load orders based on dependencies
   - Manages mod metadata and compatibility

3. **WebSocket Client (`VisualDM.Networking.ModSynchronizerClient`)**: 
   - Handles real-time communication between the Unity client and backend
   - Transmits synchronization commands and status updates
   - Receives conflict notifications and resolution results

## Workflow

The mod synchronization process follows these steps:

1. **Initialization**: The GameManager initializes the ModSynchronizer when starting to load world mods.

2. **Mod Detection**: The ModSynchronizer detects all installed mods and reads their metadata.

3. **Conflict Detection**: The system identifies several types of conflicts:
   - **Entity Overrides**: When multiple mods modify the same entity (e.g., a biome or creature)
   - **Missing Dependencies**: When a mod depends on another mod that is not installed
   - **Incompatible Mods**: When incompatible mods are installed together
   - **Circular Dependencies**: When mods form a circular dependency chain

4. **Automatic Resolution**: The system attempts to resolve conflicts automatically:
   - **Entity Overrides**: Uses the mod with the highest priority (lowest priority number)
   - **Data Merging**: For compatible entities, merges data from multiple mods
   - **Load Order Optimization**: Creates an optimal load order based on dependencies

5. **Manual Resolution**: For conflicts that cannot be resolved automatically, the system provides interfaces for manual resolution:
   - **UI Prompts**: Allowing users to choose which mod to use for conflicts
   - **Resolution Strategies**: Multiple strategies for conflict resolution
   - **Conflict Reports**: Detailed reports of all conflicts and their status

6. **Mod Loading**: Once conflicts are resolved, mods are loaded in the optimized order.

## Conflict Types

The ModSynchronizer handles several types of conflicts:

### Entity Override Conflicts

These occur when multiple mods define or modify the same entity (e.g., a biome, creature, or item). The system detects these by comparing entity IDs across all mods.

**Resolution Strategies:**
- Use highest priority mod (default)
- Merge data from multiple mods (when compatible)
- Selectively choose which mod to use
- Disable conflicting mods

### Dependency Conflicts

These include:

- **Missing Dependencies**: When a mod requires another mod that is not installed
- **Circular Dependencies**: When mods form a dependency loop (A → B → C → A)
- **Incompatible Mods**: When mods explicitly declare incompatibility with each other

## Configuration

### Mod Information Files

Each mod must include a `mod_info.json` file in its root directory with metadata:

```json
{
  "id": "example_mod",
  "name": "Example Mod",
  "version": "1.0.0",
  "description": "Description of the mod",
  "author": "Mod Author",
  "load_priority": 50,
  "dependencies": [
    {
      "id": "required_mod",
      "version": ">=1.0.0",
      "required": true
    }
  ],
  "incompatibilities": [
    {
      "id": "incompatible_mod",
      "version_range": ">=2.0.0"
    }
  ]
}
```

### Load Priority

Mods with lower `load_priority` values are loaded first and have higher precedence for conflict resolution. The default priority is 100.

## API Reference

### Unity ModSynchronizer

```csharp
// Initialize the synchronizer
ModSynchronizer.Instance.Initialize();

// Subscribe to synchronization events
ModSynchronizer.Instance.SyncCompleted += OnSyncCompleted;

// Get unresolved conflicts
List<ModConflict> conflicts = ModSynchronizer.Instance.GetUnresolvedConflicts();

// Resolve a conflict
bool success = ModSynchronizer.Instance.ResolveConflict(
    conflict, 
    ConflictResolutionStrategy.UseHighestPriority
);

// Get optimized load order
List<string> loadOrder = ModSynchronizer.Instance.GetOptimizedLoadOrder();
```

### FastAPI Backend

The backend exposes several endpoints:

- `GET /api/mods/sync/status`: Get current synchronization status
- `POST /api/mods/sync/start`: Start the synchronization process
- `POST /api/mods/sync/resolve`: Resolve a specific conflict
- `GET /api/mods/optimized-load-order`: Get the optimized load order
- `GET /api/mods/conflict-report`: Generate a detailed conflict report
- `WebSocket /api/mods/sync/ws`: Real-time synchronization updates

## WebSocket Protocol

The WebSocket connection between client and server uses JSON messages:

### Client to Server Messages

```json
{
  "type": "start_sync"
}
```

```json
{
  "type": "resolve_conflict",
  "conflict_id": "biomes_desert",
  "resolution_strategy": "use_highest_priority",
  "mod_to_use": "desert_expansion"
}
```

### Server to Client Messages

```json
{
  "type": "sync_status",
  "status": {
    "in_progress": true,
    "success": null,
    "last_sync": "2023-09-15T14:30:00Z",
    "conflicts": []
  }
}
```

```json
{
  "type": "sync_completed",
  "success": true,
  "unresolved_conflicts": 0
}
```

## Best Practices

1. **Mod Naming**: Use unique IDs for mods to avoid naming conflicts
2. **Dependencies**: Explicitly declare all mod dependencies
3. **Load Priority**: Set appropriate load priorities for mods that extend others
4. **Entity IDs**: Use namespaced entity IDs to avoid conflicts (e.g., `mod_name:entity_name`)
5. **Compatibility**: Test mods with common dependency mods

## Implementation Notes

- The ModSynchronizer uses a topological sort algorithm to determine the optimal load order based on dependencies.
- Entity conflicts are resolved by default using the highest priority mod (lowest priority number).
- Data merging is supported for compatible entity types, allowing properties from multiple mods to be combined.
- Circular dependencies are detected using a depth-first search algorithm and reported as conflicts.
- The system supports both automatic and manual conflict resolution strategies.

## Future Enhancements

- Version compatibility checking for dependencies
- Differential updates for mod changes
- Enhanced UI for conflict resolution
- Mod groups and load order presets
- Integration with mod repositories for dependency resolution 