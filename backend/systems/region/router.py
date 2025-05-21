"""
Region system API router.

This module contains the FastAPI router for the region system, managing:
- Region state (GET/POST/DELETE)
- Global event logging (with rumor propagation)
- Player questlog access
- Region map generation and access

It serves as the gateway for regional updates, world memory, and region-linked quest tracking.
It connects with region, world_log, npc, questlog, and rumor systems.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Body
from datetime import datetime
import json
import random

from backend.systems.region.schemas import RegionSchema, EventSchema, QuestlogEntrySchema, RegionGenerationSchema
from backend.systems.region.service import region_service, RegionService
from backend.world.utils.world_event_utils import log_world_event
from backend.npcs.npc_rumor_utils import sync_event_beliefs

router = APIRouter(
    prefix="/regions",
    tags=["Regions"],
)

# Load terrain types from JSON
try:
    with open("backend/data/rules_json/land_types.json") as f:
        LAND_TYPES = json.load(f)
    ALL_TERRAINS = list(LAND_TYPES.keys())
except Exception as e:
    # Fallback values if file can't be loaded
    ALL_TERRAINS = ["forest", "plains", "mountain", "swamp", "coast", "desert"]
    print(f"Warning: Could not load land_types.json: {str(e)}")

# --- Region CRUD Operations ---

@router.get("/{region_id}", response_model=RegionSchema)
def get_region(region_id: str):
    """
    Get a region by ID.
    
    Args:
        region_id: The ID of the region to get
        
    Returns:
        The region
        
    Raises:
        HTTPException: If the region is not found
    """
    region = region_service.get_region_by_id(region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found")
    return region

@router.post("/{region_id}", response_model=RegionSchema)
def update_region(region_id: str, data: Dict[str, Any] = Body(...)):
    """
    Update a region.
    
    Args:
        region_id: The ID of the region to update
        data: The updated region data
        
    Returns:
        The updated region
        
    Raises:
        HTTPException: If the region is not found
    """
    # Add timestamp
    data["last_updated"] = datetime.utcnow().isoformat()
    
    # Update the region
    updated_region = region_service.update_region(region_id, data)
    if not updated_region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found")
    return updated_region

@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_region(region_id: str):
    """
    Delete a region.
    
    Args:
        region_id: The ID of the region to delete
        
    Raises:
        HTTPException: If the region is not found
    """
    success = region_service.delete_region(region_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found")
    return None

@router.get("/{region_id}/details", response_model=Dict[str, Any])
def get_region_details_with_weather(region_id: str):
    """
    Get region details with weather.
    
    Args:
        region_id: The ID of the region to get
        
    Returns:
        Region details with weather
        
    Raises:
        HTTPException: If the region is not found or weather is unavailable
    """
    details = region_service.get_region_details_with_weather(region_id)
    if not details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found or weather unavailable")
    return details

@router.get("/by_continent/{continent_id}", response_model=List[RegionSchema])
def get_regions_by_continent(continent_id: str):
    """
    Get all regions in a continent.
    
    Args:
        continent_id: The ID of the continent
        
    Returns:
        List of regions in the continent
    """
    regions = region_service.get_regions_by_continent(continent_id)
    return regions

@router.get("/", response_model=List[RegionSchema])
def list_all_regions():
    """
    List all regions.
    
    Returns:
        List of all regions
    """
    return region_service.list_all_regions()

# --- Region Map Operations ---

@router.get("/map/{region_id}")
def get_region_map(region_id: str):
    """
    Fetch the full tile map for a region.
    
    Args:
        region_id: The ID of the region
        
    Returns:
        The region map with tiles
        
    Raises:
        HTTPException: If there is an error fetching the map
    """
    try:
        tiles = region_service.get_region_map_tiles(region_id)
        return {"tiles": tiles}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching region map: {str(e)}"
        )

@router.post("/seed/{region_id}")
def seed_region(region_id: str):
    """
    Seeds a basic 10x10 region with clustered terrain tags.
    
    Args:
        region_id: The ID of the region to seed
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If there is an error seeding the region
    """
    try:
        width = 10
        height = 10
        terrain_types = ["forest", "plains", "mountain", "swamp", "coast", "desert"]
        
        # Generate a seeded region map
        result = region_service.seed_region_map(
            region_id=region_id,
            width=width,
            height=height,
            terrain_types=terrain_types
        )
        
        return {"message": f"Region '{region_id}' seeded successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error seeding region: {str(e)}"
        )

@router.post("/generate")
def generate_region(params: RegionGenerationSchema = Body(...)):
    """
    Create a new region with starting coordinates.
    
    Args:
        params: Parameters for region generation
        
    Returns:
        Information about the generated region
        
    Raises:
        HTTPException: If there is an error generating the region
    """
    try:
        result = region_service.generate_region(params.seed_x, params.seed_y)
        
        return {
            "message": f"Region '{result['region_id']}' generated successfully.",
            "region_id": result["region_id"],
            "tiles_created": result["tiles_created"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating region: {str(e)}"
        )

@router.post("/generate/new")
def generate_new_region():
    """
    Shortcut to generate a new region at the origin (0,0).
    
    Returns:
        Information about the generated region
        
    Raises:
        HTTPException: If there is an error generating the region
    """
    try:
        result = region_service.generate_region(seed_x=0, seed_y=0)
        
        return {
            "message": f"Region '{result['region_id']}' generated successfully.",
            "region_id": result["region_id"],
            "tiles_created": result["tiles_created"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating region: {str(e)}"
        )

# --- Event and NPC Notification Operations ---

@router.post("/log_event")
def log_event_and_notify_npcs(event_data: EventSchema = Body(...)):
    """
    Log a world event and notify NPCs in the region.
    
    Args:
        event_data: The event data to log
        
    Returns:
        Information about the logged event
        
    Raises:
        HTTPException: If there is an error logging the event
    """
    try:
        region = event_data.region
        if not region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing region name"
            )
        
        # Log the event and notify NPCs
        event = log_world_event(event_data.dict())
        count = sync_event_beliefs(region, event)
        
        return {
            "message": f"Event logged and shared with {count} NPCs.",
            "event_id": event["event_id"],
            "region": region
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging event: {str(e)}"
        )

# --- Questlog Operations ---

@router.get("/questlog/{character_id}")
def get_questlog(character_id: str):
    """
    Get a character's questlog.
    
    Args:
        character_id: The ID of the character
        
    Returns:
        The character's questlog
    """
    questlog = region_service.get_character_questlog(character_id)
    return {"character_id": character_id, "questlog": questlog}

@router.post("/questlog/{character_id}")
def add_quest(character_id: str, quest_entry: QuestlogEntrySchema = Body(...)):
    """
    Add a quest to a character's questlog.
    
    Args:
        character_id: The ID of the character
        quest_entry: The quest to add
        
    Returns:
        Information about the added quest
    """
    entry = {
        "quest": quest_entry.quest,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    region_service.add_quest_to_character(character_id, entry)
    
    return {"message": "Quest added.", "quest_entry": entry} 