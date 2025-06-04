"""
Population System - Demographic Mathematical Models

This module implements the mathematical models for population dynamics including
birth/death rates, migration patterns, demographic changes, and settlement dynamics
as specified in Task 74.
"""

import math
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class AgeGroup(Enum):
    """Standard age groups for demographic analysis"""
    INFANT = "0-2"          # 0-2 years
    CHILD = "3-12"          # 3-12 years  
    ADOLESCENT = "13-17"    # 13-17 years
    YOUNG_ADULT = "18-25"   # 18-25 years
    ADULT = "26-40"         # 26-40 years
    MIDDLE_AGED = "41-60"   # 41-60 years
    ELDER = "61-80"         # 61-80 years
    ANCIENT = "81+"         # 81+ years


class MigrationType(Enum):
    """Types of migration patterns"""
    ECONOMIC = "economic"
    SAFETY = "safety"
    FAMILY = "family"
    SEASONAL = "seasonal"
    FORCED = "forced"
    RETURN = "return"


class SettlementType(Enum):
    """Types of settlements for population dynamics"""
    VILLAGE = "village"           # <500
    TOWN = "town"                # 500-2000
    CITY = "city"                # 2000-10000
    LARGE_CITY = "large_city"    # 10000-50000
    METROPOLIS = "metropolis"    # 50000+


@dataclass
class DemographicProfile:
    """Complete demographic profile for a population"""
    total_population: int
    age_distribution: Dict[AgeGroup, int]
    birth_rate: float           # births per 1000 per year
    death_rate: float           # deaths per 1000 per year
    fertility_rate: float       # children per woman of childbearing age
    life_expectancy: float      # average lifespan in years
    population_pyramid: Dict[str, Dict[str, int]]  # age/gender distribution
    migration_rate: float       # net migration per 1000 per year
    growth_rate: float          # annual population growth rate
    dependency_ratio: float     # ratio of dependents to working age
    

class DemographicModels:
    """Mathematical models for population demographics"""
    
    @staticmethod
    def calculate_age_based_mortality(age_group: AgeGroup, base_mortality: float = 0.008,
                                    healthcare_quality: float = 0.5, safety_level: float = 0.5) -> float:
        """
        Calculate mortality rate by age group with environmental factors
        
        Args:
            age_group: Age group for calculation
            base_mortality: Base mortality rate per year
            healthcare_quality: Quality of healthcare (0.0-1.0)
            safety_level: Regional safety level (0.0-1.0)
            
        Returns:
            Annual mortality rate for the age group
        """
        try:
            # Base mortality curves by age (per year)
            age_mortality_multipliers = {
                AgeGroup.INFANT: 15.0,        # High infant mortality
                AgeGroup.CHILD: 0.5,          # Low childhood mortality 
                AgeGroup.ADOLESCENT: 0.8,     # Moderate teen mortality
                AgeGroup.YOUNG_ADULT: 1.0,    # Baseline
                AgeGroup.ADULT: 1.2,          # Slightly higher
                AgeGroup.MIDDLE_AGED: 2.5,    # Rising mortality
                AgeGroup.ELDER: 8.0,          # High elderly mortality
                AgeGroup.ANCIENT: 25.0        # Very high ancient mortality
            }
            
            multiplier = age_mortality_multipliers.get(age_group, 1.0)
            age_adjusted_mortality = base_mortality * multiplier
            
            # Healthcare reduces mortality (up to 60% reduction)
            healthcare_factor = 1.0 - (healthcare_quality * 0.6)
            
            # Safety affects mortality (violence, accidents)
            safety_factor = 1.0 + ((1.0 - safety_level) * 0.8)
            
            final_mortality = age_adjusted_mortality * healthcare_factor * safety_factor
            
            return min(0.95, max(0.001, final_mortality))  # Cap between 0.1% and 95%
            
        except Exception as e:
            logger.error(f"Error calculating age-based mortality: {e}")
            return base_mortality
    
    @staticmethod
    def calculate_fertility_rate(age_group: AgeGroup, base_fertility: float = 0.12,
                               economic_prosperity: float = 0.5, cultural_factors: float = 0.5) -> float:
        """
        Calculate fertility rate by age group
        
        Args:
            age_group: Age group for calculation  
            base_fertility: Base fertility rate (children per woman per year)
            economic_prosperity: Economic conditions (0.0-1.0)
            cultural_factors: Cultural fertility preferences (0.0-1.0)
            
        Returns:
            Annual fertility rate for the age group
        """
        try:
            # Fertility curves by age (peak reproductive years)
            fertility_multipliers = {
                AgeGroup.INFANT: 0.0,
                AgeGroup.CHILD: 0.0,
                AgeGroup.ADOLESCENT: 0.3,     # Early fertility
                AgeGroup.YOUNG_ADULT: 1.0,    # Peak fertility
                AgeGroup.ADULT: 0.8,          # Good fertility
                AgeGroup.MIDDLE_AGED: 0.2,    # Declining fertility
                AgeGroup.ELDER: 0.0,          # Post-reproductive
                AgeGroup.ANCIENT: 0.0
            }
            
            multiplier = fertility_multipliers.get(age_group, 0.0)
            age_adjusted_fertility = base_fertility * multiplier
            
            # Economic factors affect fertility (complex relationship)
            # Moderate prosperity increases fertility, extreme poverty/wealth decreases it
            if economic_prosperity < 0.3:
                economic_factor = 0.7 + (economic_prosperity * 0.6)  # Poverty reduces fertility
            elif economic_prosperity > 0.8:
                economic_factor = 1.2 - (economic_prosperity * 0.4)  # Wealth also reduces fertility  
            else:
                economic_factor = 0.9 + (economic_prosperity * 0.4)  # Moderate prosperity increases
            
            # Cultural factors
            cultural_factor = 0.6 + (cultural_factors * 0.8)
            
            final_fertility = age_adjusted_fertility * economic_factor * cultural_factor
            
            return max(0.0, min(0.5, final_fertility))  # Cap at 0.5 children per woman per year
            
        except Exception as e:
            logger.error(f"Error calculating fertility rate: {e}")
            return 0.0
    
    @staticmethod
    def calculate_life_expectancy(healthcare_quality: float = 0.5, safety_level: float = 0.5,
                                economic_level: float = 0.5, environmental_quality: float = 0.5) -> float:
        """
        Calculate life expectancy based on environmental factors
        
        Args:
            healthcare_quality: Quality of medical care (0.0-1.0)
            safety_level: Regional safety from violence/war (0.0-1.0)  
            economic_level: Economic prosperity (0.0-1.0)
            environmental_quality: Environmental conditions (0.0-1.0)
            
        Returns:
            Average life expectancy in years
        """
        try:
            # Base life expectancy for medieval/fantasy setting
            base_expectancy = 45.0
            
            # Healthcare impact (can add up to 25 years)
            healthcare_bonus = healthcare_quality * 25.0
            
            # Safety impact (violence can reduce by up to 15 years)
            safety_bonus = safety_level * 15.0 - 7.5  # Centered around 0
            
            # Economic impact (wealth improves nutrition, housing - up to 10 years)
            economic_bonus = economic_level * 10.0
            
            # Environmental impact (clean air, water - up to 8 years)
            environmental_bonus = environmental_quality * 8.0
            
            total_expectancy = (base_expectancy + healthcare_bonus + 
                              safety_bonus + economic_bonus + environmental_bonus)
            
            return max(25.0, min(95.0, total_expectancy))  # Cap between 25-95 years
            
        except Exception as e:
            logger.error(f"Error calculating life expectancy: {e}")
            return 45.0
    
    @staticmethod
    def generate_population_pyramid(total_population: int, life_expectancy: float = 60.0,
                                  growth_rate: float = 0.02) -> Dict[str, Dict[str, int]]:
        """
        Generate age and gender distribution (population pyramid)
        
        Args:
            total_population: Total population size
            life_expectancy: Average life expectancy
            growth_rate: Annual population growth rate
            
        Returns:
            Dictionary with age groups and gender distribution
        """
        try:
            pyramid = {}
            
            # Calculate age group distributions based on life expectancy and growth
            age_ranges = [
                ("0-4", 5), ("5-9", 5), ("10-14", 5), ("15-19", 5),
                ("20-24", 5), ("25-29", 5), ("30-34", 5), ("35-39", 5),
                ("40-44", 5), ("45-49", 5), ("50-54", 5), ("55-59", 5),
                ("60-64", 5), ("65-69", 5), ("70-74", 5), ("75-79", 5),
                ("80-84", 5), ("85+", 15)
            ]
            
            for age_range, span in age_ranges:
                midpoint = float(age_range.split('-')[0]) + span/2 if '-' in age_range else 85
                
                # Survival probability to this age
                survival_prob = math.exp(-midpoint / (life_expectancy * 1.2))
                
                # Growth rate affects younger populations more
                growth_factor = 1.0 + (growth_rate * (80 - midpoint) / 80)
                growth_factor = max(0.1, growth_factor)
                
                # Base population for this age group
                base_pop = total_population * 0.055 * survival_prob * growth_factor
                
                # Gender distribution (slightly more males at birth, evens out with age)
                if midpoint < 30:
                    male_ratio = 0.52
                else:
                    male_ratio = 0.50 - (midpoint - 30) * 0.001  # Females live longer
                
                male_pop = int(base_pop * male_ratio)
                female_pop = int(base_pop * (1 - male_ratio))
                
                pyramid[age_range] = {
                    "male": male_pop,
                    "female": female_pop,
                    "total": male_pop + female_pop
                }
            
            # Normalize to match total population
            actual_total = sum(group["total"] for group in pyramid.values())
            if actual_total > 0:
                scaling_factor = total_population / actual_total
                for age_range in pyramid:
                    pyramid[age_range]["male"] = int(pyramid[age_range]["male"] * scaling_factor)
                    pyramid[age_range]["female"] = int(pyramid[age_range]["female"] * scaling_factor)
                    pyramid[age_range]["total"] = pyramid[age_range]["male"] + pyramid[age_range]["female"]
            
            return pyramid
            
        except Exception as e:
            logger.error(f"Error generating population pyramid: {e}")
            return {}
    
    @staticmethod
    def calculate_migration_probability(origin_factors: Dict[str, float], 
                                      destination_factors: Dict[str, float],
                                      distance_km: float, migration_type: MigrationType) -> float:
        """
        Calculate probability of migration between two locations
        
        Args:
            origin_factors: Push factors from origin (economic_opportunity, safety, resources, etc.)
            destination_factors: Pull factors to destination
            distance_km: Distance between locations
            migration_type: Type of migration
            
        Returns:
            Migration probability (0.0-1.0)
        """
        try:
            # Push factors (reasons to leave)
            economic_push = 1.0 - origin_factors.get("economic_opportunity", 0.5)
            safety_push = 1.0 - origin_factors.get("safety_level", 0.5)
            resource_push = 1.0 - origin_factors.get("resource_availability", 0.5)
            
            # Pull factors (reasons to move to destination)
            economic_pull = destination_factors.get("economic_opportunity", 0.5)
            safety_pull = destination_factors.get("safety_level", 0.5)
            resource_pull = destination_factors.get("resource_availability", 0.5)
            family_pull = destination_factors.get("family_connections", 0.0)
            
            # Calculate net migration pressure
            push_score = (economic_push + safety_push + resource_push) / 3.0
            pull_score = (economic_pull + safety_pull + resource_pull + family_pull) / 4.0
            
            # Distance decay - closer destinations more likely
            distance_factor = math.exp(-distance_km / 200.0)  # 200km half-life
            
            # Migration type modifiers
            type_modifiers = {
                MigrationType.ECONOMIC: 1.0,
                MigrationType.SAFETY: 1.5,      # Safety migration more urgent
                MigrationType.FAMILY: 0.8,      # Family migration less distance-sensitive
                MigrationType.SEASONAL: 0.5,    # Seasonal migration more common
                MigrationType.FORCED: 2.0,      # Forced migration ignores normal factors
                MigrationType.RETURN: 0.3       # Return migration less likely
            }
            
            type_modifier = type_modifiers.get(migration_type, 1.0)
            
            # Calculate final probability
            base_probability = (push_score * 0.6 + pull_score * 0.4) * distance_factor * type_modifier
            
            return max(0.0, min(1.0, base_probability))
            
        except Exception as e:
            logger.error(f"Error calculating migration probability: {e}")
            return 0.0
    
    @staticmethod
    def calculate_settlement_growth_dynamics(current_population: int, settlement_type: SettlementType,
                                           economic_activity: float = 0.5, resource_capacity: int = 10000,
                                           infrastructure_level: float = 0.5) -> Dict[str, Any]:
        """
        Calculate settlement growth dynamics and carrying capacity
        
        Args:
            current_population: Current population size
            settlement_type: Type of settlement
            economic_activity: Level of economic activity (0.0-1.0)
            resource_capacity: Maximum sustainable population
            infrastructure_level: Quality of infrastructure (0.0-1.0)
            
        Returns:
            Dictionary with growth calculations and projections
        """
        try:
            # Base growth rates by settlement type
            base_growth_rates = {
                SettlementType.VILLAGE: 0.015,      # 1.5% annual growth
                SettlementType.TOWN: 0.025,         # 2.5% annual growth
                SettlementType.CITY: 0.035,         # 3.5% annual growth
                SettlementType.LARGE_CITY: 0.030,   # 3.0% annual growth
                SettlementType.METROPOLIS: 0.020    # 2.0% annual growth
            }
            
            base_growth = base_growth_rates.get(settlement_type, 0.02)
            
            # Economic activity affects growth
            economic_modifier = 0.5 + (economic_activity * 1.0)
            
            # Carrying capacity pressure
            capacity_ratio = current_population / max(1, resource_capacity)
            if capacity_ratio < 0.5:
                capacity_modifier = 1.2  # Room to grow
            elif capacity_ratio < 0.8:
                capacity_modifier = 1.0  # Normal growth
            elif capacity_ratio < 1.0:
                capacity_modifier = 0.6  # Slowing growth
            else:
                capacity_modifier = 0.2  # Overcrowded, declining
            
            # Infrastructure affects efficiency
            infrastructure_modifier = 0.7 + (infrastructure_level * 0.6)
            
            # Calculate final growth rate
            final_growth_rate = (base_growth * economic_modifier * 
                               capacity_modifier * infrastructure_modifier)
            
            # Project future population
            projected_1_year = int(current_population * (1 + final_growth_rate))
            projected_5_years = int(current_population * ((1 + final_growth_rate) ** 5))
            projected_10_years = int(current_population * ((1 + final_growth_rate) ** 10))
            
            # Calculate urbanization pressure (likelihood of settlement type upgrade)
            urbanization_pressure = 0.0
            if settlement_type == SettlementType.VILLAGE and current_population > 400:
                urbanization_pressure = min(1.0, (current_population - 400) / 100)
            elif settlement_type == SettlementType.TOWN and current_population > 1800:
                urbanization_pressure = min(1.0, (current_population - 1800) / 200)
            elif settlement_type == SettlementType.CITY and current_population > 9000:
                urbanization_pressure = min(1.0, (current_population - 9000) / 1000)
            
            return {
                "current_population": current_population,
                "settlement_type": settlement_type.value,
                "annual_growth_rate": final_growth_rate,
                "projected_population_1_year": projected_1_year,
                "projected_population_5_years": projected_5_years,
                "projected_population_10_years": projected_10_years,
                "carrying_capacity": resource_capacity,
                "capacity_utilization": capacity_ratio,
                "urbanization_pressure": urbanization_pressure,
                "economic_health": economic_activity,
                "infrastructure_quality": infrastructure_level,
                "growth_factors": {
                    "economic_modifier": economic_modifier,
                    "capacity_modifier": capacity_modifier,
                    "infrastructure_modifier": infrastructure_modifier
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating settlement growth dynamics: {e}")
            return {
                "error": str(e),
                "current_population": current_population,
                "annual_growth_rate": 0.0
            }
    
    @staticmethod
    def create_demographic_profile(population_size: int, region_factors: Dict[str, float]) -> DemographicProfile:
        """
        Create a comprehensive demographic profile for a population
        
        Args:
            population_size: Total population size
            region_factors: Regional factors affecting demographics
            
        Returns:
            Complete demographic profile
        """
        try:
            # Extract regional factors
            healthcare = region_factors.get("healthcare_quality", 0.5)
            safety = region_factors.get("safety_level", 0.5)
            economic = region_factors.get("economic_prosperity", 0.5)
            environmental = region_factors.get("environmental_quality", 0.5)
            
            # Calculate life expectancy
            life_expectancy = DemographicModels.calculate_life_expectancy(
                healthcare, safety, economic, environmental
            )
            
            # Calculate base rates
            base_death_rate = 1000 / life_expectancy  # deaths per 1000 per year
            base_birth_rate = base_death_rate + 15  # slightly higher for growth
            
            # Generate age distribution
            age_distribution = {}
            total_distributed = 0
            
            for age_group in AgeGroup:
                mortality = DemographicModels.calculate_age_based_mortality(
                    age_group, base_death_rate/1000, healthcare, safety
                )
                fertility = DemographicModels.calculate_fertility_rate(
                    age_group, 0.12, economic, 0.5
                )
                
                # Estimate population in this age group
                if age_group in [AgeGroup.INFANT, AgeGroup.CHILD]:
                    proportion = 0.18
                elif age_group in [AgeGroup.ADOLESCENT, AgeGroup.YOUNG_ADULT]:
                    proportion = 0.16
                elif age_group in [AgeGroup.ADULT, AgeGroup.MIDDLE_AGED]:
                    proportion = 0.20
                else:
                    proportion = 0.10
                
                group_population = int(population_size * proportion)
                age_distribution[age_group] = group_population
                total_distributed += group_population
            
            # Adjust for exact total
            if total_distributed != population_size:
                adjustment = population_size - total_distributed
                age_distribution[AgeGroup.ADULT] += adjustment
            
            # Generate population pyramid
            population_pyramid = DemographicModels.generate_population_pyramid(
                population_size, life_expectancy, 0.02
            )
            
            # Calculate aggregate fertility rate
            total_fertility = sum(
                DemographicModels.calculate_fertility_rate(ag, 0.12, economic, 0.5) * count
                for ag, count in age_distribution.items()
            ) / population_size
            
            # Calculate dependency ratio
            working_age = (age_distribution.get(AgeGroup.YOUNG_ADULT, 0) + 
                          age_distribution.get(AgeGroup.ADULT, 0) + 
                          age_distribution.get(AgeGroup.MIDDLE_AGED, 0))
            dependents = population_size - working_age
            dependency_ratio = dependents / max(1, working_age)
            
            return DemographicProfile(
                total_population=population_size,
                age_distribution=age_distribution,
                birth_rate=base_birth_rate,
                death_rate=base_death_rate,
                fertility_rate=total_fertility,
                life_expectancy=life_expectancy,
                population_pyramid=population_pyramid,
                migration_rate=0.0,  # Calculate separately based on regional factors
                growth_rate=(base_birth_rate - base_death_rate) / 1000,
                dependency_ratio=dependency_ratio
            )
            
        except Exception as e:
            logger.error(f"Error creating demographic profile: {e}")
            # Return minimal profile on error
            return DemographicProfile(
                total_population=population_size,
                age_distribution={ag: population_size // len(AgeGroup) for ag in AgeGroup},
                birth_rate=25.0,
                death_rate=15.0,
                fertility_rate=0.1,
                life_expectancy=50.0,
                population_pyramid={},
                migration_rate=0.0,
                growth_rate=0.01,
                dependency_ratio=0.5
            )


class PopulationProjectionModels:
    """Models for projecting population changes over time"""
    
    @staticmethod
    def project_population_change(
        current_profile: DemographicProfile,
        time_steps: int = 12,  # months
        external_factors: Optional[Dict[str, Any]] = None
    ) -> List[DemographicProfile]:
        """
        Project population changes over time using demographic models
        
        Args:
            current_profile: Current demographic state
            time_steps: Number of time periods to project (months)
            external_factors: Wars, disasters, economic changes, etc.
            
        Returns:
            List of projected demographic profiles
        """
        try:
            projections = [current_profile]
            profile = current_profile
            
            for step in range(time_steps):
                # Calculate monthly changes
                monthly_birth_rate = profile.birth_rate / 12 / 1000
                monthly_death_rate = profile.death_rate / 12 / 1000
                monthly_migration_rate = profile.migration_rate / 12 / 1000
                
                # Apply external factors if any
                if external_factors:
                    for event_type, event_data in external_factors.items():
                        if event_data.get("start_month", 0) <= step <= event_data.get("end_month", time_steps):
                            if event_type == "war":
                                monthly_death_rate *= (1 + event_data.get("intensity", 0.1))
                                monthly_migration_rate -= event_data.get("refugee_outflow", 0.05) / 12
                            elif event_type == "economic_boom":
                                monthly_birth_rate *= (1 + event_data.get("prosperity_boost", 0.1))
                                monthly_migration_rate += event_data.get("immigration", 0.02) / 12
                            elif event_type == "famine":
                                monthly_death_rate *= (1 + event_data.get("severity", 0.2))
                                monthly_birth_rate *= (1 - event_data.get("fertility_impact", 0.3))
                
                # Calculate population changes
                births = int(profile.total_population * monthly_birth_rate)
                deaths = int(profile.total_population * monthly_death_rate)
                net_migration = int(profile.total_population * monthly_migration_rate)
                
                new_population = max(0, profile.total_population + births - deaths + net_migration)
                
                # Update age distribution (simplified aging)
                new_age_distribution = profile.age_distribution.copy()
                
                # Add births to infant category
                new_age_distribution[AgeGroup.INFANT] += births
                
                # Apply deaths proportionally across age groups
                for age_group in AgeGroup:
                    group_deaths = int(deaths * (new_age_distribution[age_group] / profile.total_population))
                    new_age_distribution[age_group] = max(0, new_age_distribution[age_group] - group_deaths)
                
                # Create new profile
                new_profile = DemographicProfile(
                    total_population=new_population,
                    age_distribution=new_age_distribution,
                    birth_rate=profile.birth_rate,
                    death_rate=profile.death_rate,
                    fertility_rate=profile.fertility_rate,
                    life_expectancy=profile.life_expectancy,
                    population_pyramid=DemographicModels.generate_population_pyramid(new_population),
                    migration_rate=profile.migration_rate,
                    growth_rate=(monthly_birth_rate - monthly_death_rate + monthly_migration_rate) * 12,
                    dependency_ratio=profile.dependency_ratio
                )
                
                projections.append(new_profile)
                profile = new_profile
            
            return projections
            
        except Exception as e:
            logger.error(f"Error projecting population change: {e}")
            return [current_profile] 