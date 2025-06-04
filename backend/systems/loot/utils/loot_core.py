"""
Loot Core Module - Pure Business Logic

This module contains all core loot functionality including item validation, 
power calculation, equipment grouping, and loot generation. Pure business logic only.
"""

from typing import Dict, List, Any, Optional, Tuple
import random
from random import choice, randint
import math
from copy import deepcopy

# Import shared functions to avoid duplication
from .shared_functions import (
    group_equipment_by_type,
    gpt_name_and_flavor,
    merge_loot_sets,
    apply_biome_to_loot_table
)


# Custom exception classes
class LootValidationError(Exception):
    """Exception raised when loot item validation fails"""
    pass


class ItemGenerationError(Exception):
    """Exception raised when item generation fails"""
    pass


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
    monster_abilities: List[Dict[str, Any]] = None,
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
        monster_abilities: List of monster-specific effects
        source_type: Source of the loot (combat, chest, quest reward, etc.)
        location_id: Optional ID of the location where loot was generated
        region_id: Optional ID of the region where loot was generated
        
    Returns:
        Complete loot bundle dictionary
    """
    if not monster_levels:
        monster_levels = [1]
    
    if equipment_pool is None:
        equipment_pool = {}
    
    if item_effects is None:
        item_effects = []
    
    if monster_abilities is None:
        monster_abilities = []
    
    # Calculate average level for scaling
    avg_level = sum(monster_levels) / len(monster_levels)
    
    # Generate base loot amounts
    base_gold = int(10 + (avg_level * 5) + random.randint(-5, 10))
    gold_amount = max(0, base_gold)
    
    # Determine number of items (based on encounter size and level)
    encounter_size = len(monster_levels)
    item_count = min(encounter_size, max(1, int(avg_level / 3) + random.randint(0, 2)))
    
    equipment = []
    quest_item = None
    magical_item = None
    
    # Generate equipment items
    for _ in range(item_count):
        if equipment_pool:
            # Choose random category
            categories = list(equipment_pool.keys())
            if categories:
                category = random.choice(categories)
                items = equipment_pool[category]
                if items:
                    base_item = random.choice(items).copy()
                    
                    # Apply level scaling and effects
                    apply_level_scaling(base_item, avg_level)
                    
                    # Determine rarity
                    rarity = determine_item_rarity(avg_level)
                    base_item["rarity"] = rarity
                    
                    # Generate identity
                    base_item = generate_item_identity(base_item)
                    
                    equipment.append(base_item)
    
    # Chance for quest item (rare)
    if random.random() < 0.05:  # 5% chance
        quest_item = generate_quest_item(avg_level)
    
    # Chance for magical item (scales with level)
    magical_chance = min(0.3, 0.05 + (avg_level * 0.01))
    if random.random() < magical_chance:
        magical_item = generate_magical_item(avg_level, item_effects, monster_abilities)
    
    return {
        "gold": gold_amount,
        "equipment": equipment,
        "quest_item": quest_item,
        "magical_item": magical_item
    }


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
    monster_abilities: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generates location-specific loot with biome and faction influences.
    
    Args:
        location_id: ID of the location
        location_type: Type of location (dungeon, wilderness, city, etc.)
        biome_type: Biome affecting loot generation
        faction_id: ID of controlling faction
        faction_type: Type of faction (for theming)
        motif: Current motif affecting the location
        monster_levels: Levels of monsters in the location
        equipment_pool: Available equipment
        item_effects: Available magical effects
        monster_abilities: Available monster abilities
        
    Returns:
        Location-themed loot bundle
    """
    if monster_levels is None:
        monster_levels = [1]
    
    # Generate base loot
    base_loot = generate_loot_bundle(
        monster_levels=monster_levels,
        equipment_pool=equipment_pool,
        item_effects=item_effects,
        monster_abilities=monster_abilities
    )
    
    # Apply biome effects if present
    if biome_type:
        base_loot = apply_biome_effects_to_loot(base_loot, biome_type)
    
    # Apply faction effects if present
    if faction_id or faction_type:
        base_loot = apply_faction_effects_to_loot(base_loot, faction_id, faction_type)
    
    # Apply motif effects if present
    if motif:
        base_loot = apply_motif_effects_to_loot(base_loot, motif)
    
    return base_loot


# Helper functions for loot generation
def apply_level_scaling(item: Dict[str, Any], level: float) -> None:
    """Apply level-based scaling to item stats."""
    if "stats" in item:
        for stat_name, stat_value in item["stats"].items():
            if isinstance(stat_value, (int, float)):
                scaling_factor = 1.0 + (level - 1) * 0.1  # 10% per level
                item["stats"][stat_name] = int(stat_value * scaling_factor)


def determine_item_rarity(level: float) -> str:
    """Determine item rarity based on level."""
    rarity_chances = {
        "common": 0.6 - (level * 0.02),
        "uncommon": 0.25,
        "rare": 0.12 + (level * 0.01),
        "epic": 0.025 + (level * 0.005),
        "legendary": 0.005 + (level * 0.002)
    }
    
    # Normalize probabilities
    total = sum(rarity_chances.values())
    normalized_chances = {k: v/total for k, v in rarity_chances.items()}
    
    roll = random.random()
    cumulative = 0
    for rarity, chance in normalized_chances.items():
        cumulative += chance
        if roll <= cumulative:
            return rarity
    return "common"


def generate_quest_item(level: float) -> Dict[str, Any]:
    """Generate a quest-specific item."""
    return {
        "id": f"quest_item_{random.randint(1000, 9999)}",
        "name": "Mysterious Artifact",
        "category": "quest",
        "rarity": "unique",
        "description": "An ancient artifact of unknown purpose.",
        "value": int(100 + level * 20),
        "properties": {
            "quest_related": True,
            "unique": True
        }
    }


def generate_magical_item(
    level: float, 
    item_effects: List[Dict[str, Any]], 
    monster_abilities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate a magical item with effects."""
    rarity = determine_item_rarity(level)
    
    # Determine max effects based on rarity
    max_effects_by_rarity = {
        "common": 0,
        "uncommon": 1,
        "rare": 2,
        "epic": 3,
        "legendary": 5
    }
    
    max_effects = max_effects_by_rarity.get(rarity, 1)
    effects = generate_item_effects(rarity, max_effects, item_effects, monster_abilities)
    
    magical_item = {
        "id": f"magical_item_{random.randint(1000, 9999)}",
        "name": "Enchanted Item",
        "category": "magical",
        "rarity": rarity,
        "effects": effects,
        "value": int(50 + level * 15),
        "properties": {
            "magical": True
        }
    }
    
    return generate_item_identity(magical_item)


def apply_biome_effects_to_loot(loot: Dict[str, Any], biome: str) -> Dict[str, Any]:
    """Apply biome-specific effects to loot."""
    biome_modifiers = {
        "forest": {"gold_multiplier": 0.9, "nature_items": True},
        "desert": {"gold_multiplier": 1.1, "heat_resistance": True},
        "mountains": {"gold_multiplier": 1.2, "cold_resistance": True},
        "swamp": {"gold_multiplier": 0.8, "poison_resistance": True},
        "ocean": {"gold_multiplier": 1.0, "water_items": True},
        "underground": {"gold_multiplier": 1.3, "earth_items": True}
    }
    
    modifier = biome_modifiers.get(biome.lower(), {"gold_multiplier": 1.0})
    
    # Adjust gold amount
    loot["gold"] = int(loot["gold"] * modifier["gold_multiplier"])
    
    return loot


def apply_faction_effects_to_loot(
    loot: Dict[str, Any], 
    faction_id: Optional[int], 
    faction_type: Optional[str]
) -> Dict[str, Any]:
    """Apply faction-specific effects to loot."""
    if faction_type:
        faction_modifiers = {
            "military": {"weapon_chance": 1.5, "armor_chance": 1.3},
            "merchant": {"gold_multiplier": 1.4, "valuable_items": True},
            "religious": {"magical_chance": 1.2, "holy_items": True},
            "criminal": {"gold_multiplier": 1.1, "illegal_items": True}
        }
        
        modifier = faction_modifiers.get(faction_type.lower(), {})
        
        if "gold_multiplier" in modifier:
            loot["gold"] = int(loot["gold"] * modifier["gold_multiplier"])
    
    return loot


def apply_motif_effects_to_loot(loot: Dict[str, Any], motif: str) -> Dict[str, Any]:
    """Apply motif-specific effects to loot."""
    motif_modifiers = {
        "prosperity": {"gold_multiplier": 1.5, "quality_bonus": True},
        "death": {"necromantic_items": True, "gold_multiplier": 0.7},
        "war": {"weapon_chance": 2.0, "armor_chance": 1.5},
        "peace": {"gold_multiplier": 1.1, "healing_items": True},
        "chaos": {"random_effects": True, "unpredictable": True},
        "order": {"consistent_quality": True, "lawful_items": True}
    }
    
    modifier = motif_modifiers.get(motif.lower(), {})
    
    if "gold_multiplier" in modifier:
        loot["gold"] = int(loot["gold"] * modifier["gold_multiplier"])
    
    return loot


# Placeholder function for event system compatibility
def get_event_dispatcher():
    """Placeholder for event dispatcher - returns None in pure business logic"""
    return None 