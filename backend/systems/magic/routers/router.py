"""
Magic System Router - D&D Compliant API Endpoints

Provides comprehensive API endpoints for:
- Spell management and casting
- Spellbook operations
- Spell slot tracking
- Active effect management
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.infrastructure.shared.database import get_db
from backend.systems.magic.models import (
    SpellResponse, SpellbookResponse, SpellSlotsResponse,
    CastSpellRequest, PrepareSpellsRequest
)
from backend.systems.magic.services import MagicService

router = APIRouter(prefix="/magic", tags=["magic"])

@router.get("/spells", response_model=List[SpellResponse])
async def get_spells(
    school: Optional[str] = None,
    level: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all spells with optional filtering."""
    service = MagicService(db)
    return await service.get_spells(school=school, level=level)

@router.get("/spells/{spell_id}", response_model=SpellResponse)
async def get_spell(spell_id: UUID, db: Session = Depends(get_db)):
    """Get specific spell by ID."""
    service = MagicService(db)
    spell = await service.get_spell(spell_id)
    if not spell:
        raise HTTPException(status_code=404, detail="Spell not found")
    return spell

@router.get("/spellbook/{character_id}", response_model=SpellbookResponse)
async def get_spellbook(character_id: UUID, db: Session = Depends(get_db)):
    """Get character's spellbook."""
    service = MagicService(db)
    spellbook = await service.get_spellbook(character_id)
    if not spellbook:
        raise HTTPException(status_code=404, detail="Spellbook not found")
    return spellbook

@router.post("/spellbook/{character_id}/prepare")
async def prepare_spells(
    character_id: UUID,
    request: PrepareSpellsRequest,
    db: Session = Depends(get_db)
):
    """Prepare daily spells."""
    service = MagicService(db)
    return await service.prepare_spells(character_id, request.spell_ids)

@router.post("/spells/cast")
async def cast_spell(
    request: CastSpellRequest,
    db: Session = Depends(get_db)
):
    """Cast a spell."""
    service = MagicService(db)
    return await service.cast_spell(request)

@router.get("/spell-slots/{character_id}", response_model=List[SpellSlotsResponse])
async def get_spell_slots(character_id: UUID, db: Session = Depends(get_db)):
    """Get character's spell slots."""
    service = MagicService(db)
    return await service.get_spell_slots(character_id)

@router.post("/spell-slots/{character_id}/rest")
async def long_rest(character_id: UUID, db: Session = Depends(get_db)):
    """Restore spell slots after long rest."""
    service = MagicService(db)
    return await service.restore_spell_slots(character_id)

@router.get("/effects/active/{character_id}")
async def get_active_effects(character_id: UUID, db: Session = Depends(get_db)):
    """Get active spell effects for character."""
    service = MagicService(db)
    return await service.get_active_effects(character_id)

@router.delete("/effects/{effect_id}")
async def dispel_effect(effect_id: UUID, db: Session = Depends(get_db)):
    """Dispel an active spell effect."""
    service = MagicService(db)
    return await service.dispel_effect(effect_id)
