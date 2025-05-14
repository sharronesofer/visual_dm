"""
API routes for player actions with comprehensive validation.
"""

from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.player import Player
from app.models.item import Item
from app.core.database import db

from app.core.validation.validators import (
    StringValidator, NumberValidator, DictValidator, ListValidator,
    validate_request_data
)
from app.core.validation.middleware import (
    validate_json, validate_query_params, validate_request_context
)
from app.core.validation.rate_limiter import rate_limit
from app.core.validation.transaction import transaction
from app.core.validation.security import require_signature
from app.core.validation.helpers import (
    validate_movement, validate_purchase, validate_combat_action,
    validate_resource_ownership,
    MOVEMENT_VALIDATOR_SCHEMA, PURCHASE_VALIDATOR_SCHEMA, 
    COMBAT_ACTION_VALIDATOR_SCHEMA, ITEM_USE_VALIDATOR_SCHEMA
)

from app.core.api.error_handling.exceptions import (
    ValidationError, NotFoundError, ForbiddenError, ResourceLockedError
)

player_actions_bp = Blueprint('player_actions', __name__)

# --- Player Movement ---
@player_actions_bp.route('/players/<int:player_id>/movement', methods=['POST'])
@jwt_required()
@validate_json(MOVEMENT_VALIDATOR_SCHEMA)
@rate_limit('movement')
@transaction('player_movement')
def move_player(player_id):
    """Move a player to a new position."""
    # Get player
    player = Player.query.get(player_id)
    if not player:
        raise NotFoundError("Player", str(player_id))
    
    # Verify ownership
    error = validate_resource_ownership(player)
    if error:
        raise error
    
    # Get validated data from request context
    data = g.validated_data
    target_position = data['position']
    
    # Get current position
    current_position = {
        'x': player.position_x,
        'y': player.position_y,
        'z': player.position_z
    }
    
    # Validate movement
    is_valid, error_message = validate_movement(
        current_position, 
        target_position,
        max_distance=player.max_movement_distance
    )
    if not is_valid:
        raise ValidationError(
            message=error_message,
            details=[{
                "field": "position",
                "message": error_message,
                "current_position": current_position,
                "target_position": target_position
            }]
        )
    
    # Update player position
    player.position_x = target_position['x']
    player.position_y = target_position['y']
    player.position_z = target_position['z']
    player.last_movement_time = db.func.now()
    
    # Commit changes (transaction decorator handles commit/rollback)
    
    return jsonify({
        "message": "Player moved successfully",
        "player_id": player_id,
        "new_position": target_position
    }), 200

# --- Item Purchase ---
@player_actions_bp.route('/players/<int:player_id>/purchases', methods=['POST'])
@jwt_required()
@validate_json(PURCHASE_VALIDATOR_SCHEMA)
@rate_limit('purchase')
@transaction('item_purchase')
def purchase_item(player_id):
    """Purchase an item for a player."""
    # Get player
    player = Player.query.get(player_id)
    if not player:
        raise NotFoundError("Player", str(player_id))
    
    # Verify ownership
    error = validate_resource_ownership(player)
    if error:
        raise error
    
    # Get validated data from request context
    data = g.validated_data
    item_id = data['item_id']
    quantity = data['quantity']
    
    # Get item
    item = Item.query.get(item_id)
    if not item:
        raise NotFoundError("Item", item_id)
    
    # Check if item is purchasable
    if not item.purchasable:
        raise ValidationError(
            message="Item is not purchasable",
            details=[{
                "field": "item_id",
                "message": "Item is not purchasable",
                "item_id": item_id
            }]
        )
    
    # Calculate total cost
    total_cost = item.price * quantity
    
    # Validate purchase
    is_valid, error_message = validate_purchase(player.currency, total_cost)
    if not is_valid:
        raise ValidationError(
            message=error_message,
            details=[{
                "field": "quantity",
                "message": error_message,
                "item_cost": item.price,
                "quantity": quantity,
                "total_cost": total_cost,
                "player_currency": player.currency
            }]
        )
    
    # Update player currency
    player.currency -= total_cost
    
    # Add item to player inventory
    # (In a real implementation, this would involve creating inventory entries)
    current_app.logger.info(f"Player {player_id} purchased {quantity} of item {item_id}")
    
    # Return success response
    return jsonify({
        "message": "Item purchased successfully",
        "player_id": player_id,
        "item_id": item_id,
        "quantity": quantity,
        "total_cost": total_cost,
        "remaining_currency": player.currency
    }), 200

# --- Combat Action ---
@player_actions_bp.route('/players/<int:player_id>/combat-actions', methods=['POST'])
@jwt_required()
@validate_json(COMBAT_ACTION_VALIDATOR_SCHEMA)
@rate_limit('combat')
@require_signature({'action_type', 'target_id'})  # Require signed requests for combat actions
@transaction('combat_action')
def perform_combat_action(player_id):
    """Perform a combat action."""
    # Get player
    player = Player.query.get(player_id)
    if not player:
        raise NotFoundError("Player", str(player_id))
    
    # Verify ownership
    error = validate_resource_ownership(player)
    if error:
        raise error
    
    # Get validated data from request context
    data = g.validated_data
    action_type = data['action_type']
    target_id = data['target_id']
    intensity = data.get('intensity', 1.0)
    
    # Get target
    target = Player.query.get(target_id)
    if not target:
        raise NotFoundError("Target", target_id)
    
    # Check if player is in combat
    if not player.is_in_combat:
        raise ValidationError(
            message="Player is not in combat",
            details=[{
                "field": "player_id",
                "message": "Player is not in combat",
                "player_id": player_id
            }]
        )
    
    # Check if target is valid for combat
    if not target.is_in_combat:
        raise ValidationError(
            message="Target is not in combat",
            details=[{
                "field": "target_id",
                "message": "Target is not in combat",
                "target_id": target_id
            }]
        )
    
    # Validate combat action
    player_stats = {
        'health': player.health,
        'energy': player.energy,
        'level': player.level
    }
    target_stats = {
        'health': target.health,
        'energy': target.energy,
        'level': target.level
    }
    cooldowns = {
        # Example cooldowns - would be retrieved from player data in practice
        'special_attack': player.last_special_attack_time
    }
    
    is_valid, error_message = validate_combat_action(
        action_type, cooldowns, player_stats, target_stats
    )
    if not is_valid:
        raise ValidationError(
            message=error_message,
            details=[{
                "field": "action_type",
                "message": error_message,
                "action_type": action_type
            }]
        )
    
    # Perform action based on type
    if action_type == 'attack':
        # Calculate damage
        damage = player.calculate_damage(intensity)
        target.health -= damage
        
        # Update last attack time
        player.last_attack_time = db.func.now()
        
        response_data = {
            "message": "Attack successful",
            "damage_dealt": damage,
            "target_remaining_health": target.health
        }
    elif action_type == 'special_attack':
        # Calculate damage for special attack
        damage = player.calculate_special_damage(intensity)
        target.health -= damage
        
        # Consume energy
        player.energy -= 20
        
        # Update last special attack time
        player.last_special_attack_time = db.func.now()
        
        response_data = {
            "message": "Special attack successful",
            "damage_dealt": damage,
            "target_remaining_health": target.health,
            "remaining_energy": player.energy
        }
    elif action_type == 'defend':
        # Apply defense effect
        player.is_defending = True
        player.defense_multiplier = 2.0
        
        response_data = {
            "message": "Defense successful",
            "defense_multiplier": player.defense_multiplier
        }
    else:
        raise ValidationError(
            message=f"Invalid action type: {action_type}",
            details=[{
                "field": "action_type",
                "message": f"Invalid action type: {action_type}",
                "action_type": action_type
            }]
        )
    
    # Return response
    return jsonify({
        "player_id": player_id,
        "target_id": target_id,
        "action_type": action_type,
        "intensity": intensity,
        **response_data
    }), 200

# --- Item Use ---
@player_actions_bp.route('/players/<int:player_id>/item-use', methods=['POST'])
@jwt_required()
@validate_json(ITEM_USE_VALIDATOR_SCHEMA)
@rate_limit('item_use')
@transaction('item_use')
def use_item(player_id):
    """Use an item."""
    # Get player
    player = Player.query.get(player_id)
    if not player:
        raise NotFoundError("Player", str(player_id))
    
    # Verify ownership
    error = validate_resource_ownership(player)
    if error:
        raise error
    
    # Get validated data from request context
    data = g.validated_data
    item_id = data['item_id']
    target_id = data.get('target_id')
    
    # Get item from player inventory
    inventory_item = player.inventory.filter_by(item_id=item_id).first()
    if not inventory_item:
        raise ValidationError(
            message="Item not in inventory",
            details=[{
                "field": "item_id",
                "message": "Item not in inventory",
                "item_id": item_id
            }]
        )
    
    # Check if item is usable
    item = inventory_item.item
    if not item.usable:
        raise ValidationError(
            message="Item is not usable",
            details=[{
                "field": "item_id",
                "message": "Item is not usable",
                "item_id": item_id
            }]
        )
    
    # Check if target is required and present
    if item.requires_target and not target_id:
        raise ValidationError(
            message="Target is required for this item",
            details=[{
                "field": "target_id",
                "message": "Target is required for this item",
                "item_id": item_id
            }]
        )
    
    # Get target if needed
    target = None
    if target_id:
        target = Player.query.get(target_id)
        if not target:
            raise NotFoundError("Target", target_id)
    
    # Use item (effects would vary by item type)
    if item.type == 'healing':
        # Healing item
        healing_amount = item.effect_value
        player.health = min(player.max_health, player.health + healing_amount)
        inventory_item.quantity -= 1
        
        response_data = {
            "message": "Healing item used successfully",
            "healing_amount": healing_amount,
            "new_health": player.health
        }
    elif item.type == 'buff':
        # Buff item
        player.apply_buff(item.effect_type, item.effect_value, item.effect_duration)
        inventory_item.quantity -= 1
        
        response_data = {
            "message": "Buff item used successfully",
            "buff_type": item.effect_type,
            "buff_value": item.effect_value,
            "buff_duration": item.effect_duration
        }
    else:
        raise ValidationError(
            message=f"Unsupported item type: {item.type}",
            details=[{
                "field": "item_id",
                "message": f"Unsupported item type: {item.type}",
                "item_id": item_id,
                "item_type": item.type
            }]
        )
    
    # Remove item if quantity is zero
    if inventory_item.quantity <= 0:
        db.session.delete(inventory_item)
    
    # Return response
    return jsonify({
        "player_id": player_id,
        "item_id": item_id,
        "item_name": item.name,
        "remaining_quantity": max(0, inventory_item.quantity),
        **response_data
    }), 200 