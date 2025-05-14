"""Character API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..services.character import CharacterService
from .schemas_pkg.character import CharacterCreate, CharacterResponse, CharacterUpdate
from ..core.api.fastapi import APIResponse, APIError, NotFoundError

router = APIRouter(tags=["characters"])

@router.get("/", response_model=APIResponse[List[CharacterResponse]])
async def list_characters(db: Session = Depends(get_db)):
    """List all characters.
    
    Args:
        db: Database session
        
    Returns:
        List of characters
    """
    try:
        service = CharacterService(db)
        data = service.get_characters()
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.post("/", response_model=CharacterResponse)
async def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character.
    
    Args:
        character: Character creation data
        db: Database session
        
    Returns:
        Created character
        
    Raises:
        HTTPException: If character creation fails
    """
    service = CharacterService(db)
    return service.create_character(character)

@router.get("/{character_id}", response_model=APIResponse[CharacterResponse])
async def get_character(character_id: int, db: Session = Depends(get_db)):
    """Get a specific character by ID.
    
    Args:
        character_id: Character ID
        db: Database session
        
    Returns:
        Character data
        
    Raises:
        NotFoundError: If character not found
        APIError: For other errors
    """
    try:
        service = CharacterService(db)
        character = service.get_character(character_id)
        if not character:
            raise NotFoundError("Character not found")
        return APIResponse.success(data=character)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    character: CharacterUpdate,
    db: Session = Depends(get_db)
):
    """Update a character.
    
    Args:
        character_id: Character ID
        character: Character update data
        db: Database session
        
    Returns:
        Updated character
        
    Raises:
        HTTPException: If character not found or update fails
    """
    service = CharacterService(db)
    updated_character = service.update_character(character_id, character)
    if not updated_character:
        raise HTTPException(status_code=404, detail="Character not found")
    return updated_character

@router.delete("/{character_id}")
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    """Delete a character.
    
    Args:
        character_id: Character ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If character not found or deletion fails
    """
    service = CharacterService(db)
    if not service.delete_character(character_id):
        raise HTTPException(status_code=404, detail="Character not found")
    return {"message": "Character deleted successfully"} 