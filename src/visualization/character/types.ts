export interface CharacterStats {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
}

export interface CharacterSkill {
  id: string;
  name: string;
  description: string;
  level: number;
  maxLevel: number;
  prerequisites: string[];
  effects: SkillEffect[];
  icon: string;
}

export interface SkillEffect {
  type: string;
  value: number;
  duration?: number;
  target: 'self' | 'ally' | 'enemy' | 'area';
}

export interface SkillTreeNode {
  skill: CharacterSkill;
  position: { x: number; y: number };
  connections: string[];
  unlocked: boolean;
}

export enum EquipmentState {
  EQUIPPED = 'equipped',
  BROKEN = 'broken',
  DISABLED = 'disabled',
  EMPOWERED = 'empowered',
  DAMAGED = 'damaged',
  REPAIRED = 'repaired',
  // Add more as needed
}

export interface InventoryItem {
  id: string;
  name: string;
  description: string;
  type: ItemType;
  rarity: ItemRarity;
  stats: Partial<CharacterStats>;
  effects: ItemEffect[];
  icon: string;
  stackable: boolean;
  quantity: number;
  state?: EquipmentState;
  durability?: number; // 0-100 or similar
  maxDurability?: number;
}

export enum ItemType {
  WEAPON = 'weapon',
  ARMOR = 'armor',
  ACCESSORY = 'accessory',
  CONSUMABLE = 'consumable',
  MATERIAL = 'material',
  QUEST = 'quest'
}

export enum ItemRarity {
  COMMON = 'common',
  UNCOMMON = 'uncommon',
  RARE = 'rare',
  EPIC = 'epic',
  LEGENDARY = 'legendary'
}

export interface ItemEffect {
  type: string;
  value: number;
  duration?: number;
  trigger?: 'onUse' | 'onEquip' | 'onHit' | 'onDamaged';
}

export interface Equipment {
  weapon: InventoryItem | null;
  armor: InventoryItem | null;
  accessory1: InventoryItem | null;
  accessory2: InventoryItem | null;
}

export interface CharacterTrait {
  id: string;
  name: string;
  description: string;
  effects: TraitEffect[];
  icon: string;
}

export interface TraitEffect {
  type: string;
  value: number;
  condition?: string;
}

export interface CharacterProgression {
  level: number;
  experience: number;
  experienceToNextLevel: number;
  skillPoints: number;
  attributePoints: number;
}

export interface Character {
  id: string;
  name: string;
  class: string;
  race: string;
  level: number;
  stats: CharacterStats;
  skills: CharacterSkill[];
  inventory: InventoryItem[];
  equipment: Equipment;
  traits: CharacterTrait[];
  progression: CharacterProgression;
}

export interface StatModifier {
  source: string;
  value: number;
  type: 'base' | 'equipment' | 'skill' | 'trait' | 'temporary';
}

export interface CalculatedStats extends CharacterStats {
  modifiers: {
    [K in keyof CharacterStats]: StatModifier[];
  };
}

export interface CharacterUIState {
  selectedCharacter: Character | null;
  selectedInventoryItem: InventoryItem | null;
  selectedSkill: CharacterSkill | null;
  comparisonItem: InventoryItem | null;
  inventoryFilter: ItemType | null;
  inventorySort: 'name' | 'type' | 'rarity';
  showTooltip: boolean;
  tooltipPosition: { x: number; y: number };
}

export interface CharacterUIOptions {
  showComparison: boolean;
  showStatChanges: boolean;
  showSkillTree: boolean;
  showInventory: boolean;
  showEquipment: boolean;
  showTraits: boolean;
  showProgression: boolean;
}

export type CharacterEventListener = (event: CharacterUIEvent) => void;

export interface CharacterUIEvent {
  type: 'select' | 'equip' | 'unequip' | 'useItem' | 'learnSkill' | 'levelUp' | 'preSwitch' | 'postSwitch' | 'equipmentStateChange';
  character: Character;
  data?: any;
} 