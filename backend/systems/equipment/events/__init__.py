"""
Equipment system events for Visual DM.

Provides event types and publishers for equipment-related events including
durability changes, repairs, enchantments, and equipment lifecycle events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

class EquipmentEventType(Enum):
    """Types of equipment events that can occur."""
    DURABILITY_CHANGED = "durability_changed"
    REPAIR_COMPLETED = "repair_completed"
    REPAIR_FAILED = "repair_failed"
    ENCHANTMENT_APPLIED = "enchantment_applied"
    ENCHANTMENT_FAILED = "enchantment_failed"
    DISENCHANTMENT_COMPLETED = "disenchantment_completed"
    DISENCHANTMENT_FAILED = "disenchantment_failed"
    IDENTIFICATION_COMPLETED = "identification_completed"
    SET_BONUS_ACTIVATED = "set_bonus_activated"
    SET_BONUS_DEACTIVATED = "set_bonus_deactivated"
    EQUIPMENT_CREATED = "equipment_created"
    EQUIPMENT_DESTROYED = "equipment_destroyed"
    EQUIPMENT_EQUIPPED = "equipment_equipped"
    EQUIPMENT_UNEQUIPPED = "equipment_unequipped"

@dataclass
class BaseEquipmentEvent:
    """Base class for all equipment events."""
    event_type: EquipmentEventType
    timestamp: datetime
    equipment_id: str
    character_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DurabilityChangedEvent(BaseEquipmentEvent):
    """Event fired when equipment durability changes."""
    old_durability: float = 0.0
    new_durability: float = 0.0
    old_status: str = ""
    new_status: str = ""
    cause: str = ""  # "time_decay", "combat", "repair", etc.

@dataclass
class RepairEvent(BaseEquipmentEvent):
    """Event fired when equipment repair is attempted."""
    repair_cost: int = 0
    materials_used: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = True
    durability_restored: Optional[float] = None
    failure_reason: Optional[str] = None

@dataclass
class EnchantmentEvent(BaseEquipmentEvent):
    """Event fired when enchantment is applied or attempted."""
    enchantment_id: str = ""
    enchantment_name: str = ""
    success: bool = True
    cost: int = 0
    character_skill_level: int = 0
    failure_reason: Optional[str] = None

@dataclass
class DisenchantmentEvent(BaseEquipmentEvent):
    """Event fired when disenchantment is attempted."""
    enchantment_learned: Optional[str] = None
    enchantment_name: Optional[str] = None
    success: bool = True
    character_skill_level: int = 0
    item_destroyed: bool = False
    failure_reason: Optional[str] = None

@dataclass
class IdentificationEvent(BaseEquipmentEvent):
    """Event fired when equipment is identified."""
    identification_level: int = 0
    abilities_revealed: List[str] = field(default_factory=list)
    cost: int = 0
    is_automatic: bool = False  # True for level-up identification

@dataclass
class SetBonusEvent(BaseEquipmentEvent):
    """Event fired when set bonuses change."""
    set_name: str = ""
    pieces_equipped: int = 0
    bonus_level: int = 0
    bonuses_applied: Dict[str, Any] = field(default_factory=dict)
    conflicts_detected: List[str] = field(default_factory=list)

@dataclass
class EquipmentLifecycleEvent(BaseEquipmentEvent):
    """Event fired for equipment creation/destruction/equipping."""
    equipment_name: str = ""
    equipment_rarity: str = ""
    equipment_quality: str = ""
    location: Optional[str] = None  # "inventory", "equipped", "destroyed"

# Event publishing interface
class EquipmentEventPublisher:
    """Publisher for equipment events to integrate with the broader event system."""
    
    def __init__(self):
        self.subscribers = []
    
    def subscribe(self, callback):
        """Subscribe to equipment events."""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback):
        """Unsubscribe from equipment events."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def publish(self, event: BaseEquipmentEvent):
        """Publish an equipment event to all subscribers."""
        for callback in self.subscribers:
            try:
                callback(event)
            except Exception as e:
                # Log error but don't let one subscriber break others
                print(f"Error in equipment event subscriber: {e}")
    
    def publish_event(self, event_type: EquipmentEventType, data: dict):
        """Publish an equipment event with simplified data format."""
        event = BaseEquipmentEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            equipment_id=data.get('item_id', ''),
            character_id=data.get('character_id'),
            metadata=data
        )
        self.publish(event)
    
    def publish_durability_changed(self, equipment_id: str, old_durability: float, 
                                 new_durability: float, old_status: str, new_status: str,
                                 cause: str, character_id: str = None, metadata: dict = None):
        """Convenience method to publish durability change events."""
        event = DurabilityChangedEvent(
            event_type=EquipmentEventType.DURABILITY_CHANGED,
            timestamp=datetime.now(),
            equipment_id=equipment_id,
            character_id=character_id,
            metadata=metadata,
            old_durability=old_durability,
            new_durability=new_durability,
            old_status=old_status,
            new_status=new_status,
            cause=cause
        )
        self.publish(event)
    
    def publish_repair_completed(self, equipment_id: str, repair_cost: int, 
                               materials_used: list, durability_restored: float,
                               character_id: str = None, metadata: dict = None):
        """Convenience method to publish successful repair events."""
        event = RepairEvent(
            event_type=EquipmentEventType.REPAIR_COMPLETED,
            timestamp=datetime.now(),
            equipment_id=equipment_id,
            character_id=character_id,
            metadata=metadata,
            repair_cost=repair_cost,
            materials_used=materials_used,
            success=True,
            durability_restored=durability_restored
        )
        self.publish(event)
    
    def publish_identification_completed(self, equipment_id: str, identification_level: int,
                                       abilities_revealed: list, cost: int, is_automatic: bool = False,
                                       character_id: str = None, metadata: dict = None):
        """Convenience method to publish identification events."""
        event = IdentificationEvent(
            event_type=EquipmentEventType.IDENTIFICATION_COMPLETED,
            timestamp=datetime.now(),
            equipment_id=equipment_id,
            character_id=character_id,
            metadata=metadata,
            identification_level=identification_level,
            abilities_revealed=abilities_revealed,
            cost=cost,
            is_automatic=is_automatic
        )
        self.publish(event)
    
    def publish_enchantment_applied(self, equipment_id: str, enchantment_id: str,
                                  character_id: str, cost: int, power_level: int,
                                  metadata: dict = None):
        """Convenience method to publish successful enchantment events."""
        event = EnchantmentEvent(
            event_type=EquipmentEventType.ENCHANTMENT_APPLIED,
            timestamp=datetime.now(),
            equipment_id=equipment_id,
            character_id=character_id,
            metadata=metadata,
            enchantment_id=enchantment_id,
            enchantment_name=metadata.get('enchantment_name', '') if metadata else '',
            success=True,
            cost=cost,
            character_skill_level=metadata.get('character_skill_level', 0) if metadata else 0
        )
        self.publish(event)
    
    def publish_enchantment_failed(self, equipment_id: str, enchantment_id: str,
                                 character_id: str, cost: int, failure_reason: str,
                                 materials_lost: bool = False, metadata: dict = None):
        """Convenience method to publish failed enchantment events."""
        event = EnchantmentEvent(
            event_type=EquipmentEventType.ENCHANTMENT_FAILED,
            timestamp=datetime.now(),
            equipment_id=equipment_id,
            character_id=character_id,
            metadata=metadata,
            enchantment_id=enchantment_id,
            enchantment_name=metadata.get('enchantment_name', '') if metadata else '',
            success=False,
            cost=cost,
            character_skill_level=metadata.get('character_skill_level', 0) if metadata else 0,
            failure_reason=failure_reason
        )
        self.publish(event)
    
    def publish_disenchantment_completed(self, equipment_id: str, character_id: str,
                                       enchantment_learned: str, success: bool,
                                       character_skill_level: int, metadata: dict = None):
        """Convenience method to publish disenchantment events."""
        event = DisenchantmentEvent(
            event_type=EquipmentEventType.DISENCHANTMENT_COMPLETED,
            timestamp=datetime.now(),
            equipment_id=equipment_id,
            character_id=character_id,
            metadata=metadata,
            enchantment_learned=enchantment_learned,
            success=success,
            character_skill_level=character_skill_level
        )
        self.publish(event)


# Global event publisher instance
equipment_event_publisher = EquipmentEventPublisher()

# Convenience functions
def publish_equipment_event(event_type: EquipmentEventType, data: dict):
    """Convenience function to publish equipment events."""
    equipment_event_publisher.publish_event(event_type, data)

def subscribe_to_equipment_events(callback):
    """Convenience function to subscribe to equipment events."""
    equipment_event_publisher.subscribe(callback)

__all__ = [
    'EquipmentEventType',
    'BaseEquipmentEvent',
    'DurabilityChangedEvent',
    'RepairEvent',
    'EnchantmentEvent',
    'DisenchantmentEvent',
    'IdentificationEvent',
    'SetBonusEvent',
    'EquipmentLifecycleEvent',
    'EquipmentEventPublisher',
    'equipment_event_publisher'
]

