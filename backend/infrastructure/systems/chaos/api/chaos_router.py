"""
Chaos System Router - API endpoints for chaos system management
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.systems.chaos.core.chaos_engine import ChaosEngine, get_chaos_engine
from backend.systems.chaos.services.mitigation_service import MitigationService
from backend.infrastructure.systems.chaos.schemas.chaos_schemas import (
    ChaosStateResponse, 
    MitigationRequest,
    EventTriggerRequest
)

router = APIRouter(prefix="/chaos", tags=["chaos"])

@router.get("/status", response_model=ChaosStateResponse)
async def get_chaos_status(
    region_id: Optional[str] = None,
    chaos_engine: ChaosEngine = Depends(get_chaos_engine)
):
    """Get current chaos status for the world or specific region"""
    try:
        if region_id:
            status = chaos_engine.get_regional_chaos_state(region_id)
        else:
            status = chaos_engine.get_current_chaos_state()
        
        return ChaosStateResponse(**status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chaos status: {e}")

@router.get("/events/active")
async def get_active_events(
    chaos_engine: ChaosEngine = Depends(get_chaos_engine)
) -> List[Dict[str, Any]]:
    """Get currently active chaos events"""
    try:
        events = chaos_engine.get_active_events()
        return [event.to_dict() for event in events]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active events: {e}")

@router.get("/pressure/summary")
async def get_pressure_summary(
    chaos_engine: ChaosEngine = Depends(get_chaos_engine)
) -> Dict[str, Any]:
    """Get summary of current pressure across all systems"""
    try:
        return chaos_engine.get_pressure_summary()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pressure summary: {e}")

@router.post("/mitigation/apply")
async def apply_mitigation(
    request: MitigationRequest,
    chaos_engine: ChaosEngine = Depends(get_chaos_engine)
) -> Dict[str, Any]:
    """Apply mitigation factors to reduce chaos pressure"""
    try:
        success = await chaos_engine.apply_mitigation(
            mitigation_type=request.mitigation_type,
            effectiveness=request.effectiveness,
            duration_hours=request.duration_hours,
            source_id=request.source_id,
            source_type=request.source_type,
            description=request.description,
            affected_regions=request.affected_regions,
            affected_sources=request.affected_sources
        )
        
        return {
            "success": success,
            "message": "Mitigation applied successfully" if success else "Mitigation failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply mitigation: {e}")

@router.post("/events/trigger")
async def force_trigger_event(
    request: EventTriggerRequest,
    chaos_engine: ChaosEngine = Depends(get_chaos_engine)
) -> Dict[str, Any]:
    """Force trigger a chaos event (admin/testing use)"""
    try:
        success = await chaos_engine.force_trigger_event(
            event_type=request.event_type,
            severity=request.severity,
            regions=request.regions
        )
        
        return {
            "success": success,
            "message": "Event triggered successfully" if success else "Event trigger failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger event: {e}")

@router.get("/metrics")
async def get_system_metrics(
    chaos_engine: ChaosEngine = Depends(get_chaos_engine)
) -> Dict[str, Any]:
    """Get chaos system performance metrics"""
    try:
        return chaos_engine.get_system_metrics()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {e}")

@router.get("/health")
async def get_system_health(
    chaos_engine: ChaosEngine = Depends(get_chaos_engine)
) -> Dict[str, Any]:
    """Get chaos system health status"""
    try:
        return await chaos_engine.get_system_health()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {e}")