"""
Combat Configuration Loader

This module provides centralized access to combat system configuration,
replacing hardcoded values throughout the system.
"""

import json
import os
from typing import Dict, Any, List, Union
from pathlib import Path

class CombatConfig:
    """
    Centralized combat configuration management.
    
    Loads configuration from JSON and provides safe access to configuration values
    with fallbacks to sensible defaults.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the combat configuration.
        
        Args:
            config_path: Optional path to config file. Defaults to config.json in data/systems/combat directory.
        """
        if config_path is None:
            # Default to config.json in the data/systems/combat directory
            config_path = Path(__file__).parent.parent.parent.parent / "data" / "systems" / "combat" / "config.json"
        
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file with fallback defaults."""
        default_config = {
            "default_stats": {
                "hp": 20,
                "ac": 10,
                "movement_speed": 30.0,
                "max_hp": 20,
                "dex_modifier": 0
            },
            "dice_systems": {
                "initiative": "1d20",
                "default_damage": "1d6",
                "initiative_die_size": 20,
                "initiative_die_count": 1
            },
            "action_economy": {
                "standard_actions_per_turn": 1,
                "bonus_actions_per_turn": 1,
                "reactions_per_round": 1,
                "free_actions_unlimited": True
            },
            "effect_durations": {
                "short_term": 3,
                "medium_term": 10,
                "long_term": 100,
                "persistent_threshold": 20
            },
            "combat_mechanics": {
                "min_damage": 0,
                "critical_hit_threshold": 20,
                "auto_miss_threshold": 1,
                "unconscious_hp_threshold": 0
            },
            "logging": {
                "enable_combat_logging": True,
                "max_log_entries": 1000,
                "enable_narrative_generation": True
            },
            "field_mappings": {
                "hp_fields": ["hp", "HP"],
                "ac_fields": ["ac", "AC"],
                "max_hp_fields": ["max_hp", "maxHP", "MAX_HP"]
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_configs(default_config, loaded_config)
            else:
                print(f"Warning: Combat config file not found at {self.config_path}, using defaults")
                return default_config
        except Exception as e:
            print(f"Error loading combat config: {e}, using defaults")
            return default_config
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge loaded config with defaults."""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value (e.g., 'default_stats.hp')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_default_stat(self, stat_name: str) -> Union[int, float]:
        """Get a default stat value."""
        return self.get(f"default_stats.{stat_name}", 0)
    
    def get_dice_config(self, dice_type: str) -> str:
        """Get dice configuration string."""
        return self.get(f"dice_systems.{dice_type}", "1d6")
    
    def get_action_economy(self, action_type: str) -> int:
        """Get action economy limits."""
        return self.get(f"action_economy.{action_type}", 1)
    
    def get_effect_duration(self, duration_type: str) -> int:
        """Get standard effect duration."""
        return self.get(f"effect_durations.{duration_type}", 3)
    
    def get_hp_fields(self) -> List[str]:
        """Get list of HP field names to check."""
        return self.get("field_mappings.hp_fields", ["hp", "HP"])
    
    def get_ac_fields(self) -> List[str]:
        """Get list of AC field names to check."""
        return self.get("field_mappings.ac_fields", ["ac", "AC"])
    
    def get_max_hp_fields(self) -> List[str]:
        """Get list of max HP field names to check."""
        return self.get("field_mappings.max_hp_fields", ["max_hp", "maxHP", "MAX_HP"])
    
    def get_safe_value(self, data: Dict[str, Any], field_names: List[str], default: Any = 0) -> Any:
        """
        Safely get a value from data using multiple possible field names.
        
        Args:
            data: Dictionary to search
            field_names: List of field names to try
            default: Default value if none found
            
        Returns:
            First found value or default
        """
        for field_name in field_names:
            if field_name in data:
                return data[field_name]
        return default
    
    def get_hp(self, character_data: Dict[str, Any]) -> int:
        """Safely get HP from character data."""
        return self.get_safe_value(character_data, self.get_hp_fields(), self.get_default_stat('hp'))
    
    def get_ac(self, character_data: Dict[str, Any]) -> int:
        """Safely get AC from character data."""
        return self.get_safe_value(character_data, self.get_ac_fields(), self.get_default_stat('ac'))
    
    def get_max_hp(self, character_data: Dict[str, Any]) -> int:
        """Safely get max HP from character data."""
        return self.get_safe_value(character_data, self.get_max_hp_fields(), self.get_hp(character_data))
    
    def set_hp(self, character_data: Dict[str, Any], new_hp: int) -> None:
        """Set HP in character data for all relevant fields."""
        hp_fields = self.get_hp_fields()
        for field in hp_fields:
            if field in character_data:
                character_data[field] = new_hp
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._config = self._load_config()

# Global configuration instance
combat_config = CombatConfig() 