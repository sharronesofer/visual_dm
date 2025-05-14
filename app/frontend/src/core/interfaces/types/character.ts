import { ValidationError } from './common';

/** Basic attributes interface */
export interface Attributes {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
}

/** Skill interface */
export interface Skill {
  name: string;
  ability: keyof Attributes;
  proficient: boolean;
  expertise: boolean;
  value: number;
}

/** Equipment interface */
export interface Equipment {
  name: string;
  type: 'weapon' | 'armor' | 'gear' | 'tool';
  quantity: number;
  description: string;
  properties?: string[];
  cost?: {
    amount: number;
    unit: 'cp' | 'sp' | 'ep' | 'gp' | 'pp';
  };
  damage?: number | string;
  armorClass?: number;
}

/** Starter kit interface */
export interface StarterKit {
  id: string;
  name: string;
  description: string;
  equipment: Equipment[];
  items: Equipment[];
  gold: number;
  requirements?: {
    class?: string[];
    background?: string[];
  };
}

/** Race interface */
export type RaceType = 'Human' | 'Elf' | 'Dwarf' | 'Halfling' | 'Gnome' | 'Half-Elf' | 'Half-Orc';

/** Background interface */
export type BackgroundType = 'Acolyte' | 'Criminal' | 'Folk Hero' | 'Noble' | 'Sage' | 'Soldier';

/** Feat interface */
export interface Feat {
  name: string;
  description: string;
  prerequisites?: {
    ability?: Partial<Attributes>;
    race?: string[];
    class?: string[];
    level?: number;
  };
  benefits: string[];
}

/** Class feature interface */
export interface ClassFeature {
  name: string;
  level: number;
  description: string;
}

/** Class proficiency interface */
export interface ClassProficiency {
  armor: string[];
  weapons: string[];
  tools: string[];
  savingThrows: Array<keyof Attributes>;
  skills: string[];
}

/** Spellcasting info interface */
export interface SpellcastingInfo {
  ability: keyof Attributes;
  spellsKnown?: number;
  cantripsKnown?: number;
  spellSlots: Record<number, number>;
  ritual: boolean;
}

/** Class interface */
export interface Class {
  name: ClassType;
  description: string;
  hitDie: number;
  primaryAbility: keyof Attributes;
  savingThrows: Array<keyof Attributes>;
  proficiencies: {
    armor: string[];
    weapons: string[];
    tools: string[];
    skills: string[];
  };
  features: ClassFeature[];
  spellcasting?: {
    ability: keyof Attributes;
    level: number;
  };
}

/** Derived stats interface */
export interface DerivedStats {
  hitPoints: number;
  armorClass: number;
  initiative: number;
  speed: number;
  proficiencyBonus: number;
  passivePerception: number;
  spellSaveDC?: number;
  spellAttackBonus?: number;
}

/** Character data interface */
export interface CharacterData {
  id: string;
  name: string;
  race: Race;
  class: Class;
  background: Background;
  level: number;
  experience: number;
  attributes: Attributes;
  skills: Skill[];
  features: ClassFeature[];
  equipment: Equipment[];
  spells?: {
    cantrips: string[];
    prepared: string[];
    known: string[];
  };
  proficiencies: string[];
  languages: string[];
  description: string;
  personality: Personality;
  alignment:
    | 'Lawful Good'
    | 'Neutral Good'
    | 'Chaotic Good'
    | 'Lawful Neutral'
    | 'True Neutral'
    | 'Chaotic Neutral'
    | 'Lawful Evil'
    | 'Neutral Evil'
    | 'Chaotic Evil';
  feats: string[];
  derivedStats: {
    hitPoints: number;
    armorClass: number;
    initiative: number;
    speed: number;
    proficiencyBonus: number;
    savingThrows: Record<keyof Attributes, number>;
  };
  appearance: {
    height: string;
    weight: string;
    age: number;
    eyes: string;
    skin: string;
    hair: string;
  };
  backstory: string;
  skillPoints: number;
}

/** Validation state interface */
export interface ValidationState {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

/**
 * Represents a skill in the character creation system
 */
export interface ISkill {
  /** Unique identifier for the skill */
  readonly id: string;
  /** Display name of the skill */
  readonly name: string;
  /** Detailed description of what the skill represents */
  readonly description: string;
  /** Number of points allocated to this skill by the user */
  points: number;
  /** Modifier applied to this skill from backgrounds */
  modifier: number;
  /** Maximum number of points that can be allocated to this skill */
  readonly maxPoints: number;
  /** Category or group this skill belongs to (e.g., "Combat", "Social") */
  readonly category: string;
}

/**
 * Represents a character background that provides skill modifiers
 */
export interface IBackground {
  /** Unique identifier for the background */
  readonly id: string;
  /** Display name of the background */
  readonly name: string;
  /** Detailed description of the background's story and implications */
  readonly description: string;
  /** Mapping of skill IDs to their modifier values for this background */
  readonly skillModifiers: Record<string, number>;
  /** Optional flavor text or additional background story */
  readonly flavorText?: string;
}

/**
 * Represents the complete state of a character during creation
 */
export interface ICharacter {
  /** Unique identifier for the character */
  readonly id: string;
  /** Character's name */
  name: string;
  /** Selected background IDs */
  selectedBackgrounds: string[];
  /** Maximum number of backgrounds that can be selected */
  readonly maxBackgrounds: number;
  /** Mapping of skill IDs to their allocated points */
  skills: Record<string, number>;
  /** Total number of skill points available to allocate */
  readonly totalSkillPoints: number;
  /** Optional character description or backstory */
  description?: string;
}

/**
 * Represents the calculated final values for a character's skills
 */
export interface ICalculatedSkills {
  /** Mapping of skill IDs to their final calculated values (base + modifiers) */
  readonly finalValues: Record<string, number>;
  /** Mapping of skill IDs to their total modifiers from all sources */
  readonly totalModifiers: Record<string, number>;
  /** Number of unallocated skill points remaining */
  readonly remainingPoints: number;
}

/**
 * Represents validation errors during character creation
 */
export interface IValidationError {
  /** Type of validation error */
  readonly type: 'SKILL_POINTS' | 'BACKGROUND_LIMIT' | 'INVALID_SKILL' | 'INVALID_BACKGROUND';
  /** Human-readable error message */
  readonly message: string;
  /** Additional error details (e.g., specific skill or background ID) */
  readonly details?: Record<string, any>;
}

/**
 * Type guard to check if a skill is valid
 */
export function isValidSkill(skill: any): skill is ISkill {
  return (
    typeof skill === 'object' &&
    typeof skill.id === 'string' &&
    typeof skill.name === 'string' &&
    typeof skill.description === 'string' &&
    typeof skill.points === 'number' &&
    typeof skill.modifier === 'number' &&
    typeof skill.maxPoints === 'number' &&
    typeof skill.category === 'string'
  );
}

/**
 * Type guard to check if a background is valid
 */
export function isValidBackground(background: any): background is IBackground {
  return (
    typeof background === 'object' &&
    typeof background.id === 'string' &&
    typeof background.name === 'string' &&
    typeof background.description === 'string' &&
    typeof background.skillModifiers === 'object' &&
    Object.entries(background.skillModifiers).every(
      ([key, value]) => typeof key === 'string' && typeof value === 'number'
    )
  );
}

export interface Personality {
  traits: string[];
  ideals: string[];
  bonds: string[];
  flaws: string[];
}

export interface Background {
  name: BackgroundType;
  description: string;
  skillProficiencies: string[];
  toolProficiencies: string[];
  languages: string[];
  equipment: Equipment[];
  feature: {
    name: string;
    description: string;
  };
  suggestedCharacteristics: {
    personalityTraits: string[];
    ideals: string[];
    bonds: string[];
    flaws: string[];
  };
}

export interface Race {
  name: RaceType;
  description: string;
  abilityScoreIncrease: Partial<Attributes>;
  speed: number;
  size: 'Small' | 'Medium';
  languages: string[];
  traits: Array<{
    name: string;
    description: string;
  }>;
  subraces?: Race[];
}

export type ClassType =
  | 'Fighter'
  | 'Wizard'
  | 'Cleric'
  | 'Rogue'
  | 'Ranger'
  | 'Paladin'
  | 'Barbarian'
  | 'Bard'
  | 'Druid'
  | 'Monk'
  | 'Sorcerer'
  | 'Warlock';

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
  description?: string;
  level: number;
  type: 'active' | 'passive';
  cost?: number;
  cooldown?: number;
  properties?: Record<string, any>;
}

export interface CharacterInventoryItem {
  id: string;
  name: string;
  description?: string;
  type: string;
  quantity: number;
  properties?: Record<string, any>;
}

export interface Character {
  id: string;
  name: string;
  level: number;
  experience: number;
  stats: CharacterStats;
  skills: CharacterSkill[];
  inventory: CharacterInventoryItem[];
  gold: number;
  createdAt: string;
  updatedAt: string;
}

export interface CharacterCreateDTO {
  name: string;
  stats: CharacterStats;
  skills?: CharacterSkill[];
  inventory?: CharacterInventoryItem[];
  gold?: number;
}

export type CharacterUpdateDTO = Partial<CharacterCreateDTO>;

export interface GameCharacterState {
  health: number;
  maxHealth: number;
  stamina: number;
  maxStamina: number;
  mana: number;
  maxMana: number;
  // Add any other character stats that can be affected by weather
  statusEffects: string[];
  temperature?: number;
  wetness?: number;
  visibility?: number;
  equipment?: {
    [slot: string]: {
      id: string;
      weatherResistance?: {
        cold?: number;
        heat?: number;
        rain?: number;
        wind?: number;
      };
    };
  };
}
