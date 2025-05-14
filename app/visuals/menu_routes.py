#This module defines the menu interface and character sheet UI endpoints, supporting:
#Character creation steps
#Player save/load
#Party view
#Known world map
#UI/game options
#It supports the character, party, map, ui, and player state systems.


from flask import Blueprint, request, jsonify
from uuid import uuid4
from firebase_admin import db
from app.rules.character_gen_rules_utils import validate_character_creation
import uuid
import requests
menu_bp = Blueprint("menu", __name__)

CREATION_STEPS = [
    "attributes",
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
    return jsonify({"steps": CREATION_STEPS}), 200


@menu_bp.route("/save_character", methods=["POST"])
def save_character():
    character = request.json
    if not character:
        return jsonify({"error": "No character data provided"}), 400

    validation = validate_character_creation(character)
    if not validation["valid"]:
        return jsonify({"error": "Validation failed", "details": validation["errors"]}), 400

    char_id = str(uuid.uuid4())
    db.reference(f"/players/{char_id}").set(character)
    return jsonify({"character_id": char_id, "status": "saved"})

@menu_bp.route('/menu/character_sheet/<character_id>', methods=['GET'])
def get_character_sheet(character_id):
    character = db.reference(f"/players/{character_id}").get()

    if not character:
        return jsonify({"error": f"No character found with ID {character_id}."}), 404

    return jsonify(character), 200


@menu_bp.route('/menu/party_view/<character_id>', methods=['GET'])
def get_party_view(character_id):
    character = db.reference(f"/players/{character_id}").get()

    if not character:
        return jsonify({"error": f"No character found with ID {character_id}."}), 404

    party_id = character.get("party_id")

    if not party_id:
        return jsonify({"error": "Character is not part of any party."}), 404

    party = db.reference(f"/parties/{party_id}").get()

    if not party:
        return jsonify({"error": "Party data not found."}), 404

    member_ids = party.get("members", [])
    party_members = []

    for member_id in member_ids:
        member_data = db.reference(f"/npcs/{member_id}").get()
        if member_data:
            party_members.append(member_data)

    return jsonify({"party": party, "members": party_members}), 200


@menu_bp.route('/menu/world_map/<character_id>', methods=['GET'])
def get_world_map(character_id):
    character = db.reference(f"/players/{character_id}").get()

    if not character:
        return jsonify({"error": f"No character found with ID {character_id}."}), 404

    known_tiles = character.get("known_tiles", [])

    return jsonify({"known_tiles": known_tiles}), 200


@menu_bp.route("/menu/options", methods=["GET"])
def get_game_options():
    return jsonify({
        "audio": {"volume": 70},
        "graphics": {"resolution": "1280x720", "fullscreen": False},
        "input": {"move_up": "W", "move_down": "S", "confirm": "Enter"},
        "model": {"npc_model": "gpt-4.1-nano", "dm_model": "gpt-4.1"}
    }), 200

@menu_bp.route('/character/random', methods=['POST'])
def generate_random_character():
    try:
        # Call the character creation endpoint to generate a random character
        response = requests.post("http://localhost:5050/character/random")
        
        if response.status_code != 201:
            return jsonify({
                "error": "Failed to generate random character",
                "details": response.json()
            }), response.status_code
            
        character_data = response.json()
        
        # Generate portrait for the random character
        portrait_res = requests.post("http://localhost:5050/generate_portrait", json={
            "character": character_data["character"]
        })
        
        if portrait_res.status_code == 200:
            character_data["character"]["portrait_url"] = portrait_res.json().get("url", "N/A")
        else:
            character_data["character"]["portrait_url"] = f"Error {portrait_res.status_code}: {portrait_res.text}"
            
        return jsonify(character_data), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
