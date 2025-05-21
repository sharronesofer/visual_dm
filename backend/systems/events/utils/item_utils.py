"""
Item management utilities.
Inherits from BaseManager for common functionality.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from app.utils.config_utils import get_config
from app.utils.game_utils import GameCalculator
from app.core.utils.base_manager import BaseManager

logger = logging.getLogger(__name__)

class ItemManager(BaseManager):
    """Manager for game items and inventory"""
    
    def __init__(self) -> None:
        """Initialize the item manager."""
        super().__init__('items')
        self.config = get_config()
        self.calculator = GameCalculator()
    
    def generate_item(
        self,
        level: int,
        item_type: str,
        rarity: str = 'common'
    ) -> Dict[str, Any]:
        """Generate a game item"""
        try:
            # Item type characteristics
            item_data = {
                'weapon': {
                    'types': ['sword', 'axe', 'bow', 'staff', 'dagger'],
                    'attributes': ['damage', 'speed', 'accuracy'],
                    'slots': ['main_hand', 'off_hand']
                },
                'armor': {
                    'types': ['helmet', 'chest', 'gloves', 'boots', 'shield'],
                    'attributes': ['defense', 'resistance', 'durability'],
                    'slots': ['head', 'chest', 'hands', 'feet', 'off_hand']
                },
                'accessory': {
                    'types': ['ring', 'amulet', 'belt', 'cloak'],
                    'attributes': ['health', 'mana', 'luck', 'speed'],
                    'slots': ['finger', 'neck', 'waist', 'back']
                },
                'consumable': {
                    'types': ['potion', 'scroll', 'food', 'bomb'],
                    'attributes': ['healing', 'buff', 'damage', 'utility'],
                    'slots': ['inventory']
                }
            }
            
            # Rarity multipliers
            rarity_multipliers = {
                'common': 1.0,
                'uncommon': 1.5,
                'rare': 2.0,
                'epic': 3.0,
                'legendary': 5.0
            }
            
            # Get item type data
            item_info = item_data.get(item_type, item_data['weapon'])
            
            # Generate item details
            item = {
                'type': item_type,
                'subtype': random.choice(item_info['types']),
                'level': level,
                'rarity': rarity,
                'name': self._generate_name(
                    {
                        'common': ['Rusty', 'Worn', 'Simple'],
                        'uncommon': ['Polished', 'Sturdy', 'Fine'],
                        'rare': ['Enchanted', 'Masterwork', 'Exquisite'],
                        'epic': ['Mythic', 'Legendary', 'Divine'],
                        'legendary': ['Ancient', 'Celestial', 'Eternal']
                    },
                    item_info['types'][0],
                    rarity
                ),
                'description': self._generate_description(
                    item_type,
                    item_info['types'][0],
                    rarity
                ),
                'attributes': self._generate_attributes(
                    item_info['attributes'],
                    level,
                    rarity_multipliers[rarity]
                ),
                'slot': random.choice(item_info['slots']),
                'value': self._calculate_value(
                    level,
                    rarity_multipliers[rarity]
                ),
                'requirements': self._generate_requirements(
                    level,
                    rarity_multipliers[rarity]
                )
            }
            
            logger.debug(f"Generated item: {item}")
            return item
            
        except Exception as e:
            self._log_error('item generation', e)
            return {}
    
    def generate_loot(
        self,
        level: int,
        difficulty: str = 'normal',
        quantity: int = 1
    ) -> List[Dict[str, Any]]:
        """Generate loot from a defeated enemy or container"""
        try:
            # Difficulty multipliers
            difficulty_multipliers = {
                'easy': 0.8,
                'normal': 1.0,
                'hard': 1.5,
                'epic': 2.0
            }
            
            multiplier = difficulty_multipliers.get(difficulty, 1.0)
            
            # Item type weights
            item_weights = {
                'weapon': 0.3,
                'armor': 0.3,
                'accessory': 0.2,
                'consumable': 0.2
            }
            
            # Rarity weights
            rarity_weights = {
                'common': 0.6,
                'uncommon': 0.25,
                'rare': 0.1,
                'epic': 0.04,
                'legendary': 0.01
            }
            
            loot = []
            
            for _ in range(quantity):
                # Determine item type
                item_type = random.choices(
                    list(item_weights.keys()),
                    weights=list(item_weights.values())
                )[0]
                
                # Determine rarity
                rarity = random.choices(
                    list(rarity_weights.keys()),
                    weights=list(rarity_weights.values())
                )[0]
                
                # Generate item
                item = self.generate_item(
                    level,
                    item_type,
                    rarity
                )
                
                # Adjust based on difficulty
                for attr in item['attributes']:
                    item['attributes'][attr] = int(
                        item['attributes'][attr] * multiplier
                    )
                
                loot.append(item)
            
            logger.debug(f"Generated loot: {loot}")
            return loot
            
        except Exception as e:
            self._log_error('loot generation', e)
            return []
    
    def _generate_attributes(
        self,
        attribute_types: List[str],
        level: int,
        rarity_multiplier: float
    ) -> Dict[str, int]:
        """Generate item attributes"""
        try:
            attributes = {}
            
            for attr in attribute_types:
                base_value = random.randint(1, 5) * level
                value = int(base_value * rarity_multiplier)
                attributes[attr] = value
            
            return attributes
            
        except Exception as e:
            self._log_error('attribute generation', e)
            return {}
    
    def _generate_requirements(
        self,
        level: int,
        rarity_multiplier: float
    ) -> Dict[str, Any]:
        """Generate item requirements"""
        try:
            requirements = {
                'level': max(1, int(level * rarity_multiplier)),
                'strength': random.randint(1, 5),
                'dexterity': random.randint(1, 5),
                'intelligence': random.randint(1, 5)
            }
            
            return requirements
            
        except Exception as e:
            self._log_error('requirements generation', e)
            return {}
    
    def _calculate_value(
        self,
        level: int,
        rarity_multiplier: float
    ) -> int:
        """Calculate item value"""
        try:
            base_value = 10 * level
            value = int(base_value * rarity_multiplier)
            return value
            
        except Exception as e:
            self._log_error('value calculation', e)
            return 0
    
    def _generate_name(
        self,
        prefixes: Dict[str, List[str]],
        subtype: str,
        rarity: str
    ) -> str:
        """Generate item name"""
        try:
            prefix = random.choice(prefixes.get(rarity, prefixes['common']))
            return f"{prefix} {subtype}"
            
        except Exception as e:
            self._log_error('name generation', e)
            return "Unknown Item"
    
    def _generate_description(
        self,
        item_type: str,
        subtype: str,
        rarity: str
    ) -> str:
        """Generate item description"""
        try:
            descriptions = {
                'weapon': f"A {rarity} {subtype} of considerable power.",
                'armor': f"A {rarity} piece of {subtype} offering protection.",
                'accessory': f"A {rarity} {subtype} with magical properties.",
                'consumable': f"A {rarity} {subtype} with potent effects."
            }
            
            return descriptions.get(item_type, "An unknown item.")
            
        except Exception as e:
            self._log_error('description generation', e)
            return "An unknown item." 