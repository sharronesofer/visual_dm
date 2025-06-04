"""
Inventory utilities for managing equipment and items.
This module provides equipment-specific functionality that builds on the
canonical inventory system.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Import durability utilities
from backend.infrastructure.systems.equipment.utils.durability_utils import adjust_stats_for_durability, get_durability_status

# Import canonical inventory functionality if it exists
try:
    from backend.infrastructure.systems.inventory.models.inventory_utils import (
        calculate_total_weight,
        group_equipment_by_type,
        get_equipped_items as get_inventory_equipped_items
    )
    from backend.infrastructure.systems.inventory.models.inventory_validator import InventoryValidator
    HAS_INVENTORY_SYSTEM = True
except ImportError:
    HAS_INVENTORY_SYSTEM = False
    logger.warning("Canonical inventory system not available. Using fallback implementations.")

# Define exports based on what's available
if HAS_INVENTORY_SYSTEM:
    __all__ = [
        'calculate_total_weight',
        'group_equipment_by_type',
        'get_equipped_items',
        'load_equipment_rules',
        'calculate_carry_capacity',
        'can_equip_item',
        'get_equipment_stats',
        'get_item_details',
        'check_durability_requirements'
    ]
else:
    __all__ = [
        'load_equipment_rules',
        'calculate_carry_capacity',
        'can_equip_item',
        'get_equipment_stats',
        'get_item_details',
        'get_equipped_items',
        'check_durability_requirements'
    ]

def get_equipped_items(items: List) -> List:
    """
    Get list of currently equipped items.
    Uses canonical function if available, otherwise falls back to local implementation.
    
    Args:
        items: List of equipment items
        
    Returns:
        List of equipped items
    """
    if HAS_INVENTORY_SYSTEM:
        return get_inventory_equipped_items(items)
    
    # Fallback implementation if inventory system not available
    return [item for item in items if item.get('equipped', False)]

def load_equipment_rules() -> Dict:
    """
    Load equipment rules from JSON file.
    
    Returns:
        Dict containing equipment rules or default rules if file not found
    """
    try:
        rules_path = Path(__file__).parent / 'data' / 'equipment_rules.json'
        if rules_path.exists():
            with open(rules_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning("Equipment rules file not found")
            return _get_default_equipment_rules()
    except Exception as e:
        logger.error(f"Error loading equipment rules: {e}")
        return _get_default_equipment_rules()

def _get_default_equipment_rules() -> Dict:
    """
    Get default equipment rules.
    
    Returns:
        Dict containing default equipment rules
    """
    return {
        "weapon_types": {},
        "armor_types": {},
        "slot_limits": {
            "head": 1,
            "body": 1,
            "hands": 1,
            "feet": 1,
            "main_hand": 1,
            "off_hand": 1,
            "accessory": 2
        },
        "carry_capacity": {
            "base": 50,
            "per_strength": 10
        },
        "durability": {
            "min_equip_percentage": 10,  # Can't equip items below 10% durability
            "broken_threshold": 0         # Items are considered broken at 0 durability
        }
    }

def calculate_carry_capacity(strength: int) -> int:
    """
    Calculate character's carrying capacity based on strength.
    
    Args:
        strength: Character's strength stat
        
    Returns:
        Integer capacity value in weight units
    """
    rules = load_equipment_rules()
    base = rules['carry_capacity'].get('base', 50)
    per_str = rules['carry_capacity'].get('per_strength', 10)
    return base + (strength * per_str)

def check_durability_requirements(equipment: Dict) -> bool:
    """
    Check if an item meets durability requirements for equipping.
    
    Args:
        equipment: Equipment data with durability information
        
    Returns:
        True if the equipment meets durability requirements, False otherwise
    """
    rules = load_equipment_rules()
    
    # Get durability settings from rules
    min_equip_percentage = rules.get('durability', {}).get('min_equip_percentage', 10)
    
    # If the item is broken, it can't be equipped
    if equipment.get('is_broken', False):
        return False
    
    # Calculate durability percentage
    current_durability = equipment.get('current_durability', 100.0)
    max_durability = equipment.get('max_durability', 100.0)
    
    if max_durability <= 0:
        return False
        
    durability_percentage = (current_durability / max_durability) * 100.0
    
    # Check if durability is above the minimum requirement
    return durability_percentage >= min_equip_percentage

def can_equip_item(character: Dict, item: Dict) -> bool:
    """
    Check if character can equip an item based on equipment-specific rules.
    
    Args:
        character: Character data with stats and equipped items
        item: Item data with requirements and slot info
        
    Returns:
        True if the character can equip the item, False otherwise
    """
    rules = load_equipment_rules()
    
    # Check slot availability
    if 'slot' in item:
        slot = item['slot']
        if slot not in rules['slot_limits']:
            return False
            
        equipped_count = sum(1 for eq in character.get('equipped_items', [])
                           if eq.get('slot') == slot)
        if equipped_count >= rules['slot_limits'][slot]:
            return False
    
    # Check durability requirements
    if not check_durability_requirements(item):
        return False
            
    # Check requirements
    if 'requirements' in item:
        for stat, value in item['requirements'].items():
            if character.get('stats', {}).get(stat, 0) < value:
                return False
                
    return True

def get_equipment_stats(equipped_items: List[Dict]) -> Dict:
    """
    Calculate total stats from equipped items, accounting for durability.
    
    Args:
        equipped_items: List of equipped item objects
        
    Returns:
        Dictionary with combined stats from all equipped items
    """
    total_stats = {
        'armor_class': 10,
        'damage_bonus': 0,
        'weight': 0
    }
    
    for item in equipped_items:
        # Skip broken items
        if item.get('is_broken', False):
            continue
            
        # Get base item stats
        item_stats = {}
        if 'armor_class' in item:
            item_stats['armor_class'] = item['armor_class']
        if 'damage_bonus' in item:
            item_stats['damage_bonus'] = item['damage_bonus']
        if 'weight' in item:
            item_stats['weight'] = item['weight']
            
        # Adjust stats for durability
        adjusted_stats = adjust_stats_for_durability(item, item_stats)
        
        # Add adjusted stats to total
        for stat, value in adjusted_stats.items():
            if stat == 'armor_class':
                total_stats['armor_class'] = max(total_stats['armor_class'], value)
            elif stat in total_stats:
                total_stats[stat] += value
            else:
                total_stats[stat] = value
    
    # Add durability status information
    for item in equipped_items:
        slot = item.get('slot', '')
        if 'current_durability' in item and 'max_durability' in item:
            if 'durability_status' not in total_stats:
                total_stats['durability_status'] = {}
            
            status = get_durability_status(
                item.get('current_durability', 0), 
                item.get('max_durability', 100)
            )
            
            total_stats['durability_status'][slot] = {
                'status': status,
                'percentage': item.get('durability_percentage', 0)
            }
            
    return total_stats

def get_item_details(item_id: str) -> Optional[Dict]:
    """
    Get detailed information about an item from equipment rules.
    
    Args:
        item_id: ID of the item to look up
        
    Returns:
        Detailed item information or None if not found
    """
    rules = load_equipment_rules()
    
    # Check weapons
    if item_id in rules.get('weapon_types', {}):
        return {
            'id': item_id,
            'type': 'weapon',
            **rules['weapon_types'][item_id]
        }
        
    # Check armor
    if item_id in rules.get('armor_types', {}):
        return {
            'id': item_id,
            'type': 'armor',
            **rules['armor_types'][item_id]
        }
        
    return None 