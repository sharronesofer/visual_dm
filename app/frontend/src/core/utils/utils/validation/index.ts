import {
  ValidationResult,
  ValidationError,
  ValidationRule,
  createValidationResult,
  createValidationError,
} from '../../types/validation/base';

/**
 * Common validation rules used across the application
 */
export const validationRules = {
  /** Validates that a value is not empty */
  required: (fieldName: string): ValidationRule => ({
    validate: (value: any) =>
      value !== undefined && value !== null && value !== '',
    message: `${fieldName} is required`,
    type: 'error',
  }),

  /** Validates minimum string length */
  minLength: (fieldName: string, length: number): ValidationRule => ({
    validate: (value: string) => value.length >= length,
    message: `${fieldName} must be at least ${length} characters long`,
    type: 'error',
  }),

  /** Validates maximum string length */
  maxLength: (fieldName: string, length: number): ValidationRule => ({
    validate: (value: string) => value.length <= length,
    message: `${fieldName} must not exceed ${length} characters`,
    type: 'error',
  }),

  /** Validates string pattern */
  pattern: (
    fieldName: string,
    regex: RegExp,
    message?: string
  ): ValidationRule => ({
    validate: (value: string) => regex.test(value),
    message: message || `${fieldName} format is invalid`,
    type: 'error',
  }),

  /** Validates numeric range */
  range: (fieldName: string, min: number, max: number): ValidationRule => ({
    validate: (value: number) => value >= min && value <= max,
    message: `${fieldName} must be between ${min} and ${max}`,
    type: 'error',
  }),

  /** Creates a custom validation rule */
  custom: (
    validate: (value: any) => boolean,
    message: string,
    type: 'error' | 'warning' = 'error'
  ): ValidationRule => ({
    validate,
    message,
    type,
  }),
};

/**
 * Combines multiple validation results into a single result
 */
export const combineValidationResults = (
  results: ValidationResult[]
): ValidationResult => {
  return {
    isValid: results.every(r => r.isValid),
    errors: results.flatMap(r => r.errors),
    warnings: results.flatMap(r => r.warnings || []),
    incompleteFields: results.flatMap(r => r.incompleteFields || []),
  };
};

/**
 * Validates a value against a set of rules
 */
export const validateValue = async (
  value: any,
  rules: ValidationRule[],
  fieldName: string
): Promise<ValidationResult> => {
  const errors: ValidationError[] = [];

  for (const rule of rules) {
    const isValid = await Promise.resolve(rule.validate(value));
    if (!isValid) {
      errors.push(createValidationError(fieldName, rule.message, rule.type));
    }
  }

  return createValidationResult(errors.length === 0, errors);
};

/**
 * Validates an object against a schema of validation rules
 */
export const validateObject = async <T extends object>(
  obj: T,
  schema: Record<keyof T, ValidationRule[]>
): Promise<ValidationResult> => {
  const results = await Promise.all(
    Object.entries(schema).map(async ([field, rules]) => {
      return validateValue(
        (obj as any)[field],
        rules as ValidationRule[],
        field
      );
    })
  );

  return combineValidationResults(results);
};
