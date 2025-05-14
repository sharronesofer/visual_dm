"""Character service module."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..models import Character
from ..api.schemas_pkg.character import CharacterCreate, CharacterUpdate

class CharacterService:
    """Service for managing characters."""

    def __init__(self, db: Session):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db

    def get_characters(self) -> List[Character]:
        """Get all characters.
        
        Returns:
            List of characters
        """
        return self.db.query(Character).all()

    def get_character(self, character_id: int) -> Optional[Character]:
        """Get a character by ID.
        
        Args:
            character_id: Character ID
            
        Returns:
            Character if found, None otherwise
        """
        return self.db.query(Character).filter(Character.id == character_id).first()

    def create_character(self, character: CharacterCreate) -> Character:
        """Create a new character.
        
        Args:
            character: Character creation data
            
        Returns:
            Created character
            
        Raises:
            HTTPException: If character creation fails
        """
        db_character = Character(**character.dict())
        self.db.add(db_character)
        try:
            self.db.commit()
            self.db.refresh(db_character)
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return db_character

    def update_character(self, character_id: int, character: CharacterUpdate) -> Optional[Character]:
        """Update a character.
        
        Args:
            character_id: ID of character to update
            character: Character update data
            
        Returns:
            Updated character if found, None otherwise
            
        Raises:
            HTTPException: If character update fails
        """
        db_character = self.get_character(character_id)
        if not db_character:
            return None

        # Update character fields
        update_data = character.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_character, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_character)
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return db_character

    def delete_character(self, character_id: int) -> bool:
        """Delete a character.
        
        Args:
            character_id: ID of character to delete
            
        Returns:
            True if character was deleted, False if not found
        """
        db_character = self.get_character(character_id)
        if not db_character:
            return False

        try:
            self.db.delete(db_character)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return True 