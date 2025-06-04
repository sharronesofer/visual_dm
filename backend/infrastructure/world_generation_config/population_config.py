"""
Population Configuration Manager - Infrastructure

Technical infrastructure for loading and managing population configurations from external JSON files.
This handles file I/O and configuration loading, separated from business logic.
"""

from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import random

from backend.infrastructure.config_loaders import JsonConfigLoader


class PopulationConfigManager:
    """Technical infrastructure for managing population configurations loaded from JSON files."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Point to the JSON file in data directory
            config_path = Path("data/systems/world_generation/population_config.json")
        
        # Use the infrastructure JSON loader with default config
        self._config_loader = JsonConfigLoader(
            config_path=str(config_path),
            default_config=self._get_default_population_config()
        )
    
    def _get_default_population_config(self) -> Dict[str, Any]:
        """Provide default population configuration as fallback."""
        return {
            "world_scale": {
                "visible_npc_targets": {
                    "minimal": 50000,
                    "standard": 100000,
                    "revolutionary": 200000,
                    "godlike": 400000
                },
                "npc_computational_costs": {
                    "tier_1_active": 10.0,
                    "tier_2_background": 2.0,
                    "tier_3_dormant": 0.1,
                    "tier_3_5_compressed": 0.02,
                    "tier_4_statistical": 0.0
                },
                "npc_memory_costs": {
                    "tier_1_active": 2.5,
                    "tier_2_background": 1.0,
                    "tier_3_dormant": 0.2,
                    "tier_3_5_compressed": 0.05,
                    "tier_4_statistical": 0.0
                }
            },
            "region_level": {
                "total_population_range": [2000, 5000],
                "visible_population_range": [800, 2000],
                "metropolis_total_population_range": [5000, 15000],
                "metropolis_visible_population_range": [2000, 6000]
            },
            "poi_level": {
                "settlement_population_ranges": {
                    "hamlet": [20, 80],
                    "village": [80, 300],
                    "town": [300, 1200],
                    "city": [1200, 5000],
                    "metropolis": [5000, 15000]
                },
                "non_settlement_population_ranges": {
                    "dungeon": [5, 50],
                    "mine": [20, 150],
                    "fortress": [100, 800],
                    "temple": [10, 100],
                    "ruins": [0, 20],
                    "wilderness": [1, 10],
                    "exploration": [5, 30]
                }
            },
            "poi_distribution": {
                "settlements_per_region": 12,
                "settlement_type_distribution": {
                    "hamlet": 0.4,
                    "village": 0.35,
                    "town": 0.20,
                    "city": 0.04,
                    "metropolis": 0.01
                },
                "non_settlement_pois_per_region": 25,
                "non_settlement_type_distribution": {
                    "dungeon": 0.25,
                    "mine": 0.15,
                    "fortress": 0.08,
                    "temple": 0.10,
                    "ruins": 0.12,
                    "wilderness": 0.20,
                    "exploration": 0.10
                }
            },
            "continental_scale": {
                "continent_region_range": [80, 120],
                "island_region_range": [5, 15],
                "islands_per_world": 3
            },
            "npc_distribution": {
                "default_tier_ratios": {
                    "tier_4_statistical": 0.85,
                    "tier_3_dormant": 0.10,
                    "tier_2_background": 0.05,
                    "tier_1_active": 0.00
                },
                "poi_type_adjustments": {
                    "city": {
                        "tier_4_statistical": 0.80,
                        "tier_3_dormant": 0.12,
                        "tier_2_background": 0.08,
                        "tier_1_active": 0.00
                    },
                    "metropolis": {
                        "tier_4_statistical": 0.80,
                        "tier_3_dormant": 0.12,
                        "tier_2_background": 0.08,
                        "tier_1_active": 0.00
                    },
                    "fortress": {
                        "tier_4_statistical": 0.75,
                        "tier_3_dormant": 0.15,
                        "tier_2_background": 0.10,
                        "tier_1_active": 0.00
                    },
                    "military": {
                        "tier_4_statistical": 0.75,
                        "tier_3_dormant": 0.15,
                        "tier_2_background": 0.10,
                        "tier_1_active": 0.00
                    }
                }
            },
            "region_type_multipliers": {
                "rural": 0.7,
                "standard": 1.0,
                "urban": 1.5,
                "metropolis": 2.5
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get the full population configuration."""
        return self._config_loader.load_config()
    
    def get_world_visible_npc_targets(self) -> Dict[str, int]:
        """Get visible NPC targets for different immersion levels."""
        config = self.get_config()
        return config.get("world_scale", {}).get("visible_npc_targets", {})
    
    def get_npc_computational_costs(self) -> Dict[str, float]:
        """Get computational costs per NPC tier."""
        config = self.get_config()
        return config.get("world_scale", {}).get("npc_computational_costs", {})
    
    def get_npc_memory_costs(self) -> Dict[str, float]:
        """Get memory costs per NPC tier."""
        config = self.get_config()
        return config.get("world_scale", {}).get("npc_memory_costs", {})
    
    def get_region_total_population_range(self) -> Tuple[int, int]:
        """Get total population range for regions."""
        config = self.get_config()
        range_list = config.get("region_level", {}).get("total_population_range", [2000, 5000])
        return tuple(range_list)
    
    def get_region_visible_population_range(self) -> Tuple[int, int]:
        """Get visible population range for regions."""
        config = self.get_config()
        range_list = config.get("region_level", {}).get("visible_population_range", [800, 2000])
        return tuple(range_list)
    
    def get_metropolis_total_population_range(self) -> Tuple[int, int]:
        """Get total population range for metropolis regions."""
        config = self.get_config()
        range_list = config.get("region_level", {}).get("metropolis_total_population_range", [5000, 15000])
        return tuple(range_list)
    
    def get_metropolis_visible_population_range(self) -> Tuple[int, int]:
        """Get visible population range for metropolis regions."""
        config = self.get_config()
        range_list = config.get("region_level", {}).get("metropolis_visible_population_range", [2000, 6000])
        return tuple(range_list)
    
    def get_settlement_population_ranges(self) -> Dict[str, Tuple[int, int]]:
        """Get population ranges for different settlement types."""
        config = self.get_config()
        ranges = config.get("poi_level", {}).get("settlement_population_ranges", {})
        return {k: tuple(v) for k, v in ranges.items()}
    
    def get_non_settlement_population_ranges(self) -> Dict[str, Tuple[int, int]]:
        """Get population ranges for different non-settlement POI types."""
        config = self.get_config()
        ranges = config.get("poi_level", {}).get("non_settlement_population_ranges", {})
        return {k: tuple(v) for k, v in ranges.items()}
    
    def get_settlements_per_region(self) -> int:
        """Get number of settlements per region."""
        config = self.get_config()
        return config.get("poi_distribution", {}).get("settlements_per_region", 12)
    
    def get_settlement_type_distribution(self) -> Dict[str, float]:
        """Get distribution of settlement types."""
        config = self.get_config()
        return config.get("poi_distribution", {}).get("settlement_type_distribution", {})
    
    def get_non_settlement_pois_per_region(self) -> int:
        """Get number of non-settlement POIs per region."""
        config = self.get_config()
        return config.get("poi_distribution", {}).get("non_settlement_pois_per_region", 25)
    
    def get_non_settlement_type_distribution(self) -> Dict[str, float]:
        """Get distribution of non-settlement POI types."""
        config = self.get_config()
        return config.get("poi_distribution", {}).get("non_settlement_type_distribution", {})
    
    def get_total_pois_per_region(self) -> int:
        """Get total POIs per region."""
        return self.get_settlements_per_region() + self.get_non_settlement_pois_per_region()
    
    def get_continent_region_range(self) -> Tuple[int, int]:
        """Get region count range for main continent."""
        config = self.get_config()
        range_list = config.get("continental_scale", {}).get("continent_region_range", [80, 120])
        return tuple(range_list)
    
    def get_island_region_range(self) -> Tuple[int, int]:
        """Get region count range for islands."""
        config = self.get_config()
        range_list = config.get("continental_scale", {}).get("island_region_range", [5, 15])
        return tuple(range_list)
    
    def get_islands_per_world(self) -> int:
        """Get number of islands per world."""
        config = self.get_config()
        return config.get("continental_scale", {}).get("islands_per_world", 3)
    
    def get_total_world_regions(self) -> Tuple[int, int]:
        """Calculate total regions in world (continent + islands)."""
        continent_range = self.get_continent_region_range()
        island_range = self.get_island_region_range()
        islands_count = self.get_islands_per_world()
        
        min_total = continent_range[0] + (islands_count * island_range[0])
        max_total = continent_range[1] + (islands_count * island_range[1])
        
        return (min_total, max_total)
    
    def get_total_world_pois(self) -> Tuple[int, int]:
        """Calculate total POIs in world."""
        min_regions, max_regions = self.get_total_world_regions()
        pois_per_region = self.get_total_pois_per_region()
        
        return (min_regions * pois_per_region, max_regions * pois_per_region)
    
    def get_total_world_population(self) -> Tuple[int, int]:
        """Calculate total world population (all tiers)."""
        min_regions, max_regions = self.get_total_world_regions()
        population_range = self.get_region_total_population_range()
        
        return (min_regions * population_range[0], max_regions * population_range[1])
    
    def get_total_visible_world_population(self) -> Tuple[int, int]:
        """Calculate total visible world population (Tiers 1-3.5)."""
        min_regions, max_regions = self.get_total_world_regions()
        visible_range = self.get_region_visible_population_range()
        
        return (min_regions * visible_range[0], max_regions * visible_range[1])
    
    def get_npc_tier_ratios(self, poi_type: str = None) -> Dict[str, float]:
        """Get NPC tier distribution ratios for a POI type."""
        config = self.get_config()
        npc_dist = config.get("npc_distribution", {})
        
        # Start with default ratios
        ratios = npc_dist.get("default_tier_ratios", {}).copy()
        
        # Apply POI-specific adjustments if available
        if poi_type:
            adjustments = npc_dist.get("poi_type_adjustments", {})
            if poi_type in adjustments:
                ratios.update(adjustments[poi_type])
        
        return ratios
    
    def get_region_type_multipliers(self) -> Dict[str, float]:
        """Get population multipliers for different region types."""
        config = self.get_config()
        return config.get("region_type_multipliers", {})
    
    def reload_configs(self):
        """Reload configuration from files."""
        self._config_loader.reload_config()
    
    def save_default_config_file(self):
        """Save the default configuration to file for editing."""
        self._config_loader.save_default_config()


# Utility functions that work with the new configuration manager
def get_poi_population_range(poi_type: str, poi_size: str = None, 
                            config_manager: PopulationConfigManager = None) -> Tuple[int, int]:
    """
    Get population range for a specific POI type and size.
    
    Args:
        poi_type: Type of POI ('settlement', 'dungeon', etc.)
        poi_size: Size category for settlements ('hamlet', 'village', etc.)
        config_manager: Optional config manager instance
        
    Returns:
        Tuple of (min_population, max_population)
    """
    if config_manager is None:
        config_manager = PopulationConfigManager()
    
    if poi_type == 'settlement' or poi_type == 'social':
        settlement_ranges = config_manager.get_settlement_population_ranges()
        if poi_size and poi_size in settlement_ranges:
            return settlement_ranges[poi_size]
        else:
            # Default to village size
            return settlement_ranges.get('village', (80, 300))
    else:
        # Non-settlement POI
        non_settlement_ranges = config_manager.get_non_settlement_population_ranges()
        if poi_type in non_settlement_ranges:
            return non_settlement_ranges[poi_type]
        else:
            # Default to exploration size
            return non_settlement_ranges.get('exploration', (5, 30))


def calculate_region_population_target(region_type: str = 'standard',
                                     config_manager: PopulationConfigManager = None) -> int:
    """
    Calculate target population for a region based on type.
    
    Args:
        region_type: Type of region ('rural', 'standard', 'urban', 'metropolis')
        config_manager: Optional config manager instance
        
    Returns:
        Target total population for the region
    """
    if config_manager is None:
        config_manager = PopulationConfigManager()
    
    multipliers = config_manager.get_region_type_multipliers()
    base_range = config_manager.get_region_total_population_range()
    
    multiplier = multipliers.get(region_type, 1.0)
    
    target = random.randint(int(base_range[0] * multiplier), int(base_range[1] * multiplier))
    return target


def get_settlement_type_by_population(population: int,
                                    config_manager: PopulationConfigManager = None) -> str:
    """
    Determine settlement type based on population.
    
    Args:
        population: Population count
        config_manager: Optional config manager instance
        
    Returns:
        Settlement type string
    """
    if config_manager is None:
        config_manager = PopulationConfigManager()
    
    settlement_ranges = config_manager.get_settlement_population_ranges()
    
    for settlement_type, (min_pop, max_pop) in settlement_ranges.items():
        if min_pop <= population <= max_pop:
            return settlement_type
    
    # Default fallback
    if population < 80:
        return 'hamlet'
    elif population >= 5000:
        return 'metropolis'
    else:
        return 'village'


def calculate_npc_distribution_for_poi(total_population: int, poi_type: str,
                                     config_manager: PopulationConfigManager = None) -> Dict[str, int]:
    """
    Calculate NPC tier distribution for a POI based on type and population.
    
    Most NPCs start as Tier 4 (statistical) and are promoted when players visit.
    
    Args:
        total_population: Total NPC count for the POI
        poi_type: Type of POI
        config_manager: Optional config manager instance
        
    Returns:
        Dict with tier distribution
    """
    if config_manager is None:
        config_manager = PopulationConfigManager()
    
    ratios = config_manager.get_npc_tier_ratios(poi_type)
    
    return {
        'tier_1_active': int(total_population * ratios.get('tier_1_active', 0.0)),
        'tier_2_background': int(total_population * ratios.get('tier_2_background', 0.05)),
        'tier_3_dormant': int(total_population * ratios.get('tier_3_dormant', 0.10)),
        'tier_4_statistical': int(total_population * ratios.get('tier_4_statistical', 0.85))
    }


def get_world_population_summary(config_manager: PopulationConfigManager = None) -> Dict[str, Any]:
    """
    Get a summary of world population calculations for planning.
    
    Args:
        config_manager: Optional config manager instance
        
    Returns:
        Dict with population statistics and projections
    """
    if config_manager is None:
        config_manager = PopulationConfigManager()
    
    min_regions, max_regions = config_manager.get_total_world_regions()
    min_pois, max_pois = config_manager.get_total_world_pois()
    min_population, max_population = config_manager.get_total_world_population()
    min_visible, max_visible = config_manager.get_total_visible_world_population()
    
    visible_targets = config_manager.get_world_visible_npc_targets()
    
    return {
        'world_scale': {
            'regions': f"{min_regions:,} - {max_regions:,}",
            'pois': f"{min_pois:,} - {max_pois:,}",
            'total_population': f"{min_population:,} - {max_population:,}",
            'visible_population': f"{min_visible:,} - {max_visible:,}"
        },
        'immersion_targets': visible_targets,
        'computational_feasibility': {
            'revolutionary_target': visible_targets.get('revolutionary', 200000),
            'world_can_support': min_visible,
            'feasible': min_visible >= visible_targets.get('revolutionary', 200000)
        },
        'poi_distribution': {
            'settlements_per_region': config_manager.get_settlements_per_region(),
            'non_settlements_per_region': config_manager.get_non_settlement_pois_per_region(),
            'total_pois_per_region': config_manager.get_total_pois_per_region()
        }
    }


# Create global instance for backward compatibility
def create_population_config_manager() -> PopulationConfigManager:
    """Factory function to create population config manager."""
    return PopulationConfigManager()


# Global instance for backward compatibility
POPULATION_CONFIG_MANAGER = create_population_config_manager() 