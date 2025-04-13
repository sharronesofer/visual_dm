from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
from app.regions.worldgen_utils import log_world_event
from app.npc.npc_rumor_utils import sync_event_beliefs

region_management_bp = Blueprint('region_management', __name__)

@region_management_bp.route('/region/<region_id>', methods=['GET'])
def get_region(region_id):
    region_ref = db.reference(f'/regions/{region_id}')
    region_data = region_ref.get()
    if not region_data:
        return jsonify({"error": "Region not found."}), 404
    return jsonify(region_data)

@region_management_bp.route('/region/<region_id>', methods=['POST'])
def update_region(region_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided."}), 400
    data["last_updated"] = datetime.utcnow().isoformat()
    region_ref = db.reference(f'/regions/{region_id}')
    region_ref.update(data)
    return jsonify({"message": "Region updated.", "region": data})

@region_management_bp.route('/region/<region_id>', methods=['DELETE'])
def delete_region(region_id):
    region_ref = db.reference(f'/regions/{region_id}')
    if not region_ref.get():
        return jsonify({"error": "Region not found."}), 404
    region_ref.delete()
    return jsonify({"message": "Region deleted."})

@region_management_bp.route('/log_event_and_notify_npcs', methods=['POST'])
def route_log_event_and_notify_npcs():
    data = request.json
    if not data:
        return jsonify({"error": "Missing event data"}), 400

    region = data.get("region")
    if not region:
        return jsonify({"error": "Missing region name"}), 400

    try:
        event = log_world_event(data)
        count = sync_event_beliefs(region, event)
        return jsonify({
            "message": f"Event logged and shared with {count} NPCs.",
            "event_id": event["event_id"],
            "region": region
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@region_management_bp.route('/questlog/<character_id>', methods=['GET'])
def get_questlog(character_id):
    questlog = db.reference(f'/questlogs/{character_id}').get() or []
    return jsonify({"character_id": character_id, "questlog": questlog})

@region_management_bp.route('/questlog/<character_id>', methods=['POST'])
def add_quest(character_id):
    data = request.get_json()
    quest = data.get("quest")
    if not quest:
        return jsonify({"error": "Quest data required."}), 400

    quest_entry = {
        "quest": quest,
        "timestamp": datetime.utcnow().isoformat()
    }

    questlog_ref = db.reference(f'/questlogs/{character_id}')
    questlog = questlog_ref.get() or []
    questlog.append(quest_entry)
    questlog_ref.set(questlog)

    return jsonify({"message": "Quest added.", "quest_entry": quest_entry})
