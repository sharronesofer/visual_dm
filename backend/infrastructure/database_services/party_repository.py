"""
Party Repository
---------------
Repository for handling Party database operations.
Separates data access from business logic.
"""
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from datetime import datetime

from backend.systems.character.models.character import Character
from backend.infrastructure.shared.exceptions import NotFoundError, RepositoryError


class PartyRepository:
    """Repository for Party database operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_character_by_id(self, character_id: Union[str, UUID]) -> Optional[Character]:
        """Get character by ID"""
        try:
            return self.db.query(Character).filter(Character.id == character_id).first()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get character by ID {character_id}: {str(e)}")
    
    def update_character_party(self, character_id: Union[str, UUID], party_id: Optional[str]) -> Character:
        """Update character's party reference"""
        try:
            character = self.get_character_by_id(character_id)
            if not character:
                raise NotFoundError(f"Character {character_id} not found")
            
            character.party_id = party_id
            self.db.flush()
            return character
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to update character party: {str(e)}")
    
    def get_characters_by_ids(self, character_ids: List[Union[str, UUID]]) -> List[Character]:
        """Get multiple characters by their IDs"""
        try:
            return self.db.query(Character).filter(Character.id.in_(character_ids)).all()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get characters: {str(e)}")
    
    def get_party_members(self, party_id: str) -> List[Character]:
        """Get all characters that are members of a party"""
        try:
            return self.db.query(Character).filter(Character.party_id == party_id).all()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get party members: {str(e)}")
    
    def update_character_xp(self, character_id: Union[str, UUID], xp_amount: int) -> Character:
        """Update character's XP"""
        try:
            character = self.get_character_by_id(character_id)
            if not character:
                raise NotFoundError(f"Character {character_id} not found")
            
            # Assuming character has an xp field
            current_xp = getattr(character, 'xp', 0)
            character.xp = current_xp + xp_amount
            self.db.flush()
            return character
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to update character XP: {str(e)}")
    
    def commit(self):
        """Commit transaction"""
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to commit transaction: {str(e)}")
    
    def rollback(self):
        """Rollback transaction"""
        self.db.rollback()
    
    def refresh(self, character: Character):
        """Refresh character instance"""
        self.db.refresh(character) 