"""Events for religion system"""

# Import all events from the religion_events module
from .religion_events import *

# Import event publisher
from .event_publisher import *

from .religion_events import (
    # Core religion events
    ReligionCreatedEvent,
    ReligionUpdatedEvent,
    ReligionDeletedEvent,
    
    # Membership events
    MembershipCreatedEvent,
    MembershipUpdatedEvent,
    MembershipDeletedEvent,
    ConversionEvent,
    
    # Devotion events
    DevotionChangedEvent,
    ReligiousRitualEvent,
    
    # Narrative events
    ReligiousNarrativeEvent,
    SchismEvent,
    
    # System integration events
    ReligiousInfluenceEvent,
    ReligiousConflictEvent,
    
    # Event types enums
    ReligionEventType,
    MembershipEventType,
    DevotionEventType,
    NarrativeEventType,
    InfluenceEventType,
)

__all__ = [
    # Core religion events
    'ReligionCreatedEvent',
    'ReligionUpdatedEvent', 
    'ReligionDeletedEvent',
    
    # Membership events
    'MembershipCreatedEvent',
    'MembershipUpdatedEvent',
    'MembershipDeletedEvent',
    'ConversionEvent',
    
    # Devotion events
    'DevotionChangedEvent',
    'ReligiousRitualEvent',
    
    # Narrative events
    'ReligiousNarrativeEvent',
    'SchismEvent',
    
    # System integration events
    'ReligiousInfluenceEvent',
    'ReligiousConflictEvent',
    
    # Event types enums
    'ReligionEventType',
    'MembershipEventType', 
    'DevotionEventType',
    'NarrativeEventType',
    'InfluenceEventType',
]

