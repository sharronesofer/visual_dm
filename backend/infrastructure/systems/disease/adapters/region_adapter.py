"""
Disease-Region System Adapter

Adapter for integrating disease system with region system.
Handles environmental factors, regional disease spread, and geographic constraints.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)


class DiseaseRegionAdapter:
    """
    Adapter for disease-region system integration.
    
    Provides methods for:
    - Getting environmental factors from regions
    - Calculating regional disease spread
    - Managing climate and geographic impacts
    - Coordinating cross-regional transmission
    """
    
    def __init__(self, region_service=None):
        """
        Initialize the adapter.
        
        Args:
            region_service: Region system service for accessing region data
        """
        self.region_service = region_service
    
    def get_region_environmental_factors(self, region_id: UUID) -> Dict[str, Any]:
        """
        Get environmental factors from a region that affect disease transmission.
        
        Args:
            region_id: Region identifier
            
        Returns:
            Environmental factors including climate, geography, and infrastructure
        """
        try:
            if not self.region_service:
                logger.warning("Region service not available, using mock data")
                return self._get_mock_environmental_factors(region_id)
            
            # This would integrate with the actual region system
            region = self.region_service.get_region_by_id(region_id)
            
            if not region:
                return self._get_default_environmental_factors()
            
            return {
                "temperature": region.get("climate", {}).get("temperature", 20.0),
                "humidity": region.get("climate", {}).get("humidity", 0.5),
                "seasonal_modifier": region.get("climate", {}).get("seasonal_modifier", 1.0),
                "terrain_type": region.get("geography", {}).get("terrain", "plains"),
                "water_access": region.get("geography", {}).get("water_access", "moderate"),
                "trade_routes": region.get("infrastructure", {}).get("trade_routes", []),
                "population_density": region.get("demographics", {}).get("density", "normal"),
                "urbanization_level": region.get("infrastructure", {}).get("urbanization", "rural"),
                "sanitation_level": region.get("infrastructure", {}).get("sanitation", "basic"),
                "healthcare_infrastructure": region.get("infrastructure", {}).get("healthcare", "basic"),
                "quarantine_capability": region.get("infrastructure", {}).get("quarantine_capability", "limited")
            }
            
        except Exception as e:
            logger.error(f"Error getting environmental factors for region {region_id}: {str(e)}")
            return self._get_default_environmental_factors()
    
    def calculate_climate_modifiers(
        self, 
        environmental_factors: Dict[str, Any], 
        disease_profile: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate climate-based modifiers for disease transmission.
        
        Args:
            environmental_factors: Regional environmental data
            disease_profile: Disease characteristics
            
        Returns:
            Dictionary of climate modifiers
        """
        modifiers = {
            "temperature_modifier": 1.0,
            "humidity_modifier": 1.0,
            "seasonal_modifier": 1.0,
            "terrain_modifier": 1.0,
            "overall_modifier": 1.0
        }
        
        try:
            temperature = environmental_factors.get("temperature", 20.0)
            humidity = environmental_factors.get("humidity", 0.5)
            terrain = environmental_factors.get("terrain_type", "plains")
            
            # Temperature effects (disease-specific)
            disease_type = disease_profile.get("disease_type", "fever")
            temp_preferences = {
                "plague": {"optimal": 25.0, "range": 10.0},
                "fever": {"optimal": 30.0, "range": 15.0},
                "pox": {"optimal": 20.0, "range": 12.0},
                "flux": {"optimal": 35.0, "range": 8.0},
                "lung_rot": {"optimal": 15.0, "range": 10.0},
                "sweating_sickness": {"optimal": 28.0, "range": 12.0}
            }
            
            if disease_type in temp_preferences:
                optimal_temp = temp_preferences[disease_type]["optimal"]
                temp_range = temp_preferences[disease_type]["range"]
                temp_diff = abs(temperature - optimal_temp)
                
                if temp_diff <= temp_range:
                    modifiers["temperature_modifier"] = 1.0 + (temp_range - temp_diff) / temp_range * 0.5
                else:
                    modifiers["temperature_modifier"] = max(0.3, 1.0 - (temp_diff - temp_range) / 20.0)
            
            # Humidity effects
            humidity_preferences = {
                "plague": 0.6,  # Prefers moderate to high humidity
                "fever": 0.7,  # High humidity
                "pox": 0.4,    # Lower humidity
                "flux": 0.8,   # Very high humidity
                "lung_rot": 0.9,  # Extremely high humidity
                "sweating_sickness": 0.5  # Moderate humidity
            }
            
            if disease_type in humidity_preferences:
                optimal_humidity = humidity_preferences[disease_type]
                humidity_diff = abs(humidity - optimal_humidity)
                modifiers["humidity_modifier"] = max(0.5, 1.0 - humidity_diff)
            
            # Terrain effects
            terrain_modifiers = {
                "swamp": {"flux": 2.0, "lung_rot": 1.8, "fever": 1.5},
                "mountains": {"lung_rot": 1.3, "pox": 0.8},
                "desert": {"flux": 0.3, "fever": 0.7, "pox": 1.2},
                "forest": {"plague": 1.2, "fever": 1.1},
                "plains": {},  # Neutral
                "coastal": {"flux": 1.4, "fever": 1.2},
                "urban": {"plague": 1.8, "pox": 1.6, "fever": 1.3}
            }
            
            if terrain in terrain_modifiers and disease_type in terrain_modifiers[terrain]:
                modifiers["terrain_modifier"] = terrain_modifiers[terrain][disease_type]
            
            # Seasonal modifier
            modifiers["seasonal_modifier"] = environmental_factors.get("seasonal_modifier", 1.0)
            
            # Calculate overall modifier
            modifiers["overall_modifier"] = (
                modifiers["temperature_modifier"] *
                modifiers["humidity_modifier"] *
                modifiers["seasonal_modifier"] *
                modifiers["terrain_modifier"]
            )
            
            return modifiers
            
        except Exception as e:
            logger.error(f"Error calculating climate modifiers: {str(e)}")
            return modifiers
    
    def get_neighboring_regions(self, region_id: UUID) -> List[Dict[str, Any]]:
        """
        Get neighboring regions for disease spread calculations.
        
        Args:
            region_id: Source region identifier
            
        Returns:
            List of neighboring region data
        """
        try:
            if not self.region_service:
                logger.warning("Region service not available, returning mock neighbors")
                return self._get_mock_neighbors(region_id)
            
            # This would integrate with the actual region system
            neighbors = self.region_service.get_neighboring_regions(region_id)
            
            return [
                {
                    "id": neighbor.get("id"),
                    "name": neighbor.get("name"),
                    "distance": neighbor.get("distance", 100.0),
                    "connection_type": neighbor.get("connection_type", "land"),
                    "trade_volume": neighbor.get("trade_volume", 0.5),
                    "travel_time": neighbor.get("travel_time", 7),
                    "border_control": neighbor.get("border_control", "open")
                }
                for neighbor in neighbors
            ]
            
        except Exception as e:
            logger.error(f"Error getting neighboring regions for {region_id}: {str(e)}")
            return []
    
    def calculate_transmission_probability(
        self, 
        source_region_id: UUID, 
        target_region_id: UUID,
        outbreak_data: Dict[str, Any]
    ) -> float:
        """
        Calculate probability of disease transmission between regions.
        
        Args:
            source_region_id: Source region with outbreak
            target_region_id: Target region for potential spread
            outbreak_data: Current outbreak information
            
        Returns:
            Transmission probability (0.0 to 1.0)
        """
        try:
            # Get region connection data
            neighbors = self.get_neighboring_regions(source_region_id)
            target_neighbor = next(
                (n for n in neighbors if n["id"] == target_region_id), 
                None
            )
            
            if not target_neighbor:
                return 0.0  # No direct connection
            
            # Base transmission probability
            base_probability = 0.1
            
            # Distance factor (closer = higher probability)
            distance = target_neighbor.get("distance", 100.0)
            distance_factor = max(0.1, 1.0 - (distance / 500.0))  # 500km max effective range
            
            # Trade volume factor
            trade_volume = target_neighbor.get("trade_volume", 0.5)
            trade_factor = 1.0 + trade_volume
            
            # Travel time factor (faster = higher probability)
            travel_time = target_neighbor.get("travel_time", 7)
            travel_factor = max(0.3, 1.0 - (travel_time / 30.0))  # 30 days max
            
            # Border control factor
            border_control = target_neighbor.get("border_control", "open")
            border_factors = {
                "open": 1.0,
                "monitored": 0.7,
                "restricted": 0.4,
                "closed": 0.1
            }
            border_factor = border_factors.get(border_control, 1.0)
            
            # Outbreak severity factor
            infected_count = outbreak_data.get("infected_count", 0)
            severity_factor = min(2.0, 1.0 + (infected_count / 1000.0))
            
            # Calculate final probability
            probability = (
                base_probability *
                distance_factor *
                trade_factor *
                travel_factor *
                border_factor *
                severity_factor
            )
            
            return min(1.0, probability)
            
        except Exception as e:
            logger.error(f"Error calculating transmission probability: {str(e)}")
            return 0.0
    
    def apply_regional_quarantine(
        self, 
        region_id: UUID, 
        quarantine_level: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Apply quarantine measures to a region.
        
        Args:
            region_id: Region to quarantine
            quarantine_level: Level of quarantine (light, moderate, strict, total)
            
        Returns:
            Quarantine effectiveness and impacts
        """
        try:
            environmental_factors = self.get_region_environmental_factors(region_id)
            quarantine_capability = environmental_factors.get("quarantine_capability", "limited")
            
            # Base effectiveness by quarantine level
            base_effectiveness = {
                "light": 0.2,
                "moderate": 0.5,
                "strict": 0.8,
                "total": 0.95
            }
            
            # Capability modifiers
            capability_modifiers = {
                "none": 0.1,
                "limited": 0.7,
                "moderate": 1.0,
                "advanced": 1.3,
                "excellent": 1.5
            }
            
            effectiveness = (
                base_effectiveness.get(quarantine_level, 0.5) *
                capability_modifiers.get(quarantine_capability, 1.0)
            )
            
            # Economic and social costs
            cost_multipliers = {
                "light": 0.1,
                "moderate": 0.3,
                "strict": 0.7,
                "total": 1.0
            }
            
            economic_cost = cost_multipliers.get(quarantine_level, 0.3)
            social_cost = cost_multipliers.get(quarantine_level, 0.3) * 0.8
            
            return {
                "region_id": region_id,
                "quarantine_level": quarantine_level,
                "effectiveness": min(1.0, effectiveness),
                "economic_impact": economic_cost,
                "social_impact": social_cost,
                "duration_recommended": self._calculate_quarantine_duration(quarantine_level),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error applying regional quarantine: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _calculate_quarantine_duration(self, quarantine_level: str) -> int:
        """Calculate recommended quarantine duration in days."""
        durations = {
            "light": 7,
            "moderate": 14,
            "strict": 21,
            "total": 30
        }
        return durations.get(quarantine_level, 14)
    
    def _get_mock_environmental_factors(self, region_id: UUID) -> Dict[str, Any]:
        """Generate mock environmental factors for testing."""
        return {
            "temperature": 22.0,
            "humidity": 0.6,
            "seasonal_modifier": 1.0,
            "terrain_type": "plains",
            "water_access": "moderate",
            "trade_routes": ["north_road", "river_route"],
            "population_density": "normal",
            "urbanization_level": "rural",
            "sanitation_level": "basic",
            "healthcare_infrastructure": "basic",
            "quarantine_capability": "limited"
        }
    
    def _get_default_environmental_factors(self) -> Dict[str, Any]:
        """Get default environmental factors when region data is unavailable."""
        return {
            "temperature": 20.0,
            "humidity": 0.5,
            "seasonal_modifier": 1.0,
            "terrain_type": "plains",
            "water_access": "moderate",
            "trade_routes": [],
            "population_density": "normal",
            "urbanization_level": "rural",
            "sanitation_level": "basic",
            "healthcare_infrastructure": "basic",
            "quarantine_capability": "limited"
        }
    
    def _get_mock_neighbors(self, region_id: UUID) -> List[Dict[str, Any]]:
        """Generate mock neighboring regions for testing."""
        return [
            {
                "id": UUID("12345678-1234-5678-9012-123456789012"),
                "name": "Northern Region",
                "distance": 150.0,
                "connection_type": "land",
                "trade_volume": 0.7,
                "travel_time": 5,
                "border_control": "open"
            },
            {
                "id": UUID("87654321-4321-8765-2109-876543210987"),
                "name": "Eastern Region",
                "distance": 200.0,
                "connection_type": "river",
                "trade_volume": 0.5,
                "travel_time": 3,
                "border_control": "monitored"
            }
        ] 