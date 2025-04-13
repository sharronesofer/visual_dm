from flask import Blueprint, request, jsonify
from firebase_admin import db
from app.combat.combat_utils import simulate_tactical_combat_round, attempt_rest
from app.regions.worldgen_utils import attempt_rest

combat_bp = Blueprint("combat", __name__)

@combat_bp.route('/combat_round', methods=['POST'])
def combat_round():
    data = request.get_json(force=True)
    combatants = data.get("combatants")

    if not isinstance(combatants, list) or not combatants:
        return jsonify({"error": "A non-empty 'combatants' list is required."}), 400

    result = simulate_tactical_combat_round(combatants)
    return jsonify(result), 200


@combat_bp.route('/long_rest/<character_id>', methods=['POST'])
def long_rest(character_id):
    char_ref = db.reference(f"/players/{character_id}")
    character = char_ref.get()

    if not character:
        return jsonify({"error": "Character not found."}), 404

    spell_slots = character.get("spell_slots")

    if not spell_slots:
        return jsonify({"error": "Character has no spell slots to reset."}), 400

    for level_info in spell_slots.values():
        level_info["used"] = 0

    char_ref.update({"spell_slots": spell_slots})

    return jsonify({
        "message": f"{character.get('character_name', 'Character')} has completed a long rest.",
        "spell_slots": spell_slots
    }), 200


@combat_bp.route('/rest/<region>/<poi>/<character_id>', methods=['POST'])
def rest_attempt(region, poi, character_id):
    result = attempt_rest(region, poi)
    msg = {"rest_result": result}

    if result["success"]:
        # Example logic to refill MP (customize to your rules)
        char_ref = db.reference(f"/players/{character_id}")
        character = char_ref.get()
        if character:
            max_mp = character.get("max_MP", 10)
            char_ref.update({"MP": max_mp})
            msg["message"] = "Rest completed successfully. MP restored."
        else:
            msg["message"] = "Rest completed, but character not found for MP update."
    else:
        msg["message"] = "Rest was interrupted by an encounter."

    return jsonify(msg), 200
