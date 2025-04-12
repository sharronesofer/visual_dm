# menu.py

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from firebase_admin import db
import logging

menu_bp = Blueprint("menu", __name__)
__all__ = ["menu_bp"]

# ----------------------------
# Character Creation Flow
# ----------------------------

CREATION_STEPS = [
    "Stats",
    "Race",
    "Skills",
    "Feats",
    "Name",
    "Background",
    "Kit",
    "Summary"
]

@menu_bp.route('/character_creator/start', methods=['GET'])
def start_character_creation():
    return jsonify({"steps": CREATION_STEPS})

@menu_bp.route('/character_creator/save', methods=['POST'])
def save_character():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No character data provided"}), 400

    character_id = str(uuid.uuid4())
    data["character_id"] = character_id

    db.reference(f"/players/{character_id}").set(data)

    return jsonify({"message": "Character saved successfully", "character_id": character_id}), 200

# ----------------------------
# Pause Menu Routes
# ----------------------------

@menu_bp.route('/menu/character_sheet/<character_id>', methods=['GET'])
def get_character_sheet(character_id):
    character = db.reference(f"/players/{character_id}").get()
    if not character:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404
    return jsonify(character), 200

@menu_bp.route('/menu/inventory/<character_id>', methods=['GET'])
def get_inventory(character_id):
    character = db.reference(f"/players/{character_id}").get()
    if not character:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404

    return jsonify({
        "inventory": character.get("inventory", []),
        "gold": character.get("gold", 0)
    }), 200

@menu_bp.route('/menu/party_view/<character_id>', methods=['GET'])
def get_party_view(character_id):
    character = db.reference(f"/players/{character_id}").get()
    if not character:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404

    party_id = character.get("party_id")
    if not party_id:
        return jsonify({"error": "Character not part of any party."}), 404

    party = db.reference(f"/parties/{party_id}").get()
    if not party:
        return jsonify({"error": "Party data not found."}), 404

    party_members = []
    for member_id in party.get("members", []):
        npc_data = db.reference(f"/npcs/{member_id}").get()
        if npc_data:
            party_members.append(npc_data)

    return jsonify({"party": party, "members": party_members}), 200

@menu_bp.route('/menu/world_map/<character_id>', methods=['GET'])
def get_world_map(character_id):
    character = db.reference(f"/players/{character_id}").get()
    if not character:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404

    known_tiles = character.get("known_tiles", [])
    return jsonify({"known_tiles": known_tiles}), 200

@menu_bp.route("/menu/options", methods=["GET"])
def get_game_options():
    return jsonify({
        "audio": {"volume": 70},
        "graphics": {"resolution": "1280x720", "fullscreen": False},
        "input": {"move_up": "W", "move_down": "S", "confirm": "Enter"},
        "model": {"npc_model": "gpt-4o-mini", "dm_model": "gpt-4o"}
    })

# ----------------------------
# Optional: Local Testing
# ----------------------------

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(menu_bp)
    app.run(debug=True)
