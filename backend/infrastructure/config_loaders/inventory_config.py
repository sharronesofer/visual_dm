"""
Configuration loader for inventory system.

This module provides utilities to load and validate configuration files
for the inventory system, making business rules externally configurable.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class InventoryConfigLoader:
    """Loads and manages inventory system configuration"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            # Default to data/systems/inventory directory
            self.config_dir = Path(__file__).parent.parent.parent.parent / "data" / "systems" / "inventory"
        else:
            self.config_dir = Path(config_dir)
    
    @lru_cache(maxsize=None)
    def load_inventory_types(self) -> Dict[str, Any]:
        """Load inventory type definitions"""
        return self._load_config_file("inventory_types.json")
    
    @lru_cache(maxsize=None)
    def load_inventory_statuses(self) -> Dict[str, Any]:
        """Load inventory status definitions"""
        return self._load_config_file("inventory_statuses.json")
    
    @lru_cache(maxsize=None)
    def load_inventory_rules(self) -> Dict[str, Any]:
        """Load inventory business rules"""
        return self._load_config_file("inventory_rules.json")
    
    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """Load a JSON configuration file"""
        try:
            config_path = self.config_dir / filename
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return {}
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            logger.debug(f"Loaded config from {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config file {filename}: {str(e)}")
            return {}
    
    def get_inventory_type_config(self, inventory_type: str) -> Dict[str, Any]:
        """Get configuration for a specific inventory type"""
        types_config = self.load_inventory_types()
        return types_config.get(inventory_type, {})
    
    def get_status_config(self, status: str) -> Dict[str, Any]:
        """Get configuration for a specific status"""
        statuses_config = self.load_inventory_statuses()
        return statuses_config.get(status, {})
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules"""
        rules_config = self.load_inventory_rules()
        return rules_config.get("validation", {})
    
    def get_sorting_options(self) -> Dict[str, Any]:
        """Get available sorting options"""
        rules_config = self.load_inventory_rules()
        return rules_config.get("sorting_options", {})
    
    def get_filtering_options(self) -> Dict[str, Any]:
        """Get available filtering options"""
        rules_config = self.load_inventory_rules()
        return rules_config.get("filtering_options", {})
    
    def get_pagination_config(self) -> Dict[str, Any]:
        """Get pagination configuration"""
        rules_config = self.load_inventory_rules()
        return rules_config.get("pagination", {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default values"""
        rules_config = self.load_inventory_rules()
        return rules_config.get("defaults", {})
    
    def validate_inventory_type(self, inventory_type: str) -> bool:
        """Check if inventory type is valid"""
        types_config = self.load_inventory_types()
        return inventory_type in types_config
    
    def validate_status(self, status: str) -> bool:
        """Check if status is valid"""
        validation_rules = self.get_validation_rules()
        allowed_statuses = validation_rules.get("allowed_status_values", [])
        return status in allowed_statuses
    
    def can_transition_status(self, from_status: str, to_status: str) -> bool:
        """Check if status transition is allowed"""
        from_config = self.get_status_config(from_status)
        allowed_transitions = from_config.get("can_transition_to", [])
        return to_status in allowed_transitions
    
    def allows_operations(self, status: str) -> bool:
        """Check if status allows operations"""
        status_config = self.get_status_config(status)
        return status_config.get("allows_operations", True)
    
    def is_visible_to_player(self, status: str) -> bool:
        """Check if inventory with this status is visible to players"""
        status_config = self.get_status_config(status)
        return status_config.get("visible_to_player", True)

# Global instance for easy access
_config_loader = None

def get_config_loader() -> InventoryConfigLoader:
    """Get the global configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = InventoryConfigLoader()
    return _config_loader

def reload_config():
    """Reload configuration from files (clears cache)"""
    global _config_loader
    if _config_loader is not None:
        # Clear the cache
        _config_loader.load_inventory_types.cache_clear()
        _config_loader.load_inventory_statuses.cache_clear()
        _config_loader.load_inventory_rules.cache_clear()
        logger.info("Inventory configuration reloaded") 