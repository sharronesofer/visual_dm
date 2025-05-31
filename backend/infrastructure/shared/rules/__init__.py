"""
Shared rules module for backend systems.
Contains game rules, calculations, and utility functions.
"""

import json
import os
from typing import Dict, Any

# Default balance constants
DEFAULT_BALANCE_CONSTANTS = {
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

def load_data(filename: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        filename: Name of the file to load
        
    Returns:
        Dictionary containing the loaded data
    """
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
    Get balance constants, loading from file if available.
    
    Returns:
        Dictionary containing balance constants
    """
    # Try to load from file first
    file_constants = load_data("balance_constants.json")
    
    # Merge with defaults
    constants = DEFAULT_BALANCE_CONSTANTS.copy()
    constants.update(file_constants)
    
    return constants

# Create the balance_constants object
balance_constants = get_balance_constants()

__all__ = [
    "balance_constants",
    "load_data",
    "get_balance_constants",
    "DEFAULT_BALANCE_CONSTANTS"
]
