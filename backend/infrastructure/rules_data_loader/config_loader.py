"""
Rules Configuration Loader Infrastructure
-----------------------------------------
Technical infrastructure for loading and managing rules configuration files.
Handles file I/O, JSON parsing, error handling, and caching.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Import infrastructure JSON utilities
from backend.infrastructure.utils.json_utils import load_json_safe
from backend.infrastructure.datautils import load_data, get_default_data


class RulesConfigError(Exception):
    """Custom exception for rules configuration loading errors"""
    pass


def load_json_config(filename: str, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load JSON configuration file with fallback to hardcoded data.
    
    Technical infrastructure function that handles:
    - File system operations
    - JSON parsing 
    - Error handling and logging
    - Fallback data management
    
    Args:
        filename: Name of the JSON file to load
        fallback_data: Fallback data if file doesn't exist
    
    Returns:
        Configuration dictionary
        
    Raises:
        RulesConfigError: If critical loading errors occur
    """
    try:
        # Try to load from data/systems/rules/ first (new location)
        config_path = Path("data/systems/rules") / filename
        if config_path.exists():
            return load_json_safe(str(config_path), fallback_data or {})
        
        # Fallback to infrastructure data loading
        try:
            return load_data(filename.replace('.json', ''), filename)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
            
    except Exception as e:
        print(f"Warning: Could not load {filename}: {e}")
    
    # Return fallback data or empty dict
    return fallback_data or {}


def reload_rules_config() -> None:
    """
    Reload all rules configuration files.
    
    Technical infrastructure function for reloading cached configuration.
    This would be called when configuration files change.
    """
    # Clear cache when implemented
    global _config_cache
    _config_cache.clear()


# Global config cache (for future optimization)
_config_cache: Dict[str, Dict[str, Any]] = {}


def get_cached_config(filename: str) -> Optional[Dict[str, Any]]:
    """
    Get cached configuration data.
    
    Technical infrastructure function for configuration caching.
    
    Args:
        filename: Configuration file name
        
    Returns:
        Cached configuration or None if not cached
    """
    return _config_cache.get(filename)


def cache_config(filename: str, config_data: Dict[str, Any]) -> None:
    """
    Cache configuration data.
    
    Technical infrastructure function for storing loaded configuration.
    
    Args:
        filename: Configuration file name
        config_data: Configuration data to cache
    """
    _config_cache[filename] = config_data 