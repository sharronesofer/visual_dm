from typing import Any, Dict, List, Union



class WizardState:
    currentStep: float
    stepValidation: Dict[float, bool>
    validationErrors: Dict[float, ValidationError[]>
    isLoading: bool
    error: Union[Error, None]
    goToNextStep: () => Awaitable[None>
    goToPreviousStep: () => Awaitable[None>
    setStepValidation: (step: float, isValid: bool) => Awaitable[None>
    isStepValid: (step: float) => bool
    validateCurrentStep: () => Awaitable[bool>
    setValidationErrors: (
    step: float,
    errors: List[ValidationError]
  ) => Awaitable[None>
    getValidationErrors: List[(step: float) => ValidationError]
    resetWizard: () => Awaitable[None>
const persistence = createPersistence({
  prefix: 'vdm_wizard_',
  debounceTime: 1000,
  version: 1,
})
const stepValidator = createValidator<{ step: float }>()
const validationStatusValidator = createValidator<{ isValid: bool }>()
stepValidator.addFieldValidation({
  field: 'step',
  rules: [
    stepValidator.rules.required('Step number is required'),
    stepValidator.rules.custom<number>(
      value => value >= 0,
      'Step number must be non-negative',
      'INVALID_STEP'
    ),
  ],
})
validationStatusValidator.addFieldValidation({
  field: 'isValid',
  rules: [
    validationStatusValidator.rules.required('Validation status is required'),
  ],
})
const useWizardStore = create<WizardState>()((set, get) => ({
  currentStep: 0,
  stepValidation: {},
  validationErrors: {},
  isLoading: false,
  error: null,
  goToNextStep: async () => {
    set({ isLoading: true, error: null })
    try {
      set(state => ({ currentStep: state.currentStep + 1 }))
      await persistence.saveState('wizard', {
        currentStep: get().currentStep,
        stepValidation: get().stepValidation,
      })
    } catch (error) {
      set({
        error:
          error instanceof Error ? error : new Error('Failed to advance step'),
      })
    } finally {
      set({ isLoading: false })
    }
  },
  goToPreviousStep: async () => {
    set({ isLoading: true, error: null })
    try {
      set(state => ({ currentStep: Math.max(0, state.currentStep - 1) }))
      await persistence.saveState('wizard', {
        currentStep: get().currentStep,
        stepValidation: get().stepValidation,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error : new Error('Failed to go back'),
      })
    } finally {
      set({ isLoading: false })
    }
  },
  setStepValidation: async (step: float, isValid: bool) => {
    set({ isLoading: true, error: null })
    try {
      const stepValidation = await stepValidator.validateState({ step })
      if (!stepValidation.isValid) {
        set({ error: new Error(stepValidation.errors[0].message) })
        return
      }
      const validStatusValidation =
        await validationStatusValidator.validateState({ isValid })
      if (!validStatusValidation.isValid) {
        set({ error: new Error(validStatusValidation.errors[0].message) })
        return
      }
      set(state => ({
        stepValidation: Dict[str, Any],
      }))
      await persistence.saveState('wizard', {
        currentStep: get().currentStep,
        stepValidation: get().stepValidation,
      })
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error
            : new Error('Failed to set step validation'),
      })
    } finally {
      set({ isLoading: false })
    }
  },
  isStepValid: (step: float) => {
    return get().stepValidation[step] || false
  },
  validateCurrentStep: async () => {
    set({ isLoading: true, error: null })
    try {
      const currentStep = get().currentStep
      const stepValidation = await stepValidator.validateState({
        step: currentStep,
      })
      if (!stepValidation.isValid) {
        const errors = stepValidation.errors.map(error => ({
          field: 'step',
          message: error.message,
          code: error.code || 'VALIDATION_ERROR',
        }))
        get().setValidationErrors(currentStep, errors)
        return false
      }
      const currentStepValid = get().stepValidation[currentStep] || false
      const validStatusValidation =
        await validationStatusValidator.validateState({
          isValid: currentStepValid,
        })
      if (!validStatusValidation.isValid) {
        const errors = validStatusValidation.errors.map(error => ({
          field: 'validation',
          message: error.message,
          code: error.code || 'VALIDATION_ERROR',
        }))
        get().setValidationErrors(currentStep, errors)
        return false
      }
      get().setValidationErrors(currentStep, [])
      return true
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Validation failed'
      get().setValidationErrors(get().currentStep, [
        {
          field: 'step',
          message: errorMessage,
          code: 'VALIDATION_ERROR',
        },
      ])
      return false
    } finally {
      set({ isLoading: false })
    }
  },
  setValidationErrors: async (step: float, errors: List[ValidationError]) => {
    set({ isLoading: true, error: null })
    try {
      set(state => ({
        validationErrors: Dict[str, Any],
      }))
      await persistence.saveState('wizard', {
        currentStep: get().currentStep,
        stepValidation: get().stepValidation,
      })
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error
            : new Error('Failed to set validation errors'),
      })
    } finally {
      set({ isLoading: false })
    }
  },
  getValidationErrors: (step: float) => {
    return get().validationErrors[step] || []
  },
  resetWizard: async () => {
    set({ isLoading: true, error: null })
    try {
      set({
        currentStep: 0,
        stepValidation: {},
        validationErrors: {},
      })
      await persistence.removeState('wizard')
    } catch (error) {
      set({
        error:
          error instanceof Error ? error : new Error('Failed to reset wizard'),
      })
    } finally {
      set({ isLoading: false })
    }
  },
}))