"""
Core Diplomacy Database Adapter

Handles all database operations for core diplomatic functionality including 
treaties, negotiations, incidents, ultimatums, and sanctions.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import UUID

from backend.infrastructure.repositories.diplomacy_repository import DiplomacyRepository
from backend.systems.diplomacy.models.core_models import (
    Treaty, TreatyType, TreatyStatus, TreatyViolation, TreatyViolationType,
    Negotiation, NegotiationStatus, NegotiationOffer,
    DiplomaticEvent, DiplomaticEventType, DiplomaticStatus,
    DiplomaticIncident, DiplomaticIncidentType, DiplomaticIncidentSeverity,
    Ultimatum, UltimatumStatus,
    Sanction, SanctionType, SanctionStatus
)

logger = logging.getLogger(__name__)

class CoreDiplomacyDatabaseAdapter:
    """Database adapter for core diplomacy operations."""
    
    def __init__(self, repository: Optional[DiplomacyRepository] = None):
        """Initialize the adapter with a repository."""
        self.repository = repository or DiplomacyRepository()
    
    # === Relationship Operations ===
    
    def get_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID) -> Dict:
        """Get the relationship between two factions."""
        return self.repository.get_faction_relationship(faction_a_id, faction_b_id)
    
    def get_all_faction_relationships(self, faction_id: UUID) -> List[Dict]:
        """Get all relationships for a faction."""
        return self.repository.get_all_faction_relationships(faction_id)
    
    def update_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID, updates: Dict) -> Dict:
        """Update relationship between two factions."""
        return self.repository.update_faction_relationship(faction_a_id, faction_b_id, updates)
    
    # === Treaty Operations ===
    
    def create_treaty(self, treaty: Treaty) -> Treaty:
        """Create a new treaty in the database."""
        return self.repository.create_treaty(treaty)
    
    def get_treaty(self, treaty_id: UUID) -> Optional[Treaty]:
        """Get a treaty by ID."""
        return self.repository.get_treaty(treaty_id)
    
    def update_treaty(self, treaty_id: UUID, updates: Dict) -> Optional[Treaty]:
        """Update a treaty."""
        return self.repository.update_treaty(treaty_id, updates)
    
    def list_treaties(self, faction_id: Optional[UUID] = None, 
                     active_only: bool = False, 
                     treaty_type: Optional[TreatyType] = None) -> List[Treaty]:
        """List treaties with optional filters."""
        return self.repository.list_treaties(faction_id, active_only, treaty_type)
    
    def get_treaties_by_parties(self, parties: List[UUID]) -> List[Treaty]:
        """Get treaties involving specific parties."""
        return self.repository.get_treaties_by_parties(parties)
    
    def get_active_treaties_between_factions(self, faction_a_id: UUID, faction_b_id: UUID) -> List[Treaty]:
        """Get active treaties between two factions."""
        return self.repository.get_active_treaties_between_factions(faction_a_id, faction_b_id)
    
    def expire_treaty(self, treaty_id: UUID, expiry_reason: str = "Natural expiration") -> Optional[Treaty]:
        """Mark a treaty as expired."""
        updates = {
            'status': TreatyStatus.EXPIRED,
            'expired_at': datetime.utcnow(),
            'expiry_reason': expiry_reason
        }
        return self.repository.update_treaty(treaty_id, updates)
    
    # === Treaty Violation Operations ===
    
    def create_treaty_violation(self, violation: TreatyViolation) -> TreatyViolation:
        """Create a new treaty violation."""
        return self.repository.create_treaty_violation(violation)
    
    def get_treaty_violation(self, violation_id: UUID) -> Optional[TreatyViolation]:
        """Get a treaty violation by ID."""
        return self.repository.get_treaty_violation(violation_id)
    
    def update_treaty_violation(self, violation_id: UUID, updates: Dict) -> Optional[TreatyViolation]:
        """Update a treaty violation."""
        return self.repository.update_treaty_violation(violation_id, updates)
    
    def get_treaty_violations(self, treaty_id: Optional[UUID] = None,
                            faction_id: Optional[UUID] = None,
                            violation_type: Optional[TreatyViolationType] = None,
                            resolved: Optional[bool] = None) -> List[TreatyViolation]:
        """Get treaty violations with filters."""
        return self.repository.get_treaty_violations(treaty_id, faction_id, violation_type, resolved)
    
    def get_unresolved_violations_for_treaties(self, treaty_ids: List[UUID]) -> List[TreatyViolation]:
        """Get unresolved violations for specific treaties."""
        return self.repository.get_unresolved_violations_for_treaties(treaty_ids)
    
    # === Negotiation Operations ===
    
    def create_negotiation(self, negotiation: Negotiation) -> Negotiation:
        """Create a new negotiation."""
        return self.repository.create_negotiation(negotiation)
    
    def get_negotiation(self, negotiation_id: UUID) -> Optional[Negotiation]:
        """Get a negotiation by ID."""
        return self.repository.get_negotiation(negotiation_id)
    
    def update_negotiation(self, negotiation_id: UUID, updates: Dict) -> Optional[Negotiation]:
        """Update a negotiation."""
        return self.repository.update_negotiation(negotiation_id, updates)
    
    def create_negotiation_offer(self, offer: NegotiationOffer) -> NegotiationOffer:
        """Create a new negotiation offer."""
        return self.repository.create_negotiation_offer(offer)
    
    def get_negotiation_offers(self, negotiation_id: UUID) -> List[NegotiationOffer]:
        """Get all offers for a negotiation."""
        return self.repository.get_negotiation_offers(negotiation_id)
    
    def get_latest_offer(self, negotiation_id: UUID) -> Optional[NegotiationOffer]:
        """Get the most recent offer in a negotiation."""
        return self.repository.get_latest_offer(negotiation_id)
    
    # === Diplomatic Event Operations ===
    
    def create_diplomatic_event(self, event: DiplomaticEvent) -> DiplomaticEvent:
        """Create a new diplomatic event."""
        return self.repository.create_diplomatic_event(event)
    
    def get_diplomatic_event(self, event_id: UUID) -> Optional[DiplomaticEvent]:
        """Get a diplomatic event by ID."""
        return self.repository.get_diplomatic_event(event_id)
    
    def get_recent_events(self, faction_id: Optional[UUID] = None, 
                         event_type: Optional[DiplomaticEventType] = None,
                         days: int = 30) -> List[DiplomaticEvent]:
        """Get recent diplomatic events."""
        return self.repository.get_recent_events(faction_id, event_type, days)
    
    # === Diplomatic Incident Operations ===
    
    def create_diplomatic_incident(self, incident: DiplomaticIncident) -> DiplomaticIncident:
        """Create a new diplomatic incident."""
        return self.repository.create_diplomatic_incident(incident)
    
    def get_diplomatic_incident(self, incident_id: UUID) -> Optional[DiplomaticIncident]:
        """Get a diplomatic incident by ID."""
        return self.repository.get_diplomatic_incident(incident_id)
    
    def update_diplomatic_incident(self, incident_id: UUID, updates: Dict) -> Optional[DiplomaticIncident]:
        """Update a diplomatic incident."""
        return self.repository.update_diplomatic_incident(incident_id, updates)
    
    def list_diplomatic_incidents(self, faction_id: Optional[UUID] = None,
                                as_perpetrator: bool = True,
                                as_victim: bool = True,
                                resolved: Optional[bool] = None,
                                incident_type: Optional[DiplomaticIncidentType] = None,
                                limit: int = 100,
                                offset: int = 0) -> List[DiplomaticIncident]:
        """List diplomatic incidents with filters."""
        return self.repository.list_diplomatic_incidents(
            faction_id, as_perpetrator, as_victim, resolved, incident_type, limit, offset
        )
    
    def get_recent_major_incidents(self, faction_a_id: UUID, faction_b_id: UUID, days: int = 30) -> List[DiplomaticIncident]:
        """Get recent major incidents between two factions."""
        return self.repository.get_recent_major_incidents(faction_a_id, faction_b_id, days)
    
    # === Ultimatum Operations ===
    
    def create_ultimatum(self, ultimatum: Ultimatum) -> Ultimatum:
        """Create a new ultimatum."""
        return self.repository.create_ultimatum(ultimatum)
    
    def get_ultimatum(self, ultimatum_id: UUID) -> Optional[Ultimatum]:
        """Get an ultimatum by ID."""
        return self.repository.get_ultimatum(ultimatum_id)
    
    def update_ultimatum(self, ultimatum_id: UUID, updates: Dict) -> Optional[Ultimatum]:
        """Update an ultimatum."""
        return self.repository.update_ultimatum(ultimatum_id, updates)
    
    def list_ultimatums(self, faction_id: Optional[UUID] = None,
                       as_issuer: bool = True,
                       as_recipient: bool = True,
                       status: Optional[UltimatumStatus] = None,
                       active_only: bool = False,
                       limit: int = 100,
                       offset: int = 0) -> List[Ultimatum]:
        """List ultimatums with filters."""
        return self.repository.list_ultimatums(
            faction_id, as_issuer, as_recipient, status, active_only, limit, offset
        )
    
    def get_expired_ultimatums(self) -> List[Ultimatum]:
        """Get ultimatums that have passed their deadline."""
        return self.repository.get_expired_ultimatums()
    
    # === Sanction Operations ===
    
    def create_sanction(self, sanction: Sanction) -> Sanction:
        """Create a new sanction."""
        return self.repository.create_sanction(sanction)
    
    def get_sanction(self, sanction_id: UUID) -> Optional[Sanction]:
        """Get a sanction by ID."""
        return self.repository.get_sanction(sanction_id)
    
    def update_sanction(self, sanction_id: UUID, updates: Dict) -> Optional[Sanction]:
        """Update a sanction."""
        return self.repository.update_sanction(sanction_id, updates)
    
    def list_sanctions(self, imposer_id: Optional[UUID] = None,
                      target_id: Optional[UUID] = None,
                      sanction_type: Optional[SanctionType] = None,
                      status: Optional[SanctionStatus] = None,
                      active_only: bool = False,
                      limit: int = 100,
                      offset: int = 0) -> List[Sanction]:
        """List sanctions with filters."""
        return self.repository.list_sanctions(
            imposer_id, target_id, sanction_type, status, active_only, limit, offset
        )
    
    def get_expired_sanctions(self) -> List[Sanction]:
        """Get sanctions that have passed their end date."""
        return self.repository.get_expired_sanctions()
    
    def get_active_sanctions_by_target(self, target_id: UUID) -> List[Sanction]:
        """Get all active sanctions against a target."""
        return self.repository.get_active_sanctions_by_target(target_id)
    
    # === Compliance and Validation Operations ===
    
    def get_faction_treaties_for_compliance_check(self, faction_id: UUID) -> List[Treaty]:
        """Get faction's active treaties for compliance checking."""
        return self.repository.get_faction_treaties_for_compliance_check(faction_id)
    
    def check_faction_at_war(self, faction_a_id: UUID, faction_b_id: UUID) -> bool:
        """Check if two factions are at war."""
        return self.repository.check_faction_at_war(faction_a_id, faction_b_id)
    
    def get_faction_military_actions(self, faction_id: UUID, days: int = 30) -> List[Dict]:
        """Get recent military actions by a faction."""
        return self.repository.get_faction_military_actions(faction_id, days)
    
    def get_faction_trade_volumes(self, faction_a_id: UUID, faction_b_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get trade volume data between factions."""
        return self.repository.get_faction_trade_volumes(faction_a_id, faction_b_id, days)
    
    # Event publishing methods
    
    def publish_tension_changed_event(self, faction_a_id: UUID, faction_b_id: UUID, 
                                    old_tension: float, new_tension: float, 
                                    reason: Optional[str] = None) -> None:
        """Publish an event when tension changes between factions."""
        try:
            event_data = {
                "event_type": "tension_changed",
                "faction_a_id": str(faction_a_id),
                "faction_b_id": str(faction_b_id),
                "old_tension": old_tension,
                "new_tension": new_tension,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Tension changed between {faction_a_id} and {faction_b_id}: {old_tension} → {new_tension}")
            # In a real implementation, this would publish to an event bus
        except Exception as e:
            logger.error(f"Failed to publish tension changed event: {e}")
    
    def publish_status_changed_event(self, faction_a_id: UUID, faction_b_id: UUID,
                                   old_status: str, new_status: str) -> None:
        """Publish an event when diplomatic status changes between factions."""
        try:
            event_data = {
                "event_type": "status_changed",
                "faction_a_id": str(faction_a_id),
                "faction_b_id": str(faction_b_id),
                "old_status": old_status,
                "new_status": new_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Diplomatic status changed between {faction_a_id} and {faction_b_id}: {old_status} → {new_status}")
            # In a real implementation, this would publish to an event bus
        except Exception as e:
            logger.error(f"Failed to publish status changed event: {e}")
    
    def publish_treaty_created_event(self, treaty_id: UUID, treaty_name: str,
                                   treaty_type: str, parties: List[UUID]) -> None:
        """Publish an event when a treaty is created."""
        try:
            event_data = {
                "event_type": "treaty_created",
                "treaty_id": str(treaty_id),
                "treaty_name": treaty_name,
                "treaty_type": treaty_type,
                "parties": [str(party) for party in parties],
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Treaty created: {treaty_name} ({treaty_type}) with {len(parties)} parties")
            # In a real implementation, this would publish to an event bus
        except Exception as e:
            logger.error(f"Failed to publish treaty created event: {e}")
    
    def publish_treaty_expired_event(self, treaty_id: UUID, treaty_name: str,
                                   treaty_type: str, parties: List[UUID]) -> None:
        """Publish an event when a treaty expires."""
        try:
            event_data = {
                "event_type": "treaty_expired",
                "treaty_id": str(treaty_id),
                "treaty_name": treaty_name,
                "treaty_type": treaty_type,
                "parties": [str(party) for party in parties],
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Treaty expired: {treaty_name} ({treaty_type})")
            # In a real implementation, this would publish to an event bus
        except Exception as e:
            logger.error(f"Failed to publish treaty expired event: {e}")
    
    def publish_negotiation_started_event(self, negotiation_id: UUID, parties: List[UUID],
                                        initiator_id: UUID, treaty_type: Optional[str] = None) -> None:
        """Publish an event when a negotiation starts."""
        try:
            event_data = {
                "event_type": "negotiation_started",
                "negotiation_id": str(negotiation_id),
                "parties": [str(party) for party in parties],
                "initiator_id": str(initiator_id),
                "treaty_type": treaty_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Negotiation started: {negotiation_id} between {len(parties)} parties")
            # In a real implementation, this would publish to an event bus
        except Exception as e:
            logger.error(f"Failed to publish negotiation started event: {e}")
    
    def publish_offer_made_event(self, negotiation_id: UUID, parties: List[UUID],
                               initiator_id: UUID) -> None:
        """Publish an event when an offer is made in a negotiation."""
        try:
            event_data = {
                "event_type": "offer_made",
                "negotiation_id": str(negotiation_id),
                "parties": [str(party) for party in parties],
                "initiator_id": str(initiator_id),
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Offer made in negotiation: {negotiation_id}")
            # In a real implementation, this would publish to an event bus
        except Exception as e:
            logger.error(f"Failed to publish offer made event: {e}")
    
    def publish_offer_accepted_event(self, negotiation_id: UUID, parties: List[UUID],
                                   initiator_id: UUID) -> None:
        """Publish an event when an offer is accepted."""
        try:
            event_data = {
                "event_type": "offer_accepted",
                "negotiation_id": str(negotiation_id),
                "parties": [str(party) for party in parties],
                "initiator_id": str(initiator_id),
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Offer accepted in negotiation: {negotiation_id}")
            # In a real implementation, this would publish to an event bus
        except Exception as e:
            logger.error(f"Failed to publish offer accepted event: {e}")
    
    def publish_offer_rejected_event(self, negotiation_id: UUID, parties: List[UUID],
                                   initiator_id: UUID) -> None:
        """Publish an event when an offer is rejected."""
        try:
            event_data = {
                "event_type": "offer_rejected",
                "negotiation_id": str(negotiation_id),
                "parties": [str(party) for party in parties],
                "initiator_id": str(initiator_id),
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Offer rejected in negotiation: {negotiation_id}")
            # In a real implementation, this would publish to an event bus
        except Exception as e:
            logger.error(f"Failed to publish offer rejected event: {e}") 