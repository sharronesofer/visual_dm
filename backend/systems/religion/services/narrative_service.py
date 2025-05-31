"""
Narrative service for the religion system.

This module provides services for narrative hooks, event generation,
and integration with the event system for religion-related events.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID, uuid4

from backend.systems.religion.models import ReligionModel, ReligionEntity
from backend.systems.religion.utils import generate_conversion_narrative, generate_religion_event

# Setup logging
logger = logging.getLogger(__name__)

# Import proper event dispatcher and religion events
try:
    from backend.infrastructure.events import get_dispatcher
    from backend.systems.religion.events.event_publisher import get_religion_event_publisher
    from backend.systems.religion.events import (
        ReligiousNarrativeEvent,
        ConversionEvent,
        DevotionChangedEvent,
        SchismEvent
    )
    HAS_EVENT_SYSTEM = True
    logger.info("Religion narrative service initialized with full event system integration")
except ImportError as e:
    HAS_EVENT_SYSTEM = False
    logger.warning(f"Event system not fully available for religion narrative service: {e}")

class ReligionNarrativeService:
    """Service for handling religion-related narrative events and story generation"""
    
    def __init__(self):
        """Initialize the narrative service with event integration"""
        self.has_events = HAS_EVENT_SYSTEM
        if self.has_events:
            self.event_publisher = get_religion_event_publisher()
            self.dispatcher = get_dispatcher()
        else:
            self.event_publisher = None
            self.dispatcher = None
            
    def generate_conversion_story(
        self,
        entity_id: UUID,
        entity_type: str,
        from_religion_id: Optional[UUID],
        to_religion_id: UUID,
        conversion_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a narrative story for religious conversion"""
        try:
            # Generate narrative content
            story_content = generate_conversion_narrative(
                entity_id=entity_id,
                from_religion=from_religion_id,
                to_religion=to_religion_id,
                reason=conversion_reason
            )
            
            narrative_id = uuid4()
            story_data = {
                "narrative_id": narrative_id,
                "type": "conversion",
                "entity_id": entity_id,
                "entity_type": entity_type,
                "from_religion_id": from_religion_id,
                "to_religion_id": to_religion_id,
                "content": story_content,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": conversion_reason
            }
            
            # Publish events if event system is available
            if self.has_events and self.event_publisher:
                # Publish conversion event
                self.event_publisher.publish_conversion(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    from_religion_id=from_religion_id,
                    to_religion_id=to_religion_id,
                    conversion_reason=conversion_reason,
                    conversion_strength=1.0
                )
                
                # Publish narrative event
                self.event_publisher.publish_religious_narrative(
                    narrative_id=narrative_id,
                    religion_id=to_religion_id,
                    narrative_type="conversion",
                    title=f"Religious Conversion of {entity_type}",
                    content=story_content,
                    entities_involved=[entity_id],
                    impact_level="medium"
                )
                
                logger.info(f"Published conversion narrative events for {entity_type} {entity_id}")
            
            return story_data
            
        except Exception as e:
            logger.error(f"Error generating conversion story: {str(e)}")
            raise

    def generate_religious_event_story(
        self, 
        religion_id: UUID,
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate narrative story for religious events"""
        try:
            # Generate narrative content
            story_content = generate_religion_event(
                religion_id=religion_id,
                event_type=event_type,
                event_data=event_data
            )
            
            narrative_id = uuid4()
            story_data = {
                "narrative_id": narrative_id,
                "type": event_type,
                "religion_id": religion_id,
                "content": story_content,
                "timestamp": datetime.utcnow().isoformat(),
                "event_data": event_data
            }
            
            # Publish narrative event if event system is available
            if self.has_events and self.event_publisher:
                self.event_publisher.publish_religious_narrative(
                    narrative_id=narrative_id,
                    religion_id=religion_id,
                    narrative_type=event_type,
                    title=f"Religious Event: {event_type.title()}",
                    content=story_content,
                    entities_involved=event_data.get('entities_involved', []),
                    location=event_data.get('location'),
                    impact_level=event_data.get('impact_level', 'minor')
                )
                
                logger.info(f"Published religious event narrative for religion {religion_id}: {event_type}")
            
            return story_data
            
        except Exception as e:
            logger.error(f"Error generating religious event story: {str(e)}")
            raise

    def handle_devotion_change(
        self,
        membership_id: UUID,
        religion_id: UUID,
        entity_id: UUID,
        old_devotion: float,
        new_devotion: float,
        change_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle devotion level changes with narrative and events"""
        try:
            # Create narrative for devotion change
            devotion_delta = new_devotion - old_devotion
            change_type = "increased" if devotion_delta > 0 else "decreased"
            
            narrative_content = f"The devotion of entity {entity_id} has {change_type} "
            narrative_content += f"by {abs(devotion_delta):.2f} points"
            if change_reason:
                narrative_content += f" due to {change_reason}"
            
            narrative_id = uuid4()
            devotion_data = {
                "narrative_id": narrative_id,
                "type": "devotion_change",
                "membership_id": membership_id,
                "religion_id": religion_id,
            "entity_id": entity_id,
                "old_devotion": old_devotion,
                "new_devotion": new_devotion,
                "devotion_delta": devotion_delta,
                "change_reason": change_reason,
                "content": narrative_content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish events if event system is available
            if self.has_events and self.event_publisher:
                # Publish devotion changed event
                self.event_publisher.publish_devotion_changed(
                    membership_id=membership_id,
                    religion_id=religion_id,
                    entity_id=entity_id,
                    old_devotion=old_devotion,
                    new_devotion=new_devotion,
                    change_reason=change_reason
                )
                
                # Publish narrative event
                self.event_publisher.publish_religious_narrative(
                    narrative_id=narrative_id,
                    religion_id=religion_id,
                    narrative_type="devotion_change",
                    title=f"Devotion {change_type.title()}",
                    content=narrative_content,
                    entities_involved=[entity_id],
                    impact_level="minor"
                )
                
                logger.info(f"Published devotion change events for entity {entity_id}")
            
            return devotion_data
            
        except Exception as e:
            logger.error(f"Error handling devotion change: {str(e)}")
            raise

    def handle_religious_schism(
        self,
        parent_religion_id: UUID,
        schism_cause: str,
        leader_id: Optional[UUID] = None,
        followers_affected: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """Handle religious schism events with narrative"""
        try:
            schism_id = uuid4()
            
            # Generate schism narrative
            narrative_content = f"A schism has occurred within the religion due to {schism_cause}."
            if leader_id:
                narrative_content += f" Led by {leader_id}."
            if followers_affected:
                narrative_content += f" Affecting {len(followers_affected)} followers."
            
            narrative_id = uuid4()
            schism_data = {
                "schism_id": schism_id,
                "narrative_id": narrative_id,
                "type": "schism",
                "parent_religion_id": parent_religion_id,
                "cause": schism_cause,
                "leader_id": leader_id,
                "followers_affected": followers_affected,
                "content": narrative_content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish events if event system is available
            if self.has_events and self.event_publisher:
                # Publish schism event
                self.event_publisher.publish_schism(
                    schism_id=schism_id,
                    parent_religion_id=parent_religion_id,
                    schism_type="doctrinal",
                    cause=schism_cause,
                    leader_id=leader_id,
                    followers_affected=followers_affected
                )
                
                # Publish narrative event
                self.event_publisher.publish_religious_narrative(
                    narrative_id=narrative_id,
                    religion_id=parent_religion_id,
                    narrative_type="schism",
                    title="Religious Schism",
                    content=narrative_content,
                    entities_involved=[leader_id] if leader_id else [],
                    impact_level="major"
                )
                
                logger.info(f"Published schism events for religion {parent_religion_id}")
            
            return schism_data
            
        except Exception as e:
            logger.error(f"Error handling religious schism: {str(e)}")
            raise

    def subscribe_to_events(self):
        """Subscribe to relevant events from other systems"""
        if not self.has_events or not self.dispatcher:
            logger.warning("Cannot subscribe to events - event system not available")
            return
            
        try:
            # Subscribe to character events that might affect religion
            from backend.infrastructure.events import CharacterEvent
            self.dispatcher.subscribe(CharacterEvent, self._handle_character_event)
            
            # Subscribe to faction events that might affect religion
            from backend.infrastructure.events import FactionEvent
            self.dispatcher.subscribe(FactionEvent, self._handle_faction_event)
            
            # Subscribe to time events for religious calendar processing
            from backend.infrastructure.events import TimeEvent
            self.dispatcher.subscribe(TimeEvent, self._handle_time_event)
            
            logger.info("Religion narrative service subscribed to cross-system events")
            
        except ImportError as e:
            logger.warning(f"Some event types not available for subscription: {e}")
        except Exception as e:
            logger.error(f"Error subscribing to events: {str(e)}")

    def _handle_character_event(self, event):
        """Handle character events that might affect religious devotion"""
        try:
            # Example: character actions could affect devotion
            logger.debug(f"Religion narrative service received character event: {event.event_type}")
            # Add logic here to handle character-religion interactions
        except Exception as e:
            logger.error(f"Error handling character event: {str(e)}")

    def _handle_faction_event(self, event):
        """Handle faction events that might affect religious relationships"""
        try:
            # Example: faction conflicts could affect religious alliances
            logger.debug(f"Religion narrative service received faction event: {event.event_type}")
            # Add logic here to handle faction-religion interactions
        except Exception as e:
            logger.error(f"Error handling faction event: {str(e)}")

    def _handle_time_event(self, event):
        """Handle time events for religious calendar processing"""
        try:
            # Example: time passage could trigger religious holidays/events
            logger.debug(f"Religion narrative service received time event: {event.event_type}")
            # Add logic here to handle time-based religious events
        except Exception as e:
            logger.error(f"Error handling time event: {str(e)}")

# Global instance for easy access
_narrative_service = None

def get_religion_narrative_service() -> ReligionNarrativeService:
    """Get the global religion narrative service instance"""
    global _narrative_service
    if _narrative_service is None:
        _narrative_service = ReligionNarrativeService()
        # Subscribe to events on first initialization
        _narrative_service.subscribe_to_events()
    return _narrative_service 