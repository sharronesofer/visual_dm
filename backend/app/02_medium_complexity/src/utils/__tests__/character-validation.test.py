from typing import Any, Dict



  validateCharacter,
  validateAttributes,
  validateSkills,
  validateEquipment,
  ValidationError,
} from '../validation'
describe('Character Validation', () => {
  describe('validateAttributes', () => {
    it('should validate valid attributes', () => {
      const validAttributes: Attributes = {
        strength: 10,
        dexterity: 12,
        constitution: 14,
        intelligence: 13,
        wisdom: 11,
        charisma: 15,
      }
      const errors = validateAttributes(validAttributes)
      expect(errors).toHaveLength(0)
    })
    it('should return errors for invalid attributes', () => {
      const invalidAttributes: Attributes = {
        strength: 2, 
        dexterity: 21, 
        constitution: 14,
        intelligence: 13,
        wisdom: 11,
        charisma: 15,
      }
      const errors = validateAttributes(invalidAttributes)
      expect(errors).toHaveLength(2)
      expect(errors[0]).toEqual({
        field: 'strength',
        message: 'Strength must be between 3 and 20',
        severity: 'error',
      })
      expect(errors[1]).toEqual({
        field: 'dexterity',
        message: 'Dexterity must be between 3 and 20',
        severity: 'error',
      })
    })
  })
  describe('validateSkills', () => {
    it('should validate valid skills', () => {
      const validSkills = [
        { name: 'Athletics', isProficient: true },
        { name: 'Stealth', isProficient: false },
      ]
      const errors = validateSkills(validSkills)
      expect(errors).toHaveLength(0)
    })
    it('should return errors for empty skills', () => {
      const errors = validateSkills([])
      expect(errors).toHaveLength(1)
      expect(errors[0]).toEqual({
        field: 'skills',
        message: 'Must select at least one skill',
        severity: 'error',
      })
    })
    it('should return errors when no proficient skills', () => {
      const noProficentSkills = [
        { name: 'Athletics', isProficient: false },
        { name: 'Stealth', isProficient: false },
      ]
      const errors = validateSkills(noProficentSkills)
      expect(errors).toHaveLength(1)
      expect(errors[0]).toEqual({
        field: 'skills',
        message: 'Must have at least one proficient skill',
        severity: 'error',
      })
    })
  })
  describe('validateEquipment', () => {
    it('should validate valid equipment', () => {
      const validEquipment = [
        { name: 'Longsword', type: 'weapon', quantity: 1, description: 'A versatile sword' },
        { name: 'Chain Mail', type: 'armor', quantity: 1, description: 'Heavy armor' },
      ]
      const errors = validateEquipment(validEquipment)
      expect(errors).toHaveLength(0)
    })
    it('should return errors for invalid equipment', () => {
      const invalidEquipment = [
        { name: '', type: '', quantity: 0, description: '' },
      ]
      const errors = validateEquipment(invalidEquipment)
      expect(errors).toHaveLength(3)
      expect(errors).toContainEqual({
        field: 'equipment[0].name',
        message: 'Item name is required',
        severity: 'error',
      })
      expect(errors).toContainEqual({
        field: 'equipment[0].type',
        message: 'Item type is required',
        severity: 'error',
      })
      expect(errors).toContainEqual({
        field: 'equipment[0].quantity',
        message: 'Quantity must be at least 1',
        severity: 'error',
      })
    })
  })
  describe('validateCharacter', () => {
    const mockRace: Race = {
      name: 'Human',
      description: 'Versatile and adaptable',
      abilityScoreIncrease: Dict[str, Any],
      speed: 30,
      size: 'Medium',
      languages: ['Common'],
      traits: [{ name: 'Versatile', description: 'Gain proficiency in one skill' }],
    }
    const mockClass: Class = {
      name: 'Fighter',
      description: 'Master of martial combat',
      hitDie: 10,
      primaryAbility: 'strength',
      savingThrows: ['strength', 'constitution'],
      proficiencies: Dict[str, Any],
      features: [{ name: 'Fighting Style', level: 1, description: 'Choose a fighting style' }],
    }
    const mockBackground: Background = {
      name: 'Soldier',
      description: 'Military background',
      skillProficiencies: ['Athletics', 'Intimidation'],
      toolProficiencies: ['Gaming Set', 'Vehicles (Land)'],
      languages: [],
      equipment: [{ name: 'Common Clothes', type: 'gear', quantity: 1, description: 'A set of common clothes' }],
      feature: Dict[str, Any],
      suggestedCharacteristics: Dict[str, Any],
    }
    it('should validate a valid character', () => {
      const validCharacter: CharacterData = {
        id: '123',
        name: 'Test Character',
        race: mockRace,
        class: mockClass,
        background: mockBackground,
        level: 1,
        experience: 0,
        attributes: Dict[str, Any],
        skills: [{ name: 'Athletics', ability: 'strength', proficient: true, expertise: false, value: 4 }],
        features: [],
        equipment: [
          { name: 'Longsword', type: 'weapon', quantity: 1, description: 'A versatile sword' },
          { name: 'Chain Mail', type: 'armor', quantity: 1, description: 'Heavy armor' },
        ],
        proficiencies: ['simple weapons', 'martial weapons'],
        languages: ['Common'],
        description: 'A brave warrior',
        personality: Dict[str, Any],
        alignment: 'Lawful Good',
        feats: [],
        derivedStats: Dict[str, Any],
        },
        appearance: Dict[str, Any],
        backstory: 'Grew up in a military family',
        skillPoints: 0,
      }
      const result = validateCharacter(validCharacter)
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })
    it('should return errors for an invalid character', () => {
      const invalidCharacter: Partial<CharacterData> = {
        id: '123',
        name: '',  
        background: mockBackground,
        level: 1,
        experience: 0,
        attributes: Dict[str, Any],
        skills: [],  
        features: [],
        equipment: [],  
        proficiencies: [],
        languages: [],
        description: '',
        personality: Dict[str, Any],
        alignment: 'Lawful Good',
        feats: [],
        derivedStats: Dict[str, Any],
        },
        appearance: Dict[str, Any],
        backstory: '',
        skillPoints: 0,
      }
      const result = validateCharacter(invalidCharacter as CharacterData)
      expect(result.isValid).toBe(false)
      const errorMessages = result.errors.map(e => e.message)
      expect(errorMessages).toContain('Name is required')
      expect(errorMessages).toContain('Race is required')
      expect(errorMessages).toContain('Class is required')
      expect(errorMessages).toContain('Strength must be between 3 and 20')
      expect(errorMessages).toContain('Dexterity must be between 3 and 20')
      expect(errorMessages).toContain('Must select at least one skill')
      expect(errorMessages).toContain('No armor selected')
      expect(errorMessages).toContain('No weapon selected')
    })
  })
}) 