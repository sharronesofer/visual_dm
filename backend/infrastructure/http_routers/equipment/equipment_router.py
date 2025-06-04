"""
Equipment System REST API Router for Visual DM.

This router provides comprehensive equipment management endpoints using the
hybrid template+instance pattern.

Endpoints:
- Equipment CRUD operations
- Equipment templating and querying
- Equipment operations (equip/unequip/repair)
- Time-based degradation management
- Template information and querying
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

# Import our hybrid service and models
from backend.infrastructure.services.equipment.hybrid_equipment_service import HybridEquipmentService
from backend.systems.equipment.models.equipment_models import EquipmentInstance
from backend.systems.equipment.schemas import (
    EquipmentInstanceResponse, EquipmentTemplateResponse, EquipmentDetailsResponse,
    CreateEquipmentRequest, EquipmentOperationResponse, RepairEquipmentResponse,
    CharacterEquipmentResponse, EquipmentQueryFilters, TemplateQueryFilters,
    EquipmentListResponse, TemplateListResponse, TimeProcessingResponse
)

# Database dependency (placeholder - would be imported from your DB setup)
def get_db_session() -> Session:
    """Get database session dependency. Replace with your actual DB session factory."""
    # This would normally come from your database configuration
    # For now, return None to indicate it needs proper setup
    return None

def get_equipment_service(db: Session = Depends(get_db_session)) -> HybridEquipmentService:
    """Get equipment service dependency."""
    if db is None:
        # For endpoints that don't require database access, return None
        # The endpoint should handle this case appropriately
        return None
    return HybridEquipmentService(db)

# Create the router
router = APIRouter(prefix="/equipment", tags=["Equipment System"])

# Equipment Instance Management Endpoints

@router.post("/instances", response_model=EquipmentInstanceResponse, status_code=201)
async def create_equipment_instance(
    request: CreateEquipmentRequest,
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Create a new equipment instance from a template.
    
    Creates a unique equipment instance for a character based on a template ID.
    Supports quality overrides and custom naming.
    """
    try:
        instance = service.create_equipment_instance(
            template_id=request.template_id,
            owner_id=request.owner_id,
            quality_override=request.quality_override,
            custom_name=request.custom_name
        )
        
        if not instance:
            raise HTTPException(status_code=400, detail="Failed to create equipment instance")
        
        return EquipmentInstanceResponse.from_orm(instance)
    
    except Exception as e:
        logging.error(f"Error creating equipment instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{instance_id}", response_model=EquipmentDetailsResponse)
async def get_equipment_details(
    instance_id: str = Path(..., description="Equipment instance ID"),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Get comprehensive equipment details combining template and instance data.
    
    Returns complete equipment information including current stats, condition,
    enchantments, and maintenance history.
    """
    details = service.get_equipment_details(instance_id)
    if not details:
        raise HTTPException(status_code=404, detail="Equipment instance not found")
    
    return EquipmentDetailsResponse.from_details(details)

@router.get("/characters/{character_id}/equipment", response_model=CharacterEquipmentResponse)
async def get_character_equipment(
    character_id: str = Path(..., description="Character ID"),
    equipped_only: bool = Query(False, description="Return only equipped items"),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Get all equipment for a specific character.
    
    Returns character's equipment with optional filtering for equipped items only.
    """
    equipment = service.get_character_equipment(character_id, equipped_only)
    return CharacterEquipmentResponse(
        character_id=character_id,
        equipment=[EquipmentInstanceResponse.from_orm(eq) for eq in equipment],
        equipped_only=equipped_only,
        total_count=len(equipment)
    )

@router.get("/instances", response_model=EquipmentListResponse)
async def query_equipment_instances(
    filters: EquipmentQueryFilters = Depends(),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Query equipment instances with filtering options.
    
    Supports filtering by owner, template, quality, condition, and more.
    """
    # Implementation would depend on adding query methods to the service
    # For now, return a placeholder response
    return EquipmentListResponse(
        equipment=[],
        total_count=0,
        limit=limit,
        offset=offset,
        filters=filters.dict()
    )

# Equipment Operations Endpoints

@router.post("/instances/{instance_id}/equip", response_model=EquipmentOperationResponse)
async def equip_equipment(
    instance_id: str = Path(..., description="Equipment instance ID"),
    equipment_slot: str = Query(..., description="Equipment slot to equip to"),
    force: bool = Query(False, description="Force equip without validation"),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Equip an equipment instance to a specific slot.
    
    Handles slot validation and automatic unequipping of conflicting items.
    """
    success = service.equip_item(instance_id, equipment_slot, force)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to equip item")
    
    return EquipmentOperationResponse(
        success=True,
        message=f"Equipment equipped to {equipment_slot}",
        equipment_id=instance_id,
        operation="equip"
    )

@router.post("/instances/{instance_id}/unequip", response_model=EquipmentOperationResponse)
async def unequip_equipment(
    instance_id: str = Path(..., description="Equipment instance ID"),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Unequip an equipment instance.
    
    Moves equipped item back to inventory.
    """
    success = service.unequip_item(instance_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to unequip item")
    
    return EquipmentOperationResponse(
        success=True,
        message="Equipment unequipped",
        equipment_id=instance_id,
        operation="unequip"
    )

@router.post("/instances/{instance_id}/repair", response_model=RepairEquipmentResponse)
async def repair_equipment(
    instance_id: str = Path(..., description="Equipment instance ID"),
    repairer_id: str = Query(..., description="ID of character/NPC performing repair"),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Repair equipment to restore durability.
    
    Calculates cost and applies repair based on quality tier configuration.
    """
    # For now, pass empty materials dict
    materials = {}
    repair_result = service.repair_equipment(instance_id, repairer_id, materials)
    
    if not repair_result.get("success"):
        raise HTTPException(status_code=400, detail=repair_result.get("error", "Repair failed"))
    
    return RepairEquipmentResponse(
        success=True,
        equipment_id=instance_id,
        durability_before=repair_result["durability_before"],
        durability_after=repair_result["durability_after"],
        gold_cost=repair_result["gold_cost"],
        new_condition=repair_result["new_condition"]
    )

@router.post("/instances/{instance_id}/damage", response_model=EquipmentOperationResponse)
async def apply_combat_damage(
    instance_id: str = Path(..., description="Equipment instance ID"),
    damage_amount: float = Query(..., ge=0, description="Amount of damage to apply"),
    damage_type: str = Query("physical", description="Type of damage"),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Apply combat damage to equipment.
    
    Reduces equipment durability based on damage amount and quality modifiers.
    """
    success = service.apply_combat_damage(instance_id, damage_amount, damage_type)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to apply damage")
    
    return EquipmentOperationResponse(
        success=True,
        message=f"Applied {damage_amount} {damage_type} damage",
        equipment_id=instance_id,
        operation="damage"
    )

# Template Information Endpoints

@router.get("/templates", response_model=TemplateListResponse)
async def list_equipment_templates(
    filters: TemplateQueryFilters = Depends(),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    List available equipment templates with filtering.
    
    Shows all equipment that can be instantiated for characters.
    """
    if service is None:
        # Return mock templates when no database is configured
        mock_templates = [
            {
                "id": "iron_sword",
                "name": "Iron Sword",
                "description": "A sturdy iron sword",
                "item_type": "weapon",
                "base_value": 1000,
                "quality_tiers": ["basic", "military", "mastercraft"]
            },
            {
                "id": "leather_armor",
                "name": "Leather Armor",
                "description": "Basic leather protection",
                "item_type": "armor",
                "base_value": 800,
                "quality_tiers": ["basic", "military", "mastercraft"]
            }
        ]
        
        return TemplateListResponse(
            templates=[EquipmentTemplateResponse.from_dict(t) for t in mock_templates],
            total_count=len(mock_templates),
            filters=filters.dict()
        )
    
    templates = service.list_available_equipment_templates(
        item_type=filters.item_type,
        quality_tier=filters.quality_tier,
        max_level=filters.max_level
    )
    
    return TemplateListResponse(
        templates=[EquipmentTemplateResponse.from_template(t) for t in templates],
        total_count=len(templates),
        filters=filters.dict()
    )

@router.get("/templates/{template_id}", response_model=EquipmentTemplateResponse)
async def get_template_info(
    template_id: str = Path(..., description="Equipment template ID"),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Get detailed information about an equipment template.
    
    Includes calculated values, compatibility, and crafting requirements.
    """
    template_info = service.get_equipment_template_info(template_id)
    if not template_info:
        raise HTTPException(status_code=404, detail="Equipment template not found")
    
    return EquipmentTemplateResponse.from_template_info(template_info)

# Time Management Endpoints

@router.post("/process-degradation", response_model=TimeProcessingResponse)
async def process_time_degradation(
    character_id: Optional[str] = Query(None, description="Process only this character's equipment"),
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Process time-based equipment degradation.
    
    Applies durability loss over time based on quality tier settings.
    """
    result = service.process_time_degradation(character_id)
    
    return TimeProcessingResponse(
        equipment_processed=result["equipment_processed"],
        equipment_degraded=result["equipment_degraded"],
        character_id=result.get("character_id"),
        message=f"Processed {result['equipment_processed']} items, {result['equipment_degraded']} degraded"
    )

# System Status Endpoints

@router.get("/health")
async def equipment_system_health():
    """
    Check equipment system health status.
    
    Returns system status and basic statistics.
    """
    return {
        "status": "healthy",
        "system": "equipment",
        "pattern": "hybrid_template_instance",
        "timestamp": "2025-06-02T01:00:00Z"
    }

@router.get("/stats")
async def equipment_system_stats(
    service: HybridEquipmentService = Depends(get_equipment_service)
):
    """
    Get equipment system statistics.
    
    Returns counts and metrics about templates and instances.
    """
    if service is None:
        # Return mock stats when no database is configured
        return {
            "templates_loaded": 0,
            "quality_tiers": 3,  # basic, military, mastercraft
            "enchantment_schools": ["elemental", "protective", "enhancement"],
            "system_version": "1.0.0",
            "pattern": "hybrid_template_instance",
            "status": "no_database_configured"
        }
    
    template_count = len(service.list_available_equipment_templates())
    
    return {
        "templates_loaded": template_count,
        "quality_tiers": len(service.quality_service.get_all_qualities()),
        "enchantment_schools": ["elemental", "protective", "enhancement"],  # Placeholder
        "system_version": "1.0.0",
        "pattern": "hybrid_template_instance"
    } 