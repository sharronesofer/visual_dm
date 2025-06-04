"""
Religion System Utilities

This module provides utility functions for the religion system.
Updated to use configuration-driven approach instead of hardcoded values.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

# Import the new configuration system
try:
    from backend.systems.religion.config import (
        calculate_devotion_change as config_calculate_devotion_change,
        check_religion_compatibility as config_check_compatibility,
        get_narrative_template,
        get_religion_type_info
    )
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False

logger = logging.getLogger(__name__)

def generate_conversion_narrative(
    entity_id: UUID,
    from_religion: Optional[Any], 
    to_religion: Any,
    reason: Optional[str] = None
) -> str:
    """
    Generate narrative text for a conversion event using configuration templates.
    
    Args:
        entity_id: UUID of the entity converting
        from_religion: Previous religion (None if first conversion)
        to_religion: New religion being converted to
        reason: Optional reason for conversion
        
    Returns:
        Narrative text describing the conversion
    """
    if not HAS_CONFIG:
        # Fallback to simple narrative
        entity_name = f"Entity {entity_id}"
        if from_religion is None:
            return f"{entity_name} has embraced the faith of {getattr(to_religion, 'name', str(to_religion))}, finding spiritual guidance in its teachings."
        else:
            return f"{entity_name} has converted from {getattr(from_religion, 'name', str(from_religion))} to {getattr(to_religion, 'name', str(to_religion))}, seeking new spiritual enlightenment."
    
    # Determine conversion type based on reason
    conversion_type = "voluntary"  # Default
    if reason:
        reason_lower = reason.lower()
        if any(word in reason_lower for word in ["crisis", "tragedy", "disaster", "desperate"]):
            conversion_type = "crisis_driven"
        elif any(word in reason_lower for word in ["political", "alliance", "marriage", "decree"]):
            conversion_type = "political"
        elif any(word in reason_lower for word in ["study", "debate", "logic", "philosophy"]):
            conversion_type = "intellectual"
        elif any(word in reason_lower for word in ["vision", "dream", "miracle", "divine"]):
            conversion_type = "mystical"
    
    # Format template variables
    format_vars = {
        "entity_name": f"Entity {entity_id}",
        "to_religion": getattr(to_religion, 'name', str(to_religion)),
        "from_religion": getattr(from_religion, 'name', str(from_religion)) if from_religion else "no prior faith",
        "reason": reason or "personal spiritual growth",
        "core_tenet": getattr(to_religion, 'core_beliefs', ["salvation"])[0] if hasattr(to_religion, 'core_beliefs') else "enlightenment"
    }
    
    try:
        return get_narrative_template("conversion_templates", conversion_type, **format_vars)
    except Exception as e:
        logger.error(f"Error generating conversion narrative: {e}")
        # Fallback to simple narrative
        return f"{format_vars['entity_name']} converted from {format_vars['from_religion']} to {format_vars['to_religion']}"


def generate_religion_event(
    religion_id: UUID, 
    event_type: str, 
    event_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a religion event structure with narrative content.
    
    Args:
        religion_id: Religion UUID
        event_type: Type of event
        event_data: Additional event data
        
    Returns:
        Event structure dictionary
    """
    # Generate narrative content if config is available
    narrative_content = ""
    if HAS_CONFIG:
        try:
            # Format template variables from event data
            format_vars = {
                "religion": event_data.get("religion_name", str(religion_id)),
                "event_name": event_data.get("event_name", event_type),
                "participant_count": event_data.get("participant_count", "many"),
                "location": event_data.get("location", "sacred grounds"),
                "leader_name": event_data.get("leader_name", "a charismatic leader"),
                "follower_count": event_data.get("follower_count", "numerous")
            }
            
            narrative_content = get_narrative_template("religious_event_templates", event_type, **format_vars)
        except Exception as e:
            logger.warning(f"Could not generate narrative for event {event_type}: {e}")
            narrative_content = f"A {event_type} event occurred for religion {religion_id}"
    else:
        narrative_content = f"A {event_type} event occurred for religion {religion_id}"
    
    return {
        "religion_id": str(religion_id),
        "religion_name": event_data.get("religion_name", str(religion_id)),
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "narrative": narrative_content,
        "data": event_data
    }


def calculate_devotion_change(
    current_devotion: float,
    action_type: str,
    intensity: float = 1.0,
    **kwargs
) -> float:
    """
    Calculate devotion level changes based on actions using configuration.
    
    Args:
        current_devotion: Current devotion level (0.0 to 1.0)
        action_type: Type of action affecting devotion
        intensity: Intensity multiplier for the change
        **kwargs: Additional parameters (e.g., severity for transgressions)
        
    Returns:
        New devotion level
    """
    if HAS_CONFIG:
        return config_calculate_devotion_change(current_devotion, action_type, intensity, **kwargs)
    
    # Fallback to original hardcoded values
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
    
    # Apply severity multiplier for transgressions
    if action_type == "transgression" and "severity" in kwargs:
        change *= kwargs["severity"]
    
    new_devotion = max(0.0, min(1.0, current_devotion + change))
    return new_devotion


def check_religion_compatibility(
    religion1: Any, 
    religion2: Any,
    shared_factors: Optional[list] = None,
    conflict_factors: Optional[list] = None
) -> float:
    """
    Check compatibility between two religions using configuration.
    
    Args:
        religion1: First religion object
        religion2: Second religion object
        shared_factors: List of shared compatibility factors
        conflict_factors: List of conflict factors
        
    Returns:
        Compatibility score (0.0 to 1.0)
    """
    if HAS_CONFIG:
        # Extract religion types from objects
        religion1_type = getattr(religion1, 'type', 'monotheistic')
        religion2_type = getattr(religion2, 'type', 'monotheistic')
        
        return config_check_compatibility(
            religion1_type, 
            religion2_type, 
            shared_factors, 
            conflict_factors
        )
    
    # Fallback implementation
    if hasattr(religion1, 'type') and hasattr(religion2, 'type'):
        if religion1.type == religion2.type:
            return 0.8
        else:
            return 0.3
    
    return 0.5  # Default neutral compatibility


def generate_devotion_narrative(
    entity_id: UUID,
    religion: Any,
    action_type: str,
    old_devotion: float,
    new_devotion: float
) -> str:
    """
    Generate narrative text for devotion changes.
    
    Args:
        entity_id: UUID of the entity
        religion: Religion object
        action_type: Type of action that caused the change
        old_devotion: Previous devotion level
        new_devotion: New devotion level
        
    Returns:
        Narrative text describing the devotion change
    """
    if not HAS_CONFIG:
        # Simple fallback
        direction = "increased" if new_devotion > old_devotion else "decreased"
        return f"Entity {entity_id}'s devotion to {getattr(religion, 'name', str(religion))} has {direction}"
    
    try:
        # Determine if this is an increase or decrease
        change_direction = "increase" if new_devotion > old_devotion else "decrease"
        
        format_vars = {
            "entity_name": f"Entity {entity_id}",
            "religion": getattr(religion, 'name', str(religion))
        }
        
        # Use subcategory parameter for the action type
        return get_narrative_template("devotion_change_narratives", change_direction, action_type, **format_vars)
    except Exception as e:
        logger.warning(f"Could not generate devotion narrative: {e}")
        # Fallback
        direction = "increased" if new_devotion > old_devotion else "decreased"
        return f"Entity {entity_id}'s devotion to {getattr(religion, 'name', str(religion))} has {direction} due to {action_type}"


def get_religion_type_info(religion_type: str) -> Dict[str, Any]:
    """
    Get information about a religion type from configuration.
    
    Args:
        religion_type: Type of religion
        
    Returns:
        Dictionary with religion type information
    """
    if not HAS_CONFIG:
        return {"name": religion_type.title(), "description": f"A {religion_type} religion"}
    
    try:
        from backend.systems.religion.config import get_religion_types
        types_config = get_religion_types()
        return types_config.get(religion_type, {"name": religion_type.title(), "description": ""})
    except Exception as e:
        logger.warning(f"Could not get religion type info: {e}")
        return {"name": religion_type.title(), "description": ""}


def calculate_regional_influence(
    base_influence: float,
    region_type: str,
    religion_type: str,
    competing_religions: int = 0
) -> float:
    """
    Calculate religious influence in a specific region.
    
    Args:
        base_influence: Base influence level
        region_type: Type of region (urban, rural, etc.)
        religion_type: Type of religion
        competing_religions: Number of competing religions in the region
        
    Returns:
        Modified influence level
    """
    if not HAS_CONFIG:
        # Simple fallback calculation
        region_modifier = 1.0
        if region_type == "urban":
            region_modifier = 1.2
        elif region_type == "rural":
            region_modifier = 0.8
        
        competition_penalty = max(0.5, 1.0 - (competing_religions * 0.1))
        return base_influence * region_modifier * competition_penalty
    
    try:
        from backend.systems.religion.config import get_regional_modifier, get_religion_types
        
        # Get regional modifiers
        spread_rate = get_regional_modifier(region_type, "spread_rate")
        resistance = get_regional_modifier(region_type, "resistance")
        
        # Get religion type info
        types_config = get_religion_types()
        religion_spread_rate = types_config.get(religion_type, {}).get("influence_spread_rate", 1.0)
        
        # Calculate competition penalty
        competition_penalty = max(0.3, 1.0 - (competing_religions * 0.15))
        
        # Apply all modifiers
        modified_influence = base_influence * spread_rate * religion_spread_rate * competition_penalty / resistance
        
        return max(0.0, min(1.0, modified_influence))
        
    except Exception as e:
        logger.warning(f"Could not calculate regional influence: {e}")
        return base_influence 