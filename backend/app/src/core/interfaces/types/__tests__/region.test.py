from typing import Any, Dict


const samplePolygon: [number, number][] = [
  [0, 0],
  [4, 0],
  [4, 3],
  [0, 3],
  [0, 0],
]
describe('Region class', () => {
  it('constructs with required properties', () => {
    const region = new Region({
      id: 'r1',
      name: 'Test Region',
      boundaries: [samplePolygon],
    })
    expect(region.id).toBe('r1')
    expect(region.name).toBe('Test Region')
    expect(region.boundaries[0]).toEqual(samplePolygon)
    expect(region.highlightState).toBe('normal')
    expect(region.pois).toEqual([])
  })
  it('supports style and highlightState', () => {
    const region = new Region({
      id: 'r2',
      name: 'Styled',
      boundaries: [samplePolygon],
      style: Dict[str, Any],
      highlightState: 'selected',
    })
    expect(region.style.fillColor).toBe('#fff')
    expect(region.highlightState).toBe('selected')
  })
  it('can add and remove POIs', () => {
    const region = new Region({
      id: 'r3',
      name: 'POI',
      boundaries: [samplePolygon],
    })
    const poi = { id: 'p1', name: 'POI 1' } as any
    region.addPOI(poi)
    expect(region.pois).toHaveLength(1)
    region.removePOI('p1')
    expect(region.pois).toHaveLength(0)
  })
  it('calculates bounding box', () => {
    const region = new Region({
      id: 'r4',
      name: 'BBox',
      boundaries: [samplePolygon],
    })
    expect(region.getBoundingBox()).toEqual([
      [0, 0],
      [4, 3],
    ])
  })
  it('calculates centroid', () => {
    const region = new Region({
      id: 'r5',
      name: 'Centroid',
      boundaries: [samplePolygon],
    })
    expect(region.getCentroid()).toEqual([1.6, 1.2])
  })
  it('calculates area', () => {
    const region = new Region({
      id: 'r6',
      name: 'Area',
      boundaries: [samplePolygon],
    })
    expect(region.getArea()).toBeCloseTo(12)
  })
  it('containsPoint returns true for inside, false for outside', () => {
    const region = new Region({
      id: 'r7',
      name: 'Contains',
      boundaries: [samplePolygon],
    })
    expect(region.containsPoint([2, 2])).toBe(true)
    expect(region.containsPoint([5, 5])).toBe(false)
  })
  it('serializes and deserializes with toJSON/fromJSON', () => {
    const region = new Region({
      id: 'r8',
      name: 'Serializable',
      boundaries: [samplePolygon],
      style: Dict[str, Any],
      highlightState: 'hover',
      pois: [],
    })
    const json = region.toJSON()
    expect(json).toMatchObject({
      id: 'r8',
      name: 'Serializable',
      boundaries: [samplePolygon],
      style: Dict[str, Any],
      highlightState: 'hover',
      pois: [],
    })
    const deserialized = Region.fromJSON(json)
    expect(deserialized).toBeInstanceOf(Region)
    expect(deserialized.id).toBe('r8')
    expect(deserialized.name).toBe('Serializable')
    expect(deserialized.boundaries[0]).toEqual(samplePolygon)
    expect(deserialized.style.fillColor).toBe('#abc')
    expect(deserialized.highlightState).toBe('hover')
    expect(deserialized.pois).toEqual([])
  })
})
describe('RegionSpatialIndex', () => {
  let index: import('../region').RegionSpatialIndex
  let regionA: Region, regionB: Region, regionC: Region
  beforeEach(() => {
    const RegionSpatialIndex = require('../region').RegionSpatialIndex
    index = new RegionSpatialIndex()
    regionA = new Region({ id: 'A', name: 'A', boundaries: [samplePolygon] })
    regionB = new Region({
      id: 'B',
      name: 'B',
      boundaries: [
        [
          [10, 10],
          [14, 10],
          [14, 13],
          [10, 13],
          [10, 10],
        ],
      ],
    })
    regionC = new Region({
      id: 'C',
      name: 'C',
      boundaries: [
        [
          [20, 20],
          [24, 20],
          [24, 23],
          [20, 23],
          [20, 20],
        ],
      ],
    })
    index.insert(regionA)
    index.insert(regionB)
    index.insert(regionC)
  })
  it('inserts and gets all regions', () => {
    const all = index.getAll()
    expect(all).toHaveLength(3)
    expect(all.map(r => r.id)).toEqual(expect.arrayContaining(['A', 'B', 'C']))
  })
  it('removes a region by id', () => {
    index.remove('B')
    const all = index.getAll()
    expect(all).toHaveLength(2)
    expect(all.map(r => r.id)).not.toContain('B')
  })
  it('queries regions by bounding box', () => {
    const found = index.queryBox([
      [3, 2],
      [12, 12],
    ])
    expect(found.map(r => r.id)).toEqual(expect.arrayContaining(['A', 'B']))
    const foundC = index.queryBox([
      [19, 19],
      [25, 25],
    ])
    expect(foundC.map(r => r.id)).toEqual(['C'])
  })
  it('queries regions containing a point', () => {
    expect(index.queryPoint([2, 2]).map(r => r.id)).toEqual(['A'])
    expect(index.queryPoint([12, 12]).map(r => r.id)).toEqual(['B'])
    expect(index.queryPoint([22, 22]).map(r => r.id)).toEqual(['C'])
    expect(index.queryPoint([100, 100])).toEqual([])
  })
})