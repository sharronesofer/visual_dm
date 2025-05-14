"""
Global state management routes.
"""

from flask import Blueprint, jsonify, request

global_state_bp = Blueprint('global_state', __name__)

@global_state_bp.route('/settings', methods=['GET'])
def get_global_settings():
    """Get global settings."""
    # For now, return empty settings
    return jsonify({})

@global_state_bp.route('/update', methods=['POST'])
def update_global_state():
    """Update global state."""
    data = request.get_json()
    # For now, just acknowledge the update
    return jsonify({"status": "ok", "updated": data}) 