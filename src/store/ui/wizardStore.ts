import { create } from 'zustand';
import { ValidationError } from '../../types/errors';
import { createPersistence } from '../utils/persistence';
import { createValidator } from '../utils/validation';

interface WizardState {
  // State
  currentStep: number;
  stepValidation: Record<number, boolean>;
  validationErrors: Record<number, ValidationError[]>;
  isLoading: boolean;
  error: Error | null;

  // Actions
  goToNextStep: () => Promise<void>;
  goToPreviousStep: () => Promise<void>;
  setStepValidation: (step: number, isValid: boolean) => Promise<void>;
  isStepValid: (step: number) => boolean;
  validateCurrentStep: () => Promise<boolean>;
  setValidationErrors: (
    step: number,
    errors: ValidationError[]
  ) => Promise<void>;
  getValidationErrors: (step: number) => ValidationError[];
  resetWizard: () => Promise<void>;
}

// Create persistence handler
const persistence = createPersistence({
  prefix: 'vdm_wizard_',
  debounceTime: 1000,
  version: 1,
});

// Create separate validators for step and validation status
const stepValidator = createValidator<{ step: number }>();
const validationStatusValidator = createValidator<{ isValid: boolean }>();

// Add validation rules
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
});

validationStatusValidator.addFieldValidation({
  field: 'isValid',
  rules: [
    validationStatusValidator.rules.required('Validation status is required'),
  ],
});

export const useWizardStore = create<WizardState>()((set, get) => ({
  // Initial state
  currentStep: 0,
  stepValidation: {},
  validationErrors: {},
  isLoading: false,
  error: null,

  // Navigation
  goToNextStep: async () => {
    set({ isLoading: true, error: null });
    try {
      set(state => ({ currentStep: state.currentStep + 1 }));
      await persistence.saveState('wizard', {
        currentStep: get().currentStep,
        stepValidation: get().stepValidation,
      });
    } catch (error) {
      set({
        error:
          error instanceof Error ? error : new Error('Failed to advance step'),
      });
    } finally {
      set({ isLoading: false });
    }
  },

  goToPreviousStep: async () => {
    set({ isLoading: true, error: null });
    try {
      set(state => ({ currentStep: Math.max(0, state.currentStep - 1) }));
      await persistence.saveState('wizard', {
        currentStep: get().currentStep,
        stepValidation: get().stepValidation,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error : new Error('Failed to go back'),
      });
    } finally {
      set({ isLoading: false });
    }
  },

  // Validation
  setStepValidation: async (step: number, isValid: boolean) => {
    set({ isLoading: true, error: null });
    try {
      // Validate step number
      const stepValidation = await stepValidator.validateState({ step });
      if (!stepValidation.isValid) {
        set({ error: new Error(stepValidation.errors[0].message) });
        return;
      }

      // Validate isValid flag
      const validStatusValidation =
        await validationStatusValidator.validateState({ isValid });
      if (!validStatusValidation.isValid) {
        set({ error: new Error(validStatusValidation.errors[0].message) });
        return;
      }

      set(state => ({
        stepValidation: {
          ...state.stepValidation,
          [step]: isValid,
        },
      }));

      await persistence.saveState('wizard', {
        currentStep: get().currentStep,
        stepValidation: get().stepValidation,
      });
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error
            : new Error('Failed to set step validation'),
      });
    } finally {
      set({ isLoading: false });
    }
  },

  isStepValid: (step: number) => {
    return get().stepValidation[step] || false;
  },

  validateCurrentStep: async () => {
    set({ isLoading: true, error: null });
    try {
      const currentStep = get().currentStep;

      // Validate step number
      const stepValidation = await stepValidator.validateState({
        step: currentStep,
      });
      if (!stepValidation.isValid) {
        const errors = stepValidation.errors.map(error => ({
          field: 'step',
          message: error.message,
          code: error.code || 'VALIDATION_ERROR',
        }));
        get().setValidationErrors(currentStep, errors);
        return false;
      }

      // Validate current step's validation status
      const currentStepValid = get().stepValidation[currentStep] || false;
      const validStatusValidation =
        await validationStatusValidator.validateState({
          isValid: currentStepValid,
        });
      if (!validStatusValidation.isValid) {
        const errors = validStatusValidation.errors.map(error => ({
          field: 'validation',
          message: error.message,
          code: error.code || 'VALIDATION_ERROR',
        }));
        get().setValidationErrors(currentStep, errors);
        return false;
      }

      // Clear any existing errors
      get().setValidationErrors(currentStep, []);
      return true;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Validation failed';
      get().setValidationErrors(get().currentStep, [
        {
          field: 'step',
          message: errorMessage,
          code: 'VALIDATION_ERROR',
        },
      ]);
      return false;
    } finally {
      set({ isLoading: false });
    }
  },

  setValidationErrors: async (step: number, errors: ValidationError[]) => {
    set({ isLoading: true, error: null });
    try {
      set(state => ({
        validationErrors: {
          ...state.validationErrors,
          [step]: errors,
        },
      }));

      // Only persist validation state, not errors
      await persistence.saveState('wizard', {
        currentStep: get().currentStep,
        stepValidation: get().stepValidation,
      });
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error
            : new Error('Failed to set validation errors'),
      });
    } finally {
      set({ isLoading: false });
    }
  },

  getValidationErrors: (step: number) => {
    return get().validationErrors[step] || [];
  },

  resetWizard: async () => {
    set({ isLoading: true, error: null });
    try {
      set({
        currentStep: 0,
        stepValidation: {},
        validationErrors: {},
      });
      await persistence.removeState('wizard');
    } catch (error) {
      set({
        error:
          error instanceof Error ? error : new Error('Failed to reset wizard'),
      });
    } finally {
      set({ isLoading: false });
    }
  },
}));
