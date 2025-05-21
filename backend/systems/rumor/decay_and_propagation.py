"""
Utilities for rumor decay and propagation.

This module provides utility functions for calculating rumor decay rates,
mutation probabilities, and other aspects of rumor propagation.
"""
import math
from typing import Optional
from backend.systems.rumor.models.rumor import RumorSeverity

def calculate_rumor_decay(
    days_inactive: int, 
    rumor_severity: RumorSeverity,
    base_decay: float = 0.05
) -> float:
    """
    Calculate how much a rumor's believability should decay.
    
    Args:
        days_inactive: Number of days since the rumor was last reinforced
        rumor_severity: Severity of the rumor
        base_decay: Base daily decay rate
        
    Returns:
        Amount to reduce believability by (0.0 to 1.0)
    """
    # More severe rumors decay more slowly
    severity_factor = {
        RumorSeverity.TRIVIAL: 1.5,   # Decays 50% faster
        RumorSeverity.MINOR: 1.2,     # Decays 20% faster
        RumorSeverity.MODERATE: 1.0,  # Normal decay rate
        RumorSeverity.MAJOR: 0.8,     # Decays 20% slower
        RumorSeverity.CRITICAL: 0.6   # Decays 40% slower
    }.get(rumor_severity, 1.0)
    
    # Calculate decay amount - uses a logarithmic curve to model memory decay
    # The longer it's been, the less additional decay occurs
    decay = base_decay * severity_factor * math.log10(days_inactive + 1)
    
    # Ensure decay is within reasonable bounds
    return min(1.0, max(0.0, decay))

def calculate_mutation_probability(
    base_chance: float,
    rumor_severity: RumorSeverity,
    spread_count: int
) -> float:
    """
    Calculate the probability that a rumor mutates when spread.
    
    Args:
        base_chance: Base probability of mutation
        rumor_severity: Severity of the rumor
        spread_count: Number of times the rumor has been spread
        
    Returns:
        Probability of mutation (0.0 to 1.0)
    """
    # More severe rumors are less likely to mutate
    severity_factor = {
        RumorSeverity.TRIVIAL: 1.5,   # 50% more likely to mutate
        RumorSeverity.MINOR: 1.2,     # 20% more likely to mutate
        RumorSeverity.MODERATE: 1.0,  # Normal mutation rate
        RumorSeverity.MAJOR: 0.8,     # 20% less likely to mutate
        RumorSeverity.CRITICAL: 0.6   # 40% less likely to mutate
    }.get(rumor_severity, 1.0)
    
    # The more a rumor has spread, the more likely it is to mutate
    # This models how information tends to change as it spreads widely
    spread_factor = min(2.0, 1.0 + (spread_count / 50.0))
    
    # Calculate final probability
    probability = base_chance * severity_factor * spread_factor
    
    # Ensure probability is within bounds
    return min(1.0, max(0.0, probability))

def calculate_spread_radius(
    initial_radius: int,
    rumor_severity: RumorSeverity,
    days_active: int,
    saturation_factor: float = 0.8
) -> int:
    """
    Calculate how far a rumor can spread.
    
    Args:
        initial_radius: Initial spread radius
        rumor_severity: Severity of the rumor
        days_active: Number of days the rumor has been active
        saturation_factor: Factor affecting how quickly spread slows down
        
    Returns:
        Maximum spread radius in arbitrary units
    """
    # More severe rumors spread farther
    severity_factor = {
        RumorSeverity.TRIVIAL: 0.7,   # 30% reduced spread
        RumorSeverity.MINOR: 0.9,     # 10% reduced spread
        RumorSeverity.MODERATE: 1.0,  # Normal spread
        RumorSeverity.MAJOR: 1.2,     # 20% increased spread
        RumorSeverity.CRITICAL: 1.5   # 50% increased spread
    }.get(rumor_severity, 1.0)
    
    # Spread increases with time but eventually saturates
    time_factor = 1.0 - math.exp(-saturation_factor * days_active)
    
    # Calculate radius
    radius = initial_radius * severity_factor * (1.0 + time_factor)
    
    # Return as integer
    return max(1, int(radius))

def calculate_believability_threshold(
    base_threshold: float,
    rumor_severity: RumorSeverity,
    relationship_strength: float
) -> float:
    """
    Calculate the minimum believability needed for an entity to spread a rumor.
    
    Args:
        base_threshold: Base believability threshold
        rumor_severity: Severity of the rumor
        relationship_strength: Strength of relationship between entities (-1.0 to 1.0)
        
    Returns:
        Believability threshold (0.0 to 1.0)
    """
    # More severe rumors need higher believability to spread
    severity_factor = {
        RumorSeverity.TRIVIAL: 0.8,   # 20% lower threshold
        RumorSeverity.MINOR: 0.9,     # 10% lower threshold
        RumorSeverity.MODERATE: 1.0,  # Normal threshold
        RumorSeverity.MAJOR: 1.1,     # 10% higher threshold
        RumorSeverity.CRITICAL: 1.2   # 20% higher threshold
    }.get(rumor_severity, 1.0)
    
    # Stronger relationships lower the threshold
    relationship_modifier = -0.2 * relationship_strength
    
    # Calculate threshold
    threshold = base_threshold * severity_factor + relationship_modifier
    
    # Ensure threshold is within bounds
    return min(1.0, max(0.1, threshold)) 