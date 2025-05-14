"""
Utility functions for inventory management.
"""

from typing import Dict, List, Optional
from ..models.character import Character
from ..models.item import Item

def group_equipment_by_type(items: List[Item]) -> Dict[str, List[Item]]:
    """
    Group equipment items by their type.
    
    Args:
        items: List of equipment items
        
    Returns:
        Dictionary with equipment types as keys and lists of items as values
    """
    grouped = {}
    
    for item in items:
        if item.type not in grouped:
            grouped[item.type] = []
        grouped[item.type].append(item)
        
    # Sort items within each category
    for category in grouped:
        grouped[category].sort(key=lambda x: x.name)
        
    return grouped

def calculate_total_weight(items: List[Item]) -> float:
    """
    Calculate total weight of all equipment.
    
    Args:
        items: List of equipment items
        
    Returns:
        Total weight in pounds
    """
    return sum(item.weight * item.quantity for item in items)

def get_equipped_items(items: List[Item]) -> List[Item]:
    """
    Get list of currently equipped items.
    
    Args:
        items: List of equipment items
        
    Returns:
        List of equipped items
    """
    return [item for item in items if item.is_equipped]

def can_equip_item(character: Character, item: Item) -> Dict[str, bool]:
    """
    Check if a character can equip an item.
    
    Args:
        character: Character attempting to equip
        item: Item to equip
        
    Returns:
        Dictionary with requirements and whether they are met
    """
    result = {
        "meets_proficiency": True,
        "meets_ability_score": True,
        "meets_level": True,
        "can_equip": True
    }
    
    # Check proficiency requirements
    if item.type in ["weapon", "armor"]:
        if item.name not in character.weapon_proficiencies and item.name not in character.armor_proficiencies:
            result["meets_proficiency"] = False
            
    # Check ability score requirements
    if item.ability_requirements:
        for ability, score in item.ability_requirements.items():
            if character.ability_scores[ability] < score:
                result["meets_ability_score"] = False
                break
                
    # Check level requirements
    if item.level_requirement and character.level < item.level_requirement:
        result["meets_level"] = False
        
    # Overall result
    result["can_equip"] = all([
        result["meets_proficiency"],
        result["meets_ability_score"],
        result["meets_level"]
    ])
    
    return result 