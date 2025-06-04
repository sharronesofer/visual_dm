"""
Faction routes module.
"""

from fastapi import APIRouter, Request
# # # from firebase_admin import db  # TODO: Replace with proper database integration  # TODO: Replace with proper database integration  # TODO: Replace with proper database integration
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from backend.infrastructure.database import get_db_session

from backend.systems.faction.models import Faction, FactionRelationship
from backend.infrastructure.schemas.faction.faction_types import FactionType
# from backend.systems.faction.services import FactionService, MembershipService, RelationshipService

# TODO: These imports need to be converted to canonical backend.systems.* format
# from backend.systems.faction.faction_tick_utils import propagate_faction_influence
# from backend.systems.npc.npc_loyalty_utils import drift_npc_faction_opinions

# Placeholder functions until canonical implementations are found/created
def propagate_faction_influence(*args, **kwargs):
    """Placeholder for faction influence propagation logic."""

def drift_npc_faction_opinions(*args, **kwargs):
    """Placeholder for NPC faction opinion drift logic."""

faction_routes = APIRouter(prefix="/faction", tags=["faction"])

@faction_routes.post('/admin/propagate_faction_influence')
async def trigger_faction_influence():
    """
    Manually triggers the faction influence tick and logs changes.
    Use this route during dev/debug to simulate world updates.
    """
    try:
        propagate_faction_influence()
        return {"message": "Faction influence propagation complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@faction_routes.post("/factions/tick_all")
async def tick_all_factions():
    try:
        propagate_faction_influence()
        return {"message": "Faction influence propagation complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@faction_routes.post("/factions/create")
async def create_faction(request: Request):
    data = await request.json()
    name = data.get("name")
    description = data.get("description", "No description provided.")
    tags = data.get("tags", [])
    region_origins = data.get("region_origins", [])
    poi_outposts = data.get("poi_outposts", [])
    hidden_attributes = data.get("hidden_attributes")

    if not name or not hidden_attributes:
        raise HTTPException(status_code=400, detail="Missing name or hidden_attributes.")

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

    # TODO: Replace with proper database integration
    # db.reference(f"/factions/{faction_id}").set(faction_data)
    return {"message": "Faction created.", "faction": faction_data}

@faction_routes.post("/factions/npc_drift_all")
async def drift_all_npc_opinions():
    try:
        drift_npc_faction_opinions()
        return {"message": "NPC faction opinions drifted based on proximity and affinity."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@faction_routes.get('/poi/{region}/{poi_id}/faction_events')
async def get_faction_influence_log(region: str, poi_id: str):
    """
    Retrieve recent faction influence events for a specific POI.
    Filters from the event log in /poi_state/<region>/<poi_id>/evolution_state
    """
    try:
        # TODO: Replace with proper database integration
        # ref = db.reference(f"/poi_state/{region}/{poi_id}/evolution_state/event_log")
        # log = ref.get() or []
        log = []

        # Filter only 'faction_influence' entries
        faction_events = [e for e in log if e.get("type") == "faction_influence"]

        # Optional: sort newest first
        faction_events.sort(key=lambda e: e.get("day", 0), reverse=True)

        return {
            "poi_id": poi_id,
            "region": region,
            "faction_influence_events": faction_events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
