from typing import Any, Dict


describe('Schema Validation', () => {
  describe('validate', () => {
    it('should validate string fields', async () => {
      const schema: Schema = {
        name: Dict[str, Any],
      }
      const validResult: ValidationResult = await validate({ name: 'John' }, schema)
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validate({ name: '' }, schema)
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain('must be at least 2 characters')
    })
    it('should validate number fields', async () => {
      const schema: Schema = {
        age: Dict[str, Any],
      }
      const validResult: ValidationResult = await validate({ age: 25 }, schema)
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validate({ age: -1 }, schema)
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain('must be at least 0')
    })
    it('should validate boolean fields', async () => {
      const schema: Schema = {
        active: Dict[str, Any],
      }
      const validResult: ValidationResult = await validate({ active: true }, schema)
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validate({ active: 'true' }, schema)
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain('must be a boolean')
    })
    it('should validate date fields', async () => {
      const schema: Schema = {
        birthDate: Dict[str, Any],
      }
      const validResult: ValidationResult = await validate({ birthDate: new Date() }, schema)
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validate({ birthDate: 'not a date' }, schema)
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain('must be a valid date')
    })
    it('should validate array fields', async () => {
      const schema: Schema = {
        tags: Dict[str, Any],
        },
      }
      const validResult: ValidationResult = await validate({ tags: ['tag1', 'tag2'] }, schema)
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validate({ tags: ['a'] }, schema)
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain('must be at least 2 characters')
    })
    it('should validate nested object fields', async () => {
      const schema: Schema = {
        user: Dict[str, Any],
            age: Dict[str, Any],
          },
        },
      }
      const validResult: ValidationResult = await validate(
        {
          user: Dict[str, Any],
        },
        schema
      )
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validate(
        {
          user: Dict[str, Any],
        },
        schema
      )
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain('must be a number')
    })
    it('should validate with custom validation functions', async () => {
      const schema: Schema = {
        password: Dict[str, Any],
      }
      const validResult: ValidationResult = await validate({ password: 'Password123' }, schema)
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validate({ password: 'password' }, schema)
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain(
        'Password must contain at least one uppercase letter and one number'
      )
    })
    it('should validate with enum values', async () => {
      const schema: Schema = {
        role: Dict[str, Any],
      }
      const validResult: ValidationResult = await validate({ role: 'admin' }, schema)
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validate({ role: 'superuser' }, schema)
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain('must be one of: admin, user, guest')
    })
    it('should validate with pattern matching', async () => {
      const schema: Schema = {
        email: Dict[str, Any]$/,
          message: 'Invalid email format',
        },
      }
      const validResult: ValidationResult = await validate({ email: 'test@example.com' }, schema)
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validate({ email: 'not-an-email' }, schema)
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain('Invalid email format')
    })
  })
  describe('createValidator', () => {
    it('should create a reusable validator function', async () => {
      const schema: Schema = {
        name: Dict[str, Any],
        age: Dict[str, Any],
      }
      const validator = createValidator(schema)
      const validResult: ValidationResult = await validator({
        name: 'John',
        age: 25,
      })
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      const invalidResult: ValidationResult = await validator({
        name: 'John',
        age: 'not a number',
      })
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors[0].message).toContain('must be a number')
    })
  })
}) 