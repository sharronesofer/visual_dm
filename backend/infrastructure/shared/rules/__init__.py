"""
Shared rules module for backend systems.
Contains game rules, calculations, and utility functions.

DEPRECATED: This module is being phased out in favor of the canonical rules system.
Use backend.systems.rules.rules instead for all new code.
"""

import json
import os
from typing import Dict, Any
import warnings

def load_data(filename: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    DEPRECATED: Use backend.systems.rules.rules.load_data instead.
    
    Args:
        filename: Name of the file to load
        
    Returns:
        Dictionary containing the loaded data
    """
    warnings.warn(
        "backend.infrastructure.shared.rules.load_data is deprecated. "
        "Use backend.systems.rules.rules.load_data instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    try:
        # Try to load from data directory
        data_path = os.path.join("data", filename)
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                return json.load(f)
        
        # Try to load from current directory
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        
        # Return empty dict if file not found
        return {}
    except Exception:
        return {}

def get_balance_constants() -> Dict[str, Any]:
    """
    Get balance constants from the canonical rules system.
    
    DEPRECATED: Use backend.systems.rules.rules.balance_constants directly.
    
    Returns:
        Dictionary containing balance constants
    """
    warnings.warn(
        "backend.infrastructure.shared.rules.get_balance_constants is deprecated. "
        "Use backend.systems.rules.rules.balance_constants directly.",
        DeprecationWarning,
        stacklevel=2
    )
    
    try:
        # Import the canonical rules system
        from backend.systems.rules.rules import balance_constants as canonical_constants
        return canonical_constants
    except ImportError:
        # Fallback to local constants if canonical system unavailable
        return _get_fallback_constants()

def _get_fallback_constants() -> Dict[str, Any]:
    """Fallback constants if canonical system is unavailable."""
    return {
        "starting_gold": 100,
        "starting_health": 100,
        "starting_mana": 50,
        "level_up_health_gain": 10,
        "level_up_mana_gain": 5,
        "max_level": 20,
        "experience_per_level": 1000,
        "attribute_point_cost": 1,
        "skill_point_cost": 1,
        "equipment_durability_loss_rate": 0.1,
        "rest_health_recovery": 0.5,
        "rest_mana_recovery": 0.8
    }

# Create the balance_constants object that delegates to canonical system
try:
    from backend.systems.rules.rules import balance_constants as _canonical_constants
    balance_constants = _canonical_constants
except ImportError:
    # Fallback if canonical system not available
    balance_constants = _get_fallback_constants()

# Legacy alias for backward compatibility
DEFAULT_BALANCE_CONSTANTS = _get_fallback_constants()

__all__ = [
    "balance_constants",
    "load_data", 
    "get_balance_constants",
    "DEFAULT_BALANCE_CONSTANTS"
]
