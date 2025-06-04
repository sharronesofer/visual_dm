"""
Skill Configuration Loader
--------------------------
Handles loading, validation, and hot-reloading of skill configuration data.
Provides centralized access to all skill-related configuration.
"""

import json
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import jsonschema

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Raised when there's an error with configuration."""
    pass

class ConfigFileHandler(FileSystemEventHandler):
    """Handles file system events for configuration hot-reload."""
    
    def __init__(self, config_loader):
        self.config_loader = config_loader
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('skill_configurations.json'):
            logger.info("Configuration file changed, reloading...")
            self.config_loader.reload_config()

class SkillConfigLoader:
    """
    Centralized configuration loader for the noncombat skills system.
    Supports validation, hot-reload, and cached access to configuration values.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure one config loader instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SkillConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.config_path = Path(__file__).parent.parent.parent.parent / "data" / "systems" / "character" / "skill_configurations.json"
        self._config_data = None
        self._last_loaded = None
        self._observer = None
        self._validation_schema = self._create_validation_schema()
        self._cache = {}
        self._cache_lock = threading.RLock()
        
        # Load initial configuration
        self.load_config()
        
        # Start file watcher for hot-reload
        self.start_hot_reload()
    
    def _create_validation_schema(self) -> Dict[str, Any]:
        """Create JSON schema for configuration validation."""
        return {
            "type": "object",
            "required": [
                "skill_check_difficulties",
                "environmental_modifiers", 
                "skill_synergies"
            ],
            "properties": {
                "skill_check_difficulties": {
                    "type": "object",
                    "properties": {
                        "trivial": {"type": "integer", "minimum": 1, "maximum": 50},
                        "easy": {"type": "integer", "minimum": 1, "maximum": 50},
                        "medium": {"type": "integer", "minimum": 1, "maximum": 50},
                        "hard": {"type": "integer", "minimum": 1, "maximum": 50},
                        "very_hard": {"type": "integer", "minimum": 1, "maximum": 50},
                        "nearly_impossible": {"type": "integer", "minimum": 1, "maximum": 50}
                    },
                    "required": ["trivial", "easy", "medium", "hard", "very_hard", "nearly_impossible"]
                },
                "environmental_modifiers": {
                    "type": "object",
                    "properties": {
                        "lighting": {"type": "object"},
                        "weather": {"type": "object"},
                        "terrain": {"type": "object"},
                        "sound": {"type": "object"}
                    }
                },
                "stealth_modifiers": {"type": "object"},
                "social_modifiers": {"type": "object"},
                "perception_modifiers": {"type": "object"},
                "skill_synergies": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-z_]+$": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "dc_calculations": {"type": "object"},
                "passive_skill_formulas": {"type": "object"},
                "group_check_mechanics": {"type": "object"},
                "extended_check_mechanics": {"type": "object"},
                "critical_success_failure": {"type": "object"},
                "contextual_bonuses": {"type": "object"},
                "skill_usage_limits": {"type": "object"},
                "xp_rewards": {"type": "object"}
            }
        }
    
    def load_config(self) -> bool:
        """Load configuration from file with validation."""
        try:
            if not self.config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Validate configuration
            self._validate_config(config_data)
            
            # Update configuration
            self._config_data = config_data
            self._last_loaded = datetime.now()
            
            # Clear cache
            with self._cache_lock:
                self._cache.clear()
            
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise ConfigurationError(f"Error loading configuration: {e}")
    
    def _validate_config(self, config_data: Dict[str, Any]) -> None:
        """Validate configuration against schema."""
        try:
            jsonschema.validate(config_data, self._validation_schema)
        except jsonschema.ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {e.message}")
    
    def reload_config(self) -> bool:
        """Reload configuration from file."""
        try:
            return self.load_config()
        except ConfigurationError as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def start_hot_reload(self) -> None:
        """Start file system watcher for hot-reload."""
        try:
            if self._observer is not None:
                self.stop_hot_reload()
            
            event_handler = ConfigFileHandler(self)
            self._observer = Observer()
            self._observer.schedule(event_handler, str(self.config_path.parent), recursive=False)
            self._observer.start()
            
            logger.info("Configuration hot-reload enabled")
        except Exception as e:
            logger.warning(f"Could not start configuration hot-reload: {e}")
    
    def stop_hot_reload(self) -> None:
        """Stop file system watcher."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("Configuration hot-reload disabled")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        if self._config_data is None:
            raise ConfigurationError("Configuration not loaded")
        return self._config_data.copy()
    
    def get_cached(self, cache_key: str, generator_func):
        """Get cached value or generate and cache it."""
        with self._cache_lock:
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            value = generator_func()
            self._cache[cache_key] = value
            return value
    
    # === SPECIFIC CONFIGURATION GETTERS ===
    
    def get_difficulty_dc(self, difficulty: str) -> int:
        """Get DC value for a difficulty level."""
        difficulties = self._config_data.get("skill_check_difficulties", {})
        if difficulty not in difficulties:
            raise ConfigurationError(f"Unknown difficulty level: {difficulty}")
        return difficulties[difficulty]
    
    def get_environmental_modifiers(self, category: str = None) -> Dict[str, Any]:
        """Get environmental modifiers, optionally filtered by category."""
        modifiers = self._config_data.get("environmental_modifiers", {})
        if category:
            return modifiers.get(category, {})
        return modifiers
    
    def get_stealth_modifiers(self, category: str = None) -> Dict[str, Any]:
        """Get stealth modifiers, optionally filtered by category."""
        modifiers = self._config_data.get("stealth_modifiers", {})
        if category:
            return modifiers.get(category, {})
        return modifiers
    
    def get_social_modifiers(self, category: str = None) -> Dict[str, Any]:
        """Get social modifiers, optionally filtered by category."""
        modifiers = self._config_data.get("social_modifiers", {})
        if category:
            return modifiers.get(category, {})
        return modifiers
    
    def get_perception_modifiers(self, category: str = None) -> Dict[str, Any]:
        """Get perception modifiers, optionally filtered by category."""
        modifiers = self._config_data.get("perception_modifiers", {})
        if category:
            return modifiers.get(category, {})
        return modifiers
    
    def get_skill_synergies(self, skill_name: str = None) -> Dict[str, List[str]]:
        """Get skill synergies, optionally for a specific skill."""
        synergies = self._config_data.get("skill_synergies", {})
        if skill_name:
            return synergies.get(skill_name, [])
        return synergies
    
    def get_dc_calculation_rules(self, calculation_type: str = None) -> Dict[str, Any]:
        """Get DC calculation rules."""
        rules = self._config_data.get("dc_calculations", {})
        if calculation_type:
            return rules.get(calculation_type, {})
        return rules
    
    def get_passive_skill_formulas(self) -> Dict[str, Any]:
        """Get passive skill calculation formulas."""
        return self._config_data.get("passive_skill_formulas", {})
    
    def get_group_check_mechanics(self) -> Dict[str, Any]:
        """Get group check mechanics configuration."""
        return self._config_data.get("group_check_mechanics", {})
    
    def get_extended_check_mechanics(self) -> Dict[str, Any]:
        """Get extended check mechanics configuration."""
        return self._config_data.get("extended_check_mechanics", {})
    
    def get_critical_effects(self) -> Dict[str, Any]:
        """Get critical success/failure effects configuration."""
        return self._config_data.get("critical_success_failure", {})
    
    def get_contextual_bonuses(self, category: str = None) -> Dict[str, Any]:
        """Get contextual bonuses configuration."""
        bonuses = self._config_data.get("contextual_bonuses", {})
        if category:
            return bonuses.get(category, {})
        return bonuses
    
    def get_skill_usage_limits(self) -> Dict[str, Any]:
        """Get skill usage limits configuration."""
        return self._config_data.get("skill_usage_limits", {})
    
    def get_xp_rewards(self) -> Dict[str, Any]:
        """Get XP rewards configuration."""
        return self._config_data.get("xp_rewards", {})
    
    def calculate_modifier_from_conditions(self, modifier_category: str, conditions: List[str]) -> int:
        """Calculate total modifier from a list of conditions."""
        cache_key = f"modifier_{modifier_category}_{hash(tuple(sorted(conditions)))}"
        
        def _calculate():
            total_modifier = 0
            category_modifiers = self.get_environmental_modifiers().get(modifier_category, {})
            
            for condition in conditions:
                if condition in category_modifiers:
                    total_modifier += category_modifiers[condition]
                else:
                    logger.warning(f"Unknown condition '{condition}' in category '{modifier_category}'")
            
            return total_modifier
        
        return self.get_cached(cache_key, _calculate)
    
    def get_status(self) -> Dict[str, Any]:
        """Get configuration loader status information."""
        return {
            "config_loaded": self._config_data is not None,
            "last_loaded": self._last_loaded.isoformat() if self._last_loaded else None,
            "config_path": str(self.config_path),
            "hot_reload_active": self._observer is not None and self._observer.is_alive(),
            "cache_size": len(self._cache)
        }

# Global configuration instance
skill_config = SkillConfigLoader()

# Convenience functions for common operations
def get_difficulty_dc(difficulty: str) -> int:
    """Get DC for a difficulty level."""
    return skill_config.get_difficulty_dc(difficulty)

def get_environmental_modifier(condition: str) -> int:
    """Get modifier for an environmental condition."""
    for category, modifiers in skill_config.get_environmental_modifiers().items():
        if condition in modifiers:
            return modifiers[condition]
    return 0

def get_skill_synergy_bonus(skill_name: str, character_skills: Dict[str, Any]) -> int:
    """Calculate synergy bonus for a skill based on character's other skills."""
    synergies = skill_config.get_skill_synergies(skill_name)
    bonus = 0
    
    for synergy_skill in synergies:
        skill_info = character_skills.get(synergy_skill, {})
        if skill_info.get("proficient", False):
            bonus += 2  # Standard synergy bonus
    
    return min(bonus, 10)  # Cap at +10

def validate_configuration_file(config_path: Optional[str] = None) -> bool:
    """Validate a configuration file without loading it into the main config."""
    try:
        path = Path(config_path) if config_path else skill_config.config_path
        
        with open(path, 'r') as f:
            config_data = json.load(f)
        
        loader = SkillConfigLoader()
        loader._validate_config(config_data)
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False 