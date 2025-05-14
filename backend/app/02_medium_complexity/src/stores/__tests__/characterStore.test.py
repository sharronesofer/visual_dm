from typing import Any, Dict, List



jest.mock('../../utils/autoSaveService')
jest.mock('../../utils/validationService')
describe('characterStore', () => {
  let mockAutoSaveService: jest.Mocked<AutoSaveService>
  let mockValidationService: jest.Mocked<ValidationService>
  const mockEquipment: List[Equipment] = [
    {
      name: 'Longsword',
      type: 'weapon',
      quantity: 1,
      description: 'A versatile sword',
      properties: ['Versatile (1d10)'],
      cost: 15,
      weight: 3,
    },
    {
      name: 'Chain Mail',
      type: 'armor',
      quantity: 1,
      description: 'Heavy armor',
      properties: ['Heavy'],
      cost: 75,
      weight: 55,
    },
  ]
  const mockCharacterData: CharacterData = {
    name: 'Test Character',
    race: 'Elf',
    class: 'Wizard',
    background: 'Sage',
    level: 1,
    attributes: Dict[str, Any],
    skills: [],
    equipment: mockEquipment,
    gold: 0,
    selectedFeats: [],
    availableFeats: [],
  }
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
    mockAutoSaveService = {
      getInstance: jest.fn().mockReturnThis(),
      configure: jest.fn(),
      saveCharacter: jest.fn(),
      getLatestSave: jest.fn(),
      getLatestValidSave: jest.fn(),
      clearSaves: jest.fn(),
    } as unknown as jest.Mocked<AutoSaveService>
    mockValidationService = {
      getInstance: jest.fn().mockReturnThis(),
      validateCharacter: jest.fn().mockReturnValue({
        isValid: true,
        errors: [],
        warnings: [],
        incompleteFields: [],
      }),
      validateField: jest.fn(),
      getFieldValidationRules: jest.fn(),
      handleApiError: jest.fn(),
    } as unknown as jest.Mocked<ValidationService>
    (AutoSaveService.getInstance as jest.Mock).mockReturnValue(
      mockAutoSaveService
    )
    (ValidationService.getInstance as jest.Mock).mockReturnValue(
      mockValidationService
    )
  })
  it('should initialize with default state', () => {
    const { result } = renderHook(() => useCharacterStore())
    expect(result.current.character).toBeDefined()
    expect(result.current.character.name).toBe('')
    expect(result.current.isDirty).toBe(false)
  })
  it('should update character and trigger autosave', () => {
    const { result } = renderHook(() => useCharacterStore())
    act(() => {
      result.current.setCharacter({ name: 'Test Character' })
    })
    expect(result.current.character.name).toBe('Test Character')
    expect(result.current.isDirty).toBe(true)
    expect(mockAutoSaveService.saveCharacter).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'Test Character' }),
      true
    )
  })
  it('should load saved character', () => {
    const savedCharacter = {
      data: mockCharacterData,
      timestamp: Date.now(),
      isValid: true,
      isAutosave: true,
    }
    mockAutoSaveService.getLatestSave.mockReturnValue(savedCharacter)
    const { result } = renderHook(() => useCharacterStore())
    act(() => {
      result.current.loadSavedCharacter()
    })
    expect(result.current.character.name).toBe('Test Character')
    expect(result.current.isDirty).toBe(false)
  })
  it('should clear saved character', () => {
    const { result } = renderHook(() => useCharacterStore())
    act(() => {
      result.current.clearSavedCharacter()
    })
    expect(mockAutoSaveService.clearSaves).toHaveBeenCalled()
    expect(result.current.character.name).toBe('')
    expect(result.current.isDirty).toBe(false)
  })
  it('should discard changes and restore latest valid save', () => {
    const validSave = {
      data: mockCharacterData,
      timestamp: Date.now(),
      isValid: true,
      isAutosave: false,
    }
    mockAutoSaveService.getLatestValidSave.mockReturnValue(validSave)
    const { result } = renderHook(() => useCharacterStore())
    act(() => {
      result.current.setCharacter({ name: 'Invalid Changes' })
      result.current.discardChanges()
    })
    expect(result.current.character.name).toBe('Test Character')
    expect(result.current.isDirty).toBe(false)
  })
  it('should handle submission with autosave', async () => {
    const { result } = renderHook(() => useCharacterStore())
    mockValidationService.validateCharacter.mockReturnValue({
      isValid: true,
      errors: [],
      warnings: [],
      incompleteFields: [],
    })
    await act(async () => {
      await result.current.submitCharacter()
    })
    expect(mockAutoSaveService.saveCharacter).toHaveBeenCalledWith(
      expect.any(Object),
      false
    )
    expect(mockAutoSaveService.clearSaves).toHaveBeenCalled()
    expect(result.current.isDirty).toBe(false)
  })
  it('should handle submission failure', async () => {
    const { result } = renderHook(() => useCharacterStore())
    mockValidationService.validateCharacter.mockReturnValue({
      isValid: false,
      errors: ['Validation failed'],
      warnings: [],
      incompleteFields: [],
    })
    await act(async () => {
      await expect(result.current.submitCharacter()).rejects.toThrow(
        'Character validation failed'
      )
    })
    expect(mockAutoSaveService.clearSaves).not.toHaveBeenCalled()
    expect(result.current.isDirty).toBe(false)
  })
})