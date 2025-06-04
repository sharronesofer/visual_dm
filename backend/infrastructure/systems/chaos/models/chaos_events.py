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
import json


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
    
    # Legacy fields for backward compatibility
    trigger_reason: Optional[str] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
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
    # Legacy simplified event types for backward compatibility
    POLITICAL_UPHEAVAL = "political_upheaval"
    NATURAL_DISASTER = "natural_disaster"  # Legacy alias
    ECONOMIC_COLLAPSE = "economic_collapse"
    WAR_OUTBREAK = "war_outbreak"
    RESOURCE_SCARCITY = "resource_scarcity"
    FACTION_BETRAYAL = "faction_betrayal"
    CHARACTER_REVELATION = "character_revelation"
    
    # Political Events
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
    MARKET_CRASH = "market_crash"
    CURRENCY_DEVALUATION = "currency_devaluation"
    TRADE_DISRUPTION = "trade_disruption"
    BANKING_CRISIS = "banking_crisis"
    
    # Military/War Events
    TERRITORIAL_CONFLICT = "territorial_conflict"
    RESOURCE_WAR = "resource_war"
    MILITARY_COUP = "military_coup"
    BORDER_SKIRMISH = "border_skirmish"
    
    # Resource Events
    FOOD_SHORTAGE = "food_shortage"
    MATERIAL_SCARCITY = "material_scarcity"
    ENERGY_CRISIS = "energy_crisis"
    WATER_SHORTAGE = "water_shortage"
    
    # Social Events
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
    MINOR = 1        # Low impact, localized effects
    MODERATE = 2     # Regional impact, noticeable effects
    MAJOR = 3        # Multi-regional impact, significant effects
    CRITICAL = 4     # Critical impact, severe effects (alias for backward compatibility)
    CATASTROPHIC = 5 # Global impact, world-changing effects


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
    target_id: Optional[Union[str, UUID]] = None  # Specific entity ID if applicable (made optional for compatibility)
    effect_type: str = ""  # "reduce_stability", "increase_tension", etc.
    magnitude: float = 0.0  # How strong the effect is (0.0 to 1.0)
    duration_hours: float = 24.0  # How long the effect lasts
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
    triggered_at: Optional[datetime] = field(default_factory=datetime.now)  # Set by default for legacy compatibility
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
    
    # Legacy fields for backward compatibility
    government_type: Optional[str] = None
    magnitude: Optional[float] = None
    collapse_type: Optional[str] = None
    aggressor_faction: Optional[str] = None
    defender_faction: Optional[str] = None
    scarce_resources: Optional[List[str]] = None
    betraying_faction: Optional[str] = None
    target_faction: Optional[str] = None
    character_id: Optional[str] = None
    revelation_details: Optional[str] = None
    
    # Additional legacy fields from tests
    rebellion_strength: Optional[float] = None
    affected_factions: Optional[List[str]] = None
    disaster_type: Optional[str] = None
    affected_resources: Optional[List[str]] = None
    economic_impact: Optional[float] = None
    war_type: Optional[str] = None
    estimated_duration_days: Optional[int] = None
    scarcity_level: Optional[float] = None
    cause: Optional[str] = None
    betrayed_faction: Optional[str] = None
    betrayal_type: Optional[str] = None
    trust_impact: Optional[float] = None
    revelation_type: Optional[str] = None
    revelation_content: Optional[str] = None
    narrative_impact: Optional[float] = None
    
    def __post_init__(self):
        """Set derived properties after initialization"""
        # Validation
        if self.event_type is None:
            raise ValueError("event_type cannot be None")
        
        # Validate affected_regions - empty list is not allowed for non-global events
        if not self.global_event and self.affected_regions is not None and len(self.affected_regions) == 0:
            raise ValueError("affected_regions cannot be empty for non-global events")
        
        if not self.title:
            self.title = self.event_type.value.replace('_', ' ').title()
        
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=self.duration_hours)
    
    def __init__(self, **kwargs):
        """Custom init to handle backward compatibility for chaos_score_trigger"""
        # Handle backward compatibility: chaos_score_trigger -> chaos_score_at_trigger
        if 'chaos_score_trigger' in kwargs and 'chaos_score_at_trigger' not in kwargs:
            kwargs['chaos_score_at_trigger'] = kwargs.pop('chaos_score_trigger')
        
        # Set defaults for required fields
        kwargs.setdefault('event_id', str(uuid4()))
        kwargs.setdefault('event_type', ChaosEventType.SOCIAL_UNREST)
        kwargs.setdefault('severity', EventSeverity.MINOR)
        kwargs.setdefault('status', EventStatus.PENDING)
        kwargs.setdefault('title', "")
        kwargs.setdefault('description', "")
        kwargs.setdefault('flavor_text', "")
        kwargs.setdefault('created_at', datetime.now())
        kwargs.setdefault('triggered_at', datetime.now())
        kwargs.setdefault('expires_at', None)
        kwargs.setdefault('duration_hours', 24.0)
        kwargs.setdefault('affected_regions', [])
        kwargs.setdefault('primary_region', None)
        kwargs.setdefault('global_event', False)
        kwargs.setdefault('trigger_conditions', [])
        kwargs.setdefault('chaos_score_at_trigger', 0.0)
        kwargs.setdefault('pressure_sources_at_trigger', {})
        kwargs.setdefault('immediate_effects', [])
        kwargs.setdefault('ongoing_effects', [])
        kwargs.setdefault('resolution_effects', [])
        kwargs.setdefault('secondary_events', [])
        kwargs.setdefault('cascade_probability', 0.0)
        kwargs.setdefault('cascade_delay_hours', 1.0)
        kwargs.setdefault('mitigation_factors', {})
        kwargs.setdefault('resolution_conditions', {})
        kwargs.setdefault('auto_resolve', True)
        kwargs.setdefault('cooldown_hours', 72.0)
        kwargs.setdefault('regional_cooldown_hours', 168.0)
        kwargs.setdefault('max_concurrent', 1)
        kwargs.setdefault('tags', [])
        kwargs.setdefault('weight', 1.0)
        kwargs.setdefault('rarity', 1.0)
        
        # Set all attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Call post_init manually since we're overriding __init__
        self.__post_init__()
    
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
            EventSeverity.CRITICAL: 1.75,
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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary for WebSocket compatibility"""
        result = {
            'event_id': self.event_id,
            'event_type': self.event_type.name,  # Use .name for enum serialization
            'severity': self.severity.name,      # Use .name for enum serialization  
            'status': self.status.value,
            'title': self.title,
            'description': self.description,
            'flavor_text': self.flavor_text,
            'affected_regions': [str(r) for r in self.affected_regions],
            'global_event': self.global_event,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'duration_hours': self.duration_hours,
            'chaos_score_at_trigger': self.chaos_score_at_trigger,
            'cascade_probability': self.cascade_probability,
            'cooldown_hours': self.cooldown_hours,
            'weight': self.weight,
            'rarity': self.rarity
        }
        
        # Add legacy fields if they exist
        legacy_fields = [
            'government_type', 'magnitude', 'collapse_type', 'aggressor_faction', 
            'defender_faction', 'scarce_resources', 'betraying_faction', 'target_faction',
            'character_id', 'revelation_details', 'rebellion_strength', 'affected_factions',
            'disaster_type', 'affected_resources', 'economic_impact', 'war_type',
            'estimated_duration_days', 'scarcity_level', 'cause', 'betrayed_faction',
            'betrayal_type', 'trust_impact', 'revelation_type', 'revelation_content',
            'narrative_impact'
        ]
        
        for field in legacy_fields:
            value = getattr(self, field, None)
            if value is not None:
                result[field] = value
        
        return result

    def to_json(self) -> str:
        """Convert to JSON string for WebSocket compatibility"""
        return json.dumps(self.to_dict())
    
    @property
    def chaos_score_trigger(self) -> float:
        """Backward compatibility property for chaos_score_at_trigger"""
        return self.chaos_score_at_trigger
    
    @chaos_score_trigger.setter
    def chaos_score_trigger(self, value: float) -> None:
        """Backward compatibility setter for chaos_score_at_trigger"""
        self.chaos_score_at_trigger = value


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
    
    # LLM enhancement settings
    use_llm_generation: bool = True  # Whether to use LLM for text generation
    llm_service: Optional[Any] = None  # Reference to LLM service (set externally)
    
    def create_event(self, chaos_score: float, severity_override: Optional[EventSeverity] = None,
                    affected_regions: Optional[List[Union[str, UUID]]] = None,
                    context: Optional[Dict[str, Any]] = None) -> ChaosEvent:
        """Create a chaos event from this template"""
        severity = severity_override or self.base_severity
        context = context or {}
        
        # Apply scaling based on chaos score and severity
        duration = self._scale_property('duration', self.base_duration_hours, chaos_score, severity)
        cooldown = self._scale_property('cooldown', self.base_cooldown_hours, chaos_score, severity)
        cascade_prob = self._scale_property('cascade_probability', self.base_cascade_probability, chaos_score, severity)
        
        # Generate text content (LLM-enhanced or template-based)
        title, description, flavor_text = self._generate_event_text(
            severity, chaos_score, affected_regions, context
        )
        
        # Create event
        event = ChaosEvent(
            event_type=self.event_type,
            severity=severity,
            title=title,
            description=description,
            flavor_text=flavor_text,
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
    
    def _generate_event_text(self, severity: EventSeverity, chaos_score: float, 
                           affected_regions: Optional[List[Union[str, UUID]]], 
                           context: Dict[str, Any]) -> tuple:
        """Generate event text using LLM or templates"""
        
        # Try LLM generation if available and enabled
        if self.use_llm_generation and self.llm_service:
            try:
                # Prepare context for LLM
                llm_context = {
                    'affected_regions': [str(r) for r in (affected_regions or [])],
                    'chaos_score': chaos_score,
                    **context
                }
                
                # This would be called asynchronously in practice, but we need sync here
                # In a real implementation, you'd need to handle this properly
                import asyncio
                
                # Try to get event loop, create one if needed
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, we can't await here
                        # Fall back to template generation
                        return self._generate_template_text(severity, chaos_score, affected_regions)
                    else:
                        llm_response = loop.run_until_complete(
                            self.llm_service.generate_event_description(
                                self.event_type, severity, llm_context
                            )
                        )
                except RuntimeError:
                    # No event loop, create a new one
                    llm_response = asyncio.run(
                        self.llm_service.generate_event_description(
                            self.event_type, severity, llm_context
                        )
                    )
                
                if llm_response.success:
                    # Parse LLM response - could be just description or structured
                    description = llm_response.content.strip()
                    
                    # Generate title from description or use template
                    title = self._generate_title_from_description(description, severity)
                    
                    # Use description as flavor text too, or generate separate
                    flavor_text = description
                    
                    return title, description, flavor_text
                    
            except Exception as e:
                # LLM generation failed, fall back to templates
                print(f"LLM generation failed for {self.event_type.value}: {e}")
                pass
        
        # Fall back to template-based generation
        return self._generate_template_text(severity, chaos_score, affected_regions)
    
    def _generate_template_text(self, severity: EventSeverity, chaos_score: float,
                              affected_regions: Optional[List[Union[str, UUID]]]) -> tuple:
        """Generate text using traditional templates"""
        title = self._format_template(self.title_template, chaos_score, severity)
        description = self._format_template(self.description_template, chaos_score, severity)
        flavor_text = self._format_template(self.flavor_text_template, chaos_score, severity)
        
        return title, description, flavor_text
    
    def _generate_title_from_description(self, description: str, severity: EventSeverity) -> str:
        """Generate a title from LLM description"""
        # Simple title generation - take first sentence and clean it up
        sentences = description.split('.')
        if sentences:
            title_base = sentences[0].strip()
            # Add severity indicator
            severity_prefix = {
                EventSeverity.MINOR: "Minor",
                EventSeverity.MODERATE: "Significant", 
                EventSeverity.MAJOR: "Major",
                EventSeverity.CRITICAL: "Critical",
                EventSeverity.CATASTROPHIC: "Catastrophic"
            }
            prefix = severity_prefix.get(severity, "")
            if prefix and not title_base.startswith(prefix):
                title_base = f"{prefix} {title_base}"
            
            # Limit title length
            if len(title_base) > 60:
                title_base = title_base[:57] + "..."
                
            return title_base
        
        # Fallback to template
        return self._format_template(self.title_template, 0.0, severity)
    
    def set_llm_service(self, llm_service: Any) -> None:
        """Set the LLM service for this template"""
        self.llm_service = llm_service
    
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
                EventSeverity.CRITICAL: 1.75,
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
            EventSeverity.CRITICAL: "critical",
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
        # For legacy compatibility, always use NATURAL_DISASTER as the event type
        # Store specific disaster type in the disaster_type field
        super().__init__(
            event_type=ChaosEventType.NATURAL_DISASTER,
            title=f"Natural Disaster: {disaster_type.replace('_', ' ').title()}",
            description=f"A {disaster_type.replace('_', ' ')} strikes the region",
            disaster_type=disaster_type,
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
        # For legacy compatibility, always use RESOURCE_SCARCITY as the event type
        # Store specific resource type in the scarce_resources field
        super().__init__(
            event_type=ChaosEventType.RESOURCE_SCARCITY,
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
        # For legacy compatibility, always use CHARACTER_REVELATION as the event type
        # Store specific revelation type in the revelation_type field
        super().__init__(
            event_type=ChaosEventType.CHARACTER_REVELATION,
            title=f"Character Revelation: {revelation_type.title()}",
            description=f"A shocking {revelation_type} about a key character is revealed",
            revelation_type=revelation_type,
            **kwargs
        ) 