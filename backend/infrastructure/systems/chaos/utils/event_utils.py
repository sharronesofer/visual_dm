"""
Event Utilities

Helper functions for managing chaos events, including filtering, sorting,
analysis, and effect application utilities.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import UUID

from backend.infrastructure.systems.chaos.models.chaos_events import (
    ChaosEvent, ChaosEventType, EventSeverity, EventStatus,
    EventEffect, EventTemplate
)
from backend.infrastructure.systems.chaos.models.chaos_state import ChaosState

logger = logging.getLogger(__name__)


class EventUtils:
    """Utility functions for event management"""
    
    @staticmethod
    def filter_events_by_status(events: List[ChaosEvent], status: EventStatus) -> List[ChaosEvent]:
        """Filter events by their status"""
        return [event for event in events if event.status == status]
    
    @staticmethod
    def filter_events_by_type(events: List[ChaosEvent], event_type: ChaosEventType) -> List[ChaosEvent]:
        """Filter events by their type"""
        return [event for event in events if event.event_type == event_type]
    
    @staticmethod
    def filter_events_by_severity(events: List[ChaosEvent], severity: EventSeverity) -> List[ChaosEvent]:
        """Filter events by their severity"""
        return [event for event in events if event.severity == severity]
    
    @staticmethod
    def filter_events_by_region(events: List[ChaosEvent], region_id: Union[str, UUID]) -> List[ChaosEvent]:
        """Filter events that affect a specific region"""
        return [event for event in events if region_id in event.affected_regions or event.global_event]
    
    @staticmethod
    def filter_active_events(events: List[ChaosEvent]) -> List[ChaosEvent]:
        """Get only currently active events"""
        return [event for event in events if event.is_active()]
    
    @staticmethod
    def filter_recent_events(events: List[ChaosEvent], hours: int = 24) -> List[ChaosEvent]:
        """Get events that occurred within the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [event for event in events if event.triggered_at and event.triggered_at >= cutoff_time]
    
    @staticmethod
    def sort_events_by_severity(events: List[ChaosEvent], descending: bool = True) -> List[ChaosEvent]:
        """Sort events by severity level"""
        severity_order = {
            EventSeverity.MINOR: 1,
            EventSeverity.MODERATE: 2,
            EventSeverity.MAJOR: 3,
            EventSeverity.CATASTROPHIC: 4
        }
        
        return sorted(events, 
                     key=lambda x: severity_order.get(x.severity, 0), 
                     reverse=descending)
    
    @staticmethod
    def sort_events_by_trigger_time(events: List[ChaosEvent], descending: bool = True) -> List[ChaosEvent]:
        """Sort events by when they were triggered"""
        return sorted(events, 
                     key=lambda x: x.triggered_at or datetime.min,
                     reverse=descending)
    
    @staticmethod
    def sort_events_by_remaining_duration(events: List[ChaosEvent], descending: bool = False) -> List[ChaosEvent]:
        """Sort events by remaining duration"""
        return sorted(events, 
                     key=lambda x: x.get_remaining_duration(),
                     reverse=descending)
    
    @staticmethod
    def get_events_by_impact_level(events: List[ChaosEvent]) -> Dict[str, List[ChaosEvent]]:
        """Group events by their impact level"""
        impact_groups = {
            'low': [],
            'medium': [],
            'high': [],
            'critical': []
        }
        
        for event in events:
            if event.severity == EventSeverity.MINOR:
                impact_groups['low'].append(event)
            elif event.severity == EventSeverity.MODERATE:
                impact_groups['medium'].append(event)
            elif event.severity == EventSeverity.MAJOR:
                impact_groups['high'].append(event)
            elif event.severity == EventSeverity.CATASTROPHIC:
                impact_groups['critical'].append(event)
        
        return impact_groups
    
    @staticmethod
    def get_events_by_region(events: List[ChaosEvent]) -> Dict[Union[str, UUID], List[ChaosEvent]]:
        """Group events by affected regions"""
        region_groups = {}
        
        for event in events:
            if event.global_event:
                if 'global' not in region_groups:
                    region_groups['global'] = []
                region_groups['global'].append(event)
            else:
                for region_id in event.affected_regions:
                    if region_id not in region_groups:
                        region_groups[region_id] = []
                    region_groups[region_id].append(event)
        
        return region_groups
    
    @staticmethod
    def calculate_total_chaos_impact(events: List[ChaosEvent]) -> float:
        """Calculate the total chaos impact from a list of events"""
        total_impact = 0.0
        
        for event in events:
            if not event.is_active():
                continue
            
            # Base impact from severity
            severity_impact = {
                EventSeverity.MINOR: 0.1,
                EventSeverity.MODERATE: 0.25,
                EventSeverity.MAJOR: 0.5,
                EventSeverity.CATASTROPHIC: 1.0
            }.get(event.severity, 0.0)
            
            # Multiply by intensity modifier
            intensity_modifier = event.get_intensity_modifier()
            
            # Account for remaining duration (events lose impact over time)
            duration_factor = min(1.0, event.get_remaining_duration() / event.duration_hours)
            
            event_impact = severity_impact * intensity_modifier * duration_factor
            total_impact += event_impact
        
        return min(1.0, total_impact)  # Cap at 1.0
    
    @staticmethod
    def get_dominant_event_types(events: List[ChaosEvent]) -> List[Tuple[ChaosEventType, int]]:
        """Get the most common event types in order of frequency"""
        type_counts = {}
        
        for event in events:
            event_type = event.event_type
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        # Sort by count (descending)
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_types
    
    @staticmethod
    def analyze_event_patterns(events: List[ChaosEvent]) -> Dict[str, Any]:
        """Analyze patterns in event occurrences"""
        if not events:
            return {
                'total_events': 0,
                'average_severity': 0.0,
                'most_common_type': None,
                'average_duration': 0.0,
                'global_vs_regional': {'global': 0, 'regional': 0}
            }
        
        # Basic statistics
        total_events = len(events)
        
        # Severity analysis
        severity_scores = {
            EventSeverity.MINOR: 1,
            EventSeverity.MODERATE: 2,
            EventSeverity.MAJOR: 3,
            EventSeverity.CATASTROPHIC: 4
        }
        
        total_severity = sum(severity_scores.get(event.severity, 1) for event in events)
        average_severity = total_severity / total_events
        
        # Most common event type
        dominant_types = EventUtils.get_dominant_event_types(events)
        most_common_type = dominant_types[0][0].value if dominant_types else None
        
        # Average duration
        durations = [event.duration_hours for event in events]
        average_duration = sum(durations) / len(durations)
        
        # Global vs regional
        global_count = sum(1 for event in events if event.global_event)
        regional_count = total_events - global_count
        
        # Cascade analysis
        events_with_cascades = sum(1 for event in events if event.cascade_probability > 0)
        cascade_rate = events_with_cascades / total_events
        
        return {
            'total_events': total_events,
            'average_severity': average_severity,
            'most_common_type': most_common_type,
            'average_duration': average_duration,
            'global_vs_regional': {
                'global': global_count,
                'regional': regional_count
            },
            'cascade_rate': cascade_rate,
            'severity_distribution': {
                severity.value: sum(1 for event in events if event.severity == severity)
                for severity in EventSeverity
            },
            'type_distribution': {
                event_type.value: count for event_type, count in dominant_types
            }
        }
    
    @staticmethod
    def check_event_conflicts(new_event: ChaosEvent, existing_events: List[ChaosEvent]) -> List[str]:
        """Check if a new event conflicts with existing events"""
        conflicts = []
        
        for existing in existing_events:
            if not existing.is_active():
                continue
            
            # Check for same type conflicts
            if (new_event.event_type == existing.event_type and 
                existing.max_concurrent <= 1):
                conflicts.append(f"Same event type already active: {existing.event_type.value}")
            
            # Check for regional conflicts for incompatible events
            incompatible_pairs = {
                ChaosEventType.EARTHQUAKE: [ChaosEventType.FLOOD, ChaosEventType.VOLCANIC_ERUPTION],
                ChaosEventType.WAR_OUTBREAK: [ChaosEventType.POLITICAL_UPHEAVAL],
                ChaosEventType.ECONOMIC_COLLAPSE: [ChaosEventType.MARKET_CRASH]
            }
            
            if new_event.event_type in incompatible_pairs:
                incompatible_types = incompatible_pairs[new_event.event_type]
                if existing.event_type in incompatible_types:
                    # Check if they affect the same regions
                    overlapping_regions = set(new_event.affected_regions) & set(existing.affected_regions)
                    if overlapping_regions or (new_event.global_event and existing.global_event):
                        conflicts.append(
                            f"Incompatible event types in same region: "
                            f"{new_event.event_type.value} vs {existing.event_type.value}"
                        )
        
        return conflicts
    
    @staticmethod
    def calculate_event_priority(event: ChaosEvent, chaos_state: ChaosState) -> float:
        """Calculate priority score for event processing"""
        priority = 0.0
        
        # Base priority from severity
        severity_priorities = {
            EventSeverity.MINOR: 1.0,
            EventSeverity.MODERATE: 2.0,
            EventSeverity.MAJOR: 3.0,
            EventSeverity.CATASTROPHIC: 4.0
        }
        priority += severity_priorities.get(event.severity, 1.0)
        
        # Higher priority for events about to expire
        remaining_ratio = event.get_remaining_duration() / event.duration_hours
        if remaining_ratio < 0.2:  # Less than 20% time remaining
            priority += 2.0
        
        # Higher priority for global events
        if event.global_event:
            priority += 1.0
        
        # Higher priority for events affecting many regions
        priority += len(event.affected_regions) * 0.1
        
        # Higher priority for cascading events
        if event.cascade_probability > 0.3:
            priority += 1.0
        
        return priority
    
    @staticmethod
    def get_event_impact_summary(events: List[ChaosEvent]) -> Dict[str, Any]:
        """Get a summary of event impacts across different systems"""
        system_impacts = {}
        
        for event in events:
            if not event.is_active():
                continue
            
            # Analyze immediate effects
            for effect in event.immediate_effects:
                system = effect.target_system
                if system not in system_impacts:
                    system_impacts[system] = {
                        'total_magnitude': 0.0,
                        'effect_count': 0,
                        'effect_types': set()
                    }
                
                system_impacts[system]['total_magnitude'] += effect.magnitude
                system_impacts[system]['effect_count'] += 1
                system_impacts[system]['effect_types'].add(effect.effect_type)
            
            # Analyze ongoing effects
            for effect in event.ongoing_effects:
                system = effect.target_system
                if system not in system_impacts:
                    system_impacts[system] = {
                        'total_magnitude': 0.0,
                        'effect_count': 0,
                        'effect_types': set()
                    }
                
                # Weight ongoing effects by remaining time
                time_factor = min(1.0, effect.duration_hours / 24.0)  # Normalize to 24 hours
                weighted_magnitude = effect.magnitude * time_factor
                
                system_impacts[system]['total_magnitude'] += weighted_magnitude
                system_impacts[system]['effect_count'] += 1
                system_impacts[system]['effect_types'].add(effect.effect_type)
        
        # Convert sets to lists for JSON serialization
        for system_data in system_impacts.values():
            system_data['effect_types'] = list(system_data['effect_types'])
        
        return system_impacts
    
    @staticmethod
    def recommend_mitigation_strategies(events: List[ChaosEvent]) -> List[Dict[str, Any]]:
        """Recommend strategies to mitigate the impact of active events"""
        strategies = []
        
        # Group events by type for targeted mitigation
        type_groups = {}
        for event in events:
            if not event.is_active():
                continue
            
            event_type = event.event_type
            if event_type not in type_groups:
                type_groups[event_type] = []
            type_groups[event_type].append(event)
        
        # Generate type-specific mitigation strategies
        for event_type, type_events in type_groups.items():
            total_severity = sum(
                4 if event.severity == EventSeverity.CATASTROPHIC else
                3 if event.severity == EventSeverity.MAJOR else
                2 if event.severity == EventSeverity.MODERATE else 1
                for event in type_events
            )
            
            if event_type == ChaosEventType.ECONOMIC_COLLAPSE:
                strategies.append({
                    'type': 'economic_stabilization',
                    'priority': total_severity * 0.8,
                    'description': 'Implement emergency economic measures',
                    'cost': total_severity * 100,
                    'effectiveness': 0.7,
                    'duration_days': 30
                })
            
            elif event_type == ChaosEventType.POLITICAL_UPHEAVAL:
                strategies.append({
                    'type': 'diplomatic_intervention',
                    'priority': total_severity * 0.9,
                    'description': 'Deploy diplomatic teams to negotiate peace',
                    'cost': total_severity * 150,
                    'effectiveness': 0.6,
                    'duration_days': 20
                })
            
            elif event_type == ChaosEventType.NATURAL_DISASTER:
                strategies.append({
                    'type': 'disaster_relief',
                    'priority': total_severity * 1.0,
                    'description': 'Provide emergency aid and reconstruction',
                    'cost': total_severity * 200,
                    'effectiveness': 0.8,
                    'duration_days': 60
                })
        
        # Sort by priority
        strategies.sort(key=lambda x: x['priority'], reverse=True)
        
        return strategies[:5]  # Return top 5 strategies

    @staticmethod
    def create_event_from_type(event_type: ChaosEventType, event_data: Dict[str, Any]) -> ChaosEvent:
        """Create a ChaosEvent from event type and data"""
        from uuid import uuid4
        
        # Extract required fields
        severity = event_data.get('severity', EventSeverity.MODERATE)
        affected_regions = event_data.get('affected_regions', [])
        chaos_score_trigger = event_data.get('chaos_score_trigger', 0.5)
        
        # Generate event details based on type
        title = EventUtils._generate_event_title(event_type, severity)
        description = EventUtils._generate_event_description(event_type, severity, event_data)
        
        # Create the event
        event = ChaosEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            severity=severity,
            status=EventStatus.PENDING,
            title=title,
            description=description,
            affected_regions=affected_regions,
            triggered_at=datetime.now(),
            chaos_score_at_trigger=chaos_score_trigger,
            duration_hours=EventUtils._calculate_duration_hours(event_type, severity),
            global_event=len(affected_regions) == 0
        )
        
        return event
    
    @staticmethod
    def validate_event_data(event_data: Dict[str, Any]) -> bool:
        """Validate event data for required fields and proper types"""
        required_fields = ['event_type', 'severity', 'affected_regions', 'chaos_score_trigger']
        
        # Check for required fields
        for field in required_fields:
            if field not in event_data:
                return False
        
        # Validate event_type
        if not isinstance(event_data['event_type'], ChaosEventType):
            return False
        
        # Validate severity
        if not isinstance(event_data['severity'], EventSeverity):
            return False
        
        # Validate affected_regions
        if not isinstance(event_data['affected_regions'], list):
            return False
        
        # Validate chaos_score_trigger
        trigger = event_data['chaos_score_trigger']
        if not isinstance(trigger, (int, float)) or not (0.0 <= trigger <= 1.0):
            return False
        
        return True
    
    @staticmethod
    def calculate_event_impact(event: ChaosEvent) -> Dict[str, Any]:
        """Calculate the impact of an event"""
        # Severity multiplier
        severity_multipliers = {
            EventSeverity.MINOR: 1.0,
            EventSeverity.MODERATE: 2.0,
            EventSeverity.MAJOR: 4.0,
            EventSeverity.CRITICAL: 6.0,
            EventSeverity.CATASTROPHIC: 10.0
        }
        severity_multiplier = severity_multipliers.get(event.severity, 1.0)
        
        # Regional impact (number of regions affected)
        if event.global_event:
            regional_impact = 10.0  # Global events have maximum regional impact
        else:
            regional_impact = len(event.affected_regions)
        
        # Duration factor (longer events have more impact)
        duration_factor = min(5.0, event.duration_hours / 24.0)  # Cap at 5x for very long events
        
        # Overall impact score
        impact_score = severity_multiplier * regional_impact * duration_factor
        
        return {
            'severity_multiplier': severity_multiplier,
            'regional_impact': regional_impact,
            'duration_factor': duration_factor,
            'overall_impact': impact_score,
            'impact_level': EventUtils._categorize_impact_level(impact_score)
        }
    
    @staticmethod
    def get_event_cooldown_duration(event_type: ChaosEventType, severity: EventSeverity) -> timedelta:
        """Calculate cooldown duration for an event type and severity"""
        # Base cooldown hours by event type
        base_cooldowns = {
            ChaosEventType.POLITICAL_UPHEAVAL: 48,
            ChaosEventType.ECONOMIC_COLLAPSE: 72,
            ChaosEventType.NATURAL_DISASTER: 24,
            ChaosEventType.WAR_OUTBREAK: 168,  # 1 week
            ChaosEventType.FACTION_BETRAYAL: 96,
            ChaosEventType.PLAGUE: 120,
            ChaosEventType.RESOURCE_SCARCITY: 60,
            ChaosEventType.CHARACTER_REVELATION: 36
        }
        
        base_hours = base_cooldowns.get(event_type, 48)  # Default 48 hours
        
        # Severity multipliers
        severity_multipliers = {
            EventSeverity.MINOR: 0.5,
            EventSeverity.MODERATE: 1.0,
            EventSeverity.MAJOR: 1.5,
            EventSeverity.CRITICAL: 2.0,
            EventSeverity.CATASTROPHIC: 3.0
        }
        
        multiplier = severity_multipliers.get(severity, 1.0)
        cooldown_hours = base_hours * multiplier
        
        return timedelta(hours=cooldown_hours)
    
    @staticmethod
    def format_event_description(event: ChaosEvent) -> str:
        """Format an event description for display"""
        severity_names = {
            EventSeverity.MINOR: "Minor",
            EventSeverity.MODERATE: "Moderate", 
            EventSeverity.MAJOR: "Major",
            EventSeverity.CRITICAL: "Critical",
            EventSeverity.CATASTROPHIC: "Catastrophic"
        }
        
        severity_name = severity_names.get(event.severity, "Unknown")
        regions_str = ", ".join(str(r) for r in event.affected_regions) if event.affected_regions else "Global"
        
        # Include both severity name and numeric value for test compatibility
        formatted = f"[{severity_name}] {event.title} (Region: {regions_str}) - {event.description}"
        formatted += f" (Severity: {event.severity.value})"
        
        return formatted
    
    # Helper methods
    @staticmethod
    def _generate_event_title(event_type: ChaosEventType, severity: EventSeverity) -> str:
        """Generate a title for an event"""
        titles = {
            ChaosEventType.POLITICAL_UPHEAVAL: "Political Upheaval",
            ChaosEventType.ECONOMIC_COLLAPSE: "Economic Crisis",
            ChaosEventType.NATURAL_DISASTER: "Natural Disaster",
            ChaosEventType.WAR_OUTBREAK: "War Outbreak",
            ChaosEventType.FACTION_BETRAYAL: "Faction Betrayal",
            ChaosEventType.PLAGUE: "Plague Outbreak",
            ChaosEventType.RESOURCE_SCARCITY: "Resource Crisis",
            ChaosEventType.CHARACTER_REVELATION: "Character Revelation",
            ChaosEventType.EARTHQUAKE: "Earthquake",
            ChaosEventType.FLOOD: "Flood",
            ChaosEventType.DROUGHT: "Drought",
            ChaosEventType.MARKET_CRASH: "Market Crash",
            ChaosEventType.REBELLION: "Rebellion",
            ChaosEventType.SOCIAL_UNREST: "Social Unrest"
        }
        
        base_title = titles.get(event_type, "Unknown Event")
        
        if severity == EventSeverity.CATASTROPHIC:
            return f"Catastrophic {base_title}"
        elif severity == EventSeverity.CRITICAL:
            return f"Critical {base_title}"
        elif severity == EventSeverity.MAJOR:
            return f"Major {base_title}"
        else:
            return base_title
    
    @staticmethod
    def _generate_event_description(event_type: ChaosEventType, severity: EventSeverity, data: Dict[str, Any]) -> str:
        """Generate a description for an event"""
        descriptions = {
            ChaosEventType.POLITICAL_UPHEAVAL: "Political tensions have reached a breaking point",
            ChaosEventType.ECONOMIC_COLLAPSE: "Economic instability is causing widespread disruption",
            ChaosEventType.NATURAL_DISASTER: "A natural disaster has struck the region",
            ChaosEventType.WAR_OUTBREAK: "Armed conflict has erupted",
            ChaosEventType.FACTION_BETRAYAL: "A faction has betrayed their allies",
            ChaosEventType.PLAGUE: "A disease outbreak is spreading",
            ChaosEventType.RESOURCE_SCARCITY: "Critical resources are becoming scarce",
            ChaosEventType.CHARACTER_REVELATION: "Important information has been revealed",
            ChaosEventType.EARTHQUAKE: "A powerful earthquake has shaken the region",
            ChaosEventType.FLOOD: "Devastating floods have inundated the area",
            ChaosEventType.DROUGHT: "A severe drought is affecting the region",
            ChaosEventType.MARKET_CRASH: "Financial markets are in freefall",
            ChaosEventType.REBELLION: "A rebellion has begun against the established order",
            ChaosEventType.SOCIAL_UNREST: "Social tensions have erupted into unrest"
        }
        
        return descriptions.get(event_type, "An unknown event has occurred")
    
    @staticmethod
    def _calculate_duration_hours(event_type: ChaosEventType, severity: EventSeverity) -> float:
        """Calculate event duration in hours"""
        base_durations = {
            ChaosEventType.POLITICAL_UPHEAVAL: 72,
            ChaosEventType.ECONOMIC_COLLAPSE: 168,
            ChaosEventType.NATURAL_DISASTER: 48,
            ChaosEventType.WAR_OUTBREAK: 336,  # 2 weeks
            ChaosEventType.FACTION_BETRAYAL: 120,
            ChaosEventType.PLAGUE: 240,
            ChaosEventType.RESOURCE_SCARCITY: 96,
            ChaosEventType.CHARACTER_REVELATION: 60,
            ChaosEventType.EARTHQUAKE: 24,
            ChaosEventType.FLOOD: 72,
            ChaosEventType.DROUGHT: 720,  # 30 days
            ChaosEventType.MARKET_CRASH: 48,
            ChaosEventType.REBELLION: 168,
            ChaosEventType.SOCIAL_UNREST: 48
        }
        
        base = base_durations.get(event_type, 72)
        
        severity_multipliers = {
            EventSeverity.MINOR: 0.5,
            EventSeverity.MODERATE: 1.0,
            EventSeverity.MAJOR: 1.5,
            EventSeverity.CRITICAL: 2.0,
            EventSeverity.CATASTROPHIC: 3.0
        }
        
        multiplier = severity_multipliers.get(severity, 1.0)
        return base * multiplier
    
    @staticmethod
    def _calculate_intensity_modifier(severity: EventSeverity) -> float:
        """Calculate intensity modifier based on severity"""
        modifiers = {
            EventSeverity.MINOR: 0.3,
            EventSeverity.MODERATE: 0.6,
            EventSeverity.MAJOR: 1.0,
            EventSeverity.CRITICAL: 1.5,
            EventSeverity.CATASTROPHIC: 2.0
        }
        return modifiers.get(severity, 1.0)
    
    @staticmethod
    def _categorize_impact_level(impact_score: float) -> str:
        """Categorize impact score into readable levels"""
        if impact_score < 5:
            return "Low"
        elif impact_score < 15:
            return "Moderate"
        elif impact_score < 30:
            return "High"
        elif impact_score < 50:
            return "Severe"
        else:
            return "Catastrophic" 