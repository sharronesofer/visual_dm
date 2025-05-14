from typing import Any, Dict, List


/**
 * Validation error interface
 */
class ValidationError:
    field: str
    message: str
    code: str
/**
 * Validation result interface
 */
class ValidationResult:
    isValid: bool
    errors: List[ValidationError]
/**
 * Validation rule interface
 */
interface ValidationRule<T> {
  validate: (value: T) => boolean | Promise<boolean>
  message: str
  code: str
}
/**
 * Field validation configuration
 */
interface FieldValidation<T> {
  field: keyof T
  rules: ValidationRule<T[keyof T]>[]
}
/**
 * Creates a validator for store state
 */
const createValidator = <T extends Record<string, unknown>>() => {
  const validations = new Map<keyof T, ValidationRule<T[keyof T]>[]>()
  return {
    /**
     * Add validation rules for a field
     */
    addFieldValidation: (validation: FieldValidation<T>) => {
      validations.set(validation.field, validation.rules)
    },
    /**
     * Remove validation rules for a field
     */
    removeFieldValidation: (field: keyof T) => {
      validations.delete(field)
    },
    /**
     * Validate a single field
     */
    validateField: async (
      field: keyof T,
      value: T[keyof T]
    ): Promise<ValidationResult> => {
      const rules = validations.get(field)
      if (!rules) {
        return { isValid: true, errors: [] }
      }
      const errors: List[ValidationError] = []
      for (const rule of rules) {
        const isValid = await Promise.resolve(rule.validate(value))
        if (!isValid) {
          errors.push({
            field: field as string,
            message: rule.message,
            code: rule.code,
          })
        }
      }
      return {
        isValid: errors.length === 0,
        errors,
      }
    },
    /**
     * Validate entire state
     */
    validateState: async (state: T): Promise<ValidationResult> => {
      const errors: List[ValidationError] = []
      for (const [field, rules] of validations.entries()) {
        const value = state[field]
        for (const rule of rules) {
          const isValid = await Promise.resolve(rule.validate(value))
          if (!isValid) {
            errors.push({
              field: field as string,
              message: rule.message,
              code: rule.code,
            })
          }
        }
      }
      return {
        isValid: errors.length === 0,
        errors,
      }
    },
    /**
     * Create common validation rules
     */
    rules: Dict[str, Any]),
      minLength: (
        min: float,
        message = `Minimum length is ${min}`
      ): ValidationRule<string> => ({
        validate: value => value.length >= min,
        message,
        code: 'MIN_LENGTH',
      }),
      maxLength: (
        max: float,
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
        message: str,
        code = 'CUSTOM'
      ): ValidationRule<V> => ({
        validate,
        message,
        code,
      }),
    },
  }
}