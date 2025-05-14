from typing import Any, Dict, List, Union


/**
 * Form validation utilities
 */
FormFieldValue = Union[str, float, bool, Date, None, None]
class FormValues:
    [key: Union[str]: FormFieldValue, List[FormFieldValue], Dict[str, Any>]
class FormFieldError:
    message: str
FormErrorValue = Union[FormFieldError, List[FormFieldError], { [key: str]: \'FormFieldError\' }]
class FormErrors:
    [key: str]: FormErrorValue
class FormValidationOptions:
    validateOnChange?: bool
    validateOnBlur?: bool
    validateOnSubmit?: bool
interface FormState<T extends FormValues = FormValues> {
  values: T
  errors: \'FormErrors\'
  touched: Record<keyof T, boolean>
  dirty: Record<keyof T, boolean>
  isValid: bool
  isSubmitting: bool
}
/**
 * Creates initial form state
 */
const createInitialFormState = <T extends FormValues>(initialValues: T): FormState<T> => {
  const touched = Object.keys(initialValues).reduce(
    (acc, key) => ({ ...acc, [key]: false }),
    {} as Record<keyof T, boolean>
  )
  const dirty = Object.keys(initialValues).reduce(
    (acc, key) => ({ ...acc, [key]: false }),
    {} as Record<keyof T, boolean>
  )
  return {
    values: initialValues,
    errors: {},
    touched,
    dirty,
    isValid: true,
    isSubmitting: false,
  }
}
/**
 * Converts validation errors to form errors
 */
const convertValidationResultToFormErrors = (result: ValidationResult): \'FormErrors\' => {
  const formErrors: \'FormErrors\' = {}
  for (const error of result.errors) {
    const path = error.field.split('.')
    let current = formErrors
    for (let i = 0; i < path.length - 1; i++) {
      const key = path[i]
      if (key.endsWith(']')) {
        const [arrayKey, indexStr] = key.split('[')
        const index = parseInt(indexStr.slice(0, -1))
        if (!current[arrayKey]) {
          current[arrayKey] = [] as FormFieldError[]
        }
        if (!(current[arrayKey] as FormFieldError[])[index]) {
          (current[arrayKey] as FormFieldError[])[index] = { message: '' }
        }
        current = (current[arrayKey] as FormFieldError[])[index] as {
          [key: string]: \'FormFieldError\'
        }
      } else {
        if (!current[key]) {
          current[key] = { message: '' }
        }
        current = current[key] as { [key: string]: \'FormFieldError\' }
      }
    }
    const lastKey = path[path.length - 1]
    current[lastKey] = { message: error.message }
  }
  return formErrors
}
/**
 * Creates a form validator function
 */
const createFormValidator = (schema: Schema) => {
  return async (values: FormValues): Promise<FormErrors> => {
    const result = await validate(values, schema)
    return convertValidationResultToFormErrors(result)
  }
}
/**
 * Creates a form validation handler
 */
const createFormValidationHandler = (
  schema: Schema,
  options: \'FormValidationOptions\' = {}
) => {
  const validator = createFormValidator(schema)
  const handleChange = async <T extends FormValues>(
    field: keyof T,
    value: Any,
    state: FormState<T>
  ): Promise<FormState<T>> => {
    const newValues = { ...state.values, [field]: value }
    const newDirty = { ...state.dirty, [field]: true }
    let newErrors = state.errors
    let isValid = state.isValid
    if (options.validateOnChange) {
      newErrors = await validator(newValues)
      isValid = Object.keys(newErrors).length === 0
    }
    return {
      ...state,
      values: newValues,
      errors: newErrors,
      dirty: newDirty,
      isValid,
    }
  }
  const handleBlur = async <T extends FormValues>(
    field: keyof T,
    state: FormState<T>
  ): Promise<FormState<T>> => {
    const newTouched = { ...state.touched, [field]: true }
    let newErrors = state.errors
    let isValid = state.isValid
    if (options.validateOnBlur) {
      newErrors = await validator(state.values)
      isValid = Object.keys(newErrors).length === 0
    }
    return {
      ...state,
      touched: newTouched,
      errors: newErrors,
      isValid,
    }
  }
  const handleSubmit = async <T extends FormValues>(state: FormState<T>): Promise<FormState<T>> => {
    const newTouched = Object.keys(state.values).reduce(
      (acc, key) => ({ ...acc, [key]: true }),
      {} as Record<keyof T, boolean>
    )
    const newErrors = await validator(state.values)
    const isValid = Object.keys(newErrors).length === 0
    return {
      ...state,
      touched: newTouched,
      errors: newErrors,
      isValid,
      isSubmitting: false,
    }
  }
  return {
    handleChange,
    handleBlur,
    handleSubmit,
  }
}
/**
 * Creates a form controller with validation
 */
const createFormController = <T extends FormValues>(
  initialValues: T,
  schema: Schema,
  options: \'FormValidationOptions\' = {}
) => {
  const initialState = createInitialFormState(initialValues)
  const { handleChange, handleBlur, handleSubmit } = createFormValidationHandler(schema, options)
  return {
    initialState,
    handleChange,
    handleBlur,
    handleSubmit,
  }
}