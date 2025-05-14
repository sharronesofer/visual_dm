"""Equipment-related routes and endpoints."""

from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
from typing import Dict, Any
from app.auth.auth_utils import require_auth
from app.rules.rules_utils import validate_equipment_item

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/equip', methods=['POST'])
@require_auth
def equip_item() -> Dict[str, Any]:
    """
    Equip an item on a character.
    
    Returns:
        Dict containing equipment result
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['character_id', 'item_id', 'slot']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Get character and item data
        character_ref = db.reference(f'/characters/{data["character_id"]}')
        item_ref = db.reference(f'/items/{data["item_id"]}')
        
        character = character_ref.get()
        item = item_ref.get()
        
        if not character or not item:
            return jsonify({
                'success': False,
                'message': 'Character or item not found'
            }), 404
            
        # Validate item can be equipped
        valid, details = validate_equipment_item(item['name'])
        if not valid:
            return jsonify({
                'success': False,
                'message': details
            }), 400
            
        # Update equipment slots
        equipment = character.get('equipment', {})
        old_item = equipment.get(data['slot'])
        equipment[data['slot']] = data['item_id']
        
        # Update character
        character_ref.update({'equipment': equipment})
        
        # If replacing an item, return it to inventory
        if old_item:
            inventory = character.get('inventory', [])
            inventory.append(old_item)
            character_ref.update({'inventory': inventory})
        
        return jsonify({
            'success': True,
            'equipment': equipment,
            'replaced_item': old_item
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error equipping item: {str(e)}'
        }), 500

@equipment_bp.route('/unequip', methods=['POST'])
@require_auth
def unequip_item() -> Dict[str, Any]:
    """
    Unequip an item from a character.
    
    Returns:
        Dict containing unequip result
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['character_id', 'slot']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Get character data
        character_ref = db.reference(f'/characters/{data["character_id"]}')
        character = character_ref.get()
        
        if not character:
            return jsonify({
                'success': False,
                'message': 'Character not found'
            }), 404
            
        # Get item from equipment slot
        equipment = character.get('equipment', {})
        item_id = equipment.get(data['slot'])
        
        if not item_id:
            return jsonify({
                'success': False,
                'message': f'No item equipped in slot {data["slot"]}'
            }), 400
            
        # Remove item from equipment
        equipment.pop(data['slot'])
        
        # Add item to inventory
        inventory = character.get('inventory', [])
        inventory.append(item_id)
        
        # Update character
        character_ref.update({
            'equipment': equipment,
            'inventory': inventory
        })
        
        return jsonify({
            'success': True,
            'equipment': equipment,
            'inventory': inventory
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error unequipping item: {str(e)}'
        }), 500

@equipment_bp.route('/transfer', methods=['POST'])
@require_auth
def transfer_item() -> Dict[str, Any]:
    """
    Transfer an item between characters.
    
    Returns:
        Dict containing transfer result
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['from_character_id', 'to_character_id', 'item_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Get character data
        from_ref = db.reference(f'/characters/{data["from_character_id"]}')
        to_ref = db.reference(f'/characters/{data["to_character_id"]}')
        
        from_char = from_ref.get()
        to_char = to_ref.get()
        
        if not from_char or not to_char:
            return jsonify({
                'success': False,
                'message': 'One or both characters not found'
            }), 404
            
        # Check item exists in inventory
        from_inventory = from_char.get('inventory', [])
        if data['item_id'] not in from_inventory:
            return jsonify({
                'success': False,
                'message': 'Item not found in source character inventory'
            }), 400
            
        # Transfer item
        from_inventory.remove(data['item_id'])
        to_inventory = to_char.get('inventory', [])
        to_inventory.append(data['item_id'])
        
        # Update both characters
        from_ref.update({'inventory': from_inventory})
        to_ref.update({'inventory': to_inventory})
        
        # Log transfer
        transfer_log = {
            'from_character': data['from_character_id'],
            'to_character': data['to_character_id'],
            'item_id': data['item_id'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        db.reference('/item_transfers').push(transfer_log)
        
        return jsonify({
            'success': True,
            'from_inventory': from_inventory,
            'to_inventory': to_inventory,
            'transfer_log': transfer_log
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error transferring item: {str(e)}'
        }), 500 