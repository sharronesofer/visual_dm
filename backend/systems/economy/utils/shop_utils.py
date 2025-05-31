"""
Shop utilities for the economy system.

This module provides shop-related utilities integrated with the EconomyManager
for consistent pricing, inventory management, and economic calculations.
"""

import logging
from datetime import datetime, timedelta
# from firebase_admin import db  # TODO: Replace with proper database integration
import random
from typing import Dict, Any, List, Optional, Tuple, Union
from uuid import uuid4

from backend.systems.economy.services.economy_manager import EconomyManager

# Try to import from backend systems, fallback if not available
try:
    from backend.systems.equipment.inventory_utils import equipment_rules
    from backend.systems.equipment.loot_utils import generate_item_identity
except ImportError:
    # Fallback stubs if equipment system not available
    equipment_rules = {}
    def generate_item_identity(*args, **kwargs):
        return {"id": str(uuid4()), "name": "Unknown Item"}

# Constants for UI and display
RARITY_COLORS = {
    "common": "gray",
    "uncommon": "blue",
    "rare": "green",
    "epic": "purple",
    "legendary": "orange"
}

def get_shop_inventory(npc_id):
    inventory = db.reference(f"/npcs/{npc_id}/shop_inventory").get() or {}

    for item_id, item in inventory.items():
        if item.get("name_revealed"):
            rarity = item.get("rarity", "common")
            item["rarity_color"] = RARITY_COLORS.get(rarity, "gray")

    return inventory

def get_expected_gold_at_level(level):
    """
    Calculate the expected gold a player should have at a given level.
    Used for scaling shop prices appropriately.
    
    Args:
        level: Player level
        
    Returns:
        Expected gold amount
    """
    xp_to_level = {
        1: 0,
        2: 300,
        3: 900,
        4: 2700,
        5: 6500,
        6: 14000,
        7: 23000,
        8: 34000,
        9: 48000,
        10: 64000
    }
    xp = xp_to_level.get(level, 64000 + (level - 10) * 20000)
    return xp // 10

def calculate_sale_value(item, player_level, economy_manager=None):
    """
    Calculate how much a shop will pay for an item.
    
    Args:
        item: Item data
        player_level: Player's level
        economy_manager: Optional EconomyManager instance
        
    Returns:
        Sale value
    """
    # If we have an economy manager, use market pricing if possible
    if economy_manager and 'resource_id' in item and 'market_id' in item:
        price, _ = economy_manager.calculate_price(
            item['resource_id'], 
            item['market_id'], 
            quantity=1.0
        )
        # Apply a discount for selling to shops
        return round(price * 0.6)  
    
    # Fallback to level-based calculation
    rarity = item.get("rarity", "normal")
    base = get_expected_gold_at_level(player_level)
    multiplier = {"normal": 0.25, "epic": 0.5, "legendary": 1.0}.get(rarity, 0.25)
    return round(base * multiplier)

def calculate_resale_value(item, player_level, economy_manager=None):
    """
    Calculate how much a shop will sell an item for.
    
    Args:
        item: Item data
        player_level: Player's level
        economy_manager: Optional EconomyManager instance
        
    Returns:
        Resale value
    """
    if economy_manager and 'resource_id' in item and 'market_id' in item:
        price, _ = economy_manager.calculate_price(
            item['resource_id'], 
            item['market_id'], 
            quantity=1.0
        )
        return round(price)
    
    # Fallback to level-based calculation
    sale = calculate_sale_value(item, player_level)
    return round(sale * 1.5)

def format_shop_inventory(inventory):
    """
    Format a shop's inventory as a string.
    
    Args:
        inventory: List of items
        
    Returns:
        Formatted string
    """
    lines = []
    for item in inventory:
        name = item.get("display_name") or item.get("base_item", "Unnamed")
        rarity = item.get("rarity", "normal").title()
        price = item.get("resale_price", "?")
        weight = item.get("weight_lbs", "?")
        lines.append(f"[{rarity}] {name} — {price}g, {weight} lbs")
    return "\n".join(lines)

def summarize_shop(shop_id, shop_data, sort_by=None, filter_type=None, page=1, page_size=10):
    """
    Create a paginated summary of a shop's inventory.
    
    Args:
        shop_id: Shop ID
        shop_data: Shop data containing inventory
        sort_by: Field to sort by
        filter_type: Item type to filter by
        page: Page number
        page_size: Items per page
        
    Returns:
        Dictionary with summary information
    """
    inventory = shop_data.get("inventory", [])

    if filter_type:
        inventory = [i for i in inventory if i.get("category") == filter_type]

    if sort_by == "value":
        inventory.sort(key=lambda x: x.get("resale_price", 0), reverse=True)
    elif sort_by == "rarity":
        rarity_order = {"legendary": 3, "epic": 2, "normal": 1}
        inventory.sort(key=lambda x: rarity_order.get(x.get("rarity", "normal"), 0), reverse=True)
    elif sort_by == "weight":
        inventory.sort(key=lambda x: x.get("weight_lbs", 0), reverse=True)

    total_items = len(inventory)
    total_pages = (total_items + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    page_items = inventory[start:end]

    return {
        "shop_id": shop_id,
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "items_on_page": len(page_items),
        "preview": format_shop_inventory(page_items)
    }

def tick_shop_inventory(shop_data, max_days=2):
    """
    Clean up shop inventory by removing old items.
    
    Args:
        shop_data: Shop data containing inventory
        max_days: Maximum age of items in days
        
    Returns:
        Updated shop data
    """
    now = datetime.utcnow()
    inventory = shop_data.get("inventory", [])
    cleaned = []

    for item in inventory:
        timestamp = item.get("added_at")
        if timestamp:
            try:
                item_time = datetime.fromisoformat(timestamp)
                if now - item_time <= timedelta(days=max_days):
                    cleaned.append(item)
            except ValueError:
                cleaned.append(item)  # If timestamp broken, keep
        else:
            cleaned.append(item)  # If no timestamp, keep

    shop_data["inventory"] = cleaned
    return shop_data

def buy_item_from_shop(character_id, npc_id, item_id):
    player_ref = db.reference(f"/players/{character_id}")
    gold = player_ref.child("gold").get() or 0
    attributes = player_ref.child("attributes").get() or {}
    cha_mod = attributes.get("CHA", 0)

    # Load item from NPC shop
    shop_ref = db.reference(f"/npcs/{npc_id}/shop_inventory/{item_id}")
    item = shop_ref.get()
    if not item:
        return {"error": "Item not found in shop"}, 404

    base_price = item.get("gold_value", 0)

    # Load goodwill
    opinion_ref = db.reference(f"/npc_opinion_matrix/{npc_id}/{character_id}")
    goodwill = opinion_ref.get() or 0

    # Calculate modifier
    modifier = 1.0
    modifier *= 1.0 - (cha_mod * 0.02)
    modifier *= 1.0 - (goodwill * 0.02)
    modifier = max(0.7, min(modifier, 1.3))

    final_price = int(base_price * modifier)

    if gold < final_price:
        return {"error": "Not enough gold", "price": final_price, "current": gold}, 402

    # Transaction
    player_ref.child("gold").set(gold - final_price)
    inventory_ref = player_ref.child("inventory")
    inventory = inventory_ref.get() or []
    inventory.append(item)
    inventory_ref.set(inventory)
    shop_ref.delete()

    return {
        "message": "Item purchased",
        "item": item,
        "gold_spent": final_price,
        "gold_remaining": gold - final_price
    }, 200

def restock_shop_inventory(npc_id):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()

    if not npc:
        return {"error": "NPC not found"}

    # Tags determine what kinds of items the shop should carry
    building_tags = npc.get("shop_profile", {}).get("inventory_tags", ["gear"])
    inventory = {}

    matching_items = [
        item for item in equipment_rules.values()
        if item.get("category") in building_tags
    ]

    for _ in range(random.randint(3, 6)):
        base = random.choice(matching_items)
        item = generate_item_identity(base.copy())
        inventory[f"item_{uuid4().hex[:6]}"] = item

    db.reference(f"/npcs/{npc_id}/shop_inventory").set(inventory)
    return {"npc_id": npc_id, "new_items": list(inventory.values())}

def calculate_price_with_modifiers(base_price, character_attributes=None, faction_reputation=None):
    """
    Calculate item price with character attribute and faction reputation modifiers.
    
    Args:
        base_price: Base price of the item
        character_attributes: Character attributes dict (optional)
        faction_reputation: Faction reputation value (optional)
        
    Returns:
        Final price after applying modifiers
    """
    modifier = 1.0
    
    # Apply charisma modifier if available
    if character_attributes and "CHA" in character_attributes:
        cha_mod = character_attributes.get("CHA", 0)
        modifier *= 1.0 - (cha_mod * 0.02)  # 2% discount per CHA point
    
    # Apply faction reputation if available
    if faction_reputation is not None:
        modifier *= 1.0 - (faction_reputation * 0.02)  # 2% discount per reputation point
    
    # Ensure price stays in reasonable bounds
    modifier = max(0.7, min(modifier, 1.3))
    
    return int(base_price * modifier)

def generate_inventory_from_tags(tags, economy_manager=None):
    """
    Given a list of tags like ["armor", "weapons"], return a randomized inventory list.
    Uses EconomyManager data if available.
    
    Args:
        tags: List of category tags
        economy_manager: Optional EconomyManager instance
        
    Returns:
        List of items
    """
    inventory = []
    
    # If we have an economy manager, use it to find appropriate resources
    if economy_manager:
        for tag in tags:
            resources = economy_manager.get_available_resources(resource_type=tag)
            if resources:
                # Convert resources to items
                for resource in resources[:3]:  # Limit to 3 per category
                    inventory.append({
                        "name": resource.name,
                        "category": resource.resource_type,
                        "rarity": "common",  # Default, could be based on resource rarity
                        "gold_value": resource.base_value,
                        "resource_id": resource.id
                    })
    
    # Fallback to hardcoded item pools if needed
    if not inventory:
        item_pools = {
            "armor": ["Leather Armor", "Chain Shirt", "Breastplate", "Plate Armor"],
            "weapons": ["Short Sword", "Longbow", "Warhammer", "Dagger"],
            "food": ["Rations", "Ale Cask", "Dried Fruits", "Hardtack"],
            "magic": ["Potion of Healing", "Scroll of Fireball", "Wand of Light", "Amulet of Protection"],
            "tools": ["Thieves' Tools", "Carpenter's Kit", "Alchemy Set", "Smithing Kit"]
        }

        for tag in tags:
            pool = item_pools.get(tag, [])
            if pool:
                for item_name in random.sample(pool, k=min(3, len(pool))):
                    inventory.append({
                        "name": item_name,
                        "category": tag,
                        "rarity": "common",
                        "gold_value": random.randint(5, 50)
                    })

    # Shuffle inventory for flavor
    random.shuffle(inventory)
    return inventory