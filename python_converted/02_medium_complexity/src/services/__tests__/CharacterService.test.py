from typing import Any



  Character,
  CharacterStats,
  CharacterInventory,
  CharacterSkills,
} from '../../types/character'
describe('CharacterService', () => {
  let service: CharacterService
  let mock: MockAdapter
  beforeEach(() => {
    service = new CharacterService()
    mock = new MockAdapter(axios)
  })
  afterEach(() => {
    mock.reset()
  })
  describe('Character Operations', () => {
    const mockStats: CharacterStats = {
      strength: 10,
      dexterity: 10,
      constitution: 10,
      intelligence: 10,
      wisdom: 10,
      charisma: 10,
      points: 0,
    }
    const mockInventory: CharacterInventory = {
      id: '1',
      characterId: '1',
      items: [],
      gold: 0,
      maxSlots: 20,
      usedSlots: 0,
    }
    const mockSkills: CharacterSkills = {
      available: 0,
      learned: [],
      active: [],
    }
    const mockCharacter: Character = {
      id: '1',
      name: 'Test Character',
      class: 'Warrior',
      level: 1,
      experience: 0,
      health: 100,
      maxHealth: 100,
      mana: 100,
      maxMana: 100,
      stats: mockStats,
      inventory: mockInventory,
      skills: mockSkills,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    it('should get character by id', async () => {
      mock.onGet('/api/characters/1').reply(200, mockCharacter)
      const response = await service.getCharacter('1')
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockCharacter)
    })
    it('should create character', async () => {
      const { id, ...newCharacter } = mockCharacter
      mock.onPost('/api/characters/').reply(200, mockCharacter)
      const response = await service.createCharacter(newCharacter)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockCharacter)
    })
    it('should update character', async () => {
      const updates = { name: 'Updated Character' }
      const updatedCharacter = { ...mockCharacter, ...updates }
      mock.onPut('/api/characters/1').reply(200, updatedCharacter)
      const response = await service.updateCharacter('1', updates)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(updatedCharacter)
    })
    it('should delete character', async () => {
      mock.onDelete('/api/characters/1').reply(200)
      const response = await service.deleteCharacter('1')
      expect(response.success).toBe(true)
    })
  })
  describe('Stats Operations', () => {
    const mockStats: CharacterStats = {
      strength: 11,
      dexterity: 10,
      constitution: 10,
      intelligence: 10,
      wisdom: 10,
      charisma: 10,
      points: 4,
    }
    it('should update character stats', async () => {
      mock.onPut('/api/characters/1/stats').reply(200, mockStats)
      const response = await service.updateStats('1', mockStats)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockStats)
    })
    it('should validate stats update', async () => {
      const invalidStats = { ...mockStats, points: -1 }
      mock.onPut('/api/characters/1/stats').reply(400, {
        message: 'Invalid stats',
        code: 'VALIDATION_ERROR',
        validationErrors: [
          { field: 'points', message: 'Points cannot be negative' },
        ],
      })
      const response = await service.updateStats('1', invalidStats)
      expect(response.success).toBe(false)
      expect(response.validationErrors).toBeDefined()
      expect(response.validationErrors?.[0].field).toBe('points')
    })
  })
  describe('Inventory Operations', () => {
    const mockItem = {
      id: 'item1',
      name: 'Health Potion',
      description: 'Restores health',
      type: 'consumable',
      rarity: 'common',
      quantity: 1,
      slots: 1,
    }
    it('should add item to inventory', async () => {
      mock.onPost('/api/characters/1/inventory/items').reply(200, mockItem)
      const response = await service.addInventoryItem('1', mockItem)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockItem)
    })
    it('should remove item from inventory', async () => {
      mock.onDelete('/api/characters/1/inventory/items/item1').reply(200)
      const response = await service.removeInventoryItem('1', 'item1')
      expect(response.success).toBe(true)
    })
    it('should update item quantity', async () => {
      const updatedItem = { ...mockItem, quantity: 2 }
      mock
        .onPut('/api/characters/1/inventory/items/item1')
        .reply(200, updatedItem)
      const response = await service.updateInventoryItem('1', 'item1', {
        quantity: 2,
      })
      expect(response.success).toBe(true)
      expect(response.data).toEqual(updatedItem)
    })
  })
  describe('Skills Operations', () => {
    const mockSkill = {
      id: 'skill1',
      name: 'Fireball',
      description: 'Launches a ball of fire',
      type: 'active',
      cost: 10,
      cooldown: 5,
    }
    it('should learn new skill', async () => {
      mock.onPost('/api/characters/1/skills').reply(200, mockSkill)
      const response = await service.learnSkill('1', mockSkill)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockSkill)
    })
    it('should forget skill', async () => {
      mock.onDelete('/api/characters/1/skills/skill1').reply(200)
      const response = await service.forgetSkill('1', 'skill1')
      expect(response.success).toBe(true)
    })
    it('should set active skills', async () => {
      const activeSkills = ['skill1', 'skill2']
      mock.onPut('/api/characters/1/skills/active').reply(200, activeSkills)
      const response = await service.setActiveSkills('1', activeSkills)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(activeSkills)
    })
  })
})