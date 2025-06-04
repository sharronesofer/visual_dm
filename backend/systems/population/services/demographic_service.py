"""
Population System - Demographic Service

This service provides comprehensive demographic analysis and simulation using
the mathematical models implemented for Task 74.
"""

import logging
import asyncio
import math
from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID
from datetime import datetime

from backend.systems.population.utils.demographic_models import (
    DemographicModels,
    PopulationProjectionModels,
    DemographicProfile,
    AgeGroup,
    MigrationType,
    SettlementType
)
from backend.systems.population.utils.consolidated_utils import (
    calculate_controlled_growth_rate,
    calculate_racial_distribution,
    calculate_seasonal_growth_modifier,
    calculate_seasonal_death_rate_modifier,
    PopulationState,
    RaceType
)

logger = logging.getLogger(__name__)


# Business Logic Protocols (dependency injection)
class PopulationRepository(Protocol):
    """Protocol for population data access"""
    
    def get_population_by_id(self, population_id: UUID) -> Optional[Dict[str, Any]]:
        """Get population by ID"""
        ...
    
    def update_population(self, population_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing population"""
        ...


class DemographicAnalysisBusinessService:
    """Service for demographic analysis and population simulation - pure business logic"""
    
    def __init__(self, population_repository: PopulationRepository):
        self.population_repository = population_repository

    def analyze_population_demographics(
        self, 
        population_id: UUID,
        region_factors: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive demographic analysis for a population
        
        Args:
            population_id: ID of the population to analyze
            region_factors: Regional factors affecting demographics
            
        Returns:
            Complete demographic analysis including all mathematical models
        """
        # Get population data
        population_data = self.population_repository.get_population_by_id(population_id)
        if not population_data:
            raise ValueError(f"Population {population_id} not found")
        
        # Extract current population size
        properties = population_data.get('properties', {})
        current_population = properties.get("population_count", 1000)
        
        # Use provided region factors or defaults
        if region_factors is None:
            region_factors = {
                "healthcare_quality": properties.get("healthcare_quality", 0.5),
                "safety_level": properties.get("safety_level", 0.5),
                "economic_prosperity": properties.get("economic_prosperity", 0.5),
                "environmental_quality": properties.get("environmental_quality", 0.5)
            }
        
        # Create comprehensive demographic profile
        demographic_profile = DemographicModels.create_demographic_profile(
            current_population, region_factors
        )
        
        # Calculate age-specific mortality rates
        age_mortality_rates = {}
        for age_group in AgeGroup:
            mortality_rate = DemographicModels.calculate_age_based_mortality(
                age_group,
                demographic_profile.death_rate / 1000,
                region_factors.get("healthcare_quality", 0.5),
                region_factors.get("safety_level", 0.5)
            )
            age_mortality_rates[age_group.value] = mortality_rate
        
        # Calculate age-specific fertility rates
        age_fertility_rates = {}
        for age_group in AgeGroup:
            fertility_rate = DemographicModels.calculate_fertility_rate(
                age_group,
                0.12,
                region_factors.get("economic_prosperity", 0.5),
                0.5
            )
            age_fertility_rates[age_group.value] = fertility_rate
        
        # Determine settlement type based on population
        if current_population < 500:
            settlement_type = SettlementType.VILLAGE
        elif current_population < 2000:
            settlement_type = SettlementType.TOWN
        elif current_population < 10000:
            settlement_type = SettlementType.CITY
        elif current_population < 50000:
            settlement_type = SettlementType.LARGE_CITY
        else:
            settlement_type = SettlementType.METROPOLIS
        
        # Calculate settlement growth dynamics
        growth_dynamics = DemographicModels.calculate_settlement_growth_dynamics(
            current_population,
            settlement_type,
            region_factors.get("economic_prosperity", 0.5),
            properties.get("carrying_capacity", current_population * 2),
            region_factors.get("infrastructure_quality", 0.5)
        )
        
        # Update population with demographic data
        self._update_demographic_properties(population_data, demographic_profile, region_factors)
        
        return {
            "population_id": str(population_id),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "demographic_profile": {
                "total_population": demographic_profile.total_population,
                "age_distribution": {ag.value: count for ag, count in demographic_profile.age_distribution.items()},
                "birth_rate": demographic_profile.birth_rate,
                "death_rate": demographic_profile.death_rate,
                "fertility_rate": demographic_profile.fertility_rate,
                "life_expectancy": demographic_profile.life_expectancy,
                "population_pyramid": demographic_profile.population_pyramid,
                "migration_rate": demographic_profile.migration_rate,
                "growth_rate": demographic_profile.growth_rate,
                "dependency_ratio": demographic_profile.dependency_ratio
            },
            "age_specific_rates": {
                "mortality_by_age": age_mortality_rates,
                "fertility_by_age": age_fertility_rates
            },
            "settlement_analysis": growth_dynamics,
            "regional_factors": region_factors,
            "recommendations": self._generate_demographic_recommendations(demographic_profile, region_factors)
        }

    def calculate_migration_flows(
        self,
        origin_population_id: UUID,
        destination_population_ids: List[UUID],
        migration_type: str = "economic"
    ) -> Dict[str, Any]:
        """
        Calculate migration probabilities and flows between populations
        
        Args:
            origin_population_id: ID of origin population
            destination_population_ids: List of potential destination population IDs
            migration_type: Type of migration (economic, safety, family, etc.)
            
        Returns:
            Migration flow analysis and probabilities
        """
        # Get origin population
        origin_data = self.population_repository.get_population_by_id(origin_population_id)
        if not origin_data:
            raise ValueError(f"Origin population {origin_population_id} not found")
        
        origin_properties = origin_data.get('properties', {})
        origin_factors = {
            "economic_opportunity": origin_properties.get("economic_prosperity", 0.5),
            "safety_level": origin_properties.get("safety_level", 0.5),
            "resource_availability": origin_properties.get("resource_availability", 0.5)
        }
        
        migration_flows = []
        migration_type_enum = MigrationType(migration_type.lower())
        
        # Calculate migration probabilities for each destination
        for dest_id in destination_population_ids:
            dest_data = self.population_repository.get_population_by_id(dest_id)
            if not dest_data:
                continue
            
            dest_properties = dest_data.get('properties', {})
            dest_factors = {
                "economic_opportunity": dest_properties.get("economic_prosperity", 0.5),
                "safety_level": dest_properties.get("safety_level", 0.5),
                "resource_availability": dest_properties.get("resource_availability", 0.5)
            }
            
            # Calculate migration probability using demographic models
            migration_probability = DemographicModels.calculate_migration_probability(
                origin_factors,
                dest_factors,
                migration_type_enum,
                100.0  # Default distance
            )
            
            migration_flows.append({
                "destination_id": str(dest_id),
                "destination_name": dest_data.get('name', 'Unknown'),
                "migration_probability": migration_probability,
                "migration_type": migration_type,
                "factors": {
                    "origin": origin_factors,
                    "destination": dest_factors
                }
            })
        
        # Sort by migration probability
        migration_flows.sort(key=lambda x: x["migration_probability"], reverse=True)
        
        return {
            "origin_population_id": str(origin_population_id),
            "migration_type": migration_type,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "migration_flows": migration_flows,
            "total_destinations_analyzed": len(migration_flows)
        }

    def project_population_future(
        self,
        population_id: UUID,
        months_ahead: int = 12,
        scenario_factors: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Project population changes into the future using demographic models
        
        Args:
            population_id: ID of the population to project
            months_ahead: Number of months to project ahead
            scenario_factors: Optional scenario modifiers
            
        Returns:
            Future population projections
        """
        # Get population data
        population_data = self.population_repository.get_population_by_id(population_id)
        if not population_data:
            raise ValueError(f"Population {population_id} not found")
        
        properties = population_data.get('properties', {})
        current_population = properties.get("population_count", 1000)
        
        # Use scenario factors or defaults
        if scenario_factors is None:
            scenario_factors = {
                "economic_growth": 0.0,
                "healthcare_improvement": 0.0,
                "environmental_change": 0.0,
                "conflict_risk": 0.0
            }
        
        # Create demographic profile for projections
        region_factors = {
            "healthcare_quality": properties.get("healthcare_quality", 0.5),
            "safety_level": properties.get("safety_level", 0.5),
            "economic_prosperity": properties.get("economic_prosperity", 0.5),
            "environmental_quality": properties.get("environmental_quality", 0.5)
        }
        
        demographic_profile = DemographicModels.create_demographic_profile(
            current_population, region_factors
        )
        
        # Generate monthly projections
        projections = PopulationProjectionModels.project_population_monthly(
            demographic_profile,
            months_ahead,
            scenario_factors
        )
        
        return {
            "population_id": str(population_id),
            "projection_timestamp": datetime.utcnow().isoformat(),
            "months_projected": months_ahead,
            "scenario_factors": scenario_factors,
            "current_population": current_population,
            "projections": projections,
            "summary": {
                "final_population": projections[-1]["population"] if projections else current_population,
                "total_change": (projections[-1]["population"] - current_population) if projections else 0,
                "average_monthly_growth": sum(p["growth_rate"] for p in projections) / len(projections) if projections else 0
            }
        }

    def _update_demographic_properties(
        self,
        population_data: Dict[str, Any],
        profile: DemographicProfile,
        region_factors: Dict[str, float]
    ) -> None:
        """Update population properties with demographic analysis results"""
        properties = population_data.get('properties', {})
        
        # Update demographic properties
        properties.update({
            "demographic_analysis": {
                "last_analysis": datetime.utcnow().isoformat(),
                "birth_rate": profile.birth_rate,
                "death_rate": profile.death_rate,
                "fertility_rate": profile.fertility_rate,
                "life_expectancy": profile.life_expectancy,
                "growth_rate": profile.growth_rate,
                "dependency_ratio": profile.dependency_ratio,
                "age_distribution": {ag.value: count for ag, count in profile.age_distribution.items()}
            },
            "regional_factors": region_factors
        })
        
        # Update the population via repository
        update_data = {
            'id': population_data['id'],
            'properties': properties
        }
        self.population_repository.update_population(update_data)

    def _generate_demographic_recommendations(
        self,
        profile: DemographicProfile,
        region_factors: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on demographic analysis"""
        recommendations = []
        
        # Population growth recommendations
        if profile.growth_rate < 0:
            recommendations.append("Population is declining - consider policies to encourage growth")
        elif profile.growth_rate > 0.05:
            recommendations.append("Rapid population growth - ensure infrastructure can support expansion")
        
        # Age distribution recommendations
        if profile.dependency_ratio > 0.7:
            recommendations.append("High dependency ratio - focus on supporting working-age population")
        elif profile.dependency_ratio < 0.3:
            recommendations.append("Low dependency ratio - opportunity for economic growth")
        
        # Regional factor recommendations
        if region_factors.get("healthcare_quality", 0.5) < 0.4:
            recommendations.append("Healthcare quality is low - investment needed to reduce mortality")
        
        if region_factors.get("economic_prosperity", 0.5) < 0.4:
            recommendations.append("Economic conditions are poor - development programs recommended")
        
        if region_factors.get("safety_level", 0.5) < 0.4:
            recommendations.append("Safety concerns present - security improvements needed")
        
        # Life expectancy recommendations
        if profile.life_expectancy < 60:
            recommendations.append("Low life expectancy - urgent healthcare and safety improvements needed")
        elif profile.life_expectancy > 80:
            recommendations.append("High life expectancy - prepare for aging population challenges")
        
        return recommendations


def create_demographic_analysis_business_service(
    population_repository: PopulationRepository
) -> DemographicAnalysisBusinessService:
    """Factory function to create demographic analysis business service"""
    return DemographicAnalysisBusinessService(population_repository)


# Legacy compatibility layer
class DemographicAnalysisService(DemographicAnalysisBusinessService):
    """Legacy service class for backward compatibility"""
    
    def __init__(self, db_session=None):
        # Import here to avoid circular dependencies
        from backend.infrastructure.population.repositories.population_repository import create_population_repository
        
        if db_session:
            repository = create_population_repository(db_session)
        else:
            # Use a default session - this should be injected properly in production
            from backend.infrastructure.shared.database import get_db_session
            repository = create_population_repository(get_db_session())
        
        super().__init__(repository)

    # Legacy async method compatibility
    async def analyze_population_demographics(self, population_id: UUID, region_factors: Optional[Dict[str, float]] = None):
        """Legacy async analyze method"""
        return self.analyze_population_demographics(population_id, region_factors)

    async def calculate_migration_flows(self, origin_population_id: UUID, destination_population_ids: List[UUID], migration_type: str = "economic"):
        """Legacy async migration method"""
        return self.calculate_migration_flows(origin_population_id, destination_population_ids, migration_type)

    async def project_population_future(self, population_id: UUID, months_ahead: int = 12, scenario_factors: Optional[Dict[str, Any]] = None):
        """Legacy async projection method"""
        return self.project_population_future(population_id, months_ahead, scenario_factors)


def create_demographic_analysis_service(db_session) -> DemographicAnalysisService:
    """Factory function to create legacy demographic analysis service"""
    return DemographicAnalysisService(db_session) 