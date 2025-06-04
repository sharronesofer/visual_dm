"""
Character API Router
-------------------
FastAPI router for character CRUD operations and management.
Provides comprehensive RESTful API endpoints for character system integration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

# Import canonical character system components
from backend.infrastructure.database import get_db
from backend.systems.character.models.character import Character
from backend.systems.character.services.character_service import CharacterService
from backend.infrastructure.schemas.character.character_schemas import (
    CharacterSchema,
    CharacterCreateSchema,
    CharacterUpdateSchema,
    CharacterListResponseSchema
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/characters", tags=["characters"])

@router.get("/", response_model=CharacterListResponseSchema)
async def list_characters(
    skip: int = Query(0, ge=0, description="Number of characters to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of characters to return"),
    race: Optional[str] = Query(None, description="Filter by character race"),
    level_min: Optional[int] = Query(None, ge=1, description="Minimum character level"),
    level_max: Optional[int] = Query(None, ge=1, description="Maximum character level"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Retrieve a list of characters with optional filtering.
    
    Supports pagination and filtering by race and level range.
    """
    try:
        characters = await character_service.list_characters(
            db=db,
            skip=skip,
            limit=limit,
            race=race,
            level_min=level_min,
            level_max=level_max
        )
        
        total_count = await character_service.count_characters(
            db=db,
            race=race,
            level_min=level_min,
            level_max=level_max
        )
        
        return CharacterListResponseSchema(
            characters=[CharacterSchema.from_orm(char) for char in characters],
            total=total_count,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing characters: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{character_id}", response_model=CharacterSchema)
async def get_character(
    character_id: int = Path(..., description="Character ID"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Retrieve a specific character by ID.
    """
    try:
        character = await character_service.get_character_by_id(db=db, character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return CharacterSchema.from_orm(character)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/uuid/{character_uuid}", response_model=CharacterSchema)
async def get_character_by_uuid(
    character_uuid: str = Path(..., description="Character UUID"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Retrieve a specific character by UUID.
    """
    try:
        character = await character_service.get_character_by_uuid(db=db, character_uuid=character_uuid)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return CharacterSchema.from_orm(character)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving character {character_uuid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=CharacterSchema, status_code=201)
async def create_character(
    character_data: CharacterCreateSchema,
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Create a new character.
    """
    try:
        character = await character_service.create_character(
            db=db,
            character_data=character_data.dict()
        )
        
        return CharacterSchema.from_orm(character)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating character: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{character_id}", response_model=CharacterSchema)
async def update_character(
    character_id: int = Path(..., description="Character ID"),
    character_data: CharacterUpdateSchema = ...,
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Update an existing character.
    """
    try:
        # Check if character exists
        existing_character = await character_service.get_character_by_id(db=db, character_id=character_id)
        if not existing_character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        character = await character_service.update_character(
            db=db,
            character_id=character_id,
            character_data=character_data.dict(exclude_unset=True)
        )
        
        return CharacterSchema.from_orm(character)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{character_id}", status_code=204)
async def delete_character(
    character_id: int = Path(..., description="Character ID"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Delete a character.
    """
    try:
        # Check if character exists
        existing_character = await character_service.get_character_by_id(db=db, character_id=character_id)
        if not existing_character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        await character_service.delete_character(db=db, character_id=character_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{character_id}/level-up", response_model=CharacterSchema)
async def level_up_character(
    character_id: int = Path(..., description="Character ID"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Level up a character.
    """
    try:
        character = await character_service.level_up_character(db=db, character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return CharacterSchema.from_orm(character)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leveling up character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{character_id}/heal", response_model=CharacterSchema)
async def heal_character(
    character_id: int = Path(..., description="Character ID"),
    heal_amount: int = Query(..., ge=1, description="Amount of HP to heal"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Heal a character by the specified amount.
    """
    try:
        character = await character_service.heal_character(db=db, character_id=character_id, amount=heal_amount)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return CharacterSchema.from_orm(character)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error healing character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{character_id}/damage", response_model=CharacterSchema)
async def damage_character(
    character_id: int = Path(..., description="Character ID"),
    damage_amount: int = Query(..., ge=1, description="Amount of damage to deal"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Deal damage to a character.
    """
    try:
        character = await character_service.damage_character(db=db, character_id=character_id, amount=damage_amount)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return CharacterSchema.from_orm(character)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error damaging character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{character_id}/visual-model")
async def get_character_visual_model(
    character_id: int = Path(..., description="Character ID"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Get the visual model for a character.
    """
    try:
        visual_model = await character_service.get_character_visual_model(db=db, character_id=character_id)
        if not visual_model:
            raise HTTPException(status_code=404, detail="Character or visual model not found")
        
        return visual_model.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving visual model for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{character_id}/visual-model")
async def update_character_visual_model(
    character_id: int = Path(..., description="Character ID"),
    visual_model_data: Dict[str, Any] = ...,
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Update the visual model for a character.
    """
    try:
        visual_model = await character_service.update_character_visual_model(
            db=db, 
            character_id=character_id, 
            visual_model_data=visual_model_data
        )
        if not visual_model:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return visual_model.to_dict()
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating visual model for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@router.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint for character router."""
    return {"status": "healthy", "service": "character_router"}

__all__ = ["router"] 