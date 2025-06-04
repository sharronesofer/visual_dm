"""
Population System Consolidated Utilities

This module consolidates and improves all population calculation functions,
eliminating duplicates and adding enhanced population control levers.
"""

import math
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND TYPES
# ============================================================================

class WarImpactSeverity(Enum):
    """War impact severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CATASTROPHIC = "catastrophic"

class CatastropheType(Enum):
    """Types of catastrophes that can affect population"""
    NATURAL_DISASTER = "natural_disaster"
    DISEASE = "disease"
    FAMINE = "famine"
    MAGICAL_EVENT = "magical_event"
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    DROUGHT = "drought"
    STORM = "storm"
    VOLCANIC = "volcanic"

class PopulationState(Enum):
    """Population states"""
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL = "critical"
    RECOVERING = "recovering"
    EVACUATED = "evacuated"
    EXTINCT = "extinct"

class RaceType(Enum):
    """Fantasy race types for population distribution"""
    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    HALFLING = "halfling"
    ORC = "orc"
    GOBLIN = "goblin"
    GIANT = "giant"
    DRAGON = "dragon"
    FAIRY = "fairy"
    BEAST_FOLK = "beast_folk"

# ============================================================================
# POPULATION CONTROL CONFIGURATION
# ============================================================================

DEFAULT_POPULATION_CONFIG = {
    "growth_control": {
        "base_growth_rate": 0.02,  # 2% annual growth
        "max_growth_rate": 0.08,   # 8% maximum
        "min_growth_rate": -0.05,  # -5% minimum (decline)
        "carrying_capacity_factor": 1.2,  # Soft cap multiplier
        "overpopulation_penalty": 0.15,   # Growth penalty when over capacity
        "underpopulation_bonus": 0.05     # Growth bonus when under minimum
    },
    "racial_distribution": {
        "default_weights": {
            RaceType.HUMAN.value: 0.60,     # 60% human default
            RaceType.ELF.value: 0.15,       # 15% elf
            RaceType.DWARF.value: 0.10,     # 10% dwarf
            RaceType.HALFLING.value: 0.08,  # 8% halfling
            RaceType.ORC.value: 0.04,       # 4% orc
            RaceType.GOBLIN.value: 0.02,    # 2% goblin
            RaceType.GIANT.value: 0.005,    # 0.5% giant
            RaceType.DRAGON.value: 0.001,   # 0.1% dragon
            RaceType.FAIRY.value: 0.003,    # 0.3% fairy
            RaceType.BEAST_FOLK.value: 0.002 # 0.2% beast folk
        },
        "regional_modifiers": {
            "forest": {
                RaceType.ELF.value: 2.0,     # Double elf population in forests
                RaceType.FAIRY.value: 3.0    # Triple fairy population
            },
            "mountain": {
                RaceType.DWARF.value: 3.0,   # Triple dwarf population in mountains
                RaceType.GIANT.value: 5.0    # 5x giant population
            },
            "urban": {
                RaceType.HUMAN.value: 1.5,   # More humans in cities
                RaceType.HALFLING.value: 1.8 # More halflings too
            },
            "wasteland": {
                RaceType.ORC.value: 4.0,     # 4x orc population in wastelands
                RaceType.GOBLIN.value: 3.0   # 3x goblin population
            }
        },
        "migration_preferences": {
            RaceType.ELF.value: ["forest", "coastal"],
            RaceType.DWARF.value: ["mountain", "underground"],
            RaceType.HUMAN.value: ["urban", "plains", "coastal"],
            RaceType.HALFLING.value: ["rural", "plains", "urban"],
            RaceType.ORC.value: ["wasteland", "mountain"],
            RaceType.GOBLIN.value: ["wasteland", "underground"],
            RaceType.GIANT.value: ["mountain", "remote"],
            RaceType.DRAGON.value: ["mountain", "remote", "ancient"],
            RaceType.FAIRY.value: ["forest", "magical"],
            RaceType.BEAST_FOLK.value: ["forest", "plains", "tribal"]
        }
    }
}

# ============================================================================
# POPULATION GROWTH CONTROL FUNCTIONS
# ============================================================================

def calculate_controlled_growth_rate(
    current_population: int,
    base_growth_rate: float,
    carrying_capacity: int,
    minimum_viable_population: int = 50,
    resource_availability: float = 1.0,
    stability_factor: float = 1.0,
    config: Optional[Dict] = None
) -> float:
    """
    Calculate population growth rate with comprehensive controls to prevent
    over/under-population issues.
    
    Args:
        current_population: Current settlement population
        base_growth_rate: Base annual growth rate
        carrying_capacity: Maximum sustainable population
        minimum_viable_population: Minimum to avoid extinction
        resource_availability: Resource abundance (0.0-2.0)
        stability_factor: Political/social stability (0.0-1.0)
        config: Optional configuration overrides
        
    Returns:
        Adjusted growth rate with all controls applied
    """
    if config is None:
        config = DEFAULT_POPULATION_CONFIG["growth_control"]
    
    # Start with base rate
    growth_rate = base_growth_rate
    
    # Carrying capacity effects (S-curve growth)
    capacity_ratio = current_population / max(1, carrying_capacity)
    if capacity_ratio > 1.0:
        # Overpopulation penalty
        overpopulation_factor = 1.0 - (capacity_ratio - 1.0) * config["overpopulation_penalty"]
        growth_rate *= max(0.1, overpopulation_factor)
    elif capacity_ratio < 0.3:
        # Underpopulation recovery bonus
        underpopulation_bonus = (0.3 - capacity_ratio) * config["underpopulation_bonus"]
        growth_rate += underpopulation_bonus
    
    # Minimum viable population effects
    if current_population < minimum_viable_population:
        extinction_pressure = 1.0 - (current_population / minimum_viable_population)
        growth_rate *= (1.0 - extinction_pressure * 0.8)  # Severe decline penalty
    
    # Resource availability effects
    if resource_availability < 0.8:
        resource_penalty = (0.8 - resource_availability) * 0.5
        growth_rate -= resource_penalty
    elif resource_availability > 1.2:
        resource_bonus = (resource_availability - 1.2) * 0.3
        growth_rate += resource_bonus
    
    # Stability effects
    stability_modifier = 0.5 + (stability_factor * 0.5)  # 0.5x to 1.0x
    growth_rate *= stability_modifier
    
    # Apply hard limits
    growth_rate = max(config["min_growth_rate"], min(config["max_growth_rate"], growth_rate))
    
    return growth_rate

def calculate_racial_distribution(
    total_population: int,
    region_type: str = "plains",
    cultural_factors: Optional[Dict[str, float]] = None,
    historical_distribution: Optional[Dict[str, float]] = None,
    migration_pressure: Optional[Dict[str, float]] = None,
    config: Optional[Dict] = None
) -> Dict[str, int]:
    """
    Calculate racial/species distribution for a population with detailed controls.
    
    Args:
        total_population: Total population to distribute
        region_type: Type of region (affects racial preferences)
        cultural_factors: Cultural modifiers per race
        historical_distribution: Previous racial makeup
        migration_pressure: Current migration forces per race
        config: Optional configuration overrides
        
    Returns:
        Dict mapping race names to population counts
    """
    if config is None:
        config = DEFAULT_POPULATION_CONFIG["racial_distribution"]
    
    # Start with base weights
    weights = config["default_weights"].copy()
    
    # Apply regional modifiers
    if region_type in config["regional_modifiers"]:
        regional_mods = config["regional_modifiers"][region_type]
        for race, modifier in regional_mods.items():
            if race in weights:
                weights[race] *= modifier
    
    # Apply cultural factors
    if cultural_factors:
        for race, factor in cultural_factors.items():
            if race in weights:
                weights[race] *= factor
    
    # Apply historical continuity (populations tend to stay similar)
    if historical_distribution:
        for race, historical_ratio in historical_distribution.items():
            if race in weights:
                # Blend 70% current calculation with 30% historical
                weights[race] = weights[race] * 0.7 + historical_ratio * 0.3
    
    # Apply migration pressure
    if migration_pressure:
        for race, pressure in migration_pressure.items():
            if race in weights:
                weights[race] *= (1.0 + pressure)
    
    # Normalize weights to ensure they sum to 1.0
    total_weight = sum(weights.values())
    if total_weight > 0:
        for race in weights:
            weights[race] /= total_weight
    
    # Calculate actual populations
    distribution = {}
    remaining_population = total_population
    
    # Assign populations (ensuring we don't exceed total)
    for race, weight in weights.items():
        if remaining_population <= 0:
            distribution[race] = 0
        else:
            race_population = min(remaining_population, round(total_population * weight))
            distribution[race] = race_population
            remaining_population -= race_population
    
    # Distribute any remainder to the most populous race
    if remaining_population > 0:
        most_populous_race = max(distribution, key=distribution.get)
        distribution[most_populous_race] += remaining_population
    
    return distribution

# ============================================================================
# WAR IMPACT SYSTEM (CONSOLIDATED)
# ============================================================================

def calculate_war_impact(
    population: int, 
    war_intensity: float, 
    duration_days: int,
    defensive_strength: float = 0.5,
    war_severity: Optional[WarImpactSeverity] = None
) -> Dict[str, Any]:
    """
    Consolidated war impact calculation with both intensity and severity options.
    
    Args:
        population: Current population count
        war_intensity: War intensity factor (0.0-1.0) - takes precedence
        duration_days: Duration of war in days
        defensive_strength: Defensive capabilities (0.0-1.0)
        war_severity: Alternative severity enum
        
    Returns:
        Dict containing comprehensive war impact results
    """
    try:
        # Convert severity to intensity if provided
        if war_severity and war_intensity <= 0:
            severity_to_intensity = {
                WarImpactSeverity.MINOR: 0.2,
                WarImpactSeverity.MODERATE: 0.4,
                WarImpactSeverity.MAJOR: 0.7,
                WarImpactSeverity.CATASTROPHIC: 1.0
            }
            war_intensity = severity_to_intensity.get(war_severity, 0.4)
        
        # Base mortality rate calculation
        base_mortality_rate = war_intensity * 0.3  # Up to 30% base mortality
        
        # Duration factor (longer wars are more devastating)
        duration_factor = 1.0 + (duration_days / 365.0) * 0.5  # +50% per year
        duration_factor = min(2.5, duration_factor)  # Cap at 2.5x
        
        # Defensive strength reduces casualties
        defense_modifier = 1.0 - (defensive_strength * 0.6)  # Up to 60% reduction
        
        # Calculate final mortality rate
        final_mortality_rate = base_mortality_rate * duration_factor * defense_modifier
        final_mortality_rate = max(0.0, min(final_mortality_rate, 0.85))  # Cap at 85%
        
        # Calculate casualties and refugees
        casualties = int(population * final_mortality_rate)
        refugee_rate = war_intensity * 0.4 * (1.0 - defensive_strength * 0.3)
        refugees = int(population * refugee_rate)
        
        # Infrastructure and economic damage
        infrastructure_damage = war_intensity * 0.7 * duration_factor * 0.8
        economic_impact = war_intensity * duration_factor * 0.5
        
        # Recovery time estimation
        recovery_time_days = int(duration_days * (1.5 + war_intensity))
        
        # Remaining population
        remaining_population = max(0, population - casualties)
        
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
            "infrastructure_damage": min(0.95, infrastructure_damage),
            "economic_impact": min(1.0, economic_impact),
            "recovery_time_days": recovery_time_days,
            "war_severity": war_severity.value if war_severity else "custom",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"War impact calculated: {casualties} casualties from {population} population")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating war impact: {e}")
        return {"error": str(e), "original_population": population}

# ============================================================================
# CATASTROPHE IMPACT SYSTEM (CONSOLIDATED)
# ============================================================================

def calculate_catastrophe_impact(
    population: int, 
    catastrophe_type: str, 
    severity: float,
    preparedness: float = 0.3,
    catastrophe_enum: Optional[CatastropheType] = None
) -> Dict[str, Any]:
    """
    Consolidated catastrophe impact calculation supporting both string and enum types.
    
    Args:
        population: Current population count
        catastrophe_type: Type of catastrophe (string)
        severity: Severity level (0.0-1.0)
        preparedness: Community preparedness level (0.0-1.0)
        catastrophe_enum: Alternative enum type
        
    Returns:
        Dict containing comprehensive catastrophe impact results
    """
    try:
        # Unified catastrophe impact table
        catastrophe_impacts = {
            "earthquake": {"mortality": 0.15, "displacement": 0.4, "injury": 0.25},
            "flood": {"mortality": 0.08, "displacement": 0.6, "injury": 0.15},
            "fire": {"mortality": 0.12, "displacement": 0.5, "injury": 0.3},
            "disease": {"mortality": 0.25, "displacement": 0.1, "injury": 0.4},
            "famine": {"mortality": 0.3, "displacement": 0.7, "injury": 0.1},
            "drought": {"mortality": 0.1, "displacement": 0.5, "injury": 0.05},
            "storm": {"mortality": 0.05, "displacement": 0.3, "injury": 0.2},
            "volcanic": {"mortality": 0.2, "displacement": 0.8, "injury": 0.15},
            "natural_disaster": {"mortality": 0.12, "displacement": 0.5, "injury": 0.3},
            "magical_event": {"mortality": 0.18, "displacement": 0.4, "injury": 0.35}
        }
        
        # Convert enum to string if provided
        if catastrophe_enum:
            catastrophe_type = catastrophe_enum.value
        
        base_impact = catastrophe_impacts.get(catastrophe_type.lower(), catastrophe_impacts["earthquake"])
        
        # Apply severity and preparedness modifiers
        preparedness_modifier = 1.0 - (preparedness * 0.7)  # Up to 70% reduction
        severity_modifier = 0.3 + (severity * 0.7)  # Scale from 30% to 100%
        
        # Calculate impacts
        mortality_rate = base_impact["mortality"] * severity_modifier * preparedness_modifier
        displacement_rate = base_impact["displacement"] * severity_modifier * preparedness_modifier
        injury_rate = base_impact["injury"] * severity_modifier * preparedness_modifier
        
        # Cap rates at reasonable maximums
        mortality_rate = max(0.0, min(mortality_rate, 0.75))
        displacement_rate = max(0.0, min(displacement_rate, 0.95))
        injury_rate = max(0.0, min(injury_rate, 0.9))
        
        # Calculate absolute numbers
        deaths = int(population * mortality_rate)
        displaced = int(population * displacement_rate)
        injured = int(population * injury_rate)
        
        remaining_population = max(0, population - deaths)
        
        # Recovery time based on severity and preparedness
        base_recovery_days = 30 + (severity * 300)  # 30 days to 11 months
        recovery_modifier = 1.0 - (preparedness * 0.5)
        recovery_time_days = int(base_recovery_days * recovery_modifier)
        
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
            "recovery_time_days": recovery_time_days,
            "infrastructure_damage": severity * 0.8,
            "economic_impact": severity * displacement_rate * 0.6,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Catastrophe impact calculated: {catastrophe_type} caused {deaths} deaths")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating catastrophe impact: {e}")
        return {"error": str(e), "original_population": population}

# ============================================================================
# RESOURCE MANAGEMENT SYSTEM (CONSOLIDATED)
# ============================================================================

def calculate_resource_consumption(
    population: int, 
    resource_type: str,
    base_consumption_per_capita: Optional[float] = None,
    efficiency_modifier: float = 1.0,
    modifiers: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Consolidated resource consumption calculation.
    
    Args:
        population: Population count
        resource_type: Type of resource
        base_consumption_per_capita: Override base consumption
        efficiency_modifier: Overall efficiency factor
        modifiers: Additional modifiers dict
        
    Returns:
        Dict containing comprehensive consumption analysis
    """
    try:
        # Default consumption rates per person per day
        default_consumption = {
            "food": 2.5,      # kg per day
            "water": 50.0,    # liters per day  
            "fuel": 5.0,      # liters per day
            "medicine": 0.1,  # units per day
            "materials": 1.0, # kg per day
            "luxury": 0.5,    # units per day
            "housing": 0.1,   # units per day
            "tools": 0.05     # units per day
        }
        
        base_rate = base_consumption_per_capita or default_consumption.get(resource_type, 1.0)
        
        # Apply efficiency modifier
        daily_consumption = population * base_rate * efficiency_modifier
        
        # Apply additional modifiers
        if modifiers:
            for modifier_name, multiplier in modifiers.items():
                daily_consumption *= multiplier
        
        # Calculate time periods
        weekly_consumption = daily_consumption * 7
        monthly_consumption = daily_consumption * 30
        yearly_consumption = daily_consumption * 365
        
        # Calculate thresholds
        critical_threshold = daily_consumption * 7   # 1 week supply
        shortage_threshold = daily_consumption * 3   # 3 day supply
        abundance_threshold = daily_consumption * 30 # 1 month supply
        
        result = {
            "population": population,
            "resource_type": resource_type,
            "efficiency_modifier": efficiency_modifier,
            "base_rate_per_person": base_rate,
            "daily_consumption": daily_consumption,
            "weekly_consumption": weekly_consumption,
            "monthly_consumption": monthly_consumption,
            "yearly_consumption": yearly_consumption,
            "critical_threshold": critical_threshold,
            "shortage_threshold": shortage_threshold,
            "abundance_threshold": abundance_threshold,
            "modifiers_applied": modifiers or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.debug(f"Resource consumption calculated: {daily_consumption:.1f} {resource_type}/day")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating resource consumption: {e}")
        return {"error": str(e)}

def calculate_resource_shortage_impact(
    population: int, 
    resource_type: str,
    shortage_percentage: float, 
    duration_days: int,
    resource_criticality: Optional[float] = None
) -> Dict[str, Any]:
    """
    Consolidated resource shortage impact calculation.
    
    Args:
        population: Current population
        resource_type: Type of resource in shortage
        shortage_percentage: Severity of shortage (0.0-1.0)
        duration_days: Duration of shortage
        resource_criticality: How critical the resource is (0.0-1.0)
        
    Returns:
        Dict containing shortage impact results
    """
    try:
        # Resource criticality mapping
        criticality_map = {
            "food": 0.9,      # Highly critical
            "water": 0.95,    # Most critical
            "medicine": 0.7,  # Moderately critical
            "fuel": 0.5,      # Less critical
            "materials": 0.3, # Least critical
            "luxury": 0.1,    # Almost no impact
            "housing": 0.6,   # Moderately critical
            "tools": 0.4      # Less critical
        }
        
        criticality = resource_criticality or criticality_map.get(resource_type, 0.5)
        
        # Calculate base impact rate
        base_impact_rate = shortage_percentage * criticality
        
        # Duration factor (longer shortages are worse)
        duration_factor = 1.0 + (duration_days / 30.0) * 0.3  # +30% per month
        duration_factor = min(2.0, duration_factor)
        
        # Calculate final impact
        final_impact_rate = base_impact_rate * duration_factor
        final_impact_rate = min(0.6, final_impact_rate)  # Cap at 60%
        
        # Calculate deaths and migration
        deaths = int(population * final_impact_rate * 0.7)  # 70% die
        migrants = int(population * final_impact_rate * 0.3) # 30% migrate
        
        remaining_population = max(0, population - deaths - migrants)
        
        result = {
            "original_population": population,
            "resource_type": resource_type,
            "shortage_percentage": shortage_percentage,
            "duration_days": duration_days,
            "resource_criticality": criticality,
            "impact_rate": final_impact_rate,
            "deaths": deaths,
            "migrants": migrants,
            "remaining_population": remaining_population,
            "recovery_time_days": duration_days + int(shortage_percentage * 60),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Resource shortage impact: {resource_type} shortage caused {deaths} deaths, {migrants} migrants")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating resource shortage impact: {e}")
        return {"error": str(e)}

# ============================================================================
# MIGRATION SYSTEM (CONSOLIDATED)
# ============================================================================

def calculate_migration_impact(
    origin_population: int,
    destination_capacity: int,
    push_factors: Dict[str, float],
    pull_factors: Dict[str, float],
    distance_km: float = 100.0,
    migration_barriers: float = 0.0
) -> Dict[str, Any]:
    """
    Consolidated migration calculation with comprehensive factors.
    
    Args:
        origin_population: Population at origin
        destination_capacity: Available capacity at destination
        push_factors: Factors driving migration away from origin
        pull_factors: Factors attracting migration to destination
        distance_km: Distance between locations
        migration_barriers: Barriers to migration (0.0-1.0)
        
    Returns:
        Dict containing migration results
    """
    try:
        # Calculate push pressure (sum of negative factors)
        push_pressure = sum(max(0, factor) for factor in push_factors.values())
        push_pressure = min(1.0, push_pressure)  # Cap at 100%
        
        # Calculate pull pressure (sum of positive factors)
        pull_pressure = sum(max(0, factor) for factor in pull_factors.values())
        pull_pressure = min(1.0, pull_pressure)  # Cap at 100%
        
        # Distance penalty (farther = less migration)
        distance_penalty = 1.0 / (1.0 + distance_km / 100.0)
        
        # Migration barriers factor
        barrier_factor = 1.0 - migration_barriers
        
        # Calculate migration pressure
        migration_pressure = (push_pressure + pull_pressure) * 0.5
        migration_pressure *= distance_penalty * barrier_factor
        
        # Calculate potential migrants
        potential_migrants = int(origin_population * migration_pressure * 0.2)  # Max 20% migrate
        
        # Limit by destination capacity
        actual_migrants = min(potential_migrants, destination_capacity)
        
        # Calculate remaining population
        remaining_at_origin = max(0, origin_population - actual_migrants)
        
        result = {
            "origin_population": origin_population,
            "destination_capacity": destination_capacity,
            "push_pressure": push_pressure,
            "pull_pressure": pull_pressure,
            "migration_pressure": migration_pressure,
            "distance_km": distance_km,
            "distance_penalty": distance_penalty,
            "migration_barriers": migration_barriers,
            "potential_migrants": potential_migrants,
            "actual_migrants": actual_migrants,
            "remaining_at_origin": remaining_at_origin,
            "push_factors": push_factors,
            "pull_factors": pull_factors,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Migration calculated: {actual_migrants} people migrating")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating migration impact: {e}")
        return {"error": str(e)}

# ============================================================================
# SEASONAL EFFECTS (CONSOLIDATED)
# ============================================================================

def calculate_seasonal_growth_modifier(
    current_season: str,
    climate_type: str = "temperate",
    base_growth_rate: float = 0.02,
    resource_availability: float = 1.0
) -> float:
    """
    Consolidated seasonal growth rate modifier calculation.
    
    Args:
        current_season: Current season name
        climate_type: Climate type of region
        base_growth_rate: Base growth rate to modify
        resource_availability: Resource abundance factor
        
    Returns:
        Modified growth rate incorporating seasonal effects
    """
    try:
        # Seasonal modifiers by climate
        seasonal_modifiers = {
            "temperate": {
                "spring": 1.2,   # 20% boost
                "summer": 1.1,   # 10% boost
                "autumn": 1.0,   # No change
                "winter": 0.8    # 20% penalty
            },
            "tropical": {
                "wet_season": 1.15,  # 15% boost
                "dry_season": 0.9    # 10% penalty
            },
            "arctic": {
                "summer": 1.3,   # 30% boost (short growing season)
                "winter": 0.6    # 40% penalty
            },
            "desert": {
                "spring": 1.1,   # 10% boost
                "summer": 0.7,   # 30% penalty (too hot)
                "autumn": 1.0,   # No change
                "winter": 0.9    # 10% penalty
            }
        }
        
        climate_mods = seasonal_modifiers.get(climate_type, seasonal_modifiers["temperate"])
        season_modifier = climate_mods.get(current_season.lower(), 1.0)
        
        # Apply resource availability
        resource_modifier = 0.5 + (resource_availability * 0.5)  # 0.5x to 1.0x
        
        # Calculate final modifier
        final_modifier = season_modifier * resource_modifier
        
        # Apply to base growth rate
        modified_growth_rate = base_growth_rate * final_modifier
        
        logger.debug(f"Seasonal growth modifier: {current_season} in {climate_type} = {final_modifier}")
        return modified_growth_rate
        
    except Exception as e:
        logger.error(f"Error calculating seasonal growth modifier: {e}")
        return base_growth_rate

def calculate_seasonal_death_rate_modifier(
    current_season: str,
    climate_type: str = "temperate",
    base_death_rate: float = 0.015,
    medical_care: float = 0.5,
    food_security: float = 1.0,
    healthcare_level: float = 0.5
) -> float:
    """
    Consolidated seasonal death rate modifier calculation.
    
    Args:
        current_season: Current season name
        climate_type: Climate type of region
        base_death_rate: Base death rate to modify
        medical_care: Medical care quality (0.0-1.0)
        food_security: Food security level (0.0-2.0)
        healthcare_level: Alternative healthcare parameter
        
    Returns:
        Modified death rate incorporating seasonal effects
    """
    try:
        # Use the higher of medical_care or healthcare_level
        effective_healthcare = max(medical_care, healthcare_level)
        
        # Seasonal death rate modifiers
        seasonal_modifiers = {
            "temperate": {
                "spring": 0.9,   # 10% reduction
                "summer": 0.85,  # 15% reduction
                "autumn": 1.0,   # No change
                "winter": 1.3    # 30% increase
            },
            "tropical": {
                "wet_season": 1.1,   # 10% increase (disease)
                "dry_season": 0.95   # 5% reduction
            },
            "arctic": {
                "summer": 0.8,   # 20% reduction
                "winter": 1.6    # 60% increase (harsh)
            },
            "desert": {
                "spring": 0.95,  # 5% reduction
                "summer": 1.4,   # 40% increase (heat)
                "autumn": 1.0,   # No change
                "winter": 1.1    # 10% increase
            }
        }
        
        climate_mods = seasonal_modifiers.get(climate_type, seasonal_modifiers["temperate"])
        season_modifier = climate_mods.get(current_season.lower(), 1.0)
        
        # Healthcare reduces seasonal death rate variations
        healthcare_dampening = 1.0 - (effective_healthcare * 0.4)  # Up to 40% reduction
        adjusted_modifier = 1.0 + ((season_modifier - 1.0) * healthcare_dampening)
        
        # Food security affects death rates
        food_modifier = 2.0 - food_security  # Low food = higher death rate
        food_modifier = max(0.5, min(food_modifier, 2.0))
        
        # Calculate final death rate
        final_modifier = adjusted_modifier * food_modifier
        modified_death_rate = base_death_rate * final_modifier
        
        logger.debug(f"Seasonal death rate modifier: {current_season} in {climate_type} = {final_modifier}")
        return modified_death_rate
        
    except Exception as e:
        logger.error(f"Error calculating seasonal death rate modifier: {e}")
        return base_death_rate

# ============================================================================
# STATE MANAGEMENT FUNCTIONS (CONSOLIDATED)
# ============================================================================

def is_valid_transition(
    current_state: str,
    target_state: str, 
    population: int,
    resources: Optional[Dict[str, float]] = None
) -> bool:
    """
    Validate if a population state transition is allowed.
    
    Args:
        current_state: Current population state
        target_state: Desired target state
        population: Current population count
        resources: Available resources
        
    Returns:
        True if transition is valid
    """
    try:
        if resources is None:
            resources = {}
        
        # State transition rules
        valid_transitions = {
            "growing": ["stable", "declining", "critical"],
            "stable": ["growing", "declining", "critical"],
            "declining": ["stable", "critical", "recovering", "evacuated"],
            "critical": ["declining", "recovering", "evacuated", "extinct"],
            "recovering": ["stable", "growing", "declining"],
            "evacuated": ["recovering", "extinct"],
            "extinct": []  # No transitions from extinct
        }
        
        # Check if transition is in allowed list
        allowed_targets = valid_transitions.get(current_state, [])
        if target_state not in allowed_targets:
            return False
        
        # Population-based validation
        if target_state == "extinct" and population > 10:
            return False
        
        if target_state == "critical" and population > 100:
            # Can only be critical if population is very low or resources are scarce
            resource_scarcity = sum(1 for v in resources.values() if v < 0.3)
            if resource_scarcity < 2:  # Need at least 2 scarce resources
                return False
        
        if target_state == "growing" and population < 20:
            return False  # Need minimum population to grow
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating state transition: {e}")
        return False

def is_valid_state_progression(
    state_history: List[Dict[str, Any]], 
    max_changes_per_period: int = 2
) -> bool:
    """
    Validate that state changes aren't happening too rapidly.
    
    Args:
        state_history: List of state change records
        max_changes_per_period: Maximum changes allowed per time period
        
    Returns:
        True if progression is valid
    """
    try:
        if len(state_history) < 2:
            return True
        
        # Check for rapid state changes (more than max_changes_per_period in 30 days)
        recent_changes = []
        now = datetime.utcnow()
        
        for entry in state_history:
            if "timestamp" in entry:
                timestamp = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                days_ago = (now - timestamp).days
                if days_ago <= 30:
                    recent_changes.append(entry)
        
        if len(recent_changes) > max_changes_per_period:
            return False
        
        # Check for logical progressions (no sudden jumps)
        for i in range(1, len(state_history)):
            current = state_history[i].get("state", "")
            previous = state_history[i-1].get("state", "")
            
            # Prevent impossible jumps
            impossible_jumps = [
                ("extinct", "growing"),
                ("extinct", "stable"),
                ("critical", "growing"),
                ("evacuated", "growing")
            ]
            
            if (previous, current) in impossible_jumps:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating state progression: {e}")
        return False

def estimate_time_to_state(
    current_population: int,
    current_state: str,
    target_state: str,
    growth_rate: float = 0.02,
    resource_modifier: float = 1.0
) -> Optional[int]:
    """
    Estimate time required to reach a target population state.
    
    Args:
        current_population: Current population
        current_state: Current state
        target_state: Target state to reach
        growth_rate: Annual growth rate
        resource_modifier: Resource availability modifier
        
    Returns:
        Estimated days to reach target state, or None if impossible
    """
    try:
        # State population thresholds
        state_thresholds = {
            "extinct": 0,
            "critical": 50,
            "declining": 100,
            "recovering": 200,
            "stable": 500,
            "growing": 1000
        }
        
        current_threshold = state_thresholds.get(current_state, current_population)
        target_threshold = state_thresholds.get(target_state, None)
        
        if target_threshold is None:
            return None
        
        # Calculate population change needed
        population_change = target_threshold - current_population
        
        if population_change == 0:
            return 0
        
        # Apply resource modifier to growth rate
        effective_growth_rate = growth_rate * resource_modifier
        
        if effective_growth_rate <= 0 and population_change > 0:
            return None  # Can't grow with negative or zero growth
        
        if effective_growth_rate >= 0 and population_change < 0:
            # Need to estimate decline time (harder to predict)
            decline_rate = abs(effective_growth_rate) * 0.5  # Slower decline
            if decline_rate <= 0:
                return None
            days_to_decline = abs(population_change) / (current_population * decline_rate / 365)
            return int(days_to_decline)
        
        # Calculate growth time using compound growth formula
        if population_change > 0 and effective_growth_rate > 0:
            # Target = Current * (1 + rate)^years
            # years = ln(Target/Current) / ln(1 + rate)
            years_to_grow = math.log(target_threshold / current_population) / math.log(1 + effective_growth_rate)
            return int(years_to_grow * 365)
        
        return None
        
    except Exception as e:
        logger.error(f"Error estimating time to state: {e}")
        return None

def get_poi_status_description(
    population: int,
    state: str,
    recent_events: Optional[List[str]] = None,
    resource_status: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate a descriptive status for a POI based on its population and conditions.
    
    Args:
        population: Current population
        state: Current population state
        recent_events: List of recent events
        resource_status: Status of various resources
        
    Returns:
        Human-readable status description
    """
    try:
        # Base descriptions by state
        base_descriptions = {
            "growing": f"Thriving settlement with {population} residents showing strong growth",
            "stable": f"Established community of {population} people maintaining steady population",
            "declining": f"Settlement of {population} residents experiencing population decline",
            "critical": f"Struggling community with only {population} residents in dire circumstances",
            "recovering": f"Recovering settlement of {population} people rebuilding after hardship",
            "evacuated": f"Largely abandoned area with {population} remaining residents",
            "extinct": "Abandoned settlement with no remaining population"
        }
        
        description = base_descriptions.get(state, f"Settlement with {population} residents")
        
        # Add recent events context
        if recent_events:
            event_context = {
                "war": "affected by recent conflict",
                "disaster": "recovering from natural disaster",
                "plague": "dealing with disease outbreak",
                "famine": "suffering from food shortages",
                "migration": "experiencing population movement"
            }
            
            for event in recent_events:
                if event.lower() in event_context:
                    description += f", {event_context[event.lower()]}"
        
        # Add resource status
        if resource_status:
            critical_resources = [k for k, v in resource_status.items() if v == "critical"]
            if critical_resources:
                description += f", critically short on {', '.join(critical_resources)}"
            
            abundant_resources = [k for k, v in resource_status.items() if v == "abundant"]
            if abundant_resources:
                description += f", well-supplied with {', '.join(abundant_resources)}"
        
        return description
        
    except Exception as e:
        logger.error(f"Error generating POI status description: {e}")
        return f"Settlement with {population} residents" 