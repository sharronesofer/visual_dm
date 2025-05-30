# !!! DEPRECATED !!!
# This module is deprecated and will be removed in a future version.
# Please use the modern FastAPI routes in router.py instead.
# The functions here are maintained for backward compatibility only.

from flask import Blueprint, request, jsonify
import logging
# Import from utils.py instead of war_utils directly
from backend.systems.tension_war.utils import (
    initialize_war,
    advance_war_day,
    record_poi_conquest,
    generate_daily_raids
)
from app.quests.player_arc_utils import trigger_war_arc
from firebase_admin import db

# Show deprecation warning
logging.warning("war_routes.py is deprecated - use router.py instead")

war_routes = Blueprint('war_routes', __name__)

@war_routes.route('/admin/generate_raids/<region_name>', methods=['POST'])
def trigger_daily_raids(region_name):
    try:
        results = generate_daily_raids(region_name)
        return jsonify({
            "message": f"Daily raids completed in {region_name}.",
            "results": results
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@war_routes.route('/admin/init_war', methods=['POST'])
def start_war():
    data = request.get_json()
    region_a = data.get("region_a")
    region_b = data.get("region_b")
    faction_a = data.get("faction_a")
    faction_b = data.get("faction_b")
    if not all([region_a, region_b, faction_a, faction_b]):
        return jsonify({"error": "Missing parameters"}), 400
    result = initialize_war(region_a, region_b, faction_a, faction_b)

    # Automatically create defense arcs
    trigger_war_arc(region_a, arc_type="defend")
    trigger_war_arc(region_b, arc_type="defend")

    return jsonify(result), 200

@war_routes.route('/admin/advance_war/<region>', methods=['POST'])
def tick_war_day(region):
    result = advance_war_day(region)
    return jsonify(result), 200

@war_routes.route('/admin/conquer_poi', methods=['POST'])
def conquer_poi():
    data = request.get_json()
    region = data.get("region")
    poi_id = data.get("poi_id")
    faction = data.get("faction")
    if not all([region, poi_id, faction]):
        return jsonify({"error": "Missing parameters"}), 400
    record_poi_conquest(region, poi_id, faction)

    # Trigger evac and possibly reclaim arcs
    trigger_war_arc(region, poi_id=poi_id, arc_type="evacuate")

    poi_data = db.reference(f"/poi_state/{region}/{poi_id}").get() or {}
    if poi_data.get("poi_type") == "dungeon":
        trigger_war_arc(region, poi_id=poi_id, arc_type="reclaim")

    return jsonify({"message": f"{poi_id} conquered by {faction}"}), 200

@war_routes.route('/admin/war_arcs', methods=['GET'])
def get_war_arcs():
    """
    Fetch all active arcs tagged with 'war'
    """
    all_arcs = db.reference("/player_arcs").get() or {}
    war_arcs = {
        aid: arc for aid, arc in all_arcs.items()
        if "tags" in arc and "war" in arc["tags"]
    }
    return jsonify({"war_arcs": war_arcs})
