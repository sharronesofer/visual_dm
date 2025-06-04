"""
Shared utility functions for the loot system.

This module contains functions that were previously duplicated across multiple files.
Centralizing them here reduces maintenance burden and ensures consistency.
"""

from typing import Dict, List, Any, Tuple
import random
from copy import deepcopy


def group_equipment_by_type(equipment_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorizes equipment items into armor, weapon, and gear pools.
    
    Args:
        equipment_list: List of equipment items
        
    Returns:
        Dictionary with equipment items organized by category
    """
    pool = {"armor": [], "weapon": [], "gear": []}
    for item in equipment_list:
        category = item.get("category")
        if category in pool:
            pool[category].append(item)
        elif category in ["melee", "ranged"]:
            pool["weapon"].append(item)
    return pool


def gpt_name_and_flavor(base_type: str = "item") -> Tuple[str, str]:
    """Generate AI-powered names and flavor text for epic/legendary items"""
    try:
        from backend.infrastructure.llm.llm_service import get_llm_service
        
        llm_service = get_llm_service()
        
        prompt = f"""Generate a creative fantasy name and flavor text for a {base_type}.
        
Requirements:
- Name should be 2-4 words, evocative and memorable
- Flavor text should be 1-2 sentences describing the item's history or powers
- Style should match epic fantasy (D&D, Lord of the Rings)
- Avoid generic or boring names

Format response as:
NAME: [item name]
FLAVOR: [flavor text]

Example:
NAME: Shadowbane's Whisper
FLAVOR: This blade once belonged to a legendary demon hunter, its edge forever stained with the essence of vanquished shadows.
"""
        
        response = llm_service.generate_text(
            prompt=prompt,
            max_tokens=150,
            temperature=0.8
        )
        
        # Parse the response
        lines = response.strip().split('\n')
        name = "Unnamed Item"
        flavor = "An item of mysterious origin."
        
        for line in lines:
            if line.startswith("NAME:"):
                name = line.replace("NAME:", "").strip()
            elif line.startswith("FLAVOR:"):
                flavor = line.replace("FLAVOR:", "").strip()
        
        return name, flavor
        
    except Exception as e:
        logger.error(f"Failed to generate AI name/flavor: {e}")
        # Fallback to generic naming
        return f"Enchanted {base_type.title()}", f"A {base_type} imbued with magical properties."


def merge_loot_sets(loot_sets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merges multiple loot sets into a single consolidated set.
    
    Args:
        loot_sets: List of loot sets to merge
        
    Returns:
        Merged loot set with combined gold and equipment
    """
    if not loot_sets:
        return {"gold": 0, "equipment": [], "quest_item": None, "magical_item": None}
    
    merged_loot = {
        "gold": 0,
        "equipment": [],
        "quest_item": None,
        "magical_item": None
    }
    
    for loot_set in loot_sets:
        # Combine gold
        merged_loot["gold"] += loot_set.get("gold", 0)
        
        # Combine equipment
        merged_loot["equipment"].extend(loot_set.get("equipment", []))
        
        # Keep first quest item found
        if not merged_loot["quest_item"] and loot_set.get("quest_item"):
            merged_loot["quest_item"] = loot_set["quest_item"]
        
        # Keep first magical item found
        if not merged_loot["magical_item"] and loot_set.get("magical_item"):
            merged_loot["magical_item"] = loot_set["magical_item"]
    
    return merged_loot


def apply_biome_to_loot_table(
    base_loot: Dict[str, Any], 
    biome_type: str, 
    biome_effects: Dict[str, Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Applies biome-specific modifiers to loot generation.
    
    Args:
        base_loot: Base loot set to modify
        biome_type: Type of biome (forest, mountains, desert, etc.)
        biome_effects: Optional dict of biome effects to apply
        
    Returns:
        Modified loot set with biome effects applied
    """
    if not biome_type:
        return base_loot
    
    # Default biome effects if none provided
    if biome_effects is None:
        biome_effects = {
            "forest": {"crafting_material": 10, "weapon": -5, "armor": -5},
            "mountains": {"crafting_material": 15, "weapon": 5, "armor": 5, "jewelry": -10},
            "desert": {"water": 20, "crafting_material": -5, "luxury": 10},
            "swamp": {"poison": 15, "disease": 10, "luxury": -15},
            "tundra": {"survival_gear": 20, "food": 10, "luxury": -10},
            "ocean": {"navigation": 15, "treasure": 5, "weapon": -10},
            "underground": {"mining": 20, "light_source": 15, "navigation": 10}
        }
    
    effects = biome_effects.get(biome_type.lower(), {})
    
    # Apply effects to equipment
    modified_loot = deepcopy(base_loot)
    
    for equipment in modified_loot.get("equipment", []):
        item_category = equipment.get("category", "").lower()
        
        # Apply relevant biome effects
        for effect_type, bonus in effects.items():
            if effect_type in item_category or item_category in effect_type:
                # Increase chance of getting items that match the biome
                if bonus > 0:
                    equipment["biome_bonus"] = equipment.get("biome_bonus", 0) + bonus
                # Decrease value of items that don't fit the biome
                elif bonus < 0:
                    equipment["biome_penalty"] = equipment.get("biome_penalty", 0) + abs(bonus)
    
    # Add biome-specific items if effects are positive enough
    if any(bonus >= 15 for bonus in effects.values()):
        # Add a special biome-specific item
        biome_item = {
            "name": f"{biome_type.title()} Artifact",
            "category": "treasure",
            "rarity": "rare",
            "value": 500,
            "biome_origin": biome_type,
            "description": f"A valuable artifact native to the {biome_type} region."
        }
        modified_loot["equipment"].append(biome_item)
    
    return modified_loot


def get_current_supply(item_name: str, region_id: int) -> int:
    """Get current supply level for an item in a region (0-100) - Business Logic Interface"""
    try:
        from backend.infrastructure.systems.loot.utils.economic_integration import get_current_supply as infra_get_supply
        return infra_get_supply(item_name, region_id)
    except ImportError:
        # Fallback to simple business logic calculation
        return _calculate_simple_supply(item_name)


def get_current_demand(item_name: str, region_id: int) -> int:
    """Get current demand level for an item in a region (0-100) - Business Logic Interface"""
    try:
        from backend.infrastructure.systems.loot.utils.economic_integration import get_current_demand as infra_get_demand
        return infra_get_demand(item_name, region_id)
    except ImportError:
        # Fallback to simple business logic calculation
        return _calculate_simple_demand(item_name)


def apply_economic_factors_to_price(base_price: int, region_id: int, item_name: str) -> int:
    """Apply economic factors to adjust pricing - Business Logic Interface"""
    try:
        from backend.infrastructure.systems.loot.utils.economic_integration import apply_economic_factors_to_price as infra_apply_factors
        return infra_apply_factors(base_price, region_id, item_name)
    except ImportError:
        # Fallback to simple business logic calculation
        return _calculate_simple_price_adjustment(base_price, item_name, region_id)


def _calculate_simple_supply(item_name: str) -> int:
    """Simple business logic for supply calculation"""
    # Basic supply estimation based on item characteristics
    item_lower = item_name.lower()
    
    # Common items have higher supply
    if any(common_type in item_lower for common_type in ['bread', 'water', 'simple', 'basic']):
        return random.randint(70, 90)
    
    # Rare items have lower supply
    elif any(rare_type in item_lower for rare_type in ['legendary', 'epic', 'artifact', 'unique']):
        return random.randint(5, 25)
    
    # Medium items have medium supply
    else:
        return random.randint(40, 70)


def _calculate_simple_demand(item_name: str) -> int:
    """Simple business logic for demand calculation"""
    # Basic demand estimation based on item characteristics
    item_lower = item_name.lower()
    
    # Useful items have higher demand
    if any(useful_type in item_lower for useful_type in ['weapon', 'armor', 'potion', 'healing']):
        return random.randint(60, 85)
    
    # Luxury items have variable demand
    elif any(luxury_type in item_lower for luxury_type in ['jewelry', 'gem', 'art', 'decoration']):
        return random.randint(30, 70)
    
    # Common consumables have steady demand
    else:
        return random.randint(45, 65)


def _calculate_simple_price_adjustment(base_price: int, item_name: str, region_id: int) -> int:
    """Simple business logic for price adjustment"""
    supply = _calculate_simple_supply(item_name)
    demand = _calculate_simple_demand(item_name)
    
    # Basic supply/demand calculation
    if supply == 0:
        supply = 1  # Avoid division by zero
    
    ratio = demand / supply
    
    # Simple price adjustment based on business rules
    if ratio > 1.2:  # High demand, low supply
        multiplier = 1.0 + ((ratio - 1.0) * 0.3)
    elif ratio < 0.8:  # Low demand, high supply
        multiplier = 1.0 - ((1.0 - ratio) * 0.2)
    else:
        multiplier = 1.0  # Balanced
    
    # Clamp to reasonable bounds
    multiplier = max(0.5, min(2.0, multiplier))
    
    adjusted_price = int(base_price * multiplier)
    return max(1, adjusted_price) 