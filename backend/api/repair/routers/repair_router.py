"""
Repair API Router

FastAPI router for repair operations, replacing the crafting system.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uuid

from backend.systems.repair.services.repair_service import RepairService
from backend.infrastructure.services.equipment.durability_service import DurabilityService

router = APIRouter(prefix="/repair", tags=["repair"])

# Pydantic models for API requests/responses
class RepairEstimateRequest(BaseModel):
    """Request model for repair cost estimation."""
    equipment_id: str = Field(..., description="Equipment ID to repair")
    target_durability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Target durability (0.0-1.0)")

class RepairEstimateResponse(BaseModel):
    """Response model for repair cost estimation."""
    equipment_id: str
    current_durability: float
    target_durability: float
    estimated_cost: int
    required_materials: List[Dict[str, Any]]
    estimated_time: int  # seconds
    success_rate: float
    recommended_station: str

class PerformRepairRequest(BaseModel):
    """Request model for performing repairs."""
    equipment_id: str = Field(..., description="Equipment ID to repair")
    station_id: Optional[str] = Field(None, description="Repair station ID")
    target_durability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Target durability")
    use_materials: List[Dict[str, Any]] = Field(default_factory=list, description="Materials to use")

class PerformRepairResponse(BaseModel):
    """Response model for repair operations."""
    success: bool
    equipment_id: str
    new_durability: float
    cost_paid: int
    materials_used: List[Dict[str, Any]]
    experience_gained: int
    message: str

class EquipmentStatusResponse(BaseModel):
    """Response model for equipment status."""
    equipment_id: str
    name: str
    quality: str
    current_durability: float
    max_durability: float
    status: str  # excellent, good, worn, damaged, broken
    days_until_next_decay: int
    repair_needed: bool

class RepairStationResponse(BaseModel):
    """Response model for repair stations."""
    station_id: str
    name: str
    station_type: str
    efficiency_bonus: float
    specializations: List[str]
    available: bool
    location: Optional[str] = None

# Dependency injection
def get_repair_service() -> RepairService:
    """Get repair service instance."""
    return RepairService()

def get_durability_service() -> DurabilityService:
    """Get durability service instance."""
    return DurabilityService()

# API Endpoints

@router.get("/stations", response_model=List[RepairStationResponse])
async def get_repair_stations(
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    repair_service: RepairService = Depends(get_repair_service)
):
    """
    Get available repair stations.
    
    Returns list of repair stations, optionally filtered by equipment type.
    """
    try:
        stations = repair_service.get_available_stations(equipment_type)
        return [RepairStationResponse(**station) for station in stations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve repair stations: {str(e)}"
        )

@router.post("/estimate", response_model=RepairEstimateResponse)
async def get_repair_estimate(
    request: RepairEstimateRequest,
    repair_service: RepairService = Depends(get_repair_service)
):
    """
    Get repair cost estimate for equipment.
    
    Provides detailed information about repair requirements and costs.
    """
    try:
        estimate = repair_service.get_repair_estimate(
            equipment_id=request.equipment_id,
            target_durability=request.target_durability
        )
        return RepairEstimateResponse(**estimate)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to estimate repair cost: {str(e)}"
        )

@router.post("/perform", response_model=PerformRepairResponse)
async def perform_repair(
    request: PerformRepairRequest,
    repair_service: RepairService = Depends(get_repair_service)
):
    """
    Perform equipment repair.
    
    Executes the repair operation and updates equipment durability.
    """
    try:
        result = repair_service.perform_repair(
            equipment_id=request.equipment_id,
            station_id=request.station_id,
            target_durability=request.target_durability,
            materials=request.use_materials
        )
        return PerformRepairResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to perform repair: {str(e)}"
        )

@router.get("/equipment/{equipment_id}/status", response_model=EquipmentStatusResponse)
async def get_equipment_status(
    equipment_id: str,
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Get current status of specific equipment.
    
    Returns detailed durability and status information.
    """
    try:
        status_info = durability_service.get_equipment_status(equipment_id)
        return EquipmentStatusResponse(**status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment not found or status unavailable: {str(e)}"
        )

@router.get("/equipment/damaged", response_model=List[EquipmentStatusResponse])
async def get_damaged_equipment(
    character_id: Optional[str] = Query(None, description="Filter by character ID"),
    min_damage_level: Optional[float] = Query(0.3, ge=0.0, le=1.0, description="Minimum damage level"),
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Get list of damaged equipment that needs repair.
    
    Returns equipment below specified condition threshold.
    """
    try:
        damaged_equipment = durability_service.get_damaged_equipment(
            character_id=character_id,
            damage_threshold=min_damage_level
        )
        return [EquipmentStatusResponse(**eq) for eq in damaged_equipment]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve damaged equipment: {str(e)}"
        )

@router.post("/equipment/{equipment_id}/decay")
async def simulate_equipment_decay(
    equipment_id: str,
    days: int = Query(1, ge=1, le=30, description="Number of days to simulate"),
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Simulate equipment decay over time (for testing/admin purposes).
    
    Applies time-based durability reduction to equipment.
    """
    try:
        result = durability_service.simulate_decay(equipment_id, days)
        return {
            "equipment_id": equipment_id,
            "days_simulated": days,
            "durability_before": result["durability_before"],
            "durability_after": result["durability_after"],
            "status_change": result.get("status_change", False)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to simulate decay: {str(e)}"
        )

@router.get("/materials", response_model=List[Dict[str, Any]])
async def get_repair_materials():
    """
    Get available repair materials and their properties.
    
    Returns list of materials that can be used for repairs.
    """
    try:
        # This could be expanded to load from the building_materials.json
        # For now, return basic material types
        materials = [
            {
                "material_id": "iron_scraps",
                "name": "Iron Scraps",
                "category": "basic",
                "repair_bonus": 0.1,
                "cost": 10
            },
            {
                "material_id": "iron_ingot",
                "name": "Iron Ingot", 
                "category": "refined",
                "repair_bonus": 0.2,
                "cost": 25
            },
            {
                "material_id": "steel_ingot",
                "name": "Steel Ingot",
                "category": "refined", 
                "repair_bonus": 0.3,
                "cost": 50
            },
            {
                "material_id": "leather",
                "name": "Leather",
                "category": "basic",
                "repair_bonus": 0.15,
                "cost": 15
            },
            {
                "material_id": "fine_cloth",
                "name": "Fine Cloth",
                "category": "refined",
                "repair_bonus": 0.25,
                "cost": 30
            }
        ]
        return materials
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve repair materials: {str(e)}"
        )

# Legacy compatibility endpoint (for gradual migration)
@router.get("/legacy/craftable", response_model=List[Dict[str, Any]])
async def get_legacy_craftable_items(
    character_skills: str = Query(..., description="JSON string of character skills"),
    repair_service: RepairService = Depends(get_repair_service)
):
    """
    Legacy endpoint that mimics crafting 'get_craftable_items' API.
    
    This endpoint provides backwards compatibility during migration.
    Returns repairable equipment in crafting-compatible format.
    """
    import json
    
    try:
        skills = json.loads(character_skills)
        
        # Use the compatibility service
        from backend.systems.repair.compat.crafting_bridge import create_crafting_compatibility_service
        compat_service = create_crafting_compatibility_service()
        
        craftable_items = compat_service.get_craftable_items(skills)
        return craftable_items
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format for character_skills parameter"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve legacy craftable items: {str(e)}"
        )

@router.get("/equipment/{equipment_id}/condition", response_model=Dict[str, Any])
async def get_equipment_condition(
    equipment_id: str,
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Get detailed condition analysis for specific equipment.
    
    Returns comprehensive condition effects and status information.
    """
    try:
        # Get equipment to check current durability
        # This would normally come from equipment service
        current_durability = 45.5  # Mock for now
        
        condition_effects = durability_service.get_condition_effects(current_durability)
        return {
            "equipment_id": equipment_id,
            **condition_effects
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment condition unavailable: {str(e)}"
        )

@router.get("/equipment/condition-summary", response_model=Dict[str, Any])
async def get_condition_summary(
    character_id: Optional[str] = Query(None, description="Filter by character ID"),
    durability_service: DurabilityService = Depends(get_durability_service)
):
    """
    Get summary of equipment conditions across all equipment.
    
    Returns statistics about equipment condition distribution.
    """
    try:
        # This would get all equipment for character and analyze conditions
        # Mock implementation for now
        summary = {
            "total_equipment": 10,
            "condition_breakdown": {
                "perfect": 2,
                "excellent": 3, 
                "good": 2,
                "worn": 2,
                "damaged": 1,
                "very_damaged": 0,
                "broken": 0
            },
            "needs_repair": 3,
            "urgent_repairs": 1,
            "average_durability": 75.5
        }
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate condition summary: {str(e)}"
        ) 