"""
NPC Configuration Loader

Loads and manages JSON configuration files for the NPC system,
providing centralized access to NPC behavior, economic, and movement settings.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class NPCConfigLoader:
    """Loads and manages NPC system configuration from JSON files"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the config loader with the config directory"""
        if config_dir is None:
            # Point to the new data location
            config_dir = Path(__file__).parent.parent.parent.parent / "data" / "systems" / "npc"
        self.config_dir = Path(config_dir)
        self._config_cache = {}
        
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load a specific configuration file"""
        if config_name in self._config_cache:
            return self._config_cache[config_name]
            
        config_file = self.config_dir / f"{config_name}.json"
        if not config_file.exists():
            logger.warning(f"Configuration file not found: {config_file}")
            return {}
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self._config_cache[config_name] = config_data
            logger.info(f"Loaded NPC configuration: {config_name}")
            return config_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_file}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")
            return {}
    
    def reload_config(self, config_name: str) -> Dict[str, Any]:
        """Reload a configuration file, clearing cache"""
        if config_name in self._config_cache:
            del self._config_cache[config_name]
        return self.load_config(config_name)
    
    def get_npc_types_config(self) -> Dict[str, Any]:
        """Get NPC type behavior profiles configuration"""
        return self.load_config("npc-types")
    
    def get_economic_regions_config(self) -> Dict[str, Any]:
        """Get economic regional settings configuration"""
        return self.load_config("economic-regions")
    
    def get_item_trading_rules_config(self) -> Dict[str, Any]:
        """Get item availability rules configuration"""
        return self.load_config("item-trading-rules")
    
    def get_loyalty_rules_config(self) -> Dict[str, Any]:
        """Get loyalty system configuration"""
        return self.load_config("loyalty-rules")
    
    def get_travel_behaviors_config(self) -> Dict[str, Any]:
        """Get NPC movement patterns configuration"""
        return self.load_config("travel-behaviors")
    
    def get_npc_type_behavior(self, npc_type: str) -> Dict[str, Any]:
        """Get behavior configuration for a specific NPC type"""
        config = self.get_npc_types_config()
        return config.get(npc_type, config.get("unknown", {}))
    
    def get_region_economic_data(self, region_id: str) -> Dict[str, Any]:
        """Get economic data for a specific region"""
        config = self.get_economic_regions_config()
        regions = config.get("regions", {})
        return regions.get(region_id, regions.get("default", {}))
    
    def get_loyalty_settings(self) -> Dict[str, Any]:
        """Get loyalty system settings"""
        return self.get_loyalty_rules_config()
    
    def get_travel_settings_for_wanderlust(self, wanderlust_level: int) -> Dict[str, Any]:
        """Get travel settings for a specific wanderlust level"""
        config = self.get_travel_behaviors_config()
        behaviors = config.get("wanderlust_behaviors", {})
        return behaviors.get(str(wanderlust_level), behaviors.get("0", {}))
    
    def get_profession_essential_items(self, profession: str) -> list:
        """Get essential items for a profession"""
        config = self.get_item_trading_rules_config()
        essentials = config.get("profession_essential_items", {})
        return essentials.get(profession.lower(), [])
    
    def clear_cache(self):
        """Clear all cached configuration data"""
        self._config_cache.clear()
        logger.info("Cleared NPC configuration cache")


# Global config loader instance
_global_config_loader = None


def get_npc_config() -> NPCConfigLoader:
    """Get the global NPC configuration loader instance"""
    global _global_config_loader
    if _global_config_loader is None:
        _global_config_loader = NPCConfigLoader()
    return _global_config_loader


def reload_npc_config():
    """Reload all NPC configuration files"""
    global _global_config_loader
    if _global_config_loader is not None:
        _global_config_loader.clear_cache()
    logger.info("Reloaded NPC configuration")


@lru_cache(maxsize=128)
def get_cached_npc_type_behavior(npc_type: str) -> Dict[str, Any]:
    """Get cached NPC type behavior (with LRU cache for performance)"""
    return get_npc_config().get_npc_type_behavior(npc_type)


@lru_cache(maxsize=64)
def get_cached_region_economic_data(region_id: str) -> Dict[str, Any]:
    """Get cached region economic data (with LRU cache for performance)"""
    return get_npc_config().get_region_economic_data(region_id) 