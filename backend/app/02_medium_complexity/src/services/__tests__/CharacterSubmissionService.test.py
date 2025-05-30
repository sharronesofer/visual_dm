from typing import Any, Dict



jest.mock('../ApiService')
describe('CharacterSubmissionService', () => {
  let service: CharacterSubmissionService
  let mockApiService: jest.Mocked<ApiService>
  beforeEach(() => {
    jest.clearAllMocks()
    mockApiService = {
      getInstance: jest.fn().mockReturnThis(),
      post: jest.fn(),
      get: jest.fn(),
    } as any
    (ApiService.getInstance as jest.Mock).mockReturnValue(mockApiService)
    service = CharacterSubmissionService.getInstance()
  })
  const mockValidCharacter: CharacterData = {
    name: 'Test Character',
    race: 'Human',
    class: 'Fighter',
    background: 'Soldier',
    level: 1,
    alignment: 'Lawful Good',
    attributes: Dict[str, Any],
    skills: [
      {
        name: 'Athletics',
        isProficient: true,
        hasExpertise: false,
        ability: 'strength',
      },
      {
        name: 'Intimidation',
        isProficient: true,
        hasExpertise: false,
        ability: 'charisma',
      },
      {
        name: 'Perception',
        isProficient: true,
        hasExpertise: false,
        ability: 'wisdom',
      },
      {
        name: 'Survival',
        isProficient: true,
        hasExpertise: false,
        ability: 'wisdom',
      },
    ],
    equipment: [
      { name: 'Longsword', type: 'weapon', quantity: 1 },
      { name: 'Chain Mail', type: 'armor', quantity: 1 },
    ],
    selectedFeats: [],
    availableFeats: [],
    gold: 10,
    racialFeatures: ['Versatile'],
    classFeatures: ['Fighting Style', 'Second Wind'],
    backgroundFeatures: ['Military Rank'],
    personalityTraits: ['Brave'],
    ideals: ['Honor'],
    bonds: ['Protect the weak'],
    flaws: ['Stubborn'],
  }
  describe('submitCharacter', () => {
    it('should successfully submit a valid character', async () => {
      const mockResponse = { data: Dict[str, Any], error: null }
      mockApiService.post.mockResolvedValue(mockResponse)
      const result = await service.submitCharacter(mockValidCharacter)
      expect(result).toEqual(mockResponse)
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/submit',
        expect.objectContaining({
          name: mockValidCharacter.name,
          race: mockValidCharacter.race,
          class: mockValidCharacter.class,
        })
      )
    })
    it('should return validation error for invalid character', async () => {
      const invalidCharacter = { ...mockValidCharacter, name: '' }
      const result = await service.submitCharacter(invalidCharacter)
      expect(result.error).toBeDefined()
      expect(result.error?.code).toBe('VALIDATION_ERROR')
      expect(mockApiService.post).not.toHaveBeenCalled()
    })
    it('should handle API errors', async () => {
      const mockError = {
        data: Dict[str, Any],
        error: null,
      }
      mockApiService.post.mockResolvedValue(mockError)
      const result = await service.submitCharacter(mockValidCharacter)
      expect(result).toEqual(mockError)
    })
  })
  describe('validation', () => {
    it('should validate required fields', async () => {
      const invalidCharacter = { ...mockValidCharacter, race: '' }
      const result = await service.submitCharacter(invalidCharacter)
      expect(result.error?.message).toBe('Character validation failed')
      expect(mockApiService.post).not.toHaveBeenCalled()
    })
    it('should validate attribute ranges', async () => {
      const invalidCharacter = {
        ...mockValidCharacter,
        attributes: Dict[str, Any],
      }
      const result = await service.submitCharacter(invalidCharacter)
      expect(result.error?.message).toBe('Character validation failed')
      expect(mockApiService.post).not.toHaveBeenCalled()
    })
    it('should validate skill proficiencies count', async () => {
      const invalidCharacter = {
        ...mockValidCharacter,
        skills: mockValidCharacter.skills.slice(0, 1), 
      }
      const result = await service.submitCharacter(invalidCharacter)
      expect(result.error?.message).toBe('Character validation failed')
      expect(mockApiService.post).not.toHaveBeenCalled()
    })
    it('should validate spellcasting requirements for spellcasters', async () => {
      const invalidCharacter = {
        ...mockValidCharacter,
        class: 'Wizard', 
        spellcasting: undefined, 
      }
      const result = await service.submitCharacter(invalidCharacter)
      expect(result.error?.message).toBe('Character validation failed')
      expect(mockApiService.post).not.toHaveBeenCalled()
    })
  })
  describe('getSubmissionStatus', () => {
    it('should fetch submission status', async () => {
      const mockStatus = {
        data: Dict[str, Any],
        error: null,
      }
      mockApiService.get.mockResolvedValue(mockStatus)
      const result = await service.getSubmissionStatus('123')
      expect(result).toEqual(mockStatus)
      expect(mockApiService.get).toHaveBeenCalledWith(
        '/character-builder/submission/123/status'
      )
    })
    it('should handle status check errors', async () => {
      const mockError = {
        data: Dict[str, Any],
        error: Dict[str, Any],
      }
      mockApiService.get.mockResolvedValue(mockError)
      const result = await service.getSubmissionStatus('invalid-id')
      expect(result).toEqual(mockError)
    })
  })
})