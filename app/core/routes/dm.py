"""
DM-related routes for handling DM responses and interactions.
"""

from flask import Blueprint, jsonify, request

dm_bp = Blueprint('dm', __name__)

@dm_bp.route('/response', methods=['POST'])
def dm_response():
    """Handle DM response generation."""
    data = request.get_json()
    mode = data.get('mode')
    
    if mode == 'background_prompt':
        # Generate a simple background for now
        return jsonify({
            "reply": "You grew up in a small village on the outskirts of civilization. From an early age, you showed promise in your chosen path, training diligently to master your skills. Now you seek adventure and glory in the wider world."
        })
    
    return jsonify({"reply": "The DM ponders your request..."}) 