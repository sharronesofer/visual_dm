"""
Identification System Infrastructure Integration

This module provides the technical infrastructure integration for the loot identification system,
handling events, logging, and economic calculations.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class IdentificationEventPublisher:
    """Infrastructure implementation for publishing identification events"""
    
    def __init__(self):
        self.event_dispatcher = None
        try:
            from backend.infrastructure.events import EventDispatcher
            self.event_dispatcher = EventDispatcher.get_instance()
        except ImportError:
            logger.warning("Event dispatcher not available - events will not be published")
    
    def publish_identification_event(self, event_data: Dict[str, Any]) -> None:
        """Publish identification event with logging and error handling"""
        try:
            if self.event_dispatcher:
                from backend.infrastructure.systems.loot.events.loot_events_core import ItemIdentificationEvent
                
                event = ItemIdentificationEvent(
                    event_type=event_data.get("event_type", "loot.item_identified"),
                    item_id=event_data.get("item_id", ""),
                    item_name=event_data.get("item_name", "Unknown Item"),
                    item_rarity=event_data.get("item_rarity", "common"),
                    identification_method=event_data.get("identification_method", "unknown"),
                    identification_result=event_data.get("identification_result", "failure"),
                    identification_level=event_data.get("identification_level", 0),
                    character_id=event_data.get("character_id", 0),
                    skill_level=event_data.get("skill_level", 0),
                    cost_paid=event_data.get("cost_paid", 0),
                    properties_revealed=event_data.get("properties_revealed", [])
                )
                
                self.event_dispatcher.publish_sync(event)
                logger.debug(f"Published identification event for item {event_data.get('item_name')}")
            else:
                logger.debug(f"Event dispatcher not available - skipping event: {event_data}")
        except Exception as e:
            logger.error(f"Failed to publish identification event: {e}")


class IdentificationEconomicCalculator:
    """Infrastructure implementation for economic calculations in identification"""
    
    def apply_economic_factors_to_price(self, cost: int, region_id: int, item_name: str) -> int:
        """Apply economic factors to identification cost using infrastructure services"""
        try:
            # Use the economic integration from shared functions
            from backend.infrastructure.systems.loot.utils.economic_integration import apply_economic_factors_to_price
            return apply_economic_factors_to_price(cost, region_id, item_name)
        except ImportError:
            logger.warning("Economic integration not available - using fallback calculation")
            return self._fallback_price_calculation(cost, region_id, item_name)
        except Exception as e:
            logger.error(f"Error applying economic factors to identification cost: {e}")
            return cost
    
    def _fallback_price_calculation(self, cost: int, region_id: int, item_name: str) -> int:
        """Simple fallback calculation when economic system unavailable"""
        # Apply basic regional modifier
        regional_modifiers = {
            1: 1.2,  # Capital - expensive
            2: 0.9,  # Rural - cheaper
            3: 1.1,  # Trade center - moderate markup
            4: 0.8,  # Frontier - very cheap
        }
        
        modifier = regional_modifiers.get(region_id, 1.0)
        adjusted_cost = int(cost * modifier)
        return max(1, adjusted_cost)


# Factory function for creating a fully configured identification system
def create_identification_system_with_infrastructure():
    """Create identification system with infrastructure dependencies injected"""
    from backend.systems.loot.utils.identification_system import TieredIdentificationSystem
    
    event_publisher = IdentificationEventPublisher()
    economic_calculator = IdentificationEconomicCalculator()
    
    return TieredIdentificationSystem(
        event_publisher=event_publisher,
        economic_calculator=economic_calculator
    ) 