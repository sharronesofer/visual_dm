import { validationRules, validateField } from '../validationUtils';

describe('validationUtils', () => {
  describe('validationRules', () => {
    describe('minLength', () => {
      const rule = validationRules.minLength('Test Field', 3);

      it('should pass for valid length', () => {
        expect(rule.validate('valid')).toBe(true);
      });

      it('should fail for short input', () => {
        expect(rule.validate('ab')).toBe(false);
        expect(rule.message).toBe(
          'Test Field must be at least 3 characters long'
        );
      });

      it('should handle empty input', () => {
        expect(rule.validate('')).toBe(false);
        expect(rule.message).toBe(
          'Test Field must be at least 3 characters long'
        );
      });
    });

    describe('pattern', () => {
      const rule = validationRules.pattern(
        'Username',
        /^[a-zA-Z0-9]+$/,
        'Username can only contain letters and numbers'
      );

      it('should pass for valid pattern', () => {
        expect(rule.validate('validUser123')).toBe(true);
      });

      it('should fail for invalid pattern', () => {
        expect(rule.validate('invalid@user')).toBe(false);
        expect(rule.message).toBe(
          'Username can only contain letters and numbers'
        );
      });

      it('should handle empty input', () => {
        expect(rule.validate('')).toBe(false);
        expect(rule.message).toBe(
          'Username can only contain letters and numbers'
        );
      });
    });

    describe('email', () => {
      const rule = validationRules.pattern(
        'Email',
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        'Invalid email format'
      );

      it('should pass for valid email', () => {
        expect(rule.validate('test@example.com')).toBe(true);
      });

      it('should fail for invalid email', () => {
        expect(rule.validate('invalid-email')).toBe(false);
        expect(rule.message).toBe('Invalid email format');
      });

      it('should fail for empty input', () => {
        expect(rule.validate('')).toBe(false);
        expect(rule.message).toBe('Invalid email format');
      });
    });
  });

  describe('validateField', () => {
    const mockConfig = {
      required: true,
      rules: [
        validationRules.minLength('Test Field', 3),
        validationRules.pattern(
          'Test Field',
          /^[a-zA-Z]+$/,
          'Only letters allowed'
        ),
      ],
    };

    it('should pass all validations', async () => {
      const result = await validateField('valid', 'testField', mockConfig);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('should fail required validation', async () => {
      const result = await validateField('', 'testField', mockConfig);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('testField is required');
    });

    it('should fail rule validation', async () => {
      const result = await validateField('a1', 'testField', mockConfig);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Only letters allowed');
    });

    it('should handle async validation', async () => {
      const configWithAsync = {
        ...mockConfig,
        asyncValidation: async (value: string) => value !== 'taken',
      };

      const validResult = await validateField(
        'valid',
        'testField',
        configWithAsync
      );
      expect(validResult.isValid).toBe(true);

      const invalidResult = await validateField(
        'taken',
        'testField',
        configWithAsync
      );
      expect(invalidResult.isValid).toBe(false);
      expect(invalidResult.error).toBe('testField validation failed');
    });

    it('should handle optional fields', async () => {
      const optionalConfig = {
        ...mockConfig,
        required: false,
      };

      const result = await validateField('', 'testField', optionalConfig);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });
  });
});
