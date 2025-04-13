from flask import Blueprint, request, jsonify
from firebase_admin import db

from app.rules.rules_validation_routes import resolve_combat_action
from app.combat.ai_combat_utils import choose_action_gpt
from app.regions.worldgen_utils import attempt_rest

combat_bp = Blueprint("combat", __name__)

@combat_bp.route('/combat_round', methods=['POST'])
def combat_round():
    data = request.get_json(force=True)
    combatants = data.get("combatants")
    battlefield_context = data.get("battlefield_context", {})

    if not isinstance(combatants, list) or not combatants:
        return jsonify({"error": "A non-empty 'combatants' list is required."}), 400

    actions = []

    for combatant in combatants:
        if combatant.get("type") == "npc":
            action_data = choose_action_gpt(combatant, battlefield_context)
            result = resolve_combat_action(combatant, action_data, battlefield_context)
            actions.append(result)
        else:
            # Player-controlled characters should submit actions separately
            actions.append({
                "character_id": combatant.get("character_id"),
                "result": "awaiting_player_action"
            })

    return jsonify({"results": actions}), 200


@combat_bp.route('/long_rest/<character_id>', methods=['POST'])
def long_rest(character_id):
    char_ref = db.reference(f"/players/{character_id}")
    character = char_ref.get()

    if not character:
        return jsonify({"error": "Character not found."}), 404

    result = attempt_rest(character_id, character)
    return jsonify(result), 200