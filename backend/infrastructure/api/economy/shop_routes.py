"""
Shop API routes integrated with EconomyManager.

This module provides RESTful API endpoints for shop functionality,
fully integrated with the economy system via EconomyManager.
"""

import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.infrastructure.database import get_db

from backend.systems.economy.services.economy_manager import EconomyManager
from backend.infrastructure.utils.shop_utils import (
    calculate_sale_value, 
    calculate_resale_value, 
    summarize_shop, 
    calculate_price_with_modifiers,
    generate_inventory_from_tags
)
from backend.infrastructure.database.economy.market_models import Market
from backend.systems.economy.services.resource import Resource

# Try to import from backend systems, fallback if not available
try:
    from backend.infrastructure.database import get_async_session
    from backend.systems.loot.utils.loot_core import generate_item_identity
    from backend.systems.character.models.relationship import Relationship
except ImportError:
    # Create fallbacks
    def get_async_session():
        return None
    def generate_item_identity(*args, **kwargs):
        return {"id": "unknown", "name": "Unknown Item"}
    class Relationship:
        pass

# Set up logging
logger = logging.getLogger(__name__)

shop_bp = APIRouter(prefix="", tags=["economy"])

# Request models for proper API contracts
class SellItemRequest(BaseModel):
    item: Dict[str, Any]
    player_level: int

class BuyItemRequest(BaseModel):
    item_id: str
    player_gold: int
    quantity: Optional[int] = 1

class PreviewPriceRequest(BaseModel):
    item_id: int
    shop_id: int
    is_buying: bool
    quantity: int

# Helper function to get economy manager
def get_economy_manager(db_session: Session = Depends(get_db)) -> EconomyManager:
    """Get economy manager instance with database session."""
    return EconomyManager.get_instance(db_session)

# FIXED: Changed from GET to POST and updated path to match Development Bible
@shop_bp.post("/sell/{shop_id}")
async def sell_item_to_shop(
    shop_id: int,
    request: SellItemRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Sell an item to a shop.
    
    Args:
        shop_id: Shop ID
        request: Item data and player level
        
    Returns:
        JSON response with gold earned and resale price
    """
    try:
        item = request.item
        player_level = request.player_level

        # Identify all levels known to player
        item.setdefault("identified_levels", [e["level"] for e in item.get("effects", []) if e["level"] <= player_level])

        # Get market for shop
        market = economy_manager.get_market(shop_id)
        if not market:
            # Try to find market by region if shop_id is a region_id
            markets = economy_manager.get_markets_by_region(shop_id)
            market = markets[0] if markets else None
            
            if not market:
                # Create a default market for this shop/region
                market = economy_manager.create_market({
                    "name": f"Shop {shop_id}",
                    "region_id": shop_id,
                    "market_type": "general"
                })
        
        # Add market_id to item if not exists
        if market:
            item["market_id"] = market.id
            
        # Calculate sale/resale value
        sale_price = calculate_sale_value(item, player_level, economy_manager)
        resale_price = calculate_resale_value(item, player_level, economy_manager)
        
        # Store in shop inventory
        # First, check if item corresponds to a resource
        resource = None
        if "resource_id" in item:
            resource = economy_manager.get_resource(item["resource_id"])
            
        if not resource and "resource_type" in item:
            # Create a new resource
            resource = economy_manager.create_resource({
                "name": item.get("name", "Unknown Item"),
                "resource_type": item.get("resource_type", "item"),
                "region_id": shop_id,
                "amount": 1,
                "base_value": resale_price,
                "metadata": {"item_data": item}
            })
            if resource:
                item["resource_id"] = resource.id
                
        # Set the resale price
        item["resale_price"] = resale_price
        
        # Store in shop inventory (we'll use market's metadata for this)
        if market:
            inventory = market.metadata.get("inventory", [])
            inventory.append(item)
            
            # Update market metadata
            economy_manager.update_market(market.id, {
                "metadata": {**market.metadata, "inventory": inventory}
            })
        
        return {
            "message": "Item sold to shop.",
            "gold_earned": sale_price,
            "resale_price": resale_price
        }
    except Exception as e:
        logger.error(f"Error selling item to shop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# FIXED: Updated path pattern to match Development Bible    
@shop_bp.get("/inventory/{shop_id}")
async def get_shop_inventory(
    shop_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get a shop's inventory.
    
    Args:
        shop_id: Shop ID
        
    Returns:
        JSON response with shop inventory
    """
    try:
        # Get market for shop
        market = economy_manager.get_market(shop_id)
        if not market:
            # Try to find market by region if shop_id is a region_id
            markets = economy_manager.get_markets_by_region(shop_id)
            market = markets[0] if markets else None
            
        if not market:
            raise HTTPException(status_code=404, detail="Shop not found")
            
        # Get inventory from market metadata
        inventory = market.metadata.get("inventory", [])
        
        # Ensure each item has proper identity
        for item in inventory:
            if not item.get("item_id"):
                item["item_id"] = str(item.get("resource_id", ""))
            
        return {"shop_id": shop_id, "inventory": inventory}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shop inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# FIXED: Changed from GET to POST and updated path to match Development Bible
@shop_bp.post("/buy/{shop_id}")
async def buy_item_from_shop(
    shop_id: int,
    request: BuyItemRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Buy an item from a shop.
    
    Args:
        shop_id: Shop ID
        request: Item ID and player gold
        
    Returns:
        JSON response with item and remaining gold
    """
    try:
        item_id = request.item_id
        player_gold = request.player_gold
        quantity = request.quantity

        # Get market for shop
        market = economy_manager.get_market(shop_id)
        if not market:
            # Try to find market by region if shop_id is a region_id
            markets = economy_manager.get_markets_by_region(shop_id)
            market = markets[0] if markets else None
            
        if not market:
            raise HTTPException(status_code=404, detail="Shop not found")
            
        # Get inventory from market metadata
        inventory = market.metadata.get("inventory", [])
        
        # Find item in inventory
        item = next((i for i in inventory if str(i.get("item_id", "")) == str(item_id) or 
                    str(i.get("resource_id", "")) == str(item_id)), None)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found in shop")

        price = item.get("resale_price", 9999) * quantity
        if player_gold < price:
            raise HTTPException(status_code=403, detail=f"Not enough gold. Required: {price}")

        # Remove item from inventory (or reduce quantity)
        inventory = [i for i in inventory if (str(i.get("item_id", "")) != str(item_id) and 
                                            str(i.get("resource_id", "")) != str(item_id))]
        
        # Update market metadata
        economy_manager.update_market(market.id, {
            "metadata": {**market.metadata, "inventory": inventory}
        })
        
        # If this item has a resource_id, adjust the resource amount
        if "resource_id" in item:
            resource = economy_manager.get_resource(item["resource_id"])
            if resource and resource.amount >= quantity:
                economy_manager.adjust_resource_amount(resource.id, -quantity)

        return {
            "item": item,
            "quantity": quantity,
            "gold_spent": price,
            "remaining_gold": player_gold - price
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error buying item from shop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# FIXED: Changed from GET to POST to match Development Bible
@shop_bp.post("/restock/{shop_id}")
async def restock_shop(
    shop_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Restock a shop with new items.
    
    Args:
        shop_id: Shop ID
        
    Returns:
        JSON response with restocking results
    """
    try:
        # Get market for shop
        market = economy_manager.get_market(shop_id)
        if not market:
            # Try to find market by region if shop_id is a region_id
            markets = economy_manager.get_markets_by_region(shop_id)
            market = markets[0] if markets else None
            
        if not market:
            raise HTTPException(status_code=404, detail="Shop not found")

        # Generate new inventory
        new_inventory = generate_inventory_from_tags(
            ["general"], 
            item_count=10,
            average_level=5,
            economy_manager=economy_manager
        )
        
        # Update market metadata with new inventory
        economy_manager.update_market(market.id, {
            "metadata": {**market.metadata, "inventory": new_inventory}
        })
        
        return {
            "message": f"Shop {shop_id} restocked successfully",
            "items_added": len(new_inventory),
            "new_inventory": new_inventory
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restocking shop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@shop_bp.post("/preview_price")
async def preview_price(
    request: PreviewPriceRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Preview the price of an item with all economic modifiers applied.
    
    Args:
        request: Preview price request with item and shop details
        
    Returns:
        JSON response with calculated price and modifiers
    """
    try:
        item_id = request.item_id
        shop_id = request.shop_id
        is_buying = request.is_buying
        quantity = request.quantity

        # Get market for shop
        market = economy_manager.get_market(shop_id)
        if not market:
            markets = economy_manager.get_markets_by_region(shop_id)
            market = markets[0] if markets else None
            
        if not market:
            raise HTTPException(status_code=404, detail="Shop not found")

        # Get resource or item
        resource = economy_manager.get_resource(item_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Item not found")

        # Calculate price with modifiers
        base_price = resource.base_value if resource else 100
        price, modifiers = economy_manager.calculate_price(item_id, shop_id, quantity)
        
        return {
            "item_id": item_id,
            "shop_id": shop_id,
            "is_buying": is_buying,
            "quantity": quantity,
            "base_price": base_price,
            "calculated_price": price,
            "total_price": price * quantity,
            "modifiers": modifiers
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional shop routes for compatibility
@shop_bp.get("/view_shop_inventory/{npc_id}")
async def view_shop_inventory(
    npc_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager),
    player_level: int = 10,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    filter_type: Optional[str] = None
):
    """View shop inventory with filtering and sorting options.
    
    Args:
        npc_id: NPC shop owner ID
        player_level: Player level for item identification
        search: Search term for item names
        sort: Sort criteria
        filter_type: Filter by item type
        
    Returns:
        JSON response with filtered shop inventory
    """
    try:
        # Use the standard inventory endpoint but with additional filtering
        inventory_response = await get_shop_inventory(npc_id, economy_manager)
        inventory = inventory_response.get("inventory", [])
        
        # Apply filters
        def filter_item(item):
            if search and search.lower() not in item.get("name", "").lower():
                return False
            if filter_type and item.get("type") != filter_type:
                return False
            return True
        
        def rarity_color(item):
            rarity = item.get("rarity", "common")
            color_map = {
                "common": "#FFFFFF",
                "uncommon": "#00FF00", 
                "rare": "#0080FF",
                "epic": "#8000FF",
                "legendary": "#FF8000"
            }
            return color_map.get(rarity, "#FFFFFF")
        
        filtered_inventory = []
        for item in inventory:
            if filter_item(item):
                # Add display properties
                item["rarity_color"] = rarity_color(item)
                item["can_afford"] = True  # TODO: Check player gold
                filtered_inventory.append(item)
        
        # Apply sorting
        if sort == "name":
            filtered_inventory.sort(key=lambda x: x.get("name", ""))
        elif sort == "price":
            filtered_inventory.sort(key=lambda x: x.get("resale_price", 0))
        elif sort == "rarity":
            rarity_order = {"common": 1, "uncommon": 2, "rare": 3, "epic": 4, "legendary": 5}
            filtered_inventory.sort(key=lambda x: rarity_order.get(x.get("rarity", "common"), 1))
        
        return {
            "npc_id": npc_id,
            "inventory": filtered_inventory,
            "total_items": len(filtered_inventory),
            "player_level": player_level
        }
    except Exception as e:
        logger.error(f"Error viewing shop inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@shop_bp.get("/shops/view_inventory/{npc_id}")
async def simple_shop_inventory(
    npc_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get simplified shop inventory for basic display.
    
    Args:
        npc_id: NPC shop owner ID
        
    Returns:
        JSON response with simplified shop inventory
    """
    try:
        # Use the standard inventory endpoint
        inventory_response = await get_shop_inventory(npc_id, economy_manager)
        inventory = inventory_response.get("inventory", [])
        
        # Simplify the inventory data
        simplified_inventory = []
        for item in inventory:
            simplified_item = {
                "id": item.get("item_id", item.get("resource_id", "")),
                "name": item.get("name", "Unknown Item"),
                "price": item.get("resale_price", 0),
                "type": item.get("type", "item"),
                "rarity": item.get("rarity", "common"),
                "description": item.get("description", "")
            }
            simplified_inventory.append(simplified_item)
        
        return {
            "npc_id": npc_id,
            "shop_name": f"Shop {npc_id}",
            "inventory": simplified_inventory,
            "item_count": len(simplified_inventory)
        }
    except Exception as e:
        logger.error(f"Error getting simple shop inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
