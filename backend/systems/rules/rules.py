"""
Core Rules Module
----------------
Game rules, balance constants, and data loading utilities.
Provides standardized game mechanics and balance values.
"""

from typing import Dict, Any, List, Optional
import json
import os
from pathlib import Path

# Balance Constants
balance_constants = {
    # Character Creation
    "starting_gold": 100,
    "starting_level": 1,
    "max_level": 20,
    "min_stat": 3,
    "max_stat": 20,
    "default_stat": 10,
    
    # Combat
    "base_ac": 10,
    "base_hp": 8,
    "base_speed": 30,
    "proficiency_bonus_progression": [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6],
    
    # Experience and Leveling
    "xp_thresholds": [
        0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
        85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
    ],
    
    # Racial Modifiers
    "racial_bonuses": {
        "human": {"all_stats": 1},
        "elf": {"dexterity": 2, "intelligence": 1},
        "dwarf": {"constitution": 2, "strength": 1},
        "halfling": {"dexterity": 2, "charisma": 1},
        "orc": {"strength": 2, "constitution": 1, "intelligence": -1},
        "gnome": {"intelligence": 2, "constitution": 1},
        "tiefling": {"charisma": 2, "intelligence": 1}
    },
    
    # Class Base Values
    "class_hit_dice": {
        "barbarian": 12,
        "fighter": 10,
        "paladin": 10,
        "ranger": 10,
        "bard": 8,
        "cleric": 8,
        "druid": 8,
        "monk": 8,
        "rogue": 8,
        "warlock": 8,
        "sorcerer": 6,
        "wizard": 6
    },
    
    # Equipment
    "equipment_weight_limits": {
        "light": 5,
        "medium": 15,
        "heavy": 25
    },
    
    # Currency
    "currency_conversion": {
        "copper": 1,
        "silver": 10,
        "electrum": 50,
        "gold": 100,
        "platinum": 1000
    }
}

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

def calculate_ability_modifier(ability_score: int) -> int:
    """
    Calculate ability modifier from ability score.
    
    Args:
        ability_score: The ability score (3-20)
    
    Returns:
        The ability modifier
    """
    return (ability_score - 10) // 2

def calculate_proficiency_bonus(level: int) -> int:
    """
    Calculate proficiency bonus for a given level.
    
    Args:
        level: Character level (1-20)
    
    Returns:
        Proficiency bonus
    """
    if level < 1:
        return 2
    if level > 20:
        return 6
    
    return balance_constants["proficiency_bonus_progression"][level - 1]

def calculate_hp_for_level(character_class: str, level: int, constitution_modifier: int) -> int:
    """
    Calculate hit points for a character at a given level.
    
    Args:
        character_class: Character class name
        level: Character level
        constitution_modifier: Constitution modifier
    
    Returns:
        Total hit points
    """
    hit_die = balance_constants["class_hit_dice"].get(character_class.lower(), 8)
    
    # First level: max hit die + con modifier
    if level == 1:
        return hit_die + constitution_modifier
    
    # Additional levels: average of hit die + con modifier per level
    average_hp_per_level = (hit_die // 2) + 1 + constitution_modifier
    additional_hp = (level - 1) * average_hp_per_level
    
    return hit_die + constitution_modifier + additional_hp

def get_starting_equipment(character_class: str, background: str = None) -> List[str]:
    """
    Get starting equipment for a character class and background.
    
    Args:
        character_class: Character class name
        background: Character background (optional)
    
    Returns:
        List of starting equipment
    """
    class_equipment = {
        "fighter": ["chain mail", "shield", "longsword", "light crossbow", "20 bolts"],
        "wizard": ["robes", "spellbook", "dagger", "component pouch"],
        "rogue": ["leather armor", "shortsword", "dagger", "thieves' tools"],
        "cleric": ["scale mail", "shield", "mace", "holy symbol"],
        "ranger": ["leather armor", "longbow", "20 arrows", "shortsword"],
        "barbarian": ["hide armor", "greataxe", "javelin", "explorer's pack"],
        "bard": ["leather armor", "rapier", "lute", "diplomat's pack"],
        "druid": ["leather armor", "scimitar", "shield", "druidcraft focus"],
        "monk": ["simple weapon", "monk's pack"],
        "paladin": ["chain mail", "shield", "longsword", "holy symbol"],
        "sorcerer": ["light crossbow", "component pouch", "dagger"],
        "warlock": ["light armor", "simple weapon", "arcane focus"]
    }
    
    equipment = class_equipment.get(character_class.lower(), ["basic equipment"])
    
    # Add background equipment
    if background:
        background_equipment = {
            "acolyte": ["holy symbol", "prayer book", "incense"],
            "criminal": ["crowbar", "dark clothes", "belt pouch"],
            "folk_hero": ["smith's tools", "artisan tools"],
            "noble": ["signet ring", "scroll of pedigree", "fine clothes"],
            "sage": ["ink", "quill", "small knife", "letter"],
            "soldier": ["rank insignia", "trophy", "playing cards"]
        }
        
        if background.lower() in background_equipment:
            equipment.extend(background_equipment[background.lower()])
    
    return equipment

__all__ = [
    "balance_constants",
    "load_data",
    "get_default_data",
    "calculate_ability_modifier",
    "calculate_proficiency_bonus", 
    "calculate_hp_for_level",
    "get_starting_equipment"
] 