"""
FastAPI routes for World State system.

This module provides HTTP endpoints for world state operations.
"""

# HACK: Placeholder for missing region_generation_utils
# TODO: Implement proper region generation or use existing world_generation utils
def generate_region():
    """Placeholder for missing generate_region function"""
    return "default_region", {"tiles": {}, "poi_list": []}

from fastapi import APIRouter, Request, HTTPException, Depends
from backend.systems.world_state.manager import WorldStateManager
from backend.systems.world_state.world_types import StateCategory, WorldRegion

# Create FastAPI router instead of Flask Blueprint
router = APIRouter(prefix="/world", tags=["world_state"])

@router.post('/generate_initial_world')
async def generate_initial_world():
    """
    Creates a world, stores it as the default /global_state/home_region.
    """
    try:
        region_id, region_data = generate_region()

        # Use the WorldStateManager to update the state
        manager = WorldStateManager()
        world_state = manager.get_world_state()
        world_state["home_region"] = region_id
        manager.update_world_state({"home_region": region_id})

        return ({
            "message": f"World generated with starting region {region_id}.",
            "region_id": region_id,
            "tiles_created": len(region_data.get("tiles", {})),
            "poi_count": len(region_data.get("poi_list", []))
        }), 200

    except Exception as e:
        return ({"error": str(e)}), 500

@router.get("/world_summary")
def get_world_summary():
    try:
        # Use the WorldStateManager to get state data
        manager = WorldStateManager()
        world_state = manager.get_world_state()
        
        # Extract the components needed for the summary
        global_state = world_state.get("global", {})
        regional_state = world_state.get("regions", {})
        poi_state = world_state.get("pois", {})

        summary = {
            "global_state": global_state,
            "regional_state": regional_state,
            "poi_state": poi_state
        }
        return (summary)
    except Exception as e:
        return ({"error": str(e)}), 500

@router.post("/tick_world")
async def tick_world(request: Request):
    try:
        # Use the WorldStateManager to advance time
        manager = WorldStateManager()
        data = await request.json() if hasattr(request, 'json') else {}
        days = data.get("days", 0)
        hours = data.get("hours", 0)
        minutes = data.get("minutes", 1)  # Default to 1 minute if not specified
        
        # Advance the world time
        updated_state = manager.advance_world_time(days=days, hours=hours, minutes=minutes)
        
        return {
            "message": "World tick processed.",
            "current_date": updated_state.get("current_date", {})
        }
    except Exception as e:
        return {"error": str(e)}

@router.get('/global_state')
async def get_global_state():
    """
    Fetches the current global state document.
    """
    try:
        # Use the WorldStateManager to get global state
        manager = WorldStateManager()
        world_state = manager.get_world_state()
        global_state = world_state.get("global", {})
        return (global_state)
    except Exception as e:
        return ({"error": str(e)}), 500

@router.post('/global_state/update')
async def update_global_state(request: Request):
    """
    Updates the global state document with provided fields.
    """
    try:
        data = await request.json() if hasattr(request, 'json') else {}
        
        # Use the WorldStateManager to update the state
        manager = WorldStateManager()
        updates = {"global": data}
        manager.update_world_state(updates)
        
        return {"message": "Global state updated successfully."}
    except Exception as e:
        return {"error": str(e)}

