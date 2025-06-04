"""
Economy Configuration Loader

Utility for loading and caching economy configuration files.
Provides centralized access to all economy system configuration data.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EconomyConfigLoader:
    """Loader for economy system configuration files"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config loader.
        
        Args:
            config_dir: Optional custom config directory path
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to data/systems/economy directory relative to project root
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent  # Go up from backend/infrastructure/config_loaders/
            self.config_dir = project_root / "data" / "systems" / "economy"
        
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._loaded_files: set = set()
    
    def load_config(self, config_name: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load a configuration file by name.
        
        Args:
            config_name: Name of config file (without .json extension)
            force_reload: Force reload even if cached
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file has invalid JSON
        """
        if config_name in self._cache and not force_reload:
            return self._cache[config_name]
        
        config_path = self.config_dir / f"{config_name}.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self._cache[config_name] = config_data
            self._loaded_files.add(config_name)
            
            logger.debug(f"Loaded economy config: {config_name}")
            return config_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading config file {config_path}: {str(e)}")
            raise
    
    def get_price_modifiers(self) -> Dict[str, Any]:
        """Get price modifier configuration"""
        return self.load_config("price_modifiers")
    
    def get_economic_cycles(self) -> Dict[str, Any]:
        """Get economic cycles configuration"""
        return self.load_config("economic_cycles")
    
    def get_player_economy(self) -> Dict[str, Any]:
        """Get player economy configuration"""
        return self.load_config("player_economy")
    
    def get_danger_level_modifiers(self) -> Dict[str, float]:
        """Get danger level price modifiers"""
        config = self.get_price_modifiers()
        return config["danger_level_modifiers"]["modifiers"]
    
    def get_infrastructure_modifiers(self) -> Dict[str, float]:
        """Get infrastructure price modifiers"""
        config = self.get_price_modifiers()
        return config["infrastructure_modifiers"]
    
    def get_trade_route_config(self) -> Dict[str, float]:
        """Get trade route safety configuration"""
        config = self.get_price_modifiers()
        return config["trade_route_safety"]
    
    def get_guild_control_config(self) -> Dict[str, float]:
        """Get guild control configuration"""
        config = self.get_price_modifiers()
        return config["guild_control"]
    
    def get_shop_pricing_config(self) -> Dict[str, float]:
        """Get shop pricing configuration"""
        config = self.get_price_modifiers()
        return config["shop_pricing"]
    
    def get_gold_earning_rates(self) -> Dict[str, Any]:
        """Get player gold earning rates by level"""
        config = self.get_player_economy()
        return config["gold_earning_rates"]
    
    def get_item_cost_scaling(self) -> Dict[str, Any]:
        """Get item cost scaling configuration"""
        config = self.get_player_economy()
        return config["item_cost_scaling"]
    
    def get_tournament_config(self) -> Dict[str, Any]:
        """Get tournament economy configuration"""
        return self.load_config("tournament_config")
    
    def get_central_bank_config(self) -> Dict[str, Any]:
        """Get central bank configuration"""
        return self.load_config("central_bank_config")
    
    def get_economic_sinks(self) -> Dict[str, Any]:
        """Get economic sink mechanisms configuration"""
        config = self.get_player_economy()
        return config["economic_sinks"]
    
    def get_phase_modifiers(self) -> Dict[str, Any]:
        """Get economic cycle phase modifiers"""
        config = self.get_economic_cycles()
        return config["phase_modifiers"]
    
    def get_phase_durations(self) -> Dict[str, int]:
        """Get economic cycle phase durations"""
        config = self.get_economic_cycles()
        return config["phase_durations"]
    
    def reload_all(self) -> None:
        """Reload all cached configuration files"""
        for config_name in list(self._loaded_files):
            self.load_config(config_name, force_reload=True)
        logger.info("Reloaded all economy configuration files")
    
    def clear_cache(self) -> None:
        """Clear configuration cache"""
        self._cache.clear()
        self._loaded_files.clear()
        logger.debug("Cleared economy configuration cache")


# Global instance for easy access
_config_loader: Optional[EconomyConfigLoader] = None


def get_economy_config() -> EconomyConfigLoader:
    """Get global economy configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = EconomyConfigLoader()
    return _config_loader


def reload_economy_config() -> None:
    """Reload all economy configuration"""
    global _config_loader
    if _config_loader is not None:
        _config_loader.reload_all()
    else:
        _config_loader = EconomyConfigLoader()


# Convenience functions for common config access
def get_danger_level_modifier(danger_level: int) -> float:
    """Get price modifier for a danger level"""
    modifiers = get_economy_config().get_danger_level_modifiers()
    return modifiers.get(str(danger_level), 1.0)


def get_daily_gold_for_level(level: int) -> int:
    """Get expected daily gold earning for a player level"""
    rates = get_economy_config().get_gold_earning_rates()
    return rates["base_rates_per_level"].get(str(level), 100)


def get_item_cost_multiplier(item_category: str, item_tier: str) -> float:
    """Get cost multiplier for an item category and tier"""
    scaling = get_economy_config().get_item_cost_scaling()
    category_config = scaling.get(item_category, {})
    return category_config.get(item_tier, 1.0) 