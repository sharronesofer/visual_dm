from typing import Any, Dict, List, Union



/** Basic attributes interface */
class Attributes:
    strength: float
    dexterity: float
    constitution: float
    intelligence: float
    wisdom: float
    charisma: float
/** Skill interface */
class Skill:
    name: str
    ability: keyof Attributes
    proficient: bool
    expertise: bool
    value: float
/** Equipment interface */
class Equipment:
    name: str
    type: Union['weapon', 'armor', 'gear', 'tool']
    quantity: float
    description: str
    properties?: List[str]
    cost?: {
    amount: float
    unit: Union['cp', 'sp', 'ep', 'gp', 'pp']
  damage?: float | string
  armorClass?: float
}
/** Starter kit interface */
class StarterKit:
    id: str
    name: str
    description: str
    equipment: List[Equipment]
    items: List[Equipment]
    gold: float
    requirements?: List[{
    class?: str]
    background?: List[str]
}
/** Race interface */
RaceType = Union['Human', 'Elf', 'Dwarf', 'Halfling', 'Gnome', 'Half-Elf', 'Half-Orc']
/** Background interface */
BackgroundType = Union['Acolyte', 'Criminal', 'Folk Hero', 'Noble', 'Sage', 'Soldier']
/** Feat interface */
class Feat:
    name: str
    description: str
    prerequisites?: {
    ability?: Partial<Attributes>
    race?: List[str]
    class?: List[str]
    level?: float
  benefits: List[string]
}
/** Class feature interface */
class ClassFeature:
    name: str
    level: float
    description: str
/** Class proficiency interface */
class ClassProficiency:
    armor: List[str]
    weapons: List[str]
    tools: List[str]
    savingThrows: List[keyof Attributes>
    skills: List[str]
/** Spellcasting info interface */
class SpellcastingInfo:
    ability: keyof Attributes
    spellsKnown?: float
    cantripsKnown?: float
    spellSlots: Dict[float, float>
    ritual: bool
/** Class interface */
class Class:
    name: ClassType
    description: str
    hitDie: float
    primaryAbility: keyof Attributes
    savingThrows: List[keyof Attributes>
    proficiencies: List[{
    armor: str]
    weapons: List[str]
    tools: List[str]
    skills: List[str]
  features: List[ClassFeature]
  spellcasting?: {
    ability: keyof Attributes
    level: float
  }
}
/** Derived stats interface */
class DerivedStats:
    hitPoints: float
    armorClass: float
    initiative: float
    speed: float
    proficiencyBonus: float
    passivePerception: float
    spellSaveDC?: float
    spellAttackBonus?: float
/** Character data interface */
class CharacterData:
    id: str
    name: str
    race: \'Race\'
    class: \'Class\'
    background: \'Background\'
    level: float
    experience: float
    attributes: \'Attributes\'
    skills: List[Skill]
    features: List[ClassFeature]
    equipment: List[Equipment]
    spells?: List[{
    cantrips: str]
    prepared: List[str]
    known: List[str]
  proficiencies: List[string]
  languages: List[string]
  description: str
  personality: \'Personality\'
  alignment:
    | 'Lawful Good'
    | 'Neutral Good'
    | 'Chaotic Good'
    | 'Lawful Neutral'
    | 'True Neutral'
    | 'Chaotic Neutral'
    | 'Lawful Evil'
    | 'Neutral Evil'
    | 'Chaotic Evil'
  feats: List[string]
  derivedStats: Dict[str, Any]
  appearance: Dict[str, Any]
  backstory: str
  skillPoints: float
}
/** Validation state interface */
class ValidationState:
    isValid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
/**
 * Represents a skill in the character creation system
 */
class ISkill:
    /** Unique identifier for the skill */
  readonly id: str
    /** Display name of the skill */
  readonly name: str
    /** Detailed description of what the skill represents */
  readonly description: str
    /** Number of points allocated to this skill by the user */
  points: float
    /** Modifier applied to this skill from backgrounds */
  modifier: float
    /** Maximum number of points that can be allocated to this skill */
  readonly maxPoints: float
    /** Category or group this skill belongs to (e.g., "Combat", "Social") */
  readonly category: str
/**
 * Represents a character background that provides skill modifiers
 */
class IBackground:
    /** Unique identifier for the background */
  readonly id: str
    /** Display name of the background */
  readonly name: str
    /** Detailed description of the background's story and implications */
  readonly description: str
    /** Mapping of skill IDs to their modifier values for this background */
  readonly skillModifiers: Dict[str, float>
    /** Optional flavor text or additional background story */
  readonly flavorText?: str
/**
 * Represents the complete state of a character during creation
 */
class ICharacter:
    /** Unique identifier for the character */
  readonly id: str
    /** Character's name */
  name: str
    /** Selected background IDs */
  selectedBackgrounds: List[str]
    /** Maximum number of backgrounds that can be selected */
  readonly maxBackgrounds: float
    /** Mapping of skill IDs to their allocated points */
  skills: Dict[str, float>
    /** Total number of skill points available to allocate */
  readonly totalSkillPoints: float
    /** Optional character description or backstory */
  description?: str
/**
 * Represents the calculated final values for a character's skills
 */
class ICalculatedSkills:
    /** Mapping of skill IDs to their final calculated values (base + modifiers) */
  readonly finalValues: Dict[str, float>
    /** Mapping of skill IDs to their total modifiers from all sources */
  readonly totalModifiers: Dict[str, float>
    /** Number of unallocated skill points remaining */
  readonly remainingPoints: float
/**
 * Represents validation errors during character creation
 */
class IValidationError:
    /** Type of validation error */
  readonly type: Union['SKILL_POINTS', 'BACKGROUND_LIMIT', 'INVALID_SKILL', 'INVALID_BACKGROUND']
    /** Human-readable error message */
  readonly message: str
    /** Additional error details (e.g., specific skill or background ID) */
  readonly details?: Dict[str, Any>
/**
 * Type guard to check if a skill is valid
 */
function isValidSkill(skill: Any): skill is ISkill {
  return (
    typeof skill === 'object' &&
    typeof skill.id === 'string' &&
    typeof skill.name === 'string' &&
    typeof skill.description === 'string' &&
    typeof skill.points === 'number' &&
    typeof skill.modifier === 'number' &&
    typeof skill.maxPoints === 'number' &&
    typeof skill.category === 'string'
  )
}
/**
 * Type guard to check if a background is valid
 */
function isValidBackground(background: Any): background is IBackground {
  return (
    typeof background === 'object' &&
    typeof background.id === 'string' &&
    typeof background.name === 'string' &&
    typeof background.description === 'string' &&
    typeof background.skillModifiers === 'object' &&
    Object.entries(background.skillModifiers).every(
      ([key, value]) => typeof key === 'string' && typeof value === 'number'
    )
  )
}
class Personality:
    traits: List[str]
    ideals: List[str]
    bonds: List[str]
    flaws: List[str]
class Background:
    name: BackgroundType
    description: str
    skillProficiencies: List[str]
    toolProficiencies: List[str]
    languages: List[str]
    equipment: List[Equipment]
    feature: Dict[str, Any]
}
class Race:
    name: RaceType
    description: str
    abilityScoreIncrease: Partial[Attributes]
    speed: float
    size: Union['Small', 'Medium']
    languages: List[str]
    traits: List[{
    name: str
    description: str>
  subraces?: Race[]
}
ClassType = Union[, 'Fighter', 'Wizard', 'Cleric', 'Rogue', 'Ranger', 'Paladin', 'Barbarian', 'Bard', 'Druid', 'Monk', 'Sorcerer', 'Warlock']
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
    description?: str
    level: float
    type: Union['active', 'passive']
    cost?: float
    cooldown?: float
    properties?: Dict[str, Any>
class CharacterInventoryItem:
    id: str
    name: str
    description?: str
    type: str
    quantity: float
    properties?: Dict[str, Any>
class Character:
    id: str
    name: str
    level: float
    experience: float
    stats: \'CharacterStats\'
    skills: List[CharacterSkill]
    inventory: List[CharacterInventoryItem]
    gold: float
    createdAt: str
    updatedAt: str
class CharacterCreateDTO:
    name: str
    stats: \'CharacterStats\'
    skills?: List[CharacterSkill]
    inventory?: List[CharacterInventoryItem]
    gold?: float
CharacterUpdateDTO = Partial[CharacterCreateDTO]
class GameCharacterState:
    health: float
    maxHealth: float
    stamina: float
    maxStamina: float
    mana: float
    maxMana: float
    statusEffects: List[str]
    temperature?: float
    wetness?: float
    visibility?: float
    equipment?: {
    [slot: str]: {
      id: str
    weatherResistance?: {
        cold?: float
    heat?: float
    rain?: float
    wind?: float
    }
  }
}