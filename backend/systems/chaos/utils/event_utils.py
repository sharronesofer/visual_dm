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

from backend.systems.chaos.models.chaos_events import (
    ChaosEvent, ChaosEventType, EventSeverity, EventStatus,
    EventEffect, EventTemplate
)
from backend.systems.chaos.models.chaos_state import ChaosState

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
        """Recommend mitigation strategies based on active events"""
        recommendations = []
        
        # Analyze event patterns
        patterns = EventUtils.analyze_event_patterns(events)
        active_events = EventUtils.filter_active_events(events)
        
        if not active_events:
            return recommendations
        
        # Get most severe events
        severe_events = [e for e in active_events if e.severity in [EventSeverity.MAJOR, EventSeverity.CATASTROPHIC]]
        
        if severe_events:
            recommendations.append({
                'strategy': 'Emergency Response',
                'priority': 'high',
                'description': f'Address {len(severe_events)} severe events immediately',
                'target_events': [e.event_id for e in severe_events],
                'actions': [
                    'Deploy emergency resources to affected regions',
                    'Activate crisis management protocols',
                    'Coordinate with faction leaders for stability measures'
                ]
            })
        
        # Analyze most common event type
        if patterns['most_common_type']:
            event_type = patterns['most_common_type']
            type_specific_recommendations = {
                'political_upheaval': {
                    'strategy': 'Political Stabilization',
                    'actions': [
                        'Initiate diplomatic negotiations',
                        'Strengthen government institutions',
                        'Address underlying political grievances'
                    ]
                },
                'economic_collapse': {
                    'strategy': 'Economic Recovery',
                    'actions': [
                        'Inject emergency funding into markets',
                        'Stabilize currency exchange rates',
                        'Support critical industries'
                    ]
                },
                'natural_disaster': {
                    'strategy': 'Disaster Relief',
                    'actions': [
                        'Deploy humanitarian aid',
                        'Rebuild critical infrastructure',
                        'Establish temporary shelters'
                    ]
                }
            }
            
            category = 'natural_disaster' if event_type in ['earthquake', 'flood', 'drought'] else event_type
            if category in type_specific_recommendations:
                recommendation = type_specific_recommendations[category].copy()
                recommendation['priority'] = 'medium'
                recommendation['description'] = f'Address recurring {event_type} events'
                recommendations.append(recommendation)
        
        # Regional concentration recommendations
        regional_events = EventUtils.get_events_by_region(active_events)
        for region_id, region_events in regional_events.items():
            if len(region_events) >= 2 and region_id != 'global':
                recommendations.append({
                    'strategy': 'Regional Focus',
                    'priority': 'medium',
                    'description': f'Multiple events concentrated in region {region_id}',
                    'target_region': region_id,
                    'actions': [
                        'Allocate additional resources to region',
                        'Establish regional crisis center',
                        'Coordinate cross-event response'
                    ]
                })
        
        return recommendations 