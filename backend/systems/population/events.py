from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

from backend.core.events.event_dispatcher import EventBase
from backend.systems.population.models import POIState, POIType

class PopulationEventType(str, Enum):
    """Types of population events"""
    CHANGED = "population:changed"
    BIRTH = "population:birth"
    DEATH = "population:death"
    MIGRATION = "population:migration"
    STATE_CHANGED = "population:state_changed"
    CATASTROPHE = "population:catastrophe"
    WAR_IMPACT = "population:war_impact"

class PopulationEventBase(EventBase):
    """Base class for population-related events"""
    poi_id: str
    poi_name: str
    poi_type: POIType
    event_type: PopulationEventType
    timestamp: datetime = datetime.utcnow()
    metadata: Dict[str, Any] = {}

class PopulationChangedEventData(PopulationEventBase):
    """Event emitted when a POI's population changes"""
    old_population: int
    new_population: int
    old_state: Optional[POIState] = None
    new_state: Optional[POIState] = None
    change_type: str  # "growth", "decline", "manual", "migration", "catastrophe", "war"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.event_type = PopulationEventType.CHANGED

class PopulationStateChangedEventData(PopulationEventBase):
    """Event emitted when a POI's state changes"""
    old_state: POIState
    new_state: POIState
    population: int
    reason: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        self.event_type = PopulationEventType.STATE_CHANGED

class PopulationCatastropheEventData(PopulationEventBase):
    """Event emitted when a catastrophe affects population"""
    old_population: int
    new_population: int
    catastrophe_type: str  # "disease", "famine", "natural_disaster", etc.
    severity: float  # 0.0 to 1.0
    
    def __init__(self, **data):
        super().__init__(**data)
        self.event_type = PopulationEventType.CATASTROPHE

class PopulationWarImpactEventData(PopulationEventBase):
    """Event emitted when war affects population"""
    old_population: int
    new_population: int
    war_id: str
    damage_level: float  # 0.0 to 1.0
    
    def __init__(self, **data):
        super().__init__(**data)
        self.event_type = PopulationEventType.WAR_IMPACT

# Re-export the old class names for backward compatibility,
# but make it clear they are being renamed
PopulationEvent = PopulationEventBase
PopulationChangedEvent = PopulationChangedEventData
PopulationStateChangedEvent = PopulationStateChangedEventData
PopulationCatastropheEvent = PopulationCatastropheEventData
PopulationWarImpactEvent = PopulationWarImpactEventData 