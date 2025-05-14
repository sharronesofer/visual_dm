import { ApiService, ApiResponse } from './ApiService';
import { CharacterData, Attributes, Equipment, Skill } from '../types/character';

export interface CharacterSubmissionData {
  id?: string;
  name: string;
  race: string;
  class: string;
  background: string;
  level: number;
  attributes: Attributes;
  skills: {
    proficiencies: string[];
    expertise: string[];
  };
  equipment: {
    items: Equipment[];
    gold: number;
  };
  features: {
    racial: string[];
    class: string[];
    background: string[];
    feats: string[];
  };
  spellcasting?: {
    ability: string;
    spellsKnown: string[];
    cantripsKnown: string[];
    spellSlots: Record<string, number>;
  };
  personality: {
    traits: string[];
    ideals: string[];
    bonds: string[];
    flaws: string[];
  };
  metadata: {
    version: string;
    createdAt: string;
    lastModified: string;
  };
}

export interface ValidationResult {
  isValid: boolean;
  errors: {
    field: string;
    message: string;
    severity: 'error' | 'warning';
  }[];
}

class CharacterSubmissionService {
  private static instance: CharacterSubmissionService;
  private apiService: ApiService;

  private constructor() {
    this.apiService = ApiService.getInstance();
  }

  public static getInstance(): CharacterSubmissionService {
    if (!CharacterSubmissionService.instance) {
      CharacterSubmissionService.instance = new CharacterSubmissionService();
    }
    return CharacterSubmissionService.instance;
  }

  private formatCharacterData(character: CharacterData): CharacterSubmissionData {
    const now = new Date().toISOString();

    return {
      id: character.id,
      name: character.name,
      race: character.race,
      class: character.class,
      background: character.background,
      level: character.level,
      attributes: character.attributes,
      skills: {
        proficiencies: character.skills
          .filter(skill => skill.isProficient)
          .map(skill => skill.name),
        expertise: character.skills.filter(skill => skill.hasExpertise).map(skill => skill.name),
      },
      equipment: {
        items: character.equipment,
        gold: character.gold,
      },
      features: {
        racial: character.racialFeatures || [],
        class: character.classFeatures || [],
        background: character.backgroundFeatures || [],
        feats: character.selectedFeats,
      },
      spellcasting: character.spellcasting
        ? {
            ability: character.spellcasting.ability,
            spellsKnown: character.spellcasting.spellsKnown,
            cantripsKnown: character.spellcasting.cantripsKnown,
            spellSlots: character.spellcasting.spellSlots,
          }
        : undefined,
      personality: {
        traits: character.personalityTraits || [],
        ideals: character.ideals || [],
        bonds: character.bonds || [],
        flaws: character.flaws || [],
      },
      metadata: {
        version: '1.0',
        createdAt: character.createdAt || now,
        lastModified: now,
      },
    };
  }

  private validateCharacterData(character: CharacterData): ValidationResult {
    const errors: ValidationResult['errors'] = [];

    // Required fields
    const requiredFields: Array<keyof CharacterData> = [
      'name',
      'race',
      'class',
      'background',
      'level',
      'attributes',
    ];
    requiredFields.forEach(field => {
      if (!character[field]) {
        errors.push({
          field,
          message: `${field} is required`,
          severity: 'error',
        });
      }
    });

    // Attribute validation
    const attributes = character.attributes;
    Object.entries(attributes).forEach(([attr, value]) => {
      if (value < 3 || value > 20) {
        errors.push({
          field: `attributes.${attr}`,
          message: `${attr} must be between 3 and 20`,
          severity: 'error',
        });
      }
    });

    // Skills validation
    const skillCount = character.skills.filter(skill => skill.isProficient).length;
    const expectedSkillCount = this.getExpectedSkillCount(character.class, character.background);
    if (skillCount !== expectedSkillCount) {
      errors.push({
        field: 'skills',
        message: `Character should have exactly ${expectedSkillCount} skill proficiencies`,
        severity: 'error',
      });
    }

    // Equipment validation
    if (!character.equipment || character.equipment.length === 0) {
      errors.push({
        field: 'equipment',
        message: 'Character must have some equipment',
        severity: 'warning',
      });
    }

    // Spellcasting validation for spellcasting classes
    if (this.isSpellcaster(character.class) && !character.spellcasting) {
      errors.push({
        field: 'spellcasting',
        message: 'Spellcasting configuration required for spellcasting class',
        severity: 'error',
      });
    }

    return {
      isValid: errors.filter(e => e.severity === 'error').length === 0,
      errors,
    };
  }

  private getExpectedSkillCount(characterClass: string, background: string): number {
    // This would be replaced with actual logic based on class and background
    const classSkillCount =
      {
        Barbarian: 2,
        Bard: 3,
        Cleric: 2,
        Druid: 2,
        Fighter: 2,
        Monk: 2,
        Paladin: 2,
        Ranger: 3,
        Rogue: 4,
        Sorcerer: 2,
        Warlock: 2,
        Wizard: 2,
      }[characterClass] || 2;

    const backgroundSkillCount = 2; // Most backgrounds grant 2 skills

    return classSkillCount + backgroundSkillCount;
  }

  private isSpellcaster(characterClass: string): boolean {
    return ['Bard', 'Cleric', 'Druid', 'Sorcerer', 'Warlock', 'Wizard'].includes(characterClass);
  }

  public async submitCharacter(character: CharacterData): Promise<ApiResponse<{ id: string }>> {
    // First validate the character data
    const validationResult = this.validateCharacterData(character);
    if (!validationResult.isValid) {
      return {
        data: { id: '' },
        error: {
          message: 'Character validation failed',
          code: 'VALIDATION_ERROR',
          status: 400,
        },
      };
    }

    // Format the data for submission
    const submissionData = this.formatCharacterData(character);

    // Submit to the backend
    return this.apiService.post<{ id: string }>('/character-builder/submit', submissionData);
  }

  public async getSubmissionStatus(
    submissionId: string
  ): Promise<ApiResponse<{ status: string; message?: string }>> {
    return this.apiService.get<{ status: string; message?: string }>(
      `/character-builder/submission/${submissionId}/status`
    );
  }
}

export default CharacterSubmissionService;
