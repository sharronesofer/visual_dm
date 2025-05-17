"""
Service layer for managing factions and their relationships.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy import and_, or_
from app.core.models.world import Faction
from app.core.database import db
from app.core.exceptions import (
    FactionNotFoundError, InvalidRelationshipError,
    DuplicateFactionError
)
from app.core.api.validation.faction_validators import FactionType
from app.core.api.validation.faction_validators import FactionStatus

class FactionService:
    """Service for managing faction operations."""
    
    @staticmethod
    def create_faction(
        name: str,
        description: str,
        faction_type: FactionType,
        influence: float = 0.0,
        resources: Dict = None,
        territory: Dict = None,
        traits: Dict = None,
        metadata: Dict = None
    ) -> Faction:
        """Create a new faction."""
        # Check for existing faction with same name
        if db.session.query(Faction).filter(Faction.name == name).first():
            raise DuplicateFactionError(f"Faction with name {name} already exists")
            
        faction = Faction(
            name=name,
            description=description,
            faction_type=faction_type,
            influence=influence,
            resources=resources or {},
            territory=territory or {},
            traits=traits or {},
            metadata=metadata or {}
        )
        
        db.session.add(faction)
        db.session.commit()
        return faction

    @staticmethod
    def get_faction(faction_id: int) -> Optional[Faction]:
        """Get a faction by ID."""
        return db.session.query(Faction).get(faction_id)

    @staticmethod
    def get_factions(
        faction_type: FactionType = None,
        status: FactionStatus = None,
        min_influence: float = None
    ) -> List[Faction]:
        """Get factions with optional filters."""
        query = db.session.query(Faction)
        
        if faction_type:
            query = query.filter(Faction.faction_type == faction_type)
        if status:
            query = query.filter(Faction.status == status)
        if min_influence is not None:
            query = query.filter(Faction.influence >= min_influence)
            
        return query.all()

    @staticmethod
    def update_faction(
        faction_id: int,
        name: str = None,
        description: str = None,
        status: FactionStatus = None,
        influence: float = None,
        resources: Dict = None,
        territory: Dict = None,
        traits: Dict = None,
        metadata: Dict = None
    ) -> Faction:
        """Update faction attributes."""
        faction = FactionService.get_faction(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")

        if name:
            existing = db.session.query(Faction).filter(
                and_(Faction.name == name, Faction.id != faction_id)
            ).first()
            if existing:
                raise DuplicateFactionError(f"Faction with name {name} already exists")
            faction.name = name
            
        if description:
            faction.description = description
        if status:
            faction.status = status
        if influence is not None:
            faction.influence = influence
        if resources:
            faction.resources.update(resources)
        if territory:
            faction.territory.update(territory)
        if traits:
            faction.traits.update(traits)
        if metadata:
            faction.metadata.update(metadata)

        db.session.commit()
        return faction

    @staticmethod
    def delete_faction(faction_id: int) -> None:
        """Delete a faction and all its relationships."""
        faction = FactionService.get_faction(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        db.session.delete(faction)
        db.session.commit()

class FactionRelationshipService:
    """Service for managing relationships between any two entities (not just factions)."""
    @staticmethod
    def set_relationship(
        entity1_id: int,
        entity1_type: str,
        entity2_id: int,
        entity2_type: str,
        relationship_type: str = None,
        relationship_value: int = 0,
        metadata: Dict = None
    ) -> 'Relationship':
        """Create or update a relationship between any two entities."""
        from app.social.models.social import Relationship, EntityType
        # Validate entity types
        e1_type = EntityType(entity1_type)
        e2_type = EntityType(entity2_type)
        # Get or create relationship
        relationship = db.session.query(Relationship).filter_by(
            entity1_id=entity1_id,
            entity1_type=e1_type,
            entity2_id=entity2_id,
            entity2_type=e2_type
        ).first()
        if relationship:
            relationship.relationship_type = relationship_type
            relationship.relationship_value = relationship_value
            if metadata:
                if relationship.metadata:
                    relationship.metadata.update(metadata)
                else:
                    relationship.metadata = metadata
        else:
            relationship = Relationship(
                entity1_id=entity1_id,
                entity1_type=e1_type,
                entity2_id=entity2_id,
                entity2_type=e2_type,
                relationship_type=relationship_type,
                relationship_value=relationship_value,
                metadata=metadata or {}
            )
            db.session.add(relationship)
        db.session.commit()
        return relationship

    @staticmethod
    def get_relationship(
        entity1_id: int,
        entity1_type: str,
        entity2_id: int,
        entity2_type: str
    ) -> Optional['Relationship']:
        from app.social.models.social import Relationship, EntityType
        e1_type = EntityType(entity1_type)
        e2_type = EntityType(entity2_type)
        return db.session.query(Relationship).filter_by(
            entity1_id=entity1_id,
            entity1_type=e1_type,
            entity2_id=entity2_id,
            entity2_type=e2_type
        ).first()

    @staticmethod
    def get_entity_relationships(
        entity_id: int,
        entity_type: str,
        relationship_type: str = None,
        min_value: int = None,
        include_incoming: bool = False
    ) -> List['Relationship']:
        from app.social.models.social import Relationship, EntityType
        e_type = EntityType(entity_type)
        query = db.session.query(Relationship)
        if include_incoming:
            query = query.filter(
                or_(
                    Relationship.entity1_id == entity_id,
                    Relationship.entity2_id == entity_id
                ),
                or_(
                    Relationship.entity1_type == e_type,
                    Relationship.entity2_type == e_type
                )
            )
        else:
            query = query.filter(
                Relationship.entity1_id == entity_id,
                Relationship.entity1_type == e_type
            )
        if relationship_type:
            query = query.filter(Relationship.relationship_type == relationship_type)
        if min_value is not None:
            query = query.filter(Relationship.relationship_value >= min_value)
        return query.all()

    @staticmethod
    def update_relationship_value(
        entity1_id: int,
        entity1_type: str,
        entity2_id: int,
        entity2_type: str,
        delta: int
    ) -> Optional['Relationship']:
        rel = FactionRelationshipService.get_relationship(entity1_id, entity1_type, entity2_id, entity2_type)
        if rel:
            rel.relationship_value += delta
            db.session.commit()
        return rel

    @staticmethod
    def delete_relationship(
        entity1_id: int,
        entity1_type: str,
        entity2_id: int,
        entity2_type: str
    ) -> None:
        rel = FactionRelationshipService.get_relationship(entity1_id, entity1_type, entity2_id, entity2_type)
        if rel:
            db.session.delete(rel)
            db.session.commit() 