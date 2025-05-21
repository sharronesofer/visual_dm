# !!! DEPRECATED !!!
# This module is deprecated and will be removed in a future version.
# Please use the modern FastAPI routes in router.py instead.
# The functions here are maintained for backward compatibility only.

#This module provides API endpoints for managing regional tension—a key variable representing narrative pressure, threat, or instability in a region. It lets you:
#Retrieve current tension
#Increase/decrease based on events
#Reset or decay values over time
#It supports the region, arc, chaos, motif, and faction systems.

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
# Import from utils.py instead of tension_utils directly
from backend.systems.tension_war.utils import get_tension, modify_tension, reset_tension, decay_tension, check_for_region_conflict
from firebase_admin import db
from collections import defaultdict

# Show deprecation warning
logging.warning("tension_routes.py is deprecated - use router.py instead")

# Constants
tension_levels = [
    (0, 10, "peaceful"),
    (11, 30, "watchful"),
    (31, 60, "anxious"),
    (61, 80, "violent"),
    (81, 100, "collapsing")
]

tension_bp = Blueprint('tension', __name__)

@tension_bp.route('/tension/<region_id>', methods=['GET'])
def route_get_tension(region_id):
    return jsonify(get_tension(region_id))


@tension_bp.route("/region/modify_tension", methods=["POST"])
def route_modify_tension():
    data = request.json
    region = data.get("region_id")
    source = data.get("source", "unknown")
    amount = int(data.get("amount", 0))
    broadcast = data.get("broadcast", False)

    if not region or amount == 0:
        return jsonify({"error": "region_id and amount required"}), 400

    ref = db.reference(f"/regional_state/{region}/tension_log")
    log = ref.get() or []

    log.append({
        "source": source,
        "delta": amount,
        "timestamp": datetime.utcnow().isoformat()
    })
    ref.set(log)

    # Optional total tracker
    total_ref = db.reference(f"/regional_state/{region}/tension_score")
    score = total_ref.get() or 0
    total_ref.set(score + amount)

    # Broadcast to DM
    if broadcast:
        db.reference("/dm_events").push({
            "type": "tension_spike",
            "region": region,
            "delta": amount,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        })

    return jsonify({"region": region, "delta": amount})
@tension_bp.route('/tension/reset/<region_id>', methods=['POST'])
def route_reset_tension(region_id):
    data = reset_tension(region_id)
    return jsonify(data)

@tension_bp.route('/tension/decay/<region_id>', methods=['POST'])
def route_decay_tension(region_id):
    payload = request.json or {}
    decay_rate = payload.get("decay_rate", 1)

    data = decay_tension(region_id, decay_rate)
    return jsonify(data)

def update_region_faction_attunement():
    """
    Updates each region's ruling faction, faction influence breakdown, and friction score.
    """
    poi_root = db.reference("/poi_state").get() or {}
    region_ref = db.reference("/regional_state")
    updates = {}

    for region, pois in poi_root.items():
        faction_scores = defaultdict(int)
        largest_city = None
        largest_population = 0

        for poi_id, poi_data in pois.items():
            population = len(poi_data.get("npcs_present", []))
            if population > largest_population:
                largest_city = poi_id
                largest_population = population

            influence = poi_data.get("faction_influence", {})
            for faction_id, score in influence.items():
                faction_scores[faction_id] += score

        total_score = sum(faction_scores.values())
        if not total_score:
            continue  # no data to compute

        ruling_faction = max(faction_scores, key=faction_scores.get)
        friction = sum(score for fid, score in faction_scores.items() if fid != ruling_faction) / total_score

        updates[region] = {
            "ruling_faction": ruling_faction,
            "largest_city": largest_city,
            "faction_attunement": dict(faction_scores),
            "friction_score": round(friction, 3)
        }

        region_ref.child(region).update(updates[region])

    return updates


@tension_bp.route('/admin/check_region_conflicts', methods=['POST'])
def trigger_region_conflict_check():
    """
    Manually trigger a check for regional faction conflicts or civil wars.
    """
    try:
        conflicts = check_for_region_conflict()
        return jsonify({
            "message": "Conflict detection complete.",
            "conflicts": conflicts
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500