"""
Utility functions for the religion system.

This module provides helper functions for working with religions, conversions
between data formats, and helper functions for narrative hook generation.
"""

import random
from typing import Dict, List, Optional, Any, Union
from .models import Religion, ReligionType, ReligionMembership


def calculate_devotion_change(base_change: int, factors: Dict[str, float]) -> int:
    """
    Calculate devotion change based on various factors.
    
    Args:
        base_change: Base amount of devotion change
        factors: Dictionary of factors and their weights
        
    Returns:
        Modified devotion change amount
    """
    multiplier = 1.0
    for factor, weight in factors.items():
        multiplier += weight
    
    return int(base_change * multiplier)


def generate_conversion_narrative(
    entity_name: str, 
    from_religion: Optional[Religion], 
    to_religion: Religion
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
        templates = [
            f"{entity_name} has found faith in the teachings of {to_religion.name}.",
            f"After a spiritual awakening, {entity_name} joins {to_religion.name}.",
            f"{entity_name} becomes a follower of {to_religion.name}."
        ]
    else:
        templates = [
            f"{entity_name} abandons {from_religion.name} to follow {to_religion.name}.",
            f"Disillusioned with {from_religion.name}, {entity_name} converts to {to_religion.name}.",
            f"{entity_name} secretly turns from {from_religion.name} to embrace {to_religion.name}."
        ]
    
    return random.choice(templates)


def generate_religion_event(
    religion: Religion,
    event_type: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a religion event structure.
    
    Args:
        religion: Religion object the event relates to
        event_type: Type of event (conversion, festival, ritual, etc.)
        context: Additional context for the event
        
    Returns:
        Event data structure
    """
    return {
        "religion_id": religion.id,
        "religion_name": religion.name,
        "religion_type": religion.type,
        "event_type": event_type,
        "context": context,
        "timestamp": context.get("timestamp", None),
    }


def calculate_religion_compatibility(religion1: Religion, religion2: Religion) -> float:
    """
    Calculate compatibility between two religions (0.0 to 1.0).
    
    Args:
        religion1: First religion
        religion2: Second religion
        
    Returns:
        Compatibility score between 0.0 (incompatible) and 1.0 (perfectly compatible)
    """
    # Start with base compatibility based on religion types
    type_compatibility = {
        (ReligionType.POLYTHEISTIC, ReligionType.POLYTHEISTIC): 0.8,
        (ReligionType.POLYTHEISTIC, ReligionType.MONOTHEISTIC): 0.2,
        (ReligionType.POLYTHEISTIC, ReligionType.ANIMISTIC): 0.7,
        (ReligionType.POLYTHEISTIC, ReligionType.ANCESTOR): 0.6,
        (ReligionType.POLYTHEISTIC, ReligionType.CULT): 0.3,
        (ReligionType.POLYTHEISTIC, ReligionType.SYNCRETIC): 0.9,
        (ReligionType.MONOTHEISTIC, ReligionType.MONOTHEISTIC): 0.4, 
        (ReligionType.MONOTHEISTIC, ReligionType.ANIMISTIC): 0.2,
        (ReligionType.MONOTHEISTIC, ReligionType.ANCESTOR): 0.3,
        (ReligionType.MONOTHEISTIC, ReligionType.CULT): 0.1,
        (ReligionType.MONOTHEISTIC, ReligionType.SYNCRETIC): 0.5,
        (ReligionType.ANIMISTIC, ReligionType.ANIMISTIC): 0.9,
        (ReligionType.ANIMISTIC, ReligionType.ANCESTOR): 0.8,
        (ReligionType.ANIMISTIC, ReligionType.CULT): 0.4,
        (ReligionType.ANIMISTIC, ReligionType.SYNCRETIC): 0.8,
        (ReligionType.ANCESTOR, ReligionType.ANCESTOR): 0.9,
        (ReligionType.ANCESTOR, ReligionType.CULT): 0.3,
        (ReligionType.ANCESTOR, ReligionType.SYNCRETIC): 0.7,
        (ReligionType.CULT, ReligionType.CULT): 0.2,
        (ReligionType.CULT, ReligionType.SYNCRETIC): 0.4,
        (ReligionType.SYNCRETIC, ReligionType.SYNCRETIC): 1.0,
        (ReligionType.CUSTOM, ReligionType.CUSTOM): 0.5,
    }
    
    # Get base compatibility score
    key = (religion1.type, religion2.type)
    reversed_key = (religion2.type, religion1.type)
    
    base_score = type_compatibility.get(
        key, 
        type_compatibility.get(reversed_key, 0.3)  # Default compatibility
    )
    
    # Add compatibility from shared tenets
    shared_tenets = set(religion1.tenets).intersection(set(religion2.tenets))
    tenet_score = len(shared_tenets) / max(len(religion1.tenets) + len(religion2.tenets), 1) * 0.3
    
    # Add compatibility from shared holy places
    shared_places = set(religion1.holy_places).intersection(set(religion2.holy_places))
    place_score = len(shared_places) / max(len(religion1.holy_places) + len(religion2.holy_places), 1) * 0.2
    
    # Add compatibility from shared tags
    shared_tags = set(religion1.tags).intersection(set(religion2.tags))
    tag_score = len(shared_tags) / max(len(religion1.tags) + len(religion2.tags), 1) * 0.2
    
    # Calculate final score, capped at 1.0
    final_score = min(base_score + tenet_score + place_score + tag_score, 1.0)
    
    return final_score


def calculate_schism_probability(
    religion: Religion, 
    devotees: List[ReligionMembership],
    factors: Dict[str, float]
) -> float:
    """
    Calculate the probability of a schism occurring in a religion.
    
    Args:
        religion: Religion object
        devotees: List of religion memberships
        factors: Dictionary of factors influencing schism (size, age, etc.)
        
    Returns:
        Probability of schism (0.0 to 1.0)
    """
    # Base probability is low
    base_probability = 0.01
    
    # Size factor - larger religions more prone to schisms
    size = len(devotees)
    size_factor = min(size / 100, 0.5)  # Cap at 0.5
    
    # Devotion variance - higher variance means more probability
    if size > 1:
        devotion_levels = [d.devotion_level for d in devotees]
        mean_devotion = sum(devotion_levels) / len(devotion_levels)
        variance = sum((d - mean_devotion)**2 for d in devotion_levels) / len(devotion_levels)
        normalized_variance = min(variance / 1000, 0.3)  # Cap at 0.3
    else:
        normalized_variance = 0
    
    # Age factor (if present in metadata)
    age_factor = 0
    if religion.metadata and "age" in religion.metadata:
        age = religion.metadata["age"]
        age_factor = min(age / 100, 0.2)  # Cap at 0.2
    
    # Custom factors from parameters
    custom_factor = sum(factors.values())
    
    # Calculate final probability, capped at 0.95
    final_probability = min(
        base_probability + size_factor + normalized_variance + age_factor + custom_factor,
        0.95
    )
    
    return final_probability 