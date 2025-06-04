"""
Biome Placement Configuration Manager - Infrastructure

Technical infrastructure for loading and managing biome placement configurations from external JSON files.
This handles file I/O and configuration loading, separated from business logic.
"""

from typing import Dict, Optional, Tuple
from pathlib import Path

from backend.infrastructure.config_loaders import JsonConfigLoader


class BiomePlacementConfigManager:
    """Technical infrastructure for managing biome placement configurations loaded from JSON files."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Point to the JSON file in data directory
            config_path = Path("data/systems/world_generation/biome_placement_config.json")
        
        # Use the infrastructure JSON loader with default config
        self._config_loader = JsonConfigLoader(
            config_path=str(config_path),
            default_config=self._get_default_biome_placement_config()
        )
    
    def _get_default_biome_placement_config(self) -> Dict[str, dict]:
        """Provide default biome placement configuration as fallback."""
        return {
            "biome_scoring": {
                "environmental_weights": {
                    "temperature": 0.4,
                    "humidity": 0.4,
                    "elevation": 0.2
                },
                "elevation_bonuses": {
                    "mountains": {
                        "min_elevation": 0.6,
                        "bonus_multiplier": 1.5
                    },
                    "coastal": {
                        "max_elevation": 0.3,
                        "bonus_multiplier": 1.2
                    },
                    "swamp": {
                        "max_elevation": 0.2,
                        "bonus_multiplier": 1.3
                    }
                },
                "range_scoring": {
                    "perfect_fit_center_penalty": 0.2,
                    "outside_range_decay_base": 0.8,
                    "outside_range_decay_multiplier": 10
                }
            },
            "clustering": {
                "default_clustering_factor": 0.8,
                "max_clustering_iterations": 3,
                "influence_calculation": {
                    "neighbor_influence_weight": 1.0
                }
            },
            "adjacency_validation": {
                "max_validation_iterations": 5,
                "validation_enabled": True
            }
        }
    
    def get_config(self) -> Dict[str, dict]:
        """Get the full biome placement configuration."""
        return self._config_loader.load_config()
    
    def get_environmental_weights(self) -> Dict[str, float]:
        """Get weights for environmental factors in biome scoring."""
        config = self.get_config()
        return config.get("biome_scoring", {}).get("environmental_weights", {
            "temperature": 0.4,
            "humidity": 0.4,
            "elevation": 0.2
        })
    
    def get_elevation_bonus_config(self, biome_type: str) -> Optional[Dict[str, float]]:
        """Get elevation bonus configuration for a specific biome type."""
        config = self.get_config()
        elevation_bonuses = config.get("biome_scoring", {}).get("elevation_bonuses", {})
        return elevation_bonuses.get(biome_type.lower())
    
    def get_range_scoring_config(self) -> Dict[str, float]:
        """Get configuration for range scoring calculations."""
        config = self.get_config()
        return config.get("biome_scoring", {}).get("range_scoring", {
            "perfect_fit_center_penalty": 0.2,
            "outside_range_decay_base": 0.8,
            "outside_range_decay_multiplier": 10
        })
    
    def get_clustering_config(self) -> Dict[str, float]:
        """Get configuration for biome clustering behavior."""
        config = self.get_config()
        return config.get("clustering", {})
    
    def get_default_clustering_factor(self) -> float:
        """Get the default clustering factor."""
        clustering_config = self.get_clustering_config()
        return clustering_config.get("default_clustering_factor", 0.8)
    
    def get_max_clustering_iterations(self) -> int:
        """Get the maximum number of clustering iterations."""
        clustering_config = self.get_clustering_config()
        return clustering_config.get("max_clustering_iterations", 3)
    
    def get_adjacency_validation_config(self) -> Dict[str, any]:
        """Get configuration for adjacency validation."""
        config = self.get_config()
        return config.get("adjacency_validation", {
            "max_validation_iterations": 5,
            "validation_enabled": True
        })
    
    def get_max_validation_iterations(self) -> int:
        """Get the maximum number of validation iterations."""
        validation_config = self.get_adjacency_validation_config()
        return validation_config.get("max_validation_iterations", 5)
    
    def is_validation_enabled(self) -> bool:
        """Check if adjacency validation is enabled."""
        validation_config = self.get_adjacency_validation_config()
        return validation_config.get("validation_enabled", True)
    
    def reload_configs(self):
        """Reload configuration from files."""
        self._config_loader.reload_config()
    
    def save_default_config_file(self):
        """Save the default configuration to file for editing."""
        self._config_loader.save_default_config()


# Create global instance for access
def create_biome_placement_config_manager() -> BiomePlacementConfigManager:
    """Factory function to create biome placement config manager."""
    return BiomePlacementConfigManager()


# Global instance
BIOME_PLACEMENT_CONFIG_MANAGER = create_biome_placement_config_manager() 