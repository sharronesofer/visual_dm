"""
Cascade Engine

Implements enhanced cascading effects for chaos events, creating
secondary and tertiary event chains that propagate across systems
and regions with realistic delays and probability calculations.
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4

from backend.infrastructure.systems.chaos.models.chaos_events import ChaosEvent, ChaosEventType, EventSeverity
from backend.infrastructure.systems.chaos.models.pressure_data import PressureData
from backend.systems.chaos.core.config import ChaosConfig

logger = logging.getLogger(__name__)


class CascadeType(Enum):
    """Types of cascade relationships"""
    IMMEDIATE = "immediate"      # Triggers within hours
    DELAYED = "delayed"          # Triggers within days
    CONDITIONAL = "conditional"  # Triggers only if conditions are met
    AMPLIFYING = "amplifying"    # Increases severity of existing events
    MITIGATING = "mitigating"    # Reduces impact of other events


@dataclass
class CascadeRule:
    """Defines how one event can cascade to another"""
    rule_id: str = field(default_factory=lambda: str(uuid4()))
    trigger_event_type: ChaosEventType = ChaosEventType.SOCIAL_UNREST
    cascade_event_type: ChaosEventType = ChaosEventType.SOCIAL_UNREST
    cascade_type: CascadeType = CascadeType.DELAYED
    
    # Probability and timing
    base_probability: float = 0.3  # Base chance of cascade (0-1)
    min_delay_hours: float = 1.0   # Minimum delay before cascade
    max_delay_hours: float = 72.0  # Maximum delay before cascade
    
    # Conditions
    required_severity: Optional[EventSeverity] = None  # Minimum severity needed
    required_regions: List[str] = field(default_factory=list)  # Must affect these regions
    required_conditions: Dict[str, Any] = field(default_factory=dict)  # Additional conditions
    
    # Effects on cascade event
    severity_modifier: float = 0.0  # How much to modify cascade event severity (-2 to +2)
    probability_modifiers: Dict[str, float] = field(default_factory=dict)  # Context-based probability changes
    
    # Metadata
    description: str = ""
    narrative_reason: str = ""  # Why this cascade makes narrative sense
    
    def calculate_cascade_probability(self, 
                                    trigger_event: ChaosEvent,
                                    world_context: Dict[str, Any]) -> float:
        """Calculate actual cascade probability based on context"""
        probability = self.base_probability
        
        # Apply severity modifiers
        if trigger_event.severity == EventSeverity.CATASTROPHIC:
            probability *= 1.5
        elif trigger_event.severity == EventSeverity.CRITICAL:
            probability *= 1.3
        elif trigger_event.severity == EventSeverity.MAJOR:
            probability *= 1.1
        elif trigger_event.severity == EventSeverity.MINOR:
            probability *= 0.7
        
        # Apply context-based modifiers
        for context_key, modifier in self.probability_modifiers.items():
            if context_key in world_context:
                context_value = world_context[context_key]
                if isinstance(context_value, (int, float)):
                    probability *= (1.0 + modifier * context_value)
                elif context_value is True:
                    probability *= (1.0 + modifier)
        
        # Check required conditions
        if self.required_severity and trigger_event.severity.value < self.required_severity.value:
            probability = 0.0
        
        if self.required_regions:
            if not any(region in trigger_event.affected_regions for region in self.required_regions):
                probability *= 0.5  # Reduce but don't eliminate
        
        return max(0.0, min(1.0, probability))
    
    def calculate_cascade_delay(self, trigger_event: ChaosEvent) -> float:
        """Calculate delay before cascade triggers"""
        if self.cascade_type == CascadeType.IMMEDIATE:
            return random.uniform(0.1, 2.0)  # 6 minutes to 2 hours
        elif self.cascade_type == CascadeType.DELAYED:
            base_delay = random.uniform(self.min_delay_hours, self.max_delay_hours)
            # Higher severity events cascade faster
            severity_factor = 1.0 - (trigger_event.severity.value * 0.1)
            return base_delay * severity_factor
        else:
            return random.uniform(self.min_delay_hours, self.max_delay_hours)


@dataclass
class CascadeEvent:
    """A scheduled cascade event"""
    cascade_id: str = field(default_factory=lambda: str(uuid4()))
    trigger_event_id: str = ""
    cascade_rule: CascadeRule = None
    
    # Scheduled event details
    scheduled_event_type: ChaosEventType = ChaosEventType.SOCIAL_UNREST
    scheduled_severity: EventSeverity = EventSeverity.MODERATE
    scheduled_time: datetime = field(default_factory=datetime.now)
    affected_regions: List[str] = field(default_factory=list)
    
    # State
    triggered: bool = False
    cancelled: bool = False
    actual_event_id: Optional[str] = None  # ID of the actual event when triggered
    
    # Context
    cascade_context: Dict[str, Any] = field(default_factory=dict)
    narrative_context: str = ""
    
    def is_due(self) -> bool:
        """Check if this cascade should trigger now"""
        return not self.triggered and not self.cancelled and datetime.now() >= self.scheduled_time
    
    def time_until_trigger(self) -> timedelta:
        """Get time remaining until cascade triggers"""
        return self.scheduled_time - datetime.now()


class CascadeEngine:
    """
    Manages cascading effects for chaos events.
    
    This engine:
    - Defines cascade rules between different event types
    - Calculates cascade probabilities based on context
    - Schedules and manages cascade events
    - Handles cross-regional cascade propagation
    - Implements feedback loops and amplification effects
    - Uses LLM reasoning for intelligent cascade prediction
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.cascade_rules: List[CascadeRule] = []
        self.scheduled_cascades: Dict[str, CascadeEvent] = {}
        self.cascade_history: List[Tuple[datetime, CascadeEvent]] = []
        
        # LLM service reference (set by chaos manager)
        self.llm_service: Optional[Any] = None
        
        # System state
        self._initialized = False
        self._running = False
        self._paused = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self.metrics = {
            'cascades_processed': 0,
            'cascades_triggered': 0,
            'llm_analyzed_cascades': 0,
            'rule_based_cascades': 0,
            'prevented_cascades': 0
        }
        
        # Initialize cascade rules
        self._initialize_cascade_rules()

    def set_llm_service(self, llm_service: Any) -> None:
        """Set the LLM service for intelligent cascade analysis"""
        self.llm_service = llm_service

    async def initialize(self) -> None:
        """Initialize the cascade engine"""
        if self._initialized:
            return
        self._initialized = True
        if self.llm_service:
            print("Cascade engine initialized with LLM-enhanced cascade reasoning")
        else:
            print("Cascade engine initialized with rule-based cascades")

    async def start(self) -> None:
        """Start cascade monitoring"""
        if not self._initialized:
            await self.initialize()
        
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        print("Cascade engine started")

    async def stop(self) -> None:
        """Stop cascade monitoring"""
        if not self._running:
            return
        
        self._running = False
        self._paused = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        print("Cascade engine stopped")

    async def pause(self) -> None:
        """Pause cascade monitoring"""
        if not self._running:
            return
        self._paused = True

    async def resume(self) -> None:
        """Resume cascade monitoring"""
        if not self._running:
            return
        self._paused = False

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for processing scheduled cascades"""
        while self._running:
            try:
                if self._paused:
                    await asyncio.sleep(1.0)
                    continue
                
                # Process any due cascades
                await self.process_due_cascades()
                
                # Clean up old history
                self._cleanup_old_history()
                
                # Check every 30 seconds
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cascade monitoring loop: {e}")
                await asyncio.sleep(60)

    def _initialize_cascade_rules(self) -> None:
        """Initialize default cascade rules"""
        # Economic cascades
        self.cascade_rules.extend([
            CascadeRule(
                rule_id="economic_to_social",
                trigger_event_type=ChaosEventType.ECONOMIC_COLLAPSE,
                cascade_event_type=ChaosEventType.SOCIAL_UNREST,
                cascade_type=CascadeType.DELAYED,
                base_probability=0.7,
                min_delay_hours=12.0,
                max_delay_hours=48.0,
                severity_modifier=0.5,
                description="Economic collapse often leads to social unrest",
                narrative_reason="People become desperate when they lose their livelihoods"
            ),
            CascadeRule(
                rule_id="economic_to_political",
                trigger_event_type=ChaosEventType.ECONOMIC_COLLAPSE,
                cascade_event_type=ChaosEventType.POLITICAL_UPHEAVAL,
                cascade_type=CascadeType.DELAYED,
                base_probability=0.5,
                min_delay_hours=24.0,
                max_delay_hours=72.0,
                severity_modifier=0.0,
                description="Economic crisis can destabilize political systems",
                narrative_reason="Governments often face blame for economic failures"
            ),
            # Political cascades
            CascadeRule(
                rule_id="political_to_economic",
                trigger_event_type=ChaosEventType.POLITICAL_UPHEAVAL,
                cascade_event_type=ChaosEventType.ECONOMIC_COLLAPSE,
                cascade_type=CascadeType.DELAYED,
                base_probability=0.6,
                min_delay_hours=6.0,
                max_delay_hours=24.0,
                severity_modifier=-0.5,
                description="Political instability disrupts economic activity",
                narrative_reason="Uncertainty and conflict harm trade and investment"
            ),
            CascadeRule(
                rule_id="political_to_social", 
                trigger_event_type=ChaosEventType.POLITICAL_UPHEAVAL,
                cascade_event_type=ChaosEventType.SOCIAL_UNREST,
                cascade_type=CascadeType.IMMEDIATE,
                base_probability=0.8,
                min_delay_hours=1.0,
                max_delay_hours=12.0,
                severity_modifier=0.0,
                description="Political upheaval often triggers social unrest",
                narrative_reason="Citizens take to the streets during political crises"
            ),
            # Social cascades
            CascadeRule(
                rule_id="social_to_political",
                trigger_event_type=ChaosEventType.SOCIAL_UNREST,
                cascade_event_type=ChaosEventType.POLITICAL_UPHEAVAL,
                cascade_type=CascadeType.CONDITIONAL,
                base_probability=0.4,
                min_delay_hours=8.0,
                max_delay_hours=48.0,
                severity_modifier=1.0,
                required_severity=EventSeverity.MAJOR,
                description="Major social unrest can trigger political change",
                narrative_reason="Sustained protests pressure governments to respond"
            )
        ])
        
        # Add cross-regional cascades
        self._add_cross_regional_cascades()
    
    def _add_cross_regional_cascades(self) -> None:
        """Add rules for cascades that spread between regions"""
        cross_regional_rules = [
            CascadeRule(
                rule_id="economic_contagion",
                trigger_event_type=ChaosEventType.ECONOMIC_COLLAPSE,
                cascade_event_type=ChaosEventType.ECONOMIC_COLLAPSE,
                cascade_type=CascadeType.DELAYED,
                base_probability=0.3,
                min_delay_hours=24.0,
                max_delay_hours=168.0,  # Up to a week
                severity_modifier=-1.0,  # Usually less severe
                description="Economic collapse can spread to connected regions",
                narrative_reason="Trade relationships and economic dependencies create contagion"
            ),
            CascadeRule(
                rule_id="refugee_crisis",
                trigger_event_type=ChaosEventType.SOCIAL_UNREST,
                cascade_event_type=ChaosEventType.SOCIAL_UNREST,
                cascade_type=CascadeType.DELAYED,
                base_probability=0.4,
                min_delay_hours=48.0,
                max_delay_hours=336.0,  # Up to two weeks
                severity_modifier=-0.5,
                required_severity=EventSeverity.CRITICAL,
                description="Severe unrest can cause refugee flows to neighboring regions",
                narrative_reason="People flee violence and instability, bringing tensions with them"
            )
        ]
        
        self.cascade_rules.extend(cross_regional_rules)
    
    async def process_event_cascades(self, 
                                   trigger_event: ChaosEvent,
                                   world_context: Dict[str, Any]) -> List[CascadeEvent]:
        """
        Process potential cascades from a trigger event using both LLM analysis and rules.
        
        Args:
            trigger_event: The event that might cause cascades
            world_context: Current state of the world
            
        Returns:
            List of scheduled cascade events
        """
        self.metrics['cascades_processed'] += 1
        cascades = []
        
        # Try LLM analysis first for more intelligent cascades
        if self.llm_service:
            try:
                llm_cascades = await self._analyze_cascades_with_llm(trigger_event, world_context)
                cascades.extend(llm_cascades)
                self.metrics['llm_analyzed_cascades'] += 1
            except Exception as e:
                logger.warning(f"LLM cascade analysis failed: {e}")
                # Continue to rule-based analysis
        
        # Rule-based cascade analysis (always run for comparison/backup)
        rule_cascades = await self._analyze_cascades_with_rules(trigger_event, world_context)
        
        # Merge LLM and rule-based cascades, avoiding duplicates
        if not cascades:  # If LLM didn't work, use rule cascades
            cascades = rule_cascades
            self.metrics['rule_based_cascades'] += 1
        else:
            # Combine intelligently - LLM cascades take priority
            cascades = self._merge_cascade_analyses(cascades, rule_cascades)
        
        # Schedule all determined cascades
        for cascade in cascades:
            self.scheduled_cascades[cascade.cascade_id] = cascade
            logger.info(f"Scheduled cascade: {cascade.scheduled_event_type.value} in {cascade.time_until_trigger()}")
        
        return cascades
    
    async def _analyze_cascades_with_llm(self, trigger_event: ChaosEvent, 
                                       world_context: Dict[str, Any]) -> List[CascadeEvent]:
        """Use LLM to analyze potential cascades"""
        llm_response = await self.llm_service.analyze_cascade_potential(trigger_event, world_context)
        
        if not llm_response.success:
            return []
        
        try:
            import json
            cascade_data = json.loads(llm_response.content)
            cascades = []
            
            for cascade_info in cascade_data.get('cascades', []):
                # Create cascade event from LLM analysis
                cascade_event = self._create_cascade_from_llm_analysis(
                    trigger_event, cascade_info, world_context
                )
                if cascade_event:
                    cascades.append(cascade_event)
            
            return cascades
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse LLM cascade response: {e}")
            return []
    
    def _create_cascade_from_llm_analysis(self, trigger_event: ChaosEvent, 
                                        cascade_info: Dict[str, Any],
                                        world_context: Dict[str, Any]) -> Optional[CascadeEvent]:
        """Create a cascade event from LLM analysis results"""
        try:
            # Map LLM event type to our enum
            event_type_str = cascade_info.get('event_type', '').lower().replace(' ', '_')
            event_type_mapping = {
                'economic_crisis': ChaosEventType.ECONOMIC_COLLAPSE,
                'economic_collapse': ChaosEventType.ECONOMIC_COLLAPSE,
                'political_upheaval': ChaosEventType.POLITICAL_UPHEAVAL,
                'political_crisis': ChaosEventType.POLITICAL_UPHEAVAL,
                'social_unrest': ChaosEventType.SOCIAL_UNREST,
                'civil_unrest': ChaosEventType.SOCIAL_UNREST,
                'resource_scarcity': ChaosEventType.ECONOMIC_COLLAPSE,  # Close enough
                'natural_disaster': ChaosEventType.ENVIRONMENTAL_CRISIS,
                'environmental_crisis': ChaosEventType.ENVIRONMENTAL_CRISIS
            }
            
            cascade_event_type = event_type_mapping.get(event_type_str, ChaosEventType.SOCIAL_UNREST)
            
            # Calculate severity
            severity_modifier = cascade_info.get('severity_modifier', 0)
            base_severity = trigger_event.severity
            new_severity_value = max(1, min(5, base_severity.value + severity_modifier))
            severity_values = list(EventSeverity)
            cascade_severity = severity_values[new_severity_value - 1]
            
            # Calculate timing
            delay_hours = cascade_info.get('delay_hours', 24)
            scheduled_time = datetime.now() + timedelta(hours=delay_hours)
            
            # Determine affected regions
            affected_regions = cascade_info.get('affected_regions', trigger_event.affected_regions)
            
            # Create cascade event
            cascade_event = CascadeEvent(
                trigger_event_id=trigger_event.event_id,
                scheduled_event_type=cascade_event_type,
                scheduled_severity=cascade_severity,
                scheduled_time=scheduled_time,
                affected_regions=affected_regions,
                cascade_context={
                    'llm_generated': True,
                    'probability': cascade_info.get('probability', 0.5),
                    'reasoning': cascade_info.get('reasoning', ''),
                    'trigger_event_type': trigger_event.event_type.value
                },
                narrative_context=cascade_info.get('reasoning', 'LLM-determined cascade')
            )
            
            return cascade_event
            
        except Exception as e:
            logger.warning(f"Failed to create cascade from LLM analysis: {e}")
            return None
    
    async def _analyze_cascades_with_rules(self, trigger_event: ChaosEvent,
                                         world_context: Dict[str, Any]) -> List[CascadeEvent]:
        """Analyze cascades using traditional rule-based approach"""
        cascades = []
        
        for rule in self.cascade_rules:
            if rule.trigger_event_type != trigger_event.event_type:
                continue
            
            # Calculate probability
            probability = rule.calculate_cascade_probability(trigger_event, world_context)
            
            if probability <= 0:
                continue
            
            # Roll for cascade
            if random.random() <= probability:
                # Calculate cascade properties
                cascade_severity = self._calculate_cascade_severity(trigger_event, rule)
                cascade_delay = rule.calculate_cascade_delay(trigger_event)
                cascade_regions = self._determine_cascade_regions(trigger_event, rule, world_context)
                
                # Create cascade event
                cascade_event = CascadeEvent(
                    trigger_event_id=trigger_event.event_id,
                    cascade_rule=rule,
                    scheduled_event_type=rule.cascade_event_type,
                    scheduled_severity=cascade_severity,
                    scheduled_time=datetime.now() + timedelta(hours=cascade_delay),
                    affected_regions=cascade_regions,
                    cascade_context={
                        'rule_based': True,
                        'rule_id': rule.rule_id,
                        'calculated_probability': probability,
                        'trigger_event_type': trigger_event.event_type.value
                    },
                    narrative_context=rule.narrative_reason
                )
                
                cascades.append(cascade_event)
        
        return cascades
    
    def _merge_cascade_analyses(self, llm_cascades: List[CascadeEvent],
                              rule_cascades: List[CascadeEvent]) -> List[CascadeEvent]:
        """Merge LLM and rule-based cascade analyses intelligently"""
        merged = list(llm_cascades)  # Start with LLM cascades
        
        # Add rule cascades that don't conflict with LLM cascades
        for rule_cascade in rule_cascades:
            # Check if there's a similar LLM cascade
            conflict = False
            for llm_cascade in llm_cascades:
                if (rule_cascade.scheduled_event_type == llm_cascade.scheduled_event_type and
                    any(region in llm_cascade.affected_regions for region in rule_cascade.affected_regions)):
                    conflict = True
                    break
            
            if not conflict:
                # Reduce probability for rule-based cascade when LLM is also working
                rule_cascade.cascade_context['reduced_probability'] = True
                merged.append(rule_cascade)
        
        return merged
    
    def _calculate_cascade_severity(self, 
                                  trigger_event: ChaosEvent,
                                  rule: CascadeRule) -> EventSeverity:
        """Calculate the severity of a cascade event"""
        base_severity = trigger_event.severity.value
        modified_severity = base_severity + rule.severity_modifier
        
        # Apply cascade type modifiers
        if rule.cascade_type == CascadeType.AMPLIFYING:
            modified_severity += 1
        elif rule.cascade_type == CascadeType.MITIGATING:
            modified_severity -= 1
        
        # Clamp to valid range
        severity_value = max(1, min(5, int(modified_severity)))
        
        severity_map = {
            1: EventSeverity.MINOR,
            2: EventSeverity.MODERATE,
            3: EventSeverity.MAJOR,
            4: EventSeverity.CRITICAL,
            5: EventSeverity.CATASTROPHIC
        }
        
        return severity_map[severity_value]
    
    def _determine_cascade_regions(self,
                                 trigger_event: ChaosEvent,
                                 rule: CascadeRule,
                                 world_context: Dict[str, Any]) -> List[str]:
        """Determine which regions a cascade event should affect"""
        cascade_regions = []
        
        # Start with trigger event regions
        if rule.cascade_type in [CascadeType.IMMEDIATE, CascadeType.AMPLIFYING]:
            # Same regions as trigger
            cascade_regions = trigger_event.affected_regions.copy()
        else:
            # May spread to connected regions
            cascade_regions = trigger_event.affected_regions.copy()
            
            # Add connected regions based on context
            connected_regions = world_context.get('connected_regions', {})
            for region in trigger_event.affected_regions:
                if region in connected_regions:
                    # Add some connected regions with probability
                    for connected_region in connected_regions[region]:
                        if random.random() < 0.3:  # 30% chance to spread
                            if connected_region not in cascade_regions:
                                cascade_regions.append(connected_region)
        
        return cascade_regions
    
    async def process_due_cascades(self) -> List[ChaosEvent]:
        """
        Process cascade events that are due to trigger.
        
        Returns:
            List of chaos events to be triggered
        """
        triggered_events = []
        completed_cascades = []
        
        for cascade_id, cascade_event in self.scheduled_cascades.items():
            if cascade_event.is_due():
                # Create the actual chaos event
                chaos_event = self._create_chaos_event_from_cascade(cascade_event)
                triggered_events.append(chaos_event)
                
                # Mark cascade as triggered
                cascade_event.triggered = True
                cascade_event.actual_event_id = chaos_event.event_id
                
                # Record in history
                self.cascade_history.append((datetime.now(), cascade_event))
                completed_cascades.append(cascade_id)
        
        # Clean up completed cascades
        for cascade_id in completed_cascades:
            del self.scheduled_cascades[cascade_id]
        
        return triggered_events
    
    def _create_chaos_event_from_cascade(self, cascade_event: CascadeEvent) -> ChaosEvent:
        """Create a ChaosEvent from a CascadeEvent"""
        chaos_event = ChaosEvent(
            event_type=cascade_event.scheduled_event_type,
            severity=cascade_event.scheduled_severity,
            title=f"Cascading {cascade_event.scheduled_event_type.value.replace('_', ' ').title()}",
            description=f"A {cascade_event.scheduled_event_type.value.replace('_', ' ')} "
                       f"triggered by cascading effects from previous events. "
                       f"{cascade_event.narrative_context}",
            affected_regions=cascade_event.affected_regions,
            triggered_at=datetime.now(),
            chaos_score_at_trigger=0.0,  # Will be set by the chaos engine
            tags=['cascade', 'secondary_effect']
        )
        
        # Add cascade-specific metadata
        chaos_event.metadata = {
            'cascade_id': cascade_event.cascade_id,
            'trigger_event_id': cascade_event.trigger_event_id,
            'cascade_rule_id': cascade_event.cascade_rule.rule_id,
            'cascade_type': cascade_event.cascade_rule.cascade_type.value,
            'narrative_reason': cascade_event.narrative_context
        }
        
        return chaos_event
    
    def cancel_cascade(self, cascade_id: str, reason: str = "intervention") -> bool:
        """
        Cancel a scheduled cascade event.
        
        Args:
            cascade_id: ID of the cascade to cancel
            reason: Reason for cancellation
            
        Returns:
            True if cascade was cancelled successfully
        """
        if cascade_id in self.scheduled_cascades:
            cascade_event = self.scheduled_cascades[cascade_id]
            cascade_event.cancelled = True
            
            return True
        
        return False
    
    def get_scheduled_cascades(self, 
                             hours_ahead: float = 72.0) -> List[CascadeEvent]:
        """Get cascades scheduled within the next N hours"""
        cutoff_time = datetime.now() + timedelta(hours=hours_ahead)
        
        return [
            cascade for cascade in self.scheduled_cascades.values()
            if not cascade.cancelled and cascade.scheduled_time <= cutoff_time
        ]
    
    def get_cascade_statistics(self) -> Dict[str, Any]:
        """Get statistics about cascade system performance"""
        total_scheduled = len(self.scheduled_cascades)
        total_completed = len(self.cascade_history)
        
        # Analyze cascade types
        cascade_type_counts = {}
        for cascade in self.scheduled_cascades.values():
            cascade_type = cascade.cascade_rule.cascade_type.value
            cascade_type_counts[cascade_type] = cascade_type_counts.get(cascade_type, 0) + 1
        
        # Analyze trigger patterns
        trigger_patterns = {}
        for _, cascade in self.cascade_history[-50:]:  # Last 50 cascades
            trigger_type = cascade.cascade_rule.trigger_event_type.value
            cascade_type = cascade.cascade_rule.cascade_event_type.value
            pattern = f"{trigger_type} -> {cascade_type}"
            trigger_patterns[pattern] = trigger_patterns.get(pattern, 0) + 1
        
        return {
            'total_scheduled_cascades': total_scheduled,
            'total_completed_cascades': total_completed,
            'cascade_type_distribution': cascade_type_counts,
            'common_cascade_patterns': dict(sorted(trigger_patterns.items(), 
                                                  key=lambda x: x[1], reverse=True)[:10]),
            'average_cascade_delay': self._calculate_average_cascade_delay()
        }
    
    def _calculate_average_cascade_delay(self) -> float:
        """Calculate average delay between trigger and cascade"""
        if not self.cascade_history:
            return 0.0
        
        delays = []
        for triggered_time, cascade in self.cascade_history[-20:]:  # Last 20 cascades
            if hasattr(cascade, 'scheduled_time'):
                delay = (triggered_time - cascade.scheduled_time).total_seconds() / 3600.0
                delays.append(abs(delay))  # Use absolute value
        
        return sum(delays) / len(delays) if delays else 0.0

    def _cleanup_old_history(self) -> None:
        """Clean up old cascade history to manage memory usage"""
        if len(self.cascade_history) > 1000:  # Arbitrary limit
            self.cascade_history = self.cascade_history[-500:]  # Keep last 500
        
        # Clean up old scheduled cascades
        cutoff_time = datetime.now() - timedelta(days=7)  # Arbitrary cutoff
        self.scheduled_cascades = {
            cascade_id: cascade for cascade_id, cascade in self.scheduled_cascades.items()
            if not cascade.cancelled and cascade.scheduled_time > cutoff_time
        } 