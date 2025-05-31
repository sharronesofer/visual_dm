"""
Chaos Events Model

Defines all types of chaos events that can be triggered by the chaos system,
including their properties, severity levels, and data structures.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4


@dataclass
class EventMetadata:
    """Metadata for chaos events"""
    source_system: str = "chaos"  # System that generated this event
    generation_method: str = "automatic"  # How the event was generated
    confidence_score: float = 1.0  # Confidence in event appropriateness (0.0 to 1.0)
    narrative_weight: float = 1.0  # How important this event is narratively
    
    # Context information
    world_state_snapshot: Dict[str, Any] = field(default_factory=dict)
    pressure_context: Dict[str, float] = field(default_factory=dict)
    related_events: List[str] = field(default_factory=list)  # IDs of related events
    
    # Generation details
    generation_timestamp: datetime = field(default_factory=datetime.now)
    generation_parameters: Dict[str, Any] = field(default_factory=dict)
    template_used: Optional[str] = None
    
    # Quality metrics
    coherence_score: float = 1.0  # How well this fits with existing narrative
    impact_score: float = 1.0  # Expected impact on game world
    player_relevance: float = 1.0  # How relevant this is to player actions
    
    def update_quality_metrics(self, coherence: float, impact: float, relevance: float) -> None:
        """Update quality metrics for this event"""
        self.coherence_score = max(0.0, min(1.0, coherence))
        self.impact_score = max(0.0, min(1.0, impact))
        self.player_relevance = max(0.0, min(1.0, relevance))
    
    def get_overall_quality(self) -> float:
        """Get overall quality score combining all metrics"""
        return (self.confidence_score + self.coherence_score + 
                self.impact_score + self.player_relevance) / 4.0


class ChaosEventType(Enum):
    """Types of chaos events that can be triggered"""
    # Political Events
    POLITICAL_UPHEAVAL = "political_upheaval"
    LEADERSHIP_COUP = "leadership_coup"
    REBELLION = "rebellion"
    GOVERNMENT_COLLAPSE = "government_collapse"
    
    # Natural Disasters
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    DROUGHT = "drought"
    PLAGUE = "plague"
    VOLCANIC_ERUPTION = "volcanic_eruption"
    STORM = "storm"
    WILDFIRE = "wildfire"
    
    # Economic Events
    ECONOMIC_COLLAPSE = "economic_collapse"
    MARKET_CRASH = "market_crash"
    CURRENCY_DEVALUATION = "currency_devaluation"
    TRADE_DISRUPTION = "trade_disruption"
    BANKING_CRISIS = "banking_crisis"
    
    # Military/War Events
    WAR_OUTBREAK = "war_outbreak"
    TERRITORIAL_CONFLICT = "territorial_conflict"
    RESOURCE_WAR = "resource_war"
    MILITARY_COUP = "military_coup"
    BORDER_SKIRMISH = "border_skirmish"
    
    # Resource Events
    RESOURCE_SCARCITY = "resource_scarcity"
    FOOD_SHORTAGE = "food_shortage"
    MATERIAL_SCARCITY = "material_scarcity"
    ENERGY_CRISIS = "energy_crisis"
    WATER_SHORTAGE = "water_shortage"
    
    # Social Events
    FACTION_BETRAYAL = "faction_betrayal"
    ALLIANCE_BREAK = "alliance_break"
    SOCIAL_UNREST = "social_unrest"
    MASS_MIGRATION = "mass_migration"
    CULTURAL_SCHISM = "cultural_schism"
    
    # Character/Revelation Events
    SCANDAL_REVELATION = "scandal_revelation"
    SECRET_DISCOVERY = "secret_discovery"
    BETRAYAL_EXPOSURE = "betrayal_exposure"
    CORRUPTION_EXPOSED = "corruption_exposed"
    CONSPIRACY_UNCOVERED = "conspiracy_uncovered"


class EventSeverity(Enum):
    """Severity levels for chaos events"""
    MINOR = "minor"        # Low impact, localized effects
    MODERATE = "moderate"  # Regional impact, noticeable effects
    MAJOR = "major"        # Multi-regional impact, significant effects
    CATASTROPHIC = "catastrophic"  # Global impact, world-changing effects


class EventStatus(Enum):
    """Status of a chaos event"""
    PENDING = "pending"         # Event queued but not yet triggered
    ACTIVE = "active"           # Event currently happening
    RESOLVING = "resolving"     # Event winding down
    RESOLVED = "resolved"       # Event completed
    CANCELLED = "cancelled"     # Event cancelled before triggering


@dataclass
class EventEffect:
    """A specific effect that an event has on game systems"""
    target_system: str  # "faction", "economy", "region", etc.
    target_id: Optional[Union[str, UUID]]  # Specific entity ID if applicable
    effect_type: str  # "reduce_stability", "increase_tension", etc.
    magnitude: float  # How strong the effect is (0.0 to 1.0)
    duration_hours: float  # How long the effect lasts
    delay_hours: float = 0.0  # Delay before effect triggers
    
    # Effect details
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def is_delayed(self) -> bool:
        """Check if this effect has a delay"""
        return self.delay_hours > 0.0


@dataclass
class EventTriggerCondition:
    """Conditions that must be met for an event to trigger"""
    pressure_source: str  # Which pressure source triggers this
    minimum_threshold: float  # Minimum chaos score needed
    maximum_threshold: float = 1.0  # Maximum chaos score (for scaling)
    required_regions: List[Union[str, UUID]] = field(default_factory=list)  # Specific regions needed
    blacklist_regions: List[Union[str, UUID]] = field(default_factory=list)  # Regions that prevent this event
    required_conditions: Dict[str, Any] = field(default_factory=dict)  # Additional conditions
    
    def is_met(self, chaos_score: float, active_regions: List[Union[str, UUID]], 
               context: Dict[str, Any]) -> bool:
        """Check if trigger conditions are met"""
        # Check chaos threshold
        if not (self.minimum_threshold <= chaos_score <= self.maximum_threshold):
            return False
        
        # Check required regions
        if self.required_regions:
            if not any(region in active_regions for region in self.required_regions):
                return False
        
        # Check blacklisted regions
        if self.blacklist_regions:
            if any(region in active_regions for region in self.blacklist_regions):
                return False
        
        # Check additional conditions
        for condition, required_value in self.required_conditions.items():
            if context.get(condition) != required_value:
                return False
        
        return True


@dataclass
class ChaosEvent:
    """A chaos event that can be triggered by the chaos system"""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: ChaosEventType = ChaosEventType.SOCIAL_UNREST
    severity: EventSeverity = EventSeverity.MINOR
    status: EventStatus = EventStatus.PENDING
    
    # Basic properties
    title: str = ""
    description: str = ""
    flavor_text: str = ""  # Narrative description for storytelling
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    triggered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    duration_hours: float = 24.0  # How long the event lasts
    
    # Location and scope
    affected_regions: List[Union[str, UUID]] = field(default_factory=list)
    primary_region: Optional[Union[str, UUID]] = None
    global_event: bool = False  # Whether this affects the entire world
    
    # Trigger conditions
    trigger_conditions: List[EventTriggerCondition] = field(default_factory=list)
    chaos_score_at_trigger: float = 0.0
    pressure_sources_at_trigger: Dict[str, float] = field(default_factory=dict)
    
    # Effects and consequences
    immediate_effects: List[EventEffect] = field(default_factory=list)
    ongoing_effects: List[EventEffect] = field(default_factory=list)
    resolution_effects: List[EventEffect] = field(default_factory=list)
    
    # Cascading events
    secondary_events: List[str] = field(default_factory=list)  # Event types that might cascade
    cascade_probability: float = 0.0  # Chance of triggering secondary events
    cascade_delay_hours: float = 1.0  # Delay before cascading events
    
    # Mitigation and resolution
    mitigation_factors: Dict[str, float] = field(default_factory=dict)  # What can reduce this event's impact
    resolution_conditions: Dict[str, Any] = field(default_factory=dict)  # What ends the event early
    auto_resolve: bool = True  # Whether the event resolves automatically
    
    # Cooldowns and restrictions
    cooldown_hours: float = 72.0  # How long before this event type can trigger again
    regional_cooldown_hours: float = 168.0  # Cooldown per region
    max_concurrent: int = 1  # Max instances of this event type at once
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    weight: float = 1.0  # Relative probability weight
    rarity: float = 1.0  # How rare this event is (lower = rarer)
    
    def __post_init__(self):
        """Set derived properties after initialization"""
        if not self.title:
            self.title = self.event_type.value.replace('_', ' ').title()
        
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=self.duration_hours)
    
    def trigger(self, chaos_score: float, pressure_sources: Dict[str, float]) -> None:
        """Trigger this event"""
        self.status = EventStatus.ACTIVE
        self.triggered_at = datetime.now()
        self.chaos_score_at_trigger = chaos_score
        self.pressure_sources_at_trigger = pressure_sources.copy()
        
        # Set expiration based on actual trigger time
        self.expires_at = self.triggered_at + timedelta(hours=self.duration_hours)
    
    def resolve(self) -> None:
        """Resolve this event"""
        self.status = EventStatus.RESOLVED
    
    def cancel(self) -> None:
        """Cancel this event before it triggers"""
        self.status = EventStatus.CANCELLED
    
    def is_active(self) -> bool:
        """Check if this event is currently active"""
        return self.status == EventStatus.ACTIVE and datetime.now() < self.expires_at
    
    def is_expired(self) -> bool:
        """Check if this event has expired"""
        return self.expires_at is not None and datetime.now() >= self.expires_at
    
    def get_remaining_duration(self) -> float:
        """Get remaining duration in hours"""
        if not self.is_active() or self.expires_at is None:
            return 0.0
        
        remaining = (self.expires_at - datetime.now()).total_seconds() / 3600.0
        return max(0.0, remaining)
    
    def get_intensity_modifier(self) -> float:
        """Get intensity modifier based on severity"""
        intensity_map = {
            EventSeverity.MINOR: 0.5,
            EventSeverity.MODERATE: 1.0,
            EventSeverity.MAJOR: 1.5,
            EventSeverity.CATASTROPHIC: 2.0
        }
        return intensity_map.get(self.severity, 1.0)
    
    def can_cascade_to(self, other_event_type: ChaosEventType) -> bool:
        """Check if this event can cascade to another event type"""
        return other_event_type.value in self.secondary_events
    
    def get_event_summary(self) -> Dict[str, Any]:
        """Get a summary of this event"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'title': self.title,
            'description': self.description,
            'affected_regions': [str(r) for r in self.affected_regions],
            'global_event': self.global_event,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'remaining_hours': self.get_remaining_duration(),
            'chaos_score_at_trigger': self.chaos_score_at_trigger,
            'immediate_effects_count': len(self.immediate_effects),
            'ongoing_effects_count': len(self.ongoing_effects),
            'intensity_modifier': self.get_intensity_modifier()
        }


@dataclass
class EventTemplate:
    """Template for creating chaos events with predefined configurations"""
    event_type: ChaosEventType
    base_severity: EventSeverity
    base_duration_hours: float
    base_cooldown_hours: float
    
    # Template properties
    title_template: str
    description_template: str
    flavor_text_template: str
    
    # Default effects templates
    immediate_effect_templates: List[Dict[str, Any]] = field(default_factory=list)
    ongoing_effect_templates: List[Dict[str, Any]] = field(default_factory=list)
    resolution_effect_templates: List[Dict[str, Any]] = field(default_factory=list)
    
    # Default trigger conditions
    default_trigger_conditions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Scaling parameters
    severity_scaling: Dict[str, float] = field(default_factory=dict)  # How severity affects properties
    chaos_scaling: Dict[str, float] = field(default_factory=dict)  # How chaos score affects properties
    
    # Cascading configuration
    cascade_events: List[ChaosEventType] = field(default_factory=list)
    base_cascade_probability: float = 0.0
    
    def create_event(self, chaos_score: float, severity_override: Optional[EventSeverity] = None,
                    affected_regions: Optional[List[Union[str, UUID]]] = None) -> ChaosEvent:
        """Create a chaos event from this template"""
        severity = severity_override or self.base_severity
        
        # Apply scaling based on chaos score and severity
        duration = self._scale_property('duration', self.base_duration_hours, chaos_score, severity)
        cooldown = self._scale_property('cooldown', self.base_cooldown_hours, chaos_score, severity)
        cascade_prob = self._scale_property('cascade_probability', self.base_cascade_probability, chaos_score, severity)
        
        # Create event
        event = ChaosEvent(
            event_type=self.event_type,
            severity=severity,
            title=self._format_template(self.title_template, chaos_score, severity),
            description=self._format_template(self.description_template, chaos_score, severity),
            flavor_text=self._format_template(self.flavor_text_template, chaos_score, severity),
            duration_hours=duration,
            cooldown_hours=cooldown,
            cascade_probability=cascade_prob,
            secondary_events=[event.value for event in self.cascade_events],
            affected_regions=affected_regions or []
        )
        
        # Add effects from templates
        event.immediate_effects = self._create_effects_from_templates(
            self.immediate_effect_templates, chaos_score, severity
        )
        event.ongoing_effects = self._create_effects_from_templates(
            self.ongoing_effect_templates, chaos_score, severity
        )
        event.resolution_effects = self._create_effects_from_templates(
            self.resolution_effect_templates, chaos_score, severity
        )
        
        # Add trigger conditions
        event.trigger_conditions = self._create_trigger_conditions_from_templates(
            self.default_trigger_conditions, chaos_score, severity
        )
        
        return event
    
    def _scale_property(self, property_name: str, base_value: float, 
                       chaos_score: float, severity: EventSeverity) -> float:
        """Scale a property based on chaos score and severity"""
        # Apply chaos scaling
        chaos_multiplier = 1.0
        if property_name in self.chaos_scaling:
            chaos_multiplier = 1.0 + (chaos_score * self.chaos_scaling[property_name])
        
        # Apply severity scaling
        severity_multiplier = 1.0
        if property_name in self.severity_scaling:
            severity_multipliers = {
                EventSeverity.MINOR: 0.5,
                EventSeverity.MODERATE: 1.0,
                EventSeverity.MAJOR: 1.5,
                EventSeverity.CATASTROPHIC: 2.0
            }
            base_severity_mult = severity_multipliers.get(severity, 1.0)
            severity_multiplier = base_severity_mult * self.severity_scaling[property_name]
        
        return base_value * chaos_multiplier * severity_multiplier
    
    def _format_template(self, template: str, chaos_score: float, severity: EventSeverity) -> str:
        """Format a text template with current values"""
        return template.format(
            chaos_score=chaos_score,
            severity=severity.value,
            intensity=self._get_intensity_adjective(severity)
        )
    
    def _get_intensity_adjective(self, severity: EventSeverity) -> str:
        """Get an adjective describing the intensity"""
        adjectives = {
            EventSeverity.MINOR: "minor",
            EventSeverity.MODERATE: "significant", 
            EventSeverity.MAJOR: "severe",
            EventSeverity.CATASTROPHIC: "catastrophic"
        }
        return adjectives.get(severity, "significant")
    
    def _create_effects_from_templates(self, templates: List[Dict[str, Any]], 
                                     chaos_score: float, severity: EventSeverity) -> List[EventEffect]:
        """Create event effects from templates"""
        effects = []
        for template in templates:
            effect = EventEffect(
                target_system=template['target_system'],
                target_id=template.get('target_id'),
                effect_type=template['effect_type'],
                magnitude=self._scale_property('magnitude', template['magnitude'], chaos_score, severity),
                duration_hours=self._scale_property('duration_hours', template['duration_hours'], chaos_score, severity),
                delay_hours=template.get('delay_hours', 0.0),
                description=template.get('description', ''),
                parameters=template.get('parameters', {})
            )
            effects.append(effect)
        return effects
    
    def _create_trigger_conditions_from_templates(self, templates: List[Dict[str, Any]],
                                                chaos_score: float, severity: EventSeverity) -> List[EventTriggerCondition]:
        """Create trigger conditions from templates"""
        conditions = []
        for template in templates:
            condition = EventTriggerCondition(
                pressure_source=template['pressure_source'],
                minimum_threshold=template['minimum_threshold'],
                maximum_threshold=template.get('maximum_threshold', 1.0),
                required_regions=template.get('required_regions', []),
                blacklist_regions=template.get('blacklist_regions', []),
                required_conditions=template.get('required_conditions', {})
            )
            conditions.append(condition)
        return conditions


# Specific Event Classes
# These are convenience classes for creating specific types of chaos events

class PoliticalUpheavalEvent(ChaosEvent):
    """Political upheaval chaos event"""
    
    def __init__(self, **kwargs):
        super().__init__(
            event_type=ChaosEventType.POLITICAL_UPHEAVAL,
            title="Political Upheaval",
            description="Political instability and upheaval disrupts governance",
            **kwargs
        )


class NaturalDisasterEvent(ChaosEvent):
    """Natural disaster chaos event"""
    
    def __init__(self, disaster_type: str = "earthquake", **kwargs):
        disaster_types = {
            "earthquake": ChaosEventType.EARTHQUAKE,
            "flood": ChaosEventType.FLOOD,
            "drought": ChaosEventType.DROUGHT,
            "plague": ChaosEventType.PLAGUE,
            "volcanic_eruption": ChaosEventType.VOLCANIC_ERUPTION,
            "storm": ChaosEventType.STORM,
            "wildfire": ChaosEventType.WILDFIRE
        }
        
        event_type = disaster_types.get(disaster_type, ChaosEventType.EARTHQUAKE)
        
        super().__init__(
            event_type=event_type,
            title=f"Natural Disaster: {disaster_type.replace('_', ' ').title()}",
            description=f"A {disaster_type.replace('_', ' ')} strikes the region",
            **kwargs
        )


class EconomicCollapseEvent(ChaosEvent):
    """Economic collapse chaos event"""
    
    def __init__(self, **kwargs):
        super().__init__(
            event_type=ChaosEventType.ECONOMIC_COLLAPSE,
            title="Economic Collapse",
            description="Economic systems fail, causing widespread financial disruption",
            **kwargs
        )


class WarOutbreakEvent(ChaosEvent):
    """War outbreak chaos event"""
    
    def __init__(self, **kwargs):
        super().__init__(
            event_type=ChaosEventType.WAR_OUTBREAK,
            title="War Outbreak",
            description="Armed conflict erupts between factions",
            **kwargs
        )


class ResourceScarcityEvent(ChaosEvent):
    """Resource scarcity chaos event"""
    
    def __init__(self, resource_type: str = "food", **kwargs):
        resource_types = {
            "food": ChaosEventType.FOOD_SHORTAGE,
            "material": ChaosEventType.MATERIAL_SCARCITY,
            "energy": ChaosEventType.ENERGY_CRISIS,
            "water": ChaosEventType.WATER_SHORTAGE
        }
        
        event_type = resource_types.get(resource_type, ChaosEventType.RESOURCE_SCARCITY)
        
        super().__init__(
            event_type=event_type,
            title=f"{resource_type.title()} Scarcity",
            description=f"Critical shortage of {resource_type} resources",
            **kwargs
        )


class FactionBetrayalEvent(ChaosEvent):
    """Faction betrayal chaos event"""
    
    def __init__(self, **kwargs):
        super().__init__(
            event_type=ChaosEventType.FACTION_BETRAYAL,
            title="Faction Betrayal",
            description="A trusted faction breaks their alliance and betrays their allies",
            **kwargs
        )


class CharacterRevelationEvent(ChaosEvent):
    """Character revelation chaos event"""
    
    def __init__(self, revelation_type: str = "scandal", **kwargs):
        revelation_types = {
            "scandal": ChaosEventType.SCANDAL_REVELATION,
            "secret": ChaosEventType.SECRET_DISCOVERY,
            "betrayal": ChaosEventType.BETRAYAL_EXPOSURE,
            "corruption": ChaosEventType.CORRUPTION_EXPOSED,
            "conspiracy": ChaosEventType.CONSPIRACY_UNCOVERED
        }
        
        event_type = revelation_types.get(revelation_type, ChaosEventType.SCANDAL_REVELATION)
        
        super().__init__(
            event_type=event_type,
            title=f"Character Revelation: {revelation_type.title()}",
            description=f"A shocking {revelation_type} about a key character is revealed",
            **kwargs
        ) 