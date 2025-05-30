from typing import Any, Dict, List



describe('FactionService', () => {
  const mockFactions: List[FactionData] = [
    {
      id: FactionType.MERCHANTS,
      name: 'Merchants',
      description: 'Trade-focused faction',
      relationships: Dict[str, Any],
      values: Dict[str, Any],
      resources: Dict[str, Any],
      standing: 50,
      tier: 2
    },
    {
      id: FactionType.WARRIORS,
      name: 'Warriors',
      description: 'Combat-focused faction',
      relationships: Dict[str, Any],
      values: Dict[str, Any],
      resources: Dict[str, Any],
      standing: 40,
      tier: 2
    }
  ]
  it('initializes and retrieves factions', () => {
    const service = new FactionService(mockFactions)
    const merchants = service.getFaction(FactionType.MERCHANTS)
    expect(merchants).toBeDefined()
    expect(merchants!.name).toBe('Merchants')
    expect(merchants!.relationships.get(FactionType.WARRIORS)).toBe(10)
  })
  it('updates relationships and enforces boundaries', () => {
    const service = new FactionService(mockFactions)
    service.updateRelationship(FactionType.MERCHANTS, FactionType.WARRIORS, 95)
    const merchants = service.getFaction(FactionType.MERCHANTS)!
    const warriors = service.getFaction(FactionType.WARRIORS)!
    expect(merchants.relationships.get(FactionType.WARRIORS)).toBe(100)
    expect(warriors.relationships.get(FactionType.MERCHANTS)).toBe(100)
    service.updateRelationship(FactionType.MERCHANTS, FactionType.WARRIORS, -300)
    expect(merchants.relationships.get(FactionType.WARRIORS)).toBe(-100)
    expect(warriors.relationships.get(FactionType.MERCHANTS)).toBe(-100)
  })
  it('updates and retrieves resources', () => {
    const service = new FactionService(mockFactions)
    service.updateResource(FactionType.MERCHANTS, 'gold', 500)
    expect(service.getResource(FactionType.MERCHANTS, 'gold')).toBe(1500)
    service.updateResource(FactionType.MERCHANTS, 'gold', -2000)
    expect(service.getResource(FactionType.MERCHANTS, 'gold')).toBe(-500)
  })
  it('serializes and deserializes faction data', () => {
    const service = new FactionService(mockFactions)
    const serialized = service.serialize()
    expect(serialized.length).toBe(2)
    for (const f of serialized) {
      for (const key of Object.values(FactionType)) {
        expect(f.relationships).toHaveProperty(key)
      }
    }
    const newService = new FactionService()
    newService.deserialize(serialized)
    expect(newService.getFaction(FactionType.MERCHANTS)).toBeDefined()
    expect(newService.getFaction(FactionType.WARRIORS)).toBeDefined()
  })
  it('throws on missing factions', () => {
    const service = new FactionService(mockFactions)
    expect(() => service.getFaction(FactionType.SCHOLARS)).not.toThrow() 
    expect(() => service.updateRelationship(FactionType.MERCHANTS, FactionType.SCHOLARS, 10)).toThrow()
    expect(() => service.updateResource(FactionType.SCHOLARS, 'gold', 10)).toThrow()
    expect(() => service.getResource(FactionType.SCHOLARS, 'gold')).toThrow()
  })
  it('getRelationships returns all relationships as a plain object', () => {
    const service = new FactionService(mockFactions)
    const rels = service.getRelationships(FactionType.MERCHANTS)
    expect(rels[FactionType.WARRIORS]).toBe(10)
    expect(rels[FactionType.NOBLES]).toBe(-20)
  })
}) 