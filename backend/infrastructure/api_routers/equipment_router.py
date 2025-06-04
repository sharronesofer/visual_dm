"""
Equipment API Router

FastAPI router for equipment system HTTP endpoints.
Provides RESTful API for equipment management, character loadouts, and equipment operations.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Infrastructure imports
from backend.infrastructure.database import get_db
from backend.infrastructure.database.repositories.equipment_database_repository import (
    create_equipment_database_repository
)
from backend.infrastructure.database.repositories.equipment_template_database_repository import (
    create_equipment_template_database_repository
)

# Business logic imports
from backend.systems.equipment.services import (
    create_equipment_business_service,
    create_character_equipment_service
)

logger = logging.getLogger(__name__)

# Pydantic models for API
class EquipmentInstanceResponse(BaseModel):
    """Response model for equipment instance"""
    id: UUID
    template_id: str
    owner_id: UUID
    quality_tier: str
    custom_name: Optional[str] = None
    durability: float
    magical_effects: List[Dict[str, Any]] = []
    creation_date: str
    last_used: Optional[str] = None
    is_equipped: bool = False
    equipped_slot: Optional[str] = None

class EquipmentTemplateResponse(BaseModel):
    """Response model for equipment template"""
    id: str
    name: str
    item_type: str
    base_stats: Dict[str, int] = {}
    equipment_slots: List[str] = []
    base_value: int

class CharacterEquipmentLoadoutResponse(BaseModel):
    """Response model for character equipment loadout"""
    character_id: UUID
    equipped_items: List[EquipmentInstanceResponse]
    inventory_items: List[EquipmentInstanceResponse]
    equipment_slots: Dict[str, Optional[UUID]]
    total_stat_bonuses: Dict[str, int]
    equipped_count: int
    total_items: int

class CreateEquipmentRequest(BaseModel):
    """Request model for creating equipment"""
    template_id: str
    character_id: UUID
    quality_tier: str = "basic"
    magical_effects: List[Dict[str, Any]] = []
    custom_name: Optional[str] = None

class EquipItemRequest(BaseModel):
    """Request model for equipping item"""
    equipment_id: UUID
    slot: str

class UpdateEquipmentRequest(BaseModel):
    """Request model for updating equipment"""
    quality_tier: Optional[str] = None
    custom_name: Optional[str] = None
    durability: Optional[float] = None

class EquipmentStatsResponse(BaseModel):
    """Response model for equipment system statistics"""
    total_equipment_instances: int
    characters_with_equipment: int
    total_equipped_items: int
    total_unequipped_items: int
    database_stats: Dict[str, int]

# Router setup
router = APIRouter(prefix="/api/equipment", tags=["equipment"])


def get_equipment_services(db: Session = Depends(get_db)):
    """Dependency to create equipment services"""
    business_logic = create_equipment_business_service()
    equipment_repo = create_equipment_database_repository(db)
    template_repo = create_equipment_template_database_repository(db)
    
    character_equipment_service = create_character_equipment_service(
        business_logic, equipment_repo, template_repo
    )
    
    return {
        'business_logic': business_logic,
        'equipment_repo': equipment_repo,
        'template_repo': template_repo,
        'character_equipment': character_equipment_service
    }


# Equipment Instance Endpoints
@router.post("/instances", response_model=EquipmentInstanceResponse)
async def create_equipment_instance(
    request: CreateEquipmentRequest,
    services = Depends(get_equipment_services)
):
    """Create a new unique equipment instance for a character"""
    try:
        character_equipment_service = services['character_equipment']
        
        equipment = character_equipment_service.create_unique_equipment_for_character(
            character_id=request.character_id,
            template_id=request.template_id,
            quality_tier=request.quality_tier,
            magical_effects=request.magical_effects,
            custom_name=request.custom_name
        )
        
        return EquipmentInstanceResponse(
            id=equipment.id,
            template_id=equipment.template_id,
            owner_id=equipment.owner_id,
            quality_tier=equipment.quality_tier,
            custom_name=equipment.custom_name,
            durability=equipment.durability,
            magical_effects=equipment.magical_effects,
            creation_date=equipment.creation_date.isoformat(),
            last_used=equipment.last_used.isoformat() if equipment.last_used else None,
            is_equipped=False,
            equipped_slot=None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating equipment instance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create equipment instance")


@router.get("/instances/{equipment_id}", response_model=EquipmentInstanceResponse)
async def get_equipment_instance(
    equipment_id: UUID = Path(..., description="Equipment instance ID"),
    services = Depends(get_equipment_services)
):
    """Get specific equipment instance by ID"""
    try:
        equipment_repo = services['equipment_repo']
        equipment = equipment_repo.get_equipment_by_id(equipment_id)
        
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment instance not found")
        
        # Get slot info if equipped
        slot = equipment_repo.get_item_equipped_slot(equipment_id)
        
        return EquipmentInstanceResponse(
            id=equipment.id,
            template_id=equipment.template_id,
            owner_id=equipment.owner_id,
            quality_tier=equipment.quality_tier,
            custom_name=equipment.custom_name,
            durability=equipment.durability,
            magical_effects=equipment.magical_effects,
            creation_date=equipment.creation_date.isoformat(),
            last_used=equipment.last_used.isoformat() if equipment.last_used else None,
            is_equipped=slot is not None,
            equipped_slot=slot
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting equipment instance {equipment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get equipment instance")


@router.put("/instances/{equipment_id}", response_model=EquipmentInstanceResponse)
async def update_equipment_instance(
    equipment_id: UUID = Path(..., description="Equipment instance ID"),
    request: UpdateEquipmentRequest = Body(...),
    services = Depends(get_equipment_services)
):
    """Update equipment instance properties"""
    try:
        equipment_repo = services['equipment_repo']
        equipment = equipment_repo.get_equipment_by_id(equipment_id)
        
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment instance not found")
        
        # Update fields
        if request.quality_tier is not None:
            equipment.quality_tier = request.quality_tier
        if request.custom_name is not None:
            equipment.custom_name = request.custom_name
        if request.durability is not None:
            equipment.durability = request.durability
        
        success = equipment_repo.update_equipment(equipment)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update equipment")
        
        # Get updated equipment
        updated_equipment = equipment_repo.get_equipment_by_id(equipment_id)
        slot = equipment_repo.get_item_equipped_slot(equipment_id)
        
        return EquipmentInstanceResponse(
            id=updated_equipment.id,
            template_id=updated_equipment.template_id,
            owner_id=updated_equipment.owner_id,
            quality_tier=updated_equipment.quality_tier,
            custom_name=updated_equipment.custom_name,
            durability=updated_equipment.durability,
            magical_effects=updated_equipment.magical_effects,
            creation_date=updated_equipment.creation_date.isoformat(),
            last_used=updated_equipment.last_used.isoformat() if updated_equipment.last_used else None,
            is_equipped=slot is not None,
            equipped_slot=slot
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating equipment instance {equipment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update equipment instance")


@router.delete("/instances/{equipment_id}")
async def delete_equipment_instance(
    equipment_id: UUID = Path(..., description="Equipment instance ID"),
    services = Depends(get_equipment_services)
):
    """Delete equipment instance"""
    try:
        equipment_repo = services['equipment_repo']
        success = equipment_repo.remove_equipment(equipment_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Equipment instance not found")
        
        return {"message": "Equipment instance deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting equipment instance {equipment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete equipment instance")


# Character Equipment Endpoints
@router.get("/characters/{character_id}/loadout", response_model=CharacterEquipmentLoadoutResponse)
async def get_character_equipment_loadout(
    character_id: UUID = Path(..., description="Character ID"),
    services = Depends(get_equipment_services)
):
    """Get character's complete equipment loadout"""
    try:
        character_equipment_service = services['character_equipment']
        loadout = character_equipment_service.get_character_equipment_loadout(character_id)
        
        def convert_equipment(eq) -> EquipmentInstanceResponse:
            return EquipmentInstanceResponse(
                id=eq.id,
                template_id=eq.template_id,
                owner_id=eq.owner_id,
                quality_tier=eq.quality_tier,
                custom_name=eq.custom_name,
                durability=eq.durability,
                magical_effects=eq.magical_effects,
                creation_date=eq.creation_date.isoformat(),
                last_used=eq.last_used.isoformat() if eq.last_used else None,
                is_equipped=eq.id in [item.id for item in loadout.equipped_items],
                equipped_slot=None  # Would need to look up
            )
        
        return CharacterEquipmentLoadoutResponse(
            character_id=loadout.character_id,
            equipped_items=[convert_equipment(eq) for eq in loadout.equipped_items],
            inventory_items=[convert_equipment(eq) for eq in loadout.inventory_items],
            equipment_slots={slot: slot_info.equipped_item_id for slot, slot_info in loadout.equipment_slots.items()},
            total_stat_bonuses=loadout.total_stat_bonuses,
            equipped_count=loadout.get_equipped_count(),
            total_items=loadout.get_total_items()
        )
        
    except Exception as e:
        logger.error(f"Error getting character equipment loadout for {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get character equipment loadout")


@router.get("/characters/{character_id}/equipment", response_model=List[EquipmentInstanceResponse])
async def get_character_equipment(
    character_id: UUID = Path(..., description="Character ID"),
    equipped_only: bool = Query(False, description="Return only equipped items"),
    services = Depends(get_equipment_services)
):
    """Get all equipment owned by a character"""
    try:
        equipment_repo = services['equipment_repo']
        
        if equipped_only:
            equipment_list = equipment_repo.get_equipped_items(character_id)
        else:
            equipment_list = equipment_repo.get_character_equipment(character_id)
        
        def convert_equipment(eq) -> EquipmentInstanceResponse:
            slot = equipment_repo.get_item_equipped_slot(eq.id)
            return EquipmentInstanceResponse(
                id=eq.id,
                template_id=eq.template_id,
                owner_id=eq.owner_id,
                quality_tier=eq.quality_tier,
                custom_name=eq.custom_name,
                durability=eq.durability,
                magical_effects=eq.magical_effects,
                creation_date=eq.creation_date.isoformat(),
                last_used=eq.last_used.isoformat() if eq.last_used else None,
                is_equipped=slot is not None,
                equipped_slot=slot
            )
        
        return [convert_equipment(eq) for eq in equipment_list]
        
    except Exception as e:
        logger.error(f"Error getting character equipment for {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get character equipment")


@router.get("/characters/{character_id}/combat-stats", response_model=Dict[str, int])
async def get_character_combat_stats(
    character_id: UUID = Path(..., description="Character ID"),
    services = Depends(get_equipment_services)
):
    """Get character's combat stats from equipped equipment"""
    try:
        character_equipment_service = services['character_equipment']
        stats = character_equipment_service.get_character_combat_stats(character_id)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting character combat stats for {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get character combat stats")


# Equipment Operations
@router.post("/characters/{character_id}/equip")
async def equip_item_to_character(
    character_id: UUID = Path(..., description="Character ID"),
    request: EquipItemRequest = Body(...),
    services = Depends(get_equipment_services)
):
    """Equip an item to a character's equipment slot"""
    try:
        character_equipment_service = services['character_equipment']
        result = character_equipment_service.equip_item_to_character(
            character_id, request.equipment_id, request.slot
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {"message": result['message']}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error equipping item for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to equip item")


@router.post("/characters/{character_id}/unequip/{equipment_id}")
async def unequip_item_from_character(
    character_id: UUID = Path(..., description="Character ID"),
    equipment_id: UUID = Path(..., description="Equipment instance ID"),
    services = Depends(get_equipment_services)
):
    """Unequip an item from character"""
    try:
        character_equipment_service = services['character_equipment']
        result = character_equipment_service.unequip_item_from_character(
            character_id, equipment_id
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {"message": result['message']}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unequipping item for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unequip item")


@router.post("/instances/{equipment_id}/transfer/{new_owner_id}")
async def transfer_equipment(
    equipment_id: UUID = Path(..., description="Equipment instance ID"),
    new_owner_id: UUID = Path(..., description="New owner character ID"),
    services = Depends(get_equipment_services)
):
    """Transfer equipment to a different character"""
    try:
        equipment_repo = services['equipment_repo']
        success = equipment_repo.transfer_equipment(equipment_id, new_owner_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Equipment instance not found")
        
        return {"message": "Equipment transferred successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transferring equipment {equipment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to transfer equipment")


# Equipment Templates
@router.get("/templates", response_model=List[EquipmentTemplateResponse])
async def list_equipment_templates(
    item_type: Optional[str] = Query(None, description="Filter by item type"),
    quality_tier: Optional[str] = Query(None, description="Filter by quality tier"),
    services = Depends(get_equipment_services)
):
    """List available equipment templates"""
    try:
        template_repo = services['template_repo']
        templates = template_repo.list_templates(item_type, quality_tier)
        
        return [
            EquipmentTemplateResponse(
                id=template.id,
                name=template.name,
                item_type=template.item_type,
                base_stats=template.base_stats,
                equipment_slots=template.equipment_slots,
                base_value=template.base_value
            )
            for template in templates
        ]
        
    except Exception as e:
        logger.error(f"Error listing equipment templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list equipment templates")


@router.get("/templates/{template_id}", response_model=EquipmentTemplateResponse)
async def get_equipment_template(
    template_id: str = Path(..., description="Equipment template ID"),
    services = Depends(get_equipment_services)
):
    """Get specific equipment template"""
    try:
        template_repo = services['template_repo']
        template = template_repo.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Equipment template not found")
        
        return EquipmentTemplateResponse(
            id=template.id,
            name=template.name,
            item_type=template.item_type,
            base_stats=template.base_stats,
            equipment_slots=template.equipment_slots,
            base_value=template.base_value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting equipment template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get equipment template")


# System Statistics
@router.get("/statistics", response_model=EquipmentStatsResponse)
async def get_equipment_system_statistics(
    services = Depends(get_equipment_services)
):
    """Get equipment system statistics"""
    try:
        equipment_repo = services['equipment_repo']
        template_repo = services['template_repo']
        
        equipment_stats = equipment_repo.get_all_equipment_stats()
        
        if hasattr(template_repo, 'get_database_stats'):
            database_stats = template_repo.get_database_stats()
        else:
            database_stats = {'templates': 0, 'quality_tiers': 0, 'magical_effects': 0}
        
        return EquipmentStatsResponse(
            total_equipment_instances=equipment_stats['total_equipment_instances'],
            characters_with_equipment=equipment_stats['characters_with_equipment'],
            total_equipped_items=equipment_stats['total_equipped_items'],
            total_unequipped_items=equipment_stats['total_unequipped_items'],
            database_stats=database_stats
        )
        
    except Exception as e:
        logger.error(f"Error getting equipment system statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get equipment system statistics")


# Administrative Endpoints
@router.post("/admin/load-templates")
async def load_templates_from_json(
    services = Depends(get_equipment_services)
):
    """Load equipment templates from JSON files into database"""
    try:
        template_repo = services['template_repo']
        
        if hasattr(template_repo, 'load_templates_from_json'):
            loaded_count = template_repo.load_templates_from_json()
            return {"message": f"Loaded {loaded_count} templates from JSON"}
        else:
            raise HTTPException(status_code=501, detail="Template loading not supported by this repository")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading templates from JSON: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load templates from JSON") 