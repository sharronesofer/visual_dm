"""
Loot Events Module

This module contains all event classes for the loot system, providing
event-driven architecture for loot generation, item identification,
enhancement, and shop operations.

Expected by test files for proper system integration.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

# TODO: Re-enable when shared events are implemented
# from backend.infrastructure.events import EventDispatcher, EventBase

# Temporary stub for EventBase until shared events are implemented
class EventBase:
    """Temporary stub for EventBase class"""
    pass


class LootEventType(Enum):
    """Enumeration of loot event types"""
    LOOT_GENERATED = "loot.generated"
    ITEM_IDENTIFIED = "item.identified"
    ITEM_ENHANCEMENT = "item.enhancement"
    SHOP_INVENTORY = "shop.inventory"
    SHOP_TRANSACTION = "shop.transaction"
    LOOT_ANALYTICS = "loot.analytics"


class IdentificationResult(Enum):
    """Enumeration of identification results"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    CURSED = "cursed"


class EnhancementResult(Enum):
    """Enumeration of enhancement results"""
    SUCCESS = "success"
    FAILURE = "failure"
    CRITICAL_SUCCESS = "critical_success"
    CRITICAL_FAILURE = "critical_failure"
    ITEM_DESTROYED = "item_destroyed"


class TransactionType(Enum):
    """Enumeration of transaction types"""
    PURCHASE = "purchase"
    SALE = "sale"
    TRADE = "trade"
    REFUND = "refund"


@dataclass
class LootGeneratedEvent(EventBase):
    """
    Event triggered when loot is generated.
    
    This event is fired whenever the loot system generates items,
    whether from combat, chests, quests, or other sources.
    """
    event_type: str = field(default=LootEventType.LOOT_GENERATED.value)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Core event data
    location: Dict[str, Any] = field(default_factory=dict)
    loot_bundle: Dict[str, Any] = field(default_factory=dict)
    generation_context: Dict[str, Any] = field(default_factory=dict)
    
    # Additional metadata
    source_type: str = "unknown"  # combat, chest, quest, etc.
    player_id: Optional[str] = None
    session_id: Optional[str] = None
    total_value: float = 0.0
    item_count: int = 0
    rarity_distribution: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.loot_bundle:
            # Calculate derived metrics
            items = self.loot_bundle.get('items', [])
            self.item_count = len(items)
            
            # Calculate total value
            self.total_value = sum(item.get('value', 0) for item in items)
            
            # Calculate rarity distribution
            rarity_counts = {}
            for item in items:
                rarity = item.get('rarity', 'common')
                rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
            self.rarity_distribution = rarity_counts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_type': self.event_type,
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'location': self.location,
            'loot_bundle': self.loot_bundle,
            'generation_context': self.generation_context,
            'source_type': self.source_type,
            'player_id': self.player_id,
            'session_id': self.session_id,
            'total_value': self.total_value,
            'item_count': self.item_count,
            'rarity_distribution': self.rarity_distribution
        }


@dataclass
class ItemIdentificationEvent(EventBase):
    """
    Event triggered during item identification.
    
    This event is fired when a player attempts to identify an item,
    whether through skills, services, or magical means.
    """
    event_type: str = field(default=LootEventType.ITEM_IDENTIFIED.value)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Core event data
    item: Dict[str, Any] = field(default_factory=dict)
    identification_result: IdentificationResult = IdentificationResult.SUCCESS
    player_context: Dict[str, Any] = field(default_factory=dict)
    
    # Identification details
    identification_method: str = "skill"  # skill, service, magic, scroll
    cost_paid: float = 0.0
    skill_level: int = 0
    success_probability: float = 0.0
    properties_revealed: List[str] = field(default_factory=list)
    
    # Results
    identified_properties: Dict[str, Any] = field(default_factory=dict)
    hidden_properties: Dict[str, Any] = field(default_factory=dict)
    curse_detected: bool = False
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Calculate success probability based on context
        if self.player_context and self.item:
            item_rarity = self.item.get('rarity', 'common')
            base_difficulty = {
                'common': 0.9,
                'uncommon': 0.7,
                'rare': 0.5,
                'epic': 0.3,
                'legendary': 0.1
            }.get(item_rarity, 0.5)
            
            skill_bonus = min(self.skill_level * 0.05, 0.4)
            self.success_probability = min(base_difficulty + skill_bonus, 0.95)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_type': self.event_type,
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'item': self.item,
            'identification_result': self.identification_result.value,
            'player_context': self.player_context,
            'identification_method': self.identification_method,
            'cost_paid': self.cost_paid,
            'skill_level': self.skill_level,
            'success_probability': self.success_probability,
            'properties_revealed': self.properties_revealed,
            'identified_properties': self.identified_properties,
            'hidden_properties': self.hidden_properties,
            'curse_detected': self.curse_detected
        }


@dataclass
class ItemEnhancementEvent(EventBase):
    """
    Event triggered during item enhancement.
    
    This event is fired when a player attempts to enhance an item
    through enchantment, upgrading, or other modification methods.
    """
    event_type: str = field(default=LootEventType.ITEM_ENHANCEMENT.value)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Core event data
    item: Dict[str, Any] = field(default_factory=dict)
    enhancement_type: str = "enchantment"
    success_result: EnhancementResult = EnhancementResult.SUCCESS
    
    # Enhancement details
    enhancement_level: int = 1
    materials_used: List[Dict[str, Any]] = field(default_factory=list)
    cost_paid: float = 0.0
    success_probability: float = 0.0
    risk_level: str = "low"  # low, medium, high, extreme
    
    # Results
    enhancement_applied: Dict[str, Any] = field(default_factory=dict)
    stat_changes: Dict[str, float] = field(default_factory=dict)
    new_properties: List[str] = field(default_factory=list)
    item_destroyed: bool = False
    
    # Context
    enhancer_skill: int = 0
    workshop_quality: str = "basic"
    special_conditions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Calculate success probability based on enhancement level and risk
        base_success = {
            "low": 0.9,
            "medium": 0.7,
            "high": 0.5,
            "extreme": 0.3
        }.get(self.risk_level, 0.7)
        
        # Adjust for enhancement level (higher levels are harder)
        level_penalty = (self.enhancement_level - 1) * 0.1
        skill_bonus = min(self.enhancer_skill * 0.02, 0.3)
        
        self.success_probability = max(base_success - level_penalty + skill_bonus, 0.05)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_type': self.event_type,
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'item': self.item,
            'enhancement_type': self.enhancement_type,
            'success_result': self.success_result.value,
            'enhancement_level': self.enhancement_level,
            'materials_used': self.materials_used,
            'cost_paid': self.cost_paid,
            'success_probability': self.success_probability,
            'risk_level': self.risk_level,
            'enhancement_applied': self.enhancement_applied,
            'stat_changes': self.stat_changes,
            'new_properties': self.new_properties,
            'item_destroyed': self.item_destroyed,
            'enhancer_skill': self.enhancer_skill,
            'workshop_quality': self.workshop_quality,
            'special_conditions': self.special_conditions
        }


@dataclass
class ShopInventoryEvent(EventBase):
    """
    Event triggered when shop inventory changes.
    
    This event is fired when shop inventory is updated, restocked,
    or modified through various means.
    """
    event_type: str = field(default=LootEventType.SHOP_INVENTORY.value)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Core event data
    shop: Dict[str, Any] = field(default_factory=dict)
    inventory_changes: Dict[str, Any] = field(default_factory=dict)
    economic_context: Dict[str, Any] = field(default_factory=dict)
    
    # Shop details
    shop_id: str = ""
    shop_type: str = "general_store"
    location: Dict[str, Any] = field(default_factory=dict)
    
    # Inventory changes
    items_added: List[Dict[str, Any]] = field(default_factory=list)
    items_removed: List[Dict[str, Any]] = field(default_factory=list)
    items_modified: List[Dict[str, Any]] = field(default_factory=list)
    price_changes: Dict[str, float] = field(default_factory=dict)
    
    # Economic factors
    supply_demand_factors: Dict[str, float] = field(default_factory=dict)
    regional_modifiers: Dict[str, float] = field(default_factory=dict)
    seasonal_effects: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    restock_reason: str = "scheduled"  # scheduled, sold_out, event, manual
    total_inventory_value: float = 0.0
    inventory_count: int = 0
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Calculate total inventory metrics
        all_items = self.items_added + self.items_modified
        self.inventory_count = len(all_items)
        self.total_inventory_value = sum(item.get('price', 0) for item in all_items)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_type': self.event_type,
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'shop': self.shop,
            'inventory_changes': self.inventory_changes,
            'economic_context': self.economic_context,
            'shop_id': self.shop_id,
            'shop_type': self.shop_type,
            'location': self.location,
            'items_added': self.items_added,
            'items_removed': self.items_removed,
            'items_modified': self.items_modified,
            'price_changes': self.price_changes,
            'supply_demand_factors': self.supply_demand_factors,
            'regional_modifiers': self.regional_modifiers,
            'seasonal_effects': self.seasonal_effects,
            'restock_reason': self.restock_reason,
            'total_inventory_value': self.total_inventory_value,
            'inventory_count': self.inventory_count
        }


@dataclass
class ShopTransactionEvent(EventBase):
    """
    Event triggered during shop transactions.
    
    This event is fired when players buy, sell, or trade items
    with shops, including all transaction details.
    """
    event_type: str = field(default=LootEventType.SHOP_TRANSACTION.value)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Core event data
    shop: Dict[str, Any] = field(default_factory=dict)
    item: Dict[str, Any] = field(default_factory=dict)
    transaction_type: TransactionType = TransactionType.PURCHASE
    price: float = 0.0
    player: Dict[str, Any] = field(default_factory=dict)
    
    # Transaction details
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    shop_id: str = ""
    player_id: str = ""
    item_id: str = ""
    quantity: int = 1
    
    # Pricing breakdown
    base_price: float = 0.0
    shop_modifier: float = 1.0
    reputation_modifier: float = 1.0
    economic_modifier: float = 1.0
    bulk_discount: float = 0.0
    final_price: float = 0.0
    
    # Context
    player_reputation: int = 0
    shop_relationship: str = "neutral"  # hostile, unfriendly, neutral, friendly, allied
    economic_conditions: Dict[str, float] = field(default_factory=dict)
    
    # Results
    transaction_successful: bool = True
    failure_reason: Optional[str] = None
    reputation_change: int = 0
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Calculate final price if not set
        if self.final_price == 0.0:
            self.final_price = (
                self.base_price * 
                self.shop_modifier * 
                self.reputation_modifier * 
                self.economic_modifier * 
                self.quantity
            ) - self.bulk_discount
            
        # Set price to final price if not explicitly set
        if self.price == 0.0:
            self.price = self.final_price
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_type': self.event_type,
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'shop': self.shop,
            'item': self.item,
            'transaction_type': self.transaction_type.value,
            'price': self.price,
            'player': self.player,
            'transaction_id': self.transaction_id,
            'shop_id': self.shop_id,
            'player_id': self.player_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'base_price': self.base_price,
            'shop_modifier': self.shop_modifier,
            'reputation_modifier': self.reputation_modifier,
            'economic_modifier': self.economic_modifier,
            'bulk_discount': self.bulk_discount,
            'final_price': self.final_price,
            'player_reputation': self.player_reputation,
            'shop_relationship': self.shop_relationship,
            'economic_conditions': self.economic_conditions,
            'transaction_successful': self.transaction_successful,
            'failure_reason': self.failure_reason,
            'reputation_change': self.reputation_change
        }


@dataclass
class LootAnalyticsEvent(EventBase):
    """
    Event for loot system analytics and monitoring.
    
    This event is used for tracking system performance,
    balance metrics, and player behavior analytics.
    """
    event_type: str = field(default=LootEventType.LOOT_ANALYTICS.value)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Analytics data
    event_category: str = "loot"
    event_action: str = "generation"
    source_type: str = "unknown"
    location_id: Optional[int] = None
    region_id: Optional[int] = None
    gold_amount: float = 0.0
    value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_type': self.event_type,
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_category': self.event_category,
            'event_action': self.event_action,
            'source_type': self.source_type,
            'location_id': self.location_id,
            'region_id': self.region_id,
            'gold_amount': self.gold_amount,
            'value': self.value,
            'metadata': self.metadata
        }


# Event factory functions for easy creation
def create_loot_generated_event(
    location: Dict[str, Any],
    loot_bundle: Dict[str, Any],
    generation_context: Dict[str, Any],
    source_type: str = "unknown",
    player_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> LootGeneratedEvent:
    """Create a LootGeneratedEvent with the provided data"""
    return LootGeneratedEvent(
        location=location,
        loot_bundle=loot_bundle,
        generation_context=generation_context,
        source_type=source_type,
        player_id=player_id,
        session_id=session_id
    )


def create_item_identification_event(
    item: Dict[str, Any],
    player_context: Dict[str, Any],
    identification_method: str = "skill",
    skill_level: int = 0
) -> ItemIdentificationEvent:
    """Create an ItemIdentificationEvent with the provided data"""
    return ItemIdentificationEvent(
        item=item,
        player_context=player_context,
        identification_method=identification_method,
        skill_level=skill_level
    )


def create_item_enhancement_event(
    item: Dict[str, Any],
    enhancement_type: str = "enchantment",
    enhancement_level: int = 1,
    materials_used: Optional[List[Dict[str, Any]]] = None,
    enhancer_skill: int = 0
) -> ItemEnhancementEvent:
    """Create an ItemEnhancementEvent with the provided data"""
    return ItemEnhancementEvent(
        item=item,
        enhancement_type=enhancement_type,
        enhancement_level=enhancement_level,
        materials_used=materials_used or [],
        enhancer_skill=enhancer_skill
    )


def create_shop_inventory_event(
    shop: Dict[str, Any],
    inventory_changes: Dict[str, Any],
    economic_context: Dict[str, Any],
    restock_reason: str = "scheduled"
) -> ShopInventoryEvent:
    """Create a ShopInventoryEvent with the provided data"""
    return ShopInventoryEvent(
        shop=shop,
        inventory_changes=inventory_changes,
        economic_context=economic_context,
        restock_reason=restock_reason
    )


def create_shop_transaction_event(
    shop: Dict[str, Any],
    item: Dict[str, Any],
    player: Dict[str, Any],
    transaction_type: TransactionType = TransactionType.PURCHASE,
    price: float = 0.0,
    quantity: int = 1
) -> ShopTransactionEvent:
    """Create a ShopTransactionEvent with the provided data"""
    return ShopTransactionEvent(
        shop=shop,
        item=item,
        player=player,
        transaction_type=transaction_type,
        price=price,
        quantity=quantity
    )


# Event publishing utilities
class LootEventPublisher:
    """Utility class for publishing loot events"""
    
    @staticmethod
    def publish_loot_generated(event: LootGeneratedEvent) -> None:
        """Publish a loot generated event"""
        # TODO: Re-enable when shared events are implemented
        # dispatcher = EventDispatcher.get_instance()
        # dispatcher.publish_sync(event)
        pass
    
    @staticmethod
    def publish_item_identification(event: ItemIdentificationEvent) -> None:
        """Publish an item identification event"""
        # TODO: Re-enable when shared events are implemented
        # dispatcher = EventDispatcher.get_instance()
        # dispatcher.publish_sync(event)
        pass
    
    @staticmethod
    def publish_item_enhancement(event: ItemEnhancementEvent) -> None:
        """Publish an item enhancement event"""
        # TODO: Re-enable when shared events are implemented
        # dispatcher = EventDispatcher.get_instance()
        # dispatcher.publish_sync(event)
        pass
    
    @staticmethod
    def publish_shop_inventory(event: ShopInventoryEvent) -> None:
        """Publish a shop inventory event"""
        # TODO: Re-enable when shared events are implemented
        # dispatcher = EventDispatcher.get_instance()
        # dispatcher.publish_sync(event)
        pass
    
    @staticmethod
    def publish_shop_transaction(event: ShopTransactionEvent) -> None:
        """Publish a shop transaction event"""
        # TODO: Re-enable when shared events are implemented
        # dispatcher = EventDispatcher.get_instance()
        # dispatcher.publish_sync(event)
        pass
    
    @staticmethod
    def publish_loot_analytics(event: LootAnalyticsEvent) -> None:
        """Publish a loot analytics event"""
        # TODO: Re-enable when shared events are implemented
        # dispatcher = EventDispatcher.get_instance()
        # dispatcher.publish_sync(event)
        pass


# Export all event classes and utilities
__all__ = [
    'LootEventType',
    'IdentificationResult',
    'EnhancementResult',
    'TransactionType',
    'LootGeneratedEvent',
    'ItemIdentificationEvent',
    'ItemEnhancementEvent',
    'ShopInventoryEvent',
    'ShopTransactionEvent',
    'LootAnalyticsEvent',
    'create_loot_generated_event',
    'create_item_identification_event',
    'create_item_enhancement_event',
    'create_shop_inventory_event',
    'create_shop_transaction_event',
    'LootEventPublisher'
] 