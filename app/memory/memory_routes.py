from flask import Blueprint, jsonify, request
from memory_utils import store_interaction, update_long_term_memory, summarize_and_clean_memory, get_recent_interactions

memory_bp = Blueprint('memory', __name__)

@memory_bp.route('/memory/<npc_id>', methods=['GET'])
def get_npc_memory(npc_id):
    character_id = request.args.get("character_id")
    interactions = get_recent_interactions(npc_id, character_id)
    return jsonify({"recent": interactions})

@memory_bp.route('/memory/<npc_id>/clear', methods=['POST'])
def clear_npc_memory(npc_id):
    return summarize_and_clean_memory(npc_id)

@memory_bp.route('/memory/<npc_id>/sample', methods=['POST'])
def add_sample_memory(npc_id):
    character_id = request.json.get("character_id", "test")
    store_interaction(npc_id, character_id, "Met the hero")
    store_interaction(npc_id, character_id, "Fought a monster")
    return jsonify({"message": f"Sample memory added for NPC {npc_id}."})
