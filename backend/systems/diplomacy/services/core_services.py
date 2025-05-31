"""
Services Module for Diplomacy System

This module implements the business logic for diplomatic operations, including:
- Treaty management (creation, signing, expiration)
- Negotiation logic (offers, counter-offers, agreements)
- Diplomatic event processing
- Faction relationship management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from backend.systems.diplomacy.models import (
    DiplomaticEvent, 
    DiplomaticEventType, 
    DiplomaticStatus, 
    Negotiation, 
    NegotiationOffer,
    NegotiationStatus, 
    Treaty, 
    TreatyType,
    TreatyStatus,
    TreatyViolation,
    TreatyViolationType,
    DiplomaticIncident,
    DiplomaticIncidentType,
    DiplomaticIncidentSeverity,
    Ultimatum,
    UltimatumStatus,
    Sanction,
    SanctionType,
    SanctionStatus
)
from backend.systems.diplomacy.repositories.repository import DiplomacyRepository
# Temporarily disabled to avoid circular imports
# from backend.infrastructure.events import EventDispatcher
# from backend.systems.app.core.logging import logger


class TensionService:
    """Service for managing tension between factions.
    
    This service handles:
    - Tension calculation and updates between factions
    - Tension decay over time
    - War threshold evaluation
    - Faction relationship status management
    """
    
    def __init__(self, repository: Optional[DiplomacyRepository] = None):
        """
        Initialize the service with a repository.
        
        Args:
            repository: Repository for data persistence, creates a new one if None
        """
        self.repository = repository or DiplomacyRepository()
        self._tension_cache = {}
        self._last_update = {}
        # self._event_dispatcher = EventDispatcher.get_instance()
        
        # Config parameters for tension calculation
        self.decay_rate = 0.1  # How quickly tension decays per hour
        self.max_tension = 100.0
        self.min_tension = -100.0
        self.war_threshold = 100.0
        self.alliance_threshold = -75.0
    
    def get_faction_relationship(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID
    ) -> Dict:
        """Get the relationship between two factions."""
        return self.repository.get_faction_relationship(faction_a_id, faction_b_id)
    
    def get_faction_relationships(self, faction_id: UUID) -> List[Dict]:
        """Get all relationships for a faction."""
        return self.repository.get_all_faction_relationships(faction_id)
    
    def update_faction_tension(
        self,
        faction_a_id: UUID,
        faction_b_id: UUID,
        tension_change: int,
        reason: Optional[str] = None
    ) -> Dict:
        """
        Update tension between two factions.
        
        Args:
            faction_a_id: ID of the first faction
            faction_b_id: ID of the second faction
            tension_change: Amount to change tension by (positive or negative)
            reason: Optional reason for the tension change
        
        Returns:
            Updated relationship dict
        """
        # Normalize faction order to ensure consistency
        if str(faction_a_id) > str(faction_b_id):
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        # Get the current relationship and apply decay
        relation = self.repository.get_faction_relationship(faction_a_id, faction_b_id)
        current_tension = relation.get("tension", 0)
        
        # Apply decay since last update
        current_time = datetime.utcnow()
        last_update_time = relation.get("last_updated", current_time)
        hours_passed = (current_time - last_update_time).total_seconds() / 3600
        
        if hours_passed > 0:
            decay_amount = self.decay_rate * hours_passed
            if current_tension > 0:
                current_tension = max(0, current_tension - decay_amount)
            elif current_tension < 0:
                current_tension = min(0, current_tension + decay_amount)
        
        # Calculate new tension value with limits
        new_tension = max(self.min_tension, min(self.max_tension, current_tension + tension_change))
        
        # Update relationship with new tension
        updates = {
            "tension": new_tension,
            "last_updated": current_time
        }
        
        # Check if we need to update status based on tension
        if new_tension >= self.war_threshold and relation.get("status") != DiplomaticStatus.WAR:
            updates["status"] = DiplomaticStatus.WAR
        elif new_tension <= self.alliance_threshold and relation.get("status") != DiplomaticStatus.ALLIANCE:
            updates["status"] = DiplomaticStatus.ALLIANCE
        
        # Apply updates
        updated_relation = self.repository.update_faction_relationship(faction_a_id, faction_b_id, updates)
        
        # Create and emit event
        event_data = {
            "faction_a_id": str(faction_a_id),
            "faction_b_id": str(faction_b_id),
            "old_tension": current_tension,
            "new_tension": new_tension,
            "reason": reason,
            "timestamp": current_time.isoformat()
        }
        # self._event_dispatcher.publish("faction.tension.changed", event_data)
        
        return updated_relation
    
    def set_diplomatic_status(
        self,
        faction_a_id: UUID,
        faction_b_id: UUID,
        status: DiplomaticStatus
    ) -> Dict:
        """
        Set the diplomatic status between two factions.
        
        Args:
            faction_a_id: ID of the first faction
            faction_b_id: ID of the second faction
            status: New diplomatic status
        
        Returns:
            Updated relationship dict
        """
        # Get current relationship
        relation = self.repository.get_faction_relationship(faction_a_id, faction_b_id)
        old_status = relation.get("status")
        
        # Don't update if status is the same
        if old_status == status:
            return relation
        
        # Update tension based on new status
        tension_change = 0
        
        if status == DiplomaticStatus.WAR:
            tension_change = self.war_threshold - relation.get("tension", 0)
        elif status == DiplomaticStatus.ALLIANCE:
            tension_change = self.alliance_threshold - relation.get("tension", 0)
        elif status == DiplomaticStatus.HOSTILE:
            tension_change = 50
        elif status == DiplomaticStatus.TRUCE:
            tension_change = -25
        elif status == DiplomaticStatus.NEUTRAL:
            # Move halfway back toward 0
            current_tension = relation.get("tension", 0)
            tension_change = -current_tension / 2
        
        # Update relationship with new status and tension
        updates = {
            "status": status,
            "last_status_change": datetime.utcnow()
        }
        
        updated_relation = self.repository.update_faction_relationship(faction_a_id, faction_b_id, updates)
        
        # If tension needs adjustment, do that separately
        if tension_change != 0:
            updated_relation = self.update_faction_tension(
                faction_a_id, 
                faction_b_id, 
                tension_change, 
                reason=f"Status change to {status}"
            )
        
        # Create and emit event
        event_data = {
            "faction_a_id": str(faction_a_id),
            "faction_b_id": str(faction_b_id),
            "old_status": old_status,
            "new_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        # self._event_dispatcher.publish("faction.status.changed", event_data)
        
        return updated_relation
    
    def are_at_war(self, faction_a_id: UUID, faction_b_id: UUID) -> bool:
        """Check if two factions are at war."""
        relation = self.repository.get_faction_relationship(faction_a_id, faction_b_id)
        return relation.get("status") == DiplomaticStatus.WAR
    
    def are_allied(self, faction_a_id: UUID, faction_b_id: UUID) -> bool:
        """Check if two factions are allied."""
        relation = self.repository.get_faction_relationship(faction_a_id, faction_b_id)
        return relation.get("status") == DiplomaticStatus.ALLIANCE
    
    def check_war_threshold(self, faction_a_id: UUID, faction_b_id: UUID) -> bool:
        """Check if tension between factions has reached the war threshold."""
        relation = self.repository.get_faction_relationship(faction_a_id, faction_b_id)
        return relation.get("tension", 0) >= self.war_threshold


class DiplomacyService:
    """Service for managing diplomatic operations."""

    def __init__(self, repository: Optional[DiplomacyRepository] = None):
        """
        Initialize the service with a repository.
        
        Args:
            repository: Repository for data persistence, creates a new one if None
        """
        self.repository = repository or DiplomacyRepository()
        self.tension_service = TensionService(self.repository)
    
    # Treaty methods
    
    def create_treaty(
        self,
        name: str,
        treaty_type: TreatyType,
        parties: List[UUID],
        terms: Dict = None,
        end_date: Optional[datetime] = None,
        is_public: bool = True,
        negotiation_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None
    ) -> Treaty:
        """
        Create a new treaty between factions.
        
        Args:
            name: Name of the treaty
            treaty_type: Type of treaty
            parties: List of faction IDs
            terms: Treaty terms as a dictionary
            end_date: When the treaty expires (indefinite if None)
            is_public: Whether the treaty is public knowledge
            negotiation_id: ID of the negotiation that led to this treaty
            created_by: ID of the character or system that created the treaty
        
        Returns:
            The created treaty
        """
        if terms is None:
            terms = {}
        
        # Create new treaty
        treaty = Treaty(
            name=name,
            type=treaty_type,
            parties=parties,
            terms=terms,
            end_date=end_date,
            is_public=is_public,
            negotiation_id=negotiation_id,
            created_by=created_by
        )
        
        # Save the treaty
        treaty = self.repository.create_treaty(treaty)
        
        # Update faction relationships
        self._update_faction_relationships_for_treaty(treaty)
        
        # Create treaty event
        self._create_treaty_event(treaty)
        
        return treaty
    
    def _update_faction_relationships_for_treaty(self, treaty: Treaty) -> None:
        """Update faction relationships based on a new or updated treaty."""
        # For each pair of factions in the treaty
        for i, faction_a in enumerate(treaty.parties):
            for faction_b in treaty.parties[i+1:]:
                # Get their current relationship
                relation = self.repository.get_faction_relationship(faction_a, faction_b)
                
                # Add treaty to their relationship
                if "treaties" not in relation:
                    relation["treaties"] = []
                
                if str(treaty.id) not in relation["treaties"]:
                    relation["treaties"].append(str(treaty.id))
                
                # Update diplomatic status based on treaty type
                updates = {"treaties": relation["treaties"]}
                tension_change = 0
                
                if treaty.type == TreatyType.ALLIANCE:
                    self.tension_service.set_diplomatic_status(faction_a, faction_b, DiplomaticStatus.ALLIANCE)
                elif treaty.type == TreatyType.PEACE:
                    self.tension_service.set_diplomatic_status(faction_a, faction_b, DiplomaticStatus.NEUTRAL)
                elif treaty.type == TreatyType.CEASEFIRE:
                    self.tension_service.set_diplomatic_status(faction_a, faction_b, DiplomaticStatus.TRUCE)
                elif treaty.type == TreatyType.TRADE:
                    tension_change = -15
                elif treaty.type == TreatyType.DEFENSE:
                    tension_change = -30
                elif treaty.type == TreatyType.NON_AGGRESSION:
                    tension_change = -25
                
                # Update tension if needed
                if tension_change != 0:
                    self.tension_service.update_faction_tension(
                        faction_a, 
                        faction_b, 
                        tension_change, 
                        reason=f"Treaty signed: {treaty.name}"
                    )
    
    def _create_treaty_event(self, treaty: Treaty) -> DiplomaticEvent:
        """Create a diplomatic event for a treaty signing."""
        event = DiplomaticEvent(
            event_type=DiplomaticEventType.TREATY,
            factions=treaty.parties,
            description=f"Treaty '{treaty.name}' of type {treaty.type} was signed.",
            severity=50,  # Medium-high significance
            public=treaty.is_public,
            related_treaty_id=treaty.id
        )
        
        # Add tension changes to event metadata
        for i, faction_a in enumerate(treaty.parties):
            for faction_b in treaty.parties[i+1:]:
                key = f"{faction_a}_{faction_b}"
                relation = self.repository.get_faction_relationship(faction_a, faction_b)
                event.tension_change[key] = relation.get("tension", 0)
        
        return self.repository.create_event(event)
    
    def get_treaty(self, treaty_id: UUID) -> Optional[Treaty]:
        """Get a treaty by ID."""
        return self.repository.get_treaty(treaty_id)
    
    def expire_treaty(self, treaty_id: UUID) -> Optional[Treaty]:
        """Mark a treaty as expired/inactive."""
        treaty = self.repository.get_treaty(treaty_id)
        if not treaty or not treaty.is_active:
            return None
        
        updates = {
            "is_active": False,
            "end_date": datetime.utcnow()
        }
        
        treaty = self.repository.update_treaty(treaty_id, updates)
        
        # Create expiration event
        event = DiplomaticEvent(
            event_type=DiplomaticEventType.TREATY,
            factions=treaty.parties,
            description=f"Treaty '{treaty.name}' has expired.",
            severity=30,  # Medium significance
            public=treaty.is_public,
            related_treaty_id=treaty.id
        )
        self.repository.create_event(event)
        
        # Update faction relationships
        self._update_relationships_for_expired_treaty(treaty)
        
        return treaty
    
    def _update_relationships_for_expired_treaty(self, treaty: Treaty) -> None:
        """Update faction relationships when a treaty expires."""
        # For each pair of factions in the treaty
        for i, faction_a in enumerate(treaty.parties):
            for faction_b in treaty.parties[i+1:]:
                # Get their current relationship
                relation = self.repository.get_faction_relationship(faction_a, faction_b)
                
                # Remove treaty from their relationship
                if "treaties" in relation and str(treaty.id) in relation["treaties"]:
                    relation["treaties"].remove(str(treaty.id))
                
                updates = {"treaties": relation.get("treaties", [])}
                
                # Potentially update status if this was their only alliance treaty
                if treaty.type == TreatyType.ALLIANCE:
                    # Check if they have any other active alliance treaties
                    has_other_alliance = False
                    for treaty_id in relation.get("treaties", []):
                        other_treaty = self.repository.get_treaty(UUID(treaty_id))
                        if other_treaty and other_treaty.is_active and other_treaty.type == TreatyType.ALLIANCE:
                            has_other_alliance = True
                            break
                    
                    if not has_other_alliance:
                        self.tension_service.set_diplomatic_status(faction_a, faction_b, DiplomaticStatus.NEUTRAL)
                
                # Apply tension change for expired treaty
                self.tension_service.update_faction_tension(
                    faction_a, 
                    faction_b, 
                    10,  # Small increase in tension when treaties expire
                    reason=f"Treaty expired: {treaty.name}"
                )
    
    def list_treaties(
        self, 
        faction_id: Optional[UUID] = None,
        active_only: bool = False,
        treaty_type: Optional[TreatyType] = None
    ) -> List[Treaty]:
        """List treaties, optionally filtered."""
        return self.repository.list_treaties(faction_id, active_only, treaty_type)
    
    # Negotiation methods
    
    def start_negotiation(
        self,
        parties: List[UUID],
        initiator_id: UUID,
        treaty_type: Optional[TreatyType] = None,
        initial_offer: Optional[Dict] = None,
        metadata: Dict = None
    ) -> Negotiation:
        """
        Start a new diplomatic negotiation.
        
        Args:
            parties: List of faction IDs involved
            initiator_id: ID of the faction initiating the negotiation
            treaty_type: Type of treaty being negotiated (if applicable)
            initial_offer: Initial terms offered
            metadata: Additional metadata
        
        Returns:
            The created negotiation
        """
        if metadata is None:
            metadata = {}
        
        # Create negotiation
        negotiation = Negotiation(
            parties=parties,
            initiator_id=initiator_id,
            treaty_type=treaty_type,
            status=NegotiationStatus.PENDING,
            metadata=metadata
        )
        
        # Add initial offer if provided
        if initial_offer:
            offer = NegotiationOffer(
                faction_id=initiator_id,
                terms=initial_offer
            )
            negotiation.offers.append(offer)
            negotiation.current_offer_id = offer.faction_id
        
        # Save negotiation
        negotiation = self.repository.create_negotiation(negotiation)
        
        # Create negotiation event
        self._create_negotiation_event(negotiation, "started")
        
        # Update faction relationships
        self._update_relationships_for_negotiation(negotiation)
        
        return negotiation
    
    def _create_negotiation_event(
        self, 
        negotiation: Negotiation, 
        action: str
    ) -> DiplomaticEvent:
        """Create a diplomatic event for a negotiation action."""
        parties_str = ", ".join([str(faction_id) for faction_id in negotiation.parties])
        description = f"Negotiation {action} between {parties_str}"
        if negotiation.treaty_type:
            description += f" for {negotiation.treaty_type} treaty"
        
        event = DiplomaticEvent(
            event_type=DiplomaticEventType.NEGOTIATION,
            factions=negotiation.parties,
            description=description,
            severity=20,  # Medium-low significance
            public=True,  # Negotiations are generally public knowledge
            related_negotiation_id=negotiation.id
        )
        
        return self.repository.create_event(event)
    
    def _update_relationships_for_negotiation(self, negotiation: Negotiation) -> None:
        """Update faction relationships when a negotiation starts."""
        # For each pair of factions in the negotiation
        for i, faction_a in enumerate(negotiation.parties):
            for faction_b in negotiation.parties[i+1:]:
                # Get their current relationship
                relation = self.repository.get_faction_relationship(faction_a, faction_b)
                
                # Add negotiation to their relationship
                if "negotiations" not in relation:
                    relation["negotiations"] = []
                
                if str(negotiation.id) not in relation["negotiations"]:
                    relation["negotiations"].append(str(negotiation.id))
                
                # Small reduction in tension for starting negotiations
                tension_change = -5
                current_tension = relation.get("tension", 0)
                new_tension = max(-100, min(100, current_tension + tension_change))
                
                # Apply updates
                updates = {
                    "negotiations": relation["negotiations"],
                    "tension": new_tension
                }
                self.repository.update_faction_relationship(faction_a, faction_b, updates)
    
    def get_negotiation(self, negotiation_id: UUID) -> Optional[Negotiation]:
        """Get a negotiation by ID."""
        return self.repository.get_negotiation(negotiation_id)
    
    def make_offer(
        self,
        negotiation_id: UUID,
        faction_id: UUID,
        terms: Dict,
        counter_to: Optional[UUID] = None
    ) -> Optional[Tuple[Negotiation, NegotiationOffer]]:
        """
        Make an offer in a negotiation.
        
        Args:
            negotiation_id: ID of the negotiation
            faction_id: ID of the faction making the offer
            terms: Terms of the offer
            counter_to: ID of the offer this is countering
            
        Returns:
            Tuple of (updated negotiation, new offer) or None if failed
        """
        # Get negotiation
        negotiation = self.repository.get_negotiation(negotiation_id)
        if not negotiation or negotiation.status != NegotiationStatus.PENDING:
            return None
        
        # Check if faction is a party to the negotiation
        if faction_id not in negotiation.parties:
            return None
        
        # Create new offer
        offer = NegotiationOffer(
            faction_id=faction_id,
            terms=terms,
            counter_offer_id=counter_to
        )
        
        # Add offer to negotiation
        negotiation.offers.append(offer)
        negotiation.current_offer_id = offer.faction_id
        negotiation.status = NegotiationStatus.COUNTER_OFFERED
        
        # Update negotiation
        negotiation = self.repository.update_negotiation(negotiation_id, {
            "offers": negotiation.offers,
            "current_offer_id": offer.faction_id,
            "status": NegotiationStatus.COUNTER_OFFERED
        })
        
        return (negotiation, offer)
    
    def accept_offer(
        self,
        negotiation_id: UUID,
        faction_id: UUID
    ) -> Optional[Tuple[Negotiation, Treaty]]:
        """
        Accept the current offer in a negotiation, potentially creating a treaty.
        
        Args:
            negotiation_id: ID of the negotiation
            faction_id: ID of the faction accepting the offer
            
        Returns:
            Tuple of (closed negotiation, new treaty) or None if failed
        """
        # Get negotiation
        negotiation = self.repository.get_negotiation(negotiation_id)
        if not negotiation or negotiation.status != NegotiationStatus.COUNTER_OFFERED:
            return None
        
        # Check if faction is a party to the negotiation
        if faction_id not in negotiation.parties:
            return None
        
        # Get current offer
        if not negotiation.current_offer_id:
            return None
        
        current_offer = next((o for o in negotiation.offers if o.faction_id == negotiation.current_offer_id), None)
        if not current_offer:
            return None
        
        # Cannot accept your own offer
        if current_offer.faction_id == faction_id:
            return None
        
        # Mark offer as accepted
        current_offer.accepted = True
        
        # Update negotiation status and end date
        now = datetime.utcnow()
        updates = {
            "status": NegotiationStatus.ACCEPTED,
            "end_date": now,
            "offers": negotiation.offers  # Update the modified offer
        }
        
        # Create treaty from accepted offer
        treaty_name = negotiation.metadata.get("treaty_name", f"Treaty of {now.strftime('%Y-%m-%d')}")
        treaty = self.create_treaty(
            name=treaty_name,
            treaty_type=negotiation.treaty_type or TreatyType.CUSTOM,
            parties=negotiation.parties,
            terms=current_offer.terms,
            is_public=True,
            negotiation_id=negotiation.id
        )
        
        # Update negotiation with treaty reference
        updates["result_treaty_id"] = treaty.id
        negotiation = self.repository.update_negotiation(negotiation_id, updates)
        
        # Create event for successful negotiation
        event = DiplomaticEvent(
            event_type=DiplomaticEventType.NEGOTIATION,
            factions=negotiation.parties,
            description=f"Negotiation concluded successfully with treaty '{treaty_name}'",
            severity=40,  # Medium-high significance
            public=True,
            related_negotiation_id=negotiation.id,
            related_treaty_id=treaty.id
        )
        self.repository.create_event(event)
        
        # Update relationships for completed negotiation
        self._update_relationships_for_completed_negotiation(negotiation, successful=True)
        
        return (negotiation, treaty)
    
    def reject_offer(
        self,
        negotiation_id: UUID,
        faction_id: UUID,
        final: bool = False
    ) -> Optional[Negotiation]:
        """
        Reject the current offer in a negotiation.
        
        Args:
            negotiation_id: ID of the negotiation
            faction_id: ID of the faction rejecting the offer
            final: If True, ends the negotiation as rejected
            
        Returns:
            Updated negotiation or None if failed
        """
        # Get negotiation
        negotiation = self.repository.get_negotiation(negotiation_id)
        if not negotiation or negotiation.status != NegotiationStatus.COUNTER_OFFERED:
            return None
        
        # Check if faction is a party to the negotiation
        if faction_id not in negotiation.parties:
            return None
        
        # Get current offer
        if not negotiation.current_offer_id:
            return None
        
        current_offer = next((o for o in negotiation.offers if o.faction_id == negotiation.current_offer_id), None)
        if not current_offer:
            return None
        
        # Cannot reject your own offer
        if current_offer.faction_id == faction_id:
            return None
        
        # Mark offer as rejected
        current_offer.accepted = False
        
        updates = {
            "offers": negotiation.offers  # Update the modified offer
        }
        
        # If final rejection, end negotiation
        if final:
            now = datetime.utcnow()
            updates.update({
                "status": NegotiationStatus.REJECTED,
                "end_date": now
            })
            
            # Create event for failed negotiation
            event = DiplomaticEvent(
                event_type=DiplomaticEventType.NEGOTIATION,
                factions=negotiation.parties,
                description=f"Negotiation ended without agreement",
                severity=30,  # Medium significance
                public=True,
                related_negotiation_id=negotiation.id
            )
            self.repository.create_event(event)
            
            # Update relationships for failed negotiation
            self._update_relationships_for_completed_negotiation(negotiation, successful=False)
        else:
            # Just update the negotiation but leave it open for counter-offers
            updates["status"] = NegotiationStatus.PENDING
        
        return self.repository.update_negotiation(negotiation_id, updates)
    
    def _update_relationships_for_completed_negotiation(
        self, 
        negotiation: Negotiation,
        successful: bool
    ) -> None:
        """Update faction relationships when a negotiation is completed."""
        # For each pair of factions in the negotiation
        for i, faction_a in enumerate(negotiation.parties):
            for faction_b in negotiation.parties[i+1:]:
                # Get their current relationship
                relation = self.repository.get_faction_relationship(faction_a, faction_b)
                
                # Remove negotiation from active negotiations
                if "negotiations" in relation and str(negotiation.id) in relation["negotiations"]:
                    relation["negotiations"].remove(str(negotiation.id))
                
                updates = {"negotiations": relation.get("negotiations", [])}
                
                # Adjust tension based on negotiation outcome
                tension_change = -10 if successful else 10  # Decrease for success, increase for failure
                current_tension = relation.get("tension", 0)
                new_tension = max(-100, min(100, current_tension + tension_change))
                updates["tension"] = new_tension
                
                # Apply updates
                self.repository.update_faction_relationship(faction_a, faction_b, updates)
    
    # Delegates for tension service methods
    
    def get_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID) -> Dict:
        """Get the relationship between two factions."""
        return self.tension_service.get_faction_relationship(faction_a_id, faction_b_id)
    
    def get_faction_relationships(self, faction_id: UUID) -> List[Dict]:
        """Get all relationships for a faction."""
        return self.tension_service.get_faction_relationships(faction_id)
    
    def update_faction_tension(
        self,
        faction_a_id: UUID,
        faction_b_id: UUID,
        tension_change: int,
        reason: Optional[str] = None
    ) -> Dict:
        """Update tension between two factions."""
        return self.tension_service.update_faction_tension(
            faction_a_id, faction_b_id, tension_change, reason
        )
    
    def set_diplomatic_status(
        self,
        faction_a_id: UUID,
        faction_b_id: UUID,
        status: DiplomaticStatus
    ) -> Dict:
        """Set the diplomatic status between two factions."""
        return self.tension_service.set_diplomatic_status(faction_a_id, faction_b_id, status)
    
    def are_at_war(self, faction_a_id: UUID, faction_b_id: UUID) -> bool:
        """Check if two factions are at war."""
        return self.tension_service.are_at_war(faction_a_id, faction_b_id)
    
    def are_allied(self, faction_a_id: UUID, faction_b_id: UUID) -> bool:
        """Check if two factions are allied."""
        return self.tension_service.are_allied(faction_a_id, faction_b_id)
    
    def has_treaty_of_type(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID, 
        treaty_type: TreatyType
    ) -> bool:
        """Check if two factions have an active treaty of the specified type."""
        treaties = self.list_treaties(faction_id=faction_a_id, active_only=True, treaty_type=treaty_type)
        for treaty in treaties:
            if faction_b_id in treaty.parties:
                return True
        return False
    
    # Treaty Enforcement and Violation Methods
    
    def report_treaty_violation(
        self,
        treaty_id: UUID,
        violator_id: UUID,
        violation_type: TreatyViolationType,
        description: str,
        evidence: Dict,
        reported_by: UUID,
        severity: int = 50
    ) -> TreatyViolation:
        """
        Report a violation of a treaty by one of its parties.
        
        Args:
            treaty_id: ID of the treaty that was violated
            violator_id: ID of the faction that violated the treaty
            violation_type: Type of violation that occurred
            description: Description of what happened
            evidence: Dict containing proof or context of the violation
            reported_by: ID of the faction reporting the violation
            severity: How severe the violation is (0-100)
            
        Returns:
            The created treaty violation record
            
        Raises:
            ValueError: If the treaty doesn't exist, violator isn't a party to treaty, etc.
        """
        # Validate the treaty
        treaty = self.get_treaty(treaty_id)
        if not treaty:
            raise ValueError(f"Treaty {treaty_id} does not exist")
        if not treaty.is_active:
            raise ValueError(f"Treaty {treaty_id} is not active")
        
        # Validate the factions
        if violator_id not in treaty.parties:
            raise ValueError(f"Faction {violator_id} is not a party to this treaty")
        if reported_by not in treaty.parties and reported_by != UUID('00000000-0000-0000-0000-000000000000'):  # System ID
            raise ValueError(f"Faction {reported_by} is not a party to this treaty")
        
        # Create the violation record
        violation = TreatyViolation(
            treaty_id=treaty_id,
            violator_id=violator_id,
            violation_type=violation_type,
            description=description,
            evidence=evidence,
            reported_by=reported_by,
            severity=severity
        )
        
        # Save it
        violation = self.repository.create_violation(violation)
        
        # Create a diplomatic event for this violation
        event = DiplomaticEvent(
            event_type=DiplomaticEventType.TREATY_VIOLATION,
            factions=treaty.parties,
            description=f"Treaty {treaty.name} violated by {violator_id}",
            severity=severity,
            related_treaty_id=treaty_id,
            metadata={
                "violation_id": str(violation.id),
                "violation_type": violation.violation_type,
                "violator_id": str(violator_id),
                "reported_by": str(reported_by)
            }
        )
        self.repository.create_event(event)
        
        # Apply tension changes
        for faction_id in treaty.parties:
            if faction_id != violator_id:
                # Update tension between violator and other parties
                tension_change = min(severity // 2, 25)  # Cap at +25 per violation
                self.update_faction_tension(
                    faction_a_id=faction_id,
                    faction_b_id=violator_id,
                    tension_change=tension_change,
                    reason=f"Treaty violation: {violation_type}"
                )
        
        return violation
    
    def acknowledge_violation(
        self,
        violation_id: UUID,
        acknowledging_faction_id: UUID,
        resolution_details: Optional[str] = None
    ) -> Optional[TreatyViolation]:
        """
        Acknowledge a treaty violation as the violating faction.
        
        Args:
            violation_id: ID of the violation to acknowledge
            acknowledging_faction_id: ID of the faction acknowledging (must be the violator)
            resolution_details: Optional details about resolution
            
        Returns:
            Updated violation record or None if not found
            
        Raises:
            ValueError: If acknowledging faction is not the violator
        """
        # Get the violation
        violation = self.repository.get_violation(violation_id)
        if not violation:
            return None
        
        # Verify the acknowledging faction
        if violation.violator_id != acknowledging_faction_id:
            raise ValueError(f"Only the violating faction ({violation.violator_id}) can acknowledge this violation")
        
        # Update the violation
        updates = {
            "acknowledged": True,
            "resolution_details": resolution_details if resolution_details else violation.resolution_details
        }
        
        # Apply tension reduction if acknowledging
        treaty = self.get_treaty(violation.treaty_id)
        if treaty and treaty.is_active:
            for faction_id in treaty.parties:
                if faction_id != acknowledging_faction_id:
                    # Reduce tension slightly when acknowledging a violation
                    tension_change = -10  # -10 for acknowledging
                    self.update_faction_tension(
                        faction_a_id=faction_id,
                        faction_b_id=acknowledging_faction_id,
                        tension_change=tension_change,
                        reason="Acknowledged treaty violation"
                    )
        
        return self.repository.update_violation(violation_id, updates)
    
    def resolve_violation(
        self,
        violation_id: UUID,
        resolution_details: str
    ) -> Optional[TreatyViolation]:
        """
        Mark a treaty violation as resolved.
        
        Args:
            violation_id: ID of the violation to resolve
            resolution_details: Details about how the violation was resolved
            
        Returns:
            Updated violation record or None if not found
        """
        # Get the violation
        violation = self.repository.get_violation(violation_id)
        if not violation:
            return None
        
        # Update the violation
        updates = {
            "resolved": True,
            "resolution_details": resolution_details
        }
        
        updated_violation = self.repository.update_violation(violation_id, updates)
        
        # Create a resolution event
        if updated_violation:
            treaty = self.get_treaty(violation.treaty_id)
            if treaty:
                event = DiplomaticEvent(
                    event_type=DiplomaticEventType.DIPLOMATIC_INCIDENT,
                    factions=treaty.parties,
                    description=f"Treaty violation resolved: {resolution_details}",
                    severity=20,  # Medium severity for resolution events
                    related_treaty_id=treaty.id,
                    metadata={
                        "violation_id": str(violation.id),
                        "resolution": resolution_details
                    }
                )
                self.repository.create_event(event)
        
        return updated_violation
    
    def get_treaty_violations(
        self,
        treaty_id: Optional[UUID] = None,
        faction_id: Optional[UUID] = None,
        violation_type: Optional[TreatyViolationType] = None,
        resolved: Optional[bool] = None
    ) -> List[TreatyViolation]:
        """
        Get treaty violations, optionally filtered.
        
        Args:
            treaty_id: Optional ID of treaty to filter by
            faction_id: Optional ID of faction to filter by (violator or reporter)
            violation_type: Optional type of violation to filter by
            resolved: Optional resolved status to filter by
            
        Returns:
            List of matching treaty violations
        """
        return self.repository.list_violations(
            treaty_id=treaty_id,
            faction_id=faction_id,
            violation_type=violation_type,
            resolved=resolved
        )
    
    def check_treaty_compliance(
        self, 
        faction_id: UUID,
        violation_types: Optional[List[TreatyViolationType]] = None
    ) -> Dict[UUID, List[TreatyViolation]]:
        """
        Check if a faction is compliant with all its treaties.
        
        Args:
            faction_id: ID of the faction to check compliance for
            violation_types: Optional list of violation types to check for
            
        Returns:
            Dict mapping treaty IDs to lists of unresolved violations
        """
        # Get all treaties the faction is a party to
        treaties = self.list_treaties(faction_id=faction_id, active_only=True)
        
        result = {}
        for treaty in treaties:
            # Check for unresolved violations where this faction is the violator
            violations = self.repository.list_violations(
                treaty_id=treaty.id,
                faction_id=faction_id,  # This will match violator or reporter
                violation_type=None,    # Any violation type
                resolved=False          # Only unresolved violations
            )
            
            # Filter to only violations where this faction is the violator
            violations = [v for v in violations if v.violator_id == faction_id]
            
            # Filter by violation types if specified
            if violation_types:
                violations = [v for v in violations if v.violation_type in violation_types]
            
            if violations:  # Only include treaties with violations
                result[treaty.id] = violations
        
        return result
    
    def enforce_treaties_automatically(self) -> List[TreatyViolation]:
        """
        Automatically detect and report treaty violations based on world state.
        This would be called periodically to enforce treaties without manual reporting.
        
        In a real implementation, this would check world state, faction actions, etc.
        
        Returns:
            List of newly detected treaty violations
        """
        # Placeholder for automatic enforcement logic
        # In a real implementation, this would:
        # 1. Get all active treaties
        # 2. For each treaty, check if its terms are being violated
        # 3. If violations are found, report them
        # 4. Return the list of new violations
        
        # Example placeholder logic:
        treaties = self.list_treaties(active_only=True)
        new_violations = []
        
        # This would actually check game state to detect violations
        # For now, we're just returning an empty list
        
        return new_violations

    # Diplomatic Incident Methods
    
    def create_diplomatic_incident(
        self,
        incident_type: DiplomaticIncidentType,
        perpetrator_id: UUID,
        victim_id: UUID,
        description: str,
        evidence: Dict[str, Union[str, int, bool, Dict, List]] = {},
        severity: DiplomaticIncidentSeverity = DiplomaticIncidentSeverity.MODERATE,
        tension_impact: int = 20,
        public: bool = True,
        witnessed_by: List[UUID] = [],
        related_event_id: Optional[UUID] = None,
        related_treaty_id: Optional[UUID] = None
    ) -> DiplomaticIncident:
        """
        Create a new diplomatic incident.
        
        Args:
            incident_type: Type of the incident
            perpetrator_id: ID of the faction that caused the incident
            victim_id: ID of the faction affected by the incident
            description: Description of the incident
            evidence: Evidence supporting the incident claim
            severity: How severe the incident is
            tension_impact: How much diplomatic tension this adds between the factions
            public: Whether this incident is public knowledge
            witnessed_by: List of faction IDs that witnessed the incident
            related_event_id: ID of a related diplomatic event, if any
            related_treaty_id: ID of a related treaty, if any
            
        Returns:
            The created diplomatic incident object
        """
        incident_data = {
            "incident_type": incident_type,
            "perpetrator_id": perpetrator_id,
            "victim_id": victim_id,
            "description": description,
            "evidence": evidence,
            "severity": severity,
            "tension_impact": tension_impact,
            "public": public,
            "witnessed_by": witnessed_by,
            "related_event_id": related_event_id,
            "related_treaty_id": related_treaty_id
        }
        
        # Create the incident
        incident = self.repository.create_diplomatic_incident(incident_data)
        
        # Update diplomatic tension between the factions
        self.tension_service.update_tension(
            faction_a_id=perpetrator_id,
            faction_b_id=victim_id, 
            change=tension_impact
        )
        
        # If this is a treaty violation, check for potential treaty breach
        if incident_type == DiplomaticIncidentType.TREATY_VIOLATION and related_treaty_id:
            treaty = self.repository.get_treaty(related_treaty_id)
            if treaty and treaty.is_active:
                # Check if this is a severe violation
                if severity in [DiplomaticIncidentSeverity.MAJOR, DiplomaticIncidentSeverity.CRITICAL]:
                    # Trigger an event that might lead to treaty cancellation
                    self.notify_treaty_breach(treaty.id, perpetrator_id, incident.id)
        
        return incident
    
    def get_diplomatic_incident(
        self,
        incident_id: UUID
    ) -> Optional[DiplomaticIncident]:
        """
        Get a diplomatic incident by ID.
        
        Args:
            incident_id: ID of the incident to get
            
        Returns:
            The incident if found, None otherwise
        """
        return self.repository.get_diplomatic_incident(incident_id)
    
    def update_diplomatic_incident(
        self,
        incident_id: UUID,
        severity: Optional[DiplomaticIncidentSeverity] = None,
        resolved: Optional[bool] = None,
        resolution_details: Optional[str] = None
    ) -> Optional[DiplomaticIncident]:
        """
        Update a diplomatic incident.
        
        Args:
            incident_id: ID of the incident to update
            severity: New severity level
            resolved: Mark incident as resolved
            resolution_details: Details about how the incident was resolved
            
        Returns:
            The updated incident if found, None otherwise
        """
        updates = {}
        
        if severity is not None:
            updates["severity"] = severity
            
        if resolved is not None:
            updates["resolved"] = resolved
            
        if resolution_details is not None:
            updates["resolution_details"] = resolution_details
            
        if not updates:
            return self.repository.get_diplomatic_incident(incident_id)
        
        return self.repository.update_diplomatic_incident(incident_id, updates)
    
    def list_diplomatic_incidents(
        self,
        faction_id: Optional[UUID] = None,
        as_perpetrator: bool = True,
        as_victim: bool = True,
        resolved: Optional[bool] = None,
        incident_type: Optional[DiplomaticIncidentType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[DiplomaticIncident]:
        """
        List diplomatic incidents with optional filtering.
        
        Args:
            faction_id: Filter by faction involved
            as_perpetrator: Include incidents where faction is the perpetrator
            as_victim: Include incidents where faction is the victim
            resolved: Filter by resolution status
            incident_type: Filter by incident type
            limit: Maximum number of incidents to return
            offset: Number of incidents to skip
            
        Returns:
            List of diplomatic incidents matching the criteria
        """
        return self.repository.list_diplomatic_incidents(
            faction_id=faction_id,
            as_perpetrator=as_perpetrator,
            as_victim=as_victim,
            resolved=resolved,
            incident_type=incident_type,
            limit=limit,
            offset=offset
        )
    
    def resolve_diplomatic_incident(
        self,
        incident_id: UUID,
        resolution_details: str
    ) -> Optional[DiplomaticIncident]:
        """
        Mark a diplomatic incident as resolved.
        
        Args:
            incident_id: ID of the incident to resolve
            resolution_details: Description of how the incident was resolved
            
        Returns:
            The updated incident if found, None otherwise
        """
        return self.repository.update_diplomatic_incident(
            incident_id=incident_id,
            updates={
                "resolved": True,
                "resolution_details": resolution_details
            }
        )
    
    def notify_treaty_breach(
        self,
        treaty_id: UUID,
        violator_id: UUID,
        incident_id: UUID
    ) -> DiplomaticEvent:
        """
        Create a notification event for a potential treaty breach.
        
        Args:
            treaty_id: ID of the treaty that was breached
            violator_id: ID of the faction that violated the treaty
            incident_id: ID of the incident that constitutes the breach
            
        Returns:
            The created diplomatic event
        """
        treaty = self.repository.get_treaty(treaty_id)
        if not treaty:
            raise ValueError(f"Treaty {treaty_id} not found")
            
        incident = self.repository.get_diplomatic_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        # Create a treaty breach event
        event_data = {
            "event_type": DiplomaticEventType.TREATY_BREACH,
            "factions": treaty.parties,
            "description": f"Treaty breach: {treaty.name} violated by {violator_id}. {incident.description}",
            "severity": 80,  # Treaty breaches are very serious
            "public": True,
            "related_treaty_id": treaty_id,
            "metadata": {
                "treaty_id": str(treaty_id),
                "violator_id": str(violator_id),
                "incident_id": str(incident_id)
            }
        }
        
        return self.repository.create_diplomatic_event(event_data)

    # Ultimatum Methods
    
    def create_ultimatum(
        self,
        issuer_id: UUID,
        recipient_id: UUID,
        demands: Dict[str, Union[str, int, bool, Dict, List]],
        consequences: Dict[str, Union[str, int, bool, Dict, List]],
        deadline: datetime,
        justification: str,
        public: bool = True,
        witnessed_by: List[UUID] = [],
        related_incident_id: Optional[UUID] = None,
        related_treaty_id: Optional[UUID] = None,
        related_event_id: Optional[UUID] = None,
        tension_change_on_issue: int = 20,
        tension_change_on_accept: int = -10,
        tension_change_on_reject: int = 40
    ) -> Ultimatum:
        """
        Create a new ultimatum.
        
        Args:
            issuer_id: ID of the faction issuing the ultimatum
            recipient_id: ID of the faction receiving the ultimatum
            demands: What the issuer is demanding from the recipient
            consequences: What will happen if the demands are not met
            deadline: When the ultimatum expires
            justification: Why the ultimatum is being issued
            public: Whether this ultimatum is public knowledge
            witnessed_by: List of faction IDs that witnessed the ultimatum
            related_incident_id: ID of a related diplomatic incident, if any
            related_treaty_id: ID of a related treaty, if any
            related_event_id: ID of a related diplomatic event, if any
            tension_change_on_issue: How much diplomatic tension to add when issued
            tension_change_on_accept: How much diplomatic tension to add/remove if accepted
            tension_change_on_reject: How much diplomatic tension to add if rejected
            
        Returns:
            The created ultimatum object
        """
        ultimatum_data = {
            "issuer_id": issuer_id,
            "recipient_id": recipient_id,
            "demands": demands,
            "consequences": consequences,
            "deadline": deadline,
            "justification": justification,
            "public": public,
            "witnessed_by": witnessed_by,
            "related_incident_id": related_incident_id,
            "related_treaty_id": related_treaty_id,
            "related_event_id": related_event_id,
            "tension_change_on_issue": tension_change_on_issue,
            "tension_change_on_accept": tension_change_on_accept,
            "tension_change_on_reject": tension_change_on_reject
        }
        
        # Create the ultimatum
        ultimatum = self.repository.create_ultimatum(ultimatum_data)
        
        # Update diplomatic tension between the factions when ultimatum is issued
        self.tension_service.update_tension(
            faction_a_id=issuer_id,
            faction_b_id=recipient_id, 
            change=tension_change_on_issue
        )
        
        return ultimatum
    
    def get_ultimatum(
        self,
        ultimatum_id: UUID
    ) -> Optional[Ultimatum]:
        """
        Get an ultimatum by ID.
        
        Args:
            ultimatum_id: ID of the ultimatum to get
            
        Returns:
            The ultimatum if found, None otherwise
        """
        return self.repository.get_ultimatum(ultimatum_id)
    
    def update_ultimatum(
        self,
        ultimatum_id: UUID,
        status: Optional[UltimatumStatus] = None,
        deadline: Optional[datetime] = None,
        demands: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None,
        consequences: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None
    ) -> Optional[Ultimatum]:
        """
        Update an ultimatum.
        
        Args:
            ultimatum_id: ID of the ultimatum to update
            status: New status
            deadline: New deadline
            demands: Updated demands
            consequences: Updated consequences
            
        Returns:
            The updated ultimatum if found, None otherwise
        """
        updates = {}
        
        if status is not None:
            updates["status"] = status
            
        if deadline is not None:
            updates["deadline"] = deadline
            
        if demands is not None:
            updates["demands"] = demands
            
        if consequences is not None:
            updates["consequences"] = consequences
            
        if not updates:
            return self.repository.get_ultimatum(ultimatum_id)
        
        # Get current ultimatum before updating
        current_ultimatum = self.repository.get_ultimatum(ultimatum_id)
        if not current_ultimatum:
            return None
            
        # Update the ultimatum
        updated_ultimatum = self.repository.update_ultimatum(ultimatum_id, updates)
        
        # If status changed to ACCEPTED or REJECTED, update diplomatic tension
        if status in [UltimatumStatus.ACCEPTED, UltimatumStatus.REJECTED] and current_ultimatum.status != status:
            tension_change = (
                current_ultimatum.tension_change_on_accept 
                if status == UltimatumStatus.ACCEPTED 
                else current_ultimatum.tension_change_on_reject
            )
            
            self.tension_service.update_tension(
                faction_a_id=current_ultimatum.issuer_id,
                faction_b_id=current_ultimatum.recipient_id,
                change=tension_change
            )
            
            # If accepted, implement the consequences of accepting the ultimatum
            if status == UltimatumStatus.ACCEPTED:
                self._handle_accepted_ultimatum(current_ultimatum)
            
            # If rejected, check if consequences should be automatically applied
            if status == UltimatumStatus.REJECTED:
                self._handle_rejected_ultimatum(current_ultimatum)
        
        return updated_ultimatum
    
    def list_ultimatums(
        self,
        faction_id: Optional[UUID] = None,
        as_issuer: bool = True,
        as_recipient: bool = True,
        status: Optional[UltimatumStatus] = None,
        active_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Ultimatum]:
        """
        List ultimatums with optional filtering.
        
        Args:
            faction_id: Filter by faction involved
            as_issuer: Include ultimatums where faction is the issuer
            as_recipient: Include ultimatums where faction is the recipient
            status: Filter by ultimatum status
            active_only: Only include active ultimatums (pending and not expired)
            limit: Maximum number of ultimatums to return
            offset: Number of ultimatums to skip
            
        Returns:
            List of ultimatum objects matching the criteria
        """
        return self.repository.list_ultimatums(
            faction_id=faction_id,
            as_issuer=as_issuer,
            as_recipient=as_recipient,
            status=status,
            active_only=active_only,
            limit=limit,
            offset=offset
        )
    
    def respond_to_ultimatum(
        self,
        ultimatum_id: UUID,
        accept: bool,
        response_justification: Optional[str] = None
    ) -> Optional[Ultimatum]:
        """
        Respond to an ultimatum.
        
        Args:
            ultimatum_id: ID of the ultimatum to respond to
            accept: Whether to accept the ultimatum
            response_justification: Optional justification for the response
            
        Returns:
            The updated ultimatum if found, None otherwise
        """
        ultimatum = self.repository.get_ultimatum(ultimatum_id)
        if not ultimatum:
            return None
            
        if ultimatum.status != UltimatumStatus.PENDING:
            raise ValueError(f"Ultimatum {ultimatum_id} has already been responded to")
            
        now = datetime.now()
        if ultimatum.deadline < now:
            raise ValueError(f"Ultimatum {ultimatum_id} has expired")
            
        status = UltimatumStatus.ACCEPTED if accept else UltimatumStatus.REJECTED
        
        updates = {
            "status": status
        }
        
        if response_justification:
            updates["metadata"] = ultimatum.dict().get("metadata", {})
            updates["metadata"]["response_justification"] = response_justification
            
        return self.update_ultimatum(ultimatum_id, status=status)
    
    def check_expired_ultimatums(self) -> List[Ultimatum]:
        """
        Check for expired ultimatums and mark them as EXPIRED.
        
        Returns:
            List of ultimatums that were marked as expired
        """
        now = datetime.now()
        pending_ultimatums = self.list_ultimatums(status=UltimatumStatus.PENDING)
        expired_ultimatums = []
        
        for ultimatum in pending_ultimatums:
            if ultimatum.deadline < now:
                updated = self.repository.update_ultimatum(
                    ultimatum_id=ultimatum.id,
                    updates={"status": UltimatumStatus.EXPIRED}
                )
                
                if updated:
                    # Create an expiration event
                    event_data = {
                        "event_type": DiplomaticEventType.ULTIMATUM_EXPIRED,
                        "factions": [ultimatum.issuer_id, ultimatum.recipient_id] + ultimatum.witnessed_by,
                        "description": f"Ultimatum expired without response: {ultimatum.justification}",
                        "severity": 50,
                        "public": ultimatum.public,
                        "related_treaty_id": ultimatum.related_treaty_id,
                        "metadata": {
                            "ultimatum_id": str(ultimatum.id),
                            "issuer_id": str(ultimatum.issuer_id),
                            "recipient_id": str(ultimatum.recipient_id),
                        },
                        "tension_change": {
                            str(ultimatum.issuer_id): ultimatum.tension_change_on_reject // 2  # Half the rejection tension
                        }
                    }
                    
                    self.repository.create_diplomatic_event(event_data)
                    
                    # Also handle consequences automatically, similar to rejection
                    self._handle_rejected_ultimatum(ultimatum)
                    
                    expired_ultimatums.append(updated)
        
        return expired_ultimatums
    
    def _handle_accepted_ultimatum(self, ultimatum: Ultimatum) -> None:
        """
        Handle the consequences of an accepted ultimatum.
        
        Args:
            ultimatum: The accepted ultimatum
        """
        # This could involve creating new treaties, ending wars, etc.
        # The specific implementation depends on the type of demands
        
        # Example: If the demands include creating a treaty
        if "create_treaty" in ultimatum.demands:
            treaty_data = ultimatum.demands["create_treaty"]
            if isinstance(treaty_data, dict):
                try:
                    self.create_treaty(
                        name=treaty_data.get("name", f"Treaty from ultimatum {ultimatum.id}"),
                        type=TreatyType(treaty_data.get("type", "peace")),
                        parties=[ultimatum.issuer_id, ultimatum.recipient_id],
                        terms=treaty_data.get("terms", {}),
                        end_date=treaty_data.get("end_date"),
                        is_public=treaty_data.get("is_public", True)
                    )
                except (ValueError, KeyError) as e:
                    # Log the error but don't raise - ultimatum is still considered accepted
                    print(f"Error creating treaty from ultimatum {ultimatum.id}: {e}")
    
    def _handle_rejected_ultimatum(self, ultimatum: Ultimatum) -> None:
        """
        Handle the consequences of a rejected ultimatum.
        
        Args:
            ultimatum: The rejected ultimatum
        """
        # This could involve declaring war, imposing sanctions, etc.
        # The specific implementation depends on the type of consequences
        
        # Example: If the consequences include declaring war
        if "declare_war" in ultimatum.consequences and ultimatum.consequences["declare_war"]:
            try:
                # Create a war declaration event
                war_event_data = {
                    "event_type": DiplomaticEventType.WAR_DECLARATION,
                    "factions": [ultimatum.issuer_id, ultimatum.recipient_id],
                    "description": f"War declared by {ultimatum.issuer_id} against {ultimatum.recipient_id} following ultimatum rejection.",
                    "severity": 100,  # War is maximum severity
                    "public": True,
                    "metadata": {
                        "ultimatum_id": str(ultimatum.id),
                        "casus_belli": ultimatum.justification
                    },
                    "tension_change": {
                        str(ultimatum.recipient_id): 100  # Set tension to maximum
                    }
                }
                
                self.repository.create_diplomatic_event(war_event_data)
                
                # Update the diplomatic status to WAR
                self.tension_service.set_diplomatic_status(
                    faction_a_id=ultimatum.issuer_id,
                    faction_b_id=ultimatum.recipient_id,
                    status=DiplomaticStatus.WAR
                )
            except Exception as e:
                # Log the error but don't raise - ultimatum is still considered rejected
                print(f"Error applying war consequences for ultimatum {ultimatum.id}: {e}") 

    # Sanction Methods
    
    def create_sanction(
        self,
        imposer_id: UUID,
        target_id: UUID,
        sanction_type: SanctionType,
        description: str,
        justification: str,
        end_date: Optional[datetime] = None,
        conditions_for_lifting: Dict[str, Union[str, int, bool, Dict, List]] = None,
        severity: int = 50,
        economic_impact: int = 50,
        diplomatic_impact: int = 50,
        enforcement_measures: Dict[str, Union[str, int, bool, Dict, List]] = None,
        supporting_factions: List[UUID] = None,
        opposing_factions: List[UUID] = None,
        is_public: bool = True
    ) -> Sanction:
        """
        Create a new diplomatic sanction.
        
        Args:
            imposer_id: ID of the faction imposing the sanction
            target_id: ID of the faction targeted by the sanction
            sanction_type: Type of sanction being imposed
            description: Description of the sanction
            justification: Reason for imposing the sanction
            end_date: When the sanction will end (None for indefinite)
            conditions_for_lifting: Conditions that must be met to lift the sanction
            severity: How severe the sanction is (0-100)
            economic_impact: Estimated economic impact on target (0-100)
            diplomatic_impact: Estimated diplomatic impact (0-100)
            enforcement_measures: How the sanction will be enforced
            supporting_factions: Other factions supporting this sanction
            opposing_factions: Factions opposing this sanction
            is_public: Whether this sanction is publicly announced
            
        Returns:
            The created sanction object
        """
        conditions_for_lifting = conditions_for_lifting or {}
        enforcement_measures = enforcement_measures or {}
        supporting_factions = supporting_factions or []
        opposing_factions = opposing_factions or []
        
        # Create the sanction
        sanction = Sanction(
            imposer_id=imposer_id,
            target_id=target_id,
            sanction_type=sanction_type,
            description=description,
            justification=justification,
            end_date=end_date,
            conditions_for_lifting=conditions_for_lifting,
            severity=severity,
            economic_impact=economic_impact,
            diplomatic_impact=diplomatic_impact,
            enforcement_measures=enforcement_measures,
            supporting_factions=supporting_factions,
            opposing_factions=opposing_factions,
            is_public=is_public
        )
        
        sanction = self.repository.create_sanction(sanction)
        
        # Update diplomatic tension between the factions
        tension_change = severity // 2  # The more severe the sanction, the more tension it creates
        self.tension_service.update_tension(
            faction_a_id=imposer_id,
            faction_b_id=target_id,
            change=tension_change,
            reason=f"Sanction imposed: {sanction_type.value}"
        )
        
        # Create a corresponding diplomatic event
        event_data = {
            "event_type": DiplomaticEventType.OTHER,
            "factions": [imposer_id, target_id] + supporting_factions + opposing_factions,
            "description": f"Sanction imposed: {description}",
            "severity": severity,
            "public": is_public,
            "metadata": {
                "sanction_id": str(sanction.id),
                "sanction_type": sanction_type.value,
                "imposer_id": str(imposer_id),
                "target_id": str(target_id),
                "justification": justification
            },
            "tension_change": {
                str(target_id): tension_change
            }
        }
        
        self.repository.create_event(DiplomaticEvent(**event_data))
        
        # Create a diplomatic incident
        if severity >= 50:  # Only create incidents for more severe sanctions
            incident_data = {
                "incident_type": DiplomaticIncidentType.TRADE_DISPUTE if sanction_type == SanctionType.TRADE_EMBARGO else DiplomaticIncidentType.OTHER,
                "perpetrator_id": imposer_id,
                "victim_id": target_id,
                "description": f"Diplomatic incident due to sanction: {description}",
                "evidence": {"sanction_id": str(sanction.id), "justification": justification},
                "severity": DiplomaticIncidentSeverity.MAJOR if severity >= 75 else DiplomaticIncidentSeverity.MODERATE,
                "tension_impact": tension_change,
                "public": is_public,
                "witnessed_by": supporting_factions
            }
            
            self.create_diplomatic_incident(**incident_data)
        
        return sanction
    
    def get_sanction(self, sanction_id: UUID) -> Optional[Sanction]:
        """
        Get a sanction by ID.
        
        Args:
            sanction_id: ID of the sanction to retrieve
            
        Returns:
            The sanction if found, None otherwise
        """
        return self.repository.get_sanction(sanction_id)
    
    def update_sanction(
        self,
        sanction_id: UUID,
        status: Optional[SanctionStatus] = None,
        end_date: Optional[datetime] = None,
        lifted_date: Optional[datetime] = None,
        conditions_for_lifting: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None,
        enforcement_measures: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None,
        supporting_factions: Optional[List[UUID]] = None,
        opposing_factions: Optional[List[UUID]] = None
    ) -> Optional[Sanction]:
        """
        Update a diplomatic sanction.
        
        Args:
            sanction_id: ID of the sanction to update
            status: New status of the sanction
            end_date: New end date for the sanction
            lifted_date: When the sanction was lifted (if applicable)
            conditions_for_lifting: New conditions for lifting the sanction
            enforcement_measures: New enforcement measures
            supporting_factions: Updated list of supporting factions
            opposing_factions: Updated list of opposing factions
            
        Returns:
            The updated sanction if found, None otherwise
        """
        sanction = self.repository.get_sanction(sanction_id)
        if not sanction:
            return None
        
        current_status = sanction.status
        
        updates = {}
        if status is not None:
            updates["status"] = status
        if end_date is not None:
            updates["end_date"] = end_date
        if lifted_date is not None:
            updates["lifted_date"] = lifted_date
        if conditions_for_lifting is not None:
            updates["conditions_for_lifting"] = conditions_for_lifting
        if enforcement_measures is not None:
            updates["enforcement_measures"] = enforcement_measures
        if supporting_factions is not None:
            updates["supporting_factions"] = supporting_factions
        if opposing_factions is not None:
            updates["opposing_factions"] = opposing_factions
        
        if not updates:
            return sanction
        
        # Update the sanction
        updated_sanction = self.repository.update_sanction(sanction_id, updates)
        
        # If the status changed to LIFTED, create an event and reduce tension
        if status == SanctionStatus.LIFTED and current_status != SanctionStatus.LIFTED:
            # Create a diplomatic event for the lifting
            event_data = {
                "event_type": DiplomaticEventType.OTHER,
                "factions": [sanction.imposer_id, sanction.target_id] + sanction.supporting_factions + sanction.opposing_factions,
                "description": f"Sanction lifted: {sanction.description}",
                "severity": sanction.severity // 2,
                "public": sanction.is_public,
                "metadata": {
                    "sanction_id": str(sanction.id),
                    "sanction_type": sanction.sanction_type.value,
                    "imposer_id": str(sanction.imposer_id),
                    "target_id": str(sanction.target_id),
                    "lifted_date": lifted_date.isoformat() if lifted_date else datetime.utcnow().isoformat()
                },
                "tension_change": {
                    str(sanction.target_id): -sanction.severity // 3  # Reduce tension somewhat when lifting sanctions
                }
            }
            
            self.repository.create_event(DiplomaticEvent(**event_data))
            
            # Update tension between the factions
            self.tension_service.update_tension(
                faction_a_id=sanction.imposer_id,
                faction_b_id=sanction.target_id,
                change=-sanction.severity // 3,
                reason=f"Sanction lifted: {sanction.sanction_type.value}"
            )
        
        return updated_sanction
    
    def lift_sanction(
        self,
        sanction_id: UUID,
        reason: str = "Sanction conditions met"
    ) -> Optional[Sanction]:
        """
        Lift a diplomatic sanction.
        
        Args:
            sanction_id: ID of the sanction to lift
            reason: Reason for lifting the sanction
            
        Returns:
            The updated sanction if found, None otherwise
        """
        sanction = self.repository.get_sanction(sanction_id)
        if not sanction:
            return None
        
        if sanction.status == SanctionStatus.LIFTED:
            return sanction  # Already lifted
        
        updates = {
            "status": SanctionStatus.LIFTED,
            "lifted_date": datetime.utcnow()
        }
        
        # Update the sanction
        return self.update_sanction(sanction_id, **updates)
    
    def list_sanctions(
        self,
        imposer_id: Optional[UUID] = None,
        target_id: Optional[UUID] = None,
        sanction_type: Optional[SanctionType] = None,
        status: Optional[SanctionStatus] = None,
        active_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Sanction]:
        """
        List diplomatic sanctions with optional filtering.
        
        Args:
            imposer_id: Filter by faction imposing the sanction
            target_id: Filter by faction targeted by the sanction
            sanction_type: Filter by type of sanction
            status: Filter by sanction status
            active_only: Only include active sanctions
            limit: Maximum number of sanctions to return
            offset: Number of sanctions to skip
            
        Returns:
            List of sanctions matching the criteria
        """
        return self.repository.list_sanctions(
            imposer_id=imposer_id,
            target_id=target_id,
            sanction_type=sanction_type,
            status=status,
            active_only=active_only,
            limit=limit,
            offset=offset
        )
    
    def record_sanction_violation(
        self,
        sanction_id: UUID,
        description: str,
        evidence: Dict[str, Union[str, int, bool, Dict, List]],
        reported_by: UUID,
        severity: int = 50
    ) -> Optional[Sanction]:
        """
        Record a violation of a sanction.
        
        Args:
            sanction_id: ID of the sanction that was violated
            description: Description of how the sanction was violated
            evidence: Evidence supporting the violation claim
            reported_by: ID of the faction reporting the violation
            severity: Severity of the violation (0-100)
            
        Returns:
            The updated sanction if found, None otherwise
        """
        sanction = self.repository.get_sanction(sanction_id)
        if not sanction:
            return None
        
        violation = {
            "violation_date": datetime.utcnow().isoformat(),
            "description": description,
            "evidence": evidence,
            "reported_by": str(reported_by),
            "severity": severity
        }
        
        # Record the violation
        updated_sanction = self.repository.record_sanction_violation(sanction_id, violation)
        
        if updated_sanction:
            # Create a diplomatic incident for the violation
            incident_data = {
                "incident_type": DiplomaticIncidentType.REFUSED_DEMAND,
                "perpetrator_id": sanction.target_id,
                "victim_id": sanction.imposer_id,
                "description": f"Sanction violation: {description}",
                "evidence": {
                    "sanction_id": str(sanction_id),
                    "sanction_type": sanction.sanction_type.value,
                    "violation": violation
                },
                "severity": DiplomaticIncidentSeverity.MAJOR if severity >= 75 else DiplomaticIncidentSeverity.MODERATE,
                "tension_impact": severity // 2,
                "public": sanction.is_public,
                "witnessed_by": sanction.supporting_factions
            }
            
            self.create_diplomatic_incident(**incident_data)
            
            # Update tension between the factions
            self.tension_service.update_tension(
                faction_a_id=sanction.imposer_id,
                faction_b_id=sanction.target_id,
                change=severity // 2,
                reason=f"Sanction violation: {sanction.sanction_type.value}"
            )
        
        return updated_sanction
    
    def check_expired_sanctions(self) -> List[Sanction]:
        """
        Check for and update expired sanctions.
        
        Returns:
            List of sanctions that were marked as expired
        """
        now = datetime.utcnow()
        active_sanctions = self.list_sanctions(status=SanctionStatus.ACTIVE)
        expired_sanctions = []
        
        for sanction in active_sanctions:
            if sanction.end_date and sanction.end_date < now:
                # Mark as expired
                updated = self.repository.update_sanction(
                    sanction_id=sanction.id,
                    updates={"status": SanctionStatus.EXPIRED}
                )
                
                if updated:
                    # Create an expiration event
                    event_data = {
                        "event_type": DiplomaticEventType.OTHER,
                        "factions": [sanction.imposer_id, sanction.target_id] + sanction.supporting_factions + sanction.opposing_factions,
                        "description": f"Sanction expired: {sanction.description}",
                        "severity": sanction.severity // 3,
                        "public": sanction.is_public,
                        "metadata": {
                            "sanction_id": str(sanction.id),
                            "sanction_type": sanction.sanction_type.value,
                            "imposer_id": str(sanction.imposer_id),
                            "target_id": str(sanction.target_id),
                            "end_date": sanction.end_date.isoformat()
                        },
                        "tension_change": {
                            str(sanction.target_id): -sanction.severity // 4  # Reduce tension slightly when sanctions expire
                        }
                    }
                    
                    self.repository.create_event(DiplomaticEvent(**event_data))
                    
                    # Update tension between the factions
                    self.tension_service.update_tension(
                        faction_a_id=sanction.imposer_id,
                        faction_b_id=sanction.target_id,
                        change=-sanction.severity // 4,
                        reason=f"Sanction expired: {sanction.sanction_type.value}"
                    )
                    
                    expired_sanctions.append(updated)
        
        return expired_sanctions 