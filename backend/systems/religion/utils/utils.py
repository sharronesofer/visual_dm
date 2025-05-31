"""
Religion System Utilities

This module provides utility functions for the religion system.
"""

from typing import Optional, Dict, Any
from datetime import datetime


def generate_conversion_narrative(
    entity_name: str, 
    from_religion: Optional[Any], 
    to_religion: Any
) -> str:
    """
    Generate narrative text for a conversion event.
    
    Args:
        entity_name: Name of the entity converting
        from_religion: Previous religion (None if first conversion)
        to_religion: New religion being converted to
        
    Returns:
        Narrative text describing the conversion
    """
    if from_religion is None:
        return f"{entity_name} has embraced the faith of {to_religion.name}, finding spiritual guidance in its teachings."
    else:
        return f"{entity_name} has converted from {from_religion.name} to {to_religion.name}, seeking new spiritual enlightenment."


def generate_religion_event(
    religion: Any, 
    event_type: str, 
    event_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a religion event structure.
    
    Args:
        religion: Religion object
        event_type: Type of event
        event_data: Additional event data
        
    Returns:
        Event structure dictionary
    """
    return {
        "religion_id": getattr(religion, 'id', str(religion)),
        "religion_name": getattr(religion, 'name', str(religion)),
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": event_data
    }


def calculate_devotion_change(
    current_devotion: float,
    action_type: str,
    intensity: float = 1.0
) -> float:
    """
    Calculate devotion level changes based on actions.
    
    Args:
        current_devotion: Current devotion level (0.0 to 1.0)
        action_type: Type of action affecting devotion
        intensity: Intensity multiplier for the change
        
    Returns:
        New devotion level
    """
    change_map = {
        "prayer": 0.05,
        "ritual": 0.1,
        "pilgrimage": 0.2,
        "donation": 0.08,
        "service": 0.12,
        "transgression": -0.15,
        "doubt": -0.05,
        "apostasy": -0.5
    }
    
    change = change_map.get(action_type, 0.0) * intensity
    new_devotion = max(0.0, min(1.0, current_devotion + change))
    
    return new_devotion


def check_religion_compatibility(religion1: Any, religion2: Any) -> float:
    """
    Check compatibility between two religions.
    
    Args:
        religion1: First religion
        religion2: Second religion
        
    Returns:
        Compatibility score (0.0 to 1.0)
    """
    # Placeholder implementation - would need proper religion type checking
    if hasattr(religion1, 'type') and hasattr(religion2, 'type'):
        if religion1.type == religion2.type:
            return 0.8
        else:
            return 0.3
    
    return 0.5  # Default neutral compatibility 