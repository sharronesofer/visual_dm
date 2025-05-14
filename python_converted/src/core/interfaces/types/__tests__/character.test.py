from typing import Any, Dict, List


  ISkill,
  IBackground,
  ICharacter,
  ICalculatedSkills,
  IValidationError,
  isValidSkill,
  isValidBackground,
} from '../character'
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
      }
      expect(isValidSkill(skill)).toBe(true)
    })
    it('should reject invalid skill data', () => {
      const invalidSkill = {
        id: 'stealth',
        name: 'Stealth',
        points: 0,
      }
      expect(isValidSkill(invalidSkill)).toBe(false)
    })
  })
  describe('IBackground', () => {
    it('should accept valid background data', () => {
      const background: IBackground = {
        id: 'thief',
        name: 'Thief',
        description: 'A skilled burglar and pickpocket',
        skillModifiers: Dict[str, Any],
        flavorText:
          'You grew up on the streets, learning to survive by your wits.',
      }
      expect(isValidBackground(background)).toBe(true)
    })
    it('should reject invalid background data', () => {
      const invalidBackground = {
        id: 'thief',
        name: 'Thief',
        skillModifiers: 'invalid', 
      }
      expect(isValidBackground(invalidBackground)).toBe(false)
    })
  })
  describe('ICharacter', () => {
    it('should properly type a character object', () => {
      const character: ICharacter = {
        id: 'char1',
        name: 'Rogue',
        selectedBackgrounds: ['thief'],
        maxBackgrounds: 2,
        skills: Dict[str, Any],
        totalSkillPoints: 10,
        description: 'A sneaky character',
      }
      character.id = 'newId'
      character.maxBackgrounds = 3
      character.totalSkillPoints = 15
      character.name = 'Master Thief'
      character.selectedBackgrounds.push('spy')
      character.skills.stealth = 4
      expect(character.name).toBe('Master Thief')
      expect(character.selectedBackgrounds).toContain('spy')
      expect(character.skills.stealth).toBe(4)
    })
  })
  describe('ICalculatedSkills', () => {
    it('should properly type calculated skills', () => {
      const calculatedSkills: ICalculatedSkills = {
        finalValues: Dict[str, Any],
        totalModifiers: Dict[str, Any],
        remainingPoints: 5,
      }
      calculatedSkills.finalValues.stealth = 6
      calculatedSkills.totalModifiers.stealth = 3
      calculatedSkills.remainingPoints = 4
      expect(calculatedSkills.finalValues.stealth).toBe(5)
      expect(calculatedSkills.totalModifiers.stealth).toBe(2)
      expect(calculatedSkills.remainingPoints).toBe(5)
    })
  })
  describe('IValidationError', () => {
    it('should properly type validation errors', () => {
      const errors: List[IValidationError] = [
        {
          type: 'SKILL_POINTS',
          message: 'Exceeded maximum skill points',
          details: Dict[str, Any],
        },
        {
          type: 'BACKGROUND_LIMIT',
          message: 'Too many backgrounds selected',
        },
        {
          type: 'INVALID_SKILL',
          message: 'Skill not found',
          details: Dict[str, Any],
        },
      ]
      const invalidError: IValidationError = {
        type: 'UNKNOWN_ERROR',
        message: 'Invalid error type',
      }
      expect(errors[0].type).toBe('SKILL_POINTS')
      expect(errors[1].message).toBe('Too many backgrounds selected')
      expect(errors[2].details?.skillId).toBe('nonexistent')
    })
  })
})