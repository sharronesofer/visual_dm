"""FastAPI router for world map endpoints."""

from typing import List, Dict, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from uuid import uuid4

from ..database import get_db
from .region import Region, RegionProperties, RegionManager
from .websocket import WorldStateManager
from ..core.api.fastapi import APIResponse, APIError, NotFoundError
from backend.app.models.market import MarketItem
from backend.app.repositories.market_repository import MarketItemRepository

router = APIRouter(tags=["world"])

# Initialize managers
region_manager = RegionManager()
world_state = WorldStateManager(region_manager)

class RegionCreate(BaseModel):
    """Schema for creating a region."""
    name: str = Field(..., description="Region name")
    description: str = Field(..., description="Region description")
    boundary: List[List[float]] = Field(
        ...,
        description="List of [x, y] coordinates defining the region boundary"
    )
    color: List[int] = Field(
        ...,
        description="RGB color values [r, g, b]",
        min_items=3,
        max_items=3
    )
    border_color: List[int] = Field(
        ...,
        description="RGB border color values [r, g, b]",
        min_items=3,
        max_items=3
    )
    z_index: Optional[int] = Field(0, description="Z-index for rendering order")

class RegionUpdate(BaseModel):
    """Schema for updating a region."""
    name: Optional[str] = Field(None, description="Region name")
    description: Optional[str] = Field(None, description="Region description")
    color: Optional[List[int]] = Field(
        None,
        description="RGB color values [r, g, b]",
        min_items=3,
        max_items=3
    )
    border_color: Optional[List[int]] = Field(
        None,
        description="RGB border color values [r, g, b]",
        min_items=3,
        max_items=3
    )
    z_index: Optional[int] = Field(None, description="Z-index for rendering order")
    is_visible: Optional[bool] = Field(None, description="Region visibility")

class MarketResponse(BaseModel):
    id: int
    name: str
    type: str
    description: str = ""
    # Add location fields if available in the model

@router.post("/regions/", response_model=APIResponse[Dict[str, str]])
async def create_region(region: RegionCreate, db: Session = Depends(get_db)):
    """Create a new region.
    
    Args:
        region: Region creation data
        db: Database session
        
    Returns:
        Dict containing the new region ID
    """
    try:
        # Create region ID
        region_id = str(uuid4())
        
        # Create region properties
        properties = RegionProperties(
            name=region.name,
            description=region.description,
            color=tuple(region.color),
            border_color=tuple(region.border_color),
            z_index=region.z_index
        )
        
        # Create region
        new_region = Region(
            region_id=region_id,
            boundary=[(x, y) for x, y in region.boundary],
            properties=properties
        )
        
        # Add to manager
        region_manager.add_region(new_region)
        
        # Notify clients
        await world_state.handle_region_update(region_id)
        
        return APIResponse.created(data={"id": region_id})
    except Exception as e:
        raise APIError(str(e))

@router.put("/regions/{region_id}", response_model=APIResponse[dict])
async def update_region(
    region_id: str,
    update: RegionUpdate,
    db: Session = Depends(get_db)
):
    """Update a region.
    
    Args:
        region_id: ID of region to update
        update: Region update data
        db: Database session
    """
    try:
        if region_id not in region_manager.regions:
            raise NotFoundError("Region not found")
            
        # Update properties
        if update.name is not None:
            region_manager.update_region_property(region_id, "name", update.name)
        if update.description is not None:
            region_manager.update_region_property(region_id, "description", update.description)
        if update.color is not None:
            region_manager.update_region_property(region_id, "color", tuple(update.color))
        if update.border_color is not None:
            region_manager.update_region_property(region_id, "border_color", tuple(update.border_color))
        if update.z_index is not None:
            region_manager.update_region_property(region_id, "z_index", update.z_index)
        if update.is_visible is not None:
            region_manager.update_region_property(region_id, "is_visible", update.is_visible)
            
        # Notify clients
        await world_state.handle_region_update(region_id)
        
        return APIResponse.success(data={"status": "success"})
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.delete("/regions/{region_id}", response_model=APIResponse[dict])
async def delete_region(region_id: str, db: Session = Depends(get_db)):
    """Delete a region.
    
    Args:
        region_id: ID of region to delete
        db: Database session
    """
    try:
        if region_id not in region_manager.regions:
            raise NotFoundError("Region not found")
            
        # Remove region
        region_manager.remove_region(region_id)
        
        # Notify clients
        await world_state.handle_region_update(region_id)
        
        return APIResponse.success(data={"status": "success"})
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.get("/regions/", response_model=APIResponse[Dict[str, dict]])
async def list_regions(db: Session = Depends(get_db)):
    """List all regions.
    
    Args:
        db: Database session
        
    Returns:
        List of region data
    """
    try:
        data = {
            region_id: {
                "name": region.properties.name,
                "description": region.properties.description,
                "color": region.properties.color,
                "border_color": region.properties.border_color,
                "z_index": region.properties.z_index,
                "is_visible": region.properties.is_visible,
                "is_selected": region.properties.is_selected,
                "boundary": list(region.boundary.exterior.coords)
            }
            for region_id, region in region_manager.regions.items()
        }
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    width: float,
    height: float
):
    """WebSocket endpoint for real-time updates.
    
    Args:
        websocket: WebSocket connection
        client_id: Client identifier
        width: Initial viewport width
        height: Initial viewport height
    """
    try:
        # Connect client
        await world_state.connections.connect(websocket, client_id, width, height)
        
        # Send initial viewport update
        await world_state.send_viewport_update(client_id)
        
        # Handle messages
        while True:
            message = await websocket.receive_json()
            await world_state.handle_client_message(
                client_id,
                message["type"],
                message["data"]
            )
            
    except WebSocketDisconnect:
        world_state.connections.disconnect(client_id)
    except Exception as e:
        await websocket.close(code=1001, reason=str(e))

@router.get("/markets/discovered", response_model=APIResponse[List[MarketResponse]])
async def get_discovered_markets(db: Session = Depends(get_db)):
    """Return all discovered markets for the current user (placeholder: all markets)."""
    try:
        repo = MarketItemRepository()
        markets = repo.get_all(db)
        # Convert to response model
        market_list = [
            MarketResponse(
                id=m.id,
                name=m.name,
                type=m.type,
                description=m.description or ""
            ) for m in markets
        ]
        return APIResponse.success(data=market_list)
    except Exception as e:
        raise APIError(str(e)) 