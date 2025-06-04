"""
Game Data Loading Utilities
---------------------------
Technical utilities for loading and managing game data files.
Provides standardized data loading and default structure handling.
"""

from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

def load_data(data_type: str, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Load game data from JSON files.
    
    Args:
        data_type: Type of data to load (e.g., 'spells', 'items', 'monsters')
        filename: Optional specific filename to load
    
    Returns:
        Dictionary containing the loaded data
    """
    if filename is None:
        filename = f"{data_type}.json"
    
    # Look for data files in multiple locations
    search_paths = [
        f"data/{filename}",
        f"data/system/validation/{filename}",
        f"data/builders/schemas/{filename}",
        f"data/system/runtime/{filename}",
        f"data/system/runtime/rules/{filename}",
        f"data/system/runtime/game/{filename}"
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError, IOError):
                continue
    
    # Return default empty data structure if file not found
    return get_default_data(data_type)

def get_default_data(data_type: str) -> Dict[str, Any]:
    """
    Get default data structure for various data types.
    
    Args:
        data_type: Type of data to get defaults for
    
    Returns:
        Default data structure
    """
    defaults = {
        "spells": {
            "cantrips": [],
            "level_1": [],
            "level_2": [],
            "level_3": [],
            "level_4": [],
            "level_5": [],
            "level_6": [],
            "level_7": [],
            "level_8": [],
            "level_9": []
        },
        "items": {
            "weapons": [],
            "armor": [],
            "tools": [],
            "consumables": [],
            "treasures": []
        },
        "monsters": {
            "cr_0": [],
            "cr_1": [],
            "cr_2": [],
            "cr_3": [],
            "cr_4": [],
            "cr_5": []
        },
        "classes": {
            "barbarian": {"hit_die": 12, "primary_ability": "strength"},
            "bard": {"hit_die": 8, "primary_ability": "charisma"},
            "cleric": {"hit_die": 8, "primary_ability": "wisdom"},
            "druid": {"hit_die": 8, "primary_ability": "wisdom"},
            "fighter": {"hit_die": 10, "primary_ability": "strength"},
            "monk": {"hit_die": 8, "primary_ability": "dexterity"},
            "paladin": {"hit_die": 10, "primary_ability": "strength"},
            "ranger": {"hit_die": 10, "primary_ability": "dexterity"},
            "rogue": {"hit_die": 8, "primary_ability": "dexterity"},
            "sorcerer": {"hit_die": 6, "primary_ability": "charisma"},
            "warlock": {"hit_die": 8, "primary_ability": "charisma"},
            "wizard": {"hit_die": 6, "primary_ability": "intelligence"}
        },
        "races": {
            "human": {"size": "medium", "speed": 30, "languages": ["Common"]},
            "elf": {"size": "medium", "speed": 30, "languages": ["Common", "Elvish"]},
            "dwarf": {"size": "medium", "speed": 25, "languages": ["Common", "Dwarvish"]},
            "halfling": {"size": "small", "speed": 25, "languages": ["Common", "Halfling"]},
            "orc": {"size": "medium", "speed": 30, "languages": ["Common", "Orcish"]},
            "gnome": {"size": "small", "speed": 25, "languages": ["Common", "Gnomish"]},
            "tiefling": {"size": "medium", "speed": 30, "languages": ["Common", "Infernal"]}
        }
    }
    
    return defaults.get(data_type, {})

__all__ = [
    "load_data",
    "get_default_data"
] 