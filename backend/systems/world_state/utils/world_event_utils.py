"""
World_State system - World Event Utils.

Utilities for creating and managing world events.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4

from backend.systems.world_state.world_types import StateCategory, WorldRegion

logger = logging.getLogger(__name__)


def create_world_event(
    event_type: str,
    description: str,
    category: Optional[StateCategory] = None,
    region: Optional[WorldRegion] = None,
    entity_id: Optional[str] = None,
    severity: int = 1,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized world event.
    
    Args:
        event_type: Type of event (e.g., "faction_change", "economic_shift")
        description: Human-readable description of the event
        category: Optional category for the event
        region: Optional region where the event occurred
        entity_id: Optional ID of the entity involved
        severity: Event severity level (1-10, higher = more important)
        metadata: Additional event-specific data
        
    Returns:
        Dictionary representing the world event
    """
    event = {
        "id": str(uuid4()),
        "type": event_type,
        "description": description,
        "timestamp": datetime.utcnow().isoformat(),
        "severity": max(1, min(10, severity)),  # Clamp between 1-10
        "metadata": metadata or {}
    }
    
    if category:
        event["category"] = category.value if hasattr(category, 'value') else str(category)
    
    if region:
        event["region"] = region.value if hasattr(region, 'value') else str(region)
        
    if entity_id:
        event["entity_id"] = entity_id
    
    logger.debug(f"Created world event: {event_type} in {region} with severity {severity}")
    return event


def filter_events_by_visibility(
    events: List[Dict[str, Any]],
    player_region: Optional[str] = None,
    player_knowledge_level: int = 1,
    max_events: int = 50
) -> List[Dict[str, Any]]:
    """
    Filter events based on what a player should realistically know.
    
    Args:
        events: List of world events to filter
        player_region: Player's current region (affects visibility)
        player_knowledge_level: Player's information network quality (1-10)
        max_events: Maximum number of events to return
        
    Returns:
        Filtered list of events the player should know about
    """
    filtered_events = []
    
    for event in events:
        # Calculate visibility score
        visibility_score = _calculate_event_visibility(
            event, player_region, player_knowledge_level
        )
        
        # Only include events that meet the visibility threshold
        if visibility_score > 0:
            event_copy = event.copy()
            event_copy["visibility_score"] = visibility_score
            filtered_events.append(event_copy)
    
    # Sort by relevance (combination of severity and visibility)
    filtered_events.sort(
        key=lambda e: (e["severity"] * e["visibility_score"]),
        reverse=True
    )
    
    return filtered_events[:max_events]


def _calculate_event_visibility(
    event: Dict[str, Any],
    player_region: Optional[str],
    knowledge_level: int
) -> float:
    """
    Calculate how visible an event should be to a player.
    
    Returns:
        Float between 0.0 and 1.0 representing visibility
    """
    base_visibility = 0.1  # Minimum visibility for any event
    
    # Higher severity events are more visible
    severity_bonus = event.get("severity", 1) / 10.0
    
    # Events in player's region are more visible
    region_bonus = 0.0
    event_region = event.get("region")
    if event_region and player_region and event_region == player_region:
        region_bonus = 0.5
    elif event_region == "global":
        region_bonus = 0.3
    
    # Player knowledge level affects visibility
    knowledge_bonus = knowledge_level / 10.0
    
    # Some event types are naturally more visible
    event_type = event.get("type", "")
    type_bonus = 0.0
    if "political" in event_type or "war" in event_type:
        type_bonus = 0.2
    elif "economic" in event_type:
        type_bonus = 0.1
    
    total_visibility = min(1.0, base_visibility + severity_bonus + region_bonus + knowledge_bonus + type_bonus)
    return total_visibility


def format_event_for_newspaper(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Format a world event as a newspaper article.
    
    Args:
        event: World event dictionary
        
    Returns:
        Dictionary with headline, body, byline, and date
    """
    event_type = event.get("type", "unknown")
    description = event.get("description", "An event occurred.")
    region = event.get("region", "the world")
    timestamp = event.get("timestamp", datetime.utcnow().isoformat())
    
    # Generate headline based on event type
    headline = _generate_headline(event_type, region, event.get("severity", 1))
    
    # Create article body
    body = f"{description}"
    
    # Add context from metadata if available
    metadata = event.get("metadata", {})
    if metadata:
        if "old_value" in metadata and "new_value" in metadata:
            body += f" The change was from {metadata['old_value']} to {metadata['new_value']}."
        if "affected_entities" in metadata:
            entities = metadata["affected_entities"]
            if isinstance(entities, list) and entities:
                body += f" This affects {', '.join(str(e) for e in entities)}."
    
    return {
        "headline": headline,
        "body": body,
        "byline": "World Affairs Correspondent",
        "date": timestamp
    }


def _generate_headline(event_type: str, region: str, severity: int) -> str:
    """Generate an appropriate headline for an event."""
    intensity = "Minor"
    if severity >= 7:
        intensity = "Major"
    elif severity >= 4:
        intensity = "Significant"
    
    if "faction" in event_type:
        return f"{intensity} Faction Activity Reported in {region.title()}"
    elif "economic" in event_type:
        return f"{intensity} Economic Changes in {region.title()}"
    elif "political" in event_type:
        return f"{intensity} Political Developments in {region.title()}"
    elif "military" in event_type:
        return f"{intensity} Military Activity in {region.title()}"
    elif "population" in event_type:
        return f"Population Changes Noted in {region.title()}"
    else:
        return f"{intensity} Event Reported in {region.title()}"


def aggregate_similar_events(events: List[Dict[str, Any]], time_window_hours: int = 24) -> List[Dict[str, Any]]:
    """
    Aggregate similar events that occurred within a time window.
    
    Args:
        events: List of events to potentially aggregate
        time_window_hours: Time window for considering events similar
        
    Returns:
        List of events with similar ones aggregated
    """
    if not events:
        return []
    
    # Sort events by timestamp
    sorted_events = sorted(events, key=lambda e: e.get("timestamp", ""))
    aggregated = []
    current_group = [sorted_events[0]]
    
    for event in sorted_events[1:]:
        if _should_aggregate_events(current_group[-1], event, time_window_hours):
            current_group.append(event)
        else:
            # Process current group
            if len(current_group) > 1:
                aggregated.append(_create_aggregated_event(current_group))
            else:
                aggregated.append(current_group[0])
            current_group = [event]
    
    # Handle the last group
    if len(current_group) > 1:
        aggregated.append(_create_aggregated_event(current_group))
    else:
        aggregated.append(current_group[0])
    
    return aggregated


def _should_aggregate_events(event1: Dict[str, Any], event2: Dict[str, Any], time_window_hours: int) -> bool:
    """Check if two events should be aggregated."""
    # Must be same type and region
    if event1.get("type") != event2.get("type"):
        return False
    if event1.get("region") != event2.get("region"):
        return False
    
    # Must be within time window
    try:
        time1 = datetime.fromisoformat(event1.get("timestamp", ""))
        time2 = datetime.fromisoformat(event2.get("timestamp", ""))
        time_diff = abs((time2 - time1).total_seconds() / 3600)  # Convert to hours
        return time_diff <= time_window_hours
    except (ValueError, TypeError):
        return False


def _create_aggregated_event(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create an aggregated event from multiple similar events."""
    base_event = events[0].copy()
    count = len(events)
    
    # Update description to reflect aggregation
    base_event["description"] = f"Multiple {base_event.get('type', 'events')} occurred ({count} incidents)"
    
    # Use the latest timestamp
    latest_time = max(e.get("timestamp", "") for e in events)
    base_event["timestamp"] = latest_time
    
    # Aggregate severity (average, but cap at 10)
    avg_severity = sum(e.get("severity", 1) for e in events) / count
    base_event["severity"] = min(10, int(avg_severity))
    
    # Add aggregation metadata
    base_event["metadata"]["aggregated_count"] = count
    base_event["metadata"]["aggregated_events"] = [e.get("id") for e in events]
    
    return base_event
