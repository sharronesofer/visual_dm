"""Equipment Infrastructure Utilities

This module contains technical utilities for equipment operations.

Import directly from the specific utility modules:
- from backend.infrastructure.systems.equipment.utils.durability_utils import get_durability_status
- from backend.infrastructure.systems.equipment.utils.inventory_utils import get_equipped_items
- from backend.infrastructure.systems.equipment.utils.identify_item_utils import identify_item
- from backend.infrastructure.systems.equipment.utils.set_bonus_utils import calculate_set_bonuses
"""

# Note: No imports here to avoid circular dependencies
# Import directly from the specific modules as needed

__all__ = [
    # Durability utilities
    'get_durability_status',
    'calculate_combat_damage',
    'calculate_wear_damage',
    'apply_durability_damage',
    'calculate_repair_cost',
    'repair_equipment',
    'adjust_stats_for_durability',
    'get_durability_history',
    
    # Inventory utilities
    'get_equipped_items',
    'load_equipment_rules',
    'calculate_carry_capacity',
    'can_equip_item',
    'get_equipment_stats',
    'get_item_details',
    'check_durability_requirements',
    
    # Identification utilities
    'calculate_identification_cost',
    'identify_item',
    'fully_identify_item',
    'is_fully_identified',
    
    # Set bonus utilities
    'get_equipment_sets',
    'get_equipment_set',
    'get_item_set_membership',
    'calculate_set_bonuses',
    'apply_set_bonuses'
]
