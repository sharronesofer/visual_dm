from typing import Any, List


  ValidationResult,
  ValidationError,
  ValidationRule,
  createValidationResult,
  createValidationError,
} from '../../types/validation/base'
/**
 * Common validation rules used across the application
 */
const validationRules = {
  /** Validates that a value is not empty */
  required: (fieldName: str): ValidationRule => ({
    validate: (value: Any) =>
      value !== undefined && value !== null && value !== '',
    message: `${fieldName} is required`,
    type: 'error',
  }),
  /** Validates minimum string length */
  minLength: (fieldName: str, length: float): ValidationRule => ({
    validate: (value: str) => value.length >= length,
    message: `${fieldName} must be at least ${length} characters long`,
    type: 'error',
  }),
  /** Validates maximum string length */
  maxLength: (fieldName: str, length: float): ValidationRule => ({
    validate: (value: str) => value.length <= length,
    message: `${fieldName} must not exceed ${length} characters`,
    type: 'error',
  }),
  /** Validates string pattern */
  pattern: (
    fieldName: str,
    regex: RegExp,
    message?: str
  ): ValidationRule => ({
    validate: (value: str) => regex.test(value),
    message: message || `${fieldName} format is invalid`,
    type: 'error',
  }),
  /** Validates numeric range */
  range: (fieldName: str, min: float, max: float): ValidationRule => ({
    validate: (value: float) => value >= min && value <= max,
    message: `${fieldName} must be between ${min} and ${max}`,
    type: 'error',
  }),
  /** Creates a custom validation rule */
  custom: (
    validate: (value: Any) => boolean,
    message: str,
    type: 'error' | 'warning' = 'error'
  ): ValidationRule => ({
    validate,
    message,
    type,
  }),
}
/**
 * Combines multiple validation results into a single result
 */
const combineValidationResults = (
  results: List[ValidationResult]
): ValidationResult => {
  return {
    isValid: results.every(r => r.isValid),
    errors: results.flatMap(r => r.errors),
    warnings: results.flatMap(r => r.warnings || []),
    incompleteFields: results.flatMap(r => r.incompleteFields || []),
  }
}
/**
 * Validates a value against a set of rules
 */
const validateValue = async (
  value: Any,
  rules: List[ValidationRule],
  fieldName: str
): Promise<ValidationResult> => {
  const errors: List[ValidationError] = []
  for (const rule of rules) {
    const isValid = await Promise.resolve(rule.validate(value))
    if (!isValid) {
      errors.push(createValidationError(fieldName, rule.message, rule.type))
    }
  }
  return createValidationResult(errors.length === 0, errors)
}
/**
 * Validates an object against a schema of validation rules
 */
const validateObject = async <T extends object>(
  obj: T,
  schema: Record<keyof T, ValidationRule[]>
): Promise<ValidationResult> => {
  const results = await Promise.all(
    Object.entries(schema).map(async ([field, rules]) => {
      return validateValue(
        (obj as any)[field],
        rules as ValidationRule[],
        field
      )
    })
  )
  return combineValidationResults(results)
}