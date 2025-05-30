# Inventory System Architecture and Optimization

This document outlines the architecture of the Visual DM inventory system, focusing on data validation, real-time synchronization, and optimization.

## System Overview

The inventory system is built on a three-tier architecture:

1. **Backend (FastAPI)**: Manages inventory data persistence, validation, and business rules
2. **WebSocket Layer**: Handles real-time communication between backend and frontend
3. **Unity Client**: Provides UI and user interaction with inventory items

## Key Components

### Backend Components

#### Inventory Models
- `Inventory`: Represents a container for items with constraints (weight limit, slot limit)
- `InventoryItem`: Associates items with inventories, including quantity
- `Item`: Defines the base characteristics of items (weight, value, stackability)

#### Inventory API (FastAPI)
- RESTful endpoints for inventory CRUD operations
- Transfer validation and processing
- Comprehensive error handling with detailed feedback

#### Inventory Validator
- Validates inventory operations against business rules
- Performs weight and slot limit validation
- Enforces inventory type compatibility rules for transfers
- Provides detailed error information for improved UX

#### Inventory WebSocket
- Real-time inventory state synchronization
- Event-based communication for inventory changes
- Connection management and reconnection logic
- Event history for catching up after reconnection

### Unity Client Components

#### Inventory WebSocket Client
- Manages WebSocket connections to backend
- Handles connection lifecycle (connect, disconnect, reconnect)
- Processes incoming inventory events

#### Inventory Manager
- Central point for inventory operations in Unity
- UI updates and event dispatching
- Caches inventory state for offline functionality
- Weight and slot visualization

## Optimizations

### Performance Optimizations

1. **Reduced Network Traffic**
   - WebSocket-based real-time updates instead of polling
   - Delta updates when possible (only sending changed data)
   - Compression for larger payloads

2. **Validation Optimizations**
   - Early validation to fail fast before database operations
   - Caching validation results when appropriate
   - Optimized validation logic with short-circuit evaluation

3. **Database Optimizations**
   - Efficient queries with proper indexing
   - Transaction-based updates for atomic operations
   - Batch processing for multi-item operations

### Memory Optimizations

1. **Client-Side Caching**
   - Local caching of inventory state to reduce requests
   - Incremental updates to avoid full state transfers
   - Smart invalidation of cached data

2. **Connection Management**
   - Efficient connection pooling for WebSockets
   - Heartbeat mechanism to detect stale connections
   - Connection reuse to avoid reconnection overhead

## Data Flow

### Item Transfer Flow

1. Client initiates transfer request
2. Backend validates transfer against business rules
3. If valid, backend processes transfer and updates database
4. Backend emits transfer event to WebSocket
5. WebSocket broadcasts event to connected clients
6. Clients update local state and UI based on event

### Real-Time Synchronization

1. Backend emits events for inventory changes
2. WebSocket server broadcasts events to interested clients
3. Clients process events and update UI
4. New connections receive recent event history for state synchronization

## Validation Rules

### Weight Validation
- Each inventory has an optional weight limit
- Adding items checks if total weight would exceed limit
- Provides details on current weight, limit, and excess

### Slot Validation
- Slot-based inventories have a maximum number of slots
- Stackable items may share a slot up to their stack limit
- Non-stackable items require one slot each

### Transfer Validation
- Validates source has sufficient quantity
- Validates target has capacity (weight and slots)
- Validates inventory type compatibility (e.g., character to container)
- Custom game rules can be applied for specific inventory types

## Error Handling

- Detailed validation errors with actionable feedback
- Fallback mechanisms for network disruptions
- Reconnection logic with event history replay
- Error events propagated to UI for user feedback

## Future Improvements

1. **Optimistic Updates**
   - Apply changes locally before server confirmation
   - Roll back on error for better perceived performance

2. **Partial Transfers**
   - Allow transfers to succeed partially when limits are hit
   - Provide feedback on what was transferred and what failed

3. **Batched Operations**
   - Support for multi-item transfers in a single operation
   - Atomic transactions for complex inventory manipulations

4. **Enhanced Filtering**
   - Server-side filtering for large inventories
   - Pagination for inventory display

## Code Examples

### Example: Validating Item Transfer

```python
# Backend validation using the new InventoryValidator
validation_result = InventoryValidator.validate_transfer_item(
    source_inventory, 
    target_inventory, 
    item_id, 
    quantity
)

if not validation_result.valid:
    return {
        "success": False, 
        "message": validation_result.error_message, 
        "details": validation_result.details
    }
```

### Example: WebSocket Event Handling

```csharp
// Unity C# code to handle item added event
private void HandleItemAdded(JObject data)
{
    int inventoryId = data["inventory_id"].Value<int>();
    int itemId = data["item_id"].Value<int>();
    int quantity = data["quantity"].Value<int>();
    
    // Convert to dictionary for the event
    Dictionary<string, object> eventData = data.ToObject<Dictionary<string, object>>();
    
    // Request updated inventory state
    _websocketClient.RequestInventoryState();
    
    // Notify listeners
    OnItemAdded?.Invoke(eventData);
} 