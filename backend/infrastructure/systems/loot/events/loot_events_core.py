"""
Core event definitions for the loot system.
Extracted from loot_utils_core.py to separate infrastructure from business logic.
"""

from typing import Dict, List, Any, Optional
from backend.infrastructure.events import EventDispatcher, EventBase

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

class PriceAdjustmentEvent(EventBase):
    """Event emitted when item prices are adjusted"""
    event_type: str = "loot.price_adjusted"
    item_id: int
    item_name: str
    old_price: int
    new_price: int
    adjustment_factor: float
    reason: str
    region_id: int 