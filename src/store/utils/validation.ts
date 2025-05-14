/**
 * Validation error interface
 */
export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

/**
 * Validation result interface
 */
export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

/**
 * Validation rule interface
 */
export interface ValidationRule<T> {
  validate: (value: T) => boolean | Promise<boolean>;
  message: string;
  code: string;
}

/**
 * Field validation configuration
 */
export interface FieldValidation<T> {
  field: keyof T;
  rules: ValidationRule<T[keyof T]>[];
}

/**
 * Creates a validator for store state
 */
export const createValidator = <T extends Record<string, unknown>>() => {
  const validations = new Map<keyof T, ValidationRule<T[keyof T]>[]>();

  return {
    /**
     * Add validation rules for a field
     */
    addFieldValidation: (validation: FieldValidation<T>) => {
      validations.set(validation.field, validation.rules);
    },

    /**
     * Remove validation rules for a field
     */
    removeFieldValidation: (field: keyof T) => {
      validations.delete(field);
    },

    /**
     * Validate a single field
     */
    validateField: async (
      field: keyof T,
      value: T[keyof T]
    ): Promise<ValidationResult> => {
      const rules = validations.get(field);
      if (!rules) {
        return { isValid: true, errors: [] };
      }

      const errors: ValidationError[] = [];

      for (const rule of rules) {
        const isValid = await Promise.resolve(rule.validate(value));
        if (!isValid) {
          errors.push({
            field: field as string,
            message: rule.message,
            code: rule.code,
          });
        }
      }

      return {
        isValid: errors.length === 0,
        errors,
      };
    },

    /**
     * Validate entire state
     */
    validateState: async (state: T): Promise<ValidationResult> => {
      const errors: ValidationError[] = [];

      for (const [field, rules] of validations.entries()) {
        const value = state[field];
        for (const rule of rules) {
          const isValid = await Promise.resolve(rule.validate(value));
          if (!isValid) {
            errors.push({
              field: field as string,
              message: rule.message,
              code: rule.code,
            });
          }
        }
      }

      return {
        isValid: errors.length === 0,
        errors,
      };
    },

    /**
     * Create common validation rules
     */
    rules: {
      required: (message = 'Field is required'): ValidationRule<unknown> => ({
        validate: value => value != null && value !== '',
        message,
        code: 'REQUIRED',
      }),

      minLength: (
        min: number,
        message = `Minimum length is ${min}`
      ): ValidationRule<string> => ({
        validate: value => value.length >= min,
        message,
        code: 'MIN_LENGTH',
      }),

      maxLength: (
        max: number,
        message = `Maximum length is ${max}`
      ): ValidationRule<string> => ({
        validate: value => value.length <= max,
        message,
        code: 'MAX_LENGTH',
      }),

      pattern: (
        regex: RegExp,
        message = 'Invalid format'
      ): ValidationRule<string> => ({
        validate: value => regex.test(value),
        message,
        code: 'PATTERN',
      }),

      custom: <V>(
        validate: (value: V) => boolean | Promise<boolean>,
        message: string,
        code = 'CUSTOM'
      ): ValidationRule<V> => ({
        validate,
        message,
        code,
      }),
    },
  };
};
