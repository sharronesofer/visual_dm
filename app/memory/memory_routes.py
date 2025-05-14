
#This Flask route module provides access to the NPC memory system, supporting:
#Viewing short-term memory
#Triggering memory summarization
#Adding test interactions
#Evaluating beliefs from monthly summaries
#It ties into the memory, firebase, npc, and beliefs systems.

from flask import Blueprint, jsonify, request
from app.memory.memory_utils import store_interaction, update_long_term_memory, summarize_and_clean_memory, get_recent_interactions, generate_beliefs_from_meta_summary
from firebase_admin import db

memory_bp = Blueprint('memory', __name__)

@memory_bp.route('/memory/<npc_id>', methods=['GET'])
def get_recent_memory(npc_id):
    character_id = request.args.get("character_id")
    entries = db.reference(f"/npc_memory/{npc_id}").get() or {}
    return jsonify({"recent": list(entries.values())})

@memory_bp.route('/memory/<npc_id>/clear', methods=['POST'])
def clear_npc_memory(npc_id):
    return summarize_and_clean_memory(npc_id)

@memory_bp.route('/memory/<npc_id>/evaluate_beliefs', methods=['POST'])
def evaluate_beliefs(npc_id):
    # Pull last few meta-summaries from Firebase
    summaries_ref = db.reference(f"/npcs/{npc_id}/monthly_meta")
    summaries = summaries_ref.get()

    if not summaries:
        return jsonify({"error": "No meta summaries found."}), 404

    # Merge into one prompt string
    text = "\n".join(summaries.values() if isinstance(summaries, dict) else summaries)
    result = generate_beliefs_from_meta_summary(npc_id, text)
    return jsonify(result)

