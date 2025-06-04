"""
Core business logic for loot system - Pure Business Logic

This module contains core loot business logic including motif application,
pricing adjustments, and item modifications. Pure business logic only.
"""

from typing import Dict, List, Any, Tuple, Optional, Protocol
from datetime import datetime, timedelta
import math
import random
import hashlib

# Import shared functions to avoid duplication
from .shared_functions import (
    group_equipment_by_type,
    gpt_name_and_flavor,
    merge_loot_sets,
    apply_biome_to_loot_table,
    get_current_supply,
    get_current_demand,
    apply_economic_factors_to_price
)


# Business Logic Protocols
class LootEventPublisher(Protocol):
    """Protocol for publishing loot-related events"""
    
    def publish_loot_event(self, event_data: Dict[str, Any]) -> None:
        """Publish loot event"""
        ...


class PriceAnalytics(Protocol):
    """Protocol for price analytics and logging"""
    
    def log_price_adjustment(self, item_id: int, item_name: str, old_price: int, new_price: int, 
                           multiplier: float, reason: str, region_id: int) -> None:
        """Log price adjustment"""
        ...


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


def adjust_price_for_supply_demand(
    base_price: int, 
    item_name: str, 
    item_id: int,
    region_id: int,
    price_analytics: Optional[PriceAnalytics] = None
) -> int:
    """
    Adjust item price based on supply and demand in the region.
    
    Args:
        base_price: Starting price
        item_name: Name of the item
        item_id: ID of the item
        region_id: ID of the region
        price_analytics: Optional analytics logger
        
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
    
    # Apply the adjustment
    if ratio > 1.5:  # High demand, low supply
        price_multiplier = 1.0 + (ratio - 1.0) * 0.3 * volatility
    elif ratio < 0.7:  # Low demand, high supply
        price_multiplier = 1.0 - (1.0 - ratio) * 0.2 * volatility
    else:
        price_multiplier = 1.0  # Balanced
    
    # Clamp to reasonable bounds
    price_multiplier = max(0.3, min(3.0, price_multiplier))
    
    adjusted_price = int(base_price * price_multiplier)
    
    # Log the adjustment if significant and analytics available
    if abs(price_multiplier - 1.0) > 0.1 and price_analytics:
        reason = f"Supply/Demand: {supply}/{demand} (ratio: {ratio:.2f})"
        price_analytics.log_price_adjustment(
            item_id, item_name, base_price, adjusted_price, price_multiplier, reason, region_id
        )
    
    return adjusted_price


def apply_motif_to_prices(
    base_price: int, 
    item_name: str, 
    item_id: int,
    region_id: int, 
    motif: str,
    price_analytics: Optional[PriceAnalytics] = None
) -> int:
    """
    Adjust item price based on the active motif.
    
    Args:
        base_price: Starting price
        item_name: Name of the item
        item_id: ID of the item
        region_id: ID of the region
        motif: The current motif affecting the region
        price_analytics: Optional analytics logger
        
    Returns:
        Adjusted price
    """
    # Default: no change
    price_multiplier = 1.0
    reason = f"Motif: {motif} (no effect)"
    
    # Apply effects based on motif themes
    motif = motif.lower()
    
    if motif == "wealth" or motif == "prosperity":
        # All prices slightly higher due to prosperity
        price_multiplier = 1.2
        reason = f"Motif: {motif} (prosperity premium)"
        
        # Luxury items even more expensive
        if "luxury" in item_name.lower() or "jewelry" in item_name.lower():
            price_multiplier = 1.5
            reason = f"Motif: {motif} (luxury demand)"
    
    elif motif == "death" or motif == "ruin":
        # Most prices lower due to economic decline
        price_multiplier = 0.8
        reason = f"Motif: {motif} (economic decline)"
        
        # But weapons and protective items more expensive
        if "weapon" in item_name.lower() or "armor" in item_name.lower() or "protection" in item_name.lower():
            price_multiplier = 1.3
            reason = f"Motif: {motif} (danger premium)"
    
    elif motif == "transformation" or motif == "change":
        # Prices more volatile - random adjustment
        volatility = random.uniform(0.7, 1.4)
        price_multiplier = volatility
        reason = f"Motif: {motif} (market volatility)"
    
    elif motif == "conflict" or motif == "war":
        # War economy effects
        if "weapon" in item_name.lower() or "armor" in item_name.lower():
            price_multiplier = 1.8
            reason = f"Motif: {motif} (war demand)"
        elif "luxury" in item_name.lower() or "decoration" in item_name.lower():
            price_multiplier = 0.5
            reason = f"Motif: {motif} (luxuries devalued)"
    
    adjusted_price = int(base_price * price_multiplier)
    
    # Log significant changes if analytics available
    if abs(price_multiplier - 1.0) > 0.1 and price_analytics:
        price_analytics.log_price_adjustment(
            item_id, item_name, base_price, adjusted_price, price_multiplier, reason, region_id
        )
    
    return adjusted_price


def apply_event_to_prices(
    base_price: int, 
    item_name: str, 
    item_id: int,
    region_id: int, 
    event_type: str,
    price_analytics: Optional[PriceAnalytics] = None
) -> int:
    """
    Adjust item price based on special events.
    
    Args:
        base_price: Starting price
        item_name: Name of the item
        item_id: ID of the item
        region_id: ID of the region
        event_type: Type of event affecting prices
        price_analytics: Optional analytics logger
        
    Returns:
        Adjusted price
    """
    price_multiplier = 1.0
    reason = f"Event: {event_type} (no effect)"
    
    # Apply event-based adjustments
    event_type = event_type.lower()
    
    if event_type == "festival" or event_type == "celebration":
        # Increased prices during festivities
        price_multiplier = 1.3
        reason = f"Event: {event_type} (festival markup)"
        
        # Luxury items especially expensive
        if "luxury" in item_name.lower() or "food" in item_name.lower():
            price_multiplier = 1.6
            reason = f"Event: {event_type} (celebration demand)"
    
    elif event_type == "plague" or event_type == "disaster":
        # Mixed effects - some items more expensive, others cheaper
        if "medicine" in item_name.lower() or "healing" in item_name.lower():
            price_multiplier = 2.0
            reason = f"Event: {event_type} (critical need)"
        elif "luxury" in item_name.lower():
            price_multiplier = 0.3
            reason = f"Event: {event_type} (luxuries abandoned)"
        else:
            price_multiplier = 0.8
            reason = f"Event: {event_type} (economic disruption)"
    
    elif event_type == "harvest" or event_type == "abundance":
        # Generally lower prices due to abundance
        price_multiplier = 0.8
        reason = f"Event: {event_type} (abundant supply)"
        
        # Food especially cheap
        if "food" in item_name.lower() or "provision" in item_name.lower():
            price_multiplier = 0.5
            reason = f"Event: {event_type} (harvest surplus)"
    
    elif event_type == "siege" or event_type == "blockade":
        # Scarcity drives up prices
        price_multiplier = 1.8
        reason = f"Event: {event_type} (supply shortage)"
        
        # Essential items extremely expensive
        if "weapon" in item_name.lower() or "food" in item_name.lower() or "medicine" in item_name.lower():
            price_multiplier = 3.0
            reason = f"Event: {event_type} (critical shortage)"
    
    adjusted_price = int(base_price * price_multiplier)
    
    # Log significant changes if analytics available
    if abs(price_multiplier - 1.0) > 0.1 and price_analytics:
        price_analytics.log_price_adjustment(
            item_id, item_name, base_price, adjusted_price, price_multiplier, reason, region_id
        )
    
    return adjusted_price


def sell_item_to_shop(
    shop_id: int,
    shop_type: str,
    shop_tier: int,
    item: Dict[str, Any],
    character_id: int,
    negotiation_bonus: int = 0,
    location_id: Optional[int] = None,
    region_id: Optional[int] = None,
    event_publisher: Optional[LootEventPublisher] = None
) -> int:
    """
    Calculate the price for selling an item to a shop using business logic.
    
    Args:
        shop_id: ID of the shop
        shop_type: Type of shop
        shop_tier: Quality tier of the shop
        item: Item being sold
        character_id: ID of character selling
        negotiation_bonus: Bonus from negotiation skills
        location_id: Optional location ID
        region_id: Optional region ID
        event_publisher: Optional event publisher
        
    Returns:
        Final sell price
    """
    # Base value calculation
    base_value = item.get("value", 10)
    condition = item.get("condition", 100)  # 0-100 condition
    
    # Condition affects price
    condition_multiplier = condition / 100.0
    adjusted_value = int(base_value * condition_multiplier)
    
    # Shop type affects buy-back rate
    shop_multipliers = {
        "general_store": 0.4,  # Buy at 40% of value
        "weapon_smith": 0.6,   # Specialized shops pay more
        "armor_crafter": 0.6,
        "magic_shop": 0.7,
        "black_market": 0.8,   # Best prices but risky
        "alchemist": 0.5
    }
    
    # Check if shop specializes in this item type
    item_category = item.get("category", "misc").lower()
    is_specialized = (
        (shop_type == "weapon_smith" and "weapon" in item_category) or
        (shop_type == "armor_crafter" and "armor" in item_category) or
        (shop_type == "magic_shop" and "magical" in item.get("properties", {}).get("type", "")) or
        (shop_type == "alchemist" and "consumable" in item_category)
    )
    
    shop_multiplier = shop_multipliers.get(shop_type, 0.4)
    if is_specialized:
        shop_multiplier *= 1.3  # 30% bonus for specialized shops
    
    # Shop tier affects prices
    tier_bonus = (shop_tier - 1) * 0.1  # +10% per tier above 1
    shop_multiplier += tier_bonus
    
    # Apply negotiation bonus
    negotiation_multiplier = 1.0 + (negotiation_bonus * 0.05)  # 5% per negotiation point
    
    # Calculate final price
    final_price = int(adjusted_value * shop_multiplier * negotiation_multiplier)
    final_price = max(1, final_price)  # Minimum 1 gold
    
    # Publish event if publisher available
    if event_publisher:
        event_data = {
            "event_type": "shop.item_sold",
            "shop_id": shop_id,
            "shop_type": shop_type,
            "item_id": item.get("id", "unknown"),
            "item_name": item.get("name", "Unknown Item"),
            "character_id": character_id,
            "sell_price": final_price,
            "base_value": base_value,
            "condition": condition,
            "negotiation_bonus": negotiation_bonus,
            "timestamp": datetime.utcnow().isoformat()
        }
        event_publisher.publish_loot_event(event_data)
    
    return final_price


def apply_rarity_to_item(item: Dict[str, Any], rarity: str) -> None:
    """
    Apply rarity-based modifications to an item using business logic.
    
    Args:
        item: Item to modify
        rarity: Rarity to apply (common, uncommon, rare, epic, legendary)
    """
    rarity = rarity.lower()
    
    # Rarity affects various item properties
    rarity_modifiers = {
        "common": {
            "value_multiplier": 1.0,
            "stat_bonus": 0,
            "max_effects": 0,
            "quality_bonus": 0
        },
        "uncommon": {
            "value_multiplier": 2.0,
            "stat_bonus": 1,
            "max_effects": 1,
            "quality_bonus": 10
        },
        "rare": {
            "value_multiplier": 5.0,
            "stat_bonus": 3,
            "max_effects": 2,
            "quality_bonus": 25
        },
        "epic": {
            "value_multiplier": 15.0,
            "stat_bonus": 8,
            "max_effects": 3,
            "quality_bonus": 50
        },
        "legendary": {
            "value_multiplier": 50.0,
            "stat_bonus": 20,
            "max_effects": 5,
            "quality_bonus": 100
        }
    }
    
    modifiers = rarity_modifiers.get(rarity, rarity_modifiers["common"])
    
    # Apply value multiplier
    if "value" in item:
        item["value"] = int(item["value"] * modifiers["value_multiplier"])
    
    # Apply stat bonuses
    if "stats" in item and modifiers["stat_bonus"] > 0:
        for stat_name, stat_value in item["stats"].items():
            if isinstance(stat_value, (int, float)):
                item["stats"][stat_name] = stat_value + modifiers["stat_bonus"]
    
    # Set rarity and max effects
    item["rarity"] = rarity
    item["max_effects"] = modifiers["max_effects"]
    
    # Apply quality bonus
    if modifiers["quality_bonus"] > 0:
        item["quality_bonus"] = item.get("quality_bonus", 0) + modifiers["quality_bonus"]


def apply_magical_effects(item: Dict[str, Any], rarity: str, level: int) -> None:
    """
    Apply magical effects to an item based on rarity and level using business logic.
    
    Args:
        item: Item to enchant
        rarity: Item rarity
        level: Character/area level for scaling
    """
    max_effects = item.get("max_effects", 0)
    if max_effects == 0:
        return
    
    # Generate effects based on rarity
    effects = []
    for i in range(max_effects):
        effect_power = 1 + (level // 5)  # Effect power scales with level
        
        if rarity in ["rare", "epic", "legendary"]:
            # Higher rarity items get more powerful effects
            effect_power += {"rare": 1, "epic": 3, "legendary": 6}[rarity]
        
        effect = {
            "name": f"Magic Effect {i+1}",
            "power": effect_power,
            "type": "enchantment"
        }
        effects.append(effect)
    
    item["magical_effects"] = effects
    item["is_magical"] = True


def apply_thematic_elements(item: Dict[str, Any], faction_id: int = None, motif: str = None) -> None:
    """
    Apply thematic elements based on faction and motif using business logic.
    
    Args:
        item: Item to modify
        faction_id: Optional faction ID for theming
        motif: Optional motif for theming
    """
    properties = item.get("properties", {})
    
    # Apply faction theming
    if faction_id:
        faction_themes = {
            1: {"theme": "royal", "color": "gold", "symbol": "crown"},
            2: {"theme": "military", "color": "steel", "symbol": "sword"},
            3: {"theme": "mystical", "color": "purple", "symbol": "star"},
            4: {"theme": "natural", "color": "green", "symbol": "leaf"},
            5: {"theme": "shadowy", "color": "black", "symbol": "dagger"}
        }
        
        theme = faction_themes.get(faction_id, {"theme": "generic", "color": "gray", "symbol": "circle"})
        properties.update({
            "faction_theme": theme["theme"],
            "faction_color": theme["color"],
            "faction_symbol": theme["symbol"],
            "faction_id": faction_id
        })
    
    # Apply motif theming
    if motif:
        motif_effects = {
            "prosperity": {"bonus_value": 1.2, "appearance": "gleaming"},
            "death": {"curse_chance": 0.1, "appearance": "ominous"},
            "war": {"combat_bonus": 2, "appearance": "battle-worn"},
            "nature": {"natural_bonus": 1, "appearance": "organic"},
            "magic": {"magic_bonus": 1, "appearance": "glowing"}
        }
        
        effect = motif_effects.get(motif.lower(), {})
        if effect:
            properties.update({
                "motif": motif,
                "motif_effects": effect
            })
    
    item["properties"] = properties


def add_enchantment_to_item(
    item: Dict[str, Any],
    enchantment: Dict[str, Any],
    character_id: int,
    skill_level: int = 0,
    use_catalyst: bool = False,
    catalyst_bonus: int = 0,
    event_publisher: Optional[LootEventPublisher] = None
) -> Tuple[Dict[str, Any], bool, str]:
    """
    Add an enchantment to an item using business logic.
    
    Args:
        item: Item to enchant
        enchantment: Enchantment to add
        character_id: ID of character performing enchantment
        skill_level: Enchanting skill level
        use_catalyst: Whether using a catalyst
        catalyst_bonus: Bonus from catalyst
        event_publisher: Optional event publisher
        
    Returns:
        Tuple of (modified_item, success, message)
    """
    # Calculate success chance based on skill and item rarity
    base_chance = 0.5  # 50% base chance
    skill_bonus = skill_level * 0.02  # 2% per skill level
    catalyst_bonus_chance = catalyst_bonus * 0.1 if use_catalyst else 0
    
    # Rarity affects difficulty
    rarity_penalties = {
        "common": 0,
        "uncommon": -0.1,
        "rare": -0.2,
        "epic": -0.3,
        "legendary": -0.4
    }
    
    rarity = item.get("rarity", "common").lower()
    rarity_penalty = rarity_penalties.get(rarity, 0)
    
    success_chance = base_chance + skill_bonus + catalyst_bonus_chance + rarity_penalty
    success_chance = max(0.05, min(0.95, success_chance))  # Clamp between 5% and 95%
    
    # Determine success
    success = random.random() < success_chance
    
    if success:
        # Add enchantment to item
        enchantments = item.get("enchantments", [])
        enchantments.append(enchantment)
        item["enchantments"] = enchantments
        
        # Increase item value
        enchantment_value = enchantment.get("value", 100)
        item["value"] = item.get("value", 10) + enchantment_value
        
        message = f"Successfully enchanted {item.get('name', 'item')} with {enchantment.get('name', 'enchantment')}"
        
        # Publish success event if publisher available
        if event_publisher:
            event_data = {
                "event_type": "item.enchanted",
                "item_id": item.get("id", "unknown"),
                "item_name": item.get("name", "Unknown Item"),
                "enchantment_name": enchantment.get("name", "Unknown Enchantment"),
                "character_id": character_id,
                "skill_level": skill_level,
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            event_publisher.publish_loot_event(event_data)
    else:
        message = f"Failed to enchant {item.get('name', 'item')}"
        
        # Publish failure event if publisher available
        if event_publisher:
            event_data = {
                "event_type": "item.enchantment_failed",
                "item_id": item.get("id", "unknown"),
                "item_name": item.get("name", "Unknown Item"),
                "character_id": character_id,
                "skill_level": skill_level,
                "success": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            event_publisher.publish_loot_event(event_data)
    
    return item, success, message


def get_region_economic_factors(region_id: int) -> Dict[str, float]:
    """
    Get economic factors for a region using business logic.
    
    Args:
        region_id: ID of the region
        
    Returns:
        Dictionary with economic factors
    """
    # Generate consistent factors based on region ID
    random.seed(region_id)
    
    factors = {
        "prosperity": random.uniform(0.5, 1.5),
        "trade_volume": random.uniform(0.7, 1.3),
        "resource_availability": random.uniform(0.6, 1.4),
        "political_stability": random.uniform(0.5, 1.2),
        "population_density": random.uniform(0.4, 1.6)
    }
    
    # Reset random seed
    random.seed()
    
    return factors


# Deprecated functions for backward compatibility - delegate to new implementations
def select_rarity():
    """Deprecated - use item generation functions in loot_core instead"""
    return "common"


def select_item_type():
    """Deprecated - use item generation functions in loot_core instead"""
    return "misc"


# Redirect functions to main implementations
def generate_loot_bundle(*args, **kwargs):
    """Redirect to loot_core.generate_loot_bundle"""
    from .loot_core import generate_loot_bundle as core_generate
    return core_generate(*args, **kwargs)


def generate_location_specific_loot(*args, **kwargs):
    """Redirect to loot_core.generate_location_specific_loot"""
    from .loot_core import generate_location_specific_loot as core_generate
    return core_generate(*args, **kwargs)


def get_dynamic_item_price(*args, **kwargs):
    """Redirect to loot_shop.get_dynamic_item_price"""
    from .loot_shop import get_dynamic_item_price
    return get_dynamic_item_price(*args, **kwargs)


def get_item_description_for_player(*args, **kwargs):
    """Redirect to identification_system"""
    return {"description": "Item description functionality moved to identification system"}


def attempt_identify_item(*args, **kwargs):
    """Redirect to identification_system.identify_item_by_skill"""
    from .identification_system import identify_item_by_skill
    return identify_item_by_skill(*args, **kwargs)


def identify_item_completely(*args, **kwargs):
    """Redirect to identification_system"""
    from .identification_system import identify_item_at_shop
    return identify_item_at_shop(*args, **kwargs)


def enhance_item(*args, **kwargs):
    """Redirect to loot_manager.enhance_item"""
    from ..services.loot_manager import LootBusinessManager
    manager = LootBusinessManager(None)
    return manager.enhance_item(*args, **kwargs)


def generate_random_item(*args, **kwargs):
    """Redirect to loot_core item generation"""
    from .loot_core import generate_item_identity
    return generate_item_identity(*args, **kwargs)


def generate_shop_inventory(*args, **kwargs):
    """Redirect to loot_shop.generate_shop_inventory"""
    from .loot_shop import generate_shop_inventory
    return generate_shop_inventory(*args, **kwargs)


def update_shop_prices(*args, **kwargs):
    """Redirect to loot_shop price functions"""
    return {"message": "Use specific price adjustment functions from loot_shop module"}

