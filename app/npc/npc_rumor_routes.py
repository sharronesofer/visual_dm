from flask import Blueprint, request, jsonify
import random
import json
import openai
from datetime import datetime
from firebase_admin import db

from app.utils.gpt_utils import log_gpt_usage
from app.memory.memory_utils import store_interaction
from app.npc.npc_rumor_utils import share_rumors_between_npcs
from app.npc.npc_relationships_utils import update_npc_location

rumor_bp = Blueprint('rumor', __name__)


@rumor_bp.route('/simulate_npc_interactions', methods=['POST'])
def simulate_npc_interactions():
    data = request.get_json(force=True)
    region_name = data.get("region_name", "")
    poi_id = data.get("poi_id", "")
    if not region_name or not poi_id:
        return jsonify({"error": "Both region_name and poi_id are required."}), 400

    poi_ref = db.reference(f'/poi_state/{region_name}/{poi_id}')
    poi_state = poi_ref.get()
    if not poi_state:
        return jsonify({"error": f"POI '{poi_id}' in region '{region_name}' not found."}), 404

    npcs = poi_state.get("npcs_present", [])
    if len(npcs) < 2:
        return jsonify({"message": "Not enough NPCs present to simulate interactions."}), 200

    interaction_log = []
    for npc in npcs:
        others = [o for o in npcs if o != npc]
        if not others or random.random() > 0.6:
            continue

        partner = random.choice(others)
        matrix_ref = db.reference(f'/npc_opinion_matrix/{npc}/{partner}')
        score = matrix_ref.get() or 0

        tone = "friendly" if score >= 5 else "hostile" if score <= -5 else "neutral"

        system_prompt = "You are narrating social encounters between NPCs in a persistent fantasy world."
        user_prompt = (
            f"NPC A ({npc}) and NPC B ({partner}) are having a {tone} interaction at '{poi_id}'."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=60
            )
            summary = response.choices[0].message.content.strip()
            log_gpt_usage("gpt-4o-mini", response.get("usage", {}))
        except Exception:
            summary = f"{npc} and {partner} interact (GPT failed)."

        # Use memory_utils store_interaction for both NPCs
        store_interaction(npc, partner, summary)
        store_interaction(partner, npc, summary)

        rumor_result = share_rumors_between_npcs(npc, partner)
        new_score = score + {"friendly": 2, "neutral": 0, "hostile": -2}[tone]
        matrix_ref.set(new_score)

        interaction_log.append({
            "npc": npc,
            "partner": partner,
            "tone": tone,
            "summary": summary,
            "shared_rumors": rumor_result.get("shared", []),
            "new_score": new_score
        })

    return jsonify({"message": f"Interactions at '{poi_id}' simulated.", "interactions": interaction_log}), 200


@rumor_bp.route('/npc/travel/<npc_id>', methods=['POST'])
def npc_travel(npc_id):
    result = update_npc_location(npc_id)
    return jsonify(result), 200
