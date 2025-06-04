"""
Faction Relationship Repository for Diplomacy System

This module provides faction relationship-specific repository operations,
managing diplomatic relationships, tension, and status between factions.
"""

from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from .base_repository import BaseDiplomacyRepository


class FactionRelationshipRepository(BaseDiplomacyRepository[Dict]):
    """
    Repository for faction relationship operations within the diplomacy system.
    
    Manages diplomatic relationships, tension levels, and status between factions.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the faction relationship repository."""
        super().__init__(db_session)
    
    def create(self, entity: Dict) -> Dict:
        """Create a new faction relationship (not typically used directly)."""
        # Relationships are typically created implicitly when accessing
        return entity
    
    def get_by_id(self, relationship_id: UUID) -> Optional[Dict]:
        """Get a relationship by ID (not typically used for relationships)."""
        return None
    
    def update(self, relationship_id: UUID, updates: Dict) -> Optional[Dict]:
        """Update a relationship (handled by specific methods)."""
        return None
    
    def delete(self, relationship_id: UUID) -> bool:
        """Delete a relationship (not typically used)."""
        return False
    
    def list_all(self, **filters) -> List[Dict]:
        """List all relationships (handled by specific methods)."""
        return []
    
    # Faction relationship-specific methods
    
    def get_relationship(self, faction_a_id: UUID, faction_b_id: UUID) -> Dict:
        """Get the relationship between two factions."""
        return self.infrastructure_repo.get_faction_relationship(faction_a_id, faction_b_id)
    
    def get_all_relationships(self, faction_id: UUID) -> List[Dict]:
        """Get all relationships for a specific faction."""
        return self.infrastructure_repo.get_all_faction_relationships(faction_id)
    
    def update_relationship(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID, 
        updates: Dict
    ) -> Dict:
        """Update the relationship between two factions."""
        return self.infrastructure_repo.update_faction_relationship(
            faction_a_id, faction_b_id, updates
        )
    
    def get_relationships_by_status(self, faction_id: UUID, status: str) -> List[Dict]:
        """Get all relationships for a faction with a specific status."""
        relationships = self.get_all_relationships(faction_id)
        return [rel for rel in relationships if rel.get('status') == status]
    
    def get_high_tension_relationships(self, faction_id: UUID, threshold: int = 70) -> List[Dict]:
        """Get relationships with tension above the threshold."""
        relationships = self.get_all_relationships(faction_id)
        return [rel for rel in relationships if rel.get('tension', 0) >= threshold]
    
    def get_allied_factions(self, faction_id: UUID) -> List[UUID]:
        """Get all factions that are allied with the given faction."""
        relationships = self.get_relationships_by_status(faction_id, 'ALLIED')
        return [UUID(rel['other_faction_id']) for rel in relationships]
    
    def get_hostile_factions(self, faction_id: UUID) -> List[UUID]:
        """Get all factions that are hostile to the given faction."""
        relationships = self.get_relationships_by_status(faction_id, 'HOSTILE')
        return [UUID(rel['other_faction_id']) for rel in relationships] 