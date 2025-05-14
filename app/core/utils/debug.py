from flask import Blueprint, jsonify
from firebase_admin import db

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/seed_poi", methods=["POST"])
def seed_debug_poi():
    try:
        db.reference("/poi_state/dev_region/dev_village").set({
            "state_tags": ["village", "starting_area"],
            "control_status": "friendly",
            "event_log": []
        })
        return jsonify({"status": "✅ Seeded dev POI."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
