"""
Lifecycle Events Service for POI System

Manages POI lifecycle events including creation, growth, decline, and destruction,
coordinating with other systems for comprehensive world simulation.
"""

from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta
import random

from backend.infrastructure.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.database import get_db_session
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LifecycleEventType(str, Enum):
    """Types of lifecycle events that can occur to POIs"""
    FOUNDING = "founding"                # New POI established
    GROWTH = "growth"                   # Population/size increase
    DECLINE = "decline"                 # Population/economic decline
    PROSPERITY = "prosperity"           # Economic boom
    DISASTER = "disaster"               # Natural disaster
    PLAGUE = "plague"                   # Disease outbreak
    WAR_IMPACT = "war_impact"          # Effects of conflict
    TRADE_BOOM = "trade_boom"          # Trade route establishment
    TRADE_LOSS = "trade_loss"          # Trade route loss
    RESOURCE_DISCOVERY = "resource_discovery"  # New resource found
    RESOURCE_DEPLETION = "resource_depletion"  # Resource exhausted
    CULTURAL_SHIFT = "cultural_shift"   # Cultural change
    TECHNOLOGY_ADVANCE = "technology_advance"  # Tech improvement
    LEADERSHIP_CHANGE = "leadership_change"    # Political change
    SEASONAL_EVENT = "seasonal_event"   # Seasonal occurrences
    MIGRATION_WAVE = "migration_wave"   # Large population movement
    ABANDONMENT = "abandonment"         # POI abandoned
    RESTORATION = "restoration"         # Abandoned POI restored


class EventSeverity(str, Enum):
    """Severity levels for lifecycle events"""
    TRIVIAL = "trivial"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class EventFrequency(str, Enum):
    """How frequently events occur"""
    VERY_RARE = "very_rare"      # Once per several years
    RARE = "rare"                # Once per year
    UNCOMMON = "uncommon"        # Few times per year
    COMMON = "common"            # Monthly
    FREQUENT = "frequent"        # Weekly
    VERY_FREQUENT = "very_frequent"  # Daily


@dataclass
class LifecycleEvent:
    """Represents a lifecycle event affecting a POI"""
    id: UUID = field(default_factory=uuid4)
    poi_id: UUID = field(default_factory=uuid4)
    event_type: LifecycleEventType = LifecycleEventType.GROWTH
    severity: EventSeverity = EventSeverity.MINOR
    name: str = ""
    description: str = ""
    effects: Dict[str, Any] = field(default_factory=dict)
    duration_days: int = 1
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.end_date is None and self.duration_days > 0:
            self.end_date = self.start_date + timedelta(days=self.duration_days)
    
    def is_expired(self) -> bool:
        """Check if the event has expired"""
        return self.end_date and datetime.utcnow() > self.end_date
    
    def get_remaining_days(self) -> int:
        """Get remaining days for the event"""
        if not self.end_date:
            return 0
        remaining = (self.end_date - datetime.utcnow()).days
        return max(0, remaining)


@dataclass
class EventTemplate:
    """Template for generating lifecycle events"""
    event_type: LifecycleEventType
    name: str
    description_template: str
    base_probability: float  # 0.0 to 1.0
    poi_type_modifiers: Dict[POIType, float] = field(default_factory=dict)
    population_modifiers: Dict[Tuple[int, int], float] = field(default_factory=dict)  # (min, max) -> modifier
    state_modifiers: Dict[POIState, float] = field(default_factory=dict)
    severity_distribution: Dict[EventSeverity, float] = field(default_factory=dict)
    effect_generators: List[Callable] = field(default_factory=list)
    min_duration: int = 1
    max_duration: int = 30
    
    def calculate_probability(self, poi: PoiEntity) -> float:
        """Calculate actual probability for this POI"""
        probability = self.base_probability
        
        # POI type modifier
        poi_type = POIType(poi.poi_type)
        if poi_type in self.poi_type_modifiers:
            probability *= self.poi_type_modifiers[poi_type]
        
        # Population modifier
        population = poi.population or 0
        for (min_pop, max_pop), modifier in self.population_modifiers.items():
            if min_pop <= population <= max_pop:
                probability *= modifier
                break
        
        # State modifier
        poi_state = POIState(poi.state)
        if poi_state in self.state_modifiers:
            probability *= self.state_modifiers[poi_state]
        
        return min(1.0, max(0.0, probability))
    
    def generate_severity(self) -> EventSeverity:
        """Generate event severity based on distribution"""
        if not self.severity_distribution:
            return EventSeverity.MINOR
        
        rand = random.random()
        cumulative = 0.0
        
        for severity, weight in self.severity_distribution.items():
            cumulative += weight
            if rand <= cumulative:
                return severity
        
        return EventSeverity.MINOR


@dataclass
class POILifecycleData:
    """Tracks lifecycle data for a POI"""
    poi_id: UUID
    foundation_date: datetime
    current_age_days: int = 0
    lifecycle_stage: str = "young"  # young, mature, old, ancient
    stability: float = 1.0  # 0.0 to 1.0
    prosperity: float = 0.5  # 0.0 to 1.0
    recent_events: List[UUID] = field(default_factory=list)
    event_history: List[UUID] = field(default_factory=list)
    next_major_event_date: Optional[datetime] = None
    
    def update_age(self):
        """Update the age and lifecycle stage"""
        self.current_age_days = (datetime.utcnow() - self.foundation_date).days
        
        if self.current_age_days < 365:
            self.lifecycle_stage = "young"
        elif self.current_age_days < 3650:  # 10 years
            self.lifecycle_stage = "mature"
        elif self.current_age_days < 18250:  # 50 years
            self.lifecycle_stage = "old"
        else:
            self.lifecycle_stage = "ancient"


class LifecycleEventsService:
    """Service for managing POI lifecycle events and evolution"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db_session()
        self.event_dispatcher = EventDispatcher()
        
        # Event and lifecycle data
        self.active_events: Dict[UUID, LifecycleEvent] = {}
        self.poi_lifecycle_data: Dict[UUID, POILifecycleData] = {}
        self.event_templates: List[EventTemplate] = []
        
        # Initialize event templates
        self._initialize_event_templates()
        
        # Configuration
        self.base_event_chance = 0.1  # 10% chance per day for any event
        self.max_simultaneous_events = 3
        self.event_memory_days = 365  # How long to remember events
    
    def _initialize_event_templates(self):
        """Initialize the event templates"""
        self.event_templates = [
            # Growth events
            EventTemplate(
                event_type=LifecycleEventType.GROWTH,
                name="Population Boom",
                description_template="A period of rapid population growth in {poi_name}",
                base_probability=0.05,
                poi_type_modifiers={
                    POIType.CITY: 1.5,
                    POIType.TOWN: 1.2,
                    POIType.VILLAGE: 0.8
                },
                state_modifiers={
                    POIState.GROWING: 2.0,
                    POIState.DECLINING: 0.2
                },
                severity_distribution={
                    EventSeverity.MINOR: 0.4,
                    EventSeverity.MODERATE: 0.4,
                    EventSeverity.MAJOR: 0.2
                },
                min_duration=30,
                max_duration=180
            ),
            
            # Disaster events
            EventTemplate(
                event_type=LifecycleEventType.DISASTER,
                name="Natural Disaster",
                description_template="A {disaster_type} strikes {poi_name}",
                base_probability=0.02,
                severity_distribution={
                    EventSeverity.MINOR: 0.3,
                    EventSeverity.MODERATE: 0.3,
                    EventSeverity.MAJOR: 0.25,
                    EventSeverity.SEVERE: 0.15
                },
                min_duration=1,
                max_duration=7
            ),
            
            # Trade events
            EventTemplate(
                event_type=LifecycleEventType.TRADE_BOOM,
                name="Trade Route Establishment",
                description_template="New trade routes bring prosperity to {poi_name}",
                base_probability=0.03,
                poi_type_modifiers={
                    POIType.MARKET: 2.0,
                    POIType.CITY: 1.5,
                    POIType.TOWN: 1.2
                },
                severity_distribution={
                    EventSeverity.MODERATE: 0.4,
                    EventSeverity.MAJOR: 0.6
                },
                min_duration=60,
                max_duration=365
            ),
            
            # Resource events
            EventTemplate(
                event_type=LifecycleEventType.RESOURCE_DISCOVERY,
                name="Resource Discovery",
                description_template="Valuable {resource_type} discovered near {poi_name}",
                base_probability=0.01,
                severity_distribution={
                    EventSeverity.MODERATE: 0.3,
                    EventSeverity.MAJOR: 0.5,
                    EventSeverity.SEVERE: 0.2
                },
                min_duration=1,
                max_duration=1  # Instant discovery
            ),
            
            # Plague events
            EventTemplate(
                event_type=LifecycleEventType.PLAGUE,
                name="Disease Outbreak",
                description_template="A {disease_name} outbreak affects {poi_name}",
                base_probability=0.015,
                population_modifiers={
                    (1000, 10000): 1.5,  # Larger populations more susceptible
                    (10000, 100000): 2.0
                },
                severity_distribution={
                    EventSeverity.MINOR: 0.4,
                    EventSeverity.MODERATE: 0.3,
                    EventSeverity.MAJOR: 0.2,
                    EventSeverity.SEVERE: 0.1
                },
                min_duration=30,
                max_duration=120
            )
        ]
    
    def initialize_poi_lifecycle(self, poi_id: UUID, foundation_date: Optional[datetime] = None) -> bool:
        """Initialize lifecycle tracking for a POI"""
        try:
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                return False
            
            foundation = foundation_date or poi.created_at or datetime.utcnow()
            
            lifecycle_data = POILifecycleData(
                poi_id=poi_id,
                foundation_date=foundation,
                stability=random.uniform(0.7, 1.0),
                prosperity=random.uniform(0.3, 0.7)
            )
            
            lifecycle_data.update_age()
            self.poi_lifecycle_data[poi_id] = lifecycle_data
            
            logger.info(f"Initialized lifecycle data for POI {poi_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing POI lifecycle: {e}")
            return False
    
    def process_daily_lifecycle(self, poi_id: UUID) -> Dict[str, Any]:
        """Process daily lifecycle events for a POI"""
        try:
            results = {
                'events_started': 0,
                'events_ended': 0,
                'new_events': [],
                'expired_events': []
            }
            
            # Update lifecycle data
            lifecycle_data = self.poi_lifecycle_data.get(poi_id)
            if lifecycle_data:
                lifecycle_data.update_age()
            
            # Process existing events
            for event in list(self.active_events.values()):
                if event.poi_id == poi_id and event.is_expired():
                    self._end_event(event)
                    results['events_ended'] += 1
                    results['expired_events'].append(str(event.id))
            
            # Check for new events
            new_events = self._check_for_new_events(poi_id)
            for event in new_events:
                if self._start_event(event):
                    results['events_started'] += 1
                    results['new_events'].append({
                        'id': str(event.id),
                        'type': event.event_type.value,
                        'name': event.name,
                        'severity': event.severity.value
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing daily lifecycle: {e}")
            return {'error': str(e)}
    
    def create_event(self, poi_id: UUID, event_type: LifecycleEventType, 
                    severity: EventSeverity = EventSeverity.MINOR,
                    custom_effects: Dict[str, Any] = None) -> Optional[LifecycleEvent]:
        """Manually create a lifecycle event"""
        try:
            # Find matching template
            template = None
            for t in self.event_templates:
                if t.event_type == event_type:
                    template = t
                    break
            
            if not template:
                logger.warning(f"No template found for event type {event_type}")
                return None
            
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                return None
            
            # Generate event
            event = LifecycleEvent(
                poi_id=poi_id,
                event_type=event_type,
                severity=severity,
                name=template.name,
                description=template.description_template.format(poi_name=poi.name),
                duration_days=random.randint(template.min_duration, template.max_duration),
                effects=custom_effects or {}
            )
            
            # Generate effects
            event.effects.update(self._generate_event_effects(event, poi))
            
            return event
            
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return None
    
    def apply_event_effects(self, event: LifecycleEvent) -> bool:
        """Apply the effects of an event to a POI"""
        try:
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == event.poi_id).first()
            if not poi:
                return False
            
            lifecycle_data = self.poi_lifecycle_data.get(event.poi_id)
            
            # Apply population effects
            if 'population_change' in event.effects:
                change = event.effects['population_change']
                new_population = max(0, (poi.population or 0) + change)
                poi.population = new_population
            
            # Apply state changes
            if 'state_change' in event.effects:
                new_state = event.effects['state_change']
                if new_state in [state.value for state in POIState]:
                    poi.state = new_state
            
            # Apply prosperity changes
            if lifecycle_data and 'prosperity_change' in event.effects:
                change = event.effects['prosperity_change']
                lifecycle_data.prosperity = max(0.0, min(1.0, lifecycle_data.prosperity + change))
            
            # Apply stability changes
            if lifecycle_data and 'stability_change' in event.effects:
                change = event.effects['stability_change']
                lifecycle_data.stability = max(0.0, min(1.0, lifecycle_data.stability + change))
            
            self.db_session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error applying event effects: {e}")
            return False
    
    def get_poi_lifecycle_status(self, poi_id: UUID) -> Dict[str, Any]:
        """Get comprehensive lifecycle status for a POI"""
        try:
            lifecycle_data = self.poi_lifecycle_data.get(poi_id)
            if not lifecycle_data:
                return {}
            
            active_events = [
                {
                    'id': str(event.id),
                    'type': event.event_type.value,
                    'name': event.name,
                    'severity': event.severity.value,
                    'remaining_days': event.get_remaining_days()
                }
                for event in self.active_events.values()
                if event.poi_id == poi_id
            ]
            
            return {
                'age_days': lifecycle_data.current_age_days,
                'lifecycle_stage': lifecycle_data.lifecycle_stage,
                'stability': lifecycle_data.stability,
                'prosperity': lifecycle_data.prosperity,
                'active_events': active_events,
                'recent_events_count': len(lifecycle_data.recent_events),
                'total_events_count': len(lifecycle_data.event_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting lifecycle status: {e}")
            return {}
    
    def _check_for_new_events(self, poi_id: UUID) -> List[LifecycleEvent]:
        """Check if new events should be triggered for a POI"""
        new_events = []
        
        try:
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                return new_events
            
            # Check if POI already has too many active events
            active_count = len([e for e in self.active_events.values() if e.poi_id == poi_id])
            if active_count >= self.max_simultaneous_events:
                return new_events
            
            # Roll for each event template
            for template in self.event_templates:
                probability = template.calculate_probability(poi)
                
                if random.random() < probability:
                    event = self._generate_event_from_template(template, poi)
                    if event:
                        new_events.append(event)
                        break  # Only one event per day per POI
            
            return new_events
            
        except Exception as e:
            logger.error(f"Error checking for new events: {e}")
            return []
    
    def _generate_event_from_template(self, template: EventTemplate, poi: PoiEntity) -> Optional[LifecycleEvent]:
        """Generate an event from a template"""
        try:
            severity = template.generate_severity()
            duration = random.randint(template.min_duration, template.max_duration)
            
            # Customize description
            description = template.description_template.format(
                poi_name=poi.name,
                disaster_type=random.choice(["earthquake", "flood", "fire", "storm"]),
                resource_type=random.choice(["iron ore", "gold", "precious gems", "fertile soil"]),
                disease_name=random.choice(["red fever", "wasting sickness", "bone rot", "mind fog"])
            )
            
            event = LifecycleEvent(
                poi_id=poi.id,
                event_type=template.event_type,
                severity=severity,
                name=template.name,
                description=description,
                duration_days=duration
            )
            
            # Generate effects
            event.effects = self._generate_event_effects(event, poi)
            
            return event
            
        except Exception as e:
            logger.error(f"Error generating event from template: {e}")
            return None
    
    def _generate_event_effects(self, event: LifecycleEvent, poi: PoiEntity) -> Dict[str, Any]:
        """Generate effects for an event"""
        effects = {}
        
        severity_multiplier = {
            EventSeverity.TRIVIAL: 0.1,
            EventSeverity.MINOR: 0.3,
            EventSeverity.MODERATE: 0.5,
            EventSeverity.MAJOR: 0.8,
            EventSeverity.SEVERE: 1.2,
            EventSeverity.CATASTROPHIC: 2.0
        }.get(event.severity, 0.5)
        
        population = poi.population or 100
        
        if event.event_type == LifecycleEventType.GROWTH:
            effects['population_change'] = int(population * 0.1 * severity_multiplier)
            effects['prosperity_change'] = 0.1 * severity_multiplier
            
        elif event.event_type == LifecycleEventType.DISASTER:
            effects['population_change'] = -int(population * 0.05 * severity_multiplier)
            effects['stability_change'] = -0.2 * severity_multiplier
            if severity_multiplier > 1.0:
                effects['state_change'] = POIState.DECLINING.value
                
        elif event.event_type == LifecycleEventType.PLAGUE:
            effects['population_change'] = -int(population * 0.1 * severity_multiplier)
            effects['stability_change'] = -0.3 * severity_multiplier
            
        elif event.event_type == LifecycleEventType.TRADE_BOOM:
            effects['prosperity_change'] = 0.2 * severity_multiplier
            effects['population_change'] = int(population * 0.05 * severity_multiplier)
            
        elif event.event_type == LifecycleEventType.RESOURCE_DISCOVERY:
            effects['prosperity_change'] = 0.3 * severity_multiplier
            effects['population_change'] = int(population * 0.15 * severity_multiplier)
        
        return effects
    
    def _start_event(self, event: LifecycleEvent) -> bool:
        """Start a lifecycle event"""
        try:
            self.active_events[event.id] = event
            
            # Apply immediate effects
            self.apply_event_effects(event)
            
            # Update lifecycle data
            lifecycle_data = self.poi_lifecycle_data.get(event.poi_id)
            if lifecycle_data:
                lifecycle_data.recent_events.append(event.id)
                lifecycle_data.event_history.append(event.id)
            
            # Dispatch event
            self.event_dispatcher.publish({
                'type': 'lifecycle_event_started',
                'event_id': str(event.id),
                'poi_id': str(event.poi_id),
                'event_type': event.event_type.value,
                'severity': event.severity.value,
                'name': event.name,
                'description': event.description,
                'duration_days': event.duration_days,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting event: {e}")
            return False
    
    def _end_event(self, event: LifecycleEvent) -> bool:
        """End a lifecycle event"""
        try:
            event.is_active = False
            
            # Remove from active events
            if event.id in self.active_events:
                del self.active_events[event.id]
            
            # Dispatch event
            self.event_dispatcher.publish({
                'type': 'lifecycle_event_ended',
                'event_id': str(event.id),
                'poi_id': str(event.poi_id),
                'event_type': event.event_type.value,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error ending event: {e}")
            return False


# Factory function for dependency injection
def get_lifecycle_events_service(db_session: Optional[Session] = None) -> LifecycleEventsService:
    """Factory function to create LifecycleEventsService instance"""
    return LifecycleEventsService(db_session) 