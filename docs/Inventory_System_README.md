# Visual DM Inventory System

## Overview

The Visual DM Inventory System provides a robust, scalable solution for managing in-game inventories with real-time synchronization between server and client. The system includes comprehensive weight validation, slot management, and modding support through JSON configuration files.

## Key Features

- **WebSocket-based real-time updates**: Changes to inventories are immediately reflected on all connected clients
- **Comprehensive validation**: Weight limits, slot constraints, stack sizes, and inventory type compatibility
- **Modding support**: Configurable item types and inventory types via JSON
- **Performance monitoring**: Built-in metrics for tracking system health and identifying bottlenecks
- **Error handling**: Detailed error reporting for improved debugging and user feedback
- **Unity integration**: Ready-to-use Unity client components

## Implementation Details

This implementation follows Visual DM's architecture standards:
- Backend uses FastAPI for RESTful endpoints
- WebSockets for real-time communication
- Unity C# client for frontend
- JSON-based configuration for modding

### File Structure

```
backend/
  ├── api/v2/routes/
  │   └── inventory_api_fastapi.py      # REST API endpoints
  ├── inventory/
  │   ├── models/
  │   │   └── inventory.py              # Data models
  │   ├── inventory_utils.py            # Utility functions
  │   └── inventory_validator.py        # Validation logic
  ├── websockets/
  │   └── inventory_websocket.py        # WebSocket implementation
  ├── systems/integration/
  │   └── monitoring.py                 # Performance metrics
  └── data/modding/
      └── item_types.json               # Item/inventory type definitions

VDM/Assets/Scripts/Inventory/
  ├── InventoryWebSocketClient.cs       # WebSocket client
  └── InventoryManager.cs               # Unity integration

docs/
  ├── Inventory_System_Architecture.md  # Detailed architecture
  └── Inventory_System_README.md        # This file
```

## Usage

### Connecting to Inventory (Unity)

```csharp
// Get the inventory manager
InventoryManager inventoryManager = InventoryManager.Instance;

// Connect to a character's inventory
inventoryManager.ConnectToInventory("character_id_1", "character");

// Open inventory UI when needed
inventoryManager.OpenInventory();

// Register for events
inventoryManager.OnItemAdded.AddListener(OnItemAddedHandler);

// Transfer items between inventories
StartCoroutine(inventoryManager.TransferItem(
    sourceInventoryId: 1,
    targetInventoryId: 2,
    itemId: 101,
    quantity: 5,
    callback: (success, message) => {
        Debug.Log($"Transfer result: {success} - {message}");
    }
));
```

### Backend API Endpoints

#### GET /api/v2/inventory/{inventory_id}

Fetches a specific inventory and its contents.

#### POST /api/v2/inventory/transfer

Transfers items between inventories with validation.

Request body:
```json
{
  "source_inventory_id": 1,
  "target_inventory_id": 2,
  "item_id": 101,
  "quantity": 5
}
```

#### GET /api/v2/inventory/{inventory_id}/validate

Performs a full validation check of an inventory.

### WebSocket Events

The WebSocket at `/ws/inventory/{owner_id}` provides these events:

- `inventory_state`: Complete inventory state
- `inventory_item_added`: When items are added
- `inventory_item_removed`: When items are removed
- `inventory_item_transferred`: When items move between inventories

## Modding

### Adding New Item Types

Add entries to the `item_types` array in `data/builders/item_types.json`:

```json
{
  "id": "artifact",
  "name": "Artifact",
  "description": "Magical artifact with special powers",
  "properties": {
    "equippable": true,
    "slot_type": "artifact",
    "can_be_stacked": false,
    "default_weight": 1.0,
    "inventory_icon": "artifact_icon.png"
  }
}
```

### Adding New Inventory Types

Add entries to the `inventory_types` array in the same file:

```json
{
  "id": "bank",
  "name": "Bank Storage",
  "description": "Secure banking storage",
  "properties": {
    "default_slot_limit": 100,
    "default_weight_limit": 500.0,
    "slot_based": true,
    "allowed_item_types": ["valuable", "material"]
  }
}
```

## Performance Monitoring

The system includes built-in performance monitoring:

- Connection metrics
- WebSocket message processing time
- Database query timings
- Automatic logging of slow operations

Check the log files in `logs/` for performance metrics and system.log for general logging.

## Future Improvements

See `docs/Inventory_System_Architecture.md` for planned improvements including:
- Optimistic updates
- Partial transfers
- Batched operations
- Enhanced filtering and pagination 