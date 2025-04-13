from flask import Blueprint, request, jsonify
from app.characters.character_utils import (
    build_character_from_input,
    save_partial_character_data
)
from app.characters.character_utils import (
    save_character_to_firebase,
    load_character_from_firebase
)

character_bp = Blueprint("character", __name__)


@character_bp.route("/character/create", methods=["POST"])
def create_character():
    """
    Creates a full player character based on input data and rulebook JSONs.
    Automatically saves to Firebase under /players/<character_id>.
    """
    try:
        data = request.get_json(force=True)

        # Build full character object
        character = build_character_from_input(data)

        # Get character_id (either provided or fallback to name)
        character_id = character.get("character_id") or character.get("character_name")
        if not character_id:
            return jsonify({"error": "Missing character_id or character_name"}), 400

        # Save to Firebase
        save_character_to_firebase(character_id, character)

        return jsonify(character), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@character_bp.route("/character/save_partial", methods=["POST"])
def save_partial_character():
    """
    Saves a single field during the character creation process.
    Expects JSON: { "player_id": "abc", "field": "stats", "value": { "STR": 10 } }
    """
    try:
        data = request.get_json(force=True)
        player_id = data.get("player_id")
        field = data.get("field")
        value = data.get("value")

        if not player_id or not field:
            return jsonify({"error": "Missing player_id or field."}), 400

        save_partial_character_data(player_id, field, value)
        return jsonify({"message": "Field saved successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@character_bp.route("/character/<character_id>", methods=["GET"])
def load_character(character_id):
    """
    Loads a character from Firebase based on character_id.
    """
    try:
        character = load_character_from_firebase(character_id)
        if not character:
            return jsonify({"error": f"Character '{character_id}' not found."}), 404
        return jsonify(character), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
