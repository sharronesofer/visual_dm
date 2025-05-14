/**
 * Represents a resource requirement for a quest
 */
export interface QuestResource {
  id: string;
  name: string;
  amount: number;
  type: 'ITEM' | 'CURRENCY' | 'MATERIAL';
  description?: string;
}

/**
 * Represents an environmental or state condition for a quest
 */
export interface QuestCondition {
  type: 'WEATHER' | 'TIME' | 'SEASON' | 'FACTION_STATE' | 'WORLD_STATE';
  value: string | number | boolean;
  description?: string;
  customData?: Record<string, any>;
} 