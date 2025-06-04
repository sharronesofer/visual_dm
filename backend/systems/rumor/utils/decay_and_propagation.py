"""
Utilities for rumor decay and propagation.

This module provides utility functions for calculating rumor decay rates,
mutation probabilities, and other aspects of rumor propagation.
"""
import math
from typing import Optional, Union
from enum import Enum

# Pure business logic enum (no infrastructure dependencies)
class RumorSeverity(Enum):
    """Severity levels for rumors - pure business logic"""
    TRIVIAL = "trivial"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

# Import centralized rules configuration
try:
    from backend.systems.rules.rules import (
        get_rumor_decay_rate,
        get_rumor_mutation_chance,
        get_rumor_spread_radius,
        get_rumor_believability_threshold,
        get_rumor_config
    )
    _USE_CENTRALIZED_CONFIG = True
except ImportError:
    _USE_CENTRALIZED_CONFIG = False

def calculate_rumor_decay(
    days_inactive: int, 
    rumor_severity: Union[RumorSeverity, str],
    base_decay: float = 0.05
) -> float:
    """
    Calculate how much a rumor's believability should decay.
    Uses centralized configuration if available, falls back to legacy calculation.
    
    Args:
        days_inactive: Number of days since the rumor was last reinforced
        rumor_severity: Severity of the rumor
        base_decay: Base daily decay rate (used as fallback)
        
    Returns:
        Amount to reduce believability by (0.0 to 1.0)
    """
    severity_name = rumor_severity.value if hasattr(rumor_severity, 'value') else str(rumor_severity).lower()
    
    if _USE_CENTRALIZED_CONFIG:
        # Use centralized configuration
        return get_rumor_decay_rate(severity_name, days_inactive)
    else:
        # Legacy fallback calculation
        severity_factor = {
            RumorSeverity.TRIVIAL: 1.5,   # Decays 50% faster
            RumorSeverity.MINOR: 1.2,     # Decays 20% faster
            RumorSeverity.MODERATE: 1.0,  # Normal decay rate
            RumorSeverity.MAJOR: 0.8,     # Decays 20% slower
            RumorSeverity.CRITICAL: 0.6   # Decays 40% slower
        }.get(rumor_severity, 1.0)
        
        decay = base_decay * severity_factor * math.log10(days_inactive + 1)
        return min(1.0, max(0.0, decay))

def calculate_mutation_probability(
    base_chance: float,
    rumor_severity: Union[RumorSeverity, str],
    spread_count: int
) -> float:
    """
    Calculate the probability that a rumor mutates when spread.
    Uses centralized configuration if available, falls back to legacy calculation.
    
    Args:
        base_chance: Base probability of mutation (used as fallback)
        rumor_severity: Severity of the rumor
        spread_count: Number of times the rumor has been spread
        
    Returns:
        Probability of mutation (0.0 to 1.0)
    """
    severity_name = rumor_severity.value if hasattr(rumor_severity, 'value') else str(rumor_severity).lower()
    
    if _USE_CENTRALIZED_CONFIG:
        # Use centralized configuration
        return get_rumor_mutation_chance(severity_name, spread_count)
    else:
        # Legacy fallback calculation
        severity_factor = {
            RumorSeverity.TRIVIAL: 1.5,   # 50% more likely to mutate
            RumorSeverity.MINOR: 1.2,     # 20% more likely to mutate
            RumorSeverity.MODERATE: 1.0,  # Normal mutation rate
            RumorSeverity.MAJOR: 0.8,     # 20% less likely to mutate
            RumorSeverity.CRITICAL: 0.6   # 40% less likely to mutate
        }.get(rumor_severity, 1.0)
        
        spread_factor = min(2.0, 1.0 + (spread_count / 50.0))
        probability = base_chance * severity_factor * spread_factor
        return min(1.0, max(0.0, probability))

def calculate_spread_radius(
    initial_radius: int,
    rumor_severity: Union[RumorSeverity, str],
    days_active: int,
    saturation_factor: float = 0.8
) -> int:
    """
    Calculate how far a rumor can spread.
    Uses centralized configuration if available, falls back to legacy calculation.
    
    Args:
        initial_radius: Initial spread radius (used as fallback)
        rumor_severity: Severity of the rumor
        days_active: Number of days the rumor has been active
        saturation_factor: Factor affecting how quickly spread slows down (used as fallback)
        
    Returns:
        Maximum spread radius in arbitrary units
    """
    severity_name = rumor_severity.value if hasattr(rumor_severity, 'value') else str(rumor_severity).lower()
    
    if _USE_CENTRALIZED_CONFIG:
        # Use centralized configuration
        return get_rumor_spread_radius(severity_name, days_active)
    else:
        # Legacy fallback calculation
        severity_factor = {
            RumorSeverity.TRIVIAL: 0.7,   # 30% reduced spread
            RumorSeverity.MINOR: 0.9,     # 10% reduced spread
            RumorSeverity.MODERATE: 1.0,  # Normal spread
            RumorSeverity.MAJOR: 1.2,     # 20% increased spread
            RumorSeverity.CRITICAL: 1.5   # 50% increased spread
        }.get(rumor_severity, 1.0)
        
        time_factor = 1.0 - math.exp(-saturation_factor * days_active)
        radius = initial_radius * severity_factor * (1.0 + time_factor)
        return max(1, int(radius))

def calculate_believability_threshold(
    base_threshold: float,
    rumor_severity: Union[RumorSeverity, str],
    relationship_strength: float
) -> float:
    """
    Calculate the minimum believability needed for an entity to spread a rumor.
    Uses centralized configuration if available, falls back to legacy calculation.
    
    Args:
        base_threshold: Base believability threshold (used as fallback)
        rumor_severity: Severity of the rumor
        relationship_strength: Strength of relationship between entities (-1.0 to 1.0)
        
    Returns:
        Believability threshold (0.0 to 1.0)
    """
    severity_name = rumor_severity.value if hasattr(rumor_severity, 'value') else str(rumor_severity).lower()
    
    if _USE_CENTRALIZED_CONFIG:
        # Use centralized configuration
        return get_rumor_believability_threshold(severity_name, relationship_strength)
    else:
        # Legacy fallback calculation
        severity_factor = {
            RumorSeverity.TRIVIAL: 0.8,   # 20% lower threshold
            RumorSeverity.MINOR: 0.9,     # 10% lower threshold
            RumorSeverity.MODERATE: 1.0,  # Normal threshold
            RumorSeverity.MAJOR: 1.1,     # 10% higher threshold
            RumorSeverity.CRITICAL: 1.2   # 20% higher threshold
        }.get(rumor_severity, 1.0)
        
        relationship_modifier = -0.2 * relationship_strength
        threshold = base_threshold * severity_factor + relationship_modifier
        return min(1.0, max(0.1, threshold))

def get_location_modifiers(location_type: str) -> dict:
    """
    Get location-specific modifiers for rumor spreading.
    
    Args:
        location_type: Type of location (e.g., 'tavern', 'marketplace', 'court')
        
    Returns:
        Dictionary with modifiers for the location
    """
    if _USE_CENTRALIZED_CONFIG:
        config = get_rumor_config("environment")
        location_modifiers = config.get("location_modifiers", {})
        return location_modifiers.get(location_type.lower(), {
            "spread_multiplier": 1.0,
            "mutation_chance_modifier": 0.0
        })
    else:
        # Legacy fallback
        default_modifiers = {
            "tavern": {"spread_multiplier": 1.5, "mutation_chance_modifier": 0.1},
            "marketplace": {"spread_multiplier": 1.3, "mutation_chance_modifier": 0.05},
            "court": {"spread_multiplier": 1.2, "mutation_chance_modifier": -0.1},
            "temple": {"spread_multiplier": 0.8, "mutation_chance_modifier": -0.2},
            "wilderness": {"spread_multiplier": 0.3, "mutation_chance_modifier": 0.0}
        }
        return default_modifiers.get(location_type.lower(), {
            "spread_multiplier": 1.0,
            "mutation_chance_modifier": 0.0
        }) 