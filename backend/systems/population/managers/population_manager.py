"""
Population Manager

Centralized manager for population operations that integrates all population
services and provides a unified interface for other systems.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

from backend.systems.population.services.services import PopulationService
from backend.systems.population.services.demographic_service import DemographicAnalysisService
from backend.systems.population.utils.consolidated_utils import (
    calculate_controlled_growth_rate,
    calculate_racial_distribution,
    calculate_war_impact,
    calculate_catastrophe_impact,
    calculate_resource_shortage_impact,
    calculate_migration_impact,
    calculate_seasonal_growth_modifier,
    calculate_seasonal_death_rate_modifier,
    RaceType,
    PopulationState,
    WarImpactSeverity,
    CatastropheType
)
from backend.infrastructure.population.utils.config_loader import (
    get_population_config_loader,
    load_population_config
)

logger = logging.getLogger(__name__)

class PopulationManager:
    """
    Central manager for all population operations with enhanced controls
    for growth rates and racial distributions.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the PopulationManager.
        
        Args:
            config_path: Optional path to population configuration JSON
        """
        self.population_service = PopulationService()
        self.demographic_service = DemographicAnalysisService()
        
        # Load configuration using infrastructure loader
        if config_path:
            from backend.infrastructure.population.utils.config_loader import PopulationConfigLoader
            self.config_loader = PopulationConfigLoader(config_path)
        else:
            self.config_loader = get_population_config_loader()
        
        self.config = self.config_loader.load_config()
        
        logger.info("PopulationManager initialized")
    
    # ============================================================================
    # POPULATION CONTROL METHODS
    # ============================================================================
    
    def get_controlled_growth_rate(
        self,
        poi_id: str,
        current_population: int,
        carrying_capacity: int,
        resource_availability: float = 1.0,
        stability_factor: float = 1.0
    ) -> float:
        """
        Get population growth rate with comprehensive controls to prevent
        over/under-population issues.
        
        Args:
            poi_id: Point of Interest ID
            current_population: Current settlement population
            carrying_capacity: Maximum sustainable population
            resource_availability: Resource abundance (0.0-2.0)
            stability_factor: Political/social stability (0.0-1.0)
            
        Returns:
            Controlled growth rate that prevents population issues
        """
        base_growth_rate = self.config["growth_control"]["base_growth_rate"]
        minimum_viable = self.config["growth_control"].get("minimum_viable_population", 50)
        
        controlled_rate = calculate_controlled_growth_rate(
            current_population=current_population,
            base_growth_rate=base_growth_rate,
            carrying_capacity=carrying_capacity,
            minimum_viable_population=minimum_viable,
            resource_availability=resource_availability,
            stability_factor=stability_factor,
            config=self.config["growth_control"]
        )
        
        logger.info(f"POI {poi_id}: Controlled growth rate = {controlled_rate:.3f}")
        return controlled_rate
    
    def set_global_growth_modifier(self, modifier: float) -> None:
        """
        Set a global growth rate modifier for all settlements.
        
        Args:
            modifier: Global growth modifier (0.5 = half speed, 2.0 = double speed)
        """
        self.config["growth_control"]["base_growth_rate"] *= modifier
        logger.info(f"Applied global growth modifier: {modifier}")
    
    def get_racial_distribution(
        self,
        poi_id: str,
        total_population: int,
        region_type: str = "plains",
        cultural_factors: Optional[Dict[str, float]] = None,
        historical_distribution: Optional[Dict[str, float]] = None
    ) -> Dict[str, int]:
        """
        Calculate racial/species distribution for a POI with detailed controls.
        
        Args:
            poi_id: Point of Interest ID
            total_population: Total population to distribute
            region_type: Type of region (affects racial preferences)
            cultural_factors: Cultural modifiers per race
            historical_distribution: Previous racial makeup
            
        Returns:
            Dict mapping race names to population counts
        """
        distribution = calculate_racial_distribution(
            total_population=total_population,
            region_type=region_type,
            cultural_factors=cultural_factors,
            historical_distribution=historical_distribution,
            config=self.config["racial_distribution"]
        )
        
        logger.info(f"POI {poi_id}: Calculated racial distribution for {total_population} population")
        return distribution
    
    def set_racial_weights(self, race_weights: Dict[str, float]) -> None:
        """
        Update global racial distribution weights.
        
        Args:
            race_weights: New default weights for racial distribution
        """
        self.config["racial_distribution"]["default_weights"].update(race_weights)
        logger.info(f"Updated racial weights: {race_weights}")
    
    def set_regional_modifiers(self, region_type: str, modifiers: Dict[str, float]) -> None:
        """
        Set racial modifiers for a specific region type.
        
        Args:
            region_type: Type of region
            modifiers: Race-specific modifiers for this region
        """
        if "regional_modifiers" not in self.config["racial_distribution"]:
            self.config["racial_distribution"]["regional_modifiers"] = {}
        
        self.config["racial_distribution"]["regional_modifiers"][region_type] = modifiers
        logger.info(f"Set regional modifiers for {region_type}: {modifiers}")
    
    # ============================================================================
    # POPULATION IMPACT METHODS
    # ============================================================================
    
    def apply_war_impact(
        self,
        poi_id: str,
        war_intensity: float,
        duration_days: int,
        defensive_strength: float = 0.5
    ) -> Dict[str, Any]:
        """
        Apply war impact to a population using consolidated calculations.
        
        Args:
            poi_id: Point of Interest ID
            war_intensity: War intensity (0.0-1.0)
            duration_days: Duration in days
            defensive_strength: Defensive capabilities (0.0-1.0)
            
        Returns:
            War impact results
        """
        # Get current population
        population_data = self.population_service.get_population(poi_id)
        if not population_data:
            logger.error(f"No population data found for POI {poi_id}")
            return {"error": "POI not found"}
        
        current_population = population_data.get("population", 0)
        
        # Calculate war impact
        impact_result = calculate_war_impact(
            population=current_population,
            war_intensity=war_intensity,
            duration_days=duration_days,
            defensive_strength=defensive_strength
        )
        
        # Update population if impact calculated successfully
        if "error" not in impact_result:
            new_population = impact_result["remaining_population"]
            self.population_service.update_population(poi_id, {
                "population": new_population,
                "last_war_impact": impact_result
            })
        
        logger.info(f"Applied war impact to POI {poi_id}")
        return impact_result
    
    def apply_catastrophe_impact(
        self,
        poi_id: str,
        catastrophe_type: str,
        severity: float,
        preparedness: float = 0.3
    ) -> Dict[str, Any]:
        """
        Apply catastrophe impact to a population.
        
        Args:
            poi_id: Point of Interest ID
            catastrophe_type: Type of catastrophe
            severity: Severity level (0.0-1.0)
            preparedness: Community preparedness (0.0-1.0)
            
        Returns:
            Catastrophe impact results
        """
        # Get current population
        population_data = self.population_service.get_population(poi_id)
        if not population_data:
            logger.error(f"No population data found for POI {poi_id}")
            return {"error": "POI not found"}
        
        current_population = population_data.get("population", 0)
        
        # Calculate catastrophe impact
        impact_result = calculate_catastrophe_impact(
            population=current_population,
            catastrophe_type=catastrophe_type,
            severity=severity,
            preparedness=preparedness
        )
        
        # Update population if impact calculated successfully
        if "error" not in impact_result:
            new_population = impact_result["remaining_population"]
            self.population_service.update_population(poi_id, {
                "population": new_population,
                "last_catastrophe_impact": impact_result
            })
        
        logger.info(f"Applied catastrophe impact to POI {poi_id}")
        return impact_result
    
    def apply_resource_shortage(
        self,
        poi_id: str,
        resource_type: str,
        shortage_percentage: float,
        duration_days: int
    ) -> Dict[str, Any]:
        """
        Apply resource shortage impact to a population.
        
        Args:
            poi_id: Point of Interest ID
            resource_type: Type of resource in shortage
            shortage_percentage: Severity of shortage (0.0-1.0)
            duration_days: Duration of shortage
            
        Returns:
            Resource shortage impact results
        """
        # Get current population
        population_data = self.population_service.get_population(poi_id)
        if not population_data:
            logger.error(f"No population data found for POI {poi_id}")
            return {"error": "POI not found"}
        
        current_population = population_data.get("population", 0)
        
        # Get resource criticality from config
        criticality = self.config.get("resource_consumption", {}).get("criticality_levels", {}).get(resource_type, 0.5)
        
        # Calculate resource shortage impact
        impact_result = calculate_resource_shortage_impact(
            population=current_population,
            resource_type=resource_type,
            shortage_percentage=shortage_percentage,
            duration_days=duration_days,
            resource_criticality=criticality
        )
        
        # Update population if impact calculated successfully
        if "error" not in impact_result:
            new_population = impact_result["remaining_population"]
            self.population_service.update_population(poi_id, {
                "population": new_population,
                "last_resource_shortage": impact_result
            })
        
        logger.info(f"Applied resource shortage impact to POI {poi_id}")
        return impact_result
    
    # ============================================================================
    # SEASONAL AND ENVIRONMENTAL EFFECTS
    # ============================================================================
    
    def apply_seasonal_effects(
        self,
        poi_id: str,
        current_season: str,
        climate_type: str = "temperate",
        resource_availability: float = 1.0,
        medical_care: float = 0.5
    ) -> Dict[str, float]:
        """
        Apply seasonal effects to population growth and death rates.
        
        Args:
            poi_id: Point of Interest ID
            current_season: Current season name
            climate_type: Climate type of region
            resource_availability: Resource abundance factor
            medical_care: Medical care quality
            
        Returns:
            Dict with modified growth and death rates
        """
        # Get current population data
        population_data = self.population_service.get_population(poi_id)
        if not population_data:
            logger.error(f"No population data found for POI {poi_id}")
            return {"error": "POI not found"}
        
        base_growth_rate = population_data.get("growth_rate", 0.02)
        base_death_rate = population_data.get("death_rate", 0.015)
        
        # Calculate seasonal modifiers
        modified_growth_rate = calculate_seasonal_growth_modifier(
            current_season=current_season,
            climate_type=climate_type,
            base_growth_rate=base_growth_rate,
            resource_availability=resource_availability
        )
        
        modified_death_rate = calculate_seasonal_death_rate_modifier(
            current_season=current_season,
            climate_type=climate_type,
            base_death_rate=base_death_rate,
            medical_care=medical_care,
            food_security=resource_availability
        )
        
        # Update population data
        self.population_service.update_population(poi_id, {
            "current_growth_rate": modified_growth_rate,
            "current_death_rate": modified_death_rate,
            "last_seasonal_update": current_season
        })
        
        result = {
            "growth_rate": modified_growth_rate,
            "death_rate": modified_death_rate,
            "season": current_season,
            "climate": climate_type
        }
        
        logger.info(f"Applied seasonal effects to POI {poi_id}: {current_season} in {climate_type}")
        return result
    
    # ============================================================================
    # MIGRATION METHODS
    # ============================================================================
    
    def calculate_migration(
        self,
        origin_poi_id: str,
        destination_poi_id: str,
        push_factors: Dict[str, float],
        pull_factors: Dict[str, float],
        distance_km: float = 100.0
    ) -> Dict[str, Any]:
        """
        Calculate migration between two POIs.
        
        Args:
            origin_poi_id: Origin POI ID
            destination_poi_id: Destination POI ID
            push_factors: Factors driving migration away
            pull_factors: Factors attracting migration
            distance_km: Distance between locations
            
        Returns:
            Migration calculation results
        """
        # Get population data for both POIs
        origin_data = self.population_service.get_population(origin_poi_id)
        dest_data = self.population_service.get_population(destination_poi_id)
        
        if not origin_data or not dest_data:
            logger.error(f"Population data missing for migration calculation")
            return {"error": "POI data not found"}
        
        origin_population = origin_data.get("population", 0)
        destination_capacity = dest_data.get("carrying_capacity", 1000) - dest_data.get("population", 0)
        
        # Calculate migration
        migration_result = calculate_migration_impact(
            origin_population=origin_population,
            destination_capacity=max(0, destination_capacity),
            push_factors=push_factors,
            pull_factors=pull_factors,
            distance_km=distance_km
        )
        
        # Apply migration if successful
        if "error" not in migration_result:
            migrants = migration_result["actual_migrants"]
            
            # Update origin population
            new_origin_population = migration_result["remaining_at_origin"]
            self.population_service.update_population(origin_poi_id, {
                "population": new_origin_population
            })
            
            # Update destination population
            new_dest_population = dest_data.get("population", 0) + migrants
            self.population_service.update_population(destination_poi_id, {
                "population": new_dest_population
            })
        
        logger.info(f"Calculated migration from {origin_poi_id} to {destination_poi_id}")
        return migration_result
    
    # ============================================================================
    # INTEGRATION METHODS FOR OTHER SYSTEMS
    # ============================================================================
    
    def get_population_summary(self, poi_id: str) -> Dict[str, Any]:
        """
        Get comprehensive population summary for other systems.
        
        Args:
            poi_id: Point of Interest ID
            
        Returns:
            Comprehensive population summary
        """
        population_data = self.population_service.get_population(poi_id)
        if not population_data:
            return {"error": "POI not found"}
        
        # Get racial distribution
        total_population = population_data.get("population", 0)
        region_type = population_data.get("region_type", "plains")
        
        racial_dist = self.get_racial_distribution(
            poi_id=poi_id,
            total_population=total_population,
            region_type=region_type
        )
        
        # Calculate social metrics
        social_stability = self._calculate_social_stability(population_data, racial_dist)
        
        summary = {
            "poi_id": poi_id,
            "total_population": total_population,
            "population_state": population_data.get("state", "stable"),
            "growth_rate": population_data.get("current_growth_rate", 0.02),
            "racial_distribution": racial_dist,
            "social_stability": social_stability,
            "carrying_capacity": population_data.get("carrying_capacity", 1000),
            "resource_needs": self._calculate_resource_needs(total_population),
            "last_updated": population_data.get("last_updated")
        }
        
        return summary
    
    def _calculate_social_stability(self, population_data: Dict, racial_dist: Dict[str, int]) -> float:
        """Calculate social stability based on population factors."""
        total_pop = sum(racial_dist.values())
        if total_pop == 0:
            return 0.0
        
        # Diversity index (higher diversity can mean more tension or more tolerance)
        diversity = 1.0 - sum((count / total_pop) ** 2 for count in racial_dist.values())
        
        # Population pressure
        carrying_capacity = population_data.get("carrying_capacity", 1000)
        population_pressure = min(1.0, total_pop / carrying_capacity)
        
        # Recent events impact
        recent_impacts = 0
        if population_data.get("last_war_impact"):
            recent_impacts += 0.3
        if population_data.get("last_catastrophe_impact"):
            recent_impacts += 0.2
        if population_data.get("last_resource_shortage"):
            recent_impacts += 0.1
        
        # Calculate stability (0.0 to 1.0)
        base_stability = 0.8  # Baseline stability
        diversity_factor = diversity * 0.1  # Small diversity impact
        pressure_factor = population_pressure * 0.3  # Population pressure impact
        
        stability = base_stability + diversity_factor - pressure_factor - recent_impacts
        return max(0.0, min(1.0, stability))
    
    def _calculate_resource_needs(self, population: int) -> Dict[str, float]:
        """Calculate daily resource needs for a population."""
        consumption_rates = self.config.get("resource_consumption", {}).get("base_rates_per_capita_per_day", {})
        
        needs = {}
        for resource, rate in consumption_rates.items():
            needs[resource] = population * rate
        
        return needs
    
    # ============================================================================
    # CONFIGURATION METHODS
    # ============================================================================
    
    def update_config(self, config_updates: Dict[str, Any]) -> None:
        """Update configuration with nested dictionary updates."""
        def update_nested_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = update_nested_dict(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        update_nested_dict(self.config, config_updates)
        logger.info(f"Updated configuration: {config_updates}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
    
    def save_config(self, config_path: Optional[str] = None) -> None:
        """
        Save current configuration to JSON file.
        
        Args:
            config_path: Optional path to save to (defaults to loaded path)
        """
        self.config_loader.save_config(self.config, config_path)

# Create a global instance for easy access
_population_manager = None

def get_population_manager() -> PopulationManager:
    """Get a global instance of PopulationManager."""
    global _population_manager
    if _population_manager is None:
        _population_manager = PopulationManager()
    return _population_manager 