from typing import Any


  validateRequired,
  validateEmail,
  validateLength,
  validateNumber,
  validateArray,
} from '../validation'
describe('validation utilities', () => {
  describe('validateRequired', () => {
    it('should return value when defined', () => {
      expect(validateRequired('test', 'field')).toBe('test')
      expect(validateRequired(0, 'field')).toBe(0)
      expect(validateRequired(false, 'field')).toBe(false)
      expect(validateRequired({}, 'field')).toEqual({})
    })
    it('should throw ValidationError when undefined', () => {
      expect(() => validateRequired(undefined, 'field')).toThrow(ValidationError)
      expect(() => validateRequired(undefined, 'field')).toThrow('field is required')
    })
    it('should throw ValidationError when null', () => {
      expect(() => validateRequired(null, 'field')).toThrow(ValidationError)
      expect(() => validateRequired(null, 'field')).toThrow('field is required')
    })
  })
  describe('validateEmail', () => {
    it('should return true for valid emails', () => {
      expect(validateEmail('test@example.com')).toBe(true)
      expect(validateEmail('test.name@example.co.uk')).toBe(true)
      expect(validateEmail('test+label@example.com')).toBe(true)
    })
    it('should throw ValidationError for invalid emails', () => {
      expect(() => validateEmail('test')).toThrow(ValidationError)
      expect(() => validateEmail('test@')).toThrow(ValidationError)
      expect(() => validateEmail('@example.com')).toThrow(ValidationError)
      expect(() => validateEmail('test@example')).toThrow(ValidationError)
      expect(() => validateEmail('test@.com')).toThrow(ValidationError)
    })
  })
  describe('validateLength', () => {
    it('should return true for valid lengths', () => {
      expect(validateLength('test', 'field', 1, 10)).toBe(true)
      expect(validateLength('test', 'field', 4, 4)).toBe(true)
      expect(validateLength('', 'field', 0, 10)).toBe(true)
    })
    it('should throw ValidationError when too short', () => {
      expect(() => validateLength('test', 'field', 5, 10)).toThrow(ValidationError)
      expect(() => validateLength('test', 'field', 5, 10)).toThrow('field must be between 5 and 10 characters')
    })
    it('should throw ValidationError when too long', () => {
      expect(() => validateLength('test', 'field', 1, 3)).toThrow(ValidationError)
      expect(() => validateLength('test', 'field', 1, 3)).toThrow('field must be between 1 and 3 characters')
    })
  })
  describe('validateNumber', () => {
    it('should return true for valid numbers', () => {
      expect(validateNumber(5, 'field')).toBe(true)
      expect(validateNumber(5, 'field', 0)).toBe(true)
      expect(validateNumber(5, 'field', 0, 10)).toBe(true)
      expect(validateNumber(0, 'field', 0, 10)).toBe(true)
      expect(validateNumber(10, 'field', 0, 10)).toBe(true)
    })
    it('should throw ValidationError when below minimum', () => {
      expect(() => validateNumber(5, 'field', 6)).toThrow(ValidationError)
      expect(() => validateNumber(5, 'field', 6)).toThrow('field must be greater than or equal to 6')
    })
    it('should throw ValidationError when above maximum', () => {
      expect(() => validateNumber(5, 'field', undefined, 4)).toThrow(ValidationError)
      expect(() => validateNumber(5, 'field', undefined, 4)).toThrow('field must be less than or equal to 4')
    })
  })
  describe('validateArray', () => {
    it('should return true for valid arrays', () => {
      expect(validateArray([], 'field')).toBe(true)
      expect(validateArray([1, 2, 3], 'field')).toBe(true)
      expect(validateArray([1], 'field', 1)).toBe(true)
      expect(validateArray([1, 2], 'field', 1, 3)).toBe(true)
    })
    it('should throw ValidationError when array is too short', () => {
      expect(() => validateArray([], 'field', 1)).toThrow(ValidationError)
      expect(() => validateArray([], 'field', 1)).toThrow('field must contain at least 1 items')
    })
    it('should throw ValidationError when array is too long', () => {
      expect(() => validateArray([1, 2, 3], 'field', undefined, 2)).toThrow(ValidationError)
      expect(() => validateArray([1, 2, 3], 'field', undefined, 2)).toThrow('field must contain at most 2 items')
    })
  })
}) 