"""
Relationship Service
------------------
Service for managing character relationships with other entities.
Provides methods for creating, updating, retrieving, and removing relationships.
"""

import logging
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.systems.events.event_dispatcher import EventDispatcher
from backend.systems.events.canonical_events import RelationshipCreated, RelationshipUpdated, RelationshipRemoved
from backend.systems.character.models.relationship import Relationship, RelationshipType
from backend.systems.character.models.character import Character

logger = logging.getLogger(__name__)

class RelationshipService:
    """
    Service for managing character relationships with other entities.
    Follows the repository pattern for data access.
    """
    
    def __init__(self, db_session: Session):
        """Initialize the service with a database session."""
        self.db = db_session
        self.event_dispatcher = EventDispatcher.get_instance()
    
    # Create Methods
    
    def create_relationship(self, 
                           source_id: Union[str, UUID], 
                           target_id: Union[str, UUID], 
                           rel_type: Union[str, RelationshipType], 
                           data: Dict[str, Any] = None) -> Relationship:
        """
        Create a generic relationship between two entities.
        
        Args:
            source_id: UUID of the source entity
            target_id: UUID of the target entity
            rel_type: Type of relationship (faction, quest, etc.)
            data: Additional type-specific data
            
        Returns:
            The created relationship object
        """
        # Convert string type to enum if needed
        if isinstance(rel_type, str):
            rel_type = RelationshipType(rel_type)
            
        # Create relationship
        relationship = Relationship(
            source_id=str(source_id),
            target_id=str(target_id),
            type=rel_type,
            data=data or {}
        )
        
        # Save to database
        self.db.add(relationship)
        self.db.commit()
        
        # Emit event
        self.event_dispatcher.emit(RelationshipCreated(
            event_type="relationship.created",
            source_id=str(source_id),
            target_id=str(target_id),
            relationship_type=rel_type,
            relationship_id=relationship.id,
            data=data or {}
        ))
        
        logger.info(f"Created {rel_type} relationship between {source_id} and {target_id}")
        return relationship
    
    def create_character_relationship(self, 
                                     source_character_id: Union[str, UUID], 
                                     target_character_id: Union[str, UUID], 
                                     relationship_level: int = 0, 
                                     relationship_type: str = "neutral") -> Relationship:
        """
        Create a relationship between two characters.
        
        Args:
            source_character_id: UUID of the source character
            target_character_id: UUID of the target character
            relationship_level: Numeric level of relationship (-100 to 100)
            relationship_type: Type descriptor (friend, rival, etc.)
            
        Returns:
            The created relationship object
        """
        return self.create_relationship(
            source_id=source_character_id,
            target_id=target_character_id,
            rel_type=RelationshipType.CHARACTER,
            data={
                "level": relationship_level,
                "type": relationship_type
            }
        )
    
    def create_faction_relationship(self, 
                                   character_id: Union[str, UUID], 
                                   faction_id: Union[str, UUID], 
                                   reputation: int = 0, 
                                   standing: str = "neutral") -> Relationship:
        """
        Create a relationship between a character and a faction.
        
        Args:
            character_id: UUID of the character
            faction_id: UUID of the faction
            reputation: Numeric reputation value
            standing: String description of standing
            
        Returns:
            The created relationship object
        """
        return self.create_relationship(
            source_id=character_id,
            target_id=faction_id,
            rel_type=RelationshipType.FACTION,
            data={
                "reputation": reputation,
                "standing": standing
            }
        )
    
    def create_quest_relationship(self, 
                                 character_id: Union[str, UUID], 
                                 quest_id: Union[str, UUID], 
                                 status: str = "active", 
                                 progress: float = 0.0) -> Relationship:
        """
        Create a relationship between a character and a quest.
        
        Args:
            character_id: UUID of the character
            quest_id: UUID of the quest
            status: Current quest status
            progress: Numeric progress value (0.0 to 1.0)
            
        Returns:
            The created relationship object
        """
        return self.create_relationship(
            source_id=character_id,
            target_id=quest_id,
            rel_type=RelationshipType.QUEST,
            data={
                "status": status,
                "progress": progress
            }
        )
    
    # Query Methods
    
    def get_relationship(self, 
                        source_id: Union[str, UUID], 
                        target_id: Union[str, UUID], 
                        rel_type: Union[str, RelationshipType]) -> Optional[Relationship]:
        """
        Get a specific relationship if it exists.
        
        Args:
            source_id: UUID of the source entity
            target_id: UUID of the target entity
            rel_type: Type of relationship
            
        Returns:
            Relationship object or None if not found
        """
        # Convert string type to enum if needed
        if isinstance(rel_type, str):
            rel_type = RelationshipType(rel_type)
            
        return self.db.query(Relationship).filter(
            Relationship.source_id == str(source_id),
            Relationship.target_id == str(target_id),
            Relationship.type == rel_type
        ).first()
    
    def get_relationships_by_source(self, 
                                  source_id: Union[str, UUID], 
                                  rel_type: Optional[Union[str, RelationshipType]] = None) -> List[Relationship]:
        """
        Get all relationships where the given entity is the source.
        
        Args:
            source_id: UUID of the source entity
            rel_type: Optional filter by relationship type
            
        Returns:
            List of relationship objects
        """
        query = self.db.query(Relationship).filter(Relationship.source_id == str(source_id))
        
        if rel_type:
            # Convert string type to enum if needed
            if isinstance(rel_type, str):
                rel_type = RelationshipType(rel_type)
            query = query.filter(Relationship.type == rel_type)
            
        return query.all()
    
    def get_relationships_by_target(self, 
                                  target_id: Union[str, UUID], 
                                  rel_type: Optional[Union[str, RelationshipType]] = None) -> List[Relationship]:
        """
        Get all relationships where the given entity is the target.
        
        Args:
            target_id: UUID of the target entity
            rel_type: Optional filter by relationship type
            
        Returns:
            List of relationship objects
        """
        query = self.db.query(Relationship).filter(Relationship.target_id == str(target_id))
        
        if rel_type:
            # Convert string type to enum if needed
            if isinstance(rel_type, str):
                rel_type = RelationshipType(rel_type)
            query = query.filter(Relationship.type == rel_type)
            
        return query.all()
    
    def get_all_relationships(self, 
                            entity_id: Union[str, UUID], 
                            rel_type: Optional[Union[str, RelationshipType]] = None) -> List[Relationship]:
        """
        Get all relationships where the given entity is either source or target.
        
        Args:
            entity_id: UUID of the entity
            rel_type: Optional filter by relationship type
            
        Returns:
            List of relationship objects
        """
        entity_id_str = str(entity_id)
        query = self.db.query(Relationship).filter(
            or_(
                Relationship.source_id == entity_id_str,
                Relationship.target_id == entity_id_str
            )
        )
        
        if rel_type:
            # Convert string type to enum if needed
            if isinstance(rel_type, str):
                rel_type = RelationshipType(rel_type)
            query = query.filter(Relationship.type == rel_type)
            
        return query.all()
    
    def get_character_relationships(self, character_id: Union[str, UUID]) -> List[Relationship]:
        """
        Get all character-to-character relationships for a given character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            List of relationship objects
        """
        return self.get_relationships_by_source(
            source_id=character_id,
            rel_type=RelationshipType.CHARACTER
        )
    
    def get_faction_relationships(self, character_id: Union[str, UUID]) -> List[Relationship]:
        """
        Get all faction relationships for a given character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            List of relationship objects
        """
        return self.get_relationships_by_source(
            source_id=character_id,
            rel_type=RelationshipType.FACTION
        )
    
    def get_quest_relationships(self, character_id: Union[str, UUID]) -> List[Relationship]:
        """
        Get all quest relationships for a given character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            List of relationship objects
        """
        return self.get_relationships_by_source(
            source_id=character_id,
            rel_type=RelationshipType.QUEST
        )
    
    # Update Methods
    
    def update_relationship_data(self, 
                               source_id: Union[str, UUID], 
                               target_id: Union[str, UUID], 
                               rel_type: Union[str, RelationshipType], 
                               new_data: Dict[str, Any]) -> Optional[Relationship]:
        """
        Update the data field of a specific relationship.
        
        Args:
            source_id: UUID of the source entity
            target_id: UUID of the target entity
            rel_type: Type of relationship
            new_data: New data to merge with existing data
            
        Returns:
            Updated relationship object or None if not found
        """
        # Convert string type to enum if needed
        if isinstance(rel_type, str):
            rel_type = RelationshipType(rel_type)
            
        relationship = self.get_relationship(source_id, target_id, rel_type)
        if not relationship:
            logger.warning(f"Attempted to update non-existent relationship: {source_id} -> {target_id} ({rel_type})")
            return None
        
        # Update data
        old_data = relationship.data.copy()
        relationship.update_data(new_data)
        
        # Save changes
        self.db.commit()
        
        # Emit event
        self.event_dispatcher.emit(RelationshipUpdated(
            event_type="relationship.updated",
            source_id=str(source_id),
            target_id=str(target_id),
            relationship_type=rel_type,
            relationship_id=relationship.id,
            old_data=old_data,
            new_data=relationship.data
        ))
        
        logger.info(f"Updated {rel_type} relationship between {source_id} and {target_id}")
        return relationship
    
    def update_character_relationship(self, 
                                     source_id: Union[str, UUID], 
                                     target_id: Union[str, UUID], 
                                     relationship_level: Optional[int] = None, 
                                     relationship_type: Optional[str] = None) -> Optional[Relationship]:
        """
        Update a character-to-character relationship.
        
        Args:
            source_id: UUID of the source character
            target_id: UUID of the target character
            relationship_level: New numeric level
            relationship_type: New type descriptor
            
        Returns:
            Updated relationship object or None if not found
        """
        new_data = {}
        if relationship_level is not None:
            new_data["level"] = relationship_level
        if relationship_type is not None:
            new_data["type"] = relationship_type
            
        return self.update_relationship_data(
            source_id=source_id,
            target_id=target_id,
            rel_type=RelationshipType.CHARACTER,
            new_data=new_data
        )
    
    def update_faction_relationship(self, 
                                   character_id: Union[str, UUID], 
                                   faction_id: Union[str, UUID], 
                                   reputation: Optional[int] = None, 
                                   standing: Optional[str] = None) -> Optional[Relationship]:
        """
        Update a character-faction relationship.
        
        Args:
            character_id: UUID of the character
            faction_id: UUID of the faction
            reputation: New reputation value
            standing: New standing description
            
        Returns:
            Updated relationship object or None if not found
        """
        new_data = {}
        if reputation is not None:
            new_data["reputation"] = reputation
        if standing is not None:
            new_data["standing"] = standing
            
        return self.update_relationship_data(
            source_id=character_id,
            target_id=faction_id,
            rel_type=RelationshipType.FACTION,
            new_data=new_data
        )
    
    def update_quest_relationship(self, 
                                 character_id: Union[str, UUID], 
                                 quest_id: Union[str, UUID], 
                                 status: Optional[str] = None, 
                                 progress: Optional[float] = None) -> Optional[Relationship]:
        """
        Update a character-quest relationship.
        
        Args:
            character_id: UUID of the character
            quest_id: UUID of the quest
            status: New quest status
            progress: New progress value
            
        Returns:
            Updated relationship object or None if not found
        """
        new_data = {}
        if status is not None:
            new_data["status"] = status
        if progress is not None:
            new_data["progress"] = progress
            
        return self.update_relationship_data(
            source_id=character_id,
            target_id=quest_id,
            rel_type=RelationshipType.QUEST,
            new_data=new_data
        )
    
    # Remove Methods
    
    def remove_relationship(self, 
                          source_id: Union[str, UUID], 
                          target_id: Union[str, UUID], 
                          rel_type: Union[str, RelationshipType]) -> bool:
        """
        Remove a specific relationship.
        
        Args:
            source_id: UUID of the source entity
            target_id: UUID of the target entity
            rel_type: Type of relationship
            
        Returns:
            True if successful, False if not found
        """
        # Convert string type to enum if needed
        if isinstance(rel_type, str):
            rel_type = RelationshipType(rel_type)
            
        relationship = self.get_relationship(source_id, target_id, rel_type)
        if not relationship:
            logger.warning(f"Attempted to remove non-existent relationship: {source_id} -> {target_id} ({rel_type})")
            return False
        
        # Store relationship data for event
        rel_id = relationship.id
        rel_data = relationship.data.copy()
        
        # Remove relationship
        self.db.delete(relationship)
        self.db.commit()
        
        # Emit event
        self.event_dispatcher.emit(RelationshipRemoved(
            event_type="relationship.removed",
            source_id=str(source_id),
            target_id=str(target_id),
            relationship_type=rel_type,
            relationship_id=rel_id,
            data=rel_data
        ))
        
        logger.info(f"Removed {rel_type} relationship between {source_id} and {target_id}")
        return True
    
    def remove_all_entity_relationships(self, entity_id: Union[str, UUID]) -> int:
        """
        Remove all relationships where the given entity is either source or target.
        
        Args:
            entity_id: UUID of the entity
            
        Returns:
            Number of relationships removed
        """
        entity_id_str = str(entity_id)
        
        # Get all relationships to emit events later
        relationships = self.get_all_relationships(entity_id)
        
        # Remove relationships
        result = self.db.query(Relationship).filter(
            or_(
                Relationship.source_id == entity_id_str,
                Relationship.target_id == entity_id_str
            )
        ).delete()
        
        self.db.commit()
        
        # Emit events for each deleted relationship
        for rel in relationships:
            self.event_dispatcher.emit(RelationshipRemoved(
                event_type="relationship.removed",
                source_id=rel.source_id,
                target_id=rel.target_id,
                relationship_type=rel.type,
                relationship_id=rel.id,
                data=rel.data
            ))
        
        logger.info(f"Removed {result} relationships for entity {entity_id}")
        return result 