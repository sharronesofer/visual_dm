import { ValidationService } from '../validationService';
import { CharacterData, Equipment } from '../../types/character';
import { RaceType, ClassType, BackgroundType } from '../../types/character';
import { Attributes } from '../../types/character';

describe('ValidationService', () => {
  let validationService: ValidationService;

  const mockEquipment: Equipment[] = [
    {
      name: 'Longsword',
      type: 'weapon',
      quantity: 1,
      description: 'A versatile sword',
      properties: ['versatile'],
      weight: 3,
      cost: { amount: 15, unit: 'gp' },
      damage: '1d8',
    } as Equipment,
    {
      name: 'Chain Mail',
      type: 'armor',
      quantity: 1,
      description: 'Heavy armor',
      properties: ['heavy'],
      weight: 55,
      cost: { amount: 75, unit: 'gp' },
      armorClass: 16,
    } as Equipment,
  ];

  const mockRace = {
    name: 'Human' as RaceType,
    description: 'A versatile and ambitious people',
    abilityScoreIncrease: {},
    speed: 30,
    size: 'Medium' as 'Medium',
    languages: ['Common'],
    traits: [],
  };

  const mockClass = {
    name: 'Fighter' as ClassType,
    description: 'A master of martial combat',
    hitDie: 10,
    primaryAbility: 'strength' as keyof Attributes,
    savingThrows: ['strength', 'constitution'] as Array<keyof Attributes>,
    proficiencies: {
      armor: ['all'],
      weapons: ['all'],
      tools: [],
      skills: [],
    },
    features: [],
  };

  const mockBackground = {
    name: 'Soldier' as BackgroundType,
    description: 'A background of military service',
    skillProficiencies: [],
    toolProficiencies: [],
    languages: [],
    equipment: [],
    feature: { name: 'Military Rank', description: 'You have a military rank.' },
    suggestedCharacteristics: {
      personalityTraits: [],
      ideals: [],
      bonds: [],
      flaws: [],
    },
  };

  const mockCharacter: CharacterData = {
    id: '1',
    name: 'Test Character',
    race: mockRace,
    class: mockClass,
    background: mockBackground,
    level: 1,
    experience: 0,
    attributes: {
      strength: 14,
      dexterity: 12,
      constitution: 13,
      intelligence: 10,
      wisdom: 11,
      charisma: 8,
    },
    skills: [],
    features: [],
    equipment: mockEquipment,
    spells: { cantrips: [], prepared: [], known: [] },
    proficiencies: [],
    languages: [],
    description: '',
    personality: { traits: [], ideals: [], bonds: [], flaws: [] },
    alignment: 'Lawful Good',
    feats: [],
    derivedStats: {
      hitPoints: 10,
      armorClass: 16,
      initiative: 1,
      speed: 30,
      proficiencyBonus: 2,
      savingThrows: { strength: 2, dexterity: 1, constitution: 2, intelligence: 0, wisdom: 0, charisma: 0 },
    },
    appearance: { height: '', weight: '', age: 20, eyes: '', skin: '', hair: '' },
    backstory: '',
    skillPoints: 0,
  };

  beforeEach(() => {
    validationService = ValidationService.getInstance();
  });

  describe('validateCharacter', () => {
    it('should return valid result for valid character', () => {
      const result = validationService.validateCharacter(mockCharacter);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.incompleteFields).toHaveLength(0);
    });

    it('should detect missing required fields', () => {
      const invalidCharacter = { ...mockCharacter, name: '', race: { ...mockRace, name: '' as any } };
      const result = validationService.validateCharacter(invalidCharacter);
      expect(result.isValid).toBe(false);
      expect(result.incompleteFields).toHaveLength(2);
      expect(result.incompleteFields).toContain('name');
      expect(result.incompleteFields).toContain('race');
    });

    it('should validate attribute ranges', () => {
      const invalidCharacter = {
        ...mockCharacter,
        attributes: {
          ...mockCharacter.attributes,
          strength: 2,
          dexterity: 21,
        },
      };
      const result = validationService.validateCharacter(invalidCharacter);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('strength cannot be less than 3');
      expect(result.errors).toContain('dexterity cannot be greater than 20');
    });

    it('should validate equipment based on class', () => {
      const wizardCharacter = {
        ...mockCharacter,
        class: { ...mockClass, name: 'Wizard' as ClassType },
        equipment: [
          {
            name: 'Staff',
            type: 'weapon',
            quantity: 1,
            description: 'A magical staff',
            properties: ['versatile'],
            weight: 4,
            cost: { amount: 5, unit: 'gp' },
            damage: '1d6',
          } as Equipment,
        ],
      };
      const result = validationService.validateCharacter(wizardCharacter);
      expect(result.warnings).toContain('Wizards typically need a spellbook');
    });

    it('should warn about missing equipment', () => {
      const noEquipmentCharacter = { ...mockCharacter, equipment: [] };
      const result = validationService.validateCharacter(noEquipmentCharacter);
      expect(result.warnings).toContain('Character has no equipment selected');
    });

    it('should validate fighter equipment preferences', () => {
      const lightArmorFighter = {
        ...mockCharacter,
        equipment: [
          {
            name: 'Leather Armor',
            type: 'armor',
            quantity: 1,
            description: 'Light armor',
            properties: ['light'],
            weight: 10,
            cost: { amount: 10, unit: 'gp' },
            armorClass: 11,
          } as Equipment,
        ],
      };
      const result = validationService.validateCharacter(lightArmorFighter);
      expect(result.warnings).toContain('Fighters often benefit from heavy armor');
    });

    it('should validate rogue equipment preferences', () => {
      const heavyArmorRogue = {
        ...mockCharacter,
        class: { ...mockClass, name: 'Rogue' as ClassType },
        equipment: [mockEquipment[1]], // Chain Mail (heavy armor)
      };
      const result = validationService.validateCharacter(heavyArmorRogue);
      expect(result.warnings).toContain('Rogues typically use light armor');
    });
  });

  describe('getFieldValidationRules', () => {
    it('should return validation rules for all required fields', () => {
      const rules = validationService.getFieldValidationRules();
      expect(rules).toHaveProperty('name');
      expect(rules).toHaveProperty('race');
      expect(rules).toHaveProperty('class');
      expect(rules).toHaveProperty('background');
      expect(rules).toHaveProperty('level');
      expect(rules).toHaveProperty('gold');
    });

    it('should validate name rules correctly', () => {
      const rules = validationService.getFieldValidationRules();
      const nameRules = rules.name;

      expect(nameRules[0].validate('Al')).toBe(true);
      expect(nameRules[0].validate('A')).toBe(false);
      expect(nameRules[1].validate('A'.repeat(50))).toBe(true);
      expect(nameRules[1].validate('A'.repeat(51))).toBe(false);
      expect(nameRules[2].validate("D'Artagnan")).toBe(true);
      expect(nameRules[2].validate('Invalid123')).toBe(false);
    });

    it('should validate level rules correctly', () => {
      const rules = validationService.getFieldValidationRules();
      const levelRules = rules.level;

      expect(levelRules[0].validate(1)).toBe(true);
      expect(levelRules[0].validate(20)).toBe(true);
      expect(levelRules[0].validate(0)).toBe(false);
      expect(levelRules[0].validate(21)).toBe(false);
    });

    it('should validate gold rules correctly', () => {
      const rules = validationService.getFieldValidationRules();
      const goldRules = rules.gold;

      expect(goldRules[0].validate(0)).toBe(true);
      expect(goldRules[0].validate(100)).toBe(true);
      expect(goldRules[0].validate(-1)).toBe(false);
    });
  });

  describe('handleApiError', () => {
    it('should handle structured API errors', () => {
      const apiError = {
        response: {
          data: {
            errors: ['Invalid race selection', 'Class requirements not met'],
          },
        },
      };
      const result = validationService.handleApiError(apiError);
      expect(result.isValid).toBe(false);
      expect(result.errors).toEqual([
        'Invalid race selection',
        'Class requirements not met',
      ]);
    });

    it('should handle single error message', () => {
      const apiError = {
        response: {
          data: {
            message: 'Character validation failed',
          },
        },
      };
      const result = validationService.handleApiError(apiError);
      expect(result.isValid).toBe(false);
      expect(result.errors).toEqual(['Character validation failed']);
    });

    it('should handle unknown errors', () => {
      const result = validationService.handleApiError({});
      expect(result.isValid).toBe(false);
      expect(result.errors).toEqual([
        'An unexpected error occurred. Please try again.',
      ]);
    });
  });
});
