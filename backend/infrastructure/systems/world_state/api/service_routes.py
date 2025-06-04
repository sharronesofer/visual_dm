"""
World State Service API Routes

FastAPI routes for the world state service layer, providing access to
business logic functionality through HTTP endpoints.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field

from backend.systems.world_state.services.services import WorldStateService, create_world_state_service
from backend.systems.world_state.world_types import StateCategory
from backend.systems.world_state.integrations import (
    FactionWorldStateIntegration,
    create_faction_world_state_integration
)

router = APIRouter(prefix="/api/v1/world-state", tags=["world-state-service"])

# Global service instance (will be initialized on first use)
_world_state_service: Optional[WorldStateService] = None
_faction_integration: Optional[FactionWorldStateIntegration] = None


async def get_world_state_service() -> WorldStateService:
    """Get or create the world state service instance"""
    global _world_state_service
    if _world_state_service is None:
        _world_state_service = await create_world_state_service()
    return _world_state_service


async def get_faction_integration() -> FactionWorldStateIntegration:
    """Get or create the faction integration instance"""
    global _faction_integration
    if _faction_integration is None:
        service = await get_world_state_service()
        _faction_integration = await create_faction_world_state_integration(service)
    return _faction_integration


# ===== REQUEST/RESPONSE MODELS =====

class StateVariableRequest(BaseModel):
    """Request model for setting state variables"""
    key: str = Field(..., description="State variable key")
    value: Any = Field(..., description="State variable value")
    region_id: Optional[str] = Field(None, description="Region ID for regional state")
    category: StateCategory = Field(StateCategory.OTHER, description="State category")
    reason: Optional[str] = Field(None, description="Reason for change")
    user_id: Optional[str] = Field(None, description="User making the change")


class StateQueryRequest(BaseModel):
    """Request model for querying state"""
    category: Optional[StateCategory] = Field(None, description="Filter by category")
    region_id: Optional[str] = Field(None, description="Filter by region")
    key_pattern: Optional[str] = Field(None, description="Key pattern to match")
    start_time: Optional[datetime] = Field(None, description="Start time for time range")
    end_time: Optional[datetime] = Field(None, description="End time for time range")


class RegionRequest(BaseModel):
    """Request model for creating regions"""
    region_id: str = Field(..., description="Region identifier")
    initial_state: Optional[Dict[str, Any]] = Field(None, description="Initial state data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Region metadata")


class WorldEventRequest(BaseModel):
    """Request model for recording world events"""
    event_type: str = Field(..., description="Type of event")
    description: str = Field(..., description="Event description")
    affected_regions: Optional[List[str]] = Field(None, description="Affected regions")
    category: StateCategory = Field(StateCategory.OTHER, description="Event category")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Event metadata")


class FactionControlRequest(BaseModel):
    """Request model for faction territorial control"""
    region_id: str = Field(..., description="Region identifier")
    faction_id: Optional[UUID] = Field(None, description="Faction ID (null to remove control)")
    reason: str = Field("Territorial control change", description="Reason for change")


class FactionInfluenceRequest(BaseModel):
    """Request model for faction influence"""
    region_id: str = Field(..., description="Region identifier")
    faction_id: UUID = Field(..., description="Faction ID")
    influence_level: float = Field(..., ge=0.0, le=1.0, description="Influence level (0.0-1.0)")
    reason: str = Field("Influence change", description="Reason for change")


# ===== STATE MANAGEMENT ENDPOINTS =====

@router.get("/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        service = await get_world_state_service()
        return await service.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


@router.get("/state/{key}")
async def get_state_variable(
    key: str = Path(..., description="State variable key"),
    region_id: Optional[str] = Query(None, description="Region ID for regional state"),
    default: Optional[str] = Query(None, description="Default value if not found")
):
    """Get a state variable value"""
    try:
        service = await get_world_state_service()
        value = await service.get_state_variable(key, region_id, default)
        return {"key": key, "value": value, "region_id": region_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get state variable: {str(e)}")


@router.post("/state")
async def set_state_variable(request: StateVariableRequest):
    """Set a state variable value"""
    try:
        service = await get_world_state_service()
        success = await service.set_state_variable(
            request.key,
            request.value,
            request.region_id,
            request.category,
            request.reason,
            request.user_id
        )
        return {"success": success, "key": request.key, "region_id": request.region_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set state variable: {str(e)}")


@router.post("/query")
async def query_state(request: StateQueryRequest):
    """Query state variables with filters"""
    try:
        service = await get_world_state_service()
        
        time_range = None
        if request.start_time and request.end_time:
            time_range = (request.start_time, request.end_time)
        
        result = await service.query_state(
            request.category,
            request.region_id,
            request.key_pattern,
            time_range
        )
        return {"results": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query state: {str(e)}")


# ===== REGION MANAGEMENT ENDPOINTS =====

@router.post("/regions")
async def create_region(request: RegionRequest):
    """Create a new region"""
    try:
        service = await get_world_state_service()
        success = await service.create_region(
            request.region_id,
            request.initial_state,
            request.metadata
        )
        return {"success": success, "region_id": request.region_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create region: {str(e)}")


@router.get("/regions/{region_id}")
async def get_region_state(region_id: str = Path(..., description="Region identifier")):
    """Get current state for a region"""
    try:
        service = await get_world_state_service()
        state = await service.get_region_state(region_id)
        return {"region_id": region_id, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get region state: {str(e)}")


@router.put("/regions/{region_id}")
async def update_region_state(
    region_id: str = Path(..., description="Region identifier"),
    updates: Dict[str, Any] = Body(..., description="State updates"),
    reason: Optional[str] = Body(None, description="Reason for update"),
    create_snapshot: bool = Body(False, description="Create snapshot after update")
):
    """Update region state"""
    try:
        service = await get_world_state_service()
        success = await service.update_region_state(region_id, updates, reason, create_snapshot)
        return {"success": success, "region_id": region_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update region state: {str(e)}")


@router.post("/regions/{region_id}/snapshots")
async def create_region_snapshot(
    region_id: str = Path(..., description="Region identifier"),
    metadata: Optional[Dict[str, Any]] = Body(None, description="Snapshot metadata")
):
    """Create a snapshot of region state"""
    try:
        service = await get_world_state_service()
        snapshot_id = await service.create_region_snapshot(region_id, metadata)
        return {"success": bool(snapshot_id), "snapshot_id": snapshot_id, "region_id": region_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create region snapshot: {str(e)}")


@router.get("/regions/{region_id}/snapshots")
async def list_region_snapshots(
    region_id: str = Path(..., description="Region identifier"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of snapshots")
):
    """List snapshots for a region"""
    try:
        service = await get_world_state_service()
        snapshots = await service.list_region_snapshots(region_id, start_time, end_time, limit)
        return {"region_id": region_id, "snapshots": snapshots, "count": len(snapshots)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list region snapshots: {str(e)}")


# ===== HISTORICAL DATA ENDPOINTS =====

@router.get("/regions/{region_id}/history")
async def get_historical_state(
    region_id: str = Path(..., description="Region identifier"),
    timestamp: datetime = Query(..., description="Historical timestamp"),
    include_global: bool = Query(True, description="Include global context")
):
    """Get historical state for a region at a specific time"""
    try:
        service = await get_world_state_service()
        state = await service.get_historical_state(region_id, timestamp, include_global)
        return {"region_id": region_id, "timestamp": timestamp.isoformat(), "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get historical state: {str(e)}")


@router.get("/history/summary")
async def get_historical_summary(
    start_time: datetime = Query(..., description="Start time"),
    end_time: datetime = Query(..., description="End time"),
    region_id: Optional[str] = Query(None, description="Region filter"),
    period_type: Optional[str] = Query(None, description="Period type filter")
):
    """Get historical summary for a time period"""
    try:
        service = await get_world_state_service()
        summary = await service.get_historical_summary(start_time, end_time, region_id, period_type)
        return {"summary": summary, "count": len(summary)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get historical summary: {str(e)}")


# ===== EVENT MANAGEMENT ENDPOINTS =====

@router.post("/events")
async def record_world_event(request: WorldEventRequest):
    """Record a world event"""
    try:
        service = await get_world_state_service()
        event_id = await service.record_world_event(
            request.event_type,
            request.description,
            request.affected_regions,
            request.category,
            request.metadata
        )
        return {"success": bool(event_id), "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record world event: {str(e)}")


# ===== FACTION INTEGRATION ENDPOINTS =====

@router.post("/factions/control")
async def set_faction_control(request: FactionControlRequest):
    """Set faction control over a region"""
    try:
        integration = await get_faction_integration()
        success = await integration.set_region_controller(
            request.region_id,
            request.faction_id,
            request.reason
        )
        return {"success": success, "region_id": request.region_id, "faction_id": request.faction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set faction control: {str(e)}")


@router.get("/factions/{faction_id}/territories")
async def get_faction_territories(faction_id: UUID = Path(..., description="Faction ID")):
    """Get all territories controlled by a faction"""
    try:
        integration = await get_faction_integration()
        territories = await integration.get_faction_territories(faction_id)
        return {"faction_id": faction_id, "territories": territories, "count": len(territories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get faction territories: {str(e)}")


@router.post("/factions/influence")
async def set_faction_influence(request: FactionInfluenceRequest):
    """Set faction influence in a region"""
    try:
        integration = await get_faction_integration()
        success = await integration.set_faction_influence(
            request.region_id,
            request.faction_id,
            request.influence_level,
            request.reason
        )
        return {"success": success, "region_id": request.region_id, "faction_id": request.faction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set faction influence: {str(e)}")


@router.get("/regions/{region_id}/factions")
async def get_region_faction_influences(region_id: str = Path(..., description="Region identifier")):
    """Get all faction influences in a region"""
    try:
        integration = await get_faction_integration()
        influences = await integration.get_region_faction_influences(region_id)
        return {"region_id": region_id, "influences": influences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get region faction influences: {str(e)}")


@router.get("/factions/summary")
async def get_world_faction_summary():
    """Get summary of all faction-related world state data"""
    try:
        integration = await get_faction_integration()
        summary = await integration.get_world_faction_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get world faction summary: {str(e)}")


# ===== SYSTEM OPERATIONS ENDPOINTS =====

@router.post("/tick")
async def process_tick():
    """Process a world state tick"""
    try:
        service = await get_world_state_service()
        summary = await service.process_tick()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process tick: {str(e)}")


@router.post("/save")
async def save_state():
    """Save current state to repository"""
    try:
        service = await get_world_state_service()
        success = await service.save_state()
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save state: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_data(days_to_keep: int = Query(90, ge=1, description="Days of data to keep")):
    """Clean up old data beyond retention policy"""
    try:
        service = await get_world_state_service()
        result = await service.cleanup_old_data(days_to_keep)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup old data: {str(e)}")


@router.get("/regions/{region_id}/export")
async def export_region_history(
    region_id: str = Path(..., description="Region identifier"),
    start_time: Optional[datetime] = Query(None, description="Start time for export"),
    end_time: Optional[datetime] = Query(None, description="End time for export")
):
    """Export complete history for a region"""
    try:
        service = await get_world_state_service()
        export_data = await service.export_region_history(region_id, start_time, end_time)
        return export_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export region history: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        service = await get_world_state_service()
        status = await service.get_system_status()
        return {"status": "healthy", "initialized": status.get("initialized", False)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)} 