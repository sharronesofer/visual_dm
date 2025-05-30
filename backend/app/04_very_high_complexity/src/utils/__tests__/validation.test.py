from typing import Any, Dict



  validateCharacter,
  validateAttributes,
  validateSkills,
  validateEquipment,
  isString,
  isNumber,
  isBoolean,
  isArray,
  isObject,
  isDate,
  isEmail,
  isURL,
  isNumericString,
  isAlphanumeric,
  isAlpha,
  isEmpty,
  isLength,
  isPositive,
  isNegative,
  isInteger,
  isFloat,
  isInRange,
  hasId,
  isValidJSON,
} from '../validation'
  isUndefined,
  isNull,
  isNullOrUndefined,
  isFunction,
  isSymbol,
  isValidationError,
  isValidationResult,
  isAttributes,
  isUUID,
  isISO8601Date,
  isStrongPassword,
  isArrayOf,
  hasMinLength,
  hasMaxLength,
  isUnique,
  hasRequiredProperties,
  isEmptyObject,
  isPositiveInteger,
  isNegativeInteger,
  isPercentage,
  isValidGold,
} from '../validation'
describe('Validation Utils', () => {
  describe('validateCharacter', () => {
    const mockRace = {
      name: 'Human' as RaceType,
      description: 'Versatile and adaptable',
      abilityScoreIncrease: Dict[str, Any],
      speed: 30,
      size: 'Medium' as 'Medium',
      languages: ['Common'],
      traits: [{ name: 'Versatile', description: 'Gain proficiency in one skill' }],
    }
    const mockClass = {
      name: 'Fighter' as ClassType,
      description: 'Master of martial combat',
      hitDie: 10,
      primaryAbility: 'strength' as keyof Attributes,
      savingThrows: ['strength', 'constitution'] as Array<keyof Attributes>,
      proficiencies: Dict[str, Any],
      features: [{ name: 'Fighting Style', level: 1, description: 'Choose a fighting style' }],
    }
    const mockBackground = {
      name: 'Soldier' as BackgroundType,
      description: 'Military background',
      skillProficiencies: ['Athletics', 'Intimidation'],
      toolProficiencies: ['Gaming Set', 'Vehicles (Land)'],
      languages: [],
      equipment: [{ name: 'Common Clothes', type: 'gear' as 'gear', quantity: 1, description: 'A set of common clothes' }],
      feature: Dict[str, Any],
      suggestedCharacteristics: Dict[str, Any],
    }
    const validCharacter: CharacterData = {
      id: '1',
      name: 'Test Character',
      race: mockRace,
      class: mockClass,
      background: mockBackground,
      level: 1,
      experience: 0,
      attributes: Dict[str, Any],
      skills: [
        {
          name: 'Athletics',
          ability: 'strength',
          proficient: true,
          expertise: false,
          value: 4,
        },
      ],
      features: [],
      equipment: [
        { name: 'Longsword', type: 'weapon', quantity: 1, description: 'A versatile sword' },
        { name: 'Chain Mail', type: 'armor', quantity: 1, description: 'Heavy armor' },
      ],
      spells: Dict[str, Any],
      proficiencies: [],
      languages: ['Common'],
      description: '',
      personality: Dict[str, Any],
      alignment: 'Lawful Good',
      feats: [],
      derivedStats: Dict[str, Any],
      },
      appearance: Dict[str, Any],
      backstory: 'Grew up in a military family',
      skillPoints: 0,
    }
    it('should validate a valid character', () => {
      const result = validateCharacter(validCharacter)
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })
    it('should validate required fields', () => {
      const invalidCharacter = {
        ...validCharacter,
        name: '',
        race: Dict[str, Any],
        class: Dict[str, Any],
      }
      const result = validateCharacter(invalidCharacter)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'name',
          message: 'Name is required',
          severity: 'error',
        })
      )
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'race',
          message: 'Race is required',
          severity: 'error',
        })
      )
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'class',
          message: 'Class is required',
          severity: 'error',
        })
      )
    })
    it('should validate name length', () => {
      const invalidCharacter = {
        ...validCharacter,
        name: 'A',
      }
      const result = validateCharacter(invalidCharacter)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'name',
          message: 'Name must be at least 2 characters',
          severity: 'error',
        })
      )
    })
    it('should validate attributes', () => {
      const invalidCharacter = {
        ...validCharacter,
        attributes: Dict[str, Any],
      }
      const result = validateCharacter(invalidCharacter)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'attributes.strength',
          message: 'Strength must be between 3 and 20',
          severity: 'error',
        })
      )
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'attributes.dexterity',
          message: 'Dexterity must be between 3 and 20',
          severity: 'error',
        })
      )
    })
    it('should validate skills', () => {
      const invalidCharacter = {
        ...validCharacter,
        skills: [],
      }
      const result = validateCharacter(invalidCharacter)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'skills',
          message: 'Must select at least one skill',
          severity: 'error',
        })
      )
    })
    it('should validate equipment warnings', () => {
      const characterWithoutEquipment = {
        ...validCharacter,
        equipment: [],
      }
      const result = validateCharacter(characterWithoutEquipment)
      expect(result.isValid).toBe(true) 
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'equipment',
          message: 'No armor selected',
          severity: 'warning',
        })
      )
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'equipment',
          message: 'No weapon selected',
          severity: 'warning',
        })
      )
    })
  })
  describe('validateAttributes', () => {
    const validAttributes = {
      strength: 15,
      dexterity: 14,
      constitution: 13,
      intelligence: 12,
      wisdom: 10,
      charisma: 8,
    }
    it('should validate valid attributes', () => {
      const result = validateAttributes(validAttributes)
      expect(result).toHaveLength(0)
    })
    it('should validate missing attributes', () => {
      const invalidAttributes = {
        ...validAttributes,
        strength: undefined,
        dexterity: null,
      } as any
      const result = validateAttributes(invalidAttributes)
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'strength',
          message: 'Strength is required',
          severity: 'error',
        })
      )
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'dexterity',
          message: 'Dexterity is required',
          severity: 'error',
        })
      )
    })
    it('should validate attribute ranges', () => {
      const invalidAttributes = {
        ...validAttributes,
        wisdom: 2,
        charisma: 21,
      }
      const result = validateAttributes(invalidAttributes)
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'wisdom',
          message: 'Wisdom must be between 3 and 20',
          severity: 'error',
        })
      )
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'charisma',
          message: 'Charisma must be between 3 and 20',
          severity: 'error',
        })
      )
    })
  })
  describe('validateSkills', () => {
    const validSkills = [
      { name: 'Athletics', ability: 'strength', proficient: true, expertise: false, value: 4 },
      { name: 'Acrobatics', ability: 'dexterity', proficient: false, expertise: false, value: 2 },
    ]
    it('should validate valid skills', () => {
      const result = validateSkills(validSkills)
      expect(result).toHaveLength(0)
    })
    it('should validate empty skills', () => {
      const result = validateSkills([])
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'skills',
          message: 'Must select at least one skill',
          severity: 'error',
        })
      )
    })
    it('should validate proficient skills', () => {
      const skillsWithoutProficiency = [
        { name: 'Athletics', ability: 'strength', proficient: false, expertise: false, value: 3 },
        { name: 'Acrobatics', ability: 'dexterity', proficient: false, expertise: false, value: 2 },
      ]
      const result = validateSkills(skillsWithoutProficiency)
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'skills',
          message: 'Must have at least one proficient skill',
          severity: 'error',
        })
      )
    })
  })
  describe('validateEquipment', () => {
    const validEquipment = [
      { name: 'Longsword', type: 'weapon', quantity: 1 },
      { name: 'Chain Mail', type: 'armor', quantity: 1 },
    ]
    it('should validate valid equipment', () => {
      const result = validateEquipment(validEquipment)
      expect(result).toHaveLength(0)
    })
    it('should validate missing equipment fields', () => {
      const invalidEquipment = [
        { name: '', type: '', quantity: 0 },
        { name: 'Chain Mail', type: undefined, quantity: -1 } as any,
      ]
      const result = validateEquipment(invalidEquipment)
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'equipment[0].name',
          message: 'Item name is required',
          severity: 'error',
        })
      )
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'equipment[0].type',
          message: 'Item type is required',
          severity: 'error',
        })
      )
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'equipment[0].quantity',
          message: 'Quantity must be at least 1',
          severity: 'error',
        })
      )
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'equipment[1].type',
          message: 'Item type is required',
          severity: 'error',
        })
      )
      expect(result).toContainEqual(
        expect.objectContaining({
          field: 'equipment[1].quantity',
          message: 'Quantity must be at least 1',
          severity: 'error',
        })
      )
    })
  })
})
describe('Type Guards', () => {
  describe('isString', () => {
    it('should return true for strings', () => {
      expect(isString('test')).toBe(true)
      expect(isString('')).toBe(true)
    })
    it('should return false for non-strings', () => {
      expect(isString(123)).toBe(false)
      expect(isString({})).toBe(false)
      expect(isString(null)).toBe(false)
      expect(isString(undefined)).toBe(false)
    })
  })
  describe('isNumber', () => {
    it('should return true for numbers', () => {
      expect(isNumber(123)).toBe(true)
      expect(isNumber(0)).toBe(true)
      expect(isNumber(-123.45)).toBe(true)
    })
    it('should return false for NaN and non-numbers', () => {
      expect(isNumber(NaN)).toBe(false)
      expect(isNumber('123')).toBe(false)
      expect(isNumber(null)).toBe(false)
    })
  })
  describe('isBoolean', () => {
    it('should return true for booleans', () => {
      expect(isBoolean(true)).toBe(true)
      expect(isBoolean(false)).toBe(true)
    })
    it('should return false for non-booleans', () => {
      expect(isBoolean(1)).toBe(false)
      expect(isBoolean('true')).toBe(false)
      expect(isBoolean(null)).toBe(false)
    })
  })
  describe('isArray', () => {
    it('should return true for arrays', () => {
      expect(isArray([])).toBe(true)
      expect(isArray([1, 2, 3])).toBe(true)
    })
    it('should return false for non-arrays', () => {
      expect(isArray({})).toBe(false)
      expect(isArray('[]')).toBe(false)
      expect(isArray(null)).toBe(false)
    })
  })
  describe('isObject', () => {
    it('should return true for objects', () => {
      expect(isObject({})).toBe(true)
      expect(isObject({ key: 'value' })).toBe(true)
    })
    it('should return false for non-objects', () => {
      expect(isObject(null)).toBe(false)
      expect(isObject([])).toBe(false)
      expect(isObject('object')).toBe(false)
    })
  })
  describe('isDate', () => {
    it('should return true for valid dates', () => {
      expect(isDate(new Date())).toBe(true)
      expect(isDate(new Date('2024-01-01'))).toBe(true)
    })
    it('should return false for invalid dates and non-dates', () => {
      expect(isDate(new Date('invalid'))).toBe(false)
      expect(isDate('2024-01-01')).toBe(false)
      expect(isDate(null)).toBe(false)
    })
  })
})
describe('Common Validations', () => {
  describe('isEmail', () => {
    it('should return true for valid email addresses', () => {
      expect(isEmail('test@example.com')).toBe(true)
      expect(isEmail('user.name+tag@domain.co.uk')).toBe(true)
    })
    it('should return false for invalid email addresses', () => {
      expect(isEmail('invalid')).toBe(false)
      expect(isEmail('@domain.com')).toBe(false)
      expect(isEmail('user@')).toBe(false)
    })
  })
  describe('isURL', () => {
    it('should return true for valid URLs', () => {
      expect(isURL('https:
      expect(isURL('http:
    })
    it('should return false for invalid URLs', () => {
      expect(isURL('invalid')).toBe(false)
      expect(isURL('http:
    })
  })
  describe('isNumericString', () => {
    it('should return true for numeric strings', () => {
      expect(isNumericString('123')).toBe(true)
      expect(isNumericString('-123.45')).toBe(true)
    })
    it('should return false for non-numeric strings', () => {
      expect(isNumericString('abc')).toBe(false)
      expect(isNumericString('12.34.56')).toBe(false)
    })
  })
  describe('isAlphanumeric', () => {
    it('should return true for alphanumeric strings', () => {
      expect(isAlphanumeric('abc123')).toBe(true)
      expect(isAlphanumeric('ABC123')).toBe(true)
    })
    it('should return false for non-alphanumeric strings', () => {
      expect(isAlphanumeric('abc 123')).toBe(false)
      expect(isAlphanumeric('abc-123')).toBe(false)
    })
  })
  describe('isAlpha', () => {
    it('should return true for alphabetic strings', () => {
      expect(isAlpha('abc')).toBe(true)
      expect(isAlpha('ABC')).toBe(true)
    })
    it('should return false for non-alphabetic strings', () => {
      expect(isAlpha('abc123')).toBe(false)
      expect(isAlpha('abc ')).toBe(false)
    })
  })
  describe('isEmpty', () => {
    it('should return true for empty values', () => {
      expect(isEmpty('')).toBe(true)
      expect(isEmpty('   ')).toBe(true)
      expect(isEmpty([])).toBe(true)
      expect(isEmpty({})).toBe(true)
      expect(isEmpty(null)).toBe(true)
      expect(isEmpty(undefined)).toBe(true)
    })
    it('should return false for non-empty values', () => {
      expect(isEmpty('test')).toBe(false)
      expect(isEmpty([1])).toBe(false)
      expect(isEmpty({ key: 'value' })).toBe(false)
    })
  })
  describe('isLength', () => {
    it('should validate string length within range', () => {
      expect(isLength('test', 2, 6)).toBe(true)
      expect(isLength('test', 4, 4)).toBe(true)
      expect(isLength('test', 5)).toBe(false)
    })
    it('should validate array length within range', () => {
      expect(isLength([1, 2, 3], 2, 4)).toBe(true)
      expect(isLength([1, 2, 3], 3, 3)).toBe(true)
      expect(isLength([1, 2, 3], 4)).toBe(false)
    })
  })
  describe('isPositive', () => {
    it('should return true for positive numbers', () => {
      expect(isPositive(1)).toBe(true)
      expect(isPositive(0.1)).toBe(true)
    })
    it('should return false for zero and negative numbers', () => {
      expect(isPositive(0)).toBe(false)
      expect(isPositive(-1)).toBe(false)
    })
  })
  describe('isNegative', () => {
    it('should return true for negative numbers', () => {
      expect(isNegative(-1)).toBe(true)
      expect(isNegative(-0.1)).toBe(true)
    })
    it('should return false for zero and positive numbers', () => {
      expect(isNegative(0)).toBe(false)
      expect(isNegative(1)).toBe(false)
    })
  })
  describe('isInteger', () => {
    it('should return true for integers', () => {
      expect(isInteger(1)).toBe(true)
      expect(isInteger(-1)).toBe(true)
      expect(isInteger(0)).toBe(true)
    })
    it('should return false for non-integers', () => {
      expect(isInteger(1.1)).toBe(false)
      expect(isInteger(-1.1)).toBe(false)
    })
  })
  describe('isFloat', () => {
    it('should return true for floating-point numbers', () => {
      expect(isFloat(1.1)).toBe(true)
      expect(isFloat(-1.1)).toBe(true)
    })
    it('should return false for integers', () => {
      expect(isFloat(1)).toBe(false)
      expect(isFloat(-1)).toBe(false)
      expect(isFloat(0)).toBe(false)
    })
  })
  describe('isInRange', () => {
    it('should return true for numbers within range', () => {
      expect(isInRange(5, 0, 10)).toBe(true)
      expect(isInRange(0, 0, 10)).toBe(true)
      expect(isInRange(10, 0, 10)).toBe(true)
    })
    it('should return false for numbers outside range', () => {
      expect(isInRange(-1, 0, 10)).toBe(false)
      expect(isInRange(11, 0, 10)).toBe(false)
    })
  })
})
describe('Custom Type Guards', () => {
  describe('hasId', () => {
    it('should return true for objects with string or number id', () => {
      expect(hasId({ id: '123' })).toBe(true)
      expect(hasId({ id: 123 })).toBe(true)
    })
    it('should return false for objects without valid id', () => {
      expect(hasId({})).toBe(false)
      expect(hasId({ id: null })).toBe(false)
      expect(hasId({ id: {} })).toBe(false)
    })
  })
  describe('isValidJSON', () => {
    it('should return true for valid JSON strings', () => {
      expect(isValidJSON('{}')).toBe(true)
      expect(isValidJSON('{"key":"value"}')).toBe(true)
      expect(isValidJSON('[1,2,3]')).toBe(true)
    })
    it('should return false for invalid JSON strings', () => {
      expect(isValidJSON('{')).toBe(false)
      expect(isValidJSON('invalid')).toBe(false)
      expect(isValidJSON('[1,2,')).toBe(false)
    })
  })
})
describe('Validation Utilities', () => {
  describe('Primitive Type Guards', () => {
    it('isString should correctly identify strings', () => {
      expect(isString('')).toBe(true)
      expect(isString('hello')).toBe(true)
      expect(isString(123)).toBe(false)
      expect(isString(null)).toBe(false)
      expect(isString(undefined)).toBe(false)
    })
    it('isNumber should correctly identify numbers', () => {
      expect(isNumber(0)).toBe(true)
      expect(isNumber(123.45)).toBe(true)
      expect(isNumber(NaN)).toBe(false)
      expect(isNumber('123')).toBe(false)
      expect(isNumber(null)).toBe(false)
    })
    it('isBoolean should correctly identify booleans', () => {
      expect(isBoolean(true)).toBe(true)
      expect(isBoolean(false)).toBe(true)
      expect(isBoolean(0)).toBe(false)
      expect(isBoolean('true')).toBe(false)
      expect(isBoolean(null)).toBe(false)
    })
    it('isArray should correctly identify arrays', () => {
      expect(isArray([])).toBe(true)
      expect(isArray([1, 2, 3])).toBe(true)
      expect(isArray({})).toBe(false)
      expect(isArray(null)).toBe(false)
      expect(isArray('[]')).toBe(false)
    })
    it('isObject should correctly identify objects', () => {
      expect(isObject({})).toBe(true)
      expect(isObject({ key: 'value' })).toBe(true)
      expect(isObject([])).toBe(false)
      expect(isObject(null)).toBe(false)
      expect(isObject(() => {})).toBe(false)
    })
    it('isDate should correctly identify valid dates', () => {
      expect(isDate(new Date())).toBe(true)
      expect(isDate(new Date('2024-03-20'))).toBe(true)
      expect(isDate(new Date('invalid'))).toBe(false)
      expect(isDate('2024-03-20')).toBe(false)
      expect(isDate(null)).toBe(false)
    })
  })
  describe('String Validations', () => {
    it('isEmail should validate email addresses', () => {
      expect(isEmail('test@example.com')).toBe(true)
      expect(isEmail('test.name@sub.example.co.uk')).toBe(true)
      expect(isEmail('invalid')).toBe(false)
      expect(isEmail('test@')).toBe(false)
      expect(isEmail('@example.com')).toBe(false)
    })
    it('isURL should validate URLs', () => {
      expect(isURL('https:
      expect(isURL('http:
      expect(isURL('invalid')).toBe(false)
      expect(isURL('http:
      expect(isURL('example.com')).toBe(false)
    })
    it('isUUID should validate UUIDs', () => {
      expect(isUUID('123e4567-e89b-12d3-a456-426614174000')).toBe(true)
      expect(isUUID('123e4567-e89b-42d3-a456-426614174000')).toBe(true)
      expect(isUUID('invalid')).toBe(false)
      expect(isUUID('123e4567-e89b-12d3-a456')).toBe(false)
    })
    it('isISO8601Date should validate ISO 8601 dates', () => {
      expect(isISO8601Date('2024-03-20')).toBe(true)
      expect(isISO8601Date('2024-03-20T15:30:00Z')).toBe(true)
      expect(isISO8601Date('invalid')).toBe(false)
      expect(isISO8601Date('2024/03/20')).toBe(false)
    })
    it('isStrongPassword should validate strong passwords', () => {
      expect(isStrongPassword('Abcd123!')).toBe(true)
      expect(isStrongPassword('P@ssw0rd')).toBe(true)
      expect(isStrongPassword('weak')).toBe(false)
      expect(isStrongPassword('NoSpecialChar1')).toBe(false)
      expect(isStrongPassword('no-upper-1!')).toBe(false)
    })
  })
  describe('Array Validations', () => {
    it('isArrayOf should validate array elements', () => {
      expect(isArrayOf(['a', 'b', 'c'], isString)).toBe(true)
      expect(isArrayOf([1, 2, 3], isNumber)).toBe(true)
      expect(isArrayOf([1, '2', 3], isNumber)).toBe(false)
      expect(isArrayOf([], isString)).toBe(true)
    })
    it('hasMinLength should validate minimum length', () => {
      expect(hasMinLength([1, 2, 3], 2)).toBe(true)
      expect(hasMinLength('abc', 2)).toBe(true)
      expect(hasMinLength([], 1)).toBe(false)
      expect(hasMinLength('a', 2)).toBe(false)
    })
    it('hasMaxLength should validate maximum length', () => {
      expect(hasMaxLength([1, 2], 3)).toBe(true)
      expect(hasMaxLength('abc', 3)).toBe(true)
      expect(hasMaxLength([1, 2, 3, 4], 3)).toBe(false)
      expect(hasMaxLength('abcd', 3)).toBe(false)
    })
    it('isUnique should validate array uniqueness', () => {
      expect(isUnique([1, 2, 3])).toBe(true)
      expect(isUnique(['a', 'b', 'c'])).toBe(true)
      expect(isUnique([1, 2, 2])).toBe(false)
      expect(isUnique(['a', 'b', 'a'])).toBe(false)
    })
  })
  describe('Object Validations', () => {
    it('hasRequiredProperties should validate required properties', () => {
      const obj = { name: 'Test', age: 25 } as const
      expect(hasRequiredProperties(obj, ['name'])).toBe(true)
      expect(hasRequiredProperties(obj, ['name', 'age'])).toBe(true)
      expect(hasRequiredProperties(obj, ['name', 'age' as keyof typeof obj])).toBe(true)
    })
    it('isEmptyObject should validate empty objects', () => {
      expect(isEmptyObject({})).toBe(true)
      expect(isEmptyObject({ key: 'value' })).toBe(false)
    })
  })
  describe('Numeric Validations', () => {
    it('isPositiveInteger should validate positive integers', () => {
      expect(isPositiveInteger(1)).toBe(true)
      expect(isPositiveInteger(0)).toBe(false)
      expect(isPositiveInteger(-1)).toBe(false)
      expect(isPositiveInteger(1.5)).toBe(false)
    })
    it('isNegativeInteger should validate negative integers', () => {
      expect(isNegativeInteger(-1)).toBe(true)
      expect(isNegativeInteger(0)).toBe(false)
      expect(isNegativeInteger(1)).toBe(false)
      expect(isNegativeInteger(-1.5)).toBe(false)
    })
    it('isPercentage should validate percentage values', () => {
      expect(isPercentage(0)).toBe(true)
      expect(isPercentage(50)).toBe(true)
      expect(isPercentage(100)).toBe(true)
      expect(isPercentage(-1)).toBe(false)
      expect(isPercentage(101)).toBe(false)
    })
    it('isValidGold should validate gold values', () => {
      expect(isValidGold(0)).toBe(true)
      expect(isValidGold(100)).toBe(true)
      expect(isValidGold(-1)).toBe(false)
      expect(isValidGold('100')).toBe(false)
      expect(isValidGold(null)).toBe(false)
    })
  })
  describe('Custom Type Predicates', () => {
    it('isValidationError should validate ValidationError objects', () => {
      expect(isValidationError({
        field: 'test',
        message: 'Test error',
        severity: 'error'
      })).toBe(true)
      expect(isValidationError({
        field: 'test',
        message: 'Test warning',
        severity: 'warning'
      })).toBe(true)
      expect(isValidationError({
        field: 'test',
        message: 'Test error'
      })).toBe(true)
      expect(isValidationError({
        field: 'test'
      })).toBe(false)
      expect(isValidationError(null)).toBe(false)
    })
    it('isValidationResult should validate ValidationResult objects', () => {
      expect(isValidationResult({
        isValid: true,
        errors: []
      })).toBe(true)
      expect(isValidationResult({
        isValid: false,
        errors: [{
          field: 'test',
          message: 'Test error',
          severity: 'error'
        }]
      })).toBe(true)
      expect(isValidationResult({
        isValid: true
      })).toBe(false)
      expect(isValidationResult(null)).toBe(false)
    })
    it('isAttributes should validate Attributes objects', () => {
      expect(isAttributes({
        strength: 10,
        dexterity: 12,
        constitution: 14,
        intelligence: 13,
        wisdom: 11,
        charisma: 15
      })).toBe(true)
      expect(isAttributes({
        strength: 2,
        dexterity: 12,
        constitution: 14,
        intelligence: 13,
        wisdom: 11,
        charisma: 15
      })).toBe(false)
      expect(isAttributes({
        strength: 10,
        dexterity: 12
      })).toBe(false)
      expect(isAttributes(null)).toBe(false)
    })
  })
})