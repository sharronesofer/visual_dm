"""
Shop utilities for managing and processing shop data.

This module provides functionality for managing shop inventories,
calculating prices, and processing transactions.
"""

import random
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.infrastructure.config_loaders.economy_config_loader import get_economy_config

logger = logging.getLogger(__name__)

# Mock data for equipment rules
def load_equipment_rules():
    return {}

def generate_item_identity(*args, **kwargs):
    """Mock function for generating item identity."""
    return {"id": "mock_item_id", "name": "Unknown Item"}

# Constants for UI and display
RARITY_COLORS = {
    "common": "gray",
    "uncommon": "blue",
    "rare": "green",
    "epic": "purple",
    "legendary": "orange"
}

def get_shop_inventory(npc_id: str, db_session: Session = None):
    """
    Get shop inventory using SQLAlchemy through EconomyManager.
    
    Args:
        npc_id: NPC shop owner ID
        db_session: SQLAlchemy session
        
    Returns:
        Shop inventory dictionary
    """
    if not db_session:
        raise ValueError("Database session required for shop inventory access")
    
    from backend.systems.economy.services.economy_manager import EconomyManager
    economy_manager = EconomyManager.get_instance(db_session)
    
    # Generate shop inventory dynamically using the economy system
    # This approach avoids the need for persistent shop inventory storage
    # while leveraging the rich resource and pricing systems
    
    try:
        # Use the economy manager's shop inventory generation
        inventory_items = economy_manager.generate_shop_inventory(
            npc_id=npc_id,
            shop_type="general",
            item_count=15,
            average_player_level=10
        )
        
        # Convert to expected format and add UI enhancements
        inventory = {}
        for i, item in enumerate(inventory_items):
            item_id = f"{npc_id}_item_{i}"
            inventory[item_id] = item
            
            # Add rarity color for UI
            if item.get("name_revealed", True):
                rarity = item.get("rarity", "common")
                item["rarity_color"] = RARITY_COLORS.get(rarity, "gray")
        
        return inventory
        
    except Exception as e:
        logger.error(f"Failed to generate shop inventory for NPC {npc_id}: {e}")
        return {}

def get_expected_gold_at_level(level):
    """
    Get expected daily gold income using the unified economy configuration.
    
    Args:
        level: Player level
        
    Returns:
        Expected daily gold income
    """
    # Delegate to economy manager for configuration-based pricing
    from backend.systems.economy.services.economy_manager import EconomyManager
    economy_manager = EconomyManager.get_instance()
    return economy_manager.get_expected_gold_at_level(level)

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
    # Always use economy manager for consistent pricing
    if not economy_manager:
        from backend.systems.economy.services.economy_manager import EconomyManager
        economy_manager = EconomyManager.get_instance()
    
    # Use unified shop pricing interface
    price, details = economy_manager.calculate_shop_buy_price(item, player_level)
    return round(price)

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
    # Always use economy manager for consistent pricing
    if not economy_manager:
        from backend.systems.economy.services.economy_manager import EconomyManager
        economy_manager = EconomyManager.get_instance()
    
    # Use unified shop pricing interface
    price, details = economy_manager.calculate_shop_sell_price(item, player_level)
    return round(price)

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
    Update shop inventories based on time progression.
    
    Args:
        shop_data: Shop data containing inventory
        max_days: Maximum days to process
        
    Returns:
        Updated shop data
    """
    inventory = shop_data.get("inventory", [])
    
    # Update each item's stock and quality
    for item in inventory:
        # Simulate item aging and restocking
        if random.random() < 0.1:  # 10% chance of new stock
            item["quantity"] = item.get("quantity", 1) + random.randint(1, 3)
        
        # Simulate items selling
        if random.random() < 0.05:  # 5% chance of selling
            quantity = item.get("quantity", 1)
            if quantity > 0:
                item["quantity"] = max(0, quantity - random.randint(1, 2))
    
    # Remove sold out items
    inventory = [item for item in inventory if item.get("quantity", 1) > 0]
    
    shop_data["inventory"] = inventory
    shop_data["last_updated"] = datetime.utcnow().isoformat()
    
    return shop_data

def buy_item_from_shop(character_id: str, npc_id: str, item_id: str, db_session: Session = None):
    """
    Handle a character buying an item from a shop.
    
    Args:
        character_id: Character making the purchase
        npc_id: NPC shop owner
        item_id: Item being purchased
        db_session: Database session
        
    Returns:
        Transaction result
    """
    if not db_session:
        raise ValueError("Database session required for shop transactions")
    
    from backend.systems.economy.services.economy_manager import EconomyManager
    economy_manager = EconomyManager.get_instance(db_session)
    
    try:
        # Get shop inventory
        inventory = get_shop_inventory(npc_id, db_session)
        
        if item_id not in inventory:
            return {
                "success": False,
                "error": "Item not found in shop inventory",
                "item_id": item_id
            }
        
        item = inventory[item_id]
        price = item.get("resale_price", 0)
        
        # Process the transaction through economy manager
        transaction_result = economy_manager.process_shop_transaction(
            buyer_id=character_id,
            seller_id=npc_id,
            item_data=item,
            transaction_type="purchase",
            amount=price
        )
        
        if transaction_result.get("success"):
            # Remove item from shop inventory (or decrease quantity)
            quantity = item.get("quantity", 1)
            if quantity > 1:
                item["quantity"] = quantity - 1
            else:
                # Item sold out, could trigger restock logic here
                pass
        
        return transaction_result
        
    except Exception as e:
        logger.error(f"Error processing shop purchase: {e}")
        return {
            "success": False,
            "error": f"Transaction failed: {str(e)}",
            "item_id": item_id
        }

def restock_shop_inventory(npc_id: str, db_session: Session = None):
    """
    Restock a shop's inventory with new items.
    
    Args:
        npc_id: NPC shop owner ID
        db_session: Database session
        
    Returns:
        Restock result
    """
    if not db_session:
        raise ValueError("Database session required for shop restocking")
    
    from backend.systems.economy.services.economy_manager import EconomyManager
    economy_manager = EconomyManager.get_instance(db_session)
    
    try:
        # Generate new inventory using economy manager
        new_items = economy_manager.generate_shop_inventory(
            npc_id=npc_id,
            shop_type="general",
            item_count=random.randint(8, 15),
            average_player_level=10,
            restock_mode=True
        )
        
        # Process restock through economy system
        restock_result = economy_manager.process_shop_restock(
            npc_id=npc_id,
            new_items=new_items
        )
        
        return {
            "success": True,
            "npc_id": npc_id,
            "new_items_count": len(new_items),
            "restock_timestamp": datetime.utcnow().isoformat(),
            "details": restock_result
        }
        
    except Exception as e:
        logger.error(f"Error restocking shop {npc_id}: {e}")
        return {
            "success": False,
            "error": f"Restock failed: {str(e)}",
            "npc_id": npc_id
        }

def calculate_price_with_modifiers(base_price, character_attributes=None, faction_reputation=None):
    """
    Calculate final price with character and faction modifiers.
    
    Args:
        base_price: Base item price
        character_attributes: Character attributes affecting price
        faction_reputation: Faction reputation modifiers
        
    Returns:
        Modified price
    """
    final_price = base_price
    
    # Character-based modifiers
    if character_attributes:
        charisma = character_attributes.get("charisma", 10)
        # Higher charisma = better prices
        charisma_modifier = 1.0 - ((charisma - 10) * 0.02)  # 2% per point above/below 10
        final_price *= max(0.7, min(1.3, charisma_modifier))  # Cap between 70% and 130%
    
    # Faction reputation modifiers
    if faction_reputation:
        rep_level = faction_reputation.get("level", 0)
        # Better reputation = better prices
        rep_modifier = 1.0 - (rep_level * 0.05)  # 5% discount per reputation level
        final_price *= max(0.5, min(1.0, rep_modifier))  # Cap between 50% and 100%
    
    return round(final_price, 2)

def generate_inventory_from_tags(tags, economy_manager=None):
    """
    Generate shop inventory based on tags and themes.
    
    Args:
        tags: List of tags to influence generation
        economy_manager: Optional EconomyManager instance
        
    Returns:
        Generated inventory list
    """
    if not economy_manager:
        from backend.systems.economy.services.economy_manager import EconomyManager
        economy_manager = EconomyManager.get_instance()
    
    try:
        # Use economy manager to generate themed inventory
        inventory = economy_manager.generate_themed_inventory(
            tags=tags,
            item_count=random.randint(10, 20)
        )
        
        return inventory
        
    except Exception as e:
        logger.error(f"Error generating tagged inventory: {e}")
        return [] 