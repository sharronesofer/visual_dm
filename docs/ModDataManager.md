# ModDataManager for Visual DM

This document describes the ModDataManager system, which handles loading and validating JSON world seed data from mods for initial world generation in Visual DM.

## Overview

The ModDataManager provides a centralized system for loading, validating, and managing JSON data from mods. It handles mod priorities, conflict resolution, and provides an API for accessing mod data. The system consists of backend (Python/FastAPI) and frontend (Unity/C#) components that communicate via HTTP REST API and WebSocket.

## Architecture

The ModDataManager system consists of the following components:

### Backend Components

1. **`ModDataManager` Class (`backend/data/mod_data_manager.py`)**
   - Core class that handles loading and managing mod data
   - Provides methods for accessing and validating mod data
   - Singleton pattern for global access
   - Integrates with the existing `GameDataRegistry` system

2. **REST API Routes (`backend/data/api/mod_data_api.py`)**
   - FastAPI routes for interacting with ModDataManager
   - Endpoints for listing, getting, and manipulating mod data
   - Handles file uploads and conflict resolution

3. **WebSocket Handler (`backend/data/websocket/mod_data_socket.py`)**
   - Real-time communication between backend and frontend
   - Handles events like mod updates and conflict detection
   - Subscription system for targeted updates

### Frontend Components

1. **Unity ModDataManager (`VDM/Assets/Scripts/VisualDM/Data/ModDataManager.cs`)**
   - C# implementation that communicates with the backend
   - Singleton pattern for global access
   - Caches mod data locally for quick access
   - Provides events for mod updates

## Data Structure

### Mod Data

Mods are structured as follows:

```
mods/
  ├── mod_name/
  │   ├── mod_info.json     # Mod metadata
  │   ├── biomes/           # Biome definitions
  │   │   ├── biome1.json
  │   │   └── biome2.json
  │   ├── weapons/          # Weapon definitions
  │   │   ├── weapon1.json
  │   │   └── weapon2.json
  │   └── ... (other categories)
  └── another_mod/
      └── ...
```

Each mod contains a `mod_info.json` file with metadata and directories for different data categories.

### Schemas

Schemas are used for validation and are stored in:

```
schemas/
  ├── biomes.schema.json
  ├── weapons.schema.json
  └── ... (other schemas)
```

## Features

### Mod Loading

- Loads base game content as a special "base" mod
- Loads all mods from the `mods` directory
- Validates mod data against schemas
- Merges mod data based on priorities

### Conflict Detection and Resolution

- Detects conflicts between mods (e.g., two mods defining the same item)
- Provides methods for resolving conflicts automatically
- Allows manual conflict resolution via API

### Real-time Updates

- WebSocket communication for real-time updates
- Subscription system for targeted updates
- Broadcast system for global updates

## API Reference

### REST API Endpoints

- `GET /api/mods/`: Get all loaded mods
- `GET /api/mods/{mod_id}`: Get a specific mod
- `GET /api/mods/categories/list`: Get all categories
- `GET /api/mods/categories/{category}/items`: Get all items in a category
- `GET /api/mods/categories/{category}/items/{item_id}`: Get a specific item
- `POST /api/mods/categories/{category}/items`: Add or update an item
- `GET /api/mods/conflicts`: Get all mod conflicts
- `POST /api/mods/conflicts/resolve`: Resolve a conflict
- `POST /api/mods/validate`: Validate a mod
- `POST /api/mods/upload`: Upload a new mod package

### WebSocket Messages

#### Client to Server:
- `{ "type": "subscribe_mod", "mod_id": "..." }`: Subscribe to mod updates
- `{ "type": "subscribe_category", "category": "..." }`: Subscribe to category updates
- `{ "type": "get_mods" }`: Get all mods
- `{ "type": "get_categories" }`: Get all categories
- `{ "type": "get_items", "category": "..." }`: Get items in a category
- `{ "type": "get_item", "category": "...", "item_id": "..." }`: Get a specific item
- `{ "type": "add_item", "category": "...", "item_id": "...", "data": {...} }`: Add or update an item
- `{ "type": "get_conflicts" }`: Get all conflicts
- `{ "type": "resolve_conflict", "entity_id": "...", "strategy": "..." }`: Resolve a conflict

#### Server to Client:
- `{ "type": "subscription_success", ... }`: Subscription confirmation
- `{ "type": "mods_list", "mods": [...] }`: List of mods
- `{ "type": "categories_list", "categories": [...] }`: List of categories
- `{ "type": "items_list", "category": "...", "items": [...] }`: List of items
- `{ "type": "item_data", "category": "...", "item_id": "...", "item": {...} }`: Item data
- `{ "type": "category_update", "category": "...", "data": {...} }`: Category update
- `{ "type": "conflict_update", "conflicts": [...] }`: Conflict update
- `{ "type": "success", "message": "..." }`: Success message
- `{ "type": "error", "message": "..." }`: Error message

## Usage Examples

### Backend (Python)

```python
from backend.data.mod_data_manager import get_mod_data_manager

# Get the ModDataManager instance
manager = get_mod_data_manager()

# Get all mods
mods = manager.get_all_mods()

# Get all categories
categories = manager.get_categories()

# Get all items in a category
items = manager.get_all_items_in_category("biomes")

# Get a specific item
item = manager.get_item("biomes", "temperate_forest")

# Add an item to a category
success = manager.add_item_to_category("biomes", "new_biome", { ... })

# Detect conflicts
conflicts = manager.detect_conflicts()

# Resolve conflicts
remaining = manager.resolve_conflicts_by_priority(conflicts)
```

### Frontend (C#)

```csharp
// Get the ModDataManager instance
ModDataManager manager = ModDataManager.Instance;

// Initialize the manager
manager.Initialize();

// Subscribe to events
manager.OnModsLoaded += (mods) => {
    Debug.Log($"Loaded {mods.Count} mods");
};

manager.OnItemAdded += (category, item) => {
    Debug.Log($"Item added to {category}: {item["id"]}");
};

manager.OnConflictsDetected += (conflicts) => {
    Debug.Log($"Detected {conflicts.Count} conflicts");
};

// Get all mods
Dictionary<string, ModData> mods = manager.GetAllMods();

// Get all categories
IEnumerable<string> categories = manager.GetCategories();

// Get all items in a category
IEnumerable<JObject> items = manager.GetAllItemsInCategory("biomes");

// Get a specific item
JObject item = manager.GetItem("biomes", "temperate_forest");

// Add an item to a category
JObject newItem = new JObject();
newItem["id"] = "new_biome";
newItem["name"] = "New Biome";
// ...
await manager.AddItemToCategory("biomes", "new_biome", newItem);

// Resolve a conflict
await manager.ResolveConflict("biomes_temperate_forest");

// Subscribe to category updates
await manager.SubscribeToCategory("biomes");
```

## Integration with Existing Systems

The ModDataManager integrates with the following existing systems:

1. **GameDataRegistry**: Uses the existing registry system for loading base game content
2. **FastAPI Integration**: Hooks into the FastAPI application using the existing integration system
3. **WebSocket Handlers**: Uses the same pattern as existing WebSocket handlers for consistency

## Conclusion

The ModDataManager provides a flexible and extensible system for managing mod data in Visual DM. It handles loading, validation, conflict resolution, and provides a unified interface for accessing mod data. The system is designed to be easily integrated with existing systems and to provide a robust foundation for future mod support. 