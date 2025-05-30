"""
Magic system API router.

This module defines the FastAPI router for magic system endpoints.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from starlette import status

from app.core.database import get_db
from app.core.auth import get_current_user

from .schemas import (
    MagicAbilityCreate, MagicAbilityUpdate, MagicAbilityResponse,
    SpellCreate, SpellUpdate, SpellResponse,
    SpellComponentCreate, SpellComponentResponse,
    SpellbookCreate, SpellbookResponse,
    SpellEffectCreate, SpellEffectResponse,
    SpellSlotCreate, SpellSlotResponse,
    CastSpellRequest,
    MagicTypeEnum, MagicSchoolEnum, ComponentTypeEnum, EffectTypeEnum
)
from .services import (
    MagicService, SpellService, SpellbookService, SpellEffectService, SpellSlotService
)

# Create the router
router = APIRouter(prefix="/magic", tags=["magic"])

# ================ Magic Ability Routes ================

@router.post("/abilities", response_model=MagicAbilityResponse, status_code=status.HTTP_201_CREATED)
def create_magic_ability(
    ability: MagicAbilityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new magic ability."""
    service = MagicService(db)
    result = service.create_magic_ability(ability.dict())
    return result

@router.get("/abilities", response_model=List[MagicAbilityResponse])
def list_magic_abilities(
    skip: int = Query(0, description="Skip the first n items"),
    limit: int = Query(100, description="Limit the number of items returned"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List magic abilities."""
    service = MagicService(db)
    repository = service.repository
    abilities = repository.get_all(skip=skip, limit=limit)
    return abilities

@router.get("/abilities/{ability_id}", response_model=MagicAbilityResponse)
def get_magic_ability(
    ability_id: int = Path(..., description="The ID of the magic ability"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a magic ability by ID."""
    service = MagicService(db)
    ability = service.get_magic_ability(ability_id)
    if not ability:
        raise HTTPException(status_code=404, detail="Magic ability not found")
    return ability

@router.put("/abilities/{ability_id}", response_model=MagicAbilityResponse)
def update_magic_ability(
    ability_id: int = Path(..., description="The ID of the magic ability"),
    ability: MagicAbilityUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a magic ability."""
    service = MagicService(db)
    updated_ability = service.update_magic_ability(ability_id, ability.dict(exclude_unset=True))
    if not updated_ability:
        raise HTTPException(status_code=404, detail="Magic ability not found")
    return updated_ability

@router.delete("/abilities/{ability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_magic_ability(
    ability_id: int = Path(..., description="The ID of the magic ability"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a magic ability."""
    service = MagicService(db)
    success = service.delete_magic_ability(ability_id)
    if not success:
        raise HTTPException(status_code=404, detail="Magic ability not found")
    return None

# ================ Spell Routes ================

@router.post("/spells", response_model=SpellResponse, status_code=status.HTTP_201_CREATED)
def create_spell(
    spell: SpellCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new spell."""
    service = SpellService(db)
    result = service.create_spell(spell.dict())
    return result

@router.get("/spells", response_model=List[SpellResponse])
def list_spells(
    skip: int = Query(0, description="Skip the first n items"),
    limit: int = Query(100, description="Limit the number of items returned"),
    school: Optional[MagicSchoolEnum] = Query(None, description="Filter by spell school"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List spells."""
    service = SpellService(db)
    repository = service.repository
    spells = repository.get_all(skip=skip, limit=limit, school=school.value if school else None)
    return spells

@router.get("/spells/{spell_id}", response_model=SpellResponse)
def get_spell(
    spell_id: int = Path(..., description="The ID of the spell"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a spell by ID."""
    service = SpellService(db)
    spell = service.get_spell(spell_id)
    if not spell:
        raise HTTPException(status_code=404, detail="Spell not found")
    return spell

@router.put("/spells/{spell_id}", response_model=SpellResponse)
def update_spell(
    spell_id: int = Path(..., description="The ID of the spell"),
    spell: SpellUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a spell."""
    service = SpellService(db)
    updated_spell = service.update_spell(spell_id, spell.dict(exclude_unset=True))
    if not updated_spell:
        raise HTTPException(status_code=404, detail="Spell not found")
    return updated_spell

@router.delete("/spells/{spell_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spell(
    spell_id: int = Path(..., description="The ID of the spell"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a spell."""
    service = SpellService(db)
    success = service.delete_spell(spell_id)
    if not success:
        raise HTTPException(status_code=404, detail="Spell not found")
    return None

@router.post("/spells/cast", response_model=SpellEffectResponse)
def cast_spell(
    cast_request: CastSpellRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cast a spell on a target."""
    service = MagicService(db)
    effect = service.cast_spell(
        spell_id=cast_request.spell_id,
        caster_id=cast_request.caster_id,
        target_id=cast_request.target_id,
        target_type=cast_request.target_type,
        additional_data=cast_request.additional_data
    )
    
    if not effect:
        raise HTTPException(status_code=400, detail="Failed to cast spell")
    
    return effect

# ================ Spellbook Routes ================

@router.post("/spellbooks", response_model=SpellbookResponse, status_code=status.HTTP_201_CREATED)
def create_spellbook(
    spellbook: SpellbookCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new spellbook."""
    service = SpellbookService(db)
    # Use the existing repository for direct creation
    repository = service.repository
    result = repository.create(spellbook.dict())
    return result

@router.get("/spellbooks", response_model=List[SpellbookResponse])
def list_spellbooks(
    owner_type: Optional[str] = Query(None, description="Filter by owner type"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List spellbooks."""
    service = SpellbookService(db)
    repository = service.repository
    spellbooks = repository.get_all(owner_type=owner_type)
    return spellbooks

@router.get("/spellbooks/{spellbook_id}", response_model=SpellbookResponse)
def get_spellbook(
    spellbook_id: int = Path(..., description="The ID of the spellbook"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a spellbook by ID."""
    service = SpellbookService(db)
    repository = service.repository
    spellbook = repository.get_by_id(spellbook_id)
    if not spellbook:
        raise HTTPException(status_code=404, detail="Spellbook not found")
    return spellbook

@router.get("/characters/{owner_id}/spellbook", response_model=SpellbookResponse)
def get_character_spellbook(
    owner_id: int = Path(..., description="The ID of the character"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a character's spellbook."""
    service = SpellbookService(db)
    spellbook = service.get_spellbook("character", owner_id)
    if not spellbook:
        raise HTTPException(status_code=404, detail="Spellbook not found")
    return spellbook

@router.post("/spellbooks/{spellbook_id}/spells/{spell_id}")
def add_spell_to_spellbook(
    spellbook_id: int = Path(..., description="The ID of the spellbook"),
    spell_id: int = Path(..., description="The ID of the spell"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a spell to a spellbook."""
    service = SpellbookService(db)
    repository = service.repository
    
    # Get the spellbook to find owner information
    spellbook = repository.get_by_id(spellbook_id)
    if not spellbook:
        raise HTTPException(status_code=404, detail="Spellbook not found")
    
    # Add the spell to the spellbook
    success = service.add_spell(spellbook.owner_type, spellbook.owner_id, spell_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add spell to spellbook")
    
    return {"message": "Spell added to spellbook successfully"}

@router.delete("/spellbooks/{spellbook_id}/spells/{spell_id}")
def remove_spell_from_spellbook(
    spellbook_id: int = Path(..., description="The ID of the spellbook"),
    spell_id: int = Path(..., description="The ID of the spell"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove a spell from a spellbook."""
    service = SpellbookService(db)
    repository = service.repository
    
    # Get the spellbook to find owner information
    spellbook = repository.get_by_id(spellbook_id)
    if not spellbook:
        raise HTTPException(status_code=404, detail="Spellbook not found")
    
    # Remove the spell from the spellbook
    success = service.remove_spell(spellbook.owner_type, spellbook.owner_id, spell_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove spell from spellbook")
    
    return {"message": "Spell removed from spellbook successfully"}

# ================ Spell Effect Routes ================

@router.get("/effects", response_model=List[SpellEffectResponse])
def list_spell_effects(
    target_id: Optional[int] = Query(None, description="Filter by target ID"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List spell effects."""
    service = SpellEffectService(db)
    repository = service.repository
    
    if target_id and target_type:
        effects = repository.get_by_target(target_type, target_id)
    else:
        effects = repository.get_all()
        
    return effects

@router.get("/effects/{effect_id}", response_model=SpellEffectResponse)
def get_spell_effect(
    effect_id: int = Path(..., description="The ID of the spell effect"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a spell effect by ID."""
    service = SpellEffectService(db)
    effect = service.get_effect(effect_id)
    if not effect:
        raise HTTPException(status_code=404, detail="Spell effect not found")
    return effect

@router.delete("/effects/{effect_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spell_effect(
    effect_id: int = Path(..., description="The ID of the spell effect"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a spell effect."""
    service = SpellEffectService(db)
    success = service.end_effect(effect_id)
    if not success:
        raise HTTPException(status_code=404, detail="Spell effect not found")
    return None

@router.post("/effects/{effect_id}/dispel", response_model=Dict[str, Any])
def dispel_spell_effect(
    effect_id: int = Path(..., description="The ID of the spell effect"),
    dispel_power: int = Query(..., description="Power of the dispel attempt"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Attempt to dispel a spell effect."""
    service = SpellEffectService(db)
    success, message = service.dispel_effect(effect_id, dispel_power)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}

@router.put("/effects/{effect_id}/modify-duration", response_model=SpellEffectResponse)
def modify_effect_duration(
    effect_id: int = Path(..., description="The ID of the spell effect"),
    duration_change: int = Query(..., description="Amount to change duration (can be negative)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Modify the duration of a spell effect."""
    service = SpellEffectService(db)
    updated_effect = service.modify_effect_duration(effect_id, duration_change)
    
    if not updated_effect:
        if duration_change < 0:
            # If duration was reduced to 0 or below, the effect was ended
            return {"message": "Effect ended due to duration reduction."}
        else:
            raise HTTPException(status_code=404, detail="Spell effect not found")
    
    return updated_effect

# ================ Spell Slot Routes ================

@router.post("/characters/{character_id}/spell-slots", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_character_spell_slots(
    character_id: int = Path(..., description="The ID of the character"),
    level_counts: Dict[str, int] = Body(..., description="Dictionary mapping level to count"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create spell slots for a character."""
    service = SpellSlotService(db)
    
    # Convert string keys to integers
    level_counts_int = {int(k): v for k, v in level_counts.items()}
    
    created_slots = {}
    for level, count in level_counts_int.items():
        slots = service.create_slots("character", character_id, level, count)
        created_slots[level] = len(slots)
    
    return {"character_id": character_id, "created_slots": created_slots}


@router.get("/characters/{character_id}/spell-slots", response_model=Dict[str, Any])
def get_character_spell_slots(
    character_id: int = Path(..., description="The ID of the character"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get spell slots for a character."""
    service = SpellSlotService(db)
    slot_summary = service.get_slot_summary("character", character_id)
    return {"character_id": character_id, "slot_summary": slot_summary}


@router.get("/characters/{character_id}/spell-slots/available", response_model=List[SpellSlotResponse])
def get_character_available_slots(
    character_id: int = Path(..., description="The ID of the character"),
    level: Optional[int] = Query(None, description="Filter by spell level"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available spell slots for a character."""
    service = SpellSlotService(db)
    slots = service.get_available_slots("character", character_id, level)
    return slots


@router.post("/spell-slots/{slot_id}/use", response_model=Dict[str, Any])
def use_spell_slot(
    slot_id: int = Path(..., description="The ID of the spell slot"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Use a spell slot."""
    service = SpellSlotService(db)
    success = service.use_slot(slot_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to use spell slot")
    return {"success": True, "message": "Spell slot used successfully"}


@router.post("/characters/{character_id}/spell-slots/refresh", response_model=Dict[str, Any])
def refresh_character_spell_slots(
    character_id: int = Path(..., description="The ID of the character"),
    level: Optional[int] = Query(None, description="Filter by spell level"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Refresh spell slots for a character."""
    service = SpellSlotService(db)
    refreshed_count = service.refresh_slots("character", character_id, level)
    return {"character_id": character_id, "refreshed_count": refreshed_count}


# ================ Magic System Utilities ================

@router.post("/system/process-tick", response_model=Dict[str, Any])
def process_magic_tick(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Process a magic system tick."""
    service = MagicService(db)
    result = service.process_magic_tick()
    return result


@router.get("/characters/{character_id}/magic-summary", response_model=Dict[str, Any])
def get_character_magic_summary(
    character_id: int = Path(..., description="The ID of the character"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a summary of a character's magical abilities and resources."""
    service = MagicService(db)
    summary = service.get_character_magic_summary(character_id)
    return summary 