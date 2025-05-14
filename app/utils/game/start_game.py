"""Game start utilities and routes."""

from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
from typing import Dict, Any
from flasgger import swag_from
from app.core.schemas.game_routes_schemas import (
    StartGameRequestSchema,
    StartGameResponseSchema,
    EndGameRequestSchema,
    EndGameResponseSchema,
    ErrorResponseSchema
)

start_game_bp = Blueprint('start_game', __name__)

@start_game_bp.route('/start', methods=['POST'])
@swag_from({
    'tags': ['game'],
    'summary': 'Start a new game session',
    'description': 'Initialize a new game session for a character',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': StartGameRequestSchema
        }
    ],
    'responses': {
        '200': {
            'description': 'Game session started successfully',
            'schema': StartGameResponseSchema
        },
        '400': {
            'description': 'Invalid request parameters',
            'schema': ErrorResponseSchema
        },
        '500': {
            'description': 'Server error',
            'schema': ErrorResponseSchema
        }
    }
})
def start_game() -> Dict[str, Any]:
    """
    Initialize a new game session.
    
    Returns:
        Dict containing game session info
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        character_id = data.get('character_id')
        
        if not user_id or not character_id:
            return jsonify({
                'success': False,
                'message': 'Missing user_id or character_id'
            }), 400
            
        # Create game session
        session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        session_data = {
            'user_id': user_id,
            'character_id': character_id,
            'start_time': datetime.utcnow().isoformat(),
            'status': 'active',
            'current_location': 'starting_town',
            'quest_log': [],
            'inventory': [],
            'stats': {
                'playtime': 0,
                'quests_completed': 0,
                'battles_won': 0
            }
        }
        
        # Save session
        db.reference(f'/game_sessions/{session_id}').set(session_data)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'session_data': session_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting game: {str(e)}'
        }), 500

@start_game_bp.route('/end', methods=['POST'])
@swag_from({
    'tags': ['game'],
    'summary': 'End a game session',
    'description': 'End an active game session and save final state',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': EndGameRequestSchema
        }
    ],
    'responses': {
        '200': {
            'description': 'Game session ended successfully',
            'schema': EndGameResponseSchema
        },
        '400': {
            'description': 'Invalid request parameters',
            'schema': ErrorResponseSchema
        },
        '404': {
            'description': 'Session not found',
            'schema': ErrorResponseSchema
        },
        '500': {
            'description': 'Server error',
            'schema': ErrorResponseSchema
        }
    }
})
def end_game() -> Dict[str, Any]:
    """
    End a game session.
    
    Returns:
        Dict containing session summary
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'message': 'Missing session_id'
            }), 400
            
        # Get session data
        session_ref = db.reference(f'/game_sessions/{session_id}')
        session_data = session_ref.get()
        
        if not session_data:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
            
        # Update session status
        end_time = datetime.utcnow()
        session_data.update({
            'status': 'completed',
            'end_time': end_time.isoformat(),
            'duration': (end_time - datetime.fromisoformat(session_data['start_time'])).total_seconds()
        })
        
        # Save final state
        session_ref.set(session_data)
        
        return jsonify({
            'success': True,
            'session_summary': session_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error ending game: {str(e)}'
        }), 500 