"""
Equipment API router for handling equipment-related requests.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any, List, Optional
from .service import EquipmentService
from .identify_item_utils import (
    calculate_identification_cost,
    reveal_item_name_and_flavor
)

# Importing narrative system utils, with fallback if not available
try:
    from backend.systems.narrative.utils import (
        gpt_flavor_identify_effect,
        gpt_flavor_reveal_full_item
    )
    HAS_NARRATIVE_SYSTEM = True
except ImportError:
    HAS_NARRATIVE_SYSTEM = False
    # Fallback functions if narrative system not available
    def gpt_flavor_identify_effect(item_name, effect):
        return f"You discover that {item_name} has the effect: {effect}."
    def gpt_flavor_reveal_full_item(item):
        return f"All properties of {item.get('name', 'the item')} are now revealed."

router = APIRouter(prefix="/equipment", tags=["equipment"])

@router.post("/{character_id}/equip")
async def equip_item(character_id: int, item_id: int, slot: str) -> Dict[str, Any]:
    """
    Equip an item from inventory to a character's equipment slot.
    
    Args:
        character_id: ID of the character
        item_id: ID of the item to equip
        slot: Slot to equip the item in
        
    Returns:
        Dict with success status and result information
    """
    result = await EquipmentService.equip_item(character_id, item_id, slot)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.post("/{character_id}/unequip")
async def unequip_item(character_id: int, slot: str) -> Dict[str, Any]:
    """
    Unequip an item from a character's equipment slot.
    
    Args:
        character_id: ID of the character
        slot: Slot to unequip the item from
        
    Returns:
        Dict with success status and result information
    """
    result = await EquipmentService.unequip_item(character_id, slot)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.get("/{character_id}")
async def get_character_equipment(character_id: int) -> Dict[str, Any]:
    """
    Get a character's equipped items.
    
    Args:
        character_id: ID of the character
        
    Returns:
        Dict with equipment information
    """
    result = await EquipmentService.get_character_equipment(character_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.post("/{character_id}/swap")
async def swap_equipment(character_id: int, slot: str, new_item_id: int) -> Dict[str, Any]:
    """
    Swap an equipped item with a new item in one operation.
    
    Args:
        character_id: ID of the character
        slot: Slot to swap item in
        new_item_id: ID of the new item to equip
        
    Returns:
        Dict with success status and result information
    """
    result = await EquipmentService.swap_equipment(character_id, slot, new_item_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.post("/durability/{equipment_id}/damage/combat")
async def apply_combat_damage(
    equipment_id: int,
    equipment_type: str = Body(...),
    combat_intensity: float = Body(1.0),
    is_critical: bool = Body(False)
) -> Dict[str, Any]:
    """
    Apply combat damage to an equipment item.
    
    Args:
        equipment_id: ID of the equipment
        equipment_type: Type of equipment (weapon, armor, shield, accessory)
        combat_intensity: Multiplier for combat intensity (1.0 is normal)
        is_critical: Whether this was a critical hit (more damage)
        
    Returns:
        Dict with damage result
    """
    result = await EquipmentService.apply_combat_damage(
        equipment_id, equipment_type, combat_intensity, is_critical
    )
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.post("/durability/{equipment_id}/damage/wear")
async def apply_wear_damage(
    equipment_id: int,
    equipment_type: str = Body(...),
    time_worn: float = Body(1.0),
    environmental_factor: float = Body(1.0)
) -> Dict[str, Any]:
    """
    Apply wear and tear damage to an equipment item.
    
    Args:
        equipment_id: ID of the equipment
        equipment_type: Type of equipment (weapon, armor, shield, accessory)
        time_worn: Hours the equipment has been worn/used
        environmental_factor: Multiplier for environmental conditions (rain, heat, etc.)
        
    Returns:
        Dict with damage result
    """
    result = await EquipmentService.apply_wear_damage(
        equipment_id, equipment_type, time_worn, environmental_factor
    )
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.post("/durability/{equipment_id}/repair")
async def repair_equipment(
    equipment_id: int,
    repair_amount: Optional[float] = Body(None),
    full_repair: bool = Body(False)
) -> Dict[str, Any]:
    """
    Repair an equipment item.
    
    Args:
        equipment_id: ID of the equipment
        repair_amount: Amount of durability to restore (None for full repair)
        full_repair: Force full repair regardless of repair_amount
        
    Returns:
        Dict with repair result
    """
    result = await EquipmentService.repair_equipment_item(
        equipment_id, repair_amount, full_repair
    )
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.get("/durability/{equipment_id}/status")
async def get_durability_status(equipment_id: int) -> Dict[str, Any]:
    """
    Get the durability status of an equipment item.
    
    Args:
        equipment_id: ID of the equipment
        
    Returns:
        Dict with durability status information
    """
    result = await EquipmentService.get_durability_status(equipment_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.get("/durability/{equipment_id}/repair-cost")
async def get_repair_cost(
    equipment_id: int,
    repair_amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate the cost to repair an equipment item.
    
    Args:
        equipment_id: ID of the equipment
        repair_amount: Optional specific amount to repair, otherwise full repair
        
    Returns:
        Dict with repair cost information
    """
    result = await EquipmentService.get_repair_cost(equipment_id, repair_amount)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.get("/durability/{equipment_id}/history")
async def get_durability_history(
    equipment_id: int,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get durability change history for an equipment item.
    
    Args:
        equipment_id: ID of the equipment
        limit: Maximum number of log entries to return
        
    Returns:
        Dict with durability history
    """
    result = await EquipmentService.get_durability_history(equipment_id, limit)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.post("/{character_id}/identify")
async def identify_item(
    character_id: int, 
    item_id: int,
    region: Optional[str] = None,
    faction_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Identify a single unknown effect on an item.
    
    Args:
        character_id: ID of the character
        item_id: ID of the item to identify
        region: Optional region name for economic modifiers
        faction_id: Optional faction ID for discounts
        
    Returns:
        Dict with identification result
    """
    result = await EquipmentService.identify_item(character_id, item_id, region, faction_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.post("/{character_id}/identify_full")
async def identify_item_full(
    character_id: int,
    item_id: int,
    npc_id: int = Body(...)
) -> Dict[str, Any]:
    """
    Fully identify all effects on an item at once (requires special NPC).
    
    Args:
        character_id: ID of the character
        item_id: ID of the item to identify
        npc_id: ID of the NPC performing the identification (must have special permissions)
        
    Returns:
        Dict with full identification result
    """
    result = await EquipmentService.identify_item_full(character_id, item_id, npc_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.get("/{character_id}/set_bonuses")
async def get_character_set_bonuses(character_id: int) -> Dict[str, Any]:
    """
    Get all active set bonuses for a character.
    
    Args:
        character_id: ID of the character
        
    Returns:
        Dict with active set bonuses information
    """
    result = await EquipmentService.get_character_set_bonuses(character_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.get("/sets")
async def get_all_equipment_sets() -> Dict[str, Any]:
    """
    Get all available equipment sets.
    
    Returns:
        Dict with equipment sets information
    """
    result = await EquipmentService.get_all_equipment_sets()
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.get("/sets/{set_id}")
async def get_equipment_set_by_id(set_id: int) -> Dict[str, Any]:
    """
    Get a specific equipment set by ID.
    
    Args:
        set_id: ID of the equipment set
        
    Returns:
        Dict with equipment set information
    """
    result = await EquipmentService.get_equipment_set_by_id(set_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.post("/sets")
async def create_equipment_set(
    name: str = Body(...),
    description: str = Body(...),
    item_ids: List[int] = Body(...),
    set_bonuses: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """
    Create a new equipment set.
    
    Args:
        name: Name of the equipment set
        description: Description of the equipment set
        item_ids: List of item IDs that belong to this set
        set_bonuses: Dictionary mapping number of pieces to bonuses
        
    Returns:
        Dict with created equipment set information
    """
    result = await EquipmentService.create_new_equipment_set(
        name, description, item_ids, set_bonuses
    )
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.put("/sets/{set_id}")
async def update_equipment_set(
    set_id: int,
    name: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    item_ids: Optional[List[int]] = Body(None),
    set_bonuses: Optional[Dict[str, Any]] = Body(None)
) -> Dict[str, Any]:
    """
    Update an existing equipment set.
    
    Args:
        set_id: ID of the equipment set to update
        name: Optional new name for the equipment set
        description: Optional new description
        item_ids: Optional new list of item IDs
        set_bonuses: Optional new set bonuses
        
    Returns:
        Dict with updated equipment set information
    """
    result = await EquipmentService.update_existing_equipment_set(
        set_id, name, description, item_ids, set_bonuses
    )
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result

@router.delete("/sets/{set_id}")
async def delete_equipment_set(set_id: int) -> Dict[str, Any]:
    """
    Delete an equipment set.
    
    Args:
        set_id: ID of the equipment set to delete
        
    Returns:
        Dict with deletion result
    """
    result = await EquipmentService.delete_equipment_set_by_id(set_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return result 