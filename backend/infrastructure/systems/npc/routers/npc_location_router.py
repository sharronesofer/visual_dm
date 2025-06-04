"""
NPC Location Router
------------------
FastAPI router for NPC location and movement endpoints.
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from backend.systems.npc.services.npc_location_service import NpcLocationService
from backend.infrastructure.database import get_db_session
from sqlalchemy.orm import Session

router = APIRouter(prefix="/npcs", tags=["npcs", "locations"])

def get_location_service(db: Session = Depends(get_db_session)) -> NpcLocationService:
    """Dependency for getting an NpcLocationService instance."""
    return NpcLocationService(db_session=db)

@router.post("/{npc_id}/update-location", response_model=Dict[str, Any])
async def update_npc_location(
    npc_id: UUID,
    service: NpcLocationService = Depends(get_location_service)
):
    """
    Update an NPC's location based on mobility settings.
    
    Parameters:
    -----------
    npc_id: UUID
        The NPC ID to update location for
    
    Returns:
    --------
    Dict containing results of the operation, including whether the NPC moved
    and if so, where to and why.
    """
    result = service.update_npc_location(npc_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@router.get("/{npc_id}/location")
async def get_npc_location(
    npc_id: UUID,
    service: NpcLocationService = Depends(get_location_service)
):
    """
    Get an NPC's current location.
    
    Parameters:
    -----------
    npc_id: UUID
        The NPC ID to get location for
    
    Returns:
    --------
    Dict containing the NPC's current location information.
    """
    npc = service._get_npc(npc_id)
    
    if not npc:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
        
    mobility = npc.get("mobility", {})
    current_location = mobility.get("current_poi", "unknown")
    home_location = mobility.get("home_poi", "unknown")
    last_moved = mobility.get("last_moved", None)
    
    return {
        "npc_id": str(npc_id),
        "current_location": current_location,
        "home_location": home_location,
        "last_moved": last_moved,
        "travel_motive": npc.get("travel_motive", "wander")
    }

@router.post("/daily-movement-tick")
async def run_daily_movement_tick(
    service: NpcLocationService = Depends(get_location_service)
):
    """
    Trigger movement updates for all NPCs at once (daily tick).
    
    This route is intended for automated daily updates to simulate
    world activity.
    
    Returns:
    --------
    Summary of NPC movements.
    """
    # In a real implementation, this would fetch all NPCs and
    # update their locations in a batch operation
    
    # For now, this is a stub implementation that would be expanded
    return {
        "message": "Daily NPC movement tick completed",
        "npcs_moved": 0,
        "npcs_stayed": 0
    } 