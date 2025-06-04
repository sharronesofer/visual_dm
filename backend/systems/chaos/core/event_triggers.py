"""
Event Trigger System

Handles the triggering of chaos events when thresholds are exceeded.
Manages event cascading, cooldowns, and intensity scaling.
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID

from backend.infrastructure.systems.chaos.models.chaos_events import (
    ChaosEvent, ChaosEventType, EventSeverity, EventStatus,
    PoliticalUpheavalEvent, NaturalDisasterEvent, EconomicCollapseEvent,
    WarOutbreakEvent, ResourceScarcityEvent, FactionBetrayalEvent,
    CharacterRevelationEvent, EventTemplate
)
from backend.infrastructure.systems.chaos.models.chaos_state import ChaosState, EventCooldown, ChaosLevel
from backend.infrastructure.systems.chaos.models.pressure_data import PressureData, RegionalPressure
from backend.systems.chaos.core.config import ChaosConfig

logger = logging.getLogger(__name__)


class EventTriggerSystem:
    """
    Main system for triggering chaos events based on pressure and chaos calculations
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.active_events: Dict[str, ChaosEvent] = {}
        self.event_templates = self._initialize_event_templates()
        self.last_trigger_check = datetime.now()
        
        # Event trigger configuration
        self.max_events_per_hour = config.max_events_per_hour
        self.max_concurrent_events = config.max_concurrent_events
        self.cascade_delay_minutes = config.cascade_delay_minutes
        
        # Random variation parameters
        self.trigger_variance = 0.1  # ±10% randomness in thresholds
        self.cascade_variance = 0.2  # ±20% randomness in cascade probability
        
        # Performance tracking
        self.events_triggered_today = 0
        self.last_reset_date = datetime.now().date()
        
    async def evaluate_triggers(self, chaos_result: Any, 
                              pressure_data: PressureData, chaos_state: ChaosState) -> List[ChaosEvent]:
        """
        Evaluate whether to trigger any chaos events based on current conditions
        """
        
        # Reset daily counter if needed
        self._reset_daily_counter_if_needed()
        
        # Check rate limiting
        if not self._can_trigger_events():
            return []
        
        # Clean up expired events and cooldowns
        self._cleanup_expired_events()
        chaos_state.clean_expired_cooldowns()
        
        # Find candidate events
        candidate_events = self._find_candidate_events(
            chaos_result, pressure_data, chaos_state
        )
        
        if not candidate_events:
            return []
        
        # Select and trigger events
        triggered_events = await self._select_and_trigger_events(
            candidate_events, chaos_result, chaos_state
        )
        
        # Handle cascading events
        cascade_events = await self._handle_cascading_events(
            triggered_events, chaos_result, chaos_state
        )
        
        all_triggered = triggered_events + cascade_events
        
        if all_triggered:
            for event in all_triggered:
                pass  # Events processed by other systems
        
        return all_triggered
    
    async def evaluate_and_trigger(self, chaos_result: Any, 
                                 pressure_data: PressureData, chaos_state: ChaosState) -> List[ChaosEvent]:
        """
        Alias for evaluate_triggers method to match event manager expectations
        """
        return await self.evaluate_triggers(chaos_result, pressure_data, chaos_state)
    
    async def get_candidate_events(self, chaos_result: Any,
                                 pressure_data: PressureData, chaos_state: ChaosState) -> List[ChaosEvent]:
        """
        Get candidate events without triggering them (for narrative intelligence weighting)
        """
        
        # Reset daily counter if needed
        self._reset_daily_counter_if_needed()
        
        # Check rate limiting
        if not self._can_trigger_events():
            return []
        
        # Clean up expired events and cooldowns
        self._cleanup_expired_events()
        chaos_state.clean_expired_cooldowns()
        
        # Find candidate events
        candidate_templates = self._find_candidate_events(
            chaos_result, pressure_data, chaos_state
        )
        
        if not candidate_templates:
            return []
        
        # Convert template candidates to actual events without triggering
        candidate_events = []
        for template, trigger_probability in candidate_templates:
            try:
                # Determine event severity and affected regions
                severity = self._determine_event_severity(chaos_result.chaos_score)
                affected_regions = self._select_affected_regions(
                    template, chaos_result, chaos_state
                )
                
                # Create event from template but don't trigger it
                event = template.create_event(
                    chaos_result.chaos_score,
                    severity_override=severity,
                    affected_regions=affected_regions
                )
                
                # Set the trigger probability for narrative intelligence weighting
                event.trigger_probability = trigger_probability
                
                candidate_events.append(event)
                
            except Exception as e:
                pass  # Error creating candidate event
        
        return candidate_events
    
    async def initialize(self) -> None:
        """Initialize the event trigger system"""
        pass  # Initialization complete
    
    def _find_candidate_events(self, chaos_result: Any,
                             pressure_data: PressureData, chaos_state: ChaosState) -> List[Tuple[EventTemplate, float]]:
        """Find events that could potentially be triggered"""
        candidates = []
        
        for template in self.event_templates:
            # Check if this event type is on cooldown
            if chaos_state.is_event_on_cooldown(template.event_type.value):
                continue
            
            # Check concurrent event limits
            if self._count_concurrent_events(template.event_type) >= template.create_event(0.0).max_concurrent:
                continue
            
            # Evaluate trigger conditions
            trigger_probability = self._calculate_trigger_probability(
                template, chaos_result, pressure_data, chaos_state
            )
            
            if trigger_probability > 0.0:
                candidates.append((template, trigger_probability))
        
        # Sort by probability (highest first)
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return candidates
    
    def _calculate_trigger_probability(self, template: EventTemplate, 
                                     chaos_result: Any,
                                     pressure_data: PressureData, 
                                     chaos_state: ChaosState) -> float:
        """Calculate the probability of triggering this event template"""
        
        # Get base chaos score
        chaos_score = chaos_result.chaos_score
        
        # Get pressure source mapping
        pressure_source_map = {
            ChaosEventType.POLITICAL_UPHEAVAL: "faction_conflict",
            ChaosEventType.LEADERSHIP_COUP: "faction_conflict", 
            ChaosEventType.REBELLION: "population_stress",
            ChaosEventType.EARTHQUAKE: "environmental_pressure",
            ChaosEventType.FLOOD: "environmental_pressure",
            ChaosEventType.DROUGHT: "environmental_pressure",
            ChaosEventType.PLAGUE: "population_stress",
            ChaosEventType.ECONOMIC_COLLAPSE: "economic_instability",
            ChaosEventType.MARKET_CRASH: "economic_instability",
            ChaosEventType.TRADE_DISRUPTION: "economic_instability",
            ChaosEventType.WAR_OUTBREAK: "military_buildup",
            ChaosEventType.TERRITORIAL_CONFLICT: "diplomatic_tension",
            ChaosEventType.RESOURCE_WAR: "resource_scarcity",
            ChaosEventType.RESOURCE_SCARCITY: "resource_scarcity",
            ChaosEventType.FOOD_SHORTAGE: "resource_scarcity",
            ChaosEventType.FACTION_BETRAYAL: "diplomatic_tension",
            ChaosEventType.ALLIANCE_BREAK: "diplomatic_tension",
            ChaosEventType.SOCIAL_UNREST: "population_stress",
            ChaosEventType.SCANDAL_REVELATION: "corruption",
            ChaosEventType.CORRUPTION_EXPOSED: "corruption"
        }
        
        # Get relevant pressure source
        relevant_pressure_source = pressure_source_map.get(template.event_type)
        if not relevant_pressure_source:
            # Fallback to general chaos score
            source_contribution = 1.0
        else:
            source_contribution = chaos_result.source_contributions.get(relevant_pressure_source, 0.0)
        
        # Calculate base probability from chaos levels
        chaos_level_probs = {
            ChaosLevel.DORMANT: 0.0,
            ChaosLevel.STABLE: 0.01,
            ChaosLevel.ELEVATED: 0.05, 
            ChaosLevel.HIGH: 0.15,
            ChaosLevel.CRITICAL: 0.35,
            ChaosLevel.EXTREME: 0.60
        }
        
        base_probability = chaos_level_probs.get(chaos_result.chaos_level, 0.0)
        
        # Apply source contribution weighting
        weighted_probability = base_probability * source_contribution
        
        # Apply event-specific modifiers
        event_sample = template.create_event(chaos_score)
        rarity_modifier = event_sample.rarity
        weight_modifier = event_sample.weight
        
        # Calculate severity modifier based on chaos score
        severity = self._determine_event_severity(chaos_score)
        severity_modifier = {
            EventSeverity.MINOR: 1.0,
            EventSeverity.MODERATE: 0.8,
            EventSeverity.MAJOR: 0.6,
            EventSeverity.CATASTROPHIC: 0.3
        }.get(severity, 1.0)
        
        # Apply all modifiers
        final_probability = (weighted_probability * 
                           rarity_modifier * 
                           weight_modifier * 
                           severity_modifier)
        
        # Add random variance
        variance = random.uniform(-self.trigger_variance, self.trigger_variance)
        final_probability *= (1.0 + variance)
        
        # Cap probability
        final_probability = max(0.0, min(1.0, final_probability))
        
        
        return final_probability
    
    async def _select_and_trigger_events(self, candidates: List[Tuple[EventTemplate, float]],
                                       chaos_result: Any,
                                       chaos_state: ChaosState) -> List[ChaosEvent]:
        """Select which events to trigger from candidates"""
        triggered_events = []
        
        for template, probability in candidates:
            # Check if we've hit our concurrent event limit
            if len(self.active_events) >= self.max_concurrent_events:
                break
            
            # Check if we've hit our hourly limit
            if self.events_triggered_today >= self.max_events_per_hour:
                break
            
            # Roll for trigger
            if random.random() < probability:
                event = await self._create_and_trigger_event(
                    template, chaos_result, chaos_state
                )
                
                if event:
                    triggered_events.append(event)
                    self.events_triggered_today += 1
        
        return triggered_events
    
    async def _create_and_trigger_event(self, template: EventTemplate,
                                      chaos_result: Any,
                                      chaos_state: ChaosState) -> Optional[ChaosEvent]:
        """Create and trigger a specific event"""
        try:
            # Determine event severity and affected regions
            severity = self._determine_event_severity(chaos_result.chaos_score)
            affected_regions = self._select_affected_regions(
                template, chaos_result, chaos_state
            )
            
            # Create event from template
            event = template.create_event(
                chaos_result.chaos_score,
                severity_override=severity,
                affected_regions=affected_regions
            )
            
            # Trigger the event
            event.trigger(
                chaos_result.chaos_score,
                chaos_result.source_contributions
            )
            
            # Add to active events
            self.active_events[event.event_id] = event
            
            # Set cooldowns
            chaos_state.set_event_cooldown(
                event.event_type.value,
                event.cooldown_hours * 3600.0  # Convert to seconds
            )
            
            # Set regional cooldowns
            for region_id in event.affected_regions:
                chaos_state.set_event_cooldown(
                    event.event_type.value,
                    event.regional_cooldown_hours * 3600.0,
                    region_id
                )
            
            # Record in chaos state
            chaos_state.record_event(event.get_event_summary())
            
            
            return event
            
        except Exception as e:
            return None
    
    async def _handle_cascading_events(self, triggered_events: List[ChaosEvent],
                                     chaos_result: Any,
                                     chaos_state: ChaosState) -> List[ChaosEvent]:
        """Handle cascading secondary events"""
        cascade_events = []
        
        for event in triggered_events:
            if event.cascade_probability <= 0.0 or not event.secondary_events:
                continue
            
            # Check if cascade should happen
            cascade_chance = event.cascade_probability
            variance = random.uniform(-self.cascade_variance, self.cascade_variance)
            cascade_chance *= (1.0 + variance)
            
            if random.random() < cascade_chance:
                # Select a secondary event type
                secondary_type_str = random.choice(event.secondary_events)
                try:
                    secondary_type = ChaosEventType(secondary_type_str)
                except ValueError:
                    continue
                
                # Find template for secondary event
                secondary_template = None
                for template in self.event_templates:
                    if template.event_type == secondary_type:
                        secondary_template = template
                        break
                
                if not secondary_template:
                    continue
                
                # Check cooldowns for secondary event
                if chaos_state.is_event_on_cooldown(secondary_type.value):
                    continue
                
                # Schedule cascading event with delay
                await asyncio.sleep(event.cascade_delay_hours * 3600.0)  # Convert to seconds
                
                cascade_event = await self._create_and_trigger_event(
                    secondary_template, chaos_result, chaos_state
                )
                
                if cascade_event:
                    cascade_events.append(cascade_event)
        
        return cascade_events
    
    def _determine_event_severity(self, chaos_score: float) -> EventSeverity:
        """Determine event severity based on chaos score"""
        # Add some randomness to prevent predictability
        adjusted_score = chaos_score + random.uniform(-0.1, 0.1)
        adjusted_score = max(0.0, min(1.0, adjusted_score))
        
        if adjusted_score < 0.3:
            return EventSeverity.MINOR
        elif adjusted_score < 0.5:
            return EventSeverity.MODERATE
        elif adjusted_score < 0.8:
            return EventSeverity.MAJOR
        else:
            return EventSeverity.CATASTROPHIC
    
    def _select_affected_regions(self, template: EventTemplate,
                               chaos_result: Any,
                               chaos_state: ChaosState) -> List[Union[str, UUID]]:
        """Select which regions are affected by an event"""
        # For now, select regions with highest chaos scores
        if not chaos_result.regional_scores:
            return []
        
        # Sort regions by chaos score
        sorted_regions = sorted(
            chaos_result.regional_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Select top regions based on event severity
        event_sample = template.create_event(chaos_result.chaos_score)
        severity = self._determine_event_severity(chaos_result.chaos_score)
        
        max_regions = {
            EventSeverity.MINOR: 1,
            EventSeverity.MODERATE: 2,
            EventSeverity.MAJOR: 3,
            EventSeverity.CATASTROPHIC: 5
        }.get(severity, 1)
        
        # Take top regions but add some randomness
        num_regions = min(max_regions, len(sorted_regions))
        selected_regions = []
        
        for i in range(num_regions):
            # Higher probability for higher-scoring regions
            probability = 1.0 - (i * 0.2)  # Reduce probability for lower-ranked regions
            if random.random() < probability:
                selected_regions.append(sorted_regions[i][0])
        
        # Ensure at least one region if possible
        if not selected_regions and sorted_regions:
            selected_regions.append(sorted_regions[0][0])
        
        return selected_regions
    
    def _can_trigger_events(self) -> bool:
        """Check if we can trigger events based on rate limits"""
        # Check hourly limit
        if self.events_triggered_today >= self.max_events_per_hour:
            return False
        
        # Check concurrent limit
        if len(self.active_events) >= self.max_concurrent_events:
            return False
        
        # Check minimum time between triggers
        time_since_last = (datetime.now() - self.last_trigger_check).total_seconds()
        min_interval = 60.0  # At least 1 minute between trigger attempts
        
        if time_since_last < min_interval:
            return False
        
        self.last_trigger_check = datetime.now()
        return True
    
    def _count_concurrent_events(self, event_type: ChaosEventType) -> int:
        """Count how many events of this type are currently active"""
        count = 0
        for event in self.active_events.values():
            if event.event_type == event_type and event.is_active():
                count += 1
        return count
    
    def _cleanup_expired_events(self) -> None:
        """Remove expired events from active events"""
        expired_ids = []
        for event_id, event in self.active_events.items():
            if event.is_expired() or event.status == EventStatus.RESOLVED:
                expired_ids.append(event_id)
        
        for event_id in expired_ids:
            del self.active_events[event_id]
    
    def _reset_daily_counter_if_needed(self) -> None:
        """Reset daily event counter if it's a new day"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.events_triggered_today = 0
            self.last_reset_date = current_date
    
    def get_active_events(self) -> List[ChaosEvent]:
        """Get all currently active events"""
        return [event for event in self.active_events.values() if event.is_active()]
    
    def get_event_by_id(self, event_id: str) -> Optional[ChaosEvent]:
        """Get a specific event by ID"""
        return self.active_events.get(event_id)
    
    def force_resolve_event(self, event_id: str) -> bool:
        """Force resolve an event (for testing or admin purposes)"""
        if event_id in self.active_events:
            self.active_events[event_id].resolve()
            return True
        return False
    
    def get_trigger_statistics(self) -> Dict[str, Any]:
        """Get statistics about event triggering"""
        return {
            'events_triggered_today': self.events_triggered_today,
            'active_events_count': len(self.active_events),
            'max_events_per_hour': self.max_events_per_hour,
            'max_concurrent_events': self.max_concurrent_events,
            'active_event_types': [event.event_type.value for event in self.active_events.values()],
            'last_trigger_check': self.last_trigger_check.isoformat()
        }
    
    def _initialize_event_templates(self) -> List[EventTemplate]:
        """Initialize event templates with predefined configurations"""
        templates = []
        
        # Political Events
        templates.append(EventTemplate(
            event_type=ChaosEventType.POLITICAL_UPHEAVAL,
            base_severity=EventSeverity.MODERATE,
            base_duration_hours=48.0,
            base_cooldown_hours=168.0,  # 1 week
            title_template="Political Upheaval: {intensity} unrest",
            description_template="Political tensions have reached a breaking point, causing {intensity} upheaval",
            flavor_text_template="The political landscape shifts as factions clash for power and influence",
            immediate_effect_templates=[
                {
                    'target_system': 'faction',
                    'effect_type': 'reduce_stability',
                    'magnitude': 0.3,
                    'duration_hours': 24.0,
                    'description': 'Political instability reduces faction stability'
                }
            ],
            cascade_events=[ChaosEventType.SOCIAL_UNREST, ChaosEventType.LEADERSHIP_COUP],
            base_cascade_probability=0.3
        ))
        
        # Natural Disasters
        templates.append(EventTemplate(
            event_type=ChaosEventType.EARTHQUAKE,
            base_severity=EventSeverity.MAJOR,
            base_duration_hours=12.0,
            base_cooldown_hours=720.0,  # 30 days
            title_template="Earthquake: {intensity} tremors",
            description_template="A {intensity} earthquake has struck the region",
            flavor_text_template="The earth shakes with tremendous force, toppling structures and disrupting life",
            immediate_effect_templates=[
                {
                    'target_system': 'region',
                    'effect_type': 'damage_infrastructure',
                    'magnitude': 0.4,
                    'duration_hours': 168.0,  # 1 week
                    'description': 'Earthquake damages regional infrastructure'
                },
                {
                    'target_system': 'economy',
                    'effect_type': 'disrupt_trade',
                    'magnitude': 0.3,
                    'duration_hours': 72.0,
                    'description': 'Trade routes disrupted by earthquake damage'
                }
            ],
            cascade_events=[ChaosEventType.RESOURCE_SCARCITY, ChaosEventType.MASS_MIGRATION],
            base_cascade_probability=0.4
        ))
        
        # Economic Events
        templates.append(EventTemplate(
            event_type=ChaosEventType.ECONOMIC_COLLAPSE,
            base_severity=EventSeverity.MAJOR,
            base_duration_hours=168.0,  # 1 week
            base_cooldown_hours=2160.0,  # 90 days
            title_template="Economic Collapse: {intensity} market failure",
            description_template="The economy has suffered a {intensity} collapse",
            flavor_text_template="Markets crash and currencies tumble as economic foundations crumble",
            immediate_effect_templates=[
                {
                    'target_system': 'economy',
                    'effect_type': 'reduce_stability',
                    'magnitude': 0.6,
                    'duration_hours': 168.0,
                    'description': 'Economic systems destabilized'
                },
                {
                    'target_system': 'faction',
                    'effect_type': 'reduce_resources',
                    'magnitude': 0.4,
                    'duration_hours': 336.0,
                    'description': 'Faction resources depleted by economic crisis'
                }
            ],
            cascade_events=[ChaosEventType.SOCIAL_UNREST, ChaosEventType.POLITICAL_UPHEAVAL],
            base_cascade_probability=0.5
        ))
        
        # Military Events
        templates.append(EventTemplate(
            event_type=ChaosEventType.WAR_OUTBREAK,
            base_severity=EventSeverity.CATASTROPHIC,
            base_duration_hours=720.0,  # 30 days
            base_cooldown_hours=2160.0,  # 90 days
            title_template="War Outbreak: {intensity} conflict",
            description_template="War has broken out with {intensity} fighting",
            flavor_text_template="The drums of war sound as factions clash in devastating conflict",
            immediate_effect_templates=[
                {
                    'target_system': 'faction',
                    'effect_type': 'initiate_conflict',
                    'magnitude': 0.8,
                    'duration_hours': 720.0,
                    'description': 'Active military conflict between factions'
                },
                {
                    'target_system': 'region',
                    'effect_type': 'war_damage',
                    'magnitude': 0.5,
                    'duration_hours': 1440.0,
                    'description': 'Regional damage from warfare'
                }
            ],
            cascade_events=[ChaosEventType.MASS_MIGRATION, ChaosEventType.RESOURCE_SCARCITY],
            base_cascade_probability=0.6
        ))
        
        # Add more templates for other event types...
        # (For brevity, showing a few key examples)
        
        return templates 