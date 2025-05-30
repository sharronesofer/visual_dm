"""
FastAPI Router for Tension and War Management System

This module provides the API endpoints for tension and war operations.
It replaces the deprecated Flask-based routes in tension_routes.py and war_routes.py.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.core.logging import logger

# Import from consolidated services and utils modules
from backend.systems.tension_war.services import TensionManager, WarManager
from backend.systems.tension_war.schemas import (
    TensionRequest, 
    TensionResponse, 
    WarStatusResponse,
    WarInitiationRequest,
    WarAdvanceResponse,
    PoiConquestRequest
)

router = APIRouter(prefix="/api/v1", tags=["tension-war"])

# Initialize managers
tension_mgr = TensionManager()
war_mgr = WarManager()

# ---------- Tension Routes ----------

@router.get("/tension/{region_id}", response_model=TensionResponse)
async def get_region_tension(
    region_id: str = Path(..., description="The region ID to get tension for"),
    current_user: Dict = Depends(get_current_user)
):
    """Get the current tension values for a region"""
    try:
        return tension_mgr.get_tension(region_id)
    except Exception as e:
        logger.error(f"Error getting tension for region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tension/{region_id}", response_model=TensionResponse)
async def modify_region_tension(
    request: TensionRequest,
    region_id: str = Path(..., description="The region ID to modify tension for"),
    current_user: Dict = Depends(get_current_user)
):
    """Modify tension values for a region"""
    try:
        return tension_mgr.modify_tension(
            region_id=region_id,
            faction=request.faction,
            value=request.value,
            reason=request.reason
        )
    except Exception as e:
        logger.error(f"Error modifying tension for region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tension/{region_id}/reset", response_model=TensionResponse)
async def reset_region_tension(
    region_id: str = Path(..., description="The region ID to reset tension for"),
    current_user: Dict = Depends(get_current_user)
):
    """Reset tension values for a region"""
    try:
        return tension_mgr.reset_tension(region_id)
    except Exception as e:
        logger.error(f"Error resetting tension for region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tension/{region_id}/decay", response_model=TensionResponse)
async def decay_region_tension(
    region_id: str = Path(..., description="The region ID to decay tension for"),
    current_user: Dict = Depends(get_current_user)
):
    """Apply daily tension decay for a region"""
    try:
        return tension_mgr.decay_tension(region_id)
    except Exception as e:
        logger.error(f"Error decaying tension for region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- War Routes ----------

@router.post("/war/initialize", response_model=WarStatusResponse)
async def initialize_new_war(
    request: WarInitiationRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Initialize a new war between two factions in their respective regions"""
    try:
        return war_mgr.initialize_war(
            region_a=request.region_a,
            region_b=request.region_b,
            faction_a=request.faction_a,
            faction_b=request.faction_b
        )
    except Exception as e:
        logger.error(f"Error initializing war: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/war/{region_id}/advance", response_model=WarAdvanceResponse)
async def advance_war(
    region_id: str = Path(..., description="The region ID to advance war for"),
    current_user: Dict = Depends(get_current_user)
):
    """Advance the war by one day in the specified region"""
    try:
        return war_mgr.advance_war_day(region_id)
    except Exception as e:
        logger.error(f"Error advancing war for region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/war/conquer-poi", response_model=Dict[str, Any])
async def conquer_poi(
    request: PoiConquestRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Record the conquest of a POI by a faction"""
    try:
        return war_mgr.record_poi_conquest(
            region=request.region,
            poi_id=request.poi_id,
            faction=request.faction
        )
    except Exception as e:
        logger.error(f"Error recording POI conquest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/war/{region_id}/generate-raids", response_model=List[Dict[str, Any]])
async def generate_raids(
    region_id: str = Path(..., description="The region ID to generate raids for"),
    current_user: Dict = Depends(get_current_user)
):
    """Generate daily raids for a region in war"""
    try:
        return war_mgr.generate_daily_raids(region_id)
    except Exception as e:
        logger.error(f"Error generating raids for region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/war/{region_id}/status", response_model=WarStatusResponse)
async def get_war_status(
    region_id: str = Path(..., description="The region ID to get war status for"),
    current_user: Dict = Depends(get_current_user)
):
    """Get the current war status for a region"""
    try:
        return war_mgr.get_war_status(region_id)
    except Exception as e:
        logger.error(f"Error getting war status for region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 