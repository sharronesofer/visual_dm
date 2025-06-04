"""
Character Equipment Integration Router

FastAPI router for character-equipment integration endpoints.
Provides character-specific equipment management functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
import logging

from backend.infrastructure.database import get_db
from backend.infrastructure.services.equipment.character_equipment_integration import CharacterEquipmentIntegration
from backend.systems.equipment.schemas import (
    EquipmentInstanceResponse,
    CharacterEquipmentResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/characters", tags=["character-equipment"])

def get_character_equipment_service(db: Session = Depends(get_db)) -> CharacterEquipmentIntegration:
    """Dependency to get character equipment integration service."""
    return CharacterEquipmentIntegration(db)

@router.post("/{character_id}/equipment/setup-starting", response_model=Dict[str, Any])
async def setup_starting_equipment(
    character_id: str = Path(..., description="Character ID"),
    character_data: Dict[str, Any] = Body(..., description="Character creation data including race, background, level"),
    service: CharacterEquipmentIntegration = Depends(get_character_equipment_service)
):
    """
    Set up starting equipment for a character based on race, background, and level.
    
    This endpoint is typically called when a new character is created to provide
    them with appropriate starting gear.
    """
    try:
        logger.info(f"Setting up starting equipment for character {character_id}")
        
        equipment_instances = service.setup_starting_equipment(character_id, character_data)
        
        return {
            "character_id": character_id,
            "starting_equipment": [
                {
                    "id": eq.id,
                    "name": eq.custom_name,
                    "template_id": eq.template_id,
                    "is_equipped": eq.is_equipped,
                    "equipment_slot": eq.equipment_slot
                }
                for eq in equipment_instances
            ],
            "total_items": len(equipment_instances),
            "message": f"Successfully set up {len(equipment_instances)} starting equipment items"
        }
        
    except Exception as e:
        logger.error(f"Error setting up starting equipment for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to setup starting equipment: {str(e)}")

@router.get("/{character_id}/equipment/summary", response_model=Dict[str, Any])
async def get_character_equipment_summary(
    character_id: str = Path(..., description="Character ID"),
    service: CharacterEquipmentIntegration = Depends(get_character_equipment_service)
):
    """
    Get comprehensive equipment summary for a character including computed stats and bonuses.
    
    Returns detailed information about the character's equipment including:
    - Total equipment count
    - Equipped vs unequipped items
    - Stat bonuses from equipped gear
    - Equipment value and durability averages
    """
    try:
        summary = service.get_character_equipment_summary(character_id)
        return summary
        
    except Exception as e:
        logger.error(f"Error getting equipment summary for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get equipment summary: {str(e)}")

@router.get("/{character_id}/equipment/recommendations", response_model=Dict[str, Any])
async def get_equipment_recommendations(
    character_id: str = Path(..., description="Character ID"),
    character_level: Optional[int] = Query(None, description="Character level (optional, will be looked up if not provided)"),
    service: CharacterEquipmentIntegration = Depends(get_character_equipment_service)
):
    """
    Get equipment upgrade recommendations based on character level and current gear.
    
    Analyzes the character's current equipment and suggests upgrades appropriate
    for their level, including quality tier improvements and missing equipment slots.
    """
    try:
        recommendations = service.recommend_equipment_upgrades(character_id, character_level)
        
        return {
            "character_id": character_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "message": f"Generated {len(recommendations)} equipment recommendations"
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/{character_id}/equipment/stat-bonuses", response_model=Dict[str, int])
async def get_character_equipment_stat_bonuses(
    character_id: str = Path(..., description="Character ID"),
    service: CharacterEquipmentIntegration = Depends(get_character_equipment_service)
):
    """
    Calculate stat bonuses provided by the character's equipped items.
    
    Returns a dictionary of stat bonuses that should be applied to the character's
    base stats, including penalties for damaged equipment.
    """
    try:
        stat_bonuses = service.apply_equipment_to_character_stats(character_id)
        return stat_bonuses
        
    except Exception as e:
        logger.error(f"Error calculating stat bonuses for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate stat bonuses: {str(e)}")

@router.post("/{character_id}/equipment/level-up", response_model=Dict[str, Any])
async def handle_character_level_up(
    character_id: str = Path(..., description="Character ID"),
    level_data: Dict[str, Any] = Body(..., description="Level up data including new level"),
    service: CharacterEquipmentIntegration = Depends(get_character_equipment_service)
):
    """
    Handle equipment-related changes when a character levels up.
    
    Processes level-up equipment recommendations and quality tier milestones.
    """
    try:
        new_level = level_data.get("new_level")
        if not new_level:
            raise HTTPException(status_code=400, detail="new_level is required in request body")
        
        result = service.on_character_level_up(character_id, new_level)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling level-up for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to handle level-up: {str(e)}")

@router.post("/{character_id}/equipment/character-created", response_model=Dict[str, Any])
async def handle_character_created(
    character_id: str = Path(..., description="Character ID"),
    character_data: Dict[str, Any] = Body(..., description="Character creation data"),
    service: CharacterEquipmentIntegration = Depends(get_character_equipment_service)
):
    """
    Handle equipment setup when a new character is created.
    
    This is a convenience endpoint that combines starting equipment setup
    with equipment summary generation for new characters.
    """
    try:
        result = service.on_character_created(character_id, character_data)
        return result
        
    except Exception as e:
        logger.error(f"Error handling character creation for {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to handle character creation: {str(e)}")

@router.get("/equipment/health", include_in_schema=False)
async def character_equipment_health_check():
    """Health check endpoint for character-equipment integration."""
    return {
        "status": "healthy", 
        "service": "character_equipment_integration",
        "message": "Character-Equipment integration service is operational"
    } 