"""
Routes for managing world ticks and time progression.
"""

from flask import Blueprint, jsonify, request
from app.utils.world_tick_utils import tick_world_day
from app.world_state.world_state_utils import process_world_tick, cleanup_old_events
from app.auth.auth_utils import require_auth

world_tick_bp = Blueprint('world_tick', __name__)

@world_tick_bp.route('/manual', methods=['POST'])
@require_auth
def manual_world_tick():
    """
    Manually trigger a world tick.
    """
    try:
        # Execute world tick
        tick_world_day()
        
        # Process world state changes
        process_world_tick()
        
        # Clean up old events
        cleanup_old_events()
        
        return jsonify({
            'success': True,
            'message': 'World tick executed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error during world tick: {str(e)}'
        }), 500

@world_tick_bp.route('/status', methods=['GET'])
@require_auth
def get_tick_status():
    """
    Get the current world tick status.
    """
    try:
        # TODO: Implement status check logic
        return jsonify({
            'success': True,
            'last_tick': 'Not implemented',
            'next_tick': 'Not implemented'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting tick status: {str(e)}'
        }), 500 