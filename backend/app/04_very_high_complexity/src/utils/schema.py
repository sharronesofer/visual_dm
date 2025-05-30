from typing import Any, List, Union



/**
 * Schema validation utilities for object validation
 */
SchemaFieldType = Union['str', 'float', 'bool', 'date', 'array', 'dict']
class SchemaField:
    type: SchemaFieldType
    required?: bool
    min?: float
    max?: float
    pattern?: RegExp
    enum?: List[Any]
    message?: str
    validate?: Union[(value: Any) => bool, Awaitable[bool>]
    fields?: \'Schema\'
    items?: \'SchemaField\'
class Schema:
    [key: str]: \'SchemaField\'
class ValidationError:
    field: str
    message: str
class ValidationResult:
    valid: bool
    errors: List[ValidationError]
/**
 * Validates a value against a schema field
 */
const validateField = async (
  value: Any,
  field: \'SchemaField\',
  fieldPath: str
): Promise<ValidationError[]> => {
  const errors: List[ValidationError] = []
  if (field.required && (value === undefined || value === null)) {
    errors.push({
      field: fieldPath,
      message: field.message || `${fieldPath} is required`,
    })
    return errors
  }
  if (value === undefined || value === null) {
    return errors
  }
  switch (field.type) {
    case 'string':
      if (!isString(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be a string`,
        })
      } else {
        if (field.min !== undefined && value.length < field.min) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be at least ${field.min} characters`,
          })
        }
        if (field.max !== undefined && value.length > field.max) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be at most ${field.max} characters`,
          })
        }
        if (field.pattern && !field.pattern.test(value)) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must match pattern ${field.pattern}`,
          })
        }
        if (field.enum && !field.enum.includes(value)) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be one of: ${field.enum.join(', ')}`,
          })
        }
      }
      break
    case 'number':
      if (!isNumber(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be a number`,
        })
      } else {
        if (field.min !== undefined && value < field.min) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be at least ${field.min}`,
          })
        }
        if (field.max !== undefined && value > field.max) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be at most ${field.max}`,
          })
        }
        if (field.enum && !field.enum.includes(value)) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must be one of: ${field.enum.join(', ')}`,
          })
        }
      }
      break
    case 'boolean':
      if (!isBoolean(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be a boolean`,
        })
      }
      break
    case 'date':
      if (!isDate(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be a valid date`,
        })
      }
      break
    case 'array':
      if (!isArray(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be an array`,
        })
      } else {
        if (field.min !== undefined && value.length < field.min) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must have at least ${field.min} items`,
          })
        }
        if (field.max !== undefined && value.length > field.max) {
          errors.push({
            field: fieldPath,
            message: field.message || `${fieldPath} must have at most ${field.max} items`,
          })
        }
        if (field.items) {
          for (let i = 0; i < value.length; i++) {
            const itemErrors = await validateField(value[i], field.items, `${fieldPath}[${i}]`)
            errors.push(...itemErrors)
          }
        }
      }
      break
    case 'object':
      if (!isObject(value)) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} must be an object`,
        })
      } else if (field.fields) {
        const nestedErrors = await validateObject(value, field.fields, fieldPath)
        errors.push(...nestedErrors)
      }
      break
  }
  if (field.validate) {
    try {
      const isValid = await field.validate(value)
      if (!isValid) {
        errors.push({
          field: fieldPath,
          message: field.message || `${fieldPath} failed custom validation`,
        })
      }
    } catch (error) {
      errors.push({
        field: fieldPath,
        message: field.message || `${fieldPath} validation failed: ${error.message}`,
      })
    }
  }
  return errors
}
/**
 * Validates an object against a schema
 */
const validateObject = async (
  obj: Record<string, any>,
  schema: \'Schema\',
  parentPath = ''
): Promise<ValidationError[]> => {
  const errors: List[ValidationError] = []
  for (const [key, field] of Object.entries(schema)) {
    const fieldPath = parentPath ? `${parentPath}.${key}` : key
    const value = obj[key]
    const fieldErrors = await validateField(value, field, fieldPath)
    errors.push(...fieldErrors)
  }
  return errors
}
/**
 * Validates an object against a schema and returns a validation result
 */
const validate = async (
  obj: Record<string, any>,
  schema: \'Schema\'
): Promise<ValidationResult> => {
  const errors = await validateObject(obj, schema)
  return {
    valid: errors.length === 0,
    errors,
  }
}
/**
 * Creates a validation function for a specific schema
 */
const createValidator = (schema: Schema) => {
  return (obj: Record<string, any>) => validate(obj, schema)
}