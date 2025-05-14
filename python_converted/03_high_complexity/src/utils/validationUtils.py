from typing import Any, List, Union



class FieldValidation:
    isValid: bool
    error?: str
    warning?: str
    isValidating?: bool
class ValidationRule:
    validate: Union[(value: Any) => bool, Awaitable[bool>]
    message: str
    type: Union['error', 'warning']
class FieldConfig:
    required?: bool
    rules?: List[ValidationRule]
    asyncValidation?: (value: Any) => Awaitable[bool>
const validateField = async (
  value: Any,
  fieldName: str,
  config: \'FieldConfig\'
): Promise<FieldValidation> => {
  if (config.required && (value === undefined || value === null || value === '')) {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    }
  }
  if (config.rules) {
    for (const rule of config.rules) {
      const isValid = await Promise.resolve(rule.validate(value))
      if (!isValid) {
        return {
          isValid: false,
          [rule.type]: rule.message,
        }
      }
    }
  }
  if (config.asyncValidation) {
    try {
      const isValid = await config.asyncValidation(value)
      if (!isValid) {
        return {
          isValid: false,
          error: `${fieldName} validation failed`,
        }
      }
    } catch (error) {
      return {
        isValid: false,
        error: `Error validating ${fieldName}`,
      }
    }
  }
  return { isValid: true }
}
const validationRules = {
  required: (fieldName: str): \'ValidationRule\' => ({
    validate: (value: Any) => value !== undefined && value !== null && value !== '',
    message: `${fieldName} is required`,
    type: 'error',
  }),
  minLength: (fieldName: str, length: float): \'ValidationRule\' => ({
    validate: (value: str) => value.length >= length,
    message: `${fieldName} must be at least ${length} characters long`,
    type: 'error',
  }),
  maxLength: (fieldName: str, length: float): \'ValidationRule\' => ({
    validate: (value: str) => value.length <= length,
    message: `${fieldName} must not exceed ${length} characters`,
    type: 'error',
  }),
  pattern: (fieldName: str, regex: RegExp, message?: str): \'ValidationRule\' => ({
    validate: (value: str) => regex.test(value),
    message: message || `${fieldName} format is invalid`,
    type: 'error',
  }),
  range: (fieldName: str, min: float, max: float): \'ValidationRule\' => ({
    validate: (value: float) => value >= min && value <= max,
    message: `${fieldName} must be between ${min} and ${max}`,
    type: 'error',
  }),
  custom: (
    validate: (value: Any) => boolean,
    message: str,
    type: 'error' | 'warning' = 'error'
  ): \'ValidationRule\' => ({
    validate,
    message,
    type,
  }),
}
const combineValidationResults = (results: List[ValidationResult]): ValidationResult => {
  return {
    isValid: results.every(r => r.isValid),
    errors: results.flatMap(r => r.errors),
    warnings: results.flatMap(r => r.warnings),
    incompleteFields: results.flatMap(r => r.incompleteFields),
  }
}
const formatApiError = (error: Any): ValidationResult => {
  if (error.response?.data?.errors) {
    return {
      isValid: false,
      errors: error.response.data.errors.map((e: Any) => e.message),
      warnings: [],
      incompleteFields: [],
    }
  } else if (error.message) {
    return {
      isValid: false,
      errors: [error.message],
      warnings: [],
      incompleteFields: [],
    }
  } else {
    return {
      isValid: false,
      errors: ['An unexpected error occurred'],
      warnings: [],
      incompleteFields: [],
    }
  }
}