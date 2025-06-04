"""
Religion Event Types and Classes
---------------------------------
This module defines all religion-related events for the Visual DM system.

These events enable cross-system communication and real-time updates for
the religion system, supporting narrative integration and system interconnectivity.
"""

from enum import Enum, auto
from typing import Dict, Any, Optional, List, Union
from uuid import UUID
from datetime import datetime

from backend.infrastructure.events.core.event_base import EventBase

# ============================================================================
# Event Type Enumerations
# ============================================================================

class ReligionEventType(Enum):
    """Core religion lifecycle event types"""
    CREATED = "religion.created"
    UPDATED = "religion.updated"
    DELETED = "religion.deleted"
    STATUS_CHANGED = "religion.status_changed"

class MembershipEventType(Enum):
    """Religion membership event types"""
    CREATED = "membership.created"
    UPDATED = "membership.updated"
    DELETED = "membership.deleted"
    ROLE_CHANGED = "membership.role_changed"
    CONVERSION = "membership.conversion"

class DevotionEventType(Enum):
    """Devotion and religious practice event types"""
    DEVOTION_INCREASED = "devotion.increased"
    DEVOTION_DECREASED = "devotion.decreased"
    RITUAL_PERFORMED = "devotion.ritual_performed"
    BLESSING_RECEIVED = "devotion.blessing_received"
    PRAYER_OFFERED = "devotion.prayer_offered"

class NarrativeEventType(Enum):
    """Religious narrative and story event types"""
    RELIGIOUS_NARRATIVE = "narrative.religious_story"
    SCHISM = "narrative.schism"
    PROPHECY = "narrative.prophecy"
    MIRACLE = "narrative.miracle"
    PILGRIMAGE = "narrative.pilgrimage"

class InfluenceEventType(Enum):
    """Religious influence and cross-system event types"""
    INFLUENCE_SPREAD = "influence.spread"
    CONFLICT = "influence.conflict"
    ALLIANCE = "influence.alliance"
    REGIONAL_DOMINANCE = "influence.regional_dominance"

# ============================================================================
# Core Religion Events
# ============================================================================

class ReligionCreatedEvent(EventBase):
    """Event fired when a new religion is created"""
    
    def __init__(self, 
                 religion_id: UUID,
                 name: str,
                 religion_type: str,
                 creator_id: Optional[UUID] = None,
                 region_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = ReligionEventType.CREATED.value
        self.religion_id = religion_id
        self.name = name
        self.religion_type = religion_type
        self.creator_id = creator_id
        self.region_id = region_id
        self.metadata = metadata or {}

class ReligionUpdatedEvent(EventBase):
    """Event fired when a religion is updated"""
    
    def __init__(self,
                 religion_id: UUID,
                 changes: Dict[str, Any],
                 old_values: Optional[Dict[str, Any]] = None,
                 updated_by: Optional[UUID] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = ReligionEventType.UPDATED.value
        self.religion_id = religion_id
        self.changes = changes
        self.old_values = old_values or {}
        self.updated_by = updated_by

class ReligionDeletedEvent(EventBase):
    """Event fired when a religion is deleted"""
    
    def __init__(self,
                 religion_id: UUID,
                 name: str,
                 deletion_reason: Optional[str] = None,
                 deleted_by: Optional[UUID] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = ReligionEventType.DELETED.value
        self.religion_id = religion_id
        self.name = name
        self.deletion_reason = deletion_reason
        self.deleted_by = deleted_by

# ============================================================================
# Membership Events
# ============================================================================

class MembershipCreatedEvent(EventBase):
    """Event fired when an entity joins a religion"""
    
    def __init__(self,
                 membership_id: UUID,
                 religion_id: UUID,
                 entity_id: UUID,
                 entity_type: str,
                 role: str = "follower",
                 devotion_level: float = 0.5,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = MembershipEventType.CREATED.value
        self.membership_id = membership_id
        self.religion_id = religion_id
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.role = role
        self.devotion_level = devotion_level

class MembershipUpdatedEvent(EventBase):
    """Event fired when a membership is updated"""
    
    def __init__(self,
                 membership_id: UUID,
                 religion_id: UUID,
                 entity_id: UUID,
                 changes: Dict[str, Any],
                 old_values: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = MembershipEventType.UPDATED.value
        self.membership_id = membership_id
        self.religion_id = religion_id
        self.entity_id = entity_id
        self.changes = changes
        self.old_values = old_values or {}

class MembershipDeletedEvent(EventBase):
    """Event fired when an entity leaves a religion"""
    
    def __init__(self,
                 membership_id: UUID,
                 religion_id: UUID,
                 entity_id: UUID,
                 reason: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = MembershipEventType.DELETED.value
        self.membership_id = membership_id
        self.religion_id = religion_id
        self.entity_id = entity_id
        self.reason = reason

class ConversionEvent(EventBase):
    """Event fired when an entity converts between religions"""
    
    def __init__(self,
                 entity_id: UUID,
                 entity_type: str,
                 from_religion_id: Optional[UUID],
                 to_religion_id: UUID,
                 conversion_reason: Optional[str] = None,
                 conversion_strength: float = 1.0,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = MembershipEventType.CONVERSION.value
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.from_religion_id = from_religion_id
        self.to_religion_id = to_religion_id
        self.conversion_reason = conversion_reason
        self.conversion_strength = conversion_strength

# ============================================================================
# Devotion Events
# ============================================================================

class DevotionChangedEvent(EventBase):
    """Event fired when an entity's devotion level changes"""
    
    def __init__(self,
                 membership_id: UUID,
                 religion_id: UUID,
                 entity_id: UUID,
                 old_devotion: float,
                 new_devotion: float,
                 change_reason: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = DevotionEventType.DEVOTION_INCREASED.value if new_devotion > old_devotion else DevotionEventType.DEVOTION_DECREASED.value
        self.membership_id = membership_id
        self.religion_id = religion_id
        self.entity_id = entity_id
        self.old_devotion = old_devotion
        self.new_devotion = new_devotion
        self.change_reason = change_reason
        self.devotion_delta = new_devotion - old_devotion

class ReligiousRitualEvent(EventBase):
    """Event fired when a religious ritual is performed"""
    
    def __init__(self,
                 ritual_id: UUID,
                 religion_id: UUID,
                 entity_id: UUID,
                 ritual_type: str,
                 ritual_name: str,
                 location: Optional[str] = None,
                 participants: Optional[List[UUID]] = None,
                 devotion_effect: Optional[float] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = DevotionEventType.RITUAL_PERFORMED.value
        self.ritual_id = ritual_id
        self.religion_id = religion_id
        self.entity_id = entity_id
        self.ritual_type = ritual_type
        self.ritual_name = ritual_name
        self.location = location
        self.participants = participants or []
        self.devotion_effect = devotion_effect

# ============================================================================
# Narrative Events
# ============================================================================

class ReligiousNarrativeEvent(EventBase):
    """Event fired for religion-related narrative elements"""
    
    def __init__(self,
                 narrative_id: UUID,
                 religion_id: UUID,
                 narrative_type: str,
                 title: str,
                 content: str,
                 entities_involved: Optional[List[UUID]] = None,
                 location: Optional[str] = None,
                 impact_level: str = "minor",
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = NarrativeEventType.RELIGIOUS_NARRATIVE.value
        self.narrative_id = narrative_id
        self.religion_id = religion_id
        self.narrative_type = narrative_type
        self.title = title
        self.content = content
        self.entities_involved = entities_involved or []
        self.location = location
        self.impact_level = impact_level

class SchismEvent(EventBase):
    """Event fired when a religion splits or experiences internal conflict"""
    
    def __init__(self,
                 schism_id: UUID,
                 parent_religion_id: UUID,
                 new_religion_id: Optional[UUID] = None,
                 schism_type: str = "doctrinal",
                 cause: str = "unknown",
                 leader_id: Optional[UUID] = None,
                 followers_affected: Optional[List[UUID]] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = NarrativeEventType.SCHISM.value
        self.schism_id = schism_id
        self.parent_religion_id = parent_religion_id
        self.new_religion_id = new_religion_id
        self.schism_type = schism_type
        self.cause = cause
        self.leader_id = leader_id
        self.followers_affected = followers_affected or []

# ============================================================================
# System Integration Events
# ============================================================================

class ReligiousInfluenceEvent(EventBase):
    """Event fired when religious influence spreads or affects regions/entities"""
    
    def __init__(self,
                 religion_id: UUID,
                 influence_type: str,
                 target_type: str,  # "region", "faction", "character", etc.
                 target_id: Union[UUID, str],
                 influence_strength: float,
                 influence_change: float,
                 cause: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = InfluenceEventType.INFLUENCE_SPREAD.value
        self.religion_id = religion_id
        self.influence_type = influence_type
        self.target_type = target_type
        self.target_id = target_id
        self.influence_strength = influence_strength
        self.influence_change = influence_change
        self.cause = cause

class ReligiousConflictEvent(EventBase):
    """Event fired when religious conflicts occur between religions or with other systems"""
    
    def __init__(self,
                 conflict_id: UUID,
                 religion_ids: List[UUID],
                 conflict_type: str,
                 cause: str,
                 location: Optional[str] = None,
                 intensity: float = 1.0,
                 resolution: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.event_type = InfluenceEventType.CONFLICT.value
        self.conflict_id = conflict_id
        self.religion_ids = religion_ids
        self.conflict_type = conflict_type
        self.cause = cause
        self.location = location
        self.intensity = intensity
        self.resolution = resolution 