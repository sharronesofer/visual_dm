"""
Item identification utility functions.
This module provides functionality for identifying magical items, 
revealing their properties progressively, and calculating costs.
"""

from typing import Dict, List, Optional, Any
import logging

# Import database functionality if it exists
try:
    from backend.core.database import db
    from backend.systems.economy.models import Economy
    from backend.systems.faction.models import Faction
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False

logger = logging.getLogger(__name__)

# Rarity multipliers for identification cost
RARITY_MULTIPLIER = {
    "common": 1.0,
    "uncommon": 1.25,
    "rare": 1.5,
    "epic": 2.0,
    "legendary": 4.0
}

def calculate_identification_cost(item_data: Dict, region_name: Optional[str] = None, faction_id: Optional[int] = None) -> int:
    """
    Calculate the cost to identify one unknown effect on an item.
    Cost = base × rarity × regional economic modifier × faction discount
    
    Args:
        item_data: Dictionary containing item properties
        region_name: Optional region name for economic modifiers
        faction_id: Optional faction ID for discounts
        
    Returns:
        Integer cost in gold
    """
    rarity = item_data.get("rarity", "common").lower()
    base_cost = 20 * len(item_data.get("unknown_effects", []))
    multiplier = RARITY_MULTIPLIER.get(rarity, 1.0)

    economic_mod = 1.0
    if region_name and HAS_DATABASE:
        try:
            # Get economic modifier from region
            economic_data = Economy.query.filter_by(region=region_name).first()
            if economic_data:
                economic_mod = economic_data.modifier
        except Exception as e:
            logger.warning(f"Error getting economic data: {e}")

    faction_discount = 1.0
    if faction_id and HAS_DATABASE:
        try:
            # Check if faction gives identification discount
            faction_data = Faction.query.filter_by(id=faction_id).first()
            if faction_data and faction_data.type == "mage":
                faction_discount = 0.85  # Mage Guild discount
        except Exception as e:
            logger.warning(f"Error getting faction data: {e}")

    return int(base_cost * multiplier * economic_mod * faction_discount)

def identify_item(item: Dict, player_level: int) -> Dict:
    """
    Identify an item based on player level, revealing effects
    that require a level less than or equal to the player's level.
    
    Args:
        item: Dictionary containing item data
        player_level: Integer representing player's level
        
    Returns:
        Updated item dictionary with newly identified effects
    """
    effects = item.get("effects", [])
    known = set(item.get("identified_levels", []))
    
    # Find effects that can be identified based on player level
    new_levels = sorted(e["level"] for e in effects 
                      if e["level"] <= player_level and e["level"] not in known)
    
    if not new_levels:
        return item
        
    # Add newly identified levels
    item.setdefault("identified_levels", []).extend(new_levels)
    
    return item

def fully_identify_item(item: Dict) -> Dict:
    """
    Fully identify all effects on an item, regardless of level requirements.
    
    Args:
        item: Dictionary containing item data
        
    Returns:
        Updated item dictionary with all effects identified
    """
    effects = item.get("effects", [])
    all_levels = [e["level"] for e in effects]
    item["identified_levels"] = list(sorted(set(all_levels)))
    item["is_identified"] = True
    return item

def is_fully_identified(item: Dict) -> bool:
    """
    Check if an item is fully identified.
    
    Args:
        item: Dictionary containing item data
        
    Returns:
        Boolean indicating if all effects are identified
    """
    # Check if item has the is_identified flag
    if item.get("is_identified", False):
        return True
        
    # Otherwise check if all effect levels are known
    levels = set(e["level"] for e in item.get("effects", []))
    known = set(item.get("identified_levels", []))
    return levels.issubset(known)

def get_next_identifiable_level(item: Dict, player_level: int) -> Optional[int]:
    """
    Get the next level of effects that can be identified.
    
    Args:
        item: Dictionary containing item data
        player_level: Integer representing player's level
        
    Returns:
        Next identifiable level or None if none available
    """
    effects = item.get("effects", [])
    known = set(item.get("identified_levels", []))
    
    # Find levels that can be identified based on player level
    new_levels = sorted([e["level"] for e in effects 
                      if e["level"] <= player_level and e["level"] not in known])
    
    return new_levels[0] if new_levels else None

def reveal_item_name_and_flavor(item: Dict) -> str:
    """
    Reveals generated item name and flavor, stores it for narrative delivery.
    Only runs once per item.
    
    Args:
        item: Dictionary containing item data
        
    Returns:
        Flavor text string for the item
    """
    if not item.get("name_revealed", False):
        item["name_revealed"] = True
        item["identified_name"] = item.get("generated_name", item.get("name", "Unnamed Item"))
        item["reveal_flavor"] = item.get("flavor_text", "It gives off a subtle magical hum...")

    return item.get("reveal_flavor", "")

