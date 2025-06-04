"""
Arc System Utilities

Utilities for loading and managing arc system configuration.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

def get_config_path() -> Path:
    """Get the path to arc system configuration directory."""
    return Path(__file__).parent.parent.parent.parent.parent / "data" / "system" / "config" / "arc"

def load_business_rules() -> Dict[str, Any]:
    """Load business rules configuration from JSON."""
    config_path = get_config_path() / "arc_business_rules.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Business rules configuration not found at {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)

def load_system_config() -> Dict[str, Any]:
    """Load system configuration from JSON."""
    config_path = get_config_path() / "system_config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"System configuration not found at {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)

def get_arc_type_rules(arc_type: str) -> Optional[Dict[str, Any]]:
    """Get business rules for a specific arc type."""
    rules = load_business_rules()
    return rules.get("arc_type_rules", {}).get(arc_type)

def get_system_limits() -> Dict[str, Any]:
    """Get system limits configuration."""
    config = load_system_config()
    return config.get("system_limits", {})

def get_system_defaults() -> Dict[str, Any]:
    """Get system default values."""
    config = load_system_config()
    return config.get("system_defaults", {})

__all__ = [
    'load_business_rules',
    'load_system_config', 
    'get_arc_type_rules',
    'get_system_limits',
    'get_system_defaults'
] 