"""
Event Helpers

Helper functions for chaos event creation and management.
Provides utilities for event generation, validation, and processing.
"""

import logging
import random
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from uuid import UUID

from backend.systems.chaos.models.chaos_events import ChaosEvent, ChaosEventType, EventSeverity
from backend.systems.chaos.models.pressure_data import PressureData

logger = logging.getLogger(__name__)

class EventHelpers:
    """
    Utility class providing helper functions for chaos event management.
    
    This class contains static methods for event processing, validation,
    coordination, and analysis.
    """
    
    @staticmethod
    def calculate_event_probability(
        chaos_score: float,
        event_type: ChaosEventType,
        pressure_data: PressureData,
        base_probability: float = 0.1
    ) -> float:
        """
        Calculate the probability of a specific event type triggering.
        
        Args:
            chaos_score: Current chaos score (0.0 to 1.0)
            event_type: Type of event to calculate probability for
            pressure_data: Current pressure data
            base_probability: Base probability before adjustments
            
        Returns:
            Probability of event triggering (0.0 to 1.0)
        """
        # Map event types to pressure sources
        event_pressure_mapping = {
            ChaosEventType.POLITICAL_UPHEAVAL: ['faction_conflict', 'diplomatic_tension'],
            ChaosEventType.ECONOMIC_COLLAPSE: ['economic_instability', 'trade_disruption'],
            ChaosEventType.WAR_OUTBREAK: ['military_buildup', 'faction_conflict'],
            ChaosEventType.RESOURCE_SCARCITY: ['population_stress', 'environmental_pressure'],
            ChaosEventType.FACTION_BETRAYAL: ['faction_conflict', 'diplomatic_tension'],
            ChaosEventType.SOCIAL_UNREST: ['population_stress', 'economic_instability']
        }
        
        # Get relevant pressure sources for this event type
        relevant_sources = event_pressure_mapping.get(event_type, [])
        
        # Calculate pressure contribution
        pressure_contribution = 0.0
        if relevant_sources:
            total_pressure = sum(
                pressure_data.pressure_sources.get(source, 0.0)
                for source in relevant_sources
            )
            pressure_contribution = total_pressure / len(relevant_sources)
        
        # Calculate final probability
        chaos_multiplier = 1.0 + (chaos_score * 2.0)  # Chaos score amplifies probability
        pressure_multiplier = 1.0 + pressure_contribution
        
        final_probability = base_probability * chaos_multiplier * pressure_multiplier
        
        return min(1.0, final_probability)
    
    @staticmethod
    def determine_event_severity(
        chaos_score: float,
        pressure_intensity: float,
        regional_factors: Optional[Dict[str, Any]] = None
    ) -> EventSeverity:
        """
        Determine the appropriate severity level for an event.
        
        Args:
            chaos_score: Current chaos score
            pressure_intensity: Intensity of pressure causing the event
            regional_factors: Optional regional modifying factors
            
        Returns:
            Appropriate event severity level
        """
        # Base severity calculation
        combined_intensity = (chaos_score + pressure_intensity) / 2.0
        
        # Apply regional modifiers
        if regional_factors:
            population_modifier = regional_factors.get('population_density', 1.0)
            stability_modifier = regional_factors.get('stability_factor', 1.0)
            combined_intensity *= population_modifier * (2.0 - stability_modifier)
        
        # Determine severity thresholds
        if combined_intensity < 0.3:
            return EventSeverity.MINOR
        elif combined_intensity < 0.6:
            return EventSeverity.MODERATE
        elif combined_intensity < 0.85:
            return EventSeverity.MAJOR
        else:
            return EventSeverity.CATASTROPHIC
    
    @staticmethod
    def calculate_event_duration(
        event_type: ChaosEventType,
        severity: EventSeverity,
        base_duration_hours: float = 24.0
    ) -> float:
        """
        Calculate appropriate duration for an event based on type and severity.
        
        Args:
            event_type: Type of chaos event
            severity: Severity level of the event
            base_duration_hours: Base duration before modifiers
            
        Returns:
            Duration in hours
        """
        # Event type duration modifiers
        type_modifiers = {
            ChaosEventType.POLITICAL_UPHEAVAL: 2.0,
            ChaosEventType.ECONOMIC_COLLAPSE: 3.0,
            ChaosEventType.WAR_OUTBREAK: 4.0,
            ChaosEventType.NATURAL_DISASTER: 1.5,
            ChaosEventType.RESOURCE_SCARCITY: 2.5,
            ChaosEventType.FACTION_BETRAYAL: 1.0,
            ChaosEventType.SOCIAL_UNREST: 1.5
        }
        
        # Severity duration modifiers
        severity_modifiers = {
            EventSeverity.MINOR: 0.5,
            EventSeverity.MODERATE: 1.0,
            EventSeverity.MAJOR: 2.0,
            EventSeverity.CATASTROPHIC: 4.0
        }
        
        type_modifier = type_modifiers.get(event_type, 1.0)
        severity_modifier = severity_modifiers.get(severity, 1.0)
        
        return base_duration_hours * type_modifier * severity_modifier
    
    @staticmethod
    def get_cascade_events(
        triggering_event: ChaosEvent,
        current_pressure: PressureData,
        cascade_probability: float = 0.3
    ) -> List[ChaosEventType]:
        """
        Determine what events might cascade from a triggering event.
        
        Args:
            triggering_event: The event that might cause cascades
            current_pressure: Current pressure state
            cascade_probability: Base probability of cascading
            
        Returns:
            List of event types that might cascade
        """
        # Define cascade relationships
        cascade_mapping = {
            ChaosEventType.POLITICAL_UPHEAVAL: [
                ChaosEventType.SOCIAL_UNREST,
                ChaosEventType.ECONOMIC_COLLAPSE
            ],
            ChaosEventType.ECONOMIC_COLLAPSE: [
                ChaosEventType.SOCIAL_UNREST,
                ChaosEventType.RESOURCE_SCARCITY,
                ChaosEventType.POLITICAL_UPHEAVAL
            ],
            ChaosEventType.WAR_OUTBREAK: [
                ChaosEventType.RESOURCE_SCARCITY,
                ChaosEventType.ECONOMIC_COLLAPSE,
                ChaosEventType.SOCIAL_UNREST
            ],
            ChaosEventType.NATURAL_DISASTER: [
                ChaosEventType.RESOURCE_SCARCITY,
                ChaosEventType.SOCIAL_UNREST
            ],
            ChaosEventType.FACTION_BETRAYAL: [
                ChaosEventType.WAR_OUTBREAK,
                ChaosEventType.POLITICAL_UPHEAVAL
            ]
        }
        
        potential_cascades = cascade_mapping.get(triggering_event.event_type, [])
        
        # Filter based on current pressure and probability
        likely_cascades = []
        for cascade_type in potential_cascades:
            # Calculate cascade probability based on relevant pressure
            cascade_prob = EventHelpers.calculate_event_probability(
                triggering_event.chaos_score_at_trigger,
                cascade_type,
                current_pressure,
                cascade_probability
            )
            
            # Include if probability is above threshold
            if cascade_prob > 0.4:  # 40% threshold for cascading
                likely_cascades.append(cascade_type)
        
        return likely_cascades
    
    @staticmethod
    def calculate_regional_impact(
        event: ChaosEvent,
        region_data: Dict[Union[str, UUID], Dict[str, Any]]
    ) -> Dict[Union[str, UUID], float]:
        """
        Calculate the impact of an event on different regions.
        
        Args:
            event: The chaos event
            region_data: Data about regions (population, stability, etc.)
            
        Returns:
            Dict mapping region IDs to impact scores (0.0 to 1.0)
        """
        regional_impacts = {}
        
        for region_id, data in region_data.items():
            # Base impact from event severity
            base_impact = {
                EventSeverity.MINOR: 0.2,
                EventSeverity.MODERATE: 0.4,
                EventSeverity.MAJOR: 0.7,
                EventSeverity.CATASTROPHIC: 1.0
            }.get(event.severity, 0.4)
            
            # Modify based on regional factors
            population_factor = min(2.0, data.get('population_density', 1.0))
            stability_factor = data.get('stability', 1.0)
            distance_factor = data.get('distance_from_epicenter', 1.0)
            
            # Calculate final impact
            regional_impact = base_impact * population_factor * (2.0 - stability_factor) / distance_factor
            regional_impacts[region_id] = min(1.0, regional_impact)
        
        return regional_impacts
    
    @staticmethod
    def validate_event_conditions(
        event_type: ChaosEventType,
        current_state: Dict[str, Any],
        active_events: List[ChaosEvent]
    ) -> bool:
        """
        Validate whether conditions are appropriate for triggering an event.
        
        Args:
            event_type: Type of event to validate
            current_state: Current game state
            active_events: Currently active events
            
        Returns:
            True if conditions are met for triggering
        """
        # Check for conflicting events
        conflicting_events = {
            ChaosEventType.POLITICAL_UPHEAVAL: [ChaosEventType.POLITICAL_UPHEAVAL],
            ChaosEventType.WAR_OUTBREAK: [ChaosEventType.WAR_OUTBREAK],
            ChaosEventType.ECONOMIC_COLLAPSE: [ChaosEventType.ECONOMIC_COLLAPSE]
        }
        
        conflicts = conflicting_events.get(event_type, [])
        for active_event in active_events:
            if active_event.event_type in conflicts:
                return False
        
        # Check state-specific conditions
        if event_type == ChaosEventType.WAR_OUTBREAK:
            # Need at least 2 factions with tension
            faction_tensions = current_state.get('faction_tensions', {})
            high_tension_factions = sum(1 for tension in faction_tensions.values() if tension > 0.7)
            if high_tension_factions < 2:
                return False
        
        elif event_type == ChaosEventType.RESOURCE_SCARCITY:
            # Check resource levels
            resource_levels = current_state.get('resource_levels', {})
            low_resources = sum(1 for level in resource_levels.values() if level < 0.3)
            if low_resources == 0:
                return False
        
        return True
    
    @staticmethod
    def format_event_description(
        event: ChaosEvent,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a formatted description for an event.
        
        Args:
            event: The chaos event
            context: Optional context for description customization
            
        Returns:
            Formatted event description
        """
        severity_adjectives = {
            EventSeverity.MINOR: "minor",
            EventSeverity.MODERATE: "significant",
            EventSeverity.MAJOR: "severe",
            EventSeverity.CATASTROPHIC: "catastrophic"
        }
        
        severity_adj = severity_adjectives.get(event.severity, "significant")
        
        # Base description templates
        templates = {
            ChaosEventType.POLITICAL_UPHEAVAL: f"A {severity_adj} political crisis has erupted",
            ChaosEventType.ECONOMIC_COLLAPSE: f"A {severity_adj} economic downturn has begun",
            ChaosEventType.WAR_OUTBREAK: f"A {severity_adj} military conflict has started",
            ChaosEventType.NATURAL_DISASTER: f"A {severity_adj} natural disaster has struck",
            ChaosEventType.RESOURCE_SCARCITY: f"A {severity_adj} resource shortage has developed",
            ChaosEventType.FACTION_BETRAYAL: f"A {severity_adj} betrayal has been revealed",
            ChaosEventType.SOCIAL_UNREST: f"A {severity_adj} social uprising has emerged"
        }
        
        base_description = templates.get(
            event.event_type,
            f"A {severity_adj} chaos event has occurred"
        )
        
        # Add regional context if available
        if event.affected_regions and context:
            region_names = context.get('region_names', {})
            if len(event.affected_regions) == 1:
                region_name = region_names.get(str(event.affected_regions[0]), "the region")
                base_description += f" in {region_name}"
            elif len(event.affected_regions) > 1:
                base_description += f" across {len(event.affected_regions)} regions"
        
        return base_description
    
    @staticmethod
    def calculate_event_cooldown(
        event_type: ChaosEventType,
        severity: EventSeverity,
        base_cooldown_hours: float = 72.0
    ) -> float:
        """
        Calculate appropriate cooldown period for an event.
        
        Args:
            event_type: Type of event
            severity: Severity of the event
            base_cooldown_hours: Base cooldown before modifiers
            
        Returns:
            Cooldown period in hours
        """
        # Event type cooldown modifiers
        type_modifiers = {
            ChaosEventType.POLITICAL_UPHEAVAL: 2.0,
            ChaosEventType.ECONOMIC_COLLAPSE: 3.0,
            ChaosEventType.WAR_OUTBREAK: 4.0,
            ChaosEventType.NATURAL_DISASTER: 1.0,
            ChaosEventType.RESOURCE_SCARCITY: 1.5,
            ChaosEventType.FACTION_BETRAYAL: 2.0,
            ChaosEventType.SOCIAL_UNREST: 1.0
        }
        
        # Severity cooldown modifiers
        severity_modifiers = {
            EventSeverity.MINOR: 0.5,
            EventSeverity.MODERATE: 1.0,
            EventSeverity.MAJOR: 1.5,
            EventSeverity.CATASTROPHIC: 2.0
        }
        
        type_modifier = type_modifiers.get(event_type, 1.0)
        severity_modifier = severity_modifiers.get(severity, 1.0)
        
        return base_cooldown_hours * type_modifier * severity_modifier 