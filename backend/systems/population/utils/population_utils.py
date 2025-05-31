"""
Population System Utilities

This module implements the missing functionality for the Population System
as identified in Task 45.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from enum import Enum

# Remove problematic imports to avoid circular imports
# from backend.infrastructure.models import BaseModel
# from backend.systems.population.models import PopulationModel

logger = logging.getLogger(__name__)


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


def calculate_war_impact(
    population: int,
    war_severity: WarImpactSeverity,
    duration_days: int,
    defensive_measures: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate the impact of war on population
    
    Args:
        population: Current population count
        war_severity: Severity of the war impact
        duration_days: Duration of war in days
        defensive_measures: Defensive effectiveness (0.0-1.0)
    
    Returns:
        Dict containing impact calculations
    """
    try:
        # Base mortality rates by severity
        mortality_rates = {
            WarImpactSeverity.MINOR: 0.01,      # 1% loss
            WarImpactSeverity.MODERATE: 0.05,   # 5% loss
            WarImpactSeverity.MAJOR: 0.15,      # 15% loss
            WarImpactSeverity.CATASTROPHIC: 0.30 # 30% loss
        }
        
        base_mortality = mortality_rates.get(war_severity, 0.05)
        
        # Apply duration factor (longer wars have increased impact)
        duration_factor = min(2.0, 1.0 + (duration_days / 365.0))
        
        # Apply defensive measures (reduces impact)
        defense_factor = 1.0 - (defensive_measures * 0.7)  # Max 70% reduction
        
        # Calculate final mortality rate
        final_mortality = base_mortality * duration_factor * defense_factor
        final_mortality = min(0.8, final_mortality)  # Cap at 80% loss
        
        population_loss = int(population * final_mortality)
        surviving_population = population - population_loss
        
        # Calculate additional effects
        refugee_count = int(population_loss * 0.3)  # 30% become refugees
        infrastructure_damage = min(0.9, final_mortality * 1.2)
        
        return {
            "initial_population": population,
            "population_loss": population_loss,
            "surviving_population": surviving_population,
            "mortality_rate": final_mortality,
            "refugee_count": refugee_count,
            "infrastructure_damage": infrastructure_damage,
            "economic_impact": final_mortality * 0.8,
            "recovery_time_days": int(duration_days * 2.5),
            "war_severity": war_severity.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating war impact: {e}")
        return {
            "error": str(e),
            "initial_population": population,
            "population_loss": 0,
            "surviving_population": population
        }


def calculate_catastrophe_impact(
    population: int,
    catastrophe_type: CatastropheType,
    severity: float,
    preparation_level: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate the impact of catastrophes on population
    
    Args:
        population: Current population count
        catastrophe_type: Type of catastrophe
        severity: Severity level (0.0-1.0)
        preparation_level: Community preparation (0.0-1.0)
    
    Returns:
        Dict containing catastrophe impact calculations
    """
    try:
        # Base impact rates by catastrophe type
        base_impacts = {
            CatastropheType.NATURAL_DISASTER: 0.1,  # 10% base impact
            CatastropheType.DISEASE: 0.15,          # 15% base impact
            CatastropheType.FAMINE: 0.2,            # 20% base impact
            CatastropheType.MAGICAL_EVENT: 0.25,    # 25% base impact
        }
        
        base_impact = base_impacts.get(catastrophe_type, 0.1)
        
        # Apply severity multiplier
        severity_multiplier = 0.5 + (severity * 1.5)  # 0.5x to 2.0x
        
        # Apply preparation factor (reduces impact)
        preparation_factor = 1.0 - (preparation_level * 0.6)  # Max 60% reduction
        
        # Calculate final impact
        final_impact = base_impact * severity_multiplier * preparation_factor
        final_impact = min(0.7, final_impact)  # Cap at 70% loss
        
        population_loss = int(population * final_impact)
        surviving_population = population - population_loss
        
        # Type-specific effects
        type_effects = {
            CatastropheType.NATURAL_DISASTER: {
                "displaced_population": int(population_loss * 0.8),
                "infrastructure_damage": final_impact * 1.5,
                "resource_loss": final_impact * 0.7
            },
            CatastropheType.DISEASE: {
                "quarantine_needed": True,
                "medical_demand": final_impact * 2.0,
                "trade_disruption": final_impact * 0.9
            },
            CatastropheType.FAMINE: {
                "migration_pressure": final_impact * 1.2,
                "social_unrest": final_impact * 0.8,
                "economic_collapse": final_impact * 1.1
            },
            CatastropheType.MAGICAL_EVENT: {
                "magical_instability": final_impact * 1.3,
                "reality_distortion": severity,
                "magical_contamination": final_impact * 0.6
            }
        }
        
        return {
            "initial_population": population,
            "population_loss": population_loss,
            "surviving_population": surviving_population,
            "impact_rate": final_impact,
            "catastrophe_type": catastrophe_type.value,
            "severity": severity,
            "preparation_level": preparation_level,
            "specific_effects": type_effects.get(catastrophe_type, {}),
            "recovery_time_days": int(30 + (final_impact * 365)),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating catastrophe impact: {e}")
        return {
            "error": str(e),
            "initial_population": population,
            "population_loss": 0,
            "surviving_population": population
        }


def calculate_resource_consumption(
    population: int,
    resource_type: str,
    base_consumption_per_capita: float,
    modifiers: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Calculate resource consumption for a population
    
    Args:
        population: Population count
        resource_type: Type of resource (food, water, materials, etc.)
        base_consumption_per_capita: Base consumption per person
        modifiers: Dict of modifier names to multipliers
    
    Returns:
        Dict containing consumption calculations
    """
    try:
        if modifiers is None:
            modifiers = {}
            
        # Calculate base consumption
        base_total = population * base_consumption_per_capita
        
        # Apply modifiers
        final_multiplier = 1.0
        for modifier_name, multiplier in modifiers.items():
            final_multiplier *= multiplier
            
        final_consumption = base_total * final_multiplier
        
        # Calculate efficiency metrics
        efficiency = 1.0 / final_multiplier if final_multiplier > 0 else 1.0
        waste_factor = max(0.0, final_multiplier - 1.0) * 0.3
        
        return {
            "population": population,
            "resource_type": resource_type,
            "base_consumption_per_capita": base_consumption_per_capita,
            "base_total_consumption": base_total,
            "final_consumption": final_consumption,
            "modifiers_applied": modifiers,
            "final_multiplier": final_multiplier,
            "efficiency_rating": efficiency,
            "estimated_waste": final_consumption * waste_factor,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating resource consumption: {e}")
        return {
            "error": str(e),
            "population": population,
            "final_consumption": 0
        }


def calculate_resource_shortage_impact(
    population: int,
    shortage_severity: float,
    resource_criticality: float,
    duration_days: int
) -> Dict[str, Any]:
    """
    Calculate the impact of resource shortages on population
    
    Args:
        population: Current population
        shortage_severity: How severe the shortage is (0.0-1.0)
        resource_criticality: How critical the resource is (0.0-1.0)
        duration_days: How long the shortage lasts
    
    Returns:
        Dict containing shortage impact analysis
    """
    try:
        # Calculate impact based on severity and criticality
        base_impact = shortage_severity * resource_criticality
        
        # Duration amplifies impact
        duration_factor = min(3.0, 1.0 + (duration_days / 30.0))  # Max 3x for month+
        
        final_impact = base_impact * duration_factor
        final_impact = min(0.8, final_impact)  # Cap at 80%
        
        # Calculate effects
        population_stress = final_impact
        migration_pressure = final_impact * 0.7
        social_unrest = final_impact * 0.6
        health_decline = final_impact * 0.8
        
        # Critical shortage threshold effects
        critical_effects = {}
        if final_impact > 0.6:  # Critical shortage
            critical_effects = {
                "mass_migration": True,
                "government_collapse_risk": final_impact > 0.7,
                "humanitarian_crisis": True,
                "international_intervention_needed": final_impact > 0.75
            }
            
        return {
            "population": population,
            "shortage_severity": shortage_severity,
            "resource_criticality": resource_criticality,
            "duration_days": duration_days,
            "final_impact": final_impact,
            "population_stress": population_stress,
            "migration_pressure": migration_pressure,
            "social_unrest": social_unrest,
            "health_decline": health_decline,
            "critical_effects": critical_effects,
            "estimated_population_loss": int(population * final_impact * 0.1),
            "recovery_time_days": duration_days * 2,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating resource shortage impact: {e}")
        return {
            "error": str(e),
            "population": population,
            "final_impact": 0
        }


def calculate_migration_impact(
    origin_population: int,
    destination_capacity: int,
    migration_pressure: float,
    migration_barriers: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate migration between populations
    
    Args:
        origin_population: Population of origin location
        destination_capacity: Capacity of destination
        migration_pressure: Pressure to migrate (0.0-1.0)
        migration_barriers: Barriers to migration (0.0-1.0)
    
    Returns:
        Dict containing migration calculations
    """
    try:
        # Calculate potential migrants
        potential_migrants = int(origin_population * migration_pressure)
        
        # Apply barriers (reduces actual migration)
        barrier_factor = 1.0 - migration_barriers
        actual_migrants = int(potential_migrants * barrier_factor)
        
        # Check destination capacity constraints
        available_capacity = max(0, destination_capacity - destination_capacity * 0.8)  # Assume 80% full
        capacity_limited_migrants = min(actual_migrants, int(available_capacity))
        
        # Calculate overflow (refugees, displaced)
        overflow = actual_migrants - capacity_limited_migrants
        
        # Calculate impacts
        origin_impact = {
            "population_loss": capacity_limited_migrants,
            "economic_impact": (capacity_limited_migrants / origin_population) * 0.6,
            "social_stability": 1.0 - (migration_pressure * 0.4)
        }
        
        destination_impact = {
            "population_gain": capacity_limited_migrants,
            "resource_strain": (capacity_limited_migrants / destination_capacity) * 1.2,
            "cultural_change": (capacity_limited_migrants / destination_capacity) * 0.5,
            "economic_boost": (capacity_limited_migrants / destination_capacity) * 0.3
        }
        
        return {
            "origin_population": origin_population,
            "destination_capacity": destination_capacity,
            "migration_pressure": migration_pressure,
            "migration_barriers": migration_barriers,
            "potential_migrants": potential_migrants,
            "actual_migrants": capacity_limited_migrants,
            "overflow_displaced": overflow,
            "origin_impact": origin_impact,
            "destination_impact": destination_impact,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating migration impact: {e}")
        return {
            "error": str(e),
            "actual_migrants": 0,
            "overflow_displaced": 0
        }


def calculate_seasonal_growth_modifier(
    base_growth_rate: float,
    season: str,
    climate_type: str = "temperate"
) -> float:
    """
    Calculate seasonal modifier for population growth
    
    Args:
        base_growth_rate: Base population growth rate
        season: Current season (spring, summer, autumn, winter)
        climate_type: Climate type affecting seasonal impact
    
    Returns:
        Modified growth rate
    """
    try:
        # Seasonal modifiers by climate
        seasonal_modifiers = {
            "temperate": {
                "spring": 1.1,   # +10% growth (favorable)
                "summer": 1.05,  # +5% growth (good conditions)
                "autumn": 0.95,  # -5% growth (harvest/preparation)
                "winter": 0.85   # -15% growth (harsh conditions)
            },
            "tropical": {
                "spring": 1.0,
                "summer": 1.02,
                "autumn": 1.0,
                "winter": 1.0
            },
            "arctic": {
                "spring": 1.2,   # +20% (relief from winter)
                "summer": 1.1,   # +10% (best conditions)
                "autumn": 0.9,   # -10% (preparing for winter)
                "winter": 0.7    # -30% (harsh survival)
            },
            "desert": {
                "spring": 1.05,
                "summer": 0.8,   # -20% (extreme heat)
                "autumn": 1.05,
                "winter": 1.1    # +10% (mild season)
            }
        }
        
        modifier = seasonal_modifiers.get(climate_type, {}).get(season, 1.0)
        return base_growth_rate * modifier
        
    except Exception as e:
        logger.error(f"Error calculating seasonal growth modifier: {e}")
        return base_growth_rate


def calculate_seasonal_death_rate_modifier(
    base_death_rate: float,
    season: str,
    climate_type: str = "temperate",
    healthcare_level: float = 0.5
) -> float:
    """
    Calculate seasonal modifier for death rate
    
    Args:
        base_death_rate: Base death rate
        season: Current season
        climate_type: Climate type
        healthcare_level: Healthcare quality (0.0-1.0)
    
    Returns:
        Modified death rate
    """
    try:
        # Base seasonal death rate modifiers
        seasonal_modifiers = {
            "temperate": {
                "spring": 0.9,   # -10% (mild weather)
                "summer": 0.95,  # -5% (good conditions)
                "autumn": 1.0,   # baseline
                "winter": 1.3    # +30% (cold, disease)
            },
            "tropical": {
                "spring": 1.0,
                "summer": 1.1,   # +10% (disease season)
                "autumn": 1.0,
                "winter": 0.95
            },
            "arctic": {
                "spring": 0.8,   # -20% (survival relief)
                "summer": 0.7,   # -30% (best conditions)
                "autumn": 1.1,   # +10% (prep stress)
                "winter": 1.8    # +80% (extreme survival)
            },
            "desert": {
                "spring": 0.95,
                "summer": 1.4,   # +40% (extreme heat)
                "autumn": 0.95,
                "winter": 0.9
            }
        }
        
        base_modifier = seasonal_modifiers.get(climate_type, {}).get(season, 1.0)
        
        # Healthcare reduces seasonal death rate increases
        healthcare_factor = 1.0 - (healthcare_level * 0.4)  # Up to 40% reduction
        if base_modifier > 1.0:  # Only reduce negative modifiers
            final_modifier = 1.0 + ((base_modifier - 1.0) * healthcare_factor)
        else:
            final_modifier = base_modifier
            
        return base_death_rate * final_modifier
        
    except Exception as e:
        logger.error(f"Error calculating seasonal death rate modifier: {e}")
        return base_death_rate
