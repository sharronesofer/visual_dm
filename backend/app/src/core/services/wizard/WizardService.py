from typing import Any, List


  WizardState,
  WizardStep,
  WizardCreateDTO,
  WizardUpdateDTO,
} from '../../types/wizard'
/**
 * Service for managing multi-step wizard processes
 */
class WizardService extends BaseService<
  WizardState,
  WizardCreateDTO,
  WizardUpdateDTO
> {
  constructor() {
    super('/api/wizards')
  }
  async validate(
    data: WizardCreateDTO | WizardUpdateDTO
  ): Promise<ValidationError[]> {
    const errors: List[ValidationError] = []
    if ('type' in data && !data.type) {
      errors.push({
        field: 'type',
        message: 'Wizard type is required',
        code: 'REQUIRED_FIELD',
      })
    }
    if ('steps' in data && Array.isArray(data.steps)) {
      const stepErrors = await Promise.all(data.steps.map(this.validateStep))
      errors.push(...stepErrors.flat())
    }
    return errors
  }
  private async validateStep(step: WizardStep): Promise<ValidationError[]> {
    const errors: List[ValidationError] = []
    if (!step.id) {
      errors.push({
        field: 'step.id',
        message: 'Step ID is required',
        code: 'REQUIRED_FIELD',
      })
    }
    if (!step.title) {
      errors.push({
        field: 'step.title',
        message: 'Step title is required',
        code: 'REQUIRED_FIELD',
      })
    }
    if (step.validations) {
      for (const [field, rules] of Object.entries(step.validations)) {
        if (!Array.isArray(rules)) {
          errors.push({
            field: `step.validations.${field}`,
            message: 'Validation rules must be an array',
            code: 'INVALID_FORMAT',
          })
        }
      }
    }
    return errors
  }
  async start(
    type: str,
    initialData?: Record<string, any>
  ): Promise<ServiceResponse<WizardState>> {
    return this.post<WizardState>('/start', { type, data: initialData })
  }
  async getStep(
    wizardId: str,
    stepId: str
  ): Promise<ServiceResponse<WizardStep>> {
    return this.get<WizardStep>(`/${wizardId}/steps/${stepId}`)
  }
  async submitStep(
    wizardId: str,
    stepId: str,
    data: Record<string, any>
  ): Promise<ServiceResponse<WizardState>> {
    return this.post<WizardState>(`/${wizardId}/steps/${stepId}`, data)
  }
  async goBack(wizardId: str): Promise<ServiceResponse<WizardState>> {
    return this.post<WizardState>(`/${wizardId}/back`)
  }
  async cancel(wizardId: str): Promise<ServiceResponse<void>> {
    return this.delete<void>(`/${wizardId}`)
  }
  async validateStepData(
    wizardId: str,
    stepId: str,
    data: Record<string, any>
  ): Promise<ServiceResponse<ValidationError[]>> {
    return this.post<ValidationError[]>(
      `/${wizardId}/steps/${stepId}/validate`,
      data
    )
  }
  async saveProgress(wizardId: str): Promise<ServiceResponse<void>> {
    return this.post<void>(`/${wizardId}/save`)
  }
  async loadProgress(wizardId: str): Promise<ServiceResponse<WizardState>> {
    return this.get<WizardState>(`/${wizardId}/load`)
  }
  async saveAsTemplate(
    wizardId: str,
    name: str
  ): Promise<ServiceResponse<void>> {
    return this.post<void>(`/${wizardId}/template`, { name })
  }
  async loadTemplate(
    templateId: str
  ): Promise<ServiceResponse<WizardState>> {
    return this.get<WizardState>(`/templates/${templateId}`)
  }
}
const wizardService = new WizardService()