"""
Shop API routes integrated with EconomyManager.

This module provides RESTful API endpoints for shop functionality,
fully integrated with the economy system via EconomyManager.
"""

import logging
from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from backend.infrastructure.database import get_db

from backend.systems.economy.services.economy_manager import EconomyManager
from backend.systems.economy.utils.shop_utils import (
    calculate_sale_value, 
    calculate_resale_value, 
    summarize_shop, 
    calculate_price_with_modifiers,
    generate_inventory_from_tags
)
from backend.systems.economy.models import Market
from backend.systems.economy.services.resource import Resource

# Try to import from backend systems, fallback if not available
try:
    from backend.infrastructure.database import get_async_session
    from backend.systems.equipment.loot_utils import generate_item_identity
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

shop_bp = APIRouter(prefix="/shop", tags=["shop"])

# Helper function to get database session


@shop_bp.get("/sell_item_to_shop")
def sell_item_to_shop():
    """Sell an item to a shop.
    
    Request body:
        shop_id: Shop ID
        item: Item data
        player_level: Player's level
        
    Returns:
        JSON response with gold earned and resale price
    """
    data = request.get_json(force=True)
    shop_id = data.get("shop_id")
    item = data.get("item")
    player_level = data.get("player_level")

    if not item or player_level is None or not shop_id:
        return jsonify({"error": "Missing item, player_level, or shop_id"}), 400

    # Identify all levels known to player
    item.setdefault("identified_levels", [e["level"] for e in item.get("effects", []) if e["level"] <= player_level])

    try:
        # Get database session
        db_session = get_db()
        economy = EconomyManager.get_instance(db_session)
        
        # Get market for shop
        market = economy.get_market(shop_id)
        if not market:
            # Try to find market by region if shop_id is a region_id
            markets = economy.get_markets_by_region(shop_id)
            market = markets[0] if markets else None
            
            if not market:
                # Create a default market for this shop/region
                market = economy.create_market({
                    "name": f"Shop {shop_id}",
                    "region_id": shop_id,
                    "market_type": "general"
                })
        
        # Add market_id to item if not exists
        if market:
            item["market_id"] = market.id
            
        # Calculate sale/resale value
        sale_price = calculate_sale_value(item, player_level, economy)
        resale_price = calculate_resale_value(item, player_level, economy)
        
        # Store in shop inventory
        # First, check if item corresponds to a resource
        resource = None
        if "resource_id" in item:
            resource = economy.get_resource(item["resource_id"])
            
        if not resource and "resource_type" in item:
            # Create a new resource
            resource = economy.create_resource({
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
            economy.update_market(market.id, {
                "metadata": {**market.metadata, "inventory": inventory}
            })
        
        return jsonify({
            "message": "Item sold to shop.",
            "gold_earned": sale_price,
            "resale_price": resale_price
        })
    except Exception as e:
        logger.error(f"Error selling item to shop: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@shop_bp.get("/get_shop_inventory/<shop_id>")
def get_shop_inventory(shop_id):
    """Get a shop's inventory.
    
    Args:
        shop_id: Shop ID
        
    Returns:
        JSON response with shop inventory
    """
    try:
        db_session = get_db()
        economy = EconomyManager.get_instance(db_session)
        
        # Get market for shop
        market = economy.get_market(shop_id)
        if not market:
            # Try to find market by region if shop_id is a region_id
            markets = economy.get_markets_by_region(shop_id)
            market = markets[0] if markets else None
            
        if not market:
            return jsonify({"shop_id": shop_id, "inventory": []}), 404
            
        # Get inventory from market metadata
        inventory = market.metadata.get("inventory", [])
        
        # Ensure each item has proper identity
        for item in inventory:
            if not item.get("item_id"):
                item["item_id"] = str(item.get("resource_id", ""))
            
        return jsonify({"shop_id": shop_id, "inventory": inventory})
    except Exception as e:
        logger.error(f"Error getting shop inventory: {str(e)}")
        return jsonify({"error": str(e)}), 500

@shop_bp.get("/buy_item_from_shop/<shop_id>")
def buy_item_from_shop(shop_id):
    """Buy an item from a shop.
    
    Args:
        shop_id: Shop ID
        
    Request body:
        item_id: Item ID
        player_gold: Player's gold
        
    Returns:
        JSON response with item and remaining gold
    """
    data = request.get_json(force=True)
    item_id = data.get("item_id")
    player_gold = data.get("player_gold", 0)

    try:
        db_session = get_db()
        economy = EconomyManager.get_instance(db_session)
        
        # Get market for shop
        market = economy.get_market(shop_id)
        if not market:
            # Try to find market by region if shop_id is a region_id
            markets = economy.get_markets_by_region(shop_id)
            market = markets[0] if markets else None
            
        if not market:
            return jsonify({"error": "Shop not found."}), 404
            
        # Get inventory from market metadata
        inventory = market.metadata.get("inventory", [])
        
        # Find item in inventory
        item = next((i for i in inventory if str(i.get("item_id", "")) == str(item_id) or 
                    str(i.get("resource_id", "")) == str(item_id)), None)
        if not item:
            return jsonify({"error": "Item not found in shop."}), 404

        price = item.get("resale_price", 9999)
        if player_gold < price:
            return jsonify({"error": "Not enough gold.", "required": price}), 403

        # Remove item from inventory
        inventory = [i for i in inventory if (str(i.get("item_id", "")) != str(item_id) and 
                                            str(i.get("resource_id", "")) != str(item_id))]
        
        # Update market metadata
        economy.update_market(market.id, {
            "metadata": {**market.metadata, "inventory": inventory}
        })
        
        # If this item has a resource_id, adjust the resource amount
        if "resource_id" in item:
            resource = economy.get_resource(item["resource_id"])
            if resource and resource.amount > 0:
                economy.adjust_resource_amount(resource.id, -1)

        return jsonify({
            "item": item,
            "gold_spent": price,
            "remaining_gold": player_gold - price
        })
    except Exception as e:
        logger.error(f"Error buying item from shop: {str(e)}")
        return jsonify({"error": str(e)}), 500

@shop_bp.get("/shops/preview_price")
def preview_price():
    """Preview the price of an item based on character attributes and NPC relationship.
    
    Request body:
        character_id: Character ID
        npc_id: NPC ID
        item_id: Item ID
        
    Returns:
        JSON response with price information
    """
    data = request.get_json()
    character_id = data.get("character_id")
    npc_id = data.get("npc_id")
    item_id = data.get("item_id")

    try:
        db_session = get_db()
        economy = EconomyManager.get_instance(db_session)
        
        # Get market for shop (using npc_id as shop_id)
        market = economy.get_market(npc_id)
        if not market:
            # Try to find market by region if npc_id is a region_id
            markets = economy.get_markets_by_region(npc_id)
            market = markets[0] if markets else None
            
        if not market:
            return {"error": "Shop not found."}, 404
            
        # Get inventory from market metadata
        inventory = market.metadata.get("inventory", [])
        
        # Find item in inventory
        item = next((i for i in inventory if str(i.get("item_id", "")) == str(item_id) or 
                    str(i.get("resource_id", "")) == str(item_id)), None)
        if not item:
            return {"error": "Item not found in shop"}, 404

        # Get character attributes from relationships
        attributes = {}
        faction_rep = 0
        
        # Try to get character attributes and faction reputation
        if db_session and character_id:
            # Get character attributes
            attrs_rel = db_session.query(Relationship).filter(
                Relationship.source_id == character_id,
                Relationship.type == "attributes"
            ).first()
            if attrs_rel:
                attributes = attrs_rel.data or {}
                
            # Get faction reputation
            faction_rel = db_session.query(Relationship).filter(
                Relationship.source_id == character_id,
                Relationship.target_id == npc_id,
                Relationship.type == "faction"
            ).first()
            if faction_rel:
                faction_rep = faction_rel.data.get("reputation", 0)

        base_price = item.get("gold_value", item.get("resale_price", 0))
        final_price = calculate_price_with_modifiers(base_price, attributes, faction_rep)
        modifier = final_price / base_price if base_price > 0 else 1.0

        return {
            "base_price": base_price,
            "final_price": final_price,
            "modifier": round(modifier, 2),
            "charisma": attributes.get("CHA", 0),
            "goodwill": faction_rep
        }
    except Exception as e:
        logger.error(f"Error previewing price: {str(e)}")
        return {"error": str(e)}, 500

@shop_bp.get("/view_shop_inventory/<npc_id>")
def view_shop_inventory(npc_id):
    """View a shop's inventory with filtering and sorting.
    
    Args:
        npc_id: NPC ID (used as shop_id)
        
    Query params:
        type: Filter by item type
        rarity: Filter by rarity
        sort: Sort field (default: gold_value)
        
    Returns:
        JSON response with filtered and sorted inventory
    """
    query_type = request.args.get("type")
    rarity = request.args.get("rarity")
    sort_by = request.args.get("sort", "gold_value")
    
    try:
        db_session = get_db()
        economy = EconomyManager.get_instance(db_session)
        
        # Get market for shop
        market = economy.get_market(npc_id)
        if not market:
            # Try to find market by region if npc_id is a region_id
            markets = economy.get_markets_by_region(npc_id)
            market = markets[0] if markets else None
            
        if not market:
            return jsonify([])
            
        # Get inventory from market metadata
        inventory = market.metadata.get("inventory", [])
        if not inventory:
            # If no inventory in metadata, try to generate one
            resources = economy.get_resources_by_region(market.region_id)
            inventory = []
            for resource in resources:
                if resource.amount > 0:
                    inventory.append({
                        "item_id": f"resource_{resource.id}",
                        "resource_id": resource.id,
                        "name": resource.name,
                        "category": resource.resource_type,
                        "rarity": "common",  # Default, could be from resource metadata
                        "gold_value": resource.base_value,
                        "name_revealed": True
                    })
            
            # Update market metadata with generated inventory
            economy.update_market(market.id, {
                "metadata": {**market.metadata, "inventory": inventory}
            })

        def filter_item(item):
            if query_type and item.get("category") != query_type:
                return False
            if rarity and item.get("rarity") != rarity:
                return False
            return True

        def rarity_color(item):
            if item.get("name_revealed"):
                return {
                    "common": "gray",
                    "uncommon": "blue",
                    "rare": "green",
                    "epic": "purple",
                    "legendary": "orange"
                }.get(item.get("rarity", "common"), "gray")
            return None

        filtered = [
            {
                **item, 
                "item_id": item.get("item_id", f"resource_{item.get('resource_id')}"),
                "rarity_color": rarity_color(item)
            }
            for item in inventory if filter_item(item)
        ]

        if sort_by:
            filtered.sort(key=lambda x: x.get(sort_by, 0))

        return jsonify(filtered)
    except Exception as e:
        logger.error(f"Error viewing shop inventory: {str(e)}")
        return jsonify([]), 500

@shop_bp.get("/shops/view_inventory/<npc_id>")
def simple_shop_inventory(npc_id):
    """Get a simplified view of a shop's inventory.
    
    Args:
        npc_id: NPC ID (used as shop_id)
        
    Returns:
        JSON response with simplified inventory
    """
    try:
        db_session = get_db()
        economy = EconomyManager.get_instance(db_session)
        
        # Get market for shop
        market = economy.get_market(npc_id)
        if not market:
            # Try to find market by region if npc_id is a region_id
            markets = economy.get_markets_by_region(npc_id)
            market = markets[0] if markets else None
            
        if not market:
            return jsonify([])
            
        # Get inventory from market metadata
        inventory = market.metadata.get("inventory", [])

        simplified = []
        for item in inventory:
            if item.get("name_revealed", True):
                entry = {
                    "item_id": item.get("item_id", f"resource_{item.get('resource_id')}"),
                    "name": item.get("identified_name", item.get("name", "Unknown Item")),
                    "rarity": item.get("rarity", "common"),
                    "rarity_color": {
                        "common": "gray",
                        "uncommon": "blue",
                        "rare": "green",
                        "epic": "purple",
                        "legendary": "orange"
                    }.get(item.get("rarity", "common"), "gray"),
                    "gold_value": item.get("gold_value", item.get("resale_price", 0))
                }
                simplified.append(entry)

        return jsonify(simplified)
    except Exception as e:
        logger.error(f"Error getting simplified shop inventory: {str(e)}")
        return jsonify([]), 500

@shop_bp.get("/restock_shop/<shop_id>")
def restock_shop(shop_id):
    """Restock a shop's inventory.
    
    Args:
        shop_id: Shop ID
        
    Request body:
        tags: List of tags for item categories (optional)
        
    Returns:
        JSON response with new inventory
    """
    data = request.get_json(force=True) or {}
    tags = data.get("tags", ["weapons", "armor", "potions"])
    
    try:
        db_session = get_db()
        economy = EconomyManager.get_instance(db_session)
        
        # Get market for shop
        market = economy.get_market(shop_id)
        if not market:
            # Try to find market by region if shop_id is a region_id
            markets = economy.get_markets_by_region(shop_id)
            market = markets[0] if markets else None
            
            if not market:
                # Create a default market for this shop/region
                market = economy.create_market({
                    "name": f"Shop {shop_id}",
                    "region_id": int(shop_id) if shop_id.isdigit() else 0,
                    "market_type": "general"
                })
                
        if not market:
            return jsonify({"error": "Could not find or create shop."}), 404
            
        # Generate inventory from tags
        inventory = generate_inventory_from_tags(tags, economy)
        
        # Add item_id to each item
        for i, item in enumerate(inventory):
            item["item_id"] = f"item_{i}"
            item["added_at"] = datetime.utcnow().isoformat()
            
            # Create resource for item if it doesn't exist
            if "resource_id" not in item and "name" in item:
                resource = economy.create_resource({
                    "name": item["name"],
                    "resource_type": item.get("category", "item"),
                    "region_id": market.region_id,
                    "amount": 1,
                    "base_value": item.get("gold_value", 10),
                    "metadata": {"item_data": item}
                })
                if resource:
                    item["resource_id"] = resource.id
        
        # Update market metadata with new inventory
        economy.update_market(market.id, {
            "metadata": {**market.metadata, "inventory": inventory}
        })
        
        return jsonify({
            "shop_id": shop_id,
            "market_id": market.id,
            "inventory": inventory
        })
    except Exception as e:
        logger.error(f"Error restocking shop: {str(e)}")
        return jsonify({"error": str(e)}), 500
