"""Faction-related routes and endpoints."""

from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
from typing import Dict, Any
from app.auth.auth_utils import require_auth
from app.utils.social import process_faction_influence

faction_bp = Blueprint('faction', __name__)

@faction_bp.route('/create', methods=['POST'])
@require_auth
def create_faction() -> Dict[str, Any]:
    """
    Create a new faction.
    
    Returns:
        Dict containing faction data
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'alignment']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Generate faction ID
        faction_id = f"faction_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create faction data
        faction_data = {
            'faction_id': faction_id,
            'name': data['name'],
            'description': data['description'],
            'alignment': data['alignment'],
            'members': [],
            'allies': [],
            'enemies': [],
            'resources': data.get('resources', []),
            'influence': {},
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Save faction
        db.reference(f'/factions/{faction_id}').set(faction_data)
        
        return jsonify({
            'success': True,
            'faction': faction_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating faction: {str(e)}'
        }), 500

@faction_bp.route('/<faction_id>/join', methods=['POST'])
@require_auth
def join_faction(faction_id: str) -> Dict[str, Any]:
    """
    Add a character to a faction.
    
    Args:
        faction_id: ID of the faction
        
    Returns:
        Dict containing updated faction data
    """
    try:
        data = request.get_json()
        character_id = data.get('character_id')
        
        if not character_id:
            return jsonify({
                'success': False,
                'message': 'Missing character_id'
            }), 400
            
        # Get faction and character data
        faction_ref = db.reference(f'/factions/{faction_id}')
        character_ref = db.reference(f'/characters/{character_id}')
        
        faction = faction_ref.get()
        character = character_ref.get()
        
        if not faction or not character:
            return jsonify({
                'success': False,
                'message': 'Faction or character not found'
            }), 404
            
        # Add character to faction
        members = faction.get('members', [])
        if character_id not in members:
            members.append(character_id)
            faction_ref.update({'members': members})
            
        # Update character's faction
        character_ref.update({'faction_id': faction_id})
        
        return jsonify({
            'success': True,
            'faction': faction,
            'character': character
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error joining faction: {str(e)}'
        }), 500

@faction_bp.route('/<faction_id>/leave', methods=['POST'])
@require_auth
def leave_faction(faction_id: str) -> Dict[str, Any]:
    """
    Remove a character from a faction.
    
    Args:
        faction_id: ID of the faction
        
    Returns:
        Dict containing updated faction data
    """
    try:
        data = request.get_json()
        character_id = data.get('character_id')
        
        if not character_id:
            return jsonify({
                'success': False,
                'message': 'Missing character_id'
            }), 400
            
        # Get faction and character data
        faction_ref = db.reference(f'/factions/{faction_id}')
        character_ref = db.reference(f'/characters/{character_id}')
        
        faction = faction_ref.get()
        character = character_ref.get()
        
        if not faction or not character:
            return jsonify({
                'success': False,
                'message': 'Faction or character not found'
            }), 404
            
        # Remove character from faction
        members = faction.get('members', [])
        if character_id in members:
            members.remove(character_id)
            faction_ref.update({'members': members})
            
        # Remove faction from character
        character_ref.update({'faction_id': None})
        
        return jsonify({
            'success': True,
            'faction': faction,
            'character': character
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error leaving faction: {str(e)}'
        }), 500

@faction_bp.route('/<faction_id>/influence', methods=['POST'])
@require_auth
def update_influence(faction_id: str) -> Dict[str, Any]:
    """
    Update a faction's influence in a region.
    
    Args:
        faction_id: ID of the faction
        
    Returns:
        Dict containing influence results
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['region_id', 'action_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Process influence change
        result = process_faction_influence(
            faction_id,
            data['region_id'],
            data['action_type'],
            data.get('magnitude', 1)
        )
        
        if not result['success']:
            return jsonify(result), 400
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating influence: {str(e)}'
        }), 500 