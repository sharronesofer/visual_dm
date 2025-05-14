/**
 * Base item types and interfaces for the loot system
 */

export enum ItemType {
  WEAPON = 'WEAPON',
  ARMOR = 'ARMOR',
  POTION = 'POTION',
  SCROLL = 'SCROLL',
  MATERIAL = 'MATERIAL',
  TREASURE = 'TREASURE',
  KEY = 'KEY',
  QUEST = 'QUEST',
  MISC = 'MISC'
}

export enum ItemRarity {
  COMMON = 'COMMON',
  UNCOMMON = 'UNCOMMON',
  RARE = 'RARE',
  EPIC = 'EPIC',
  LEGENDARY = 'LEGENDARY'
}

export interface BaseStats {
  damage?: number;
  armor?: number;
  healing?: number;
  duration?: number;
  charges?: number;
  [key: string]: number | undefined;
}

export interface BaseItem {
  id: string;
  name: string;
  description: string;
  type: ItemType;
  weight: number;
  value: number;
  baseStats: BaseStats;
  createdAt: Date;
  updatedAt: Date;
}

export interface RarityTier {
  id: number;
  name: ItemRarity;
  probability: number;
  valueMultiplier: number;
  colorHex: string;
}

export interface ItemWithRarity extends BaseItem {
  rarity: RarityTier;
} 