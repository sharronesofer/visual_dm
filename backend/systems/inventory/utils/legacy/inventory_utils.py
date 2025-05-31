"""
Inventory utilities for managing equipment and items.
All inventory and equipment operations should use the canonical Inventory/InventoryItem models and services.
Legacy direct field logic has been removed.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_equipment_rules() -> Dict:
    """Load equipment rules from JSON file (for reference only; canonical inventory logic is in Inventory/InventoryItem models)."""
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
    """Get default equipment rules (for reference only)."""
    return {
        "weapon_types": {},
        "armor_types": {},
        "slot_limits": {},
        "carry_capacity": {}
    }

# All legacy direct inventory/equipment logic has been removed.
# Use InventoryService and Inventory/InventoryItem models for all operations.

def calculate_carry_capacity(strength: int) -> int:
    """Calculate character's carrying capacity."""
    rules = load_equipment_rules()
    base = rules['carry_capacity']['base']
    per_str = rules['carry_capacity']['per_strength']
    return base + (strength * per_str)

def can_equip_item(character: Dict, item: Dict) -> bool:
    """Check if character can equip an item."""
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
            
    # Check requirements
    if 'requirements' in item:
        for stat, value in item['requirements'].items():
            if character.get('stats', {}).get(stat, 0) < value:
                return False
                
    return True

def get_equipment_stats(equipped_items: List[Dict]) -> Dict:
    """Calculate total stats from equipped items."""
    total_stats = {
        'armor_class': 10,
        'damage_bonus': 0,
        'weight': 0
    }
    
    for item in equipped_items:
        if 'armor_class' in item:
            total_stats['armor_class'] = max(total_stats['armor_class'], item['armor_class'])
        if 'damage_bonus' in item:
            total_stats['damage_bonus'] += item['damage_bonus']
        if 'weight' in item:
            total_stats['weight'] += item['weight']
            
    return total_stats

def get_item_details(item_id: str) -> Optional[Dict]:
    """Get detailed information about an item."""
    rules = load_equipment_rules()
    
    # Check weapons
    if item_id in rules['weapon_types']:
        return {
            'id': item_id,
            'type': 'weapon',
            **rules['weapon_types'][item_id]
        }
        
    # Check armor
    if item_id in rules['armor_types']:
        return {
            'id': item_id,
            'type': 'armor',
            **rules['armor_types'][item_id]
        }
        
    return None 
