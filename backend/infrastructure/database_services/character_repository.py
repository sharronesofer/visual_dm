"""
Character Repository
-------------------
Repository for handling Character database operations.
Separates data access from business logic.
"""
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID

from backend.systems.character.models.character import Character
from backend.infrastructure.shared.exceptions import NotFoundError, RepositoryError


class CharacterRepository:
    """Repository for Character database operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_id(self, character_id: Union[int, UUID]) -> Optional[Character]:
        """Get character by ID"""
        try:
            return self.db.query(Character).filter(Character.id == character_id).first()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get character by ID {character_id}: {str(e)}")
    
    def get_by_uuid(self, character_uuid: Union[str, UUID]) -> Optional[Character]:
        """Get character by UUID"""
        try:
            return self.db.query(Character).filter(Character.uuid == str(character_uuid)).first()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get character by UUID {character_uuid}: {str(e)}")
    
    def create(self, character_data: Dict[str, Any]) -> Character:
        """Create a new character"""
        try:
            new_character = Character(
                name=character_data.get("name"),
                race=character_data.get("race"),
                level=character_data.get("level", 1),
                stats=character_data.get("stats"),
                background=character_data.get("background"),
                alignment=character_data.get("alignment", "Neutral"),
                notes=character_data.get("notes", []),
            )
            
            self.db.add(new_character)
            self.db.flush()  # Get ID without committing
            return new_character
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to create character: {str(e)}")
    
    def update(self, character: Character, update_data: Dict[str, Any]) -> Character:
        """Update character with new data"""
        try:
            for key, value in update_data.items():
                if hasattr(character, key):
                    setattr(character, key, value)
                elif key in character.stats and isinstance(character.stats, dict):
                    # Handle stats JSON field
                    if not isinstance(character.stats, dict):
                        character.stats = dict(character.stats or {})
                    character.stats[key] = value
                    from sqlalchemy.orm.attributes import flag_modified
                    flag_modified(character, "stats")
            
            self.db.flush()
            return character
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to update character {character.id}: {str(e)}")
    
    def delete(self, character: Character) -> bool:
        """Delete a character"""
        try:
            self.db.delete(character)
            self.db.flush()
            return True
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to delete character {character.id}: {str(e)}")
    
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