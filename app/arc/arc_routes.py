"""
Arc-related API routes.
"""

from flask import Blueprint, jsonify, request
from .arc_utils import (
    generate_arc_stages,
    create_arc,
    update_arc_progress,
    load_arc_from_firebase,
    save_arc_to_firebase
)
from .arc_models import PlayerArc

arc_bp = Blueprint('arc', __name__)

@arc_bp.route('/<character_id>', methods=['POST'])
def create_character_arc(character_id):
    """Create a new character arc."""
    try:
        data = request.get_json()
        theme = data.get('theme')
        arc = create_arc(character_id, theme)
        if not save_arc_to_firebase(arc):
            return jsonify({"error": "Failed to save arc"}), 500
        return jsonify(arc.dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@arc_bp.route('/<arc_id>', methods=['GET'])
def get_arc(arc_id):
    """Get arc details."""
    arc = load_arc_from_firebase(arc_id)
    if not arc:
        return jsonify({"error": "Arc not found"}), 404
    return jsonify(arc.dict())

@arc_bp.route('/<arc_id>/progress', methods=['PUT'])
def update_arc(arc_id):
    """Update arc progress."""
    try:
        data = request.get_json()
        stage_id = data.get('stage_id')
        success = update_arc_progress(arc_id, stage_id)
        if not success:
            return jsonify({"error": "Failed to update arc progress"}), 500
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@arc_bp.route('/character/<character_id>', methods=['GET'])
def get_character_arcs(character_id):
    """Get all arcs for a character."""
    # TODO: Implement character arc retrieval from storage
    return jsonify({"error": "Not implemented"}), 501 