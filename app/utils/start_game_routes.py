"""
Routes for starting and initializing the game.
"""

from flask import Blueprint, jsonify, request
from app.auth.auth_utils import require_auth
from firebase_admin import db
from datetime import datetime

start_game_bp = Blueprint('start_game', __name__)

@start_game_bp.route('/initialize', methods=['POST'])
@require_auth
def initialize_game():
    """
    Initialize a new game session.
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Missing user_id'
            }), 400
            
        # Create initial game state
        game_state = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat(),
            'status': 'active',
            'settings': {
                'difficulty': 'normal',
                'permadeath': False,
                'tutorial': True
            }
        }
        
        # Save to Firebase
        db.reference(f'/game_sessions/{user_id}').set(game_state)
        
        return jsonify({
            'success': True,
            'message': 'Game initialized successfully',
            'game_state': game_state
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error initializing game: {str(e)}'
        }), 500

@start_game_bp.route('/status', methods=['GET'])
@require_auth
def get_game_status():
    """
    Get the current game status.
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Missing user_id'
            }), 400
            
        # Get game state from Firebase
        game_state = db.reference(f'/game_sessions/{user_id}').get()
        
        if not game_state:
            return jsonify({
                'success': False,
                'message': 'No active game session found'
            }), 404
            
        return jsonify({
            'success': True,
            'game_state': game_state
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting game status: {str(e)}'
        }), 500

@start_game_bp.route('/end', methods=['POST'])
@require_auth
def end_game():
    """
    End a game session.
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Missing user_id'
            }), 400
            
        # Update game state
        game_ref = db.reference(f'/game_sessions/{user_id}')
        game_state = game_ref.get()
        
        if not game_state:
            return jsonify({
                'success': False,
                'message': 'No active game session found'
            }), 404
            
        game_state['status'] = 'ended'
        game_state['ended_at'] = datetime.utcnow().isoformat()
        game_ref.set(game_state)
        
        return jsonify({
            'success': True,
            'message': 'Game ended successfully',
            'game_state': game_state
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error ending game: {str(e)}'
        }), 500 