import math
from typing import Dict, Tuple, List, Optional
from datetime import datetime, timedelta

from backend.systems.population.models import POIPopulation, POIState, POIType

def calculate_growth_rate(population: POIPopulation, global_multiplier: float, 
                         soft_cap_threshold: float, soft_cap_multiplier: float) -> float:
    """
    Calculate the growth rate for a POI based on the formula:
    Monthly NPC Generation = BaseRate × (CurrentPopulation ÷ TargetPopulation) × GlobalMultiplier
    
    Args:
        population: The POI population data
        global_multiplier: The global multiplier for all population growth
        soft_cap_threshold: Threshold (as ratio of target) where soft cap applies
        soft_cap_multiplier: Multiplier applied at soft cap
        
    Returns:
        The calculated growth rate
    """
    # Skip calculation for non-growing POI states
    if population.state in [POIState.RUINS, POIState.DUNGEON, POIState.ABANDONED]:
        return 0.0
        
    # Base calculation from Development Bible formula
    rate = (population.base_rate * 
            (population.current_population / population.target_population) * 
            global_multiplier)
    
    # Apply soft cap if near target population
    if (population.current_population >= 
        soft_cap_threshold * population.target_population):
        rate *= soft_cap_multiplier
    
    return rate

def calculate_next_state(population: POIPopulation, 
                         thresholds: Dict[str, float]) -> POIState:
    """
    Calculate the next state for a POI based on population ratio.
    
    Args:
        population: The POI population data
        thresholds: Dictionary of transition thresholds
        
    Returns:
        The calculated next state
    """
    # If already in ruins or dungeon, keep that state
    if population.state in [POIState.RUINS, POIState.DUNGEON]:
        return population.state
        
    # Calculate population ratio
    ratio = population.current_population / population.target_population if population.target_population > 0 else 0
    
    # State transition logic
    if population.state == POIState.NORMAL:
        if ratio < thresholds["normal_to_declining"]:
            return POIState.DECLINING
        return POIState.NORMAL
        
    elif population.state == POIState.DECLINING:
        if ratio < thresholds["declining_to_abandoned"]:
            return POIState.ABANDONED
        elif ratio >= thresholds["normal_to_declining"]:
            return POIState.NORMAL
        return POIState.DECLINING
        
    elif population.state == POIState.ABANDONED:
        if ratio < thresholds["abandoned_to_ruins"]:
            return POIState.RUINS
        elif ratio >= thresholds["declining_to_abandoned"]:
            return POIState.REPOPULATING
        return POIState.ABANDONED
        
    elif population.state == POIState.REPOPULATING:
        if ratio >= thresholds["repopulating_to_normal"]:
            return POIState.NORMAL
        elif ratio < thresholds["declining_to_abandoned"]:
            return POIState.ABANDONED
        return POIState.REPOPULATING
        
    # Default: keep current state
    return population.state

def estimate_population_timeline(population: POIPopulation, 
                                 global_multiplier: float,
                                 soft_cap_threshold: float,
                                 soft_cap_multiplier: float,
                                 months: int = 12) -> List[Tuple[int, POIState]]:
    """
    Estimate population and state changes over time.
    
    Args:
        population: The POI population data
        global_multiplier: The global multiplier for all population growth
        soft_cap_threshold: Threshold (as ratio of target) where soft cap applies
        soft_cap_multiplier: Multiplier applied at soft cap
        months: Number of months to simulate
        
    Returns:
        List of (population, state) tuples for each month
    """
    results = []
    
    # Create a copy to avoid modifying the original
    current_pop = population.current_population
    current_state = population.state
    
    for _ in range(months):
        # Skip growth for non-growing states
        if current_state not in [POIState.RUINS, POIState.DUNGEON, POIState.ABANDONED]:
            if current_pop < population.target_population:
                # Calculate growth
                rate = (population.base_rate * 
                        (current_pop / population.target_population) * 
                        global_multiplier)
                
                # Apply soft cap
                if current_pop >= soft_cap_threshold * population.target_population:
                    rate *= soft_cap_multiplier
                
                # Update population
                current_pop += math.floor(rate)
                
                # Apply hard cap
                if current_pop > population.target_population:
                    current_pop = population.target_population
            
        # Apply minimum threshold
        if current_pop < population.min_population:
            current_pop = population.min_population
        
        # Calculate ratio for state transition
        ratio = current_pop / population.target_population if population.target_population > 0 else 0
        
        # Determine next state based on current state and ratio
        # This is a simplified version of the state transition logic
        if current_state == POIState.NORMAL and ratio < 0.6:
            current_state = POIState.DECLINING
        elif current_state == POIState.DECLINING:
            if ratio < 0.3:
                current_state = POIState.ABANDONED
            elif ratio >= 0.6:
                current_state = POIState.NORMAL
        elif current_state == POIState.ABANDONED:
            if ratio < 0.1:
                current_state = POIState.RUINS
            elif ratio >= 0.3:
                current_state = POIState.REPOPULATING
        elif current_state == POIState.REPOPULATING and ratio >= 0.7:
            current_state = POIState.NORMAL
        
        results.append((current_pop, current_state))
    
    return results

def calculate_target_population(poi_type: POIType, size_modifier: float = 1.0) -> int:
    """
    Calculate a target population for a POI based on its type and a size modifier.
    
    Args:
        poi_type: The type of POI
        size_modifier: Multiplier for size variation (0.5-2.0 typical range)
        
    Returns:
        The calculated target population
    """
    base_targets = {
        POIType.CITY: 200,
        POIType.TOWN: 100,
        POIType.VILLAGE: 50,
        POIType.RELIGIOUS: 30,
        POIType.EMBASSY: 25,
        POIType.OUTPOST: 20,
        POIType.MARKET: 40,
        POIType.CUSTOM: 30,
        POIType.RUINS: 0,
        POIType.DUNGEON: 0
    }
    
    base = base_targets.get(poi_type, 30)
    return math.ceil(base * size_modifier) 