/**
 * Schema validation utilities for object validation
 */

import { isObject, isArray, isString, isNumber, isBoolean, isDate } from './validation';

// Schema field types
export type SchemaFieldType = 'string' | 'number' | 'boolean' | 'date' | 'array' | 'object';

// Schema field definition
export interface SchemaField {
  type: SchemaFieldType;
  required?: boolean;
  min?: number;
  max?: number;
  pattern?: RegExp;
  enum?: any[];
  message?: string;
  validate?: (value: any) => boolean | Promise<boolean>;
  fields?: Schema; // For nested objects
  items?: SchemaField; // For array items
}

// Schema definition
export interface Schema {
  [key: string]: SchemaField;
}

// Validation error structure
export interface ValidationError {
  field: string;
  message: string;
}

// Validation result
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

/**
 * Validates a value against a schema field
 */
const validateField = async (
  value: any,
  field: SchemaField,
  fieldPath: string
): Promise<ValidationError[]> => {
  const errors: ValidationError[] = [];

  // Check required
  if (field.required && (value === undefined || value === null)) {
    errors.push({
      field: fieldPath,
      message: field.message || `${fieldPath} is required`,
    });
    return errors;
  }

  // Skip validation if value is undefined/null and not required
  if (value === undefined || value === null) {
    return errors;
  }

  // Type validation
  switch (field.type) {
    case 'string':
      if (!isString(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be a string`,
        });
      } else {
        if (field.min !== undefined && value.length < field.min) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be at least ${field.min} characters`,
          });
        }
        if (field.max !== undefined && value.length > field.max) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be at most ${field.max} characters`,
          });
        }
        if (field.pattern && !field.pattern.test(value)) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must match pattern ${field.pattern}`,
          });
        }
        if (field.enum && !field.enum.includes(value)) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be one of: ${field.enum.join(', ')}`,
          });
        }
      }
      break;

    case 'number':
      if (!isNumber(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be a number`,
        });
      } else {
        if (field.min !== undefined && value < field.min) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be at least ${field.min}`,
          });
        }
        if (field.max !== undefined && value > field.max) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be at most ${field.max}`,
          });
        }
        if (field.enum && !field.enum.includes(value)) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be one of: ${field.enum.join(', ')}`,
          });
        }
      }
      break;

    case 'boolean':
      if (!isBoolean(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be a boolean`,
        });
      }
      break;

    case 'date':
      if (!isDate(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be a valid date`,
        });
      }
      break;

    case 'array':
      if (!isArray(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be an array`,
        });
      } else {
        if (field.min !== undefined && value.length < field.min) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must have at least ${field.min} items`,
          });
        }
        if (field.max !== undefined && value.length > field.max) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must have at most ${field.max} items`,
          });
        }
        if (field.items) {
          for (let i = 0; i < value.length; i++) {
            const itemErrors = await validateField(value[i], field.items, `${fieldPath}[${i}]`);
            errors.push(...itemErrors);
          }
        }
      }
      break;

    case 'object':
      if (!isObject(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be an object`,
        });
      } else if (field.fields) {
        const nestedErrors = await validateObject(value, field.fields, fieldPath);
        errors.push(...nestedErrors);
      }
      break;
  }

  // Custom validation
  if (field.validate) {
    try {
      const isValid = await field.validate(value);
      if (!isValid) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} failed custom validation`,
        });
      }
    } catch (error) {
      errors.push({
        field: fieldPath,
        message: field.message || `${fieldPath} validation failed: ${error.message}`,
      });
    }
  }

  return errors;
};

/**
 * Validates an object against a schema
 */
export const validateObject = async (
  obj: Record<string, any>,
  schema: Schema,
  parentPath = ''
): Promise<ValidationError[]> => {
  const errors: ValidationError[] = [];

  // Validate each field in the schema
  for (const [key, field] of Object.entries(schema)) {
    const fieldPath = parentPath ? `${parentPath}.${key}` : key;
    const value = obj[key];
    const fieldErrors = await validateField(value, field, fieldPath);
    errors.push(...fieldErrors);
  }

  return errors;
};

/**
 * Validates an object against a schema and returns a validation result
 */
export const validate = async (
  obj: Record<string, any>,
  schema: Schema
): Promise<ValidationResult> => {
  const errors = await validateObject(obj, schema);
  return {
    valid: errors.length === 0,
    errors,
  };
};

/**
 * Creates a validation function for a specific schema
 */
export const createValidator = (schema: Schema) => {
  return (obj: Record<string, any>) => validate(obj, schema);
};
