"""Social interaction routes for Visual DM."""

from flask import Blueprint, request, jsonify, current_app
from google.cloud import firestore
from app.utils.auth import login_required
from app.utils.exceptions import InvalidUsage
from app.utils.logging import log_action
from datetime import datetime

social_bp = Blueprint('social', __name__)

def get_firestore():
    """Get the Firestore client from app extensions."""
    if 'firestore' not in current_app.extensions:
        if current_app.config.get('TESTING', False):
            from unittest.mock import MagicMock
            return MagicMock()
        raise RuntimeError("Firestore client not initialized")
    return current_app.extensions['firestore']

@social_bp.route('/interact', methods=['POST'])
@login_required
def interact():
    """Handle social interaction between characters."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['character_id', 'target_id', 'interaction_type']
    for field in required_fields:
        if field not in data:
            raise InvalidUsage(f"Missing required field: {field}")
    
    character_id = data['character_id']
    target_id = data['target_id']
    interaction_type = data['interaction_type']
    
    try:
        db = get_firestore()
        
        # Get character and target data
        character_ref = db.collection('characters').document(character_id)
        target_ref = db.collection('characters').document(target_id)
        
        character = character_ref.get()
        target = target_ref.get()
        
        if not character.exists:
            raise InvalidUsage(f"Character {character_id} not found")
        if not target.exists:
            raise InvalidUsage(f"Target character {target_id} not found")
        
        # Process interaction
        interaction_data = {
            'type': interaction_type,
            'timestamp': datetime.utcnow().isoformat(),
            'character_id': character_id,
            'target_id': target_id
        }
        
        # Store interaction in both characters' histories
        db.collection('social_interactions').add(interaction_data)
        
        # Update relationship scores
        relationship_ref = db.collection('relationships').document(f"{character_id}_{target_id}")
        if relationship_ref.get().exists:
            relationship_ref.update({
                'last_interaction': datetime.utcnow().isoformat(),
                'interaction_count': firestore.Increment(1)
            })
        else:
            relationship_ref.set({
                'character_id': character_id,
                'target_id': target_id,
                'created_at': datetime.utcnow().isoformat(),
                'last_interaction': datetime.utcnow().isoformat(),
                'interaction_count': 1,
                'relationship_level': 1
            })
        
        log_action('social_interaction', interaction_data)
        
        return jsonify({
            'status': 'success',
            'message': f"Interaction {interaction_type} processed successfully"
        }), 200
        
    except Exception as e:
        log_action('social_interaction_error', {'error': str(e), **data})
        raise InvalidUsage(f"Failed to process interaction: {str(e)}")

@social_bp.route('/relationships/<character_id>', methods=['GET'])
@login_required
def get_relationships(character_id):
    """Get all relationships for a character."""
    try:
        db = get_firestore()
        
        # Get character's relationships
        relationships = db.collection('relationships')\
            .where('character_id', '==', character_id)\
            .stream()
        
        result = []
        for rel in relationships:
            rel_data = rel.to_dict()
            # Get target character info
            target = db.collection('characters').document(rel_data['target_id']).get()
            if target.exists:
                target_data = target.to_dict()
                rel_data['target_name'] = target_data.get('name', 'Unknown')
                rel_data['target_type'] = target_data.get('type', 'Unknown')
            result.append(rel_data)
        
        return jsonify({
            'status': 'success',
            'relationships': result
        }), 200
        
    except Exception as e:
        log_action('get_relationships_error', {'error': str(e), 'character_id': character_id})
        raise InvalidUsage(f"Failed to get relationships: {str(e)}")

@social_bp.route('/party/create', methods=['POST'])
@login_required
def create_party():
    """Create a new party."""
    data = request.get_json()
    
    # Validate required fields
    if 'name' not in data or 'leader_id' not in data:
        raise InvalidUsage("Missing required fields: name and leader_id")
    
    try:
        db = get_firestore()
        
        # Check if leader exists
        leader = db.collection('characters').document(data['leader_id']).get()
        if not leader.exists:
            raise InvalidUsage(f"Leader character {data['leader_id']} not found")
        
        # Create party
        party_data = {
            'name': data['name'],
            'leader_id': data['leader_id'],
            'members': [data['leader_id']],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add optional members if provided
        if 'members' in data and isinstance(data['members'], list):
            # Verify all members exist
            for member_id in data['members']:
                member = db.collection('characters').document(member_id).get()
                if not member.exists:
                    raise InvalidUsage(f"Member character {member_id} not found")
            party_data['members'].extend(data['members'])
        
        # Create party document
        party_ref = db.collection('parties').add(party_data)
        
        log_action('create_party', party_data)
        
        return jsonify({
            'status': 'success',
            'party_id': party_ref[1].id,
            'message': "Party created successfully"
        }), 201
        
    except Exception as e:
        log_action('create_party_error', {'error': str(e), **data})
        raise InvalidUsage(f"Failed to create party: {str(e)}")

@social_bp.route('/party/<party_id>/join', methods=['POST'])
@login_required
def join_party(party_id):
    """Join an existing party."""
    data = request.get_json()
    
    if 'character_id' not in data:
        raise InvalidUsage("Missing required field: character_id")
    
    try:
        db = get_firestore()
        
        # Get party and character
        party_ref = db.collection('parties').document(party_id)
        character_ref = db.collection('characters').document(data['character_id'])
        
        party = party_ref.get()
        character = character_ref.get()
        
        if not party.exists:
            raise InvalidUsage(f"Party {party_id} not found")
        if not character.exists:
            raise InvalidUsage(f"Character {data['character_id']} not found")
        
        party_data = party.to_dict()
        
        # Check if character is already in party
        if data['character_id'] in party_data['members']:
            raise InvalidUsage("Character is already in this party")
        
        # Check party size limit
        if len(party_data['members']) >= current_app.config['MAX_PARTY_SIZE']:
            raise InvalidUsage("Party is already at maximum size")
        
        # Add character to party
        party_ref.update({
            'members': firestore.ArrayUnion([data['character_id']]),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        log_action('join_party', {
            'party_id': party_id,
            'character_id': data['character_id']
        })
        
        return jsonify({
            'status': 'success',
            'message': "Successfully joined party"
        }), 200
        
    except Exception as e:
        log_action('join_party_error', {
            'error': str(e),
            'party_id': party_id,
            **data
        })
        raise InvalidUsage(f"Failed to join party: {str(e)}") 