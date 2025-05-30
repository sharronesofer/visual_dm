"""
Narrative service for the religion system.

This module provides services for narrative hooks, event generation,
and integration with the event system for religion-related events.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import Religion, ReligionMembership, ReligionType
from .utils import generate_conversion_narrative, generate_religion_event

# Setup logging
logger = logging.getLogger(__name__)

# Try to import the event dispatcher if available
try:
    from backend.app.core.events.event_dispatcher import EventDispatcher, EventBase
    HAS_EVENT_DISPATCHER = True
except ImportError:
    HAS_EVENT_DISPATCHER = False
    logger.warning("EventDispatcher not available, narrative events will not be published")


class ReligionEventBase(EventBase):
    """Base class for all religion events."""
    pass


class ReligionNarrativeEvent(ReligionEventBase):
    """Event published when a religion-related narrative event occurs."""
    religion_id: str
    event_type: str
    entity_id: Optional[str] = None
    event_data: Dict[str, Any] = {}


class ReligionNarrativeService:
    """
    Service for handling religion narrative events and hooks.
    
    Provides methods for generating narrative text, triggering events,
    and integrating with the broader event system.
    """
    
    def __init__(self):
        """Initialize the narrative service."""
        self.event_dispatcher = None
        if HAS_EVENT_DISPATCHER:
            self.event_dispatcher = EventDispatcher.get_instance()
    
    def trigger_narrative_hook(
        self, 
        entity_id: str, 
        religion: Religion, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> None:
        """
        Trigger a narrative event for a religion.
        
        Args:
            entity_id: ID of the entity involved
            religion: Religion object
            event_type: Type of event (conversion, promotion, etc.)
            event_data: Additional data for the event
        """
        logger.info(
            f"Religion narrative event: {event_type} for entity {entity_id} "
            f"and religion {religion.name} ({religion.id})"
        )
        
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = datetime.utcnow().isoformat()
            
        # Generate event structure
        event = generate_religion_event(religion, event_type, {
            "entity_id": entity_id,
            **event_data
        })
        
        # Publish event if dispatcher is available
        if self.event_dispatcher:
            self.event_dispatcher.publish_sync(
                ReligionNarrativeEvent(
                    event_type="religion.narrative",
                    religion_id=religion.id,
                    event_type=event_type,
                    entity_id=entity_id,
                    event_data=event_data
                )
            )
    
    def generate_conversion_narrative(
        self, 
        entity_name: str, 
        from_religion: Optional[Religion], 
        to_religion: Religion
    ) -> str:
        """
        Generate narrative text for a conversion event.
        
        Args:
            entity_name: Name of the entity converting
            from_religion: Previous religion (None if first conversion)
            to_religion: New religion being converted to
            
        Returns:
            Narrative text describing the conversion
        """
        return generate_conversion_narrative(entity_name, from_religion, to_religion)
    
    def get_religion_summary(self, religion: Religion) -> Dict[str, Any]:
        """
        Generate a summary of a religion for narrative context.
        
        Args:
            religion: Religion to summarize
            
        Returns:
            Dictionary with religion summary
        """
        # Create a rich summary with narrative elements
        summary = {
            "id": religion.id,
            "name": religion.name,
            "description": religion.description,
            "type": religion.get_type_string(),
            "tenets": religion.tenets,
            "holy_places": religion.holy_places,
            "sacred_texts": religion.sacred_texts,
        }
        
        # Add narrative elements based on religion type
        if religion.type == ReligionType.POLYTHEISTIC:
            summary["narrative_elements"] = {
                "worship_style": "Pantheon-based with multiple deities",
                "ceremonies": "Often elaborate and communal",
                "hierarchy": "Variable, often with specialized priests for each deity"
            }
        elif religion.type == ReligionType.MONOTHEISTIC:
            summary["narrative_elements"] = {
                "worship_style": "Centered on a single divine entity",
                "ceremonies": "Structured and formal",
                "hierarchy": "Often hierarchical with central authority"
            }
        elif religion.type == ReligionType.ANIMISTIC:
            summary["narrative_elements"] = {
                "worship_style": "Reverence for spirits in nature",
                "ceremonies": "Nature-based and seasonal",
                "hierarchy": "Shamans or spiritual guides rather than strict hierarchy"
            }
        elif religion.type == ReligionType.ANCESTOR:
            summary["narrative_elements"] = {
                "worship_style": "Veneration of lineage and predecessors",
                "ceremonies": "Family-centered, often at shrines or graves",
                "hierarchy": "Often based on age and family position"
            }
        elif religion.type == ReligionType.CULT:
            summary["narrative_elements"] = {
                "worship_style": "Secretive and often intensive",
                "ceremonies": "Hidden rituals, possibly requiring sacrifice",
                "hierarchy": "Strong leader-follower dynamic"
            }
        elif religion.type == ReligionType.SYNCRETIC:
            summary["narrative_elements"] = {
                "worship_style": "Blended practices from multiple traditions",
                "ceremonies": "Diverse and adaptable",
                "hierarchy": "Often loose and flexible"
            }
        
        return summary


# Singleton instance
_narrative_service_instance = None

def get_narrative_service() -> ReligionNarrativeService:
    """Get the singleton instance of the ReligionNarrativeService."""
    global _narrative_service_instance
    if _narrative_service_instance is None:
        _narrative_service_instance = ReligionNarrativeService()
    return _narrative_service_instance 