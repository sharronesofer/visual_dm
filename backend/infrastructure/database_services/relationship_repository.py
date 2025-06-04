"""
Relationship Repository
----------------------
Repository for handling Relationship database operations.
Separates data access from business logic.
"""
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID

from backend.systems.character.models.relationship import Relationship, RelationshipType
from backend.infrastructure.shared.exceptions import NotFoundError, RepositoryError


class RelationshipRepository:
    """Repository for Relationship database operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_id(self, relationship_id: Union[int, UUID]) -> Optional[Relationship]:
        """Get relationship by ID"""
        try:
            return self.db.query(Relationship).filter(Relationship.id == relationship_id).first()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get relationship by ID {relationship_id}: {str(e)}")
    
    def find_existing(self, source_id: Union[str, UUID], target_id: Union[str, UUID], 
                     relationship_type: Union[str, RelationshipType]) -> Optional[Relationship]:
        """Find existing relationship between entities"""
        try:
            return self.db.query(Relationship).filter(
                Relationship.source_entity_id == str(source_id),
                Relationship.target_entity_id == str(target_id),
                Relationship.relationship_type == relationship_type
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to find existing relationship: {str(e)}")
    
    def get_character_relationships(self, character_id: Union[str, UUID], 
                                  relationship_type: Optional[str] = None) -> List[Relationship]:
        """Get all relationships for a character"""
        try:
            query = self.db.query(Relationship).filter(
                Relationship.source_entity_id == str(character_id)
            )
            
            if relationship_type:
                query = query.filter(Relationship.relationship_type == relationship_type)
                
            return query.all()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get character relationships: {str(e)}")
    
    def get_faction_relationships(self, character_id: Union[str, UUID]) -> List[Relationship]:
        """Get faction relationships for a character"""
        try:
            return self.db.query(Relationship).filter(
                Relationship.source_entity_id == str(character_id),
                Relationship.relationship_type == RelationshipType.FACTION
            ).all()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get faction relationships: {str(e)}")
    
    def get_quest_relationships(self, character_id: Union[str, UUID]) -> List[Relationship]:
        """Get quest relationships for a character"""
        try:
            return self.db.query(Relationship).filter(
                Relationship.source_entity_id == str(character_id),
                Relationship.relationship_type == RelationshipType.QUEST
            ).all()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get quest relationships: {str(e)}")
    
    def create(self, relationship_data: Dict[str, Any]) -> Relationship:
        """Create a new relationship"""
        try:
            new_relationship = Relationship(
                source_entity_id=str(relationship_data.get("source_entity_id")),
                target_entity_id=str(relationship_data.get("target_entity_id")),
                relationship_type=relationship_data.get("relationship_type"),
                strength=relationship_data.get("strength", 0),
                metadata=relationship_data.get("metadata", {})
            )
            
            self.db.add(new_relationship)
            self.db.flush()  # Get ID without committing
            return new_relationship
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to create relationship: {str(e)}")
    
    def update(self, relationship: Relationship, update_data: Dict[str, Any]) -> Relationship:
        """Update relationship with new data"""
        try:
            for key, value in update_data.items():
                if hasattr(relationship, key):
                    setattr(relationship, key, value)
            
            self.db.flush()
            return relationship
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to update relationship {relationship.id}: {str(e)}")
    
    def delete(self, relationship: Relationship) -> bool:
        """Delete a relationship"""
        try:
            self.db.delete(relationship)
            self.db.flush()
            return True
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to delete relationship {relationship.id}: {str(e)}")
    
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
    
    def refresh(self, relationship: Relationship):
        """Refresh relationship instance"""
        self.db.refresh(relationship) 