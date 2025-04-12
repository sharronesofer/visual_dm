from flask import Blueprint, request, jsonify
from firebase_admin import db
from character_utils import complete_character
import random
import uuid
from datetime import datetime

player_bp = Blueprint("player_bp", __name__)
__all__ = ["player_bp"]

# -------------------------
# Utility Functions
# -------------------------

def save_partial_character_data(player_id, field, value):
    temp_ref = db.reference(f"/temp_characters/{player_id}")
    data = temp_ref.get() or {}
    data[field] = value
    temp_ref.set(data)

def finalize_character_creation(player_id):
    temp_ref = db.reference(f"/temp_characters/{player_id}")
    temp_data = temp_ref.get()
    if not temp_data:
        return {"error": "No partial data found."}, 404

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
        "languages": ["Common"]
    }

    if "ability_scores" in temp_data:
        for abbr, score_info in temp_data["ability_scores"].items():
            core[abbr] = score_info["total"]

    db.reference(f"/players/{character_id}").set(complete_character(core))
    temp_ref.delete()

    return {
        "message": "Character creation finalized",
        "character_id": character_id,
        "player_id": player_id
    }, 200

def generate_ability_scores():
    abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    result = {}
    for ability in abilities:
        rolls = [random.randint(1, 6) for _ in range(4)]
        sorted_rolls = sorted(rolls)
        total = sum(sorted_rolls[1:])
        result[ability] = {
            "total": total,
            "rolls": rolls
        }
    return result

def parse_coords(loc):
    try:
        return tuple(map(int, loc.split("_")))
    except:
        return None, None

def perform_skill_check(character, skill, dc=12):
    SKILL_TO_ABILITY = {
        "stealth": "DEX",
        "pickpocket": "DEX",
        "intimidate": "CHA",
        "diplomacy": "CHA",
        "persuasion": "CHA",
        "deception": "CHA",
        "perception": "WIS",
        "insight": "WIS",
        "arcana": "INT"
    }
    ability = SKILL_TO_ABILITY.get(skill.lower(), "INT")
    modifier = (character.get(ability, 10) - 10) // 2
    if skill.lower() in [s.lower() for s in character.get("skills", [])]:
        modifier += 2
    roll = random.randint(1, 20)
    total = roll + modifier
    return {
        "skill": skill,
        "roll": roll,
        "modifier": modifier,
        "total": total,
        "success": total >= dc,
        "dc": dc
    }

# -------------------------
# Routes
# -------------------------

@player_bp.route('/run_command_parser', methods=['POST'])
def route_run_command_parser():
    from command_parser import parse_action_command
    data = request.json
    text = data.get("text", "")
    context = data.get("context", {})
    result = parse_action_command(text, context)
    return jsonify(result)

@player_bp.route('/ability_scores/4d6', methods=['GET'])
def roll_ability_scores():
    results = []
    for _ in range(6):
        rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
        total = 19 if rolls == [6, 6, 6, 6] else sum(rolls[:3])
        results.append({"rolls": rolls, "score": total})
    return jsonify({"method": "4d6-drop-lowest", "results": results})

@player_bp.route('/update_known_tiles/<character_id>', methods=['PATCH'])
def update_known_tiles(character_id):
    data = request.get_json(force=True)
    ref = db.reference(f"/players/{character_id}")
    existing = ref.get()
    if not existing:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404

    allowed_fields = ["known_tiles", "location"]
    for field in allowed_fields:
        if field in data:
            existing[field] = data[field]

    ref.set(existing)
    return jsonify({
        "message": "Character data patched successfully.",
        "updated_fields": {field: existing[field] for field in allowed_fields if field in data}
    }), 200

@player_bp.route('/players/<character_id>', methods=['GET'])
def get_character(character_id):
    ref = db.reference(f"/players/{character_id}")
    existing = ref.get()
    if not existing:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404
    return jsonify(existing), 200

@player_bp.route('/players/<character_id>', methods=['PATCH'])
def patch_character(character_id):
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    ref = db.reference(f"/players/{character_id}")
    existing = ref.get()
    if not existing:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404

    existing.update(data)
    ref.set(existing)
    return jsonify(existing), 200

@player_bp.route('/players', methods=['GET'])
def list_players():
    ref = db.reference("/players")
    players = ref.get() or {}
    return jsonify(players)

@player_bp.route('/move_player', methods=['POST'])
def move_player():
    data = request.get_json(force=True)
    character_id = data.get("character_id")
    new_location = data.get("new_location")
    if not character_id or not new_location:
        return jsonify({"error": "character_id and new_location are required"}), 400

    character_ref = db.reference(f'/players/{character_id}')
    character_state = character_ref.get() or {}
    prev_location = character_state.get("location", "0_0")

    x1, y1 = parse_coords(prev_location)
    x2, y2 = parse_coords(new_location)
    if None in [x1, y1, x2, y2]:
        return jsonify({"error": "Invalid coordinate format. Expected 'x_y'."}), 400

    path = []
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    for i in range(1, steps + 1):
        x = x1 + round(i * dx / steps)
        y = y1 + round(i * dy / steps)
        path.append(f"{x}_{y}")

    character_state["location"] = new_location
    character_state["known_tiles"] = list(set(character_state.get("known_tiles", []) + path))

    updated_character = complete_character(character_state)
    character_ref.set(updated_character)

    return jsonify({
        "message": f"Character {character_id} moved successfully.",
        "location": new_location,
        "path": path,
        "character_state": updated_character
    }), 200

@player_bp.route('/test_known_tiles/<character_id>', methods=['POST'])
def test_known_tiles(character_id):
    return jsonify({
        "message": "Route test successful.",
        "character_id": character_id
    }), 200

@player_bp.route('/debug_firebase_connection', methods=['GET'])
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
