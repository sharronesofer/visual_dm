"""
Negotiation Repository for Diplomacy System

This module provides negotiation-specific repository operations,
delegating to the infrastructure layer while providing 
negotiation-focused abstractions and business logic.
"""

from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from backend.systems.diplomacy.models.core_models import Negotiation, NegotiationStatus
from .base_repository import BaseDiplomacyRepository


class NegotiationRepository(BaseDiplomacyRepository[Negotiation]):
    """
    Repository for negotiation operations within the diplomacy system.
    
    Provides negotiation-specific data access methods while delegating
    to the infrastructure repository for actual persistence.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the negotiation repository."""
        super().__init__(db_session)
    
    def create(self, entity: Negotiation) -> Negotiation:
        """Create a new negotiation."""
        return self.infrastructure_repo.create_negotiation(entity)
    
    def get_by_id(self, negotiation_id: UUID) -> Optional[Negotiation]:
        """Get a negotiation by its ID."""
        return self.infrastructure_repo.get_negotiation(negotiation_id)
    
    def update(self, negotiation_id: UUID, updates: Dict) -> Optional[Negotiation]:
        """Update a negotiation with new values."""
        return self.infrastructure_repo.update_negotiation(negotiation_id, updates)
    
    def delete(self, negotiation_id: UUID) -> bool:
        """Delete a negotiation by its ID."""
        return self.infrastructure_repo.delete_negotiation(negotiation_id)
    
    def list_all(
        self, 
        faction_id: Optional[UUID] = None,
        status: Optional[NegotiationStatus] = None
    ) -> List[Negotiation]:
        """List negotiations with optional filters."""
        return self.infrastructure_repo.list_negotiations(
            faction_id=faction_id,
            status=status
        )
    
    # Negotiation-specific methods
    
    def get_negotiations_by_faction(self, faction_id: UUID) -> List[Negotiation]:
        """Get all negotiations involving a specific faction."""
        return self.list_all(faction_id=faction_id)
    
    def get_active_negotiations(self) -> List[Negotiation]:
        """Get all active negotiations (pending or counter-offered)."""
        pending = self.list_all(status=NegotiationStatus.PENDING)
        counter_offered = self.list_all(status=NegotiationStatus.COUNTER_OFFERED)
        return pending + counter_offered
    
    def get_completed_negotiations(self) -> List[Negotiation]:
        """Get all completed negotiations (successful or failed)."""
        successful = self.list_all(status=NegotiationStatus.SUCCESSFUL)
        failed = self.list_all(status=NegotiationStatus.FAILED)
        return successful + failed
    
    def get_negotiations_between_factions(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID
    ) -> List[Negotiation]:
        """Get all negotiations between two specific factions."""
        all_negotiations = self.list_all()
        return [
            negotiation for negotiation in all_negotiations
            if faction_a_id in negotiation.parties and faction_b_id in negotiation.parties
        ]
    
    def get_faction_initiated_negotiations(self, faction_id: UUID) -> List[Negotiation]:
        """Get all negotiations initiated by a specific faction."""
        all_negotiations = self.get_negotiations_by_faction(faction_id)
        return [
            negotiation for negotiation in all_negotiations
            if negotiation.initiator_id == faction_id
        ]
    
    def count_active_negotiations_by_faction(self, faction_id: UUID) -> int:
        """Count active negotiations for a faction."""
        active_negotiations = self.get_active_negotiations()
        return len([
            negotiation for negotiation in active_negotiations
            if faction_id in negotiation.parties
        ])
    
    def has_active_negotiation_between_factions(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID
    ) -> bool:
        """Check if there's an active negotiation between two factions."""
        negotiations = self.get_negotiations_between_factions(faction_a_id, faction_b_id)
        return any(
            negotiation.status in [NegotiationStatus.PENDING, NegotiationStatus.COUNTER_OFFERED]
            for negotiation in negotiations
        ) 