from typing import Any, Dict


jest.mock('../../utils/validationUtils', () => ({
  validateField: jest.fn(),
}))
describe('useFormValidation', () => {
  const mockConfig: Record<string, FieldConfig> = {
    username: Dict[str, Any],
      ],
    },
    email: Dict[str, Any],
      ],
    },
  }
  beforeEach(() => {
    jest.clearAllMocks()
  })
  it('should initialize with empty validation state', () => {
    const { result } = renderHook(() => useFormValidation(mockConfig))
    expect(result.current.isValidating).toBe(false)
    expect(result.current.isDirty).toBe(false)
    expect(result.current.getFormValidation()).toEqual({
      isValid: true,
      errors: [],
      warnings: [],
      incompleteFields: [],
    })
  })
  it('should validate a single field', async () => {
    const mockValidation = { isValid: true, error: null, warning: null }
    (validateField as jest.Mock).mockResolvedValue(mockValidation)
    const { result } = renderHook(() => useFormValidation(mockConfig))
    await act(async () => {
      await result.current.validateField('username', 'testuser')
    })
    expect(validateField).toHaveBeenCalledWith(
      'testuser',
      'username',
      mockConfig.username
    )
    expect(result.current.getFieldValidation('username')).toEqual(
      mockValidation
    )
  })
  it('should validate all fields', async () => {
    const mockValues = {
      username: 'testuser',
      email: 'test@example.com',
    }
    const mockValidations = {
      username: Dict[str, Any],
      email: Dict[str, Any],
    }
    (validateField as jest.Mock).mockImplementation((value, fieldName) =>
      Promise.resolve(
        mockValidations[fieldName as keyof typeof mockValidations]
      )
    )
    const { result } = renderHook(() => useFormValidation(mockConfig))
    await act(async () => {
      await result.current.validateAllFields(mockValues)
    })
    expect(validateField).toHaveBeenCalledTimes(2)
    expect(result.current.getFormValidation().isValid).toBe(true)
  })
  it('should handle validation errors', async () => {
    const mockValidation = {
      isValid: false,
      error: 'Username must be at least 3 characters',
      warning: null,
    }
    (validateField as jest.Mock).mockResolvedValue(mockValidation)
    const { result } = renderHook(() => useFormValidation(mockConfig))
    await act(async () => {
      await result.current.validateField('username', 'te')
    })
    expect(result.current.getFormValidation()).toEqual({
      isValid: false,
      errors: ['Username must be at least 3 characters'],
      warnings: [],
      incompleteFields: ['username'],
    })
  })
  it('should handle validation warnings', async () => {
    const mockValidation = {
      isValid: true,
      error: null,
      warning: 'Weak password',
    }
    (validateField as jest.Mock).mockResolvedValue(mockValidation)
    const { result } = renderHook(() => useFormValidation(mockConfig))
    await act(async () => {
      await result.current.validateField('username', 'test')
    })
    expect(result.current.getFormValidation()).toEqual({
      isValid: true,
      errors: [],
      warnings: ['Weak password'],
      incompleteFields: [],
    })
  })
  it('should reset validation state', () => {
    const { result } = renderHook(() => useFormValidation(mockConfig))
    act(() => {
      result.current.setFieldDirty('username')
      result.current.resetValidation()
    })
    expect(result.current.isDirty).toBe(false)
    expect(result.current.getFormValidation()).toEqual({
      isValid: true,
      errors: [],
      warnings: [],
      incompleteFields: [],
    })
  })
  it('should handle missing field config gracefully', async () => {
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation()
    const { result } = renderHook(() => useFormValidation(mockConfig))
    await act(async () => {
      await result.current.validateField('nonexistent', 'value')
    })
    expect(consoleSpy).toHaveBeenCalledWith(
      'No validation config found for field: nonexistent'
    )
    consoleSpy.mockRestore()
  })
  it('should track dirty state', () => {
    const { result } = renderHook(() => useFormValidation(mockConfig))
    act(() => {
      result.current.setFieldDirty('username')
    })
    expect(result.current.isDirty).toBe(true)
  })
  it('should handle async validation', async () => {
    const asyncConfig: Record<string, FieldConfig> = {
      ...mockConfig,
      username: Dict[str, Any],
    }
    const mockAsyncValidation = {
      isValid: true,
      error: null,
      warning: null,
    }
    (validateField as jest.Mock).mockResolvedValue(mockAsyncValidation)
    const { result } = renderHook(() => useFormValidation(asyncConfig))
    await act(async () => {
      await result.current.validateField('username', 'available')
    })
    expect(validateField).toHaveBeenCalledWith(
      'available',
      'username',
      asyncConfig.username
    )
    expect(result.current.getFieldValidation('username')).toEqual(
      mockAsyncValidation
    )
  })
})