"""
Character Relationship Service
----------------------------
Service for managing character relationships including NPC, faction, and quest relationships.
"""

from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4
from datetime import datetime

# Business logic imports
from backend.systems.character.models.relationship import Relationship, RelationshipType
from backend.infrastructure.database_services.relationship_repository import RelationshipRepository
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
from backend.infrastructure.events.events.canonical_events import (
    RelationshipCreated, RelationshipUpdated, RelationshipDeleted
)
from backend.infrastructure.shared.exceptions import NotFoundError, RepositoryError, ValidationError

import logging

logger = logging.getLogger(__name__)


class RelationshipService:
    """Service for managing character relationships with full database integration"""
    
    def __init__(self, relationship_repository: RelationshipRepository):
        self.relationship_repository = relationship_repository
        self.event_dispatcher = EventDispatcher()
        logger.info("RelationshipService initialized")

    def create_relationship(self, 
                           source_entity_id: Union[str, UUID], 
                           target_entity_id: Union[str, UUID],
                           relationship_type: Union[str, RelationshipType],
                           strength: int = 0,
                           metadata: Optional[Dict[str, Any]] = None,
                           commit: bool = True) -> Relationship:
        """
        Creates a new relationship between two entities.
        
        Args:
            source_entity_id: ID of the source entity (usually character)
            target_entity_id: ID of the target entity
            relationship_type: Type of relationship
            strength: Relationship strength (-100 to 100)
            metadata: Additional metadata
            commit: Whether to commit the transaction
            
        Returns:
            Created Relationship instance
        """
        # Check for existing relationship
        existing = self.relationship_repository.find_existing(
            source_entity_id, target_entity_id, relationship_type
        )
        
        if existing:
            logger.warning(f"Relationship already exists between {source_entity_id} and {target_entity_id}")
            return existing
        
        # Validate relationship type
        if isinstance(relationship_type, str):
            try:
                relationship_type = RelationshipType(relationship_type)
            except ValueError:
                raise ValidationError(f"Invalid relationship type: {relationship_type}")
        
        # Validate strength
        if not (-100 <= strength <= 100):
            raise ValidationError("Relationship strength must be between -100 and 100")
        
        relationship_data = {
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "relationship_type": relationship_type,
            "strength": strength,
            "metadata": metadata or {}
        }
        
        new_relationship = self.relationship_repository.create(relationship_data)
        
        if commit:
            try:
                self.relationship_repository.commit()
                self.relationship_repository.refresh(new_relationship)
                
                # Dispatch relationship created event
                self.event_dispatcher.dispatch(RelationshipCreated(
                    source_id=str(source_entity_id),
                    target_id=str(target_entity_id),
                    relationship_type=str(relationship_type),
                    strength=strength
                ))
                
                logger.info(f"Created relationship: {source_entity_id} -> {target_entity_id} ({relationship_type})")
            except Exception as e:
                self.relationship_repository.rollback()
                raise RepositoryError(f"Failed to create relationship: {str(e)}")
        
        return new_relationship

    def get_character_relationships(self, 
                                  character_id: Union[str, UUID], 
                                  relationship_type: Optional[str] = None) -> List[Relationship]:
        """Get all relationships for a character, optionally filtered by type"""
        return self.relationship_repository.get_character_relationships(character_id, relationship_type)

    def get_faction_relationships(self, character_id: Union[str, UUID]) -> List[Relationship]:
        """Get faction relationships for a character"""
        return self.relationship_repository.get_faction_relationships(character_id)

    def get_quest_relationships(self, character_id: Union[str, UUID]) -> List[Relationship]:
        """Get quest relationships for a character"""
        return self.relationship_repository.get_quest_relationships(character_id)

    def update_relationship_strength(self, 
                                   relationship_id: Union[int, UUID],
                                   new_strength: int,
                                   commit: bool = True) -> Optional[Relationship]:
        """Update the strength of a relationship"""
        relationship = self.relationship_repository.get_by_id(relationship_id)
        if not relationship:
            raise NotFoundError(f"Relationship with ID {relationship_id} not found")
        
        # Validate strength
        if not (-100 <= new_strength <= 100):
            raise ValidationError("Relationship strength must be between -100 and 100")
        
        old_strength = relationship.strength
        update_data = {"strength": new_strength}
        
        updated_relationship = self.relationship_repository.update(relationship, update_data)
        
        if commit:
            try:
                self.relationship_repository.commit()
                self.relationship_repository.refresh(updated_relationship)
                
                # Dispatch relationship updated event
                self.event_dispatcher.dispatch(RelationshipUpdated(
                    relationship_id=str(relationship_id),
                    source_id=updated_relationship.source_entity_id,
                    target_id=updated_relationship.target_entity_id,
                    old_strength=old_strength,
                    new_strength=new_strength
                ))
                
                logger.info(f"Updated relationship {relationship_id} strength: {old_strength} -> {new_strength}")
            except Exception as e:
                self.relationship_repository.rollback()
                raise RepositoryError(f"Failed to update relationship: {str(e)}")
        
        return updated_relationship

    def update_relationship_metadata(self, 
                                   relationship_id: Union[int, UUID],
                                   metadata_updates: Dict[str, Any],
                                   commit: bool = True) -> Optional[Relationship]:
        """Update the metadata of a relationship"""
        relationship = self.relationship_repository.get_by_id(relationship_id)
        if not relationship:
            raise NotFoundError(f"Relationship with ID {relationship_id} not found")
        
        # Merge metadata
        current_metadata = relationship.metadata or {}
        current_metadata.update(metadata_updates)
        
        update_data = {"metadata": current_metadata}
        updated_relationship = self.relationship_repository.update(relationship, update_data)
        
        if commit:
            try:
                self.relationship_repository.commit()
                self.relationship_repository.refresh(updated_relationship)
                logger.info(f"Updated relationship {relationship_id} metadata")
            except Exception as e:
                self.relationship_repository.rollback()
                raise RepositoryError(f"Failed to update relationship metadata: {str(e)}")
        
        return updated_relationship

    def delete_relationship(self, relationship_id: Union[int, UUID], commit: bool = True) -> bool:
        """Delete a relationship"""
        relationship = self.relationship_repository.get_by_id(relationship_id)
        if not relationship:
            raise NotFoundError(f"Relationship with ID {relationship_id} not found")
        
        source_id = relationship.source_entity_id
        target_id = relationship.target_entity_id
        relationship_type = relationship.relationship_type
        
        success = self.relationship_repository.delete(relationship)
        
        if commit and success:
            try:
                self.relationship_repository.commit()
                
                # Dispatch relationship deleted event
                self.event_dispatcher.dispatch(RelationshipDeleted(
                    relationship_id=str(relationship_id),
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=str(relationship_type)
                ))
                
                logger.info(f"Deleted relationship {relationship_id}")
                return True
            except Exception as e:
                self.relationship_repository.rollback()
                raise RepositoryError(f"Failed to delete relationship: {str(e)}")
        
        return success

    # --- Helper Methods for Specific Relationship Types ---
    
    def create_faction_relationship(self, 
                                  character_id: Union[str, UUID],
                                  faction_id: Union[str, UUID],
                                  reputation: int,
                                  standing: str = "neutral") -> Relationship:
        """Create a faction relationship with reputation and standing"""
        metadata = {
            "reputation": reputation,
            "standing": standing,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return self.create_relationship(
            source_entity_id=character_id,
            target_entity_id=faction_id,
            relationship_type=RelationshipType.FACTION,
            strength=reputation,
            metadata=metadata
        )
    
    def create_quest_relationship(self, 
                                character_id: Union[str, UUID],
                                quest_id: Union[str, UUID],
                                status: str = "active",
                                progress: float = 0.0) -> Relationship:
        """Create a quest relationship with status and progress"""
        metadata = {
            "status": status,
            "progress": progress,
            "started_at": datetime.utcnow().isoformat()
        }
        
        return self.create_relationship(
            source_entity_id=character_id,
            target_entity_id=quest_id,
            relationship_type=RelationshipType.QUEST,
            strength=0,  # Quest relationships use metadata for tracking
            metadata=metadata
        )
    
    def create_character_relationship(self,
                                    source_character_id: Union[str, UUID],
                                    target_character_id: Union[str, UUID],
                                    relationship_data: Dict[str, Any]) -> Relationship:
        """Create a relationship between two characters"""
        relationship_type = relationship_data.get("type", RelationshipType.PERSONAL)
        strength = relationship_data.get("strength", 0)
        metadata = relationship_data.get("metadata", {})
        
        # Add relationship creation timestamp
        metadata["created_at"] = datetime.utcnow().isoformat()
        
        return self.create_relationship(
            source_entity_id=source_character_id,
            target_entity_id=target_character_id,
            relationship_type=relationship_type,
            strength=strength,
            metadata=metadata
        )
