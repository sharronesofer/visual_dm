"""
Generic JSON Configuration Loader

Provides technical utilities for loading and saving JSON configuration files.
Extracted from world generation system configuration managers.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class JsonConfigLoader:
    """Generic JSON configuration loader with error handling and defaults."""
    
    def __init__(self, config_path: str, default_config: Dict[str, Any] = None):
        """
        Initialize the JSON config loader.
        
        Args:
            config_path: Path to the JSON configuration file
            default_config: Default configuration to use if file loading fails
        """
        self.config_path = Path(config_path)
        self.default_config = default_config or {}
        self._cached_config = None
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load configuration from JSON file with error handling.
        
        Args:
            force_reload: Force reload even if config is cached
            
        Returns:
            Configuration dictionary
        """
        if self._cached_config is not None and not force_reload:
            return self._cached_config
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._cached_config = json.load(f)
                    return self._cached_config
            else:
                print(f"Warning: Configuration file not found at {self.config_path}")
                self._cached_config = self.default_config.copy()
                return self._cached_config
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file {self.config_path}: {e}")
            self._cached_config = self.default_config.copy()
            return self._cached_config
        except Exception as e:
            print(f"Warning: Could not load configuration from {self.config_path}: {e}")
            self._cached_config = self.default_config.copy()
            return self._cached_config
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Save configuration to JSON file.
        
        Args:
            config_data: Configuration data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # Update cache
            self._cached_config = config_data.copy()
            return True
        except Exception as e:
            print(f"Error: Could not save configuration to {self.config_path}: {e}")
            return False
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value (e.g., "section.subsection.key")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        config = self.load_config()
        
        try:
            keys = key_path.split('.')
            value = config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config_value(self, key_path: str, value: Any) -> bool:
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        config = self.load_config()
        
        try:
            keys = key_path.split('.')
            current = config
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set the final value
            current[keys[-1]] = value
            
            return self.save_config(config)
        except Exception as e:
            print(f"Error: Could not set configuration value {key_path}: {e}")
            return False
    
    def reload_config(self):
        """Force reload configuration from file."""
        self._cached_config = None
        self.load_config()
    
    def get_file_path(self) -> Path:
        """Get the configuration file path."""
        return self.config_path 