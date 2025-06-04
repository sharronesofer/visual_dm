"""
Character Relationship Repository
---------------------------------
Repository for handling Character Relationship database operations.
Separates data access from business logic.
"""
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func
from uuid import UUID
from datetime import datetime

from backend.systems.character.models.character import Character
from backend.infrastructure.systems.npc.models.models import NpcEntity
from backend.infrastructure.shared.exceptions import NotFoundError, RepositoryError


class CharacterRelationshipRepository:
    """Repository for Character Relationship database operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_character_by_id(self, character_id: str) -> Optional[Character]:
        """Get character by ID"""
        try:
            return self.db.query(Character).filter(Character.uuid == character_id).first()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching character: {str(e)}")
    
    def get_npc_by_id(self, npc_id: UUID) -> Optional[NpcEntity]:
        """Get NPC by UUID"""
        try:
            return self.db.query(NpcEntity).filter(NpcEntity.uuid == npc_id).first()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching NPC: {str(e)}")
    
    def get_character_relationships_data(self, character_id: str) -> List[Dict[str, Any]]:
        """Get all relationship data for a character from database"""
        try:
            # This would query actual relationship tables when they exist
            # For now, return empty list as placeholder
            return []
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching character relationships: {str(e)}")
    
    def save_relationship_data(self, character_id: str, npc_id: UUID, relationship_data: Dict[str, Any]) -> None:
        """Save relationship data to database"""
        try:
            # This would save to actual relationship tables when they exist
            # For now, this is a placeholder
            pass
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error saving relationship data: {str(e)}")
    
    def get_relationship_data(self, character_id: str, npc_id: UUID) -> Optional[Dict[str, Any]]:
        """Get specific relationship data from database"""
        try:
            # This would query actual relationship tables when they exist
            # For now, return None as placeholder
            return None
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching relationship data: {str(e)}")
    
    def get_faction_relationship_status(self, faction_a_id: str, faction_b_id: str) -> str:
        """Get relationship status between two factions"""
        try:
            # This would query faction relationship tables when they exist
            # For now, return neutral as default
            return "neutral"
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching faction relationship: {str(e)}")
    
    def get_character_faction_id(self, character_id: str) -> Optional[str]:
        """Get character's primary faction ID"""
        try:
            character = self.get_character_by_id(character_id)
            if character and hasattr(character, 'faction_id'):
                return character.faction_id
            return None
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching character faction: {str(e)}")
    
    def get_npc_faction_id(self, npc_id: UUID) -> Optional[str]:
        """Get NPC's primary faction ID"""
        try:
            npc = self.get_npc_by_id(npc_id)
            if npc and hasattr(npc, 'faction_id'):
                return npc.faction_id
            return None
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching NPC faction: {str(e)}")
    
    def update_relationship_batch(self, relationship_updates: List[Dict[str, Any]]) -> None:
        """Update multiple relationships in a batch"""
        try:
            # This would batch update relationship tables when they exist
            # For now, this is a placeholder
            pass
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error batch updating relationships: {str(e)}")
    
    def commit(self):
        """Commit current transaction"""
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Error committing transaction: {str(e)}")
    
    def rollback(self):
        """Rollback current transaction"""
        try:
            self.db.rollback()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error rolling back transaction: {str(e)}")
    
    def refresh(self, entity):
        """Refresh entity from database"""
        try:
            self.db.refresh(entity)
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error refreshing entity: {str(e)}") 