import { ValidationError } from '../types/errors';

/**
 * Validation result type
 */
export interface ValidationResult {
  isValid: boolean;
  errors?: string[];
}

/**
 * Validation options for common validations
 */
export interface ValidationOptions {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  customValidator?: (value: any) => boolean | string;
}

/**
 * Common validation patterns
 */
export const ValidationPatterns = {
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
};

/**
 * Creates a validation error from a validation result
 */
export function createValidationError(
  result: ValidationResult
): ValidationError {
  return new ValidationError(result.errors?.join(', ') || 'Validation failed', {
    details: result.errors || [],
  });
}

/**
 * Validates a string value against the provided options
 */
export function validateString(
  value: string,
  options: ValidationOptions = {}
): ValidationResult {
  const errors: string[] = [];

  // Check required
  if (options.required && !value) {
    errors.push('Value is required');
  }

  // Skip other validations if value is empty and not required
  if (!value && !options.required) {
    return { isValid: true };
  }

  // Check min length
  if (options.minLength !== undefined && value.length < options.minLength) {
    errors.push(`Value must be at least ${options.minLength} characters long`);
  }

  // Check max length
  if (options.maxLength !== undefined && value.length > options.maxLength) {
    errors.push(`Value must be at most ${options.maxLength} characters long`);
  }

  // Check pattern
  if (options.pattern && !options.pattern.test(value)) {
    errors.push('Value does not match the required pattern');
  }

  // Run custom validator
  if (options.customValidator) {
    const result = options.customValidator(value);
    if (typeof result === 'string') {
      errors.push(result);
    } else if (!result) {
      errors.push('Value failed custom validation');
    }
  }

  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  };
}

/**
 * Validates an email address
 */
export function validateEmail(
  email: string,
  options: ValidationOptions = {}
): ValidationResult {
  return validateString(email, {
    ...options,
    pattern: ValidationPatterns.EMAIL,
  });
}

/**
 * Validates a phone number
 */
export function validatePhone(
  phone: string,
  options: ValidationOptions = {}
): ValidationResult {
  return validateString(phone, {
    ...options,
    pattern: ValidationPatterns.PHONE,
  });
}

/**
 * Validates a URL
 */
export function validateUrl(
  url: string,
  options: ValidationOptions = {}
): ValidationResult {
  return validateString(url, {
    ...options,
    pattern: ValidationPatterns.URL,
  });
}

/**
 * Validates a password
 */
export function validatePassword(
  password: string,
  options: ValidationOptions = {}
): ValidationResult {
  return validateString(password, {
    ...options,
    pattern: ValidationPatterns.PASSWORD,
  });
}

/**
 * Validates a username
 */
export function validateUsername(
  username: string,
  options: ValidationOptions = {}
): ValidationResult {
  return validateString(username, {
    ...options,
    pattern: ValidationPatterns.USERNAME,
  });
}

/**
 * Validates a number value
 */
export function validateNumber(
  value: number,
  options: {
    required?: boolean;
    min?: number;
    max?: number;
    integer?: boolean;
    customValidator?: (value: number) => boolean | string;
  } = {}
): ValidationResult {
  const errors: string[] = [];

  // Check required
  if (options.required && (value === undefined || value === null)) {
    errors.push('Value is required');
  }

  // Skip other validations if value is undefined/null and not required
  if ((value === undefined || value === null) && !options.required) {
    return { isValid: true };
  }

  // Check if it's a valid number
  if (typeof value !== 'number' || isNaN(value)) {
    errors.push('Value must be a valid number');
    return { isValid: false, errors };
  }

  // Check integer
  if (options.integer && !Number.isInteger(value)) {
    errors.push('Value must be an integer');
  }

  // Check min
  if (options.min !== undefined && value < options.min) {
    errors.push(`Value must be greater than or equal to ${options.min}`);
  }

  // Check max
  if (options.max !== undefined && value > options.max) {
    errors.push(`Value must be less than or equal to ${options.max}`);
  }

  // Run custom validator
  if (options.customValidator) {
    const result = options.customValidator(value);
    if (typeof result === 'string') {
      errors.push(result);
    } else if (!result) {
      errors.push('Value failed custom validation');
    }
  }

  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  };
}

/**
 * Validates a date value
 */
export function validateDate(
  value: Date | string,
  options: {
    required?: boolean;
    min?: Date;
    max?: Date;
    format?: RegExp;
    customValidator?: (value: Date) => boolean | string;
  } = {}
): ValidationResult {
  const errors: string[] = [];

  // Check required
  if (options.required && !value) {
    errors.push('Value is required');
  }

  // Skip other validations if value is empty and not required
  if (!value && !options.required) {
    return { isValid: true };
  }

  // Convert string to Date if needed
  let dateValue: Date;
  if (typeof value === 'string') {
    if (options.format && !options.format.test(value)) {
      errors.push('Date string does not match the required format');
      return { isValid: false, errors };
    }
    dateValue = new Date(value);
  } else {
    dateValue = value;
  }

  // Check if it's a valid date
  if (isNaN(dateValue.getTime())) {
    errors.push('Value must be a valid date');
    return { isValid: false, errors };
  }

  // Check min date
  if (options.min && dateValue < options.min) {
    errors.push(`Date must be after ${options.min.toISOString()}`);
  }

  // Check max date
  if (options.max && dateValue > options.max) {
    errors.push(`Date must be before ${options.max.toISOString()}`);
  }

  // Run custom validator
  if (options.customValidator) {
    const result = options.customValidator(dateValue);
    if (typeof result === 'string') {
      errors.push(result);
    } else if (!result) {
      errors.push('Date failed custom validation');
    }
  }

  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  };
}

/**
 * Validates an array
 */
export function validateArray<T>(
  value: T[],
  options: {
    required?: boolean;
    minLength?: number;
    maxLength?: number;
    itemValidator?: (item: T) => ValidationResult;
    customValidator?: (value: T[]) => boolean | string;
  } = {}
): ValidationResult {
  const errors: string[] = [];

  // Check required
  if (options.required && !value) {
    errors.push('Value is required');
  }

  // Skip other validations if value is empty and not required
  if (!value && !options.required) {
    return { isValid: true };
  }

  // Check if it's an array
  if (!Array.isArray(value)) {
    errors.push('Value must be an array');
    return { isValid: false, errors };
  }

  // Check min length
  if (options.minLength !== undefined && value.length < options.minLength) {
    errors.push(`Array must contain at least ${options.minLength} items`);
  }

  // Check max length
  if (options.maxLength !== undefined && value.length > options.maxLength) {
    errors.push(`Array must contain at most ${options.maxLength} items`);
  }

  // Validate items
  if (options.itemValidator) {
    const itemErrors = value
      .map((item, index) => {
        const result = options.itemValidator!(item);
        if (!result.isValid && result.errors) {
          return result.errors.map(error => `Item ${index}: ${error}`);
        }
        return [];
      })
      .flat();

    errors.push(...itemErrors);
  }

  // Run custom validator
  if (options.customValidator) {
    const result = options.customValidator(value);
    if (typeof result === 'string') {
      errors.push(result);
    } else if (!result) {
      errors.push('Array failed custom validation');
    }
  }

  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  };
}

/**
 * Validation schema type for object validation
 */
export type ValidationSchema<T> = {
  [K in keyof T]: (value: T[K]) => ValidationResult;
};

/**
 * Validates an object against a schema
 */
export function validateObject<T extends object>(
  value: T,
  schema: ValidationSchema<T>,
  options: {
    required?: boolean;
    allowUnknown?: boolean;
    customValidator?: (value: T) => boolean | string;
  } = {}
): ValidationResult {
  const errors: string[] = [];

  // Check required
  if (options.required && !value) {
    errors.push('Value is required');
  }

  // Skip other validations if value is empty and not required
  if (!value && !options.required) {
    return { isValid: true };
  }

  // Check if it's an object
  if (typeof value !== 'object' || value === null) {
    errors.push('Value must be an object');
    return { isValid: false, errors };
  }

  // Check unknown fields
  if (!options.allowUnknown) {
    const unknownFields = Object.keys(value).filter(key => !(key in schema));
    if (unknownFields.length > 0) {
      errors.push(`Unknown fields: ${unknownFields.join(', ')}`);
    }
  }

  // Validate each field
  for (const [key, validator] of Object.entries(schema) as [
    keyof T,
    (value: any) => ValidationResult,
  ][]) {
    const fieldValue = value[key];
    const result = validator(fieldValue);
    if (!result.isValid && result.errors) {
      errors.push(
        ...result.errors.map((error: string) => `${String(key)}: ${error}`)
      );
    }
  }

  // Run custom validator
  if (options.customValidator) {
    const result = options.customValidator(value);
    if (typeof result === 'string') {
      errors.push(result);
    } else if (!result) {
      errors.push('Object failed custom validation');
    }
  }

  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  };
}

/**
 * Combines multiple validation results into one
 */
export function combineValidationResults(
  ...results: ValidationResult[]
): ValidationResult {
  const errors = results
    .filter(result => !result.isValid && result.errors)
    .flatMap(result => result.errors!);

  return {
    isValid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  };
}
