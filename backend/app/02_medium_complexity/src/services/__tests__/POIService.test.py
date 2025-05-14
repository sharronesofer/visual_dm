from typing import Any, Dict, List



describe('POIService', () => {
  let service: POIService
  let mock: MockAdapter
  beforeEach(() => {
    service = new POIService()
    mock = new MockAdapter(axios)
  })
  afterEach(() => {
    mock.reset()
  })
  describe('POI Operations', () => {
    const mockPOI: Partial<POI> = {
      id: '1',
      name: 'Test POI',
      description: 'Test Description',
      position: Dict[str, Any],
      type: POIType.LANDMARK,
      tags: ['test'],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    it('should get POI by id', async () => {
      mock.onGet('/api/pois/1').reply(200, mockPOI)
      const response = await service.getPOI('1')
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockPOI)
    })
    it('should create POI', async () => {
      const { id, ...newPOI } = mockPOI
      mock.onPost('/api/pois/').reply(200, mockPOI)
      const response = await service.createPOI(newPOI)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockPOI)
    })
    it('should update POI', async () => {
      const updates = { name: 'Updated POI' }
      const updatedPOI = { ...mockPOI, ...updates }
      mock.onPut('/api/pois/1').reply(200, updatedPOI)
      const response = await service.updatePOI('1', updates)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(updatedPOI)
    })
    it('should delete POI', async () => {
      mock.onDelete('/api/pois/1').reply(200)
      const response = await service.deletePOI('1')
      expect(response.success).toBe(true)
    })
  })
  describe('Chunk Operations', () => {
    const mockChunk: POIChunk = {
      id: '1',
      poiId: '1',
      position: Dict[str, Any],
      entities: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    it('should get chunk', async () => {
      mock.onGet('/api/pois/1/chunks/0,0').reply(200, mockChunk)
      const response = await service.getChunk('1', { x: 0, y: 0 })
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockChunk)
    })
    it('should save chunk', async () => {
      mock.onPut('/api/pois/1/chunks/0,0').reply(200, mockChunk)
      const response = await service.saveChunk('1', mockChunk)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockChunk)
    })
    it('should delete chunk', async () => {
      mock.onDelete('/api/pois/1/chunks/0,0').reply(200)
      const response = await service.deleteChunk('1', { x: 0, y: 0 })
      expect(response.success).toBe(true)
    })
  })
  describe('Entity Operations', () => {
    const mockEntity: POIEntity = {
      id: '1',
      type: 'NPC',
      position: Dict[str, Any],
      properties: {},
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    it('should add entity', async () => {
      const { id, ...newEntity } = mockEntity
      mock.onPost('/api/pois/1/chunks/0,0/entities').reply(200, mockEntity)
      const response = await service.addEntity('1', { x: 0, y: 0 }, newEntity)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockEntity)
    })
    it('should update entity', async () => {
      const updates = { properties: Dict[str, Any] }
      const updatedEntity = { ...mockEntity, ...updates }
      mock.onPut('/api/pois/1/chunks/0,0/entities/1').reply(200, updatedEntity)
      const response = await service.updateEntity(
        '1',
        { x: 0, y: 0 },
        '1',
        updates
      )
      expect(response.success).toBe(true)
      expect(response.data).toEqual(updatedEntity)
    })
    it('should delete entity', async () => {
      mock.onDelete('/api/pois/1/chunks/0,0/entities/1').reply(200)
      const response = await service.deleteEntity('1', { x: 0, y: 0 }, '1')
      expect(response.success).toBe(true)
    })
    it('should move entity between chunks', async () => {
      const fromPos = { x: 0, y: 0 }
      const toPos = { x: 1, y: 1 }
      const newPos = { x: 15, y: 15 }
      const movedEntity = { ...mockEntity, position: newPos }
      mock
        .onPost('/api/pois/1/chunks/0,0/entities/1/move')
        .reply(200, movedEntity)
      const response = await service.moveEntity(
        '1',
        '1',
        fromPos,
        toPos,
        newPos
      )
      expect(response.success).toBe(true)
      expect(response.data).toEqual(movedEntity)
    })
  })
  describe('Search Operations', () => {
    const mockPOIs: List[POI] = [
      {
        id: '1',
        name: 'Test POI 1',
        description: 'Test Description 1',
        position: Dict[str, Any],
        type: POIType.LANDMARK,
        tags: ['test'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: '2',
        name: 'Test POI 2',
        description: 'Test Description 2',
        position: Dict[str, Any],
        type: POIType.LANDMARK,
        tags: ['test'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ]
    it('should search POIs', async () => {
      mock.onGet('/api/pois/search').reply(200, mockPOIs)
      const response = await service.searchPOIs('test', { radius: 100 })
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockPOIs)
    })
    it('should get nearby POIs', async () => {
      mock.onGet('/api/pois/nearby').reply(200, mockPOIs)
      const response = await service.getNearbyPOIs({ x: 0, y: 0 }, 100)
      expect(response.success).toBe(true)
      expect(response.data).toEqual(mockPOIs)
    })
  })
})