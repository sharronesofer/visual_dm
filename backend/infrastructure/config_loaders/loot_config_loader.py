"""
Loot Configuration Loader - Infrastructure Layer

This module loads configuration from JSON files and provides it to the loot system,
handling all file I/O and caching operations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# Get the config directory relative to data/systems/loot
CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "data" / "systems" / "loot"


class LootConfigLoader:
    """Loads and caches loot system configuration from JSON files."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the config loader.
        
        Args:
            config_dir: Optional custom config directory path
        """
        self.config_dir = config_dir or CONFIG_DIR
        self._cache = {}
    
    @lru_cache(maxsize=10)
    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """
        Load a configuration file with caching.
        
        Args:
            filename: Name of the config file to load
            
        Returns:
            Dictionary containing the configuration data
        """
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"Loaded config from {config_path}")
            return config
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}
    
    def get_rarity_config(self) -> Dict[str, Any]:
        """Get item rarity configuration."""
        return self._load_config_file("rarity_config.json")
    
    def get_economic_config(self) -> Dict[str, Any]:
        """Get economic factors and pricing configuration."""
        return self._load_config_file("economic_config.json")
    
    def get_shop_config(self) -> Dict[str, Any]:
        """Get shop types and specializations configuration."""
        return self._load_config_file("shop_config.json")
    
    def get_environmental_config(self) -> Dict[str, Any]:
        """Get biome and motif effects configuration."""
        return self._load_config_file("environmental_config.json")
    
    def get_rarity_chances(self) -> Dict[str, float]:
        """Get just the rarity chance values."""
        config = self.get_rarity_config()
        rarities = config.get("rarities", {})
        return {rarity: data.get("chance", 0.0) for rarity, data in rarities.items()}
    
    def get_rarity_multipliers(self) -> Dict[str, float]:
        """Get just the rarity value multipliers."""
        config = self.get_rarity_config()
        rarities = config.get("rarities", {})
        return {rarity: data.get("value_multiplier", 1.0) for rarity, data in rarities.items()}
    
    def get_shop_type_config(self, shop_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific shop type.
        
        Args:
            shop_type: The shop type to get config for
            
        Returns:
            Configuration dict for the shop type
        """
        config = self.get_shop_config()
        return config.get("shop_types", {}).get(shop_type, {})
    
    def get_biome_effects(self, biome: str) -> Dict[str, Any]:
        """
        Get biome-specific loot effects.
        
        Args:
            biome: The biome name to get effects for
            
        Returns:
            Biome effects configuration
        """
        config = self.get_environmental_config()
        return config.get("environmental_effects", {}).get("biomes", {}).get(biome, {})
    
    def get_motif_effects(self, motif: str) -> Dict[str, Any]:
        """
        Get motif-specific loot effects.
        
        Args:
            motif: The motif name to get effects for
            
        Returns:
            Motif effects configuration
        """
        config = self.get_environmental_config()
        return config.get("environmental_effects", {}).get("motifs", {}).get(motif, {})
    
    def get_economic_factors(self) -> Dict[str, Any]:
        """Get economic factor ranges and defaults."""
        config = self.get_economic_config()
        return config.get("economic_factors", {})
    
    def get_supply_demand_config(self) -> Dict[str, Any]:
        """Get supply and demand configuration."""
        config = self.get_economic_config()
        return config.get("supply_demand", {})
    
    def clear_cache(self):
        """Clear the configuration cache."""
        self._load_config_file.cache_clear()
        self._cache.clear()
        logger.info("Configuration cache cleared")


# Global instance for easy access
config_loader = LootConfigLoader()


# Convenience functions for backward compatibility
def get_rarity_chances() -> Dict[str, float]:
    """Get item rarity chances."""
    return config_loader.get_rarity_chances()


def get_rarity_multipliers() -> Dict[str, float]:
    """Get item rarity value multipliers."""
    return config_loader.get_rarity_multipliers()


def get_shop_config(shop_type: str) -> Dict[str, Any]:
    """Get configuration for a specific shop type."""
    return config_loader.get_shop_type_config(shop_type)


def get_biome_effects(biome: str) -> Dict[str, Any]:
    """Get biome-specific loot effects."""
    return config_loader.get_biome_effects(biome)


def get_motif_effects(motif: str) -> Dict[str, Any]:
    """Get motif-specific loot effects."""
    return config_loader.get_motif_effects(motif)


def get_economic_factors() -> Dict[str, Any]:
    """Get economic factor configuration."""
    return config_loader.get_economic_factors()


# Default fallback values if config files are missing
DEFAULT_RARITY_CHANCES = {
    "common": 0.6,
    "uncommon": 0.25,
    "rare": 0.12,
    "epic": 0.025,
    "legendary": 0.0025
}

DEFAULT_RARITY_MULTIPLIERS = {
    "common": 1.0,
    "uncommon": 2.0,
    "rare": 5.0,
    "epic": 15.0,
    "legendary": 50.0
} 