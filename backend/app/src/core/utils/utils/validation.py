from typing import Any, Dict, List, Union


/**
 * Validation result type
 */
class ValidationResult:
    isValid: bool
    errors?: List[str]
/**
 * Validation options for common validations
 */
class ValidationOptions:
    required?: bool
    minLength?: float
    maxLength?: float
    pattern?: RegExp
    customValidator?: Union[(value: Any) => bool, str]
/**
 * Common validation patterns
 */
const ValidationPatterns = {
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  PHONE: /^\+?[\d\s-()]{10,}$/,
  URL: /^(https?:\/\/)?([a-z0-9-]+\.)+[a-z]{2,}(\/[^\s]*)?$/i,
  UUID: /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
  PASSWORD: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/,
  USERNAME: /^[a-zA-Z0-9_-]{3,20}$/,
  IPV4: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  IPV6: /^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$/i,
  DATE_ISO: /^\d{4}-\d{2}-\d{2}$/,
  TIME_24H: /^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$/,
}
/**
 * Creates a validation error from a validation result
 */
function createValidationError(
  result: \'ValidationResult\'
): ValidationError {
  return new ValidationError(result.errors?.join(', ') || 'Validation failed', {
    details: result.errors || [],
  })
}
/**
 * Validates a string value against the provided options
 */
function validateString(
  value: str,
  options: \'ValidationOptions\' = {}
): \'ValidationResult\' {
  const errors: List[string] = []
  if (options.required && !value) {
    errors.push('Value is required')
  }
  if (!value && !options.required) {
    return { isValid: true }
  }
  if (options.minLength !== undefined && value.length < options.minLength) {
    errors.push(`Value must be at least ${options.minLength} characters long`)
  }
  if (options.maxLength !== undefined && value.length > options.maxLength) {
    errors.push(`Value must be at most ${options.maxLength} characters long`)
  }
  if (options.pattern && !options.pattern.test(value)) {
    errors.push('Value does not match the required pattern')
  }
  if (options.customValidator) {
    const result = options.customValidator(value)
    if (typeof result === 'string') {
      errors.push(result)
    } else if (!result) {
      errors.push('Value failed custom validation')
    }
  }
  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  }
}
/**
 * Validates an email address
 */
function validateEmail(
  email: str,
  options: \'ValidationOptions\' = {}
): \'ValidationResult\' {
  return validateString(email, {
    ...options,
    pattern: ValidationPatterns.EMAIL,
  })
}
/**
 * Validates a phone number
 */
function validatePhone(
  phone: str,
  options: \'ValidationOptions\' = {}
): \'ValidationResult\' {
  return validateString(phone, {
    ...options,
    pattern: ValidationPatterns.PHONE,
  })
}
/**
 * Validates a URL
 */
function validateUrl(
  url: str,
  options: \'ValidationOptions\' = {}
): \'ValidationResult\' {
  return validateString(url, {
    ...options,
    pattern: ValidationPatterns.URL,
  })
}
/**
 * Validates a password
 */
function validatePassword(
  password: str,
  options: \'ValidationOptions\' = {}
): \'ValidationResult\' {
  return validateString(password, {
    ...options,
    pattern: ValidationPatterns.PASSWORD,
  })
}
/**
 * Validates a username
 */
function validateUsername(
  username: str,
  options: \'ValidationOptions\' = {}
): \'ValidationResult\' {
  return validateString(username, {
    ...options,
    pattern: ValidationPatterns.USERNAME,
  })
}
/**
 * Validates a number value
 */
function validateNumber(
  value: float,
  options: Dict[str, Any] = {}
): \'ValidationResult\' {
  const errors: List[string] = []
  if (options.required && (value === undefined || value === null)) {
    errors.push('Value is required')
  }
  if ((value === undefined || value === null) && !options.required) {
    return { isValid: true }
  }
  if (typeof value !== 'number' || isNaN(value)) {
    errors.push('Value must be a valid number')
    return { isValid: false, errors }
  }
  if (options.integer && !Number.isInteger(value)) {
    errors.push('Value must be an integer')
  }
  if (options.min !== undefined && value < options.min) {
    errors.push(`Value must be greater than or equal to ${options.min}`)
  }
  if (options.max !== undefined && value > options.max) {
    errors.push(`Value must be less than or equal to ${options.max}`)
  }
  if (options.customValidator) {
    const result = options.customValidator(value)
    if (typeof result === 'string') {
      errors.push(result)
    } else if (!result) {
      errors.push('Value failed custom validation')
    }
  }
  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  }
}
/**
 * Validates a date value
 */
function validateDate(
  value: Date | string,
  options: Dict[str, Any] = {}
): \'ValidationResult\' {
  const errors: List[string] = []
  if (options.required && !value) {
    errors.push('Value is required')
  }
  if (!value && !options.required) {
    return { isValid: true }
  }
  let dateValue: Date
  if (typeof value === 'string') {
    if (options.format && !options.format.test(value)) {
      errors.push('Date string does not match the required format')
      return { isValid: false, errors }
    }
    dateValue = new Date(value)
  } else {
    dateValue = value
  }
  if (isNaN(dateValue.getTime())) {
    errors.push('Value must be a valid date')
    return { isValid: false, errors }
  }
  if (options.min && dateValue < options.min) {
    errors.push(`Date must be after ${options.min.toISOString()}`)
  }
  if (options.max && dateValue > options.max) {
    errors.push(`Date must be before ${options.max.toISOString()}`)
  }
  if (options.customValidator) {
    const result = options.customValidator(dateValue)
    if (typeof result === 'string') {
      errors.push(result)
    } else if (!result) {
      errors.push('Date failed custom validation')
    }
  }
  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  }
}
/**
 * Validates an array
 */
function validateArray<T>(
  value: List[T],
  options: Dict[str, Any] = {}
): \'ValidationResult\' {
  const errors: List[string] = []
  if (options.required && !value) {
    errors.push('Value is required')
  }
  if (!value && !options.required) {
    return { isValid: true }
  }
  if (!Array.isArray(value)) {
    errors.push('Value must be an array')
    return { isValid: false, errors }
  }
  if (options.minLength !== undefined && value.length < options.minLength) {
    errors.push(`Array must contain at least ${options.minLength} items`)
  }
  if (options.maxLength !== undefined && value.length > options.maxLength) {
    errors.push(`Array must contain at most ${options.maxLength} items`)
  }
  if (options.itemValidator) {
    const itemErrors = value
      .map((item, index) => {
        const result = options.itemValidator!(item)
        if (!result.isValid && result.errors) {
          return result.errors.map(error => `Item ${index}: ${error}`)
        }
        return []
      })
      .flat()
    errors.push(...itemErrors)
  }
  if (options.customValidator) {
    const result = options.customValidator(value)
    if (typeof result === 'string') {
      errors.push(result)
    } else if (!result) {
      errors.push('Array failed custom validation')
    }
  }
  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  }
}
/**
 * Validation schema type for object validation
 */
type ValidationSchema<T> = {
  [K in keyof T]: (value: T[K]) => ValidationResult
}
/**
 * Validates an object against a schema
 */
function validateObject<T extends object>(
  value: T,
  schema: ValidationSchema<T>,
  options: Dict[str, Any] = {}
): \'ValidationResult\' {
  const errors: List[string] = []
  if (options.required && !value) {
    errors.push('Value is required')
  }
  if (!value && !options.required) {
    return { isValid: true }
  }
  if (typeof value !== 'object' || value === null) {
    errors.push('Value must be an object')
    return { isValid: false, errors }
  }
  if (!options.allowUnknown) {
    const unknownFields = Object.keys(value).filter(key => !(key in schema))
    if (unknownFields.length > 0) {
      errors.push(`Unknown fields: ${unknownFields.join(', ')}`)
    }
  }
  for (const [key, validator] of Object.entries(schema) as [
    keyof T,
    (value: Any) => ValidationResult,
  ][]) {
    const fieldValue = value[key]
    const result = validator(fieldValue)
    if (!result.isValid && result.errors) {
      errors.push(
        ...result.errors.map((error: str) => `${String(key)}: ${error}`)
      )
    }
  }
  if (options.customValidator) {
    const result = options.customValidator(value)
    if (typeof result === 'string') {
      errors.push(result)
    } else if (!result) {
      errors.push('Object failed custom validation')
    }
  }
  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  }
}
/**
 * Combines multiple validation results into one
 */
function combineValidationResults(
  ...results: List[ValidationResult]
): \'ValidationResult\' {
  const errors = results
    .filter(result => !result.isValid && result.errors)
    .flatMap(result => result.errors!)
  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  }
}