"""
Character API
-----------
FastAPI router for character-related endpoints.
Replaces the Flask routes in character_routes.py.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from backend.infrastructure.database import get_db
from backend.systems.character.services.character_service import CharacterService
from backend.systems.character.models.character_builder import CharacterBuilder
from backend.systems.character.api.schemas import (
    CharacterCreate,
    CharacterResponse,
    CharacterUpdate,
    CharacterList
)

router = APIRouter(prefix="/characters", tags=["characters"])

@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db_session)
):
    """
    Create a new character.
    """
    try:
        service = CharacterService(db_session=db)
        character = service.build_character_from_input(character_data.dict())
        return service.create_character_from_builder(CharacterBuilder.from_dict(character))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating character: {str(e)}"
        )

@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(
    character_id: UUID,
    db: Session = Depends(get_db_session)
):
    """
    Get a character by ID.
    """
    try:
        service = CharacterService(db_session=db)
        return service.get_character_by_id(character_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character not found: {str(e)}"
        )

@router.get("/", response_model=List[CharacterList])
def list_characters(
    db: Session = Depends(get_db_session)
):
    """
    List all characters.
    """
    # Implementation would depend on a list_characters method in CharacterService
    # For now, we'll leave it as a stub
    try:
        service = CharacterService(db_session=db)
        return []  # Replace with service.list_characters()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing characters: {str(e)}"
        )

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(
    character_id: UUID,
    db: Session = Depends(get_db_session)
):
    """
    Delete a character by ID.
    """
    try:
        service = CharacterService(db_session=db)
        service.delete_character(character_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character not found or could not be deleted: {str(e)}"
        )

@router.put("/{character_id}", response_model=CharacterResponse)
def update_character(
    character_id: UUID,
    update_data: CharacterUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Update a character by ID.
    """
    try:
        service = CharacterService(db_session=db)
        return service.update_character_data(character_id, update_data.dict(exclude_unset=True))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character not found or could not be updated: {str(e)}"
        ) 