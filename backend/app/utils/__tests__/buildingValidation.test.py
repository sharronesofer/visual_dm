from typing import Any, Dict


describe('Building Validation', () => {
  describe('Base Building Validation', () => {
    it('should validate a valid building base', () => {
      const validBuilding = {
        id: '1',
        name: 'Test Building',
        type: BuildingType.INN,
        category: POICategory.SOCIAL,
        dimensions: Dict[str, Any],
        entrances: [{ x: 0, y: 0 }],
        tags: ['test'],
        minDangerLevel: 1,
        maxDangerLevel: 5
      }
      const result = validateBuildingBase(validBuilding)
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })
    it('should invalidate a building with missing required fields', () => {
      const invalidBuilding = {
        id: '1',
        type: BuildingType.INN,
        category: POICategory.SOCIAL,
        dimensions: Dict[str, Any],
        entrances: [{ x: 0, y: 0 }],
        tags: ['test'],
        minDangerLevel: 1,
        maxDangerLevel: 5
      }
      const result = validateBuildingBase(invalidBuilding as any)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Missing name')
    })
    it('should invalidate a building with invalid danger level range', () => {
      const invalidBuilding = {
        id: '1',
        name: 'Test Building',
        type: BuildingType.INN,
        category: POICategory.SOCIAL,
        dimensions: Dict[str, Any],
        entrances: [{ x: 0, y: 0 }],
        tags: ['test'],
        minDangerLevel: 5,
        maxDangerLevel: 1
      }
      const result = validateBuildingBase(invalidBuilding)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Min danger level cannot be greater than max danger level')
    })
  })
  describe('Social Building Validation', () => {
    it('should validate a valid social building', () => {
      const validSocialBuilding = {
        id: '1',
        name: 'Test Inn',
        type: BuildingType.INN,
        category: POICategory.SOCIAL as POICategory.SOCIAL,
        dimensions: Dict[str, Any],
        entrances: [{ x: 0, y: 0 }],
        tags: ['test'],
        minDangerLevel: 1,
        maxDangerLevel: 5,
        npcCapacity: 10,
        openingHours: Dict[str, Any],
        services: [SocialService.LODGING]
      }
      const result = validateSocialBuilding(validSocialBuilding)
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })
    it('should invalidate a social building with wrong category', () => {
      const invalidSocialBuilding = {
        id: '1',
        name: 'Test Inn',
        type: BuildingType.INN,
        category: POICategory.DUNGEON as POICategory.DUNGEON,
        dimensions: Dict[str, Any],
        entrances: [{ x: 0, y: 0 }],
        tags: ['test'],
        minDangerLevel: 1,
        maxDangerLevel: 5,
        npcCapacity: 10,
        openingHours: Dict[str, Any],
        services: [SocialService.LODGING]
      }
      const result = validateSocialBuilding(invalidSocialBuilding as any)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid category for social building')
    })
  })
  describe('Dungeon Structure Validation', () => {
    it('should validate a valid dungeon structure', () => {
      const validDungeon = {
        id: '1',
        name: 'Test Dungeon',
        type: BuildingType.ENEMY_LAIR,
        category: POICategory.DUNGEON as POICategory.DUNGEON,
        dimensions: Dict[str, Any],
        entrances: [{ x: 0, y: 0 }],
        tags: ['test'],
        minDangerLevel: 1,
        maxDangerLevel: 5,
        difficulty: DifficultyRating.MEDIUM,
        requiredLevel: 5,
        rewards: [RewardType.EXPERIENCE]
      }
      const result = validateDungeonStructure(validDungeon)
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })
    it('should invalidate a dungeon with invalid required level', () => {
      const invalidDungeon = {
        id: '1',
        name: 'Test Dungeon',
        type: BuildingType.ENEMY_LAIR,
        category: POICategory.DUNGEON as POICategory.DUNGEON,
        dimensions: Dict[str, Any],
        entrances: [{ x: 0, y: 0 }],
        tags: ['test'],
        minDangerLevel: 1,
        maxDangerLevel: 5,
        difficulty: DifficultyRating.MEDIUM,
        requiredLevel: 0,
        rewards: [RewardType.EXPERIENCE]
      }
      const result = validateDungeonStructure(invalidDungeon)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid required level')
    })
  })
  describe('Exploration Feature Validation', () => {
    it('should validate a valid exploration feature', () => {
      const validFeature = {
        id: '1',
        name: 'Test Ruins',
        type: BuildingType.RUINS,
        category: POICategory.EXPLORATION as POICategory.EXPLORATION,
        dimensions: Dict[str, Any],
        entrances: [{ x: 0, y: 0 }],
        tags: ['test'],
        minDangerLevel: 1,
        maxDangerLevel: 5,
        discoveryDC: 15,
        interactionType: [InteractionType.INVESTIGATE],
        seasonalAvailability: [Season.SUMMER]
      }
      const result = validateExplorationFeature(validFeature)
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })
    it('should invalidate an exploration feature with invalid discovery DC', () => {
      const invalidFeature = {
        id: '1',
        name: 'Test Ruins',
        type: BuildingType.RUINS,
        category: POICategory.EXPLORATION as POICategory.EXPLORATION,
        dimensions: Dict[str, Any],
        entrances: [{ x: 0, y: 0 }],
        tags: ['test'],
        minDangerLevel: 1,
        maxDangerLevel: 5,
        discoveryDC: 0,
        interactionType: [InteractionType.INVESTIGATE],
        seasonalAvailability: [Season.SUMMER]
      }
      const result = validateExplorationFeature(invalidFeature)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid discovery DC')
    })
  })
}) 