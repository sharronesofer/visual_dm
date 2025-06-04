"""
Population Configuration Loader

Technical utility for loading population configuration from JSON files.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PopulationConfigLoader:
    """Loads population configuration from JSON files"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Optional path to population configuration JSON
        """
        if config_path is None:
            # Default config path in data directory
            config_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "systems" / "population" / "population_config.json"
        
        self.config_path = Path(config_path)
        self._config_cache = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load population configuration from JSON file."""
        if self._config_cache is not None:
            return self._config_cache
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded population configuration from {self.config_path}")
            self._config_cache = config
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found at {self.config_path}, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file loading fails."""
        return {
            "growth_control": {
                "base_growth_rate": 0.02,
                "max_growth_rate": 0.08,
                "min_growth_rate": -0.05,
                "carrying_capacity_factor": 1.2,
                "overpopulation_penalty": 0.15,
                "underpopulation_bonus": 0.05,
                "minimum_viable_population": 50,
                "extinction_threshold": 10
            },
            "racial_distribution": {
                "default_weights": {
                    "human": 0.60,
                    "elf": 0.15,
                    "dwarf": 0.10,
                    "halfling": 0.08,
                    "orc": 0.04,
                    "goblin": 0.02,
                    "giant": 0.005,
                    "dragon": 0.001,
                    "fairy": 0.003,
                    "beast_folk": 0.002
                }
            }
        }
    
    def save_config(self, config: Dict[str, Any], config_path: Optional[str] = None) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            config: Configuration dictionary to save
            config_path: Optional path to save to (defaults to loaded path)
        """
        save_path = Path(config_path) if config_path else self.config_path
        
        try:
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved population configuration to {save_path}")
            self._config_cache = config  # Update cache
            
        except Exception as e:
            logger.error(f"Error saving configuration to {save_path}: {e}")
            raise
    
    def reload_config(self) -> Dict[str, Any]:
        """Force reload configuration from file."""
        self._config_cache = None
        return self.load_config()


# Global instance for easy access
_config_loader = None

def get_population_config_loader() -> PopulationConfigLoader:
    """Get the global population configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = PopulationConfigLoader()
    return _config_loader

def load_population_config() -> Dict[str, Any]:
    """Load population configuration using the global loader."""
    return get_population_config_loader().load_config() 