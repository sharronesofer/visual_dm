"""
Equipment API Router

FastAPI router for equipment quality and durability management.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from datetime import datetime

from backend.infrastructure.services.equipment.durability_service import DurabilityService
from backend.systems.equipment.models.equipment_quality import EquipmentQuality, QualityConfig

router = APIRouter(prefix="/equipment", tags=["equipment"])

# Pydantic models for API requests/responses
class EquipmentQualityResponse(BaseModel):
    """Response model for equipment quality information."""
    quality: str
    durability_weeks: int
    repair_cost_multiplier: float
    value_multiplier: float
    sprite_suffix: str
    daily_decay_rate: float

class EquipmentCreateRequest(BaseModel):
    """Request model for creating new equipment."""
    name: str = Field(..., description="Equipment name")
    base_type: str = Field(..., description="Equipment type (weapon, armor, etc.)")
    quality: str = Field(..., description="Equipment quality (basic, military, mastercraft)")
    base_value: int = Field(..., ge=1, description="Base value in gold")

class EquipmentResponse(BaseModel):
    """Response model for equipment."""
    equipment_id: str
    name: str
    base_type: str
    quality: str
    current_durability: float
    max_durability: float
    value: int
    status: str
    created_at: datetime
    last_used: Optional[datetime] = None

class BulkDurabilityUpdateRequest(BaseModel):
    """Request model for bulk durability updates."""
    equipment_ids: List[str] = Field(..., description="List of equipment IDs")
    days_passed: int = Field(1, ge=1, le=30, description="Number of days to simulate")

# Dependency injection
def get_durability_service() -> DurabilityService:
    """Get durability service instance."""
    return DurabilityService()

# API Endpoints

@router.get("/qualities", response_model=List[EquipmentQualityResponse])
async def get_equipment_qualities():
    """
    Get all available equipment qualities and their properties.
    
    Returns configuration for basic, military, and mastercraft quality tiers.
    """
    try:
        qualities = []
        for quality in EquipmentQuality:
            config = QualityConfig.get_config(quality)
            qualities.append(EquipmentQualityResponse(
                quality=quality.value,
                durability_weeks=config.durability_weeks,
                repair_cost_multiplier=config.repair_cost_multiplier,
                value_multiplier=config.value_multiplier,
                sprite_suffix=config.sprite_suffix,
                daily_decay_rate=config.get_daily_decay_rate()
            ))
        return qualities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve equipment qualities: {str(e)}"
        )

@router.post("/create", response_model=EquipmentResponse)
async def create_equipment(
    request: EquipmentCreateRequest,
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Create new equipment with specified quality.
    
    Creates equipment with full durability based on quality tier.
    """
    try:
        equipment = durability_service.create_equipment(
            name=request.name,
            base_type=request.base_type,
            quality=request.quality,
            base_value=request.base_value
        )
        return EquipmentResponse(**equipment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create equipment: {str(e)}"
        )

@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: str,
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Get detailed information about specific equipment.
    
    Returns full equipment details including durability status.
    """
    try:
        equipment = durability_service.get_equipment_details(equipment_id)
        return EquipmentResponse(**equipment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment not found: {str(e)}"
        )

@router.patch("/{equipment_id}/durability")
async def update_equipment_durability(
    equipment_id: str,
    new_durability: float = Query(..., ge=0.0, le=1.0, description="New durability (0.0-1.0)"),
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Manually update equipment durability.
    
    For admin purposes or special game events.
    """
    try:
        result = durability_service.set_durability(equipment_id, new_durability)
        return {
            "equipment_id": equipment_id,
            "old_durability": result["old_durability"],
            "new_durability": result["new_durability"],
            "status_changed": result["status_changed"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update durability: {str(e)}"
        )

@router.post("/{equipment_id}/use")
async def use_equipment(
    equipment_id: str,
    intensity: float = Query(1.0, ge=0.1, le=5.0, description="Usage intensity multiplier"),
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Apply usage wear to equipment.
    
    Simulates equipment degradation from use in combat or activities.
    """
    try:
        result = durability_service.apply_usage_wear(equipment_id, intensity)
        return {
            "equipment_id": equipment_id,
            "durability_before": result["durability_before"],
            "durability_after": result["durability_after"],
            "wear_applied": result["wear_applied"],
            "status": result["new_status"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to apply usage wear: {str(e)}"
        )

@router.post("/bulk/daily-update")
async def bulk_daily_durability_update(
    request: BulkDurabilityUpdateRequest,
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Apply daily durability decay to multiple equipment items.
    
    For automated daily maintenance tasks.
    """
    try:
        results = durability_service.bulk_update_durability(
            equipment_ids=request.equipment_ids,
            days_passed=request.days_passed
        )
        
        return {
            "equipment_count": len(request.equipment_ids),
            "days_simulated": request.days_passed,
            "equipment_updated": len(results["updated"]),
            "equipment_broken": len(results["broken"]),
            "equipment_unchanged": len(results["unchanged"]),
            "detailed_results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to perform bulk update: {str(e)}"
        )

@router.get("/character/{character_id}/all", response_model=List[EquipmentResponse])
async def get_character_equipment(
    character_id: str,
    include_broken: bool = Query(False, description="Include broken equipment"),
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Get all equipment for a specific character.
    
    Returns character's equipment with current durability status.
    """
    try:
        equipment_list = durability_service.get_character_equipment(
            character_id=character_id,
            include_broken=include_broken
        )
        return [EquipmentResponse(**eq) for eq in equipment_list]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve character equipment: {str(e)}"
        )

@router.get("/analytics/durability-distribution")
async def get_durability_distribution(
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    quality: Optional[str] = Query(None, description="Filter by quality"),
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Get analytics on equipment durability distribution.
    
    Useful for game balance and monitoring equipment health.
    """
    try:
        distribution = durability_service.get_durability_analytics(
            equipment_type=equipment_type,
            quality=quality
        )
        return distribution
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve durability analytics: {str(e)}"
        )

@router.post("/{equipment_id}/restore")
async def restore_equipment(
    equipment_id: str,
    target_durability: float = Query(1.0, ge=0.0, le=1.0, description="Target durability"),
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Fully restore equipment durability (admin/cheat function).
    
    Bypasses normal repair mechanics for testing or admin purposes.
    """
    try:
        result = durability_service.restore_equipment(equipment_id, target_durability)
        return {
            "equipment_id": equipment_id,
            "restored_from": result["old_durability"],
            "restored_to": result["new_durability"],
            "fully_restored": result["new_durability"] >= 1.0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to restore equipment: {str(e)}"
        ) 