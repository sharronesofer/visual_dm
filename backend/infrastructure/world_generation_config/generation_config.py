"""
Generation Configuration Manager - Infrastructure

Technical infrastructure for managing generation settings loaded from JSON configuration files,
replacing hardcoded constants in the world generation system. Handles file I/O and configuration loading.
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from backend.infrastructure.config_loaders import JsonConfigLoader


class GenerationConfigManager:
    """Technical infrastructure for managing generation configuration loaded from JSON files."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Point to the JSON file in data directory
            config_path = Path("data/systems/world_generation/generation_config.json")
        
        # Use the infrastructure JSON loader with default config
        self._config_loader = JsonConfigLoader(
            config_path=str(config_path),
            default_config=self._get_default_config()
        )
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Provide default configuration as fallback."""
        return {
            "poi_generation": {
                "type_weights": {"social": 0.5, "dungeon": 0.3, "exploration": 0.2},
                "terrain_constraints": {
                    "forbidden": ["mountain", "swamp", "tundra"],
                    "less_likely": ["desert", "coast"],
                    "less_likely_chance": 0.2
                },
                "spacing_requirements": {
                    "settlement_min_spacing": 350,
                    "non_settlement_min_spacing": 250
                }
            },
            "population_settings": {
                "region_population_range": [200, 400],
                "settlement_population_range": [30, 100],
                "metropolis_population_range": [200, 500]
            },
            "region_settings": {
                "total_region_tiles": 225,
                "settlements_per_region": 7,
                "non_settlement_pois_per_region": 14
            }
        }
    
    # POI Generation Methods
    def get_poi_type_weights(self) -> Dict[str, float]:
        """Get POI type weights for random selection."""
        return self._config_loader.get_config_value("poi_generation.type_weights", {})
    
    def get_forbidden_terrains(self) -> List[str]:
        """Get list of terrains where POIs cannot be placed."""
        return self._config_loader.get_config_value("poi_generation.terrain_constraints.forbidden", [])
    
    def get_less_likely_terrains(self) -> List[str]:
        """Get list of terrains where POIs are less likely to be placed."""
        return self._config_loader.get_config_value("poi_generation.terrain_constraints.less_likely", [])
    
    def get_less_likely_chance(self) -> float:
        """Get chance for POI placement on less likely terrains."""
        return self._config_loader.get_config_value("poi_generation.terrain_constraints.less_likely_chance", 0.2)
    
    def get_settlement_min_spacing(self) -> int:
        """Get minimum spacing between settlements."""
        return self._config_loader.get_config_value("poi_generation.spacing_requirements.settlement_min_spacing", 350)
    
    def get_non_settlement_min_spacing(self) -> int:
        """Get minimum spacing between non-settlement POIs."""
        return self._config_loader.get_config_value("poi_generation.spacing_requirements.non_settlement_min_spacing", 250)
    
    # Population Methods
    def get_region_population_range(self) -> Tuple[int, int]:
        """Get population range for regions."""
        range_list = self._config_loader.get_config_value("population_settings.region_population_range", [200, 400])
        return tuple(range_list)
    
    def get_settlement_population_range(self) -> Tuple[int, int]:
        """Get population range for settlements."""
        range_list = self._config_loader.get_config_value("population_settings.settlement_population_range", [30, 100])
        return tuple(range_list)
    
    def get_metropolis_population_range(self) -> Tuple[int, int]:
        """Get population range for metropolises."""
        range_list = self._config_loader.get_config_value("population_settings.metropolis_population_range", [200, 500])
        return tuple(range_list)
    
    def get_settlement_min_pop(self) -> int:
        """Get minimum population for settlements."""
        return self._config_loader.get_config_value("population_settings.settlement_min_pop", 30)
    
    def get_settlement_max_pop(self) -> int:
        """Get maximum population for settlements."""
        return self._config_loader.get_config_value("population_settings.settlement_max_pop", 100)
    
    def get_max_settlements(self) -> int:
        """Get maximum number of settlements per region."""
        return self._config_loader.get_config_value("population_settings.max_settlements", 12)
    
    # Region Settings
    def get_total_region_tiles(self) -> int:
        """Get total number of tiles per region."""
        return self._config_loader.get_config_value("region_settings.total_region_tiles", 225)
    
    def get_settlements_per_region(self) -> int:
        """Get number of settlements per region."""
        return self._config_loader.get_config_value("region_settings.settlements_per_region", 7)
    
    def get_non_settlement_pois_per_region(self) -> int:
        """Get number of non-settlement POIs per region."""
        return self._config_loader.get_config_value("region_settings.non_settlement_pois_per_region", 14)
    
    def get_region_hexes_per_region(self) -> int:
        """Get number of hexes per region."""
        return self._config_loader.get_config_value("region_settings.region_hexes_per_region", 225)
    
    def get_poi_spacing_hexes(self) -> int:
        """Get average spacing between POIs in hexes."""
        return self._config_loader.get_config_value("poi_generation.spacing_requirements.poi_spacing_hexes", 463)
    
    # Continent Settings
    def get_continent_min_regions(self) -> int:
        """Get minimum number of regions per continent."""
        return self._config_loader.get_config_value("continent_settings.continent_min_regions", 50)
    
    def get_continent_max_regions(self) -> int:
        """Get maximum number of regions per continent."""
        return self._config_loader.get_config_value("continent_settings.continent_max_regions", 70)
    
    # Coordinate Settings
    def get_origin_latitude(self) -> float:
        """Get origin latitude for coordinate mapping."""
        return self._config_loader.get_config_value("coordinate_settings.origin_latitude", -54.8019)
    
    def get_origin_longitude(self) -> float:
        """Get origin longitude for coordinate mapping."""
        return self._config_loader.get_config_value("coordinate_settings.origin_longitude", -68.3030)
    
    def get_region_latlon_scale(self) -> float:
        """Get scale for region to lat/lon conversion."""
        return self._config_loader.get_config_value("coordinate_settings.region_latlon_scale_degrees", 0.5)
    
    # Metropolis Types
    def get_metropolis_types(self) -> List[Dict[str, Any]]:
        """Get list of available metropolis types."""
        return self._config_loader.get_config_value("metropolis_types", [])
    
    def get_metropolis_type_names(self) -> List[str]:
        """Get list of metropolis type names."""
        return [mt["name"] for mt in self.get_metropolis_types()]
    
    def get_metropolis_type_info(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific metropolis type."""
        for mt in self.get_metropolis_types():
            if mt["name"] == type_name:
                return mt
        return None
    
    # Monster Generation
    def get_base_cr_range(self) -> Tuple[float, float]:
        """Get base challenge rating range for monsters."""
        range_list = self._config_loader.get_config_value("monster_generation.base_cr_range", [0.5, 2.0])
        return tuple(range_list)
    
    def get_danger_level_modifier(self, danger_level: int) -> float:
        """Get CR modifier for a specific danger level."""
        modifiers = self._config_loader.get_config_value("monster_generation.danger_level_modifiers", {})
        return modifiers.get(str(danger_level), 0.0)
    
    def get_party_cr_variance(self) -> float:
        """Get variance range for party CR adjustments."""
        return self._config_loader.get_config_value("monster_generation.party_cr_variance", 1.5)
    
    def get_monsters_per_encounter_range(self) -> Tuple[int, int]:
        """Get range for number of monsters per encounter."""
        range_list = self._config_loader.get_config_value("monster_generation.monsters_per_encounter", [1, 4])
        return tuple(range_list)
    
    # Tile Generation
    def get_tile_poi_chance(self) -> float:
        """Get chance for a tile to have a POI."""
        return self._config_loader.get_config_value("tile_generation.tile_poi_chance", 0.20)
    
    def get_terrain_types(self) -> List[str]:
        """Get list of available terrain types."""
        return self._config_loader.get_config_value("terrain_types", [])
    
    def reload_config(self):
        """Force reload configuration from file."""
        self._config_loader.reload_config()
    
    def save_config(self, config_data: Dict[str, Any]):
        """Save configuration data to file."""
        self._config_loader.save_config(config_data) 