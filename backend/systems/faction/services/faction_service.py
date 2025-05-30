"""
Service layer for managing factions.

This module provides the FactionService class for creating, retrieving, updating,
and deleting factions.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from backend.systems.faction.models.faction import Faction
from backend.systems.faction.schemas.faction_types import FactionType, FactionAlignment


class FactionNotFoundError(Exception):
    """Raised when a faction cannot be found."""
    pass


class DuplicateFactionError(Exception):
    """Raised when attempting to create a faction with a name that already exists."""
    pass


class FactionService:
    """Service for managing faction operations."""
    
    @staticmethod
    def create_faction(
        db: Session,
        name: str,
        description: str,
        faction_type: FactionType,
        alignment: Optional[FactionAlignment] = None,
        influence: float = 50.0,
        resources: Dict[str, Any] = None,
        territory: Dict[str, Any] = None,
        leader_id: Optional[int] = None,
        headquarters_id: Optional[int] = None,
        parent_faction_id: Optional[int] = None,
        metadata: Dict[str, Any] = None
    ) -> Faction:
        """
        Create a new faction.
        
        Args:
            db: Database session
            name: Faction name (unique)
            description: Faction description
            faction_type: Type of faction (see FactionType enum)
            alignment: Moral alignment (see FactionAlignment enum)
            influence: Initial influence value (0-100)
            resources: Initial resources (optional)
            territory: Initial territories (optional)
            leader_id: ID of NPC leader (optional)
            headquarters_id: ID of headquarters location (optional)
            parent_faction_id: ID of parent faction (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Newly created Faction instance
            
        Raises:
            DuplicateFactionError: If a faction with the same name already exists
        """
        # Check for existing faction with same name
        if db.query(Faction).filter(Faction.name == name).first():
            raise DuplicateFactionError(f"Faction with name {name} already exists")
            
        faction = Faction(
            name=name,
            description=description,
            type=faction_type.value if isinstance(faction_type, FactionType) else faction_type,
            alignment=alignment.value if isinstance(alignment, FactionAlignment) else alignment,
            influence=influence,
            leader_id=leader_id,
            headquarters_id=headquarters_id,
            parent_faction_id=parent_faction_id
        )
        
        # Set optional JSON fields
        if resources:
            faction.resources.update(resources)
        if territory:
            faction.territory.update(territory)
        if metadata:
            faction.state['metadata'] = metadata
        
        db.add(faction)
        db.commit()
        db.refresh(faction)
        return faction

    @staticmethod
    def get_faction(db: Session, faction_id: int) -> Optional[Faction]:
        """
        Get a faction by ID.
        
        Args:
            db: Database session
            faction_id: ID of faction to retrieve
            
        Returns:
            Faction instance or None if not found
        """
        return db.query(Faction).filter(Faction.id == faction_id).first()

    @staticmethod
    def get_faction_by_name(db: Session, name: str) -> Optional[Faction]:
        """
        Get a faction by name.
        
        Args:
            db: Database session
            name: Name of faction to retrieve
            
        Returns:
            Faction instance or None if not found
        """
        return db.query(Faction).filter(Faction.name == name).first()

    @staticmethod
    def get_factions(
        db: Session,
        faction_type: Optional[FactionType] = None,
        is_active: Optional[bool] = None,
        min_influence: Optional[float] = None,
        parent_faction_id: Optional[int] = None
    ) -> List[Faction]:
        """
        Get factions with optional filters.
        
        Args:
            db: Database session
            faction_type: Filter by faction type (optional)
            is_active: Filter by active status (optional)
            min_influence: Filter by minimum influence value (optional)
            parent_faction_id: Filter by parent faction ID (optional)
            
        Returns:
            List of Faction instances matching filters
        """
        query = db.query(Faction)
        
        if faction_type:
            type_str = faction_type.value if isinstance(faction_type, FactionType) else faction_type
            query = query.filter(Faction.type == type_str)
        
        if is_active is not None:
            query = query.filter(Faction.is_active == is_active)
            
        if min_influence is not None:
            query = query.filter(Faction.influence >= min_influence)
            
        if parent_faction_id is not None:
            query = query.filter(Faction.parent_faction_id == parent_faction_id)
            
        return query.all()

    @staticmethod
    def update_faction(
        db: Session,
        faction_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        faction_type: Optional[FactionType] = None,
        alignment: Optional[FactionAlignment] = None,
        influence: Optional[float] = None,
        resources: Optional[Dict] = None,
        territory: Optional[Dict] = None,
        leader_id: Optional[int] = None,
        headquarters_id: Optional[int] = None,
        parent_faction_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        metadata: Optional[Dict] = None
    ) -> Faction:
        """
        Update faction attributes.
        
        Args:
            db: Database session
            faction_id: ID of faction to update
            [various optional attributes to update]
            
        Returns:
            Updated Faction instance
            
        Raises:
            FactionNotFoundError: If faction with given ID doesn't exist
            DuplicateFactionError: If updating name to one that already exists
        """
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")

        if name:
            # Check if name is already taken by another faction
            existing = db.query(Faction).filter(Faction.name == name).first()
            if existing and existing.id != faction_id:
                raise DuplicateFactionError(f"Faction with name {name} already exists")
            faction.name = name
            
        if description:
            faction.description = description
            
        if faction_type:
            faction.type = faction_type.value if isinstance(faction_type, FactionType) else faction_type
            
        if alignment:
            faction.alignment = alignment.value if isinstance(alignment, FactionAlignment) else alignment
            
        if influence is not None:
            faction.influence = influence
            
        if leader_id is not None:
            faction.leader_id = leader_id
            
        if headquarters_id is not None:
            faction.headquarters_id = headquarters_id
            
        if parent_faction_id is not None:
            faction.parent_faction_id = parent_faction_id
            
        if is_active is not None:
            faction.is_active = is_active
            
        if resources:
            faction.resources.update(resources)
            
        if territory:
            faction.territory.update(territory)
            
        if metadata:
            if 'metadata' not in faction.state:
                faction.state['metadata'] = {}
            faction.state['metadata'].update(metadata)
            
        # Update timestamp
        faction.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(faction)
        return faction

    @staticmethod
    def delete_faction(db: Session, faction_id: int) -> None:
        """
        Delete a faction.
        
        Args:
            db: Database session
            faction_id: ID of faction to delete
            
        Raises:
            FactionNotFoundError: If faction with given ID doesn't exist
        """
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        db.delete(faction)
        db.commit()
        
    @staticmethod
    def assign_faction_to_poi(
        db: Session,
        faction_id: int,
        poi_id: int,
        control_level: int = 10,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Assign a faction to a POI with a control level.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            poi_id: ID of the POI
            control_level: Control/influence level (0-10)
            metadata: Additional control metadata
            
        Returns:
            POI control data
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        # Check if faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        # Note: This is a stub that would integrate with the POI system
        # In a real implementation, this would update POI data in the database
        
        # Create event data
        event_data = {
            "faction_id": faction_id,
            "poi_id": poi_id,
            "control_level": control_level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            event_data["metadata"] = metadata
            
        # For now, just return the event data
        # In a real implementation, this would return actual POI control data
        return event_data

    @staticmethod
    def calculate_affinity(
        db: Session,
        character_id: int,
        faction_id: int
    ) -> int:
        """
        Calculate affinity score between a character and faction.
        Compares character traits against faction traits.
        
        Args:
            db: Database session
            character_id: ID of the character/NPC
            faction_id: ID of the faction
            
        Returns:
            Affinity score (0-36)
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        # Check if faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        # Note: This is a stub that would integrate with the Character system
        # In a real implementation, this would calculate actual affinity
        
        # For now, return a random score
        # In a real implementation, this would compare character and faction traits
        import random
        return random.randint(1, 36) 