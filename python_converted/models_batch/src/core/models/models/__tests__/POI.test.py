from typing import Any



describe('POI Class', () => {
  test('should create a POI with valid parameters', () => {
    const poi = new POI(
      'poi1',
      'Eiffel Tower',
      [2.2945, 48.8584],
      'landmark',
      'paris'
    )
    expect(poi.id).toBe('poi1')
    expect(poi.name).toBe('Eiffel Tower')
    expect(poi.coordinates).toEqual([2.2945, 48.8584])
    expect(poi.type).toBe('landmark')
    expect(poi.state).toBe('inactive') 
    expect(poi.regionId).toBe('paris')
  })
  test('should throw error for invalid coordinates', () => {
    expect(() => {
      new POI('poi1', 'Invalid', [200, 48], 'landmark', 'paris')
    }).toThrow('Invalid longitude value')
    expect(() => {
      new POI('poi1', 'Invalid', [20, 100], 'landmark', 'paris')
    }).toThrow('Invalid latitude value')
  })
  test('should calculate distance correctly between two points', () => {
    const eiffelTower = new POI(
      'poi1',
      'Eiffel Tower',
      [2.2945, 48.8584],
      'landmark',
      'paris'
    )
    const louvre = new POI(
      'poi2',
      'Louvre Museum',
      [2.3376, 48.8606],
      'museum',
      'paris'
    )
    const distance = eiffelTower.distanceTo(louvre)
    expect(distance).toBeGreaterThan(3100)
    expect(distance).toBeLessThan(3250)
    const notreCoords: [number, number] = [2.3499, 48.8529]
    const distanceToNotreDame = eiffelTower.distanceTo(notreCoords)
    expect(distanceToNotreDame).toBeGreaterThan(3800)
    expect(distanceToNotreDame).toBeLessThan(4100)
  })
  test('should change state correctly', () => {
    const poi = new POI(
      'poi1',
      'Eiffel Tower',
      [2.2945, 48.8584],
      'landmark',
      'paris'
    )
    expect(poi.state).toBe('inactive')
    poi.setState('active')
    expect(poi.state).toBe('active')
    poi.setState('inactive')
    expect(poi.state).toBe('inactive')
  })
  test('should return correct display info', () => {
    const poi = new POI(
      'poi1',
      'Eiffel Tower',
      [2.2945, 48.8584],
      'landmark',
      'paris',
      'inactive',
      { description: 'Famous landmark in Paris', iconUrl: 'eiffel.png' }
    )
    const displayInfo = poi.getDisplayInfo()
    expect(displayInfo.title).toBe('Eiffel Tower')
    expect(displayInfo.description).toBe('Famous landmark in Paris')
    expect(displayInfo.iconUrl).toBe('eiffel.png')
  })
  test('serialization and deserialization', () => {
    const original = new POI(
      'poi1',
      'Eiffel Tower',
      [2.2945, 48.8584],
      'landmark',
      'paris',
      'active',
      { description: 'Famous landmark' }
    )
    const json = original.toJSON()
    const restored = POI.fromJSON(json)
    expect(restored.id).toBe(original.id)
    expect(restored.name).toBe(original.name)
    expect(restored.coordinates).toEqual(original.coordinates)
    expect(restored.state).toBe(original.state)
    expect(restored.metadata).toEqual(original.metadata)
  })
})