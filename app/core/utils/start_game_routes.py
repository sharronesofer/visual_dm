# start_game_routes.py

from flask import Blueprint, request, jsonify
from firebase_admin import db

start_game_bp = Blueprint("start_game", __name__)

@start_game_bp.route('/start_game/<character_id>', methods=['POST'])
def start_game(character_id):
    """
    Initializes the game for an existing character.
    Loads the region, starting position, and tiles.
    """
    try:
        char_ref = db.reference(f"/players/{character_id}")
        character = char_ref.get()
        if not character:
            return jsonify({"error": "Character not found"}), 404

        region_id = character.get("region_id")
        start_pos = character.get("position", {"x": 0, "y": 0})

        # Load region tiles
        region_tiles = db.reference(f"/region_maps/{region_id}/tiles").get() or {}

        tile_key = f"{start_pos['x']}_{start_pos['y']}"
        starting_tile = region_tiles.get(tile_key, {})

        return jsonify({
            "character": character,
            "region_tiles": region_tiles,
            "starting_tile_info": starting_tile
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
