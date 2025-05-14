import { ValidationResult, ValidationError, ValidationRule } from '../../types/validation/base';
import { Schema, SchemaField, validate as validateSchema } from '../../../utils/schema';
import { validateValue } from './index';

/**
 * Form field configuration
 */
export interface FormFieldConfig {
  required?: boolean;
  rules?: ValidationRule[];
  asyncValidate?: (value: any) => Promise<boolean>;
  schema?: SchemaField; // For nested object validation
  dependencies?: string[]; // Fields that this field depends on
  transform?: (value: any) => any; // Transform value before validation
}

/**
 * Form configuration
 */
export interface FormConfig {
  fields: Record<string, FormFieldConfig>;
  onSubmit?: (values: Record<string, any>) => Promise<void>;
}

/**
 * Form validation state
 */
export interface FormValidationState {
  isValid: boolean;
  errors: Record<string, string[]>;
  warnings: Record<string, string[]>;
  touched: Record<string, boolean>;
  dirty: Record<string, boolean>;
  isSubmitting: boolean;
  isValidating: boolean;
}

/**
 * Creates initial form validation state
 */
export const createInitialFormState = (): FormValidationState => ({
  isValid: true,
  errors: {},
  warnings: {},
  touched: {},
  dirty: {},
  isSubmitting: false,
  isValidating: false,
});

/**
 * Validates a single form field
 */
export const validateFormField = async (
  value: any,
  fieldName: string,
  config: FormFieldConfig,
  formValues?: Record<string, any>
): Promise<ValidationResult> => {
  // Transform value if needed
  const transformedValue = config.transform ? config.transform(value) : value;

  // Check dependencies
  if (config.dependencies && formValues) {
    for (const dep of config.dependencies) {
      if (!formValues[dep]) {
        return {
          isValid: false,
          errors: [`Depends on missing field: ${dep}`],
        };
      }
    }
  }

  // Validate against schema if provided
  if (config.schema) {
    const schemaResult = await validateSchema({ [fieldName]: transformedValue }, {
      [fieldName]: config.schema as SchemaField,
    });
    if (!schemaResult.valid) {
      return {
        isValid: false,
        errors: schemaResult.errors.map(e => e.message),
      };
    }
  }

  // Run through validation rules
  if (config.rules) {
    const ruleResult = await validateValue(transformedValue, config.rules, fieldName);
    if (!ruleResult.isValid) {
      return ruleResult;
    }
  }

  // Run async validation if provided
  if (config.asyncValidate) {
    try {
      const isValid = await config.asyncValidate(transformedValue);
      if (!isValid) {
        return {
          isValid: false,
          errors: [`${fieldName} failed async validation`],
        };
      }
    } catch (error: any) {
      return {
        isValid: false,
        errors: [`Error validating ${fieldName}: ${error.message}`],
      };
    }
  }

  return { isValid: true };
};

/**
 * Validates an entire form
 */
export const validateForm = async (
  values: Record<string, any>,
  config: FormConfig
): Promise<FormValidationState> => {
  const state = createInitialFormState();
  state.isValidating = true;

  try {
    const results = await Promise.all(
      Object.entries(config.fields).map(async ([fieldName, fieldConfig]) => {
        const result = await validateFormField(
          values[fieldName],
          fieldName,
          fieldConfig,
          values
        );

        if (!result.isValid) {
          state.isValid = false;
          state.errors[fieldName] = result.errors || [];
          if (result.warnings) {
            state.warnings[fieldName] = result.warnings;
          }
        }

        return result;
      })
    );

    return state;
  } finally {
    state.isValidating = false;
  }
};

/**
 * Creates a form validator function
 */
export const createFormValidator = (config: FormConfig) => {
  return (values: Record<string, any>) => validateForm(values, config);
};

/**
 * Combines multiple validation rules
 */
export const composeValidations = (
  ...rules: ValidationRule[]
): ValidationRule => ({
  validate: async (value: any) => {
    for (const rule of rules) {
      const isValid = await Promise.resolve(rule.validate(value));
      if (!isValid) return false;
    }
    return true;
  },
  message: 'Combined validation failed',
  type: 'error',
});

/**
 * Creates an async validation rule
 */
export const createAsyncValidation = (
  validateFn: (value: any) => Promise<boolean>,
  message: string
): ValidationRule => ({
  validate: validateFn,
  message,
  type: 'error',
});

/**
 * Updates form validation state when a field is touched
 */
export const touchField = (
  state: FormValidationState,
  fieldName: string
): FormValidationState => ({
  ...state,
  touched: {
    ...state.touched,
    [fieldName]: true,
  },
});

/**
 * Updates form validation state when a field is changed
 */
export const setFieldDirty = (
  state: FormValidationState,
  fieldName: string
): FormValidationState => ({
  ...state,
  dirty: {
    ...state.dirty,
    [fieldName]: true,
  },
});

/**
 * Resets form validation state
 */
export const resetFormState = (
  state: FormValidationState,
  fieldNames?: string[]
): FormValidationState => {
  if (!fieldNames) {
    return createInitialFormState();
  }

  const newState = { ...state };
  for (const field of fieldNames) {
    delete newState.errors[field];
    delete newState.warnings[field];
    delete newState.touched[field];
    delete newState.dirty[field];
  }

  newState.isValid = Object.keys(newState.errors).length === 0;
  return newState;
}; 