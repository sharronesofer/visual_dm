
#This module provides a complete API for player arcs and quests, including:
#Arc creation, retrieval, and progression
#Quest logging, listing, retrieval, and completion
#It integrates directly with narrative, quest, arc, firebase, and POI systems.

from flask import Blueprint, request, jsonify
from app.quests.player_arc_utils import (
    load_player_arc,
    save_player_arc,
    update_arc_with_event
)
from app.quests.quests_class import QuestManager
from firebase_admin import db

quest_bp = Blueprint("quest", __name__)

# === ARC ROUTES ===
@quest_bp.route("/arc/<character_id>", methods=["GET"])
def get_player_arc(character_id):
    try:
        arc = load_player_arc(character_id)
        if not arc:
            return jsonify({"error": f"No arc found for character '{character_id}'."}), 404
        return jsonify(arc.finalize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@quest_bp.route("/arc/<character_id>", methods=["POST"])
def post_arc_update(character_id):
    try:
        data = request.get_json(force=True)
        event = data.get("event")
        if not event:
            return jsonify({"error": "Missing event text."}), 400

        arc = update_arc_with_event(character_id, event)
        return jsonify(arc.finalize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# === QUEST LOG ROUTES ===

@quest_bp.route("/quests/<player_id>", methods=["GET"])
def list_quests(player_id):
    try:
        quests = list_quests_for_player(player_id)
        return jsonify(quests), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@quest_bp.route("/quests/<player_id>/<entry_id>", methods=["GET"])
def get_quest(player_id, entry_id):
    try:
        entry = get_quest_log_entry(player_id, entry_id)
        if not entry:
            return jsonify({"error": "Quest entry not found."}), 404
        return jsonify(entry), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@quest_bp.route("/quests/<player_id>", methods=["POST"])
def post_quest(player_id):
    try:
        data = request.get_json(force=True)
        required = ["region", "poi", "summary", "tags", "source"]
        if not all(k in data for k in required):
            return jsonify({"error": f"Missing one of: {required}"}), 400

        entry_id = create_quest_log_entry(
            data["region"],
            data["poi"],
            data["summary"],
            data["tags"],
            data["source"],
            player_id
        )
        return jsonify({"message": "Quest entry created", "entry_id": entry_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@quest_bp.route("/quests/complete/<character_id>/<quest_id>", methods=["POST"])
def complete_quest_route(character_id, quest_id):
    try:
        result = complete_quest(character_id, quest_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quest_bp.route("/players/<character_id>/questlog", methods=["GET"])
def get_player_questlog(character_id):
    ref = db.reference(f"/players/{character_id}/questlog")
    questlog = ref.get() or []
    return jsonify({
        "character_id": character_id,
        "questlog": questlog
    })

@quest_bp.route("/quest_board/accept", methods=["POST"])
def accept_quest_from_board():
    data = request.json
    region = data.get("region")
    poi = data.get("poi")
    quest_id = data.get("quest_id")
    player_id = data.get("player_id")

    board_ref = db.reference(f"/quest_boards/{region}/{poi}/quests")
    board = board_ref.get() or []

    accepted = None
    board = [q for q in board if not (q["id"] == quest_id and (accepted := q))]

    board_ref.set(board)

    if not accepted:
        return {"error": "Quest not found or already accepted."}

    # Add to player questlog
    qlog_ref = db.reference(f"/players/{player_id}/questlog")
    log = qlog_ref.get() or []

    accepted["player_id"] = player_id
    accepted["status"] = "active"
    accepted["region"] = region
    accepted["poi"] = poi
    accepted["timestamp"] = datetime.utcnow().isoformat()
    accepted["tags"] = ["board"]
    accepted["source"] = "quest_board"

    log.append(accepted)
    qlog_ref.set(log)

    # Tag NPC with posted quest
    npc_ref = db.reference(f"/npcs/{accepted['npc']}/posted_quests")
    npc_quests = npc_ref.get() or []
    if accepted["id"] not in npc_quests:
        npc_quests.append(accepted["id"])
        npc_ref.set(npc_quests)

    return {"message": f"Quest {quest_id} accepted by {player_id}", "quest": accepted}
