"""
Diplomatic Event Publisher

This module provides event publishing for diplomatic operations to integrate
with the broader event system while avoiding circular imports. It uses the
infrastructure event system to broadcast diplomatic events to other systems.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass, asdict

# Safe event system imports
try:
    from backend.infrastructure.events import get_event_bus, EventBase
    HAS_EVENT_SYSTEM = True
except ImportError:
    # Fallback for development environments
    HAS_EVENT_SYSTEM = False
    get_event_bus = None
    EventBase = None

logger = logging.getLogger(__name__)


@dataclass
class DiplomaticEventData:
    """Base class for diplomatic event data"""
    event_type: str
    timestamp: str
    source_system: str = "diplomacy"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event publishing"""
        return asdict(self)


@dataclass
class TensionChangeEventData(DiplomaticEventData):
    """Event data for faction tension changes"""
    faction_a_id: str
    faction_b_id: str
    old_tension: float
    new_tension: float
    reason: Optional[str] = None
    
    def __post_init__(self):
        self.event_type = "diplomacy.tension.changed"


@dataclass
class StatusChangeEventData(DiplomaticEventData):
    """Event data for diplomatic status changes"""
    faction_a_id: str
    faction_b_id: str
    old_status: str
    new_status: str
    
    def __post_init__(self):
        self.event_type = "diplomacy.status.changed"


@dataclass
class TreatyEventData(DiplomaticEventData):
    """Event data for treaty operations"""
    treaty_id: str
    treaty_name: str
    treaty_type: str
    parties: List[str]
    action: str  # "created", "signed", "expired", "violated"
    
    def __post_init__(self):
        self.event_type = f"diplomacy.treaty.{self.action}"


@dataclass
class NegotiationEventData(DiplomaticEventData):
    """Event data for negotiation operations"""
    negotiation_id: str
    parties: List[str]
    initiator_id: str
    action: str  # "started", "offer_made", "offer_accepted", "offer_rejected", "concluded"
    treaty_type: Optional[str] = None
    
    def __post_init__(self):
        self.event_type = f"diplomacy.negotiation.{self.action}"


@dataclass
class IncidentEventData(DiplomaticEventData):
    """Event data for diplomatic incidents"""
    incident_id: str
    incident_type: str
    perpetrator_id: str
    victim_id: str
    severity: str
    public: bool
    action: str  # "created", "resolved", "escalated"
    
    def __post_init__(self):
        self.event_type = f"diplomacy.incident.{self.action}"


@dataclass
class UltimatumEventData(DiplomaticEventData):
    """Event data for ultimatum operations"""
    ultimatum_id: str
    issuer_id: str
    recipient_id: str
    deadline: str
    action: str  # "issued", "accepted", "rejected", "expired"
    
    def __post_init__(self):
        self.event_type = f"diplomacy.ultimatum.{self.action}"


@dataclass
class SanctionEventData(DiplomaticEventData):
    """Event data for sanction operations"""
    sanction_id: str
    imposer_id: str
    target_id: str
    sanction_type: str
    action: str  # "imposed", "lifted", "violated"
    
    def __post_init__(self):
        self.event_type = f"diplomacy.sanction.{self.action}"


@dataclass
class ViolationEventData(DiplomaticEventData):
    """Event data for treaty violations"""
    violation_id: str
    treaty_id: str
    violator_id: str
    violation_type: str
    severity: int
    action: str  # "reported", "acknowledged", "resolved"
    
    def __post_init__(self):
        self.event_type = f"diplomacy.violation.{self.action}"


class DiplomaticEventPublisher:
    """
    Publisher for diplomatic events that integrates with the infrastructure event system.
    
    This class handles publishing of all diplomatic events while managing the 
    complex event system integration and avoiding circular import issues.
    """
    
    def __init__(self):
        """Initialize the diplomatic event publisher."""
        self.enabled = HAS_EVENT_SYSTEM
        self._event_bus = None
        
        if self.enabled:
            try:
                self._event_bus = get_event_bus()
                logger.info("Diplomatic event publisher initialized with event system")
            except Exception as e:
                logger.warning(f"Failed to initialize event system: {e}")
                self.enabled = False
        else:
            logger.warning("Event system not available, diplomatic events will not be published")
    
    def _publish(self, event_data: DiplomaticEventData) -> bool:
        """
        Internal method to publish event data.
        
        Args:
            event_data: Event data to publish
            
        Returns:
            bool: True if event was published successfully
        """
        if not self.enabled or not self._event_bus:
            logger.debug(f"Event publishing disabled, skipping: {event_data.event_type}")
            return False
        
        try:
            # Convert event data to dictionary
            event_dict = event_data.to_dict()
            
            # Publish event using the event bus
            self._event_bus.publish(event_data.event_type, event_dict)
            
            logger.debug(f"Published diplomatic event: {event_data.event_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish diplomatic event {event_data.event_type}: {e}")
            return False
    
    # ===========================
    # Tension and Relationship Events
    # ===========================
    
    def publish_tension_changed(
        self,
        faction_a_id: UUID,
        faction_b_id: UUID,
        old_tension: float,
        new_tension: float,
        reason: Optional[str] = None
    ) -> bool:
        """Publish faction tension change event."""
        event_data = TensionChangeEventData(
            faction_a_id=str(faction_a_id),
            faction_b_id=str(faction_b_id),
            old_tension=old_tension,
            new_tension=new_tension,
            reason=reason,
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_status_changed(
        self,
        faction_a_id: UUID,
        faction_b_id: UUID,
        old_status: str,
        new_status: str
    ) -> bool:
        """Publish diplomatic status change event."""
        event_data = StatusChangeEventData(
            faction_a_id=str(faction_a_id),
            faction_b_id=str(faction_b_id),
            old_status=old_status,
            new_status=new_status,
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    # ===========================
    # Treaty Events
    # ===========================
    
    def publish_treaty_created(
        self,
        treaty_id: UUID,
        treaty_name: str,
        treaty_type: str,
        parties: List[UUID]
    ) -> bool:
        """Publish treaty creation event."""
        event_data = TreatyEventData(
            treaty_id=str(treaty_id),
            treaty_name=treaty_name,
            treaty_type=treaty_type,
            parties=[str(p) for p in parties],
            action="created",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_treaty_signed(
        self,
        treaty_id: UUID,
        treaty_name: str,
        treaty_type: str,
        parties: List[UUID]
    ) -> bool:
        """Publish treaty signing event."""
        event_data = TreatyEventData(
            treaty_id=str(treaty_id),
            treaty_name=treaty_name,
            treaty_type=treaty_type,
            parties=[str(p) for p in parties],
            action="signed",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_treaty_expired(
        self,
        treaty_id: UUID,
        treaty_name: str,
        treaty_type: str,
        parties: List[UUID]
    ) -> bool:
        """Publish treaty expiration event."""
        event_data = TreatyEventData(
            treaty_id=str(treaty_id),
            treaty_name=treaty_name,
            treaty_type=treaty_type,
            parties=[str(p) for p in parties],
            action="expired",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    # ===========================
    # Negotiation Events
    # ===========================
    
    def publish_negotiation_started(
        self,
        negotiation_id: UUID,
        parties: List[UUID],
        initiator_id: UUID,
        treaty_type: Optional[str] = None
    ) -> bool:
        """Publish negotiation start event."""
        event_data = NegotiationEventData(
            negotiation_id=str(negotiation_id),
            parties=[str(p) for p in parties],
            initiator_id=str(initiator_id),
            action="started",
            treaty_type=treaty_type,
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_offer_made(
        self,
        negotiation_id: UUID,
        parties: List[UUID],
        initiator_id: UUID
    ) -> bool:
        """Publish negotiation offer made event."""
        event_data = NegotiationEventData(
            negotiation_id=str(negotiation_id),
            parties=[str(p) for p in parties],
            initiator_id=str(initiator_id),
            action="offer_made",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_offer_accepted(
        self,
        negotiation_id: UUID,
        parties: List[UUID],
        initiator_id: UUID
    ) -> bool:
        """Publish negotiation offer accepted event."""
        event_data = NegotiationEventData(
            negotiation_id=str(negotiation_id),
            parties=[str(p) for p in parties],
            initiator_id=str(initiator_id),
            action="offer_accepted",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_offer_rejected(
        self,
        negotiation_id: UUID,
        parties: List[UUID],
        initiator_id: UUID
    ) -> bool:
        """Publish negotiation offer rejected event."""
        event_data = NegotiationEventData(
            negotiation_id=str(negotiation_id),
            parties=[str(p) for p in parties],
            initiator_id=str(initiator_id),
            action="offer_rejected",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    # ===========================
    # Incident Events
    # ===========================
    
    def publish_incident_created(
        self,
        incident_id: UUID,
        incident_type: str,
        perpetrator_id: UUID,
        victim_id: UUID,
        severity: str,
        public: bool
    ) -> bool:
        """Publish diplomatic incident creation event."""
        event_data = IncidentEventData(
            incident_id=str(incident_id),
            incident_type=incident_type,
            perpetrator_id=str(perpetrator_id),
            victim_id=str(victim_id),
            severity=severity,
            public=public,
            action="created",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_incident_resolved(
        self,
        incident_id: UUID,
        incident_type: str,
        perpetrator_id: UUID,
        victim_id: UUID,
        severity: str,
        public: bool
    ) -> bool:
        """Publish diplomatic incident resolution event."""
        event_data = IncidentEventData(
            incident_id=str(incident_id),
            incident_type=incident_type,
            perpetrator_id=str(perpetrator_id),
            victim_id=str(victim_id),
            severity=severity,
            public=public,
            action="resolved",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    # ===========================
    # Ultimatum Events
    # ===========================
    
    def publish_ultimatum_issued(
        self,
        ultimatum_id: UUID,
        issuer_id: UUID,
        recipient_id: UUID,
        deadline: datetime
    ) -> bool:
        """Publish ultimatum issued event."""
        event_data = UltimatumEventData(
            ultimatum_id=str(ultimatum_id),
            issuer_id=str(issuer_id),
            recipient_id=str(recipient_id),
            deadline=deadline.isoformat(),
            action="issued",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_ultimatum_accepted(
        self,
        ultimatum_id: UUID,
        issuer_id: UUID,
        recipient_id: UUID,
        deadline: datetime
    ) -> bool:
        """Publish ultimatum accepted event."""
        event_data = UltimatumEventData(
            ultimatum_id=str(ultimatum_id),
            issuer_id=str(issuer_id),
            recipient_id=str(recipient_id),
            deadline=deadline.isoformat(),
            action="accepted",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_ultimatum_rejected(
        self,
        ultimatum_id: UUID,
        issuer_id: UUID,
        recipient_id: UUID,
        deadline: datetime
    ) -> bool:
        """Publish ultimatum rejected event."""
        event_data = UltimatumEventData(
            ultimatum_id=str(ultimatum_id),
            issuer_id=str(issuer_id),
            recipient_id=str(recipient_id),
            deadline=deadline.isoformat(),
            action="rejected",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    # ===========================
    # Sanction Events
    # ===========================
    
    def publish_sanction_imposed(
        self,
        sanction_id: UUID,
        imposer_id: UUID,
        target_id: UUID,
        sanction_type: str
    ) -> bool:
        """Publish sanction imposed event."""
        event_data = SanctionEventData(
            sanction_id=str(sanction_id),
            imposer_id=str(imposer_id),
            target_id=str(target_id),
            sanction_type=sanction_type,
            action="imposed",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_sanction_lifted(
        self,
        sanction_id: UUID,
        imposer_id: UUID,
        target_id: UUID,
        sanction_type: str
    ) -> bool:
        """Publish sanction lifted event."""
        event_data = SanctionEventData(
            sanction_id=str(sanction_id),
            imposer_id=str(imposer_id),
            target_id=str(target_id),
            sanction_type=sanction_type,
            action="lifted",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    # ===========================
    # Violation Events
    # ===========================
    
    def publish_violation_reported(
        self,
        violation_id: UUID,
        treaty_id: UUID,
        violator_id: UUID,
        violation_type: str,
        severity: int
    ) -> bool:
        """Publish treaty violation reported event."""
        event_data = ViolationEventData(
            violation_id=str(violation_id),
            treaty_id=str(treaty_id),
            violator_id=str(violator_id),
            violation_type=violation_type,
            severity=severity,
            action="reported",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    def publish_violation_resolved(
        self,
        violation_id: UUID,
        treaty_id: UUID,
        violator_id: UUID,
        violation_type: str,
        severity: int
    ) -> bool:
        """Publish treaty violation resolved event."""
        event_data = ViolationEventData(
            violation_id=str(violation_id),
            treaty_id=str(treaty_id),
            violator_id=str(violator_id),
            violation_type=violation_type,
            severity=severity,
            action="resolved",
            timestamp=datetime.utcnow().isoformat()
        )
        return self._publish(event_data)
    
    # ===========================
    # Publisher Status and Management
    # ===========================
    
    def get_status(self) -> Dict[str, Any]:
        """Get publisher status information."""
        return {
            "enabled": self.enabled,
            "event_system_available": HAS_EVENT_SYSTEM,
            "event_bus_connected": self._event_bus is not None,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global publisher instance
_diplomatic_event_publisher = None


def get_diplomatic_event_publisher() -> DiplomaticEventPublisher:
    """
    Get or create the global diplomatic event publisher instance.
    
    Returns:
        DiplomaticEventPublisher: Global publisher instance
    """
    global _diplomatic_event_publisher
    if _diplomatic_event_publisher is None:
        _diplomatic_event_publisher = DiplomaticEventPublisher()
    return _diplomatic_event_publisher


# Convenience functions for direct event publishing
def publish_tension_changed(faction_a_id: UUID, faction_b_id: UUID, old_tension: float, new_tension: float, reason: Optional[str] = None) -> bool:
    """Convenience function to publish tension change event."""
    return get_diplomatic_event_publisher().publish_tension_changed(faction_a_id, faction_b_id, old_tension, new_tension, reason)


def publish_status_changed(faction_a_id: UUID, faction_b_id: UUID, old_status: str, new_status: str) -> bool:
    """Convenience function to publish status change event."""
    return get_diplomatic_event_publisher().publish_status_changed(faction_a_id, faction_b_id, old_status, new_status)


def publish_treaty_created(treaty_id: UUID, treaty_name: str, treaty_type: str, parties: List[UUID]) -> bool:
    """Convenience function to publish treaty creation event."""
    return get_diplomatic_event_publisher().publish_treaty_created(treaty_id, treaty_name, treaty_type, parties) 