"""
Shop system functionality for the loot system - Pure Business Logic

This module provides shop-specific functions including dynamic pricing,
specialization, economic factors, and inventory management.
Pure business logic with no technical dependencies.
"""

import random
from typing import Dict, List, Any, Optional, Protocol
from copy import deepcopy
import math

from backend.systems.loot.utils.loot_core import generate_item_identity, calculate_item_power_score


# Business Logic Protocols
class ShopEventPublisher(Protocol):
    """Protocol for publishing shop-related events"""
    
    def publish_shop_event(self, event_data: Dict[str, Any]) -> None:
        """Publish shop event"""
        ...


# Data structures for shop specialization and economic factors
class ShopSpecialization:
    """Container for shop specialization data"""
    
    def __init__(self, shop_type: str, modifiers: Dict[str, float]):
        self.shop_type = shop_type
        self.modifiers = modifiers
        

class EconomicFactors:
    """Container for regional economic factor data"""
    
    def __init__(self, region_id: int, factors: Dict[str, float]):
        self.region_id = region_id
        self.factors = factors


# Custom exception class
class ShopError(Exception):
    """Exception raised for shop operation failures"""
    pass


def get_shop_type_specialization(shop_type: str) -> Dict[str, float]:
    """
    Get shop specialization data including item type weights and pricing modifiers.
    
    Args:
        shop_type: Type of shop
        
    Returns:
        Dictionary with specialization data
    """
    specializations = {
        "weapon_smith": {
            "item_weights": {
                "weapon": 0.7,
                "armor": 0.1,
                "accessory": 0.1,
                "consumable": 0.05,
                "crafting_material": 0.05
            },
            "price_modifier": 1.2,
            "quality_bonus": 0.3,
            "rarity_weights": {
                "common": 0.4,
                "uncommon": 0.3,
                "rare": 0.2,
                "epic": 0.08,
                "legendary": 0.02
            }
        },
        "armor_crafter": {
            "item_weights": {
                "armor": 0.7,
                "weapon": 0.1,
                "accessory": 0.15,
                "consumable": 0.03,
                "crafting_material": 0.02
            },
            "price_modifier": 1.15,
            "quality_bonus": 0.25,
            "rarity_weights": {
                "common": 0.45,
                "uncommon": 0.3,
                "rare": 0.18,
                "epic": 0.06,
                "legendary": 0.01
            }
        },
        "general_store": {
            "item_weights": {
                "weapon": 0.2,
                "armor": 0.2,
                "accessory": 0.2,
                "consumable": 0.3,
                "crafting_material": 0.1
            },
            "price_modifier": 1.0,
            "quality_bonus": 0.0,
            "rarity_weights": {
                "common": 0.6,
                "uncommon": 0.25,
                "rare": 0.12,
                "epic": 0.025,
                "legendary": 0.005
            }
        },
        "magic_shop": {
            "item_weights": {
                "weapon": 0.25,
                "armor": 0.25,
                "accessory": 0.35,
                "consumable": 0.1,
                "crafting_material": 0.05
            },
            "price_modifier": 2.0,
            "quality_bonus": 0.5,
            "rarity_weights": {
                "common": 0.1,
                "uncommon": 0.3,
                "rare": 0.4,
                "epic": 0.15,
                "legendary": 0.05
            }
        },
        "black_market": {
            "item_weights": {
                "weapon": 0.3,
                "armor": 0.2,
                "accessory": 0.3,
                "consumable": 0.15,
                "crafting_material": 0.05
            },
            "price_modifier": 1.8,
            "quality_bonus": 0.4,
            "rarity_weights": {
                "common": 0.2,
                "uncommon": 0.25,
                "rare": 0.35,
                "epic": 0.15,
                "legendary": 0.05
            }
        },
        "alchemist": {
            "item_weights": {
                "weapon": 0.05,
                "armor": 0.05,
                "accessory": 0.2,
                "consumable": 0.6,
                "crafting_material": 0.1
            },
            "price_modifier": 1.3,
            "quality_bonus": 0.2,
            "rarity_weights": {
                "common": 0.5,
                "uncommon": 0.3,
                "rare": 0.15,
                "epic": 0.04,
                "legendary": 0.01
            }
        }
    }
    
    return specializations.get(shop_type, specializations["general_store"])


def get_region_economic_factors(region_id: int) -> Dict[str, float]:
    """
    Get economic factors for a region that affect pricing.
    
    Args:
        region_id: ID of the region
        
    Returns:
        Dictionary with economic factors
    """
    # Business logic for generating consistent regional economic factors
    base_factors = {
        "prosperity": 1.0,
        "trade_volume": 1.0,
        "resource_availability": 1.0,
        "political_stability": 1.0,
        "population_density": 1.0,
        "distance_from_capital": 1.0
    }
    
    # Use region_id to generate consistent but varied factors
    random.seed(region_id)
    
    factors = {}
    for factor, base_value in base_factors.items():
        # Generate factors between 0.5 and 1.5
        variation = random.uniform(-0.5, 0.5)
        factors[factor] = max(0.5, min(1.5, base_value + variation))
    
    # Reset random seed
    random.seed()
    
    return factors


def get_dynamic_item_price(
    item: Dict[str, Any], 
    shop_type: str, 
    region_id: int,
    shop_tier: int = 1,
    supply_demand_modifier: float = 1.0
) -> int:
    """
    Calculate dynamic item price based on multiple factors.
    
    Args:
        item: Item to price
        shop_type: Type of shop
        region_id: Region where shop is located
        shop_tier: Quality tier of the shop
        supply_demand_modifier: Supply/demand adjustment
        
    Returns:
        Final item price in gold
    """
    try:
        # Base item value
        base_value = 10
        
        # Rarity multiplier
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 2.5,
            "rare": 8.0,
            "epic": 25.0,
            "legendary": 100.0
        }
        rarity = item.get("rarity", "common").lower()
        base_value *= rarity_multipliers.get(rarity, 1.0)
        
        # Level/power multiplier
        level = item.get("level", 1)
        power_score = calculate_item_power_score(item)
        base_value *= (1 + level * 0.2 + power_score * 0.1)
        
        # Shop specialization modifier
        specialization = get_shop_type_specialization(shop_type)
        base_value *= specialization["price_modifier"]
        
        # Shop tier modifier
        tier_multiplier = 1.0 + (shop_tier - 1) * 0.3
        base_value *= tier_multiplier
        
        # Regional economic factors
        economic_factors = get_region_economic_factors(region_id)
        prosperity_modifier = economic_factors.get("prosperity", 1.0)
        trade_modifier = economic_factors.get("trade_volume", 1.0)
        stability_modifier = economic_factors.get("political_stability", 1.0)
        
        economic_multiplier = (prosperity_modifier + trade_modifier + stability_modifier) / 3
        base_value *= economic_multiplier
        
        # Supply and demand
        base_value *= supply_demand_modifier
        
        # Item category modifier for shop specialization
        item_category = item.get("category", "misc")
        category_weights = specialization["item_weights"]
        if item_category in category_weights:
            # Higher weight = lower price (shop specializes in this)
            weight = category_weights[item_category]
            category_modifier = 1.0 - (weight * 0.2)  # Up to 20% discount for specialization
            base_value *= category_modifier
        
        return max(1, int(base_value))
    except Exception as e:
        logger.error(f"Failed to calculate dynamic price: {e}")
        return 10


def calculate_shop_price_modifier(
    shop: Dict[str, Any], 
    item: Dict[str, Any], 
    context: Dict[str, Any] = None
) -> float:
    """
    Calculate price modifier for a specific shop and item combination.
    
    Args:
        shop: Shop data
        item: Item data
        context: Additional context
        
    Returns:
        Price modifier (1.0 = no change)
    """
    try:
        modifier = 1.0
        
        shop_type = shop.get("type", "general_store")
        shop_tier = shop.get("tier", 1)
        
        # Shop reputation modifier
        reputation = shop.get("reputation", 50)  # 0-100 scale
        reputation_modifier = 0.8 + (reputation / 100) * 0.4  # 0.8 to 1.2
        modifier *= reputation_modifier
        
        # Shop tier modifier
        tier_modifier = 1.0 + (shop_tier - 1) * 0.2
        modifier *= tier_modifier
        
        # Item rarity vs shop specialization
        specialization = get_shop_type_specialization(shop_type)
        item_rarity = item.get("rarity", "common").lower()
        rarity_weights = specialization["rarity_weights"]
        
        if item_rarity in rarity_weights:
            rarity_weight = rarity_weights[item_rarity]
            # Higher weight = better price for customer
            rarity_modifier = 1.0 - (rarity_weight * 0.1)
            modifier *= rarity_modifier
        
        # Context modifiers
        if context:
            # Player reputation with shop
            player_reputation = context.get("player_reputation", 0)
            if player_reputation > 0:
                rep_discount = min(0.2, player_reputation / 100 * 0.2)
                modifier *= (1.0 - rep_discount)
            
            # Bulk purchase discount
            quantity = context.get("quantity", 1)
            if quantity > 1:
                bulk_discount = min(0.15, (quantity - 1) * 0.02)
                modifier *= (1.0 - bulk_discount)
        
        return modifier
    except Exception as e:
        logger.error(f"Failed to calculate shop price modifier: {e}")
        return 1.0


def generate_shop_inventory(
    shop_type: str = "general_store",
    shop_tier: int = 1,
    region_id: Optional[int] = None,
    faction_id: Optional[int] = None,
    equipment_pool: Dict[str, List[Dict[str, Any]]] = None,
    item_effects: List[Dict[str, Any]] = None,
    count: int = 10
) -> List[Dict[str, Any]]:
    """
    Generate shop inventory based on shop type and other factors.
    
    Args:
        shop_type: Type of shop
        shop_tier: Quality tier of shop
        region_id: Region where shop is located
        faction_id: Controlling faction
        equipment_pool: Available equipment items
        item_effects: Available magical effects
        count: Number of items to generate
        
    Returns:
        List of items in shop inventory
    """
    try:
        if equipment_pool is None:
            equipment_pool = {"weapon": [], "armor": [], "gear": [], "accessory": [], "consumable": []}
        if item_effects is None:
            item_effects = []
        
        inventory = []
        specialization = get_shop_type_specialization(shop_type)
        item_weights = specialization["item_weights"]
        rarity_weights = specialization["rarity_weights"]
        quality_bonus = specialization["quality_bonus"]
        
        for _ in range(count):
            # Select item category based on shop specialization
            category = random.choices(
                list(item_weights.keys()),
                weights=list(item_weights.values())
            )[0]
            
            # Get items of this category
            available_items = equipment_pool.get(category, [])
            if not available_items:
                continue
            
            # Select base item
            base_item = deepcopy(random.choice(available_items))
            
            # Select rarity based on shop specialization
            rarity = random.choices(
                list(rarity_weights.keys()),
                weights=list(rarity_weights.values())
            )[0]
            
            base_item["rarity"] = rarity
            
            # Apply quality bonus from shop tier
            if shop_tier > 1:
                level_bonus = (shop_tier - 1) + random.randint(0, shop_tier)
                base_item["level"] = base_item.get("level", 1) + level_bonus
            
            # Add magical effects for higher rarity items
            if rarity in ["rare", "epic", "legendary"] and item_effects:
                max_effects = {"rare": 2, "epic": 4, "legendary": 6}[rarity]
                effects_count = random.randint(1, max_effects)
                
                effects = []
                for i in range(effects_count):
                    effect = random.choice(item_effects)
                    effects.append({
                        "level": i + 1,
                        "effect": effect
                    })
                base_item["effects"] = effects
            
            # Generate item identity
            base_item = generate_item_identity(base_item)
            
            # Calculate price
            price = get_dynamic_item_price(
                item=base_item,
                shop_type=shop_type,
                region_id=region_id or 1,
                shop_tier=shop_tier
            )
            base_item["shop_price"] = price
            
            # Add shop-specific metadata
            base_item["shop_metadata"] = {
                "shop_type": shop_type,
                "shop_tier": shop_tier,
                "region_id": region_id,
                "faction_id": faction_id,
                "restocked_at": None,
                "times_viewed": 0
            }
            
            inventory.append(base_item)
        
        return inventory
    except Exception as e:
        logger.error(f"Failed to generate shop inventory: {e}")
        return []


def restock_shop_inventory(
    current_inventory: List[Dict[str, Any]],
    shop_type: str = "general_store",
    shop_tier: int = 1,
    region_id: Optional[int] = None,
    faction_id: Optional[int] = None,
    equipment_pool: Dict[str, List[Dict[str, Any]]] = None,
    item_effects: List[Dict[str, Any]] = None,
    restock_percentage: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Restock shop inventory by replacing some items.
    
    Args:
        current_inventory: Current shop inventory
        shop_type: Type of shop
        shop_tier: Quality tier of shop
        region_id: Region where shop is located
        faction_id: Controlling faction
        equipment_pool: Available equipment items
        item_effects: Available magical effects
        restock_percentage: Percentage of inventory to replace
        
    Returns:
        Updated inventory
    """
    try:
        if not current_inventory:
            return generate_shop_inventory(
                shop_type=shop_type,
                shop_tier=shop_tier,
                region_id=region_id,
                faction_id=faction_id,
                equipment_pool=equipment_pool,
                item_effects=item_effects
            )
        
        # Calculate how many items to replace
        items_to_replace = max(1, int(len(current_inventory) * restock_percentage))
        
        # Remove random items
        new_inventory = current_inventory.copy()
        for _ in range(items_to_replace):
            if new_inventory:
                new_inventory.pop(random.randint(0, len(new_inventory) - 1))
        
        # Generate new items
        new_items = generate_shop_inventory(
            shop_type=shop_type,
            shop_tier=shop_tier,
            region_id=region_id,
            faction_id=faction_id,
            equipment_pool=equipment_pool,
            item_effects=item_effects,
            count=items_to_replace
        )
        
        # Add new items
        new_inventory.extend(new_items)
        
        return new_inventory
    except Exception as e:
        logger.error(f"Failed to restock shop inventory: {e}")
        return current_inventory


def calculate_sell_price(
    item: Dict[str, Any],
    shop_type: str,
    shop_tier: int = 1,
    region_id: int = 1,
    player_reputation: int = 0
) -> int:
    """
    Calculate the price a shop will pay for an item.
    
    Args:
        item: Item being sold
        shop_type: Type of shop
        shop_tier: Quality tier of shop
        region_id: Region where shop is located
        player_reputation: Player's reputation with shop
        
    Returns:
        Price shop will pay for the item
    """
    try:
        # Get base market price
        market_price = get_dynamic_item_price(
            item=item,
            shop_type=shop_type,
            region_id=region_id,
            shop_tier=shop_tier
        )
        
        # Shops typically buy at 30-60% of market price
        base_buy_percentage = 0.4
        
        # Shop tier affects buy price
        tier_bonus = (shop_tier - 1) * 0.05
        buy_percentage = base_buy_percentage + tier_bonus
        
        # Player reputation affects buy price
        reputation_bonus = min(0.2, player_reputation / 100 * 0.2)
        buy_percentage += reputation_bonus
        
        # Shop specialization affects buy price
        specialization = get_shop_type_specialization(shop_type)
        item_category = item.get("category", "misc")
        category_weights = specialization["item_weights"]
        
        if item_category in category_weights:
            weight = category_weights[item_category]
            # Higher weight = better buy price (shop wants this item type)
            category_bonus = weight * 0.2
            buy_percentage += category_bonus
        
        # Cap the buy percentage
        buy_percentage = min(0.8, buy_percentage)
        
        return max(1, int(market_price * buy_percentage))
    except Exception as e:
        logger.error(f"Failed to calculate sell price: {e}")
        return 1


def get_shop_specialization_bonus(shop_type: str, item: Dict[str, Any]) -> float:
    """
    Get specialization bonus for an item in a specific shop type.
    
    Args:
        shop_type: Type of shop
        item: Item to check
        
    Returns:
        Specialization bonus multiplier
    """
    specialization = get_shop_type_specialization(shop_type)
    item_category = item.get("category", "misc")
    category_weights = specialization["item_weights"]
    
    if item_category in category_weights:
        weight = category_weights[item_category]
        return 1.0 + (weight * specialization["quality_bonus"])
    
    return 1.0 