"""
Character Relationship API Router
---------------------------------
FastAPI router for character relationship management.
Handles character-to-character relationships, factions, and social connections.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

# Import canonical character system components
from backend.infrastructure.database import get_db
from backend.systems.character.services.character_service import CharacterService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/characters/{character_id}/relationships", tags=["character-relationships"])

@router.get("/")
async def get_character_relationships(
    character_id: int = Path(..., description="Character ID"),
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Get all relationships for a character.
    """
    try:
        # Verify character exists
        character = await character_service.get_character_by_id(db=db, character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        relationships = await character_service.get_character_relationships(
            db=db, 
            character_id=character_id,
            relationship_type=relationship_type
        )
        
        return {"character_id": character_id, "relationships": relationships}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving relationships for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/")
async def create_character_relationship(
    character_id: int = Path(..., description="Character ID"),
    relationship_data: Dict[str, Any] = ...,
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Create a new character relationship.
    """
    try:
        # Verify character exists
        character = await character_service.get_character_by_id(db=db, character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        relationship = await character_service.create_character_relationship(
            db=db,
            character_id=character_id,
            relationship_data=relationship_data
        )
        
        return relationship
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating relationship for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{relationship_id}")
async def update_character_relationship(
    character_id: int = Path(..., description="Character ID"),
    relationship_id: int = Path(..., description="Relationship ID"),
    relationship_data: Dict[str, Any] = ...,
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Update an existing character relationship.
    """
    try:
        # Verify character exists
        character = await character_service.get_character_by_id(db=db, character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        relationship = await character_service.update_character_relationship(
            db=db,
            character_id=character_id,
            relationship_id=relationship_id,
            relationship_data=relationship_data
        )
        
        if not relationship:
            raise HTTPException(status_code=404, detail="Relationship not found")
        
        return relationship
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating relationship {relationship_id} for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{relationship_id}", status_code=204)
async def delete_character_relationship(
    character_id: int = Path(..., description="Character ID"),
    relationship_id: int = Path(..., description="Relationship ID"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Delete a character relationship.
    """
    try:
        # Verify character exists
        character = await character_service.get_character_by_id(db=db, character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        success = await character_service.delete_character_relationship(
            db=db,
            character_id=character_id,
            relationship_id=relationship_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Relationship not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting relationship {relationship_id} for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Faction relationships
@router.get("/factions")
async def get_character_faction_relationships(
    character_id: int = Path(..., description="Character ID"),
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Get all faction relationships for a character.
    """
    try:
        # Verify character exists
        character = await character_service.get_character_by_id(db=db, character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        faction_relationships = await character_service.get_character_faction_relationships(
            db=db, 
            character_id=character_id
        )
        
        return {"character_id": character_id, "faction_relationships": faction_relationships}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving faction relationships for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/factions")
async def create_character_faction_relationship(
    character_id: int = Path(..., description="Character ID"),
    faction_relationship_data: Dict[str, Any] = ...,
    db: Session = Depends(get_db),
    character_service: CharacterService = Depends(lambda: CharacterService())
):
    """
    Create a new character-faction relationship.
    """
    try:
        # Verify character exists
        character = await character_service.get_character_by_id(db=db, character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        faction_relationship = await character_service.create_character_faction_relationship(
            db=db,
            character_id=character_id,
            faction_relationship_data=faction_relationship_data
        )
        
        return faction_relationship
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating faction relationship for character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@router.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint for relationship router."""
    return {"status": "healthy", "service": "relationship_router"}

__all__ = ["router"] 