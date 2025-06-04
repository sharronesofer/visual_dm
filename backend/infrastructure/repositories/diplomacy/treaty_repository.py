"""
Treaty Repository for Diplomacy System

This module provides treaty-specific repository operations,
delegating to the infrastructure layer while providing 
treaty-focused abstractions and business logic.
"""

from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from backend.systems.diplomacy.models.core_models import Treaty, TreatyType, TreatyStatus
from .base_repository import BaseDiplomacyRepository


class TreatyRepository(BaseDiplomacyRepository[Treaty]):
    """
    Repository for treaty operations within the diplomacy system.
    
    Provides treaty-specific data access methods while delegating
    to the infrastructure repository for actual persistence.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the treaty repository."""
        super().__init__(db_session)
    
    def create(self, entity: Treaty) -> Treaty:
        """Create a new treaty."""
        return self.infrastructure_repo.create_treaty(entity)
    
    def get_by_id(self, treaty_id: UUID) -> Optional[Treaty]:
        """Get a treaty by its ID."""
        return self.infrastructure_repo.get_treaty(treaty_id)
    
    def update(self, treaty_id: UUID, updates: Dict) -> Optional[Treaty]:
        """Update a treaty with new values."""
        return self.infrastructure_repo.update_treaty(treaty_id, updates)
    
    def delete(self, treaty_id: UUID) -> bool:
        """Delete a treaty by its ID."""
        return self.infrastructure_repo.delete_treaty(treaty_id)
    
    def list_all(
        self, 
        faction_id: Optional[UUID] = None,
        active_only: bool = False,
        treaty_type: Optional[TreatyType] = None
    ) -> List[Treaty]:
        """List treaties with optional filters."""
        return self.infrastructure_repo.list_treaties(
            faction_id=faction_id,
            active_only=active_only,
            treaty_type=treaty_type
        )
    
    # Treaty-specific methods
    
    def get_treaties_by_faction(self, faction_id: UUID, active_only: bool = True) -> List[Treaty]:
        """Get all treaties for a specific faction."""
        return self.list_all(faction_id=faction_id, active_only=active_only)
    
    def get_treaties_by_type(self, treaty_type: TreatyType, active_only: bool = True) -> List[Treaty]:
        """Get all treaties of a specific type."""
        return self.list_all(treaty_type=treaty_type, active_only=active_only)
    
    def get_bilateral_treaties(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID,
        active_only: bool = True
    ) -> List[Treaty]:
        """Get all treaties between two specific factions."""
        treaties = self.list_all(active_only=active_only)
        return [
            treaty for treaty in treaties
            if faction_a_id in treaty.parties and faction_b_id in treaty.parties
        ]
    
    def get_multilateral_treaties(self, faction_id: UUID, active_only: bool = True) -> List[Treaty]:
        """Get all multilateral treaties involving a faction."""
        treaties = self.get_treaties_by_faction(faction_id, active_only)
        return [treaty for treaty in treaties if len(treaty.parties) > 2]
    
    def get_expired_treaties(self) -> List[Treaty]:
        """Get all treaties that have expired."""
        all_treaties = self.list_all(active_only=False)
        return [
            treaty for treaty in all_treaties 
            if treaty.status == TreatyStatus.EXPIRED
        ]
    
    def get_treaties_expiring_soon(self, days_ahead: int = 30) -> List[Treaty]:
        """Get treaties that will expire within the specified number of days."""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        active_treaties = self.list_all(active_only=True)
        
        return [
            treaty for treaty in active_treaties
            if treaty.end_date and treaty.end_date <= cutoff_date
        ]
    
    def count_active_treaties_by_faction(self, faction_id: UUID) -> int:
        """Count active treaties for a faction."""
        return len(self.get_treaties_by_faction(faction_id, active_only=True))
    
    def has_treaty_type_with_faction(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID, 
        treaty_type: TreatyType
    ) -> bool:
        """Check if two factions have an active treaty of a specific type."""
        bilateral_treaties = self.get_bilateral_treaties(faction_a_id, faction_b_id, active_only=True)
        return any(treaty.type == treaty_type for treaty in bilateral_treaties) 