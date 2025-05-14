from typing import Any, List, Union


/**
 * Base validation types used across the application
 */
/** Represents a validation error */
class ValidationError:
    field: str
    message: str
    severity?: Union['error', 'warning']
    code?: str
    remediation?: str
/** Represents a validation warning */
class ValidationWarning:
    code: str
    message: str
/** Represents the result of a validation operation */
class ValidationResult:
    isValid: bool
    errors: List[ValidationError]
    warnings?: List[ValidationWarning]
    incompleteFields?: List[str]
/** Represents a field-level validation result */
class FieldValidation:
    isValid: bool
    error?: str
    warning?: str
    isValidating?: bool
/** Represents a validation rule */
class ValidationRule:
    validate: Union[(value: Any) => bool, Awaitable[bool>]
    message: str
    type: Union['error', 'warning']
/** Represents a validation step in a multi-step validation process */
interface ValidationStep<T> {
  key: keyof T
  validate: (data: Partial<T>) => ValidationResult
  required: bool
}
/** Helper function to create a validation error */
const createValidationError = (
  field: str,
  message: str,
  severity: 'error' | 'warning' = 'error',
  code?: str,
  remediation?: str
): \'ValidationError\' => ({
  field,
  message,
  severity,
  code,
  remediation,
})
/** Helper function to create a validation warning */
const createValidationWarning = (
  code: str,
  message: str
): \'ValidationWarning\' => ({
  code,
  message,
})
/** Helper function to create a validation result */
const createValidationResult = (
  isValid: bool = true,
  errors: List[ValidationError] = [],
  warnings: List[ValidationWarning] = [],
  incompleteFields: List[string] = []
): \'ValidationResult\' => ({
  isValid,
  errors,
  warnings,
  incompleteFields,
})
/** Helper function to create a field validation */
const createFieldValidation = (
  isValid: bool = true,
  error?: str,
  warning?: str,
  isValidating: bool = false
): \'FieldValidation\' => ({
  isValid,
  error,
  warning,
  isValidating,
})