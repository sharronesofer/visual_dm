"""
API router for the enchanting system.

Provides RESTful endpoints for:
- Disenchanting items to learn enchantments
- Applying enchantments to items
- Querying character enchanting profiles and available enchantments
- Managing enchantment learning progression
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from backend.systems.equipment.services.enchanting_service import EnchantingService
from backend.infrastructure.services.equipment.equipment_quality import EquipmentQualityService
from backend.systems.equipment.models.enchanting import (
    DisenchantmentOutcome, EnchantmentSchool, EnchantmentRarity,
    CharacterEnchantingProfile
)

# Initialize services
equipment_quality_service = EquipmentQualityService()
enchanting_service = EnchantingService(equipment_quality_service)

router = APIRouter(prefix="/enchanting", tags=["enchanting"])

# Request/Response Models

class DisenchantmentRequest(BaseModel):
    """Request to disenchant an item."""
    character_id: UUID
    item_id: UUID
    item_data: Dict[str, Any]  # Complete item data including enchantments
    arcane_manipulation_level: int = Field(ge=0, le=10)
    character_level: int = Field(ge=1, le=20)
    target_enchantment: Optional[str] = None

class DisenchantmentResponse(BaseModel):
    """Response from a disenchantment attempt."""
    success: bool
    outcome: str
    enchantment_learned: Optional[str]
    item_destroyed: bool
    experience_gained: int
    additional_consequences: List[str]
    attempt_id: UUID

class EnchantmentApplicationRequest(BaseModel):
    """Request to apply an enchantment to an item."""
    character_id: UUID
    item_id: UUID
    item_data: Dict[str, Any]
    enchantment_id: str
    gold_available: int = Field(ge=0)

class EnchantmentApplicationResponse(BaseModel):
    """Response from an enchantment application."""
    success: bool
    cost_paid: int
    final_power_level: Optional[int]
    mastery_increased: bool
    failure_reason: Optional[str]
    materials_lost: bool
    application_id: UUID

class AvailableEnchantmentInfo(BaseModel):
    """Information about an enchantment available for application."""
    enchantment_id: str
    name: str
    description: str
    school: str
    rarity: str
    cost: int
    mastery_level: int
    times_applied: int

class LearnableEnchantmentInfo(BaseModel):
    """Information about an enchantment that can be learned."""
    enchantment_id: str
    name: str
    description: str
    school: str
    rarity: str
    success_rate: float
    min_arcane_manipulation: int

class CharacterEnchantingInfo(BaseModel):
    """Character's enchanting profile information."""
    character_id: UUID
    learned_enchantments_count: int
    total_items_disenchanted: int
    successful_applications: int
    failed_applications: int
    success_rate: float
    preferred_school: Optional[str]
    known_enchantments: List[Dict[str, Any]]

# API Endpoints

@router.post("/disenchant", response_model=DisenchantmentResponse)
async def disenchant_item(request: DisenchantmentRequest):
    """
    Attempt to disenchant an item to learn its enchantments.
    
    The item will be destroyed in the process (on most outcomes).
    Success depends on character's Arcane Manipulation level and experience.
    """
    try:
        attempt = enchanting_service.attempt_disenchantment(
            character_id=request.character_id,
            item_id=request.item_id,
            item_data=request.item_data,
            arcane_manipulation_level=request.arcane_manipulation_level,
            character_level=request.character_level,
            target_enchantment=request.target_enchantment
        )
        
        return DisenchantmentResponse(
            success=attempt.outcome in [DisenchantmentOutcome.SUCCESS_LEARNED, DisenchantmentOutcome.SUCCESS_KNOWN],
            outcome=attempt.outcome.value,
            enchantment_learned=attempt.enchantment_learned,
            item_destroyed=attempt.item_destroyed,
            experience_gained=attempt.experience_gained,
            additional_consequences=attempt.additional_consequences,
            attempt_id=attempt.id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disenchant item: {str(e)}"
        )

@router.post("/enchant", response_model=EnchantmentApplicationResponse)
async def apply_enchantment(request: EnchantmentApplicationRequest):
    """
    Apply a learned enchantment to an item.
    
    Requires the character to have learned the enchantment through disenchanting.
    Costs gold and may fail, potentially losing materials.
    """
    try:
        application = enchanting_service.attempt_enchantment(
            character_id=request.character_id,
            item_id=request.item_id,
            item_data=request.item_data,
            enchantment_id=request.enchantment_id,
            gold_available=request.gold_available
        )
        
        return EnchantmentApplicationResponse(
            success=application.success,
            cost_paid=application.cost_paid,
            final_power_level=application.final_power_level if application.success else None,
            mastery_increased=getattr(application, 'mastery_increased', False),
            failure_reason=application.failure_reason,
            materials_lost=application.materials_lost,
            application_id=application.id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply enchantment: {str(e)}"
        )

@router.get("/character/{character_id}/available", response_model=List[AvailableEnchantmentInfo])
async def get_available_enchantments(character_id: UUID, item_data: Dict[str, Any]):
    """
    Get list of enchantments this character can apply to the specified item.
    
    Returns enchantments the character has learned that are compatible
    with the item's type and quality.
    """
    try:
        available_enchantments = enchanting_service.get_available_enchantments_for_item(
            character_id=character_id,
            item_data=item_data
        )
        
        return [
            AvailableEnchantmentInfo(
                enchantment_id=e['enchantment_id'],
                name=e['name'],
                description=e['description'],
                school=e['school'],
                rarity=e['rarity'],
                cost=e['cost'],
                mastery_level=e['mastery_level'],
                times_applied=e['times_applied']
            )
            for e in available_enchantments
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available enchantments: {str(e)}"
        )

@router.get("/item/learnable", response_model=List[LearnableEnchantmentInfo])
async def get_learnable_enchantments(character_id: UUID, item_data: Dict[str, Any]):
    """
    Get list of enchantments that can be learned by disenchanting this item.
    
    Returns only enchantments the character doesn't already know,
    with success rates and requirements.
    """
    try:
        learnable_enchantments = enchanting_service.get_learnable_enchantments_from_item(
            character_id=character_id,
            item_data=item_data
        )
        
        return [
            LearnableEnchantmentInfo(
                enchantment_id=e['enchantment_id'],
                name=e['name'],
                description=e['description'],
                school=e['school'],
                rarity=e['rarity'],
                success_rate=e['success_rate'],
                min_arcane_manipulation=e['min_arcane_manipulation']
            )
            for e in learnable_enchantments
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get learnable enchantments: {str(e)}"
        )

@router.get("/character/{character_id}/profile", response_model=CharacterEnchantingInfo)
async def get_character_enchanting_profile(character_id: UUID):
    """
    Get complete enchanting profile for a character.
    
    Includes learned enchantments, statistics, and progression information.
    """
    try:
        profile = enchanting_service.get_character_profile(character_id)
        
        # Calculate success rate
        total_attempts = profile.successful_applications + profile.failed_applications
        success_rate = (profile.successful_applications / total_attempts * 100) if total_attempts > 0 else 0.0
        
        # Format known enchantments
        known_enchantments = []
        for enchantment_id, learned_enchantment in profile.learned_enchantments.items():
            from backend.systems.equipment.models.enchanting import get_enchantment_definition
            enchantment_def = get_enchantment_definition(enchantment_id)
            if enchantment_def:
                known_enchantments.append({
                    'id': enchantment_id,
                    'name': enchantment_def.name,
                    'school': enchantment_def.school.value,
                    'rarity': enchantment_def.rarity.value,
                    'mastery_level': learned_enchantment.mastery_level,
                    'times_applied': learned_enchantment.times_applied,
                    'learned_at': learned_enchantment.learned_at.isoformat(),
                    'learned_from': learned_enchantment.learned_from_item
                })
        
        return CharacterEnchantingInfo(
            character_id=character_id,
            learned_enchantments_count=len(profile.learned_enchantments),
            total_items_disenchanted=profile.total_items_disenchanted,
            successful_applications=profile.successful_applications,
            failed_applications=profile.failed_applications,
            success_rate=round(success_rate, 1),
            preferred_school=profile.preferred_school.value if profile.preferred_school else None,
            known_enchantments=known_enchantments
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get character enchanting profile: {str(e)}"
        )

@router.get("/schools", response_model=List[Dict[str, str]])
async def get_enchantment_schools():
    """Get list of all enchantment schools."""
    return [
        {"id": school.value, "name": school.value.title()}
        for school in EnchantmentSchool
    ]

@router.get("/rarities", response_model=List[Dict[str, str]])
async def get_enchantment_rarities():
    """Get list of all enchantment rarities."""
    return [
        {"id": rarity.value, "name": rarity.value.title()}
        for rarity in EnchantmentRarity
    ]

@router.get("/enchantments/by-school/{school}", response_model=List[Dict[str, Any]])
async def get_enchantments_by_school(school: str):
    """Get all enchantments in a specific school."""
    try:
        school_enum = EnchantmentSchool(school)
        from backend.systems.equipment.models.enchanting import get_enchantments_by_school
        enchantments = get_enchantments_by_school(school_enum)
        
        return [
            {
                'id': e.id,
                'name': e.name,
                'description': e.description,
                'rarity': e.rarity.value,
                'min_arcane_manipulation': e.min_arcane_manipulation,
                'base_cost': e.base_cost,
                'min_item_quality': e.min_item_quality,
                'compatible_types': list(e.compatible_item_types),
                'thematic_tags': list(e.thematic_tags)
            }
            for e in enchantments
        ]
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid enchantment school: {school}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get enchantments by school: {str(e)}"
        )

@router.get("/enchantments/by-rarity/{rarity}", response_model=List[Dict[str, Any]])
async def get_enchantments_by_rarity(rarity: str):
    """Get all enchantments of a specific rarity."""
    try:
        rarity_enum = EnchantmentRarity(rarity)
        from backend.systems.equipment.models.enchanting import get_enchantments_by_rarity
        enchantments = get_enchantments_by_rarity(rarity_enum)
        
        return [
            {
                'id': e.id,
                'name': e.name,
                'description': e.description,
                'school': e.school.value,
                'min_arcane_manipulation': e.min_arcane_manipulation,
                'base_cost': e.base_cost,
                'min_item_quality': e.min_item_quality,
                'compatible_types': list(e.compatible_item_types),
                'thematic_tags': list(e.thematic_tags)
            }
            for e in enchantments
        ]
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid enchantment rarity: {rarity}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get enchantments by rarity: {str(e)}"
        ) 