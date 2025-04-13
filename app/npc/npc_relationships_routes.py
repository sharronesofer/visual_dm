from flask import Blueprint, request, jsonify
import random
from app.utils.firebase_utils import db

# External functions - ensure these are defined and imported properly
from app.npc.npc_relationships_utils import loyalty_tick, run_daily_relationship_tick
from app.characters.character_utils import rotate_motifs_if_needed
from app.data.party_utils import add_to_party, create_party

npc_relationship_bp = Blueprint('npc_relationship', __name__)

@npc_relationship_bp.route('/relationships/update', methods=['POST'])
def update_relationships():
    data = request.get_json(force=True)
    npc_id = data["npc_id"]
    target_id = data["target_id"]

    relationship_ref = db.reference(f'/npc_opinion_matrix/{npc_id}/{target_id}')
    current_score = relationship_ref.get() or 0
    delta = random.choice([-2, -1, 0, 1, 2])
    new_score = current_score + delta
    relationship_ref.set(new_score)

    return jsonify({"message": "Relationship updated", "new_score": new_score}), 200


@npc_relationship_bp.route('/recruit_npc', methods=['POST'])
def recruit_npc():
    data = request.get_json(force=True)
    character_id = data.get("character_id")
    npc_id = data.get("npc_id")

    player_data = db.reference(f"/players/{character_id}").get()
    npc_data = db.reference(f"/npcs/{npc_id}").get()

    if not player_data or not npc_data:
        return jsonify({"error": "Invalid player or NPC ID"}), 400

    existing_party = player_data.get("party_id")
    if existing_party:
        add_to_party(existing_party, npc_id)
    else:
        existing_party = create_party(character_id, [npc_id])

    return jsonify({
        "message": f"{npc_data['character_name']} has joined your party!",
        "party_id": existing_party
    }), 200


@npc_relationship_bp.route('/npc_loyalty_tick', methods=['POST'])
def npc_loyalty_tick():
    data = request.get_json(force=True)
    npc_id = data.get("npc_id")
    character_id = data.get("character_id")
    cha_score = data.get("cha", 10)

    if not npc_id or not character_id:
        return jsonify({"error": "Missing npc_id or character_id"}), 400

    result = loyalty_tick(npc_id, character_id, cha_score=cha_score)
    return jsonify(result), 200


@npc_relationship_bp.route('/npc_relationship_tick', methods=['POST'])
def npc_relationship_tick_route():
    run_daily_relationship_tick()
    return jsonify({"status": "NPC relationships updated"}), 200


@npc_relationship_bp.route('/npc_motif_tick', methods=['POST'])
def npc_motif_tick():
    all_npcs = db.reference('/npcs').get() or {}
    updated = {}
    for npc_id, npc in all_npcs.items():
        pool = npc.get("narrative_motif_pool", {})
        updated_pool = rotate_motifs_if_needed(pool)  # External function; ensure defined
        db.reference(f'/npcs/{npc_id}/narrative_motif_pool').set(updated_pool)
        updated[npc_id] = updated_pool.get("active_motifs", [])

    return jsonify({"message": "NPC motifs rotated", "updated": updated}), 200