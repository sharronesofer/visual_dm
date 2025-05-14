from typing import Any


  validateString,
  validateEmail,
  validatePhone,
  validateUrl,
  validatePassword,
  validateUsername,
  validateNumber,
  validateDate,
  validateArray,
  ValidationSchema,
  validateObject,
  combineValidationResults,
  createValidationError,
  ValidationPatterns,
} from '../validation'
describe('Validation Utilities', () => {
  describe('validateString', () => {
    it('should validate required strings', () => {
      expect(validateString('', { required: true })).toEqual({
        isValid: false,
        errors: ['Value is required'],
      })
      expect(validateString('test', { required: true })).toEqual({
        isValid: true,
      })
    })
    it('should validate string length', () => {
      expect(validateString('test', { minLength: 5 })).toEqual({
        isValid: false,
        errors: ['Value must be at least 5 characters long'],
      })
      expect(validateString('test', { maxLength: 3 })).toEqual({
        isValid: false,
        errors: ['Value must be at most 3 characters long'],
      })
      expect(validateString('test', { minLength: 3, maxLength: 5 })).toEqual({
        isValid: true,
      })
    })
    it('should validate against patterns', () => {
      expect(validateString('test', { pattern: /^[a-z]+$/ })).toEqual({
        isValid: true,
      })
      expect(validateString('Test123', { pattern: /^[a-z]+$/ })).toEqual({
        isValid: false,
        errors: ['Value does not match the required pattern'],
      })
    })
    it('should run custom validators', () => {
      const customValidator = (value: str) =>
        value === 'valid' || 'Value must be "valid"'
      expect(validateString('invalid', { customValidator })).toEqual({
        isValid: false,
        errors: ['Value must be "valid"'],
      })
      expect(validateString('valid', { customValidator })).toEqual({
        isValid: true,
      })
    })
  })
  describe('validateEmail', () => {
    it('should validate email addresses', () => {
      expect(validateEmail('test@example.com')).toEqual({
        isValid: true,
      })
      expect(validateEmail('invalid-email')).toEqual({
        isValid: false,
        errors: ['Value does not match the required pattern'],
      })
      expect(validateEmail('test@example')).toEqual({
        isValid: false,
        errors: ['Value does not match the required pattern'],
      })
    })
  })
  describe('validatePhone', () => {
    it('should validate phone numbers', () => {
      expect(validatePhone('+1234567890')).toEqual({
        isValid: true,
      })
      expect(validatePhone('123-456-7890')).toEqual({
        isValid: true,
      })
      expect(validatePhone('abc')).toEqual({
        isValid: false,
        errors: ['Value does not match the required pattern'],
      })
    })
  })
  describe('validateUrl', () => {
    it('should validate URLs', () => {
      expect(validateUrl('https:
        isValid: true,
      })
      expect(validateUrl('http:
        isValid: true,
      })
      expect(validateUrl('not-a-url')).toEqual({
        isValid: false,
        errors: ['Value does not match the required pattern'],
      })
    })
  })
  describe('validatePassword', () => {
    it('should validate passwords', () => {
      expect(validatePassword('Password123')).toEqual({
        isValid: true,
      })
      expect(validatePassword('weak')).toEqual({
        isValid: false,
        errors: ['Value does not match the required pattern'],
      })
      expect(validatePassword('onlynumbers123')).toEqual({
        isValid: false,
        errors: ['Value does not match the required pattern'],
      })
    })
  })
  describe('validateUsername', () => {
    it('should validate usernames', () => {
      expect(validateUsername('john_doe')).toEqual({
        isValid: true,
      })
      expect(validateUsername('ab')).toEqual({
        isValid: false,
        errors: ['Value does not match the required pattern'],
      })
      expect(validateUsername('very_long_username_that_exceeds_limit')).toEqual(
        {
          isValid: false,
          errors: ['Value does not match the required pattern'],
        }
      )
    })
  })
  describe('validateNumber', () => {
    it('should validate required numbers', () => {
      expect(validateNumber(undefined as any, { required: true })).toEqual({
        isValid: false,
        errors: ['Value is required'],
      })
      expect(validateNumber(123, { required: true })).toEqual({
        isValid: true,
      })
    })
    it('should validate number ranges', () => {
      expect(validateNumber(5, { min: 10 })).toEqual({
        isValid: false,
        errors: ['Value must be greater than or equal to 10'],
      })
      expect(validateNumber(15, { max: 10 })).toEqual({
        isValid: false,
        errors: ['Value must be less than or equal to 10'],
      })
      expect(validateNumber(5, { min: 1, max: 10 })).toEqual({
        isValid: true,
      })
    })
    it('should validate integers', () => {
      expect(validateNumber(1.5, { integer: true })).toEqual({
        isValid: false,
        errors: ['Value must be an integer'],
      })
      expect(validateNumber(2, { integer: true })).toEqual({
        isValid: true,
      })
    })
  })
  describe('validateDate', () => {
    it('should validate required dates', () => {
      expect(validateDate(undefined as any, { required: true })).toEqual({
        isValid: false,
        errors: ['Value is required'],
      })
      expect(validateDate(new Date(), { required: true })).toEqual({
        isValid: true,
      })
    })
    it('should validate date ranges', () => {
      const now = new Date()
      const past = new Date(now.getTime() - 1000)
      const future = new Date(now.getTime() + 1000)
      expect(validateDate(past, { min: now })).toEqual({
        isValid: false,
        errors: [`Date must be after ${now.toISOString()}`],
      })
      expect(validateDate(future, { max: now })).toEqual({
        isValid: false,
        errors: [`Date must be before ${now.toISOString()}`],
      })
      expect(validateDate(now, { min: past, max: future })).toEqual({
        isValid: true,
      })
    })
    it('should validate date formats', () => {
      expect(
        validateDate('2023-01-01', { format: ValidationPatterns.DATE_ISO })
      ).toEqual({
        isValid: true,
      })
      expect(
        validateDate('invalid-date', { format: ValidationPatterns.DATE_ISO })
      ).toEqual({
        isValid: false,
        errors: ['Date string does not match the required format'],
      })
    })
  })
  describe('validateArray', () => {
    it('should validate required arrays', () => {
      expect(validateArray(undefined as any, { required: true })).toEqual({
        isValid: false,
        errors: ['Value is required'],
      })
      expect(validateArray([], { required: true })).toEqual({
        isValid: true,
      })
    })
    it('should validate array length', () => {
      expect(validateArray([1], { minLength: 2 })).toEqual({
        isValid: false,
        errors: ['Array must contain at least 2 items'],
      })
      expect(validateArray([1, 2, 3], { maxLength: 2 })).toEqual({
        isValid: false,
        errors: ['Array must contain at most 2 items'],
      })
      expect(validateArray([1, 2], { minLength: 1, maxLength: 3 })).toEqual({
        isValid: true,
      })
    })
    it('should validate array items', () => {
      const itemValidator = (item: float) => ({
        isValid: item > 0,
        errors: item > 0 ? undefined : ['Item must be positive'],
      })
      expect(validateArray([1, -2, 3], { itemValidator })).toEqual({
        isValid: false,
        errors: ['Item 1: Item must be positive'],
      })
      expect(validateArray([1, 2, 3], { itemValidator })).toEqual({
        isValid: true,
      })
    })
  })
  describe('validateObject', () => {
    class TestObject:
    name: str
    age: float
    const schema: ValidationSchema<TestObject> = {
      name: value => validateString(value, { required: true, minLength: 2 }),
      age: value => validateNumber(value, { required: true, min: 0 }),
    }
    it('should validate required objects', () => {
      expect(
        validateObject(undefined as any, schema, { required: true })
      ).toEqual({
        isValid: false,
        errors: ['Value is required'],
      })
      expect(validateObject({} as TestObject, schema)).toEqual({
        isValid: false,
        errors: ['name: Value is required', 'age: Value is required'],
      })
    })
    it('should validate object fields', () => {
      expect(
        validateObject(
          {
            name: 'a',
            age: -1,
          } as TestObject,
          schema
        )
      ).toEqual({
        isValid: false,
        errors: [
          'name: Value must be at least 2 characters long',
          'age: Value must be greater than or equal to 0',
        ],
      })
      expect(
        validateObject(
          {
            name: 'John',
            age: 25,
          } as TestObject,
          schema
        )
      ).toEqual({
        isValid: true,
      })
    })
    it('should handle unknown fields', () => {
      expect(
        validateObject(
          {
            name: 'John',
            age: 25,
            extra: 'field',
          } as any,
          schema
        )
      ).toEqual({
        isValid: false,
        errors: ['Unknown fields: extra'],
      })
      expect(
        validateObject(
          {
            name: 'John',
            age: 25,
            extra: 'field',
          } as any,
          schema,
          { allowUnknown: true }
        )
      ).toEqual({
        isValid: true,
      })
    })
  })
  describe('combineValidationResults', () => {
    it('should combine multiple validation results', () => {
      const result1 = { isValid: true }
      const result2 = { isValid: false, errors: ['Error 1'] }
      const result3 = { isValid: false, errors: ['Error 2'] }
      expect(combineValidationResults(result1, result2, result3)).toEqual({
        isValid: false,
        errors: ['Error 1', 'Error 2'],
      })
      expect(combineValidationResults(result1)).toEqual({
        isValid: true,
      })
    })
  })
  describe('createValidationError', () => {
    it('should create a ValidationError from a validation result', () => {
      const result = {
        isValid: false,
        errors: ['Error 1', 'Error 2'],
      }
      const error = createValidationError(result)
      expect(error).toBeInstanceOf(ValidationError)
      expect(error.message).toBe('Error 1, Error 2')
      expect(error.details).toEqual(['Error 1', 'Error 2'])
    })
    it('should handle validation results without errors', () => {
      const result = {
        isValid: false,
      }
      const error = createValidationError(result)
      expect(error).toBeInstanceOf(ValidationError)
      expect(error.message).toBe('Validation failed')
      expect(error.details).toEqual([])
    })
  })
})