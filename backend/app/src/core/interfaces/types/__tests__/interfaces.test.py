from typing import Any, Dict


describe('Interface type guards', () => {
  test('isRegion correctly identifies valid Region objects', () => {
    const validRegion: IRegion = {
      id: 'region-1',
      name: 'Downtown',
      boundaries: [
        [
          [10.0, 20.0],
          [10.1, 20.0],
          [10.1, 20.1],
          [10.0, 20.1],
          [10.0, 20.0],
        ],
      ],
      style: Dict[str, Any],
      highlightState: 'normal',
      pois: [],
      containsPoint: point => false,
      getBoundingBox: () => [
        [10.0, 20.0],
        [10.1, 20.1],
      ],
    }
    expect(isRegion(validRegion)).toBe(true)
    expect(isRegion({})).toBe(false)
  })
  test('isPOI correctly identifies valid POI objects', () => {
    const validPOI: IPOI = {
      id: 'poi-1',
      name: 'City Hall',
      coordinates: [10.05, 20.05],
      type: 'government',
      state: 'active',
      regionId: 'region-1',
      distanceTo: point => 0,
      getDisplayInfo: () => ({ title: 'City Hall' }),
    }
    expect(isPOI(validPOI)).toBe(true)
    expect(isPOI({})).toBe(false)
  })
})