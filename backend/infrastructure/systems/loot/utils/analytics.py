"""
Analytics and logging utilities for the loot system.
Extracted from loot_utils_core.py to separate infrastructure from business logic.
"""

from typing import Dict, List, Any, Optional
from backend.infrastructure.events import EventDispatcher
from backend.infrastructure.systems.loot.events.loot_events_core import (
    LootAnalyticsEvent,
    PriceAdjustmentEvent
)

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
            "items_bought_count": len(items_bought),
            "items_sold_count": len(items_sold),
            "gold_spent": gold_spent,
            "gold_earned": gold_earned,
            "net_gold_flow": gold_spent - gold_earned
        }
    )
    dispatcher.publish_sync(event)
    
    # Log each item bought
    for item in items_bought:
        dispatcher = EventDispatcher.get_instance()
        event = LootAnalyticsEvent(
            event_type="loot.analytics",
            event_category="shop",
            event_action="item_purchased",
            item_id=item.get("id", 0),
            item_name=item.get("name", "Unknown Item"),
            item_rarity=item.get("rarity", "common"),
            character_id=character_id,
            location_id=location_id,
            region_id=region_id,
            value=float(item.get("price", 0)),
            metadata={
                "shop_id": shop_id,
                "category": item.get("category", ""),
                "quantity": item.get("quantity", 1)
            }
        )
        dispatcher.publish_sync(event)
    
    # Log each item sold
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
            location_id=location_id,
            region_id=region_id,
            value=float(item.get("sale_price", 0)),
            metadata={
                "shop_id": shop_id,
                "category": item.get("category", ""),
                "quantity": item.get("quantity", 1)
            }
        )
        dispatcher.publish_sync(event)

def log_price_adjustment(
    item_id: int,
    item_name: str,
    old_price: int,
    new_price: int,
    adjustment_factor: float,
    reason: str,
    region_id: int
) -> None:
    """
    Logs price adjustments for analytics.
    
    Args:
        item_id: ID of the item
        item_name: Name of the item
        old_price: Original price
        new_price: New price after adjustment
        adjustment_factor: Multiplier used for adjustment
        reason: Reason for the price adjustment
        region_id: ID of the region
    """
    dispatcher = EventDispatcher.get_instance()
    event = PriceAdjustmentEvent(
        event_type="loot.price_adjusted",
        item_id=item_id,
        item_name=item_name,
        old_price=old_price,
        new_price=new_price,
        adjustment_factor=adjustment_factor,
        reason=reason,
        region_id=region_id
    )
    dispatcher.publish_sync(event) 