from typing import Any


describe('Region class', () => {
  const samplePOI: IPOI = {
    id: 'poi-1',
    name: 'Test POI',
    coordinates: [10.05, 20.05],
    type: 'test',
    state: 'active',
    regionId: 'region-1',
    distanceTo: () => 0,
    getDisplayInfo: () => ({ title: 'Test POI' }),
  }
  const boundaries: [number, number][][] = [
    [
      [10.0, 20.0],
      [10.1, 20.0],
      [10.1, 20.1],
      [10.0, 20.1],
      [10.0, 20.0],
    ],
  ]
  it('should create a Region and access properties', () => {
    const region = new Region('region-1', 'Test Region', boundaries)
    expect(region.id).toBe('region-1')
    expect(region.name).toBe('Test Region')
    expect(region.boundaries).toEqual(boundaries)
    expect(region.style).toBeDefined()
    expect(region.highlightState).toBe('normal')
    expect(region.pois).toEqual([])
  })
  it('should add and remove POIs', () => {
    const region = new Region('region-1', 'Test Region', boundaries)
    region.addPOI(samplePOI)
    expect(region.pois.length).toBe(1)
    region.removePOI('poi-1')
    expect(region.pois.length).toBe(0)
  })
  it('should not add duplicate POIs', () => {
    const region = new Region('region-1', 'Test Region', boundaries)
    region.addPOI(samplePOI)
    region.addPOI(samplePOI)
    expect(region.pois.length).toBe(1)
  })
  it('should detect if a point is inside the region', () => {
    const region = new Region('region-1', 'Test Region', boundaries)
    expect(region.containsPoint([10.05, 20.05])).toBe(true)
    expect(region.containsPoint([11.0, 21.0])).toBe(false)
  })
  it('should calculate the correct bounding box', () => {
    const region = new Region('region-1', 'Test Region', boundaries)
    expect(region.getBoundingBox()).toEqual([
      [10.0, 20.0],
      [10.1, 20.1],
    ])
  })
  it('should handle empty POI list and complex boundaries', () => {
    const complexBoundaries: [number, number][][] = [
      [
        [0, 0],
        [2, 0],
        [2, 2],
        [0, 2],
        [0, 0],
      ],
      [
        [0.5, 0.5],
        [1.5, 0.5],
        [1.5, 1.5],
        [0.5, 1.5],
        [0.5, 0.5],
      ],
    ]
    const region = new Region('region-2', 'Complex Region', complexBoundaries)
    expect(region.pois.length).toBe(0)
    expect(region.containsPoint([1, 1])).toBe(false) 
    expect(region.containsPoint([0.25, 0.25])).toBe(true) 
  })
  it('should serialize and deserialize Region correctly', () => {
    const region = new Region('region-1', 'Test Region', boundaries)
    region.highlightState = 'selected'
    region.addPOI(samplePOI)
    const json = region.toJSON()
    expect(json.id).toBe('region-1')
    expect(json.name).toBe('Test Region')
    expect(json.boundaries).toEqual(boundaries)
    expect(json.highlightState).toBe('selected')
    expect(Array.isArray(json.pois)).toBe(true)
    expect(json.pois[0].id).toBe('poi-1')
    const RegionClass = require('../Region').Region
    const restored = RegionClass.fromJSON(json)
    expect(restored.id).toBe(region.id)
    expect(restored.name).toBe(region.name)
    expect(restored.boundaries).toEqual(region.boundaries)
    expect(restored.highlightState).toBe(region.highlightState)
    expect(restored.pois.length).toBe(1)
    expect(restored.pois[0].id).toBe('poi-1')
  })
  it('should handle empty POIs array in serialization/deserialization', () => {
    const region = new Region('region-2', 'Empty POIs', boundaries)
    const json = region.toJSON()
    expect(Array.isArray(json.pois)).toBe(true)
    expect(json.pois.length).toBe(0)
    const RegionClass = require('../Region').Region
    const restored = RegionClass.fromJSON(json)
    expect(restored.pois.length).toBe(0)
  })
  it('should throw error for missing required fields in fromJSON', () => {
    const RegionClass = require('../Region').Region
    expect(() => RegionClass.fromJSON({})).toThrow()
    expect(() => RegionClass.fromJSON({ id: 'x' })).toThrow()
    expect(() =>
      RegionClass.fromJSON({
        id: 'x',
        name: 'y',
        boundaries: [],
        style: {},
        highlightState: 123,
      })
    ).toThrow()
  })
})