# This route module handles NPC creation, retrieval, updates, and deletion, acting as the API surface for persistent NPC management. 
# It integrates with the NPCBuilder logic and database persistence.
# It supports the npc, database, motif, memory, and faction systems.

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging

# Import NPC services and models
from backend.systems.npc.services.npc_service import NPCService, get_npc_service
from backend.systems.npc.models import CreateNpcRequest, UpdateNpcRequest, NpcResponse

logger = logging.getLogger(__name__)

# Create FastAPI router
router = APIRouter(prefix="/npc", tags=["npc"])

@router.post("/create", response_model=NpcResponse)
async def create_npc(
    request: CreateNpcRequest,
    npc_service: NPCService = Depends(get_npc_service)
):
    """Create a new NPC"""
    try:
        npc = await npc_service.create_npc(request)
        return npc
    except Exception as e:
        logger.error(f"Error creating NPC: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{npc_id}", response_model=NpcResponse)
async def get_npc(
    npc_id: str,
    npc_service: NPCService = Depends(get_npc_service)
):
    """Get NPC by ID"""
    try:
        npc = await npc_service.get_npc(npc_id)
        if not npc:
            raise HTTPException(status_code=404, detail=f"NPC '{npc_id}' not found")
        return npc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{npc_id}", response_model=NpcResponse)
async def update_npc(
    npc_id: str,
    request: UpdateNpcRequest,
    npc_service: NPCService = Depends(get_npc_service)
):
    """Update NPC by ID"""
    try:
        npc = await npc_service.update_npc(npc_id, request)
        return npc
    except Exception as e:
        logger.error(f"Error updating NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{npc_id}")
async def delete_npc(
    npc_id: str,
    npc_service: NPCService = Depends(get_npc_service)
):
    """Delete NPC by ID"""
    try:
        success = await npc_service.delete_npc(npc_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"NPC '{npc_id}' not found")
        return {"message": f"NPC {npc_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{npc_id}/info")
async def get_npc_info(
    npc_id: str,
    npc_service: NPCService = Depends(get_npc_service)
):
    """Get basic NPC info for display"""
    try:
        npc = await npc_service.get_npc(npc_id)
        if not npc:
            raise HTTPException(status_code=404, detail=f"NPC '{npc_id}' not found")
        
        # Return basic display info
        return {
            "name": npc.name,
            "race": npc.race,
            "status": npc.status,
            "location": npc.location,
            "region_id": npc.region_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting NPC info {npc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))