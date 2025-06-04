"""
Biome Configuration Manager - Infrastructure

Technical infrastructure for loading and managing biome configurations from external JSON files.
This handles file I/O and configuration loading, separated from business logic.
"""

from typing import Dict, List, Optional
from pathlib import Path

from backend.systems.region.models import BiomeType, ResourceType, ClimateType
from backend.infrastructure.config_loaders import JsonConfigLoader


class BiomeConfigManager:
    """Technical infrastructure for managing biome configurations loaded from JSON files."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Point to the JSON file in data directory
            config_path = Path("data/systems/world_generation/biomes.json")
        
        # Use the infrastructure JSON loader with default config
        self._config_loader = JsonConfigLoader(
            config_path=str(config_path),
            default_config=self._get_default_biome_configs()
        )
    
    def _get_default_biome_configs(self) -> Dict[str, dict]:
        """Provide default biome configurations as fallback."""
        return {
            "temperate_forest": {
                "name": "Temperate Forest",
                "temperature_range": [0.4, 0.7],
                "humidity_range": [0.5, 0.8],
                "elevation_range": [0.1, 0.6],
                "climate_types": ["temperate", "oceanic"],
                "features": ["dense_canopy", "wildlife", "streams"],
                "resources": {
                    "timber": 0.9,
                    "herbs": 0.6,
                    "game": 0.7,
                    "fresh_water": 0.8
                },
                "adjacent_biomes": ["deciduous_forest", "grassland", "hills"],
                "transition_difficulty": 0.3,
                "rarity": 1.0
            },
            "mountains": {
                "name": "Mountains",
                "temperature_range": [0.1, 0.5],
                "humidity_range": [0.3, 0.7],
                "elevation_range": [0.7, 1.0],
                "climate_types": ["continental", "polar"],
                "features": ["peaks", "caves", "mineral_veins"],
                "resources": {
                    "stone": 0.9,
                    "iron": 0.7,
                    "copper": 0.6,
                    "gems": 0.3,
                    "coal": 0.5
                },
                "adjacent_biomes": ["hills", "tundra", "coniferous_forest"],
                "transition_difficulty": 0.8,
                "rarity": 0.7
            },
            "grassland": {
                "name": "Grassland",
                "temperature_range": [0.5, 0.8],
                "humidity_range": [0.3, 0.6],
                "elevation_range": [0.0, 0.3],
                "climate_types": ["temperate", "continental"],
                "features": ["open_plains", "wildflowers", "gentle_hills"],
                "resources": {
                    "fertile_soil": 0.9,
                    "game": 0.8,
                    "herbs": 0.5,
                    "fresh_water": 0.4
                },
                "adjacent_biomes": ["temperate_forest", "prairie", "hills"],
                "transition_difficulty": 0.2,
                "rarity": 1.0
            },
            "desert": {
                "name": "Desert",
                "temperature_range": [0.7, 1.0],
                "humidity_range": [0.0, 0.2],
                "elevation_range": [0.0, 0.4],
                "climate_types": ["arid", "semi_arid"],
                "features": ["dunes", "oases", "rock_formations"],
                "resources": {
                    "stone": 0.7,
                    "gems": 0.4,
                    "rare_earth": 0.3,
                    "gold": 0.2
                },
                "adjacent_biomes": ["savanna", "hills"],
                "transition_difficulty": 0.7,
                "rarity": 0.6
            },
            "coastal": {
                "name": "Coastal",
                "temperature_range": [0.4, 0.8],
                "humidity_range": [0.6, 1.0],
                "elevation_range": [0.0, 0.2],
                "climate_types": ["oceanic", "mediterranean"],
                "features": ["beaches", "cliffs", "tidal_pools"],
                "resources": {
                    "fish": 0.9,
                    "fresh_water": 0.6,
                    "stone": 0.5
                },
                "adjacent_biomes": ["temperate_forest", "grassland"],
                "transition_difficulty": 0.4,
                "rarity": 0.8
            },
            "swamp": {
                "name": "Swamp",
                "temperature_range": [0.5, 0.9],
                "humidity_range": [0.8, 1.0],
                "elevation_range": [0.0, 0.3],
                "climate_types": ["subtropical", "temperate"],
                "features": ["wetlands", "murky_water", "dangerous_wildlife"],
                "resources": {
                    "herbs": 0.7,
                    "fresh_water": 1.0,
                    "game": 0.4
                },
                "adjacent_biomes": ["temperate_forest", "coastal"],
                "transition_difficulty": 0.6,
                "rarity": 0.4
            },
            "tundra": {
                "name": "Tundra",
                "temperature_range": [0.0, 0.3],
                "humidity_range": [0.2, 0.6],
                "elevation_range": [0.0, 0.6],
                "climate_types": ["polar", "continental"],
                "features": ["permafrost", "sparse_vegetation", "harsh_winds"],
                "resources": {
                    "game": 0.3,
                    "fresh_water": 0.4
                },
                "adjacent_biomes": ["mountains", "coniferous_forest"],
                "transition_difficulty": 0.8,
                "rarity": 0.5
            }
        }
    
    def get_biome_config(self, biome_type: BiomeType) -> Optional[dict]:
        """Get configuration for a specific biome type."""
        biome_key = biome_type.value.lower()
        biome_configs = self._config_loader.load_config()
        return biome_configs.get(biome_key)
    
    def get_biome_resources(self, biome_type: BiomeType) -> Dict[ResourceType, float]:
        """Get resource probabilities for a biome."""
        config = self.get_biome_config(biome_type)
        if not config:
            return {}
        
        resources = {}
        for resource_name, probability in config.get("resources", {}).items():
            try:
                resource_type = ResourceType(resource_name.upper())
                resources[resource_type] = probability
            except ValueError:
                # Skip unknown resource types
                continue
        
        return resources
    
    def get_biome_temperature_range(self, biome_type: BiomeType) -> tuple:
        """Get temperature range for a biome."""
        config = self.get_biome_config(biome_type)
        return tuple(config.get("temperature_range", [0.5, 0.7])) if config else (0.5, 0.7)
    
    def get_biome_humidity_range(self, biome_type: BiomeType) -> tuple:
        """Get humidity range for a biome."""
        config = self.get_biome_config(biome_type)
        return tuple(config.get("humidity_range", [0.4, 0.6])) if config else (0.4, 0.6)
    
    def get_adjacent_biomes(self, biome_type: BiomeType) -> List[BiomeType]:
        """Get list of biomes that can be adjacent to this biome."""
        config = self.get_biome_config(biome_type)
        if not config:
            return []
        
        adjacent = []
        for biome_name in config.get("adjacent_biomes", []):
            try:
                adjacent_biome = BiomeType(biome_name.upper())
                adjacent.append(adjacent_biome)
            except ValueError:
                # Skip unknown biome types
                continue
        
        return adjacent
    
    def get_biome_rarity(self, biome_type: BiomeType) -> float:
        """Get rarity factor for biome (affects generation probability)."""
        config = self.get_biome_config(biome_type)
        return config.get("rarity", 1.0) if config else 1.0
    
    def get_transition_difficulty(self, biome_type: BiomeType) -> float:
        """Get difficulty of transitioning to this biome."""
        config = self.get_biome_config(biome_type)
        return config.get("transition_difficulty", 0.5) if config else 0.5
    
    def reload_configs(self):
        """Force reload configuration from file."""
        self._config_loader.reload_config()
    
    def save_default_config_file(self):
        """Save default configuration to file."""
        self._config_loader.save_default_config() 