"""
Loot Event Infrastructure Integration

This module provides the technical infrastructure integration for loot events,
analytics, and event publishing.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LootEventPublisher:
    """Infrastructure implementation for publishing loot-related events"""
    
    def __init__(self):
        self.event_dispatcher = None
        try:
            from backend.infrastructure.events import EventDispatcher
            self.event_dispatcher = EventDispatcher.get_instance()
        except ImportError:
            logger.warning("Event dispatcher not available - events will not be published")
    
    def publish_loot_event(self, event_data: Dict[str, Any]) -> None:
        """Publish loot event"""
        if not self.event_dispatcher:
            return
        
        try:
            # Create appropriate event based on event type
            event_type = event_data.get("event_type", "loot.generic")
            
            if event_type == "item.discovery":
                self._publish_discovery_event(event_data)
            elif event_type == "item.enchanted":
                self._publish_enchantment_event(event_data)
            elif event_type == "item.enchantment_failed":
                self._publish_enchantment_failure_event(event_data)
            elif event_type == "shop.item_sold":
                self._publish_shop_transaction_event(event_data)
            elif event_type == "item.identification":
                self._publish_identification_event(event_data)
            else:
                self._publish_generic_event(event_data)
                
        except Exception as e:
            logger.error(f"Failed to publish loot event: {e}")
    
    def _publish_discovery_event(self, event_data: Dict[str, Any]) -> None:
        """Publish item discovery event"""
        try:
            from backend.infrastructure.systems.loot.events.loot_events_core import ItemDiscoveryEvent
            
            event = ItemDiscoveryEvent(
                event_type="loot.item_discovered",
                character_id=event_data.get("character_id", 0),
                discovery_method=event_data.get("discovery_method", "unknown"),
                skill_used=event_data.get("skill_used", "unknown"),
                items_found_count=event_data.get("items_found_count", 0),
                skill_check_total=event_data.get("skill_check_total", 0),
                location=event_data.get("location", "Unknown Location")
            )
            self.event_dispatcher.publish_sync(event)
            
        except ImportError:
            logger.warning("ItemDiscoveryEvent not available - using generic event")
            self._publish_generic_event(event_data)
    
    def _publish_enchantment_event(self, event_data: Dict[str, Any]) -> None:
        """Publish item enchantment event"""
        try:
            from backend.infrastructure.systems.loot.events.loot_events_core import ItemEnhancementEvent
            
            event = ItemEnhancementEvent(
                event_type="loot.item_enhanced",
                item_id=str(event_data.get("item_id", "unknown")),
                item_name=event_data.get("item_name", "Unknown Item"),
                original_rarity="unknown",  # Not provided in business logic
                new_rarity="unknown",       # Not provided in business logic
                enhancement_type="enchantment",
                enhancement_level=1,
                success=event_data.get("success", True),
                character_id=event_data.get("character_id", 0),
                craft_skill_used="enchanting"
            )
            self.event_dispatcher.publish_sync(event)
            
        except ImportError:
            logger.warning("ItemEnhancementEvent not available - using generic event")
            self._publish_generic_event(event_data)
    
    def _publish_enchantment_failure_event(self, event_data: Dict[str, Any]) -> None:
        """Publish enchantment failure event"""
        try:
            from backend.infrastructure.systems.loot.events.loot_events_core import ItemEnhancementEvent
            
            event = ItemEnhancementEvent(
                event_type="loot.item_enhancement_failed",
                item_id=str(event_data.get("item_id", "unknown")),
                item_name=event_data.get("item_name", "Unknown Item"),
                original_rarity="unknown",
                new_rarity="unknown",
                enhancement_type="enchantment",
                enhancement_level=0,
                success=False,
                character_id=event_data.get("character_id", 0),
                craft_skill_used="enchanting"
            )
            self.event_dispatcher.publish_sync(event)
            
        except ImportError:
            logger.warning("ItemEnhancementEvent not available - using generic event")
            self._publish_generic_event(event_data)
    
    def _publish_shop_transaction_event(self, event_data: Dict[str, Any]) -> None:
        """Publish shop transaction event"""
        try:
            from backend.infrastructure.systems.loot.events.loot_events_core import ShopTransactionEvent
            
            event = ShopTransactionEvent(
                event_type="loot.shop_transaction",
                shop_id=event_data.get("shop_id", 0),
                shop_type=event_data.get("shop_type", "unknown"),
                character_id=event_data.get("character_id", 0),
                items_bought=[],
                items_sold=[{
                    "id": event_data.get("item_id", "unknown"),
                    "name": event_data.get("item_name", "Unknown Item"),
                    "price": event_data.get("sell_price", 0)
                }],
                total_cost=0,
                total_earned=event_data.get("sell_price", 0)
            )
            self.event_dispatcher.publish_sync(event)
            
        except ImportError:
            logger.warning("ShopTransactionEvent not available - using generic event")
            self._publish_generic_event(event_data)
    
    def _publish_identification_event(self, event_data: Dict[str, Any]) -> None:
        """Publish identification event"""
        try:
            from backend.infrastructure.systems.loot.events.loot_events_core import ItemIdentificationEvent
            
            event = ItemIdentificationEvent(
                event_type="loot.item_identified",
                item_id=str(event_data.get("item_id", "unknown")),
                item_name=event_data.get("item_name", "Unknown Item"),
                identification_method=event_data.get("identification_method", "unknown"),
                success=event_data.get("success", True),
                character_id=event_data.get("character_id", 0),
                skill_used=event_data.get("skill_used", "unknown"),
                cost=event_data.get("cost", 0)
            )
            self.event_dispatcher.publish_sync(event)
            
        except ImportError:
            logger.warning("ItemIdentificationEvent not available - using generic event")
            self._publish_generic_event(event_data)
    
    def _publish_generic_event(self, event_data: Dict[str, Any]) -> None:
        """Publish generic event as fallback"""
        try:
            from backend.infrastructure.events import EventBase
            
            class GenericLootEvent(EventBase):
                def __init__(self, **kwargs):
                    self.event_data = kwargs
            
            event = GenericLootEvent(**event_data)
            self.event_dispatcher.publish_sync(event)
            
        except Exception as e:
            logger.error(f"Failed to publish generic event: {e}")


class PriceAnalytics:
    """Infrastructure implementation for price analytics and logging"""
    
    def __init__(self):
        self.analytics_module = None
        try:
            from backend.infrastructure.systems.loot.utils import analytics
            self.analytics_module = analytics
        except ImportError:
            logger.warning("Analytics module not available - price adjustments will not be logged")
    
    def log_price_adjustment(self, item_id: int, item_name: str, old_price: int, new_price: int, 
                           multiplier: float, reason: str, region_id: int) -> None:
        """Log price adjustment"""
        if not self.analytics_module:
            return
        
        try:
            self.analytics_module.log_price_adjustment(
                item_id=item_id,
                item_name=item_name,
                old_price=old_price,
                new_price=new_price,
                multiplier=multiplier,
                reason=reason,
                region_id=region_id
            )
        except Exception as e:
            logger.error(f"Failed to log price adjustment: {e}")


class LootAnalytics:
    """Infrastructure implementation for general loot analytics"""
    
    def __init__(self):
        self.analytics_module = None
        try:
            from backend.infrastructure.systems.loot.utils import analytics
            self.analytics_module = analytics
        except ImportError:
            logger.warning("Analytics module not available - loot analytics will not be logged")
    
    def log_loot_acquisition(self, character_id: int, items: List[Dict[str, Any]], 
                           gold_amount: int, source_type: str, location_id: Optional[int] = None,
                           region_id: Optional[int] = None) -> None:
        """Log loot acquisition"""
        if not self.analytics_module:
            return
        
        try:
            self.analytics_module.log_loot_acquisition(
                character_id=character_id,
                items=items,
                gold_amount=gold_amount,
                source_type=source_type,
                location_id=location_id,
                region_id=region_id
            )
        except Exception as e:
            logger.error(f"Failed to log loot acquisition: {e}")
    
    def log_shop_transaction(self, character_id: int, shop_id: int, 
                           items_bought: List[Dict[str, Any]], items_sold: List[Dict[str, Any]],
                           gold_spent: int, gold_earned: int, location_id: Optional[int] = None,
                           region_id: Optional[int] = None) -> None:
        """Log shop transaction"""
        if not self.analytics_module:
            return
        
        try:
            self.analytics_module.log_shop_transaction(
                character_id=character_id,
                shop_id=shop_id,
                items_bought=items_bought,
                items_sold=items_sold,
                gold_spent=gold_spent,
                gold_earned=gold_earned,
                location_id=location_id,
                region_id=region_id
            )
        except Exception as e:
            logger.error(f"Failed to log shop transaction: {e}")


# Factory function to create integrated instances
def create_loot_infrastructure():
    """
    Create integrated loot infrastructure instances
    
    Returns:
        Tuple of (event_publisher, price_analytics, loot_analytics)
    """
    event_publisher = LootEventPublisher()
    price_analytics = PriceAnalytics()
    loot_analytics = LootAnalytics()
    
    return event_publisher, price_analytics, loot_analytics 