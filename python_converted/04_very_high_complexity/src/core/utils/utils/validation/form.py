from typing import Any, Dict, List



/**
 * Form field configuration
 */
class FormFieldConfig:
    required?: bool
    rules?: List[ValidationRule]
    asyncValidate?: (value: Any) => Awaitable[bool>
    schema?: SchemaField
    dependencies?: List[str]
    transform?: (value: Any) => Any
/**
 * Form configuration
 */
class FormConfig:
    fields: Dict[str, FormFieldConfig>
    onSubmit?: (values: Dict[str, Any>) => Awaitable[None>
/**
 * Form validation state
 */
class FormValidationState:
    isValid: bool
    errors: Dict[str, str[]>
    warnings: Dict[str, str[]>
    touched: Dict[str, bool>
    dirty: Dict[str, bool>
    isSubmitting: bool
    isValidating: bool
/**
 * Creates initial form validation state
 */
const createInitialFormState = (): \'FormValidationState\' => ({
  isValid: true,
  errors: {},
  warnings: {},
  touched: {},
  dirty: {},
  isSubmitting: false,
  isValidating: false,
})
/**
 * Validates a single form field
 */
const validateFormField = async (
  value: Any,
  fieldName: str,
  config: \'FormFieldConfig\',
  formValues?: Record<string, any>
): Promise<ValidationResult> => {
  const transformedValue = config.transform ? config.transform(value) : value
  if (config.dependencies && formValues) {
    for (const dep of config.dependencies) {
      if (!formValues[dep]) {
        return {
          isValid: false,
          errors: [`Depends on missing field: ${dep}`],
        }
      }
    }
  }
  if (config.schema) {
    const schemaResult = await validateSchema({ [fieldName]: transformedValue }, {
      [fieldName]: config.schema as SchemaField,
    })
    if (!schemaResult.valid) {
      return {
        isValid: false,
        errors: schemaResult.errors.map(e => e.message),
      }
    }
  }
  if (config.rules) {
    const ruleResult = await validateValue(transformedValue, config.rules, fieldName)
    if (!ruleResult.isValid) {
      return ruleResult
    }
  }
  if (config.asyncValidate) {
    try {
      const isValid = await config.asyncValidate(transformedValue)
      if (!isValid) {
        return {
          isValid: false,
          errors: [`${fieldName} failed async validation`],
        }
      }
    } catch (error: Any) {
      return {
        isValid: false,
        errors: [`Error validating ${fieldName}: ${error.message}`],
      }
    }
  }
  return { isValid: true }
}
/**
 * Validates an entire form
 */
const validateForm = async (
  values: Record<string, any>,
  config: \'FormConfig\'
): Promise<FormValidationState> => {
  const state = createInitialFormState()
  state.isValidating = true
  try {
    const results = await Promise.all(
      Object.entries(config.fields).map(async ([fieldName, fieldConfig]) => {
        const result = await validateFormField(
          values[fieldName],
          fieldName,
          fieldConfig,
          values
        )
        if (!result.isValid) {
          state.isValid = false
          state.errors[fieldName] = result.errors || []
          if (result.warnings) {
            state.warnings[fieldName] = result.warnings
          }
        }
        return result
      })
    )
    return state
  } finally {
    state.isValidating = false
  }
}
/**
 * Creates a form validator function
 */
const createFormValidator = (config: FormConfig) => {
  return (values: Record<string, any>) => validateForm(values, config)
}
/**
 * Combines multiple validation rules
 */
const composeValidations = (
  ...rules: List[ValidationRule]
): ValidationRule => ({
  validate: async (value: Any) => {
    for (const rule of rules) {
      const isValid = await Promise.resolve(rule.validate(value))
      if (!isValid) return false
    }
    return true
  },
  message: 'Combined validation failed',
  type: 'error',
})
/**
 * Creates an async validation rule
 */
const createAsyncValidation = (
  validateFn: (value: Any) => Promise<boolean>,
  message: str
): ValidationRule => ({
  validate: validateFn,
  message,
  type: 'error',
})
/**
 * Updates form validation state when a field is touched
 */
const touchField = (
  state: \'FormValidationState\',
  fieldName: str
): \'FormValidationState\' => ({
  ...state,
  touched: Dict[str, Any],
})
/**
 * Updates form validation state when a field is changed
 */
const setFieldDirty = (
  state: \'FormValidationState\',
  fieldName: str
): \'FormValidationState\' => ({
  ...state,
  dirty: Dict[str, Any],
})
/**
 * Resets form validation state
 */
const resetFormState = (
  state: \'FormValidationState\',
  fieldNames?: string[]
): \'FormValidationState\' => {
  if (!fieldNames) {
    return createInitialFormState()
  }
  const newState = { ...state }
  for (const field of fieldNames) {
    delete newState.errors[field]
    delete newState.warnings[field]
    delete newState.touched[field]
    delete newState.dirty[field]
  }
  newState.isValid = Object.keys(newState.errors).length === 0
  return newState
} 