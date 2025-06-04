"""
Equipment Management Router - Character Equipment Operations

HTTP endpoints for character-equipment interactions according to Development Bible standards.
This router handles equipping, unequipping, and character-specific equipment operations.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

# Authentication imports
from backend.infrastructure.auth.auth_user.services.auth_service import (
    get_current_active_user, check_user_character_access
)

from backend.systems.equipment.services.business_logic_service import (
    EquipmentSlot, EquipmentInstanceData
)


router = APIRouter(prefix="/equipment", tags=["equipment"])


# Request/Response Models
class EquipItemRequest(BaseModel):
    """Request model for equipping an item"""
    item_id: UUID
    slot: str


class UnequipItemRequest(BaseModel):
    """Request model for unequipping an item"""
    slot: str


class SwapItemRequest(BaseModel):
    """Request model for swapping items"""
    item_id: UUID
    slot: str


class CharacterEquipmentResponse(BaseModel):
    """Response model for character equipment layout"""
    character_id: UUID
    equipped_items: Dict[str, Dict[str, Any]]
    total_stats: Dict[str, Any]
    active_set_bonuses: List[Dict[str, Any]]
    equipment_summary: Dict[str, Any]

    @classmethod
    def from_character_equipment(cls, character_id: UUID, equipped_items: Dict[EquipmentSlot, EquipmentInstanceData], 
                                total_stats: Dict[str, Any], set_bonuses: List[Dict[str, Any]]) -> "CharacterEquipmentResponse":
        """Create response from character equipment data"""
        equipped_dict = {}
        for slot, equipment in equipped_items.items():
            equipped_dict[slot.value] = {
                "id": equipment.id,
                "template_id": equipment.template_id,
                "name": equipment.template_id,  # Would be resolved from template
                "quality_tier": equipment.quality_tier,
                "current_durability": equipment.current_durability,
                "max_durability": equipment.max_durability,
                "equipment_set": equipment.equipment_set,
                "effective_stats": equipment.effective_stats
            }
        
        # Calculate summary stats
        total_durability = sum(eq.current_durability for eq in equipped_items.values())
        max_durability = sum(eq.max_durability for eq in equipped_items.values())
        avg_durability = (total_durability / max_durability * 100) if max_durability > 0 else 0
        
        equipment_summary = {
            "total_items": len(equipped_items),
            "average_durability": round(avg_durability, 1),
            "active_sets": len(set_bonuses),
            "needs_repair": len([eq for eq in equipped_items.values() if eq.current_durability < eq.max_durability * 0.5])
        }
        
        return cls(
            character_id=character_id,
            equipped_items=equipped_dict,
            total_stats=total_stats,
            active_set_bonuses=set_bonuses,
            equipment_summary=equipment_summary
        )


class DurabilityDamageRequest(BaseModel):
    """Request model for applying durability damage"""
    usage_type: str = "general"  # combat, crafting, travel, etc.
    damage_amount: int = 1
    affected_slots: Optional[List[str]] = None  # If None, affects all equipped items


@router.get("/{character_id}", response_model=Dict[str, Any])
async def get_character_equipment(
    character_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get a character's equipped items"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this character's equipment"
        )
    
    try:
        # Get dependencies
        from backend.infrastructure.persistence.equipment.equipment_dependencies import (
            get_equipment_instance_repository,
            get_equipment_business_logic_service
        )
        
        instance_repo = get_equipment_instance_repository()
        business_logic = get_equipment_business_logic_service()
        
        # Get character's equipped items
        equipped_items = instance_repo.get_character_equipped_items(character_id)
        
        # Calculate total stats and set bonuses
        total_stats = business_logic.calculate_character_total_stats(equipped_items)
        set_bonuses = business_logic.calculate_character_set_bonuses(equipped_items)
        
        return {
            "character_id": character_id,
            "equipped_items": {item.slot.value: {
                "id": item.id,
                "template_id": item.template_id,
                "current_durability": item.current_durability,
                "max_durability": item.max_durability,
                "quality_tier": item.quality_tier,
                "rarity_tier": item.rarity_tier,
                "equipment_set": item.equipment_set,
                "effective_stats": item.effective_stats
            } for item in equipped_items},
            "total_stats": total_stats,
            "active_set_bonuses": set_bonuses,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get character equipment: {str(e)}"
        )


@router.post("/{character_id}/equip", response_model=Dict[str, Any])
async def equip_item(
    character_id: UUID,
    item_id: int,
    slot: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Equip an item from inventory to a character's equipment slot"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this character's equipment"
        )
    
    try:
        # Validate slot
        try:
            equipment_slot = EquipmentSlot(slot)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid equipment slot: {slot}"
            )
        
        # Get dependencies
        from backend.infrastructure.persistence.equipment.equipment_dependencies import (
            get_equipment_instance_repository,
            get_equipment_business_logic_service
        )
        
        instance_repo = get_equipment_instance_repository()
        business_logic = get_equipment_business_logic_service()
        
        # Get the item to equip
        item_to_equip = instance_repo.get_equipment_by_id(UUID(str(item_id)))
        if not item_to_equip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Verify item belongs to character
        if item_to_equip.character_id != character_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Item does not belong to this character"
            )
        
        # Verify item is not already equipped
        if item_to_equip.is_equipped:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item is already equipped"
            )
        
        # Perform equip operation
        result = business_logic.equip_item_to_slot(character_id, item_to_equip, equipment_slot)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to equip item")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to equip item: {str(e)}"
        )


@router.post("/{character_id}/unequip", response_model=Dict[str, Any])
async def unequip_item(
    character_id: UUID,
    slot: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Unequip an item from a character's equipment slot"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this character's equipment"
        )
    
    try:
        # Validate slot
        try:
            equipment_slot = EquipmentSlot(slot)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid equipment slot: {slot}"
            )
        
        # Get dependencies
        from backend.infrastructure.persistence.equipment.equipment_dependencies import (
            get_equipment_instance_repository,
            get_equipment_business_logic_service
        )
        
        instance_repo = get_equipment_instance_repository()
        business_logic = get_equipment_business_logic_service()
        
        # Perform unequip operation
        result = business_logic.unequip_item_from_slot(character_id, equipment_slot)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to unequip item")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unequip item: {str(e)}"
        )


@router.post("/{character_id}/swap", response_model=Dict[str, Any])
async def swap_equipment(
    character_id: UUID,
    item_id: int,
    slot: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Swap an equipped item with a new item in one operation"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this character's equipment"
        )
    
    try:
        # Validate slot
        try:
            equipment_slot = EquipmentSlot(slot)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid equipment slot: {slot}"
            )
        
        # Get dependencies
        from backend.infrastructure.persistence.equipment.equipment_dependencies import (
            get_equipment_instance_repository,
            get_equipment_business_logic_service
        )
        
        instance_repo = get_equipment_instance_repository()
        business_logic = get_equipment_business_logic_service()
        
        # Get the item to equip
        new_item = instance_repo.get_equipment_by_id(UUID(str(item_id)))
        if not new_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Verify item belongs to character
        if new_item.character_id != character_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Item does not belong to this character"
            )
        
        # Perform swap operation
        result = business_logic.swap_equipment_in_slot(character_id, new_item, equipment_slot)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to swap equipment")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to swap equipment: {str(e)}"
        )


@router.post("/{character_id}/repair/{equipment_id}")
async def repair_equipment(
    character_id: UUID,
    equipment_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Repair a character's equipment item (requires authentication and ownership)"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "write")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to repair this character's equipment"
        )
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Equipment repair requires character equipment service completion"
    )


@router.post("/{character_id}/durability-damage")
async def apply_durability_damage(
    character_id: UUID,
    request: DurabilityDamageRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Apply durability damage to character's equipped items (requires authentication and ownership)"""
    
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
        detail="Durability damage requires character equipment service completion"
    )


@router.get("/{character_id}/stats", response_model=Dict[str, Any])
async def get_character_equipment_stats(
    character_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get character's total stats from equipped items (requires authentication and ownership)"""
    
    # Check user has access to this character
    user_id = str(current_user["id"])
    character_id_str = str(character_id)
    
    has_access = await check_user_character_access(user_id, character_id_str, "read")
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this character's equipment stats"
        )
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Character equipment stats require character equipment service completion"
    ) 