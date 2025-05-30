from typing import Any



describe('POI class', () => {
  const baseParams = {
    id: 'poi1',
    name: 'Test POI',
    coordinates: [10, 20] as [number, number],
    type: 'city' as POIType,
    regionId: 'region1',
  }
  it('constructs with required properties', () => {
    const poi = new POI(baseParams)
    expect(poi.id).toBe('poi1')
    expect(poi.name).toBe('Test POI')
    expect(poi.coordinates).toEqual([10, 20])
    expect(poi.type).toBe('city')
    expect(poi.state).toBe('active')
    expect(poi.regionId).toBe('region1')
  })
  it('accepts and sets state', () => {
    const poi = new POI({ ...baseParams, state: 'inactive' })
    expect(poi.state).toBe('inactive')
    poi.setState('active')
    expect(poi.state).toBe('active')
  })
  it('throws on invalid coordinates', () => {
    expect(
      () =>
        new POI({ ...baseParams, coordinates: [200, 0] as [number, number] })
    ).toThrow()
    expect(
      () =>
        new POI({ ...baseParams, coordinates: [0, 100] as [number, number] })
    ).toThrow()
  })
  it('calculates distanceTo correctly', () => {
    const poi = new POI(baseParams)
    const dist = poi.distanceTo([10, 21])
    expect(dist).toBeGreaterThan(110000)
    expect(dist).toBeLessThan(112000)
  })
  it('returns display info', () => {
    const poi = new POI(baseParams)
    const info = poi.getDisplayInfo()
    expect(info.title).toBe('Test POI')
    expect(info.description).toContain('city')
    expect(info.description).toContain('region1')
  })
  it('serializes and deserializes with toJSON/fromJSON', () => {
    const poi = new POI({
      id: 'poi2',
      name: 'Serializable POI',
      coordinates: [1, 2],
      type: 'town',
      regionId: 'region2',
      state: 'inactive',
    })
    const json = poi.toJSON()
    expect(json).toMatchObject({
      id: 'poi2',
      name: 'Serializable POI',
      coordinates: [1, 2],
      type: 'town',
      regionId: 'region2',
      state: 'inactive',
    })
    const deserialized = POI.fromJSON(json)
    expect(deserialized).toBeInstanceOf(POI)
    expect(deserialized.id).toBe('poi2')
    expect(deserialized.name).toBe('Serializable POI')
    expect(deserialized.coordinates).toEqual([1, 2])
    expect(deserialized.type).toBe('town')
    expect(deserialized.regionId).toBe('region2')
    expect(deserialized.state).toBe('inactive')
  })
})