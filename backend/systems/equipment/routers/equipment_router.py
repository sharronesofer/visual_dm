"""
Equipment Router - Basic CRUD Operations

HTTP endpoints for basic equipment management according to Development Bible standards.
This router handles equipment instance creation, reading, updating, and deletion.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

# Authentication imports
from backend.infrastructure.auth.auth_user.services.auth_service import (
    get_current_active_user, check_user_character_access
)

from backend.infrastructure.persistence.equipment.equipment_dependencies import (
    EquipmentInstanceRepoType, EquipmentTemplateRepoType, BusinessLogicServiceType
)
from backend.systems.equipment.services.business_logic_service import (
    EquipmentInstanceData, EquipmentSlot, EquipmentBaseTemplate
)


router = APIRouter(prefix="/equipment", tags=["equipment"])


# Request/Response Models
class CreateEquipmentRequest(BaseModel):
    """Request model for creating equipment"""
    character_id: UUID
    template_id: str
    quality_tier: str = "basic"
    rarity_tier: str = "common"


class UpdateEquipmentRequest(BaseModel):
    """Request model for updating equipment"""
    current_durability: Optional[int] = None
    is_equipped: Optional[bool] = None


class EquipmentResponse(BaseModel):
    """Response model for equipment data"""
    id: UUID
    character_id: UUID
    template_id: str
    slot: str
    current_durability: int
    max_durability: int
    usage_count: int
    quality_tier: str
    rarity_tier: str
    is_equipped: bool
    equipment_set: Optional[str]
    enchantments: List[Dict[str, Any]]
    effective_stats: Dict[str, Any]
    created_at: str
    updated_at: str

    @classmethod
    def from_equipment_data(cls, equipment: EquipmentInstanceData) -> "EquipmentResponse":
        """Create response from equipment instance data"""
        return cls(
            id=equipment.id,
            character_id=equipment.character_id,
            template_id=equipment.template_id,
            slot=equipment.slot.value,
            current_durability=equipment.current_durability,
            max_durability=equipment.max_durability,
            usage_count=equipment.usage_count,
            quality_tier=equipment.quality_tier,
            rarity_tier=equipment.rarity_tier,
            is_equipped=equipment.is_equipped,
            equipment_set=equipment.equipment_set,
            enchantments=[{
                "type": ench.enchantment_type,
                "magnitude": ench.magnitude,
                "target_attribute": ench.target_attribute,
                "is_active": ench.is_active
            } for ench in equipment.enchantments],
            effective_stats=equipment.effective_stats,
            created_at=equipment.created_at.isoformat(),
            updated_at=equipment.updated_at.isoformat()
        )


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    request: CreateEquipmentRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> EquipmentResponse:
    """Create a new equipment instance (requires authentication)"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id = str(request.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create equipment for this character"
        )
    
    # Get dependencies using our simple pattern
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository,
        get_equipment_template_repository,
        get_equipment_business_logic_service
    )
    
    instance_repo = get_equipment_instance_repository()
    template_repo = get_equipment_template_repository()
    business_logic = get_equipment_business_logic_service()
    
    # Validate template exists
    template = template_repo.get_template(request.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment template '{request.template_id}' not found"
        )
    
    # Validate quality tier
    quality_tier_data = template_repo.get_quality_tier(request.quality_tier)
    if not quality_tier_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quality tier '{request.quality_tier}' not found"
        )
    
    # Validate rarity tier
    rarity_tier_data = template_repo.get_rarity_tier(request.rarity_tier)
    if not rarity_tier_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rarity tier '{request.rarity_tier}' not found"
        )
    
    # Validate quality and rarity are allowed for this template
    validation = business_logic.validate_equipment_creation(template, request.quality_tier, request.rarity_tier)
    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Equipment creation validation failed: {', '.join(validation['errors'])}"
        )
    
    try:
        # Create equipment using business logic
        equipment_data = business_logic.create_equipment_instance(
            character_id=request.character_id,
            template=template,
            quality_tier=quality_tier_data,
            rarity_tier=rarity_tier_data
        )
        
        # Save to database
        saved_equipment = instance_repo.create_equipment(equipment_data)
        
        return EquipmentResponse.from_equipment_data(saved_equipment)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create equipment: {str(e)}"
        )


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> EquipmentResponse:
    """Get equipment by ID (requires authentication and ownership)"""
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository
    )
    
    instance_repo = get_equipment_instance_repository()
    
    # Get equipment
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this equipment"
        )
    
    return EquipmentResponse.from_equipment_data(equipment)


@router.get("/character/{character_id}", response_model=List[EquipmentResponse])
async def get_character_equipment(
    character_id: UUID,
    equipped_only: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> List[EquipmentResponse]:
    """Get all equipment for a character (requires authentication and ownership)"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this character's equipment"
        )
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository
    )
    
    instance_repo = get_equipment_instance_repository()
    
    # Get equipment list
    equipment_list = instance_repo.get_character_equipment(character_id, equipped_only)
    
    return [EquipmentResponse.from_equipment_data(eq) for eq in equipment_list]


@router.get("/", response_model=List[EquipmentResponse])
async def list_equipment(
    character_id: Optional[UUID] = None,
    slot: Optional[str] = None,
    equipment_set: Optional[str] = None,
    quality_tier: Optional[str] = None,
    rarity_tier: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> List[EquipmentResponse]:
    """List equipment with optional filters (requires authentication)"""
    
    # If character_id is specified, check access
    if character_id:
        user_id = str(current_user["id"])
        character_id_str = str(character_id)
        
        has_access = await check_user_character_access(user_id, character_id_str, "read")
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this character's equipment"
            )
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository
    )
    
    instance_repo = get_equipment_instance_repository()
    
    # Convert slot string to EquipmentSlot enum if provided
    slot_enum = None
    if slot:
        try:
            slot_enum = EquipmentSlot(slot)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid equipment slot: {slot}"
            )
    
    # Get equipment list
    equipment_list = instance_repo.list_equipment(
        character_id=character_id,
        slot=slot_enum,
        equipment_set=equipment_set,
        quality_tier=quality_tier,
        rarity_tier=rarity_tier,
        limit=limit,
        offset=offset
    )
    
    return [EquipmentResponse.from_equipment_data(eq) for eq in equipment_list]


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: UUID,
    request: UpdateEquipmentRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> EquipmentResponse:
    """Update equipment instance (requires authentication and ownership)"""
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository
    )
    
    instance_repo = get_equipment_instance_repository()
    
    # Get equipment to check ownership
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this equipment"
        )
    
    # Build update dictionary
    updates = {}
    if request.current_durability is not None:
        updates["current_durability"] = request.current_durability
    if request.is_equipped is not None:
        updates["is_equipped"] = request.is_equipped
    
    # Update equipment
    updated_equipment = instance_repo.update_equipment(equipment_id, updates)
    if not updated_equipment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update equipment"
        )
    
    return EquipmentResponse.from_equipment_data(updated_equipment)


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> None:
    """Delete equipment instance (requires authentication and ownership)"""
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository
    )
    
    instance_repo = get_equipment_instance_repository()
    
    # Get equipment to check ownership
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this equipment"
        )
    
    # Delete equipment
    success = instance_repo.delete_equipment(equipment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete equipment"
        )


# Request models for template validation
class ValidateTemplateRequest(BaseModel):
    """Request model for template validation"""
    template_id: str
    name: str
    description: str
    slot: str
    equipment_set: Optional[str] = None
    base_stats: Dict[str, Any]
    allowed_quality_tiers: List[str]
    allowed_rarity_tiers: List[str]


@router.post("/templates/validation")
async def validate_template(
    request: ValidateTemplateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Validate equipment template data structure (requires authentication)"""
    
    # Check user has admin permissions for template validation
    user_permissions = current_user.get("permissions", [])
    user_roles = current_user.get("roles", [])
    
    if "admin" not in user_roles and "template_admin" not in user_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to validate templates"
        )
    
    try:
        validation_result = {
            "valid": True,
            "errors": [],
            "template_id": request.template_id,
            "warnings": []
        }
        
        # Validate template ID
        if not request.template_id or not request.template_id.strip():
            validation_result["errors"].append("Template ID cannot be empty")
            validation_result["valid"] = False
        
        # Note: Can't check existing templates without database layer
        validation_result["warnings"].append("Database layer required for duplicate template ID checking")
        
        # Validate name
        if not request.name or not request.name.strip():
            validation_result["errors"].append("Template name cannot be empty")
            validation_result["valid"] = False
        
        # Validate slot
        valid_slots = [
            "ring_1", "ring_2", "amulet", "boots", "gloves", "weapon",
            "off_hand", "earring_1", "earring_2", "hat", "pants", "chest"
        ]
        
        if request.slot not in valid_slots:
            validation_result["errors"].append(f"Invalid equipment slot: {request.slot}")
            validation_result["valid"] = False
        
        # Validate quality tiers
        valid_quality_tiers = ["basic", "military", "mastercraft"]
        for tier in request.allowed_quality_tiers:
            if tier not in valid_quality_tiers:
                validation_result["errors"].append(f"Invalid quality tier: {tier}")
                validation_result["valid"] = False
        
        # Validate rarity tiers
        valid_rarity_tiers = ["common", "rare", "epic", "legendary"]
        for tier in request.allowed_rarity_tiers:
            if tier not in valid_rarity_tiers:
                validation_result["errors"].append(f"Invalid rarity tier: {tier}")
                validation_result["valid"] = False
        
        return validation_result
        
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Validation error: {str(e)}"],
            "template_id": getattr(request, 'template_id', 'unknown'),
            "warnings": []
        }


# Create a separate router for character endpoints with proper routing
character_router = APIRouter(prefix="/characters", tags=["character-equipment"])


@character_router.get("/{character_id}/equipment")
async def get_character_equipment_summary(
    character_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get character equipment summary (requires authentication and ownership)"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this character's equipment"
        )
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Character equipment summary requires database layer completion"
    )


@character_router.get("/{character_id}/equipment/validate")
async def validate_character_equipment(
    character_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Validate character equipment configuration (requires authentication and ownership)"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to validate this character's equipment"
        )
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Character equipment validation requires database layer completion"
    )


@character_router.get("/{character_id}/equipment/repair-urgency")
async def get_equipment_repair_urgency(
    character_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get equipment repair urgency analysis (requires authentication and ownership)"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this character's equipment repair status"
        )
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Equipment repair urgency analysis requires database layer completion"
    )


@character_router.post("/{character_id}/equip")
async def equip_item_to_character(
    character_id: UUID, 
    equip_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Equip item to character (requires authentication and ownership)"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this character's equipment"
        )
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Character equipment operations require database layer completion"
    )


@router.post("/{equipment_id}/damage")
async def apply_durability_damage(
    equipment_id: UUID, 
    damage_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Apply durability damage to equipment (requires authentication and ownership)"""
    
    # Get dependencies to check equipment ownership
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository
    )
    
    instance_repo = get_equipment_instance_repository()
    
    # Get equipment to check ownership
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this equipment"
        )
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Equipment durability operations require database layer completion"
    )


@router.post("/{equipment_id}/repair")
async def repair_equipment(
    equipment_id: UUID, 
    repair_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Repair equipment (requires authentication and ownership)"""
    
    # Get dependencies to check equipment ownership
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository
    )
    
    instance_repo = get_equipment_instance_repository()
    
    # Get equipment to check ownership
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to repair this equipment"
        )
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Equipment repair operations require database layer completion"
    )


@router.get("/{equipment_id}/durability")
async def get_equipment_durability(
    equipment_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get equipment durability information (requires authentication and ownership)"""
    
    # Get dependencies to check equipment ownership
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository
    )
    
    instance_repo = get_equipment_instance_repository()
    
    # Get equipment to check ownership
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this equipment's durability"
        )
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Equipment durability information requires database layer completion"
    )


@router.get("/{equipment_id}/repair-cost")
async def get_equipment_repair_cost(
    equipment_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Calculate the cost to repair an equipment item"""
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository,
        get_equipment_business_logic_service
    )
    
    instance_repo = get_equipment_instance_repository()
    business_logic = get_equipment_business_logic_service()
    
    # Get equipment
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this equipment"
        )
    
    try:
        # Calculate repair cost
        repair_cost = business_logic.calculate_repair_cost(
            equipment.current_durability,
            equipment.max_durability,
            equipment.quality_tier
        )
        
        durability_lost = equipment.max_durability - equipment.current_durability
        repair_percentage = (durability_lost / equipment.max_durability) * 100
        
        return {
            "equipment_id": equipment_id,
            "current_durability": equipment.current_durability,
            "max_durability": equipment.max_durability,
            "durability_lost": durability_lost,
            "repair_percentage": round(repair_percentage, 1),
            "repair_cost": repair_cost,
            "quality_tier": equipment.quality_tier
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate repair cost: {str(e)}"
        )


@router.post("/durability/{equipment_id}/damage/combat", response_model=Dict[str, Any])
async def apply_combat_damage(
    equipment_id: UUID,
    equipment_type: str,
    combat_intensity: float,
    is_critical: bool,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Apply combat damage to an equipment item"""
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository,
        get_equipment_business_logic_service
    )
    
    instance_repo = get_equipment_instance_repository()
    business_logic = get_equipment_business_logic_service()
    
    # Get equipment
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this equipment"
        )
    
    try:
        # Apply combat damage
        usage_type = "critical_hit" if is_critical else "heavy_use"
        environmental_factor = combat_intensity
        
        new_durability, damage_details = business_logic.calculate_utilization_based_durability_loss(
            equipment.current_durability,
            equipment.quality_tier,
            usage_type,
            usage_count=1,
            environmental_factor=environmental_factor,
            is_critical=is_critical
        )
        
        # Update equipment
        old_durability = equipment.current_durability
        equipment.current_durability = max(0, new_durability)
        equipment.usage_count += 1
        equipment.updated_at = datetime.utcnow()
        
        updated_equipment = instance_repo.update_equipment(equipment)
        
        return {
            "equipment_id": equipment_id,
            "damage_applied": old_durability - equipment.current_durability,
            "old_durability": old_durability,
            "new_durability": equipment.current_durability,
            "equipment_type": equipment_type,
            "combat_intensity": combat_intensity,
            "is_critical": is_critical,
            "damage_details": damage_details,
            "status": business_logic.get_durability_status(equipment.current_durability)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply combat damage: {str(e)}"
        )


@router.post("/durability/{equipment_id}/damage/wear", response_model=Dict[str, Any])
async def apply_wear_damage(
    equipment_id: UUID,
    equipment_type: str,
    time_worn: float,
    environmental_factor: float,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Apply wear and tear damage to an equipment item"""
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository,
        get_equipment_business_logic_service
    )
    
    instance_repo = get_equipment_instance_repository()
    business_logic = get_equipment_business_logic_service()
    
    # Get equipment
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this equipment"
        )
    
    try:
        # Apply wear damage
        new_durability, damage_details = business_logic.calculate_durability_degradation(
            equipment.current_durability,
            equipment.quality_tier,
            time_worn,
            environmental_factor
        )
        
        # Update equipment
        old_durability = equipment.current_durability
        equipment.current_durability = max(0, new_durability)
        equipment.updated_at = datetime.utcnow()
        
        updated_equipment = instance_repo.update_equipment(equipment)
        
        return {
            "equipment_id": equipment_id,
            "wear_applied": old_durability - equipment.current_durability,
            "old_durability": old_durability,
            "new_durability": equipment.current_durability,
            "equipment_type": equipment_type,
            "time_worn": time_worn,
            "environmental_factor": environmental_factor,
            "damage_details": damage_details,
            "status": business_logic.get_durability_status(equipment.current_durability)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply wear damage: {str(e)}"
        )


@router.post("/durability/{equipment_id}/repair", response_model=Dict[str, Any])
async def repair_equipment(
    equipment_id: UUID,
    repair_amount: Optional[str] = None,
    full_repair: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Repair an equipment item"""
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository,
        get_equipment_business_logic_service
    )
    
    instance_repo = get_equipment_instance_repository()
    business_logic = get_equipment_business_logic_service()
    
    # Get equipment
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this equipment"
        )
    
    try:
        old_durability = equipment.current_durability
        
        if full_repair or repair_amount is None:
            # Full repair
            equipment.current_durability = equipment.max_durability
            repair_cost = business_logic.calculate_repair_cost(
                0, equipment.max_durability, equipment.quality_tier
            )
        else:
            # Partial repair
            repair_points = int(repair_amount) if repair_amount.isdigit() else 0
            equipment.current_durability = min(
                equipment.max_durability,
                equipment.current_durability + repair_points
            )
            repair_cost = business_logic.calculate_repair_cost(
                equipment.current_durability, equipment.max_durability, equipment.quality_tier
            )
        
        equipment.last_repaired = datetime.utcnow()
        equipment.updated_at = datetime.utcnow()
        
        updated_equipment = instance_repo.update_equipment(equipment)
        
        return {
            "equipment_id": equipment_id,
            "repair_amount": equipment.current_durability - old_durability,
            "old_durability": old_durability,
            "new_durability": equipment.current_durability,
            "repair_cost": repair_cost,
            "full_repair": full_repair,
            "status": business_logic.get_durability_status(equipment.current_durability),
            "message": "Equipment repaired successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to repair equipment: {str(e)}"
        )


@router.get("/durability/{equipment_id}/status", response_model=Dict[str, Any])
async def get_durability_status(
    equipment_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get the durability status of an equipment item"""
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository,
        get_equipment_business_logic_service
    )
    
    instance_repo = get_equipment_instance_repository()
    business_logic = get_equipment_business_logic_service()
    
    # Get equipment
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this equipment"
        )
    
    try:
        durability_percentage = (equipment.current_durability / equipment.max_durability) * 100
        status = business_logic.get_durability_status(equipment.current_durability)
        stat_penalty = business_logic.calculate_stat_penalties(equipment.current_durability)
        is_functional = business_logic.is_equipment_functional(equipment.current_durability)
        counts_for_set = business_logic.counts_for_set_bonus(equipment.current_durability)
        
        return {
            "equipment_id": equipment_id,
            "current_durability": equipment.current_durability,
            "max_durability": equipment.max_durability,
            "durability_percentage": round(durability_percentage, 1),
            "status": status,
            "stat_penalty_percentage": round(stat_penalty * 100, 1),
            "is_functional": is_functional,
            "counts_for_set_bonus": counts_for_set,
            "usage_count": equipment.usage_count,
            "quality_tier": equipment.quality_tier,
            "last_repaired": equipment.last_repaired.isoformat() if equipment.last_repaired else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get durability status: {str(e)}"
        )


@router.get("/durability/{equipment_id}/history", response_model=Dict[str, Any])
async def get_durability_history(
    equipment_id: UUID,
    limit: int = 10,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get durability change history for an equipment item"""
    
    # Get dependencies
    from backend.infrastructure.persistence.equipment.equipment_dependencies import (
        get_equipment_instance_repository
    )
    
    instance_repo = get_equipment_instance_repository()
    
    # Get equipment
    equipment = instance_repo.get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check user has access to this character's equipment
    user_id = str(current_user["id"])
    character_id = str(equipment.character_id)
    
    has_access = await check_user_character_access(user_id, character_id, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this equipment"
        )
    
    try:
        # Get maintenance history
        history = instance_repo.get_maintenance_history(equipment_id, limit)
        
        return {
            "equipment_id": equipment_id,
            "current_durability": equipment.current_durability,
            "max_durability": equipment.max_durability,
            "total_usage_count": equipment.usage_count,
            "history": [{
                "action_type": record.action_type,
                "performed_at": record.performed_at.isoformat(),
                "durability_before": record.durability_before,
                "durability_after": record.durability_after,
                "durability_change": record.durability_change(),
                "success": record.success,
                "notes": record.notes,
                "gold_cost": record.gold_cost
            } for record in history]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get durability history: {str(e)}"
        ) 