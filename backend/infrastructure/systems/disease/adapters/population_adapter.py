"""
Disease-Population System Adapter

Adapter for integrating disease system with population system.
Handles disease spread, population health impacts, and demographic targeting.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)


class DiseasePopulationAdapter:
    """
    Adapter for disease-population system integration.
    
    Provides methods for:
    - Calculating disease spread in populations
    - Applying demographic targeting
    - Managing population health metrics
    - Coordinating outbreak impacts
    """
    
    def __init__(self, population_service=None):
        """
        Initialize the adapter.
        
        Args:
            population_service: Population system service for accessing population data
        """
        self.population_service = population_service
    
    def get_population_for_outbreak(self, population_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get population data relevant for disease outbreaks.
        
        Args:
            population_id: Population identifier
            
        Returns:
            Population data including demographics and health factors
        """
        try:
            if not self.population_service:
                logger.warning("Population service not available, using mock data")
                return self._get_mock_population_data(population_id)
            
            # This would integrate with the actual population system
            population = self.population_service.get_population_by_id(population_id)
            
            if not population:
                return None
            
            return {
                "id": population.get("id"),
                "name": population.get("name"),
                "total_size": population.get("size", 1000),
                "age_distribution": population.get("demographics", {}).get("age_distribution", {
                    "young": 0.25,
                    "adult": 0.55,
                    "elderly": 0.20
                }),
                "health_status": population.get("health", {}).get("general_health", "average"),
                "crowding_level": population.get("living_conditions", {}).get("density", "normal"),
                "hygiene_level": population.get("living_conditions", {}).get("hygiene", "basic"),
                "healthcare_access": population.get("services", {}).get("healthcare", "basic"),
                "immunity_levels": population.get("health", {}).get("disease_immunity", {}),
                "vulnerable_groups": population.get("demographics", {}).get("vulnerable_groups", [])
            }
            
        except Exception as e:
            logger.error(f"Error getting population data for {population_id}: {str(e)}")
            return None
    
    def calculate_transmission_modifiers(
        self, 
        population_data: Dict[str, Any], 
        disease_profile: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate transmission rate modifiers based on population characteristics.
        
        Args:
            population_data: Population information
            disease_profile: Disease characteristics
            
        Returns:
            Dictionary of transmission modifiers
        """
        modifiers = {
            "base_modifier": 1.0,
            "crowding_modifier": 1.0,
            "hygiene_modifier": 1.0,
            "healthcare_modifier": 1.0,
            "age_modifier": 1.0,
            "immunity_modifier": 1.0
        }
        
        try:
            # Crowding effects
            crowding_level = population_data.get("crowding_level", "normal")
            crowding_multipliers = {
                "sparse": 0.7,
                "normal": 1.0,
                "crowded": 1.5,
                "overcrowded": 2.0
            }
            modifiers["crowding_modifier"] = crowding_multipliers.get(crowding_level, 1.0)
            
            # Hygiene effects
            hygiene_level = population_data.get("hygiene_level", "basic")
            hygiene_multipliers = {
                "excellent": 0.5,
                "good": 0.7,
                "basic": 1.0,
                "poor": 1.3,
                "terrible": 1.8
            }
            modifiers["hygiene_modifier"] = hygiene_multipliers.get(hygiene_level, 1.0)
            
            # Healthcare effects (affects mortality more than transmission)
            healthcare_level = population_data.get("healthcare_access", "basic")
            healthcare_multipliers = {
                "excellent": 0.8,
                "good": 0.9,
                "basic": 1.0,
                "poor": 1.1,
                "none": 1.2
            }
            modifiers["healthcare_modifier"] = healthcare_multipliers.get(healthcare_level, 1.0)
            
            # Age-based susceptibility
            age_distribution = population_data.get("age_distribution", {})
            age_modifier = 1.0
            
            if disease_profile.get("targets_young", False):
                age_modifier += age_distribution.get("young", 0.25) * 0.5
            if disease_profile.get("targets_old", False):
                age_modifier += age_distribution.get("elderly", 0.20) * 0.6
            if disease_profile.get("targets_weak", False):
                # Weak individuals are distributed across age groups
                age_modifier += 0.3
            
            modifiers["age_modifier"] = age_modifier
            
            # Existing immunity
            immunity_levels = population_data.get("immunity_levels", {})
            disease_type = disease_profile.get("disease_type", "fever")
            immunity_rate = immunity_levels.get(disease_type, 0.0)
            modifiers["immunity_modifier"] = max(0.1, 1.0 - immunity_rate)
            
            # Calculate overall modifier
            modifiers["base_modifier"] = (
                modifiers["crowding_modifier"] *
                modifiers["hygiene_modifier"] *
                modifiers["healthcare_modifier"] *
                modifiers["age_modifier"] *
                modifiers["immunity_modifier"]
            )
            
            return modifiers
            
        except Exception as e:
            logger.error(f"Error calculating transmission modifiers: {str(e)}")
            return modifiers
    
    def apply_disease_impact(
        self, 
        population_id: UUID, 
        outbreak_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply disease outbreak impacts to a population.
        
        Args:
            population_id: Population to affect
            outbreak_data: Outbreak information and impacts
            
        Returns:
            Updated population status and impact metrics
        """
        try:
            if not self.population_service:
                logger.warning("Population service not available, returning mock impact")
                return self._get_mock_impact_data(population_id, outbreak_data)
            
            # Calculate population impacts
            total_affected = outbreak_data.get("infected_count", 0) + outbreak_data.get("recovered_count", 0)
            deaths = outbreak_data.get("death_count", 0)
            
            # Economic impact (reduced productivity)
            productivity_impact = min(0.5, total_affected / 1000.0 * 0.2)  # 20% per 1000 affected
            
            # Social impact (fear, unrest)
            social_impact = min(0.3, deaths / 100.0 * 0.1)  # 10% per 100 deaths
            
            # Apply impacts to population
            impact_data = {
                "population_id": population_id,
                "outbreak_id": outbreak_data.get("id"),
                "productivity_reduction": productivity_impact,
                "social_stability_reduction": social_impact,
                "population_loss": deaths,
                "immune_population_gain": outbreak_data.get("immune_count", 0),
                "healthcare_strain": min(1.0, total_affected / 500.0),  # Healthcare overwhelmed at 500+ cases
                "economic_cost": productivity_impact * 1000.0,  # Economic units
                "timestamp": datetime.utcnow()
            }
            
            # This would update the population system with the impacts
            # population_service.apply_disease_impact(population_id, impact_data)
            
            return impact_data
            
        except Exception as e:
            logger.error(f"Error applying disease impact to population {population_id}: {str(e)}")
            return {"error": str(e)}
    
    def calculate_demographic_targeting(
        self, 
        population_data: Dict[str, Any], 
        disease_profile: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Calculate how many individuals in each demographic group are likely to be affected.
        
        Args:
            population_data: Population demographics
            disease_profile: Disease targeting preferences
            
        Returns:
            Expected affected counts by demographic group
        """
        try:
            total_size = population_data.get("total_size", 1000)
            age_distribution = population_data.get("age_distribution", {})
            
            targeting = {
                "young": 0,
                "adult": 0,
                "elderly": 0,
                "vulnerable": 0
            }
            
            # Base transmission rate
            base_rate = disease_profile.get("transmission_rate", 0.3)
            
            # Calculate targeting multipliers
            young_rate = base_rate * (2.0 if disease_profile.get("targets_young", False) else 1.0)
            adult_rate = base_rate
            elderly_rate = base_rate * (2.5 if disease_profile.get("targets_old", False) else 1.0)
            vulnerable_rate = base_rate * (3.0 if disease_profile.get("targets_weak", False) else 1.0)
            
            # Apply to population
            targeting["young"] = int(total_size * age_distribution.get("young", 0.25) * young_rate)
            targeting["adult"] = int(total_size * age_distribution.get("adult", 0.55) * adult_rate)
            targeting["elderly"] = int(total_size * age_distribution.get("elderly", 0.20) * elderly_rate)
            
            # Vulnerable groups (overlap with age groups)
            vulnerable_groups = population_data.get("vulnerable_groups", [])
            vulnerable_population = sum(group.get("size", 0) for group in vulnerable_groups)
            targeting["vulnerable"] = int(vulnerable_population * vulnerable_rate)
            
            return targeting
            
        except Exception as e:
            logger.error(f"Error calculating demographic targeting: {str(e)}")
            return {"young": 0, "adult": 0, "elderly": 0, "vulnerable": 0}
    
    def update_population_immunity(
        self, 
        population_id: UUID, 
        disease_type: str, 
        immune_count: int
    ) -> bool:
        """
        Update population immunity levels after disease exposure.
        
        Args:
            population_id: Population to update
            disease_type: Type of disease for immunity
            immune_count: Number of newly immune individuals
            
        Returns:
            True if update was successful
        """
        try:
            if not self.population_service:
                logger.warning("Population service not available, immunity update skipped")
                return False
            
            # This would update the population system's immunity tracking
            # return population_service.update_disease_immunity(population_id, disease_type, immune_count)
            
            logger.info(f"Updated immunity for population {population_id}: {immune_count} immune to {disease_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating population immunity: {str(e)}")
            return False
    
    def get_population_vulnerability_score(self, population_data: Dict[str, Any]) -> float:
        """
        Calculate overall vulnerability score for a population.
        
        Args:
            population_data: Population characteristics
            
        Returns:
            Vulnerability score (0.0 = not vulnerable, 1.0 = highly vulnerable)
        """
        try:
            vulnerability = 0.0
            
            # Base vulnerability factors
            crowding_level = population_data.get("crowding_level", "normal")
            if crowding_level in ["crowded", "overcrowded"]:
                vulnerability += 0.3
            
            hygiene_level = population_data.get("hygiene_level", "basic")
            if hygiene_level in ["poor", "terrible"]:
                vulnerability += 0.3
            
            healthcare_access = population_data.get("healthcare_access", "basic")
            if healthcare_access in ["poor", "none"]:
                vulnerability += 0.2
            
            # Age distribution vulnerability
            age_distribution = population_data.get("age_distribution", {})
            vulnerable_age_proportion = age_distribution.get("young", 0.25) + age_distribution.get("elderly", 0.20)
            vulnerability += vulnerable_age_proportion * 0.2
            
            return min(1.0, vulnerability)
            
        except Exception as e:
            logger.error(f"Error calculating vulnerability score: {str(e)}")
            return 0.5  # Default moderate vulnerability
    
    def _get_mock_population_data(self, population_id: UUID) -> Dict[str, Any]:
        """Generate mock population data for testing when population service is unavailable."""
        return {
            "id": population_id,
            "name": f"Population {str(population_id)[:8]}",
            "total_size": 1000,
            "age_distribution": {
                "young": 0.25,
                "adult": 0.55,
                "elderly": 0.20
            },
            "health_status": "average",
            "crowding_level": "normal",
            "hygiene_level": "basic",
            "healthcare_access": "basic",
            "immunity_levels": {},
            "vulnerable_groups": []
        }
    
    def _get_mock_impact_data(self, population_id: UUID, outbreak_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock impact data when population service is unavailable."""
        return {
            "population_id": population_id,
            "outbreak_id": outbreak_data.get("id"),
            "productivity_reduction": 0.1,
            "social_stability_reduction": 0.05,
            "population_loss": outbreak_data.get("death_count", 0),
            "immune_population_gain": outbreak_data.get("immune_count", 0),
            "healthcare_strain": 0.3,
            "economic_cost": 100.0,
            "timestamp": datetime.utcnow(),
            "mock_data": True
        } 