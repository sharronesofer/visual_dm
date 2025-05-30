from typing import Any, Dict, List, Union
from enum import Enum


class CharacterStats:
    strength: float
    dexterity: float
    constitution: float
    intelligence: float
    wisdom: float
    charisma: float
class CharacterSkill:
    id: str
    name: str
    description: str
    level: float
    maxLevel: float
    prerequisites: List[str]
    effects: List[SkillEffect]
    icon: str
class SkillEffect:
    type: str
    value: float
    duration?: float
    target: Union['self', 'ally', 'enemy', 'area']
class SkillTreeNode:
    skill: \'CharacterSkill\'
    position: Dict[str, Any]
class InventoryItem:
    id: str
    name: str
    description: str
    type: \'ItemType\'
    rarity: \'ItemRarity\'
    stats: Partial[CharacterStats]
    effects: List[ItemEffect]
    icon: str
    stackable: bool
    quantity: float
class ItemType(Enum):
    WEAPON = 'weapon'
    ARMOR = 'armor'
    ACCESSORY = 'accessory'
    CONSUMABLE = 'consumable'
    MATERIAL = 'material'
    QUEST = 'quest'
class ItemRarity(Enum):
    COMMON = 'common'
    UNCOMMON = 'uncommon'
    RARE = 'rare'
    EPIC = 'epic'
    LEGENDARY = 'legendary'
class ItemEffect:
    type: str
    value: float
    duration?: float
    trigger?: Union['onUse', 'onEquip', 'onHit', 'onDamaged']
class Equipment:
    weapon: Union[InventoryItem, None]
    armor: Union[InventoryItem, None]
    accessory1: Union[InventoryItem, None]
    accessory2: Union[InventoryItem, None]
class CharacterTrait:
    id: str
    name: str
    description: str
    effects: List[TraitEffect]
    icon: str
class TraitEffect:
    type: str
    value: float
    condition?: str
class CharacterProgression:
    level: float
    experience: float
    experienceToNextLevel: float
    skillPoints: float
    attributePoints: float
class Character:
    id: str
    name: str
    class: str
    race: str
    level: float
    stats: \'CharacterStats\'
    skills: List[CharacterSkill]
    inventory: List[InventoryItem]
    equipment: \'Equipment\'
    traits: List[CharacterTrait]
    progression: \'CharacterProgression\'
class StatModifier:
    source: str
    value: float
    type: Union['base', 'equipment', 'skill', 'trait', 'temporary']
class CalculatedStats:
    modifiers: List[{
    [K in keyof CharacterStats]: StatModifier]
}
class CharacterUIState:
    selectedCharacter: Union[Character, None]
    selectedInventoryItem: Union[InventoryItem, None]
    selectedSkill: Union[CharacterSkill, None]
    comparisonItem: Union[InventoryItem, None]
    inventoryFilter: Union[ItemType, None]
    inventorySort: Union['name', 'type', 'rarity']
    showTooltip: bool
    tooltipPosition: Dict[str, Any]
class CharacterUIOptions:
    showComparison: bool
    showStatChanges: bool
    showSkillTree: bool
    showInventory: bool
    showEquipment: bool
    showTraits: bool
    showProgression: bool
CharacterEventListener = (event: CharacterUIEvent) => None
class CharacterUIEvent:
    type: Union['select', 'equip', 'unequip', 'useItem', 'learnSkill', 'levelUp']
    character: \'Character\'
    data?: Any 