from flask import Blueprint, request, jsonify
from firebase_admin import db

from app.combat.ai_combat_utils import choose_action_gpt
from app.combat.combat_class import CombatAction, Combatant
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

            target_id = action_data.get("target")
            if not target_id:
                actions.append({
                    "character_id": combatant.get("npc_id"),
                    "result": "No target specified"
                })
                continue

            # TEMPORARY: Mock target data (should be loaded from DB in real case)
            target_data = {
                "id": target_id,
                "character_id": target_id,
                "stats": {"HP": 30, "AC": 12, "DEX": 10},
                "feats": [],
                "equipment": []
            }

            attacker_obj = Combatant(combatant["npc_id"], combatant)
            target_obj = Combatant(target_id, target_data)

            combat_action = CombatAction(attacker_obj, target_obj, action_data, battlefield_context)
            result = combat_action.resolve()
            actions.append(result)

        else:
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
