"""
Consolidated Item model.
Provides a single authoritative definition for items in the game.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import db
import enum
from app.core.models.inventory import InventoryItem
from app.core.models.equipment import EquipmentInstance

class ItemType(enum.Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"
    KEY = "key"
    CONTAINER = "container"
    TOOL = "tool"
    TREASURE = "treasure"
    MISC = "misc"

class ItemRarity(enum.Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    UNIQUE = "unique"

class Item(db.Model):
    """
    Represents an item in the game world
    """
    __tablename__ = 'items'

    # Basic Info
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50))
    rarity = Column(String(50), default=ItemRarity.COMMON.value)
    level = Column(Integer, default=1)
    value = Column(Integer, default=0)
    weight = Column(Float, default=0.0)
    is_stackable = Column(Boolean, default=False)
    max_stack = Column(Integer, default=1)
    is_tradeable = Column(Boolean, default=True)
    is_consumable = Column(Boolean, default=False)
    is_quest_item = Column(Boolean, default=False)
    
    # Item Stats and Properties
    stats = Column(JSON, default=lambda: {
        'damage': 0,
        'armor': 0,
        'durability': 100,
        'max_durability': 100,
        'requirements': {
            'level': 1,
            'stats': {},
            'skills': {}
        }
    })
    
    properties = Column(JSON, default=lambda: {
        'effects': [],
        'enchantments': [],
        'sockets': [],
        'modifiers': [],
        'set': None
    })
    
    # Usage Information
    usage = Column(JSON, default=lambda: {
        'cooldown': 0,
        'charges': None,
        'duration': None,
        'range': None,
        'area': None,
        'targeting': None
    })
    
    # Crafting Information
    crafting = Column(JSON, default=lambda: {
        'recipe': None,
        'materials': [],
        'tools': [],
        'skills': [],
        'time': 0
    })
    
    # Item State
    state = Column(JSON, default=lambda: {
        'condition': 100,
        'equipped': False,
        'bound_to': None,
        'created_at': datetime.utcnow().isoformat(),
        'modified_at': datetime.utcnow().isoformat(),
        'history': []
    })

    # Relationships
    inventory_items = relationship('InventoryItem', back_populates='item')
    equipment_instances = relationship('EquipmentInstance', back_populates='item')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.properties = kwargs.get('properties', {})

    def to_dict(self) -> Dict:
        """Convert item to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'rarity': self.rarity,
            'weight': self.weight,
            'value': self.value,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update(self, data: Dict) -> None:
        """Update item properties."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def is_equippable(self) -> bool:
        """Check if item can be equipped."""
        return self.type in ['weapon', 'armor', 'shield', 'accessory']

    def is_consumable(self) -> bool:
        """Check if item is consumable."""
        return self.type == 'consumable'

    def is_stackable(self) -> bool:
        """Check if item can be stacked in inventory."""
        return self.type in ['consumable', 'material', 'currency']

    def get_equipment_slot(self) -> Optional[str]:
        """Get the equipment slot this item can be equipped to."""
        return self.properties.get('equipment_slot')

    def get_requirements(self) -> Dict:
        """Get any requirements for using this item."""
        return self.stats['requirements']

    def get_effects(self) -> List[Dict]:
        """Get any effects this item has when used."""
        return self.properties['effects']

    def use(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Use the item and return the effects
        """
        if not self._can_use(user_data):
            return None
        
        effects = []
        
        # Process item effects
        for effect in self.properties['effects']:
            effect_result = self._process_effect(effect, user_data)
            if effect_result:
                effects.append(effect_result)
        
        # Update item state
        if self.is_consumable:
            self.delete()
        else:
            if 'charges' in self.usage and self.usage['charges']:
                self.usage['charges'] -= 1
                if self.usage['charges'] <= 0:
                    self.delete()
            
            if 'durability' in self.stats:
                self.stats['durability'] = max(0, self.stats['durability'] - 1)
                if self.stats['durability'] <= 0:
                    self.state['condition'] = 0
        
        self.state['modified_at'] = datetime.utcnow().isoformat()
        self.save()
        
        return {
            'effects': effects,
            'item_consumed': self.is_consumable,
            'durability': self.stats.get('durability'),
            'charges': self.usage.get('charges')
        }

    def repair(self, amount: int) -> Dict[str, Any]:
        """
        Repair the item's durability
        """
        if 'durability' not in self.stats:
            return {
                'success': False,
                'reason': 'item_not_repairable'
            }
        
        old_durability = self.stats['durability']
        self.stats['durability'] = min(
            self.stats['max_durability'],
            self.stats['durability'] + amount
        )
        
        self.state['modified_at'] = datetime.utcnow().isoformat()
        self.state['history'].append({
            'type': 'repair',
            'amount': amount,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        self.save()
        
        return {
            'success': True,
            'old_durability': old_durability,
            'new_durability': self.stats['durability'],
            'amount_repaired': self.stats['durability'] - old_durability
        }

    def enhance(self, enhancement: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an enhancement (enchantment, modifier, etc.) to the item
        """
        enhancement_type = enhancement['type']
        
        if enhancement_type == 'enchantment':
            if len(self.properties['enchantments']) >= 3:
                return {
                    'success': False,
                    'reason': 'max_enchantments_reached'
                }
            self.properties['enchantments'].append(enhancement)
        
        elif enhancement_type == 'modifier':
            if len(self.properties['modifiers']) >= 5:
                return {
                    'success': False,
                    'reason': 'max_modifiers_reached'
                }
            self.properties['modifiers'].append(enhancement)
        
        elif enhancement_type == 'socket':
            if len(self.properties['sockets']) >= 3:
                return {
                    'success': False,
                    'reason': 'max_sockets_reached'
                }
            self.properties['sockets'].append(enhancement)
        
        self.state['modified_at'] = datetime.utcnow().isoformat()
        self.state['history'].append({
            'type': 'enhancement',
            'enhancement': enhancement,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        self.save()
        
        return {
            'success': True,
            'enhancement_type': enhancement_type,
            'enhancement': enhancement
        }

    def bind_to_player(self, player_id: int) -> Dict[str, Any]:
        """
        Bind the item to a specific player
        """
        if self.state['bound_to']:
            return {
                'success': False,
                'reason': 'already_bound',
                'bound_to': self.state['bound_to']
            }
        
        self.state['bound_to'] = player_id
        self.state['modified_at'] = datetime.utcnow().isoformat()
        self.state['history'].append({
            'type': 'binding',
            'player_id': player_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        self.save()
        
        return {
            'success': True,
            'bound_to': player_id
        }

    def _can_use(self, user_data: Dict[str, Any]) -> bool:
        """
        Check if the item can be used by the user
        """
        # Check if item is usable
        if self.state['condition'] <= 0:
            return False
        
        # Check level requirement
        if user_data['level'] < self.stats['requirements']['level']:
            return False
        
        # Check stat requirements
        for stat, required in self.stats['requirements']['stats'].items():
            if user_data['stats'].get(stat, 0) < required:
                return False
        
        # Check skill requirements
        for skill, required in self.stats['requirements']['skills'].items():
            if user_data['skills'].get(skill, 0) < required:
                return False
        
        # Check cooldown
        if self.usage['cooldown'] > 0:
            # TODO: Implement cooldown checking
            pass
        
        return True

    def _process_effect(self, effect: Dict[str, Any], user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single effect of the item
        """
        effect_type = effect['type']
        result = {
            'type': effect_type,
            'success': True
        }
        
        if effect_type == 'heal':
            amount = effect['amount']
            # TODO: Apply healing to user
            result['amount'] = amount
        
        elif effect_type == 'damage':
            amount = effect['amount']
            damage_type = effect['damage_type']
            # TODO: Apply damage to target
            result.update({
                'amount': amount,
                'damage_type': damage_type
            })
        
        elif effect_type == 'buff':
            stat = effect['stat']
            amount = effect['amount']
            duration = effect['duration']
            # TODO: Apply buff to user
            result.update({
                'stat': stat,
                'amount': amount,
                'duration': duration
            })
        
        elif effect_type == 'teleport':
            destination = effect['destination']
            # TODO: Teleport user
            result['destination'] = destination
        
        return result 