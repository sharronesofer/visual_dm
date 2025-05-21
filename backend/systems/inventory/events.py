"""
Event emitter for inventory system events.

This module handles emitting events for inventory-related operations,
enabling integration with analytics, notifications, and other systems.
"""

from typing import Dict, Any, Optional, List, Callable
import logging
from datetime import datetime
import json

# Configure logger
logger = logging.getLogger(__name__)

class InventoryEventType:
    """Enum-like class for inventory event types."""
    
    ITEM_ADDED = "inventory.item.added"
    ITEM_REMOVED = "inventory.item.removed"
    ITEM_UPDATED = "inventory.item.updated"
    INVENTORY_CREATED = "inventory.created"
    INVENTORY_DELETED = "inventory.deleted"
    TRANSFER_STARTED = "inventory.transfer.started"
    TRANSFER_COMPLETED = "inventory.transfer.completed"
    TRANSFER_FAILED = "inventory.transfer.failed"
    WEIGHT_LIMIT_EXCEEDED = "inventory.weight.limit.exceeded"
    BULK_TRANSFER_STARTED = "inventory.bulk_transfer.started"
    BULK_TRANSFER_COMPLETED = "inventory.bulk_transfer.completed"
    BULK_TRANSFER_FAILED = "inventory.bulk_transfer.failed"

# Global dictionary of event handlers
_event_handlers: Dict[str, List[Callable]] = {}

def register_event_handler(event_type: str, handler: Callable) -> None:
    """
    Register an event handler for a specific event type.
    
    Args:
        event_type: Type of event to handle
        handler: Callback function to handle the event
    """
    if event_type not in _event_handlers:
        _event_handlers[event_type] = []
    
    _event_handlers[event_type].append(handler)
    logger.debug(f"Registered handler for event type: {event_type}")

def emit_event(event_type: str, payload: Dict[str, Any]) -> None:
    """
    Emit an event to all registered handlers.
    
    Args:
        event_type: Type of event
        payload: Event data
    """
    # Add timestamp if not present
    if 'timestamp' not in payload:
        payload['timestamp'] = datetime.utcnow().isoformat()
        
    # Add event type to payload
    payload['event_type'] = event_type
    
    # Log the event
    try:
        logger.debug(f"Emitting event: {event_type} - {json.dumps(payload, default=str)}")
    except Exception as e:
        logger.debug(f"Emitting event: {event_type} - {str(payload)}")
    
    # Call handlers
    if event_type in _event_handlers:
        for handler in _event_handlers[event_type]:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {str(e)}")

# Single-item transfer events

def emit_transfer_started(
    from_inventory_id: int,
    to_inventory_id: int,
    item_id: int,
    quantity: int,
    weight: float
) -> None:
    """
    Emit an event when an item transfer starts.
    
    Args:
        from_inventory_id: Source inventory ID
        to_inventory_id: Destination inventory ID
        item_id: Item being transferred
        quantity: Amount being transferred
        weight: Weight being transferred
    """
    emit_event(InventoryEventType.TRANSFER_STARTED, {
        'from_inventory_id': from_inventory_id,
        'to_inventory_id': to_inventory_id,
        'item_id': item_id,
        'quantity': quantity,
        'weight': weight
    })

def emit_transfer_completed(transfer_data: Dict[str, Any]) -> None:
    """
    Emit an event when an item transfer completes successfully.
    
    Args:
        transfer_data: Data about the completed transfer
    """
    emit_event(InventoryEventType.TRANSFER_COMPLETED, transfer_data)

def emit_transfer_failed(
    from_inventory_id: int,
    to_inventory_id: int,
    item_id: int,
    quantity: int,
    reason: str
) -> None:
    """
    Emit an event when an item transfer fails.
    
    Args:
        from_inventory_id: Source inventory ID
        to_inventory_id: Destination inventory ID
        item_id: Item that failed to transfer
        quantity: Amount that failed to transfer
        reason: Reason for failure
    """
    emit_event(InventoryEventType.TRANSFER_FAILED, {
        'from_inventory_id': from_inventory_id,
        'to_inventory_id': to_inventory_id,
        'item_id': item_id,
        'quantity': quantity,
        'reason': reason
    })

def emit_weight_limit_exceeded(
    inventory_id: int,
    current_weight: float,
    weight_limit: float,
    excess: float
) -> None:
    """
    Emit an event when a weight limit is exceeded during a transfer.
    
    Args:
        inventory_id: ID of the inventory with exceeded weight
        current_weight: Current weight of the inventory
        weight_limit: Maximum weight limit of the inventory
        excess: Amount of excess weight
    """
    emit_event(InventoryEventType.WEIGHT_LIMIT_EXCEEDED, {
        'inventory_id': inventory_id,
        'current_weight': current_weight,
        'weight_limit': weight_limit,
        'excess': excess
    })

# Bulk transfer events

def emit_bulk_transfer_started(
    from_inventory_id: int,
    to_inventory_id: int,
    item_count: int
) -> None:
    """
    Emit an event when a bulk transfer operation starts.
    
    Args:
        from_inventory_id: Source inventory ID
        to_inventory_id: Destination inventory ID
        item_count: Number of items being transferred
    """
    emit_event(InventoryEventType.BULK_TRANSFER_STARTED, {
        'from_inventory_id': from_inventory_id,
        'to_inventory_id': to_inventory_id,
        'item_count': item_count
    })

def emit_bulk_transfer_completed(transfer_data: Dict[str, Any]) -> None:
    """
    Emit an event when a bulk transfer operation completes successfully.
    
    Args:
        transfer_data: Data about the completed bulk transfer
    """
    emit_event(InventoryEventType.BULK_TRANSFER_COMPLETED, transfer_data)

def emit_bulk_transfer_failed(
    from_inventory_id: int,
    to_inventory_id: int,
    total_items: int,
    successful_items: int,
    failed_items: int,
    reason: str
) -> None:
    """
    Emit an event when a bulk transfer operation fails.
    
    Args:
        from_inventory_id: Source inventory ID
        to_inventory_id: Destination inventory ID
        total_items: Total number of items in the transfer
        successful_items: Number of items successfully transferred
        failed_items: Number of items that failed to transfer
        reason: Reason for failure
    """
    emit_event(InventoryEventType.BULK_TRANSFER_FAILED, {
        'from_inventory_id': from_inventory_id,
        'to_inventory_id': to_inventory_id,
        'total_items': total_items,
        'successful_items': successful_items,
        'failed_items': failed_items,
        'reason': reason
    }) 