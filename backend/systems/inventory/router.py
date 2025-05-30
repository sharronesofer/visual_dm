"""
FastAPI router for inventory operations.

This module defines the FastAPI router endpoints for inventory operations,
providing the API interface to the inventory system.
"""

from typing import List, Dict, Any, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, Response, status
from fastapi.responses import JSONResponse

from backend.core.database import db
from backend.systems.inventory.models import Item, Inventory, InventoryItem
from backend.systems.inventory.service import InventoryService
from backend.systems.inventory.notification import InventoryNotifier
from backend.systems.inventory.operations import TransferOperations, ItemOperations
from backend.systems.inventory.schemas import InventoryItemSchema, ItemSchema

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}}
)

# Item endpoints
@router.get("/items", response_model=List[Dict[str, Any]])
async def get_items(
    limit: int = Query(100, description="Maximum number of items to return"),
    offset: int = Query(0, description="Offset for pagination"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get a list of items with optional filtering."""
    try:
        items = InventoryService.get_items(limit=limit, offset=offset, category=category)
        return [item.to_dict() for item in items]
    except Exception as e:
        logger.error(f"Error fetching items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/items/{item_id}", response_model=Dict[str, Any])
async def get_item(item_id: int = Path(..., description="Item ID")):
    """Get a specific item by ID."""
    item = InventoryService.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item.to_dict()

@router.post("/items", response_model=Dict[str, Any])
async def create_item(item_data: Dict[str, Any] = Body(..., description="Item data")):
    """Create a new item."""
    try:
        success, error, item = InventoryService.create_item(item_data)
        if not success:
            raise HTTPException(status_code=400, detail=error)
        return item.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/items/{item_id}", response_model=Dict[str, Any])
async def update_item(
    item_id: int = Path(..., description="Item ID"),
    item_data: Dict[str, Any] = Body(..., description="Updated item data")
):
    """Update an existing item."""
    try:
        success, error, item = InventoryService.update_item(item_id, item_data)
        if not success:
            raise HTTPException(status_code=404, detail=error)
        return item.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/items/{item_id}", response_model=Dict[str, Any])
async def delete_item(item_id: int = Path(..., description="Item ID")):
    """Delete an item."""
    try:
        success, error = InventoryService.delete_item(item_id)
        if not success:
            raise HTTPException(status_code=404, detail=error)
        return {"message": f"Item {item_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Inventory endpoints
@router.get("/inventories", response_model=List[Dict[str, Any]])
async def get_inventories(
    limit: int = Query(100, description="Maximum number of inventories to return"),
    offset: int = Query(0, description="Offset for pagination"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    inventory_type: Optional[str] = Query(None, description="Filter by inventory type")
):
    """Get a list of inventories with optional filtering."""
    try:
        inventories = InventoryService.get_inventories(
            limit=limit, 
            offset=offset, 
            owner_id=owner_id, 
            inventory_type=inventory_type
        )
        return [inv.to_dict() for inv in inventories]
    except Exception as e:
        logger.error(f"Error fetching inventories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/inventories/{inventory_id}", response_model=Dict[str, Any])
async def get_inventory(
    inventory_id: int = Path(..., description="Inventory ID"),
    with_items: bool = Query(True, description="Include items in response")
):
    """Get a specific inventory by ID."""
    inventory = InventoryService.get_inventory(inventory_id, include_items=with_items)
    if not inventory:
        raise HTTPException(status_code=404, detail=f"Inventory {inventory_id} not found")
    return inventory.to_dict(include_items=with_items)

@router.post("/inventories", response_model=Dict[str, Any])
async def create_inventory(inventory_data: Dict[str, Any] = Body(..., description="Inventory data")):
    """Create a new inventory."""
    try:
        inventory = InventoryService.create_inventory(inventory_data)
        if not inventory:
            raise HTTPException(status_code=400, detail="Failed to create inventory")
            
        # Trigger notification
        InventoryNotifier.notify_inventory_created(
            inventory.id, 
            inventory.inventory_type, 
            inventory.owner_id
        )
        
        return inventory.to_dict()
    except Exception as e:
        logger.error(f"Error creating inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/inventories/{inventory_id}", response_model=Dict[str, Any])
async def update_inventory(
    inventory_id: int = Path(..., description="Inventory ID"),
    inventory_data: Dict[str, Any] = Body(..., description="Updated inventory data")
):
    """Update an existing inventory."""
    try:
        success, error, inventory = InventoryService.update_inventory(inventory_id, inventory_data)
        if not success:
            raise HTTPException(status_code=404, detail=error)
        return inventory.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating inventory {inventory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/inventories/{inventory_id}", response_model=Dict[str, Any])
async def delete_inventory(inventory_id: int = Path(..., description="Inventory ID")):
    """Delete an inventory."""
    try:
        inventory = InventoryService.get_inventory(inventory_id, include_items=False)
        if not inventory:
            raise HTTPException(status_code=404, detail=f"Inventory {inventory_id} not found")
            
        success, error = InventoryService.delete_inventory(inventory_id)
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        # Trigger notification
        InventoryNotifier.notify_inventory_deleted(
            inventory_id, 
            inventory.inventory_type, 
            inventory.owner_id
        )
        
        return {"message": f"Inventory {inventory_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting inventory {inventory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Inventory item endpoints
@router.get("/inventories/{inventory_id}/items", response_model=List[Dict[str, Any]])
async def get_inventory_items(inventory_id: int = Path(..., description="Inventory ID")):
    """Get all items in an inventory."""
    inventory = InventoryService.get_inventory(inventory_id)
    if not inventory:
        raise HTTPException(status_code=404, detail=f"Inventory {inventory_id} not found")
    
    items = InventoryService.get_inventory_items(inventory_id)
    return [item.to_dict() for item in items]

@router.post("/inventories/{inventory_id}/items", response_model=Dict[str, Any])
async def add_item_to_inventory(
    inventory_id: int = Path(..., description="Inventory ID"),
    item_data: Dict[str, Any] = Body(..., description="Item data to add")
):
    """Add an item to an inventory."""
    try:
        item_id = item_data.get("item_id")
        quantity = item_data.get("quantity", 1)
        is_equipped = item_data.get("is_equipped", False)
        custom_name = item_data.get("custom_name")
        position = item_data.get("position")
        
        success, error, inventory_item = InventoryService.add_item_to_inventory(
            inventory_id, 
            item_id, 
            quantity, 
            is_equipped,
            custom_name,
            position
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=error)
            
        # Trigger notification
        if inventory_item:
            InventoryNotifier.notify_item_added(
                inventory_id,
                item_id,
                quantity,
                inventory_item.id
            )
            
        return inventory_item.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item to inventory {inventory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/inventories/{inventory_id}/items/{inventory_item_id}", response_model=Dict[str, Any])
async def remove_item_from_inventory(
    inventory_id: int = Path(..., description="Inventory ID"),
    inventory_item_id: int = Path(..., description="Inventory item ID"),
    quantity: Optional[int] = Query(None, description="Quantity to remove (all if not specified)")
):
    """Remove an item from an inventory."""
    try:
        # Get inventory item for notification before deletion
        inventory_item = InventoryService.get_inventory_item(inventory_item_id)
        if not inventory_item or inventory_item.inventory_id != inventory_id:
            raise HTTPException(
                status_code=404, 
                detail=f"Item {inventory_item_id} not found in inventory {inventory_id}"
            )
            
        item_id = inventory_item.item_id
        removed_quantity = quantity if quantity is not None else inventory_item.quantity
        
        success, error = InventoryService.remove_item_from_inventory(
            inventory_id,
            inventory_item_id,
            quantity
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=error)
            
        # Trigger notification
        InventoryNotifier.notify_item_removed(
            inventory_id,
            item_id,
            removed_quantity,
            inventory_item_id
        )
        
        return {"message": f"Successfully removed {removed_quantity} item(s) from inventory"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing item from inventory {inventory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/inventories/{inventory_id}/items/{inventory_item_id}", response_model=Dict[str, Any])
async def update_inventory_item(
    inventory_id: int = Path(..., description="Inventory ID"),
    inventory_item_id: int = Path(..., description="Inventory item ID"),
    item_updates: Dict[str, Any] = Body(..., description="Item updates")
):
    """Update an inventory item."""
    try:
        success, error, inventory_item = InventoryService.update_inventory_item(
            inventory_id,
            inventory_item_id,
            item_updates
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=error)
            
        # Check if an equip/unequip event should be triggered
        if "is_equipped" in item_updates:
            if item_updates["is_equipped"]:
                InventoryNotifier.notify_item_equipped(
                    inventory_id,
                    inventory_item_id,
                    inventory_item.item_id
                )
            else:
                InventoryNotifier.notify_item_unequipped(
                    inventory_id,
                    inventory_item_id,
                    inventory_item.item_id
                )
                
        return inventory_item.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item in inventory {inventory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/transfer", response_model=Dict[str, Any])
async def transfer_item(
    transfer_data: Dict[str, Any] = Body(..., description="Transfer data")
):
    """Transfer an item between inventories."""
    try:
        from_inventory_id = transfer_data.get("from_inventory_id")
        to_inventory_id = transfer_data.get("to_inventory_id")
        inventory_item_id = transfer_data.get("inventory_item_id")
        quantity = transfer_data.get("quantity", 1)
        
        if not all([from_inventory_id, to_inventory_id, inventory_item_id]):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: from_inventory_id, to_inventory_id, inventory_item_id"
            )
            
        # Get source item for notification
        inventory_item = InventoryService.get_inventory_item(inventory_item_id)
        if not inventory_item or inventory_item.inventory_id != from_inventory_id:
            raise HTTPException(
                status_code=404, 
                detail=f"Item {inventory_item_id} not found in source inventory {from_inventory_id}"
            )
            
        item_id = inventory_item.item_id
        
        success, error, transfer_data = InventoryService.transfer_item(
            from_inventory_id,
            to_inventory_id,
            inventory_item_id,
            quantity
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=error)
            
        # Trigger notification
        if transfer_data:
            InventoryNotifier.notify_item_transferred(
                from_inventory_id,
                to_inventory_id,
                item_id,
                quantity,
                inventory_item_id,
                transfer_data.get("to_inventory_item_id")
            )
            
        return {"message": "Transfer successful", "data": transfer_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transferring item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/inventory/{from_inventory_id}/transfer/{to_inventory_id}/{inventory_item_id}")
async def transfer_item(
    from_inventory_id: int,
    to_inventory_id: int,
    inventory_item_id: int,
    quantity: int = Body(..., embed=True),
    response: Response = None
):
    """
    Transfer an item from one inventory to another.
    
    Args:
        from_inventory_id: Source inventory ID
        to_inventory_id: Destination inventory ID
        inventory_item_id: Inventory item ID to transfer
        quantity: Quantity to transfer
        
    Returns:
        Transfer result
    """
    success, error, data = TransferOperations.transfer_items(
        from_inventory_id,
        to_inventory_id,
        inventory_item_id,
        quantity
    )
    
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": error, "data": data}
        
    return {"success": True, "data": data}

@router.post("/inventory/{from_inventory_id}/bulk-transfer/{to_inventory_id}")
async def bulk_transfer_items(
    from_inventory_id: int,
    to_inventory_id: int,
    items_data: List[Dict[str, Any]] = Body(...),
    response: Response = None
):
    """
    Transfer multiple items between inventories in a single transaction.
    
    Args:
        from_inventory_id: Source inventory ID
        to_inventory_id: Destination inventory ID
        items_data: List of items to transfer, each containing:
            - inventory_item_id: ID of the inventory item
            - quantity: Quantity to transfer
            
    Returns:
        Bulk transfer result with details of successful and failed transfers
    """
    # Validate request data
    for i, item in enumerate(items_data):
        if 'inventory_item_id' not in item:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "success": False, 
                "error": f"Missing 'inventory_item_id' in item at index {i}"
            }
            
        if 'quantity' not in item:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "success": False, 
                "error": f"Missing 'quantity' in item at index {i}"
            }
            
        if not isinstance(item['quantity'], int) or item['quantity'] <= 0:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "success": False, 
                "error": f"Invalid quantity value in item at index {i}. Must be a positive integer."
            }
    
    # Execute bulk transfer
    success, error, data = TransferOperations.bulk_transfer_items(
        from_inventory_id,
        to_inventory_id,
        items_data
    )
    
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": error, "data": data}
        
    return {"success": True, "data": data}

# Statistics and utility endpoints
@router.get("/inventories/{inventory_id}/stats", response_model=Dict[str, Any])
async def get_inventory_stats(inventory_id: int = Path(..., description="Inventory ID")):
    """Get statistics for an inventory."""
    try:
        stats = InventoryService.calculate_inventory_stats(inventory_id)
        if not stats:
            raise HTTPException(status_code=404, detail=f"Inventory {inventory_id} not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inventory stats for {inventory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/inventories/{inventory_id}/backup", response_model=Dict[str, Any])
async def backup_inventory(inventory_id: int = Path(..., description="Inventory ID")):
    """Create a backup of an inventory."""
    try:
        result = InventoryService.backup_inventory(inventory_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Backup failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error backing up inventory {inventory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/inventories/restore", response_model=Dict[str, Any])
async def restore_inventory(
    backup_data: Dict[str, Any] = Body(..., description="Backup data from a previous backup"),
    owner_id: Optional[int] = Query(None, description="New owner ID for the restored inventory")
):
    """Restore an inventory from backup data."""
    try:
        result = InventoryService.restore_inventory(backup_data, owner_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Restore failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/inventories/{inventory_id}/export", response_model=Dict[str, Any])
async def export_inventory(inventory_id: int = Path(..., description="Inventory ID")):
    """Export an inventory to JSON format."""
    try:
        success, error, export_data = InventoryService.export_inventory(inventory_id)
        if not success:
            raise HTTPException(status_code=404, detail=error)
        return {"success": True, "data": export_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting inventory {inventory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/inventories/import", response_model=Dict[str, Any])
async def import_inventory(
    import_data: Dict[str, Any] = Body(..., description="Inventory data to import"),
    owner_id: Optional[int] = Query(None, description="Owner ID for the imported inventory")
):
    """Import an inventory from JSON format."""
    try:
        success, error, inventory = InventoryService.import_inventory(import_data, owner_id)
        if not success:
            raise HTTPException(status_code=400, detail=error)
            
        return {
            "success": True, 
            "message": "Import successful",
            "inventory_id": inventory.id if inventory else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/inventories/{inventory_id}/swap")
async def swap_items(
    inventory_id: int = Path(..., description="Inventory ID"),
    swap_data: Dict[str, Any] = Body(..., description="Items to swap"),
    response: Response = None
):
    """
    Swap the positions of two items in the same inventory.
    
    Args:
        inventory_id: ID of the inventory
        swap_data: Dictionary with item_id1 and item_id2
        
    Returns:
        Swap result
    """
    item_id1 = swap_data.get('item_id1')
    item_id2 = swap_data.get('item_id2')
    
    # Validate request
    if not item_id1 or not item_id2:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "error": "Missing required fields: item_id1 and item_id2"
        }
        
    # Execute swap
    success, error = ItemOperations.swap_items(
        inventory_id,
        item_id1,
        item_id2
    )
    
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": error}
        
    return {"success": True, "message": "Items swapped successfully"}

@router.post("/inventories/{inventory_id}/split-stack/{stack_id}")
async def split_stack(
    inventory_id: int = Path(..., description="Inventory ID"),
    stack_id: int = Path(..., description="Stack ID to split"),
    quantity: int = Body(..., embed=True, description="Quantity to move to new stack"),
    response: Response = None
):
    """
    Split an item stack into two separate stacks.
    
    Args:
        inventory_id: ID of the inventory
        stack_id: ID of the stack to split
        quantity: Quantity to move to the new stack
        
    Returns:
        Split result with new stack details
    """
    from backend.systems.inventory.utils import split_item_stack
    
    # Execute split operation
    success, error, result = split_item_stack(
        inventory_id,
        stack_id,
        quantity
    )
    
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": error, "details": result}
        
    return {"success": True, "data": result}

@router.post("/inventories/{inventory_id}/combine-stacks")
async def combine_stacks(
    inventory_id: int = Path(..., description="Inventory ID"),
    combine_data: Dict[str, Any] = Body(..., description="Stack combine data"),
    response: Response = None
):
    """
    Combine two item stacks in an inventory.
    
    Args:
        inventory_id: ID of the inventory
        combine_data: Dictionary with source_stack_id, target_stack_id, and optional quantity
        
    Returns:
        Combine result
    """
    source_stack_id = combine_data.get('source_stack_id')
    target_stack_id = combine_data.get('target_stack_id')
    quantity = combine_data.get('quantity')  # Optional
    
    # Validate request
    if not source_stack_id or not target_stack_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "error": "Missing required fields: source_stack_id and target_stack_id"
        }
        
    from backend.systems.inventory.utils import combine_item_stacks
    
    # Execute combine operation
    success, error, result = combine_item_stacks(
        inventory_id,
        source_stack_id,
        target_stack_id,
        quantity
    )
    
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": error}
        
    return {"success": True, "data": result}

@router.post("/inventories/{inventory_id}/optimize-stacks")
async def optimize_stacks(
    inventory_id: int = Path(..., description="Inventory ID"),
    response: Response = None
):
    """
    Optimize inventory by combining stackable items of the same type.
    
    Args:
        inventory_id: ID of the inventory
        
    Returns:
        Optimization result with counts of combined and removed stacks
    """
    from backend.systems.inventory.utils import optimize_inventory_stacks
    
    # Execute optimization
    success, error, result = optimize_inventory_stacks(inventory_id)
    
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": error}
        
    return {
        "success": True, 
        "data": result,
        "message": f"Combined {result['combined_stacks']} stacks and removed {result['removed_stacks']} empty stacks"
    }

@router.post("/inventories/{inventory_id}/filter")
async def filter_items(
    inventory_id: int = Path(..., description="Inventory ID"),
    filters: Dict[str, Any] = Body(..., description="Filter criteria"),
    response: Response = None
):
    """
    Filter inventory items by various criteria.
    
    Args:
        inventory_id: ID of the inventory
        filters: Dictionary of filter criteria, which may include:
            - name: String to search in item names
            - description: String to search in item descriptions
            - category: Category or list of categories to match
            - min_weight: Minimum weight
            - max_weight: Maximum weight
            - min_value: Minimum value
            - max_value: Maximum value
            - is_equipped: Boolean to filter equipped/unequipped items
            - properties: Dictionary of property key-values to match
            - sort_by: Field to sort by (name, weight, value, category)
            - sort_dir: Sort direction (asc or desc)
            
    Returns:
        Filtered items matching the criteria
    """
    from backend.systems.inventory.utils import filter_inventory_items
    
    # Execute filtering
    success, error, items = filter_inventory_items(
        inventory_id,
        filters
    )
    
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": error}
        
    return {
        "success": True,
        "data": {
            "items": items,
            "count": len(items),
            "filters_applied": filters
        }
    }

@router.post("/admin/inventory/run-migrations")
async def run_inventory_migrations(
    response: Response = None
):
    """
    Run inventory system migrations to update database schema.
    This endpoint should only be accessible to administrators.
    
    Returns:
        Migration results
    """
    try:
        from backend.systems.inventory.migrations import run_migrations
        
        # Execute migrations
        results = run_migrations()
        
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error running inventory migrations: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False,
            "error": f"Migration failed: {str(e)}"
        } 