"""
World State API Router

Provides FastAPI endpoints for interacting with the World State system.
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel

from backend.systems.world_state.core.manager import WorldStateManager
from backend.systems.world_state.core.types import WorldRegion, StateCategory, StateChangeType
from backend.utils.auth import get_current_user

# Create router
router = APIRouter(
    prefix="/api/world-state",
    tags=["world-state"],
    responses={404: {"description": "Not found"}},
)

# Models for request/response data
class WorldStateResponse(BaseModel):
    data: Dict[str, Any]
    metadata: Dict[str, Any]

class WorldStatePatchRequest(BaseModel):
    key: str
    value: Any
    region: Optional[str] = None
    category: Optional[str] = None

class WorldEventRequest(BaseModel):
    event_type: str
    description: str
    location: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    entity_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class WorldEventResponse(BaseModel):
    id: str
    type: str
    description: str
    timestamp: str
    location: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    entity_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Endpoints
@router.get("/", response_model=WorldStateResponse)
async def get_world_state(current_user = Depends(get_current_user)):
    """Get the current world state."""
    # Instantiate the manager
    manager = WorldStateManager()
    
    # Load the current state
    state = manager.get_world_state()
    
    # Get metadata
    metadata = manager.get_metadata()
    
    return {
        "data": state,
        "metadata": metadata
    }

@router.get("/history", response_model=Dict[str, Any])
async def get_world_state_history(
    keys: Optional[List[str]] = Query(None, description="Specific state keys to retrieve history for"),
    since: Optional[str] = Query(None, description="ISO timestamp to get history since"),
    limit: int = Query(10, description="Maximum number of history entries per key"),
    current_user = Depends(get_current_user)
):
    """Get historical data for world state values."""
    # Instantiate the manager
    manager = WorldStateManager()
    
    # Get history
    history = manager.get_history(keys=keys, since=since, limit=limit)
    
    return {"history": history}

@router.patch("/", response_model=Dict[str, Any])
async def update_world_state(
    update: WorldStatePatchRequest,
    current_user = Depends(get_current_user)
):
    """Update a specific value in the world state."""
    # Instantiate the manager
    manager = WorldStateManager()
    
    # Build the region enum if provided
    region = None
    if update.region:
        try:
            region = WorldRegion[update.region.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid region: {update.region}")
    
    # Build the category enum if provided
    category = None
    if update.category:
        try:
            category = StateCategory[update.category.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {update.category}")
    
    # Update the state
    result = manager.set_value(
        update.key, 
        update.value, 
        region=region,
        category=category,
        actor_id=current_user.id
    )
    
    return {"success": result, "key": update.key}

@router.post("/events", response_model=WorldEventResponse)
async def create_world_event(
    event: WorldEventRequest,
    current_user = Depends(get_current_user)
):
    """Create a new world event."""
    # Instantiate the manager
    manager = WorldStateManager()
    
    # Build the region enum if provided
    region = None
    if event.region:
        try:
            region = WorldRegion[event.region.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid region: {event.region}")
    
    # Build the category enum if provided
    category = None
    if event.category:
        try:
            category = StateCategory[event.category.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {event.category}")
    
    # Create the event
    from backend.systems.world_state.utils.world_event_utils import create_world_event
    
    created_event = create_world_event(
        event_type=event.event_type,
        description=event.description,
        location=event.location,
        category=category,
        region=region,
        entity_id=event.entity_id,
        metadata=event.metadata
    )
    
    return created_event

@router.get("/events", response_model=List[WorldEventResponse])
async def get_world_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    location: Optional[str] = Query(None, description="Filter by location"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    limit: int = Query(10, description="Maximum number of events to return"),
    current_user = Depends(get_current_user)
):
    """Get world events with optional filtering."""
    # Build the category enum if provided
    category_enum = None
    if category:
        try:
            category_enum = StateCategory[category.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    # Filter events
    from backend.systems.world_state.utils.world_event_utils import (
        filter_events_by_category, 
        filter_events_by_location
    )
    
    if category_enum:
        events = filter_events_by_category(category_enum, limit=limit)
    elif location:
        events = filter_events_by_location(location, limit=limit)
    else:
        # TODO: Implement more sophisticated filtering
        # For now, just return an empty list
        events = []
    
    # Apply additional filters
    if event_type:
        events = [e for e in events if e.get("type") == event_type]
    
    if region:
        events = [e for e in events if e.get("region") == region]
    
    if entity_id:
        events = [e for e in events if e.get("entity_id") == entity_id]
    
    return events[:limit]

@router.get("/events/{event_id}", response_model=WorldEventResponse)
async def get_world_event(
    event_id: str = Path(..., description="ID of the event to retrieve"),
    current_user = Depends(get_current_user)
):
    """Get a specific world event by ID."""
    from pathlib import Path
    
    # Check if the event exists
    event_path = Path("data/world_state/events") / f"{event_id}.json"
    if not event_path.exists():
        raise HTTPException(status_code=404, detail=f"Event not found: {event_id}")
    
    # Load the event
    import json
    with open(event_path, "r") as f:
        event = json.load(f)
    
    return event

@router.get("/related-events/{event_id}", response_model=List[WorldEventResponse])
async def get_related_events(
    event_id: str = Path(..., description="ID of the event to get related events for"),
    relationship_types: Optional[List[str]] = Query(None, description="Filter by relationship types"),
    current_user = Depends(get_current_user)
):
    """Get events related to the specified event."""
    from backend.systems.world_state.utils.world_event_utils import get_related_events
    
    # Get related events
    related_events = get_related_events(event_id, relationship_types)
    
    return related_events

@router.post("/process-tick", response_model=Dict[str, Any])
async def process_world_tick(current_user = Depends(get_current_user)):
    """Manually trigger a world tick processing cycle."""
    # Instantiate the manager
    manager = WorldStateManager()
    
    # Process tick
    result = manager.process_tick()
    
    return {"success": result}

@router.post("/chaos-event", response_model=Dict[str, Any])
async def inject_chaos_event(
    event_type: str = Query(..., description="Type of chaos event to inject"),
    region: Optional[str] = Query(None, description="Region to target"),
    current_user = Depends(get_current_user)
):
    """Inject a chaos event into the world."""
    from backend.systems.world_state.utils.world_event_utils import inject_chaos_event as inject_chaos
    
    # Inject the event
    event = inject_chaos(event_type, region)
    
    return {"success": True, "event": event}

@router.get("/regions", response_model=List[str])
async def get_world_regions(current_user = Depends(get_current_user)):
    """Get a list of valid world regions."""
    return [r.name for r in WorldRegion]

@router.get("/categories", response_model=List[str])
async def get_state_categories(current_user = Depends(get_current_user)):
    """Get a list of valid state categories."""
    return [c.name for c in StateCategory] 