import { ValidationResult } from './validationService';

export interface FieldValidation {
  isValid: boolean;
  error?: string;
  warning?: string;
  isValidating?: boolean;
}

export interface ValidationRule {
  validate: (value: any) => boolean | Promise<boolean>;
  message: string;
  type: 'error' | 'warning';
}

export interface FieldConfig {
  required?: boolean;
  rules?: ValidationRule[];
  asyncValidation?: (value: any) => Promise<boolean>;
}

export const validateField = async (
  value: any,
  fieldName: string,
  config: FieldConfig
): Promise<FieldValidation> => {
  // Check required fields
  if (config.required && (value === undefined || value === null || value === '')) {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    };
  }

  // Run through validation rules
  if (config.rules) {
    for (const rule of config.rules) {
      const isValid = await Promise.resolve(rule.validate(value));
      if (!isValid) {
        return {
          isValid: false,
          [rule.type]: rule.message,
        };
      }
    }
  }

  // Run async validation if provided
  if (config.asyncValidation) {
    try {
      const isValid = await config.asyncValidation(value);
      if (!isValid) {
        return {
          isValid: false,
          error: `${fieldName} validation failed`,
        };
      }
    } catch (error) {
      return {
        isValid: false,
        error: `Error validating ${fieldName}`,
      };
    }
  }

  return { isValid: true };
};

// Common validation rules
export const validationRules = {
  required: (fieldName: string): ValidationRule => ({
    validate: (value: any) => value !== undefined && value !== null && value !== '',
    message: `${fieldName} is required`,
    type: 'error',
  }),

  minLength: (fieldName: string, length: number): ValidationRule => ({
    validate: (value: string) => value.length >= length,
    message: `${fieldName} must be at least ${length} characters long`,
    type: 'error',
  }),

  maxLength: (fieldName: string, length: number): ValidationRule => ({
    validate: (value: string) => value.length <= length,
    message: `${fieldName} must not exceed ${length} characters`,
    type: 'error',
  }),

  pattern: (fieldName: string, regex: RegExp, message?: string): ValidationRule => ({
    validate: (value: string) => regex.test(value),
    message: message || `${fieldName} format is invalid`,
    type: 'error',
  }),

  range: (fieldName: string, min: number, max: number): ValidationRule => ({
    validate: (value: number) => value >= min && value <= max,
    message: `${fieldName} must be between ${min} and ${max}`,
    type: 'error',
  }),

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

// Helper to combine multiple validation results
export const combineValidationResults = (results: ValidationResult[]): ValidationResult => {
  return {
    isValid: results.every(r => r.isValid),
    errors: results.flatMap(r => r.errors),
    warnings: results.flatMap(r => r.warnings),
    incompleteFields: results.flatMap(r => r.incompleteFields),
  };
};

// Format API errors for display
export const formatApiError = (error: any): ValidationResult => {
  if (error.response?.data?.errors) {
    // Handle structured API errors
    return {
      isValid: false,
      errors: error.response.data.errors.map((e: any) => e.message),
      warnings: [],
      incompleteFields: [],
    };
  } else if (error.message) {
    // Handle generic errors
    return {
      isValid: false,
      errors: [error.message],
      warnings: [],
      incompleteFields: [],
    };
  } else {
    // Fallback error
    return {
      isValid: false,
      errors: ['An unexpected error occurred'],
      warnings: [],
      incompleteFields: [],
    };
  }
};
