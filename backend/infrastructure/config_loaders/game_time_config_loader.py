"""
Configuration Loader for the Time System

Loads and manages JSON configuration files for the time system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from backend.systems.game_time.models.time_model import TimeConfig, Season

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Loads and manages configuration for the time system.
    
    Handles loading from JSON files and provides easy access to configuration values.
    """
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # Default to the config file in the data directory
            # Navigate up from backend/infrastructure/config_loaders/ to project root, then to data
            project_root = Path(__file__).parent.parent.parent.parent
            config_file = project_root / "data" / "systems" / "game_time" / "time_system_config.json"
        
        self.config_file = Path(config_file)
        self._config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            if not self.config_file.exists():
                logger.warning(f"Config file not found: {self.config_file}, using defaults")
                self._config_data = self._get_default_config()
                return
            
            with open(self.config_file, 'r') as f:
                self._config_data = json.load(f)
            
            logger.info(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load config file: {e}, using defaults")
            self._config_data = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "time_progression": {
                "real_seconds_per_game_hour": 60.0,
                "ticks_per_second": 10,
                "default_time_scale": 1.0,
                "auto_save_interval_seconds": 300
            },
            "calendar": {
                "days_per_month": 30,
                "months_per_year": 12,
                "hours_per_day": 24,
                "minutes_per_hour": 60,
                "has_leap_year": True,
                "leap_year_interval": 4,
                "season_boundaries": {
                    "winter_end_day": 90,
                    "spring_end_day": 180,
                    "summer_end_day": 270,
                    "autumn_end_day": 360
                }
            },
            "weather": {
                "enabled": True,
                "change_frequency_hours": 6,
                "seasonal_influence": 0.7,
                "randomness_factor": 0.3
            },
            "events": {
                "enable_seasonal_events": True,
                "default_event_priority": 0
            },
            "system": {
                "save_directory": "data/game_time",
                "backup_retention_count": 10
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration value (e.g., 'weather.enabled')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config_data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logger.warning(f"Configuration key '{key_path}' not found, using default: {default}")
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name (e.g., 'weather', 'calendar')
            
        Returns:
            Dictionary containing the section data
        """
        return self._config_data.get(section, {})
    
    def create_time_config(self) -> TimeConfig:
        """
        Create a TimeConfig object from the loaded configuration.
        
        Returns:
            TimeConfig object with values from configuration
        """
        time_config = TimeConfig(
            real_seconds_per_game_hour=self.get("time_progression.real_seconds_per_game_hour", 60.0),
            ticks_per_second=self.get("time_progression.ticks_per_second", 10),
            time_scale=self.get("time_progression.default_time_scale", 1.0),
            enable_seasonal_events=self.get("events.enable_seasonal_events", True),
            enable_weather_system=self.get("weather.enabled", True),
            weather_change_frequency_hours=self.get("weather.change_frequency_hours", 6),
            weather_seasonal_influence=self.get("weather.seasonal_influence", 0.7),
            weather_randomness=self.get("weather.randomness_factor", 0.3),
            auto_save_interval=self.get("time_progression.auto_save_interval_seconds", 300)
        )
        
        return time_config
    
    def get_weather_probabilities(self, season: Season) -> Dict[str, float]:
        """
        Get weather probabilities for a specific season.
        
        Args:
            season: Season to get probabilities for
            
        Returns:
            Dictionary mapping weather conditions to probabilities
        """
        season_name = season.value.lower()
        if season_name == "autumn":
            season_name = "autumn"  # Handle potential FALL alias
        
        probabilities = self.get(f"weather.seasonal_probabilities.{season_name}", {})
        
        # Provide fallback defaults if not found
        if not probabilities:
            logger.warning(f"No weather probabilities found for season {season_name}, using defaults")
            probabilities = {
                "clear": 0.3,
                "partly_cloudy": 0.25,
                "cloudy": 0.2,
                "rain": 0.15,
                "fog": 0.1
            }
        
        return probabilities
    
    def get_temperature_range(self, season: Season) -> tuple[float, float]:
        """
        Get temperature range for a specific season.
        
        Args:
            season: Season to get temperature range for
            
        Returns:
            Tuple of (min_temp, max_temp)
        """
        season_name = season.value.lower()
        if season_name == "autumn":
            season_name = "autumn"  # Handle potential FALL alias
        
        temp_range = self.get(f"weather.temperature_ranges.{season_name}", {})
        
        if not temp_range:
            logger.warning(f"No temperature range found for season {season_name}, using defaults")
            return (40.0, 80.0)  # Default range
        
        return (temp_range.get("min", 40.0), temp_range.get("max", 80.0))
    
    def get_weather_condition_modifier(self, condition: str, modifier_type: str) -> float:
        """
        Get a weather condition modifier.
        
        Args:
            condition: Weather condition name
            modifier_type: Type of modifier ('temperature_adjustments', 'duration_modifiers')
            
        Returns:
            Modifier value or 0.0 if not found
        """
        return self.get(f"weather.condition_modifiers.{modifier_type}.{condition}", 0.0)
    
    def get_season_boundaries(self) -> Dict[str, int]:
        """
        Get season boundary configuration.
        
        Returns:
            Dictionary mapping season end names to day numbers
        """
        return self.get("calendar.season_boundaries", {
            "winter_end_day": 90,
            "spring_end_day": 180,
            "summer_end_day": 270,
            "autumn_end_day": 360
        })
    
    def get_calendar_config(self) -> Dict[str, Any]:
        """
        Get calendar configuration.
        
        Returns:
            Dictionary with calendar settings
        """
        return self.get_section("calendar")
    
    def reload_config(self) -> bool:
        """
        Reload configuration from file.
        
        Returns:
            True if reload was successful
        """
        try:
            self._load_config()
            logger.info("Configuration reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def save_config(self, config_data: Dict[str, Any] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config_data: Configuration data to save (uses current data if None)
            
        Returns:
            True if save was successful
        """
        try:
            data_to_save = config_data if config_data is not None else self._config_data
            
            with open(self.config_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """
        Validate the current configuration and return any issues found.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate time progression settings
        if self.get("time_progression.real_seconds_per_game_hour", 0) <= 0:
            errors.append("time_progression.real_seconds_per_game_hour must be positive")
        
        if self.get("time_progression.ticks_per_second", 0) <= 0:
            errors.append("time_progression.ticks_per_second must be positive")
        
        # Validate calendar settings
        if self.get("calendar.days_per_month", 0) <= 0:
            errors.append("calendar.days_per_month must be positive")
        
        if self.get("calendar.months_per_year", 0) <= 0:
            errors.append("calendar.months_per_year must be positive")
        
        # Validate weather probabilities sum to approximately 1.0 for each season
        for season in ["spring", "summer", "autumn", "winter"]:
            probs = self.get(f"weather.seasonal_probabilities.{season}", {})
            if probs:
                prob_sum = sum(probs.values())
                if abs(prob_sum - 1.0) > 0.1:  # Allow 10% tolerance
                    errors.append(f"Weather probabilities for {season} sum to {prob_sum:.2f}, should be ~1.0")
        
        return errors


# Global configuration instance
_global_config: Optional[ConfigLoader] = None


def get_config() -> ConfigLoader:
    """
    Get the global configuration instance.
    
    Returns:
        ConfigLoader instance
    """
    global _global_config
    if _global_config is None:
        _global_config = ConfigLoader()
    return _global_config


def reload_global_config() -> bool:
    """
    Reload the global configuration.
    
    Returns:
        True if reload was successful
    """
    global _global_config
    if _global_config is not None:
        return _global_config.reload_config()
    else:
        _global_config = ConfigLoader()
        return True 