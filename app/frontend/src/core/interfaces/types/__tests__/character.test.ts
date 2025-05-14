import {
  ISkill,
  IBackground,
  ICharacter,
  ICalculatedSkills,
  IValidationError,
  isValidSkill,
  isValidBackground,
} from '../character';

describe('Character Type System', () => {
  describe('ISkill', () => {
    it('should accept valid skill data', () => {
      const skill: ISkill = {
        id: 'stealth',
        name: 'Stealth',
        description: 'Ability to move silently and hide',
        points: 0,
        modifier: 0,
        maxPoints: 5,
        category: 'Subterfuge',
      };

      expect(isValidSkill(skill)).toBe(true);
    });

    it('should reject invalid skill data', () => {
      const invalidSkill = {
        id: 'stealth',
        name: 'Stealth',
        // Missing required properties
        points: 0,
      };

      expect(isValidSkill(invalidSkill)).toBe(false);
    });
  });

  describe('IBackground', () => {
    it('should accept valid background data', () => {
      const background: IBackground = {
        id: 'thief',
        name: 'Thief',
        description: 'A skilled burglar and pickpocket',
        skillModifiers: {
          stealth: 2,
          lockpicking: 1,
        },
        flavorText:
          'You grew up on the streets, learning to survive by your wits.',
      };

      expect(isValidBackground(background)).toBe(true);
    });

    it('should reject invalid background data', () => {
      const invalidBackground = {
        id: 'thief',
        name: 'Thief',
        // Missing required properties
        skillModifiers: 'invalid', // Should be an object
      };

      expect(isValidBackground(invalidBackground)).toBe(false);
    });
  });

  describe('ICharacter', () => {
    it('should properly type a character object', () => {
      const character: ICharacter = {
        id: 'char1',
        name: 'Rogue',
        selectedBackgrounds: ['thief'],
        maxBackgrounds: 2,
        skills: {
          stealth: 3,
          lockpicking: 2,
        },
        totalSkillPoints: 10,
        description: 'A sneaky character',
      };

      // Verify readonly properties cannot be modified
      // @ts-expect-error - Testing readonly protection
      character.id = 'newId';
      // @ts-expect-error - Testing readonly protection
      character.maxBackgrounds = 3;
      // @ts-expect-error - Testing readonly protection
      character.totalSkillPoints = 15;

      // Verify mutable properties can be changed
      character.name = 'Master Thief';
      character.selectedBackgrounds.push('spy');
      character.skills.stealth = 4;

      expect(character.name).toBe('Master Thief');
      expect(character.selectedBackgrounds).toContain('spy');
      expect(character.skills.stealth).toBe(4);
    });
  });

  describe('ICalculatedSkills', () => {
    it('should properly type calculated skills', () => {
      const calculatedSkills: ICalculatedSkills = {
        finalValues: {
          stealth: 5,
          lockpicking: 3,
        },
        totalModifiers: {
          stealth: 2,
          lockpicking: 1,
        },
        remainingPoints: 5,
      };

      // Verify readonly properties
      // @ts-expect-error - Testing readonly protection
      calculatedSkills.finalValues.stealth = 6;
      // @ts-expect-error - Testing readonly protection
      calculatedSkills.totalModifiers.stealth = 3;
      // @ts-expect-error - Testing readonly protection
      calculatedSkills.remainingPoints = 4;

      expect(calculatedSkills.finalValues.stealth).toBe(5);
      expect(calculatedSkills.totalModifiers.stealth).toBe(2);
      expect(calculatedSkills.remainingPoints).toBe(5);
    });
  });

  describe('IValidationError', () => {
    it('should properly type validation errors', () => {
      const errors: IValidationError[] = [
        {
          type: 'SKILL_POINTS',
          message: 'Exceeded maximum skill points',
          details: { current: 12, max: 10 },
        },
        {
          type: 'BACKGROUND_LIMIT',
          message: 'Too many backgrounds selected',
        },
        {
          type: 'INVALID_SKILL',
          message: 'Skill not found',
          details: { skillId: 'nonexistent' },
        },
      ];

      // Verify type checking
      // @ts-expect-error - Testing invalid error type
      const invalidError: IValidationError = {
        type: 'UNKNOWN_ERROR',
        message: 'Invalid error type',
      };

      expect(errors[0].type).toBe('SKILL_POINTS');
      expect(errors[1].message).toBe('Too many backgrounds selected');
      expect(errors[2].details?.skillId).toBe('nonexistent');
    });
  });
});
