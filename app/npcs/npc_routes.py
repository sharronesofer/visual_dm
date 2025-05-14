"""
NPC-related API routes.
"""

from flask import Blueprint, jsonify, request
from typing import Dict, List, Optional
from app.core.utils.error_utils import ValidationError, NotFoundError, DatabaseError
from app.models.npc import NPC
from app.npcs.npc_utils import (
    create_npc,
    get_npc,
    update_npc,
    delete_npc,
    get_npcs_by_location,
    update_relationship,
    add_rumor,
    should_abandon,
    get_relationship_tier,
    sync_event_beliefs
)

npc_bp = Blueprint('npc', __name__)

@npc_bp.route('/', methods=['POST'])
def create_npc_route():
    """Create a new NPC."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        npc = create_npc(data)
        return jsonify(npc.dict()), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@npc_bp.route('/<npc_id>', methods=['GET'])
def get_npc_route(npc_id: str):
    """Get an NPC by ID."""
    try:
        npc = get_npc(npc_id)
        return jsonify(npc.dict()), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@npc_bp.route('/<npc_id>', methods=['PUT'])
def update_npc_route(npc_id: str):
    """Update an NPC."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        npc = update_npc(npc_id, data)
        return jsonify(npc.dict()), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@npc_bp.route('/<npc_id>', methods=['DELETE'])
def delete_npc_route(npc_id: str):
    """Delete an NPC."""
    try:
        delete_npc(npc_id)
        return jsonify({'message': 'NPC deleted'}), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@npc_bp.route('/location/<location_id>', methods=['GET'])
def get_npcs_by_location_route(location_id: str):
    """Get all NPCs at a location."""
    try:
        npcs = get_npcs_by_location(location_id)
        return jsonify([npc.dict() for npc in npcs]), 200
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@npc_bp.route('/<npc_id>/relationships/<target_id>', methods=['POST'])
def update_relationship_route(npc_id: str, target_id: str):
    """Update an NPC's relationship with another entity."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        change = data.get('change', 0)
        if not isinstance(change, int):
            raise ValidationError("Change must be an integer")
        update_relationship(npc_id, target_id, change)
        return jsonify({'message': 'Relationship updated'}), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@npc_bp.route('/<npc_id>/rumors', methods=['POST'])
def add_rumor_route(npc_id: str):
    """Add or update a rumor for an NPC."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        rumor_id = data.get('rumor_id')
        confidence = data.get('confidence', 0.5)
        if not rumor_id:
            raise ValidationError("Rumor ID is required")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise ValidationError("Confidence must be a number between 0 and 1")
        add_rumor(npc_id, rumor_id, confidence)
        return jsonify({'message': 'Rumor added'}), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@npc_bp.route('/<npc_id>/should_abandon', methods=['GET'])
def should_abandon_route(npc_id: str):
    """Check if an NPC should abandon their faction."""
    try:
        result = should_abandon(npc_id)
        return jsonify({'should_abandon': result}), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@npc_bp.route('/<npc_id>/relationship_tier/<target_id>', methods=['GET'])
def get_relationship_tier_route(npc_id: str, target_id: str):
    """Get the relationship tier between an NPC and another entity."""
    try:
        tier = get_relationship_tier(npc_id, target_id)
        return jsonify({'tier': tier}), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@npc_bp.route('/<npc_id>/event_beliefs', methods=['POST'])
def sync_event_beliefs_route(npc_id: str):
    """Sync an NPC's beliefs about an event."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        event_id = data.get('event_id')
        confidence = data.get('confidence', 0.5)
        if not event_id:
            raise ValidationError("Event ID is required")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise ValidationError("Confidence must be a number between 0 and 1")
        sync_event_beliefs(npc_id, event_id, confidence)
        return jsonify({'message': 'Event beliefs synced'}), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 