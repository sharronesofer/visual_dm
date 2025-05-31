#This file provides administrative and simulation routes for faction creation, influence propagation, and NPC opinion drift. It integrates faction structures into the evolving world state and NPC simulation.
#It connects deeply with faction, firebase, npc, and world systems.

from fastapi import APIRouter as APIRouter, request, jsonify
# # # from firebase_admin import db  # TODO: Replace with proper database integration  # TODO: Replace with proper database integration  # TODO: Replace with proper database integration
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter as APIRouter, jsonify
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from backend.systems.faction.models import Faction, FactionType, FactionRelationship
from backend.systems.faction.services import FactionService, MembershipService, RelationshipService

# TODO: These imports need to be converted to canonical backend.systems.* format
# from backend.systems.faction.faction_tick_utils import propagate_faction_influence
# from backend.systems.npc.npc_loyalty_utils import drift_npc_faction_opinions

# Placeholder functions until canonical implementations are found/created
def propagate_faction_influence(*args, **kwargs):
    """Placeholder for faction influence propagation logic."""

def drift_npc_faction_opinions(*args, **kwargs):
    """Placeholder for NPC faction opinion drift logic."""

faction_bp = Blueprint("faction", __name__)

@faction_bp.route('/admin/propagate_faction_influence', methods=['POST'])
def trigger_faction_influence():
    """
    Manually triggers the faction influence tick and logs changes.
    Use this route during dev/debug to simulate world updates.
    """
    try:
        propagate_faction_influence()
        return jsonify({"message": "Faction influence propagation complete."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@faction_bp.route("/factions/tick_all", methods=["POST"])
def tick_all_factions():
    try:
        propagate_faction_influence()
        return jsonify({"message": "Faction influence propagation complete."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@faction_bp.route("/factions/create", methods=["POST"])
def create_faction():
    data = request.get_json(force=True)
    name = data.get("name")
    description = data.get("description", "No description provided.")
    tags = data.get("tags", [])
    region_origins = data.get("region_origins", [])
    poi_outposts = data.get("poi_outposts", [])
    hidden_attributes = data.get("hidden_attributes")

    if not name or not hidden_attributes:
        return jsonify({"error": "Missing name or hidden_attributes."}), 400

    faction_id = f"faction_{uuid4().hex[:8]}"
    faction_data = {
        "id": faction_id,
        "name": name,
        "description": description,
        "tags": tags,
        "region_origins": region_origins,
        "poi_outposts": poi_outposts,
        "hidden_attributes": hidden_attributes,
        "faction_relations": {},
        "created_at": datetime.utcnow().isoformat()
    }

    db.reference(f"/factions/{faction_id}").set(faction_data)
    return jsonify({"message": "Faction created.", "faction": faction_data})

@faction_bp.route("/factions/npc_drift_all", methods=["POST"])
def drift_all_npc_opinions():
    try:
        drift_npc_faction_opinions()
        return jsonify({"message": "NPC faction opinions drifted based on proximity and affinity."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@faction_bp.route('/poi/<region>/<poi_id>/faction_events', methods=['GET'])
def get_faction_influence_log(region, poi_id):
    """
    Retrieve recent faction influence events for a specific POI.
    Filters from the event log in /poi_state/<region>/<poi_id>/evolution_state
    """
    try:
        ref = db.reference(f"/poi_state/{region}/{poi_id}/evolution_state/event_log")
        log = ref.get() or []

        # Filter only 'faction_influence' entries
        faction_events = [e for e in log if e.get("type") == "faction_influence"]

        # Optional: sort newest first
        faction_events.sort(key=lambda e: e.get("day", 0), reverse=True)

        return jsonify({
            "poi_id": poi_id,
            "region": region,
            "faction_influence_events": faction_events
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
