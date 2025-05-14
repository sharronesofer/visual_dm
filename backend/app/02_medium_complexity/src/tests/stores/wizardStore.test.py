from typing import Any, Dict



jest.mock('../../stores/characterStore', () => ({
  useCharacterStore: Dict[str, Any]),
  },
}))
jest.mock('../../config/wizardSteps', () => ({
  wizardSteps: [
    {
      title: 'Step 1',
      component: jest.fn(),
    },
    {
      title: 'Step 2',
      component: jest.fn(),
    },
    {
      title: 'Step 3',
      component: jest.fn(),
    },
  ],
}))
describe('wizardStore', () => {
  beforeEach(() => {
    act(() => {
      useWizardStore.setState({
        currentStep: 0,
        stepValidation: {},
        validationErrors: {},
      })
    })
  })
  it('initializes with default state', () => {
    const { result } = renderHook(() => useWizardStore())
    expect(result.current.currentStep).toBe(0)
    expect(result.current.stepValidation).toEqual({})
    expect(result.current.validationErrors).toEqual({})
  })
  it('persists step validation state', () => {
    const { result } = renderHook(() => useWizardStore())
    act(() => {
      result.current.setStepValidation(0, true)
    })
    expect(result.current.stepValidation[0]).toBe(true)
    expect(result.current.isStepValid(0)).toBe(true)
  })
  it('persists validation errors', () => {
    const { result } = renderHook(() => useWizardStore())
    const error = { field: 'test', message: 'Test error', code: 'TEST_ERROR' }
    act(() => {
      result.current.setValidationErrors(0, [error])
    })
    expect(result.current.validationErrors[0]).toEqual([error])
  })
  it('clears validation errors when step is valid', () => {
    const { result } = renderHook(() => useWizardStore())
    const error = { field: 'test', message: 'Test error', code: 'TEST_ERROR' }
    act(() => {
      result.current.setValidationErrors(0, [error])
      result.current.setStepValidation(0, true)
    })
    expect(result.current.validationErrors[0]).toBeUndefined()
  })
  it('prevents navigation to next step when current step is invalid', () => {
    const { result } = renderHook(() => useWizardStore())
    act(() => {
      result.current.setStepValidation(0, false)
      result.current.goToNextStep()
    })
    expect(result.current.currentStep).toBe(0)
  })
  it('allows navigation when step is valid', () => {
    const { result } = renderHook(() => useWizardStore())
    act(() => {
      result.current.setStepValidation(0, true)
      result.current.goToNextStep()
    })
    expect(result.current.currentStep).toBe(1)
  })
  it('persists state after reset', () => {
    const { result } = renderHook(() => useWizardStore())
    act(() => {
      result.current.setStepValidation(0, true)
      result.current.goToNextStep()
      result.current.setStepValidation(1, true)
    })
    act(() => {
      result.current.resetWizard()
    })
    expect(result.current.currentStep).toBe(0)
    expect(result.current.stepValidation).toEqual({})
    expect(result.current.validationErrors).toEqual({})
  })
  it('maintains state between hook instances', () => {
    const { result: result1 } = renderHook(() => useWizardStore())
    act(() => {
      result1.current.setStepValidation(0, true)
      result1.current.goToNextStep()
    })
    const { result: result2 } = renderHook(() => useWizardStore())
    expect(result2.current.currentStep).toBe(1)
    expect(result2.current.stepValidation[0]).toBe(true)
  })
  it('validates steps asynchronously', async () => {
    const { result } = renderHook(() => useWizardStore())
    const mockValidate = jest.fn().mockResolvedValue(true)
    (wizardSteps[0] as any).validate = mockValidate
    await act(async () => {
      await result.current.validateCurrentStep()
    })
    expect(mockValidate).toHaveBeenCalled()
    expect(result.current.stepValidation[0]).toBe(true)
  })
  it('handles validation failures', async () => {
    const { result } = renderHook(() => useWizardStore())
    const error = { field: 'test', message: 'Test error', code: 'TEST_ERROR' }
    const mockValidate = jest.fn().mockRejectedValue(error)
    (wizardSteps[0] as any).validate = mockValidate
    await act(async () => {
      await result.current.validateCurrentStep().catch(() => {})
    })
    expect(mockValidate).toHaveBeenCalled()
    expect(result.current.validationErrors[0]).toEqual([error])
    expect(result.current.stepValidation[0]).toBe(false)
  })
})