import { BaseService, ServiceResponse } from '../base';
import {
  WizardState,
  WizardStep,
  WizardCreateDTO,
  WizardUpdateDTO,
} from '../../types/wizard';
import { ValidationError } from '../../types/errors';

/**
 * Service for managing multi-step wizard processes
 */
export class WizardService extends BaseService<
  WizardState,
  WizardCreateDTO,
  WizardUpdateDTO
> {
  constructor() {
    super('/api/wizards');
  }

  // Custom validation implementation
  async validate(
    data: WizardCreateDTO | WizardUpdateDTO
  ): Promise<ValidationError[]> {
    const errors: ValidationError[] = [];

    if ('type' in data && !data.type) {
      errors.push({
        field: 'type',
        message: 'Wizard type is required',
        code: 'REQUIRED_FIELD',
      });
    }

    if ('steps' in data && Array.isArray(data.steps)) {
      const stepErrors = await Promise.all(data.steps.map(this.validateStep));
      errors.push(...stepErrors.flat());
    }

    return errors;
  }

  private async validateStep(step: WizardStep): Promise<ValidationError[]> {
    const errors: ValidationError[] = [];

    if (!step.id) {
      errors.push({
        field: 'step.id',
        message: 'Step ID is required',
        code: 'REQUIRED_FIELD',
      });
    }

    if (!step.title) {
      errors.push({
        field: 'step.title',
        message: 'Step title is required',
        code: 'REQUIRED_FIELD',
      });
    }

    if (step.validations) {
      for (const [field, rules] of Object.entries(step.validations)) {
        if (!Array.isArray(rules)) {
          errors.push({
            field: `step.validations.${field}`,
            message: 'Validation rules must be an array',
            code: 'INVALID_FORMAT',
          });
        }
      }
    }

    return errors;
  }

  // Wizard state management
  async start(
    type: string,
    initialData?: Record<string, any>
  ): Promise<ServiceResponse<WizardState>> {
    return this.post<WizardState>('/start', { type, data: initialData });
  }

  async getStep(
    wizardId: string,
    stepId: string
  ): Promise<ServiceResponse<WizardStep>> {
    return this.get<WizardStep>(`/${wizardId}/steps/${stepId}`);
  }

  async submitStep(
    wizardId: string,
    stepId: string,
    data: Record<string, any>
  ): Promise<ServiceResponse<WizardState>> {
    return this.post<WizardState>(`/${wizardId}/steps/${stepId}`, data);
  }

  async goBack(wizardId: string): Promise<ServiceResponse<WizardState>> {
    return this.post<WizardState>(`/${wizardId}/back`);
  }

  async cancel(wizardId: string): Promise<ServiceResponse<void>> {
    return this.delete<void>(`/${wizardId}`);
  }

  // Validation methods
  async validateStepData(
    wizardId: string,
    stepId: string,
    data: Record<string, any>
  ): Promise<ServiceResponse<ValidationError[]>> {
    return this.post<ValidationError[]>(
      `/${wizardId}/steps/${stepId}/validate`,
      data
    );
  }

  // Progress management
  async saveProgress(wizardId: string): Promise<ServiceResponse<void>> {
    return this.post<void>(`/${wizardId}/save`);
  }

  async loadProgress(wizardId: string): Promise<ServiceResponse<WizardState>> {
    return this.get<WizardState>(`/${wizardId}/load`);
  }

  // Template management
  async saveAsTemplate(
    wizardId: string,
    name: string
  ): Promise<ServiceResponse<void>> {
    return this.post<void>(`/${wizardId}/template`, { name });
  }

  async loadTemplate(
    templateId: string
  ): Promise<ServiceResponse<WizardState>> {
    return this.get<WizardState>(`/templates/${templateId}`);
  }
}

// Create singleton instance
export const wizardService = new WizardService();
