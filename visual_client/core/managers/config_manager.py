"""
Configuration management system.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration settings."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            self.config_path = Path(config_path)
            self.config: Dict[str, Any] = {}
            self.defaults: Dict[str, Any] = {
                "app": {
                    "name": "Visual DM",
                    "version": "1.0.0",
                    "debug": False
                },
                "display": {
                    "width": 1280,
                    "height": 720,
                    "fullscreen": False,
                    "fps": 60,
                    "background_color": (40, 44, 52),
                    "text_color": (255, 255, 255),
                    "button_color": (70, 70, 70),
                    "button_hover_color": (90, 90, 90),
                    "button_active_color": (110, 110, 110),
                    "border_color": (100, 100, 100)
                },
                "audio": {
                    "enabled": True,
                    "music_volume": 0.7,
                    "sfx_volume": 1.0
                },
                "input": {
                    "mouse_sensitivity": 1.0,
                    "keyboard_repeat_delay": 500,
                    "keyboard_repeat_interval": 50
                },
                "network": {
                    "websocket_uri": "ws://localhost:8000/ws",
                    "api_base_url": "http://localhost:8000/api",
                    "reconnect_interval": 5,
                    "max_retries": 3
                },
                "storage": {
                    "save_dir": "saves",
                    "screenshot_dir": "screenshots",
                    "log_dir": "logs"
                }
            }
            
            # Load configuration
            self.load()
            
            logger.info("Configuration manager initialized")
            
        except Exception as e:
            handle_component_error(
                "ConfigManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def load(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                    
                # Convert color values from lists to tuples
                self._convert_color_values(self.config)
            else:
                # Use defaults if no config file exists
                self.config = self.defaults.copy()
                self.save()
                
            logger.info("Configuration loaded")
            
        except Exception as e:
            handle_component_error(
                "ConfigManager",
                "load",
                e,
                ErrorSeverity.ERROR
            )
            # Use defaults on error
            self.config = self.defaults.copy()
            
    def _convert_color_values(self, config: Dict[str, Any]) -> None:
        """Convert color values from lists to tuples recursively.
        
        Args:
            config: Configuration dictionary
        """
        for key, value in config.items():
            if isinstance(value, dict):
                self._convert_color_values(value)
            elif isinstance(value, list) and len(value) == 3 and all(isinstance(x, int) for x in value):
                config[key] = tuple(value)
            
    def save(self) -> None:
        """Save configuration to file."""
        try:
            # Convert color tuples to lists for JSON serialization
            config_copy = self._convert_tuples_to_lists(self.config.copy())
            
            with open(self.config_path, "w") as f:
                json.dump(config_copy, f, indent=4)
                
            logger.info("Configuration saved")
            
        except Exception as e:
            handle_component_error(
                "ConfigManager",
                "save",
                e,
                ErrorSeverity.ERROR
            )
            
    def _convert_tuples_to_lists(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert color tuples to lists for JSON serialization.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with tuples converted to lists
        """
        result = {}
        for key, value in config.items():
            if isinstance(value, dict):
                result[key] = self._convert_tuples_to_lists(value)
            elif isinstance(value, tuple):
                result[key] = list(value)
            else:
                result[key] = value
        return result
        
    def get_config(self) -> Dict[str, Any]:
        """Get complete configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        try:
            # Handle nested keys
            keys = key.split(".")
            value = self.config
            
            for k in keys:
                value = value.get(k)
                if value is None:
                    return default
                    
            return value
            
        except Exception as e:
            handle_component_error(
                "ConfigManager",
                "get",
                e,
                ErrorSeverity.ERROR,
                {"key": key}
            )
            return default
            
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Value to set
            save: Whether to save to file
        """
        try:
            # Handle nested keys
            keys = key.split(".")
            config = self.config
            
            # Navigate to the deepest dict
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
                
            # Convert color lists to tuples if needed
            if isinstance(value, list) and len(value) == 3 and all(isinstance(x, int) for x in value):
                value = tuple(value)
                
            # Set the value
            config[keys[-1]] = value
            
            if save:
                self.save()
                
            logger.debug(f"Configuration updated: {key} = {value}")
            
        except Exception as e:
            handle_component_error(
                "ConfigManager",
                "set",
                e,
                ErrorSeverity.ERROR,
                {"key": key, "value": value}
            )
            
    def reset(self, key: Optional[str] = None) -> None:
        """Reset configuration to defaults.
        
        Args:
            key: Specific key to reset (dot notation supported)
        """
        try:
            if key is None:
                # Reset all
                self.config = self.defaults.copy()
            else:
                # Reset specific key
                keys = key.split(".")
                config = self.config
                default = self.defaults
                
                # Navigate to the parent dict
                for k in keys[:-1]:
                    if k not in config:
                        config[k] = {}
                    if k not in default:
                        default[k] = {}
                    config = config[k]
                    default = default[k]
                    
                # Reset the value
                if keys[-1] in default:
                    config[keys[-1]] = default[keys[-1]]
                else:
                    del config[keys[-1]]
                    
            self.save()
            
        except Exception as e:
            handle_component_error(
                "ConfigManager",
                "reset",
                e,
                ErrorSeverity.ERROR,
                {"key": key}
            )
            
    def validate(self) -> bool:
        """Validate configuration against defaults.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            def _validate_dict(config: Dict[str, Any], defaults: Dict[str, Any]) -> bool:
                for key, value in defaults.items():
                    if key not in config:
                        return False
                    if isinstance(value, dict):
                        if not isinstance(config[key], dict):
                            return False
                        if not _validate_dict(config[key], value):
                            return False
                return True
                
            return _validate_dict(self.config, self.defaults)
            
        except Exception as e:
            handle_component_error(
                "ConfigManager",
                "validate",
                e,
                ErrorSeverity.ERROR
            )
            return False
            
    def cleanup(self) -> None:
        """Clean up configuration resources."""
        try:
            # Save any pending changes
            self.save()
            
            logger.info("Configuration manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "ConfigManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 