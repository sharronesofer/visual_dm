"""
Religion Event Publisher

This module provides a centralized event publisher for the religion system.
It publishes events for all religion operations, enabling real-time updates
and cross-system communication.

The publisher follows the pattern established in the NPC system and integrates
with the event dispatcher architecture.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from uuid import UUID
from datetime import datetime

# Try to import the event dispatcher
try:
    from backend.infrastructure.events import EventDispatcher, get_dispatcher
    HAS_EVENT_DISPATCHER = True
except ImportError:
    try:
        from backend.infrastructure.events import EventDispatcher, get_dispatcher
        HAS_EVENT_DISPATCHER = True
    except ImportError:
        HAS_EVENT_DISPATCHER = False
        # Fallback function when event dispatcher is not available
        def get_dispatcher():
            return None

# Import all religion events
from backend.systems.religion.events.religion_events import (
    # Core Religion Events
    ReligionCreatedEvent,
    ReligionUpdatedEvent,
    ReligionDeletedEvent,
    
    # Membership Events
    MembershipCreatedEvent,
    MembershipUpdatedEvent,
    MembershipDeletedEvent,
    ConversionEvent,
    
    # Devotion Events
    DevotionChangedEvent,
    ReligiousRitualEvent,
    
    # Narrative Events
    ReligiousNarrativeEvent,
    SchismEvent,
    
    # Influence Events
    ReligiousInfluenceEvent,
    ReligiousConflictEvent
)

logger = logging.getLogger(__name__)


class ReligionEventPublisher:
    """Centralized event publisher for religion system events."""
    
    def __init__(self):
        """Initialize the event publisher."""
        self.enabled = HAS_EVENT_DISPATCHER
        if self.enabled:
            self.dispatcher = get_dispatcher()
        else:
            self.dispatcher = None
            
    def _publish(self, event) -> bool:
        """Internal method to publish events."""
        if not self.enabled or not self.dispatcher:
            logger.debug(f"Event publishing disabled, skipping: {event.event_type}")
            return False
            
        try:
            self.dispatcher.publish_sync(event)
            logger.debug(f"Published religion event: {event.event_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish religion event {event.event_type}: {e}")
            return False
    
    # Core Religion Events
    def publish_religion_created(self, religion_id: UUID, name: str, religion_type: str,
                                creator_id: Optional[UUID] = None, region_id: Optional[str] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Publish religion created event."""
        event = ReligionCreatedEvent(
            religion_id=religion_id,
            name=name,
            religion_type=religion_type,
            creator_id=creator_id,
            region_id=region_id,
            metadata=metadata
        )
        return self._publish(event)
    
    def publish_religion_updated(self, religion_id: UUID, changes: Dict[str, Any],
                                old_values: Optional[Dict[str, Any]] = None, updated_by: Optional[UUID] = None) -> bool:
        """Publish religion updated event."""
        event = ReligionUpdatedEvent(
            religion_id=religion_id,
            changes=changes,
            old_values=old_values,
            updated_by=updated_by
        )
        return self._publish(event)
    
    def publish_religion_deleted(self, religion_id: UUID, name: str, deletion_reason: Optional[str] = None,
                                deleted_by: Optional[UUID] = None) -> bool:
        """Publish religion deleted event."""
        event = ReligionDeletedEvent(
            religion_id=religion_id,
            name=name,
            deletion_reason=deletion_reason,
            deleted_by=deleted_by
        )
        return self._publish(event)
    
    # Membership Events
    def publish_membership_created(self, membership_id: UUID, religion_id: UUID, entity_id: UUID,
                                  entity_type: str, role: str = "follower", devotion_level: float = 0.5) -> bool:
        """Publish membership created event."""
        event = MembershipCreatedEvent(
            membership_id=membership_id,
            religion_id=religion_id,
            entity_id=entity_id,
            entity_type=entity_type,
            role=role,
            devotion_level=devotion_level
        )
        return self._publish(event)
    
    def publish_membership_updated(self, membership_id: UUID, religion_id: UUID, entity_id: UUID,
                                  changes: Dict[str, Any], old_values: Optional[Dict[str, Any]] = None) -> bool:
        """Publish membership updated event."""
        event = MembershipUpdatedEvent(
            membership_id=membership_id,
            religion_id=religion_id,
            entity_id=entity_id,
            changes=changes,
            old_values=old_values
        )
        return self._publish(event)
    
    def publish_membership_deleted(self, membership_id: UUID, religion_id: UUID, entity_id: UUID,
                                  reason: Optional[str] = None) -> bool:
        """Publish membership deleted event."""
        event = MembershipDeletedEvent(
            membership_id=membership_id,
            religion_id=religion_id,
            entity_id=entity_id,
            reason=reason
        )
        return self._publish(event)
    
    def publish_conversion(self, entity_id: UUID, entity_type: str, from_religion_id: Optional[UUID],
                          to_religion_id: UUID, conversion_reason: Optional[str] = None,
                          conversion_strength: float = 1.0) -> bool:
        """Publish conversion event."""
        event = ConversionEvent(
            entity_id=entity_id,
            entity_type=entity_type,
            from_religion_id=from_religion_id,
            to_religion_id=to_religion_id,
            conversion_reason=conversion_reason,
            conversion_strength=conversion_strength
        )
        return self._publish(event)
    
    # Devotion Events
    def publish_devotion_changed(self, religion_id: UUID, entity_id: UUID, old_devotion: float,
                                new_devotion: float, change_reason: Optional[str] = None) -> bool:
        """Publish devotion changed event."""
        event = DevotionChangedEvent(
            religion_id=religion_id,
            entity_id=entity_id,
            old_devotion=old_devotion,
            new_devotion=new_devotion,
            change_reason=change_reason
        )
        return self._publish(event)
    
    def publish_religious_ritual(self, ritual_id: UUID, religion_id: UUID, entity_id: UUID,
                                ritual_type: str, ritual_name: str, location: Optional[str] = None,
                                participants: Optional[List[UUID]] = None, devotion_effect: Optional[float] = None) -> bool:
        """Publish religious ritual event."""
        event = ReligiousRitualEvent(
            ritual_id=ritual_id,
            religion_id=religion_id,
            entity_id=entity_id,
            ritual_type=ritual_type,
            ritual_name=ritual_name,
            location=location,
            participants=participants,
            devotion_effect=devotion_effect
        )
        return self._publish(event)
    
    # Narrative Events
    def publish_religious_narrative(self, narrative_id: UUID, religion_id: UUID, narrative_type: str,
                                   title: str, content: str, entities_involved: Optional[List[UUID]] = None,
                                   location: Optional[str] = None, impact_level: str = "minor") -> bool:
        """Publish religious narrative event."""
        event = ReligiousNarrativeEvent(
            narrative_id=narrative_id,
            religion_id=religion_id,
            narrative_type=narrative_type,
            title=title,
            content=content,
            entities_involved=entities_involved,
            location=location,
            impact_level=impact_level
        )
        return self._publish(event)
    
    def publish_schism(self, schism_id: UUID, parent_religion_id: UUID, new_religion_id: Optional[UUID] = None,
                      schism_type: str = "doctrinal", cause: str = "unknown", leader_id: Optional[UUID] = None,
                      followers_affected: Optional[List[UUID]] = None) -> bool:
        """Publish schism event."""
        event = SchismEvent(
            schism_id=schism_id,
            parent_religion_id=parent_religion_id,
            new_religion_id=new_religion_id,
            schism_type=schism_type,
            cause=cause,
            leader_id=leader_id,
            followers_affected=followers_affected
        )
        return self._publish(event)
    
    # Influence Events
    def publish_religious_influence(self, religion_id: UUID, influence_type: str, target_type: str,
                                   target_id: Union[UUID, str], influence_strength: float,
                                   influence_change: float, cause: Optional[str] = None) -> bool:
        """Publish religious influence event."""
        event = ReligiousInfluenceEvent(
            religion_id=religion_id,
            influence_type=influence_type,
            target_type=target_type,
            target_id=target_id,
            influence_strength=influence_strength,
            influence_change=influence_change,
            cause=cause
        )
        return self._publish(event)
    
    def publish_religious_conflict(self, conflict_id: UUID, religion_ids: List[UUID], conflict_type: str,
                                  cause: str, location: Optional[str] = None, intensity: float = 1.0,
                                  resolution: Optional[str] = None) -> bool:
        """Publish religious conflict event."""
        event = ReligiousConflictEvent(
            conflict_id=conflict_id,
            religion_ids=religion_ids,
            conflict_type=conflict_type,
            cause=cause,
            location=location,
            intensity=intensity,
            resolution=resolution
        )
        return self._publish(event)


# Global instance for easy access
_religion_event_publisher = None

def get_religion_event_publisher() -> ReligionEventPublisher:
    """Get the global religion event publisher instance."""
    global _religion_event_publisher
    if _religion_event_publisher is None:
        _religion_event_publisher = ReligionEventPublisher()
    return _religion_event_publisher


# Convenience functions for direct publishing
def publish_religion_created(*args, **kwargs) -> bool:
    """Convenience function to publish religion created event."""
    return get_religion_event_publisher().publish_religion_created(*args, **kwargs)

def publish_religion_updated(*args, **kwargs) -> bool:
    """Convenience function to publish religion updated event."""
    return get_religion_event_publisher().publish_religion_updated(*args, **kwargs)

def publish_religion_deleted(*args, **kwargs) -> bool:
    """Convenience function to publish religion deleted event."""
    return get_religion_event_publisher().publish_religion_deleted(*args, **kwargs)

def publish_membership_created(*args, **kwargs) -> bool:
    """Convenience function to publish membership created event."""
    return get_religion_event_publisher().publish_membership_created(*args, **kwargs)

def publish_membership_updated(*args, **kwargs) -> bool:
    """Convenience function to publish membership updated event."""
    return get_religion_event_publisher().publish_membership_updated(*args, **kwargs)

def publish_membership_deleted(*args, **kwargs) -> bool:
    """Convenience function to publish membership deleted event."""
    return get_religion_event_publisher().publish_membership_deleted(*args, **kwargs)

def publish_conversion(*args, **kwargs) -> bool:
    """Convenience function to publish conversion event."""
    return get_religion_event_publisher().publish_conversion(*args, **kwargs)

def publish_devotion_changed(*args, **kwargs) -> bool:
    """Convenience function to publish devotion changed event."""
    return get_religion_event_publisher().publish_devotion_changed(*args, **kwargs)

def publish_religious_ritual(*args, **kwargs) -> bool:
    """Convenience function to publish religious ritual event."""
    return get_religion_event_publisher().publish_religious_ritual(*args, **kwargs)

def publish_religious_narrative(*args, **kwargs) -> bool:
    """Convenience function to publish religious narrative event."""
    return get_religion_event_publisher().publish_religious_narrative(*args, **kwargs)

def publish_schism(*args, **kwargs) -> bool:
    """Convenience function to publish schism event."""
    return get_religion_event_publisher().publish_schism(*args, **kwargs)

def publish_religious_influence(*args, **kwargs) -> bool:
    """Convenience function to publish religious influence event."""
    return get_religion_event_publisher().publish_religious_influence(*args, **kwargs)

def publish_religious_conflict(*args, **kwargs) -> bool:
    """Convenience function to publish religious conflict event."""
    return get_religion_event_publisher().publish_religious_conflict(*args, **kwargs)

logger.info("Religion event publisher module loaded successfully") 