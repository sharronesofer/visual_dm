"""
Character Repository
------------------
Data access layer for character-related database operations. Handles direct
interactions with the Character and related models.
"""

from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError

from backend.core.database import get_db_session
from backend.core.utils.error import NotFoundError, DatabaseError
from backend.systems.character.models.character import Character, Skill

class CharacterRepository:
    """
    Repository for managing character-related database operations.
    Follows the repository pattern to abstract data access logic.
    """
    
    def __init__(self, db_session=None):
        """
        Initialize the repository with an optional database session.
        
        Args:
            db_session: SQLAlchemy database session (optional)
        """
        self.db_session = db_session
        
    def get_session(self):
        """
        Get or create a database session.
        
        Returns:
            SQLAlchemy database session
        """
        if self.db_session:
            return self.db_session
        return next(get_db_session())
    
    def get_by_id(self, character_id: int) -> Optional[Character]:
        """
        Get a character by ID.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Character instance or None if not found
        """
        session = self.get_session()
        return session.query(Character).filter(Character.id == character_id).first()
    
    def get_by_name(self, name: str) -> Optional[Character]:
        """
        Get a character by name.
        
        Args:
            name: Name of the character
            
        Returns:
            Character instance or None if not found
        """
        session = self.get_session()
        return session.query(Character).filter(Character.name == name).first()
    
    def get_all(self, 
               limit: int = 100, 
               offset: int = 0, 
               filters: Dict[str, Any] = None) -> List[Character]:
        """
        Get multiple characters with optional filtering and pagination.
        
        Args:
            limit: Maximum number of characters to return
            offset: Number of characters to skip
            filters: Dictionary of filter criteria
            
        Returns:
            List of Character instances
        """
        session = self.get_session()
        query = session.query(Character)
        
        if filters:
            # Apply filters
            if 'name' in filters:
                query = query.filter(Character.name.ilike(f"%{filters['name']}%"))
            if 'race' in filters:
                query = query.filter(Character.race == filters['race'])
            if 'level_min' in filters:
                query = query.filter(Character.level >= filters['level_min'])
            if 'level_max' in filters:
                query = query.filter(Character.level <= filters['level_max'])
                
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def create(self, character: Character) -> Character:
        """
        Create a new character.
        
        Args:
            character: Character instance to create
            
        Returns:
            Created Character instance
        """
        session = self.get_session()
        try:
            session.add(character)
            session.commit()
            session.refresh(character)
            return character
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Failed to create character: {str(e)}")
    
    def update(self, character: Character) -> Character:
        """
        Update an existing character.
        
        Args:
            character: Character instance to update
            
        Returns:
            Updated Character instance
        """
        session = self.get_session()
        try:
            session.commit()
            session.refresh(character)
            return character
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Failed to update character: {str(e)}")
    
    def delete(self, character_id: int) -> bool:
        """
        Delete a character.
        
        Args:
            character_id: ID of the character to delete
            
        Returns:
            True if the character was deleted, False otherwise
        """
        session = self.get_session()
        try:
            character = self.get_by_id(character_id)
            if not character:
                return False
                
            session.delete(character)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Failed to delete character: {str(e)}")
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """
        Count characters with optional filtering.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            Number of characters matching the criteria
        """
        session = self.get_session()
        query = session.query(Character)
        
        if filters:
            # Apply filters
            if 'name' in filters:
                query = query.filter(Character.name.ilike(f"%{filters['name']}%"))
            if 'race' in filters:
                query = query.filter(Character.race == filters['race'])
            if 'level_min' in filters:
                query = query.filter(Character.level >= filters['level_min'])
            if 'level_max' in filters:
                query = query.filter(Character.level <= filters['level_max'])
                
        return query.count()
    
    def get_skills(self, limit: int = 100, offset: int = 0) -> List[Skill]:
        """
        Get all available skills.
        
        Args:
            limit: Maximum number of skills to return
            offset: Number of skills to skip
            
        Returns:
            List of Skill instances
        """
        session = self.get_session()
        return session.query(Skill).limit(limit).offset(offset).all()
    
    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """
        Get a skill by name.
        
        Args:
            name: Name of the skill
            
        Returns:
            Skill instance or None if not found
        """
        session = self.get_session()
        return session.query(Skill).filter(Skill.name == name).first()
    
    def create_skill(self, name: str) -> Skill:
        """
        Create a new skill.
        
        Args:
            name: Name of the skill
            
        Returns:
            Created Skill instance
        """
        session = self.get_session()
        try:
            skill = Skill(name=name)
            session.add(skill)
            session.commit()
            session.refresh(skill)
            return skill
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Failed to create skill: {str(e)}")

    def add_skill_to_character(self, character_id: int, skill_name: str) -> Character:
        """
        Add a skill to a character.
        
        Args:
            character_id: ID of the character
            skill_name: Name of the skill
            
        Returns:
            Updated Character instance
        """
        session = self.get_session()
        try:
            character = self.get_by_id(character_id)
            if not character:
                raise NotFoundError(f"Character with ID {character_id} not found")
                
            skill = self.get_skill_by_name(skill_name)
            if not skill:
                skill = self.create_skill(skill_name)
                
            if skill not in character.skills:
                character.skills.append(skill)
                
            session.commit()
            session.refresh(character)
            return character
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Failed to add skill to character: {str(e)}")
    
    def remove_skill_from_character(self, character_id: int, skill_name: str) -> Character:
        """
        Remove a skill from a character.
        
        Args:
            character_id: ID of the character
            skill_name: Name of the skill
            
        Returns:
            Updated Character instance
        """
        session = self.get_session()
        try:
            character = self.get_by_id(character_id)
            if not character:
                raise NotFoundError(f"Character with ID {character_id} not found")
                
            skill = self.get_skill_by_name(skill_name)
            if skill and skill in character.skills:
                character.skills.remove(skill)
                
            session.commit()
            session.refresh(character)
            return character
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Failed to remove skill from character: {str(e)}")

# Singleton instance for easy access
character_repository = CharacterRepository()

__all__ = ['CharacterRepository', 'character_repository'] 