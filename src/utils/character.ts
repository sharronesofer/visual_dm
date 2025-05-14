import { Attributes, Skill, DerivedStats, CharacterData, Class } from '../types/character';
import { ValidationResult, ValidationError } from '../types/common';

/**
 * Calculate ability modifier from an ability score
 */
export function calculateAbilityModifier(score: number): number {
  return Math.floor((score - 10) / 2);
}

/**
 * Calculate proficiency bonus based on character level
 */
export function calculateProficiencyBonus(level: number): number {
  return Math.floor((level - 1) / 4) + 2;
}

/**
 * Calculate skill modifier
 */
export function calculateSkillModifier(
  skill: Skill,
  attributes: Attributes,
  proficiencyBonus: number
): number {
  const abilityModifier = calculateAbilityModifier(attributes[skill.ability]);
  return abilityModifier + (skill.isProficient ? proficiencyBonus : 0) + (skill.bonus || 0);
}

/**
 * Calculate derived stats
 */
export function calculateDerivedStats(
  attributes: Attributes,
  characterClass: Class,
  level: number
): DerivedStats {
  const proficiencyBonus = calculateProficiencyBonus(level);
  const constitutionModifier = calculateAbilityModifier(attributes.constitution);
  const dexterityModifier = calculateAbilityModifier(attributes.dexterity);

  // Calculate hit points
  const hitPoints =
    characterClass.hitDie +
    constitutionModifier + // First level
    (level - 1) * (Math.floor(characterClass.hitDie / 2) + 1 + constitutionModifier); // Additional levels

  // Calculate armor class (basic unarmored)
  const armorClass = 10 + dexterityModifier;

  // Calculate initiative
  const initiative = dexterityModifier;

  // Calculate passive perception (assuming Wisdom (Perception))
  const wisdomModifier = calculateAbilityModifier(attributes.wisdom);
  const passivePerception = 10 + wisdomModifier;

  // Calculate spell-related stats if the class has spellcasting
  let spellSaveDC: number | undefined;
  let spellAttackBonus: number | undefined;

  if (characterClass.spellcasting) {
    const spellcastingModifier = calculateAbilityModifier(
      attributes[characterClass.spellcasting.ability]
    );
    spellSaveDC = 8 + proficiencyBonus + spellcastingModifier;
    spellAttackBonus = proficiencyBonus + spellcastingModifier;
  }

  return {
    hitPoints,
    armorClass,
    initiative,
    speed: 30, // Default speed, should be modified by race and other effects
    proficiencyBonus,
    passivePerception,
    spellSaveDC,
    spellAttackBonus,
  };
}

/**
 * Validate character attributes
 */
export function validateAttributes(attributes: Attributes): ValidationResult {
  const errors: ValidationError[] = [];
  const minScore = 3;
  const maxScore = 20;

  for (const [ability, score] of Object.entries(attributes)) {
    if (score < minScore || score > maxScore) {
      errors.push({
        field: ability,
        message: `${ability} must be between ${minScore} and ${maxScore}`,
        type: 'error',
      });
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Calculate total attribute points used (for point buy system)
 */
export function calculateAttributePoints(attributes: Attributes): number {
  const pointCosts: Record<number, number> = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9,
  };

  return Object.values(attributes).reduce((total, score) => {
    return total + (pointCosts[score] || 0);
  }, 0);
}

/**
 * Check if a character meets class prerequisites
 */
export function meetsClassPrerequisites(
  attributes: Attributes,
  characterClass: Class
): ValidationResult {
  const errors: ValidationError[] = [];

  // Example prerequisites check (modify based on your game rules)
  if (characterClass.name === 'Wizard' && attributes.intelligence < 13) {
    errors.push({
      field: 'intelligence',
      message: 'Wizards require at least 13 Intelligence',
      type: 'error',
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Calculate experience points needed for next level
 */
export function getExperienceForLevel(level: number): number {
  const experienceThresholds = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000, 140000,
    165000, 195000, 225000, 265000, 305000, 355000,
  ];
  return experienceThresholds[level - 1] || 0;
}

/**
 * Get available skill proficiencies for a class
 */
export function getAvailableSkillProficiencies(characterClass: Class): string[] {
  return characterClass.proficiencies.skills;
}

/**
 * Check if a character can use a particular type of equipment
 */
export function canUseEquipment(
  characterClass: Class,
  equipmentType: string,
  equipmentName: string
): boolean {
  const { proficiencies } = characterClass;

  switch (equipmentType) {
    case 'armor':
      return proficiencies.armor.some(type =>
        equipmentName.toLowerCase().includes(type.toLowerCase())
      );
    case 'weapon':
      return proficiencies.weapons.some(type =>
        equipmentName.toLowerCase().includes(type.toLowerCase())
      );
    case 'tool':
      return proficiencies.tools.some(type =>
        equipmentName.toLowerCase().includes(type.toLowerCase())
      );
    default:
      return true; // Non-restricted equipment types
  }
}

/**
 * Generate a character summary
 */
export function generateCharacterSummary(character: CharacterData): string {
  return `
${character.name}
Level ${character.level} ${character.race.name} ${character.class.name}
HP: ${character.derivedStats.hitPoints}
AC: ${character.derivedStats.armorClass}
Attributes:
  STR: ${character.attributes.strength} (${calculateAbilityModifier(character.attributes.strength)})
  DEX: ${character.attributes.dexterity} (${calculateAbilityModifier(character.attributes.dexterity)})
  CON: ${character.attributes.constitution} (${calculateAbilityModifier(character.attributes.constitution)})
  INT: ${character.attributes.intelligence} (${calculateAbilityModifier(character.attributes.intelligence)})
  WIS: ${character.attributes.wisdom} (${calculateAbilityModifier(character.attributes.wisdom)})
  CHA: ${character.attributes.charisma} (${calculateAbilityModifier(character.attributes.charisma)})
`.trim();
}
