/**
 * Base validation types used across the application
 */

/** Represents a validation error */
export interface ValidationError {
  field: string;
  message: string;
  severity?: 'error' | 'warning';
  code?: string;
  remediation?: string;
}

/** Represents a validation warning */
export interface ValidationWarning {
  code: string;
  message: string;
}

/** Represents the result of a validation operation */
export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings?: ValidationWarning[];
  incompleteFields?: string[];
}

/** Represents a field-level validation result */
export interface FieldValidation {
  isValid: boolean;
  error?: string;
  warning?: string;
  isValidating?: boolean;
}

/** Represents a validation rule */
export interface ValidationRule {
  validate: (value: any) => boolean | Promise<boolean>;
  message: string;
  type: 'error' | 'warning';
}

/** Represents a validation step in a multi-step validation process */
export interface ValidationStep<T> {
  key: keyof T;
  validate: (data: Partial<T>) => ValidationResult;
  required: boolean;
}

/** Helper function to create a validation error */
export const createValidationError = (
  field: string,
  message: string,
  severity: 'error' | 'warning' = 'error',
  code?: string,
  remediation?: string
): ValidationError => ({
  field,
  message,
  severity,
  code,
  remediation,
});

/** Helper function to create a validation warning */
export const createValidationWarning = (
  code: string,
  message: string
): ValidationWarning => ({
  code,
  message,
});

/** Helper function to create a validation result */
export const createValidationResult = (
  isValid: boolean = true,
  errors: ValidationError[] = [],
  warnings: ValidationWarning[] = [],
  incompleteFields: string[] = []
): ValidationResult => ({
  isValid,
  errors,
  warnings,
  incompleteFields,
});

/** Helper function to create a field validation */
export const createFieldValidation = (
  isValid: boolean = true,
  error?: string,
  warning?: string,
  isValidating: boolean = false
): FieldValidation => ({
  isValid,
  error,
  warning,
  isValidating,
});
