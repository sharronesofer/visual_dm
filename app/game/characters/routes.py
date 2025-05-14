"""
Character routes for managing player characters.
"""

from flask import Blueprint, jsonify, request
from app.auth.auth_utils import require_auth
from firebase_admin import db
from datetime import datetime

character_bp = Blueprint('characters', __name__)

@character_bp.route('/', methods=['POST'])
@require_auth
def create_character():
    """Create a new character."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'race', 'class_name', 'background']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
    
    # Generate character ID
    character_id = f"char_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Add metadata
    data['created_at'] = datetime.utcnow().isoformat()
    data['character_id'] = character_id
    
    # Save to Firebase
    db.reference(f'/characters/{character_id}').set(data)
    
    return jsonify({
        'success': True,
        'character_id': character_id,
        'message': 'Character created successfully'
    }), 201

@character_bp.route('/<character_id>', methods=['GET'])
@require_auth
def get_character(character_id):
    """Get character details."""
    character = db.reference(f'/characters/{character_id}').get()
    
    if not character:
        return jsonify({
            'success': False,
            'error': 'Character not found'
        }), 404
    
    return jsonify({
        'success': True,
        'character': character
    })

@character_bp.route('/<character_id>', methods=['PUT'])
@require_auth
def update_character(character_id):
    """Update character details."""
    data = request.get_json()
    character_ref = db.reference(f'/characters/{character_id}')
    
    if not character_ref.get():
        return jsonify({
            'success': False,
            'error': 'Character not found'
        }), 404
    
    # Update timestamp
    data['updated_at'] = datetime.utcnow().isoformat()
    
    # Update character
    character_ref.update(data)
    
    return jsonify({
        'success': True,
        'message': 'Character updated successfully'
    })

@character_bp.route('/<character_id>', methods=['DELETE'])
@require_auth
def delete_character(character_id):
    """Delete a character."""
    character_ref = db.reference(f'/characters/{character_id}')
    
    if not character_ref.get():
        return jsonify({
            'success': False,
            'error': 'Character not found'
        }), 404
    
    # Delete character
    character_ref.delete()
    
    return jsonify({
        'success': True,
        'message': 'Character deleted successfully'
    }), 204

@character_bp.route('/list', methods=['GET'])
@require_auth
def list_characters():
    """List all characters."""
    characters = db.reference('/characters').get()
    
    if not characters:
        return jsonify({
            'success': True,
            'characters': []
        })
    
    return jsonify({
        'success': True,
        'characters': list(characters.values())
    }) 