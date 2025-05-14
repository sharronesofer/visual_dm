import { ValidationError } from './errors';

export interface WizardState {
  id: string;
  type: string;
  currentStep: string;
  steps: WizardStep[];
  data: Record<string, any>;
  isComplete: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface WizardStep {
  id: string;
  title: string;
  description?: string;
  fields: WizardField[];
  validations?: Record<string, WizardValidationRule[]>;
  nextStep?: string;
  previousStep?: string;
  isOptional?: boolean;
  properties?: Record<string, any>;
}

export interface WizardValidation {
  isValid: boolean;
  errors: ValidationError[];
  warnings?: ValidationError[];
  suggestions?: string[];
}

export enum WizardStepType {
  FORM = 'FORM',
  SELECTION = 'SELECTION',
  CONFIRMATION = 'CONFIRMATION',
  SUMMARY = 'SUMMARY',
}

export interface WizardStepConfig {
  type: WizardStepType;
  validationRules?: Record<string, any>;
  requiredFields?: string[];
  customValidation?: (data: any) => Promise<WizardValidation>;
  onComplete?: (data: any) => Promise<void>;
}

export interface WizardValidationRule {
  type: 'required' | 'minLength' | 'maxLength' | 'pattern' | 'custom';
  value?: any;
  message: string;
}

export interface WizardField {
  id: string;
  type: 'text' | 'number' | 'select' | 'multiselect' | 'checkbox' | 'radio' | 'custom';
  label: string;
  placeholder?: string;
  defaultValue?: any;
  options?: Array<{ value: any; label: string }>;
  validations?: WizardValidationRule[];
  properties?: Record<string, any>;
}

export interface WizardCreateDTO {
  type: string;
  steps: WizardStep[];
  initialData?: Record<string, any>;
}

export type WizardUpdateDTO = Partial<WizardCreateDTO>;
