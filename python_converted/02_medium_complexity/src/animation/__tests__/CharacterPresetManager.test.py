from typing import Any, Dict



  CharacterPresetManager,
  CharacterPreset,
} from '../CharacterPresetManager'
describe('CharacterPresetManager', () => {
  let manager: CharacterPresetManager
  let mockStorage: Dict[str, Any] = {}
  beforeEach(() => {
    mockStorage = {}
    global.localStorage = {
      getItem: jest.fn((key: str) => mockStorage[key] || null),
      setItem: jest.fn((key: str, value: str) => {
        mockStorage[key] = value
      }),
      removeItem: jest.fn((key: str) => {
        delete mockStorage[key]
      }),
      clear: jest.fn(() => {
        mockStorage = {}
      }),
      length: 0,
      key: jest.fn((index: float) => ''),
    }
    manager = new CharacterPresetManager()
  })
  describe('initialization', () => {
    it('should initialize with default presets when storage is empty', () => {
      const presets = manager.getAllPresets()
      expect(presets.length).toBe(8) 
      expect(presets.some(p => p.id === 'basic_male')).toBe(true)
      expect(presets.some(p => p.id === 'basic_female')).toBe(true)
    })
    it('should load existing presets from storage', () => {
      const customPreset: CharacterPreset = {
        id: 'custom_1',
        name: 'Custom Preset',
        description: 'Test preset',
        tags: ['test'],
        customization: CharacterCustomizationFactory.createBasicHumanMale(),
        createdAt: Date.now(),
        updatedAt: Date.now(),
      }
      mockStorage['character_presets'] = JSON.stringify([customPreset])
      manager = new CharacterPresetManager()
      const loadedPreset = manager.getPreset('custom_1')
      expect(loadedPreset).toEqual(customPreset)
    })
  })
  describe('savePreset', () => {
    it('should save a new preset', () => {
      const customization =
        CharacterCustomizationFactory.createBasicHumanMale()
      const preset = manager.savePreset(
        'test_1',
        'Test Preset',
        customization,
        'Test description',
        ['test']
      )
      expect(preset.id).toBe('test_1')
      expect(preset.name).toBe('Test Preset')
      expect(preset.description).toBe('Test description')
      expect(preset.tags).toEqual(['test'])
      expect(preset.customization).toEqual(customization)
      expect(preset.createdAt).toBeDefined()
      expect(preset.updatedAt).toBeDefined()
      expect(global.localStorage.setItem).toHaveBeenCalled()
    })
    it('should overwrite existing preset with same ID', () => {
      const customization1 =
        CharacterCustomizationFactory.createBasicHumanMale()
      const customization2 =
        CharacterCustomizationFactory.createBasicHumanFemale()
      manager.savePreset('test_1', 'Test 1', customization1)
      const preset2 = manager.savePreset('test_1', 'Test 2', customization2)
      expect(manager.getPreset('test_1')).toEqual(preset2)
    })
  })
  describe('updatePreset', () => {
    it('should update an existing preset', () => {
      const customization =
        CharacterCustomizationFactory.createBasicHumanMale()
      const original = manager.savePreset('test_1', 'Test', customization)
      const createdAt = original.createdAt
      const updated = manager.updatePreset('test_1', {
        name: 'Updated Test',
        description: 'Updated description',
      })
      expect(updated.name).toBe('Updated Test')
      expect(updated.description).toBe('Updated description')
      expect(updated.createdAt).toBe(createdAt)
      expect(updated.updatedAt).toBeGreaterThan(createdAt)
    })
    it('should throw error when updating non-existent preset', () => {
      expect(() => {
        manager.updatePreset('non_existent', { name: 'Test' })
      }).toThrow('Preset with ID non_existent not found')
    })
  })
  describe('deletePreset', () => {
    it('should delete an existing preset', () => {
      const customization =
        CharacterCustomizationFactory.createBasicHumanMale()
      manager.savePreset('test_1', 'Test', customization)
      const deleted = manager.deletePreset('test_1')
      expect(deleted).toBe(true)
      expect(manager.getPreset('test_1')).toBeUndefined()
    })
    it('should return false when deleting non-existent preset', () => {
      const deleted = manager.deletePreset('non_existent')
      expect(deleted).toBe(false)
    })
  })
  describe('searchPresets', () => {
    beforeEach(() => {
      manager.savePreset(
        'test_1',
        'Warrior Test',
        CharacterCustomizationFactory.createWarrior(),
        'A test warrior preset',
        ['warrior', 'test']
      )
      manager.savePreset(
        'test_2',
        'Mage Test',
        CharacterCustomizationFactory.createMage(),
        'A test mage preset',
        ['mage', 'test']
      )
    })
    it('should find presets by name', () => {
      const results = manager.searchPresets('warrior')
      expect(results.length).toBeGreaterThan(0)
      expect(results.every(p => p.name.toLowerCase().includes('warrior'))).toBe(
        true
      )
    })
    it('should find presets by description', () => {
      const results = manager.searchPresets('test warrior')
      expect(results.length).toBeGreaterThan(0)
      expect(
        results.some(p => p.description?.toLowerCase().includes('test warrior'))
      ).toBe(true)
    })
    it('should find presets by tags', () => {
      const results = manager.searchPresets('test')
      expect(results.length).toBe(2)
      expect(results.every(p => p.tags?.includes('test'))).toBe(true)
    })
  })
  describe('filterByTags', () => {
    beforeEach(() => {
      manager.savePreset(
        'test_1',
        'Warrior Test',
        CharacterCustomizationFactory.createWarrior(),
        'A test warrior preset',
        ['warrior', 'combat', 'test']
      )
      manager.savePreset(
        'test_2',
        'Mage Test',
        CharacterCustomizationFactory.createMage(),
        'A test mage preset',
        ['mage', 'magic', 'test']
      )
    })
    it('should filter presets by single tag', () => {
      const results = manager.filterByTags(['warrior'])
      expect(results.length).toBeGreaterThan(0)
      expect(results.every(p => p.tags?.includes('warrior'))).toBe(true)
    })
    it('should filter presets by multiple tags', () => {
      const results = manager.filterByTags(['test', 'combat'])
      expect(results.length).toBe(1)
      expect(results[0].tags).toContain('test')
      expect(results[0].tags).toContain('combat')
    })
    it('should handle case-insensitive tag matching', () => {
      const results = manager.filterByTags(['WARRIOR', 'Combat'])
      expect(results.length).toBeGreaterThan(0)
      expect(
        results.every(p =>
          p.tags?.some(
            tag =>
              tag.toLowerCase() === 'warrior' || tag.toLowerCase() === 'combat'
          )
        )
      ).toBe(true)
    })
  })
})