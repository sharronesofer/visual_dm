"""
World State API Router - Infrastructure Layer

Provides RESTful API endpoints for world state operations
as specified in the Development Bible API contracts.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel, Field
from uuid import UUID

from backend.systems.world_state.services.services import WorldStateService, create_world_state_service
from backend.systems.world_state.world_types import StateCategory, WorldRegion


# === REQUEST/RESPONSE MODELS ===

class StateVariableRequest(BaseModel):
    """Request model for setting state variables"""
    key: str
    value: Any
    region_id: Optional[str] = None
    category: StateCategory = StateCategory.OTHER
    reason: Optional[str] = None


class StateVariableResponse(BaseModel):
    """Response model for state variables"""
    key: str
    value: Any
    region_id: Optional[str] = None
    category: str
    last_updated: datetime
    reason: Optional[str] = None


class WorldEventRequest(BaseModel):
    """Request model for creating world events"""
    event_type: str
    description: str
    affected_regions: Optional[List[str]] = []
    category: StateCategory = StateCategory.OTHER
    metadata: Optional[Dict[str, Any]] = {}


class WorldEventResponse(BaseModel):
    """Response model for world events"""
    event_id: str
    event_type: str
    description: str
    timestamp: datetime
    affected_regions: List[str]
    category: str
    metadata: Dict[str, Any]


class ChaosEventRequest(BaseModel):
    """Request model for injecting chaos events"""
    event_type: str
    severity: float = Field(ge=0.1, le=10.0)
    target_regions: Optional[List[str]] = []
    description: Optional[str] = None


class WorldStateResponse(BaseModel):
    """Response model for current world state"""
    state_variables: Dict[str, Any]
    regions: Dict[str, Any]
    global_resources: Dict[str, Any]
    recent_events: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class HistoryQueryResponse(BaseModel):
    """Response model for historical data queries"""
    changes: List[Dict[str, Any]]
    total_count: int
    time_range: Dict[str, datetime]


class ProcessTickResponse(BaseModel):
    """Response model for tick processing"""
    tick_id: str
    processed_at: datetime
    changes_applied: int
    events_generated: int
    status: str


# === ROUTER SETUP ===

router = APIRouter(prefix="/api/world-state", tags=["world-state"])


# === DEPENDENCY INJECTION ===

async def get_world_state_service() -> WorldStateService:
    """Dependency to get world state service instance"""
    service = await create_world_state_service()
    if not service._initialized:
        await service.initialize()
    return service


# === API ENDPOINTS ===

@router.get("/", response_model=WorldStateResponse)
async def get_current_world_state(
    service: WorldStateService = Depends(get_world_state_service),
    regions: Optional[List[str]] = Query(None, description="Filter by specific regions"),
    categories: Optional[List[StateCategory]] = Query(None, description="Filter by categories")
):
    """Get the current world state with optional filtering"""
    try:
        # Get complete state
        if regions:
            state_data = {}
            for region_id in regions:
                region_state = await service.get_region_state(region_id)
                state_data[region_id] = region_state
        else:
            # Get global state
            state_data = await service.query_state()
        
        # Filter by categories if specified
        if categories:
            filtered_data = {}
            for key, value in state_data.items():
                if any(cat.value in key for cat in categories):
                    filtered_data[key] = value
            state_data = filtered_data
        
        return WorldStateResponse(
            state_variables=state_data,
            regions={},  # TODO: Implement proper region data aggregation
            global_resources={},  # TODO: Implement resource aggregation
            recent_events=[],  # TODO: Implement recent events query
            metadata={"retrieved_at": datetime.utcnow()}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve world state: {str(e)}")


@router.get("/history", response_model=HistoryQueryResponse)
async def get_world_state_history(
    service: WorldStateService = Depends(get_world_state_service),
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    region_id: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[StateCategory] = Query(None, description="Filter by category"),
    limit: int = Query(100, le=1000, description="Maximum number of records")
):
    """Get historical data for world state values"""
    try:
        # Default time range if not provided
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get historical summaries
        summaries = await service.get_historical_summary(
            start_time=start_time,
            end_time=end_time,
            region_id=region_id
        )
        
        # Convert to change format
        changes = []
        for summary in summaries[:limit]:
            changes.extend(summary.get('key_changes', []))
        
        return HistoryQueryResponse(
            changes=changes[:limit],
            total_count=len(changes),
            time_range={"start": start_time, "end": end_time}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.patch("/")
async def update_world_state(
    request: StateVariableRequest,
    service: WorldStateService = Depends(get_world_state_service)
):
    """Update a specific value in the world state"""
    try:
        success = await service.set_state_variable(
            key=request.key,
            value=request.value,
            region_id=request.region_id,
            category=request.category,
            reason=request.reason
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update state variable")
        
        return {"status": "success", "message": f"Updated {request.key}"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update state: {str(e)}")


@router.post("/events", response_model=WorldEventResponse)
async def create_world_event(
    request: WorldEventRequest,
    service: WorldStateService = Depends(get_world_state_service)
):
    """Create a new world event"""
    try:
        event_id = await service.record_world_event(
            event_type=request.event_type,
            description=request.description,
            affected_regions=request.affected_regions,
            category=request.category,
            metadata=request.metadata
        )
        
        return WorldEventResponse(
            event_id=event_id,
            event_type=request.event_type,
            description=request.description,
            timestamp=datetime.utcnow(),
            affected_regions=request.affected_regions or [],
            category=request.category.value,
            metadata=request.metadata or {}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@router.get("/events")
async def get_world_events(
    service: WorldStateService = Depends(get_world_state_service),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    category: Optional[StateCategory] = Query(None, description="Filter by category"),
    region_id: Optional[str] = Query(None, description="Filter by affected region"),
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    limit: int = Query(50, le=500, description="Maximum number of events")
):
    """Get world events with optional filtering"""
    try:
        # For now, return empty list - TODO: Implement proper event querying
        return {
            "events": [],
            "total_count": 0,
            "has_more": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")


@router.get("/events/{event_id}")
async def get_world_event(
    event_id: str = Path(..., description="Event ID"),
    service: WorldStateService = Depends(get_world_state_service)
):
    """Get a specific world event by ID"""
    try:
        # TODO: Implement specific event retrieval
        raise HTTPException(status_code=404, detail="Event not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve event: {str(e)}")


@router.get("/related-events/{event_id}")
async def get_related_events(
    event_id: str = Path(..., description="Event ID"),
    service: WorldStateService = Depends(get_world_state_service)
):
    """Get events related to the specified event"""
    try:
        # TODO: Implement related event lookup
        return {"related_events": [], "total_count": 0}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve related events: {str(e)}")


@router.post("/process-tick", response_model=ProcessTickResponse)
async def process_world_tick(
    service: WorldStateService = Depends(get_world_state_service)
):
    """Manually trigger a world tick processing cycle"""
    try:
        tick_result = await service.process_tick()
        
        return ProcessTickResponse(
            tick_id=str(UUID()),
            processed_at=datetime.utcnow(),
            changes_applied=tick_result.get('changes_applied', 0),
            events_generated=tick_result.get('events_generated', 0),
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process tick: {str(e)}")


@router.post("/chaos-event")
async def inject_chaos_event(
    request: ChaosEventRequest,
    service: WorldStateService = Depends(get_world_state_service)
):
    """Inject a chaos event into the world"""
    try:
        event_id = await service.record_world_event(
            event_type=f"chaos_{request.event_type}",
            description=request.description or f"Chaos event: {request.event_type}",
            affected_regions=request.target_regions or [],
            category=StateCategory.OTHER,
            metadata={
                "chaos_event": True,
                "severity": request.severity,
                "event_type": request.event_type
            }
        )
        
        return {"event_id": event_id, "status": "chaos_injected", "severity": request.severity}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inject chaos event: {str(e)}")


@router.get("/regions")
async def get_world_regions(
    service: WorldStateService = Depends(get_world_state_service)
):
    """Get a list of valid world regions"""
    try:
        # Return predefined regions from WorldRegion enum
        regions = [
            {"id": region.value, "name": region.value.title(), "type": "predefined"}
            for region in WorldRegion
        ]
        
        # TODO: Add dynamic regions from current world state
        
        return {"regions": regions, "total_count": len(regions)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve regions: {str(e)}")


@router.get("/categories")
async def get_state_categories(
    service: WorldStateService = Depends(get_world_state_service)
):
    """Get a list of valid state categories"""
    try:
        categories = [
            {"id": category.value, "name": category.value.title(), "description": f"{category.value.title()} related state"}
            for category in StateCategory
        ]
        
        return {"categories": categories, "total_count": len(categories)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve categories: {str(e)}")


# === HEALTH CHECK ===

@router.get("/health")
async def health_check(
    service: WorldStateService = Depends(get_world_state_service)
):
    """Check the health of the world state system"""
    try:
        status = await service.get_system_status()
        return {
            "status": "healthy",
            "service_initialized": service._initialized,
            "manager_available": service.manager is not None,
            "system_status": status
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "service_initialized": False
        } 