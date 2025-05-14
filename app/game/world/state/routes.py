"""World state routes and endpoints."""

from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
from typing import Dict, Any, List
from app.auth.auth_utils import require_auth
from app.utils.world_tick_utils import process_world_tick
from flasgger import swag_from
from app.core.schemas.world_state_schemas import (
    WorldTickResponseSchema,
    WorldStateUpdateSchema,
    WorldStateResponseSchema,
    ErrorResponseSchema
)

world_state_bp = Blueprint('world_state', __name__)

@world_state_bp.route('/tick', methods=['POST'])
@require_auth
@swag_from({
    'tags': ['world'],
    'summary': 'Process a world tick',
    'description': 'Update the world state by processing one game tick',
    'responses': {
        '200': {
            'description': 'World tick processed successfully',
            'schema': WorldTickResponseSchema
        },
        '500': {
            'description': 'Server error',
            'schema': ErrorResponseSchema
        }
    },
    'security': [
        {
            'Bearer': []
        }
    ]
})
def tick_world() -> Dict[str, Any]:
    """
    Process a world tick.
    
    Returns:
        Dict containing tick results
    """
    try:
        # Get current world state
        world_state_ref = db.reference('/world_state')
        world_state = world_state_ref.get() or {}
        
        # Process world tick
        updated_state = process_world_tick(world_state)
        
        # Update world state
        world_state_ref.set(updated_state)
        
        return jsonify({
            'success': True,
            'world_state': updated_state,
            'tick_time': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing world tick: {str(e)}'
        }), 500

@world_state_bp.route('/current', methods=['GET'])
@require_auth
@swag_from({
    'tags': ['world'],
    'summary': 'Get current world state',
    'description': 'Retrieve the current state of the game world',
    'responses': {
        '200': {
            'description': 'World state retrieved successfully',
            'schema': WorldStateResponseSchema
        },
        '500': {
            'description': 'Server error',
            'schema': ErrorResponseSchema
        }
    },
    'security': [
        {
            'Bearer': []
        }
    ]
})
def get_world_state() -> Dict[str, Any]:
    """
    Get current world state.
    
    Returns:
        Dict containing world state
    """
    try:
        world_state = db.reference('/world_state').get() or {}
        return jsonify({
            'success': True,
            'world_state': world_state
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting world state: {str(e)}'
        }), 500

@world_state_bp.route('/update', methods=['PUT'])
@require_auth
@swag_from({
    'tags': ['world'],
    'summary': 'Update world state',
    'description': 'Update specific aspects of the game world state',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': WorldStateUpdateSchema
        }
    ],
    'responses': {
        '200': {
            'description': 'World state updated successfully',
            'schema': WorldStateResponseSchema
        },
        '400': {
            'description': 'Invalid request parameters',
            'schema': ErrorResponseSchema
        },
        '500': {
            'description': 'Server error',
            'schema': ErrorResponseSchema
        }
    },
    'security': [
        {
            'Bearer': []
        }
    ]
})
def update_world_state() -> Dict[str, Any]:
    """
    Update world state.
    
    Returns:
        Dict containing updated world state
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
            
        # Get current state
        world_state_ref = db.reference('/world_state')
        current_state = world_state_ref.get() or {}
        
        # Update state
        current_state.update(data)
        world_state_ref.set(current_state)
        
        return jsonify({
            'success': True,
            'world_state': current_state
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating world state: {str(e)}'
        }), 500

@world_state_bp.route('/reset', methods=['POST'])
@require_auth
def reset_world_state() -> Dict[str, Any]:
    """
    Reset world state to default values.
    
    Returns:
        Dict containing reset world state
    """
    try:
        default_state = {
            'time': datetime.utcnow().isoformat(),
            'weather': {
                'current': 'clear',
                'temperature': 20
            },
            'events': [],
            'active_effects': [],
            'last_tick': datetime.utcnow().isoformat()
        }
        
        db.reference('/world_state').set(default_state)
        
        return jsonify({
            'success': True,
            'world_state': default_state
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error resetting world state: {str(e)}'
        }), 500 