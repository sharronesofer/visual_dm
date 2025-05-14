export type POIType = 'shop' | 'temple' | 'ruin' | 'camp' | 'outpost';

export interface POITemplate {
  id: string;
  type: POIType;
  baseDescription: string;
  baseLoot: string[];
  baseNPCs: string[];
}

export interface POIModifier {
  id: string;
  description: string;
  lootModifier?: (loot: string[]) => string[];
  npcModifier?: (npcs: string[]) => string[];
  questHook?: string;
}

export interface POIContent {
  template: POITemplate;
  modifiers: POIModifier[];
  loot: string[];
  npcs: string[];
  tags: string[];
}

export interface POIState {
  poiId: string;
  visited: boolean;
  discoveredLoot: string[];
  interactedNPCs: string[];
  questState: Record<string, any>;
} 