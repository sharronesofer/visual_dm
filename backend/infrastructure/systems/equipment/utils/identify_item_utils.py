"""
Equipment item identification utility functions.

This module provides functions for identifying equipment items, calculating
identification costs, and managing the identification process.
"""

import logging
from typing import Dict, List, Optional, Any

# Keep same-system imports at the top
logger = logging.getLogger(__name__)

# Lazy imports: Move cross-system imports into functions to prevent circular dependencies
# from backend.systems.economy.models import EconomyEntity as Economy
# from backend.systems.faction.models import Faction

def calculate_identification_cost(item_data: Dict, region_name: Optional[str] = None, faction_id: Optional[int] = None) -> int:
    """
    Calculate the cost to identify an item based on various factors.
    
    Args:
        item_data: Dictionary containing item information
        region_name: Name of the region where identification is taking place
        faction_id: ID of the faction controlling the region (optional)
        
    Returns:
        int: The cost in gold pieces to identify the item
    """
    # Lazy imports to prevent circular dependencies
    from backend.infrastructure.database.economy.models import EconomyEntity as Economy
    from backend.systems.faction.models import Faction
    
    base_cost = 50  # Base identification cost
    
    # Factor in item rarity
    rarity = item_data.get('rarity', 'common')
    rarity_multipliers = {
        'common': 1.0,
        'uncommon': 1.5,
        'rare': 2.5,
        'epic': 4.0,
        'legendary': 6.0,
        'artifact': 10.0
    }
    cost = base_cost * rarity_multipliers.get(rarity, 1.0)
    
    # Factor in item level
    item_level = item_data.get('level', 1)
    cost += item_level * 5
    
    # Apply regional economy modifiers
    if region_name:
        try:
            economy = Economy.get_by_region(region_name)
            if economy:
                # Apply economy-based cost modifiers
                prosperity = economy.prosperity_level or 1.0
                cost *= (2.0 - prosperity)  # Higher prosperity = lower costs
                
                # Factor in supply and demand for identification services
                service_availability = economy.service_availability.get('identification', 1.0)
                cost *= (2.0 - service_availability)  # Higher availability = lower costs
        except Exception as e:
            logger.warning(f"Could not retrieve economy data for region {region_name}: {e}")
    
    # Apply faction-based modifiers
    if faction_id:
        try:
            faction = Faction.get_by_id(faction_id)
            if faction:
                # Faction relationship could affect prices
                # This would need player relationship data to calculate properly
                # For now, just apply a base faction modifier
                faction_modifier = faction.get_service_modifier('identification', default=1.0)
                cost *= faction_modifier
        except Exception as e:
            logger.warning(f"Could not retrieve faction data for faction {faction_id}: {e}")
    
    return max(int(cost), 10)  # Minimum cost of 10 gold


def identify_item(item: Dict, player_level: int) -> Dict:
    """
    Identify an item and reveal its properties based on player level.
    
    Args:
        item: Item dictionary to identify
        player_level: Level of the player attempting identification
        
    Returns:
        Dict: Updated item dictionary with revealed properties
    """
    # Lazy imports to prevent circular dependencies - none needed for this function
    
    identified_item = item.copy()
    
    # Base identification always reveals name and basic type
    if not identified_item.get('identified', False):
        identified_item['name'] = identified_item.get('true_name', 'Unknown Item')
        identified_item['type'] = identified_item.get('true_type', 'equipment')
        identified_item['identified'] = True
        identified_item['identification_level'] = 1
    
    # Higher level identification reveals more properties
    current_id_level = identified_item.get('identification_level', 0)
    
    # Level 2: Reveal basic stats and requirements
    if player_level >= 3 and current_id_level < 2:
        if 'hidden_stats' in identified_item:
            revealed_stats = identified_item.get('stats', {})
            revealed_stats.update(identified_item['hidden_stats'].get('basic', {}))
            identified_item['stats'] = revealed_stats
        
        if 'hidden_requirements' in identified_item:
            identified_item['requirements'] = identified_item['hidden_requirements']
        
        identified_item['identification_level'] = 2
    
    # Level 3: Reveal magical properties and enchantments
    if player_level >= 6 and current_id_level < 3:
        if 'hidden_enchantments' in identified_item:
            identified_item['enchantments'] = identified_item['hidden_enchantments']
        
        if 'hidden_stats' in identified_item:
            revealed_stats = identified_item.get('stats', {})
            revealed_stats.update(identified_item['hidden_stats'].get('magical', {}))
            identified_item['stats'] = revealed_stats
        
        identified_item['identification_level'] = 3
    
    # Level 4: Reveal special abilities and lore
    if player_level >= 10 and current_id_level < 4:
        if 'hidden_abilities' in identified_item:
            identified_item['special_abilities'] = identified_item['hidden_abilities']
        
        if 'hidden_lore' in identified_item:
            identified_item['lore'] = identified_item['hidden_lore']
        
        identified_item['identification_level'] = 4
    
    return identified_item


def fully_identify_item(item: Dict) -> Dict:
    """
    Fully identify an item, revealing all hidden properties.
    
    Args:
        item: Item dictionary to fully identify
        
    Returns:
        Dict: Fully identified item dictionary
    """
    # Lazy imports to prevent circular dependencies - none needed for this function
    
    identified_item = item.copy()
    
    # Reveal all hidden properties
    if 'true_name' in identified_item:
        identified_item['name'] = identified_item['true_name']
    
    if 'true_type' in identified_item:
        identified_item['type'] = identified_item['true_type']
    
    if 'hidden_stats' in identified_item:
        revealed_stats = identified_item.get('stats', {})
        for stat_category in identified_item['hidden_stats'].values():
            if isinstance(stat_category, dict):
                revealed_stats.update(stat_category)
        identified_item['stats'] = revealed_stats
    
    if 'hidden_requirements' in identified_item:
        identified_item['requirements'] = identified_item['hidden_requirements']
    
    if 'hidden_enchantments' in identified_item:
        identified_item['enchantments'] = identified_item['hidden_enchantments']
    
    if 'hidden_abilities' in identified_item:
        identified_item['special_abilities'] = identified_item['hidden_abilities']
    
    if 'hidden_lore' in identified_item:
        identified_item['lore'] = identified_item['hidden_lore']
    
    identified_item['identified'] = True
    identified_item['identification_level'] = 4
    
    return identified_item


def is_fully_identified(item: Dict) -> bool:
    """
    Check if an item is fully identified.
    
    Args:
        item: Item dictionary to check
        
    Returns:
        bool: True if the item is fully identified, False otherwise
    """
    # Lazy imports to prevent circular dependencies - none needed for this function
    
    # Check if item is marked as identified and has maximum identification level
    if not item.get('identified', False):
        return False
    
    identification_level = item.get('identification_level', 0)
    
    # Level 4 is considered fully identified
    if identification_level >= 4:
        return True
    
    # Also check if there are no more hidden properties to reveal
    has_hidden_properties = any([
        'hidden_stats' in item,
        'hidden_requirements' in item,
        'hidden_enchantments' in item,
        'hidden_abilities' in item,
        'hidden_lore' in item
    ])
    
    return not has_hidden_properties


def get_next_identifiable_level(item: Dict, player_level: int) -> Optional[int]:
    """
    Get the next identification level that can be achieved for an item.
    
    Args:
        item: Item dictionary to check
        player_level: Player's current level
        
    Returns:
        Optional[int]: Next identification level possible, or None if fully identified
    """
    # Lazy imports to prevent circular dependencies - none needed for this function
    
    current_level = item.get('identification_level', 0)
    
    # Determine what levels are available based on player level
    available_levels = []
    if player_level >= 1:
        available_levels.append(1)
    if player_level >= 3:
        available_levels.append(2)
    if player_level >= 6:
        available_levels.append(3)
    if player_level >= 10:
        available_levels.append(4)
    
    # Find the next level higher than current
    for level in available_levels:
        if level > current_level:
            return level
    
    return None


def reveal_item_name_and_flavor(item: Dict) -> str:
    """
    Generate a descriptive name and flavor text for an unidentified item.
    
    Args:
        item: Item dictionary
        
    Returns:
        str: Descriptive name and flavor text
    """
    # Lazy imports to prevent circular dependencies - none needed for this function
    
    if item.get('identified', False):
        return item.get('name', 'Unknown Item')
    
    # Generate generic description based on item type and visible properties
    item_type = item.get('type', 'item')
    rarity = item.get('rarity', 'common')
    
    # Base descriptions by type
    type_descriptions = {
        'weapon': 'weapon',
        'armor': 'piece of armor',
        'shield': 'shield',
        'accessory': 'ornament',
        'tool': 'tool',
        'consumable': 'item'
    }
    
    base_desc = type_descriptions.get(item_type, 'item')
    
    # Rarity-based adjectives
    rarity_adjectives = {
        'common': 'worn',
        'uncommon': 'well-crafted',
        'rare': 'exceptional',
        'epic': 'magnificent',
        'legendary': 'legendary',
        'artifact': 'ancient'
    }
    
    adjective = rarity_adjectives.get(rarity, 'mysterious')
    
    # Check for magical aura
    has_magic = any([
        'hidden_enchantments' in item,
        'hidden_abilities' in item,
        item.get('magical', False)
    ])
    
    if has_magic:
        return f"A {adjective} {base_desc} with a faint magical aura"
    else:
        return f"A {adjective} {base_desc}"

