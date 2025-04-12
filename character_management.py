# character_management.py

from flask import Blueprint, request, jsonify
from firebase_admin import db
import uuid
from datetime import datetime
import random
from character_utils import complete_character

character_bp = Blueprint("character_bp", __name__)
__all__ = ["character_bp"]

# ------------------------------------
# Generate Ability Scores (GET)
# ------------------------------------

@character_bp.route('/generate_ability_scores', methods=['GET'])
def generate_ability_scores():
    abilities = {}
    for ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        rolls = [random.randint(1, 6) for _ in range(4)]
        sorted_rolls = sorted(rolls)
        total = sum(sorted_rolls[1:])
        abilities[ability] = {
            "total": total,
            "rolls": rolls
        }
    return jsonify(abilities), 200

# ------------------------------------
# Save Partial Character Data (POST)
# ------------------------------------

@character_bp.route('/save_partial_character_data', methods=['POST'])
def save_partial_character_data():
    data = request.get_json(force=True)
    player_id = data.get("player_id")
    field = data.get("field")
    value = data.get("value")

    if not player_id or not field or value is None:
        return jsonify({"error": "player_id, field, and value are required"}), 400

    temp_ref = db.reference(f"/temp_characters/{player_id}")
    partial_data = temp_ref.get() or {}
    partial_data[field] = value
    temp_ref.set(partial_data)

    return jsonify({"message": f"Data saved for field '{field}'"}), 200

# ------------------------------------
# Finalize Character Creation (POST)
# ------------------------------------

@character_bp.route('/finalize_character_creation', methods=['POST'])
def finalize_character_creation():
    data = request.get_json(force=True)
    player_id = data.get("player_id")

    if not player_id:
        return jsonify({"error": "player_id is required"}), 400

    temp_ref = db.reference(f"/temp_characters/{player_id}")
    temp_data = temp_ref.get()

    if not temp_data:
        return jsonify({"error": "No partial data found."}), 404

    character_id = str(uuid.uuid4())

    core = {
        "character_id": character_id,
        "player_id": player_id,
        "character_name": temp_data.get("name", "Unnamed"),
        "characterType": "Player Character",
        "race": temp_data.get("race", "Human"),
        "class": temp_data.get("class", "Fighter"),
        "region_of_origin": temp_data.get("region_of_origin", "DefaultRegion"),
        "location": "0_0",
        "region_id": "default_region",
        "XP": 0,
        "level": 1,
        "alignment": "Neutral",
        "inventory": [],
        "equipment": [],
        "languages": ["Common"],
    }

    if "ability_scores" in temp_data:
        for abbr, score_info in temp_data["ability_scores"].items():
            core[abbr] = score_info["total"]

    players_ref = db.reference(f"/players/{character_id}")
    players_ref.set(complete_character(core))

    temp_ref.delete()

    return jsonify({
        "message": "Character creation finalized",
        "character_id": character_id,
        "player_id": player_id
    }), 200

# ------------------------------------
# Character Selector by Player ID (GET)
# ------------------------------------

@character_bp.route('/character_selector/<player_id>', methods=['GET'])
def character_selector(player_id):
    ref = db.reference("/players")
    players = ref.get() or {}
    player_characters = {cid: pdata for cid, pdata in players.items() if pdata.get("player_id") == player_id}
    return jsonify(player_characters), 200

# ------------------------------------
# Firebase Connection Debug (GET)
# ------------------------------------

@character_bp.route('/debug_firebase_connection', methods=['GET'])
def debug_firebase_connection():
    try:
        root_ref = db.reference('/')
        data = root_ref.get()
        return jsonify({
            "success": True,
            "root_keys": list(data.keys()) if data else [],
            "database_url": db.reference().path
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
