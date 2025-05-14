"""
Service layer for managing factions and their relationships.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy import and_, or_
from app.core.models.faction import Faction
from app.core.database import db
from app.core.exceptions import (
    FactionNotFoundError, InvalidRelationshipError,
    DuplicateFactionError
)

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
    """Service for managing faction relationships."""
    
    @staticmethod
    def set_relationship(
        faction_id: int,
        target_faction_id: int,
        relation_type: RelationType,
        reputation_score: float = 0.0,
        trade_status: bool = False,
        metadata: Dict = None
    ) -> FactionRelationship:
        """Create or update a relationship between factions."""
        # Validate factions exist
        source_faction = FactionService.get_faction(faction_id)
        target_faction = FactionService.get_faction(target_faction_id)
        
        if not source_faction or not target_faction:
            raise FactionNotFoundError("One or both factions not found")
            
        if faction_id == target_faction_id:
            raise InvalidRelationshipError("Cannot create relationship with self")

        # Get or create relationship
        relationship = db.session.query(FactionRelationship).filter(
            and_(
                FactionRelationship.faction_id == faction_id,
                FactionRelationship.target_faction_id == target_faction_id
            )
        ).first()

        if relationship:
            # Update existing
            relationship.relation_type = relation_type
            relationship.reputation_score = reputation_score
            relationship.trade_status = trade_status
            if metadata:
                relationship.metadata.update(metadata)
                
            # Update timestamps for specific changes
            if relation_type in [RelationType.ALLIED, RelationType.VASSAL]:
                relationship.alliance_date = datetime.utcnow()
            elif relation_type in [RelationType.HOSTILE, RelationType.WAR]:
                relationship.last_conflict_date = datetime.utcnow()
        else:
            # Create new
            relationship = FactionRelationship(
                faction_id=faction_id,
                target_faction_id=target_faction_id,
                relation_type=relation_type,
                reputation_score=reputation_score,
                trade_status=trade_status,
                metadata=metadata or {},
                alliance_date=(datetime.utcnow() if relation_type in 
                             [RelationType.ALLIED, RelationType.VASSAL] else None),
                last_conflict_date=(datetime.utcnow() if relation_type in 
                                  [RelationType.HOSTILE, RelationType.WAR] else None)
            )
            db.session.add(relationship)

        db.session.commit()
        return relationship

    @staticmethod
    def get_relationship(
        faction_id: int,
        target_faction_id: int
    ) -> Optional[FactionRelationship]:
        """Get the relationship between two factions."""
        return db.session.query(FactionRelationship).filter(
            and_(
                FactionRelationship.faction_id == faction_id,
                FactionRelationship.target_faction_id == target_faction_id
            )
        ).first()

    @staticmethod
    def get_faction_relationships(
        faction_id: int,
        relation_type: RelationType = None,
        min_reputation: float = None,
        include_incoming: bool = False
    ) -> List[FactionRelationship]:
        """Get all relationships for a faction."""
        query = db.session.query(FactionRelationship)
        
        if include_incoming:
            query = query.filter(or_(
                FactionRelationship.faction_id == faction_id,
                FactionRelationship.target_faction_id == faction_id
            ))
        else:
            query = query.filter(FactionRelationship.faction_id == faction_id)
            
        if relation_type:
            query = query.filter(FactionRelationship.relation_type == relation_type)
        if min_reputation is not None:
            query = query.filter(FactionRelationship.reputation_score >= min_reputation)
            
        return query.all()

    @staticmethod
    def update_reputation(
        faction_id: int,
        target_faction_id: int,
        change: float
    ) -> Tuple[FactionRelationship, RelationType]:
        """Update reputation between factions and determine new relation type."""
        relationship = FactionRelationshipService.get_relationship(
            faction_id, target_faction_id
        )
        if not relationship:
            raise InvalidRelationshipError("Relationship does not exist")

        # Update reputation score
        old_score = relationship.reputation_score
        new_score = max(-100, min(100, old_score + change))
        relationship.reputation_score = new_score
        
        # Determine new relation type based on score
        new_type = RelationType.NEUTRAL
        if new_score >= 75:
            new_type = RelationType.ALLIED
        elif new_score >= 25:
            new_type = RelationType.FRIENDLY
        elif new_score <= -75:
            new_type = RelationType.WAR
        elif new_score <= -25:
            new_type = RelationType.HOSTILE
            
        old_type = relationship.relation_type
        if new_type != old_type:
            relationship.relation_type = new_type
            if new_type in [RelationType.ALLIED, RelationType.VASSAL]:
                relationship.alliance_date = datetime.utcnow()
            elif new_type in [RelationType.HOSTILE, RelationType.WAR]:
                relationship.last_conflict_date = datetime.utcnow()

        db.session.commit()
        return relationship, new_type

    @staticmethod
    def delete_relationship(
        faction_id: int,
        target_faction_id: int
    ) -> None:
        """Delete a relationship between factions."""
        relationship = FactionRelationshipService.get_relationship(
            faction_id, target_faction_id
        )
        if relationship:
            db.session.delete(relationship)
            db.session.commit() 