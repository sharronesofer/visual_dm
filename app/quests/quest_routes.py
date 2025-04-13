from flask import Blueprint, request, jsonify
from app.quests.player_arc_utils import (
    load_player_arc,
    save_player_arc,
    update_arc_with_event
)
from app.quests.quest_utils import (
    create_quest_log_entry,
    list_quests_for_player,
    get_quest_log_entry
)

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
