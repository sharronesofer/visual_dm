export interface CombatState {
  accuracy: number;
  damage: number;
  defense: number;
  criticalChance: number;
  // Add any other combat-related stats that can be affected by weather
  evasion?: number;
  initiative?: number;
  resistances?: {
    fire?: number;
    ice?: number;
    lightning?: number;
    wind?: number;
  };
} 