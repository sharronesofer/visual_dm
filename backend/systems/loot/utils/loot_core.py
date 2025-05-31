"""
Loot Core Module

This module contains all core loot functionality expected by test_loot_core.py,
including item validation, power calculation, equipment grouping, and loot generation.

Implements the missing functions identified during the loot system refactor.
"""

from typing import Dict, List, Any, Optional, Tuple
import random
from random import choice, randint
import math
from copy import deepcopy

# TODO: Re-enable when shared events are implemented
# from backend.infrastructure.events import EventDispatcher, EventBase


# Custom exception classes
class LootValidationError(Exception):
    """Exception raised when loot item validation fails"""
    pass


class ItemGenerationError(Exception):
    """Exception raised when item generation fails"""
    pass


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


def validate_item(item: Dict[str, Any], valid_effects: List[Dict[str, Any]] = None) -> bool:
    """
    Validates that an item's effects are in the list of valid effects.
    
    Args:
        item: The item to validate
        valid_effects: List of valid effect definitions (optional)
        
    Returns:
        True if the item's effects are valid, False otherwise
    """
    if valid_effects is None:
        # If no valid effects provided, just check basic structure
        required_fields = ["name", "category"]
        return all(field in item for field in required_fields)
    
    effect_ids = {e["id"] for e in valid_effects}
    for entry in item.get("effects", []):
        effect = entry["effect"]
        if isinstance(effect, dict) and "id" in effect and effect["id"] not in effect_ids:
            return False
    return True


def calculate_item_power_score(item: Dict[str, Any]) -> int:
    """
    Calculates an item's power score based on its effects.
    
    Args:
        item: The item to calculate power score for
        
    Returns:
        Power score as an integer
    """
    base_score = 0
    
    # Base score from rarity
    rarity_scores = {
        "common": 1,
        "uncommon": 2,
        "rare": 4,
        "epic": 8,
        "legendary": 16
    }
    rarity = item.get("rarity", "common").lower()
    base_score += rarity_scores.get(rarity, 1)
    
    # Score from effects
    effects_score = sum(1 for e in item.get("effects", []) if e.get("level", 0) <= item.get("max_effects", 0))
    
    # Score from stats
    stats_score = 0
    for stat_name, stat_value in item.get("stats", {}).items():
        if isinstance(stat_value, (int, float)):
            stats_score += int(stat_value / 10)  # Every 10 points = 1 power score
    
    return base_score + effects_score + stats_score


def gpt_name_and_flavor(base_type: str = "item") -> Tuple[str, str]:
    """
    Generates a name and flavor text for an item using GPT.
    
    Args:
        base_type: The type of item to generate a name for
        
    Returns:
        Tuple of (name, flavor_text)
    """
    # Stub — replace with real GPT call
    return (
        f"The Whispering {base_type.title()}",
        f"This {base_type} hums with mysterious power linked to forgotten ruins."
    )


def generate_item_identity(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sets an item's generated name, flavor text, and identification status.
    
    Args:
        item: The item to generate identity for
        
    Returns:
        Updated item with identity properties
    """
    rarity = item.get("rarity", "common").lower()
    is_named = rarity in ["rare", "epic", "legendary"]

    if is_named:
        name, flavor = gpt_name_and_flavor(base_type=item.get("category", "item"))
        item["generated_name"] = name
        item["flavor_text"] = flavor
        item["name_revealed"] = False
        item["identified_name"] = None
    else:
        item["generated_name"] = item["name"]
        item["flavor_text"] = f"A well-made {item['name'].lower()}, but nothing unusual stands out."
        item["name_revealed"] = True
        item["identified_name"] = item["name"]

    return item


def generate_item_effects(
    rarity: str, 
    max_effects: int, 
    effect_pool: List[Dict[str, Any]], 
    monster_pool: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Generates magical effects for an item based on rarity.
    
    Args:
        rarity: Item rarity (legendary, epic, rare, or normal)
        max_effects: Maximum number of effects to generate
        effect_pool: List of available effects
        monster_pool: List of monster-specific effects for legendary items
        
    Returns:
        List of effect entries with level and effect data
    """
    if not effect_pool:
        return []
    
    if monster_pool is None:
        monster_pool = []
    
    effects = []
    for lvl in range(1, max_effects + 1):
        if rarity == "legendary" and monster_pool and random.random() < 0.1:
            effect = choice(monster_pool)
        else:
            # Filter effects by rarity if the effect has allowed_rarity field
            valid_effects = [e for e in effect_pool if not e.get("allowed_rarity") or rarity in e.get("allowed_rarity", [])]
            if not valid_effects:
                valid_effects = effect_pool
            effect = choice(valid_effects)
        effects.append({"level": lvl, "effect": effect})
    return effects


def generate_loot_bundle(
    monster_levels: List[int],
    equipment_pool: Dict[str, List[Dict[str, Any]]] = None,
    item_effects: List[Dict[str, Any]] = None,
    monster_feats: List[Dict[str, Any]] = None,
    source_type: str = "combat",
    location_id: Optional[int] = None,
    region_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generates a complete loot bundle based on monster levels.
    
    Args:
        monster_levels: List of monster levels
        equipment_pool: Dict of equipment items by type
        item_effects: List of available magical effects
        monster_feats: List of monster-specific effects
        source_type: Source of the loot (combat, chest, quest reward, etc.)
        location_id: Optional ID of the location where loot was generated
        region_id: Optional ID of the region where loot was generated
        
    Returns:
        Loot bundle with gold, equipment, quest items, and magical items
    """
    if equipment_pool is None:
        equipment_pool = {"weapon": [], "armor": [], "gear": []}
    if item_effects is None:
        item_effects = []
    if monster_feats is None:
        monster_feats = []
    
    loot = {
        "gold": sum(randint(5 + ml, 12 + ml * 2) for ml in monster_levels),
        "equipment": [],
        "quest_item": None,
        "magical_item": None
    }

    # === GEAR DROP ===
    if random.random() < 0.5:
        gear_items = equipment_pool.get("gear", [])
        if gear_items:
            item = deepcopy(choice(gear_items))
            loot["equipment"].append(item)
    else:
        choices = equipment_pool.get("weapon", []) + equipment_pool.get("armor", [])
        if choices:
            item = deepcopy(choice(choices))
            loot["equipment"].append(item)

    # === QUEST ITEM (5%) ===
    if random.random() < 0.05:
        gear_items = equipment_pool.get("gear", [])
        if gear_items:
            gear_item = deepcopy(choice(gear_items))
            name, flavor = gpt_name_and_flavor(base_type=gear_item.get("category", "item"))
            gear_item.update({
                "quest_hook": True,
                "generated_name": name,
                "flavor_text": flavor,
                "name_revealed": False
            })
            loot["quest_item"] = gear_item

    # === MAGICAL ITEM DROP ===
    rarity = None
    if random.random() < 0.5:
        rarity_roll = random.random()
        if rarity_roll <= 0.000025:
            rarity = "legendary"
        elif rarity_roll <= 0.0025:
            rarity = "epic"
        elif rarity_roll <= 0.05:
            rarity = "rare"
        else:
            rarity = "normal"

        choices = equipment_pool.get("weapon", []) + equipment_pool.get("armor", [])
        if choices:
            base_item = deepcopy(choice(choices))
            max_effects = 20 if rarity == "legendary" else randint(8, 12) if rarity == "epic" else randint(3, 5)

            effects = generate_item_effects(rarity, max_effects, item_effects, monster_feats)

            base_item.update({
                "rarity": rarity,
                "unknown_effects": [e["effect"] for e in effects]
            })

            base_item = generate_item_identity(base_item)
            loot["magical_item"] = base_item

    return loot


def merge_loot_sets(loot_sets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merges multiple loot sets into a single combined set.
    
    Args:
        loot_sets: List of loot bundles to merge
        
    Returns:
        Combined loot bundle
    """
    combined = {"gold": 0, "equipment": [], "quest_item": [], "magical_item": []}
    for loot in loot_sets:
        combined["gold"] += loot.get("gold", 0)
        combined["equipment"].extend(loot.get("equipment", []))
        if loot.get("quest_item"):
            combined["quest_item"].append(loot["quest_item"])
        if loot.get("magical_item"):
            combined["magical_item"].append(loot["magical_item"])
    return combined


def generate_location_specific_loot(
    location_id: int,
    location_type: str = "dungeon",
    biome_type: str = None,
    faction_id: int = None,
    faction_type: str = None,
    motif: str = None,
    monster_levels: List[int] = None,
    equipment_pool: Dict[str, List[Dict[str, Any]]] = None,
    item_effects: List[Dict[str, Any]] = None,
    monster_feats: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generates location-specific loot based on various contextual factors.
    
    Args:
        location_id: ID of the location
        location_type: Type of location (dungeon, ruins, etc.)
        biome_type: Biome type (forest, desert, etc.)
        faction_id: ID of controlling faction
        faction_type: Type of faction
        motif: Current motif affecting the area
        monster_levels: Levels of monsters in the area
        equipment_pool: Available equipment
        item_effects: Available magical effects
        monster_feats: Monster-specific effects
        
    Returns:
        Location-specific loot bundle
    """
    if monster_levels is None:
        monster_levels = [1]
    
    # Generate base loot
    loot = generate_loot_bundle(
        monster_levels=monster_levels,
        equipment_pool=equipment_pool,
        item_effects=item_effects,
        monster_feats=monster_feats,
        source_type="location",
        location_id=location_id
    )
    
    # Apply location-specific modifiers
    if location_type == "treasure_vault":
        loot["gold"] = int(loot["gold"] * 2.5)
    elif location_type == "ruins":
        loot["gold"] = int(loot["gold"] * 0.7)
        # More chance for rare items in ruins
        if random.random() < 0.3 and not loot["magical_item"]:
            # Generate a rare item
            choices = equipment_pool.get("weapon", []) + equipment_pool.get("armor", []) if equipment_pool else []
            if choices:
                base_item = deepcopy(choice(choices))
                base_item["rarity"] = "rare"
                base_item = generate_item_identity(base_item)
                loot["magical_item"] = base_item
    
    return loot 