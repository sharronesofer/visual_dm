#This module powers structured loot generation with optional GPT flair. It supports generation of gold, equipment, quest items, and magical items based on encounter difficulty. Includes item validation, merging, and progressive identification.
#It is deeply tied into the asset, combat, gpt, and narrative systems.

import random
from random import random, choice, randint
from uuid import uuid4
from copy import deepcopy
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import math

# Import the event dispatcher
from backend.app.core.events.event_dispatcher import EventDispatcher, EventBase

# Event type definitions
class LootGeneratedEvent(EventBase):
    """Event emitted when loot is generated"""
    event_type: str = "loot.generated"
    monster_levels: List[int]
    gold_amount: int
    item_count: int
    has_quest_item: bool
    has_magical_item: bool
    rarity_level: Optional[str] = None
    source_type: str = "combat"
    location_id: Optional[int] = None
    region_id: Optional[int] = None

class ItemIdentificationEvent(EventBase):
    """Event emitted when an item is identified"""
    event_type: str = "loot.item_identified"
    item_id: str
    item_name: str
    item_rarity: str
    character_id: int
    skill_level: int = 0
    identification_difficulty: int
    success: bool
    discovered_effects: List[Dict[str, Any]] = []

class ItemEnhancementEvent(EventBase):
    """Event emitted when an item is enhanced"""
    event_type: str = "loot.item_enhanced"
    item_id: str
    item_name: str
    original_rarity: str
    new_rarity: str
    enhancement_type: str  # level_up, enchantment, reforge
    enhancement_level: int
    success: bool
    character_id: int
    craft_skill_used: str

class ShopInventoryEvent(EventBase):
    """Event emitted when shop inventory is generated"""
    event_type: str = "loot.shop_inventory_generated"
    shop_id: int
    shop_type: str
    shop_tier: int
    region_id: Optional[int] = None
    faction_id: Optional[int] = None
    item_count: int
    restocking: bool
    economic_factors: Dict[str, float] = {}

class ShopRestockEvent(EventBase):
    """Event emitted when a shop is restocked"""
    event_type: str = "loot.shop_restocked"
    shop_id: int
    shop_type: str
    shop_tier: int
    previous_item_count: int
    new_item_count: int
    total_item_count: int
    region_id: Optional[int] = None

class ShopTransactionEvent(EventBase):
    """Event emitted for shop transactions"""
    event_type: str = "loot.shop_transaction"
    transaction_id: str
    shop_id: int
    character_id: int
    item_id: str
    quantity: int
    gold_amount: int
    transaction_type: str  # purchase or sale
    success: bool

class LootAnalyticsEvent(EventBase):
    """Event for tracking loot-related analytics"""
    event_type: str = "loot.analytics"
    event_category: str  # what type of event (shop_transaction, enhancement, identification)
    event_action: str  # specific action (purchase, attempt, success)
    item_id: str
    item_name: str
    item_rarity: str
    character_id: int
    value: float = 0.0  # gold amount, success rate, etc.
    metadata: Dict[str, Any] = {}

# =====================================================================
# === ITEM CATEGORIZATION & ORGANIZATION ==============================
# =====================================================================

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

def validate_item(item: Dict[str, Any], valid_effects: List[Dict[str, Any]]) -> bool:
    """
    Validates that an item's effects are in the list of valid effects.
    
    Args:
        item: The item to validate
        valid_effects: List of valid effect definitions
        
    Returns:
        True if the item's effects are valid, False otherwise
    """
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
    return sum(1 for e in item.get("effects", []) if e["level"] <= item.get("max_effects", 0))

# =====================================================================
# === ITEM IDENTITY & NAMING ==========================================
# =====================================================================

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

# =====================================================================
# === MAGICAL ITEM EFFECT GENERATION =================================
# =====================================================================

def generate_item_effects(
    rarity: str, 
    max_effects: int, 
    effect_pool: List[Dict[str, Any]], 
    monster_pool: List[Dict[str, Any]]
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
    effects = []
    for lvl in range(1, max_effects + 1):
        if rarity == "legendary" and random() < 0.1:
            effect = choice(monster_pool)
        else:
            effect = choice([e for e in effect_pool if rarity in e["allowed_rarity"]])
        effects.append({"level": lvl, "effect": effect})
    return effects

# =====================================================================
# === LOOT GENERATION ================================================
# =====================================================================

def generate_loot_bundle(
    monster_levels: List[int],
    equipment_pool: Dict[str, List[Dict[str, Any]]],
    item_effects: List[Dict[str, Any]],
    monster_feats: List[Dict[str, Any]],
    gpt_name_and_flavor = gpt_name_and_flavor,
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
        gpt_name_and_flavor: Function to generate names and flavor text
        source_type: Source of the loot (combat, chest, quest reward, etc.)
        location_id: Optional ID of the location where loot was generated
        region_id: Optional ID of the region where loot was generated
        
    Returns:
        Loot bundle with gold, equipment, quest items, and magical items
    """
    loot = {
        "gold": sum(randint(5 + ml, 12 + ml * 2) for ml in monster_levels),
        "equipment": [],
        "quest_item": None,
        "magical_item": None
    }

    # === GEAR DROP ===
    if random() < 0.5:
        item = deepcopy(choice(equipment_pool.get("gear", [])))
        loot["equipment"].append(item)
    else:
        choices = equipment_pool.get("weapon", []) + equipment_pool.get("armor", [])
        item = deepcopy(choice(choices))
        loot["equipment"].append(item)

    # === QUEST ITEM (5%) ===
    if random() < 0.05:
        gear_item = deepcopy(choice(equipment_pool.get("gear", [])))
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
    if random() < 0.5:
        rarity_roll = random()
        if rarity_roll <= 0.000025:
            rarity = "legendary"
        elif rarity_roll <= 0.0025:
            rarity = "epic"
        elif rarity_roll <= 0.05:
            rarity = "rare"
        else:
            rarity = "normal"

        base_item = deepcopy(choice(equipment_pool.get("weapon", []) + equipment_pool.get("armor", [])))
        max_effects = 20 if rarity == "legendary" else randint(8, 12) if rarity == "epic" else randint(3, 5)

        effects = generate_item_effects(rarity, max_effects, item_effects, monster_feats)

        base_item.update({
            "rarity": rarity,
            "unknown_effects": [e["effect"] for e in effects]
        })

        base_item = generate_item_identity(base_item)
        loot["magical_item"] = base_item

    # Emit loot generation event
    dispatcher = EventDispatcher.get_instance()
    event = LootGeneratedEvent(
        event_type="loot.generated",
        monster_levels=monster_levels,
        gold_amount=loot["gold"],
        item_count=len(loot["equipment"]),
        has_quest_item=loot["quest_item"] is not None,
        has_magical_item=loot["magical_item"] is not None,
        rarity_level=rarity,
        source_type=source_type,
        location_id=location_id,
        region_id=region_id
    )
    dispatcher.publish_sync(event)

    return loot

def get_loot_for_encounter(encounter: Dict[str, Any], 
                        equipment_pool: Dict[str, List[Dict[str, Any]]],
                        item_effects: List[Dict[str, Any]],
                        monster_feats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to get loot for an encounter.
    
    Args:
        encounter: Encounter data with monsters
        equipment_pool: Dict of equipment items by type
        item_effects: List of available magical effects
        monster_feats: List of monster-specific effects
        
    Returns:
        Generated loot bundle
    """
    monster_lvls = [m.get("level", 1) for m in encounter.get("monsters", [])]
    return generate_loot_bundle(
        monster_levels=monster_lvls,
        equipment_pool=equipment_pool,
        item_effects=item_effects,
        monster_feats=monster_feats
    )

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

# =====================================================================
# === LOCATION-BASED LOOT GENERATION =================================
# =====================================================================

def get_location_loot_table(location_id: int, location_type: str = None) -> Dict[str, Any]:
    """
    Get the loot table for a specific location.
    
    Args:
        location_id: The ID of the location
        location_type: Optional type of location (dungeon, city, etc.)
        
    Returns:
        A dictionary containing the loot table for this location
    """
    # In a real implementation, this would query from the database
    # For now, we'll create a default loot table with probabilities
    
    base_loot_table = {
        "gold": {
            "base_amount": 50,
            "variance": 25,
            "level_multiplier": 1.5
        },
        "item_counts": {
            "min": 1,
            "max": 4,
            "level_scaling": 0.2  # Each level adds 0.2 chance for another item
        },
        "rarities": {
            "common": 60,
            "uncommon": 25,
            "rare": 10,
            "epic": 4,
            "legendary": 1
        },
        "item_types": {
            "weapon": 30,
            "armor": 25,
            "accessory": 15,
            "consumable": 20,
            "crafting_material": 5,
            "quest_item": 5
        },
        "special_rules": {
            "guaranteed_potions": False,
            "guaranteed_magical": False,
            "min_rarity": "common"
        }
    }
    
    # Adjust based on location type if provided
    if location_type:
        if location_type.lower() == "dungeon":
            base_loot_table["gold"]["base_amount"] = 100
            base_loot_table["gold"]["variance"] = 50
            base_loot_table["item_counts"]["min"] = 2
            base_loot_table["rarities"]["rare"] += 5  # Increase rare drop chance
            base_loot_table["rarities"]["common"] -= 5  # Decrease common drop chance
            base_loot_table["special_rules"]["guaranteed_potions"] = True
        elif location_type.lower() == "boss_area":
            base_loot_table["gold"]["base_amount"] = 250
            base_loot_table["gold"]["variance"] = 100
            base_loot_table["item_counts"]["min"] = 3
            base_loot_table["special_rules"]["guaranteed_magical"] = True
            base_loot_table["special_rules"]["min_rarity"] = "uncommon"
        elif location_type.lower() == "city":
            base_loot_table["gold"]["base_amount"] = 25
            base_loot_table["item_types"]["consumable"] += 10
            base_loot_table["item_types"]["weapon"] -= 5
            base_loot_table["item_types"]["armor"] -= 5
        elif location_type.lower() == "wilderness":
            base_loot_table["gold"]["base_amount"] = 30
            base_loot_table["item_types"]["crafting_material"] += 15
            base_loot_table["item_types"]["weapon"] -= 5
            base_loot_table["item_types"]["armor"] -= 10
        
    # In a production system, we would query a database for location-specific overrides
    # For now, we'll just return the base table with modifications
    
    return base_loot_table

def apply_biome_to_loot_table(loot_table: Dict[str, Any], biome_type: str) -> Dict[str, Any]:
    """
    Modify the loot table based on the biome type.
    
    Args:
        loot_table: The base loot table to modify
        biome_type: The type of biome (forest, desert, etc.)
        
    Returns:
        The modified loot table
    """
    # Make a copy to avoid modifying the original
    modified_table = {**loot_table}
    
    if biome_type.lower() == "forest":
        # Forests have more wood and plant materials
        if "crafting_material" in modified_table["item_types"]:
            modified_table["item_types"]["crafting_material"] += 10
            # Adjust other categories to maintain 100%
            modified_table["item_types"]["weapon"] -= 5
            modified_table["item_types"]["armor"] -= 5
            
    elif biome_type.lower() == "mountains":
        # Mountains have more ore and minerals
        if "crafting_material" in modified_table["item_types"]:
            modified_table["item_types"]["crafting_material"] += 15
            # Better weapons in mountain areas (dwarven/mining tools)
            modified_table["item_types"]["weapon"] += 5
            # Adjust other categories
            modified_table["item_types"]["consumable"] -= 10
            modified_table["item_types"]["accessory"] -= 10
            
    elif biome_type.lower() == "desert":
        # Less gold in deserts, but more rare items
        modified_table["gold"]["base_amount"] = int(modified_table["gold"]["base_amount"] * 0.7)
        modified_table["rarities"]["rare"] += 5
        modified_table["rarities"]["common"] -= 5
        
    elif biome_type.lower() == "swamp":
        # Swamps have more potions and alchemical ingredients
        modified_table["item_types"]["consumable"] += 15
        modified_table["item_types"]["weapon"] -= 5
        modified_table["item_types"]["armor"] -= 10
    
    return modified_table

def apply_faction_to_loot_table(loot_table: Dict[str, Any], faction_id: int, faction_type: str = None) -> Dict[str, Any]:
    """
    Modify the loot table based on faction control/influence.
    
    Args:
        loot_table: The base loot table to modify
        faction_id: The ID of the faction
        faction_type: Optional type of faction (military, merchant, etc.)
        
    Returns:
        The modified loot table
    """
    # Make a copy to avoid modifying the original
    modified_table = {**loot_table}
    
    # In a production system, we would query faction details from the database
    # For this implementation, we'll use faction_type if provided
    
    if faction_type:
        if faction_type.lower() == "military":
            # Military factions have better weapons and armor
            modified_table["item_types"]["weapon"] += 10
            modified_table["item_types"]["armor"] += 10
            modified_table["item_types"]["consumable"] -= 10
            modified_table["item_types"]["accessory"] -= 10
            
        elif faction_type.lower() == "merchant":
            # Merchant factions have more gold and trade goods
            modified_table["gold"]["base_amount"] = int(modified_table["gold"]["base_amount"] * 1.5)
            modified_table["item_types"]["accessory"] += 10
            modified_table["item_types"]["consumable"] += 5
            modified_table["item_types"]["weapon"] -= 10
            modified_table["item_types"]["armor"] -= 5
            
        elif faction_type.lower() == "magical":
            # Magical factions have more magical items
            modified_table["special_rules"]["guaranteed_magical"] = True
            modified_table["rarities"]["rare"] += 5
            modified_table["rarities"]["epic"] += 2
            modified_table["rarities"]["common"] -= 7
            
    return modified_table

def apply_motif_to_loot_table(loot_table: Dict[str, Any], motif: str) -> Dict[str, Any]:
    """
    Modify the loot table based on the active motif.
    
    Args:
        loot_table: The base loot table to modify
        motif: The current motif affecting the region/location
        
    Returns:
        The modified loot table
    """
    # Make a copy to avoid modifying the original
    modified_table = {**loot_table}
    
    # Apply changes based on motif themes from the Development Bible
    if motif.lower() == "wealth" or motif.lower() == "prosperity":
        # More gold and valuable items 
        modified_table["gold"]["base_amount"] = int(modified_table["gold"]["base_amount"] * 1.5)
        modified_table["rarities"]["rare"] += 5
        modified_table["rarities"]["epic"] += 3
        modified_table["rarities"]["common"] -= 8
        
    elif motif.lower() == "death" or motif.lower() == "ruin":
        # Less gold but more powerful/sinister items
        modified_table["gold"]["base_amount"] = int(modified_table["gold"]["base_amount"] * 0.7)
        modified_table["rarities"]["epic"] += 5
        modified_table["rarities"]["legendary"] += 1
        modified_table["rarities"]["common"] -= 6
        
    elif motif.lower() == "transformation" or motif.lower() == "change":
        # More variety and unexpected items
        modified_table["item_counts"]["min"] += 1
        modified_table["item_counts"]["max"] += 2
        modified_table["rarities"]["uncommon"] += 10
        modified_table["rarities"]["common"] -= 10
        
    elif motif.lower() == "conflict" or motif.lower() == "war":
        # More weapons and armor
        modified_table["item_types"]["weapon"] += 15
        modified_table["item_types"]["armor"] += 10
        modified_table["item_types"]["consumable"] += 5
        modified_table["item_types"]["accessory"] -= 15
        modified_table["item_types"]["crafting_material"] -= 15
        
    return modified_table

def generate_location_specific_loot(
    location_id: int,
    location_type: str,
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
    Generate location-specific loot, taking into account location, biome, faction, and motif.
    
    Args:
        location_id: The ID of the location
        location_type: Type of location (dungeon, city, etc.)
        biome_type: Optional type of biome (forest, desert, etc.)
        faction_id: Optional ID of controlling faction
        faction_type: Optional type of faction (military, merchant, etc.)
        motif: Optional motif affecting the region
        monster_levels: Optional list of monster levels (for combat loot)
        equipment_pool: Optional pool of equipment to choose from
        item_effects: Optional list of available item effects
        monster_feats: Optional list of monster feats
        
    Returns:
        A loot bundle dictionary
    """
    # Start with the base loot table for this location
    loot_table = get_location_loot_table(location_id, location_type)
    
    # Apply modifiers based on biome, faction, and motif
    if biome_type:
        loot_table = apply_biome_to_loot_table(loot_table, biome_type)
        
    if faction_id:
        loot_table = apply_faction_to_loot_table(loot_table, faction_id, faction_type)
        
    if motif:
        loot_table = apply_motif_to_loot_table(loot_table, motif)
    
    # Determine the monster levels if not provided
    if not monster_levels and location_type:
        # Assign default levels based on location type
        if location_type.lower() == "city":
            monster_levels = [1, 2]
        elif location_type.lower() == "dungeon":
            monster_levels = [3, 4, 5]
        elif location_type.lower() == "boss_area":
            monster_levels = [6, 7, 8]
        elif location_type.lower() == "wilderness":
            monster_levels = [2, 3, 4]
        else:
            monster_levels = [1]
    
    # Generate gold based on loot table
    gold_base = loot_table["gold"]["base_amount"]
    gold_variance = loot_table["gold"]["variance"]
    level_multiplier = loot_table["gold"]["level_multiplier"]
    
    avg_monster_level = sum(monster_levels) / len(monster_levels) if monster_levels else 1
    gold_amount = int(
        (gold_base + random.randint(-gold_variance, gold_variance)) * 
        (1 + (avg_monster_level - 1) * level_multiplier)
    )
    
    # Determine number of items
    min_items = loot_table["item_counts"]["min"]
    max_items = loot_table["item_counts"]["max"]
    level_scaling = loot_table["item_counts"]["level_scaling"]
    
    item_count_bonus = avg_monster_level * level_scaling
    max_items_adjusted = min(max_items, min_items + int(item_count_bonus))
    item_count = random.randint(min_items, max_items_adjusted)
    
    # If we have equipment pool and effects, generate items
    items = []
    if equipment_pool and item_effects:
        # Helper function to select rarity based on loot table probabilities
        def select_rarity():
            rarities = loot_table["rarities"]
            total = sum(rarities.values())
            roll = random.randint(1, total)
            
            cumulative = 0
            for rarity, chance in rarities.items():
                cumulative += chance
                if roll <= cumulative:
                    return rarity
            
            return "common"  # Fallback
        
        # Helper function to select item type based on loot table probabilities
        def select_item_type():
            item_types = loot_table["item_types"]
            total = sum(item_types.values())
            roll = random.randint(1, total)
            
            cumulative = 0
            for item_type, chance in item_types.items():
                cumulative += chance
                if roll <= cumulative:
                    return item_type
            
            return "weapon"  # Fallback
        
        # Ensure minimum rarity if specified
        min_rarity = loot_table["special_rules"].get("min_rarity", "common")
        rarity_order = ["common", "uncommon", "rare", "epic", "legendary"]
        min_rarity_index = rarity_order.index(min_rarity)
        
        # Generate the specified number of items
        for _ in range(item_count):
            # Select rarity
            rarity = select_rarity()
            
            # Ensure minimum rarity
            if rarity_order.index(rarity) < min_rarity_index:
                rarity = min_rarity
            
            # Select item type
            item_type = select_item_type()
            
            # Check if we have items of this type in our equipment pool
            if item_type in equipment_pool and equipment_pool[item_type]:
                # Select a random base item of this type
                base_item = random.choice(equipment_pool[item_type])
                
                # Generate a copy with modified properties
                item = base_item.copy()
                
                # Apply rarity and location context to the item
                item["rarity"] = rarity
                
                # Add faction or motif theming if applicable
                if faction_id or faction_type:
                    if "thematic_tags" not in item:
                        item["thematic_tags"] = []
                    if faction_type:
                        item["thematic_tags"].append(f"faction:{faction_type}")
                
                if motif:
                    if "thematic_tags" not in item:
                        item["thematic_tags"] = []
                    item["thematic_tags"].append(f"motif:{motif}")
                
                # Add location context
                if "metadata" not in item:
                    item["metadata"] = {}
                item["metadata"]["location_id"] = location_id
                item["metadata"]["location_type"] = location_type
                if biome_type:
                    item["metadata"]["biome_type"] = biome_type
                
                # Check if magical items are guaranteed
                if loot_table["special_rules"].get("guaranteed_magical", False):
                    # Generate magical effects
                    max_effects = {
                        "common": 0,
                        "uncommon": 1,
                        "rare": 2,
                        "epic": 3,
                        "legendary": 4
                    }.get(rarity, 0)
                    
                    if max_effects > 0:
                        # Select effects
                        if "effects" not in item:
                            item["effects"] = []
                        
                        # Add effects appropriate for the rarity
                        available_effects = [e for e in item_effects if e.get("min_rarity", "common") in rarity_order[rarity_order.index(rarity):]]
                        
                        if available_effects:
                            effect_count = random.randint(1, max_effects)
                            for _ in range(effect_count):
                                effect = random.choice(available_effects).copy()
                                # Scale effect power based on rarity
                                effect["power"] = effect.get("base_power", 1) * (1 + rarity_order.index(rarity) * 0.5)
                                item["effects"].append(effect)
                
                # Add the item to our list
                items.append(item)
            
            # TODO: Handle other item types like consumables, quest items, etc.
    
    # Create the loot bundle
    loot_bundle = {
        "gold": gold_amount,
        "items": items,
        "location_id": location_id,
        "location_type": location_type,
        "source_type": "location"
    }
    
    # Add contextual data
    if biome_type:
        loot_bundle["biome_type"] = biome_type
    if faction_id:
        loot_bundle["faction_id"] = faction_id
    if faction_type:
        loot_bundle["faction_type"] = faction_type
    if motif:
        loot_bundle["motif"] = motif
    
    # Dispatch event for loot generation
    dispatcher = EventDispatcher.get_instance()
    dispatcher.publish_sync(LootGeneratedEvent(
        monster_levels=monster_levels if monster_levels else [],
        gold_amount=gold_amount,
        item_count=len(items),
        has_quest_item=any(item.get("item_type") == "quest_item" for item in items),
        has_magical_item=any(item.get("effects", []) for item in items),
        rarity_level=max([item.get("rarity", "common") for item in items], default="common"),
        source_type="location",
        location_id=location_id,
    ))
    
    # Also log to analytics
    log_loot_generation_stats(
        monster_levels=monster_levels if monster_levels else [],
        items_generated=items,
        gold_amount=gold_amount,
        source_type="location",
        location_id=location_id
    )
    
    return loot_bundle

# =====================================================================
# === ECONOMY AND DYNAMIC PRICING ====================================
# =====================================================================

def get_region_economic_factors(region_id: int) -> Dict[str, float]:
    """
    Get economic factors for a specific region.
    
    Args:
        region_id: The ID of the region
        
    Returns:
        Dictionary of economic factors and their values
    """
    # In a real implementation, this would query from a database
    # For now, return a default set of factors with some random variation
    
    base_factors = {
        "prosperity": 1.0,       # Overall economic health (higher = better economy)
        "scarcity": 1.0,         # Resource scarcity (higher = more scarce)
        "demand": 1.0,           # General demand level (higher = more demand)
        "tax_rate": 0.1,         # Tax rate (0.1 = 10%)
        "trade_volume": 1.0,     # Trade activity (higher = more trade)
        "crafting_cost": 1.0     # Cost of crafting (higher = more expensive)
    }
    
    # Add some random variation to make each region unique
    # In a real implementation, these would be persistent values stored in the database
    import random
    random.seed(region_id)  # Ensure consistent values for the same region
    
    factors = {}
    for factor, base_value in base_factors.items():
        # Add ±20% random variation
        factors[factor] = base_value * random.uniform(0.8, 1.2)
    
    return factors

def calculate_base_price(item: Dict[str, Any]) -> int:
    """
    Calculate the base price of an item before any adjustments.
    
    Args:
        item: The item to calculate price for
        
    Returns:
        Base price as an integer
    """
    # Start with item's intrinsic value if available
    base_price = item.get("value", 0)
    
    if base_price <= 0:
        # Calculate based on rarity and type
        rarity_multipliers = {
            "common": 1,
            "uncommon": 3,
            "rare": 10,
            "epic": 50,
            "legendary": 250
        }
        
        type_base_prices = {
            "weapon": 25,
            "armor": 30,
            "accessory": 15,
            "consumable": 10,
            "crafting_material": 5,
            "quest_item": 50
        }
        
        item_type = item.get("item_type", "").lower()
        if not item_type and "category" in item:
            item_type = item.get("category", "").lower()
            
        rarity = item.get("rarity", "common").lower()
        
        type_price = type_base_prices.get(item_type, 20)
        rarity_multi = rarity_multipliers.get(rarity, 1)
        
        base_price = type_price * rarity_multi
        
        # Adjust for level/tier if present
        if "level" in item:
            level_factor = 1 + (item["level"] * 0.2)
            base_price = int(base_price * level_factor)
            
        # Adjust for magical effects
        if "effects" in item and item["effects"]:
            base_price += len(item["effects"]) * 15 * rarity_multi
    
    return max(1, base_price)  # Ensure minimum price of 1

def get_current_supply(item_name: str, region_id: int) -> int:
    """
    Get the current supply of an item in a region.
    
    Args:
        item_name: Name of the item
        region_id: ID of the region
        
    Returns:
        Current supply as integer (0-100, where 100 is abundant)
    """
    # In a real implementation, this would query the database 
    # for current stock levels across all shops in the region
    
    # For now, generate a semi-random value based on item name and region
    import hashlib
    import random
    
    # Create a hash based on item name and region for consistency
    hash_input = f"{item_name}:{region_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    random.seed(hash_value)
    
    # Generate a value between 10 and 90
    return random.randint(10, 90)

def get_current_demand(item_name: str, region_id: int) -> int:
    """
    Get the current demand for an item in a region.
    
    Args:
        item_name: Name of the item
        region_id: ID of the region
        
    Returns:
        Current demand as integer (0-100, where 100 is high demand)
    """
    # In a real implementation, this would query the database
    # for purchase history, quest requirements, etc.
    
    # For now, generate a semi-random value based on item name and region
    import hashlib
    import random
    
    # Create a hash based on item name and region for consistency
    # Use a different seed than supply to avoid correlation
    hash_input = f"demand:{item_name}:{region_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    random.seed(hash_value)
    
    # Generate a value between 10 and 90
    return random.randint(10, 90)

def adjust_price_for_supply_demand(
    base_price: int, 
    item_name: str, 
    item_id: int,
    region_id: int
) -> int:
    """
    Adjust item price based on supply and demand in the region.
    
    Args:
        base_price: Starting price
        item_name: Name of the item
        item_id: ID of the item
        region_id: ID of the region
        
    Returns:
        Adjusted price
    """
    # Get current supply and demand values (0-100)
    supply = get_current_supply(item_name, region_id)
    demand = get_current_demand(item_name, region_id)
    
    # Calculate supply/demand ratio (higher means more demand than supply)
    # Avoid division by zero
    if supply == 0:
        supply = 1
    ratio = demand / supply
    
    # Get economic factors for this region
    econ_factors = get_region_economic_factors(region_id)
    
    # Adjust ratio based on region's prosperity and trade volume
    prosperity_factor = econ_factors.get("prosperity", 1.0)
    trade_factor = econ_factors.get("trade_volume", 1.0)
    
    # High prosperity reduces price volatility, high trade increases it
    volatility = 1.0 / prosperity_factor * trade_factor
    
    # Calculate price multiplier
    # At equilibrium (ratio=1), multiplier should be 1.0
    # Allow prices to fluctuate by up to ±50% based on supply/demand
    price_multiplier = 1.0 + ((ratio - 1.0) * 0.5 * volatility)
    
    # Ensure a reasonable range
    price_multiplier = max(0.5, min(2.0, price_multiplier))
    
    # Apply tax rate
    tax_rate = econ_factors.get("tax_rate", 0.1)
    price_with_tax = base_price * (1 + tax_rate)
    
    # Calculate final adjusted price
    adjusted_price = int(price_with_tax * price_multiplier)
    
    # Ensure minimum price of 1
    adjusted_price = max(1, adjusted_price)
    
    # Emit price adjustment event
    dispatcher = EventDispatcher.get_instance()
    dispatcher.publish_sync(PriceAdjustmentEvent(
        item_id=item_id,
        item_name=item_name,
        old_price=base_price,
        new_price=adjusted_price,
        adjustment_factor=price_multiplier,
        reason=f"Supply/demand (S:{supply}, D:{demand})",
        region_id=region_id
    ))
    
    return adjusted_price

def apply_motif_to_prices(
    base_price: int, 
    item_name: str, 
    item_id: int,
    region_id: int, 
    motif: str
) -> int:
    """
    Adjust item price based on the current motif.
    
    Args:
        base_price: Starting price
        item_name: Name of the item
        item_id: ID of the item
        region_id: ID of the region
        motif: Current motif affecting the region
        
    Returns:
        Adjusted price
    """
    # Default: no change
    price_multiplier = 1.0
    reason = f"Motif: {motif} (no effect)"
    
    # Apply effects based on motif - these should align with the motifs in the Development Bible
    motif = motif.lower()
    
    if motif in ["wealth", "prosperity", "abundance"]:
        # Economy is booming - luxury items cost more, essentials cost less
        if "weapon" in item_name.lower() or "armor" in item_name.lower():
            price_multiplier = 1.2
            reason = f"Motif: {motif} (luxury premium)"
        else:
            price_multiplier = 0.9
            reason = f"Motif: {motif} (essential discount)"
    
    elif motif in ["death", "ruin", "decay"]:
        # Economy is suffering - essentials cost more, luxury items cost less
        if "potion" in item_name.lower() or "food" in item_name.lower():
            price_multiplier = 1.5
            reason = f"Motif: {motif} (essential scarcity)"
        else:
            price_multiplier = 0.7
            reason = f"Motif: {motif} (luxury devalued)"
    
    elif motif in ["conflict", "war", "struggle"]:
        # War economy - weapons and armor cost more, luxury items cost less
        if "weapon" in item_name.lower() or "armor" in item_name.lower():
            price_multiplier = 1.5
            reason = f"Motif: {motif} (war premium)"
        elif "jewelry" in item_name.lower() or "luxury" in item_name.lower():
            price_multiplier = 0.6
            reason = f"Motif: {motif} (luxury unwanted)"
    
    elif motif in ["fear", "paranoia", "madness"]:
        # Protection items at premium
        if "shield" in item_name.lower() or "protect" in item_name.lower():
            price_multiplier = 1.4
            reason = f"Motif: {motif} (protection premium)"
    
    elif motif in ["transformation", "change", "rebirth"]:
        # Crafting materials in demand
        if "material" in item_name.lower() or "ingredient" in item_name.lower():
            price_multiplier = 1.3
            reason = f"Motif: {motif} (crafting boom)"
    
    # Apply the adjustment
    adjusted_price = int(base_price * price_multiplier)
    
    # Emit price adjustment event if there was a change
    if price_multiplier != 1.0:
        dispatcher = EventDispatcher.get_instance()
        dispatcher.publish_sync(PriceAdjustmentEvent(
            item_id=item_id,
            item_name=item_name,
            old_price=base_price,
            new_price=adjusted_price,
            adjustment_factor=price_multiplier,
            reason=reason,
            region_id=region_id
        ))
    
    return adjusted_price

def apply_event_to_prices(
    base_price: int, 
    item_name: str, 
    item_id: int,
    region_id: int, 
    event_type: str
) -> int:
    """
    Adjust item price based on world events.
    
    Args:
        base_price: Starting price
        item_name: Name of the item
        item_id: ID of the item
        region_id: ID of the region
        event_type: Type of world event
        
    Returns:
        Adjusted price
    """
    # Default: no change
    price_multiplier = 1.0
    reason = f"Event: {event_type} (no effect)"
    
    # Apply effects based on world events
    event_type = event_type.lower()
    
    if event_type == "famine":
        # Food prices skyrocket, luxury items plummet
        if "food" in item_name.lower() or "ration" in item_name.lower():
            price_multiplier = 3.0
            reason = f"Event: {event_type} (extreme food scarcity)"
        elif "luxury" in item_name.lower() or "jewelry" in item_name.lower():
            price_multiplier = 0.5
            reason = f"Event: {event_type} (luxury unwanted)"
    
    elif event_type == "plague":
        # Healing items at premium, clothing/armor cheaper (fear of contamination)
        if "healing" in item_name.lower() or "potion" in item_name.lower() or "herb" in item_name.lower():
            price_multiplier = 2.5
            reason = f"Event: {event_type} (medicine premium)"
        elif "clothes" in item_name.lower() or "armor" in item_name.lower():
            price_multiplier = 0.7
            reason = f"Event: {event_type} (contamination fear)"
    
    elif event_type == "war":
        # Similar to war motif but more extreme
        if "weapon" in item_name.lower() or "armor" in item_name.lower():
            price_multiplier = 2.0
            reason = f"Event: {event_type} (war demand)"
        elif "luxury" in item_name.lower():
            price_multiplier = 0.4
            reason = f"Event: {event_type} (wartime austerity)"
    
    elif event_type == "festival":
        # Luxury, food, and drink at premium
        if "luxury" in item_name.lower() or "food" in item_name.lower() or "drink" in item_name.lower():
            price_multiplier = 1.5
            reason = f"Event: {event_type} (celebration demand)"
        elif "weapon" in item_name.lower() or "armor" in item_name.lower():
            price_multiplier = 0.8
            reason = f"Event: {event_type} (peaceful time)"
    
    elif event_type == "merchant_caravan":
        # All prices lower due to increased supply
        price_multiplier = 0.8
        reason = f"Event: {event_type} (increased supply)"
    
    # Apply the adjustment
    adjusted_price = int(base_price * price_multiplier)
    
    # Emit price adjustment event if there was a change
    if price_multiplier != 1.0:
        dispatcher = EventDispatcher.get_instance()
        dispatcher.publish_sync(PriceAdjustmentEvent(
            item_id=item_id,
            item_name=item_name,
            old_price=base_price,
            new_price=adjusted_price,
            adjustment_factor=price_multiplier,
            reason=reason,
            region_id=region_id
        ))
    
    return adjusted_price

def get_dynamic_item_price(
    item: Dict[str, Any], 
    region_id: int, 
    motif: str = None, 
    world_events: List[str] = None
) -> int:
    """
    Calculate a dynamic price for an item based on economic factors.
    
    Args:
        item: The item to price
        region_id: ID of the region
        motif: Optional current motif affecting the region
        world_events: Optional list of active world events
        
    Returns:
        Final calculated price
    """
    # Get item details
    item_id = item.get("id", 0)
    item_name = item.get("name", "Unknown Item")
    
    # Calculate base price from item properties
    base_price = calculate_base_price(item)
    current_price = base_price
    
    # Apply supply and demand adjustments
    current_price = adjust_price_for_supply_demand(
        current_price, 
        item_name, 
        item_id,
        region_id
    )
    
    # Apply motif adjustments if applicable
    if motif:
        current_price = apply_motif_to_prices(
            current_price, 
            item_name, 
            item_id,
            region_id, 
            motif
        )
    
    # Apply world event adjustments if applicable
    if world_events:
        for event in world_events:
            current_price = apply_event_to_prices(
                current_price, 
                item_name, 
                item_id,
                region_id, 
                event
            )
    
    # Final cleanup: ensure price is an integer and at least 1
    return max(1, int(current_price))

def initialize_shop_inventory(
    shop_id: int,
    shop_type: str,
    region_id: int,
    equipment_pool: Dict[str, List[Dict[str, Any]]],
    item_effects: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Initializes inventory for a shop based on shop type and region.
    
    Args:
        shop_id: ID of the shop
        shop_type: Type of shop (e.g., "blacksmith", "general", "magic")
        region_id: ID of the region
        equipment_pool: Dictionary of equipment items by type
        item_effects: List of available magical effects
        
    Returns:
        List of inventory items with dynamic pricing
    """
    inventory = []
    
    # Determine number of items based on shop type
    num_items = {
        "blacksmith": randint(5, 12),
        "general": randint(10, 20),
        "magic": randint(3, 8),
        "specialty": randint(4, 10),
        "wandering": randint(2, 5)
    }.get(shop_type, randint(5, 15))
    
    # Determine item categories based on shop type
    categories = {
        "blacksmith": ["weapon", "armor"],
        "general": ["gear", "weapon", "armor"],
        "magic": ["gear", "weapon", "armor"],
        "specialty": ["gear"],
        "wandering": ["gear", "weapon", "armor"]
    }.get(shop_type, ["gear", "weapon", "armor"])
    
    # Determine chance of magical items
    magical_chance = {
        "blacksmith": 0.1,
        "general": 0.05,
        "magic": 0.8,
        "specialty": 0.3,
        "wandering": 0.2
    }.get(shop_type, 0.1)
    
    # Generate inventory items
    for _ in range(num_items):
        # Choose a random category
        category = choice(categories)
        
        # Get a random item from the category
        if category == "weapon":
            base_item = deepcopy(choice(equipment_pool.get("weapon", [])))
        elif category == "armor":
            base_item = deepcopy(choice(equipment_pool.get("armor", [])))
        else:
            base_item = deepcopy(choice(equipment_pool.get("gear", [])))
        
        # Determine if it's a magical item
        is_magical = random() < magical_chance
        
        if is_magical and shop_type == "magic":
            # For magic shops, higher chance of rare+ items
            rarity_roll = random()
            if rarity_roll <= 0.01:
                rarity = "legendary"
            elif rarity_roll <= 0.1:
                rarity = "epic"
            elif rarity_roll <= 0.3:
                rarity = "rare"
            else:
                rarity = "uncommon"
                
            # Generate magical effects
            max_effects = 20 if rarity == "legendary" else randint(8, 12) if rarity == "epic" else randint(3, 5)
            effects = generate_item_effects(rarity, max_effects, item_effects, [])
            
            base_item.update({
                "rarity": rarity,
                "effects": [e["effect"] for e in effects]
            })
            
            # Generate name and flavor text
            base_item = generate_item_identity(base_item)
        elif is_magical:
            # For other shops, mostly uncommon items
            rarity_roll = random()
            if rarity_roll <= 0.001:
                rarity = "legendary"
            elif rarity_roll <= 0.01:
                rarity = "epic"
            elif rarity_roll <= 0.1:
                rarity = "rare"
            else:
                rarity = "uncommon"
                
            # Generate magical effects
            max_effects = 20 if rarity == "legendary" else randint(8, 12) if rarity == "epic" else randint(3, 5)
            effects = generate_item_effects(rarity, max_effects, item_effects, [])
            
            base_item.update({
                "rarity": rarity,
                "effects": [e["effect"] for e in effects]
            })
            
            # Generate name and flavor text
            base_item = generate_item_identity(base_item)
        
        # Calculate dynamic price
        base_item["id"] = randint(1000, 9999)  # Temporary ID
        base_item["price"] = get_dynamic_item_price(base_item, region_id)
        
        # Add to inventory
        inventory.append({
            "shop_id": shop_id,
            "item": base_item,
            "quantity": randint(1, 5),
            "price": base_item["price"],
            "added_at": datetime.utcnow().isoformat()
        })
    
    return inventory

def update_shop_prices(
    inventory: List[Dict[str, Any]],
    region_id: int,
    motif: str = None,
    world_events: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Updates prices for all items in a shop's inventory.
    
    Args:
        inventory: Current inventory items
        region_id: ID of the region
        motif: Optional current dominant motif
        world_events: Optional list of active world events
        
    Returns:
        Updated inventory with new prices
    """
    updated_inventory = []
    
    for entry in inventory:
        item = entry["item"]
        old_price = entry["price"]
        
        # Calculate new dynamic price
        new_price = get_dynamic_item_price(item, region_id, motif, world_events)
        
        # Update inventory entry
        updated_entry = deepcopy(entry)
        updated_entry["price"] = new_price
        updated_entry["last_price_update"] = datetime.utcnow().isoformat()
        
        # Emit price change event if price changed
        if old_price != new_price:
            dispatcher = EventDispatcher.get_instance()
            event = PriceAdjustmentEvent(
                event_type="price.adjusted",
                item_id=item.get("id", 0),
                item_name=item.get("name", "Unknown Item"),
                old_price=old_price,
                new_price=new_price,
                adjustment_factor=new_price / old_price if old_price > 0 else 1.0,
                reason="shop_update",
                region_id=region_id
            )
            dispatcher.publish_sync(event)
        
        updated_inventory.append(updated_entry)
    
    return updated_inventory

# =====================================================================
# === PROGRESSIVE ITEM IDENTIFICATION ================================
# =====================================================================

def get_identification_difficulty(item: Dict[str, Any]) -> int:
    """
    Calculate how difficult an item is to identify.
    
    Args:
        item: The item to check
        
    Returns:
        Difficulty score (1-100)
    """
    # Base difficulty depends on rarity
    rarity_difficulty = {
        "common": 10,
        "uncommon": 25,
        "rare": 50,
        "epic": 75,
        "legendary": 90
    }
    
    # Get the item's rarity
    rarity = item.get("rarity", "common").lower()
    
    # Base difficulty from rarity
    difficulty = rarity_difficulty.get(rarity, 20)
    
    # Add difficulty for each magical effect
    effects = item.get("effects", [])
    effect_count = len(effects)
    
    # Each effect adds to difficulty
    difficulty += effect_count * 5
    
    # Special/unique items are harder to identify
    if item.get("unique", False):
        difficulty += 15
    
    # Ancient/mysterious origins add difficulty
    if item.get("age", 0) > 100:
        difficulty += 10
    
    # Cursed or corrupted items are harder to identify
    has_curse = any("curse" in effect.get("type", "").lower() for effect in effects)
    if has_curse:
        difficulty += 20
    
    # Cap difficulty at 100
    return min(100, difficulty)

def identify_item(
    item: Dict[str, Any],
    character_id: int,
    skill_level: int = 0,
    use_tome: bool = False,
    tome_bonus: int = 0,
    force_identify: bool = False
) -> Tuple[Dict[str, Any], bool, List[Dict[str, Any]]]:
    """
    Attempt to identify an item or discover more of its properties.
    
    Args:
        item: The item to identify
        character_id: ID of the character attempting identification
        skill_level: Character's applicable identification skill level
        use_tome: Whether a tome of identification is being used
        tome_bonus: Identification bonus from the tome (percentage points)
        force_identify: Force full identification (admin/debug feature)
        
    Returns:
        Tuple of (updated item, success boolean, list of newly discovered effects)
    """
    # Make a copy of the item to avoid modifying the original
    updated_item = item.copy()
    
    # Check if already fully identified
    if updated_item.get("identified", False) and updated_item.get("identification_level", 0) >= 100:
        return updated_item, False, []
    
    # Initialize identification level if needed
    if "identification_level" not in updated_item:
        updated_item["identification_level"] = 0
    
    # Initialize identified effects list if needed
    if "identified_effects" not in updated_item:
        updated_item["identified_effects"] = []
    
    # Calculate identification difficulty
    difficulty = get_identification_difficulty(updated_item)
    
    # Calculate success chance
    base_chance = 50  # Base 50% chance
    
    # Skill bonus
    skill_bonus = skill_level * 2  # +2% per skill level
    
    # Tome bonus
    item_bonus = tome_bonus if use_tome else 0
    
    # Current identification level makes further identification harder
    current_level = updated_item.get("identification_level", 0)
    difficulty_modifier = -(current_level / 2)  # -0.5% per point already identified
    
    # Calculate final chance
    success_chance = base_chance + skill_bonus + item_bonus + difficulty_modifier
    
    # Ensure reasonable range
    success_chance = max(5, min(95, success_chance))
    
    # Determine success
    success = force_identify
    if not success:
        import random
        roll = random.randint(1, 100)
        success = roll <= success_chance
    
    newly_discovered = []
    
    if success or force_identify:
        # Identification successful
        
        # All items at least become basically identified
        updated_item["identified"] = True
        
        # Progress made varies by skill, item difficulty, and luck
        progress_base = max(5, int(skill_level / 2))  # 5-50% progress based on skill
        progress_random = random.randint(1, 10)  # 1-10% random
        
        if use_tome:
            progress_base += tome_bonus / 2  # Tome adds extra progress
        
        total_progress = progress_base + progress_random
        
        if force_identify:
            total_progress = 100  # Complete identification
        
        # Update identification level
        new_level = min(100, current_level + total_progress)
        updated_item["identification_level"] = new_level
        
        # Check which effects can now be identified
        all_effects = updated_item.get("effects", [])
        known_effects = updated_item.get("identified_effects", [])
        known_effect_ids = [effect.get("id") for effect in known_effects]
        
        # For each unknown effect, check if it can now be identified
        for effect in all_effects:
            effect_id = effect.get("id")
            
            if effect_id not in known_effect_ids:
                # Effect not yet identified
                
                # Each effect has a threshold to be identified
                # Simpler effects can be identified earlier
                effect_type = effect.get("type", "unknown")
                effect_power = effect.get("power", 5)
                
                # Calculate identification threshold for this effect
                # Based on effect complexity and power
                threshold_mod = 0
                
                if "base" in effect_type:
                    threshold_mod = -20  # Base properties identified early
                elif "enchantment" in effect_type:
                    threshold_mod = 0  # Standard threshold
                elif "curse" in effect_type:
                    threshold_mod = 20  # Curses are hard to identify
                elif "unique" in effect_type:
                    threshold_mod = 30  # Unique effects are very hard to identify
                
                # Power affects threshold
                power_mod = effect_power * 2
                
                # Calculate final threshold (25-90%)
                threshold = max(25, min(90, 50 + threshold_mod + power_mod))
                
                # If identification level exceeds threshold, identify this effect
                if new_level >= threshold:
                    # Add to identified effects
                    updated_item["identified_effects"].append(effect)
                    newly_discovered.append(effect)
        
        # If all effects identified, mark as fully identified
        if len(updated_item["identified_effects"]) == len(all_effects):
            updated_item["identification_level"] = 100
    
    # Create identification event
    dispatcher = EventDispatcher.get_instance()
    dispatcher.publish_sync(ItemIdentificationEvent(
        item_id=updated_item.get("id", "0"),
        item_name=updated_item.get("name", "Unknown Item"),
        item_rarity=updated_item.get("rarity", "common"),
        character_id=character_id,
        skill_level=skill_level,
        identification_difficulty=difficulty,
        success=success,
        discovered_effects=newly_discovered
    ))
    
    # Log to analytics
    dispatcher.publish_sync(LootAnalyticsEvent(
        event_category="identification",
        event_action="attempt",
        item_id=updated_item.get("id", "0"),
        item_name=updated_item.get("name", "Unknown Item"),
        item_rarity=updated_item.get("rarity", "common"),
        character_id=character_id,
        value=success_chance,
        metadata={
            "success": success,
            "skill_level": skill_level,
            "use_tome": use_tome,
            "tome_bonus": tome_bonus,
            "identification_difficulty": difficulty,
            "newly_discovered_count": len(newly_discovered),
            "current_identification_level": updated_item["identification_level"]
        }
    ))
    
    return updated_item, success, newly_discovered

def generate_unidentified_description(item: Dict[str, Any]) -> str:
    """
    Generate a description for an unidentified item based on currently known properties.
    
    Args:
        item: The item to describe
        
    Returns:
        Description string
    """
    # Base description template
    rarity = item.get("rarity", "common").lower()
    item_type = item.get("item_type", item.get("category", "item")).lower()
    
    # Get item's identification level
    id_level = item.get("identification_level", 0)
    
    # Base descriptions for different identification levels
    if id_level < 25:
        # Barely identified
        desc_map = {
            "weapon": f"A {rarity} weapon of unknown origin.",
            "armor": f"A piece of {rarity} armor with indistinct markings.",
            "accessory": f"A {rarity} ornament with an unusual design.",
            "potion": f"A vial containing a {rarity} liquid that gives off a strange aroma.",
            "scroll": f"A {rarity} scroll with faded script that's difficult to read.",
            "material": f"A {rarity} material with properties that remain mysterious.",
            "tool": f"A {rarity} tool whose purpose isn't immediately clear.",
            "trinket": f"A curious {rarity} trinket with an unknown function."
        }
        
        description = desc_map.get(item_type, f"A mysterious {rarity} item.")
    
    elif id_level < 50:
        # Partially identified
        item_name = item.get("name", "unknown item")
        
        desc_map = {
            "weapon": f"A {rarity} {item_name}. It appears to be a functional weapon, though some of its properties remain unknown.",
            "armor": f"A {rarity} {item_name}. It provides some protection, but its full capabilities are yet to be determined.",
            "accessory": f"A {rarity} {item_name}. It has a distinct style, though its magical properties remain unclear.",
            "potion": f"A {rarity} {item_name}. The liquid has a distinctive color and smell, but its effects aren't fully understood.",
            "scroll": f"A {rarity} {item_name}. The script is partially legible, but the full spell remains unclear.",
            "material": f"A {rarity} {item_name}. Some of its properties are evident, but others remain to be discovered.",
            "tool": f"A {rarity} {item_name}. Its primary function is clear, but it may have additional uses.",
            "trinket": f"A {rarity} {item_name}. Its purpose is becoming clearer, though some mystery remains."
        }
        
        description = desc_map.get(item_type, f"A partially identified {rarity} {item_name}.")
    
    elif id_level < 75:
        # Mostly identified
        item_name = item.get("name", "unknown item")
        
        # Get known effects
        known_effects = item.get("identified_effects", [])
        effect_count = len(known_effects)
        total_effects = len(item.get("effects", []))
        
        if effect_count > 0:
            effect_desc = ", ".join([e.get("name", "unknown") for e in known_effects[:2]])
            if effect_count > 2:
                effect_desc += f", and {effect_count - 2} more"
            
            desc_map = {
                "weapon": f"A {rarity} {item_name} with {effect_desc}. Most of its properties are now understood.",
                "armor": f"A {rarity} {item_name} featuring {effect_desc}. Its protective qualities are well documented.",
                "accessory": f"A {rarity} {item_name} that provides {effect_desc}. Most of its enchantments are known.",
                "potion": f"A {rarity} {item_name} that causes {effect_desc}. Its brewing method is mostly understood.",
                "scroll": f"A {rarity} {item_name} containing {effect_desc}. The magical script is mostly deciphered.",
                "material": f"A {rarity} {item_name} with properties including {effect_desc}. Most uses are documented.",
                "tool": f"A {rarity} {item_name} that facilitates {effect_desc}. Its mechanisms are largely understood.",
                "trinket": f"A {rarity} {item_name} that manifests {effect_desc}. Its purpose is now mostly clear."
            }
        else:
            desc_map = {
                "weapon": f"A {rarity} {item_name}. Most of its properties are now understood.",
                "armor": f"A {rarity} {item_name}. Its protective qualities are well documented.",
                "accessory": f"A {rarity} {item_name}. Most of its enchantments are known.",
                "potion": f"A {rarity} {item_name}. Its brewing method is mostly understood.",
                "scroll": f"A {rarity} {item_name}. The magical script is mostly deciphered.",
                "material": f"A {rarity} {item_name}. Most uses are documented.",
                "tool": f"A {rarity} {item_name}. Its mechanisms are largely understood.",
                "trinket": f"A {rarity} {item_name}. Its purpose is now mostly clear."
            }
        
        description = desc_map.get(item_type, f"A mostly identified {rarity} {item_name}.")
        
        # Add hint about unknown effects
        if effect_count < total_effects:
            unknown_count = total_effects - effect_count
            description += f" There {'appears to be' if unknown_count == 1 else 'appear to be'} {unknown_count} more undiscovered {'property' if unknown_count == 1 else 'properties'}."
    
    else:
        # Almost fully identified
        item_name = item.get("name", "unknown item")
        
        # Get all known effects
        known_effects = item.get("identified_effects", [])
        
        if known_effects:
            effect_names = [e.get("name", "unknown") for e in known_effects]
            effect_desc = ", ".join(effect_names[:-1])
            if len(effect_names) > 1:
                effect_desc += f" and {effect_names[-1]}"
            else:
                effect_desc = effect_names[0]
            
            description = f"A {rarity} {item_name} with {effect_desc}. Its properties are almost completely understood."
        else:
            description = f"A {rarity} {item_name}. Despite thorough examination, it appears to have no special properties."
    
    # Add origin hints if known
    origin = item.get("origin", "")
    age = item.get("age", 0)
    
    if origin and id_level >= 40:
        description += f" It appears to be of {origin} origin."
    
    if age > 100 and id_level >= 60:
        if age < 500:
            description += " It seems to be quite old."
        elif age < 1000:
            description += " It is clearly ancient."
        else:
            description += " It dates from a forgotten age."
    
    return description

# =====================================================================
# === ANALYTICS INTEGRATION ==========================================
# =====================================================================

def log_loot_acquisition(
    character_id: int,
    items: List[Dict[str, Any]],
    gold_amount: int,
    source_type: str,
    location_id: Optional[int] = None,
    region_id: Optional[int] = None
) -> None:
    """
    Logs loot acquisition for analytics.
    
    Args:
        character_id: ID of the character acquiring loot
        items: List of items acquired
        gold_amount: Amount of gold acquired
        source_type: Source of loot (e.g., "combat", "chest", "quest")
        location_id: Optional ID of the location
        region_id: Optional ID of the region
    """
    # Log gold acquisition
    if gold_amount > 0:
        dispatcher = EventDispatcher.get_instance()
        event = LootAnalyticsEvent(
            event_type="loot.analytics",
            event_category="loot",
            event_action="gold_acquired",
            character_id=character_id,
            gold_amount=gold_amount,
            source_type=source_type,
            location_id=location_id,
            region_id=region_id,
            value=float(gold_amount)
        )
        dispatcher.publish_sync(event)
    
    # Log each item acquisition
    for item in items:
        dispatcher = EventDispatcher.get_instance()
        event = LootAnalyticsEvent(
            event_type="loot.analytics",
            event_category="loot",
            event_action="item_acquired",
            item_id=item.get("id", 0),
            item_name=item.get("name", "Unknown Item"),
            item_rarity=item.get("rarity", "common"),
            character_id=character_id,
            source_type=source_type,
            location_id=location_id,
            region_id=region_id,
            value=float(item.get("value", 0)),
            metadata={
                "category": item.get("category", ""),
                "has_effects": len(item.get("effects", [])) > 0,
                "effects_count": len(item.get("effects", []))
            }
        )
        dispatcher.publish_sync(event)
    
    # Log rarity statistics
    rarity_counts = {}
    for item in items:
        rarity = item.get("rarity", "common").lower()
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
    
    for rarity, count in rarity_counts.items():
        dispatcher = EventDispatcher.get_instance()
        event = LootAnalyticsEvent(
            event_type="loot.analytics",
            event_category="loot",
            event_action="rarity_stats",
            character_id=character_id,
            source_type=source_type,
            item_rarity=rarity,
            location_id=location_id,
            region_id=region_id,
            value=float(count),
            metadata={
                "count": count,
                "percentage": count / len(items) if items else 0
            }
        )
        dispatcher.publish_sync(event)

def log_shop_transaction(
    character_id: int,
    shop_id: int,
    items_bought: List[Dict[str, Any]],
    items_sold: List[Dict[str, Any]],
    gold_spent: int,
    gold_earned: int,
    location_id: Optional[int] = None,
    region_id: Optional[int] = None
) -> None:
    """
    Logs shop transactions for analytics.
    
    Args:
        character_id: ID of the character making the transaction
        shop_id: ID of the shop
        items_bought: List of items bought
        items_sold: List of items sold
        gold_spent: Amount of gold spent
        gold_earned: Amount of gold earned
        location_id: Optional ID of the location
        region_id: Optional ID of the region
    """
    # Log transaction summary
    dispatcher = EventDispatcher.get_instance()
    event = LootAnalyticsEvent(
        event_type="loot.analytics",
        event_category="shop",
        event_action="transaction",
        character_id=character_id,
        location_id=location_id,
        region_id=region_id,
        value=float(gold_spent - gold_earned),  # Net gold flow (negative = player earned)
        metadata={
            "shop_id": shop_id,
            "items_bought": len(items_bought),
            "items_sold": len(items_sold),
            "gold_spent": gold_spent,
            "gold_earned": gold_earned
        }
    )
    dispatcher.publish_sync(event)
    
    # Log items bought
    for item in items_bought:
        dispatcher = EventDispatcher.get_instance()
        event = LootAnalyticsEvent(
            event_type="loot.analytics",
            event_category="shop",
            event_action="item_bought",
            item_id=item.get("id", 0),
            item_name=item.get("name", "Unknown Item"),
            item_rarity=item.get("rarity", "common"),
            character_id=character_id,
            source_type=source_type,
            location_id=location_id,
            region_id=region_id,
            value=float(item.get("price", 0)),
            metadata={
                "shop_id": shop_id,
                "category": item.get("category", ""),
                "base_value": item.get("value", 0),
                "price": item.get("price", 0),
                "markup": item.get("price", 0) / item.get("value", 1) if item.get("value", 0) > 0 else 0
            }
        )
        dispatcher.publish_sync(event)
    
    # Log items sold
    for item in items_sold:
        dispatcher = EventDispatcher.get_instance()
        event = LootAnalyticsEvent(
            event_type="loot.analytics",
            event_category="shop",
            event_action="item_sold",
            item_id=item.get("id", 0),
            item_name=item.get("name", "Unknown Item"),
            item_rarity=item.get("rarity", "common"),
            character_id=character_id,
            source_type=source_type,
            location_id=location_id,
            region_id=region_id,
            value=float(item.get("sell_price", 0)),
            metadata={
                "shop_id": shop_id,
                "category": item.get("category", ""),
                "base_value": item.get("value", 0),
                "sell_price": item.get("sell_price", 0),
                "discount": item.get("sell_price", 0) / item.get("value", 1) if item.get("value", 0) > 0 else 0
            }
        )
        dispatcher.publish_sync(event)

def log_loot_generation_stats(
    monster_levels: List[int],
    items_generated: List[Dict[str, Any]],
    gold_amount: int,
    source_type: str,
    location_id: Optional[int] = None,
    region_id: Optional[int] = None
) -> None:
    """
    Logs loot generation statistics for analytics.
    
    Args:
        monster_levels: List of monster levels
        items_generated: List of items generated
        gold_amount: Amount of gold generated
        source_type: Source of loot (e.g., "combat", "chest", "quest")
        location_id: Optional ID of the location
        region_id: Optional ID of the region
    """
    # Calculate average monster level
    avg_monster_level = sum(monster_levels) / len(monster_levels) if monster_levels else 0
    
    # Log loot generation
    dispatcher = EventDispatcher.get_instance()
    event = LootAnalyticsEvent(
        event_type="loot.analytics",
        event_category="loot",
        event_action="generation",
        source_type=source_type,
        location_id=location_id,
        region_id=region_id,
        gold_amount=gold_amount,
        value=float(len(items_generated)),
        metadata={
            "avg_monster_level": avg_monster_level,
            "max_monster_level": max(monster_levels) if monster_levels else 0,
            "gold_amount": gold_amount,
            "items_count": len(items_generated),
            "rarity_distribution": {item.get("rarity", "common"): 1 for item in items_generated}
        }
    )
    dispatcher.publish_sync(event)
    
    # Log gold generation relative to monster level
    if monster_levels:
        gold_per_level = gold_amount / sum(monster_levels)
        dispatcher = EventDispatcher.get_instance()
        event = LootAnalyticsEvent(
            event_type="loot.analytics",
            event_category="loot",
            event_action="gold_per_level",
            source_type=source_type,
            location_id=location_id,
            region_id=region_id,
            gold_amount=gold_amount,
            value=gold_per_level,
            metadata={
                "avg_monster_level": avg_monster_level,
                "total_monster_levels": sum(monster_levels),
                "gold_amount": gold_amount,
                "gold_per_level": gold_per_level
            }
        )
        dispatcher.publish_sync(event)

# =====================================================================
# === ITEM RARITY PROGRESSION & ENHANCEMENT ==========================
# =====================================================================

def calculate_item_enhancement_chance(
    item: Dict[str, Any],
    character_craft_skill: int = 0,
    tool_quality: int = 0,
    material_quality: int = 0,
    special_ingredients: List[str] = None
) -> float:
    """
    Calculates the chance of successfully enhancing an item.
    
    Args:
        item: Item data
        character_craft_skill: Crafting skill level (0-100)
        tool_quality: Quality of tools used (0-10)
        material_quality: Quality of materials used (0-10)
        special_ingredients: List of special ingredients used
        
    Returns:
        Success chance (0.0-1.0)
    """
    # Base chance depends on current rarity
    rarity_difficulty = {
        "common": 0.8,     # 80% base chance to improve common
        "uncommon": 0.6,   # 60% base chance to improve uncommon
        "rare": 0.4,       # 40% base chance to improve rare
        "epic": 0.2,       # 20% base chance to improve epic
        "legendary": 0.1,  # 10% base chance to improve legendary
    }
    
    rarity = item.get("rarity", "common").lower()
    base_chance = rarity_difficulty.get(rarity, 0.5)
    
    # Factor in character's craft skill (each point adds 0.5%)
    skill_bonus = min(0.3, character_craft_skill * 0.005)  # Cap at +30%
    
    # Factor in tool quality (each point adds 2%)
    tool_bonus = min(0.2, tool_quality * 0.02)  # Cap at +20%
    
    # Factor in material quality (each point adds 3%)
    material_bonus = min(0.3, material_quality * 0.03)  # Cap at +30%
    
    # Factor in special ingredients (each adds 5%)
    special_bonus = min(0.2, len(special_ingredients or []) * 0.05)  # Cap at +20%
    
    # Calculate final chance
    chance = base_chance + skill_bonus + tool_bonus + material_bonus + special_bonus
    
    # Cap at 95% max chance - always some risk
    return min(0.95, max(0.05, chance))

def get_next_rarity(current_rarity: str) -> str:
    """
    Gets the next rarity level above the current one.
    
    Args:
        current_rarity: Current rarity level
        
    Returns:
        Next rarity level, or current if already at max
    """
    rarity_progression = ["common", "uncommon", "rare", "epic", "legendary"]
    current = current_rarity.lower()
    
    try:
        idx = rarity_progression.index(current)
        return rarity_progression[min(idx + 1, len(rarity_progression) - 1)]
    except ValueError:
        # If current rarity not in progression, default to "uncommon"
        return "uncommon"

def enhance_item(
    item: Dict[str, Any],
    character_id: int,
    craft_skill_used: str,
    character_craft_skill: int = 0,
    tool_quality: int = 0,
    material_quality: int = 0,
    special_ingredients: List[str] = None,
    force_success: bool = False
) -> Tuple[Dict[str, Any], bool]:
    """
    Attempts to enhance an item to the next rarity level.
    
    Args:
        item: Item data
        character_id: ID of the character enhancing the item
        craft_skill_used: Type of crafting skill used (e.g., "blacksmithing")
        character_craft_skill: Crafting skill level (0-100)
        tool_quality: Quality of tools used (0-10)
        material_quality: Quality of materials used (0-10)
        special_ingredients: List of special ingredients used
        force_success: Force enhancement to succeed (for testing/admin)
        
    Returns:
        Tuple of (enhanced item, success flag)
    """
    # Clone the item to avoid modifying the original
    enhanced_item = deepcopy(item)
    
    # Get current and next rarity
    current_rarity = enhanced_item.get("rarity", "common").lower()
    next_rarity = get_next_rarity(current_rarity)
    
    # Check if already at max rarity
    if current_rarity == next_rarity:
        return enhanced_item, False
    
    # Calculate success chance
    success_chance = calculate_item_enhancement_chance(
        enhanced_item,
        character_craft_skill,
        tool_quality,
        material_quality,
        special_ingredients
    )
    
    # Determine if enhancement succeeds
    success = force_success or (random() < success_chance)
    
    # Update item if successful
    if success:
        enhanced_item["rarity"] = next_rarity
        
        # Increase item value based on new rarity
        rarity_value_multipliers = {
            "common": 1.0,
            "uncommon": 2.5,
            "rare": 6.0,
            "epic": 15.0,
            "legendary": 40.0
        }
        
        old_multiplier = rarity_value_multipliers.get(current_rarity, 1.0)
        new_multiplier = rarity_value_multipliers.get(next_rarity, 2.5)
        
        # Apply value multiplier
        base_value = enhanced_item.get("base_value", enhanced_item.get("value", 10))
        new_value = int(base_value * (new_multiplier / old_multiplier))
        
        enhanced_item["value"] = new_value
        if "base_value" not in enhanced_item:
            enhanced_item["base_value"] = base_value
            
        # Add enhancement metadata
        if "enhancements" not in enhanced_item:
            enhanced_item["enhancements"] = []
            
        enhanced_item["enhancements"].append({
            "type": "rarity_upgrade",
            "from": current_rarity,
            "to": next_rarity,
            "character_id": character_id,
            "craft_skill_used": craft_skill_used,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Add or improve an effect if lucky (30% chance for non-legendary items)
        if next_rarity != "legendary" and random() < 0.3:
            # Either add a new effect or improve an existing one
            if not enhanced_item.get("effects") or random() < 0.5:
                # Add a new effect
                effect_type = choice(["damage", "defense", "utility", "healing"])
                new_effect = generate_item_effect(effect_type, item_rarity=next_rarity)
                if new_effect:
                    if "effects" not in enhanced_item:
                        enhanced_item["effects"] = []
                    enhanced_item["effects"].append(new_effect)
            else:
                # Improve an existing effect (if any)
                effects = enhanced_item.get("effects", [])
                if effects:
                    effect_index = randint(0, len(effects) - 1)
                    effects[effect_index]["power"] = effects[effect_index].get("power", 1) + 1
                    
        # For legendary items, always add a unique effect
        if next_rarity == "legendary":
            legendary_effect = {
                "name": f"Legendary {craft_skill_used.title()} Mastery",
                "type": "legendary",
                "description": f"This item has been elevated to legendary status through masterful {craft_skill_used}.",
                "power": 3,
                "unique": True
            }
            if "effects" not in enhanced_item:
                enhanced_item["effects"] = []
            enhanced_item["effects"].append(legendary_effect)
    
    # Always emit event whether successful or not
    dispatcher = EventDispatcher.get_instance()
    event = ItemEnhancementEvent(
        item_id=enhanced_item.get("id", 0),
        item_name=enhanced_item.get("name", "Unknown Item"),
        original_rarity=current_rarity,
        new_rarity=next_rarity if success else current_rarity,
        enhancement_type="rarity_upgrade",
        enhancement_level=rarity_progression_to_level(next_rarity if success else current_rarity),
        success=success,
        character_id=character_id,
        craft_skill_used=craft_skill_used
    )
    dispatcher.publish_sync(event)
    
    return enhanced_item, success

def rarity_progression_to_level(rarity: str) -> int:
    """
    Converts a rarity to a numeric progression level.
    
    Args:
        rarity: Rarity string
        
    Returns:
        Numeric level (1-5)
    """
    rarity_levels = {
        "common": 1,
        "uncommon": 2,
        "rare": 3,
        "epic": 4,
        "legendary": 5
    }
    return rarity_levels.get(rarity.lower(), 1)

def add_enchantment_to_item(
    item: Dict[str, Any],
    character_id: int,
    enchantment_type: str,
    enchantment_level: int = 1,
    skill_level: int = 0,
    catalyst_quality: int = 0,
    special_reagents: List[str] = None
) -> Tuple[Dict[str, Any], bool]:
    """
    Adds a new enchantment to an item or enhances an existing one.
    
    Args:
        item: Item data
        character_id: ID of the character enchanting the item
        enchantment_type: Type of enchantment (e.g., "fire", "frost", "healing")
        enchantment_level: Desired level of enchantment (1-3)
        skill_level: Enchanting skill level (0-100)
        catalyst_quality: Quality of catalyst used (0-10)
        special_reagents: List of special reagents used
        
    Returns:
        Tuple of (enchanted item, success flag)
    """
    # Clone the item to avoid modifying the original
    enchanted_item = deepcopy(item)
    
    # Limit enchantment level based on item rarity
    rarity = enchanted_item.get("rarity", "common").lower()
    max_enchantment_level = {
        "common": 1,
        "uncommon": 2,
        "rare": 2,
        "epic": 3,
        "legendary": 3
    }.get(rarity, 1)
    
    target_level = min(enchantment_level, max_enchantment_level)
    
    # Calculate success chance
    base_chance = 0.7 - (target_level * 0.15)  # Level 1: 55%, Level 2: 40%, Level 3: 25%
    skill_bonus = min(0.3, skill_level * 0.003)  # Cap at +30%
    catalyst_bonus = min(0.2, catalyst_quality * 0.02)  # Cap at +20%
    reagent_bonus = min(0.2, len(special_reagents or []) * 0.05)  # Cap at +20%
    
    success_chance = base_chance + skill_bonus + catalyst_bonus + reagent_bonus
    success_chance = min(0.95, max(0.05, success_chance))  # Clamp to 5-95%
    
    # Determine if enchantment succeeds
    success = random() < success_chance
    
    if success:
        # Check if the item already has this type of enchantment
        if "enchantments" not in enchanted_item:
            enchanted_item["enchantments"] = []
            
        existing_enchantment = None
        for i, enchant in enumerate(enchanted_item.get("enchantments", [])):
            if enchant.get("type") == enchantment_type:
                existing_enchantment = (i, enchant)
                break
                
        if existing_enchantment:
            # Update existing enchantment if new level is higher
            idx, current_enchant = existing_enchantment
            if target_level > current_enchant.get("level", 1):
                enchanted_item["enchantments"][idx]["level"] = target_level
                enchanted_item["enchantments"][idx]["power"] = target_level * 2
                enchanted_item["enchantments"][idx]["last_modified"] = datetime.utcnow().isoformat()
            else:
                # No upgrade if trying to apply a lower or equal level enchantment
                success = False
        else:
            # Add new enchantment
            new_enchantment = {
                "type": enchantment_type,
                "name": f"{enchantment_type.title()} Enchantment",
                "level": target_level,
                "power": target_level * 2,
                "description": f"Grants {enchantment_type} properties of level {target_level}.",
                "added_by": character_id,
                "created_at": datetime.utcnow().isoformat()
            }
            enchanted_item["enchantments"].append(new_enchantment)
            
            # Add a visual effect based on enchantment type
            visual_effects = {
                "fire": "glowing red",
                "frost": "frosted blue",
                "lightning": "crackling yellow",
                "shadow": "shadowy darkness",
                "nature": "living green",
                "holy": "radiant gold",
                "healing": "soothing green",
                "protection": "shimmering barrier"
            }
            
            if "visual_effects" not in enchanted_item:
                enchanted_item["visual_effects"] = []
                
            visual = visual_effects.get(enchantment_type, "magical aura")
            enchanted_item["visual_effects"].append({
                "type": enchantment_type,
                "description": f"A {visual} surrounds the item when wielded."
            })
            
            # Increase item value based on enchantment
            value_increase = 1.0 + (target_level * 0.5)  # Level 1: +50%, Level 2: +100%, Level 3: +150%
            enchanted_item["value"] = int(enchanted_item.get("value", 10) * value_increase)
    
    # Emit enchantment event
    dispatcher = EventDispatcher.get_instance()
    event = ItemEnhancementEvent(
        event_type="item.enchanted",
        item_id=enchanted_item.get("id", 0),
        item_name=enchanted_item.get("name", "Unknown Item"),
        original_rarity=rarity,
        new_rarity=rarity,  # Rarity doesn't change with enchantment
        enhancement_type=f"{enchantment_type}_enchantment",
        enhancement_level=target_level if success else 0,
        success=success,
        character_id=character_id,
        craft_skill_used="enchanting"
    )
    dispatcher.publish_sync(event)
    
    return enchanted_item, success

def generate_item_effect(effect_type: str, item_rarity: str = "common") -> Dict[str, Any]:
    """
    Generates a random item effect based on type and rarity.
    
    Args:
        effect_type: Type of effect to generate
        item_rarity: Rarity of the item
        
    Returns:
        Generated effect data or None if invalid type
    """
    # Convert rarity to power modifier
    rarity_power = {
        "common": 1,
        "uncommon": 2,
        "rare": 3,
        "epic": 4,
        "legendary": 5
    }.get(item_rarity.lower(), 1)
    
    # Base power is 1-3 plus rarity bonus
    base_power = randint(1, 3) + (rarity_power - 1)
    
    # Generate effect based on type
    if effect_type == "damage":
        damage_types = ["physical", "fire", "frost", "lightning", "poison", "shadow", "holy"]
        damage_type = choice(damage_types)
        return {
            "name": f"{damage_type.title()} Damage",
            "type": "damage",
            "damage_type": damage_type,
            "power": base_power,
            "description": f"Deals +{base_power} {damage_type} damage."
        }
    elif effect_type == "defense":
        defense_types = ["physical", "magical", "elemental", "all"]
        defense_type = choice(defense_types)
        return {
            "name": f"{defense_type.title()} Protection",
            "type": "defense",
            "defense_type": defense_type,
            "power": base_power,
            "description": f"Provides +{base_power} defense against {defense_type} attacks."
        }
    elif effect_type == "utility":
        utility_types = [
            ("speed", "Increases movement speed by {value}%."),
            ("stamina", "Reduces stamina cost of actions by {value}%."),
            ("carrying", "Increases carrying capacity by {value}%."),
            ("stealth", "Improves stealth capability by {value}%."),
            ("perception", "Enhances perception by {value}%.")
        ]
        utility_type, desc_template = choice(utility_types)
        value = base_power * 5  # Convert to percentage
        return {
            "name": f"{utility_type.title()} Enhancement",
            "type": "utility",
            "utility_type": utility_type,
            "power": base_power,
            "value": value,
            "description": desc_template.format(value=value)
        }
    elif effect_type == "healing":
        healing_types = [
            ("regeneration", "Regenerates {value} health over time."),
            ("instant", "Has a {chance}% chance to heal for {value} when used."),
            ("lifesteal", "Converts {value}% of damage dealt to health.")
        ]
        healing_type, desc_template = choice(healing_types)
        value = base_power * 2
        chance = base_power * 10
        return {
            "name": f"{healing_type.title()}",
            "type": "healing",
            "healing_type": healing_type,
            "power": base_power,
            "value": value,
            "chance": chance,
            "description": desc_template.format(value=value, chance=chance)
        }
    else:
        return None

# =====================================================================
# === SHOP MANAGEMENT ===============================================
# =====================================================================

def generate_shop_inventory(
    shop_id: int,
    shop_type: str = "general",
    shop_tier: int = 1,
    region_id: Optional[int] = None,
    faction_id: Optional[int] = None,
    restocking: bool = False,
    count: int = 10
) -> List[Dict[str, Any]]:
    """
    Generate a shop's inventory based on its type, tier, and location.
    
    Args:
        shop_id: Unique ID for the shop
        shop_type: Type of shop (general, blacksmith, alchemist, etc.)
        shop_tier: Tier/quality level of the shop (1-5)
        region_id: Optional ID of the region the shop is in
        faction_id: Optional ID of the faction that owns/influences the shop
        restocking: Whether this is a restock or initial inventory
        count: Number of items to generate
        
    Returns:
        List of items for the shop inventory
    """
    import random
    from datetime import datetime, timedelta
    
    # Base inventory list
    inventory = []
    
    # Get regional economic factors
    economic_factors = {}
    if region_id:
        economic_factors = get_region_economic_factors(region_id)
    
    # Apply economic scaling based on prosperity
    prosperity = economic_factors.get("prosperity", 1.0)
    
    # Get shop type specialization
    item_type_weights = get_shop_type_specialization(shop_type)
    
    # Rarity chances based on shop tier
    rarity_chances = {
        "common": max(50 - (shop_tier * 10), 10),  # Decreases with tier
        "uncommon": 20 + (shop_tier * 5),  # Increases with tier
        "rare": 5 + (shop_tier * 5),  # Increases with tier
        "epic": max(0, shop_tier - 1) * 3,  # Only in tier 2+ shops
        "legendary": max(0, shop_tier - 3) * 2  # Only in tier 4+ shops
    }
    
    # Generate inventory items
    for i in range(count):
        # Determine item type based on shop specialization
        item_type = random.choices(
            population=list(item_type_weights.keys()),
            weights=list(item_type_weights.values()),
            k=1
        )[0]
        
        # Determine rarity based on shop tier
        rarity = random.choices(
            population=list(rarity_chances.keys()),
            weights=list(rarity_chances.values()),
            k=1
        )[0]
        
        # Generate a base item
        item = generate_item(
            item_type=item_type,
            rarity=rarity,
            level=shop_tier * 5
        )
        
        # Shop items always start identified
        item["identified"] = True
        
        # Set stock quantity based on rarity and shop type
        max_quantity = {
            "common": 5,
            "uncommon": 3,
            "rare": 1,
            "epic": 1,
            "legendary": 1
        }.get(rarity, 1)
        
        # Consumables and materials typically have higher stock
        if item_type in ["potion", "scroll", "material"]:
            max_quantity *= 2
        
        # Apply prosperity factor to quantity
        adjusted_max = max(1, int(max_quantity * prosperity))
        quantity = random.randint(1, adjusted_max)
        
        # Set shop-specific metadata
        item["shop_metadata"] = {
            "shop_id": shop_id,
            "quantity": quantity,
            "date_added": datetime.now().isoformat(),
            "restock_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "price_modifier": calculate_shop_price_modifier(
                shop_tier=shop_tier,
                economic_factors=economic_factors,
                item_rarity=rarity
            )
        }
        
        # Apply faction theming if applicable
        if faction_id:
            apply_faction_motifs(item, faction_id)
        
        # Apply regional theming
        if region_id:
            apply_regional_motifs(item, region_id)
        
        inventory.append(item)
    
    # Sort by rarity (higher rarity first)
    rarity_order = {"legendary": 0, "epic": 1, "rare": 2, "uncommon": 3, "common": 4}
    inventory.sort(key=lambda x: rarity_order.get(x.get("rarity", "common").lower(), 5))
    
    # Log analytics
    dispatcher = EventDispatcher.get_instance()
    dispatcher.publish_sync(ShopInventoryEvent(
        shop_id=shop_id,
        shop_type=shop_type,
        shop_tier=shop_tier,
        region_id=region_id,
        faction_id=faction_id,
        item_count=len(inventory),
        restocking=restocking,
        economic_factors=economic_factors
    ))
    
    return inventory

def get_shop_type_specialization(shop_type: str) -> Dict[str, float]:
    """
    Get item type weights based on shop specialization.
    
    Args:
        shop_type: Type of shop
        
    Returns:
        Dictionary of item types and their weights
    """
    # Default weights for a general store
    default_weights = {
        "weapon": 0.1,
        "armor": 0.1,
        "accessory": 0.1,
        "potion": 0.2,
        "scroll": 0.1,
        "material": 0.2,
        "tool": 0.1,
        "trinket": 0.1
    }
    
    # Shop specializations
    specializations = {
        "blacksmith": {
            "weapon": 0.4,
            "armor": 0.3,
            "material": 0.2,
            "tool": 0.1
        },
        "alchemist": {
            "potion": 0.5,
            "material": 0.3,
            "scroll": 0.1,
            "trinket": 0.1
        },
        "enchanter": {
            "scroll": 0.3,
            "accessory": 0.3,
            "trinket": 0.2,
            "material": 0.2
        },
        "armorer": {
            "armor": 0.6,
            "accessory": 0.2,
            "material": 0.1,
            "tool": 0.1
        },
        "jeweler": {
            "accessory": 0.6,
            "trinket": 0.3,
            "material": 0.1
        },
        "general": default_weights
    }
    
    return specializations.get(shop_type.lower(), default_weights)

def calculate_shop_price_modifier(
    shop_tier: int,
    economic_factors: Dict[str, float],
    item_rarity: str
) -> float:
    """
    Calculate price modifier for shop items based on economy and shop tier.
    
    Args:
        shop_tier: Quality tier of the shop (1-5)
        economic_factors: Economic factors from the region
        item_rarity: Rarity of the item
        
    Returns:
        Price modifier multiplier
    """
    # Base modifier starts at 1.0
    modifier = 1.0
    
    # Apply shop tier modifier (higher tier shops charge premium)
    tier_modifier = 1.0 + ((shop_tier - 1) * 0.05)  # +5% per tier above 1
    modifier *= tier_modifier
    
    # Apply economic factors
    if economic_factors:
        # Prosperity (higher prosperity = higher prices)
        prosperity = economic_factors.get("prosperity", 1.0)
        modifier *= prosperity
        
        # Scarcity (higher scarcity = higher prices)
        scarcity = economic_factors.get("scarcity", 1.0)
        modifier *= scarcity
        
        # Tax rate (higher taxes = higher prices)
        tax_rate = economic_factors.get("tax_rate", 0.1)
        modifier *= (1.0 + tax_rate)
    
    # Apply rarity modifier
    rarity_modifiers = {
        "common": 1.0,
        "uncommon": 1.2,
        "rare": 1.5,
        "epic": 2.0,
        "legendary": 3.0
    }
    rarity_modifier = rarity_modifiers.get(item_rarity.lower(), 1.0)
    modifier *= rarity_modifier
    
    # Ensure reasonable range
    return max(0.5, min(3.0, modifier))

def restock_shop_inventory(
    shop_id: int,
    current_inventory: List[Dict[str, Any]],
    shop_type: str = "general",
    shop_tier: int =.1,
    region_id: Optional[int] = None,
    faction_id: Optional[int] = None,
    max_items: int = 20
) -> List[Dict[str, Any]]:
    """
    Restock a shop's inventory, maintaining some existing items.
    
    Args:
        shop_id: Unique ID for the shop
        current_inventory: Current inventory items
        shop_type: Type of shop
        shop_tier: Tier/quality level of the shop (1-5)
        region_id: Optional ID of the region the shop is in
        faction_id: Optional ID of the faction that owns/influences the shop
        max_items: Maximum number of items after restocking
        
    Returns:
        Updated inventory list
    """
    from datetime import datetime, timedelta
    import random
    
    # Filter out sold out items
    current_inventory = [
        item for item in current_inventory 
        if item.get("shop_metadata", {}).get("quantity", 0) > 0
    ]
    
    # Update restock dates for existing items
    for item in current_inventory:
        if "shop_metadata" not in item:
            item["shop_metadata"] = {}
        
        # Restock existing items
        shop_meta = item["shop_metadata"]
        
        # Random chance to increase quantity if low
        current_qty = shop_meta.get("quantity", 1)
        if current_qty < 2 and random.random() < 0.7:  # 70% chance to restock if low
            # Determine restock amount based on item type/rarity
            rarity = item.get("rarity", "common").lower()
            item_type = item.get("item_type", "")
            
            if rarity in ["legendary", "epic"]:
                # Rare items rarely restock
                restock_amount = 1 if random.random() < 0.2 else 0
            elif rarity == "rare":
                restock_amount = random.randint(0, 1)
            elif item_type in ["potion", "scroll", "material"]:
                # Consumables restock more
                restock_amount = random.randint(1, 3)
            else:
                restock_amount = random.randint(0, 2)
            
            shop_meta["quantity"] = current_qty + restock_amount
        
        # Update restock date
        shop_meta["restock_date"] = (datetime.now() + timedelta(days=7)).isoformat()
    
    # Calculate how many new items to add
    current_count = len(current_inventory)
    new_items_count = max(0, max_items - current_count)
    
    # Generate new items if needed
    new_items = []
    if new_items_count > 0:
        new_items = generate_shop_inventory(
            shop_id=shop_id,
            shop_type=shop_type,
            shop_tier=shop_tier,
            region_id=region_id,
            faction_id=faction_id,
            restocking=True,
            count=new_items_count
        )
    
    # Combine and return updated inventory
    updated_inventory = current_inventory + new_items
    
    # Log analytics
    dispatcher = EventDispatcher.get_instance()
    dispatcher.publish_sync(ShopRestockEvent(
        shop_id=shop_id,
        shop_type=shop_type,
        shop_tier=shop_tier,
        previous_item_count=current_count,
        new_item_count=len(new_items),
        total_item_count=len(updated_inventory),
        region_id=region_id
    ))
    
    return updated_inventory

def purchase_item_from_shop(
    shop_id: int,
    inventory: List[Dict[str, Any]],
    item_index: int,
    character_id: int,
    quantity: int = 1,
    negotiation_bonus: int = 0,
    location_id: Optional[int] = None,
    region_id: Optional[int] = None
) -> Tuple[Dict[str, Any], int, List[Dict[str, Any]]]:
    """
    Purchases an item from a shop.
    
    Args:
        shop_id: ID of the shop
        inventory: Current inventory items
        item_index: Index of the item in the inventory
        character_id: ID of the character making the purchase
        quantity: Quantity to purchase
        negotiation_bonus: Bonus to negotiation (0-100)
        location_id: Optional ID of the location
        region_id: Optional ID of the region
        
    Returns:
        Tuple of (purchased item, final price, updated inventory)
    """
    # Clone the inventory to avoid modifying the original
    updated_inventory = deepcopy(inventory)
    
    # Check if the item exists
    if item_index < 0 or item_index >= len(updated_inventory):
        raise ValueError(f"Item index {item_index} out of bounds (0-{len(updated_inventory)-1})")
    
    # Get the item
    inventory_entry = updated_inventory[item_index]
    item = deepcopy(inventory_entry["item"])
    base_price = inventory_entry["price"]
    
    # Check if there's enough quantity
    if inventory_entry["quantity"] < quantity:
        raise ValueError(f"Not enough quantity available (requested: {quantity}, available: {inventory_entry['quantity']})")
    
    # Apply negotiation discount if any
    negotiation_discount = min(0.25, negotiation_bonus * 0.0025)  # 0.25% per point, max 25%
    final_price = int(base_price * (1.0 - negotiation_discount) * quantity)
    
    # Update inventory
    updated_inventory[item_index]["quantity"] -= quantity
    
    # Remove item if quantity reaches 0
    if updated_inventory[item_index]["quantity"] <= 0:
        updated_inventory.pop(item_index)
    
    # Emit purchase event
    dispatcher = EventDispatcher.get_instance()
    event = ShopItemEvent(
        event_type="shop.item.purchased",
        shop_id=shop_id,
        shop_name="Shop",  # Would need to be provided from outside
        item_id=item.get("id", 0),
        item_name=item.get("name", "Unknown Item"),
        item_rarity=item.get("rarity", "common"),
        price=final_price,
        character_id=character_id,
        location_id=location_id,
        region_id=region_id
    )
    dispatcher.publish_sync(event)
    
    # Track for analytics
    log_shop_transaction(
        character_id=character_id,
        shop_id=shop_id,
        items_bought=[item],
        items_sold=[],
        gold_spent=final_price,
        gold_earned=0,
        location_id=location_id,
        region_id=region_id
    )
    
    return item, final_price, updated_inventory

def sell_item_to_shop(
    shop_id: int,
    shop_type: str,
    shop_tier: int,
    item: Dict[str, Any],
    character_id: int,
    negotiation_bonus: int = 0,
    location_id: Optional[int] = None,
    region_id: Optional[int] = None
) -> int:
    """
    Sells an item to a shop.
    
    Args:
        shop_id: ID of the shop
        shop_type: Type of shop
        shop_tier: Tier/quality of the shop
        item: Item to sell
        character_id: ID of the character selling the item
        negotiation_bonus: Bonus to negotiation (0-100)
        location_id: Optional ID of the location
        region_id: Optional ID of the region
        
    Returns:
        The amount of gold received for the item
    """
    # Determine base value
    base_value = item.get("value", 10)
    
    # Calculate sell price based on shop type and item category
    category = item.get("category", "").lower()
    rarity = item.get("rarity", "common").lower()
    
    # Shops pay less for items (base: 40-60% of value depending on tier)
    base_percentage = 0.4 + (shop_tier * 0.05)  # Tier 1: 45%, Tier 5: 65%
    
    # Shops pay more for their specialty items
    specialty_match = {
        "blacksmith": ["weapon", "armor", "tool"],
        "alchemist": ["consumable", "ingredient", "potion"],
        "magic": ["magical_weapon", "magical_armor", "scroll", "potion", "trinket"],
        "clothing": ["clothing"],
        "jeweler": ["jewelry", "trinket"],
        "tavern": ["consumable"]
    }
    
    specialty_bonus = 0.0
    if shop_type in specialty_match and category in specialty_match.get(shop_type, []):
        specialty_bonus = 0.15  # 15% bonus for specialty items
    
    # Rarity bonus (shops pay more for rare items)
    rarity_bonus = {
        "common": 0.0,
        "uncommon": 0.05,
        "rare": 0.1,
        "epic": 0.15,
        "legendary": 0.2
    }.get(rarity, 0.0)
    
    # Apply negotiation bonus
    negotiation_bonus_pct = min(0.2, negotiation_bonus * 0.002)  # 0.2% per point, max 20%
    
    # Calculate final percentage
    final_percentage = base_percentage + specialty_bonus + rarity_bonus + negotiation_bonus_pct
    
    # Calculate final sell price
    sell_price = int(base_value * final_percentage)
    
    # Ensure minimum sell value (at least 1 gold)
    sell_price = max(1, sell_price)
    
    # Emit sell event
    dispatcher = EventDispatcher.get_instance()
    event = ShopItemEvent(
        event_type="shop.item.sold",
        shop_id=shop_id,
        shop_name=f"{shop_type.title()} (Tier {shop_tier})",
        item_id=item.get("id", 0),
        item_name=item.get("name", "Unknown Item"),
        item_rarity=item.get("rarity", "common"),
        price=sell_price,
        character_id=character_id,
        location_id=location_id,
        region_id=region_id
    )
    dispatcher.publish_sync(event)
    
    # Track for analytics
    log_shop_transaction(
        character_id=character_id,
        shop_id=shop_id,
        items_bought=[],
        items_sold=[item],
        gold_spent=0,
        gold_earned=sell_price,
        location_id=location_id,
        region_id=region_id
    )
    
    return sell_price

# =====================================================================
# === ITEM GENERATION =================================================
# =====================================================================

def generate_random_item(
    category: str,
    rarity: str = "common",
    magical: bool = False,
    min_level: int = 1,
    max_level: int = 10,
    faction_id: int = None,
    motif: str = None
) -> Dict[str, Any]:
    """
    Generates a random item of the specified category.
    
    Args:
        category: Type of item to generate
        rarity: Rarity level of the item
        magical: Whether to add magical effects
        min_level: Minimum level for the item
        max_level: Maximum level for the item
        faction_id: Optional ID of a faction for themed items
        motif: Optional motif to influence item generation
        
    Returns:
        Generated item data
    """
    # Select a level for the item
    level = randint(min_level, max_level)
    
    # Get base item stats based on category and level
    item = create_base_item(category, level)
    
    # Apply rarity to the item
    apply_rarity_to_item(item, rarity)
    
    # Apply magical effects if needed
    if magical:
        apply_magical_effects(item, rarity, level)
    
    # Apply faction/motif styling if provided
    if faction_id or motif:
        apply_thematic_elements(item, faction_id, motif)
    
    # Generate flavor text
    item["flavor_text"] = generate_flavor_text(item, faction_id, motif)
    
    # Generate a unique ID
    item["id"] = str(uuid4())
    
    # Add creation timestamp
    item["created_at"] = datetime.utcnow().isoformat()
    
    return item

def create_base_item(category: str, level: int) -> Dict[str, Any]:
    """
    Creates a base item of the specified category and level.
    
    Args:
        category: Type of item to create
        level: Level of the item
        
    Returns:
        Base item data
    """
    # Basic item template
    item = {
        "name": f"Level {level} {category.title()}",
        "category": category,
        "level": level,
        "value": 10 * level,
        "rarity": "common",
        "weight": 1.0,
        "description": f"A level {level} {category}."
    }
    
    # Customize based on category
    if category == "weapon":
        weapon_types = ["sword", "axe", "mace", "spear", "bow", "dagger", "staff", "wand"]
        weapon_type = choice(weapon_types)
        item["name"] = f"Level {level} {weapon_type.title()}"
        item["weapon_type"] = weapon_type
        item["damage"] = level + randint(1, 3)
        item["value"] = 15 * level
        item["weight"] = max(0.5, min(10.0, level * 0.3 + randint(-1, 2)))
    
    elif category == "armor":
        armor_types = ["helmet", "chestplate", "leggings", "boots", "gauntlets", "shield"]
        armor_type = choice(armor_types)
        item["name"] = f"Level {level} {armor_type.title()}"
        item["armor_type"] = armor_type
        item["defense"] = level + randint(0, 2)
        item["value"] = 12 * level
        item["weight"] = max(1.0, min(15.0, level * 0.5 + randint(-1, 2)))
    
    elif category == "consumable":
        consumable_types = ["potion", "food", "scroll", "elixir"]
        consumable_type = choice(consumable_types)
        item["name"] = f"Level {level} {consumable_type.title()}"
        item["consumable_type"] = consumable_type
        item["uses"] = randint(1, 3)
        item["value"] = 8 * level
        item["weight"] = 0.1 * randint(1, 5)
    
    elif category == "jewelry":
        jewelry_types = ["ring", "amulet", "bracelet", "earring", "necklace"]
        jewelry_type = choice(jewelry_types)
        item["name"] = f"Level {level} {jewelry_type.title()}"
        item["jewelry_type"] = jewelry_type
        item["value"] = 20 * level
        item["weight"] = 0.1
    
    elif category == "clothing":
        clothing_types = ["hat", "shirt", "pants", "gloves", "shoes", "belt", "cloak"]
        clothing_type = choice(clothing_types)
        item["name"] = f"Level {level} {clothing_type.title()}"
        item["clothing_type"] = clothing_type
        item["value"] = 5 * level
        item["weight"] = 0.5
    
    elif category == "tool":
        tool_types = ["pickaxe", "shovel", "hammer", "saw", "fishing rod", "cooking pot"]
        tool_type = choice(tool_types)
        item["name"] = f"Level {level} {tool_type.title()}"
        item["tool_type"] = tool_type
        item["value"] = 10 * level
        item["weight"] = 1.5
    
    elif category == "trinket":
        trinket_types = ["charm", "talisman", "token", "figurine", "gem"]
        trinket_type = choice(trinket_types)
        item["name"] = f"Level {level} {trinket_type.title()}"
        item["trinket_type"] = trinket_type
        item["value"] = 15 * level
        item["weight"] = 0.2
    
    # Add a material based on level
    item["material"] = get_material_for_level(level, category)
    
    # Update name with material
    item["name"] = f"{item['material'].title()} {item['name'].split(' ', 1)[1]}"
    
    return item

def get_material_for_level(level: int, category: str) -> str:
    """
    Determines an appropriate material for an item based on level.
    
    Args:
        level: Item level
        category: Item category
        
    Returns:
        Material name
    """
    if category in ["weapon", "armor", "tool"]:
        if level <= 3:
            return choice(["iron", "bronze", "copper"])
        elif level <= 7:
            return choice(["steel", "silver", "reinforced iron"])
        elif level <= 15:
            return choice(["mithril", "dwarven", "elven", "orichalcum"])
        else:
            return choice(["adamantine", "dragonbone", "star metal", "celestial"])
    elif category in ["jewelry", "trinket"]:
        if level <= 3:
            return choice(["copper", "bronze", "glass"])
        elif level <= 7:
            return choice(["silver", "gold", "jade"])
        elif level <= 15:
            return choice(["platinum", "crystal", "sapphire", "ruby"])
        else:
            return choice(["diamond", "obsidian", "dragonscale", "starstone"])
    elif category in ["clothing"]:
        if level <= 3:
            return choice(["cotton", "wool", "linen"])
        elif level <= 7:
            return choice(["leather", "silk", "velvet"])
        elif level <= 15:
            return choice(["elven silk", "dwarven wool", "phoenix feather"])
        else:
            return choice(["dragonscale", "celestial fiber", "void-woven"])
    else:  # consumables and others
        if level <= 3:
            return choice(["basic", "common", "simple"])
        elif level <= 7:
            return choice(["quality", "improved", "fine"])
        elif level <= 15:
            return choice(["superior", "excellent", "master"])
        else:
            return choice(["legendary", "mythical", "divine"])

def apply_rarity_to_item(item: Dict[str, Any], rarity: str) -> None:
    """
    Applies rarity modifiers to an item.
    
    Args:
        item: Item to modify
        rarity: Desired rarity level
    """
    # Set the item rarity
    item["rarity"] = rarity.lower()
    
    # Apply stat modifiers based on rarity
    rarity_multipliers = {
        "common": 1.0,
        "uncommon": 1.5,
        "rare": 2.5,
        "epic": 4.0,
        "legendary": 8.0
    }
    
    multiplier = rarity_multipliers.get(rarity.lower(), 1.0)
    
    # Apply value multiplier
    item["value"] = int(item["value"] * multiplier)
    
    # Apply stat multipliers if they exist
    if "damage" in item:
        item["damage"] = int(item["damage"] * multiplier)
    if "defense" in item:
        item["defense"] = int(item["defense"] * multiplier)
    
    # Add rarity prefix to name for uncommon and above
    if rarity.lower() != "common":
        rarity_prefixes = {
            "uncommon": ["Fine", "Quality", "Superior"],
            "rare": ["Exceptional", "Excellent", "Remarkable"],
            "epic": ["Magnificent", "Splendid", "Exquisite"],
            "legendary": ["Legendary", "Mythical", "Ancient"]
        }
        
        prefixes = rarity_prefixes.get(rarity.lower(), ["Special"])
        prefix = choice(prefixes)
        
        if not item["name"].startswith(prefix):
            item["name"] = f"{prefix} {item['name']}"
    
    # Add special description for higher rarities
    if rarity.lower() in ["rare", "epic", "legendary"]:
        item["description"] += f" This is a {rarity.lower()} item of exceptional quality."

def apply_magical_effects(item: Dict[str, Any], rarity: str, level: int) -> None:
    """
    Applies magical effects to an item.
    
    Args:
        item: Item to modify
        rarity: Rarity level of the item
        level: Level of the item
    """
    # Determine number of effects based on rarity
    effects_count = {
        "common": 0,
        "uncommon": randint(0, 1),
        "rare": randint(1, 2),
        "epic": randint(2, 3),
        "legendary": randint(3, 5)
    }.get(rarity.lower(), 0)
    
    # Don't add effects to common items
    if effects_count == 0:
        return
    
    # Initialize effects array
    if "effects" not in item:
        item["effects"] = []
    
    # Generate effects
    for _ in range(effects_count):
        effect_type = choice(["damage", "defense", "utility", "healing"])
        effect = generate_item_effect(effect_type, rarity)
        if effect:
            item["effects"].append(effect)
    
    # Add magical prefix/suffix to name
    if effects_count > 0 and "of" not in item["name"]:
        magical_suffixes = [
            "of Power", "of the Wise", "of the Berserker", "of Protection",
            "of Speed", "of the Fox", "of the Eagle", "of the Bear",
            "of Flames", "of Frost", "of Thunder", "of Shadows"
        ]
        suffix = choice(magical_suffixes)
        item["name"] = f"{item['name']} {suffix}"
    
    # Mark as magical
    item["is_magical"] = True
    
    # Add identification properties for high-tier items
    if rarity.lower() in ["rare", "epic", "legendary"]:
        item["name_revealed"] = False
        item["generated_name"] = item["name"]
        item["name"] = f"Mysterious {item['category'].title()}"
        item["effects_identified"] = []
    
    # Add visual effect description
    if "visual_effects" not in item:
        item["visual_effects"] = []
    
    # Add a visual effect based on rarity
    visual_effects = {
        "uncommon": "A faint glow surrounds the item.",
        "rare": "The item emits a soft, pulsing light.",
        "epic": "Mystical energies swirl around the item.",
        "legendary": "The item radiates powerful energy and seems to hum with power."
    }
    
    if rarity.lower() in visual_effects:
        item["visual_effects"].append({
            "type": "rarity",
            "description": visual_effects[rarity.lower()]
        })

def apply_thematic_elements(item: Dict[str, Any], faction_id: int = None, motif: str = None) -> None:
    """
    Applies faction or motif-based thematic elements to an item.
    
    Args:
        item: Item to modify
        faction_id: Optional ID of a faction for themed items
        motif: Optional motif to influence item generation
    """
    # Apply faction theming if provided
    if faction_id:
        # In a real implementation, this would look up faction data
        # For now, use placeholder faction data
        faction_themes = {
            1: {"name": "Imperial Legion", "style": "military", "colors": ["gold", "red"]},
            2: {"name": "Merchant Guild", "style": "ornate", "colors": ["purple", "gold"]},
            3: {"name": "Forest Keepers", "style": "natural", "colors": ["green", "brown"]},
            4: {"name": "Arcane Society", "style": "magical", "colors": ["blue", "silver"]}
        }
        
        faction = faction_themes.get(faction_id, {"name": "Unknown", "style": "standard", "colors": ["gray"]})
        
        # Add faction styling
        if "appearance" not in item:
            item["appearance"] = {}
        
        item["appearance"]["faction_style"] = faction["style"]
        item["appearance"]["faction_colors"] = faction["colors"]
        item["appearance"]["description"] = f"This item bears the markings of the {faction['name']}."
        
        # Add faction prefix to name if high enough rarity
        if item["rarity"] in ["rare", "epic", "legendary"]:
            if faction["name"] not in item["name"]:
                if "generated_name" in item:
                    item["generated_name"] = f"{faction['name']} {item['generated_name']}"
                else:
                    item["name"] = f"{faction['name']} {item['name']}"
    
    # Apply motif theming if provided
    if motif:
        # Apply motif-specific modifications
        motif_themes = {
            "fire": {"element": "fire", "colors": ["red", "orange"]},
            "ice": {"element": "ice", "colors": ["blue", "white"]},
            "nature": {"element": "nature", "colors": ["green", "brown"]},
            "undeath": {"element": "undeath", "colors": ["purple", "black"]},
            "sea": {"element": "water", "colors": ["blue", "cyan"]},
            "mountain": {"element": "earth", "colors": ["brown", "gray"]},
            "sky": {"element": "air", "colors": ["light blue", "white"]}
        }
        
        theme = motif_themes.get(motif, {"element": "neutral", "colors": ["beige"]})
        
        # Add motif styling
        if "appearance" not in item:
            item["appearance"] = {}
        
        item["appearance"]["motif_element"] = theme["element"]
        item["appearance"]["motif_colors"] = theme["colors"]
        
        if "description" in item["appearance"]:
            item["appearance"]["description"] += f" It is styled with {theme['element']} elements."
        else:
            item["appearance"]["description"] = f"This item is styled with {theme['element']} elements."
        
        # Add motif effect for magical items
        if item.get("is_magical") and random() < 0.5:
            motif_effects = {
                "fire": "A faint warmth emanates from the item.",
                "ice": "The item feels cool to the touch.",
                "nature": "Small vines or leaves occasionally sprout from the item.",
                "undeath": "The item seems to absorb light around it.",
                "sea": "The item occasionally drips with water that evaporates moments later.",
                "mountain": "The item feels heavier than it looks and is remarkably sturdy.",
                "sky": "The item feels unusually light and occasionally emits a gentle breeze."
            }
            
            effect_desc = motif_effects.get(motif, "The item has a distinctive aura.")
            
            if "visual_effects" not in item:
                item["visual_effects"] = []
            
            item["visual_effects"].append({
                "type": "motif",
                "description": effect_desc
            })

def generate_flavor_text(item: Dict[str, Any], faction_id: int = None, motif: str = None) -> str:
    """
    Generates flavor text for an item.
    
    Args:
        item: Item data
        faction_id: Optional ID of a faction
        motif: Optional motif
        
    Returns:
        Generated flavor text
    """
    category = item.get("category", "").lower()
    rarity = item.get("rarity", "common").lower()
    
    # Base flavor text templates by category
    flavor_templates = {
        "weapon": [
            "A {quality} weapon that has seen many battles.",
            "This {material} weapon feels {weight} in your hand.",
            "The {material} glints dangerously in the light."
        ],
        "armor": [
            "A {quality} piece of armor that offers solid protection.",
            "This {material} armor is {weight} but provides excellent defense.",
            "The craftsmanship of this {material} piece is {quality}."
        ],
        "consumable": [
            "A {quality} concoction with a distinctive smell.",
            "This {material} mixture seems {potency}.",
            "The container is labeled with {quality} script."
        ],
        "jewelry": [
            "This {material} jewelry piece catches the light beautifully.",
            "A {quality} ornament that would impress nobles.",
            "The {material} has been worked with {quality} craftsmanship."
        ],
        "clothing": [
            "A {quality} garment made of {material}.",
            "This clothing item feels {weight} and {comfort}.",
            "The stitching is {quality} and built to last."
        ],
        "tool": [
            "A {quality} tool for its intended purpose.",
            "This {material} tool feels {weight} and reliable.",
            "The craftsmanship is {quality} and practical."
        ],
        "trinket": [
            "A curious {material} trinket of unknown origin.",
            "This small item seems {quality} yet mysterious.",
            "The {material} has been shaped with {quality} detail."
        ]
    }
    
    # Get templates for this category or use generic ones
    templates = flavor_templates.get(category, ["A {quality} item made of {material}."])
    
    # Select one template randomly
    template = choice(templates)
    
    # Fill in the template variables
    quality_terms = {
        "common": ["average", "serviceable", "adequate", "functional"],
        "uncommon": ["good", "solid", "reliable", "well-crafted"],
        "rare": ["excellent", "superior", "remarkable", "distinguished"],
        "epic": ["exquisite", "magnificent", "extraordinary", "masterful"],
        "legendary": ["legendary", "mythical", "godlike", "transcendent"]
    }
    
    material = item.get("material", "common")
    quality = choice(quality_terms.get(rarity, ["decent"]))
    weight = choice(["light", "balanced", "substantial", "hefty"])
    comfort = choice(["comfortable", "smooth", "pleasant to wear", "well-fitted"])
    potency = choice(["potent", "effective", "powerful", "strong"])
    
    flavor = template.format(
        material=material,
        quality=quality,
        weight=weight,
        comfort=comfort,
        potency=potency
    )
    
    # Add additional motif-based flavor if applicable
    if motif:
        motif_descriptions = {
            "fire": " It has a warm, fiery appearance.",
            "ice": " It seems unusually cold to the touch.",
            "nature": " Subtle patterns reminiscent of leaves and vines adorn it.",
            "undeath": " There's something unsettling about its appearance.",
            "sea": " It seems to carry the faint scent of the ocean.",
            "mountain": " It has a sturdy, mountain-like resilience.",
            "sky": " It feels unusually light, as if touched by the sky."
        }
        flavor += motif_descriptions.get(motif, "")
    
    # Add faction-based flavor if applicable
    if faction_id:
        faction_descriptions = {
            1: " It bears the distinctive markings of the Imperial Legion.",
            2: " The craftsmanship shows the signature style of the Merchant Guild.",
            3: " It carries subtle signs of the Forest Keepers' handiwork.",
            4: " Arcane Society runes and symbols are etched into its surface."
        }
        flavor += faction_descriptions.get(faction_id, "")
    
    # Add magical flavor for magical items
    if item.get("is_magical") and item.get("effects", []):
        magical_hints = [
            " There's a faint magical aura surrounding it.",
            " It occasionally emits a subtle glow.",
            " Strange energies seem to flow within it.",
            " You feel a tingle when touching it.",
            " It seems to resonate with magical energy."
        ]
        flavor += choice(magical_hints)
    
    return flavor

def get_enhancement_requirements(item: Dict[str, Any], target_level: int) -> Dict[str, Any]:
    """
    Get the requirements needed to enhance an item to a target level.
    
    Args:
        item: The item to enhance
        target_level: The target enhancement level
        
    Returns:
        Dictionary with enhancement requirements
    """
    # Get current enhancement level
    current_level = item.get("enhancement_level", 0)
    
    # Cannot enhance beyond maximum level
    if current_level >= 10:
        return {
            "can_enhance": False,
            "max_level_reached": True,
            "error": "Item has reached maximum enhancement level."
        }
    
    # Cannot skip levels
    if target_level > current_level + 1:
        return {
            "can_enhance": False,
            "max_level_reached": False,
            "error": f"Cannot enhance directly to level {target_level}. Must enhance to level {current_level + 1} first."
        }
    
    # Base requirements
    rarity = item.get("rarity", "common").lower()
    item_type = item.get("item_type", item.get("category", "item")).lower()
    
    # Material requirements increase with level and rarity
    materials = {}
    gold_cost = 0
    skill_level = 0
    
    # Rarity affects base costs
    rarity_multipliers = {
        "common": 1,
        "uncommon": 2,
        "rare": 4,
        "epic": 8,
        "legendary": 16
    }
    rarity_mult = rarity_multipliers.get(rarity, 1)
    
    # Calculate base gold cost
    # Formula: (100 * rarity_mult * (current_level + 1)^2)
    gold_cost = 100 * rarity_mult * ((current_level + 1) ** 2)
    
    # Required skill level
    skill_level = 2 * (current_level + 1)
    if rarity == "rare":
        skill_level += 5
    elif rarity == "epic":
        skill_level += 10
    elif rarity == "legendary":
        skill_level += 15
    
    # Required materials depend on item type and level
    if item_type == "weapon":
        materials["metal_ingot"] = current_level + 1
        if current_level >= 4:
            materials["magical_essence"] = current_level - 3
        if current_level >= 7:
            materials["rare_gem"] = current_level - 6
    
    elif item_type == "armor":
        materials["leather_hide"] = current_level + 1
        materials["metal_ingot"] = max(1, current_level)
        if current_level >= 4:
            materials["magical_essence"] = current_level - 3
    
    elif item_type == "accessory":
        materials["fine_thread"] = current_level + 1
        if current_level >= 3:
            materials["rare_gem"] = current_level - 2
        if current_level >= 6:
            materials["magical_essence"] = current_level - 5
    
    else:
        # Generic materials for other item types
        materials["crafting_component"] = current_level + 2
        if current_level >= 5:
            materials["magical_essence"] = current_level - 4
    
    # High-level enhancements may require special materials
    if current_level >= 5:
        # Special material based on rarity
        if rarity == "epic":
            materials["epic_core"] = 1
        elif rarity == "legendary":
            materials["legendary_fragment"] = 1
    
    # Success chance decreases with level
    base_success_chance = 100 - (current_level * 5)
    # Rarity also affects success chance
    if rarity == "rare":
        base_success_chance -= 5
    elif rarity == "epic":
        base_success_chance -= 10
    elif rarity == "legendary":
        base_success_chance -= 15
    
    # Ensure minimum chance
    base_success_chance = max(25, base_success_chance)
    
    return {
        "can_enhance": True,
        "max_level_reached": False,
        "current_level": current_level,
        "target_level": target_level,
        "gold_cost": gold_cost,
        "materials": materials,
        "required_skill_level": skill_level,
        "base_success_chance": base_success_chance
    }

def attempt_enhance_item(
    item: Dict[str, Any], 
    character_id: int, 
    skill_level: int = 0,
    use_catalyst: bool = False,
    catalyst_bonus: int = 0,
    force_success: bool = False
) -> Tuple[Dict[str, Any], bool, str]:
    """
    Attempt to enhance an item to the next level.
    
    Args:
        item: The item to enhance
        character_id: ID of the character attempting enhancement
        skill_level: Character's applicable crafting skill level
        use_catalyst: Whether using a catalyst to improve chances
        catalyst_bonus: Success bonus from catalyst (percentage points)
        force_success: Force success (admin/debug feature)
        
    Returns:
        Tuple of (updated item, success boolean, result message)
    """
    # Make a copy of the item to avoid modifying the original
    updated_item = item.copy()
    
    # Get current enhancement level and target level
    current_level = updated_item.get("enhancement_level", 0)
    target_level = current_level + 1
    
    # Check if enhancement is possible
    requirements = get_enhancement_requirements(updated_item, target_level)
    if not requirements["can_enhance"]:
        return updated_item, False, requirements.get("error", "Enhancement not possible.")
    
    # Record pre-enhancement state for event logging
    original_rarity = updated_item.get("rarity", "common")
    
    # Calculate success chance
    success_chance = requirements["base_success_chance"]
    
    # Apply skill modifier
    skill_modifier = max(0, (skill_level - requirements["required_skill_level"]) * 2)
    success_chance += skill_modifier
    
    # Apply catalyst bonus
    if use_catalyst:
        success_chance += catalyst_bonus
    
    # Cap at 95% to always leave some chance of failure (unless forced)
    success_chance = min(95, success_chance)
    
    # Determine success
    success = force_success
    if not success:
        import random
        roll = random.randint(1, 100)
        success = roll <= success_chance
    
    result_message = ""
    
    if success:
        # Enhance the item
        
        # Update the enhancement level
        updated_item["enhancement_level"] = target_level
        
        # Update item stats
        if "base_stats" not in updated_item:
            updated_item["base_stats"] = {}
            
        # Apply enhancement bonuses to stats
        for stat, value in updated_item["base_stats"].items():
            # Increase stats by 5-10% per level
            increase_factor = 1.0 + (target_level * random.uniform(0.05, 0.1))
            updated_item["base_stats"][stat] = int(value * increase_factor)
        
        # Check for rarity upgrade chance
        rarity_upgrade_chance = target_level * 2  # 2% per level
        rarity_upgrade_roll = random.randint(1, 100)
        
        rarity_upgrade = False
        new_rarity = original_rarity
        
        # Check for rarity upgrade only if not already legendary
        if original_rarity.lower() != "legendary" and rarity_upgrade_roll <= rarity_upgrade_chance:
            rarity_upgrade = True
            
            # Get next rarity
            rarity_order = ["common", "uncommon", "rare", "epic", "legendary"]
            current_index = rarity_order.index(original_rarity.lower())
            
            if current_index < len(rarity_order) - 1:
                new_rarity = rarity_order[current_index + 1]
                updated_item["rarity"] = new_rarity
                
                # Add special effect for rarity upgrade
                if "effects" not in updated_item:
                    updated_item["effects"] = []
                
                # Generate a new effect based on the new rarity
                effect_id = f"enhance_{len(updated_item['effects'])}_upgrade_{current_index+1}"
                
                new_effect = {
                    "id": effect_id,
                    "name": f"Enhanced {new_rarity.title()} Power",
                    "description": f"This item has been enhanced to {new_rarity} quality, increasing its power.",
                    "type": "enhancement",
                    "power": target_level * (current_index + 2)
                }
                
                updated_item["effects"].append(new_effect)
                
                result_message = f"Enhancement successful! The item upgraded to {new_rarity} rarity!"
            else:
                result_message = "Enhancement successful!"
        else:
            result_message = "Enhancement successful!"
            
    else:
        # Enhancement failed
        
        # Failure penalty (small chance to decrease level or damage item)
        failure_penalty_chance = min(25, current_level * 5)
        penalty_roll = random.randint(1, 100)
        
        if penalty_roll <= failure_penalty_chance and current_level > 0:
            # Apply penalty
            updated_item["enhancement_level"] = current_level - 1
            result_message = "Enhancement failed! The item's enhancement level decreased by 1."
        else:
            result_message = "Enhancement failed. The item remains unchanged."
    
    # Create enhancement event
    dispatcher = EventDispatcher.get_instance()
    dispatcher.publish_sync(ItemEnhancementEvent(
        item_id=updated_item.get("id", 0),
        item_name=updated_item.get("name", "Unknown Item"),
        original_rarity=original_rarity,
        new_rarity=updated_item.get("rarity", original_rarity),
        enhancement_type="level_up",
        enhancement_level=updated_item.get("enhancement_level", 0),
        success=success,
        character_id=character_id,
        craft_skill_used="blacksmithing" if "weapon" in item.get("item_type", "").lower() or "armor" in item.get("item_type", "").lower() else "enchanting"
    ))
    
    # Also log to analytics
    dispatcher.publish_sync(LootAnalyticsEvent(
        event_category="enhancement",
        event_action="attempt",
        item_id=updated_item.get("id", 0),
        item_name=updated_item.get("name", "Unknown Item"),
        item_rarity=updated_item.get("rarity", "common"),
        character_id=character_id,
        value=success_chance,
        metadata={
            "success": success,
            "original_level": current_level,
            "new_level": updated_item.get("enhancement_level", 0),
            "skill_level": skill_level,
            "use_catalyst": use_catalyst,
            "catalyst_bonus": catalyst_bonus
        }
    ))
    
    return updated_item, success, result_message

def add_enchantment_to_item(
    item: Dict[str, Any],
    enchantment: Dict[str, Any],
    character_id: int,
    skill_level: int = 0,
    use_catalyst: bool = False,
    catalyst_bonus: int = 0
) -> Tuple[Dict[str, Any], bool, str]:
    """
    Add a new enchantment (effect) to an item.
    
    Args:
        item: The item to enchant
        enchantment: The enchantment to add
        character_id: ID of the character performing enchantment
        skill_level: Character's applicable enchanting skill level
        use_catalyst: Whether using a catalyst to improve chances
        catalyst_bonus: Success bonus from catalyst (percentage points)
        
    Returns:
        Tuple of (updated item, success boolean, result message)
    """
    # Make a copy of the item to avoid modifying the original
    updated_item = item.copy()
    
    # Check if item already has this enchantment
    if "effects" in updated_item:
        for effect in updated_item.get("effects", []):
            if effect.get("id") == enchantment.get("id"):
                return updated_item, False, "This item already has this enchantment."
    
    # Get rarity for difficulty calculation
    rarity = updated_item.get("rarity", "common").lower()
    
    # Base success chance depends on rarity
    base_chance = {
        "common": 85,
        "uncommon": 70,
        "rare": 55,
        "epic": 40,
        "legendary": 25
    }.get(rarity, 50)
    
    # Adjust based on skill
    skill_modifier = (skill_level - 10) * 2  # +2% per skill level above 10
    
    # Adjust based on existing enchantments
    existing_effect_count = len(updated_item.get("effects", []))
    effect_penalty = existing_effect_count * 10  # -10% per existing effect
    
    # Calculate final success chance
    success_chance = base_chance + skill_modifier - effect_penalty
    
    # Add catalyst bonus
    if use_catalyst:
        success_chance += catalyst_bonus
    
    # Ensure minimum and maximum chances
    success_chance = max(5, min(95, success_chance))
    
    # Determine success
    import random
    roll = random.randint(1, 100)
    success = roll <= success_chance
    
    result_message = ""
    
    if success:
        # Add the enchantment to the item
        if "effects" not in updated_item:
            updated_item["effects"] = []
        
        # Assign a unique ID if needed
        if "id" not in enchantment:
            enchantment = enchantment.copy()  # Copy to avoid modifying original
            enchantment["id"] = f"ench_{len(updated_item['effects'])}_{random.randint(1000, 9999)}"
        
        updated_item["effects"].append(enchantment)
        
        # Possibly upgrade rarity for powerful enchantments
        enchantment_power = enchantment.get("power", 1)
        rarity_order = ["common", "uncommon", "rare", "epic", "legendary"]
        current_index = rarity_order.index(rarity)
        
        # Very powerful enchantments can increase rarity
        if enchantment_power >= 10 and current_index < len(rarity_order) - 1:
            rarity_upgrade_chance = enchantment_power * 2  # 2% per power point
            if random.randint(1, 100) <= rarity_upgrade_chance:
                new_rarity = rarity_order[current_index + 1]
                updated_item["rarity"] = new_rarity
                result_message = f"Enchantment successful! The magical power increased the item's rarity to {new_rarity}!"
            else:
                result_message = f"Enchantment successful! The item now has the '{enchantment.get('name', 'New')}' effect."
        else:
            result_message = f"Enchantment successful! The item now has the '{enchantment.get('name', 'New')}' effect."
    else:
        # Enchantment failed
        
        # Small chance of damaging the item for powerful enchantments
        enchantment_power = enchantment.get("power", 1)
        if enchantment_power >= 8 and existing_effect_count > 0:
            damage_chance = enchantment_power * 3
            if random.randint(1, 100) <= damage_chance:
                # Remove a random effect
                if updated_item.get("effects", []):
                    removed_effect = random.choice(updated_item["effects"])
                    updated_item["effects"].remove(removed_effect)
                    result_message = f"Enchantment failed! The magical backlash removed the '{removed_effect.get('name', 'Existing')}' effect."
                else:
                    result_message = "Enchantment failed."
            else:
                result_message = "Enchantment failed. The item remains unchanged."
        else:
            result_message = "Enchantment failed. The item remains unchanged."
    
    # Create enhancement event
    dispatcher = EventDispatcher.get_instance()
    dispatcher.publish_sync(ItemEnhancementEvent(
        item_id=updated_item.get("id", 0),
        item_name=updated_item.get("name", "Unknown Item"),
        original_rarity=rarity,
        new_rarity=updated_item.get("rarity", rarity),
        enhancement_type="enchantment",
        enhancement_level=len(updated_item.get("effects", [])),
        success=success,
        character_id=character_id,
        craft_skill_used="enchanting"
    ))
    
    # Also log to analytics
    dispatcher.publish_sync(LootAnalyticsEvent(
        event_category="enchantment",
        event_action="attempt",
        item_id=updated_item.get("id", 0),
        item_name=updated_item.get("name", "Unknown Item"),
        item_rarity=updated_item.get("rarity", "common"),
        character_id=character_id,
        value=success_chance,
        metadata={
            "success": success,
            "enchantment_name": enchantment.get("name", "Unknown"),
            "enchantment_power": enchantment.get("power", 1),
            "skill_level": skill_level,
            "use_catalyst": use_catalyst,
            "catalyst_bonus": catalyst_bonus
        }
    ))
    
    return updated_item, success, result_message

def reforge_item(
    item: Dict[str, Any],
    character_id: int,
    target_stats: Dict[str, int] = None,
    keep_effects: bool = True,
    skill_level: int = 0
) -> Tuple[Dict[str, Any], bool, str]:
    """
    Reforge an item to modify its base stats.
    
    Args:
        item: The item to reforge
        character_id: ID of the character performing reforging
        target_stats: Optional specific stats to target (None for random)
        keep_effects: Whether to keep existing magical effects
        skill_level: Character's applicable crafting skill level
        
    Returns:
        Tuple of (updated item, success boolean, result message)
    """
    # Make a copy of the item to avoid modifying the original
    updated_item = item.copy()
    
    # Get base stats or initialize if not present
    if "base_stats" not in updated_item:
        updated_item["base_stats"] = {}
    
    # Record original stats for comparison
    original_stats = updated_item["base_stats"].copy()
    
    # Get item details for calculation
    rarity = updated_item.get("rarity", "common").lower()
    enhancement_level = updated_item.get("enhancement_level", 0)
    
    # Base success chance depends on rarity and enhancement level
    base_chance = {
        "common": 90,
        "uncommon": 75,
        "rare": 60,
        "epic": 45,
        "legendary": 30
    }.get(rarity, 60)
    
    # Enhancement level makes reforging harder
    enhancement_penalty = enhancement_level * 3
    
    # Skill level improves chances
    skill_bonus = skill_level * 2
    
    # Calculate final success chance
    success_chance = base_chance - enhancement_penalty + skill_bonus
    
    # Ensure reasonable range
    success_chance = max(5, min(95, success_chance))
    
    # Determine success
    import random
    roll = random.randint(1, 100)
    success = roll <= success_chance
    
    result_message = ""
    
    if success:
        # Reforge successful - update stats
        
        # If target stats provided, try to move towards those
        if target_stats:
            new_stats = {}
            for stat, target_value in target_stats.items():
                current_value = original_stats.get(stat, 0)
                
                # Move 10-30% towards target
                move_percentage = random.uniform(0.1, 0.3)
                difference = target_value - current_value
                change = int(difference * move_percentage)
                
                # Apply change
                new_stats[stat] = current_value + change
                
            # Add original stats not in target
            for stat, value in original_stats.items():
                if stat not in new_stats:
                    # Randomize slightly
                    variation = random.uniform(0.9, 1.1)
                    new_stats[stat] = int(value * variation)
        else:
            # Random reforge
            new_stats = {}
            for stat, value in original_stats.items():
                # Randomize up to ±20%
                variation = random.uniform(0.8, 1.2)
                new_stats[stat] = int(value * variation)
                
            # Possibly add a new stat
            if random.random() < 0.2:  # 20% chance
                # Simple stat pool for demonstration
                potential_stats = ["strength", "dexterity", "intelligence", "vitality", 
                                "armor", "magic_resist", "critical_chance", "critical_damage"]
                # Filter out existing stats
                available_stats = [s for s in potential_stats if s not in new_stats]
                
                if available_stats:
                    new_stat = random.choice(available_stats)
                    # Base value depends on rarity
                    base_values = {
                        "common": 1,
                        "uncommon": 2,
                        "rare": 4,
                        "epic": 7,
                        "legendary": 10
                    }
                    base_value = base_values.get(rarity, 2)
                    new_stats[new_stat] = base_value
        
        # Apply new stats
        updated_item["base_stats"] = new_stats
        
        # Handle effects
        if not keep_effects:
            # Remove all effects except those from enhancement
            if "effects" in updated_item:
                enhancement_effects = [
                    effect for effect in updated_item["effects"]
                    if effect.get("type") == "enhancement"
                ]
                updated_item["effects"] = enhancement_effects
                result_message = "Reforge successful! The item's magical effects were reset."
            else:
                result_message = "Reforge successful!"
        else:
            result_message = "Reforge successful!"
    else:
        # Reforge failed
        
        # Determine penalty
        severe_failure = roll < 10  # Critical failure on very low roll
        
        if severe_failure:
            # Apply severe penalty
            for stat in original_stats:
                # Reduce stats by 10-20%
                penalty = random.uniform(0.1, 0.2)
                updated_item["base_stats"][stat] = int(original_stats[stat] * (1 - penalty))
            
            result_message = "Reforge failed! The item's quality was reduced."
        else:
            # No change
            result_message = "Reforge failed. The item remains unchanged."
    
    # Create event
    dispatcher = EventDispatcher.get_instance()
    dispatcher.publish_sync(ItemEnhancementEvent(
        item_id=updated_item.get("id", 0),
        item_name=updated_item.get("name", "Unknown Item"),
        original_rarity=rarity,
        new_rarity=updated_item.get("rarity", rarity),
        enhancement_type="reforge",
        enhancement_level=updated_item.get("enhancement_level", 0),
        success=success,
        character_id=character_id,
        craft_skill_used="blacksmithing" if "weapon" in item.get("item_type", "").lower() or "armor" in item.get("item_type", "").lower() else "crafting"
    ))
    
    # Log analytics
    dispatcher.publish_sync(LootAnalyticsEvent(
        event_category="reforge",
        event_action="attempt",
        item_id=updated_item.get("id", 0),
        item_name=updated_item.get("name", "Unknown Item"),
        item_rarity=updated_item.get("rarity", "common"),
        character_id=character_id,
        value=success_chance,
        metadata={
            "success": success,
            "skill_level": skill_level,
            "keep_effects": keep_effects,
            "roll": roll
        }
    ))
    
    return updated_item, success, result_message

def generate_item_with_context(
    item_type: str,
    rarity: str = "common",
    level: int = 1,
    location_id: Optional[int] = None,
    region_id: Optional[int] = None,
    faction_id: Optional[int] = None,
    is_quest_item: bool = False,
    thematic_tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate an item with contextual details based on location, region, or faction.
    
    Args:
        item_type: Type of item to generate
        rarity: Rarity of the item
        level: Level/power of the item
        location_id: Optional specific location ID
        region_id: Optional region ID for regional theming
        faction_id: Optional faction ID for faction theming
        is_quest_item: Whether this is a quest item
        thematic_tags: Optional thematic tags to influence generation
        
    Returns:
        Generated item with contextual details
    """
    # Generate base item
    item = generate_item(item_type, rarity, level)
    
    # Add quest item flag if needed
    if is_quest_item:
        item["is_quest_item"] = True
        
        # Quest items are always at least uncommon
        if item.get("rarity", "").lower() == "common":
            item["rarity"] = "uncommon"
        
        # Quest items should be identified
        item["identified"] = True
        
        # Add quest tag if thematic tags exist
        if "thematic_tags" not in item:
            item["thematic_tags"] = []
        
        item["thematic_tags"].append("quest")
    
    # Apply location-specific theming
    if location_id:
        # Normally we would fetch location details from database
        # For now, just use location ID for randomization seed
        import random
        random.seed(location_id)
        
        item["found_at_location_id"] = location_id
        
        # If we don't have region or faction yet, there's a chance to infer from location
        if not region_id and random.random() < 0.7:  # 70% chance
            # Normally would look up region from location
            region_id = (location_id % 5) + 1
        
        if not faction_id and random.random() < 0.4:  # 40% chance
            # Normally would look up potential faction from location
            faction_id = (location_id % 5) + 1
    
    # Apply thematic tags if provided
    if thematic_tags:
        if "thematic_tags" not in item:
            item["thematic_tags"] = []
        
        item["thematic_tags"].extend(thematic_tags)
    
    # Apply faction theming if applicable
    if faction_id:
        item = apply_faction_motifs(item, faction_id)
    
    # Apply regional theming if applicable
    if region_id:
        item = apply_regional_motifs(item, region_id)
    
    # Create loot generation event
    dispatcher = EventDispatcher.get_instance()
    
    # Create base event data
    event_data = {
        "monster_levels": [level],
        "gold_amount": 0,
        "item_count": 1,
        "has_quest_item": is_quest_item,
        "has_magical_item": rarity not in ["common", "uncommon"],
        "rarity_level": rarity,
        "source_type": "contextual",
        "location_id": location_id,
        "region_id": region_id
    }
    
    # Dispatch event
    dispatcher.publish_sync(LootGeneratedEvent(**event_data))
    
    # Log to analytics
    dispatcher.publish_sync(LootAnalyticsEvent(
        event_category="generation",
        event_action="contextual_item",
        item_id=item.get("id", "0"),
        item_name=item.get("name", "Unknown Item"),
        item_rarity=item.get("rarity", "common"),
        character_id=0,  # No character involved in generation
        value=item.get("value", 0),
        metadata={
            "item_type": item_type,
            "level": level,
            "location_id": location_id,
            "region_id": region_id,
            "faction_id": faction_id,
            "is_quest_item": is_quest_item,
            "thematic_tags": item.get("thematic_tags", [])
        }
    ))
    
    return item
