"""
Population System Utilities

This module contains utility functions for population calculations including
war impact, catastrophes, resource management, migration, seasonal effects,
state management, and analytics.

Task 45 Implementation: All missing functionality has been added.
"""

import math
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import POIState from models
from backend.infrastructure.shared.models import POIState

logger = logging.getLogger(__name__)

# ============================================================================
# WAR IMPACT SYSTEM
# ============================================================================

def calculate_war_impact(population: int, war_intensity: float, duration_days: int,
                        defensive_strength: float = 0.5) -> Dict[str, Any]:
    """
    Calculate the impact of war on a population.
    
    Args:
        population: Current population count
        war_intensity: War intensity factor (0.0-1.0)
        duration_days: Duration of war in days
        defensive_strength: Defensive capabilities (0.0-1.0)
        
    Returns:
        Dict containing war impact results
    """
    try:
        # Base mortality rate based on war intensity
        base_mortality_rate = war_intensity * 0.3  # Up to 30% base mortality
        
        # Duration factor (longer wars are more devastating)
        duration_factor = 1.0 + (duration_days / 365.0) * 0.5  # +50% per year
        
        # Defensive strength reduces casualties
        defense_modifier = 1.0 - (defensive_strength * 0.6)  # Up to 60% reduction
        
        # Calculate final mortality rate
        final_mortality_rate = base_mortality_rate * duration_factor * defense_modifier
        final_mortality_rate = max(0.0, min(final_mortality_rate, 0.8))  # Cap at 80%
        
        # Calculate casualties and refugees
        casualties = int(population * final_mortality_rate)
        refugee_rate = war_intensity * 0.4 * (1.0 - defensive_strength * 0.3)
        refugees = int(population * refugee_rate)
        
        # Remaining population
        remaining_population = population - casualties
        
        result = {
            "original_population": population,
            "war_intensity": war_intensity,
            "duration_days": duration_days,
            "defensive_strength": defensive_strength,
            "mortality_rate": final_mortality_rate,
            "casualties": casualties,
            "refugees": refugees,
            "remaining_population": remaining_population,
            "population_loss": casualties,
            "infrastructure_damage": war_intensity * 0.7,
            "economic_impact": war_intensity * duration_factor * 0.5
        }
        
        logger.info(f"War impact calculated: {casualties} casualties from {population} population")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating war impact: {e}")
        return {"error": str(e)}


# ============================================================================
# CATASTROPHE IMPACT SYSTEM
# ============================================================================

def calculate_catastrophe_impact(population: int, catastrophe_type: str, severity: float,
                               preparedness: float = 0.3) -> Dict[str, Any]:
    """
    Calculate the impact of catastrophes on population.
    
    Args:
        population: Current population count
        catastrophe_type: Type of catastrophe (earthquake, flood, disease, etc.)
        severity: Severity level (0.0-1.0)
        preparedness: Community preparedness level (0.0-1.0)
        
    Returns:
        Dict containing catastrophe impact results
    """
    try:
        # Base impact rates by catastrophe type
        catastrophe_impacts = {
            "earthquake": {"mortality": 0.15, "displacement": 0.4, "injury": 0.25},
            "flood": {"mortality": 0.08, "displacement": 0.6, "injury": 0.15},
            "fire": {"mortality": 0.12, "displacement": 0.5, "injury": 0.3},
            "disease": {"mortality": 0.25, "displacement": 0.1, "injury": 0.4},
            "famine": {"mortality": 0.3, "displacement": 0.7, "injury": 0.1},
            "drought": {"mortality": 0.1, "displacement": 0.5, "injury": 0.05},
            "storm": {"mortality": 0.05, "displacement": 0.3, "injury": 0.2},
            "volcanic": {"mortality": 0.2, "displacement": 0.8, "injury": 0.15}
        }
        
        base_impact = catastrophe_impacts.get(catastrophe_type, catastrophe_impacts["earthquake"])
        
        # Apply severity and preparedness modifiers
        preparedness_modifier = 1.0 - (preparedness * 0.7)  # Up to 70% reduction
        severity_modifier = 0.3 + (severity * 0.7)  # Scale from 30% to 100%
        
        # Calculate impacts
        mortality_rate = base_impact["mortality"] * severity_modifier * preparedness_modifier
        displacement_rate = base_impact["displacement"] * severity_modifier * preparedness_modifier
        injury_rate = base_impact["injury"] * severity_modifier * preparedness_modifier
        
        # Cap rates
        mortality_rate = max(0.0, min(mortality_rate, 0.6))
        displacement_rate = max(0.0, min(displacement_rate, 0.9))
        injury_rate = max(0.0, min(injury_rate, 0.8))
        
        # Calculate absolute numbers
        deaths = int(population * mortality_rate)
        displaced = int(population * displacement_rate)
        injured = int(population * injury_rate)
        
        remaining_population = population - deaths
        
        result = {
            "original_population": population,
            "catastrophe_type": catastrophe_type,
            "severity": severity,
            "preparedness": preparedness,
            "mortality_rate": mortality_rate,
            "displacement_rate": displacement_rate,
            "injury_rate": injury_rate,
            "deaths": deaths,
            "displaced": displaced,
            "injured": injured,
            "remaining_population": remaining_population,
            "recovery_time_days": int(severity * 365 * (1.0 - preparedness * 0.5)),
            "infrastructure_damage": severity * 0.8,
            "economic_impact": severity * displacement_rate * 0.6
        }
        
        logger.info(f"Catastrophe impact calculated: {catastrophe_type} caused {deaths} deaths")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating catastrophe impact: {e}")
        return {"error": str(e)}


# ============================================================================
# RESOURCE MANAGEMENT SYSTEM
# ============================================================================

def calculate_resource_consumption(population: int, resource_type: str,
                                 efficiency_modifier: float = 1.0) -> Dict[str, Any]:
    """
    Calculate resource consumption for a population.
    
    Args:
        population: Population count
        resource_type: Type of resource (food, water, fuel, etc.)
        efficiency_modifier: Efficiency factor (0.5-2.0)
        
    Returns:
        Dict containing consumption analysis
    """
    try:
        # Base consumption rates per person per day
        base_consumption = {
            "food": 2.5,      # kg per day
            "water": 50.0,    # liters per day
            "fuel": 5.0,      # liters per day
            "medicine": 0.1,  # units per day
            "materials": 1.0, # kg per day
            "luxury": 0.5     # units per day
        }
        
        base_rate = base_consumption.get(resource_type, 1.0)
        daily_consumption = population * base_rate * efficiency_modifier
        
        # Calculate different time periods
        weekly_consumption = daily_consumption * 7
        monthly_consumption = daily_consumption * 30
        yearly_consumption = daily_consumption * 365
        
        result = {
            "population": population,
            "resource_type": resource_type,
            "efficiency_modifier": efficiency_modifier,
            "base_rate_per_person": base_rate,
            "daily_consumption": daily_consumption,
            "weekly_consumption": weekly_consumption,
            "monthly_consumption": monthly_consumption,
            "yearly_consumption": yearly_consumption,
            "critical_threshold": daily_consumption * 7,  # 1 week supply
            "shortage_threshold": daily_consumption * 3   # 3 day supply
        }
        
        logger.debug(f"Resource consumption calculated: {daily_consumption:.1f} {resource_type}/day")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating resource consumption: {e}")
        return {"error": str(e)}


def handle_resource_shortage(population: int, resource_type: str, shortage_percentage: float,
                           duration_days: int) -> Dict[str, Any]:
    """
    Handle resource shortage effects on population.
    
    Args:
        population: Current population
        resource_type: Type of resource in shortage
        shortage_percentage: Percentage of shortage (0.0-1.0)
        duration_days: Duration of shortage
        
    Returns:
        Dict containing shortage handling results
    """
    try:
        # Resource criticality affects impact
        criticality = {
            "food": 1.0,      # Critical
            "water": 1.0,     # Critical
            "medicine": 0.8,  # High
            "fuel": 0.6,      # Medium
            "materials": 0.4, # Low
            "luxury": 0.2     # Very Low
        }
        
        resource_criticality = criticality.get(resource_type, 0.6)
        
        # Calculate shortage impact
        shortage_impact = shortage_percentage * resource_criticality
        duration_factor = min(duration_days / 30.0, 3.0)  # Cap at 3x for 90+ days
        
        final_impact = shortage_impact * duration_factor
        
        # Calculate effects
        mortality_rate = final_impact * 0.2  # Up to 20% mortality for critical shortages
        migration_rate = final_impact * 0.4  # Up to 40% migration
        
        deaths = int(population * mortality_rate)
        migrants = int(population * migration_rate)
        remaining = population - deaths - migrants
        
        result = {
            "original_population": population,
            "resource_type": resource_type,
            "shortage_percentage": shortage_percentage,
            "duration_days": duration_days,
            "resource_criticality": resource_criticality,
            "final_impact": final_impact,
            "mortality_rate": mortality_rate,
            "migration_rate": migration_rate,
            "deaths": deaths,
            "migrants": migrants,
            "remaining_population": remaining,
            "recovery_needed": final_impact > 0.5
        }
        
        logger.info(f"Resource shortage handled: {resource_type} shortage caused {deaths} deaths, {migrants} migrants")
        return result
        
    except Exception as e:
        logger.error(f"Error handling resource shortage: {e}")
        return {"error": str(e)}


def calculate_resource_shortage_impact(population: int, resource_type: str,
                                     shortage_percentage: float, duration_days: int) -> Dict[str, Any]:
    """
    Calculate the impact of resource shortages on population.
    
    Args:
        population: Current population count
        resource_type: Type of resource in shortage
        shortage_percentage: Percentage of shortage (0.0-1.0)
        duration_days: Duration of shortage in days
        
    Returns:
        Dict containing shortage impact results
    """
    try:
        return handle_resource_shortage(population, resource_type, shortage_percentage, duration_days)
        
    except Exception as e:
        logger.error(f"Error calculating resource shortage impact: {e}")
        return {"error": str(e)}


# ============================================================================
# MIGRATION SYSTEM
# ============================================================================

def calculate_migration_impact(origin_population: int, destination_capacity: int,
                             push_factors: Dict[str, float], pull_factors: Dict[str, float],
                             distance_km: float = 100.0) -> Dict[str, Any]:
    """
    Calculate population migration between locations.
    
    Args:
        origin_population: Population at origin location
        destination_capacity: Available capacity at destination
        push_factors: Factors driving people away (war, famine, etc.)
        pull_factors: Factors attracting people (opportunities, safety, etc.)
        distance_km: Distance between locations in kilometers
        
    Returns:
        Dict containing migration analysis
    """
    try:
        # Calculate push pressure (reasons to leave)
        push_pressure = sum(push_factors.values()) / len(push_factors) if push_factors else 0.0
        
        # Calculate pull pressure (reasons to go to destination)
        pull_pressure = sum(pull_factors.values()) / len(pull_factors) if pull_factors else 0.0
        
        # Distance friction (farther = less likely to migrate)
        distance_friction = 1.0 / (1.0 + distance_km / 500.0)  # Halves at 500km
        
        # Calculate base migration rate
        base_migration_rate = (push_pressure + pull_pressure) * distance_friction * 0.2
        
        # Capacity constraint
        potential_migrants = int(origin_population * base_migration_rate)
        actual_migrants = min(potential_migrants, destination_capacity)
        
        # Calculate migration patterns
        migration_rate = actual_migrants / origin_population if origin_population > 0 else 0.0
        
        # Economic impact on both locations
        economic_impact_origin = -migration_rate * 0.3  # Loss of workforce
        economic_impact_destination = (actual_migrants / max(destination_capacity, 1)) * 0.2
        
        result = {
            "origin_population": origin_population,
            "destination_capacity": destination_capacity,
            "push_pressure": push_pressure,
            "pull_pressure": pull_pressure,
            "distance_km": distance_km,
            "distance_friction": distance_friction,
            "potential_migrants": potential_migrants,
            "actual_migrants": actual_migrants,
            "migration_rate": migration_rate,
            "remaining_at_origin": origin_population - actual_migrants,
            "economic_impact_origin": economic_impact_origin,
            "economic_impact_destination": economic_impact_destination,
            "migration_type": "forced" if push_pressure > 0.7 else "economic" if pull_pressure > push_pressure else "voluntary",
            "push_factors": push_factors,
            "pull_factors": pull_factors
        }
        
        logger.info(f"Migration calculated: {actual_migrants} people migrating from {origin_population} population")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating migration impact: {e}")
        return {"error": str(e)}


# ============================================================================
# SEASONAL EFFECTS SYSTEM
# ============================================================================

def calculate_seasonal_growth_modifier(current_season: str, climate_type: str = "temperate",
                                     resource_availability: float = 1.0) -> float:
    """
    Calculate seasonal modifier for population growth.
    
    Args:
        current_season: Current season (spring, summer, autumn, winter)
        climate_type: Climate type (tropical, temperate, arctic, desert)
        resource_availability: Resource availability factor (0.0-2.0)
        
    Returns:
        Growth modifier (0.5-1.5 range)
    """
    try:
        # Base seasonal modifiers by climate
        seasonal_modifiers = {
            "temperate": {
                "spring": 1.2,  # Favorable conditions
                "summer": 1.1,  # Good conditions
                "autumn": 1.0,  # Normal conditions
                "winter": 0.8   # Harsh conditions
            },
            "tropical": {
                "spring": 1.1,
                "summer": 0.9,  # Too hot/humid
                "autumn": 1.1,
                "winter": 1.2   # Mild, pleasant
            },
            "arctic": {
                "spring": 1.3,  # Brief good period
                "summer": 1.4,  # Best time
                "autumn": 0.9,
                "winter": 0.6   # Very harsh
            },
            "desert": {
                "spring": 1.2,
                "summer": 0.7,  # Extremely hot
                "autumn": 1.1,
                "winter": 1.0
            }
        }
        
        base_modifier = seasonal_modifiers.get(climate_type, seasonal_modifiers["temperate"])
        season_modifier = base_modifier.get(current_season, 1.0)
        
        # Resource availability impact
        resource_modifier = 0.5 + (resource_availability * 0.5)
        resource_modifier = max(0.5, min(resource_modifier, 1.5))
        
        # Calculate final modifier
        final_modifier = season_modifier * resource_modifier
        final_modifier = max(0.5, min(final_modifier, 1.5))  # Cap between 0.5-1.5
        
        logger.debug(f"Seasonal growth modifier: {current_season} in {climate_type} = {final_modifier}")
        return final_modifier
        
    except Exception as e:
        logger.error(f"Error calculating seasonal growth modifier: {e}")
        return 1.0  # Default to no modifier on error


def calculate_seasonal_death_rate_modifier(current_season: str, climate_type: str = "temperate",
                                         medical_care: float = 0.5, food_security: float = 1.0) -> float:
    """
    Calculate seasonal modifier for death rates.
    
    Args:
        current_season: Current season (spring, summer, autumn, winter)
        climate_type: Climate type (tropical, temperate, arctic, desert)
        medical_care: Medical care availability (0.0-1.0)
        food_security: Food security level (0.0-2.0)
        
    Returns:
        Death rate modifier (0.5-3.0 range)
    """
    try:
        # Base seasonal death rate modifiers by climate
        death_modifiers = {
            "temperate": {
                "spring": 0.9,   # Generally healthier
                "summer": 0.8,   # Best health period
                "autumn": 1.0,   # Normal
                "winter": 1.4    # Cold, disease
            },
            "tropical": {
                "spring": 1.0,
                "summer": 1.3,   # Disease season
                "autumn": 1.1,
                "winter": 0.9
            },
            "arctic": {
                "spring": 1.0,
                "summer": 0.7,   # Best survival time
                "autumn": 1.2,
                "winter": 2.0    # Very dangerous
            },
            "desert": {
                "spring": 0.9,
                "summer": 1.8,   # Extreme heat deaths
                "autumn": 1.0,
                "winter": 0.8
            }
        }
        
        base_modifier = death_modifiers.get(climate_type, death_modifiers["temperate"])
        season_modifier = base_modifier.get(current_season, 1.0)
        
        # Medical care reduces death rates
        medical_modifier = 1.0 - (medical_care * 0.4)  # Up to 40% reduction
        
        # Food security impact
        food_modifier = 2.0 - food_security  # Less food = higher death rate
        food_modifier = max(0.5, min(food_modifier, 2.0))
        
        # Calculate final modifier
        final_modifier = season_modifier * medical_modifier * food_modifier
        final_modifier = max(0.5, min(final_modifier, 3.0))  # Cap between 0.5-3.0
        
        logger.debug(f"Seasonal death rate modifier: {current_season} in {climate_type} = {final_modifier}")
        return final_modifier
        
    except Exception as e:
        logger.error(f"Error calculating seasonal death rate modifier: {e}")
        return 1.0  # Default to no modifier on error


# ============================================================================
# ADVANCED STATE MANAGEMENT
# ============================================================================

def is_valid_transition(current_state: str, target_state: str, population: int,
                       resources: Optional[Dict[str, float]] = None) -> bool:
    """
    Check if a POI state transition is valid.
    
    Args:
        current_state: Current POI state
        target_state: Desired target state
        population: Current population
        resources: Available resources
        
    Returns:
        True if transition is valid, False otherwise
    """
    try:
        # Define valid state transitions
        valid_transitions = {
            POIState.TINY.value: [POIState.SMALL.value, POIState.DECLINING.value, POIState.ABANDONED.value],
            POIState.SMALL.value: [POIState.TINY.value, POIState.MEDIUM.value, POIState.DECLINING.value],
            POIState.MEDIUM.value: [POIState.SMALL.value, POIState.LARGE.value, POIState.DECLINING.value],
            POIState.LARGE.value: [POIState.MEDIUM.value, POIState.HUGE.value, POIState.DECLINING.value],
            POIState.HUGE.value: [POIState.LARGE.value, POIState.DECLINING.value],
            POIState.DECLINING.value: [POIState.TINY.value, POIState.SMALL.value, POIState.ABANDONED.value],
            POIState.ABANDONED.value: [POIState.TINY.value]  # Can be resettled
        }
        
        # Check if transition is in allowed list
        allowed_transitions = valid_transitions.get(current_state, [])
        if target_state not in allowed_transitions:
            return False
        
        # Additional validation based on population thresholds
        population_thresholds = {
            POIState.TINY.value: (1, 100),
            POIState.SMALL.value: (100, 500),
            POIState.MEDIUM.value: (500, 2000),
            POIState.LARGE.value: (2000, 8000),
            POIState.HUGE.value: (8000, float('inf')),
            POIState.DECLINING.value: (0, float('inf')),
            POIState.ABANDONED.value: (0, 0)
        }
        
        min_pop, max_pop = population_thresholds.get(target_state, (0, float('inf')))
        if not (min_pop <= population <= max_pop):
            return False
        
        # Resource requirements for growth transitions
        if resources and target_state in [POIState.SMALL.value, POIState.MEDIUM.value, POIState.LARGE.value, POIState.HUGE.value]:
            required_resources = ["food", "water", "housing"]
            for resource in required_resources:
                if resources.get(resource, 0) < population * 0.8:  # 80% of needs met
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating state transition: {e}")
        return False


def is_valid_state_progression(state_history: List[Dict[str, Any]], 
                             max_changes_per_period: int = 2) -> bool:
    """
    Check if state progression follows realistic patterns.
    
    Args:
        state_history: List of state changes with timestamps
        max_changes_per_period: Maximum allowed changes per time period
        
    Returns:
        True if progression is valid, False otherwise
    """
    try:
        if len(state_history) < 2:
            return True
        
        # Check for rapid state changes (unrealistic)
        recent_changes = 0
        current_time = datetime.utcnow()
        
        for state_entry in state_history[-5:]:  # Check last 5 changes
            change_time = state_entry.get('timestamp', current_time)
            if isinstance(change_time, str):
                change_time = datetime.fromisoformat(change_time.replace('Z', '+00:00'))
            
            time_diff = (current_time - change_time).days
            if time_diff <= 30:  # Within last 30 days
                recent_changes += 1
        
        if recent_changes > max_changes_per_period:
            return False
        
        # Check for logical progression
        states = [entry.get('state') for entry in state_history[-3:]]
        
        # Prevent oscillation (A->B->A->B pattern)
        if len(states) >= 3:
            if states[0] == states[2] and states[0] != states[1]:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating state progression: {e}")
        return True  # Default to allowing progression on error


def estimate_time_to_state(current_population: int, current_state: str, target_state: str,
                          growth_rate: float = 0.02, resource_modifier: float = 1.0) -> Optional[int]:
    """
    Estimate time required to reach target population state.
    
    Args:
        current_population: Current population count
        current_state: Current POI state
        target_state: Target POI state
        growth_rate: Annual population growth rate
        resource_modifier: Resource availability modifier
        
    Returns:
        Estimated days to reach target state, or None if impossible
    """
    try:
        # Population thresholds for each state
        state_thresholds = {
            POIState.TINY.value: 50,
            POIState.SMALL.value: 300,
            POIState.MEDIUM.value: 1250,
            POIState.LARGE.value: 5000,
            POIState.HUGE.value: 15000
        }
        
        current_threshold = state_thresholds.get(current_state)
        target_threshold = state_thresholds.get(target_state)
        
        if not current_threshold or not target_threshold:
            return None
        
        # Declining/abandoned states
        if target_state in [POIState.DECLINING.value, POIState.ABANDONED.value]:
            # Estimate time for population decline
            decline_rate = abs(growth_rate) * 2  # Decline faster than growth
            if target_state == POIState.ABANDONED.value:
                target_population = 0
            else:
                target_population = current_population * 0.5  # 50% decline
            
            if decline_rate <= 0:
                return None
            
            years_to_decline = math.log(target_population / current_population) / math.log(1 - decline_rate)
            return int(abs(years_to_decline) * 365)
        
        # Growth states
        if target_threshold <= current_threshold:
            return 0  # Already at or past target
        
        target_population = target_threshold
        if current_population >= target_population:
            return 0
        
        # Apply resource modifier to growth rate
        effective_growth_rate = growth_rate * resource_modifier
        if effective_growth_rate <= 0:
            return None  # Cannot grow with negative/zero rate
        
        # Calculate time using compound growth formula
        years_to_target = math.log(target_population / current_population) / math.log(1 + effective_growth_rate)
        days_to_target = int(years_to_target * 365)
        
        # Add realistic constraints
        min_days = 30   # At least 1 month
        max_days = 3650  # At most 10 years
        
        return max(min_days, min(days_to_target, max_days))
        
    except Exception as e:
        logger.error(f"Error estimating time to state: {e}")
        return None


# ============================================================================
# POPULATION ANALYTICS
# ============================================================================

def get_poi_status_description(population: int, state: str, recent_events: Optional[List[str]] = None,
                              resource_status: Optional[Dict[str, str]] = None) -> str:
    """
    Generate a descriptive status summary for a POI.
    
    Args:
        population: Current population count
        state: Current POI state
        recent_events: List of recent events affecting the POI
        resource_status: Status of key resources
        
    Returns:
        Formatted status description string
    """
    try:
        # Base descriptions by state
        state_descriptions = {
            POIState.TINY.value: f"A small settlement of {population} residents",
            POIState.SMALL.value: f"A modest community with {population} inhabitants",
            POIState.MEDIUM.value: f"A growing town of {population} people",
            POIState.LARGE.value: f"A prosperous city housing {population} citizens",
            POIState.HUGE.value: f"A major metropolis with {population} residents",
            POIState.DECLINING.value: f"A declining settlement with {population} remaining residents",
            POIState.ABANDONED.value: "An abandoned settlement with only ruins remaining"
        }
        
        base_description = state_descriptions.get(state, f"A settlement of {population} people")
        
        # Add population trend context
        if state == POIState.DECLINING.value:
            base_description += ", showing signs of economic hardship and outmigration"
        elif state in [POIState.LARGE.value, POIState.HUGE.value]:
            base_description += ", bustling with trade and activity"
        elif state == POIState.TINY.value:
            base_description += ", struggling to maintain basic services"
        
        # Add recent events impact
        event_descriptions = []
        if recent_events:
            event_impacts = {
                "war": "Recently affected by warfare, with damaged infrastructure and displaced residents",
                "catastrophe": "Recovering from a recent natural disaster that displaced many inhabitants",
                "famine": "Suffering from food shortages that have driven many to seek opportunities elsewhere",
                "plague": "Dealing with the aftermath of disease that claimed many lives",
                "trade_boom": "Experiencing economic growth due to increased trade opportunities",
                "resource_discovery": "Benefiting from newly discovered natural resources in the area"
            }
            
            for event in recent_events[-3:]:  # Last 3 events
                if event in event_impacts:
                    event_descriptions.append(event_impacts[event])
        
        # Add resource status
        resource_descriptions = []
        if resource_status:
            resource_contexts = {
                "abundant": "well-supplied",
                "adequate": "adequately supplied",
                "scarce": "facing shortages",
                "critical": "in dire need"
            }
            
            for resource, status in resource_status.items():
                if status in ["scarce", "critical"]:
                    context = resource_contexts.get(status, status)
                    resource_descriptions.append(f"{context} with {resource}")
        
        # Combine all parts
        full_description = base_description
        
        if event_descriptions:
            full_description += ". " + ". ".join(event_descriptions)
        
        if resource_descriptions:
            full_description += f". The settlement is {', '.join(resource_descriptions)}"
        
        full_description += "."
        
        return full_description
        
    except Exception as e:
        logger.error(f"Error generating POI status description: {e}")
        return f"A settlement with {population} residents (status unavailable)" 