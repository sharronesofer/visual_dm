"""Magic System API Router - Canonical MP-Based Implementation

This router implements the Development Bible's canonical magic system:
- MP-based spellcasting (not spell slots)
- Domain-based efficiency and primary abilities  
- Permanent spell learning (no daily preparation)
- Four domains: Nature, Arcane, Eldritch/Occult, Divine
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from backend.infrastructure.database import get_db
from backend.infrastructure.systems.magic.models.models import (
    # Canonical models
    Spell, CharacterMP, CharacterDomainAccess, LearnedSpells, ConcentrationTracking,
    # Response models
    SpellResponse, CharacterMPResponse, DomainAccessResponse, 
    LearnedSpellsResponse, ConcentrationResponse,
    # Request models  
    CastSpellRequest, RestoreMatrixPointsRequest, LearnSpellRequest, UpdateDomainAccessRequest
)

# Import business services for canonical spell casting
from backend.systems.magic.services import MagicBusinessService, MagicCombatBusinessService
from backend.infrastructure.data_loaders.magic_config import (
    create_magic_config_repository, create_damage_type_service
)

# Import advanced features
from backend.systems.magic.services.metamagic_service import (
    create_metamagic_service, MetamagicType, MetamagicResult
)
from backend.systems.magic.services.spell_combination_service import (
    create_spell_combination_service, CombinationResult
)

# Import datetime for rest functionality
from datetime import datetime

# Add character service import
from backend.infrastructure.adapters.character_adapter import create_character_service

# Create the router
router = APIRouter(
    tags=["magic"],
    responses={404: {"description": "Not found"}},
)

# Dependency to create magic services
def get_magic_services():
    """Get magic business services"""
    config_repo = create_magic_config_repository()
    damage_service = create_damage_type_service()
    magic_service = MagicBusinessService(config_repo, damage_service)
    
    from backend.infrastructure.utils.time_provider import DefaultTimeProvider
    time_provider = DefaultTimeProvider()
    combat_service = MagicCombatBusinessService(magic_service, time_provider)
    
    return magic_service, combat_service

# Dependency to create advanced magic services
def get_advanced_magic_services():
    """Get advanced magic services"""
    metamagic_service = create_metamagic_service()
    combination_service = create_spell_combination_service()
    return metamagic_service, combination_service

# === CANONICAL SPELL ENDPOINTS ===

@router.get("/spells", response_model=List[SpellResponse])
async def get_spells(
    domain: Optional[str] = None,
    school: Optional[str] = None,
    max_mp_cost: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all spells with optional filters (canonical MP-based)."""
    query = db.query(Spell)
    
    # Filter by domain if specified
    if domain:
        query = query.filter(Spell.valid_domains.contains([domain]))
    
    # Filter by school if specified
    if school:
        query = query.filter(Spell.school == school)
    
    # Filter by MP cost if specified
    if max_mp_cost:
        query = query.filter(Spell.mp_cost <= max_mp_cost)
    
    spells = query.all()
    return [SpellResponse.model_validate(spell) for spell in spells]

@router.get("/spells/available/{character_id}", response_model=LearnedSpellsResponse)
async def get_available_spells(
    character_id: int,
    domain: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get spells available to a character based on their domain access (canonical)."""
    # Get character's domain access
    domain_access = db.query(CharacterDomainAccess).filter(
        CharacterDomainAccess.character_id == character_id
    ).all()
    
    if not domain_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No domain access found for character {character_id}"
        )
    
    # Get character's learned spells
    learned_spells = db.query(LearnedSpells).filter(
        LearnedSpells.character_id == character_id
    ).all()
    
    available_domains = [access.domain for access in domain_access]
    
    # Filter by specific domain if requested
    if domain:
        if domain not in available_domains:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Character {character_id} does not have access to domain {domain}"
            )
        available_domains = [domain]
    
    # Get spells for available domains
    spell_responses = []
    for learned in learned_spells:
        if learned.domain_learned in available_domains:
            spell_responses.append(SpellResponse.model_validate(learned.spell))
    
    return LearnedSpellsResponse(
        character_id=character_id,
        spells=spell_responses,
        domains_available=available_domains,
        total_spells_known=len(spell_responses)
    )

@router.post("/spells/cast")
async def cast_spell(
    cast_request: CastSpellRequest,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Cast a spell using the canonical MP-based system."""
    magic_service, combat_service = get_magic_services()
    
    # Get character's MP status
    character_mp = db.query(CharacterMP).filter(
        CharacterMP.character_id == character_id
    ).first()
    
    if not character_mp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MP tracking not found for character {character_id}"
        )
    
    # Verify character has access to the domain
    domain_access = db.query(CharacterDomainAccess).filter(
        CharacterDomainAccess.character_id == character_id,
        CharacterDomainAccess.domain == cast_request.domain
    ).first()
    
    if not domain_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Character {character_id} does not have access to domain {cast_request.domain}"
        )
    
    # Verify character knows the spell
    learned_spell = db.query(LearnedSpells).filter(
        LearnedSpells.character_id == character_id,
        LearnedSpells.spell_id == cast_request.spell_id
    ).first()
    
    if not learned_spell:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Character {character_id} has not learned spell {cast_request.spell_id}"
        )
    
    # Get real character abilities instead of mock
    character_service = create_character_service(db)
    abilities = character_service.get_character_abilities(character_id)
    
    if not abilities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )
    
    # Get proficiency bonus from character service
    proficiency_bonus = character_service.get_proficiency_bonus(character_id)
    
    # Attempt spell casting
    result = combat_service.attempt_spell_cast(
        caster_id=str(character_id),
        spell_name=learned_spell.spell.name,
        domain=cast_request.domain,
        target_id=str(cast_request.target_id) if cast_request.target_id else None,
        abilities=abilities,
        current_mp=character_mp.current_mp,
        proficiency_bonus=proficiency_bonus,
        extra_mp=cast_request.extra_mp
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error_message
        )
    
    # Deduct MP
    character_mp.current_mp -= result.mp_cost
    
    # Save concentration effect if applicable
    if result.concentration_effect:
        concentration = ConcentrationTracking(
            caster_id=character_id,
            spell_id=cast_request.spell_id,
            target_id=int(cast_request.target_id) if cast_request.target_id else None,
            domain_used=cast_request.domain,
            mp_spent=result.mp_cost,
            effect_data=cast_request.metadata
        )
        db.add(concentration)
    
    db.commit()
    
    return {
        "success": True,
        "mp_cost": result.mp_cost,
        "remaining_mp": character_mp.current_mp,
        "spell_effect": result.spell_effect,
        "concentration_required": bool(result.concentration_effect)
    }

@router.post("/spells/learn")
async def learn_spell(
    learn_request: LearnSpellRequest,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Learn a new spell permanently (canonical system - no daily preparation)."""
    # Verify spell exists
    spell = db.query(Spell).filter(Spell.id == learn_request.spell_id).first()
    if not spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spell {learn_request.spell_id} not found"
        )
    
    # Verify domain is valid for this spell
    if learn_request.domain not in spell.valid_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Spell {spell.name} cannot be learned through domain {learn_request.domain}"
        )
    
    # Verify character has access to domain
    domain_access = db.query(CharacterDomainAccess).filter(
        CharacterDomainAccess.character_id == character_id,
        CharacterDomainAccess.domain == learn_request.domain
    ).first()
    
    if not domain_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Character {character_id} does not have access to domain {learn_request.domain}"
        )
    
    # Check if already learned
    existing = db.query(LearnedSpells).filter(
        LearnedSpells.character_id == character_id,
        LearnedSpells.spell_id == learn_request.spell_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Character {character_id} has already learned spell {spell.name}"
        )
    
    # Learn the spell permanently
    learned_spell = LearnedSpells(
        character_id=character_id,
        spell_id=learn_request.spell_id,
        domain_learned=learn_request.domain,
        mastery_level=1
    )
    
    db.add(learned_spell)
    db.commit()
    
    return {
        "message": f"Spell {spell.name} learned through {learn_request.domain} domain",
        "spell_id": learn_request.spell_id,
        "domain": learn_request.domain,
        "learning_method": learn_request.learning_method
    }

# === ADVANCED FEATURES: METAMAGIC ===

@router.get("/metamagic/available/{spell_id}")
async def get_available_metamagic(
    spell_id: UUID,
    db: Session = Depends(get_db)
):
    """Get metamagic effects available for a specific spell."""
    # Get spell details
    spell = db.query(Spell).filter(Spell.id == spell_id).first()
    if not spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spell {spell_id} not found"
        )
    
    # Get metamagic service
    metamagic_service, _ = get_advanced_magic_services()
    
    # Convert spell to properties dict
    spell_properties = {
        "name": spell.name,
        "school": spell.school,
        "mp_cost": spell.mp_cost,
        "base_damage": spell.base_damage,
        "base_healing": spell.base_healing,
        "range_feet": spell.range_feet,
        "duration_seconds": spell.duration_seconds,
        "concentration": spell.concentration,
        "target": spell.target,
        "components": spell.components
    }
    
    # Get available metamagic
    available_metamagic = metamagic_service.get_available_metamagic(spell_properties)
    
    return {
        "spell_name": spell.name,
        "spell_id": spell_id,
        "available_metamagic": [
            {
                "type": metamagic.type.value,
                "mp_cost_multiplier": metamagic.mp_cost_multiplier,
                "description": metamagic.description,
                "extra_mp_cost": metamagic.calculate_extra_mp(spell.mp_cost)
            }
            for metamagic in available_metamagic
        ]
    }

@router.post("/spells/cast-with-metamagic")
async def cast_spell_with_metamagic(
    character_id: int,
    spell_id: UUID,
    domain: str,
    metamagic_types: List[str],
    target_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Cast a spell with metamagic enhancements."""
    # Get spell and character data
    spell = db.query(Spell).filter(Spell.id == spell_id).first()
    if not spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spell {spell_id} not found"
        )
    
    character_mp = db.query(CharacterMP).filter(
        CharacterMP.character_id == character_id
    ).first()
    
    if not character_mp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MP tracking not found for character {character_id}"
        )
    
    # Get metamagic service
    metamagic_service, _ = get_advanced_magic_services()
    
    # Convert spell to properties dict
    spell_properties = {
        "name": spell.name,
        "school": spell.school,
        "mp_cost": spell.mp_cost,
        "base_damage": spell.base_damage,
        "base_healing": spell.base_healing,
        "range_feet": spell.range_feet,
        "duration_seconds": spell.duration_seconds,
        "concentration": spell.concentration,
        "target": spell.target,
        "components": spell.components
    }
    
    # Convert metamagic strings to enums
    try:
        metamagic_enums = [MetamagicType(mt) for mt in metamagic_types]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metamagic type: {e}"
        )
    
    # Apply metamagic
    metamagic_result = metamagic_service.apply_metamagic(
        spell_properties=spell_properties,
        base_mp_cost=spell.mp_cost,
        metamagic_types=metamagic_enums,
        available_mp=character_mp.current_mp
    )
    
    if not metamagic_result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=metamagic_result.error_message
        )
    
    # Deduct MP for enhanced spell
    character_mp.current_mp -= metamagic_result.total_mp_cost
    db.commit()
    
    return {
        "success": True,
        "spell_cast": spell.name,
        "metamagic_applied": [mt.value for mt in metamagic_result.metamagic_applied],
        "base_mp_cost": spell.mp_cost,
        "total_mp_cost": metamagic_result.total_mp_cost,
        "extra_mp_used": metamagic_result.extra_mp_used,
        "remaining_mp": character_mp.current_mp,
        "enhanced_effects": metamagic_result.modified_effect
    }

# === ADVANCED FEATURES: SPELL COMBINATIONS ===

@router.get("/combinations/available")
async def get_available_combinations(
    spell_ids: List[UUID],
    db: Session = Depends(get_db)
):
    """Get spell combinations available for given spell IDs."""
    # Get spells
    spells = db.query(Spell).filter(Spell.id.in_(spell_ids)).all()
    
    if len(spells) != len(spell_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more spells not found"
        )
    
    # Get combination service
    _, combination_service = get_advanced_magic_services()
    
    # Convert spells to data objects
    spell_data = []
    for spell in spells:
        spell_data.append(type('SpellData', (), {
            'name': spell.name,
            'school': spell.school,
            'mp_cost': spell.mp_cost,
            'base_damage': spell.base_damage,
            'base_healing': spell.base_healing,
            'range_feet': spell.range_feet,
            'duration_seconds': spell.duration_seconds,
            'damage_type': spell.damage_type
        })())
    
    # Get available combinations
    available_combinations = combination_service.get_available_combinations(spell_data)
    
    return {
        "spells": [spell.name for spell in spells],
        "available_combinations": [
            {
                "name": combo.name,
                "type": combo.type.value,
                "description": combo.description,
                "mp_cost_multiplier": combo.mp_cost_multiplier,
                "estimated_cost": combination_service.calculate_combination_cost(spell_data, combo),
                "synergy_effects": combo.synergy_bonus
            }
            for combo in available_combinations
        ]
    }

@router.post("/spells/cast-combination")
async def cast_spell_combination(
    character_id: int,
    spell_ids: List[UUID],
    combination_name: str,
    db: Session = Depends(get_db)
):
    """Cast a spell combination for enhanced synergistic effects."""
    # Get spells
    spells = db.query(Spell).filter(Spell.id.in_(spell_ids)).all()
    
    if len(spells) != len(spell_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more spells not found"
        )
    
    # Get character MP
    character_mp = db.query(CharacterMP).filter(
        CharacterMP.character_id == character_id
    ).first()
    
    if not character_mp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MP tracking not found for character {character_id}"
        )
    
    # Get combination service
    _, combination_service = get_advanced_magic_services()
    
    # Convert spells to data objects
    spell_data = []
    for spell in spells:
        spell_data.append(type('SpellData', (), {
            'name': spell.name,
            'school': spell.school,
            'mp_cost': spell.mp_cost,
            'base_damage': spell.base_damage,
            'base_healing': spell.base_healing,
            'range_feet': spell.range_feet,
            'duration_seconds': spell.duration_seconds,
            'damage_type': spell.damage_type
        })())
    
    # Attempt combination
    combination_result = combination_service.combine_spells(
        spells=spell_data,
        combination_name=combination_name,
        available_mp=character_mp.current_mp
    )
    
    if not combination_result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=combination_result.error_message
        )
    
    # Deduct MP for combination
    character_mp.current_mp -= combination_result.total_mp_cost
    db.commit()
    
    return {
        "success": True,
        "combination_name": combination_result.combination_name,
        "spells_combined": combination_result.spells_combined,
        "total_mp_cost": combination_result.total_mp_cost,
        "remaining_mp": character_mp.current_mp,
        "synergy_effects": combination_result.synergy_effects,
        "enhanced_properties": combination_result.enhanced_properties
    }

# === MP TRACKING ENDPOINTS ===

@router.get("/mp/{character_id}", response_model=CharacterMPResponse)
async def get_character_mp(
    character_id: int,
    db: Session = Depends(get_db)
):
    """Get character's current MP status (canonical system)."""
    character_mp = db.query(CharacterMP).filter(
        CharacterMP.character_id == character_id
    ).first()
    
    if not character_mp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MP tracking not found for character {character_id}"
        )
    
    return CharacterMPResponse.model_validate(character_mp)

@router.post("/mp/{character_id}/rest")
async def restore_mp(
    character_id: int,
    rest_request: RestoreMatrixPointsRequest,
    db: Session = Depends(get_db)
):
    """Restore MP through rest (canonical system - not spell slot restoration)."""
    character_mp = db.query(CharacterMP).filter(
        CharacterMP.character_id == character_id
    ).first()
    
    if not character_mp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MP tracking not found for character {character_id}"
        )
    
    # Calculate MP restoration based on rest type
    if rest_request.rest_type == "short":
        mp_restored = int(character_mp.mp_regeneration_rate * rest_request.hours_rested)
    elif rest_request.rest_type == "long":
        mp_restored = int(character_mp.mp_regeneration_rate * rest_request.hours_rested * 2)
    elif rest_request.rest_type == "full":
        mp_restored = character_mp.max_mp  # Full restoration
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid rest type: {rest_request.rest_type}"
        )
    
    # Apply restoration
    old_mp = character_mp.current_mp
    character_mp.current_mp = min(character_mp.max_mp, character_mp.current_mp + mp_restored)
    character_mp.last_rest = datetime.utcnow()
    
    db.commit()
    
    return {
        "rest_type": rest_request.rest_type,
        "hours_rested": rest_request.hours_rested,
        "mp_before": old_mp,
        "mp_restored": character_mp.current_mp - old_mp,
        "mp_after": character_mp.current_mp,
        "max_mp": character_mp.max_mp
    }

# === DOMAIN ACCESS ENDPOINTS ===

@router.get("/domains/{character_id}", response_model=List[DomainAccessResponse])
async def get_domain_access(
    character_id: int,
    db: Session = Depends(get_db)
):
    """Get character's domain access (canonical system)."""
    domain_access = db.query(CharacterDomainAccess).filter(
        CharacterDomainAccess.character_id == character_id
    ).all()
    
    if not domain_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No domain access found for character {character_id}"
        )
    
    # Add efficiency bonus calculation
    responses = []
    for access in domain_access:
        # Get domain efficiency from configuration
        magic_service, _ = get_magic_services()
        domain_config = magic_service.config_repository.get_domain(access.domain)
        efficiency_bonus = domain_config.get("mp_efficiency", 1.0) if domain_config else 1.0
        
        response = DomainAccessResponse(
            character_id=access.character_id,
            domain=access.domain,
            access_level=access.access_level,
            unlocked_at=access.unlocked_at,
            efficiency_bonus=efficiency_bonus
        )
        responses.append(response)
    
    return responses

@router.post("/domains/{character_id}")
async def update_domain_access(
    character_id: int,
    domain_request: UpdateDomainAccessRequest,
    db: Session = Depends(get_db)
):
    """Update character's domain access (canonical system)."""
    # Check if access already exists
    existing = db.query(CharacterDomainAccess).filter(
        CharacterDomainAccess.character_id == character_id,
        CharacterDomainAccess.domain == domain_request.domain
    ).first()
    
    if existing:
        # Update existing access level
        existing.access_level = domain_request.access_level
    else:
        # Create new domain access
        new_access = CharacterDomainAccess(
            character_id=character_id,
            domain=domain_request.domain,
            access_level=domain_request.access_level
        )
        db.add(new_access)
    
    db.commit()
    
    return {
        "message": f"Domain access updated for character {character_id}",
        "domain": domain_request.domain,
        "access_level": domain_request.access_level
    }

# === CONCENTRATION TRACKING ENDPOINTS ===

@router.get("/concentration/{character_id}", response_model=List[ConcentrationResponse])
async def get_active_concentration(
    character_id: int,
    db: Session = Depends(get_db)
):
    """Get active concentration effects for character (canonical system)."""
    concentration_effects = db.query(ConcentrationTracking).filter(
        ConcentrationTracking.caster_id == character_id
    ).all()
    
    responses = []
    for effect in concentration_effects:
        responses.append(ConcentrationResponse(
            id=effect.id,
            caster_id=effect.caster_id,
            spell_id=effect.spell_id,
            spell_name=effect.spell.name,
            target_id=effect.target_id,
            cast_at=effect.cast_at,
            expires_at=effect.expires_at,
            domain_used=effect.domain_used,
            mp_spent=effect.mp_spent,
            effect_data=effect.effect_data
        ))
    
    return responses

@router.delete("/concentration/{effect_id}")
async def end_concentration(
    effect_id: UUID,
    db: Session = Depends(get_db)
):
    """End a concentration effect (canonical system)."""
    effect = db.query(ConcentrationTracking).filter(
        ConcentrationTracking.id == effect_id
    ).first()
    
    if not effect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concentration effect {effect_id} not found"
        )
    
    db.delete(effect)
    db.commit()
    
    return {"message": "Concentration effect ended", "effect_id": effect_id}

