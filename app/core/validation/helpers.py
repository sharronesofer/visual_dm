"""
Helper functions for validating common game actions.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from app.core.api.error_handling.exceptions import ValidationError, ForbiddenError, NotFoundError
from app.core.validation.validators import (
    ValidationResult, StringValidator, NumberValidator, 
    BooleanValidator, DateTimeValidator, ListValidator, DictValidator
)
from flask import g

def validate_resource_ownership(resource, owner_field: str = 'user_id') -> Optional[ValidationError]:
    """
    Validate that the current user owns a resource.
    
    Args:
        resource: Resource to validate ownership for
        owner_field: Field on resource that contains owner ID
        
    Returns:
        ValidationError if user doesn't own resource, None otherwise
    """
    if not hasattr(g, 'current_user') or not g.current_user:
        return ForbiddenError(message="Authentication required to access this resource")
    
    if not resource:
        return NotFoundError(resource_type="Resource", resource_id="unknown")
    
    if not hasattr(resource, owner_field) or getattr(resource, owner_field) != g.current_user.id:
        return ForbiddenError(message="You do not have permission to access this resource")
    
    return None

def validate_movement(current_position: Dict[str, float], target_position: Dict[str, float], 
                     max_distance: float = 100.0) -> Tuple[bool, Optional[str]]:
    """
    Validate a movement action.
    
    Args:
        current_position: Current position {x, y, z}
        target_position: Target position {x, y, z}
        max_distance: Maximum allowed movement distance
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for required coordinates
    for coord in ['x', 'y', 'z']:
        if coord not in current_position or coord not in target_position:
            return False, f"Missing {coord} coordinate"
    
    # Calculate distance
    dx = target_position['x'] - current_position['x']
    dy = target_position['y'] - current_position['y']
    dz = target_position['z'] - current_position['z']
    distance = (dx**2 + dy**2 + dz**2) ** 0.5
    
    # Check if distance is valid
    if distance > max_distance:
        return False, f"Movement distance {distance:.2f} exceeds maximum allowed distance {max_distance:.2f}"
    
    return True, None

def validate_purchase(player_currency: int, item_cost: int) -> Tuple[bool, Optional[str]]:
    """
    Validate a purchase action.
    
    Args:
        player_currency: Current player currency
        item_cost: Cost of the item
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if player_currency < item_cost:
        return False, f"Insufficient currency. Required: {item_cost}, Available: {player_currency}"
    
    return True, None

def validate_combat_action(
    action_type: str,
    cooldowns: Dict[str, datetime],
    player_stats: Dict[str, Any],
    target_stats: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """
    Validate a combat action.
    
    Args:
        action_type: Type of combat action
        cooldowns: Mapping of action types to cooldown timestamps
        player_stats: Player statistics
        target_stats: Target statistics
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check cooldown
    if action_type in cooldowns and cooldowns[action_type] > datetime.now():
        time_remaining = (cooldowns[action_type] - datetime.now()).total_seconds()
        return False, f"Action {action_type} is on cooldown for {time_remaining:.1f} more seconds"
    
    # Check if action requires specific stats or resources
    if action_type == 'special_attack' and player_stats.get('energy', 0) < 20:
        return False, "Special attack requires 20 energy"
    
    # Check if target is valid for the action
    if target_stats.get('health', 0) <= 0:
        return False, "Cannot perform action on defeated target"
    
    return True, None

# Validator schemas for common game actions

MOVEMENT_VALIDATOR_SCHEMA = {
    'position': DictValidator('position', schema={
        'x': NumberValidator('position.x'),
        'y': NumberValidator('position.y'),
        'z': NumberValidator('position.z')
    })
}

PURCHASE_VALIDATOR_SCHEMA = {
    'item_id': StringValidator('item_id'),
    'quantity': NumberValidator('quantity', min_value=1, is_integer=True)
}

COMBAT_ACTION_VALIDATOR_SCHEMA = {
    'action_type': StringValidator('action_type', allowed_values=[
        'attack', 'defend', 'special_attack', 'use_item'
    ]),
    'target_id': StringValidator('target_id'),
    'intensity': NumberValidator('intensity', required=False, min_value=0.1, max_value=1.0)
}

ITEM_USE_VALIDATOR_SCHEMA = {
    'item_id': StringValidator('item_id'),
    'target_id': StringValidator('target_id', required=False)
}

def create_action_validator(action_type: str) -> Dict[str, Any]:
    """
    Create a validator schema for a specific action type.
    
    Args:
        action_type: Type of action to validate
        
    Returns:
        Validator schema
    """
    if action_type == 'movement':
        return MOVEMENT_VALIDATOR_SCHEMA
    elif action_type == 'purchase':
        return PURCHASE_VALIDATOR_SCHEMA
    elif action_type == 'combat':
        return COMBAT_ACTION_VALIDATOR_SCHEMA
    elif action_type == 'item_use':
        return ITEM_USE_VALIDATOR_SCHEMA
    else:
        raise ValueError(f"Unknown action type: {action_type}") 