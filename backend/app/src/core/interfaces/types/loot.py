from typing import Any, Union
from enum import Enum


/**
 * Base item types and interfaces for the loot system
 */
class ItemType(Enum):
    WEAPON = 'WEAPON'
    ARMOR = 'ARMOR'
    POTION = 'POTION'
    SCROLL = 'SCROLL'
    MATERIAL = 'MATERIAL'
    TREASURE = 'TREASURE'
    KEY = 'KEY'
    QUEST = 'QUEST'
    MISC = 'MISC'
class ItemRarity(Enum):
    COMMON = 'COMMON'
    UNCOMMON = 'UNCOMMON'
    RARE = 'RARE'
    EPIC = 'EPIC'
    LEGENDARY = 'LEGENDARY'
class BaseStats:
    damage?: float
    armor?: float
    healing?: float
    duration?: float
    charges?: float
    [key: Union[str]: float, None]
class BaseItem:
    id: str
    name: str
    description: str
    type: \'ItemType\'
    weight: float
    value: float
    baseStats: \'BaseStats\'
    createdAt: Date
    updatedAt: Date
class RarityTier:
    id: float
    name: \'ItemRarity\'
    probability: float
    valueMultiplier: float
    colorHex: str
class ItemWithRarity:
    rarity: \'RarityTier\' 