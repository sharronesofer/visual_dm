"""Memory-related routes and endpoints."""

from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
from typing import Dict, Any
from app.auth.auth_utils import require_auth

memory_bp = Blueprint('memory', __name__)

@memory_bp.route('/add', methods=['POST'])
@require_auth
def add_memory() -> Dict[str, Any]:
    """
    Add a new memory for a character.
    
    Returns:
        Dict containing memory data
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['character_id', 'title', 'description', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Generate memory ID
        memory_id = f"memory_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create memory data
        memory_data = {
            'memory_id': memory_id,
            'character_id': data['character_id'],
            'title': data['title'],
            'description': data['description'],
            'type': data['type'],
            'timestamp': datetime.utcnow().isoformat(),
            'importance': data.get('importance', 'normal'),
            'tags': data.get('tags', []),
            'related_characters': data.get('related_characters', []),
            'location': data.get('location'),
            'emotions': data.get('emotions', {})
        }
        
        # Save memory
        db.reference(f'/memories/{memory_id}').set(memory_data)
        
        # Update character's memories list
        character_ref = db.reference(f'/characters/{data["character_id"]}')
        character = character_ref.get()
        if character:
            memories = character.get('memories', [])
            memories.append(memory_id)
            character_ref.update({'memories': memories})
        
        return jsonify({
            'success': True,
            'memory': memory_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding memory: {str(e)}'
        }), 500

@memory_bp.route('/<character_id>/list', methods=['GET'])
@require_auth
def list_memories(character_id: str) -> Dict[str, Any]:
    """
    List all memories for a character.
    
    Args:
        character_id: ID of the character
        
    Returns:
        Dict containing list of memories
    """
    try:
        # Get character's memories
        character_ref = db.reference(f'/characters/{character_id}')
        character = character_ref.get()
        
        if not character:
            return jsonify({
                'success': False,
                'message': 'Character not found'
            }), 404
            
        memories = character.get('memories', [])
        memory_data = []
        
        # Fetch each memory's details
        for memory_id in memories:
            memory_ref = db.reference(f'/memories/{memory_id}')
            memory = memory_ref.get()
            if memory:
                memory_data.append(memory)
        
        return jsonify({
            'success': True,
            'memories': memory_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listing memories: {str(e)}'
        }), 500

@memory_bp.route('/<memory_id>/update', methods=['PUT'])
@require_auth
def update_memory(memory_id: str) -> Dict[str, Any]:
    """
    Update an existing memory.
    
    Args:
        memory_id: ID of the memory to update
        
    Returns:
        Dict containing updated memory data
    """
    try:
        data = request.get_json()
        
        # Get existing memory
        memory_ref = db.reference(f'/memories/{memory_id}')
        memory = memory_ref.get()
        
        if not memory:
            return jsonify({
                'success': False,
                'message': 'Memory not found'
            }), 404
            
        # Update allowed fields
        allowed_fields = [
            'title', 'description', 'importance',
            'tags', 'related_characters', 'location',
            'emotions'
        ]
        
        for field in allowed_fields:
            if field in data:
                memory[field] = data[field]
                
        # Save updated memory
        memory_ref.set(memory)
        
        return jsonify({
            'success': True,
            'memory': memory
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating memory: {str(e)}'
        }), 500

@memory_bp.route('/<memory_id>/delete', methods=['DELETE'])
@require_auth
def delete_memory(memory_id: str) -> Dict[str, Any]:
    """
    Delete a memory.
    
    Args:
        memory_id: ID of the memory to delete
        
    Returns:
        Dict containing result
    """
    try:
        # Get memory data
        memory_ref = db.reference(f'/memories/{memory_id}')
        memory = memory_ref.get()
        
        if not memory:
            return jsonify({
                'success': False,
                'message': 'Memory not found'
            }), 404
            
        # Remove memory from character's list
        character_ref = db.reference(f'/characters/{memory["character_id"]}')
        character = character_ref.get()
        if character:
            memories = character.get('memories', [])
            if memory_id in memories:
                memories.remove(memory_id)
                character_ref.update({'memories': memories})
                
        # Delete memory
        memory_ref.delete()
        
        return jsonify({
            'success': True,
            'message': 'Memory deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting memory: {str(e)}'
        }), 500 